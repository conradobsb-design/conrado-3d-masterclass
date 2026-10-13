# Planta humanizada com IA — repositórios, modelos e boas práticas de fidelidade
_Pesquisa de 13/10/2026 para o POE 642 · Casa A. Links, estrelas e datas foram conferidos nesse dia. O que não deu para confirmar está marcado como **[não verificado]**._

## 1. Resumo

1. **A fidelidade se garante fora do modelo, não dentro do prompt.** Nenhum modelo fechado (Nano Banana Pro/Gemini, GPT Image) tem ControlNet nem "força de denoise". A própria OpenAI admite "dificuldade em posicionar elementos com precisão em composições sensíveis a layout". Quem entrega planta fiel trabalha em três camadas:
   - **(a)** base vetorial limpa, gerada do PDF;
   - **(b)** IA para material, luz e vegetação;
   - **(c)** recomposição determinística: paredes, vidros e contornos do PDF colados de volta por cima do render.
2. **O PDF já é a melhor fonte de máscaras.** O PyMuPDF, que o pipeline já usa, separa paredes, vidro, portas, piscina etc. por layer e cor, em pixel exato e sem IA. É o achado mais importante da pesquisa.
3. **Prompt: menos é mais.** Todos os guias oficiais pedem instruções curtas de "mude X, mantenha todo o resto". Pedem também o estado desejado descrito em positivo, em vez de listas de "NO". O v17 tem cerca de 1.980 palavras e 55 negações.
4. **Proporção.** A base sai em ~1,545:1 e o motor está em 16:9, então o modelo é obrigado a reenquadrar. O `gerar_bases.py` agora gera uma versão 16:9 com margem branca, sem distorção.

## 2. O que você tem no seu GitHub

| Repositório | O que é | Serve para planta? |
|---|---|---|
| `conradobsb-design/lumina-render` (privado) | App Base44 com o Lumina Director. Gera o prompt-mestre a partir da imagem do modelo 3D (SketchUp) e da lista de materiais, envia ao Higgsfield, audita o render e gera prompt de ajuste. Usa Gemini na análise de materiais e tem presets e checklist de QA | **Parcialmente.** O fluxo "gera → audita → prompt de ajuste" é exatamente o que falta para plantas. Mas os protocolos são de perspectiva (pessoas, escala de textura, luz física); não há nada de planta baixa, máscara ou recomposição |
| `conradobsb-design/conrado-3d-masterclass` | Site + agora `projetos/POE642_CasaA/` (handoff, script das bases, esta pesquisa) | Sim (este material) |

Nenhum outro repositório seu trata de render.

## 3. Repositórios públicos que valem a pena

### 3.1 Extrair geometria exata do desenho (base e máscaras)
| Repo | O que faz | ★ / atividade | Uso no nosso pipeline |
|---|---|---|---|
| [pymupdf/PyMuPDF](https://github.com/pymupdf/PyMuPDF) | `Page.get_drawings()` devolve cada path com cor, preenchimento, espessura e **layer** | 10,9k · ativo | Máscaras pixel a pixel de parede, vidro, porta, piscina e deck direto do PDF. É o que o `gerar_bases.py` faz |
| [mozman/ezdxf](https://github.com/mozman/ezdxf) | Leitura de DXF em Python | 1,5k · ativo | Se a Denise Zuba mandar **DXF**, as máscaras por layer ficam triviais e mais confiáveis que pelo PDF |
| [abhipabhi/floor-to-rendered](https://github.com/abhipabhi/floor-to-rendered) | Parser vetorial de PDF: paredes por linhas paralelas, vidro por cor, portas | 1 · ago/2026 | Referência pequena da mesma abordagem determinística (gera .glb/.obj para o Blender) |
| [CubiCasa/CubiCasa5k](https://github.com/CubiCasa/CubiCasa5k) | 5 mil plantas anotadas + modelo de segmentação | 607 · **licença não comercial** | Só para quando vier PNG sem vetor; não usar em trabalho de cliente |
| [SizheHu/Raster-to-Graph](https://github.com/SizheHu/Raster-to-Graph) | Planta raster → grafo vetorial de paredes | 64 · 2026 | Alternativa para PNG |

### 3.2 Render com modelos abertos (controle real de geometria)
| Repo | O que faz | ★ / atividade | Por que importa |
|---|---|---|---|
| [Comfy-Org/ComfyUI](https://github.com/Comfy-Org/ComfyUI) | Ambiente de nós para SDXL, Flux e Qwen | 137k · ativo | Única forma de usar ControlNet, inpainting por máscara e recomposição num fluxo só |
| [Fannovel16/comfyui_controlnet_aux](https://github.com/Fannovel16/comfyui_controlnet_aux) | Pré-processadores MLSD, lineart, canny, segmentação | 4,2k · ativo | MLSD e lineart são os que mais combinam com planta |
| [xinsir6/ControlNetPlus](https://github.com/xinsir6/ControlNetPlus) | ControlNet "union" para SDXL (linhas + segmentação no mesmo modelo) | 2,1k · parado desde 2024, muito usado | Travar paredes por linha **e** materiais por mapa de cor |
| [lquesada/ComfyUI-Inpaint-CropAndStitch](https://github.com/lquesada/ComfyUI-Inpaint-CropAndStitch) | Recorta uma zona pela máscara, gera e cola de volta | 1,2k · ativo | Render zona a zona (piscina, deck, ambientes) sem tocar no resto |
| [QwenLM/Qwen-Image](https://github.com/QwenLM/Qwen-Image) | Qwen-Image-Edit 2509/2511: edição com ControlNet nativo (bordas, profundidade) e "geometria reforçada" | 8,4k · 2026 · Apache-2.0 | **Melhor opção aberta** para editar preservando estrutura, com uso comercial liberado |
| [black-forest-labs/flux](https://github.com/black-forest-labs/flux) + LoRA [BMT-FloorPlan-Kontext](https://huggingface.co/bmtdecorai/BMT-FloorPlan-Kontext-LoRA) | Kontext com LoRA treinado em "planta → planta colorida" | 26k | O único LoRA específico de planta que achamos. **Licença FLUX.1-dev não comercial** e saída de 1024 px |
| [paulh4x/AIxArchviz_BASIC_ComfyUI](https://github.com/paulh4x/AIxArchviz_BASIC_ComfyUI) | ~40 workflows de archviz (ControlNet Union, SAM2, Flux Fill, upscale) | 62 · 2025 | Kit pronto para começar; não tem fluxo de planta específico |

Há também um workflow público de planta → render do site ComfyUI.org ([link](https://www.comfyui.org/en/architectural-floor-plan-3d-rendering-workflow)). Ele usa lineart com peso 0.8 até 80% dos passos e exige "linha pura, sem texto, paredes fechadas", que é o que o nosso script entrega. O upscale 4K é feito em tiles de 512.

### 3.3 Planta → 3D (geometria determinística para texturizar depois)
- [grebtsew/FloorplanToBlender3d](https://github.com/grebtsew/FloorplanToBlender3d) (627★): visão computacional para Blender. O próprio README diz que funciona melhor com imagens pequenas.
- [IfcOpenShell](https://github.com/IfcOpenShell/IfcOpenShell) (2,9k★): para quando o cliente tiver IFC/BIM.

### 3.4 Listas e coleções de prompt
- [YouMind-OpenLab/awesome-nano-banana-pro-prompts](https://github.com/YouMind-OpenLab/awesome-nano-banana-pro-prompts) (13,6k★) e [ZeroLu/awesome-nanobanana-pro](https://github.com/ZeroLu/awesome-nanobanana-pro) (10,3k★): gerais, não de arquitetura.
- [gudo7208/awesome-ai4cad](https://github.com/gudo7208/awesome-ai4cad) e [THUCBIMS/Awesome-AIGC4AEC](https://github.com/THUCBIMS/Awesome-AIGC4AEC): artigos acadêmicos de IA em CAD e arquitetura.
- **Não existe** uma coleção séria de prompts de planta humanizada. O que mais se aproxima são os guias oficiais da seção 5.

## 4. Qual IA usar

| Cenário | Modelo | Por quê |
|---|---|---|
| Fluxo atual (rápido, sem instalar nada) | **Nano Banana Pro** (Gemini 3 Pro Image) no Higgsfield | Aceita até 14 imagens de referência e mantém o tamanho da entrada por padrão. Respeita bem "mantenha exatamente X" |
| Segunda opinião | **GPT Image** (ChatGPT/API) | Bom em material e luz. As máscaras são **só orientação** ("pode não seguir a forma exata"), então perde para o Gemini em geometria |
| Máxima fidelidade, com controle real | **Qwen-Image-Edit-2511** ou **SDXL + ControlNet Union** no ComfyUI | ControlNet de verdade e inpainting por zona. Exige GPU ou ComfyUI em nuvem |
| Evitar em trabalho de cliente | FLUX.1 Kontext dev + LoRA de planta, CubiCasa5k | Licença não comercial |

## 5. Boas práticas de prompt dos guias oficiais

**Google — Nano Banana / Gemini** ([guia oficial](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-nano-banana), [docs da API](https://ai.google.dev/gemini-api/docs/image-generation))
- Modelo oficial de edição: *"change only the [elemento]… Keep everything else in the image exactly the same, preserving the original style, lighting, and composition."*
- **"Semantic negative prompts"**: descrever o estado desejado ("uma rua vazia") em vez de negar ("sem carros"). Isso vale para o v17. Em vez de "never blue, never cyan, never tinted", funciona melhor "glass is a flat warm-neutral pale grey #D6D6D3, the same tone as the paper".
- Padrão documentado de estrutura + textura: *"Using the attached sketch as the structure and the attached sample as the texture…"*. Ou seja, dá para mandar **a base + uma prancha de materiais** (amostras de Travertino Romano, Marrom Tabaco, Bege Bahia, pedra portuguesa, deck) como segunda imagem. **[ainda não testado em planta]**
- A saída mantém o tamanho e a proporção da entrada por padrão; também é possível fixar a proporção.

**OpenAI — GPT Image** ([guia](https://developers.openai.com/api/docs/guides/image-generation), [cookbook de abril/2026](https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide))
- Modelo oficial de desenho → render: *"Preserve the exact layout, proportions, and perspective… Do not add new elements or text."*
- Prefira blocos curtos e rotulados a parágrafos longos. Comece de um prompt-base limpo e faça uma alteração por rodada, **repetindo a lista do que preservar a cada rodada**.

**Black Forest Labs — FLUX Kontext/FLUX.2** ([guia Kontext arquivado](https://web.archive.org/web/20251219154510/https://docs.bfl.ai/guides/prompting_guide_kontext_i2i), [FLUX.2](https://docs.bfl.ai/guides/prompting_guide_flux2))
- Prompts de até 512 tokens.
- Evite o verbo **"transform"**, que sinaliza mudança completa. O BLOCK 0 do v17 usa "Transform THIS image"; troque por "Render materials onto this exact plan".
- Use "while maintaining the same composition / keep the exact framing".
- Nomeie os elementos sempre, sem pronomes.
- O FLUX.2 não aceita prompt negativo. O FLUX 3 aceita caixas delimitadoras e cores hex.

**ByteDance — Seedream** ([guia](https://docs.byteplus.com/en/docs/ModelArk/1829186)): "prompts concisos e precisos" e menos de 600 palavras, porque prompts muito longos "espalham a informação".

## 6. Pipeline recomendado para a Casa A

1. **Base**: `gerar_bases.py` no PDF com layer `ARQ_PAREDE` → `_v3_vidros_neutros_16x9.png`. Sem texto, paredes pretas, vidro neutro, já em 16:9.
2. **Render**: Nano Banana Pro com a base 16:9. Opcionalmente, uma 2ª imagem com a prancha de materiais. Prompt mais enxuto, em positivo, sem "transform".
3. **Recomposição** (o passo que falta e que mais aumenta a fidelidade):
   1. redimensionar o render para o tamanho da base;
   2. alinhar (o Gemini às vezes desloca ou estica alguns pixels; Photoshop: Auto-Align ou modo Difference, [referência](https://www.photoshopessentials.com/photo-editing/how-to-fix-nano-banana-in-photoshop-2026/));
   3. colar por cima, em modo Multiplicar, as paredes #111111 e os vidros #D6D6D3 com contorno, tirados da própria base v3.

   O resultado fica com geometria idêntica ao PDF por construção, e acaba de vez com o vazamento de azul. Dá para automatizar num script `sobrepor_paredes.py` usando só a base v3 e o render.
4. **Pós**: norte e setas de escada (já previsto no handoff).
5. **Escala futura**: se o volume justificar, o mesmo fluxo no ComfyUI com Qwen-Image-Edit-2511 ou ControlNet Union + inpainting por zona, usando as máscaras do PDF.

## 7. Ressalvas
- Algumas páginas oficiais citam nomes de modelos novos que não conseguimos confirmar de forma independente. Os nomes acima são os que aparecem nas páginas linkadas.
- Não achamos LoRA de planta para Qwen-Image-Edit. O único LoRA de planta é o do FLUX Kontext, que é não comercial.
- Quanto à eficácia da prancha de materiais como 2ª referência em planta, o padrão é documentado pelo Google, mas não foi testado aqui.

"""A ampliação A3 do Subsolo da Casa A, em 4K pelo Nano Banana Pro.

Pedido do usuário (05/11/26): "preciso que você gere uma imagem ampliada em A3, ocupando a A3 inteira da prancha A em 4k
pelo nano banana pro. só a imagem em alta resolução."

A planta da final (`renders/POE642_CasaA_PH_Subsolo_final_rotulos.png`, 3840 x 2160) ocupa uns 1674 x 778 px do quadro;
na A3 deitada (420 x 297 mm, 4961 x 3508 px a 300 dpi) ela vai na largura toda, com `margem_px` de cada lado (a planta é
mais larga que a A3, sobra branco em cima e embaixo). A IA amplia a imagem, mas texto miúdo ela redesenha errado (troca
números de área); por isso os textos saem antes e voltam depois, desenhados de novo no tamanho da A3:
  1. `preparar`: os rótulos dos ambientes (o corpo, a quebra e o lugar de cada um achados na própria final, pelo desenho
     do `retoque_1pav_casae.rotulos_ambientes`) e a seta e o "SOBE PARA O / DECK" da escada (`cliente_subsolo_casaa_0511`)
     saem da imagem (o fundo sob o texto pela conta do alfa, e o miolo do traço pelo entorno); o recorte da planta em 4:3
     (a proporção da IA mais perto da A3, sem distorcer) é a entrada do Nano Banana Pro, em 4K.
  2. `montar`: a saída da IA é alinhada à entrada (ECC afim, na escala da entrada), recortada na proporção da A3 e levada
     a 4961 x 3508 px; o fundo fora da planta volta ao branco puro; os rótulos e a escada são desenhados de novo, no corpo
     da A3 (o mesmo desenho da final, na escala 4961 / largura do recorte).

  python3 ampliacao_a3_casaa.py preparar
  python3 ampliacao_a3_casaa.py montar <saida do Nano Banana Pro>

Saídas: `entrega/POE642_CasaA_PH_Subsolo_A3_4K.png` (300 dpi) e, nas renders, a entrada da IA, a prévia e a conferência
(a final ampliada sem IA ao lado da A3, em recortes).
"""

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import final3840_casaa as FA                    # noqa: E402
import retoque_1pav_casae as R1                 # noqa: E402

FINAL_SUB = FA.CASA / "renders" / "POE642_CasaA_PH_Subsolo_final_rotulos.png"
ENTRADA_IA = FA.CASA / "renders" / "POE642_CasaA_PH_Subsolo_A3_entrada_ia.png"
AJUSTE_ROT = FA.CASA / "renders" / "POE642_CasaA_PH_Subsolo_A3_rotulos.json"
SAIDA_A3 = FA.CASA / "entrega" / "POE642_CasaA_PH_Subsolo_A3_4K.png"

# A3 deitada a 300 dpi; a margem de cada lado da planta (px da A3); o branco do fundo (o que passa dele é fundo); a
# proporção da IA (a mais perto de √2 entre as do Nano Banana Pro); o miolo do traço (alfa) que vem do entorno.
A3 = {"px": (4961, 3508), "dpi": 300, "margem_px": 150, "branco": 245, "ia": (4, 3), "cheio": 0.85,
      # o branco puro fora da planta: o fundo a mais de `fundo_folga_px` (px da final) dela
      "fundo_folga_px": 3,
      # a busca do corpo de cada rótulo (frações do corpo da regra e os corpos das buscas dos pedidos) e o raio (px)
      "corpos": (1.3, 1.105, 0.936, 0.806, 1.15, 1.0, 0.9, 0.85, 0.78), "raio_px": 260, "score_min": 0.75,
      # abaixo desta correlação o texto da final não casa px a px com o desenho (está borrado): sai inteiro, pelo piso
      # vizinho (`tirar`, copiar)
      "casa_px": 0.95,
      # os tons (a baixa frequência) da final, com este desfoque (px da final)
      "tom_sigma_px": 2.5}

# O prompt fotorrealista do Nano Banana Pro (usuário, 12/11: "NA HORA DE GERAR O 4K, PRECISO QUE TRAGA REALISMO AOS
# MATERIAIS [...] MAS MANTENDO PROPORÇÃO, ESCALA, MATERIAIS E QUALIDADE"): a entrada é o mapa exato (posição, escala e
# material de cada coisa); a IA só acrescenta a física (microtextura na escala real, relevo, oclusão nos cantos, sombras
# de contato curtas, reflexos leves), sem mudar cor, brilho, desenho ou tamanho. Em blocos: o que travar; a meta (render
# de path tracer visto de cima, iluminação neutra e uniforme, sem luz natural: usuário, "TEM UM DETALHE NO PROMPT QUE NÃO
# PODE TER: ILUMINAÇÃO NATURAL"); cada material no lugar dele e na
# escala real (a régua do vinílico: a largura de uma esteira cobre ~4 fiadas de 20 cm); o que evitar.
PROMPT_FOTO = (
    "Photorealistic 4K re-render of the reference image: a top-down orthographic architectural floor plan (humanized "
    "plan) of a luxury house basement, seen exactly from directly above. Treat the reference as the exact layout, scale "
    "and material map: keep every wall, edge, opening, object and floor boundary at exactly the same position, size, "
    "proportion and orientation, pixel-aligned to the reference. Do not add, remove, move, rotate, resize, redraw or "
    "restyle anything. Do not add text, letters, numbers, arrows, triangles, symbols, people, plants, rugs or "
    "decorations.\n\n"
    "Goal: the look of a high-end architectural visualization rendered in a physically based path tracer (Corona / "
    "V-Ray quality), real materials seen from straight above under neutral, perfectly even, uniform illumination: "
    "no natural lighting, no sunlight, no daylight, no window light, no light beams, no light falloff or gradients "
    "across the rooms, every room lit the same. Add only material realism: true-to-scale material micro-texture, "
    "subtle surface relief, soft ambient occlusion where floors meet walls and fixtures, the same short soft contact "
    "shadows under objects as in the reference, and gentle reflections on glossy surfaces. Keep the overall colors, "
    "brightness, white balance and contrast of the reference.\n\n"
    "Materials, exactly where they are in the reference and at real-world scale:\n"
    "- Walls: solid matte dark graphite poché, perfectly flat, razor-sharp straight edges and square corners, no "
    "texture, no gradient.\n"
    "- Gym (large central room): warm light-oak wood-look vinyl planks in 20 cm wide rows running horizontally, random "
    "staggered end joints, fine natural grain and subtle color variation between planks, hairline joints, satin "
    "finish. Keep the plank direction, width and pattern of the reference (the width of one treadmill spans about four "
    "plank rows).\n"
    "- Gym equipment, same size, position and orientation: two treadmills (matte graphite frame, black textured rubber "
    "belt, dark console), two exercise bikes (graphite frame, black saddle and handlebars, small chrome details), one "
    "weight bench (black padded leatherette with fine stitching) in a steel rack with a chrome barbell and black "
    "weight plates.\n"
    "- Open patio, circulation, storage room and service bathroom floors: Bege Bahia limestone, warm light beige, "
    "honed, soft cloudy low-contrast veining and fine fossil speckles, seamless, no grout lines.\n"
    "- Hall, sauna, sauna anteroom and the female and male bathrooms: raw honed light travertine, ivory-cream, fine "
    "horizontal linear veining and tiny natural pores at real stone scale; the sauna bench in the same travertine, "
    "slightly darker.\n"
    "- Bathroom fixtures: glossy white ceramic wall-hung toilets with soft highlights; chrome flush plates, faucets and "
    "square shower heads with crisp small reflections; carved basins in polished dark brown speckled granite on raw "
    "travertine countertops; in the service bathroom a brown granite countertop with a white ceramic basin.\n"
    "- Glass shower enclosures, glass doors and windows: clear glass with very thin matte black aluminum frames and a "
    "faint cool reflection, the floor visible through the glass.\n"
    "- Storage room shelves along the walls: matte warm rosy-beige wood.\n"
    "- Elevator: brushed stainless steel cabin floor; the shafts keep their thin X lines.\n"
    "- Stair to the deck: light travertine treads with the same gradual fading shading.\n"
    "- Lawn on the left: dense natural grass seen from above, fine short blades, subtle tonal variation, the same dark "
    "olive green and the same small scale, no large blades, no flowers.\n"
    "- Background outside the building: pure white (#FFFFFF), untouched.\n\n"
    "Strictly avoid: natural lighting, sun rays, daylight patches, light streaks or shafts, cast shadows from "
    "windows, shadows outside the building, perspective or tilt, 3D extrusion of walls, lens effects, vignetting, "
    "depth of field, bloom, glare, film grain, noise, painterly, illustrated, cartoon or plastic CGI look, color shifts, warmer or cooler "
    "tint, brighter or darker image, wavy or bent lines, smudges, melted details, duplicated or missing objects, a "
    "different plank size or direction, and grout lines or tiles where there are none.")



# ----------------------------------------------------------------------------------------------------------------------
# Os textos da final: os rótulos (achados na imagem) e a escada (a mesma conta do `cliente_subsolo_casaa_0511`)
def _rotulos(Q):
    q = FA.A.PAVIMENTOS[Q.chave]
    return [r for r in R1.rotulos_pdf(Q.pg) if r[0] in q.get("incluir", ()) or not any(f in r[0] for f in FA.A.FORA)]


def _alfa_um(Q, r, opc, dx, dy, forma, pdf2img=None, esc=None, W=None):
    """O alfa (0..1) do rótulo r com as opções `opc`, deslocado (dx, dy) px do quadro de 3840 (na escala de `pdf2img`)."""
    pdf2img = pdf2img or Q.p2q
    esc0 = Q.W / 2000
    esc = esc or esc0
    W = W or forma[1]
    cx, cy = pdf2img(*r[2])
    aj = [(r[0], (cx * 2000 / W, cy * 2000 / W), (dx / esc0, dy / esc0), dict(opc, cor=(255, 255, 255)))]
    o = R1.rotulos_ambientes(np.zeros(forma + (3,), np.uint8), [r], pdf2img, escala_desvio=esc, granito=None,
                             ajustes=aj)
    return o[..., 1].astype(np.float32) / 255


def ajustar_rotulos(Q, img):
    """Cada rótulo da final: o corpo e a quebra (entre as opções das buscas) e o desvio (px) que casam o desenho com a
    imagem (correlação normalizada do alfa com o escuro da imagem, na vizinhança do ponto do PDF)."""
    q = A3
    H, W = img.shape[:2]
    escuro = 255 - cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
    out = []
    for r in _rotulos(Q):
        pal = r[1][0][0].split()
        opcs = []
        for c in q["corpos"]:
            opcs.append({"corpo": c})
            if len(pal) >= 2:
                m = (len(pal) + 1) // 2
                opcs.append({"corpo": c, "quebra": [" ".join(pal[:m]), " ".join(pal[m:])]})
        melhor = None
        for opc in opcs:
            a = _alfa_um(Q, r, opc, 0, 0, (H, W))
            ys, xs = np.nonzero(a > 0.02)
            x0, y0, x1, y1 = xs.min() - 2, ys.min() - 2, xs.max() + 3, ys.max() + 3
            R_ = q["raio_px"]
            wx0, wy0, wx1, wy1 = max(0, x0 - R_), max(0, y0 - R_), min(W, x1 + R_), min(H, y1 + R_)
            s = cv2.matchTemplate(escuro[wy0:wy1, wx0:wx1], a[y0:y1, x0:x1], cv2.TM_CCOEFF_NORMED)
            _, mx, _, (lx, ly) = cv2.minMaxLoc(s)
            if melhor is None or mx > melhor[0]:
                melhor = (float(mx), opc, int(wx0 + lx - x0), int(wy0 + ly - y0))
        sc, opc, dx, dy = melhor
        a = _alfa_um(Q, r, opc, dx, dy, (H, W))
        lum = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)[a > 0.9]
        cor = R1.ROTULOS["branco"] if np.median(lum) > 128 else R1.ROTULOS["cor"]
        print(f"    {r[0]:12s} casa {sc:.3f}  corpo {opc['corpo']:.3f}{'  quebra ' + '/'.join(opc['quebra']) if 'quebra' in opc else ''}"
              f"  desvio ({dx}, {dy}) px  {'branco' if cor == R1.ROTULOS['branco'] else 'preto'}")
        if sc < q["score_min"]:
            raise SystemExit(f"o rótulo {r[0]} não casou com a imagem ({sc:.3f})")
        out.append({"nome": r[0], "pdf": list(r[2]), "opc": opc, "desvio": [dx, dy], "cor": list(cor), "casa": sc})
    return out


def _r_do_nome(Q, nome, pdf):
    return min((r for r in _rotulos(Q) if r[0] == nome), key=lambda r: np.hypot(r[2][0] - pdf[0], r[2][1] - pdf[1]))


def _alfa_texto(texto, fonte, ox, oy, caixa, ss=4):
    from PIL import Image, ImageDraw
    X0, Y0, W, H = caixa
    t = Image.new("L", (W * ss, H * ss), 0)
    ImageDraw.Draw(t).text(((ox - X0) * ss, (oy - Y0) * ss), texto, font=fonte, fill=255, anchor="ls")
    return np.asarray(t.resize((W, H), Image.LANCZOS), np.float32) / 255


def escada_camadas(forma, s=1.0, x0=0.0, y0=0.0):
    """A seta (triângulo cheio) e as linhas do "SOBE PARA O / DECK" da escada (`cliente_subsolo_casaa_0511.escada_cs`),
    como [(alfa no quadro `forma`, cor BGR)], no quadro de 3840 levado por u = (x - x0) s, v = (y - y0) s."""
    from PIL import ImageFont
    from rodape_entrega import FONTES
    import cliente_subsolo_casaa_0511 as CS
    e, q = FA.ESCADA_A, CS.ESCADA_CS
    H, W = forma
    camadas = []
    k = q["ss"]
    pts = (np.float32(q["triangulo"]) - [x0, y0]) * s
    bx0, by0 = np.floor(pts.min(axis=0)).astype(int) - 2
    bx1, by1 = np.ceil(pts.max(axis=0)).astype(int) + 3
    m = np.zeros(((by1 - by0) * k, (bx1 - bx0) * k), np.uint8)
    cv2.fillPoly(m, [np.int32(np.round((pts - [bx0, by0]) * k))], 255, cv2.LINE_AA)
    a = np.zeros((H, W), np.float32)
    a[by0:by1, bx0:bx1] = cv2.resize(m.astype(np.float32) / 255, (bx1 - bx0, by1 - by0), interpolation=cv2.INTER_AREA)
    camadas.append((a, q["cor_seta"]))
    corpo = e["corpo_px"] * s
    fonte = ImageFont.truetype(str(FONTES / e["fonte"]), int(round(corpo * 4)))
    tx, ty = q["origem_px"]
    for i, linha in enumerate(q["texto"]):
        ox, oy = (tx - x0) * s, (ty + i * q["entrelinha_px"] - y0) * s
        Wt, Ht = int(fonte.getlength(linha) / 4) + int(12 * s), int(corpo * 3)
        X0, Y0 = int(ox) - int(4 * s), int(oy) - int(corpo * 2)
        a = np.zeros((H, W), np.float32)
        a[Y0:Y0 + Ht, X0:X0 + Wt] = _alfa_texto(linha, fonte, ox, oy, (X0, Y0, Wt, Ht))
        camadas.append((a, e["cor_texto"]))
    return camadas


def rotulos_camadas(Q, ajustes, forma, pdf2img=None, s=1.0):
    """Os rótulos ajustados, como [(alfa, cor)], no quadro `forma` (pdf2img e s: a A3)."""
    esc = Q.W / 2000 * s
    out = []
    for aj in ajustes:
        r = _r_do_nome(Q, aj["nome"], aj["pdf"])
        dx, dy = aj["desvio"]
        out.append((_alfa_um(Q, r, aj["opc"], dx, dy, forma, pdf2img=pdf2img, esc=esc), tuple(aj["cor"])))
    return out


def tirar(img, camadas, cheio, copiar=()):
    """O fundo sob cada texto (alfa a, cor c): (img - c a) / (1 - a); o miolo (a > cheio) vem do entorno (inpaint).
    Os textos em `copiar` (índices das camadas: o desenho não casa px a px com a imagem, o texto da final está mais
    borrado) saem inteiros: o piso logo acima ou abaixo, deslocado na vertical, entra no lugar (máscara esfumada)."""
    f = img.astype(np.float32)
    miolo = np.zeros(img.shape[:2], np.uint8)
    for i, (a, c) in enumerate(camadas):
        if i in copiar:
            continue
        al = a[..., None]
        f = np.where(al > 0.002, (f - np.float32(c) * al) / np.maximum(1 - al, 1e-3), f)
        miolo |= (a > cheio).astype(np.uint8)
    f = np.clip(np.round(f), 0, 255).astype(np.uint8)
    out = cv2.inpaint(f, cv2.dilate(miolo, np.ones((3, 3), np.uint8)) * 255, 3, cv2.INPAINT_TELEA)
    outros = np.max([a for j, (a, _) in enumerate(camadas) if j not in copiar] + [np.zeros(img.shape[:2])],
                    axis=0) > 0.02
    for i in copiar:
        a = camadas[i][0]
        # linha a linha, de cima para baixo: cada linha recebe o piso logo acima (já limpo, na 2ª linha) ou abaixo,
        # deslocado na vertical; a fonte não pode ter nada escuro (parede, peça) nem outro texto
        linhas = (a > 0.02).any(axis=1)
        idx = np.nonzero(linhas)[0]
        for grupo in np.split(idx, np.nonzero(np.diff(idx) > 1)[0] + 1):
            al = np.zeros_like(a)
            al[grupo[0]:grupo[-1] + 1] = a[grupo[0]:grupo[-1] + 1]
            m = cv2.dilate((al > 0.02).astype(np.uint8), np.ones((7, 7), np.uint8))
            ys, xs = np.nonzero(m)
            y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
            h = y1 - y0
            resto = (a > 0.02).copy()
            resto[:y1] = False                                          # as linhas de baixo, ainda com texto
            g = cv2.cvtColor(out, cv2.COLOR_BGR2GRAY)
            melhor = None
            for d in (-(h + 2), -(h + 6), h + 2, h + 6):
                fy0, fy1 = y0 + d, y1 + d
                if fy0 < 0 or fy1 > img.shape[0]:
                    continue
                ruim = (g[fy0:fy1, x0:x1] < 150).sum() + 100 * (outros | resto)[fy0:fy1, x0:x1].sum()
                if melhor is None or ruim < melhor[0]:
                    melhor = (ruim, d)
            ruim, d = melhor
            mf = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.5)[y0:y1, x0:x1, None]
            out[y0:y1, x0:x1] = np.clip(np.round(out[y0:y1, x0:x1] * (1 - mf) + out[y0 + d:y1 + d, x0:x1] * mf), 0,
                                        255).astype(np.uint8)
            print(f"    o texto {i}, linha {y0}-{y1}: saiu inteira, o piso deslocado {d} px na vertical"
                  f"{'' if ruim == 0 else f' (fonte com {ruim} px ruins)'}")
    return out


def pintar(img, camadas):
    f = img.astype(np.float32)
    for a, c in camadas:
        al = a[..., None]
        f = f * (1 - al) + np.float32(c) * al
    return np.clip(np.round(f), 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
# Os recortes: a planta (o que não é branco) no meio da A3, com a margem; o recorte da IA na mesma largura, em 4:3
def recortes(img):
    q = A3
    Wa, Ha = q["px"]
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ys, xs = np.nonzero(g < q["branco"])
    x0, y0, x1, y1 = int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1
    Wc = int(round((x1 - x0) * Wa / (Wa - 2 * q["margem_px"])))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    X0 = int(round(cx - Wc / 2))
    Hia = int(round(Wc * q["ia"][1] / q["ia"][0]))
    Yia = int(round(cy - Hia / 2))
    Ha3 = Wc * Ha / Wa                                  # a altura (px da final) da A3
    Ya3 = Yia + (Hia - Ha3) / 2
    s = Wa / Wc
    if Yia < 0 or Yia + Hia > img.shape[0] or X0 < 0 or X0 + Wc > img.shape[1]:
        raise SystemExit("o recorte sai do quadro")
    return {"planta": (x0, y0, x1, y1), "X0": X0, "Wc": Wc, "Yia": Yia, "Hia": Hia, "Ya3": Ya3, "s": s}


def preparar():
    img = cv2.imread(str(FINAL_SUB))
    Q = FA.QuadroA("Subsolo")
    import rotulos_subsolo_casaa as RS
    if RS.SPEC.exists():                       # os rótulos da final pela especificação (com os pedidos de 10/11)
        aj = RS.ler_spec()
        print(f"[Subsolo] {len(aj)} rótulos da especificação ({RS.SPEC.name})")
        camadas = RS.camadas(Q, aj, img.shape[:2]) + escada_camadas(img.shape[:2])
    else:
        print("[Subsolo] os rótulos da final, achados na imagem:")
        aj = ajustar_rotulos(Q, img)
        camadas = rotulos_camadas(Q, aj, img.shape[:2]) + escada_camadas(img.shape[:2])
    limpa = tirar(img, camadas, A3["cheio"], copiar=[i for i, r in enumerate(aj) if r["casa"] < A3["casa_px"]])
    rc = recortes(img)
    X0, Wc, Yia, Hia = rc["X0"], rc["Wc"], rc["Yia"], rc["Hia"]
    entrada = limpa[Yia:Yia + Hia, X0:X0 + Wc]
    cv2.imwrite(str(ENTRADA_IA), entrada)
    AJUSTE_ROT.write_text(json.dumps({"rotulos": aj, "recortes": rc}, ensure_ascii=False, indent=1) + "\n")
    # conferência: o fundo sob os textos
    x0, y0, x1, y1 = rc["planta"]
    lado = np.hstack([img[y0:y1, x0:x1], limpa[y0:y1, x0:x1]])
    cv2.imwrite(str(FA.CASA / "renders" / "POE642_CasaA_PH_Subsolo_A3_sem_textos.jpg"), lado,
                [cv2.IMWRITE_JPEG_QUALITY, 92])
    print(f"    a planta {x0},{y0} - {x1},{y1}; o recorte da IA {X0},{Yia} {Wc}x{Hia} (4:3); a A3: {rc['s']:.3f}x")
    print(f"    {ENTRADA_IA}")


# ----------------------------------------------------------------------------------------------------------------------
def montar(saida_ia):
    q = A3
    Wa, Ha = q["px"]
    img = cv2.imread(str(FINAL_SUB))
    entrada = cv2.imread(str(ENTRADA_IA))
    d = json.loads(AJUSTE_ROT.read_text())
    rc, aj = d["recortes"], d["rotulos"]
    X0, Wc, Yia, Hia, Ya3, s = rc["X0"], rc["Wc"], rc["Yia"], rc["Hia"], rc["Ya3"], rc["s"]
    ia = cv2.imread(str(saida_ia))
    Hi, Wi = ia.shape[:2]
    print(f"[Subsolo] a saída da IA: {Wi}x{Hi}")
    # o alinhamento: a saída na escala da entrada, ECC afim (a entrada é o molde)
    peq = cv2.resize(ia, (Wc, Hia), interpolation=cv2.INTER_AREA)
    g0 = cv2.GaussianBlur(cv2.cvtColor(entrada, cv2.COLOR_BGR2GRAY).astype(np.float32), (0, 0), 1.2)
    g1 = cv2.GaussianBlur(cv2.cvtColor(peq, cv2.COLOR_BGR2GRAY).astype(np.float32), (0, 0), 1.2)
    M = np.eye(2, 3, dtype=np.float32)
    _, M = cv2.findTransformECC(g0, g1, M, cv2.MOTION_AFFINE,
                                (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 300, 1e-7), None, 5)
    print(f"    alinhamento (entrada -> saída, px da entrada): [[{M[0, 0]:.4f} {M[0, 1]:.4f} {M[0, 2]:.2f}]"
          f" [{M[1, 0]:.4f} {M[1, 1]:.4f} {M[1, 2]:.2f}]]")
    # A3 (u, v) -> entrada (x, y) = (u / s, v / s + Ya3 - Yia) -> saída pequena (M) -> saída (Wi / Wc, Hi / Hia)
    Au = np.array([[1 / s, 0, 0], [0, 1 / s, Ya3 - Yia], [0, 0, 1]], np.float64)
    Mm = np.vstack([M.astype(np.float64), [0, 0, 1]])
    Sg = np.diag([Wi / Wc, Hi / Hia, 1.0])
    T = (Sg @ Mm @ Au)[:2]
    a3 = cv2.warpAffine(ia, T, (Wa, Ha), flags=cv2.INTER_LANCZOS4 | cv2.WARP_INVERSE_MAP,
                        borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))
    # os tons da final aprovada: a IA clareou a madeira da academia e mudou o cinza do depósito e o elevador. A baixa
    # frequência (desfoque de `tom_sigma_px`, px da final) vem da entrada ampliada; o detalhe fino fica o da IA
    Fe = np.array([[s, 0, 0], [0, s, -s * (Ya3 - Yia)]], np.float64)
    ref = cv2.warpAffine(entrada, Fe, (Wa, Ha), flags=cv2.INTER_LANCZOS4, borderValue=(255, 255, 255))
    sg = q["tom_sigma_px"] * s
    f = a3.astype(np.float32)
    f += cv2.GaussianBlur(ref.astype(np.float32), (0, 0), sg) - cv2.GaussianBlur(f, (0, 0), sg)
    a3 = np.clip(np.round(f), 0, 255).astype(np.uint8)
    # os shafts: o miolo em branco e o X em cinza fino (usuário, 12/11: "OS X PRECISAM SER EM CINZA COM TRAÇOS MAIS
    # FINOS E DELICADOS"), desenhados de novo na escala da A3 com os traços do PDF (a IA os engrossa)
    import biblioteca_subsolo_casaa_1211 as BS
    Q = FA.QuadroA("Subsolo")
    a3 = BS.desenhar_shafts(a3, BS.miolos_shafts(Q, img), s, X0, Ya3)
    # o fundo: branco puro fora da planta (a máscara da final, levada à A3)
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    fundo = (g >= 254).astype(np.uint8)
    n, lab = cv2.connectedComponents(fundo)
    canto = lab[0, 0]
    fundo = (lab == canto).astype(np.uint8)
    k = 2 * q["fundo_folga_px"] + 1
    fundo = cv2.erode(fundo, np.ones((k, k), np.uint8))
    Fq = np.array([[s, 0, -s * X0], [0, s, -s * Ya3]], np.float64)
    fa3 = cv2.warpAffine(fundo.astype(np.float32), Fq, (Wa, Ha), flags=cv2.INTER_LINEAR, borderValue=1.0)
    fa3 = cv2.GaussianBlur(fa3, (0, 0), 2.0)[..., None]
    a3 = np.clip(np.round(a3 * (1 - fa3) + 255 * fa3), 0, 255).astype(np.uint8)
    # os textos de novo, no corpo da A3
    def p2a(x, y):
        u, v = Q.p2q(x, y)
        return (u - X0) * s, (v - Ya3) * s
    import rotulos_subsolo_casaa as RS
    camadas = RS.camadas(Q, aj, (Ha, Wa), pdf2img=p2a, s=s) + escada_camadas((Ha, Wa), s, X0, Ya3)
    a3 = pintar(a3, camadas)
    from PIL import Image
    SAIDA_A3.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(cv2.cvtColor(a3, cv2.COLOR_BGR2RGB)).save(SAIDA_A3, dpi=(q["dpi"], q["dpi"]), optimize=True)
    cv2.imwrite(str(FA.CASA / "renders" / "POE642_CasaA_PH_Subsolo_A3_4K_previa.jpg"),
                cv2.resize(a3, (2000, round(2000 * Ha / Wa)), interpolation=cv2.INTER_AREA), [cv2.IMWRITE_JPEG_QUALITY, 90])
    # conferência: a final ampliada sem IA (Lanczos) e a A3, lado a lado, em recortes (px da final)
    ref = cv2.warpAffine(img, Fq, (Wa, Ha), flags=cv2.INTER_LANCZOS4, borderValue=(255, 255, 255))
    blocos = []
    for nome, (x0, y0, x1, y1) in CONFERENCIA.items():
        u0, v0, u1, v1 = [int(round(t)) for t in ((x0 - X0) * s, (y0 - Ya3) * s, (x1 - X0) * s, (y1 - Ya3) * s)]
        par = np.hstack([ref[v0:v1, u0:u1], np.full((v1 - v0, 12, 3), 255, np.uint8), a3[v0:v1, u0:u1]])
        blocos.append(cv2.copyMakeBorder(par, 0, 12, 0, 0, cv2.BORDER_CONSTANT, value=(255, 255, 255)))
        cv2.imwrite(str(FA.CASA / "renders" / f"POE642_CasaA_PH_Subsolo_A3_conferencia_{nome}.jpg"), par,
                    [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"    {SAIDA_A3} {Wa}x{Ha} ({q['dpi']} dpi)")


# Os recortes da conferência (px da final)
CONFERENCIA = {"academia_banhos": (1300, 1050, 1900, 1650), "escada_grama": (720, 1040, 1180, 1400),
               "deposito_circulacao": (1080, 866, 1900, 1060), "hall_elevador": (1880, 1040, 2393, 1230)}


# ----------------------------------------------------------------------------------------------------------------------
# A correção da saída da IA antes da ampliação a 12K (o mapa das diferenças de estrutura entre a saída e a entrada
# ampliada mostrou o que ela inventou, em 10/11/26): a sauna com bancos em degraus em L (o PDF tem um banco só, junto à
# parede de baixo), a bancada de granito do BH. SERV. com veio de madeira e os chuveiros quadrados (com a grade de furos)
# trocados por placas lisas ou redondos. Nesses trechos (`CORRIGIR_PX`, px da final) entra a entrada ampliada (Lanczos)
# com nitidez (`nitidez`: força e raio do unsharp), com a borda esfumada; o resto (os aparelhos da academia, redesenhados
# fiéis e mais nítidos) fica o da IA.
CORRIGIR_PX = {"sauna": (1188, 1506, 1382, 1634), "bancada_bh_serv": (1100, 988, 1136, 1049),
               "chuveiro_bh_serv": (1105, 897, 1128, 922), "chuveiro_bh_sauna": (1422, 1596, 1444, 1636),
               "chuveiro_bh_fem": (1657, 1596, 1679, 1636),
               # depois (usuário, 10/11/26, nos recortes do 12K: "CORRIGIR ESSA FALHA NA PAREDE (NO PORTAL)"): a IA
               # tinha feito um pé inclinado na ponta das paredes dos portais, a partir do risco do marco da porta que a
               # final tinha ali (tirado da final por `cliente_subsolo_casaa_0511.portais_cs`); as pontas vêm da final
               "portal_bh_fem_esq": (1486, 1492, 1504, 1522), "portal_bh_fem_dir": (1545, 1492, 1563, 1522),
               "portal_bh_masc_esq": (1797, 1492, 1815, 1522), "portal_bh_masc_dir": (1853, 1492, 1871, 1522),
               "portal_bh_serv_cima": (1178, 876, 1209, 1001), "portal_bh_serv_baixo": (1181, 1028, 1209, 1049),
               # depois (OK do usuário: "PODE CORRIGIR OS DOIS PORTAIS TAMBÉM"; e "NÃO PODEMOS TER PORTAS "FLUTUANTES""):
               # os portais do depósito e do BH. da sauna, com as folhas ligadas à ponta da parede
               "portal_deposito_cima": (1326, 959, 1352, 977), "portal_deposito_baixo": (1326, 1015, 1356, 1036),
               "portal_bh_sauna_cima": (1371, 1512, 1394, 1530), "portal_bh_sauna_baixo": (1371, 1555, 1398, 1575),
               # a face esquerda da parede do BH. SERV. (do nicho ao portal), refeita na final: a IA a tinha feito
               # ondulada, com um ponto escuro junto ao nicho; e as prateleiras do depósito, no tom novo (o dos armários)
               "prateleiras_deposito_cima": (1342, 876, 1832, 912), "prateleiras_deposito_lado": (1826, 876, 1874, 1049)}
CORRECAO = {"nitidez": (0.6, 1.2), "borda_px": 2.0}
# depois (11/11, o vinílico da foto na academia: "vamos ter que alterar o vinílico do subsolo da casa A"): o que mudou na
# final contra a de antes (`MUDOU["antes"]`, a final de quando a IA foi feita) também vem da entrada nova, px a px (o que
# difere mais que `limiar`, crescido `folga_px`); os aparelhos da academia, que não mudaram, ficam os da IA
MUDOU = {"antes": None, "limiar": 6, "folga_px": 2}
# depois (12/11, o prompt fotorrealista `PROMPT_FOTO`; com `--estrutura`): a IA, mais livre, trouxe os materiais mais reais
# mas redesenhou trechos (um ambiente novo fora da casa, as paredes do BH. SERV., o portal do depósito, o supino e as
# bicicletas). Da IA fica só o que manteve o desenho: onde a estrutura (passa-banda, px da entrada) foge mais que
# `limiar`, crescido `folga_px`, vem da entrada; e também, inteiros, os aparelhos da academia (o retângulo de cada peça
# de `biblioteca_subsolo_casaa_1211.ACADEMIA`, com a `escala`/`largura_m`, e `peca_folga_px`), a escada e os buracos
# pequenos da máscara (até `buraco_max_px`). Na prática: paredes, portas, vidros, louças, bancadas e peças da final;
# pisos e grama da IA (os tons casados com a final no `montar`)
ESTRUTURA = {"ligada": False, "limiar": 7.0, "folga_px": 3, "peca_folga_px": 4, "buraco_max_px": 900,
             "caixas_px": {"escada": (900, 1050, 1090, 1132)}}


def mascara_estrutura(ia, entrada, T):
    """A máscara (px da entrada) do que a IA redesenhou: a estrutura que foge, os aparelhos da academia, a escada."""
    from scipy import ndimage
    import biblioteca_subsolo_casaa_1211 as BS
    q = ESTRUTURA
    Hc, Wc = entrada.shape[:2]
    rc = json.loads(AJUSTE_ROT.read_text())["recortes"]
    X0, Yia = rc["X0"], rc["Yia"]
    al = cv2.warpAffine(ia, T, (Wc, Hc), flags=cv2.INTER_AREA | cv2.WARP_INVERSE_MAP, borderValue=(255, 255, 255))
    g0 = cv2.GaussianBlur(cv2.cvtColor(entrada, cv2.COLOR_BGR2GRAY).astype(np.float32), (0, 0), 1.2)
    g1 = cv2.GaussianBlur(cv2.cvtColor(al, cv2.COLOR_BGR2GRAY).astype(np.float32), (0, 0), 1.2)
    b0, b1 = g0 - cv2.GaussianBlur(g0, (0, 0), 4), g1 - cv2.GaussianBlur(g1, (0, 0), 4)
    ds = cv2.GaussianBlur(np.abs(b0 - b1), (0, 0), 2)
    casa = cv2.cvtColor(entrada, cv2.COLOR_BGR2GRAY) < 245
    k = 2 * q["folga_px"] + 1
    m = cv2.dilate(((ds > q["limiar"]) & casa).astype(np.uint8), np.ones((k, k), np.uint8)) > 0
    import final3840_casaa as FA_
    import contextlib
    import io
    with contextlib.redirect_stdout(io.StringIO()):
        Q = FA_.QuadroA("Subsolo")
    f = q["peca_folga_px"]
    for pc in BS.ACADEMIA["pecas"]:
        x0, y0, x1, y1 = BS.caixa_px(Q, pc["pt"])
        e = pc.get("escala", 1.0)
        if "largura_m" in pc:
            e = pc["largura_m"] * Q.px_m / (x1 - x0)
        cx, cy, mw, mh = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) * e / 2 + f, (y1 - y0) * e / 2 + f
        m[max(int(cy - mh) - Yia, 0):int(np.ceil(cy + mh)) - Yia, max(int(cx - mw) - X0, 0):int(np.ceil(cx + mw)) - X0] = True
    for x0, y0, x1, y1 in q["caixas_px"].values():
        m[y0 - Yia:y1 - Yia, x0 - X0:x1 - X0] = True
    buracos = ndimage.binary_fill_holes(m) & ~m
    n, lab, st, _ = cv2.connectedComponentsWithStats(buracos.astype(np.uint8), 4)
    peq = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] <= q["buraco_max_px"]])
    m |= peq
    print(f"    estrutura: {m[casa].mean() * 100:.1f}% da casa vem da entrada (paredes, peças, aparelhos, escada)")
    return m.astype(np.float32)


# depois (12/11, "DEIXAR O CONTORNO EM VOLTA DOS VASOS PERFEITOS"): na final, o retângulo do vaso antigo em volta das
# bacias novas passou a ter o piso do lado (`biblioteca_subsolo_casaa_1211.sob_peca`, `fonte`); a IA foi feita com o
# retângulo chapado, e o trecho trazido da entrada (pelo `MUDOU`) deixava a borda reta dele à vista no 12K (a entrada
# ampliada é mais lisa que o piso da IA). Em volta de cada retângulo, a passagem da entrada para a IA vira uma rampa de
# `rampa_px` (px da final) para fora, em vez do degrau; dentro, a entrada. (A IA em volta não serve de fonte: ela desenhou
# a bacia antiga maior e o retângulo chapado, que a máscara da estrutura já cobre.)
VASOS_IA = {"ligada": True, "rampa_px": 6}


def rampa_vasos(X0, Yia, Wc, Hc):
    """A rampa (float, 1 no retângulo de cada vaso, 0 a `rampa_px` dele) na janela da entrada, e a zona que ela ocupa."""
    import biblioteca_subsolo_casaa_1211 as BS
    q = VASOS_IA
    Q = FA.QuadroA("Subsolo")
    caixa = np.zeros((Hc, Wc), np.uint8)
    for v in BS.BANHOS_BIB["vasos"]:
        c = BS.caixa_px(Q, v["pt"])
        x0, y0, x1, y1 = int(np.floor(c[0])) - 1, int(np.floor(c[1])) - 1, int(np.ceil(c[2])) + 1, int(np.ceil(c[3])) + 1
        caixa[y0 - Yia:y1 - Yia, x0 - X0:x1 - X0] = 1
    dist = cv2.distanceTransform(1 - caixa, cv2.DIST_L2, 5)
    rampa = np.clip(1 - dist / q["rampa_px"], 0, 1).astype(np.float32)
    zona = dist <= q["rampa_px"] + 3
    return rampa, zona


def corrigir_ia(saida_ia, destino):
    """A saída da IA com os trechos de `CORRIGIR_PX` vindos da entrada ampliada (no quadro da saída, pelo ECC)."""
    q = CORRECAO
    ia = cv2.imread(str(saida_ia))
    entrada = cv2.imread(str(ENTRADA_IA))
    rc = json.loads(AJUSTE_ROT.read_text())["recortes"]
    X0, Yia = rc["X0"], rc["Yia"]
    Hi, Wi = ia.shape[:2]
    Hc, Wc = entrada.shape[:2]
    peq = cv2.resize(ia, (Wc, Hc), interpolation=cv2.INTER_AREA)
    g0 = cv2.GaussianBlur(cv2.cvtColor(entrada, cv2.COLOR_BGR2GRAY).astype(np.float32), (0, 0), 1.2)
    g1 = cv2.GaussianBlur(cv2.cvtColor(peq, cv2.COLOR_BGR2GRAY).astype(np.float32), (0, 0), 1.2)
    M = np.eye(2, 3, dtype=np.float32)
    _, M = cv2.findTransformECC(g0, g1, M, cv2.MOTION_AFFINE,
                                (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 300, 1e-7), None, 5)
    T = (np.diag([Wi / Wc, Hi / Hc, 1.0]) @ np.vstack([M.astype(np.float64), [0, 0, 1]]))[:2]
    ref = cv2.warpAffine(entrada, T, (Wi, Hi), flags=cv2.INTER_LANCZOS4, borderValue=(255, 255, 255)).astype(np.float32)
    f_, r_ = q["nitidez"]
    ref = np.clip(ref + f_ * (ref - cv2.GaussianBlur(ref, (0, 0), r_)), 0, 255)
    m = np.zeros((Hi, Wi), np.float32)
    for nome, (x0, y0, x1, y1) in CORRIGIR_PX.items():
        pts = np.float32([[x0 - X0, y0 - Yia], [x1 - X0, y0 - Yia], [x1 - X0, y1 - Yia], [x0 - X0, y1 - Yia]])
        pq = cv2.transform(pts[None], T)[0]
        cv2.fillConvexPoly(m, np.int32(np.round(pq)), 1.0)
    if ESTRUTURA["ligada"]:
        m = np.maximum(m, cv2.warpAffine(mascara_estrutura(ia, entrada, T), T, (Wi, Hi), flags=cv2.INTER_LINEAR))
        # antes de juntar, os tons da IA (a baixa frequência) casados com os da entrada: a IA esfriou os pisos, e sem
        # isso a borda da máscara ficava um contorno claro ondulado
        sg = A3["tom_sigma_px"] * Wi / Wc
        iaf = ia.astype(np.float32)
        ia = np.clip(iaf + cv2.GaussianBlur(ref, (0, 0), sg) - cv2.GaussianBlur(iaf, (0, 0), sg), 0, 255)
    if MUDOU["antes"]:
        a0, a1 = cv2.imread(str(MUDOU["antes"])), cv2.imread(str(FINAL_SUB))
        d = (np.abs(a0.astype(np.int16) - a1.astype(np.int16)).max(axis=2) > MUDOU["limiar"]).astype(np.uint8)
        k = 2 * MUDOU["folga_px"] + 1
        d = cv2.dilate(d, np.ones((k, k), np.uint8))[Yia:Yia + Hc, X0:X0 + Wc].astype(np.float32)
        if VASOS_IA["ligada"]:
            rampa, zona = rampa_vasos(X0, Yia, Wc, Hc)
            d[zona] = rampa[zona]
        m = np.maximum(m, cv2.warpAffine(d, T, (Wi, Hi), flags=cv2.INTER_LINEAR))
        print(f"    e o que mudou na final contra {Path(MUDOU['antes']).name}: {int(d.sum())} px da entrada")
    m = cv2.GaussianBlur(m, (0, 0), q["borda_px"] * Wi / Wc / 2.7)[..., None]
    out = np.clip(np.round(ia * (1 - m) + ref * m), 0, 255).astype(np.uint8)
    cv2.imwrite(str(destino), out)
    print(f"    a saída da IA corrigida em {len(CORRIGIR_PX)} trechos ({', '.join(CORRIGIR_PX)}): {destino}")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# O JPG em 12K das duas opções de letra (usuário, 10/11/26: "PODE GERAR O ARQUIVO JPG 12K DAS DUAS OPÇÕES"; antes: "VOU
# PRECISAR DA IMAGEM, SÓ DA IMAGEM, EM JPG PARA O CLIENTE PODER TRABALHAR EM CIMA DELA PARA O BOOK DELA"). A saída do
# Nano Banana Pro (4K) é levada a 12K pelo Topaz (High Fidelity V2, no Higgsfield) e montada como a A3 de `montar`, na
# proporção da A3 deitada (`GRANDE["largura"]` x largura / √2), sem passar a imagem inteira por float: a correção dos tons
# sai na escala da entrada e é ampliada; os rótulos e a escada são desenhados numa janela em volta de cada um, na Inter
# (opção A, `rotulos_subsolo_casaa.camadas`) e na Kalam (opção B, `rotulos_manuscritos_casaa`).
GRANDE = {"largura": 12288, "janela_px": (1400, 600), "qualidade": 95,
          "saida": FA.CASA / "entrega" / "POE642_CasaA_PH_Subsolo_12K_opcao_{opcao}.jpg"}


def montar_grande(saida_topaz, largura=None):
    import rotulos_subsolo_casaa as RS
    import rotulos_manuscritos_casaa as RM
    from PIL import Image
    q, g = A3, GRANDE
    L = largura or g["largura"]
    Wa0, Ha0 = q["px"]
    Hh = int(round(L * Ha0 / Wa0))
    img = cv2.imread(str(FINAL_SUB))
    entrada = cv2.imread(str(ENTRADA_IA))
    d = json.loads(AJUSTE_ROT.read_text())
    rc, aj = d["recortes"], d["rotulos"]
    X0, Wc, Yia, Hia, Ya3 = rc["X0"], rc["Wc"], rc["Yia"], rc["Hia"], rc["Ya3"]
    s = L / Wc
    ia = cv2.imread(str(saida_topaz))
    Hi, Wi = ia.shape[:2]
    print(f"[Subsolo] a saída ampliada: {Wi}x{Hi}; o JPG: {L}x{Hh} ({s:.3f}x a final)")
    peq = cv2.resize(ia, (Wc, Hia), interpolation=cv2.INTER_AREA)
    g0 = cv2.GaussianBlur(cv2.cvtColor(entrada, cv2.COLOR_BGR2GRAY).astype(np.float32), (0, 0), 1.2)
    g1 = cv2.GaussianBlur(cv2.cvtColor(peq, cv2.COLOR_BGR2GRAY).astype(np.float32), (0, 0), 1.2)
    M = np.eye(2, 3, dtype=np.float32)
    _, M = cv2.findTransformECC(g0, g1, M, cv2.MOTION_AFFINE,
                                (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 300, 1e-7), None, 5)
    print(f"    alinhamento (entrada -> saída, px da entrada): [[{M[0, 0]:.4f} {M[0, 1]:.4f} {M[0, 2]:.2f}]"
          f" [{M[1, 0]:.4f} {M[1, 1]:.4f} {M[1, 2]:.2f}]]")
    Au = np.array([[1 / s, 0, 0], [0, 1 / s, Ya3 - Yia], [0, 0, 1]], np.float64)
    Mm = np.vstack([M.astype(np.float64), [0, 0, 1]])
    Sg = np.diag([Wi / Wc, Hi / Hia, 1.0])
    T = (Sg @ Mm @ Au)[:2]
    a3 = cv2.warpAffine(ia, T, (L, Hh), flags=cv2.INTER_LANCZOS4 | cv2.WARP_INVERSE_MAP,
                        borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))
    del ia
    # os tons da final: a baixa frequência na escala da entrada (a faixa da A3 dela), ampliada
    hb = int(round(Hh / s))
    Fe0 = np.array([[1, 0, 0], [0, 1, -(Ya3 - Yia)]], np.float64)
    ref0 = cv2.warpAffine(entrada, Fe0, (Wc, hb), flags=cv2.INTER_LINEAR, borderValue=(255, 255, 255)).astype(np.float32)
    a3p = cv2.resize(a3, (Wc, hb), interpolation=cv2.INTER_AREA).astype(np.float32)
    sg = q["tom_sigma_px"]
    corr = cv2.GaussianBlur(ref0, (0, 0), sg) - cv2.GaussianBlur(a3p, (0, 0), sg)
    corr = cv2.resize(corr, (L, Hh), interpolation=cv2.INTER_CUBIC)
    for y in range(0, Hh, 1024):
        a3[y:y + 1024] = np.clip(np.round(a3[y:y + 1024].astype(np.float32) + corr[y:y + 1024]), 0, 255).astype(np.uint8)
    del corr
    # os shafts: o miolo em branco e o X em cinza fino, desenhados de novo na escala do JPG (12/11)
    import biblioteca_subsolo_casaa_1211 as BS
    Q = FA.QuadroA("Subsolo")
    a3 = BS.desenhar_shafts(a3, BS.miolos_shafts(Q, img), s, X0, Ya3)
    # o fundo: branco puro fora da planta
    gq = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    fundo = (gq >= 254).astype(np.uint8)
    _, lab = cv2.connectedComponents(fundo)
    fundo = (lab == lab[0, 0]).astype(np.uint8)
    kk = 2 * q["fundo_folga_px"] + 1
    fundo = cv2.erode(fundo, np.ones((kk, kk), np.uint8))
    Fq = np.array([[s, 0, -s * X0], [0, s, -s * Ya3]], np.float64)
    sf = 2.0 * L / Wa0
    for y in range(0, Hh, 1024):
        y1 = min(Hh, y + 1024)
        pad = int(4 * sf) + 2
        ya, yb = max(0, y - pad), min(Hh, y1 + pad)
        Ft = Fq.copy()
        Ft[1, 2] -= ya
        fa = cv2.warpAffine(fundo.astype(np.float32), Ft, (L, yb - ya), flags=cv2.INTER_LINEAR, borderValue=1.0)
        fa = cv2.GaussianBlur(fa, (0, 0), sf)[y - ya:y1 - ya, :, None]
        a3[y:y1] = np.clip(np.round(a3[y:y1] * (1 - fa) + 255 * fa), 0, 255).astype(np.uint8)
    base = a3

    def p2a(x, y):
        u, v = Q.p2q(x, y)
        return (u - X0) * s, (v - Ya3) * s

    def janela(cx, cy):
        jw, jh = g["janela_px"]
        jw, jh = int(jw * s / 6.9), int(jh * s / 6.9)
        bx, by = int(cx - jw / 2), int(cy - jh / 2)
        return max(0, bx), max(0, by), min(L, bx + jw), min(Hh, by + jh)

    def com_alfa(out, a, cor, bx, by):
        h, w = a.shape[:2]
        reg = out[by:by + h, bx:bx + w].astype(np.float32)
        al = a[..., None] if a.ndim == 2 else a
        out[by:by + h, bx:bx + w] = np.clip(np.round(reg * (1 - al) + np.float32(cor) * al), 0, 255).astype(np.uint8)

    import cliente_subsolo_casaa_0511 as CS
    tx, ty = CS.ESCADA_CS["origem_px"]
    ex, ey = (tx - X0) * s, (ty - Ya3) * s
    ebx, eby, ebx1, eby1 = int(ex - 60 * s), int(ey - 40 * s), int(ex + 140 * s), int(ey + 60 * s)
    for opcao in ("A", "B"):
        out = base.copy()
        for b in aj:
            r, opc = RS.r_do_ajuste(Q, b)
            cx, cy = p2a(*r[2])
            cx, cy = cx + b["desvio"][0] * s, cy + b["desvio"][1] * s
            bx, by, bx1, by1 = janela(cx, cy)
            if opcao == "A":
                loc = (lambda bx_, by_: (lambda x, y: (p2a(x, y)[0] - bx_, p2a(x, y)[1] - by_)))(bx, by)
                a = _alfa_um(Q, r, opc, b["desvio"][0], b["desvio"][1], (by1 - by, bx1 - bx), pdf2img=loc,
                             esc=Q.W / 2000 * s)
                com_alfa(out, a, b["cor"], bx, by)
            else:
                k_rot = RM._altura_maiuscula(FONTES_INTER(R1.ROTULOS["fonte"])) / RM._altura_maiuscula(RM.FONTE) * \
                    RM.MANUSCRITA["altura"]
                itens = [(t_, c_ * k_rot, x_ - bx, y_ - by, "ms")
                         for t_, c_, x_, y_ in RM.linhas_rotulo(Q, b, pdf2img=p2a, escala_desvio=Q.W / 2000 * s)]
                sub = out[by:by1, bx:bx1]
                out[by:by1, bx:bx1] = RM.desenhar(sub, itens, tuple(b["cor"]),
                                                  reforco_px=RM.MANUSCRITA["reforco_px"] * s)
        # a escada: a seta e o texto (na Inter da final, ou na Kalam)
        ebx_, eby_ = max(0, ebx), max(0, eby)
        cam = escada_camadas((eby1 - eby_, ebx1 - ebx_), s, X0 + ebx_ / s, Ya3 + eby_ / s)
        if opcao == "A":
            for a, cor in cam:
                com_alfa(out, a, cor, ebx_, eby_)
        else:
            com_alfa(out, cam[0][0], cam[0][1], ebx_, eby_)
            e = FA.ESCADA_A
            k_esc = RM._altura_maiuscula(FONTES_DIR() / e["fonte"]) / RM._altura_maiuscula(RM.FONTE) * \
                RM.MANUSCRITA["altura"]
            itens = [(linha, e["corpo_px"] * s * k_esc, ex - ebx_, ey + i * CS.ESCADA_CS["entrelinha_px"] * s - eby_, "ls")
                     for i, linha in enumerate(CS.ESCADA_CS["texto"])]
            sub = out[eby_:eby1, ebx_:ebx1]
            out[eby_:eby1, ebx_:ebx1] = RM.desenhar(sub, itens, e["cor_texto"], reforco_px=RM.MANUSCRITA["reforco_px"] * s)
        arq = Path(str(g["saida"]).format(opcao=opcao))
        dpi = int(round(L / (420 / 25.4)))
        Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB)).save(arq, quality=g["qualidade"], subsampling=0,
                                                                    dpi=(dpi, dpi), optimize=True)
        prev = cv2.resize(out, (2000, round(2000 * Hh / L)), interpolation=cv2.INTER_AREA)
        cv2.imwrite(str(FA.CASA / "renders" / f"POE642_CasaA_PH_Subsolo_12K_opcao_{opcao}_previa.jpg"), prev,
                    [cv2.IMWRITE_JPEG_QUALITY, 90])
        for nome, (x0, y0, x1, y1) in CONFERENCIA.items():
            u0, v0, u1, v1 = [int(round(t_)) for t_ in ((x0 - X0) * s, (y0 - Ya3) * s, (x1 - X0) * s, (y1 - Ya3) * s)]
            cr = out[v0:v1, u0:u1]
            cv2.imwrite(str(FA.CASA / "renders" / f"POE642_CasaA_PH_Subsolo_12K_opcao_{opcao}_conferencia_{nome}.jpg"),
                        cv2.resize(cr, (cr.shape[1] // 2, cr.shape[0] // 2), interpolation=cv2.INTER_AREA),
                        [cv2.IMWRITE_JPEG_QUALITY, 90])
        print(f"    {arq} {L}x{Hh} ({dpi} dpi na A3), {arq.stat().st_size / 1e6:.1f} MB")


def FONTES_DIR():
    from rodape_entrega import FONTES
    return FONTES


def FONTES_INTER(peso):
    return FONTES_DIR() / f"Inter-{peso}.otf"


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="etapa", required=True)
    sub.add_parser("preparar")
    m = sub.add_parser("montar")
    m.add_argument("saida_ia", type=Path)
    m3 = sub.add_parser("corrigir", help="a saída da IA (4K) com os trechos inventados vindos da entrada")
    m3.add_argument("saida_ia", type=Path)
    m3.add_argument("destino", type=Path)
    m3.add_argument("--estrutura", action="store_true",
                    help="o que a IA redesenhou (a estrutura que foge, os aparelhos, a escada) vem da entrada (`ESTRUTURA`)")
    m3.add_argument("--antes_final", type=Path, default=None,
                    help="a final de quando a IA foi feita: o que mudou nela vem da entrada nova (`MUDOU`)")
    m2 = sub.add_parser("montar12k", help="a saída do Topaz (12K) -> os JPGs das opções A e B")
    m2.add_argument("saida_topaz", type=Path)
    m2.add_argument("--largura", type=int, default=None)
    a = ap.parse_args()
    if a.etapa == "preparar":
        preparar()
    elif a.etapa == "montar":
        montar(a.saida_ia)
    elif a.etapa == "corrigir":
        MUDOU["antes"] = a.antes_final
        ESTRUTURA["ligada"] = a.estrutura
        corrigir_ia(a.saida_ia, a.destino)
    else:
        montar_grande(a.saida_topaz, a.largura)

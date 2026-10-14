#!/usr/bin/env python3
"""Gera as bases das plantas humanizadas (POE 642 · Casa A) a partir dos PDFs de arquitetura.

Reescrito a partir da seção 5 do handoff (o script original não foi guardado):

  1. Remoção de texto: anotação de redação em todo texto + apply_redactions
     (sem apagar linhas nem imagens).
  2. Recorte: Rect(W*0.035, H*0.095, W*0.975, H*0.955), renderizado com 6000 px de largura.
  3. Parede x vidro a partir da layer ARQ_PAREDE:
     - preenchimento cinza 0.357 -> preto #111111;
     - formas finas com preenchimento branco e traços retos longos -> vidro;
     - folhas de porta junto a arcos ficam de fora;
     - traços que caem sobre parede ficam de fora (teste pelo ponto médio).
  4. Zonas excluídas da detecção de vidro, em coordenadas de uma visualização
     de 1800 px de largura (ver config_bases.json).
  5. Vidro final: cinza neutro #D6D6D3 com contorno preto de 2 px
     (scipy.ndimage.binary_dilation). Nunca azul.

Saídas (por pavimento):
  POE642_CasaA_BASE_<Pavimento>.png                    -> passos 1-2 (sem texto, cores do PDF)
  POE642_CasaA_BASE_<Pavimento>_v3_vidros_neutros.png  -> passos 1-5
  POE642_CasaA_BASE_<Pavimento>_debug.png              -> com --debug: conferência da detecção

Uso:
  python gerar_bases.py Terreo  caminho/planta.pdf
  python gerar_bases.py Subsolo caminho/planta.pdf --pagina 2 --debug
  python gerar_bases.py Terreo  caminho/planta.pdf --listar-layers

Dependências: pip install pymupdf numpy scipy pillow
"""

import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pymupdf
from PIL import Image, ImageDraw
from scipy import ndimage

PRETO_PAREDE = (0x11, 0x11, 0x11)
CINZA_VIDRO = (0xD6, 0xD6, 0xD3)
PRETO_CONTORNO = (0x00, 0x00, 0x00)

CONFIG_PADRAO = Path(__file__).with_name("config_bases.json")


# ----------------------------------------------------------------------------
# utilidades
# ----------------------------------------------------------------------------

def cor_igual(cor, alvo, tol):
    return cor is not None and len(cor) == len(alvo) and all(abs(a - b) <= tol for a, b in zip(cor, alvo))


def na_layer(desenho, layer):
    """Aceita o nome exato ou com prefixo de xref do AutoCAD (ex.: 'arquivo|ARQ_PAREDE')."""
    nome = desenho.get("layer") or ""
    return nome == layer or nome.endswith("|" + layer) or nome.endswith("$" + layer)


def pontos_do_item(item):
    tipo = item[0]
    if tipo == "l":
        return [item[1], item[2]]
    if tipo == "c":
        return [item[1], item[2], item[3], item[4]]
    if tipo == "re":
        r = item[1]
        return [r.tl, r.tr, r.br, r.bl]
    if tipo == "qu":
        q = item[1]
        return [q.ul, q.ur, q.lr, q.ll]
    return []


def tem_curva(desenho):
    return any(item[0] == "c" for item in desenho["items"])


def extremos_curvas(desenho):
    """Pontos inicial e final de cada curva de Bézier (arcos de porta)."""
    return [p for item in desenho["items"] if item[0] == "c" for p in (item[1], item[4])]


def replay(shape, desenho):
    """Redesenha os itens de um path do PDF numa Shape."""
    for item in desenho["items"]:
        tipo = item[0]
        if tipo == "l":
            shape.draw_line(item[1], item[2])
        elif tipo == "c":
            shape.draw_bezier(item[1], item[2], item[3], item[4])
        elif tipo == "re":
            shape.draw_rect(item[1])
        elif tipo == "qu":
            shape.draw_quad(item[1])


class Raster:
    """Converte coordenadas do PDF para pixels da base final (recorte + zoom + rotação)."""

    def __init__(self, page, recorte, largura_px, rotacao):
        W, H = page.rect.width, page.rect.height
        fx0, fy0, fx1, fy1 = recorte
        self.page_rect = page.rect
        self.clip = pymupdf.Rect(W * fx0, H * fy0, W * fx1, H * fy1)
        self.zoom = largura_px / self.clip.width
        self.matrix = pymupdf.Matrix(self.zoom, self.zoom)
        self.rotacao = rotacao % 360
        self.tamanho = None  # (w, h) da imagem antes da rotação; definido em render()

    def render(self, page):
        pix = page.get_pixmap(matrix=self.matrix, clip=self.clip, alpha=False)
        self.tamanho = (pix.width, pix.height)
        return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

    def mascara(self, desenhos, modo, largura_min_pt=0.0):
        """Rasteriza só os desenhos dados numa página em branco, alinhada à base.

        modo='fill'   -> preenche os paths (paredes, formas de vidro)
        modo='stroke' -> traça os paths com largura >= largura_min_pt (traços de vidro)
        """
        doc = pymupdf.open()
        pg = doc.new_page(width=self.page_rect.width, height=self.page_rect.height)
        for d in desenhos:
            sh = pg.new_shape()
            replay(sh, d)
            if modo == "fill":
                sh.finish(color=None, fill=(0, 0, 0), even_odd=d.get("even_odd", False), closePath=True)
            else:
                largura = max(d.get("width") or 0, largura_min_pt)
                sh.finish(color=(0, 0, 0), fill=None, width=largura, closePath=False)
            sh.commit()
        pix = pg.get_pixmap(matrix=self.matrix, clip=self.clip, alpha=False, colorspace=pymupdf.csGRAY)
        arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
        return arr < 128

    def para_px(self, ponto):
        """Ponto do PDF -> pixel (x, y) antes da rotação."""
        return ((ponto.x - self.clip.x0) * self.zoom, (ponto.y - self.clip.y0) * self.zoom)

    def rotacionar_px(self, x, y):
        """Pixel antes da rotação -> pixel na imagem final rotacionada."""
        w, h = self.tamanho
        if self.rotacao == 0:
            return x, y
        if self.rotacao == 180:
            return w - x, h - y
        if self.rotacao == 90:  # PIL rotate(-90) = horário
            return h - y, x
        if self.rotacao == 270:
            return y, w - x
        raise ValueError("rotação precisa ser 0, 90, 180 ou 270")

    def rotacionar_img(self, img):
        if self.rotacao == 0:
            return img
        return img.rotate(-self.rotacao, expand=True)

    def rotacionar_arr(self, arr):
        return np.rot90(arr, k=-(self.rotacao // 90)) if self.rotacao else arr


# ----------------------------------------------------------------------------
# passos do pipeline
# ----------------------------------------------------------------------------

def remover_texto(page):
    """Passo 1: redação de todo texto, preservando linhas e imagens."""
    palavras = page.get_text("words")
    for x0, y0, x1, y1, *_ in palavras:
        page.add_redact_annot(pymupdf.Rect(x0, y0, x1, y1), fill=False)
    if palavras:
        page.apply_redactions(
            images=pymupdf.PDF_REDACT_IMAGE_NONE,
            graphics=pymupdf.PDF_REDACT_LINE_ART_NONE,
            text=pymupdf.PDF_REDACT_TEXT_REMOVE,
        )
    return len(palavras)


def ocultar_layers(doc, nomes):
    """Desliga layers (OCGs) inteiras antes do render. Útil quando o texto do CAD vem
    vetorizado (fonte SHX em linhas) e a redação não o encontra: cotas, legendas etc."""
    if not nomes:
        return []
    alvo = set(nomes)
    desligadas = []
    # layer_ui_configs é o que o MuPDF respeita no render (set_layer sozinho não basta)
    for c in doc.layer_ui_configs():
        nome = c["text"]
        if nome in alvo or nome.split("|")[-1] in alvo or nome.split("$")[-1] in alvo:
            doc.set_layer_ui_config(c["number"], 2)
            desligadas.append(nome)
    faltando = alvo - {n.split("|")[-1].split("$")[-1] for n in desligadas} - set(desligadas)
    if faltando:
        print(f"    layers não encontradas no PDF: {sorted(faltando)}")
    return desligadas


def ocultar_em_zonas(doc, page, raster, img, regras, cfg):
    """Passo 3c: desliga layers só dentro de retângulos da visualização de 1800 px.

    No Subsolo, as projeções (DOC_LINHAS E PROJEÇÕES) dentro do depósito e junto à parede
    da academia viraram sauna e banco no render. Os X do elevador e dos shafts estão na
    mesma layer e precisam ficar, por isso a layer só some nessas zonas.
    """
    arr = np.array(img)
    w, h = raster.tamanho
    largura_final = w if raster.rotacao in (0, 180) else h
    esc = largura_final / cfg["largura_visualizacao"]
    resumo = []
    for nome, caixas in regras.items():
        nums = [c["number"] for c in doc.layer_ui_configs()
                if nome in (c["text"], c["text"].split("|")[-1], c["text"].split("$")[-1])]
        if not nums:
            resumo.append(f"{nome}: layer não encontrada")
            continue
        for n in nums:
            doc.set_layer_ui_config(n, 2)
        sem = np.array(raster.render(page))
        for n in nums:
            doc.set_layer_ui_config(n, 0)
        mask = np.zeros(raster.rotacionar_arr(arr[..., 0]).shape, bool)
        for x0, y0, x1, y1 in caixas:
            mask[int(y0 * esc):int(np.ceil(y1 * esc)), int(x0 * esc):int(np.ceil(x1 * esc))] = True
        # as zonas são medidas na base final; volta para a orientação de antes da rotação
        if raster.rotacao:
            mask = np.rot90(mask, k=raster.rotacao // 90)
        arr[mask] = sem[mask]
        resumo.append(f"{nome}: {len(caixas)} zona(s)")
    return Image.fromarray(arr), resumo


def classificar(page, raster, cfg, zonas, faixas_y, eixo_janela_max_pt=None):
    """Passos 3-4: separa paredes, vidros e descartes a partir da layer de parede.

    eixo_janela_max_pt: descarta o traço curto que atravessa uma janelinha de banho (o eixo do
    bloco do CAD). Como vidro, ele vira um '+' na parede, e o motor desenha ali um registro ou
    um chuveiro de parede.
    """
    layer = cfg["layer_parede"]
    tol = cfg["tolerancia_cor"]
    cinza = (cfg["cinza_parede"],) * 3
    v = cfg["vidro"]
    escala_vis = cfg["largura_visualizacao"] / raster.tamanho[0] if raster.rotacao in (0, 180) \
        else cfg["largura_visualizacao"] / raster.tamanho[1]

    desenhos = page.get_drawings()
    da_layer = [d for d in desenhos if na_layer(d, layer)]
    if not da_layer:
        return None

    # o cinza de parede também aparece fora da ARQ_PAREDE (ex.: parede de cima do estar no Térreo);
    # deixar esse cinza na base faz o motor ler a parede como faixa de vidro
    origem = desenhos if cfg.get("cinza_parede_qualquer_layer", True) else da_layer
    paredes = [d for d in origem if cor_igual(d.get("fill"), cinza, tol)]
    mask_parede = raster.mascara(paredes, "fill") if paredes else np.zeros(raster.tamanho[::-1], bool)
    mask_parede_teste = ndimage.binary_dilation(mask_parede, iterations=1)

    # arcos de porta: qualquer curva da página (a folha pode estar em outra layer que o arco)
    arcos = []
    for d in desenhos:
        if tem_curva(d):
            r = d["rect"]
            arcos.append((extremos_curvas(d), max(r.width, r.height)))

    def perto_de_arco(rect, comprimento):
        t = v["tolerancia_arco_pt"]
        caixa = pymupdf.Rect(rect) + (-t, -t, t, t)
        for extremos, raio in arcos:
            if raio <= 0:
                continue
            if abs(comprimento - raio) / raio <= v["tolerancia_raio"] and any(caixa.contains(p) for p in extremos):
                return True
        return False

    def sobre_parede(ponto):
        x, y = raster.para_px(ponto)
        xi, yi = int(round(x)), int(round(y))
        h, w = mask_parede_teste.shape
        return 0 <= xi < w and 0 <= yi < h and bool(mask_parede_teste[yi, xi])

    # vãos de janela: caixas brancas finas da layer de parede
    caixas_janela = []
    if eixo_janela_max_pt:
        for d in da_layer:
            r = d["rect"]
            if cor_igual(d.get("fill"), (1.0, 1.0, 1.0), tol) and min(r.width, r.height) <= 2 * v["espessura_max_pt"] \
                    and max(r.width, r.height) >= v["comprimento_min_pt"] * 0.8:
                caixas_janela.append(r)

    def eixo_de_janela(p1, p2, comp):
        if not eixo_janela_max_pt or comp > eixo_janela_max_pt:
            return False
        meio = pymupdf.Point((p1.x + p2.x) / 2, (p1.y + p2.y) / 2)
        horizontal = abs(p2.y - p1.y) < abs(p2.x - p1.x)
        for r in caixas_janela:
            # o eixo cruza a caixa pelo lado curto: caixa em pé com traço deitado, ou o contrário
            if (pymupdf.Rect(r) + (-0.6, -0.6, 0.6, 0.6)).contains(meio) and (r.height > r.width) == horizontal:
                return True
        return False

    def em_zona_excluida(ponto):
        x, y = raster.rotacionar_px(*raster.para_px(ponto))
        xv, yv = x * escala_vis, y * escala_vis
        for nome, (x0, y0, x1, y1) in zonas.items():
            if x0 <= xv <= x1 and y0 <= yv <= y1:
                return nome
        for y_min, y_max in faixas_y:
            if (y_min is None or yv >= y_min) and (y_max is None or yv < y_max):
                return "muros"
        return None

    vidros_forma, vidros_traco, descartes = [], [], []
    ids_parede = {id(d) for d in paredes}
    segmentos_vistos = set()  # paths fechados e exportações do CAD repetem o mesmo segmento

    for d in da_layer:
        if id(d) in ids_parede:
            continue
        r = d["rect"]
        fill = d.get("fill")

        # (a) formas finas com preenchimento branco
        if cor_igual(fill, (1.0, 1.0, 1.0), tol):
            fino, longo = min(r.width, r.height), max(r.width, r.height)
            if fino <= v["espessura_max_pt"] and longo >= v["comprimento_min_pt"] \
                    and longo >= v["razao_min"] * max(fino, 1e-3):
                centro = pymupdf.Point((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2)
                motivo = ("porta" if perto_de_arco(r, longo)
                          else "parede" if sobre_parede(centro)
                          else em_zona_excluida(centro))
                (descartes if motivo else vidros_forma).append((d, motivo, centro))
            continue

        # (b) traços retos longos (só linhas, sem curvas)
        if fill is None and d.get("color") is not None and not tem_curva(d):
            for item in d["items"]:
                if item[0] != "l":
                    continue
                p1, p2 = item[1], item[2]
                comp = math.dist((p1.x, p1.y), (p2.x, p2.y))
                if comp < v["comprimento_min_pt"]:
                    continue
                chave = tuple(sorted(((round(p1.x, 1), round(p1.y, 1)), (round(p2.x, 1), round(p2.y, 1)))))
                if chave in segmentos_vistos:
                    continue
                segmentos_vistos.add(chave)
                meio = pymupdf.Point((p1.x + p2.x) / 2, (p1.y + p2.y) / 2)
                seg = {"items": [item], "width": d.get("width") or 0, "rect": pymupdf.Rect(p1, p2).normalize()}
                motivo = ("porta" if perto_de_arco(seg["rect"], comp)
                          else "eixo de janela" if eixo_de_janela(p1, p2, comp)
                          else "parede" if sobre_parede(meio)
                          else em_zona_excluida(meio))
                (descartes if motivo else vidros_traco).append((seg, motivo, meio))

    return {
        "da_layer": da_layer,
        "paredes": paredes,
        "mask_parede": mask_parede,
        "vidros_forma": vidros_forma,
        "vidros_traco": vidros_traco,
        "descartes": descartes,
    }


def pintar_paredes_no_pdf(page, paredes):
    """Passo 3a: sobrepõe as paredes em #111111 no próprio vetor (bordas com antialias)."""
    cor = tuple(c / 255 for c in PRETO_PAREDE)
    for d in paredes:
        sh = page.new_shape()
        replay(sh, d)
        sh.finish(color=cor, fill=cor, width=d.get("width") or 0, even_odd=d.get("even_odd", False), closePath=True)
        sh.commit(overlay=True)


def reforcar_linhas(page, raster, regras):
    """Passo 3b: redesenha os traços de uma layer mais grossos e escuros.

    Projeções finas do CAD (ex.: pergolado em 0,21 pt cinza) somem na base de 6000 px
    e o motor não as enxerga. Ponta reta (lineCap 0) para o tracejado manter os vãos.
    """
    desenhos = page.get_drawings()
    resumo = []
    for regra in regras:
        sel = [d for d in desenhos if d["type"] in ("s", "fs") and na_layer(d, regra["layer"])]
        cor = tuple(int(c) / 255 for c in hex_rgb(regra["cor"]))
        largura = regra["largura_px"] / raster.zoom
        for d in sel:
            sh = page.new_shape()
            replay(sh, d)
            sh.finish(color=cor, fill=None, width=largura, lineCap=0, closePath=False)
            sh.commit(overlay=True)
        resumo.append(f"{regra['nome']}: {len(sel)} traços")
    return resumo


def compor_vidro(img, mask_vidro, contorno_px):
    """Passo 5: vidro cinza neutro com contorno preto por dilatação."""
    arr = np.array(img)
    contorno = ndimage.binary_dilation(mask_vidro, iterations=contorno_px) & ~mask_vidro
    arr[contorno] = PRETO_CONTORNO
    arr[mask_vidro] = CINZA_VIDRO
    return Image.fromarray(arr)


def hex_rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)])


def aplicar_legenda(img, page, raster, legenda, cfg):
    """Passo 6: deixa cada material numa cor única da legenda do prompt.

    - poligonos: preenchimentos do PDF (por layer e cor) que precisam de outra cor
      — ex.: acesso de veículos no mesmo cinza do deck;
    - trocas_cor: troca global de uma cor renderizada por outra;
    - hachuras: áreas sem preenchimento, só hachura sobre branco (deck de madeira),
      dentro de um retângulo da visualização de 1800 px;
    - gramados: o branco do entorno que chega à borda do lote vira grama;
    - setas: linha de caminhamento com seta (sentido de descida), em vis.
    Só pixels com a cor de origem mudam: linhas, móveis e símbolos ficam intactos.
    """
    arr = np.array(img).astype(int)
    tol = legenda.get("tolerancia_px", 10)
    esc = img.width / cfg["largura_visualizacao"]
    desenhos = page.get_drawings()
    resumo = []

    for regra in legenda.get("poligonos", []):
        alvo = tuple(regra["preenchimento_pdf"])
        sel = [d for d in desenhos
               if cor_igual(d.get("fill"), alvo, cfg["tolerancia_cor"]) and na_layer(d, regra["layer"])]
        if "bbox_vis" in regra:
            x0, y0, x1, y1 = regra["bbox_vis"]

            def dentro(d):
                c = pymupdf.Point((d["rect"].x0 + d["rect"].x1) / 2, (d["rect"].y0 + d["rect"].y1) / 2)
                x, y = raster.rotacionar_px(*raster.para_px(c))
                return x0 <= x / esc <= x1 and y0 <= y / esc <= y1
            sel = [d for d in sel if dentro(d)]
        if not sel:
            resumo.append(f"{regra['nome']}: nenhum polígono")
            continue
        mask = raster.rotacionar_arr(raster.mascara(sel, "fill"))
        if regra.get("proteger_layers"):
            # o que estas layers desenham dentro do polígono não muda (paredes, vidros, bordas, degraus);
            # traço com folga para cobrir o vidro alargado e o contorno preto do passo 5
            area = pymupdf.Rect(sel[0]["rect"])
            for d in sel[1:]:
                area |= d["rect"]
            prot = [d for d in desenhos if d["rect"].intersects(area)
                    and any(na_layer(d, nome) for nome in regra["proteger_layers"])]
            folga_pt = (cfg["vidro"]["largura_min_px"] + 2 * cfg["vidro"]["contorno_px"]) / raster.zoom
            mp = raster.mascara([d for d in prot if d.get("fill") is not None], "fill") \
                | raster.mascara([d for d in prot if d["type"] in ("s", "fs")], "stroke", folga_pt)
            mask &= ~raster.rotacionar_arr(mp)
        if regra.get("modo") == "neutros":
            # área sem preenchimento colorido: branco vira 'para' e os símbolos cinza (ex.: o
            # pontilhado de jardim) viram 'cor_linha'; cores com matiz (degraus, madeira) ficam
            neutro = (arr.max(axis=-1) - arr.min(axis=-1)) <= 8
            claro = arr.min(axis=-1)
            m = mask & neutro & (claro >= 235)
            arr[m] = hex_rgb(regra["para"])
            ms = mask & neutro & (claro >= regra.get("limiar_simbolo", 150)) & (claro < 235)
            arr[ms] = hex_rgb(regra.get("cor_linha", regra["para"]))
            m |= ms
        else:
            m = mask & (np.abs(arr - hex_rgb(regra["cor_render"])).max(axis=-1) <= tol)
            if regra.get("cor_linha"):
                # as linhas cinza dentro do polígono (ex.: réguas do deck, hexágonos do acesso de carros)
                # também mudam; com 'cor_linha' igual a 'para', elas somem no material
                neutro = (arr.max(axis=-1) - arr.min(axis=-1)) <= 8
                ml = mask & ~m & neutro & (arr.min(axis=-1) >= 60) & (arr.min(axis=-1) < 235)
                arr[ml] = hex_rgb(regra["cor_linha"])
            arr[m] = hex_rgb(regra["para"])
        resumo.append(f"{regra['nome']}: {len(sel)} polígono(s), {int(m.sum())} px")

    for de, para in legenda.get("trocas_cor", []):
        m = np.abs(arr - hex_rgb(de)).max(axis=-1) <= tol
        arr[m] = hex_rgb(para)
        resumo.append(f"{de}→{para}: {int(m.sum())} px")

    # a detecção usa sempre o desenho original: retângulos vizinhos não podem enxergar
    # a pintura um do outro (isso deixava uma faixa branca na emenda)
    original = arr.copy()
    for h in legenda.get("hachuras", []):
        x0, y0, x1, y1 = (int(round(v * esc)) for v in h["bbox_vis"])
        orig = original[y0:y1, x0:x1]
        sub = arr[y0:y1, x0:x1]
        neutro = (orig.max(axis=-1) - orig.min(axis=-1)) <= 6
        linhas = neutro & (orig.min(axis=-1) < h.get("limiar_linha", 230))
        vao = max(3, int(round(h["vao_vis"] * esc)))
        # hachura horizontal (deck) fecha na vertical; linhas verticais (degraus) fecham na horizontal
        kernel = np.ones((1, vao)) if h.get("linhas") == "verticais" else np.ones((vao, 1))
        # margem replicada para o fechamento não corroer as bordas do retângulo
        pad = vao + 2
        regiao = ndimage.binary_closing(np.pad(linhas, pad, mode="edge"), structure=kernel)[pad:-pad, pad:-pad]
        regiao = ndimage.binary_fill_holes(regiao)
        regiao = ndimage.binary_opening(regiao, structure=np.ones((3, 3)))
        m = regiao & (orig.min(axis=-1) >= 235)
        sub[m] = hex_rgb(h["para"])
        if h.get("cor_linha"):
            sub[regiao & linhas] = hex_rgb(h["cor_linha"])
        resumo.append(f"{h['nome']}: {int(m.sum())} px")

    # retângulo exato pintado por inteiro, com só as linhas de uma layer por cima
    # (ex.: escada do Subsolo, onde a hachura do deck invade os últimos degraus)
    for r in legenda.get("retangulos", []):
        x0, y0, x1, y1 = (int(round(v * esc)) for v in r["bbox_vis"])
        if r.get("so_cores"):
            # só as cores listadas viram 'para' (ex.: na Casa B, o malva da garagem, que no PDF está
            # no mesmo polígono da circulação); com 'cor_linha', as linhas cinza do retângulo também mudam
            bloco = arr[y0:y1, x0:x1]
            orig = bloco.copy()
            alvo = np.zeros(orig.shape[:2], bool)
            for cor in r["so_cores"]:
                alvo |= np.abs(orig - hex_rgb(cor)).max(axis=-1) <= tol
            bloco[alvo] = hex_rgb(r["para"])
            if r.get("cor_linha"):
                neutro = (orig.max(axis=-1) - orig.min(axis=-1)) <= 8
                bloco[neutro & ~alvo & (orig.min(axis=-1) >= 60) & (orig.min(axis=-1) < 235)] = hex_rgb(r["cor_linha"])
            resumo.append(f"{r['nome']}: {int(alvo.sum())} px")
            continue
        if r.get("so_branco"):
            # só o branco vira 'para' e as linhas cinza viram 'cor_linha' (ex.: vazios do
            # 1º Pavimento em cinza-escuro com o X tracejado claro); paredes pretas ficam
            bloco = arr[y0:y1, x0:x1]
            orig = bloco.copy()
            neutro = (orig.max(axis=-1) - orig.min(axis=-1)) <= 8
            branco = neutro & (orig.min(axis=-1) >= 235)
            bloco[branco] = hex_rgb(r["para"])
            if r.get("cor_linha"):
                bloco[neutro & (orig.min(axis=-1) >= 60) & (orig.min(axis=-1) < 235)] = hex_rgb(r["cor_linha"])
            resumo.append(f"{r['nome']}: {int(branco.sum())} px")
            continue
        arr[y0:y1, x0:x1] = hex_rgb(r["para"])
        if r.get("linhas_layer"):
            ds = [d for d in desenhos if na_layer(d, r["linhas_layer"]) and d["type"] in ("s", "fs")]
            if r.get("sem_linhas_bbox_vis"):
                # traços que não voltam (ex.: na Casa B, a ponta de seta e o círculo da linha de
                # caminhamento que contradizem o sentido da descida)
                def no_corte(d):
                    a = raster.rotacionar_px(*raster.para_px(d["rect"].tl))
                    b = raster.rotacionar_px(*raster.para_px(d["rect"].br))
                    xs, ys = sorted((a[0] / esc, b[0] / esc)), sorted((a[1] / esc, b[1] / esc))
                    return any(bx0 <= xs[0] and xs[1] <= bx1 and by0 <= ys[0] and ys[1] <= by1
                               for bx0, by0, bx1, by1 in r["sem_linhas_bbox_vis"])
                ds = [d for d in ds if not no_corte(d)]
            mk = raster.rotacionar_arr(raster.mascara(ds, "stroke", r.get("largura_linha_px", 2) / raster.zoom))
            bloco = arr[y0:y1, x0:x1]
            bloco[mk[y0:y1, x0:x1]] = hex_rgb(r.get("cor_linha", "#111111"))
        resumo.append(f"{r['nome']}: {(x1 - x0) * (y1 - y0)} px")

    # um quarto de círculo (ex.: o trecho da escada caracol que chega a este piso)
    for s in legenda.get("setores", []):
        m = quarto_de_circulo(arr.shape[:2], s["centro_vis"], s["raio_vis"], s["quadrante"], esc)
        linhas = m & (arr.min(axis=-1) < 200)
        arr[m & ~linhas] = hex_rgb(s["para"])
        if s.get("cor_linha"):
            arr[linhas] = hex_rgb(s["cor_linha"])
        resumo.append(f"{s['nome']}: {int(m.sum())} px")

    # linha de caminhamento com seta, quando o PDF não traz ou traz no sentido errado (ex.: na Casa C,
    # os degraus largos descem para o pátio): pontos em vis, a seta no último ponto, círculo no primeiro
    if legenda.get("setas"):
        im = Image.fromarray(arr.astype(np.uint8))
        d = ImageDraw.Draw(im)
        for st in legenda["setas"]:
            pts = [(x * esc, y * esc) for x, y in st["pontos_vis"]]
            cor = tuple(int(v) for v in hex_rgb(st.get("cor", "#5E5A52")))
            lw = max(1, round(st.get("largura_vis", 0.6) * esc))
            d.line(pts, fill=cor, width=lw)
            (xa, ya), (xb, yb) = pts[-2], pts[-1]
            ang = math.atan2(yb - ya, xb - xa)
            tam = st.get("ponta_vis", 7.0) * esc
            for lado in (-1, 1):
                a2 = ang + math.pi - lado * math.radians(st.get("abertura_graus", 28))
                d.line([(xb, yb), (xb + tam * math.cos(a2), yb + tam * math.sin(a2))], fill=cor, width=lw)
            r0 = st.get("circulo_vis", 1.6) * esc
            x0_, y0_ = pts[0]
            d.ellipse((x0_ - r0, y0_ - r0, x0_ + r0, y0_ + r0), outline=cor, width=lw)
            resumo.append(f"{st['nome']}: seta com {len(pts)} pontos")
        arr = np.array(im).astype(int)

    # gramado: o branco que chega até a borda do lote (o entorno), sem o branco fechado dentro da casa
    for g in legenda.get("gramados", []):
        x0, y0, x1, y1 = (int(round(v * esc)) for v in g["bbox_vis"])
        sub = arr[y0:y1, x0:x1]
        neutro = (sub.max(axis=-1) - sub.min(axis=-1)) <= 8
        branco = neutro & (sub.min(axis=-1) >= 235)
        lab, _ = ndimage.label(branco)
        borda = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
        m = np.isin(lab, borda[borda > 0])
        # o halo claro das linhas que cruzam o gramado (antisserrilhado) também vira grama
        halo = ndimage.binary_dilation(m, iterations=2) & ~m & neutro & (sub.min(axis=-1) >= 200)
        sub[m | halo] = hex_rgb(g["para"])
        resumo.append(f"{g['nome']}: {int((m | halo).sum())} px")

    return Image.fromarray(arr.astype(np.uint8)), resumo


def quarto_de_circulo(forma, centro_vis, raio_vis, quadrante, esc):
    """Máscara de um quarto de disco; quadrante = sup_dir, sup_esq, inf_dir ou inf_esq
    (na imagem, 'sup' é para cima). Sem quadrante, o disco inteiro."""
    h, w = forma
    cx, cy, r = centro_vis[0] * esc, centro_vis[1] * esc, raio_vis * esc
    yy, xx = np.ogrid[:h, :w]
    disco = (xx - cx) ** 2 + (yy - cy) ** 2 <= r ** 2
    if quadrante is None:
        return disco
    lado_x = (xx >= cx) if quadrante.endswith("dir") else (xx <= cx)
    lado_y = (yy <= cy) if quadrante.startswith("sup") else (yy >= cy)
    return disco & lado_x & lado_y


def esmaecer(img, regra, cfg):
    """Passo 7: clareia tudo fora dos retângulos 'manter_bbox_vis' (entorno esmaecido).

    clarear = 0 não muda nada; 1 vira branco. Ex.: no Subsolo, o que é do Térreo
    (deck, escadas, deck da piscina) e o pátio ficam claros; o subsolo, a piscina e o
    ofurô ficam com a cor cheia.
    """
    arr = np.array(img).astype(float)
    esc = img.width / cfg["largura_visualizacao"]
    manter = np.zeros(arr.shape[:2], bool)
    for x0, y0, x1, y1 in regra["manter_bbox_vis"]:
        manter[int(y0 * esc):int(np.ceil(y1 * esc)), int(x0 * esc):int(np.ceil(x1 * esc))] = True
    fora = ~manter
    clarear = regra.get("clarear", 0.5)
    # círculos que clareiam mesmo dentro das áreas mantidas, menos um quarto
    # (ex.: escada caracol do 1º Pavimento, onde só o trecho deste piso fica cheio);
    # cada círculo pode ter o próprio 'clarear'
    discos = []
    for c in regra.get("clarear_circulos", []):
        disco = quarto_de_circulo(arr.shape[:2], c["centro_vis"], c["raio_vis"], None, esc)
        if c.get("exceto_quadrante"):
            disco &= ~quarto_de_circulo(arr.shape[:2], c["centro_vis"], c["raio_vis"], c["exceto_quadrante"], esc)
        discos.append((disco, c.get("clarear", clarear)))
        fora &= ~disco
    arr[fora] += (255 - arr[fora]) * clarear
    total = int(fora.sum())
    for disco, k in discos:
        arr[disco] += (255 - arr[disco]) * k
        total += int(disco.sum())
    return Image.fromarray(arr.round().astype(np.uint8)), total


def em_16x9(img):
    """Centraliza a base numa tela branca 16:9, para o motor não precisar reenquadrar
    (a base sai ~1,545:1 e a saída do Higgsfield é 16:9)."""
    w, h = img.size
    if w / h < 16 / 9:
        nw, nh = round(h * 16 / 9), h
    else:
        nw, nh = w, round(w * 9 / 16)
    tela = Image.new("RGB", (nw, nh), (255, 255, 255))
    tela.paste(img, ((nw - w) // 2, (nh - h) // 2))
    return tela


def salvar_debug(img_final, raster, res, zonas, faixas_y, cfg, caminho):
    """Prévia de 1800 px: vidro aceito em vermelho, descartes coloridos, zonas em magenta."""
    largura = cfg["largura_visualizacao"]
    esc = largura / img_final.width
    prev = img_final.convert("RGB").resize((largura, round(img_final.height * esc)), Image.LANCZOS)
    dr = ImageDraw.Draw(prev)
    cores = {"porta": (255, 140, 0), "parede": (0, 120, 255), "muros": (160, 0, 160),
             "eixo de janela": (0, 170, 80)}
    for nome, (x0, y0, x1, y1) in zonas.items():
        dr.rectangle((x0, y0, x1, y1), outline=(220, 0, 220), width=2)
        dr.text((x0 + 3, y0 + 2), nome, fill=(220, 0, 220))
    for y_min, y_max in faixas_y:
        y = y_max if y_min is None else y_min
        dr.line((0, y, largura, y), fill=(160, 0, 160), width=1)

    def marcar(ponto, cor, r=4):
        x, y = raster.rotacionar_px(*raster.para_px(ponto))
        x, y = x * esc, y * esc
        dr.ellipse((x - r, y - r, x + r, y + r), outline=cor, width=2)

    for _, _, p in res["vidros_forma"] + res["vidros_traco"]:
        marcar(p, (230, 0, 0))
    for _, motivo, p in res["descartes"]:
        marcar(p, cores.get(motivo, (220, 0, 220)), r=3)
    prev.save(caminho)


def listar_layers(page):
    desenhos = page.get_drawings()
    cont = Counter()
    for d in desenhos:
        f = d.get("fill")
        cont[(d.get("layer") or "(sem layer)", tuple(round(c, 3) for c in f) if f else None)] += 1
    print(f"{len(desenhos)} desenhos | {len(page.get_text('words'))} palavras de texto")
    print("layer | preenchimento | quantidade")
    for (layer, fill), n in sorted(cont.items(), key=lambda kv: (-kv[1], kv[0][0])):
        print(f"  {layer} | {fill} | {n}")


# ----------------------------------------------------------------------------
# principal
# ----------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pavimento", help="chave em config_bases.json: Terreo, 1Pavimento ou Subsolo")
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--pagina", type=int, help="página do PDF (0 = primeira); sobrescreve a config")
    ap.add_argument("--rotacao", type=int, choices=(0, 90, 180, 270), help="sobrescreve a config")
    ap.add_argument("--saida", type=Path, default=Path("."), help="pasta de saída")
    ap.add_argument("--config", type=Path, default=CONFIG_PADRAO)
    ap.add_argument("--ocultar", nargs="*", default=None, metavar="LAYER",
                    help="layers a desligar antes do render (soma-se a 'layers_ocultas' da config)")
    ap.add_argument("--debug", action="store_true", help="salva a prévia de conferência da detecção")
    ap.add_argument("--listar-layers", action="store_true", help="só diagnostica layers e preenchimentos")
    args = ap.parse_args(argv)

    cfg = json.loads(args.config.read_text(encoding="utf-8"))
    if args.pavimento not in cfg["pavimentos"]:
        sys.exit(f"Pavimento '{args.pavimento}' não está em {args.config.name}: {list(cfg['pavimentos'])}")
    pav = cfg["pavimentos"][args.pavimento]
    pagina = args.pagina if args.pagina is not None else pav.get("pagina", 0)
    rotacao = args.rotacao if args.rotacao is not None else pav.get("rotacao", 0)
    # zona = [x0, y0, x1, y1] (só sai da detecção de vidro) ou {"bbox": [...], "pintar": "#hex"}
    # (sai do vidro e é pintada nessa cor — ex.: lâminas de brise em alumínio escuro)
    zonas_cfg = pav.get("zonas_excluidas", {})
    zonas = {n: (v["bbox"] if isinstance(v, dict) else v) for n, v in zonas_cfg.items()}
    cores_zona = {n: v["pintar"] for n, v in zonas_cfg.items() if isinstance(v, dict) and v.get("pintar")}
    faixas_y = pav.get("faixas_y_excluidas", [])

    doc = pymupdf.open(args.pdf)
    page = doc[pagina]

    if args.listar_layers:
        listar_layers(page)
        return 0

    args.saida.mkdir(parents=True, exist_ok=True)
    prefixo = args.saida / f"{cfg.get('prefixo', 'POE642_CasaA')}_BASE_{args.pavimento}"

    # 1. texto (real, por redação) + layers desligadas (texto vetorizado do CAD)
    n_txt = remover_texto(page)
    print(f"[1] texto removido: {n_txt} palavras")
    ocultas = ocultar_layers(doc, cfg.get("layers_ocultas", []) + pav.get("layers_ocultas", []) + (args.ocultar or []))
    if ocultas:
        print(f"    layers desligadas: {ocultas}")

    # 2. recorte + render da base sem texto
    raster = Raster(page, cfg["recorte"], cfg["largura_px"], rotacao)
    base = raster.render(page)
    raster.rotacionar_img(base).save(f"{prefixo}.png")
    print(f"[2] {prefixo}.png  ({raster.rotacionar_img(base).size[0]}x{raster.rotacionar_img(base).size[1]})")

    # 3-4. parede x vidro
    res = classificar(page, raster, cfg, zonas, faixas_y, pav.get("eixo_janela_max_pt"))
    if res is None:
        print(f"[3] ATENÇÃO: nenhuma geometria na layer '{cfg['layer_parede']}'. "
              f"Rode com --listar-layers para ver as layers deste PDF; a base v3 não foi gerada.")
        return 2
    print(f"[3] layer {cfg['layer_parede']}: {len(res['da_layer'])} desenhos | paredes {len(res['paredes'])} | "
          f"vidro (formas) {len(res['vidros_forma'])} | vidro (traços) {len(res['vidros_traco'])}")
    motivos = Counter(m for _, m, _ in res["descartes"])
    print(f"[4] descartados: {dict(motivos) or 'nenhum'}")

    pintar_paredes_no_pdf(page, res["paredes"])
    if pav.get("reforcar_linhas"):
        print(f"    linhas reforçadas: {' | '.join(reforcar_linhas(page, raster, pav['reforcar_linhas']))}")
    img = raster.render(page)
    if pav.get("ocultar_layers_zonas"):
        img, resumo = ocultar_em_zonas(doc, page, raster, img, pav["ocultar_layers_zonas"], cfg)
        print(f"    layers desligadas por zona: {' | '.join(resumo)}")

    largura_min_pt = cfg["vidro"]["largura_min_px"] / raster.zoom
    mask_vidro = np.zeros(raster.tamanho[::-1], bool)
    if res["vidros_forma"]:
        mask_vidro |= raster.mascara([d for d, _, _ in res["vidros_forma"]], "fill")
        mask_vidro |= raster.mascara([d for d, _, _ in res["vidros_forma"]], "stroke", largura_min_pt)
    if res["vidros_traco"]:
        mask_vidro |= raster.mascara([d for d, _, _ in res["vidros_traco"]], "stroke", largura_min_pt)
    mask_vidro &= ~res["mask_parede"]

    # 5. vidro neutro
    final = compor_vidro(img, mask_vidro, cfg["vidro"]["contorno_px"])

    pintados = [(d, cores_zona[m]) for d, m, _ in res["descartes"] if m in cores_zona]
    if pintados:
        arr = np.array(final)
        for cor in sorted({c for _, c in pintados}):
            ds = [d for d, c in pintados if c == cor]
            mk = raster.mascara(ds, "fill") | raster.mascara(ds, "stroke", largura_min_pt)
            arr[mk & ~res["mask_parede"]] = hex_rgb(cor)
        final = Image.fromarray(arr)
        print(f"    pintados por zona: {dict(Counter(c for _, c in pintados))}")

    final = raster.rotacionar_img(final)
    if pav.get("legenda"):
        final, resumo = aplicar_legenda(final, page, raster, pav["legenda"], cfg)
        print(f"[6] legenda de cores: {' | '.join(resumo)}")
    if pav.get("esmaecer"):
        final, n_px = esmaecer(final, pav["esmaecer"], cfg)
        print(f"[7] entorno esmaecido: {n_px} px clareados")
    final.save(f"{prefixo}_v3_vidros_neutros.png")
    print(f"[5] {prefixo}_v3_vidros_neutros.png  ({final.size[0]}x{final.size[1]})")

    if cfg.get("saida_16x9"):
        tela = em_16x9(final)
        tela.save(f"{prefixo}_v3_vidros_neutros_16x9.png")
        print(f"    {prefixo}_v3_vidros_neutros_16x9.png  ({tela.size[0]}x{tela.size[1]}, margem branca)")

    if args.debug:
        salvar_debug(final, raster, res, zonas, faixas_y, cfg, f"{prefixo}_debug.png")
        print(f"    {prefixo}_debug.png  (vermelho = vidro | laranja = porta | azul = sobre parede | "
              f"magenta = zona excluída)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

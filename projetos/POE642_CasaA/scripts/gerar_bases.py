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


def classificar(page, raster, cfg, zonas, faixas_y):
    """Passos 3-4: separa paredes, vidros e descartes a partir da layer de parede."""
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


def compor_vidro(img, mask_vidro, contorno_px):
    """Passo 5: vidro cinza neutro com contorno preto por dilatação."""
    arr = np.array(img)
    contorno = ndimage.binary_dilation(mask_vidro, iterations=contorno_px) & ~mask_vidro
    arr[contorno] = PRETO_CONTORNO
    arr[mask_vidro] = CINZA_VIDRO
    return Image.fromarray(arr)


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
    cores = {"porta": (255, 140, 0), "parede": (0, 120, 255), "muros": (160, 0, 160)}
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
    zonas = pav.get("zonas_excluidas", {})
    faixas_y = pav.get("faixas_y_excluidas", [])

    doc = pymupdf.open(args.pdf)
    page = doc[pagina]

    if args.listar_layers:
        listar_layers(page)
        return 0

    args.saida.mkdir(parents=True, exist_ok=True)
    prefixo = args.saida / f"POE642_CasaA_BASE_{args.pavimento}"

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
    res = classificar(page, raster, cfg, zonas, faixas_y)
    if res is None:
        print(f"[3] ATENÇÃO: nenhuma geometria na layer '{cfg['layer_parede']}'. "
              f"Rode com --listar-layers para ver as layers deste PDF; a base v3 não foi gerada.")
        return 2
    print(f"[3] layer {cfg['layer_parede']}: {len(res['da_layer'])} desenhos | paredes {len(res['paredes'])} | "
          f"vidro (formas) {len(res['vidros_forma'])} | vidro (traços) {len(res['vidros_traco'])}")
    motivos = Counter(m for _, m, _ in res["descartes"])
    print(f"[4] descartados: {dict(motivos) or 'nenhum'}")

    pintar_paredes_no_pdf(page, res["paredes"])
    img = raster.render(page)

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
    final = raster.rotacionar_img(final)
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

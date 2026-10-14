#!/usr/bin/env python3
"""Acabamentos finais, sem IA, na imagem que sai do elementos_do_render.py.

Onde o render não trouxe um objeto para trocar, a imagem final fica com o desenho do PDF.
Alguns desses desenhos são símbolos técnicos que não combinam com a planta humanizada. Este
script troca esses símbolos por objetos desenhados vistos de cima, com precisão de pixel,
nas posições exatas do PDF:

1. 'clonar' apaga um símbolo copiando o mesmo piso de um trecho limpo ao lado (carimbo com
   borda suave e ajuste do tom médio pelo anel em volta).
2. 'parede' refaz um trecho de parede repetindo uma linha limpa da mesma parede.
3. 'arestas_banco' troca a linha dupla entre dois degraus de um banco por uma aresta fina,
   no mesmo traço da aresta da frente.
4. 'pintar' completa uma bancada branca com a cor da bancada; 'cubas' desenha uma cuba
   branca com torneira e válvula cromadas sobre o símbolo do PDF.
5. 'armarios' troca o retângulo branco com diagonal tracejada (armário no PDF) pelo tampo
   do armário visto de cima, na cor da marcenaria dos closets da Casa A, com o contorno na
   face que dá para o ambiente.
6. 'chuveiros' desenha chuveiro de parede (canopla, braço e ducha redonda) e registro,
   cromados, na parede e na posição do símbolo do PDF.

Os desenhos são feitos em 8x e reduzidos (antisserrilhado). A config fica em
config_bases.json, no pavimento, na chave 'acabamentos'; os números estão na prévia de
1800 px (vis), como nos outros scripts. Saída: o PNG final, a prévia em JPG e um PNG
transparente só com as alterações, para usar como camada no Photoshop.

Uso:
  python acabamentos_finais.py PAVIMENTO ENTRADA.png --config CONFIG.json --saida PASTA --nome NOME
"""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np

BASE_SEM_MARGEM = 6001
SS = 8                                   # superamostragem dos desenhos

# cromado e louça (BGR)
CROMO_ESCURO = (142, 146, 150)
CROMO = (200, 203, 206)
CROMO_CLARO = (238, 240, 242)
FACE_DUCHA = (214, 217, 220)
FURO = (160, 164, 168)
LOUCA = (246, 247, 247)
LOUCA_CONTORNO = (168, 170, 171)
BACIA_BORDA = (219, 221, 222)
BACIA_FUNDO = (238, 239, 239)


def hex_bgr(h):
    h = h.lstrip("#")
    return (int(h[4:6], 16), int(h[2:4], 16), int(h[0:2], 16))


class Folha:
    """Converte vis (prévia de 1800 px) em px da imagem 16:9."""

    def __init__(self, W, H, largura_vis):
        self.k = BASE_SEM_MARGEM / largura_vis * H / 3884
        self.margem = (W - BASE_SEM_MARGEM * H / 3884) / 2

    def x(self, v):
        return v * self.k + self.margem

    def y(self, v):
        return v * self.k

    def ret(self, b):
        x0, y0, x1, y1 = b
        return (int(round(self.x(x0))), int(round(self.y(y0))),
                int(round(self.x(x1))), int(round(self.y(y1))))


class Desenho:
    """Tela RGBA em 8x sobre uma janela da imagem; as coordenadas de entrada são vis."""

    def __init__(self, folha, bbox_vis, folga=2):
        self.f = folha
        x0, y0, x1, y1 = folha.ret(bbox_vis)
        self.x0, self.y0 = x0 - folga, y0 - folga
        self.w, self.h = x1 - x0 + 2 * folga, y1 - y0 + 2 * folga
        self.cor = np.zeros((self.h * SS, self.w * SS, 3), np.float32)
        self.alfa = np.zeros((self.h * SS, self.w * SS), np.float32)

    def p(self, xv, yv):
        return (int(round((self.f.x(xv) - self.x0) * SS)), int(round((self.f.y(yv) - self.y0) * SS)))

    def d(self, v):
        return max(1, int(round(v * self.f.k * SS)))

    def _pinta(self, forma, cor):
        m = forma > 0
        self.cor[m] = cor
        self.alfa[m] = 1.0

    def circulo(self, c, r, cor):
        forma = np.zeros(self.alfa.shape, np.uint8)
        cv2.circle(forma, self.p(*c), self.d(r), 255, -1, cv2.LINE_8)
        self._pinta(forma, cor)

    def linha(self, a, b, larg, cor):
        forma = np.zeros(self.alfa.shape, np.uint8)
        cv2.line(forma, self.p(*a), self.p(*b), 255, self.d(larg), cv2.LINE_8)
        self._pinta(forma, cor)

    def ret_arred(self, b, raio, cor):
        x0, y0 = self.p(b[0], b[1])
        x1, y1 = self.p(b[2], b[3])
        r = min(self.d(raio), (x1 - x0) // 2, (y1 - y0) // 2)
        forma = np.zeros(self.alfa.shape, np.uint8)
        cv2.rectangle(forma, (x0 + r, y0), (x1 - r, y1), 255, -1)
        cv2.rectangle(forma, (x0, y0 + r), (x1, y1 - r), 255, -1)
        for cx, cy in ((x0 + r, y0 + r), (x1 - r, y0 + r), (x0 + r, y1 - r), (x1 - r, y1 - r)):
            cv2.circle(forma, (cx, cy), r, 255, -1)
        self._pinta(forma, cor)

    def aplicar(self, out):
        cor = cv2.resize(self.cor * self.alfa[..., None], (self.w, self.h), interpolation=cv2.INTER_AREA)
        a = cv2.resize(self.alfa, (self.w, self.h), interpolation=cv2.INTER_AREA)
        cor = cor / np.maximum(a, 1e-6)[..., None]
        sl = (slice(self.y0, self.y0 + self.h), slice(self.x0, self.x0 + self.w))
        out[sl] = out[sl] * (1 - a[..., None]) + cor * a[..., None]


def lum(img):
    return img.mean(axis=-1)


def clonar(out, f, op):
    """Carimbo: copia o piso deslocado sobre o símbolo, com borda suave e o tom médio ajustado."""
    x0, y0, x1, y1 = f.ret(op["bbox_vis"])
    dx, dy = int(round(op["desloc_vis"][0] * f.k)), int(round(op["desloc_vis"][1] * f.k))
    alvo = out[y0:y1, x0:x1].copy()
    fonte = out[y0 + dy:y1 + dy, x0 + dx:x1 + dx].copy()
    if op.get("corrigir_tom", True):
        # anel em volta do retângulo, sem parede e sem símbolo (só o piso claro)
        a = 6
        anel_alvo = out[y0 - a:y1 + a, x0 - a:x1 + a].reshape(-1, 3)
        anel_fonte = out[y0 + dy - a:y1 + dy + a, x0 + dx - a:x1 + dx + a].reshape(-1, 3)
        dentro = np.zeros((y1 - y0 + 2 * a, x1 - x0 + 2 * a), bool)
        dentro[a:-a, a:-a] = True
        ok = (~dentro.ravel()) & (lum(anel_alvo) > 120) & (lum(anel_fonte) > 120) & (lum(anel_alvo) < 250)
        fonte += np.median(anel_alvo[ok], axis=0) - np.median(anel_fonte[ok], axis=0)
    # borda suave só nos lados do retângulo; a parede da fonte sai com corte seco
    m = np.ones((y1 - y0, x1 - x0), np.float32)
    suave = op.get("borda_px", 1.0)
    if suave:
        pad = int(3 * suave) + 1
        m = cv2.GaussianBlur(np.pad(m, pad, constant_values=0), (0, 0), suave)[pad:-pad, pad:-pad]
        m = np.clip(m * op.get("ganho", 1.6), 0, 1)   # ganho 1: degradê largo, para pisos com réguas
    if op.get("so_onde_fonte_clara", True):
        m[lum(fonte) < op.get("lum_fonte_min", 110)] = 0   # não leva parede da fonte para o alvo
    if op.get("so_onde_alvo_branco"):
        m[alvo.min(axis=2) < 235] = 0                     # só o branco (ex.: soleira), mantém os traços
    out[y0:y1, x0:x1] = alvo * (1 - m[..., None]) + fonte * m[..., None]
    print(f"    {op['nome']}: {x1 - x0}x{y1 - y0} px, deslocamento ({dx}, {dy}) px")


def parede(out, f, op):
    """Repete uma linha (ou coluna) limpa da mesma parede sobre o trecho sujo."""
    x0, y0, x1, y1 = f.ret(op["bbox_vis"])
    if "linha_limpa_vis" in op:                         # parede vertical: repete uma linha
        r = int(round(f.y(op["linha_limpa_vis"])))
        perfil = out[r, x0:x1].copy()
        m = lum(perfil) < op.get("lum_max", 90)          # só as colunas que são parede
        out[y0:y1, x0:x1][:, m] = perfil[m][None]
    else:                                               # parede horizontal: repete uma coluna
        c = int(round(f.x(op["coluna_limpa_vis"])))
        perfil = out[y0:y1, c].copy()
        m = lum(perfil) < op.get("lum_max", 90)
        out[y0:y1, x0:x1][m, :] = perfil[m][:, None]
    print(f"    {op['nome']}: {int(m.sum())} {'colunas' if 'linha_limpa_vis' in op else 'linhas'} de parede")


def aresta_banco(out, f, op):
    """Troca a linha dupla entre dois degraus por uma aresta de 1 px, como a da frente."""
    x0, x1 = int(round(f.x(op["x_vis"][0]))), int(round(f.x(op["x_vis"][1])))
    r0, ra, r1 = (int(round(f.y(v))) for v in (op["faixa_vis"][0], op["aresta_vis"], op["faixa_vis"][1]))
    d = int(round(op.get("desloc_vis", 3.0) * f.k))
    # cada metade da faixa vem do próprio degrau, deslocada na vertical (os veios do travertino
    # são verticais, então continuam através do remendo)
    out[r0:ra, x0:x1] = out[r0 - d:ra - d, x0:x1]
    out[ra:r1, x0:x1] = out[ra + d:r1 + d, x0:x1]
    piso = lum(out[ra, x0:x1]) > 110                    # não pinta a aresta em cima da parede
    out[ra, x0:x1][piso] = hex_bgr(op.get("cor", "#7B796C"))
    print(f"    {op['nome']}: faixa de {r1 - r0} px refeita, aresta na linha {ra}")


def pintar(out, f, op):
    """Pinta uma cor chapada com um pontilhado sutil, só onde a imagem é clara (bancadas brancas)."""
    x0, y0, x1, y1 = f.ret(op["bbox_vis"])
    bloco = out[y0:y1, x0:x1]
    m = bloco.min(axis=2) >= op.get("so_onde_clara", 235)
    ruido = np.random.default_rng(7).normal(0, 2.0, m.shape)[..., None]
    bloco[m] = (np.array(hex_bgr(op["cor"]), np.float32) + ruido)[m]
    print(f"    {op['nome']}: {int(m.sum())} px")


def armario(out, f, op):
    """Tampo do armário: cor chapada com pontilhado sutil e contorno nas faces livres."""
    x0, y0, x1, y1 = f.ret(op["bbox_vis"])
    bloco = out[y0:y1, x0:x1]
    ruido = np.random.default_rng(11).normal(0, 1.5, bloco.shape[:2])[..., None]
    bloco[:] = np.array(hex_bgr(op["cor"]), np.float32) + ruido
    contorno = np.array(hex_bgr(op["contorno"]), np.float32)
    lado = {"esquerda": (slice(None), slice(0, 2)), "direita": (slice(None), slice(-2, None)),
            "cima": (slice(0, 2), slice(None)), "baixo": (slice(-2, None), slice(None))}
    for face in op.get("faces_livres", []):
        bloco[lado[face]] = contorno
    print(f"    {op['nome']}: {x1 - x0}x{y1 - y0} px, contorno em {', '.join(op.get('faces_livres', []))}")


def cuba(out, f, op):
    aro = op["aro_vis"]
    dz = Desenho(f, aro, folga=4)
    dz.ret_arred(aro, op.get("raio_aro_vis", 1.6), LOUCA_CONTORNO)
    e = 0.12                                            # contorno fino da louça
    dz.ret_arred([aro[0] + e, aro[1] + e, aro[2] - e, aro[3] - e], op.get("raio_aro_vis", 1.6) - e, LOUCA)
    b = op["bacia_vis"]
    # bacia: borda um pouco mais escura indo para o fundo claro (concavidade, sem sombra)
    passos = 6
    for i in range(passos):
        t = i / (passos - 1)
        cor = tuple(BACIA_BORDA[c] * (1 - t) + BACIA_FUNDO[c] * t for c in range(3))
        ins = t * min(b[2] - b[0], b[3] - b[1]) * 0.22
        dz.ret_arred([b[0] + ins, b[1] + ins, b[2] - ins, b[3] - ins], max(0.4, op.get("raio_bacia_vis", 2.4) - ins), cor)
    rx, ry = op["valvula_vis"]
    dz.circulo((rx, ry), 0.62, CROMO_ESCURO)
    dz.circulo((rx, ry), 0.48, CROMO_CLARO)
    dz.circulo((rx, ry), 0.18, CROMO)
    t = op["torneira"]
    bx, by = t["base_vis"]
    dz.linha((bx, by), (t["alavanca_ate_x_vis"], by), 0.62, CROMO_ESCURO)
    dz.linha((bx, by), (t["alavanca_ate_x_vis"], by), 0.36, CROMO_CLARO)
    dz.circulo((bx, by), 0.86, CROMO_ESCURO)
    dz.circulo((bx, by), 0.72, CROMO)
    dz.linha((bx, by), (t["bica_ate_x_vis"], by), 0.78, CROMO_ESCURO)
    dz.linha((bx, by), (t["bica_ate_x_vis"], by), 0.48, CROMO)
    dz.linha((bx, by), (t["bica_ate_x_vis"] - 0.2, by), 0.2, CROMO_CLARO)
    dz.circulo((bx, by), 0.42, CROMO_CLARO)
    dz.aplicar(out)
    print(f"    {op['nome']}: cuba {aro[2] - aro[0]:.1f} x {aro[3] - aro[1]:.1f} vis")


def chuveiro(out, f, op):
    px_, y = op["parede_x_vis"], op["y_vis"]
    s = 1 if op["sentido"] == "direita" else -1         # para que lado fica o box
    cx = op["cabeca_x_vis"]
    r = op.get("diametro_vis", 6.44) / 2
    ry = y + op.get("registro_dy_vis", 6.5)
    xs = sorted([px_ - s * 0.3, cx + s * (r + 0.5), px_ + s * 3.4])
    dz = Desenho(f, [xs[0], min(y - r, ry - 1.2) - 0.5, xs[-1], max(y + r, ry + 1.2) + 0.5], folga=4)
    # registro: corpo curto na parede e alavanca
    dz.ret_arred(sorted_ret(px_, ry - 0.95, px_ + s * 1.35, ry + 0.95), 0.35, CROMO_ESCURO)
    dz.ret_arred(sorted_ret(px_, ry - 0.8, px_ + s * 1.2, ry + 0.8), 0.3, CROMO)
    dz.linha((px_ + s * 0.6, ry), (px_ + s * 3.0, ry), 0.55, CROMO_ESCURO)
    dz.linha((px_ + s * 0.6, ry), (px_ + s * 2.9, ry), 0.32, CROMO_CLARO)
    # canopla na parede e braço até a ducha
    dz.ret_arred(sorted_ret(px_, y - 1.15, px_ + s * 0.55, y + 1.15), 0.25, CROMO_ESCURO)
    dz.ret_arred(sorted_ret(px_, y - 1.0, px_ + s * 0.45, y + 1.0), 0.2, CROMO)
    dz.linha((px_ + s * 0.3, y), (cx, y), 0.78, CROMO_ESCURO)
    dz.linha((px_ + s * 0.3, y), (cx, y), 0.5, CROMO)
    dz.linha((px_ + s * 0.3, y), (cx, y), 0.2, CROMO_CLARO)
    # ducha redonda: aro cromado, face fosca e furinhos em anéis
    dz.circulo((cx, y), r, CROMO_ESCURO)
    dz.circulo((cx, y), r - 0.18, CROMO_CLARO)
    dz.circulo((cx, y), r - 0.5, FACE_DUCHA)
    for raio_anel, n in ((r * 0.72, 18), (r * 0.48, 12), (r * 0.24, 6)):
        for i in range(n):
            a = 2 * np.pi * i / n
            dz.circulo((cx + raio_anel * np.cos(a), y + raio_anel * np.sin(a)), 0.13, FURO)
    dz.circulo((cx, y), 0.16, FURO)
    dz.aplicar(out)
    print(f"    {op['nome']}: ducha de {2 * r / 32.21 * 100:.0f} cm a {abs(cx - px_) / 32.21 * 100:.0f} cm da parede")


def sorted_ret(xa, ya, xb, yb):
    return [min(xa, xb), min(ya, yb), max(xa, xb), max(ya, yb)]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pavimento")
    ap.add_argument("entrada", type=Path, help="saída do elementos_do_render.py")
    ap.add_argument("--config", type=Path, required=True)
    ap.add_argument("--saida", type=Path, default=Path("."))
    ap.add_argument("--nome", required=True)
    args = ap.parse_args()

    cfg = json.loads(args.config.read_text())
    op = cfg["pavimentos"][args.pavimento]["acabamentos"]
    img = cv2.imread(str(args.entrada))
    H, W = img.shape[:2]
    f = Folha(W, H, cfg["largura_visualizacao"])
    out = img.astype(np.float32)

    print("[1] apagando símbolos do PDF")
    for o in op.get("clonar", []):
        clonar(out, f, o)
    for o in op.get("parede", []):
        parede(out, f, o)
    print("[2] arestas de banco")
    for o in op.get("arestas_banco", []):
        aresta_banco(out, f, o)
    print("[3] bancadas e cubas")
    for o in op.get("pintar", []):
        pintar(out, f, o)
    for o in op.get("cubas", []):
        cuba(out, f, o)
    print("[4] armários")
    for o in op.get("armarios", []):
        armario(out, f, o)
    print("[5] chuveiros e registros")
    for o in op.get("chuveiros", []):
        chuveiro(out, f, o)

    final = np.clip(np.round(out), 0, 255).astype(np.uint8)
    args.saida.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(args.saida / f"{args.nome}.png"), final)
    cv2.imwrite(str(args.saida / f"{args.nome}_preview.jpg"),
                cv2.resize(final, (2000, round(2000 * H / W)), interpolation=cv2.INTER_AREA), [cv2.IMWRITE_JPEG_QUALITY, 90])
    alfa = np.where(np.abs(final.astype(int) - img.astype(int)).max(axis=2) > 0, 255, 0).astype(np.uint8)
    cv2.imwrite(str(args.saida / f"{args.nome}_camada.png"), np.dstack([final, alfa]))
    print(f"[6] {args.saida / (args.nome + '.png')} ({W}x{H}); {int((alfa > 0).sum())} px alterados")


if __name__ == "__main__":
    main()

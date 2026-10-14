#!/usr/bin/env python3
"""Retoque sem IA do render do Subsolo da Casa C (prompt v3). A imagem final é o render.

1. Bege Bahia: o motor clareou o mármore (cerca de 235/224/212 contra 226/211/200 do aprovado).
   O pátio, os degraus largos, o caminho e o depósito recebem o mesmo Bege Bahia da base: o das
   varandas do 1º Pavimento da Casa A, tecido por image quilting na escala do render.
   - As áreas vêm da base chapada (v2, cor #E8E8E8), alinhada ao render por SIFT.
   - Contornos, a porta do depósito e as plantas da floreira ficam como estão.
   - Nos pixels de borda (linha ou fundo branco misturados com a pedra), só a parte da pedra
     muda de tom.
2. Sentido de descida dos degraus largos: o motor pôs a sombra embaixo de cada aresta, o que lê
   como descida para baixo. A descida é para cima, rumo ao pátio (definido pelo usuário).
   - Cada aresta é redesenhada sobre o Bege Bahia novo, na mesma posição e com o mesmo traço.
   - O perfil da aresta (linha, sombra e filete de luz) é espelhado em torno da linha: a sombra
     passa para cima e o filete de luz para baixo.
   - Como no PDF, são 9 arestas: a de cima, que o motor não fez, entra com o perfil médio das
     outras; as 2 de baixo viram em L e descem junto ao começo do caminho até o fim do pátio.
   A escada curta numerada (esmaecida) não muda.
3. Banco da sauna: o motor fez um banco em U de madeira. Fica o banco da base (pedido do
   usuário): travertino em L, em dois níveis, como o banco aprovado da Casa B.
   - Degrau da frente em L (braço junto à parede da direita e faixa ao longo do banco), um tom
     mais escuro que o piso; assento junto à parede de baixo, mais escuro ainda.
   - O travertino é o do próprio piso da sauna no render: cada coluna continua os veios
     verticais, em espelho; onde era o braço esquerdo do U, volta a ser piso.
   - Arestas finas no tom da aresta do banco da Casa B, sem sombra.
4. Porta do elevador: o motor pôs uma porta de abrir (arco e folha) no acesso ao elevador. Sai
   (pedido do usuário); o arco e a folha viram o vinílico da academia ao lado, nas mesmas linhas.
   O vão, o batente e a soleira ficam.
5. Chuveiros de teto (pedido do usuário): na ducha e no box do BH, cada um no quadradinho da
   base, com a placa quadrada aprovada na Casa A. O que o motor desenhou sai antes: a placa
   grande fora do centro, com haste, na ducha; o metal na parede da esquerda, no box.

As coordenadas estão em px do render (2000 x 1116).

Uso:
  python retoque_subsolo_casac_v3.py RENDER.webp --saida PASTA --nome NOME
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
from scipy import ndimage

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent          # projetos/
sys.path.insert(0, str(AQUI))
from texturizar_base import quilting  # noqa: E402

BASE_CHAPADA = RAIZ / "POE642_CasaC/bases/POE642_CasaC_BASE_Subsolo_v2_16x9.png"
BASE_TEXTURAS = RAIZ / "POE642_CasaC/bases/POE642_CasaC_BASE_Subsolo_v3_texturas_16x9.png"
COR_BEGE_BAHIA = 232                                    # #E8E8E8 na base chapada
FONTE_BEGE_BAHIA = (RAIZ / "POE642_CasaA/renders/POE642_CasaA_PH_1Pavimento_v7_final2.png",
                    [(1350, 582, 1452, 848), (648, 636, 698, 848)])
DEGRAUS = {"x": (191, 336), "y": (372, 520)}            # degraus largos, até a floreira
# como no PDF: 9 arestas; as 7 de cima são retas e as 2 de baixo viram em L, descendo junto ao
# começo do caminho até o fim do pátio. O motor fez 8 retas (faltou a de cima, sem os L).
DEGRAU_TOPO = 381                                       # a aresta de cima, que faltou
DEGRAUS_L = [{"y": 491, "x": 231}, {"y": 507, "x": 246}]  # aresta (y) que vira em L na coluna x
FIM_L = 567                                             # última linha do pátio (o contorno fica)
PLANTAS = (300, 360, 400, 530)                          # onde ficam as plantas da floreira
PEDRA_L = (205, 246)                                    # luminância da pedra lisa no render
PINTA_MAX = 20                                          # px: mancha escura menor que isso é do mármore
LINHA_DIF = 10                                          # quanto a linha é mais escura que a pedra em volta
JANELA = 8                                              # px de cada lado da aresta no espelho
# banco da sauna (geometria da base alinhada ao render): degrau da frente em L (braço junto à
# parede da direita e faixa ao longo do banco) e assento junto à parede de baixo
BANCO = {
    "x": (369, 423),            # colunas entre as paredes (inclusive)
    "y_ini": 416,               # acima disso nada muda
    "parede_x": 368,            # coluna de borda da parede da esquerda (antisserrilhada)
    "parede_y": 497,            # linha de borda da parede de baixo (antisserrilhada)
    "assento_y": 482.5,         # aresta entre o degrau e o assento
    "degrau_y": 468.5,          # aresta da frente do degrau
    "braco_x": 408.5,           # aresta do braço do L
    "braco_topo": 417.5,        # aresta de cima do braço do L
}
TOM_DEGRAU = 0.91               # como o banco aprovado da Casa B (degrau / piso)
TOM_ASSENTO = 0.867             # (assento / piso)
COR_ARESTA = (108, 121, 123)    # BGR de #7B796C, a aresta do banco da Casa B
LARG_ARESTA = 0.5               # px no render
# porta de abrir que o motor pôs no acesso ao elevador (arco e folha, no vinílico da academia):
# retângulo até o batente (exclusivo à direita e embaixo) e o vinílico limpo à esquerda, nas
# mesmas linhas (as réguas são horizontais)
PORTA_ELEVADOR = {"ret": (885, 429, 918, 467), "desloc_x": -36, "esfumar": 3}
# chuveiros de teto: a placa quadrada aprovada na Casa A (banho 3 do 1º Pavimento, 11 x 11 px,
# a mesma escala), no centro do quadradinho da base. Antes, sai o que o motor desenhou: na ducha
# uma placa de uns 55 x 70 cm fora do centro, com haste até a parede; no box do BH um metal na
# parede da esquerda. O piso volta continuando os veios verticais de cima, em espelho.
CHUVEIRO_TETO = (RAIZ / "POE642_CasaA/renders/POE642_CasaA_PH_1Pavimento_v7_final2.png", (1160, 214, 1171, 225))
CHUVEIROS = [
    {"nome": "ducha", "centro": (445.4, 439.5), "apagar": (436, 433, 457, 458), "limpo_y0": 413},
    {"nome": "box do BH", "centro": (445.4, 480.7), "apagar": (428, 476, 437, 486), "limpo_y0": 464},
]


def alinhar(render):
    """Afim base 16:9 (reduzida a 2000 px) → render."""
    base = cv2.resize(cv2.imread(str(BASE_TEXTURAS)), render.shape[1::-1], interpolation=cv2.INTER_AREA)
    sift = cv2.SIFT_create(8000)
    k1, d1 = sift.detectAndCompute(cv2.cvtColor(base, cv2.COLOR_BGR2GRAY), None)
    k2, d2 = sift.detectAndCompute(cv2.cvtColor(render, cv2.COLOR_BGR2GRAY), None)
    pares = [a for a, b in cv2.BFMatcher().knnMatch(d1, d2, k=2) if a.distance < 0.7 * b.distance]
    p1 = np.float32([k1[a.queryIdx].pt for a in pares])
    p2 = np.float32([k2[a.trainIdx].pt for a in pares])
    A, inl = cv2.estimateAffine2D(p1, p2, ransacReprojThreshold=2.0)
    print(f"    alinhamento: {int(inl.sum())} pontos, escala {A[0, 0]:.4f} x {A[1, 1]:.4f}")
    return A


def area_bege_bahia(render, A):
    base = cv2.imread(str(BASE_CHAPADA))
    m = (np.abs(base.astype(np.int32) - COR_BEGE_BAHIA).max(axis=2) <= 4).astype(np.float32)
    m = cv2.resize(m, render.shape[1::-1], interpolation=cv2.INTER_AREA)
    m = cv2.warpAffine(m, A, render.shape[1::-1], flags=cv2.INTER_LINEAR)
    # fecha as linhas tracejadas e a seta da base (ficam dentro da área)
    return cv2.morphologyEx((m > 0.5).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)) > 0


def plantas(render):
    a = render.astype(np.int32)
    b, g, r = a[..., 0], a[..., 1], a[..., 2]
    v = ((g > r + 3) & (g > b)) | (a.mean(axis=2) < 80)
    lim = np.zeros(v.shape, bool)
    x0, y0, x1, y1 = PLANTAS
    lim[y0:y1, x0:x1] = True
    v = ndimage.binary_fill_holes(ndimage.binary_closing(v & lim, iterations=2))
    return ndimage.binary_dilation(v, iterations=1)


def textura(forma, caixa):
    img = cv2.imread(str(FONTE_BEGE_BAHIA[0])).astype(np.float32)
    fontes = []
    for x0, y0, x1, y1 in FONTE_BEGE_BAHIA[1]:
        t = img[y0:y1, x0:x1]
        fontes += [np.ascontiguousarray(v) for v in (t, t[:, ::-1], t[::-1, :], t[::-1, ::-1])]
    x0, y0, x1, y1 = caixa
    tex = np.zeros(forma, np.float32)
    tex[y0:y1, x0:x1] = quilting(fontes, y1 - y0, x1 - x0, p=48, sobra=12, candidatos=1200)
    return tex


def relevo_degraus(L, livre):
    """Mapa multiplicativo dos degraus largos: arestas do render com o perfil espelhado."""
    x0, x1 = DEGRAUS["x"]
    y0, y1 = DEGRAUS["y"]
    K = np.ones(L.shape, np.float32)
    sub = np.where(livre[y0:y1, x0:x1], L[y0:y1, x0:x1], np.nan)
    m = np.nanmedian(sub, axis=1)
    escuras = np.nonzero(m < 180)[0]
    grupos = []
    for y in escuras:
        if grupos and y - grupos[-1][-1] <= 2:
            grupos[-1].append(y)
        else:
            grupos.append([y])
    arestas = []
    for g in grupos:
        c = y0 + g[int(np.argmin(m[g]))]                   # a linha mais escura da aresta
        liso = np.nanmedian(m[c - y0 - 7:c - y0 - 2])      # piso liso logo acima (sem sombra)
        arestas.append((c, np.clip(m[c - y0 - JANELA:c - y0 + JANELA + 1] / liso, 0.45, 1.06)))
    medio = np.mean([pf for _, pf in arestas], axis=0)
    if all(abs(c - DEGRAU_TOPO) > 4 for c, _ in arestas):
        arestas.insert(0, (DEGRAU_TOPO, medio))
    n_l = 0
    for c, perfil in arestas:
        xi = x0
        for dl in DEGRAUS_L:
            if abs(c - dl["y"]) <= 3:
                xi = dl["x"]
                n_l += 1
                # o L: a aresta desce na coluna x até o fim do pátio, com a sombra do lado de fora
                # (à esquerda, o nível mais baixo), como a de cima de cada aresta reta
                for d in range(-JANELA, JANELA + 1):
                    K[c - 1:FIM_L + 1, xi + d] *= perfil[JANELA - d]
        for d in range(-JANELA, JANELA + 1):                # linha c+d recebe o que estava em c-d
            K[c + d, xi:x1] *= perfil[JANELA - d]
    print(f"    degraus largos: {len(arestas)} arestas com a sombra virada para o pátio, {n_l} em L")
    return K


def banco_sauna(out, orig):
    """Troca o banco em U de madeira do render pelo banco da base: travertino em L, dois tons."""
    b = BANCO
    xa, xb = b["x"]
    y0, y1 = b["y_ini"], b["parede_y"]
    a = orig.astype(np.float32)
    L = a.mean(axis=2)
    # piso: cada coluna continua para baixo os veios (verticais) do próprio travertino do render,
    # em espelho, a partir do trecho limpo acima da madeira
    F = a[y0:y1].copy()
    # madeira: mais saturada que o travertino (R-B acima de 33) ou bem mais escura; o começo da
    # madeira vale também para as 2 colunas de cada lado (a borda do U tem sombra sem a cor da madeira)
    madeira = (a[y0:y1, :, 2] - a[y0:y1, :, 0] > 33) | (L[y0:y1] < 175)
    tem = madeira.any(axis=0)
    comeco = np.where(tem, y0 + madeira.argmax(axis=0), y1)
    comeco = ndimage.minimum_filter1d(comeco, 5)
    for x in range(xa, xb + 1):
        ini = 412 if x == xb else 388                     # na última coluna, só junto à parede
        fim = min(comeco[x] - 2, y1)
        seg = a[ini:fim, x]
        n = len(seg)
        for y in range(max(fim, y0), y1):
            k = (y - fim) % (2 * n)
            F[y - y0, x] = seg[n - 1 - k] if k < n else seg[k - n]
    novo = F[:, xa:xb + 1]
    ys = np.arange(y0, y1)[:, None] + 0.5
    xs = np.arange(xa, xb + 1)[None, :] + 0.5
    assento = ys > b["assento_y"]
    degrau = ~assento & ((ys > b["degrau_y"]) | ((xs > b["braco_x"]) & (ys > b["braco_topo"])))
    novo = novo * np.where(assento, TOM_ASSENTO, np.where(degrau, TOM_DEGRAU, 1.0))[..., None]
    out[y0:y1, xa:xb + 1] = novo

    # arestas de 0,5 px, desenhadas a 8x
    ss = 8
    gx0, gy0 = xa - 1, y0
    h, w = y1 - y0 + 1, xb - xa + 3
    tela = np.zeros((h * ss, w * ss), np.uint8)
    lw = max(1, round(LARG_ARESTA * ss))

    def linha(p, q):
        cv2.line(tela, (round((p[0] - gx0) * ss), round((p[1] - gy0) * ss)),
                 (round((q[0] - gx0) * ss), round((q[1] - gy0) * ss)), 255, lw)

    fim_x = xb + 1
    linha((xa - 1, b["assento_y"]), (fim_x, b["assento_y"]))
    linha((xa - 1, b["degrau_y"]), (b["braco_x"], b["degrau_y"]))
    linha((b["braco_x"], b["braco_topo"]), (b["braco_x"], b["degrau_y"]))
    linha((b["braco_x"], b["braco_topo"]), (fim_x, b["braco_topo"]))
    al = cv2.resize(tela.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None]
    reg = out[gy0:gy0 + h, gx0:gx0 + w]
    out[gy0:gy0 + h, gx0:gx0 + w] = np.where(al > 0, reg * (1 - al) + np.float32(COR_ARESTA) * al, reg)

    # bordas antisserrilhadas das paredes: a parte do pixel que era madeira passa a ser travertino
    parede = np.float32([4, 4, 4])
    for borda, vizinho in (((slice(y0, y1), b["parede_x"]), (slice(y0, y1), xa)),
                           ((b["parede_y"], slice(xa, xb + 1)), (b["parede_y"] - 1, slice(xa, xb + 1)))):
        antes, depois = a[vizinho], out[vizinho]
        mudou = np.abs(depois - antes).max(axis=-1) > 0
        wf = np.clip((a[borda].mean(-1) - 4) / np.maximum(antes.mean(-1) - 4, 1), 0, 1)[..., None]
        out[borda] = np.where(mudou[..., None], parede + wf * (depois - parede), out[borda])
    print(f"    banco da sauna: degrau em L e assento em travertino, {int(degrau.sum() + assento.sum())} px")
    return out


def porta_elevador(out):
    """Tira a porta de abrir do acesso ao elevador: arco e folha viram o vinílico ao lado."""
    x0, y0, x1, y1 = PORTA_ELEVADOR["ret"]
    dx = PORTA_ELEVADOR["desloc_x"]
    e = PORTA_ELEVADOR["esfumar"]
    alvo = out[y0:y1, x0:x1]
    fonte = out[y0:y1, x0 + dx:x1 + dx]
    # tom: o vinílico logo em volta do retângulo contra o mesmo em volta da fonte
    anel = np.ones((y1 - y0 + 2 * e, x1 - x0 + e), bool)
    anel[e:-e, e:] = False
    viz_alvo = out[y0 - e:y1 + e, x0 - e:x1][anel]
    viz_fonte = out[y0 - e:y1 + e, x0 - e + dx:x1 + dx][anel]
    fonte = fonte + (np.median(viz_alvo, axis=0) - np.median(viz_fonte, axis=0))
    # esfuma à esquerda, em cima e embaixo; à direita encosta no batente, que fica
    ay = np.minimum(np.arange(y1 - y0) + 1, np.arange(y1 - y0)[::-1] + 1) / e
    ax = (np.arange(x1 - x0) + 1) / e
    al = np.clip(np.minimum(ay[:, None], ax[None, :]), 0, 1)[..., None]
    out[y0:y1, x0:x1] = alvo * (1 - al) + fonte * al
    print(f"    porta do elevador: {(x1 - x0) * (y1 - y0)} px no vinílico da academia")
    return out


def chuveiros_teto(out):
    """Chuveiros de teto da ducha e do box do BH, cada um no quadradinho da base."""
    img = cv2.imread(str(CHUVEIRO_TETO[0])).astype(np.float32)
    hx0, hy0, hx1, hy1 = CHUVEIRO_TETO[1]
    cab = img[hy0:hy1, hx0:hx1]
    for c in CHUVEIROS:
        x0, y0, x1, y1 = c["apagar"]
        seg = out[c["limpo_y0"]:y0, x0:x1].copy()
        n = len(seg)
        for y in range(y0, y1):
            k = (y - y0) % (2 * n)
            out[y, x0:x1] = seg[n - 1 - k] if k < n else seg[k - n]
        cx, cy = c["centro"]
        px, py = round(cx - (hx1 - hx0 - 1) / 2), round(cy - (hy1 - hy0 - 1) / 2)
        out[py:py + cab.shape[0], px:px + cab.shape[1]] = cab
        print(f"    {c['nome']}: chuveiro de teto em ({cx}, {cy})")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("render", type=Path)
    ap.add_argument("--saida", type=Path, default=Path("."))
    ap.add_argument("--nome", required=True)
    args = ap.parse_args()

    orig = cv2.imread(str(args.render))
    a = orig.astype(np.float32)
    L = a.mean(axis=2)
    print("[1] áreas de Bege Bahia")
    A = alinhar(orig)
    area = area_bege_bahia(orig, A)
    verde = plantas(orig)
    area &= ~verde
    ys, xs = np.nonzero(area)
    caixa = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    print("[2] linhas que ficam (contornos, porta do depósito)")
    x0, x1 = DEGRAUS["x"]
    y0, y1 = DEGRAUS["y"]
    deg = np.zeros(area.shape, bool)
    deg[y0:y1, x0:x1] = True
    deg &= area
    # traço mais escuro que a pedra em volta (mediana local, sem as nuvens do mármore); as
    # pintinhas e os veios finos do mármore do render saem, as linhas (compridas) ficam
    med = np.median(L[area])
    fundo = cv2.medianBlur(np.where(area & (L > 200) & (L < 246), L, med).astype(np.uint8), 11)
    escuro = area & ~deg & (L < fundo.astype(np.float32) - LINHA_DIF)
    junto = ndimage.binary_closing(escuro, structure=np.ones((3, 3))) | escuro
    lab, n = ndimage.label(junto, structure=np.ones((3, 3)))
    tam = ndimage.sum(junto, lab, range(1, n + 1))
    linhas = ndimage.binary_dilation(np.isin(lab, np.nonzero(tam > PINTA_MAX)[0] + 1), iterations=1)
    print(f"    {int((tam > PINTA_MAX).sum())} linhas, {int((tam <= PINTA_MAX).sum())} pintinhas")
    pedra = area & ~linhas & (L <= PEDRA_L[1]) & (a[..., 2] >= a[..., 1] - 2)
    tom_render = np.median(a[pedra & (L >= PEDRA_L[0])], axis=0)

    print("[3] textura do Bege Bahia aprovado")
    T = textura(a.shape, caixa)
    print(f"    render {tom_render[::-1].round()} → aprovado {np.median(T[pedra], axis=0)[::-1].round()} (RGB)")

    print("[4] arestas dos degraus largos")
    K = relevo_degraus(L, deg)

    out = a.copy()
    troca = pedra | deg
    out[troca] = (T * K[..., None])[troca]
    # bordas: linha ou fundo branco misturados com a pedra; só a parte da pedra muda de tom
    anel = ndimage.binary_dilation(area, iterations=2) & ~troca & ~verde
    ls = tom_render.mean()
    w = np.where(L < ls, np.clip((L - 110) / (ls - 110), 0, 1), np.clip((255 - L) / (255 - ls), 0, 1))
    w[~anel] = 0
    out += (T - tom_render) * w[..., None] * (T.sum(axis=2) > 0)[..., None]

    print("[5] banco da sauna")
    out = banco_sauna(out, orig)

    print("[6] porta do elevador")
    out = porta_elevador(out)

    print("[7] chuveiros de teto")
    out = chuveiros_teto(out)
    out = np.clip(out, 0, 255).astype(np.uint8)

    args.saida.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(args.saida / f"{args.nome}.png"), out)
    alfa = np.where(np.abs(out.astype(int) - orig.astype(int)).max(axis=2) > 0, 255, 0).astype(np.uint8)
    cv2.imwrite(str(args.saida / f"{args.nome}_camada.png"), np.dstack([out, alfa]))
    print(f"[8] {args.saida / (args.nome + '.png')}; {int((alfa > 0).sum())} px alterados")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Biblioteca de blocos (mobiliário visto de cima) e a cortina das plantas humanizadas do POE 642 (todas as casas).

Pedido do usuário (20/10/26), com um pin do Pinterest e depois as folhas de blocos como imagem: "adicione esse
[pin] à nossa biblioteca de blocos a serem utilizados e oferecidos, dentro do escopo do projeto das casas. temos
várias opções. quero que você escolha dentro do que está nos pdfs base das casas. e encontre uma cortina para
usarmos." O Pinterest não abre desta sessão (proxy 403 / DNS); as folhas que chegaram como arquivo estão em
`originais/` (folha_01 a folha_05).

O que entra (`blocos.json`): só as peças que têm correspondente no mobiliário dos PDFs base, conferido nas camadas
ARQ_MOBILIÁRIO, ARQ_LAYOUT HUMANIZAÇÃO, ARQ_LOUÇAS E METAIS e ARQ_MARCENARIA das 12 plantas: sofás orgânicos e
retos, poltronas (em X e de leitura), mesas de centro e laterais, jantar retangular, oval e redondo, ilha com
banquetas, cooktops de 4 e 5 bocas (inox, como os eletrodomésticos), cubas, vasos sanitários, banheira oval (banho
master do 1º Pav. da Casa E), escrivaninhas, mesa e poltronas externas e plantas. Os 'extras' (guarda-sóis, sofá de
couro) são oferecidos, mas não estão nos PDFs. O que ficou de fora e por quê está em `blocos.json` ("fora"),
inclusive o banco de teca, que tem marca d'água de banco de imagens.

Como cada bloco é recortado (`recortar`): sem IA generativa. O fundo da folha (branco, cinza 232 ou o xadrez de
"PNG falso") ligado à borda da caixa, e os bolsões de fundo liso entre a mesa e as cadeiras, são fundo certo; a
sombra projetada da foto (cinza sem saturação, até 24 níveis abaixo do fundo) ligada a ele é fundo provável, para o
bloco sair sem sombra e receber a do render; o GrabCut (corte em grafo do OpenCV) separa o resto pela cor e pelas
bordas. Nas louças e pedras brancas como o fundo, o contorno é a envoltória convexa do corpo ('convexo' no JSON)
ou a área marcada como peça certa ('certo_ret' e 'certo_elipse', em px da folha); 'so_maior' fica só com a peça
maior quando a caixa pega um pedaço da vizinha. A borda leva um desfoque de 0,6 px. O recorte fica em
`recortes/<id>.png` (RGBA,
na resolução da folha); `bloco(id, px_por_m)` devolve (BGR float32, alfa 0 a 1) na medida real ('largura_m' ou
'altura_m' do JSON, ajustável ao bloco do PDF na hora de aplicar).

A cortina (`cortina`): nenhuma folha traz cortina, e nos PDFs ela é a linha ondulada junto aos vidros (quartos do
1º Pav. A e E, Térreo B). Por isso é desenhada aqui, no mesmo estilo: o trilho em linha cinza fina junto ao vidro e
o tecido de linho cru em ondas (prega "wave", 14 cm de passo, 3,5 cm de amplitude, 2,2 cm de espessura), com a luz
nas cristas e uma sombra leve para o lado de dentro; `aberta=True` franze o tecido em dois maços nas pontas (18% do
vão cada, pregas mais fechadas e fundas, o miolo cheio de tecido) e deixa só o trilho no meio.

Nada disso foi aplicado aos renders ainda (aguarda a aprovação da cartela).

Uso:
  python3 blocos.py      # recortes/*.png e cartela_blocos.jpg (escala da prancha, 60 px/m, e ampliada 2 x)
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

AQUI = Path(__file__).resolve().parent
CFG = json.loads((AQUI / "blocos.json").read_text())
SS = 4                              # supersampling da cortina
LINHO = (215, 227, 233)             # BGR, linho cru
TRILHO = (168, 168, 170)


def _frente(crop, fundo, certo=None):
    """Máscara da peça: o fundo da folha ligado à borda da caixa (e os bolsões de fundo liso, entre a mesa e as
    cadeiras) é fundo certo, a sombra da foto ligada a ele é fundo provável, o que destoa muito do fundo é peça
    certa e o resto é peça provável; o GrabCut (corte em grafo, sem IA) decide o provável pela cor e pelas bordas."""
    c = crop.astype(np.int16)
    mx, mn = c.max(2), c.min(2)
    sat = mx - mn
    if fundo == "xadrez":
        estrito = ((mn >= 236) & (sat <= 6)) | (np.abs(c - 229).max(2) <= 4)
        sombra = np.zeros_like(estrito)
        forte = (sat >= 14) | (mx <= 200)
    else:
        b = np.array(fundo, np.int16)
        B = int(b.max())
        estrito = np.abs(c - b).max(2) <= (6 if B == 255 else 4)
        sombra = (sat <= 10) & (mx < B - 4) & (mx >= B - 24)
        forte = (sat >= 14) | (mx <= B - 40) | (mn >= min(B + 14, 250))
    n, lab = cv2.connectedComponents(estrito.astype(np.uint8), connectivity=4)
    borda = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    fundo_m = np.isin(lab, borda[borda > 0])
    if fundo != "xadrez":
        n, lab, st, _ = cv2.connectedComponentsWithStats((estrito & ~fundo_m).astype(np.uint8), connectivity=4)
        cinza = crop.astype(np.float32).mean(2)
        for i in range(1, n):
            if st[i, 4] >= 60 and cinza[lab == i].std() <= 1.2:
                fundo_m |= lab == i
    n, lab = cv2.connectedComponents((fundo_m | sombra).astype(np.uint8), connectivity=4)
    ids = np.unique(lab[fundo_m])
    provavel = np.isin(lab, ids[ids > 0]) & ~fundo_m
    m = np.full(c.shape[:2], cv2.GC_PR_FGD, np.uint8)
    m[provavel] = cv2.GC_PR_BGD
    m[fundo_m] = cv2.GC_BGD
    m[forte & ~fundo_m & ~provavel] = cv2.GC_FGD
    if certo is not None:
        m[certo > 0] = cv2.GC_FGD
    m[0, :] = m[-1, :] = m[:, 0] = m[:, -1] = cv2.GC_BGD
    cv2.grabCut(crop, m, None, np.zeros((1, 65)), np.zeros((1, 65)), 5, cv2.GC_INIT_WITH_MASK)
    return ((m == cv2.GC_FGD) | (m == cv2.GC_PR_FGD)).astype(np.uint8)


def recortar(b):
    folha = CFG["folhas"][b["folha"]]
    img = cv2.imread(str(AQUI / folha["arquivo"]))
    x, y, w, h = b["caixa"]
    m = 4
    x0, y0 = max(0, x - m), max(0, y - m)
    x1, y1 = min(img.shape[1], x + w + m), min(img.shape[0], y + h + m)
    crop = img[y0:y1, x0:x1]
    certo = np.zeros(crop.shape[:2], np.uint8)
    for rx, ry, rw, rh in b.get("certo_ret", []):
        certo[ry - y0:ry - y0 + rh, rx - x0:rx - x0 + rw] = 1
    for cx, cy, ax, ay in b.get("certo_elipse", []):
        cv2.ellipse(certo, (cx - x0, cy - y0), (ax, ay), 0, 0, 360, 1, -1)
    fg = _frente(crop, folha["fundo"], certo) | certo
    n, lab, st, _ = cv2.connectedComponentsWithStats(fg, connectivity=8)
    if n > 1:
        maior = st[1:, 4].max()
        minimo = maior if b.get("so_maior") else max(25, 0.02 * maior)
        fg = np.isin(lab, [i for i in range(1, n) if st[i, 4] >= minimo]).astype(np.uint8)
    if b.get("convexo"):         # louça e pedra brancas como o fundo: o contorno é a envoltória do corpo
        corpo = cv2.morphologyEx(fg, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
        pts = cv2.findNonZero(corpo)
        if pts is not None:
            cv2.fillConvexPoly(fg, cv2.convexHull(pts), 1)
    furos = (1 - fg).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(furos, connectivity=4)
    for i in range(1, n):
        if st[i, 4] < 25:
            fg[lab == i] = 1
    alfa = cv2.GaussianBlur(fg.astype(np.float32), (0, 0), 0.6)
    alfa[cv2.erode(fg, np.ones((3, 3), np.uint8)) > 0] = 1.0
    ys, xs = np.nonzero(alfa > 0.02)
    sl = np.s_[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    rgba = np.dstack([crop[sl], np.round(alfa[sl] * 255).astype(np.uint8)])
    return rgba


def bloco(bid, px_m):
    """(BGR float32, alfa 0 a 1) do bloco na medida real, a px_m px/m."""
    b = next(b for b in CFG["blocos"] if b["id"] == bid)
    rgba = cv2.imread(str(AQUI / "recortes" / f"{bid}.png"), cv2.IMREAD_UNCHANGED).astype(np.float32)
    h, w = rgba.shape[:2]
    f = (b["largura_m"] * px_m / w) if "largura_m" in b else (b["altura_m"] * px_m / h)
    W, H = max(1, round(w * f)), max(1, round(h * f))
    a = rgba[..., 3:] / 255
    pre = cv2.resize(rgba[..., :3] * a, (W, H), interpolation=cv2.INTER_AREA)
    a = cv2.resize(a[..., 0], (W, H), interpolation=cv2.INTER_AREA)
    cor = pre / np.maximum(a, 1e-4)[..., None]
    return cor, a


def cortina(comp_m, px_m, aberta=False, cor=LINHO, passo_m=0.14, amp_m=0.035, esp_m=0.022, mac0=0.18):
    """A cortina vista de cima, na horizontal: o trilho em cima (lado do vidro), o tecido em ondas (prega wave) e a
    sombra para baixo (lado de dentro). Aberta, o tecido fica franzido em dois maços nas pontas, com as pregas mais
    fechadas e fundas e o miolo do maço cheio de tecido. Devolve (BGR float32, alfa 0 a 1)."""
    k = px_m * SS
    prof_m = 0.17
    W, H = max(1, round(comp_m * k)), max(1, round(prof_m * k))
    X, Y = np.meshgrid(np.arange(W) + 0.5, np.arange(H) + 0.5)
    x_m = X / k
    y_tr = 0.02 * k                                    # eixo do trilho
    y_c = 0.085 * k                                    # eixo do tecido
    if aberta:
        maco = max(0.25, mac0 * comp_m)
        dist = np.minimum(x_m, comp_m - x_m)
        tem = np.clip((maco - dist) / 0.02, 0, 1)      # o maço termina numa dobra, sem cauda
        lam, amp = passo_m * 0.45, amp_m * 1.45 * tem
    else:
        tem = np.ones_like(x_m)
        lam, amp = passo_m, np.full_like(x_m, amp_m)
    fase = 2 * np.pi * x_m / lam
    yc = y_c + amp * k * np.sin(fase)
    incl = amp * k * np.cos(fase) * 2 * np.pi / (lam * k)
    meia = 0.5 * esp_m * k * np.sqrt(1 + incl ** 2)
    tecido = np.clip(meia + 0.5 - np.abs(Y - yc), 0, 1) * (tem > 0.01)
    if aberta:                                         # o miolo franzido: tecido cheio entre as dobras
        miolo = np.clip(amp * k * 0.75 + 0.5 - np.abs(Y - y_c), 0, 1) * tem
        tecido = np.maximum(tecido, miolo * 0.92)
    luz = 0.80 + 0.20 * (0.5 + 0.5 * np.cos(fase + 0.9))  # cristas viradas para a luz mais claras
    luz = cv2.GaussianBlur(luz.astype(np.float32), (0, 0), 0.004 * k)
    trilho = np.clip(0.008 * k + 0.5 - np.abs(Y - y_tr), 0, 1) * 0.85
    sombra = cv2.GaussianBlur(np.roll(tecido, round(0.02 * k), axis=0), (0, 0), 0.014 * k) * 0.30
    cor_t = np.array(cor, np.float32) * luz[..., None]
    rgb = cor_t * tecido[..., None] + np.array(TRILHO, np.float32) * (trilho * (1 - tecido))[..., None]
    peso = tecido + trilho * (1 - tecido)
    rgb = rgb / np.maximum(peso, 1e-4)[..., None]
    alfa = 1 - (1 - tecido) * (1 - trilho) * (1 - sombra)
    pre = rgb * (1 - (1 - tecido) * (1 - trilho))[..., None]   # a sombra é preta
    Wr, Hr = max(1, round(comp_m * px_m)), max(1, round(prof_m * px_m))
    pre = cv2.resize(pre, (Wr, Hr), interpolation=cv2.INTER_AREA)
    a = cv2.resize(alfa.astype(np.float32), (Wr, Hr), interpolation=cv2.INTER_AREA)
    return pre / np.maximum(a, 1e-4)[..., None], a


def _pousar(tela, cor, a, x, y):
    h, w = a.shape
    reg = tela[y:y + h, x:x + w]
    reg[:] = cor * a[..., None] + reg * (1 - a[..., None])


def gerar_recortes():
    (AQUI / "recortes").mkdir(exist_ok=True)
    for b in CFG["blocos"]:
        cv2.imwrite(str(AQUI / "recortes" / f"{b['id']}.png"), recortar(b))
    for aberta in (False, True):
        c, a = cortina(3.0, 240, aberta=aberta)
        rgba = np.dstack([np.clip(c, 0, 255), a * 255]).round().astype(np.uint8)
        cv2.imwrite(str(AQUI / "recortes" / f"cortina_linho_{'aberta' if aberta else 'fechada'}.png"), rgba)


def _quebrar(texto, fonte, largura):
    linhas, atual = [], ""
    for pal in (texto or "").split():
        teste = (atual + " " + pal).strip()
        if atual and fonte.getlength(teste) > largura:
            linhas.append(atual)
            atual = pal
        else:
            atual = teste
    return linhas + ([atual] if atual else [])


def cartela():
    sys.path.insert(0, str(AQUI.parent / "POE642_CasaA" / "scripts"))
    from PIL import ImageDraw, ImageFont
    from rodape_entrega import FONTES
    f1 = ImageFont.truetype(str(FONTES / "Inter-Medium.otf"), 30)
    f2 = ImageFont.truetype(str(FONTES / "Inter-Medium.otf"), 22)
    f3 = ImageFont.truetype(str(FONTES / "Inter-Regular.otf"), 15)
    px_m = CFG["escala_prancha_px_por_m"]
    AMP = 2
    PISO = (226, 227, 228)
    LARG = 2600
    nomes_cat = {"estar": "Estar", "jantar": "Jantar e ilha", "cozinha": "Cozinha (cooktops e cubas)",
                 "banho": "Banho", "escritório": "Escritório e aparadores", "externo": "Externo (gourmet e varanda)",
                 "paisagismo": "Paisagismo", "extras": "Extras (oferecidos, não estão nos PDFs)"}
    secoes = []                      # (titulo, [(img, legenda1, legenda2)])
    for cat in nomes_cat:
        itens = []
        for b in [b for b in CFG["blocos"] if b["categoria"] == cat]:
            cor, a = bloco(b["id"], px_m * AMP)
            med = f"{b['largura_m']:.2f} m".replace(".", ",") if "largura_m" in b else \
                f"{b['altura_m']:.2f} m (na vertical)".replace(".", ",")
            itens.append((cor, a, b["nome"], med, b["onde"]))
        secoes.append((nomes_cat[cat], itens))

    # cortina: diante de um vidro, fechada e aberta, na escala da prancha x 2 e um detalhe x 6
    cort = []
    for aberta, rot in ((False, "Cortina de linho cru, fechada (3,00 m)"), (True, "Aberta, em maços nas pontas")):
        c, a = cortina(3.0, px_m * AMP, aberta=aberta)
        cort.append((c, a, rot, "trilho junto ao vidro; prega wave de 14 cm",
                     "vidros dos quartos e estares (linha ondulada dos PDFs: 1º Pav. A e E, Térreo B)"))
    c, a = cortina(0.6, px_m * 6, aberta=False)
    cort.append((c, a, "Detalhe ampliado 6 x", "luz nas cristas, sombra para dentro", ""))
    secoes.append(("Cortina (desenhada aqui: nenhuma folha traz cortina)", cort))

    # diagramação
    blocos_desenho, y = [], 120
    for titulo, itens in secoes:
        y_tit = y
        y += 50
        x, alt_linha = 40, 0
        for cor, a, n1, n2, n3 in itens:
            w = max(a.shape[1], 250) + 40
            if x + w > LARG:
                x, y = 40, y + alt_linha + 100
                alt_linha = 0
            blocos_desenho.append((cor, a, x, y, n1, n2, n3, w))
            x += w
            alt_linha = max(alt_linha, a.shape[0])
        y += alt_linha + 110
        blocos_desenho.append((None, None, 40, y_tit, titulo, None, None, None))
    tela = np.full((y + 20, LARG, 3), 255, np.float32)
    textos = []
    for cor, a, x, yy, n1, n2, n3, w in blocos_desenho:
        if cor is None:
            textos.append((x, yy, n1, f2, (40, 40, 40)))
            continue
        h, wa = a.shape
        cv2.rectangle(tela, (x - 6, yy - 6), (x + wa + 6, yy + h + 6), PISO, -1)
        if n1.startswith("Cortina") or n1.startswith("Aberta") or n1.startswith("Detalhe"):
            cv2.line(tela, (x, yy + 1), (x + wa, yy + 1), (120, 120, 124), 2)   # o vidro / a parede
        _pousar(tela, cor, a, x, yy)
        yt = yy + h + 10
        for t, c in ((n1, (40, 40, 40)), (n2, (110, 110, 110)), (n3, (140, 120, 90))):
            for l in _quebrar(t, f3, w - 34):
                textos.append((x, yt, l, f3, c))
                yt += 17
    # barra de 1 m
    cv2.rectangle(tela, (LARG - 40 - px_m * AMP, 60), (LARG - 40, 66), (60, 60, 60), -1)
    im = Image.fromarray(np.clip(tela, 0, 255).astype(np.uint8)[..., ::-1])
    d = ImageDraw.Draw(im)
    d.text((40, 24), "Biblioteca de blocos · POE 642 · todas as casas", font=f1, fill=(40, 40, 40))
    d.text((40, 66), "Peças das folhas de referência que existem no mobiliário dos PDFs base, na medida real, "
           "ampliadas 2 x a escala da prancha (60 px/m). Ainda não aplicadas.", font=f3, fill=(90, 90, 90))
    d.text((LARG - 40 - px_m * AMP, 74), "1 m (x 2)", font=f3, fill=(60, 60, 60))
    for x, yy, t, f, c in textos:
        d.text((x, yy), t, font=f, fill=c)
    im.save(AQUI / "cartela_blocos.jpg", quality=90)
    print(AQUI / "cartela_blocos.jpg", im.size)


if __name__ == "__main__":
    gerar_recortes()
    cartela()

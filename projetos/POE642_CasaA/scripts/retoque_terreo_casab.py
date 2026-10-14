#!/usr/bin/env python3
"""Retoque sem IA do render do Térreo da Casa B (prompt v4). A imagem final é o render.

1. Transbordo: o motor criou uma faixa de água comprida descendo pela esquerda da piscina,
   dos decks e do banco, onde é gramado. A faixa vira o gramado vizinho (24 px à esquerda),
   linha a linha, da borda do gramado até onde começa o deck, a borda da piscina ou o banco.
2. Área verde: o vão branco abaixo da escada de cima, ao lado do deck, vira gramado.
3. Planta do hall: o símbolo em traço junto à porta vira uma planta de verdade, recortada de
   uma touceira do próprio render (a da direita no jardim de 4,62 m², sobre terra, que se recorta limpa) e reduzida ao tamanho do símbolo.
4. Lavatório gourmet: a bancada, que o motor deixou branca e cinza, fica no mesmo quartzo
   das bancadas da cozinha (trecho da ilha repetido em espelho); por cima, as duas cubas em
   traço viram cubas brancas de louça, com bacia, válvula e torneira cromada do lado da parede.

As coordenadas estão em px do render (2000 x 1116).

Uso:
  python retoque_terreo_casab.py RENDER.webp --saida PASTA --nome NOME
"""
import argparse
from pathlib import Path

import cv2
import numpy as np
from scipy import ndimage

SS = 8
# transbordo: linhas e borda do gramado
TRANSBORDO = {"y": (501, 888), "x_gramado": 301, "x_max": 326, "x_sem_fim": 320, "desloc": 24}
# área verde: interior do vão (o contorno fica) e um trecho limpo do gramado do render
AREA_VERDE = {"ret": (350, 356, 394, 400), "fonte": (170, 600)}
# planta do hall: símbolo a apagar, centro e diâmetro; touceira de origem
PLANTA = {"simbolo": (1283, 488, 1310, 519), "centro": (1296, 503), "diametro": 30,
          "fonte": (1276, 606, 1338, 670)}
# bancada do lavatório gourmet (entre as paredes, até a parede de baixo) e trecho limpo da ilha
BANCADA = {"ret": (636, 840, 741, 855), "fonte": (858, 726, 872, 758)}
# cubas do lavatório gourmet (contorno externo do símbolo)
CUBAS = [(663, 832, 684, 850), (695, 832, 716, 850)]

LOUCA = (246, 247, 247)
LOUCA_CONTORNO = (160, 162, 163)
BACIA_BORDA = (214, 216, 217)
BACIA_FUNDO = (239, 240, 240)
CROMO_ESCURO = (130, 134, 138)
CROMO = (196, 199, 202)
CROMO_CLARO = (238, 240, 242)


def transbordo(img, orig):
    a = orig.astype(int)
    t = TRANSBORDO
    m = np.zeros(img.shape[:2], bool)
    for y in range(*t["y"]):
        xr = t["x_sem_fim"]
        for x in range(t["x_gramado"] + 2, t["x_max"]):
            r, g = a[y, x, 2], a[y, x, 1]
            if r > 200 or (r > 95 and r > g + 12):      # começa o deck, a borda ou o banco
                xr = x
                break
        m[y, t["x_gramado"]:xr] = True
    out = img.astype(np.float32)
    fonte = np.roll(out, t["desloc"], axis=1)
    anel = ndimage.binary_dilation(m, iterations=6) & ~ndimage.binary_dilation(m, iterations=1)
    anel[:, t["x_gramado"]:] = False
    corr = np.median(out[anel], 0) - np.median(fonte[anel], 0)
    alfa = m.astype(np.float32)
    alfa[:, t["x_gramado"] - 1] = np.maximum(alfa[:, t["x_gramado"] - 1], 0.5 * m[:, t["x_gramado"]])
    out = out * (1 - alfa[..., None]) + (fonte + corr) * alfa[..., None]
    print(f"    transbordo: {int(m.sum())} px viraram gramado")
    return np.clip(out, 0, 255).astype(np.uint8)


def area_verde(img):
    x0, y0, x1, y1 = AREA_VERDE["ret"]
    fx, fy = AREA_VERDE["fonte"]
    img[y0:y1, x0:x1] = img[fy:fy + (y1 - y0), fx:fx + (x1 - x0)]
    print(f"    área verde: {(x1 - x0) * (y1 - y0)} px de gramado")
    return img


def planta(img):
    x0, y0, x1, y1 = PLANTA["simbolo"]
    bloco = img[y0:y1, x0:x1].astype(int)
    piso = np.median(bloco.reshape(-1, 3), 0)
    m = np.zeros(img.shape[:2], np.uint8)
    m[y0:y1, x0:x1] = (np.abs(bloco - piso).max(2) > 12).astype(np.uint8)
    m = cv2.dilate(m, np.ones((3, 3), np.uint8))
    # a parede e o caixilho da porta ficam (só o símbolo sai)
    m[y0:y1, x0:x1][bloco.mean(2) < 90] = 0
    img = cv2.inpaint(img, m * 255, 3, cv2.INPAINT_TELEA)

    fx0, fy0, fx1, fy1 = PLANTA["fonte"]
    sp = img[fy0:fy1, fx0:fx1].astype(np.float32)
    b, g, r = sp[..., 0], sp[..., 1], sp[..., 2]
    folha = (g > r + 8) & (g > b + 4)
    folha = ndimage.binary_opening(folha, iterations=1)
    lab, n = ndimage.label(folha)
    tam = ndimage.sum(folha, lab, range(1, n + 1))
    folha = lab == (int(np.argmax(tam)) + 1)                 # a maior touceira
    folha = ndimage.binary_fill_holes(ndimage.binary_closing(folha, iterations=2))
    ys, xs = np.nonzero(folha)
    sp, folha = sp[ys.min():ys.max() + 1, xs.min():xs.max() + 1], folha[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    d = PLANTA["diametro"]
    e = d / max(sp.shape[:2])
    w, h = max(1, round(sp.shape[1] * e)), max(1, round(sp.shape[0] * e))
    sp = cv2.resize(sp, (w, h), interpolation=cv2.INTER_AREA)
    a = cv2.resize(cv2.GaussianBlur(folha.astype(np.float32), (0, 0), 1.0), (w, h), interpolation=cv2.INTER_AREA)[..., None]
    cx, cy = PLANTA["centro"]
    px, py = cx - w // 2, cy - h // 2
    reg = img[py:py + h, px:px + w].astype(np.float32)
    img[py:py + h, px:px + w] = np.clip(reg * (1 - a) + sp * a, 0, 255).astype(np.uint8)
    print(f"    planta do hall: {w}x{h} px em ({cx}, {cy})")
    return img


def bancada(img):
    x0, y0, x1, y1 = BANCADA["ret"]
    fx0, fy0, fx1, fy1 = BANCADA["fonte"]
    t = img[fy0:fy1, fx0:fx1]
    linhas = np.concatenate([t, t[::-1]] * ((y1 - y0) // (2 * t.shape[0]) + 1), axis=0)[:y1 - y0]
    tex = np.concatenate([linhas, linhas[:, ::-1]] * ((x1 - x0) // (2 * t.shape[1]) + 1), axis=1)[:, :x1 - x0]
    img[y0:y1, x0:x1] = tex
    print(f"    bancada do lavatório gourmet: {(x1 - x0) * (y1 - y0)} px no quartzo da cozinha")
    return img


def cuba(img, ret):
    x0, y0, x1, y1 = ret
    w, h = x1 - x0, y1 - y0
    cor = np.zeros((h * SS, w * SS, 3), np.float32)
    alfa = np.zeros((h * SS, w * SS), np.float32)

    def ret_arred(b, raio, c):
        bx0, by0, bx1, by1 = (int(round(v * SS)) for v in b)
        rr = min(int(round(raio * SS)), (bx1 - bx0) // 2, (by1 - by0) // 2)
        f = np.zeros(alfa.shape, np.uint8)
        cv2.rectangle(f, (bx0 + rr, by0), (bx1 - rr, by1), 255, -1)
        cv2.rectangle(f, (bx0, by0 + rr), (bx1, by1 - rr), 255, -1)
        for ccx, ccy in ((bx0 + rr, by0 + rr), (bx1 - rr, by0 + rr), (bx0 + rr, by1 - rr), (bx1 - rr, by1 - rr)):
            cv2.circle(f, (ccx, ccy), rr, 255, -1)
        cor[f > 0] = c
        alfa[f > 0] = 1

    def circulo(cx_, cy_, rr, c):
        f = np.zeros(alfa.shape, np.uint8)
        cv2.circle(f, (int(round(cx_ * SS)), int(round(cy_ * SS))), max(1, int(round(rr * SS))), 255, -1)
        cor[f > 0] = c
        alfa[f > 0] = 1

    def linha(p, q, larg, c):
        f = np.zeros(alfa.shape, np.uint8)
        cv2.line(f, (int(round(p[0] * SS)), int(round(p[1] * SS))), (int(round(q[0] * SS)), int(round(q[1] * SS))),
                 255, max(1, int(round(larg * SS))))
        cor[f > 0] = c
        alfa[f > 0] = 1

    ret_arred((0, 0, w, h), 2.5, LOUCA_CONTORNO)
    ret_arred((0.5, 0.5, w - 0.5, h - 0.5), 2.2, LOUCA)
    passos = 6
    for i in range(passos):                                   # bacia: borda mais escura indo ao fundo claro
        t = i / (passos - 1)
        c = tuple(BACIA_BORDA[k] * (1 - t) + BACIA_FUNDO[k] * t for k in range(3))
        ins = 2.2 + t * 2.0
        ret_arred((ins, ins, w - ins, h - 3.2 - t * 1.6), 2.8 - t, c)
    cx = w / 2
    circulo(cx, (h - 3.2) / 2 + 1.0, 0.75, CROMO_ESCURO)          # válvula
    circulo(cx, (h - 3.2) / 2 + 1.0, 0.5, CROMO_CLARO)
    circulo(cx, h - 1.6, 1.1, CROMO_ESCURO)                       # torneira, do lado da parede
    circulo(cx, h - 1.6, 0.85, CROMO)
    linha((cx, h - 1.6), (cx, h - 6.0), 1.0, CROMO_ESCURO)
    linha((cx, h - 1.6), (cx, h - 5.8), 0.6, CROMO_CLARO)

    c = cv2.resize(cor * alfa[..., None], (w, h), interpolation=cv2.INTER_AREA)
    a = cv2.resize(alfa, (w, h), interpolation=cv2.INTER_AREA)
    c = c / np.maximum(a, 1e-6)[..., None]
    reg = img[y0:y1, x0:x1].astype(np.float32)
    img[y0:y1, x0:x1] = np.clip(reg * (1 - a[..., None]) + c * a[..., None], 0, 255).astype(np.uint8)
    return img


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("render", type=Path)
    ap.add_argument("--saida", type=Path, default=Path("."))
    ap.add_argument("--nome", required=True)
    args = ap.parse_args()

    orig = cv2.imread(str(args.render))
    print("[1] transbordo")
    img = transbordo(orig.copy(), orig)
    print("[2] área verde")
    img = area_verde(img)
    print("[3] planta do hall")
    img = planta(img)
    print("[4] bancada e cubas do lavatório gourmet")
    img = bancada(img)
    for r in CUBAS:
        img = cuba(img, r)
    args.saida.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(args.saida / f"{args.nome}.png"), img)
    alfa = np.where(np.abs(img.astype(int) - orig.astype(int)).max(axis=2) > 0, 255, 0).astype(np.uint8)
    cv2.imwrite(str(args.saida / f"{args.nome}_camada.png"), np.dstack([img, alfa]))
    print(f"[5] {args.saida / (args.nome + '.png')}; {int((alfa > 0).sum())} px alterados")


if __name__ == "__main__":
    main()

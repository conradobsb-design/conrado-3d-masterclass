"""Casa A Térreo, 8ª leva de 25/11: o contorno bege do tracejado sobre o tapete ("sim, corrija o contorno do tracejado no
tapete").

A linha de cima do X da sala de estar (y 610,1) passa sobre o tapete redondo do jantar; ali cada traço vinha com um
contorno bege (o travertino de quando o traço foi afinado) e com a borda serrilhada, e, à esquerda do tapete, borrado
na sombra da poltrona. Na faixa da linha, de 1963 a 2100: o miolo cinza do traço achado na imagem (cinza neutro e
escuro), alargado o bastante para levar o contorno, refeito com o tapete em volta (inpaint); o traço do PDF redesenhado
por cima, com o traço do tracejado que fica (2 px a 141 na final; 0,78 px da final a 117 no 12K).

Final, prancha e 12K A e B.

  python3 terreo_casaa_2511h.py [item ...]
"""
import json
import os
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
sys.path.insert(0, str(Path(__file__).resolve().parent))
import esquadrias_pretas_1911 as EP  # noqa: E402
import vetor_2511 as V               # noqa: E402
import terreo_casaa_2511g as G       # noqa: E402

PLANTA = "A_Terreo"
TAPETE = dict(x0=1963.0, x1=2100.0, linha=610.1, meia=1.8, meia_final=2.4, dys=(4.0, 4.8, 5.6, -4.0, -4.8, -5.6), passo=7.0,
              # só na final: dois restos de traço com o contorno claro (na borda da poltrona da direita e abaixo do tapete)
              restos_final=[(2044.5, 599.5, 2052.0, 608.2), (2008.5, 617.0, 2013.0, 619.8)])


def _restos(img, s, origem, rets):
    """O miolo cinza neutro do resto de traço e o contorno claro em volta (1 px) refeitos pelo que está em volta."""
    for r in rets:
        jan = V.janela(img, r, s, origem, folga=3)
        X0, Y0, X1, Y1 = jan
        reg = img[Y0:Y1, X0:X1].copy()
        f = reg.astype(np.float32)
        miolo = ((f.max(2) - f.min(2)) < 10) & (f.mean(2) < 170)
        dentro = V.cob([V.ret(*r)], jan, s, origem) > 0.5
        m = cv2.dilate((miolo & dentro).astype(np.uint8), np.ones((3, 3), np.uint8)) & dentro.astype(np.uint8)
        img[Y0:Y1, X0:X1] = cv2.inpaint(reg, m * 255, 2.0, cv2.INPAINT_TELEA)
    return img


def _faixa_trama(img, s, origem, x0, x1, yc, meia, dys, passo):
    """A faixa x0..x1 x yc±meia refeita sem o traço e o contorno: a cor por inpaint (a borda do tapete e a sombra seguem)
    e, por cima, a trama fina da mesma faixa deslocada na vertical (trecho a trecho, o deslocamento cuja cor bate com a
    do inpaint). As poltronas (escuras e saturadas) ficam. Devolve a janela refeita, a janela e a máscara das poltronas."""
    m = max(abs(d) for d in dys) + meia + 2
    jan = V.janela(img, (x0 - 2, yc - m, x1 + 2, yc + m), s, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    reg8 = img[Y0:Y1, X0:X1].copy()
    reg = reg8.astype(np.float32)
    sat = reg.max(2) - reg.min(2)
    L = reg.mean(2)
    poltrona = (L < 135) & (sat > 14)
    xs, ys = V.coords(jan, s, origem)
    faixa = (np.abs(ys - yc) <= meia)[:, None] & ((xs >= x0) & (xs <= x1))[None, :]
    masc = faixa & ~poltrona
    inp = cv2.inpaint(reg8, masc.astype(np.uint8) * 255, max(3.0, 1.5 * s), cv2.INPAINT_TELEA).astype(np.float32)
    sig = max(0.6, 0.6 * s)
    lf = cv2.GaussianBlur(reg, (0, 0), sig)
    hf = reg - lf
    linhas = np.where(np.abs(ys - yc) <= meia)[0]
    cols = np.where((xs >= x0) & (xs <= x1))[0]
    r0, r1 = int(linhas[0]), int(linhas[-1]) + 1
    c0, c1 = int(cols[0]), int(cols[-1]) + 1
    larg = max(4, int(round(passo * s)))
    sob = max(2, int(round(0.8 * s)))
    acc = np.zeros((r1 - r0, reg.shape[1], 3), np.float32)
    pes = np.zeros((r1 - r0, reg.shape[1]), np.float32)
    alvo = cv2.GaussianBlur(inp, (0, 0), sig)
    for a in range(c0, c1, larg):
        b0, b1 = max(c0, a - sob), min(c1, a + larg + sob)
        mm = masc[r0:r1, b0:b1]
        melhor = None
        for dy in dys:
            d = int(round(dy * s))
            custo = np.mean(((lf[r0 + d:r1 + d, b0:b1] - alvo[r0:r1, b0:b1]) ** 2)[mm]) if mm.any() else 0.0
            ruim = poltrona[r0 + d:r1 + d, b0:b1].mean()          # sem a trama da poltrona
            custo += 4000.0 * ruim
            if melhor is None or custo < melhor[0]:
                melhor = (custo, hf[r0 + d:r1 + d, b0:b1])
        w = np.ones(b1 - b0, np.float32)
        rampa = np.linspace(0.15, 1.0, sob, dtype=np.float32)
        if b0 > c0:
            w[:sob] = rampa
        if b1 < c1:
            w[-sob:] = rampa[::-1]
        acc[:, b0:b1] += melhor[1] * w[None, :, None]
        pes[:, b0:b1] += w[None, :]
    trama = np.zeros_like(reg)
    trama[r0:r1] = np.where(pes[..., None] > 0, acc / np.maximum(pes, 1e-6)[..., None], 0)
    out = np.where(masc[..., None], inp + trama, reg)
    return out, jan, poltrona


def tapete_tracejado(img, s, origem, q=TAPETE):
    meia = q["meia"] if s > 1.5 else q["meia_final"]        # na final o contorno pega a linha de pixels de baixo
    out, jan, poltrona = _faixa_trama(img, s, origem, q["x0"], q["x1"], q["linha"], meia, q["dys"], q["passo"])
    a = np.zeros(out.shape[:2], np.float32)
    for p, t in G._segmentos():
        if abs(p[1] - q["linha"]) > 0.3 or abs(t[1] - q["linha"]) > 0.3:
            continue
        if max(p[0], t[0]) < q["x0"] or min(p[0], t[0]) > q["x1"]:
            continue
        a = np.maximum(a, V.cob([V.seg(p, t, G.PROJECAO["larg"] if s > 1.5 else G.PROJECAO["larg_final"])],
                                jan, s, origem))
    a *= V.cob([V.ret(q["x0"], q["linha"] - meia, q["x1"], q["linha"] + meia)], jan, s, origem)
    a *= 1.0 - poltrona                                     # o traço passa por baixo da poltrona
    out = V.compor(out, a, G.PROJECAO["cor"] if s > 1.5 else G.PROJECAO["cor_final"])
    X0, Y0, X1, Y1 = jan
    img[Y0:Y1, X0:X1] = np.clip(np.round(out), 0, 255).astype(np.uint8)
    if s < 1.5:
        img = _restos(img, s, origem, q["restos_final"])
    return img


ITENS = {"tapete_tracejado": (1955.0, 595.0, 2105.0, 625.0)}
FUNC = {"tapete_tracejado": tapete_tracejado}


def item(img, nome, escala=1.0, origem=(0.0, 0.0)):
    return FUNC[nome](img, escala, origem)


def main(so=None):
    c, pav = PLANTA.split("_")
    base = cv2.imread(str(EP.PROJ / EP.PLANTAS[PLANTA][0]))
    nomes = [n for n in ITENS if not so or n in so]
    for f in EP.PLANTAS[PLANTA]:
        im = cv2.imread(str(EP.PROJ / f))
        for nome in nomes:
            im = item(im, nome)
        cv2.imwrite(str(EP.PROJ / f), im)
        if f == EP.PLANTAS[PLANTA][0]:
            novo = im
    pf = EP.PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_entrega.png"
    pr = cv2.imread(str(pf))
    pr[:2160] = novo
    cv2.imwrite(str(pf), pr)
    dz = json.loads((EP.PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[PLANTA]
    for op in os.environ.get("OPCOES", "AB"):
        rel = EP.PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_12K_opcao_{op}.jpg"
        pil = Image.open(rel)
        dpi = pil.info.get("dpi", (743, 743))
        im = cv2.cvtColor(np.array(pil.convert("RGB")), cv2.COLOR_RGB2BGR)
        del pil
        cinza = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        for nome in nomes:
            x0, y0, x1, y1 = ITENS[nome]
            mapa, cc = EP.registro_12k(base, cinza, dz, (int(x0) - 60, int(y0) - 60, int(x1) + 60, int(y1) + 60))
            A, B = mapa(x0, y0)
            sx = (mapa(x0 + 1000.0, y0)[0] - A) / 1000.0
            im = item(im, nome, sx, (x0 - A / sx, y0 - B / sx))
            print(f"   {op}: {nome} (registro {cc:.3f}, escala {sx:.3f})")
        Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).save(rel, quality=95, subsampling=0, dpi=dpi)
        del im, cinza


if __name__ == "__main__":
    main(sys.argv[1:] or None)

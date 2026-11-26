"""Casa C Subsolo, 3ª leva de 26/11: a sombra entre os degraus da escada SOBE PARA O JARDIM, uniforme e igual em todos.

Usuário (sobre o recorte do 12K B da escada): "esse sombreamento entre degraus precisa ser uniforme e igual em todos. é
uma mancha sim, mas com efeito de igual em todos os locais". Antes, a faixa escura junto à borda de cada degrau tinha
alturas diferentes (5 px no 1º degrau e nos do L de baixo, 2 a 3 px nos degraus 3 a 6) e manchas ao longo do degrau.

Agora cada faixa (até 9 px da borda) é refeita com o Bege Bahia limpo do próprio degrau, 10 px antes da borda (o mesmo
trecho deslocado), escurecido por um perfil só, o mesmo em todas as bordas e constante ao longo de cada uma:
r(d) = 1 - 0,36 exp(-d / 1,8), d a distância à borda em px da final (0,73 rente à borda, 0,99 a 7 px), a média das
faixas de 5 px de antes; de 7 a 9 px a faixa nova passa para a de antes. As bordas (achadas na imagem, a escada não está
no PDF): os 6 degraus de cima (768, 798, 828, 858, 888 e 919, de 367 a 664), as duas do L de baixo (949, de 443 a 664, e
979, de 473 a 664) e as duas em pé (443, de 949 a 1099, e 473, de 979 a 1099), com o canto arredondado (a distância ao
canto). A borda do patamar para o 1º degrau (738), que tinha só o fio de 1 px e as manchas, recebe a mesma faixa ("eu me
refiro a esse sombreamento"). As letras sobre as faixas (o "▼ S" do 1º degrau e o JARDIM do patamar) voltam por cima,
pela cobertura de cada letra medida sobre o fundo de antes; nessas colunas a fonte do Bege Bahia vem de 22 px (S) e
95 px (JARDIM) à esquerda, sem letra.

Final, prancha e 12K A e B (pelo registro local).

  python3 subsolo_casac_2611c.py
"""
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
import um_pav_casaa_2511d as DD      # noqa: E402
import subsolo_casac_2611 as A       # noqa: E402

PLANTA = A.PLANTA
DZ = A.DZ
PERFIL = dict(A=0.36, lam=1.8, D=7.0, pena=2.0, fonte=10.0)
HORIZ = [(738.0, 366.8, 663.6), (768.0, 366.8, 663.6), (798.0, 366.8, 663.6), (828.0, 366.8, 663.6), (858.0, 366.8, 663.6),
         (888.0, 366.8, 663.6), (919.0, 366.8, 663.6), (949.0, 443.0, 663.6), (979.0, 473.0, 663.6)]
VERT = [(443.0, 949.0, 1099.0), (473.0, 979.0, 1099.0)]     # (x da borda, y do canto, y do fim)
# as letras sobre as faixas: (a caixa, o deslocamento x da fonte do Bege Bahia, as linhas onde vale)
LETRAS = [dict(caixa=(503.0, 738.6, 528.0, 765.0), dx=-22.0, y=(738.5, 790.0)),       # o "▼ S" do 1º degrau
          dict(caixa=(468.0, 712.0, 560.0, 736.7), dx=-95.0, y=(700.0, 738.5))]       # JARDIM, no patamar
# (as caixas param antes do fio da borda do patamar, 737 a 738: o fio velho não volta como letra)
RAMPA = 2.0


def _r(d, q=PERFIL):
    return 1.0 - q["A"] * np.exp(-np.maximum(d, 0.0) / q["lam"])


def degraus(img, s, origem, q=PERFIL):
    jan = V.janela(img, (355.0, 700.0, 668.0, 1102.0), s, origem, folga=int(14 * s) + 2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    H, W = reg.shape[:2]
    xs, ys = V.coords(jan, s, origem)
    X, Y = np.meshgrid(xs, ys)
    k = int(round(q["fonte"] * s))
    lim = q["D"] + q["pena"]
    # a fonte: o mesmo degrau, 10 px antes da borda (para cima nas horizontais, para a esquerda nas em pé)
    acima = np.zeros_like(reg)
    acima[k:] = reg[:-k]
    esq = np.zeros_like(reg)
    esq[:, k:] = reg[:, :-k]
    # nas colunas das letras, a fonte de cima vem também de x px à esquerda (sem a letra)
    for le in LETRAS:
        lx0, ly0, lx1, ly1 = le["caixa"]
        kx = int(round(-le["dx"] * s))
        acima_l = np.zeros_like(reg)
        acima_l[k:, kx:] = reg[:-k, :-kx]
        wl = np.clip(np.minimum(X - lx0, lx1 - X) / RAMPA + 0.5, 0, 1) * (Y > le["y"][0]) * (Y < le["y"][1])
        acima = acima * (1 - wl[..., None]) + acima_l * wl[..., None]
    # a distância à borda e de qual fonte (horizontal: 0, em pé: 1)
    dist = np.full((H, W), np.inf, np.float32)
    tipo = np.zeros((H, W), np.uint8)
    for ye, xa, xb in HORIZ:
        m = (Y < ye) & (Y > ye - lim) & (X >= xa) & (X <= xb)
        d = ye - Y
        sel = m & (d < dist)
        dist[sel] = d[sel]
        tipo[sel] = 0
    for xe, yc, yb in VERT:
        d = np.where(Y >= yc, xe - X, np.hypot(xe - X, yc - Y))
        m = (X < xe) & (X > xe - lim) & (Y > yc - lim) & (Y <= yb) & (d < lim)
        sel = m & (d < dist)
        dist[sel] = d[sel]
        tipo[sel] = 1
    dentro = np.isfinite(dist)
    dd = np.where(dentro, dist, lim)
    w = np.clip((lim - dd) / q["pena"], 0, 1) * dentro
    fonte = np.where((tipo == 1)[..., None], esq, acima)
    novo = fonte * _r(dd)[..., None]
    out = reg * (1 - w[..., None]) + novo * w[..., None]
    # as letras por cima (só onde a faixa mudou): a cobertura de cada letra, nos traços e na borda deles, sobre o fundo
    # de antes
    L = reg.mean(2)
    kk = max(int(round(0.6 * s)), 1)
    for le in LETRAS:
        lx0, ly0, lx1, ly1 = le["caixa"]
        caixa = (X >= lx0) & (X <= lx1) & (Y >= ly0) & (Y <= ly1)
        if not caixa.any():
            continue
        fundo = float(np.median(L[caixa & (L > 150)])) if (caixa & (L > 150)).any() else 170.0
        escuro = caixa & (L < 70)
        tinta = np.median(reg[escuro], axis=0) if escuro.any() else np.float32([40, 40, 42])
        traco = cv2.dilate((caixa & (L < 120)).astype(np.uint8), np.ones((2 * kk + 1, 2 * kk + 1), np.uint8)) > 0
        a = np.clip((fundo - L) / max(fundo - float(tinta.mean()), 1.0), 0, 1) * (traco & caixa & (w > 0))
        out = out * (1 - a[..., None]) + tinta[None, None, :] * a[..., None]
    img[Y0:Y1, X0:X1] = np.clip(np.round(out), 0, 255).astype(np.uint8)
    return img


FUNC = {"degraus": degraus}
ITENS = {"degraus": (355.0, 730.0, 680.0, 1105.0)}


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
    for op in os.environ.get("OPCOES", "AB"):
        rel = EP.PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_12K_opcao_{op}.jpg"
        pil = Image.open(rel)
        dpi = pil.info.get("dpi", (743, 743))
        im = cv2.cvtColor(np.array(pil.convert("RGB")), cv2.COLOR_RGB2BGR)
        del pil
        cinza = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        for nome in nomes:
            sx, org, cc = DD._registro(base, cinza, DZ, ITENS[nome])
            im = item(im, nome, sx, org)
            print(f"   {op}: {nome} (registro {cc:.3f}, escala {sx:.3f})")
        Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).save(rel, quality=95, subsampling=0, dpi=dpi)
        del im, cinza


if __name__ == "__main__":
    main(sys.argv[1:] or None)

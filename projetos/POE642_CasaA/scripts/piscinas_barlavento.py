#!/usr/bin/env python3
"""Revestimento Barlavento nas piscinas de um render já retocado (POE 642, Casas A a D).

Pedido do usuário (15/10/26), com a legenda do cliente ("revestimento Barlavento piscina"): as
piscinas de todas as casas no mesmo revestimento aprovado na Casa E (item 35 do retocado dela). O
Barlavento é a linha da Portobello que reproduz a pedra hijau, em peças de 14,5 x 14,5 cm (tom
Caribbean, entre o azul e o verde).

O que muda é só a água (piscina, prainha e spa), achada pela cor turquesa do próprio render:
- a água vira a pedra das peças (`fontes_procedurais.barlavento`) sob uma água verde-azulada clara,
  com a luz chapada (sem as manchas escuras de sombra do motor, que davam aspecto de sujo) e só uma
  sombra curta e leve junto às bordas e às peças dentro da água (espreguiçadeiras);
- os degraus e os contornos internos (prainha, degrau do spa) ficam marcados de leve, numa linha
  fina: as linhas do projeto dentro da água, tiradas da base chapada da casa alinhada ao render;
- efeitos da água, para não parecer vazia: a grade das peças ondulada pela refração, a rede de
  cáusticas do próprio render mais suave (só clareia) e um brilho difuso na diagonal;
- o que não é água fica por cima, como estava: bordas, espreguiçadeiras, linhas tracejadas de
  projeção sobre a água.

Os renders das casas estão todos na escala da base reduzida a 2000 px (~3,2 cm por px).

Uso (da pasta projetos/):
  python3 POE642_CasaA/scripts/piscinas_barlavento.py POE642_CasaD/renders/POE642_CasaD_PH_Terreo_v1_retocado.png \\
      POE642_CasaD/renders/POE642_CasaD_PH_Terreo_v1_retocado_barlavento.png \\
      --base POE642_CasaD/bases/POE642_CasaD_BASE_Terreo_v3_texturas_16x9.png \\
      --chapada POE642_CasaD/bases/POE642_CasaD_BASE_Terreo_v2_16x9.png
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
from scipy import ndimage

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

from fontes_procedurais import barlavento  # noqa: E402

# os mesmos números da Casa E (retoque_terreo_casae.PISCINAS), aprovados pelo usuário
Q = {
    "cor": (214, 222, 172),                  # BGR: água verde-azulada clara sobre a pedra
    "borda": (0.12, 1.6),                    # sombra curta junto às bordas: força e decaimento (px)
    "ondas": (1.0, 5.0),                     # refração: amplitude (px) e escala do deslocamento
    "causticas": 1.2, "suave_causticas": 0.6, "brilho": 0.04,
    "degraus": 0.16,                         # escurecimento na linha fina do degrau
    "semente": 642,
    # água no render: azulada (B acima de R; a prainha da Casa B, quase branca, tem B - R ~ 10, e a
    # borda de Bege Bahia, quente, B - R < 0), em manchas grandes
    # (a sombra antiga junto às paredes, turquesa escuro, também é água: B > 95)
    "ciano": (7, -5, 95), "area_min": 300, "escuro": 125,
    # degraus e contornos internos: as linhas do projeto dentro da água na base chapada (alinhada ao
    # render por SIFT + afim); a água nas bases é chapada, em um ou dois tons (fundo e prainha), cada
    # tom com as pequenas variações de cor entre as casas
    "agua_base": [[(254, 246, 223), (255, 247, 223)], [(255, 241, 199)]], "tol_base": 3,
}


def alinhar(img, base_textura):
    """Afim base 16:9 reduzida ao tamanho do render -> render (SIFT + afim), como nos retoques."""
    base = cv2.resize(cv2.imread(str(base_textura)), img.shape[1::-1], interpolation=cv2.INTER_AREA)
    sift = cv2.SIFT_create(10000)
    k1, d1 = sift.detectAndCompute(cv2.cvtColor(base, cv2.COLOR_BGR2GRAY), None)
    k2, d2 = sift.detectAndCompute(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), None)
    pares = [a for a, b in cv2.BFMatcher().knnMatch(d1, d2, k=2) if a.distance < 0.7 * b.distance]
    A, inl = cv2.estimateAffine2D(np.float32([k1[a.queryIdx].pt for a in pares]),
                                  np.float32([k2[a.trainIdx].pt for a in pares]), ransacReprojThreshold=2.0)
    print(f"    base alinhada: {int(inl.sum())} pontos, escala {A[0, 0]:.4f} x {A[1, 1]:.4f}")
    return A


def linhas_base(img, base_textura, chapada):
    """Linhas do projeto dentro da água (degraus da prainha e do spa), da base chapada alinhada: o
    que não é água dentro da mancha da piscina, longe da borda, e fino (as peças grandes ficam fora).
    As linhas da base têm 1 a 3 px na resolução dela (3,5 vezes a do render): as máscaras são feitas
    lá e reduzidas por área (a fração de água de cada px do render), para não sumirem na redução."""
    q = Q
    A = alinhar(img, base_textura)
    tam = img.shape[1::-1]
    ch = cv2.imread(str(chapada)).astype(np.int32)
    tons = [np.any([np.abs(ch - np.array(c)).max(axis=2) <= q["tol_base"] for c in grupo], axis=0)
            for grupo in q["agua_base"]]

    def reduz(m):
        r = cv2.resize(m.astype(np.float32), tam, interpolation=cv2.INTER_AREA)
        return cv2.warpAffine(r, A, tam, flags=cv2.INTER_LINEAR, borderValue=0)

    agua = reduz(np.any(tons, axis=0))
    cheia = agua > 0.5
    n, lab, st, _ = cv2.connectedComponentsWithStats(cheia.astype(np.uint8))
    cheia = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= q["area_min"]])
    regiao = ndimage.binary_fill_holes(cv2.morphologyEx(cheia.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8)))
    dentro = cv2.erode(regiao.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    linhas = dentro & (agua < 0.9)
    grandes = cv2.morphologyEx(linhas.astype(np.uint8), cv2.MORPH_OPEN, np.ones((4, 4), np.uint8)) > 0
    linhas &= ~(cv2.dilate(grandes.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0)
    # a fronteira entre os dois tons de água da base (fundo e prainha) também é degrau
    for i in range(len(tons)):
        for j in range(i + 1, len(tons)):
            k = np.ones((5, 5), np.uint8)
            fronteira = (cv2.dilate(tons[i].astype(np.uint8), k) > 0) & (cv2.dilate(tons[j].astype(np.uint8), k) > 0)
            linhas |= dentro & (reduz(fronteira) > 0.2)
    print(f"    linhas do projeto dentro da água: {int(linhas.sum())} px")
    return linhas


def mascara_agua(img):
    """(água, contorno da piscina com as peças grandes dentro)."""
    q = Q
    b, g, r = [img[..., i].astype(np.int32) for i in range(3)]
    db, dg, bmin = q["ciano"]
    ciano = ((b - r > db) & (g - r > dg) & (b > bmin)).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(ciano)
    ciano = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= q["area_min"]])
    # a mancha da água: os reflexos brancos e as linhas finas dentro dela entram (fechamento e furos)
    regiao = cv2.morphologyEx(ciano.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    regiao = ndimage.binary_fill_holes(regiao)
    Y = img.astype(np.float32).mean(axis=2)
    # o contorno escuro do render junto às bordas (1 px) entra na água, para não sobrar em entalhes
    anel = (cv2.dilate(regiao.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0) & ~regiao & (Y < 160)
    regiao |= anel
    nao = regiao & ~ciano
    # peças grandes (espreguiçadeiras): o que não é água e sobrevive à abertura 5 x 5
    # (sem a sombra difusa delas no render, que ficaria como um halo claro em volta: as peças são
    # o miolo claro e o contorno escuro; a sombra curta das bordas faz o assentamento na água)
    grandes = cv2.morphologyEx(nao.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)) > 0
    sat = img.max(axis=2).astype(np.int32) - img.min(axis=2)
    halo = grandes & (sat > 6) & (img[..., 0].astype(np.int32) - img[..., 2] > 0)
    grandes &= ~halo
    # traços escuros (tracejados de projeção): ficam por cima; junto às bordas não (lá o contorno
    # escuro do render vira a sombra curta, sem sobrar entalhes)
    perto = cv2.distanceTransform(regiao.astype(np.uint8), cv2.DIST_L2, 3) <= 2.5
    escuros = regiao & (Y < q["escuro"]) & ~ciano & ~perto
    escuros = cv2.dilate(escuros.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    agua = regiao & ~grandes & ~escuros
    return agua, regiao & ~grandes


def pedra_ondulada(h, wd):
    """A pedra das peças sob a água (cor da água), com a grade ondulada pela refração."""
    q = Q
    pedra = barlavento(h + 8, wd + 8, semente=q["semente"]) * np.float32(q["cor"])
    rng = np.random.default_rng(q["semente"])
    amp, sig = q["ondas"]
    dx, dy = (cv2.GaussianBlur(rng.normal(0, 1, (h, wd)).astype(np.float32), (0, 0), sig) for _ in range(2))
    dx, dy = dx * amp / max(float(dx.std()), 1e-6), dy * amp / max(float(dy.std()), 1e-6)
    gy, gx = np.mgrid[0:h, 0:wd].astype(np.float32)
    return cv2.remap(pedra, gx + 4 + dx, gy + 4 + dy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def causticas(Y, w):
    """A rede de cáusticas do próprio render (Y), mais suave: o que clareia sobre a média local da
    água (peso w), só para cima."""
    q = Q
    media = cv2.GaussianBlur(Y * w, (0, 0), 4.0) / np.maximum(cv2.GaussianBlur(w, (0, 0), 4.0), 1e-3)
    return cv2.GaussianBlur(np.clip(Y - media, 0, None), (0, 0), q["suave_causticas"]) * q["causticas"]


def brilho_diagonal(h, wd):
    gy, gx = np.mgrid[0:h, 0:wd].astype(np.float32)
    diag = ((gx / max(wd - 1, 1)) + (gy / max(h - 1, 1))) / 2
    return 1 + Q["brilho"] * (1 - diag)


def aplicar(img, linhas):
    q = Q
    agua, limite = mascara_agua(img)
    linhas = linhas & limite
    ys, xs = np.nonzero(agua)
    x0, y0 = max(xs.min() - 8, 0), max(ys.min() - 8, 0)
    x1, y1 = min(xs.max() + 9, img.shape[1]), min(ys.max() + 9, img.shape[0])
    m, lim_, ln = agua[y0:y1, x0:x1], limite[y0:y1, x0:x1], linhas[y0:y1, x0:x1]
    reg = img[y0:y1, x0:x1].astype(np.float32)
    Y = reg.mean(axis=2)
    w = m.astype(np.float32)
    h, wd = Y.shape
    forca, dec = q["borda"]
    dist = cv2.distanceTransform(lim_.astype(np.uint8), cv2.DIST_L2, 3)
    luz = 1 - forca * np.exp(-np.maximum(dist - 0.5, 0) / dec)
    # degraus: a linha fina do render, suavizada, escurece de leve (sem a mancha larga em volta)
    luz *= 1 - q["degraus"] * np.clip(cv2.GaussianBlur(ln.astype(np.float32), (0, 0), 0.6) * 1.6, 0, 1)
    pedra = pedra_ondulada(h, wd)
    caust = causticas(Y, w)
    caust *= np.clip(dist - 1.0, 0, 1)               # sem o reflexo da borda clara colada à água
    brilho = brilho_diagonal(h, wd)
    novo = pedra * (luz * brilho)[..., None] + caust[..., None] * np.float32([1.0, 1.0, 0.92])
    a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.5)
    a = np.maximum(a, m) * lim_                      # não passa para as bordas nem para as peças
    out = img.copy()
    out[y0:y1, x0:x1] = np.clip(reg * (1 - a[..., None]) + novo * a[..., None], 0, 255).astype(np.uint8)
    print(f"    Barlavento em {int(m.sum())} px de água")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entrada", type=Path)
    ap.add_argument("saida", type=Path)
    ap.add_argument("--base", type=Path, required=True, help="base 16:9 com texturas (para o alinhamento)")
    ap.add_argument("--chapada", type=Path, required=True, help="base 16:9 chapada (água em cor única)")
    args = ap.parse_args()
    img = cv2.imread(str(args.entrada))
    out = aplicar(img, linhas_base(img, args.base, args.chapada))
    cv2.imwrite(str(args.saida), out)
    print(f"[fim] {args.saida}")


if __name__ == "__main__":
    main()

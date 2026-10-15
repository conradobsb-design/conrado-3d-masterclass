#!/usr/bin/env python3
"""Retoque sem IA do render do Térreo da Casa D (prompt v1). A imagem final é o render.

Os itens são corrigidos um a um, na ordem pedida pelo usuário.

1. Porta pivotante principal (entre o hall de entrada e o estar): o motor cortou a folha no
   alinhamento da parede; no PDF ela vai de ponta a ponta, passando para o lado do hall até o arco
   pequeno. A folha é estendida com o próprio trecho dela (mesmas linhas) até o fim do PDF, onde o
   arco pequeno do render já começa. Mesmo caso da Casa C.
2. Chuveiros do banho master: o motor ligou os dois chuveiros numa barra de parede a parede. No PDF
   (ARQ_LOUÇAS E METAIS) são duas duchas quadradas de ~19 cm, cada uma num braço que sai da parede
   lateral (a da esquerda e a da direita). A barra sai, com o texto ilegível que o motor pôs junto à
   parede de baixo (as linhas viram o piso limpo de cima, em espelho, que já tem a sombra da parede
   da direita), e entram as duchas na placa aprovada da Casa A
   reduzida, com sombra curta, o braço cromado da parede até o centro da ducha e a canopla na parede.

As coordenadas estão em px do render (2000 x 1116).

Uso:
  python retoque_terreo_casad.py RENDER.webp --saida PASTA --nome NOME
"""
import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import pymupdf

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent          # projetos/
sys.path.insert(0, str(AQUI))
from retoque_terreo_casac import CHUVEIRO_TETO, CROMO, CROMO_CLARO, CROMO_ESCURO, SS  # noqa: E402

BASE = RAIZ / "POE642_CasaD/bases/POE642_CasaD_BASE_Terreo_v3_texturas_16x9.png"
BASE_CHAPADA = RAIZ / "POE642_CasaD/bases/POE642_CasaD_BASE_Terreo_v2_16x9.png"   # cores exatas da legenda
BASE_SEM_TELA = RAIZ / "POE642_CasaD/bases/POE642_CasaD_BASE_Terreo_v2.png"          # antes da tela 16:9
PDF = RAIZ / "_pdfs_cliente/642 - TÉRREO - CASA D.pdf"
CONFIG = RAIZ / "POE642_CasaD/config_bases.json"

# porta pivotante principal: linhas da folha, trecho da folha copiado e a parte que faltou (até o
# fim da folha no PDF, onde o arco pequeno do render começa)
PIVOTANTE = {"linhas": (567, 571), "fonte_x": 1240, "de": 1267, "ate": 1282}
# chuveiros do banho master: a barra do motor (com os registros, a sombra e o texto ilegível que o
# motor escreveu junto à parede de baixo), refeita com as linhas limpas de cima (em espelho); duchas,
# braços e canoplas do PDF (ARQ_LOUÇAS E METAIS, em px do render)
CHUVEIROS_BHM = {
    "barra": (403, 882, 458, 902),
    "emenda": 0,
    "duchas": [
        {"nome": "esquerda", "ducha": (411.9, 886.1, 418.0, 892.3), "braco": (403.0, 415.0, 889.2),
         "canopla": (403.0, 888.2, 404.0, 890.2)},
        {"nome": "direita", "ducha": (442.7, 886.2, 448.8, 892.4), "braco": (445.7, 457.7, 889.3),
         "canopla": (456.7, 888.3, 457.7, 890.3)},
    ],
    "larg_braco": 0.8,
    "sombra": {"desloc": (-1.0, 1.0), "sigma": 0.8, "forca": 0.3},
}


def alinhar_base(render):
    """Base 16:9 reduzida e levada ao render por SIFT + afim; também a base chapada (v2)."""
    base = cv2.resize(cv2.imread(str(BASE)), render.shape[1::-1], interpolation=cv2.INTER_AREA)
    sift = cv2.SIFT_create(10000)
    k1, d1 = sift.detectAndCompute(cv2.cvtColor(base, cv2.COLOR_BGR2GRAY), None)
    k2, d2 = sift.detectAndCompute(cv2.cvtColor(render, cv2.COLOR_BGR2GRAY), None)
    pares = [a for a, b in cv2.BFMatcher().knnMatch(d1, d2, k=2) if a.distance < 0.7 * b.distance]
    A, inl = cv2.estimateAffine2D(np.float32([k1[a.queryIdx].pt for a in pares]),
                                  np.float32([k2[a.trainIdx].pt for a in pares]), ransacReprojThreshold=2.0)
    print(f"    base alinhada: {int(inl.sum())} pontos, escala {A[0, 0]:.4f} x {A[1, 1]:.4f}")
    chapada = cv2.resize(cv2.imread(str(BASE_CHAPADA)), render.shape[1::-1], interpolation=cv2.INTER_NEAREST)
    return (cv2.warpAffine(base, A, render.shape[1::-1], flags=cv2.INTER_LINEAR, borderValue=(255, 255, 255)),
            cv2.warpAffine(chapada, A, render.shape[1::-1], flags=cv2.INTER_NEAREST, borderValue=(255, 255, 255)),
            A)


def pdf_cadeia(A, forma_render):
    """Página do PDF e a conversão PDF -> render pela mesma cadeia da base (recorte, largura da
    base, tela 16:9, redução ao tamanho do render e o afim A)."""
    cfg = json.loads(CONFIG.read_text())
    pg = pymupdf.open(PDF)[cfg["pavimentos"]["Terreo"]["pagina"]]
    fx0, fy0, fx1, fy1 = cfg["recorte"]
    clip = pymupdf.Rect(pg.rect.width * fx0, pg.rect.height * fy0, pg.rect.width * fx1, pg.rect.height * fy1)
    zoom = cfg["largura_px"] / clip.width
    hb, wb = cv2.imread(str(BASE_SEM_TELA), cv2.IMREAD_GRAYSCALE).shape
    ht, wt = cv2.imread(str(BASE_CHAPADA), cv2.IMREAD_GRAYSCALE).shape
    sx, sy = forma_render[1] / wt, forma_render[0] / ht

    def p2r(x, y):
        bx, by = ((x - clip.x0) * zoom + (wt - wb) // 2) * sx, ((y - clip.y0) * zoom + (ht - hb) // 2) * sy
        return A[0, 0] * bx + A[0, 1] * by + A[0, 2], A[1, 0] * bx + A[1, 1] * by + A[1, 2]

    return pg, p2r


def pivotante(out):
    q = PIVOTANTE
    y0, y1 = q["linhas"]
    de, ate, fx = q["de"], q["ate"], q["fonte_x"]
    out[y0:y1, de:ate] = out[y0:y1, fx:fx + ate - de]
    print(f"    porta pivotante: folha estendida até o fim do PDF (x {ate})")
    return out


def chuveiros_bhm(out):
    q = CHUVEIROS_BHM
    x0, y0, x1, y1 = q["barra"]
    n = y1 - y0
    out[y0:y1, x0:x1] = out[y0 - n:y0, x0:x1][::-1]          # piso limpo de cima, em espelho
    e = q["emenda"]
    for k in range(e):                                        # emenda suave embaixo
        t = (k + 1) / (e + 1)
        y = y1 - e + k
        out[y, x0:x1] = np.clip(out[y, x0:x1] * (1 - t) + out[y1 + k, x0:x1] * t, 0, 255).astype(np.uint8)

    wx0, wy0, wx1, wy1 = x0, y0, x1, y1
    h, w = wy1 - wy0, wx1 - wx0

    def px(v, o=0.0):
        return int(round((v - o) * SS))

    reg = out[wy0:wy1, wx0:wx1].astype(np.float32)

    def pintar(mascara, cor):
        nonlocal reg
        a = cv2.resize(mascara.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None]
        reg = reg * (1 - a) + np.array(cor, np.float32) * a

    img = cv2.imread(str(CHUVEIRO_TETO[0]))
    hx0, hy0, hx1, hy1 = CHUVEIRO_TETO[1]
    s = q["sombra"]
    for d in q["duchas"]:
        dx0, dy0, dx1, dy1 = d["ducha"]
        ducha = np.zeros((h * SS, w * SS), np.uint8)
        cv2.rectangle(ducha, (px(dx0, wx0), px(dy0, wy0)), (px(dx1, wx0), px(dy1, wy0)), 255, -1)
        M = np.float32([[1, 0, s["desloc"][0] * SS], [0, 1, s["desloc"][1] * SS]])
        sombra = cv2.GaussianBlur(cv2.warpAffine(ducha.astype(np.float32), M, (w * SS, h * SS)), (0, 0),
                                  s["sigma"] * SS) / 255
        reg *= (1 - s["forca"] * cv2.resize(sombra, (w, h), interpolation=cv2.INTER_AREA))[..., None]

        placa = cv2.resize(img[hy0:hy1, hx0:hx1], (px(dx1 - dx0), px(dy1 - dy0)), interpolation=cv2.INTER_CUBIC)
        cor = np.zeros((h * SS, w * SS, 3), np.uint8)
        cor[px(dy0, wy0):px(dy0, wy0) + placa.shape[0], px(dx0, wx0):px(dx0, wx0) + placa.shape[1]] = placa
        a = cv2.resize(ducha.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None]
        c = cv2.resize(cor.astype(np.float32) * (ducha[..., None] / 255), (w, h), interpolation=cv2.INTER_AREA)
        c = c / np.maximum(a, 1e-6)
        reg = reg * (1 - a) + c * a

        bx0, bx1, by = d["braco"]                             # braço por cima da ducha, até o centro
        braco = np.zeros_like(ducha)
        cv2.line(braco, (px(bx0, wx0), px(by, wy0)), (px(bx1, wx0), px(by, wy0)), 255, px(q["larg_braco"]))
        brilho = np.zeros_like(ducha)
        cv2.line(brilho, (px(bx0, wx0), px(by - 0.1, wy0)), (px(bx1, wx0), px(by - 0.1, wy0)), 255, max(1, px(0.3)))
        pintar(braco, CROMO_ESCURO)
        pintar(brilho, CROMO_CLARO)
        cx0, cy0, cx1, cy1 = d["canopla"]
        canopla = np.zeros_like(ducha)
        cv2.rectangle(canopla, (px(cx0, wx0), px(cy0, wy0)), (px(cx1, wx0), px(cy1, wy0)), 255, -1)
        pintar(canopla, CROMO)
        print(f"    banho master, chuveiro da {d['nome']}: ducha, braço da parede e canopla do PDF")
    out[wy0:wy1, wx0:wx1] = np.clip(reg, 0, 255).astype(np.uint8)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("render", type=Path)
    ap.add_argument("--saida", type=Path, default=Path("."))
    ap.add_argument("--nome", required=True)
    args = ap.parse_args()

    orig = cv2.imread(str(args.render))
    out = orig.copy()
    print("[1] porta pivotante principal")
    out = pivotante(out)
    print("[2] chuveiros do banho master")
    out = chuveiros_bhm(out)

    args.saida.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(args.saida / f"{args.nome}.png"), out)
    alfa = np.where(np.abs(out.astype(int) - orig.astype(int)).max(axis=2) > 0, 255, 0).astype(np.uint8)
    cv2.imwrite(str(args.saida / f"{args.nome}_camada.png"), np.dstack([out, alfa]))
    print(f"[fim] {args.saida / (args.nome + '.png')}; {int((alfa > 0).sum())} px alterados")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Retoques locais, sem IA, no render v1 do Subsolo da Casa E (POE 642).

O render (Nano Banana Pro, 2000 x 1116, fundo branco: base v3 + prompt v1) manteve a escala da base:
a base 16:9 reduzida ao tamanho do render cai nele quase pela identidade. Os retoques são feitos no
quadro do render, como no Térreo e no 1º Pavimento.

Itens (o mapa está em POE642_CasaE/renders/POE642_CasaE_PH_Subsolo_v1_erros.jpg): ver ITENS e o
handoff (POE642_HANDOFF_SESSAO_LOCAL.md, "Casa E · Subsolo").

Uso (da pasta POE642_CasaA/scripts/):
  python3 retoque_subsolo_casae.py ../../POE642_CasaE/renders/POE642_CasaE_PH_Subsolo_v1_render.webp \\
      --saida ../../POE642_CasaE/renders --nome POE642_CasaE_PH_Subsolo_v1_retocado
  python3 retoque_subsolo_casae.py <render> --mapa ../../POE642_CasaE/renders/POE642_CasaE_PH_Subsolo_v1_erros.jpg
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

from retoque_terreo_casab import BACIA_BORDA, BACIA_FUNDO, LOUCA, LOUCA_CONTORNO  # noqa: E402
from retoque_terreo_casac import CHUVEIRO_TETO, CROMO, CROMO_CLARO, CROMO_ESCURO  # noqa: E402

BASE = RAIZ / "POE642_CasaE/bases/POE642_CasaE_BASE_Subsolo_v3_texturas_16x9.png"
BASE_CHAPADA = RAIZ / "POE642_CasaE/bases/POE642_CasaE_BASE_Subsolo_v2_16x9.png"   # cores exatas da legenda
BASE_SEM_TELA = RAIZ / "POE642_CasaE/bases/POE642_CasaE_BASE_Subsolo_v2.png"          # antes da tela 16:9
PDF = RAIZ / "_pdfs_cliente/642 - SUBSOLO - CASA E.pdf"
CONFIG = RAIZ / "POE642_CasaE/config_bases.json"


def alinhar_base(render):
    """Base 16:9 reduzida ao tamanho do render e levada a ele por SIFT + afim (como nas outras casas)."""
    base = cv2.resize(cv2.imread(str(BASE)), render.shape[1::-1], interpolation=cv2.INTER_AREA)
    sift = cv2.SIFT_create(10000)
    k1, d1 = sift.detectAndCompute(cv2.cvtColor(base, cv2.COLOR_BGR2GRAY), None)
    k2, d2 = sift.detectAndCompute(cv2.cvtColor(render, cv2.COLOR_BGR2GRAY), None)
    pares = [a for a, b in cv2.BFMatcher().knnMatch(d1, d2, k=2) if a.distance < 0.7 * b.distance]
    A, inl = cv2.estimateAffine2D(np.float32([k1[a.queryIdx].pt for a in pares]),
                                  np.float32([k2[a.trainIdx].pt for a in pares]), ransacReprojThreshold=2.0)
    print(f"    base alinhada: {int(inl.sum())} pontos, escala {A[0, 0]:.4f} x {A[1, 1]:.4f}")
    return A


def pdf_cadeia(A, forma_render):
    """Página do PDF e as conversões PDF -> render e render -> PDF pela mesma cadeia da base (recorte,
    largura da base, tela 16:9, redução ao tamanho do render e o afim A), como no 1º Pavimento."""
    cfg = json.loads(CONFIG.read_text())
    pg = pymupdf.open(PDF)[cfg["pavimentos"]["Subsolo"]["pagina"]]
    fx0, fy0, fx1, fy1 = cfg["recorte"]
    clip = pymupdf.Rect(pg.rect.width * fx0, pg.rect.height * fy0, pg.rect.width * fx1, pg.rect.height * fy1)
    zoom = cfg["largura_px"] / clip.width
    hb, wb = cv2.imread(str(BASE_SEM_TELA), cv2.IMREAD_GRAYSCALE).shape
    ht, wt = cv2.imread(str(BASE_CHAPADA), cv2.IMREAD_GRAYSCALE).shape
    sx, sy = forma_render[1] / wt, forma_render[0] / ht
    Ai = np.linalg.inv(np.vstack([A, [0, 0, 1]]))

    def p2r(x, y):
        bx, by = ((x - clip.x0) * zoom + (wt - wb) // 2) * sx, ((y - clip.y0) * zoom + (ht - hb) // 2) * sy
        return A[0, 0] * bx + A[0, 1] * by + A[0, 2], A[1, 0] * bx + A[1, 1] * by + A[1, 2]

    def r2p(x, y):
        bx, by, _ = Ai @ [x, y, 1]
        return (bx / sx - (wt - wb) // 2) / zoom + clip.x0, (by / sy - (ht - hb) // 2) / zoom + clip.y0

    return pg, p2r, r2p


SS = 8                             # supersampling dos desenhos finos


def chapada_no_render(A, forma):
    """A base chapada (cores exatas da legenda) no quadro do render, sem misturar cores (vizinho mais próximo)."""
    ch = cv2.resize(cv2.imread(str(BASE_CHAPADA)), forma[1::-1], interpolation=cv2.INTER_NEAREST)
    return cv2.warpAffine(ch, A, forma[1::-1], flags=cv2.INTER_NEAREST, borderValue=(255, 255, 255))


def texturas_no_render(A, forma):
    """A base v3 (as texturas aprovadas, na escala do render) no quadro do render."""
    b = cv2.resize(cv2.imread(str(BASE)), forma[1::-1], interpolation=cv2.INTER_AREA)
    return cv2.warpAffine(b, A, forma[1::-1], flags=cv2.INTER_LINEAR, borderValue=(255, 255, 255))


def caixa_pdf(p2r, x0, y0, x1, y1, folga=0):
    (a0, b0), (a1, b1) = p2r(x0, y0), p2r(x1, y1)
    return int(np.floor(a0)) - folga, int(np.floor(b0)) - folga, int(np.ceil(a1)) + folga, int(np.ceil(b1)) + folga


def trocar_piso(out, mascara, tex, cor, borda=0.6, buracos=None):
    """Os px da máscara viram a textura aprovada da base (normalizada, média 1 por canal) na cor dada
    (a cor média do material no próprio render), com a borda suavizada. Em 'buracos' (px da máscara que
    na base não são piso: folhas e soleiras de porta), a textura é preenchida a partir do piso em volta."""
    # também os traços finos da base que a base chapada (vizinho mais próximo) não pega: px da textura
    # bem mais escuros ou mais claros que o piso
    lum = tex.astype(np.float32).mean(axis=2)
    med = np.median(lum[mascara])
    fora = mascara & ((lum < 0.85 * med) | (lum > 1.08 * med))
    buracos = fora if buracos is None else (buracos | fora)
    if buracos.any():
        tex = cv2.inpaint(tex, cv2.dilate((buracos & mascara).astype(np.uint8), np.ones((3, 3), np.uint8)),
                          3, cv2.INPAINT_TELEA)
    m = mascara.astype(np.float32)
    if borda:
        m = np.maximum(cv2.GaussianBlur(m, (0, 0), borda), m) * cv2.dilate(mascara.astype(np.uint8), np.ones((3, 3), np.uint8))
    t = tex.astype(np.float32)
    media = t[mascara].mean(axis=0)
    novo = t / media * np.asarray(cor, np.float32)
    out[:] = np.clip(out * (1 - m[..., None]) + novo * m[..., None], 0, 255).astype(np.uint8)
    return out


def pintar(reg, alfa, cor):
    """Pinta uma cor sobre a região com a cobertura alfa (0..1)."""
    reg[:] = reg * (1 - alfa[..., None]) + np.asarray(cor, np.float32) * alfa[..., None]


def tracos(h, w, x0, y0, curvas, larg):
    """Cobertura (0..1) de polilinhas em px do render, desenhadas em SS x."""
    f = np.zeros((h * SS, w * SS), np.uint8)
    for c in curvas:
        cv2.polylines(f, [np.round((np.asarray(c) - [x0, y0]) * SS).astype(np.int32)], False, 255,
                      max(1, int(round(larg * SS))), cv2.LINE_AA)
    return cv2.resize(f.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)


def arco_pdf(pg, p2r, caixa):
    """A curva de um arco de porta do PDF (a bbox dada, em pt) em px do render."""
    for d in pg.get_drawings():
        r = d["rect"]
        if abs(r.x0 - caixa[0]) < 0.3 and abs(r.y0 - caixa[1]) < 0.3 and abs(r.x1 - caixa[2]) < 0.3 \
                and abs(r.y1 - caixa[3]) < 0.3 and any(it[0] == "c" for it in d["items"]):
            curvas = []
            for it in d["items"]:
                if it[0] == "c":
                    pp = np.array([p2r(v.x, v.y) for v in it[1:5]])
                    tt = np.linspace(0, 1, 60)[:, None]
                    curvas.append((1 - tt) ** 3 * pp[0] + 3 * (1 - tt) ** 2 * tt * pp[1]
                                  + 3 * (1 - tt) * tt ** 2 * pp[2] + tt ** 3 * pp[3])
            return curvas
    raise ValueError(f"arco não achado no PDF: {caixa}")


# portas: folha (retângulo do PDF, em pt), arco (bbox do arco do PDF) e o piso em que estão
PORTA = {"folha": (236, 237, 236), "contorno": (96, 98, 100), "larg_contorno": 0.35,
         "arco": {"bege": ((128, 130, 132), 0.5), "granito": ((160, 161, 160), 0.45), "vinilico": ((160, 161, 160), 0.45)}}


def desenhar_porta(out, pg, p2r, folha, arco, piso):
    q = PORTA
    curvas = arco_pdf(pg, p2r, arco)
    x0, y0, x1, y1 = caixa_pdf(p2r, min(folha[0], arco[0]), min(folha[1], arco[1]),
                               max(folha[2], arco[2]), max(folha[3], arco[3]), folga=3)
    h, w = y1 - y0, x1 - x0
    reg = out[y0:y1, x0:x1].astype(np.float32)
    cor, larg = q["arco"][piso]
    pintar(reg, tracos(h, w, x0, y0, curvas, larg), cor)
    (a0, b0), (a1, b1) = p2r(folha[0], folha[1]), p2r(folha[2], folha[3])
    f = np.zeros((h * SS, w * SS), np.uint8)
    p0, p1 = (round((a0 - x0) * SS), round((b0 - y0) * SS)), (round((a1 - x0) * SS), round((b1 - y0) * SS))
    cv2.rectangle(f, p0, p1, 255, -1)
    pintar(reg, cv2.resize(f.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA), q["folha"])
    f[:] = 0
    cv2.rectangle(f, p0, p1, 255, max(1, round(q["larg_contorno"] * SS)))
    pintar(reg, cv2.resize(f.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA), q["contorno"])
    out[y0:y1, x0:x1] = np.clip(reg, 0, 255).astype(np.uint8)
    return out


# item 1: circulação e depósito no Bege Bahia aprovado; sem a parede que o motor pôs na borda da esquerda
BEGE = {"cor": (191, 208, 223),            # BGR: o Bege Bahia do próprio render (mediana da circulação da direita)
        "legenda": (232, 232, 232), "tol": 3,
        "regioes_pdf": [(690, 510, 1560, 690), (1560, 525, 1830, 693)],   # circulação; depósito
        "borda_esq_pdf": (694.0, 515.0, 685.0),                            # x, y0, y1 da borda sem parede
        "cor_borda": (168, 178, 180),                                       # a linha cinza da borda de cima
        "portas": [((1564.5, 564.7, 1602.6, 567.0), (1564.5, 564.7, 1602.6, 602.8)),    # depósito, folha de cima
                   ((1564.5, 638.6, 1602.6, 640.9), (1564.5, 602.8, 1602.6, 640.9))],  # e de baixo
        "soleiras_pdf": [(1556.0, 564.5, 1564.5, 641.0)]}   # o vão na espessura da parede: piso contínuo


def circulacao_deposito(out, A, pg, p2r, chapada, tex):
    q = BEGE
    piso = np.abs(chapada.astype(int) - q["legenda"]).max(axis=2) <= q["tol"]
    m = np.zeros(piso.shape, bool)
    for r in q["regioes_pdf"]:
        x0, y0, x1, y1 = caixa_pdf(p2r, *r)
        m[y0:y1, x0:x1] = True
    m &= piso
    # nas portas, também o que a base não tem como piso (folhas e arcos antigos, sombras), menos as paredes
    parede = chapada.max(axis=2) < 60
    for folha, arco in q["portas"]:
        x0, y0, x1, y1 = caixa_pdf(p2r, min(folha[0], arco[0]), min(folha[1], arco[1]),
                                   max(folha[2], arco[2]), max(folha[3], arco[3]), folga=1)
        m[y0:y1, x0:x1] |= ~parede[y0:y1, x0:x1]
    for s in q["soleiras_pdf"]:
        x0, y0, x1, y1 = caixa_pdf(p2r, *s)
        m[y0:y1, x0:x1] |= ~parede[y0:y1, x0:x1]
    # o contorno da escada (o render tinha uma linha em volta): a faixa de 2 px em volta dos degraus
    ex0, ey0, ex1, ey1 = caixa_pdf(p2r, *ESCADA["pdf"])
    anel = np.zeros_like(m)
    anel[ey0 - 2:ey1 + 2, ex0 - 2:ex1 + 2] = True
    anel[ey0 + 1:ey1 - 1, ex0 + 1:ex1 - 1] = False
    m |= anel & ~parede
    out = trocar_piso(out, m, tex, q["cor"], buracos=m & ~piso)
    # a borda da esquerda: onde o motor pôs a parede, a linha fina do contorno do piso, como a de cima
    bx, by0, by1 = q["borda_esq_pdf"]
    (xa, ya), (_, yb) = p2r(bx, by0), p2r(bx, by1)
    xi = int(round(xa))
    out[int(np.ceil(ya)):int(yb), xi] = q["cor_borda"]
    out[int(np.ceil(ya)):int(yb), xi - 6:xi] = 255
    # no canto de cima, o topo da parede do motor: as linhas de cima repetem o perfil limpo logo à direita
    yt = int(round(ya))
    out[yt - 2:yt + 2, xi + 1:xi + 20] = out[yt - 2:yt + 2, xi + 30:xi + 31]
    out[yt - 1:yt + 1, xi] = q["cor_borda"]
    for folha, arco in q["portas"]:
        out = desenhar_porta(out, pg, p2r, folha, arco, "bege")
    print(f"    Bege Bahia aprovado em {int(m.sum())} px (circulação e depósito); borda da esquerda sem parede")
    return out


# item 2: escada. É a mesma escada externa do Térreo (no mesmo lugar da folha), já aprovada lá (item 21
# do Térreo: sem linhas, com o sombreamento de descida da direita para a esquerda). O trecho dela vem do
# Térreo retocado, levado ao quadro deste render pelas duas bases (Térreo e Subsolo têm o mesmo quadro);
# a sombra curta do primeiro espelho cai na circulação, à esquerda, como no Térreo.
ESCADA = {"terreo": RAIZ / "POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_retocado.png",
          "base_terreo": RAIZ / "POE642_CasaE/bases/POE642_CasaE_BASE_Terreo_v3_texturas_16x9.png",
          "pdf": (972.0, 617.0, 1262.9, 685.0),          # os degraus (ARQ_ESCADAS E RAMPAS)
          "sombra": (0.18, 2.0), "alcance": 8}           # do 1º espelho: força, decaimento e alcance (px)


def alinhar(img, base_png):
    b = cv2.resize(cv2.imread(str(base_png)), img.shape[1::-1], interpolation=cv2.INTER_AREA)
    sift = cv2.SIFT_create(10000)
    k1, d1 = sift.detectAndCompute(cv2.cvtColor(b, cv2.COLOR_BGR2GRAY), None)
    k2, d2 = sift.detectAndCompute(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), None)
    pares = [a for a, c in cv2.BFMatcher().knnMatch(d1, d2, k=2) if a.distance < 0.7 * c.distance]
    M, inl = cv2.estimateAffine2D(np.float32([k1[a.queryIdx].pt for a in pares]),
                                  np.float32([k2[a.trainIdx].pt for a in pares]), ransacReprojThreshold=2.0)
    return M, int(inl.sum())


def terreo_no_render(A, forma):
    """O Térreo retocado (aprovado) levado ao quadro deste render pelas duas bases (mesmo quadro)."""
    q = ESCADA
    t = cv2.imread(str(q["terreo"]))
    At, n = alinhar(t, q["base_terreo"])
    M = (np.vstack([At, [0, 0, 1]]) @ np.linalg.inv(np.vstack([A, [0, 0, 1]])))[:2]     # este render -> Térreo
    return cv2.warpAffine(t, M, forma[1::-1], flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP,
                          borderValue=(255, 255, 255)), n


def cobertura(forma, p2r, rets):
    """Fração (0..1) de cada px do render coberta pela união dos retângulos do PDF (em pt), em SS x."""
    h, w = forma[:2]
    xs = [p2r(r[0], r[1])[0] for r in rets] + [p2r(r[2], r[3])[0] for r in rets]
    ys = [p2r(r[0], r[1])[1] for r in rets] + [p2r(r[2], r[3])[1] for r in rets]
    x0, y0, x1, y1 = int(min(xs)) - 2, int(min(ys)) - 2, int(np.ceil(max(xs))) + 2, int(np.ceil(max(ys))) + 2
    m = np.zeros(((y1 - y0) * SS, (x1 - x0) * SS), np.uint8)
    for r in rets:
        (a, b), (c, d) = p2r(r[0], r[1]), p2r(r[2], r[3])
        cv2.rectangle(m, (round((a - x0) * SS), round((b - y0) * SS)), (round((c - x0) * SS) - 1, round((d - y0) * SS) - 1), 255, -1)
    a = np.zeros((h, w), np.float32)
    a[y0:y1, x0:x1] = cv2.resize(m.astype(np.float32) / 255, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)
    return a


# item 5: elevador. O motor fez a caixa com piso de mármore e um quadrado claro, sem cabine. É o mesmo
# elevador do Térreo, no mesmo lugar da folha e com a porta para o mesmo lado (para baixo): o miolo da
# caixa e o vão da porta (até a face de fora da parede) vêm do Térreo aprovado.
ELEVADOR = {"caixa": (1734.6, 906.1, 1825.3, 996.8), "vao": (1760.1, 996.8, 1799.8, 1005.3)}


def elevador(out, A, p2r, tw):
    q = ELEVADOR
    a = cobertura(out.shape, p2r, [q["caixa"], q["vao"]])[..., None]
    out[:] = np.clip(out * (1 - a) + tw * a, 0, 255).astype(np.uint8)
    print(f"    elevador do Térreo aprovado: {int((a > 0.5).sum())} px")
    return out


def escada(out, A, p2r):
    q = ESCADA
    tw, n = terreo_no_render(A, out.shape)
    (xa, ya), (xb, yb) = p2r(q["pdf"][0], q["pdf"][1]), p2r(q["pdf"][2], q["pdf"][3])
    x0, y0, x1, y1 = int(np.floor(xa)), int(np.floor(ya)), int(np.ceil(xb)), int(np.ceil(yb))
    # cobertura de cada px pela escada (as bordas fracionárias misturam)
    cx = np.clip(np.minimum(np.arange(x0, x1) + 1, xb) - np.maximum(np.arange(x0, x1), xa), 0, 1)
    cy = np.clip(np.minimum(np.arange(y0, y1) + 1, yb) - np.maximum(np.arange(y0, y1), ya), 0, 1)
    a = (cy[:, None] * cx[None, :])[..., None]
    reg = out[y0:y1, x0:x1].astype(np.float32)
    out[y0:y1, x0:x1] = np.clip(reg * (1 - a) + tw[y0:y1, x0:x1] * a, 0, 255).astype(np.uint8)
    forca, dec = q["sombra"]
    xs = np.arange(x0 - q["alcance"], x0) + 0.5
    f = 1 - forca * np.exp(-(xa - xs) / dec)
    yi0, yi1 = int(np.ceil(ya)), int(np.floor(yb))
    out[yi0:yi1, x0 - q["alcance"]:x0] = np.clip(out[yi0:yi1, x0 - q["alcance"]:x0] * f[None, :, None], 0, 255).astype(np.uint8)
    print(f"    escada do Térreo aprovado ({n} pontos no alinhamento): x {xa:.1f} a {xb:.1f}, y {ya:.1f} a {yb:.1f}")
    return out


class Tela:
    """Uma janela do render desenhada em SS x: máscaras em pt do PDF, pintadas por cobertura."""

    def __init__(self, out, p2r, caixa_pt, folga=4):
        self.out, self.p2r = out, p2r
        self.x0, self.y0, self.x1, self.y1 = caixa_pdf(p2r, *caixa_pt, folga=folga)
        self.h, self.w = self.y1 - self.y0, self.x1 - self.x0
        self.reg = out[self.y0:self.y1, self.x0:self.x1].astype(np.float32)

    def pt(self, x, y):
        a, b = self.p2r(x, y)
        return (a - self.x0) * SS, (b - self.y0) * SS

    def vazia(self):
        return np.zeros((self.h * SS, self.w * SS), np.uint8)

    def ret(self, r, raio_pt=0.0):
        m = self.vazia()
        (a, b), (c, d) = self.pt(r[0], r[1]), self.pt(r[2], r[3])
        a, b, c, d = (int(round(v)) for v in (a, b, c, d))
        rr = int(min(round(raio_pt * 0.5483 * SS), (c - a) // 2, (d - b) // 2))
        if rr <= 0:
            cv2.rectangle(m, (a, b), (c, d), 255, -1)
            return m
        cv2.rectangle(m, (a + rr, b), (c - rr, d), 255, -1)
        cv2.rectangle(m, (a, b + rr), (c, d - rr), 255, -1)
        for cx, cy in ((a + rr, b + rr), (c - rr, b + rr), (a + rr, d - rr), (c - rr, d - rr)):
            cv2.circle(m, (cx, cy), rr, 255, -1)
        return m

    def reduzir(self, m):
        return cv2.resize(m.astype(np.float32) / (255 if m.dtype == np.uint8 else 1), (self.w, self.h),
                          interpolation=cv2.INTER_AREA)

    def pintar(self, m, cor, forca=1.0):
        a = self.reduzir(m)[..., None] * forca
        self.reg = self.reg * (1 - a) + np.asarray(cor, np.float32) * a

    def contorno(self, m, larg_px, cor):
        k = max(1, int(round(larg_px * SS)))
        self.pintar(m & ~cv2.erode(m, np.ones((k, k), np.uint8)), cor)

    def sombra(self, m, dx=-0.6, dy=0.6, sigma=0.7, forca=0.28):
        s = cv2.warpAffine(m.astype(np.float32) / 255, np.float32([[1, 0, dx * SS], [0, 1, dy * SS]]),
                           (self.w * SS, self.h * SS))
        s = self.reduzir(cv2.GaussianBlur(s, (0, 0), sigma * SS)) * (1 - self.reduzir(m))
        self.reg *= (1 - forca * s)[..., None]

    def gravar(self):
        self.out[self.y0:self.y1, self.x0:self.x1] = np.clip(self.reg, 0, 255).astype(np.uint8)
        return self.out


QUARTZO = (225, 232, 236)                  # BGR de #ECE8E1, as bancadas do prompt
VIDRO_BOX = {"cor": (212, 214, 213), "borda": (128, 131, 133)}
SOMBRA = {"dx": -0.6, "dy": 0.6, "sigma": 0.7, "forca": 0.28}   # a sombra curta das peças, nesta escala
VASO = {"dobradica": 4.0, "recuo": 0.9,   # pt: da parede à dobradiça do tampo; recuo do tampo
        "cor_tampo": (250, 250, 249), "volume": (0.88, 2.0), "volume_tampo": (0.92, 2.4)}


def bancada_cuba(out, p2r, bancada, cuba, torneira, parede):
    """Bancada de quartzo claro com a cuba retangular branca (aba, bacia da borda ao fundo, válvula) e a
    torneira cromada saindo da parede ('direita' ou 'esquerda'), na geometria do PDF."""
    tl = Tela(out, p2r, bancada)
    b = tl.ret(bancada)
    tl.sombra(b, **SOMBRA)
    tl.pintar(b, QUARTZO)
    tl.contorno(b, 0.35, (150, 153, 155))
    c = tl.ret(cuba, 2.0)
    tl.pintar(c, LOUCA_CONTORNO)
    x0, y0, x1, y1 = cuba
    tl.pintar(tl.ret((x0 + 0.8, y0 + 0.8, x1 - 0.8, y1 - 0.8), 1.6), LOUCA)
    for i in range(6):
        k = i / 5
        cor = tuple(BACIA_BORDA[j] * (1 - k) + BACIA_FUNDO[j] * k for j in range(3))
        ins = 2.4 + k * 3.0
        tl.pintar(tl.ret((x0 + ins, y0 + ins, x1 - ins, y1 - ins), max(0.6, 1.6 - k)), cor)
    vx, vy = tl.pt((x0 + x1) / 2, (y0 + y1) / 2)
    v = tl.vazia()
    cv2.circle(v, (int(vx), int(vy)), int(1.1 * SS), 255, -1)
    tl.pintar(v, CROMO_ESCURO)
    tx0, ty0, tx1, ty1 = torneira
    m = tl.ret(torneira, 0.8)
    tl.sombra(m, **SOMBRA)
    tl.pintar(m, CROMO_ESCURO)
    tl.pintar(tl.ret((tx0 + 0.4, ty0 + 0.4, tx1 - 0.4, (ty0 + ty1) / 2), 0.4), CROMO_CLARO)
    bx = tx1 if parede == "direita" else tx0
    base = tl.vazia()
    cx, cy = tl.pt(bx, (ty0 + ty1) / 2)
    cv2.circle(base, (int(cx), int(cy)), int(1.0 * SS), 255, -1)
    tl.pintar(base, CROMO)
    return tl.gravar()


def vaso(out, pg, p2r, caixa, parede):
    """Vaso visto de cima no contorno do PDF (ARQ_LOUÇAS E METAIS, o polígono da caixa dada), como os
    aprovados nas outras casas: louça com volume, contorno fino, sombra curta e o tampo fechado."""
    q = VASO
    corpo = next(d for d in pg.get_drawings() if d.get("layer") == "ARQ_LOUÇAS E METAIS" and d["type"] == "f"
                 and max(abs(d["rect"].x0 - caixa[0]), abs(d["rect"].y0 - caixa[1]), abs(d["rect"].x1 - caixa[2]),
                         abs(d["rect"].y1 - caixa[3])) < 0.3)
    tl = Tela(out, p2r, caixa)
    pts = [tl.pt(p.x, p.y) for it in corpo["items"] for p in it[1:] if hasattr(p, "x")]
    m = tl.vazia()
    cv2.fillPoly(m, [cv2.convexHull(np.int32(np.round(pts)))], 255)
    tl.sombra(m, **SOMBRA)
    dist = cv2.distanceTransform(m, cv2.DIST_L2, 5) / SS
    borda, alcance = q["volume"]
    tom = borda + (1 - borda) * np.clip(dist / alcance, 0, 1)
    a = tl.reduzir(m)[..., None]
    cor = cv2.resize(np.asarray(LOUCA, np.float32)[None, None] * tom[..., None] * (m / 255.0)[..., None],
                     (tl.w, tl.h), interpolation=cv2.INTER_AREA)
    tl.reg = tl.reg * (1 - a) + cor
    tl.contorno(m, 0.35, LOUCA_CONTORNO)
    k = int(2 * q["recuo"] * 0.5483 * SS) + 1
    tampo = cv2.erode(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    xd = caixa[2] - q["dobradica"] if parede == "direita" else caixa[0] + q["dobradica"]
    xs_pt = tl.pt(xd, caixa[1])[0]
    if parede == "direita":
        tampo[:, int(xs_pt):] = 0
    else:
        tampo[:, :int(xs_pt)] = 0
    tl.sombra(tampo, dx=-0.25, dy=0.3, sigma=0.4, forca=0.18)
    dt = cv2.distanceTransform(tampo, cv2.DIST_L2, 5) / SS
    borda, alcance = q["volume_tampo"]
    tom = borda + (1 - borda) * np.clip(dt / alcance, 0, 1)
    a = tl.reduzir(tampo)[..., None]
    cor = cv2.resize(np.asarray(q["cor_tampo"], np.float32)[None, None] * tom[..., None] * (tampo / 255.0)[..., None],
                     (tl.w, tl.h), interpolation=cv2.INTER_AREA)
    tl.reg = tl.reg * (1 - a) + cor
    tl.contorno(tampo, 0.3, LOUCA_CONTORNO)
    return tl.gravar()


def vidro_box(out, p2r, r):
    """Divisória de vidro do box, fina: vidro claro com as bordas finas."""
    tl = Tela(out, p2r, r)
    m = tl.ret(r)
    tl.pintar(m, VIDRO_BOX["cor"])
    tl.contorno(m, 0.3, VIDRO_BOX["borda"])
    return tl.gravar()


def chuveiro(out, p2r, ducha, braco, canopla):
    """Chuveiro visto de cima, como os aprovados: ducha quadrada (a placa da Casa A), braço cromado do
    centro da ducha à face da parede, com o brilho no eixo, e a canopla na parede; sombra curta."""
    tl = Tela(out, p2r, (min(ducha[0], braco[0], canopla[0]), min(ducha[1], braco[1], canopla[1]),
                         max(ducha[2], braco[2], canopla[2]), max(ducha[3], braco[3], canopla[3])))
    d = tl.ret(ducha, 0.6)
    tl.sombra(d, **SOMBRA)
    img = cv2.imread(str(CHUVEIRO_TETO[0]))
    hx0, hy0, hx1, hy1 = CHUVEIRO_TETO[1]
    ys, xs = np.nonzero(d)
    placa = cv2.resize(img[hy0:hy1, hx0:hx1], (xs.max() - xs.min() + 1, ys.max() - ys.min() + 1),
                       interpolation=cv2.INTER_CUBIC).astype(np.float32)
    cor = np.zeros((tl.h * SS, tl.w * SS, 3), np.float32)
    cor[ys.min():ys.max() + 1, xs.min():xs.max() + 1] = placa
    a = tl.reduzir(d)[..., None]
    c = cv2.resize(cor * (d[..., None] / 255.0), (tl.w, tl.h), interpolation=cv2.INTER_AREA) / np.maximum(a, 1e-6)
    tl.reg = tl.reg * (1 - a) + c * a
    b = tl.ret(braco)
    tl.pintar(b, CROMO_ESCURO)
    bx0, by0, bx1, by1 = braco
    if bx1 - bx0 >= by1 - by0:
        tl.pintar(tl.ret((bx0, by0 + 0.2, bx1, (by0 + by1) / 2)), CROMO_CLARO)
    else:
        tl.pintar(tl.ret((bx0 + 0.2, by0, (bx0 + bx1) / 2, by1)), CROMO_CLARO)
    tl.pintar(tl.ret(canopla), CROMO)
    return tl.gravar()


def preencher_ambiente(out, p2r, chapada, tex, caixa_pdf_amb, cor, extra=()):
    """O ambiente inteiro (menos as paredes da base) vira o piso aprovado, sem nada do render dentro."""
    # só as paredes grossas: os símbolos finos e pretos da base (registros, contornos) entram no piso
    parede = cv2.morphologyEx((chapada.max(axis=2) < 60).astype(np.uint8), cv2.MORPH_OPEN,
                              np.ones((3, 3), np.uint8)).astype(bool)
    m = np.zeros(parede.shape, bool)
    for r in (caixa_pdf_amb,) + tuple(extra):
        x0, y0, x1, y1 = caixa_pdf(p2r, *r)
        m[y0:y1, x0:x1] = True
    m &= ~parede
    piso = np.abs(chapada.astype(int) - BEGE["legenda"]).max(axis=2) <= BEGE["tol"]
    out = trocar_piso(out, m, tex, cor, buracos=m & ~piso)
    # o que o render pôs sobre as paredes em volta (restos de peças): volta ao preto da parede
    x0, y0, x1, y1 = caixa_pdf(p2r, *caixa_pdf_amb, folga=4)
    reg = out[y0:y1, x0:x1]
    lum = reg.astype(np.float32).mean(axis=2)
    pw = parede[y0:y1, x0:x1]
    resto = pw & (lum > 90) & cv2.erode(pw.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    if resto.any():
        reg[resto] = np.median(reg[pw & (lum < 40)], axis=0).astype(np.uint8)
    return out, m


# item 3: WC DCE 2. O motor fez o piso em granito (é Bege Bahia), uma bancada comprida que pega também o
# lugar da bacia, a bacia no lugar do chuveiro e nenhum chuveiro. O ambiente é refeito pelo PDF.
WC_DCE2 = {"interior": (1646.7, 693.5, 1726.1, 829.6),
           "bancada": (1697.6, 693.5, 1726.1, 729.1), "cuba": (1700.9, 700.4, 1720.8, 723.1),
           "torneira": (1712.6, 710.8, 1720.2, 713.0),
           "vaso": (1696.9, 739.2, 1726.1, 759.2),
           "vidro": (1647.3, 777.1, 1725.5, 780.0),
           "ducha": (1698.6, 797.8, 1709.8, 809.0), "braco": (1703.1, 802.7, 1725.4, 804.1),
           "canopla": (1725.4, 801.7, 1726.1, 805.1),
           "porta": ((1646.7, 697.7, 1692.0, 700.0), (1646.7, 697.7, 1692.0, 743.1))}


def wc_dce2(out, pg, p2r, chapada, tex):
    q = WC_DCE2
    out, m = preencher_ambiente(out, p2r, chapada, tex, q["interior"], BEGE["cor"])
    out = desenhar_porta(out, pg, p2r, *q["porta"], "bege")
    out = vidro_box(out, p2r, q["vidro"])
    out = bancada_cuba(out, p2r, q["bancada"], q["cuba"], q["torneira"], "direita")
    out = vaso(out, pg, p2r, q["vaso"], "direita")
    out = chuveiro(out, p2r, q["ducha"], q["braco"], q["canopla"])
    print(f"    WC DCE 2: Bege Bahia em {int(m.sum())} px; porta, bancada com cuba, bacia, vidro do box e chuveiro do PDF")
    return out


# item 4: casa de máquinas da direita. O motor fez o piso em granito; é Bege Bahia (o cinza do PDF, como o
# depósito). O ambiente vira o Bege Bahia aprovado, com o vão da porta, e a porta vinda do depósito é a do PDF.
CASA_MAQ_DIR = {"interior": (1732.9, 693.5, 1825.3, 897.6),
                "soleira": (1738.8, 685.0, 1784.2, 693.5),
                "porta": ((1738.8, 693.5, 1741.1, 738.8), (1738.8, 693.5, 1784.2, 738.8))}


def casa_maquinas_dir(out, pg, p2r, chapada, tex):
    q = CASA_MAQ_DIR
    out, m = preencher_ambiente(out, p2r, chapada, tex, q["interior"], BEGE["cor"], extra=(q["soleira"],))
    out = desenhar_porta(out, pg, p2r, *q["porta"], "bege")
    print(f"    casa de máquinas da direita: Bege Bahia em {int(m.sum())} px, porta do PDF")
    return out


# Mapa dos erros do render v1 (pontos em pt do PDF do Subsolo, convertidos ao render pela cadeia da base)
ITENS = [
    (1, "Circulação: a faixa da esquerda saiu em travertino (com uma junta) e com uma parede preta na borda "
        "da esquerda; é toda em Bege Bahia e sem parede", [(860, 590), (700, 600)]),
    (2, "Escada: linhas pretas fortes, seta nas duas pontas e uma cunha de sombra; fica o padrão aprovado "
        "(sombreamento, sem linhas)", [(1120, 650)]),
    (3, "WC DCE 2: piso em granito (é Bege Bahia); a parede com o DCE não sobe até o alto, sem a porta; "
        "cuba, bacia e box fora do lugar do PDF", [(1686, 760)]),
    (4, "Casa de máquinas da direita: piso em granito (é Bege Bahia)", [(1765, 790)]),
    (5, "Elevador: piso de mármore com um quadrado claro, sem a cabine", [(1765, 935)]),
    (6, "Academia: o suporte de halteres virou um armário alto de madeira", [(1705, 890)]),
    (7, "Academia: os dois aparelhos pequenos do PDF viraram dois halteres grandes", [(905, 750)]),
    (8, "Piscina e ofurô: degraus e bancos dentro dos tanques que o PDF não tem; o vidro entre a piscina "
        "de baixo e o ofurô virou parede branca", [(750, 820), (760, 1040), (848, 1030)]),
    (9, "Sauna: banco em L de ripas de madeira (é o banco de Bege Bahia em dois níveis, só ao longo da "
        "parede de baixo)", [(945, 1060), (900, 1000)]),
    (10, "Antessala: uma bacia sanitária que não existe no PDF", [(1105, 1060)]),
    (11, "Chuveiros fora do padrão aprovado (ducha da antessala, box do vestiário e WC DCE 2)",
     [(1036, 1069), (1268, 1059), (1705, 803)]),
    (12, "Portas: arcos tracejados em umas e nenhum arco em outras", [(1165, 980), (1465, 715)]),
    (13, "Granito do DCE e da casa de máquinas de baixo com veios de mármore (o aprovado é o granito em "
         "grão do Térreo)", [(1560, 740), (1160, 1180)]),
    (14, "Sombras longas (à direita do vestiário, sob o armário, nas bolas e nos aparelhos)", [(1310, 1010)]),
    (15, "Linha tracejada do lote, à direita: um trecho saiu deslocado; volta a do PDF", []),
]


def mapa_erros(render, p2r, caminho):
    """Marca cada item com um círculo vermelho numerado, em 2 x, e a legenda embaixo."""
    k = 2
    img = cv2.resize(render, None, fx=k, fy=k, interpolation=cv2.INTER_CUBIC)
    for n, _, pontos in ITENS:
        for x, y in pontos:
            cx, cy = (int(round(v * k)) for v in p2r(x, y))
            cv2.circle(img, (cx, cy), 22, (40, 40, 220), 3, cv2.LINE_AA)
            cv2.putText(img, str(n), (cx + 20, cy - 16), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (40, 40, 220), 2, cv2.LINE_AA)
    # recorte em volta da planta e a legenda
    x0, y0, x1, y1 = (int(v * k) for v in (420, 120, 1110, 600))
    img = img[y0:y1, x0:x1]
    linhas = [f"{n}. {t}" for n, t, _ in ITENS]
    alt = 30 * len(linhas) + 20
    leg = np.full((alt, img.shape[1], 3), 255, np.uint8)
    for i, t in enumerate(linhas):
        cv2.putText(leg, t[:150], (14, 28 + 30 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (30, 30, 30), 1, cv2.LINE_AA)
    cv2.imwrite(str(caminho), np.vstack([img, leg]), [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"    mapa dos erros: {caminho}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("render", type=Path)
    ap.add_argument("--saida", type=Path, default=Path("."))
    ap.add_argument("--nome", default=None)
    ap.add_argument("--mapa", type=Path, default=None, help="só gera o mapa dos erros neste arquivo")
    ap.add_argument("--ate", type=int, default=99, help="roda os itens só até este número (conferência)")
    args = ap.parse_args()

    orig = cv2.imread(str(args.render))
    A = alinhar_base(orig)
    pg, p2r, r2p = pdf_cadeia(A, orig.shape)
    if args.mapa:
        mapa_erros(orig, p2r, args.mapa)
        return
    if not args.nome:
        ap.error("--nome é obrigatório para o retoque")
    out = orig.copy()
    chapada = chapada_no_render(A, orig.shape)
    tex = texturas_no_render(A, orig.shape)
    itens = [
        ("circulação e depósito em Bege Bahia, sem a parede da esquerda",
         lambda o: circulacao_deposito(o, A, pg, p2r, chapada, tex)),
        ("escada: a do Térreo aprovado (sem linhas, sombreamento de descida para a esquerda)",
         lambda o: escada(o, A, p2r)),
        ("WC DCE 2: piso, porta, louças, vidro do box e chuveiro pelo PDF",
         lambda o: wc_dce2(o, pg, p2r, chapada, tex)),
        ("casa de máquinas da direita em Bege Bahia", lambda o: casa_maquinas_dir(o, pg, p2r, chapada, tex)),
        ("elevador: o do Térreo aprovado", lambda o: elevador(o, A, p2r, terreo_no_render(A, o.shape)[0])),
    ]
    for n, (desc, f) in enumerate(itens, 1):
        if n <= args.ate:
            print(f"[{n}] {desc}")
            out = f(out)

    args.saida.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(args.saida / f"{args.nome}.png"), out)
    alfa = np.where(np.abs(out.astype(int) - orig.astype(int)).max(axis=2) > 0, 255, 0).astype(np.uint8)
    cv2.imwrite(str(args.saida / f"{args.nome}_camada.png"), np.dstack([out, alfa]))
    cv2.imwrite(str(args.saida / f"{args.nome}_previa.jpg"), out, [cv2.IMWRITE_JPEG_QUALITY, 88])
    print(f"[fim] {args.saida / (args.nome + '.png')}; {int((alfa > 0).sum())} px alterados")


if __name__ == "__main__":
    main()

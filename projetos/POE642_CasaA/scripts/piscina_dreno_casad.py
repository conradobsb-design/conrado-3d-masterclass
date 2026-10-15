#!/usr/bin/env python3
"""Casa D · Térreo: piscina e spa com dreno em linha e degraus internos em níveis (POE 642).

Pedido do usuário (15/10/26), sobre o Barlavento da Casa D (`piscinas_barlavento.py`): "não gostei
da finalização da piscina. precisa melhorar a borda da piscina, degraus internos [...]. pode fazer
uma borda com dreno", e depois: "o dreno é apenas uma linha contínua fina. somente na parte externa
da piscina". As linhas duplas dos degraus pareciam um rasgo (um furo) no fundo.

Parte do render retocado (sem o Barlavento) e refaz a água inteira:
- **borda**: a água vai até o contorno do projeto (cobre o traço escuro do render), sem a sombra de
  parede, só com uma leve definição junto ao piso;
- **dreno**: uma linha contínua fina e escura no piso, a ~6 cm da água, só no contorno de fora do
  conjunto (piscina e spa). A faixa de piso entre a piscina e o spa não leva. Cantos em esquadro;
- **degraus em níveis**: cada área entre as linhas do projeto (fundo, degrau da prainha, prainha;
  banco, degrau e fundo do spa) tem a sua profundidade. Mais rasa, a água absorve menos (mais o
  vermelho) e fica mais clara; o fundo da piscina fica no tom aprovado. O degrau é a troca de tom,
  com uma luz fina na quina de cima e uma sombra curta ao pé, no nível de baixo. Sem linhas escuras;
- o resto é o Barlavento aprovado: a pedra das peças sob a água, a grade ondulada pela refração, as
  cáusticas do render suavizadas (mais nítidas no raso) e o brilho difuso na diagonal.

As áreas vêm da base chapada (componentes da água, as linhas do projeto divididas entre as duas
áreas vizinhas), alinhada ao render por SIFT + afim. Tudo é desenhado a 8x e reduzido por área.

Uso (da pasta projetos/):
  python3 POE642_CasaA/scripts/piscina_dreno_casad.py
  # e a prancha: de POE642_CasaA/scripts/, rodape_entrega.py --config ../../POE642_CasaD/config_bases.json
  #   --render Terreo=../../POE642_CasaD/renders/POE642_CasaD_PH_Terreo_v1_retocado_barlavento_v2.png
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
from scipy import ndimage

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

from piscinas_barlavento import Q, alinhar, brilho_diagonal, causticas, mascara_agua, pedra_ondulada  # noqa: E402

CASA = AQUI.parent.parent / "POE642_CasaD"

D = {
    "entrada": CASA / "renders/POE642_CasaD_PH_Terreo_v1_retocado.png",
    "saida": CASA / "renders/POE642_CasaD_PH_Terreo_v1_retocado_barlavento_v2.png",
    "base": CASA / "bases/POE642_CasaD_BASE_Terreo_v3_texturas_16x9.png",
    "chapada": CASA / "bases/POE642_CasaD_BASE_Terreo_v2_16x9.png",
    "ss": 8,
    # áreas da água (um ponto do render em cada) e a profundidade de cada uma, em m
    "areas": [((520, 380), 1.40, "fundo da piscina"),
              ((576, 330), 0.80, "degrau da prainha"),
              ((620, 330), 0.30, "prainha"),
              ((585, 461), 0.45, "banco do spa"),
              ((594.4, 461), 0.65, "degrau do spa"),
              ((619, 461), 0.90, "fundo do spa")],
    # cor da água: a aprovada (Q["cor"]) vale no fundo da piscina; mais rasa, a água absorve menos
    # (mais o vermelho) e fica mais clara e menos saturada. Absorção por m (BGR)
    "prof_ref": 1.40, "absorcao": (0.025, 0.05, 0.11),
    "pe": (0.10, 1.4),          # sombra ao pé do degrau: força e decaimento (px)
    "quina": (0.07, 0.6),       # luz na quina de cima do degrau
    # px do render (~3,2 cm por px)
    "expande": 0.8,             # a água cobre o traço escuro do render na borda
    "lamina": (0.05, 0.9),      # leve definição da água junto à borda (sem sombra de parede)
    # dreno: uma linha contínua fina no piso, só por fora do conjunto (piscina e spa), a ~6 cm da
    # água; a faixa entre a piscina e o spa não leva
    "fecha": 8,                 # fecha a faixa entre a piscina e o spa (10 px) no contorno do conjunto
    "dreno": (1.8, 0.65),       # afastamento da água e largura, px
    "dreno_cor": (92, 98, 96),
}


def areas_render(img, A, q=D):
    """Rótulo das áreas da água na grade 8x do recorte do render e a profundidade de cada rótulo."""
    ch = cv2.imread(str(q["chapada"])).astype(np.int32)
    H, W = ch.shape[:2]
    h, w = img.shape[:2]
    M = np.vstack([A, [0, 0, 1]]) @ np.array([[w / W, 0, 0], [0, h / H, 0], [0, 0, 1]])   # base cheia -> render
    tons = [np.any([np.abs(ch - np.array(c)).max(axis=2) <= Q["tol_base"] for c in g], axis=0)
            for g in Q["agua_base"]]
    agua = np.any(tons, axis=0)
    n, lab, st, _ = cv2.connectedComponentsWithStats(agua.astype(np.uint8), connectivity=4)
    Mi = cv2.invertAffineTransform(M[:2])
    rot, prof = np.zeros_like(lab), {}
    for k, ((x, y), p, nome) in enumerate(q["areas"], 1):
        bx, by = Mi @ np.array([x, y, 1.0])
        i = lab[int(round(by)), int(round(bx))]
        assert i > 0 and st[i, cv2.CC_STAT_AREA] > 2000, nome
        rot[lab == i] = k
        prof[k] = p
    # as linhas do projeto (e o resto da mancha) ficam com a área mais próxima: o degrau cai no meio
    ys, xs = np.nonzero(rot)
    x0, y0, x1, y1 = xs.min() - 20, ys.min() - 20, xs.max() + 21, ys.max() + 21
    r = rot[y0:y1, x0:x1]
    regiao = ndimage.binary_fill_holes(cv2.morphologyEx((r > 0).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8)))
    _, (iy, ix) = ndimage.distance_transform_edt(r == 0, return_indices=True)
    r = np.where(regiao, r[iy, ix], 0).astype(np.uint8)
    # para a grade 8x do recorte do render
    cx = (M[:2] @ np.array([[x0, x1], [y0, y1], [1, 1]]))
    rx0, ry0 = int(np.floor(cx[0].min())) - 6, int(np.floor(cx[1].min())) - 6
    rx1, ry1 = int(np.ceil(cx[0].max())) + 7, int(np.ceil(cx[1].max())) + 7
    ss = q["ss"]
    T = np.array([[ss, 0, -ss * rx0], [0, ss, -ss * ry0], [0, 0, 1.0]]) @ M
    T = T @ np.array([[1, 0, x0], [0, 1, y0], [0, 0, 1.0]])               # recorte da base -> 8x
    r8 = cv2.warpAffine(r, T[:2], ((rx1 - rx0) * ss, (ry1 - ry0) * ss), flags=cv2.INTER_NEAREST)
    return r8, prof, (rx0, ry0, rx1, ry1)


def dist_eixos(mask):
    """Distância (px da grade) até o primeiro px fora da máscara na mesma linha ou coluna: nas formas
    retas da piscina, as faixas da borda fazem cantos em ângulo reto, também nos cantos internos.
    Devolve a distância e se o mais perto é na horizontal (borda vertical)."""
    dh = ndimage.distance_transform_edt(mask, sampling=(1e4, 1))
    dv = ndimage.distance_transform_edt(mask, sampling=(1, 1e4))
    return np.minimum(dh, dv), dh <= dv


def reduz(a, ss):
    return cv2.resize(a.astype(np.float32), (a.shape[1] // ss, a.shape[0] // ss), interpolation=cv2.INTER_AREA)


def desenhar(img, r8, prof, caixa, q=D):
    ss = q["ss"]
    rx0, ry0, rx1, ry1 = caixa
    h, w = ry1 - ry0, rx1 - rx0
    # a água: a mancha das áreas, um pouco expandida para cobrir o traço escuro do render
    dentro = r8 > 0
    e = int(round(q["expande"] * ss))
    agua = cv2.dilate(dentro.astype(np.uint8), np.ones((2 * e + 1, 2 * e + 1), np.uint8)) > 0
    d = dist_eixos(agua)[0] / ss                                         # px do render até o piso
    # o dreno: o contorno de fora do conjunto (piscina, spa e a faixa entre eles), no piso
    f = int(round(q["fecha"] * ss))
    conjunto = cv2.morphologyEx(agua.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((2 * f + 1, 2 * f + 1), np.uint8))
    conjunto = ndimage.binary_fill_holes(conjunto)
    fora = cv2.distanceTransform((~conjunto).astype(np.uint8), cv2.DIST_C, 3) / ss   # cantos em esquadro
    o, lg = q["dreno"]
    dreno = ~conjunto & (fora > o) & (fora <= o + lg)
    # profundidade e a luz dos degraus
    p8 = np.zeros(r8.shape, np.float32)
    for k, p in prof.items():
        p8[r8 == k] = p
    p8 = np.where(dentro, p8, ndimage.grey_dilation(p8, size=(2 * e + 3, 2 * e + 3)))   # a faixa expandida herda a vizinha
    sombra = np.zeros(r8.shape, np.float32)
    luz = np.zeros(r8.shape, np.float32)
    fp, dp = q["pe"]
    fq, dq = q["quina"]
    for k, p in prof.items():
        zona = r8 == k
        rasas = agua & (p8 < p - 0.05)
        if rasas.any():
            dd = dist_eixos(~rasas)[0] / ss
            sombra[zona] = (fp * np.exp(-np.maximum(dd - 0.5, 0) / dp))[zona]
        fundas = agua & (p8 > p + 0.05)
        if fundas.any():
            dd = dist_eixos(~fundas)[0] / ss
            luz[zona] = (fq * np.exp(-np.maximum(dd - 0.5, 0) / dq))[zona]
    fl, dl = q["lamina"]
    lamina = fl * np.exp(-d / dl)
    # reduzir
    Ra, Rd = reduz(agua, ss), reduz(dreno, ss)
    pa = np.maximum(Ra, 1e-6)
    P = reduz(p8 * agua, ss) / pa
    S = reduz(sombra * agua, ss) / pa
    L = reduz(luz * agua, ss) / pa
    Lm = reduz(lamina * agua, ss) / pa

    reg = img[ry0:ry1, rx0:rx1].astype(np.float32)
    # a água: Barlavento aprovado + a cor pela profundidade
    m_old, lim_old = mascara_agua(img)
    m_old, lim_old = m_old[ry0:ry1, rx0:rx1], lim_old[ry0:ry1, rx0:rx1]
    pedra = pedra_ondulada(h, w)
    absorcao = np.float32(q["absorcao"])
    cor = np.exp(-absorcao[None, None, :] * (P - q["prof_ref"])[..., None])
    caust = causticas(reg.mean(axis=2), m_old.astype(np.float32))
    caust *= np.clip(Ra * 2 - 1, 0, 1)
    caust *= np.clip(1 - 0.3 * (P - q["prof_ref"]), 0.8, 1.4)            # mais nítidas no raso
    fator = (1 - S) * (1 + L) * (1 - Lm) * brilho_diagonal(h, w)
    agua_cor = pedra * cor * fator[..., None] + caust[..., None] * np.float32([1.0, 1.0, 0.92])
    # o piso em volta (para a sobra da água antiga fora do contorno)
    anel = (cv2.dilate((Ra > 0).astype(np.uint8), np.ones((15, 15), np.uint8)) > 0) & \
        ~(cv2.dilate((Ra > 0).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0)
    piso = np.median(reg[anel], axis=0).astype(np.float32)
    base = reg.copy()
    resto = lim_old & (Ra < 0.5)
    base[resto] = piso
    mix = base * (1 - Ra[..., None]) + agua_cor * Ra[..., None]
    mix = mix * (1 - Rd[..., None]) + np.float32(q["dreno_cor"]) * Rd[..., None]
    out = img.copy()
    out[ry0:ry1, rx0:rx1] = np.clip(mix, 0, 255).astype(np.uint8)
    print(f"    degraus em {len(prof)} níveis e dreno em linha contínua; {int(resto.sum())} px da água antiga fora do contorno")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--entrada", type=Path, default=D["entrada"])
    ap.add_argument("--saida", type=Path, default=D["saida"])
    args = ap.parse_args()
    img = cv2.imread(str(args.entrada))
    A = alinhar(img, D["base"])
    r8, prof, caixa = areas_render(img, A)
    out = desenhar(img, r8, prof, caixa)
    cv2.imwrite(str(args.saida), out)
    print(f"[fim] {args.saida}")


if __name__ == "__main__":
    main()

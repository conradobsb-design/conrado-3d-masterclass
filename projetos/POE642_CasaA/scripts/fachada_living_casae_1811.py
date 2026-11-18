"""A fachada de vidro de baixo do living do Térreo da Casa E, com o tapete e a cortina (18/11, usuário: "VAMOS CORRIGIR
ESSE ERRO NO TAPETE E PISO." e "VAMOS CORRIGIR ESSE ERRO NO CANTO ESQUERDO DAS ESQUADRIAS DE VIDRO E REPRESENTAR AS
FOLHAS DE VIDRO COM MAIS PRECISÃO"), na final e direto nos 12K A e B.

A faixa da fachada (da folha de vidro da esquerda até a parede da direita, da linha de baixo do tapete até as folhas)
é refeita por camadas:
1. o piso: o travertino limpo (o tom só, de um trecho limpo da circulação) até a face de dentro de cada folha; abaixo
   das folhas, o lado de fora fica como está;
2. o tapete: o PNG da biblioteca no círculo do PDF (ARQ_MOBILIÁRIO), inteiro, até a borda dele (em 16/11 ele ficou
   cortado reto na altura da cortina, com uma faixa cinza do desenho de antes embaixo);
3. a cortina: uma onda limpa da própria cortina (a de x 1960), repetida no passo das ondas (17,8 px) de ponta a ponta,
   sem emendas, com o trilho escuro; da crista para baixo a cortina cobre o que está atrás, acima dela aparece o tapete
   ou o piso;
4. as esquadrias pelo PDF (ARQ_PAREDE): as quatro folhas de correr desencontradas, cada uma com as duas lâminas de
   vidro claro com o fio e a linha do meio, os montantes em grafite nas pontas; no canto da esquerda, a fachada da
   esquerda desce até o encontro (a linha escura e a cortina vertical, que paravam no meio), o trilho de baixo encosta
   nela, o nó do canto (o toco de parede e os montantes do pé) pelo PDF, e o resto claro sai.

  python3 fachada_living_casae_1811.py doze [--opcao AB]     (antes da final: a final de antes é a referência)
  python3 fachada_living_casae_1811.py final
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import biblioteca_terreo_casaa_1211 as BT                   # noqa: E402
import correcoes_terreo_casab_1611 as CB                    # noqa: E402
import danae_foto as DF                                     # noqa: E402
from correcoes_terreo_casab_1611 import Mapa                # noqa: E402
from janela_pia_casaa_1611 import alfa_ret                  # noqa: E402

RAIZ = AQUI.parents[1]
FINAL = RAIZ / "POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_final.png"
DOZE = RAIZ / "POE642_CasaE/entrega/POE642_CasaE_PH_Terreo_12K_opcao_{}.jpg"
BIB = RAIZ / "POE642_CasaE/biblioteca-objetos/02-terreo"

# px da final
FAIXA = (1578.7, 1526.0, 2096.7, 1560.0)          # a faixa refeita (da linha da fachada da esquerda à parede da direita)
CANTO = (1589.0, 1505.0, 1608.0, 1527.0)          # o resto claro acima da faixa, junto ao canto da esquerda
# a fachada da esquerda (a linha escura e a cortina vertical) descendo até o encontro com a de baixo
ESQ = {"linha": (1576.9, 1524.5, 1578.7, 1551.4), "linha_cor": (88, 89, 89),
       "cortina": (1578.7, 1524.5, 1588.6, 1543.6), "onda_v": 36.17, "debaixo": (1587.0, 1557.8, 1604.0, 1560.5),
       "trilho": (1578.7, 1543.6, 1589.0, 1545.9), "trilho_cor": (74, 74, 74)}
TRAVERTINO = (1725.0, 824.0, 1853.0, 942.0)       # um trecho limpo do travertino (o tom só)
TAPETE = {"png": BIB / "living/tapete-redondo-azul-marinho-e.png", "pdf": (1612.0, 1289.8, 1853.8, 1537.6)}
CORTINA = {"onda": 17.8, "x0": 1960.0, "y": (1526.0, 1546.2), "de": 1588.0, "ate": 2096.2, "limiar": 16.0}
# as folhas de correr (lâminas de vidro) e os montantes, do PDF (ARQ_PAREDE)
FOLHAS = [(1585.0, 1554.7, 1708.1, 1557.7), (1712.9, 1551.7, 1836.0, 1554.7),
          (1840.8, 1548.7, 1964.0, 1551.7), (1968.7, 1545.7, 2091.9, 1548.7)]
MONTANTES = [(1708.1, 1551.7, 1712.9, 1557.7), (1836.0, 1548.7, 1840.8, 1554.7),
             (1964.0, 1545.7, 1968.7, 1551.7), (2091.9, 1545.7, 2096.7, 1548.7),
             (1580.2, 1554.7, 1585.0, 1557.7), (1583.8, 1552.9, 1586.8, 1557.7)]
VERTICAIS = []
PAREDES = [(1578.7, 1551.4, 1580.2, 1557.7)]
COR = {"grafite": (58, 60, 64), "fio": (34, 35, 38), "fio_px": 0.35, "vidro": (226, 229, 232),
       "vidro_fio": (120, 123, 128), "vidro_fio_px": 0.3, "meio": (150, 153, 158), "meio_px": 0.3,
       "parede": (80, 80, 80)}


def _png(caminho):
    P = cv2.imread(str(caminho), cv2.IMREAD_UNCHANGED).astype(np.float32)
    ys, xs = np.nonzero(P[..., 3] > 0)
    return np.ascontiguousarray(P[ys.min():ys.max() + 1, xs.min():xs.max() + 1])


def _tile(patch, h, w):
    t = patch
    while t.shape[0] < h:
        t = np.concatenate([t, t[::-1]], axis=0)
    while t.shape[1] < w:
        t = np.concatenate([t, t[:, ::-1]], axis=1)
    return t[:h, :w]


def _u(m, X):
    """A coordenada da final (px de borda) do índice X da imagem."""
    return (X + 0.5 - m.t[0] - 0.5) / m.s + 0.5


def _v(m, Y):
    return (Y + 0.5 - m.t[1] - 0.5) / m.s + 0.5


def aplicar(img, mp):
    out = img.copy()
    m = mp.local(out, (1570, 1480, 2110, 1570)) if mp.ref is not None else mp
    s = m.s
    X0, Y0, X1, Y1 = m.reti(FAIXA)
    h, w = Y1 - Y0, X1 - X0
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    U = _u(m, np.arange(X0, X1, dtype=np.float32))[None, :]
    V = _v(m, np.arange(Y0, Y1, dtype=np.float32))[:, None]
    # o topo de cada folha (a face de dentro), por coluna
    topo = np.full(w, np.inf, np.float32)
    for x0, y0, x1, y1 in FOLHAS + MONTANTES[:4]:
        sel = (U[0] >= x0) & (U[0] < x1)
        topo[sel] = np.minimum(topo[sel], y0)
    topo[np.isinf(topo)] = 1557.7
    dentro = (V < topo[None, :]).astype(np.float32)
    # 1. o piso de dentro
    tx0, ty0, tx1, ty1 = m.reti(TRAVERTINO)
    trav = _tile(out[ty0:ty1, tx0:tx1].astype(np.float32), h, w)
    base = reg * (1 - dentro[..., None]) + trav * dentro[..., None]
    # 2. o tapete inteiro, no círculo do PDF
    x0, y0, x1, y1 = TAPETE["pdf"]
    tcx, tcy, R = (x0 + x1) / 2, (y0 + y1) / 2, ((x1 - x0) + (y1 - y0)) / 4
    P = _png(TAPETE["png"])
    preto, branco = np.zeros((h, w, 3), np.float32), np.full((h, w, 3), 255.0, np.float32)
    for tela in (preto, branco):
        BT.pousar(tela, P, m.x(tcx) - X0, m.y(tcy) - Y0, 2 * R * s, 2 * R * s, 0.0, [], DF.PX_M * s)
    at = np.clip(1 - (branco - preto).mean(axis=2) / 255.0, 0, 1)[..., None] * dentro[..., None]
    base = base * (1 - at) + preto * dentro[..., None]
    # 3. a cortina: a onda limpa repetida no passo, com o trilho
    c = CORTINA
    # o passo das ondas medido na própria imagem (no trecho limpo da direita), com fração de px
    bx0, by0, bx1, by1 = m.reti((1800.0, 1529.0, 2090.0, 1543.0))
    seg = out[by0:by1, bx0:bx1].astype(np.float32).mean(axis=(0, 2))
    seg = seg - seg.mean()
    lags = np.arange(int((c["onda"] - 2) * s), int((c["onda"] + 2) * s) + 1)
    acs = np.array([(seg[:-k] * seg[k:]).mean() for k in lags])
    i = int(np.clip(np.argmax(acs), 1, len(lags) - 2))
    y0_, y1_, y2_ = acs[i - 1], acs[i], acs[i + 1]
    den = y0_ - 2 * y1_ + y2_
    P_ = (lags[i] + (0.5 * (y0_ - y2_) / den if den != 0 else 0.0)) / s
    # a origem da onda: onde a coluna de x0 e a de x0 + P mais se parecem (a emenda some)
    def coluna(u):
        mapx = np.full((by1 - by0, 1), m.x(u) - 0.5, np.float32)
        mapy = np.arange(by0, by1, dtype=np.float32)[:, None]
        return cv2.remap(out, mapx, mapy, cv2.INTER_LINEAR).astype(np.float32)
    melhor = None
    for x0c in np.arange(c["x0"] - 18.0, c["x0"] + 18.0, 0.25):
        e = sum(float(np.abs(coluna(x0c + dx) - coluna(x0c + P_ + dx)).mean()) for dx in (-0.5, 0.0, 0.5))
        if melhor is None or e < melhor[0]:
            melhor = (e, x0c)
    c = dict(c, x0=float(melhor[1]))
    fase = np.mod(U - c["x0"], P_)
    mapy = np.repeat((np.arange(Y0, Y1, dtype=np.float32))[:, None], w, axis=1)

    def amostra(us):
        mapx = np.repeat(m.x(us) - 0.5, h, axis=0).astype(np.float32)
        return cv2.remap(out, mapx, mapy, cv2.INTER_LINEAR).astype(np.float32)
    # sem emenda entre as ondas: no fim de cada passo, a onda passa aos poucos para a de um passo antes
    f = np.clip((fase / P_ - 0.88) / 0.12, 0, 1)
    f = (f * f * (3 - 2 * f))[..., None]
    cort = amostra(c["x0"] + fase) * (1 - f) + amostra(c["x0"] + fase - P_) * f
    rb = cort[..., 2] - cort[..., 0]
    # da crista para baixo a cortina é cheia: o quanto o px é neutro (o cinza da cortina), acumulado de cima para
    # baixo em cada coluna (a borda de cima fica suave)
    faixa_c = ((V >= c["y"][0]) & (V < c["y"][1])).astype(np.float32)
    neutro = np.clip((c["limiar"] + 6 - rb) / 12.0, 0, 1) * faixa_c
    ac = np.maximum.accumulate(neutro, axis=0) * faixa_c
    na_cortina = ((U >= c["de"]) & (U < c["ate"])).astype(np.float32)
    ac *= na_cortina
    novo = base * (1 - ac[..., None]) + cort * ac[..., None]
    # a emenda nas pontas (a da direita encosta na parede; a da esquerda na folha)
    out[Y0:Y1, X0:X1] = np.clip(np.round(novo), 0, 255).astype(np.uint8)
    # o resto claro acima da faixa, junto ao canto da esquerda: o travertino (e o tapete, se cair nele)
    cx0, cy0, cx1, cy1 = m.reti(CANTO)
    tr = _tile(out[ty0:ty1, tx0:tx1].astype(np.float32), cy1 - cy0, cx1 - cx0)
    ra = out[cy0:cy1, cx0:cx1].astype(np.float32)
    k = 2.5 * s
    yy = np.arange(cy1 - cy0, dtype=np.float32)[:, None] + 0.5
    xx = np.arange(cx1 - cx0, dtype=np.float32)[None, :] + 0.5
    a = (np.clip(yy / k, 0, 1) * np.clip((cx1 - cx0 - xx) / k, 0, 1))[..., None]
    out[cy0:cy1, cx0:cx1] = np.clip(np.round(ra * (1 - a) + tr * a), 0, 255).astype(np.uint8)
    # o canto da esquerda: a cortina vertical continua até o trilho (uma onda acima), a linha escura até o toco de
    # parede, o trilho de baixo encosta nela
    e = ESQ
    vx0, vy0, vx1, vy1 = m.reti(e["cortina"])
    hh, ww = vy1 - vy0, vx1 - vx0
    Vv = _v(m, np.arange(vy0, vy1, dtype=np.float32))
    vs = Vv - e["onda_v"]
    mapy = np.repeat((m.y(vs) - 0.5)[:, None], ww, axis=1).astype(np.float32)
    mapx = np.repeat(np.arange(vx0, vx1, dtype=np.float32)[None, :], hh, axis=0)
    out[vy0:vy1, vx0:vx1] = cv2.remap(out, mapx, mapy, cv2.INTER_LINEAR)
    CB.pintar(out, m, [(e["linha"], "ret", e["linha_cor"], 0), (e["trilho"], "ret", e["trilho_cor"], 0)])
    # o traço cinza solto de fora, logo abaixo da folha da esquerda: o lado de fora de logo abaixo
    import instalacao_terreo_casad_1711 as ID
    ID._remenda(out, m, e["debaixo"], [(0, 4), (0, 6)], None, 0)
    # 4. as esquadrias do PDF
    q = COR
    pecas = [(r, "ret", q["parede"], 0) for r in PAREDES]
    for r in FOLHAS:
        x0, y0, x1, y1 = r
        ym = (y0 + y1) / 2
        pecas += [(r, "ret", q["vidro"], 0), (r, "contorno", q["vidro_fio"], q["vidro_fio_px"]),
                  ((x0, ym - q["meio_px"] / 2, x1, ym + q["meio_px"] / 2), "ret", q["meio"], 0)]
    for r in VERTICAIS:
        x0, y0, x1, y1 = r
        xm = (x0 + x1) / 2
        pecas += [(r, "ret", q["vidro"], 0), ((x0, y0, x0 + q["vidro_fio_px"], y1), "ret", q["vidro_fio"], 0),
                  ((x1 - q["vidro_fio_px"], y0, x1, y1), "ret", q["vidro_fio"], 0),
                  ((xm - q["meio_px"] / 2, y0, xm + q["meio_px"] / 2, y1), "ret", q["meio"], 0)]
    for r in MONTANTES:
        pecas += [(r, "ret", q["grafite"], 0), (r, "contorno", q["fio"], q["fio_px"])]
    CB.pintar(out, m, pecas)
    print(f"    cortina: o passo das ondas {P_:.2f} px, a origem em x {c['x0']:.2f}")
    print("    living: a fachada de baixo refeita (o tapete inteiro até a borda, a cortina contínua no passo das ondas, "
          "as 4 folhas de correr e os montantes do PDF, o canto da esquerda)")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("acao", choices=("final", "doze"))
    ap.add_argument("--opcao", default="AB")
    ap.add_argument("--entrada")
    ap.add_argument("--saida")
    a = ap.parse_args()
    fin = cv2.imread(a.entrada or str(FINAL))
    if a.acao == "final":
        cv2.imwrite(a.saida or str(FINAL), aplicar(fin, Mapa()))
        return
    from PIL import Image
    for op in a.opcao:
        f = Path(str(DOZE).format(op))
        img = cv2.imread(str(f))
        M = DF.afim_12k(fin, img)
        mp = Mapa(float(np.hypot(M[0, 0], M[1, 0])), (float(M[0, 2]), float(M[1, 2])))
        mp.ref = fin
        out = aplicar(img, mp)
        dpi = int(round(out.shape[1] / (420 / 25.4)))
        dest = a.saida.format(op) if a.saida else str(f)
        Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB)).save(dest, quality=95, subsampling=0, dpi=(dpi, dpi))
        print(f"    {Path(dest).name}")


if __name__ == "__main__":
    main()

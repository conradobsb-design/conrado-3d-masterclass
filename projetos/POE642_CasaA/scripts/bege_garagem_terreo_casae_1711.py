"""Térreo da Casa E, 17/11, na final e direto nos 12K A (Inter) e B (Kalam):

1. `garagem` (usuário: "tire. não haverá tracejado para projeções"): a projeção tracejada da laje da garagem sai; o
   piso de logo acima no lugar dos traços (`instalacao_terreo_casad_1711._remenda`, só o que destoa da faixa).
   `revisao_terreo_casae_1711.TRACEJADOS` não desenha mais a garagem.
2. `bege` (usuário, sobre o Bege Bahia do Térreo: "Sim, pode reduzir."): as manchas a 35%, como no 1º Pavimento e nas
   Casas C e D (`pedidos_subsolo_casac_1311.bege`, pela legenda 232 do quadro: a varanda, o deck, as faixas em volta
   da casa, o caminho e os pisantes da entrada). Ficam de fora o WC DCE (a mesma legenda, outro piso) e o mobiliário da
   varanda (as caixas de `mobiliario_terreo_casae_1611.VARANDA` e de `proposta_varanda_casae_1711.LUGARES`, com
   folga: a madeira das cadeiras não pode ir ao tom do piso). No 12K, os campos da final (o tom das manchas, o piso,
   as arestas) levados pelo afim, e a fórmula na escala do 12K (o desenho fino do 12K fica); as letras e as linhas
   escuras medidas no próprio 12K (a Kalam no B).
3. `banco_fio`: o fio claro embaixo do banco B1 da varanda (o fundo branco da foto da peça) vai à sombra de logo
   abaixo.

  python3 bege_garagem_terreo_casae_1711.py doze [--opcao AB]     (antes da final: a final de antes é a referência)
  python3 bege_garagem_terreo_casae_1711.py final
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import danae_foto as DF                                     # noqa: E402
from correcoes_terreo_casab_1611 import Mapa                # noqa: E402

RAIZ = AQUI.parents[1]
FINAL = RAIZ / "POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_final.png"
DOZE = RAIZ / "POE642_CasaE/entrega/POE642_CasaE_PH_Terreo_12K_opcao_{}.jpg"

GARAGEM = {"ret": (2489.5, 482.5, 3036.5, 489.5), "ds": [(0, -7), (0, 8)], "lim": 9}
BEGE_FORA = [(2390, 490, 2482, 634)]                      # o WC DCE (px)
FOLGA_MOVEIS = 8
BLOCO = 360                                               # o lado do bloco (px da final) no 12K
# caixas com desenho para o desvio local do afim no 12K (a varanda mobiliada, o hall, a escada do deck)
CAIXAS_AFIM = [(1240, 1180, 1600, 1520), (2215, 1315, 2495, 1595), (700, 1250, 800, 1520), (1300, 860, 1500, 1020)]


def _local(out, mp, caixa):
    return mp.local(out, caixa) if mp.ref is not None else mp


# ----------------------------------------------------------------------------------------------------------------------
def garagem(out, mp, q=GARAGEM):
    import instalacao_terreo_casad_1711 as ID
    r = q["ret"]
    m = _local(out, mp, (int(r[0]) - 25, int(r[1]) - 25, int(np.ceil(r[2])) + 25, int(np.ceil(r[3])) + 25))

    def destoa(reg):
        L = reg.mean(-1)
        return np.abs(L - np.median(L)) > q["lim"]
    ID._remenda(out, m, r, q["ds"], destoa, q["lim"])
    print("    garagem: a projeção tracejada da laje saiu")


# 3. o fio claro embaixo do banco B1 da varanda (o fundo branco da foto da peça, px): a sombra de logo abaixo no lugar
BANCO_FIO = {"ret": (1361.5, 1479.6, 1488.5, 1481.9)}


def banco_fio(out, mp, q=BANCO_FIO):
    """Cada coluna do fio recebe o px da 1ª linha da sombra, logo abaixo (a sombra começa rente ao banco, sem degrau)."""
    r = q["ret"]
    m = _local(out, mp, (int(r[0]) - 25, int(r[1]) - 25, int(np.ceil(r[2])) + 25, int(np.ceil(r[3])) + 25))
    x0, y0, x1, y1 = m.ret(r)
    X0, X1 = int(round(x0)), int(round(x1))
    Y0, Y1 = int(round(y0)), int(np.ceil(y1))
    out[Y0:Y1, X0:X1] = out[Y1:Y1 + 1, X0:X1]
    print("    varanda: o fio claro embaixo do banco B1 saiu")


# ----------------------------------------------------------------------------------------------------------------------
def _fora_moveis():
    import mobiliario_terreo_casae_1611 as M
    import proposta_varanda_casae_1711 as PV
    q, f = M.VARANDA, FOLGA_MOVEIS
    cx = []
    for mesa, cads in q["mesas"]:
        for r in (mesa, *cads):
            cx.append((r[0] - f, r[1] - f, r[2] + f, r[3] + f))
    for r in (q["sofa"], *q["poltronas"], PV.LUGARES["centro"], PV.LUGARES["banco"]):
        cx.append((r[0] - f, r[1] - f - 14, r[2] + f, r[3] + f + 14))
    lx, ly, ll = q["mesa_lateral"]
    cx.append((lx - ll / 2 - f, ly - ll / 2 - f, lx + ll / 2 + f, ly + ll / 2 + f))
    return cx


def campos(Q, img, q=None):
    """Os campos de `pedidos_subsolo_casac_1311.bege` na final: (x0, y0, x1, y1), o piso, o tom (a baixa frequência
    das manchas) e as arestas do tom, na caixa do Bege Bahia."""
    import pedidos_subsolo_casac_1311 as PS
    q = q or PS.BEGE
    ch = Q.chapada.copy()
    for x0, y0, x1, y1 in BEGE_FORA + _fora_moveis():
        reg = ch[int(y0):int(np.ceil(y1)), int(x0):int(np.ceil(x1))]
        reg[np.all(reg == 232, axis=2)] = (0, 0, 1)
    B = cv2.morphologyEx(np.all(ch == np.uint8(q["chapada"]), axis=2).astype(np.uint8), cv2.MORPH_CLOSE,
                         np.ones((5, 5), np.uint8)) > 0
    B &= ~(PS.BS.quieto(PS.FA.paredes_pdf, Q) > 0.3)
    im = img.astype(np.float32)
    f = cv2.GaussianBlur(im, (0, 0), 0.7)
    lum, croma = f.mean(axis=2), f.max(axis=2) - f.min(axis=2)
    verde = f[..., 1] > f[..., 2] + 4
    cand = B & ((croma < q["croma_obj"]) | (lum < q["lum_obj"]) | verde)
    n, lab, st, _ = cv2.connectedComponentsWithStats(cand.astype(np.uint8), connectivity=8)
    ok = np.zeros(n, bool)
    ok[1:] = (st[1:, cv2.CC_STAT_AREA] >= q["area_obj"])
    obj = PS._dil(ok[lab], 1)
    ys, xs = np.nonzero(B)
    y0, y1 = max(ys.min() - 30, 0), min(ys.max() + 31, Q.H)
    x0, x1 = max(xs.min() - 30, 0), min(xs.max() + 31, Q.W)
    piso = (B & ~obj)[y0:y1, x0:x1]
    sub = cv2.inpaint(img[y0:y1, x0:x1].copy(), ((~piso) * 255).astype(np.uint8), 5, cv2.INPAINT_TELEA)
    tom = cv2.GaussianBlur(cv2.medianBlur(sub, q["mediana_px"]).astype(np.float32), (0, 0), 1.5)
    tl = tom.mean(axis=2)
    gx, gy = cv2.Sobel(tl, cv2.CV_32F, 1, 0, ksize=3), cv2.Sobel(tl, cv2.CV_32F, 0, 1, ksize=3)
    aresta = PS._dil(np.hypot(gx, gy) / 8 > q["aresta"], q["aresta_px"])
    return (x0, y0, x1, y1), piso, tom, aresta


def _aplica(reg, piso, tom, aresta, s, q):
    """A fórmula de `pedidos_subsolo_casac_1311.bege` num bloco (na escala s): as letras e as linhas escuras medidas
    no bloco."""
    import pedidos_subsolo_casac_1311 as PS
    im = reg.astype(np.float32)
    tl = tom.mean(axis=2)
    lumv = im.mean(axis=2)
    texto = PS._dil(piso & (lumv < q["texto"] * tl), max(2, int(round(2 * s))))
    escuro = (piso & (lumv < q["linha"] * tl)).astype(np.uint8)
    k = int(round(21 * s)) | 1
    linhas = (cv2.morphologyEx(escuro, cv2.MORPH_OPEN, np.ones((1, k), np.uint8)) |
              cv2.morphologyEx(escuro, cv2.MORPH_OPEN, np.ones((k, 1), np.uint8))) > 0
    texto |= PS._dil(linhas, max(2, int(round(2 * s))))
    D = im / np.maximum(tom, 1)
    novo = tom * (1 + q["forca"] * (D - 1))
    m = (piso & ~aresta & ~texto).astype(np.float32)
    m = cv2.GaussianBlur(m, (0, 0), 0.8 * s) * (piso & ~texto)
    return np.clip(np.round(im * (1 - m[..., None]) + novo * m[..., None]), 0, 255).astype(np.uint8), int(m.sum())


def bege(out, mp, cp):
    import pedidos_subsolo_casac_1311 as PS
    q = PS.BEGE
    (x0, y0, x1, y1), piso, tom, aresta = cp
    if mp.ref is None:
        out[y0:y1, x0:x1], n = _aplica(out[y0:y1, x0:x1], piso, tom, aresta, 1.0, q)
        print(f"    Bege Bahia: as manchas a {q['forca'] * 100:.0f}% ({n} px)")
        return
    # no 12K, em blocos (a final em blocos de BLOCO px com 30 px de margem), no afim global com o desvio local
    # mediano de caixas com desenho (no piso liso a busca local não tem onde se apoiar); o piso do 12K 1 px (da final)
    # para dentro, para a borda (parede, grama, degrau) não ir ao tom do Bege
    ts = [mp.local(out, c).t for c in CAIXAS_AFIM]
    m = Mapa(mp.s, (float(np.median([t[0] for t in ts])), float(np.median([t[1] for t in ts]))))
    n = 0
    mg = 30
    for by in range(y0, y1, BLOCO):
        for bx in range(x0, x1, BLOCO):
            fx0, fy0, fx1, fy1 = bx, by, min(bx + BLOCO, x1), min(by + BLOCO, y1)
            pv = piso[fy0 - y0:fy1 - y0, fx0 - x0:fx1 - x0]
            if not pv.any():
                continue
            gx0, gy0 = max(fx0 - mg, x0), max(fy0 - mg, y0)
            gx1, gy1 = min(fx1 + mg, x1), min(fy1 + mg, y1)
            s = m.s
            X0, Y0 = int(np.floor(s * gx0 + m.t[0])), int(np.floor(s * gy0 + m.t[1]))
            X1, Y1 = int(np.ceil(s * gx1 + m.t[0])), int(np.ceil(s * gy1 + m.t[1]))
            X0, Y0 = max(X0, 0), max(Y0, 0)
            X1, Y1 = min(X1, out.shape[1]), min(Y1, out.shape[0])
            # o afim dos índices da caixa dos campos (origem x0, y0) ao bloco do 12K (origem X0, Y0)
            A = np.float32([[s, 0, s * x0 + m.t[0] - X0], [0, s, s * y0 + m.t[1] - Y0]])
            w, h = X1 - X0, Y1 - Y0
            p12 = cv2.warpAffine(piso.astype(np.float32), A, (w, h), flags=cv2.INTER_LINEAR) > 0.5
            k_ = int(round(s)) * 2 + 1
            p12 = cv2.erode(p12.astype(np.uint8), np.ones((k_, k_), np.uint8)).astype(bool)
            if not p12.any():
                continue
            a12 = cv2.warpAffine(aresta.astype(np.float32), A, (w, h), flags=cv2.INTER_LINEAR) > 0.5
            t12 = cv2.warpAffine(tom, A, (w, h), flags=cv2.INTER_CUBIC)
            # só o miolo do bloco (sem a margem) é gravado
            ix0, iy0 = int(round(s * fx0 + m.t[0])) - X0, int(round(s * fy0 + m.t[1])) - Y0
            ix1, iy1 = int(round(s * fx1 + m.t[0])) - X0, int(round(s * fy1 + m.t[1])) - Y0
            ix0, iy0 = max(ix0, 0), max(iy0, 0)
            novo, k = _aplica(out[Y0:Y1, X0:X1], p12, t12, a12, s, q)
            out[Y0 + iy0:Y0 + iy1, X0 + ix0:X0 + ix1] = novo[iy0:iy1, ix0:ix1]
            n += k
    print(f"    Bege Bahia (12K): as manchas a {q['forca'] * 100:.0f}%")


# ----------------------------------------------------------------------------------------------------------------------
def aplicar(img, mp, ref):
    import final3840_casae as FE
    Q = FE.QuadroE("Terreo")
    cp = campos(Q, ref)
    out = img.copy()
    garagem(out, mp)
    bege(out, mp, cp)
    banco_fio(out, mp)
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
        cv2.imwrite(a.saida or str(FINAL), aplicar(fin, Mapa(), fin))
        return
    from PIL import Image
    for op in a.opcao:
        f = Path(str(DOZE).format(op))
        img = cv2.imread(str(f))
        M = DF.afim_12k(fin, img)
        mp = Mapa(float(np.hypot(M[0, 0], M[1, 0])), (float(M[0, 2]), float(M[1, 2])))
        mp.ref = fin
        out = aplicar(img, mp, fin)
        dpi = int(round(out.shape[1] / (420 / 25.4)))
        dest = a.saida.format(op) if a.saida else str(f)
        Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB)).save(dest, quality=95, subsampling=0, dpi=(dpi, dpi))
        print(f"    {Path(dest).name}")


if __name__ == "__main__":
    main()

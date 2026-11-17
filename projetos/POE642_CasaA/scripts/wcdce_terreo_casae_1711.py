"""O WC DCE 1 do Térreo da Casa E (17/11, o post-it do cliente: "Cor do piso desse Banheiro é no mesmo cinza usado na
casa D. A bancada é no marrom tabaco. Representar melhor a cuba e a torneira"; usuário: "WC DCE"), na final e direto nos
12K A e B.

1. o piso: o cinza do WC DCE da Casa D (o tom do piso de lá, liso) no lugar do mármore de veios cinza, com o grão fino
   do piso de agora (sem os veios); a bacia, o chuveiro, o box, o rótulo e a porta ficam;
2. a bancada (ARQ_BANCADAS, junto às paredes da direita e de baixo) no granito marrom tabaco da Casa D
   (`biblioteca_subsolo_casad_1511.tabaco`, o do WC DCE de lá), com a aresta da frente (a da esquerda e a de cima) um
   tom abaixo;
3. a cuba e a torneira como as do WC DCE da Casa D (`alternativa1_terreo_casad_1611.CUBA_DCE`), em espelho (a parede
   aqui é a da direita): a louça branca de sobrepor com os cantos arredondados e o fio cinza, o bojo com a sombra
   suave, o ralo, e o misturador cromado saindo da parede (o corpo junto a ela e a bica sobre o bojo).

  python3 wcdce_terreo_casae_1711.py doze [--opcao AB]     (antes da final: a final de antes é a referência)
  python3 wcdce_terreo_casae_1711.py final
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import danae_foto as DF                                     # noqa: E402
from alternativa1_terreo_casad_1611 import CUBA_DCE, _sd_ret   # noqa: E402
from correcoes_terreo_casab_1611 import Mapa                # noqa: E402
from janela_pia_casaa_1611 import alfa_ret                  # noqa: E402

RAIZ = AQUI.parents[1]
FINAL = RAIZ / "POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_final.png"
DOZE = RAIZ / "POE642_CasaE/entrega/POE642_CasaE_PH_Terreo_12K_opcao_{}.jpg"
FINAL_D = RAIZ / "POE642_CasaD/renders/POE642_CasaD_PH_Terreo_final_rotulos.png"

# px da final
WC = {"caixa": (2385, 500, 2490, 640),
      "piso": (2398.0, 511.5, 2476.0, 628.5),
      # o que fica: o chuveiro, a faixa do box, a bacia, a bancada, a porta e o rótulo (folgado: a Kalam é maior)
      "fica": [(2446.0, 510.5, 2469.0, 531.0), (2395.0, 539.5, 2477.0, 546.0),
               (2445.5, 590.0, 2477.0, 630.0), (2392.0, 620.5, 2440.5, 628.0), (2397.0, 585.0, 2447.0, 599.5),
               (2396.0, 599.5, 2449.0, 612.5)],
      # a bacia: pela louça (o branco) e o fio dela, não pela caixa (os cantos dela são piso)
      "bacia": (2443.0, 555.0, 2477.0, 586.0), "bacia_claro": 232.0,
      # o piso de agora: L, tolerância (a sombra velha da bacia entra), croma máximo (o pontinho alaranjado entra)
      "piso_tom": (216.0, 34.0, 45.0),
      "piso_d": (2411, 527, 2437, 553),                       # um trecho liso do piso do WC DCE da Casa D
      "grao": (0.5, 1.0, 8.0),                                # o grão fino de agora: força, sigma (px), limite
      "bancada": (2446.7, 591.4, 2476.4, 629.2), "face": 0.80, "semente": 1711}
# a cuba e o misturador do WC DCE da Casa D em espelho: a parede aqui é a da direita (x 2476.4), o meio da bancada
# em y 610.3
def _espelho(r, parede=2476.4, parede_d=2386.5, dy=610.3 - 574.1):
    x0, y0, x1, y1 = r
    return (parede - (x1 - parede_d), y0 + dy, parede - (x0 - parede_d), y1 + dy)


CUBA = dict(CUBA_DCE, borda=_espelho(CUBA_DCE["borda"]), bojo=_espelho(CUBA_DCE["bojo"]),
            corpo=_espelho(CUBA_DCE["corpo"]), bica=_espelho(CUBA_DCE["bica"]),
            ralo=(2476.4 - (CUBA_DCE["ralo"][0] - 2386.5), CUBA_DCE["ralo"][1] + 610.3 - 574.1, CUBA_DCE["ralo"][2]),
            janela=(2444, 593, 2478, 627))


def _cor_piso_d():
    d = cv2.imread(str(FINAL_D)).astype(np.float32)
    x0, y0, x1, y1 = WC["piso_d"]
    return np.median(d[y0:y1, x0:x1].reshape(-1, 3), axis=0)


def piso(out, m, q=WC):
    s = m.s
    X0, Y0, X1, Y1 = m.reti(q["piso"])
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    forma = reg.shape[:2]
    L, cr = reg.mean(axis=2), reg.max(axis=2) - reg.min(axis=2)
    l0, tol, cmax = q["piso_tom"]
    eh = (np.abs(L - l0) < tol) & (cr < cmax)
    fica = np.zeros(forma, np.float32)
    for r in q["fica"]:
        rm = m.ret(r)
        fica = np.maximum(fica, alfa_ret((rm[0] - X0, rm[1] - Y0, rm[2] - X0, rm[3] - Y0), forma))
    bx0, by0, bx1, by1 = m.reti(q["bacia"])
    sub = L[by0 - Y0:by1 - Y0, bx0 - X0:bx1 - X0]
    louca = np.zeros(forma, np.uint8)
    louca[by0 - Y0:by1 - Y0, bx0 - X0:bx1 - X0] = (sub > q["bacia_claro"]).astype(np.uint8)
    kk = max(1, int(round(1.6 * s)))
    louca = cv2.dilate(louca, np.ones((2 * kk + 1, 2 * kk + 1), np.uint8)).astype(np.float32)
    fica = np.maximum(fica, louca)
    a = eh.astype(np.float32) * (1 - fica)
    a = cv2.GaussianBlur(a, (0, 0), 0.5 * s) * eh
    f, sg, lim = q["grao"]
    grao = np.clip(f * (reg - cv2.GaussianBlur(reg, (0, 0), sg * s)), -lim, lim)
    novo = _cor_piso_d()[None, None] + grao
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg * (1 - a[..., None]) + novo * a[..., None]), 0, 255).astype(np.uint8)


def bancada(out, m, q=WC):
    import biblioteca_subsolo_casad_1511 as SD
    s = m.s
    x0, y0, x1, y1 = q["bancada"]
    rm = m.ret(q["bancada"])
    X0, Y0, X1, Y1 = int(np.floor(rm[0])), int(np.floor(rm[1])), int(np.ceil(rm[2])), int(np.ceil(rm[3]))
    forma = (Y1 - Y0, X1 - X0)
    T = SD.tabaco(int(np.ceil(y1 - y0)) + 2, int(np.ceil(x1 - x0)) + 2, q["semente"])
    T = cv2.resize(T, (forma[1], forma[0]), interpolation=cv2.INTER_CUBIC)
    a = alfa_ret((rm[0] - X0, rm[1] - Y0, rm[2] - X0, rm[3] - Y0), forma)[..., None]
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    reg = reg * (1 - a) + T * a
    # a aresta da frente (a da esquerda e a de cima), um tom abaixo
    cor = np.median(T.reshape(-1, 3), axis=0) * q["face"]
    for r in ((x0, y0, x0 + 0.8, y1), (x0, y0, x1, y0 + 0.8)):
        rr = m.ret(r)
        af = alfa_ret((rr[0] - X0, rr[1] - Y0, rr[2] - X0, rr[3] - Y0), forma)[..., None]
        reg = reg * (1 - af) + cor[None, None] * af
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)


def cuba(out, m, q=CUBA):
    """A cuba e o misturador do WC DCE da Casa D (`alternativa1_terreo_casad_1611.cuba_dce`), em espelho, desenhados
    numa grade fina sobre a imagem (a final ou o 12K)."""
    s = m.s
    A0, B0, A1, B1 = m.reti(q["janela"])
    k = max(2, int(round(8 / s)))
    w, h = (A1 - A0) * k, (B1 - B0) * k
    Xi = A0 + (np.arange(w) + 0.5) / k
    Yi = B0 + (np.arange(h) + 0.5) / k
    X, Y = np.meshgrid((Xi - m.t[0] - 0.5) / s + 0.5, (Yi - m.t[1] - 0.5) / s + 0.5)
    base = cv2.resize(out[B0:B1, A0:A1].astype(np.float32), (w, h), interpolation=cv2.INTER_LINEAR)
    lc = {kk: np.float32(v) for kk, v in q["loucas"].items()}
    passo = 1.0 / (k * s)                                       # px da final por subpx

    def mistura(img, a, cor):
        a = np.clip(a, 0, 1)[..., None]
        return img * (1 - a) + (cor if np.ndim(cor) == 3 else np.float32(cor)) * a

    def sombra(img, d_fn, forca):
        dx, dy, sig, _ = q["sombra"]
        m_ = (d_fn(X - dx, Y - dy) < 0).astype(np.float32)
        sh = cv2.GaussianBlur(m_, (0, 0), sig / passo)
        return img * (1 - forca * sh)[..., None]

    def d_borda(Xs, Ys):
        return _sd_ret(Xs, Ys, q["borda"], q["raio_borda"])
    db = d_borda(X, Y)
    base = sombra(base, d_borda, q["sombra"][3])
    base = mistura(base, (db < 0).astype(np.float32), lc["borda"])
    base = mistura(base, (np.abs(db) < 0.28).astype(np.float32) * 0.85, lc["fio"])
    dj = _sd_ret(X, Y, q["bojo"], q["raio_bojo"])
    bx0, by0, bx1, by1 = q["bojo"]
    perto_cima = np.clip(1 - (Y - by0) / 4.0, 0, 1)
    perto_dir = np.clip(1 - (bx1 - X) / 4.0, 0, 1)
    perto = np.clip(1 - (-dj) / 2.5, 0, 1)
    tom = 1 - 0.09 * perto - 0.12 * np.maximum(perto_cima, perto_dir) ** 1.5
    base = mistura(base, (dj < 0).astype(np.float32), lc["bojo"][None, None] * tom[..., None])
    base = mistura(base, (np.abs(dj) < 0.22).astype(np.float32) * 0.7, lc["aresta"])
    rx, ry, rr = q["ralo"]
    dr = np.hypot(X - rx, Y - ry)
    base = mistura(base, (dr < rr).astype(np.float32), lc["ralo"])
    base = mistura(base, (np.abs(dr - rr) < 0.2).astype(np.float32) * 0.8, lc["ralo"] * 0.75)
    c0, c1 = np.float32(q["cromo"][0]), np.float32(q["cromo"][1])
    for r_, raio in ((q["corpo"], 0.9), (q["bica"], 0.6)):
        def d_m(Xs, Ys, r_=r_, raio=raio):
            return _sd_ret(Xs, Ys, r_, raio)
        base = sombra(base, d_m, 0.35)
    for r_, raio in ((q["corpo"], 0.9), (q["bica"], 0.6)):
        d = _sd_ret(X, Y, r_, raio)
        meio = (r_[1] + r_[3]) / 2
        t = np.clip(1 - np.abs(Y - meio) / ((r_[3] - r_[1]) / 2), 0, 1) ** 0.8
        base = mistura(base, (d < 0).astype(np.float32), c0[None, None] + (c1 - c0)[None, None] * t[..., None])
    # a ponta da bica (a da esquerda, sobre o bojo), um tom abaixo
    bx = q["bica"][0]
    base = mistura(base, ((np.abs(X - (bx + 0.35)) < 0.35) & (np.abs(Y - (q["bica"][1] + q["bica"][3]) / 2) < 0.6))
                   .astype(np.float32) * 0.8, c0 * 0.9)
    novo = cv2.resize(base, (A1 - A0, B1 - B0), interpolation=cv2.INTER_AREA)
    out[B0:B1, A0:A1] = np.clip(np.round(novo), 0, 255).astype(np.uint8)


def aplicar(img, mp):
    out = img.copy()
    m = mp.local(out, WC["caixa"]) if mp.ref is not None else mp
    piso(out, m)
    bancada(out, m)
    cuba(out, m)
    print("    WC DCE 1: o piso no cinza da Casa D, a bancada no marrom tabaco, a cuba e o misturador da Casa D")
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

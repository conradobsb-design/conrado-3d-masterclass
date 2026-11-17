"""O LAVABO (6,21 m²) do Térreo da Casa E pelos itens da biblioteca, nos tons de agora (17/11, usuário: "melhorar a
representação desse lavabo inteiro. substitua pelos itens da biblioteca e mantenha os tons."), na final e direto nos
12K A e B.

- `moldura`: o contorno duplo em volta da bancada (o filete claro e o traço cinza acima dela, a faixa à direita e o vão
  junto à parede da esquerda) volta a ser piso (o piso de logo acima / à direita);
- `bancada`: a pedra redesenhada lisa no retângulo do PDF (ARQ_BANCADAS, com a borda de 1,2), no creme dela (a mediana
  de agora), as faces da frente e dos lados um tom abaixo e a sombra curta no piso;
- `cuba`: a cuba esculpida da biblioteca (`cuba-social-e`, a pedra creme com a cuba entalhada: o tom da de agora), só a
  cuba e um pouco da pedra em volta, levada ao creme da bancada; a torneira dela girada para sair da parede da
  esquerda, no lugar e no comprimento da do PDF (ARQ_LOUÇAS E METAIS), com a sombra curta;
- `bacia`: a bacia da biblioteca (`bacia-escura-render`, o marrom-escuro de agora) no retângulo do PDF, a caixa
  encostada na parede de baixo; a de agora sai (o piso de logo à esquerda).

  python3 lavabo_terreo_casae_1711.py doze [--opcao AB]     (antes da final: a final de antes é a referência)
  python3 lavabo_terreo_casae_1711.py final
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import danae_foto as DF                                     # noqa: E402
import instalacao_terreo_casad_1711 as ID                   # noqa: E402
from biblioteca_terreo_casaa_1211 import pousar             # noqa: E402
from correcoes_terreo_casab_1611 import Mapa                # noqa: E402
from janela_pia_casaa_1611 import alfa_ret                  # noqa: E402

RAIZ = AQUI.parents[1]
FINAL = RAIZ / "POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_final.png"
DOZE = RAIZ / "POE642_CasaE/entrega/POE642_CasaE_PH_Terreo_12K_opcao_{}.jpg"
BIB = RAIZ / "POE642_CasaE/biblioteca-objetos/02-terreo/lavabo"

# px da final
LAVABO = {
    "caixa": (2285, 1195, 2485, 1330),
    # o contorno de agora fora da pedra: (retângulo, deslocamento do piso que entra)
    "moldura": [((2296.7, 1283.0, 2407.5, 1292.1), (0, -10)), ((2401.3, 1283.0, 2408.0, 1318.7), (8, 0)),
                ((2296.7, 1283.0, 2300.9, 1318.7), (0, -37))],
    "bancada": (2300.9, 1292.1, 2401.3, 1318.8), "tom_px": (2345, 1296, 2395, 1316),
    "faces": {"frente": 0.88, "lado": 0.93}, "sombra": 0.14,
    # a cuba entalhada: no png, a cuba (por dentro) e a torneira; na final, a cuba por dentro
    "cuba": {"png": BIB / "cuba-social-e.png", "dentro_png": (100, 70, 336, 204), "margem_png": 8,
             "torneira_png": (214, 14, 244, 100), "desvio_png": -34,
             "dentro": (2310.0, 1298.6, 2335.0, 1312.6)},
    "bacia": {"png": BIB / "bacia-escura-render.png", "ret": (2433.3, 1288.3, 2454.4, 1319.0),
              "limpa": (2430.5, 1285.0, 2457.5, 1318.6), "limpa_d": (-26, 0),
              "sombra": [{"dx": 0.01, "dy": -0.015, "sig": 0.02, "forca": 0.25}]}}


def _png(caminho):
    P = cv2.imread(str(caminho), cv2.IMREAD_UNCHANGED).astype(np.float32)
    ys, xs = np.nonzero(P[..., 3] > 0)
    return np.ascontiguousarray(P[ys.min():ys.max() + 1, xs.min():xs.max() + 1])


def moldura(out, m, q=LAVABO):
    for r, d in q["moldura"]:
        ID._remenda(out, m, r, [d], None, 0)


def _tom(out, m, q=LAVABO):
    tx0, ty0, tx1, ty1 = m.reti(q["tom_px"])
    return np.median(out[ty0:ty1, tx0:tx1].reshape(-1, 3).astype(np.float32), axis=0)


def bancada(out, m, tom, q=LAVABO):
    s = m.s
    rm = m.ret(q["bancada"])
    g = int(np.ceil(3 * s))
    X0, Y0 = int(np.floor(rm[0])) - g, int(np.floor(rm[1])) - g
    X1, Y1 = int(np.ceil(rm[2])) + g, int(np.ceil(rm[3]))
    forma = (Y1 - Y0, X1 - X0)
    reg = out[Y0:Y1, X0:X1].astype(np.float32)

    def a_de(r):
        rr = m.ret(r)
        return alfa_ret((rr[0] - X0, rr[1] - Y0, rr[2] - X0, rr[3] - Y0), forma)
    a = a_de(q["bancada"])
    # a sombra curta no piso em volta (a pedra solta da parede da esquerda)
    sb = cv2.GaussianBlur(a, (0, 0), 0.9 * s)
    reg *= (1 - q["sombra"] * sb * (1 - a))[..., None]
    rng = np.random.default_rng(1711)
    n = cv2.GaussianBlur(rng.normal(0, 1, forma).astype(np.float32), (0, 0), sigmaX=5 * s, sigmaY=1.0 * s)
    n = 1 + 0.010 * n / max(float(n.std()), 1e-6)
    reg = reg * (1 - a[..., None]) + (tom[None, None] * n[..., None]) * a[..., None]
    # as faces: a da frente (em cima) e as dos lados, um tom abaixo
    x0, y0, x1, y1 = q["bancada"]
    for r, f in (((x0, y0, x1, y0 + 0.8), q["faces"]["frente"]), ((x0, y0, x0 + 0.6, y1), q["faces"]["lado"]),
                 ((x1 - 0.6, y0, x1, y1), q["faces"]["lado"])):
        af = a_de(r)[..., None]
        reg = reg * (1 - af) + (tom * f)[None, None] * af
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)


def _colar(out, m, P, u0, v0, k, sombra=None):
    """P (BGR + alfa 0..1, float) com o canto de cima à esquerda em (u0, v0) da final, k px da final por px de P."""
    s = m.s
    sc = k * s
    sig = max(0.0, 0.42 / sc - 0.3)
    if sig > 0:
        P = cv2.GaussianBlur(P, (0, 0), sig)
    ax = m.x(u0 + 1.5 * k) - m.x(u0 + 0.5 * k)
    bx, by = m.x(u0 + 0.5 * k) - 0.5, m.y(v0 + 0.5 * k) - 0.5
    h, w = P.shape[:2]
    X0, Y0 = int(np.floor(bx)) - 2, int(np.floor(by)) - 2
    X1, Y1 = int(np.ceil(bx + w * ax)) + 3, int(np.ceil(by + h * ax)) + 3
    M = np.float32([[ax, 0, bx - X0], [0, ax, by - Y0]])
    W = cv2.warpAffine(P, M, (X1 - X0, Y1 - Y0), flags=cv2.INTER_LINEAR, borderValue=0)
    a = np.clip(W[..., 3], 0, 1)
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    if sombra:
        dx, dy, sg, f = sombra
        Ms = np.float32([[1, 0, dx * s], [0, 1, dy * s]])
        so = cv2.GaussianBlur(cv2.warpAffine(a, Ms, (a.shape[1], a.shape[0])), (0, 0), sg * s)
        reg *= (1 - f * so)[..., None]
    reg = reg * (1 - a[..., None]) + W[..., :3] * a[..., None]
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)


def cuba(out, m, tom, q=LAVABO["cuba"]):
    P = cv2.imread(str(q["png"]), cv2.IMREAD_UNCHANGED).astype(np.float32)
    rgb = P[..., :3].copy()
    # a cuba sem a torneira: as colunas da torneira pelas de logo à esquerda (a borda da cuba é reta)
    tx0, ty0, tx1, ty1 = q["torneira_png"]
    dd = q["desvio_png"]
    limpo = rgb.copy()
    limpo[:ty1 + 12, tx0:tx1] = rgb[:ty1 + 12, tx0 + dd:tx1 + dd]
    # a cuba e a pedra em volta, levadas ao creme da bancada
    dx0, dy0, dx1, dy1 = q["dentro_png"]
    mg = q["margem_png"]
    C = limpo[dy0 - mg:dy1 + mg, dx0 - mg:dx1 + mg]
    hh, ww = C.shape[:2]
    yy, xx = np.mgrid[0:hh, 0:ww]
    borda = (np.minimum.reduce([xx, yy, ww - 1 - xx, hh - 1 - yy]) < mg - 2)
    rz = tom / np.median(C[borda].reshape(-1, 3), axis=0)
    C = C * rz[None, None]
    dist = np.minimum.reduce([xx, yy, ww - 1 - xx, hh - 1 - yy]).astype(np.float32)
    aC = np.clip((dist + 0.5) / mg, 0, 1)
    k = (q["dentro"][2] - q["dentro"][0]) / (dx1 - dx0)
    u0 = q["dentro"][0] - mg * k
    v0 = (q["dentro"][1] + q["dentro"][3]) / 2 - (dy1 - dy0) / 2 * k - mg * k
    _colar(out, m, np.dstack([C, aC]), u0, v0, k)
    # a torneira: o que difere da pedra sem ela, girada para sair da parede da esquerda (o bico para a direita)
    T = rgb[ty0:ty1, tx0:tx1]
    aT = np.clip((np.abs(T - limpo[ty0:ty1, tx0:tx1]).max(-1) - 8) / 22, 0, 1)
    aT = aT * (P[ty0:ty1, tx0:tx1, 3] / 255)
    TT = np.ascontiguousarray(np.rot90(np.dstack([T, aT]), 1))
    # no png, a borda de cima da cuba (por dentro) fica a (dy0 - ty0) px da ponta de cima do recorte
    ut = q["dentro"][0] - (dy0 - ty0) * k
    # e o eixo da torneira (a coluna média dela no png) no eixo da cuba, o da torneira do PDF
    cxT = float((aT.sum(0) * np.arange(tx1 - tx0)).sum() / max(float(aT.sum()), 1e-6))
    vt = (q["dentro"][1] + q["dentro"][3]) / 2 - ((tx1 - tx0 - 1 - cxT) + 0.5) * k
    _colar(out, m, TT, ut, vt, k, sombra=(0.5, 0.6, 0.45, 0.30))


def bacia(out, m, q=LAVABO["bacia"]):
    s = m.s
    ID._remenda(out, m, q["limpa"], [q["limpa_d"]], None, 0)
    P = _png(q["png"])
    x0, y0, x1, y1 = q["ret"]
    o = out.astype(np.float32)
    # a caixa (em cima na imagem) contra a parede de baixo: girada 180°
    pousar(o, P, m.x((x0 + x1) / 2) - 0.5, m.y((y0 + y1) / 2) - 0.5, (x1 - x0) * s, (y1 - y0) * s, 180.0,
           q["sombra"], DF.PX_M * s)
    out[...] = np.clip(np.round(o), 0, 255).astype(np.uint8)


def aplicar(img, mp):
    out = img.copy()
    m = mp.local(out, LAVABO["caixa"]) if mp.ref is not None else mp
    tom = _tom(out, m)
    moldura(out, m)
    bancada(out, m, tom)
    cuba(out, m, tom)
    bacia(out, m)
    print("    LAVABO: a bancada lisa no creme dela, a cuba esculpida e a bacia da biblioteca")
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

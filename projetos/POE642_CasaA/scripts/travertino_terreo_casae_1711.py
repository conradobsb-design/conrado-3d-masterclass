"""O travertino do Térreo da Casa E sem as manchas cinzas e sem as juntas (17/11, usuário: "as manchas cinzas, remova
as juntas também"), na final e direto nos 12K A e B.

O travertino (Living e sala de jantar, circulações, escritório, lavabo, hall, adega; a escada principal fica, com os
degraus) é hoje um grid de placas, cada uma num tom (as mais escuras são as manchas cinzas), com o fio da junta entre
elas. O piso é reconhecido pela cor (o creme do travertino; o Bege Bahia de fora é mais amarelo e fica) dentro das
áreas dele, só os pedaços grandes (o creme de dentro de um móvel não entra) e fora das peças listadas em `FICA`.
Em cada px do piso:

- o tom de fundo (o desfocado do piso em volta, só do piso) dá lugar a um tom só, a mediana do travertino longe das
  peças: somem as placas mais escuras e o degrau de tom de uma placa para a outra;
- os veios ficam (o que o px tem a mais ou a menos que o fundo dele);
- junto às peças e às paredes a sombra fica: o quanto o fundo ali é mais escuro que o tom da placa dele (o desfocado
  largo do piso longe das peças) volta, até ~25 px delas;
- os fios das juntas verticais (a linha fina que se repete no comprido da coluna, ao contrário dos veios, que correm
  deitados) saem: o que o fio tem de igual ao longo da coluna é tirado, longe das paredes.

  python3 travertino_terreo_casae_1711.py doze [--opcao AB]     (antes da final: a final de antes é a referência)
  python3 travertino_terreo_casae_1711.py final
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

# px da final
CAIXA = (1570, 740, 2490, 1592)
AREAS = [(1576, 815, 2480, 1588),          # living e jantar, circulações, escritório, lavabo, hall
         (2085, 755, 2222, 822)]           # adega
FICA = [(1872, 958, 2222, 1052),           # a escada principal (os degraus)
        (2298, 1289, 2404, 1321),          # a bancada do lavabo
        (2428, 1284, 2460, 1321)]          # a bacia do lavabo
# as peças creme sobre o travertino (o estofado tem a cor do piso): dentro delas (mais 4 px) só a correção larga e suave
# do tom, a mesma do piso em volta, sem mexer no desenho do estofado
PECAS = [(1934, 1347, 1991, 1403), (2034, 1347, 2088, 1404),      # as 4 poltronas da mesa redonda
         (1934, 1430, 1991, 1486), (2034, 1430, 2088, 1486),
         (1695, 1289, 1746, 1339), (1636, 1342, 1684, 1386),      # as 2 poltronas do tapete azul
         (1645, 1432, 1832, 1517),                                # o sofá curvo
         (2368, 1116, 2425, 1173)]                                # a poltrona do escritório
PECA_FOLGA = 4.0
COR = {"a": 130.6, "b": 135.7, "da": 2.6, "db": 3.3, "L": (188, 242)}
AREA_MIN = 6000            # px² da final: o pedaço de creme menor que isso é peça, não piso
SIG_FUNDO, SIG_PLACA = 5.0, 22.0
SOMBRA_D, SOMBRA_RAMPA = 14.0, 8.0
PINTA_DL, PINTA_AREA = 14.0, 6.0     # o pontinho: mais escuro (ou claro) que o fundo, pequeno e redondo
JUNTA_SIG_Y, JUNTA_D0, JUNTA_RAMPA = 20.0, 4.0, 6.0


def _nc(img, w, sig_x, sig_y=None):
    """O desfocado normalizado: só os px de peso w."""
    sig_y = sig_x if sig_y is None else sig_y
    num = cv2.GaussianBlur(img * (w[..., None] if img.ndim == 3 else w), (0, 0), sigmaX=sig_x, sigmaY=sig_y)
    den = cv2.GaussianBlur(w, (0, 0), sigmaX=sig_x, sigmaY=sig_y)
    d = np.maximum(den, 1e-4)
    return (num / (d[..., None] if img.ndim == 3 else d)), den


def mascara(sub, m, X0, Y0):
    s = m.s
    h, w = sub.shape[:2]
    Z = np.zeros((h, w), np.uint8)
    for r in AREAS:
        x0, y0, x1, y1 = m.reti(r)
        Z[max(0, y0 - Y0):max(0, y1 - Y0), max(0, x0 - X0):max(0, x1 - X0)] = 1
    for r in FICA:
        x0, y0, x1, y1 = m.reti(r)
        Z[max(0, y0 - Y0):max(0, y1 - Y0), max(0, x0 - X0):max(0, x1 - X0)] = 0
    lab = cv2.cvtColor(np.clip(sub, 0, 255).astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32)
    L, A, B = lab[..., 0], lab[..., 1], lab[..., 2]
    pre = (Z > 0) & (np.abs(A - COR["a"]) < 4) & (np.abs(B - COR["b"]) < 5) & (L > COR["L"][0])
    a0, b0 = float(np.median(A[pre])), float(np.median(B[pre]))
    F = ((Z > 0) & (np.abs(A - a0) < COR["da"]) & (np.abs(B - b0) < COR["db"]) & (L > COR["L"][0])
         & (L < COR["L"][1])).astype(np.uint8)
    n, lab_, st, _ = cv2.connectedComponentsWithStats(F, 4)
    grandes = np.zeros(n, bool)
    grandes[1:] = st[1:, cv2.CC_STAT_AREA] >= AREA_MIN * s * s
    pecas = np.zeros((h, w), np.float32)
    g = PECA_FOLGA
    for r in PECAS:
        x0, y0, x1, y1 = m.reti((r[0] - g, r[1] - g, r[2] + g, r[3] + g))
        pecas[max(0, y0 - Y0):max(0, y1 - Y0), max(0, x0 - X0):max(0, x1 - X0)] = 1
    return grandes[lab_] & (pecas == 0), F > 0, pecas, (a0, b0)


def aplicar(img, mp):
    s = mp.s
    X0, Y0, X1, Y1 = mp.reti(CAIXA)
    sub = img[Y0:Y1, X0:X1].astype(np.float32)
    F, Fcor, pecas, ab = mascara(sub, mp, X0, Y0)
    Ff = F.astype(np.float32)
    d = cv2.distanceTransform(F.astype(np.uint8), cv2.DIST_L2, 5)
    longe = (d > 12 * s).astype(np.float32)
    tom = np.median(sub[longe > 0].reshape(-1, 3), axis=0)
    fundo, _ = _nc(sub, Ff, SIG_FUNDO * s)
    placa, cob = _nc(sub, longe, SIG_PLACA * s)
    placa = np.where((cob > 0.02)[..., None], placa, tom[None, None])
    # a sombra junto às peças: o fundo mais escuro que a placa dele
    sombra = np.minimum(0.0, fundo - placa)
    w_s = np.clip((SOMBRA_D * s - d) / (SOMBRA_RAMPA * s), 0, 1)[..., None]
    alta = sub - fundo
    # os pontinhos cinzas (e os claros) soltos no piso: pequenos e redondos, ao contrário dos veios, que correm deitados
    aL = alta.mean(-1)
    pint = np.zeros(F.shape, np.float32)
    for sinal in (-1, 1):
        cand = ((sinal * aL > PINTA_DL) & F & (d > 2.5 * s)).astype(np.uint8)
        n, lab_, st, _ = cv2.connectedComponentsWithStats(cand, 8)
        ok = np.zeros(n, bool)
        if n > 1:
            ww, hh, ar = st[1:, cv2.CC_STAT_WIDTH], st[1:, cv2.CC_STAT_HEIGHT], st[1:, cv2.CC_STAT_AREA]
            ok[1:] = (ar <= PINTA_AREA * s * s) & (ww <= 2 * hh + 1) & (hh <= 2 * ww + 1)
        um = ok[lab_].astype(np.uint8)
        # só o pontinho solto: nenhum outro candidato logo em volta
        kk = max(1, int(round(3 * s)))
        viz = cv2.dilate(um, np.ones((2 * kk + 1, 2 * kk + 1), np.uint8)) & (cand - um)
        nviz = np.zeros(n, np.int64)
        np.add.at(nviz, cv2.dilate(lab_.astype(np.float32) * um, np.ones((2 * kk + 1, 2 * kk + 1), np.uint8))
                  .astype(np.int64)[viz > 0], 1)
        ok &= nviz == 0
        pint = np.maximum(pint, ok[lab_].astype(np.float32))
    k = max(1, int(round(0.8 * s)))
    pint = cv2.GaussianBlur(cv2.dilate(pint, np.ones((2 * k + 1, 2 * k + 1), np.uint8)), (0, 0), 0.5 * s)
    alta = alta * (1 - np.clip(pint * 1.5, 0, 1))[..., None]
    # os fios das juntas verticais: o que a alta tem de igual ao longo da coluna, longe das paredes
    fio, _ = _nc(alta, Ff, 0.35 * s, JUNTA_SIG_Y * s)
    w_j = np.clip((d - JUNTA_D0 * s) / (JUNTA_RAMPA * s), 0, 1)[..., None]
    novo = tom[None, None] + alta - w_j * fio + w_s * sombra
    delta = (novo - sub) * Ff[..., None]
    # o delta estendido 1 px além do piso (as bordas meio piso, meio peça), na medida do piso nelas
    ext, _ = _nc(delta, Ff, 0.8 * s)
    wf = np.clip(cv2.GaussianBlur(Ff, (0, 0), 0.6 * s) * 1.6, 0, 1)
    wf = np.maximum(wf, Ff)
    D = np.where(F[..., None], delta, ext * wf[..., None])
    # nas peças creme: só a correção larga (o tom da placa em volta para o tom só), nos px da cor do piso
    Mo = np.clip(cv2.GaussianBlur(pecas, (0, 0), 1.5 * s) * 2 - 0.5, 0, 1)[..., None]
    D = D * (1 - Mo) + ((tom[None, None] - placa) * Fcor[..., None]) * Mo
    out = img.copy()
    out[Y0:Y1, X0:X1] = np.clip(np.round(sub + D), 0, 255).astype(np.uint8)
    print(f"    pontinhos: {int((pint > 0.5).sum())} px")
    print(f"    travertino: {int(F.sum()):,} px de piso num tom só ({tom.round(1).tolist()}, a/b {ab[0]:.1f}/{ab[1]:.1f}),"
          " sem as placas mais escuras e sem os fios das juntas; as sombras junto às peças ficam")
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
        out = aplicar(img, mp)
        dpi = int(round(out.shape[1] / (420 / 25.4)))
        dest = a.saida.format(op) if a.saida else str(f)
        Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB)).save(dest, quality=95, subsampling=0, dpi=(dpi, dpi))
        print(f"    {Path(dest).name}")


if __name__ == "__main__":
    main()

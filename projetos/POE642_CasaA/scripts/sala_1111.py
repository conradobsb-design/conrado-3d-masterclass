r"""Casa A, Térreo: a sala de estar nos tons da vista 3D do usuário (11/11: "segue vista interna em 3d da sala da casa A,
para usar tons de poltrona e sofá e tapete"; prévia aprovada: "a sala ok"; depois: "nestas poltronas, apenas o encosto
delas em terracota. nas quatro. e precisa ficar perfeito, sem borrões e bem preenchido dentro da área de encosto";
"somente o contorno do encosto"; "contorno externo, não próximo ao assento").

- Os tapetes (`terreo_casaa_1011.tapetes_1111`, opção A): os dois em taupe; o redondo da sala de estar com o desenho
  da vista 3D (creme acinzentado com manchas abstratas em taupe, como sombra de folhagem), com a luz de cada px (a
  trama e a sombra das peças) mantida.
- O sofá curvo e a poltrona avulsa em bouclé creme quente; o par de poltronas junto à mesinha em veludo verde-floresta
  (a peça é o que não é tapete, já separado com a sombra; recolorida pela luz).
- As 4 poltronas em X: só o contorno externo do encosto em terracota. A concha é separada no próprio modelo da
  poltrona (`final3840_casae._modelo_poltrona_1p`, a mesma das 4): o vinco entre o assento e o encosto, com as pontas
  levadas até a borda; da borda de fora até a crista do encosto (`FRACAO_EXT` da espessura da concha) é terracota, o
  lado de dentro, junto ao assento, fica creme. O modelo recolorido é posto de novo exatamente como as poltronas foram
  postas (`revisao_casaa_2910.poltronas_ta`: o mesmo giro, a mesma escala e o mesmo centro), só nos px da faixa.
- A mesa de centro em nogueira e as três mesinhas laterais em grafite (a madeira delas medida antes das trocas).
"""
import contextlib
import io
import sys
from pathlib import Path

import cv2
import numpy as np
from scipy import ndimage

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

SALA_1111 = {
    "pecas": {"sofa": ("ARQ_LAYOUT HUMANIZAÇÃO", (1690.2, 582.2, 1845.2, 724.0)),
              "polt_par_esq": ("ARQ_LAYOUT HUMANIZAÇÃO", (1749.9, 754.8, 1794.0, 801.5)),
              "polt_par_dir": ("ARQ_LAYOUT HUMANIZAÇÃO", (1817.9, 754.8, 1862.0, 801.5)),
              "polt_dir": ("ARQ_LAYOUT HUMANIZAÇÃO", (1869.1, 641.5, 1920.9, 694.8)),
              "lat1": ("DOC_TEXTOS", (1842.4, 632.7, 1862.2, 652.6)),
              "lat2": ("DOC_TEXTOS", (1796.1, 763.5, 1815.9, 783.3)),
              "lat3": ("DOC_TEXTOS", (1732.8, 686.0, 1757.1, 707.8))},
    "mesa_centro_px": (1985, 470, 2080, 535),
    "redondo_px": (2036, 502, 120),
    "creme": (200, 214, 226), "verde": (58, 80, 60), "terracota": (62, 98, 172),
    "nogueira": (48, 78, 118), "grafite": (66, 68, 70),
    "tapete_base": (204, 213, 222), "tapete_mancha": (148, 158, 170), "semente": 311,
    "fracao_ext": 0.55,
}


def _maior(m, est=None):
    lab, n = ndimage.label(m, est)
    if n <= 1:
        return m
    tam = ndimage.sum(np.ones(m.shape), lab, index=np.arange(1, n + 1))
    return lab == (1 + int(np.argmax(tam)))


def _mascara_madeira(img, caixa, rb=40):
    x0, y0, x1, y1 = caixa
    im = img[y0:y1, x0:x1].astype(np.float32)
    m = ndimage.binary_opening((im[..., 2] - im[..., 0]) > rb, np.ones((2, 2)))
    return caixa, ndimage.binary_fill_holes(_maior(m))


def _pinta_madeira(out, img, mm, alvo):
    (x0, y0, x1, y1), m = mm
    im = out[y0:y1, x0:x1].astype(np.float32)
    L = img[y0:y1, x0:x1].astype(np.float32).mean(axis=2)
    a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.6)
    novo = np.float32(alvo)[None, None, :] * (L / float(L[m].mean()))[..., None]
    out[y0:y1, x0:x1] = np.clip(im * (1 - a[..., None]) + novo * a[..., None], 0, 255).astype(np.uint8)


def _desenho_tapete(out, img, q, px_m):
    """O redondo: o desenho da vista 3D por cima do taupe, com a luz do taupe pintado."""
    import paisagismo as PG
    import terreo_casaa_1011 as TA
    im0 = img.astype(np.float32)
    mud = np.abs(out.astype(np.float32) - im0).max(axis=2)
    tapete = mud > 8
    cx, cy, r = q["redondo_px"]
    H, W = mud.shape
    yy, xx = np.mgrid[0:H, 0:W]
    redondo = (xx - cx) ** 2 + (yy - cy) ** 2 <= (r + 6) ** 2
    alfa = np.clip(mud / 40.0, 0, 1) * redondo
    y0, y1, x0, x1 = cy - r - 10, cy + r + 10, cx - r - 10, cx + r + 10
    sh = (y1 - y0, x1 - x0)
    rng = np.random.default_rng(q["semente"])
    wx = PG.ruido(sh, 0.6 * px_m, rng) * 0.25 * px_m
    wy = PG.ruido(sh, 0.6 * px_m, rng) * 0.25 * px_m
    gy, gx = np.mgrid[0:sh[0], 0:sh[1]].astype(np.float32)
    n1 = PG.ruido(sh, 0.30 * px_m, rng) + 0.5 * PG.ruido(sh, 0.12 * px_m, rng) + 0.25 * PG.ruido(sh, 0.05 * px_m, rng)
    n1 = cv2.remap(n1, gx + wx, gy + wy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    mot = 1 / (1 + np.exp(-(n1 - 0.25) * 6.0))
    cor = np.float32(q["tapete_base"]) * (1 - mot[..., None]) + np.float32(q["tapete_mancha"]) * mot[..., None]
    taupe = np.float32(TA.TAPETES_1111["opcoes"]["A"])
    rel = out[y0:y1, x0:x1].astype(np.float32).mean(axis=2) / float(taupe.mean())
    a = alfa[y0:y1, x0:x1][..., None]
    o = out.astype(np.float32)
    o[y0:y1, x0:x1] = o[y0:y1, x0:x1] * (1 - a) + cor * rel[..., None] * a
    return np.clip(o, 0, 255).astype(np.uint8), tapete


def _estofado(out, img, m, alvo, tapete, contraste=1.0, tirar=None):
    """O estofado em cima do tapete: a peça é o que o tapete (já separado, com a sombra) não é, perto do PDF."""
    L = img.astype(np.float32).mean(axis=2)
    pdf = m > 0.5
    if tirar is not None:
        pdf &= ~cv2.dilate((tirar > 0.5).astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    zona = cv2.dilate(pdf.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    dentro = ndimage.binary_fill_holes(~tapete & zona)
    dentro = ndimage.binary_opening(_maior(dentro), np.ones((3, 3)))
    alfa = cv2.GaussianBlur(dentro.astype(np.float32), (0, 0), 0.6)
    rel = 1 + contraste * (L / float(L[dentro].mean()) - 1)
    novo = np.float32(alvo)[None, None, :] * rel[..., None]
    o = out.astype(np.float32)
    return np.clip(o * (1 - alfa[..., None]) + novo * alfa[..., None], 0, 255).astype(np.uint8)


def concha_modelo(cor, a):
    """A concha (encosto e braços) do modelo da poltrona: o lado de fora do vinco entre o assento e o encosto (o vinco é
    a linha escura contínua; as pontas dele são levadas até a borda do modelo)."""
    L = cor.mean(axis=2)
    dentro = a > 0.5
    borda = cv2.distanceTransform(dentro.astype(np.uint8), cv2.DIST_L2, 3)
    loc = L - cv2.GaussianBlur(L, (0, 0), 2.5)
    vinco = _maior((loc < -5) & (borda > 2.5), np.ones((3, 3)))
    ys, xs = np.nonzero(vinco)
    pts = np.stack([xs, ys], 1).astype(float)
    pontas = (pts[np.argmin(pts[:, 0] + 0.01 * pts[:, 1])], pts[np.argmax(pts[:, 1] - 0.01 * pts[:, 0])])
    corte = vinco.astype(np.uint8).copy()
    for p in pontas:
        d = np.hypot(*(pts - p).T)
        u = p - pts[(d > 3) & (d < 8)].mean(0)
        u /= np.hypot(*u)
        fim = p.copy()
        for t in range(1, 40):
            c = p + u * t
            if not (0 <= c[0] < a.shape[1] and 0 <= c[1] < a.shape[0]) or a[int(c[1]), int(c[0])] < 0.05:
                break
            fim = c
        cv2.line(corte, (int(p[0]), int(p[1])), (int(round(fim[0])), int(round(fim[1]))), 1, 2)
    corte = corte.astype(bool)
    lab, _ = ndimage.label(dentro & ~corte)
    return lab, corte, dentro


def encostos_terracota(out, Q, q):
    with contextlib.redirect_stdout(io.StringIO()):
        import final3840_casae as E
        import revisao_casaa_2910 as RA
    qe = E.POLTRONAS_TE
    cor_m, a_m = E._modelo_poltrona_1p(qe)
    fx, fy = qe["modelo"]["frente"]
    lab, corte, dent_m = concha_modelo(cor_m, a_m)
    H, W = a_m.shape
    sx, sy = int(W / 2 + fx * 0.12 * W), int(H / 2 + fy * 0.12 * W)
    assento = (lab == lab[sy, sx]) | (corte & dent_m)
    concha = ndimage.binary_opening(dent_m & ~assento, np.ones((2, 2)))
    # só o contorno externo: da borda de fora até a crista do encosto
    d_out = cv2.distanceTransform(dent_m.astype(np.uint8), cv2.DIST_L2, 5)
    d_in = cv2.distanceTransform((~(dent_m & ~concha)).astype(np.uint8), cv2.DIST_L2, 5)
    ext = concha & (d_out / np.maximum(d_out + d_in, 1e-3) <= q["fracao_ext"])
    fora = ~dent_m & (cv2.distanceTransform((~ext).astype(np.uint8), cv2.DIST_L2, 5) < 3)
    Lm = cv2.GaussianBlur(cor_m.mean(axis=2), (0, 0), 0.6)
    cor_t = np.float32(q["terracota"])[None, None, :] * np.clip(Lm / float(Lm[ext].mean()), 0.55, 1.2)[..., None]
    k_m = cv2.GaussianBlur((ext | fora).astype(np.float32), (0, 0), 0.5) * (1 - ((dent_m & ~concha) & ~ext))
    cor_novo = cor_m * (1 - k_m[..., None]) + cor_t * k_m[..., None]
    o = out.astype(np.float32)
    n = 0
    for nome, _, r, (dx, dy), t_pt in RA.POLTRONAS_TA["Terreo"]["pecas"]:
        if "em X" not in nome:
            continue
        (ax, ay), (bx_, by) = Q.p2q(r[0], r[1]), Q.p2q(r[2], r[3])
        cx, cy = (ax + bx_) / 2, (ay + by) / 2
        t = t_pt * Q.px_m / 56.69 if t_pt else max(bx_ - ax, by - ay)
        ang = np.degrees(np.arctan2(dx, dy) - np.arctan2(fx, fy))
        esc = t / max(a_m.shape)
        c2, a2 = E._girar_peca(cor_novo, a_m, esc, ang)
        lado = int(np.ceil(max(a_m.shape) * esc * 1.5)) + 4           # o quadro de `final3840_casae._girar_peca`
        M = cv2.getRotationMatrix2D((W / 2, H / 2), float(ang), esc)
        M[0, 2] += lado / 2 - W / 2
        M[1, 2] += lado / 2 - H / 2
        al = np.clip(cv2.warpAffine(k_m, M, (lado, lado), flags=cv2.INTER_LINEAR) * a2, 0, 1)
        # a borda de fora cheia: o alfa do recorte (com o bouclé da borda) reforçado, sem sobrar o creme de antes
        al = np.clip(al * 1.7, 0, 1) * (a2 > 0.08)
        h, w = al.shape
        x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
        reg = o[y0:y0 + h, x0:x0 + w]
        o[y0:y0 + h, x0:x0 + w] = reg * (1 - al[..., None]) + c2 * al[..., None]
        n += 1
    return np.clip(o, 0, 255).astype(np.uint8), n


def sala_1111(Q, img, q=None):
    import terreo_casaa_1011 as TA
    q = q or SALA_1111
    P = {}
    for k, (c, r) in q["pecas"].items():
        with contextlib.redirect_stdout(io.StringIO()):
            P[k] = Q.preencher(lambda d, c=c, r=r: d.get("layer") == c and
                               max(abs(u - v) for u, v in zip(d["rect"], r)) < 0.5, ss=2, fs=True)
    mad = {"centro": _mascara_madeira(img, q["mesa_centro_px"])}
    for k in ("lat1", "lat2", "lat3"):
        ys, xs = np.nonzero(P[k] > 0.5)
        mad[k] = _mascara_madeira(img, (xs.min() - 3, ys.min() - 3, xs.max() + 4, ys.max() + 4))
    out = TA.tapetes_1111(Q, img, dict(TA.TAPETES_1111, opcao="A"))
    out, tapete = _desenho_tapete(out, img, q, Q.px_m)
    out = _estofado(out, img, P["sofa"], q["creme"], tapete, 1.1, tirar=P["lat3"])
    out = _estofado(out, img, P["polt_dir"], q["creme"], tapete, 1.1)
    out = _estofado(out, img, P["polt_par_esq"], q["verde"], tapete, 1.5)
    out = _estofado(out, img, P["polt_par_dir"], q["verde"], tapete, 1.5)
    out, n = encostos_terracota(out, Q, q)
    _pinta_madeira(out, img, mad["centro"], q["nogueira"])
    for k in ("lat1", "lat2", "lat3"):
        _pinta_madeira(out, img, mad[k], q["grafite"])
    print(f"      sala: tapetes (taupe; o redondo com o desenho da vista 3D), sofá e poltrona avulsa em creme, o par "
          f"em verde, o contorno externo do encosto das {n} poltronas em X em terracota, a mesa de centro em nogueira, "
          f"as laterais em grafite")
    return out

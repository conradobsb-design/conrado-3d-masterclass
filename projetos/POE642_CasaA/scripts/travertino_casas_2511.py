"""O travertino bruto novo em todas as casas e pavimentos (25/11).

Usuário, depois do Térreo da Casa A (`travertino_terreo_casaa_2511.py`): "sim, aplique em todas as casas e pavimentos".
O mesmo travertino (a opção 2, Navona marfim, 1,2 m por quadro, espelhado, em coordenadas absolutas da imagem) nos
pisos de travertino bruto das outras 11 plantas, e as bancadas de travertino no tom do piso levemente escuro (o pedido
do lavabo da Casa A: "bancada no tom do piso (levemente escuro)").

- Onde é travertino: a base chapada da legenda de cada planta (o #DCD9CA, a cor do travertino em todas as casas), um
  pouco dilatada, e dentro dela o teste de cor contra o travertino de hoje daquela planta (a mediana Lab do miolo da
  região): os móveis, os tapetes, as letras e as paredes ficam; os restos do piso antigo junto às paredes entram
  (mais claros ou mais acinzentados, perto do piso achado).
- O piso: a textura vezes a luz do lugar (a luminância antiga bem desfocada, relativa à mediana), como na Casa A.
- As bancadas: os retângulos de bancada do PDF (ARQ_BANCADAS) que hoje estão no travertino (a maior parte da pedra no
  tom do piso) recebem a textura do piso (o veio ao comprido da bancada) a 90%, com a luz da própria bancada (a cuba
  esculpida); os metais (cinza) ficam.
- Finais (e as variantes), prancha e 12K A e B (no 12K, só perto do piso achado na final, pelo mapa de `doze_k.json`;
  as bancadas pelo registro local).

  python3 travertino_casas_2511.py                 # todas
  python3 travertino_casas_2511.py B_Terreo ...    # só estas
  python3 travertino_casas_2511.py --so-final ...  # sem os 12K (para conferir)
"""
import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
sys.path.insert(0, str(Path(__file__).resolve().parent))
import esquadrias_pretas_1911 as EP          # noqa: E402
import travertino_terreo_casaa_2511 as TV    # noqa: E402

LEGENDA = (202, 217, 220)                    # #DCD9CA (BGR): o travertino na base chapada de todas as casas
P = dict(lim=10.0, lim_borda=13.0, area_min=1500, dil=9, peso=(0.35, 1.6, 1.6), borda_px=6, borda_dE=15.0,
         bancada_frac=0.60, bancada_dE=12.0, bancada_escuro=0.90, bancada_area=120.0, bancada_anel=0.30)


def regiao(Q):
    ch = Q.chapada.astype(np.int16)
    m = (np.abs(ch - np.int16(LEGENDA)).sum(2) <= 6).astype(np.uint8)
    return m


def referencia(img, reg):
    er = cv2.erode(reg, np.ones((15, 15), np.uint8)) > 0
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    v = lab[er]
    v = v[(v[:, 0] > 170) & (v[:, 0] < 245) & (np.abs(v[:, 1] - 130) < 6) & (v[:, 2] >= 131)]
    if len(v) < 500:
        return None
    return np.median(v, axis=0)


def dE(img, ref):
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    return np.sqrt(((lab - np.float32(ref)) ** 2 * np.float32(P["peso"])).sum(2)), lab


def borda_velha(m, d, lab, ref, escala):
    r = max(1, int(round(P["borda_px"] * escala)))
    perto = cv2.dilate(m.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))) > 0
    return perto & (d < P["borda_dE"]) & (lab[..., 2] < ref[2] + 3) & (lab[..., 0] > ref[0] - 45)


def mascara_final(img, reg, ref):
    regd = cv2.dilate(reg, np.ones((P["dil"], P["dil"]), np.uint8)) > 0
    d, lab = dE(img, ref)
    c = ((d < P["lim"]) & regd).astype(np.uint8)
    c = cv2.morphologyEx(c, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lb, st, _ = cv2.connectedComponentsWithStats(c, 8)
    keep = np.zeros(n, bool)
    keep[1:] = st[1:, cv2.CC_STAT_AREA] > P["area_min"]
    m = keep[lb]
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8)).astype(bool)
    m &= (d < P["lim_borda"]) & regd
    m |= borda_velha(m, d, lab, ref, 1.0) & regd
    return m


def bancadas_pdf(Q, img, ref, m_piso):
    """Os retângulos de bancada do PDF que hoje estão no travertino (px da final) e num ambiente de piso de
    travertino (o anel em volta, fora das paredes, é piso de travertino: as ilhas e bancadas de Dekton da cozinha e as
    de granito ficam de fora)."""
    d, lab = dE(img, ref)
    out = []
    for dr in Q.desenhos:
        if dr["layer"] != "ARQ_BANCADAS" or dr["type"] != "f":
            continue
        r = dr["rect"]
        a, b = Q.p2q(r.x0, r.y0), Q.p2q(r.x1, r.y1)
        x0, x1 = sorted((a[0], b[0]))
        y0, y1 = sorted((a[1], b[1]))
        if (x1 - x0) * (y1 - y0) < P["bancada_area"] or min(x1 - x0, y1 - y0) < 6:
            continue
        X0, Y0, X1, Y1 = int(np.ceil(x0)), int(np.ceil(y0)), int(x1), int(y1)
        sub = d[Y0:Y1, X0:X1]
        if sub.size == 0:
            continue
        if (sub < P["bancada_dE"]).mean() < P["bancada_frac"]:
            continue
        e = 6
        a0, b0 = max(X0 - e, 0), max(Y0 - e, 0)
        anel = np.ones((Y1 - b0 + e, X1 - a0 + e), bool)
        anel[Y0 - b0:Y1 - b0, X0 - a0:X1 - a0] = False
        mp = m_piso[b0:Y1 + e, a0:X1 + e]
        anel = anel[:mp.shape[0], :mp.shape[1]]
        if anel.any() and mp[anel].mean() >= P["bancada_anel"]:
            out.append((x0, y0, x1, y1))
    # sem repetidas (o PDF desenha a mesma bancada mais de uma vez)
    uni = []
    for r in out:
        if not any(abs(r[0] - u[0]) < 1 and abs(r[1] - u[1]) < 1 and abs(r[2] - u[2]) < 1 and abs(r[3] - u[3]) < 1
                   for u in uni):
            uni.append(r)
    return uni


def bancada(img, r, escala, origem, ref, T2r):
    x0, y0, x1, y1 = r
    A0, B0 = int(round((x0 - origem[0]) * escala)), int(round((y0 - origem[1]) * escala))
    A1, B1 = int(round((x1 - origem[0]) * escala)), int(round((y1 - origem[1]) * escala))
    reg = img[B0:B1, A0:A1].astype(np.float32)
    if reg.size == 0:
        return img
    d, lab = dE(np.clip(reg, 0, 255).astype(np.uint8), ref)
    pedra = (d < P["bancada_dE"] + 8) & ((reg[..., 2] - reg[..., 0]) > 6)
    if pedra.sum() < 10:
        return img
    L = cv2.GaussianBlur(reg.mean(2), (0, 0), max(0.6, 0.5 * escala))
    sh = L / max(float(np.median(L[pedra])), 1.0)
    vert = (y1 - y0) > (x1 - x0)
    T = T2r if vert else np.ascontiguousarray(np.transpose(T2r, (1, 0, 2)))
    p = T.shape[0]
    TT = T[np.mod(np.arange(B0, B1), p)[:, None], np.mod(np.arange(A0, A1), p)[None, :]]
    a = cv2.GaussianBlur(pedra.astype(np.float32), (0, 0), max(0.4, 0.3 * escala)) * pedra
    novo = TT * (P["bancada_escuro"] * sh)[..., None]
    img[B0:B1, A0:A1] = np.clip(reg * (1 - a[..., None]) + novo * a[..., None], 0, 255).astype(np.uint8)
    return img


def tex(lado, giro=False):
    if giro:
        T = cv2.imread(str(TV.TEX / TV.PISO["textura"])).astype(np.float32)
        T = cv2.rotate(T, cv2.ROTATE_90_CLOCKWISE)
        T = cv2.resize(T, (lado, lado), interpolation=cv2.INTER_AREA)
        T2 = np.concatenate([T, T[:, ::-1]], 1)
        return np.concatenate([T2, T2[::-1]], 0)
    return TV.tex_tile(TV.PISO["textura"], lado)


def aplicar(planta, so_final=False):
    c, pav = planta.split("_")
    Q = EP.quadro(planta)
    reg = regiao(Q)
    base = cv2.imread(str(EP.PROJ / EP.PLANTAS[planta][0]))
    ref = referencia(base, reg)
    if ref is None:
        print(f"{planta}: sem piso de travertino na legenda; nada a fazer")
        return
    m_final = mascara_final(base, reg, ref)
    bancs = bancadas_pdf(Q, base, ref, m_final)
    lado = int(round(TV.PISO["m"] * Q.px_m))
    T2f, T2fr = tex(lado), tex(lado, True)
    print(f"{planta}: travertino de hoje Lab {np.round(ref, 1).tolist()}, piso {int(m_final.sum())} px, "
          f"{len(bancs)} bancadas")
    novo = None
    for f in EP.PLANTAS[planta]:
        im = cv2.imread(str(EP.PROJ / f))
        m = mascara_final(im, reg, ref) if f != EP.PLANTAS[planta][0] else m_final
        im, _ = TV.piso(im, m, 1.0, T2=T2f)
        for r in bancs:
            im = bancada(im, r, 1.0, (0.0, 0.0), ref, T2fr)
        cv2.imwrite(str(EP.PROJ / f), im)
        if novo is None:
            novo = im
    pf = EP.PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_entrega.png"
    if pf.exists():
        pr = cv2.imread(str(pf))
        pr[:2160] = novo
        cv2.imwrite(str(pf), pr)
    if so_final:
        return
    dz = json.loads((EP.PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[planta]
    s, x0, y0 = dz["s"], dz["x0"], dz["y0"]
    perto = cv2.dilate(m_final.astype(np.uint8), np.ones((7, 7), np.uint8))
    lado_k = int(round(TV.PISO["m"] * Q.px_m * s))
    T2k, T2kr = tex(lado_k), tex(lado_k, True)
    for op in "AB":
        rel = EP.PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_12K_opcao_{op}.jpg"
        if not rel.exists():
            continue
        pil = Image.open(rel)
        dpi = pil.info.get("dpi", (743, 743))
        im = cv2.cvtColor(np.array(pil.convert("RGB")), cv2.COLOR_RGB2BGR)
        del pil
        H, W = im.shape[:2]
        faixa, sobra = 1400, 120
        tot = 0
        for b0 in range(0, H, faixa):
            r0, r1 = max(0, b0 - sobra), min(H, b0 + faixa + sobra)
            sub = im[r0:r1].copy()
            M = np.float32([[s, 0, -x0 * s], [0, s, -y0 * s - r0]])
            pm = cv2.warpAffine(perto, M, (W, r1 - r0), flags=cv2.INTER_NEAREST).astype(bool)
            if not pm.any():
                continue
            d, lab = dE(sub, ref)
            m = pm & (d < P["lim"])
            m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)).astype(bool)
            m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)).astype(bool)
            m &= pm & (d < P["lim_borda"])
            m |= borda_velha(m, d, lab, ref, s) & pm
            novo_r, _ = TV.piso(sub, m, s, X0=0, Y0=r0, T2=T2k)
            a, bb = b0 - r0, min(b0 + faixa, H) - r0
            im[b0:min(b0 + faixa, H)] = novo_r[a:bb]
            tot += int(m[a:bb].sum())
            del sub, novo_r, m, d, lab, pm
        if bancs:
            cinza = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
            for r in bancs:
                bx0, by0, bx1, by1 = r
                try:
                    mapa, cc = EP.registro_12k(base, cinza, dz, (int(bx0) - 60, int(by0) - 60, int(bx1) + 60,
                                                                  int(by1) + 60))
                except Exception as e:                   # noqa: BLE001
                    print("   registro falhou", r, e)
                    continue
                A, B = mapa(bx0, by0)
                sx = (mapa(bx0 + 1000.0, by0)[0] - A) / 1000.0
                im = bancada(im, r, sx, (bx0 - A / sx, by0 - B / sx), ref, T2kr)
            del cinza
        Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).save(rel, quality=95, subsampling=0, dpi=dpi)
        print(f"   {rel.name}: piso {tot} px")
        del im


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plantas", nargs="*")
    ap.add_argument("--so-final", action="store_true")
    a = ap.parse_args()
    plantas = a.plantas or [k for k in EP.PLANTAS if k != "A_Terreo"]
    for k in plantas:
        aplicar(k, a.so_final)


if __name__ == "__main__":
    main()

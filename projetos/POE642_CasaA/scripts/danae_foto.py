"""O Dekton Danae da foto oficial (Cosentino) em todas as casas (16/11).

Usuário: "Esse Delton Danae que estamos adotando está vindo em alta resolução, 4k?"; vendo a chapa oficial e a
simulação na Casa E: "APLIQUE EM TODAS AS CASAS". Até aqui o Danae era desenhado por código
(`terreo_casaa_1011.danae`: o tom BGR 172, 189, 200 com um grão fino e manchas suaves; a foto não tinha baixado em
10/11). Agora é a chapa oficial (Cosentino, código KAC, 5550 x 2690 px de uma chapa de 327 x 147 cm, matte), guardada
reduzida a 800 px por metro em `_texturas/originais/dekton_danae_cosentino_KAC.jpg` (sobra para o 12K, ~200 px/m).

`trocar(img, px_m)`: acha o Danae desenhado pela assinatura dele (`sementes`: as manchas no tom do procedural, com o grão
dele) e cresce cada mancha pelo mesmo croma (`regiao`: a beira mais escura e o anel molhado em volta das cubas entram;
as cubas, os cooktops, as torneiras e o texto não). No lugar, a foto na escala da planta (`px_m`), com os veios no
comprido de cada bancada, cada uma num trecho da chapa; a luz do desenho de antes fica só onde ele escurecia (a beira, o
molhado, a sombra das peças), o grão e as manchas do procedural saem.

Nas finais de 3840 px (`PLANTAS`) e direto nos JPG de 12K já entregues (`DOZE_K`, as opções A e B): o 12K é a final
recortada e ampliada (o afim achado por SIFT entre a final e o 12K reduzido); o Danae de cada região da final é levado
ao 12K e refeito lá, com a foto na escala do 12K (sem nova ida ao Topaz: a pedra fica mais nítida que a ampliação).

  python3 danae_foto.py final <planta> [--saida <png>]     # planta: A_Terreo, A_1Pavimento, B_Terreo, C_Terreo,
                                                            # D_Terreo, D_Terreo_B, E_Terreo
  python3 danae_foto.py doze <planta> [--opcao A|B|AB]      # o 12K entregue (rodar com a final de ANTES da troca:
                                                            # --final_antes <png>, para achar o Danae desenhado)
  python3 danae_foto.py antes_depois                        # a folha das plantas (contra o commit ANTES)
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
RAIZ = AQUI.parent.parent
R = RAIZ

TOM = np.float32((172, 189, 200))                    # o Danae desenhado (`terreo_casaa_1011.DANAE["tom"]`)
PX_M = 59.70590031258779                             # a escala das finais de 3840 px
DANAE_FOTO = {"textura": RAIZ / "_texturas/originais/dekton_danae_cosentino_KAC.jpg", "chapa_m": 3.27,
              # as sementes: o tom do procedural (desvio < `d`) em manchas de `area_min` px ou mais, com o grão dele
              "d": 9.0, "area_min": 150, "cheio_min": 0.45, "media_tol": 4.0, "grao": (3.8, 6.5),
              # o grão do procedural é multiplicativo: no R maior que no B, como o tom (a pedra portuguesa, os
              # degraus e os tapetes não)
              "grao_rb": (1.05, 1.40),
              # a região: o mesmo croma (`croma`, a diferença da cor normalizada) e a luz entre `r` do tom, até `folga`
              # px da semente (a beira e o molhado)
              "croma": 0.013, "r": (0.74, 1.12), "folga_px": 6, "d_caixa": 28.0, "estende_px": 80,
              # a luz de antes fica abaixo de `sombra` (a beira, o molhado, as sombras); acima, a luz da foto
              "sombra": 0.965, "semente": 1611}

PLANTAS = {"A_Terreo": R / "POE642_CasaA/renders/POE642_CasaA_PH_Terreo_final_rotulos.png",
           "A_1Pavimento": R / "POE642_CasaA/renders/POE642_CasaA_PH_1Pavimento_v7_final_rotulos.png",
           "B_Terreo": R / "POE642_CasaB/renders/POE642_CasaB_PH_Terreo_final_rotulos.png",
           "C_Terreo": R / "POE642_CasaC/renders/POE642_CasaC_PH_Terreo_final_rotulos.png",
           "D_Terreo": R / "POE642_CasaD/renders/POE642_CasaD_PH_Terreo_final_rotulos.png",
           "D_Terreo_B": R / "POE642_CasaD/renders/POE642_CasaD_PH_Terreo_final_rotulos_B.png",
           "E_Terreo": R / "POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_final.png"}
# o que tem o tom e o grão do Danae desenhado mas não é bancada (px da final): o degrau junto ao S da escada da Casa E
EXCLUIR = {"E_Terreo": [(2190, 950, 2230, 1060)]}
# as bancadas que a semente não cobre de ponta a ponta (px da final): a do tanque da área de serviço da Casa E
INCLUIR = {"E_Terreo": [(1954, 564, 2070, 607)]}
DOZE_K = {"A_Terreo": R / "POE642_CasaA/entrega/POE642_CasaA_PH_Terreo_12K_opcao_{}.jpg",
          "A_1Pavimento": R / "POE642_CasaA/entrega/POE642_CasaA_PH_1Pavimento_12K_opcao_{}.jpg",
          "B_Terreo": R / "POE642_CasaB/entrega/POE642_CasaB_PH_Terreo_12K_opcao_{}.jpg",
          "C_Terreo": R / "POE642_CasaC/entrega/POE642_CasaC_PH_Terreo_12K_opcao_{}.jpg",
          "D_Terreo": R / "POE642_CasaD/entrega/POE642_CasaD_PH_Terreo_12K_opcao_{}.jpg"}


# ---------------------------------------------------------------------------------------------------------------------
_T = {}


def chapa():
    if "T" not in _T:
        _T["T"] = cv2.imread(str(DANAE_FOTO["textura"])).astype(np.float32)
    return _T["T"]


def textura(h, w, px_m, deitada=True, semente=0):
    """O trecho h x w da chapa na escala `px_m`, os veios no comprido (deitada: os veios na horizontal)."""
    T = chapa()
    k = px_m / (T.shape[1] / DANAE_FOTO["chapa_m"])
    hh, ww = (h, w) if deitada else (w, h)
    T = cv2.resize(T, None, fx=k, fy=k, interpolation=cv2.INTER_AREA if k < 1 else cv2.INTER_CUBIC)
    if T.shape[0] < hh + 2 or T.shape[1] < ww + 2:      # a bancada maior que a chapa: as chapas em espelho
        T = np.concatenate([T, T[:, ::-1]], axis=1)
        T = np.tile(T, ((hh + 2) // T.shape[0] + 1, (ww + 2) // T.shape[1] + 1, 1))
    rng = np.random.default_rng(semente)
    y0 = int(rng.integers(0, T.shape[0] - hh + 1))
    x0 = int(rng.integers(0, T.shape[1] - ww + 1))
    S = T[y0:y0 + hh, x0:x0 + ww]
    return S if deitada else np.ascontiguousarray(np.rot90(S))


def _croma(img):
    s = img.sum(axis=2, keepdims=True)
    return img / np.maximum(s, 1)


def sementes(img, q=DANAE_FOTO, planta=None):
    """As manchas do Danae desenhado: o tom dele (desvio < d) em manchas cheias, com a média e o grão dele. Três
    peneiras: a estrita (o grão do procedural, maior no R que no B); a isolada (bancadas pequenas, onde a beira e a cuba
    engrossam o grão: a média bem no tom); a vizinha (a até 15 px de uma estrita: o resto da mesma bancada)."""
    im = img.astype(np.float32)
    b = cv2.GaussianBlur(im, (0, 0), 1.5)
    m = (np.linalg.norm(b - TOM, axis=2) < q["d"]).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    hf = im - cv2.GaussianBlur(im, (0, 0), 2)
    estritas = np.zeros(img.shape[:2], bool)
    vizinhas = []
    for i in range(1, n):
        x, y, w, h, a = st[i]
        cheio = a / (w * h)
        if a < q["area_min"] or cheio < q["cheio_min"]:
            continue
        mm = lab[y:y + h, x:x + w] == i
        dm = np.abs(im[y:y + h, x:x + w][mm].mean(axis=0) - TOM).max()
        g = hf[y:y + h, x:x + w][mm].std(axis=0)
        rb = g[2] / max(g[0], 1e-6)
        estrita = (dm <= q["media_tol"] and (q["grao"][0] <= g).all() and (g <= q["grao"][1]).all()
                   and q["grao_rb"][0] <= rb <= q["grao_rb"][1])
        isolada = dm <= 3.0 and (3.8 <= g).all() and (g <= 8.0).all() and 1.0 <= rb <= 1.4 and a >= 200 and cheio >= 0.6
        if estrita or isolada:
            estritas[y:y + h, x:x + w] |= mm
        elif dm <= 4.5 and (3.0 <= g).all() and (g <= 8.0).all() and rb >= 0.9:
            vizinhas.append((x, y, w, h, mm))
    perto = cv2.dilate(estritas.astype(np.uint8), np.ones((31, 31), np.uint8)) > 0
    for x, y, w, h, mm in vizinhas:
        if (perto[y:y + h, x:x + w] & mm).any():
            estritas[y:y + h, x:x + w] |= mm
    for x0, y0, x1, y1 in EXCLUIR.get(planta, []):
        estritas[y0:y1, x0:x1] = False
    return estritas


def regiao(img, sem, q=DANAE_FOTO, esc=1.0, planta=None):
    """O Danae inteiro de cada bancada: a caixa de cada uma (as sementes a até 10 px juntadas; justa no través, estendida
    `estende` px no comprido, para o trecho do outro lado de uma cuba), e nela o mesmo croma e a luz entre r do tom
    (a beira escura e o molhado entram; as cubas, as torneiras, o cooktop, as banquetas e o texto não); os buracos
    fechados por dentro que também são pedra (as manchas do molhado e do grão do desenho) entram."""
    im = cv2.GaussianBlur(img.astype(np.float32), (0, 0), 0.8 * esc)
    dc = np.abs(_croma(im) - TOM / TOM.sum()).max(axis=2)
    r = im.mean(axis=2) / TOM.mean()
    # a luz px a px também (a beira clara de um peitoril ao lado não entra pelo borrado da borda escura da bancada)
    r_px = cv2.GaussianBlur(img.astype(np.float32), (0, 0), 0.35 * esc).mean(axis=2) / TOM.mean()
    # o grão do desenho (o procedural tem ~5 de desvio fino; as peças lisas por cima, como o assento de uma banqueta
    # clara, quase nada): fora da beira das sementes, a pedra só cresce onde há o grão dele
    fino = img.astype(np.float32) - cv2.GaussianBlur(img.astype(np.float32), (0, 0), 2 * esc)
    grao = np.sqrt(cv2.GaussianBlur(fino * fino, (0, 0), 1.5 * esc)).mean(axis=2)
    beira = cv2.dilate(sem.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    granulado = ((grao > 2.6) & (grao < 9.0)) | beira
    cand = (dc < q["croma"]) & (r > q["r"][0]) & (r < q["r"][1]) & (r_px < q["r"][1] - 0.02) & granulado
    tom = (np.linalg.norm(im - TOM, axis=2) < q["d_caixa"] * (1.0 if esc == 1.0 else 1.2)) & granulado
    g = max(1, int(round(10 * esc)))
    t = max(1, int(round(2 * esc)))
    e = int(round(q["estende_px"] * esc))
    juntas = cv2.dilate(sem.astype(np.uint8), np.ones((2 * g + 1, 2 * g + 1), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(juntas, 8)
    caixa = np.zeros(sem.shape, bool)
    for i in range(1, n):
        ms = sem & (lab == i)
        ys, xs = np.nonzero(ms)
        if not len(xs):
            continue
        x0, y0, x1, y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
        ex, ey = (e, t) if (x1 - x0) >= (y1 - y0) else (t, e)
        caixa[max(y0 - t, 0):y1 + t, max(x0 - t, 0):x1 + t] = True          # a bancada, justa
        c2 = np.zeros(sem.shape, bool)
        c2[max(y0 - ey, 0):y1 + ey, max(x0 - ex, 0):x1 + ex] = True         # e o comprido dela, só no tom
        caixa |= c2 & tom
    sem = sem.copy()
    for x0, y0, x1, y1 in INCLUIR.get(planta, []):
        caixa[y0:y1, x0:x1] |= tom[y0:y1, x0:x1]
        sem[y0:y1, x0:x1] |= tom[y0:y1, x0:x1] & cand[y0:y1, x0:x1]
    cand &= caixa
    n, lab = cv2.connectedComponents((cand | sem).astype(np.uint8), connectivity=8)
    vivos = np.unique(lab[sem])
    reg = np.isin(lab, vivos[vivos > 0])
    # os buracos fechados por dentro da bancada que são pedra (o croma do Danae, pouco mais solto)
    solto = (dc < q["croma"] * 1.7) & (r > q["r"][0] - 0.04) & (r_px < q["r"][1] - 0.02)
    # a beira (onde o contraste com o piso engrossa o grão) e os furinhos: a região fechada e 3 px para fora, só no
    # croma do Danae (as peças lisas encostadas, como as banquetas, ficam: o fechamento não passa das concavidades)
    k = 2 * max(1, int(round(3 * esc))) + 1
    fora = 2 * max(1, int(round(3 * esc))) + 1
    fechado = cv2.morphologyEx(reg.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((k, k), np.uint8)) > 0
    borda = cv2.dilate(reg.astype(np.uint8), np.ones((fora, fora), np.uint8)) > 0
    reg = reg | ((fechado | borda) & solto & caixa)
    # o que sobra do desenho junto da região (até 24 px: o trecho entre cubas, o do outro lado da cuba): o tom e o grão
    # do procedural, no croma do Danae
    perto = cv2.dilate(reg.astype(np.uint8), np.ones((49, 49), np.uint8)) > 0
    desenho = (np.linalg.norm(cv2.GaussianBlur(img.astype(np.float32), (0, 0), 1.5 * esc) - TOM, axis=2) < 27) & \
        (grao > 2.6) & (grao < 9.0) & solto
    sobra = desenho & perto & ~reg
    if sobra.any():
        n, lab = cv2.connectedComponents((reg | sobra).astype(np.uint8), connectivity=8)
        vivos = np.unique(lab[reg])
        reg = np.isin(lab, vivos[vivos > 0]) | reg
        fechado = cv2.morphologyEx(reg.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((k, k), np.uint8)) > 0
        reg = reg | (fechado & solto)
    n, lab, st, _ = cv2.connectedComponentsWithStats((~reg).astype(np.uint8), 4)
    H, W = reg.shape
    amax = 600 * esc * esc
    for i in range(1, n):
        x, y, w, h, a = st[i]
        if a > amax or x == 0 or y == 0 or x + w >= W or y + h >= H:
            continue
        mm = lab[y:y + h, x:x + w] == i
        anel = cv2.dilate(mm.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
        if not reg[y:y + h, x:x + w][anel & ~mm].all():
            continue                                    # não é fechado pela pedra
        if solto[y:y + h, x:x + w][mm].mean() >= 0.8:
            reg[y:y + h, x:x + w] |= mm
    return reg


def refazer(img, reg, px_m, semente=0, esc=1.0, q=DANAE_FOTO):
    """A foto no lugar do Danae da região `reg`: bancada por bancada (as regiões a até 10 px juntadas: os dois lados
    de uma cuba ou de um cooktop são a mesma chapa, sem emenda), os veios no comprido de cada uma, a luz de antes só
    onde ela escurecia; a borda macia só por dentro (nada vaza para fora)."""
    out = img.copy()
    g = max(1, int(round(10 * esc)))
    juntas = cv2.dilate(reg.astype(np.uint8), np.ones((2 * g + 1, 2 * g + 1), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(juntas, 8)
    for i in range(1, n):
        x, y, w, h, _ = st[i]
        m = reg[y:y + h, x:x + w] & (lab[y:y + h, x:x + w] == i)
        if m.sum() < 20:
            continue
        ys, xs = np.nonzero(m)
        x0, y0, x1, y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
        m = m[y0:y1, x0:x1]
        X, Y = x + x0, y + y0
        hh, ww = y1 - y0, x1 - x0
        sub = img[Y:Y + hh, X:X + ww].astype(np.float32)
        r = cv2.GaussianBlur(sub, (0, 0), 1.0 * esc).mean(axis=2)
        r = r / max(float(np.median(r[m])), 1.0)          # a luz relativa ao tom da própria bancada
        luz = np.where(r >= q["sombra"], 1.0, r / q["sombra"]).astype(np.float32)
        luz = cv2.GaussianBlur(luz, (0, 0), 0.6 * esc)
        T = textura(hh, ww, px_m, deitada=ww >= hh, semente=semente * 1000 + i)
        novo = T * luz[..., None]
        a_ = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.5 * esc)
        a_ = (np.where(m, np.maximum(a_, 0.5), 0.0))[..., None]
        out[Y:Y + hh, X:X + ww] = np.clip(sub * (1 - a_) + novo * a_, 0, 255).astype(np.uint8)
    return out


def trocar(img, px_m=PX_M, semente=DANAE_FOTO["semente"], planta=None):
    sem = sementes(img, planta=planta)
    reg = regiao(img, sem, planta=planta)
    return refazer(img, reg, px_m, semente), reg


# ---------------------------------------------------------------------------------------------------------------------
# o 12K
def afim_12k(final, doze, esc_aprox=3.6):
    """O afim (2 x 3, só escala e deslocamento) que leva a final ao 12K: SIFT entre a final e o 12K reduzido."""
    g1 = cv2.cvtColor(final, cv2.COLOR_BGR2GRAY)
    red = cv2.resize(doze, None, fx=1 / esc_aprox, fy=1 / esc_aprox, interpolation=cv2.INTER_AREA)
    g2 = cv2.cvtColor(red, cv2.COLOR_BGR2GRAY)
    sift = cv2.SIFT_create(nfeatures=12000)
    k1, d1 = sift.detectAndCompute(g1, None)
    k2, d2 = sift.detectAndCompute(g2, None)
    bf = cv2.BFMatcher()
    pares = [m for m, n in bf.knnMatch(d1, d2, k=2) if m.distance < 0.7 * n.distance]
    a = np.float32([k1[m.queryIdx].pt for m in pares])
    b = np.float32([k2[m.trainIdx].pt for m in pares]) * esc_aprox
    M, inl = cv2.estimateAffinePartial2D(a, b, method=cv2.RANSAC, ransacReprojThreshold=6.0, maxIters=5000)
    print(f"      o afim da final ao 12K: escala {np.hypot(M[0, 0], M[1, 0]):.4f}, deslocamento ({M[0, 2]:.1f}, "
          f"{M[1, 2]:.1f}); {int(inl.sum())} de {len(pares)} pares")
    return M


def trocar_12k(doze, final_antes, M, semente=DANAE_FOTO["semente"], q=DANAE_FOTO, planta=None):
    """O Danae no 12K: as regiões da final (antes da troca) levadas ao 12K pelo afim, refeitas lá na escala do 12K."""
    s = float(np.hypot(M[0, 0], M[1, 0]))
    reg_f = regiao(final_antes, sementes(final_antes, planta=planta), planta=planta)
    out = doze.copy()
    juntas = cv2.dilate(reg_f.astype(np.uint8), np.ones((21, 21), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(juntas, 8)
    H, W = doze.shape[:2]
    for i in range(1, n):
        x, y, w, h, a = st[i]
        mf = (reg_f & (lab == i))
        if mf.sum() < 20:
            continue
        p0 = M @ np.float32([x, y, 1])
        p1 = M @ np.float32([x + w, y + h, 1])
        xa, ya = max(int(np.floor(p0[0])), 0), max(int(np.floor(p0[1])), 0)
        xb, yb = min(int(np.ceil(p1[0])), W), min(int(np.ceil(p1[1])), H)
        if xb <= xa or yb <= ya:
            continue
        Mi = M.copy()
        Mi[:, 2] -= (xa, ya)
        m12 = cv2.warpAffine(mf.astype(np.float32), Mi, (xb - xa, yb - ya), flags=cv2.INTER_LINEAR) > 0.5
        sub = out[ya:yb, xa:xb]
        # o croma do 12K confirma (as peças por cima, o texto e a beira do Topaz ficam)
        im = cv2.GaussianBlur(sub.astype(np.float32), (0, 0), 0.8 * s)
        dc = np.abs(_croma(im) - TOM / TOM.sum()).max(axis=2)
        rr = im.mean(axis=2) / TOM.mean()
        m12 &= (dc < q["croma"] * 1.3) & (rr > q["r"][0]) & (rr < q["r"][1] + 0.03)
        out[ya:yb, xa:xb] = refazer(sub, m12, PX_M * s, semente * 7 + i, esc=s)
    return out


# ---------------------------------------------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("acao", choices=("final", "doze"))
    ap.add_argument("planta")
    ap.add_argument("--saida")
    ap.add_argument("--opcao", default="AB")
    ap.add_argument("--final_antes", help="a final de antes da troca (para achar o Danae desenhado no 12K)")
    a = ap.parse_args()
    if a.acao == "final":
        img = cv2.imread(str(PLANTAS[a.planta]))
        out, reg = trocar(img, planta=a.planta)
        cv2.imwrite(a.saida or str(PLANTAS[a.planta]), out)
        n = cv2.connectedComponents(reg.astype(np.uint8))[0] - 1
        print(f"  {a.planta}: o Danae da foto em {n} regiões ({int(reg.sum())} px)")
    else:
        fa = cv2.imread(a.final_antes)
        for op in a.opcao:
            f = Path(str(DOZE_K[a.planta]).format(op))
            doze = cv2.imread(str(f))
            print(f"  {f.name}: {doze.shape[1]}x{doze.shape[0]}")
            M = afim_12k(fa, doze)
            out = trocar_12k(doze, fa, M, planta=a.planta)
            cv2.imwrite(a.saida.format(op) if a.saida else str(f), out, [cv2.IMWRITE_JPEG_QUALITY, 95])


if __name__ == "__main__":
    main()

"""O vinílico da foto do usuário em todas as plantas com vinílico (11/11).

Usuário, com a foto de um vinílico de carvalho claro: "vamos trazer esse piso vinílico em sua respectiva escala para os
ambientes que possuem piso vinílico. vamos testar e se der certo adotaremos para todas as outras plantas"; vendo o
teste no 1º Pavimento da Casa A: "sim, aplique em todas as plantas com vinílico, mas com uma escala mais reduzida".

O 1º Pavimento da Casa A refaz o passo `pisos_1111e` (`um_pav_casaa_1111.py`, com `regua_m` daqui). As outras plantas
recebem o piso sobre a final instalada (`trocar`): o vinílico é o da base chapada (a cor do vinílico em cada casa; na
academia do Subsolo da Casa A, o retângulo da madeira de `final3840_casaa.PISOS_A`), só no que é piso (fora as peças
do PDF, as paredes e o que foge do tom do piso do lugar), com a luz e a sombra dos móveis da final como fator; os
vãos das portas com o vinílico do render entram. As réguas são as da foto (`um_pav_casaa_1111._reguas_amostra`), na
largura `regua_m`, na direção das tábuas da final (`auto`). Os rótulos e os riscos escuros sobre o piso (o texto
cinza-escuro) ficam: a cobertura de cada px é medida contra a luz do piso antigo e o texto volta, na mesma cor, sobre o
piso novo.

  python3 vinilico_foto.py <planta> [--saida <png>]      # planta: B_Terreo, B_Subsolo, C_Terreo, C_Subsolo, D_Terreo,
                                                         # D_Subsolo, E_1Pavimento, E_Subsolo, A_Subsolo
Sem --saida, grava por cima da final da planta (a de `PLANTAS`).
"""

import argparse
import contextlib
import copy
import io
import sys
from pathlib import Path

import cv2
import numpy as np
from scipy import ndimage

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
RAIZ = AQUI.parent.parent

VINILICO_FOTO = {
    # a régua da foto com 12 cm (o 1º teste, de 11/11, tinha 20 cm; "escala mais reduzida"): a das Casas B a D antes
    "regua_m": 0.12,
    "direcao": "auto",
    "camadas_pdf": ("ARQ_LAYOUT HUMANIZAÇÃO", "ARQ_LOUÇAS E METAIS", "ARQ_BANCADAS", "ARQ_ELEMENTOS FIXOS",
                    "ARQ_ESCADAS E RAMPAS"),
    "pdf_folga_px": 1, "desvio": 30, "croma": 0.030, "sombra_min": 0.70, "perto_m": 0.40, "luz_m": 0.9,
    "plano": 0.6, "fechar_px": 3, "fiapo_px": 60,
    "vao": {"px": 30, "croma": 0.035, "r": (0.75, 1.25)},
    # o texto e os riscos escuros: mais escuro que `escuro` x o piso, pouco colorido, em peças de até `lado_max` px
    "texto": {"escuro": 0.62, "croma": 0.05, "lado_max": 40, "folga_px": 2, "alfa_min": 0.12},
    # uma peça do PDF é piso se `fracao` dela tem o tom do piso do lugar (a peça que a final não desenha)
    "peca_piso": {"desvio": 16, "croma": 0.02, "fracao": 0.85, "area_min": 60},
    "semente": 1112,
}

R = RAIZ
PLANTAS = {
    "B_Terreo": ("B", "Terreo", R / "POE642_CasaB/renders/POE642_CasaB_PH_Terreo_final_rotulos.png", [(124, 162, 200)]),
    "B_Subsolo": ("B", "Subsolo", R / "POE642_CasaB/renders/POE642_CasaB_PH_Subsolo_final_rotulos.png",
                  [(124, 162, 200)]),
    "C_Terreo": ("C", "Terreo", R / "POE642_CasaC/renders/POE642_CasaC_PH_Terreo_final_rotulos.png", [(124, 162, 200)]),
    "C_Subsolo": ("C", "Subsolo", R / "POE642_CasaC/renders/POE642_CasaC_PH_Subsolo_final_rotulos.png",
                  [(124, 162, 200)]),
    "D_Terreo": ("D", "Terreo", R / "POE642_CasaD/renders/POE642_CasaD_PH_Terreo_final_rotulos.png", [(124, 162, 200)]),
    "D_Subsolo": ("D", "Subsolo", R / "POE642_CasaD/renders/POE642_CasaD_PH_Subsolo_final_rotulos.png",
                  [(124, 162, 200)]),
    "E_1Pavimento": ("E", "1Pavimento", R / "POE642_CasaE/renders/POE642_CasaE_PH_1Pavimento_v1_final.png",
                     [(79, 120, 168)]),
    "E_Subsolo": ("E", "Subsolo", R / "POE642_CasaE/renders/POE642_CasaE_PH_Subsolo_v1_final.png", [(79, 120, 168)]),
    "A_Subsolo": ("A", "Subsolo", R / "POE642_CasaA/renders/POE642_CasaA_PH_Subsolo_final_rotulos.png", "madeira"),
}


def quadro(casa, chave):
    with contextlib.redirect_stdout(io.StringIO()):
        import final3840_casab as F
        if casa == "B":
            return F.Quadro(chave)
        if casa == "C":
            import final3840_casac as C
            C.contexto_c()
            return F.Quadro(chave)
        if casa == "D":
            import final3840_casad as D
            D.contexto_d()
            return F.Quadro(chave)
        if casa == "E":
            import final3840_casae as E
            return E.QuadroE(chave)
        import final3840_casaa as A
        return A.QuadroA(chave)


def mascara_vinilico(Q, cores):
    if cores == "madeira":
        import final3840_casaa as A
        m = np.zeros((Q.H, Q.W), np.uint8)
        for x0, y0, x1, y1 in A.PISOS_A["madeira"]["rets"]:
            pts = np.float32([Q.p2q(x0, y0), Q.p2q(x1, y0), Q.p2q(x1, y1), Q.p2q(x0, y1)])
            cv2.fillPoly(m, [np.int32(np.round(pts))], 1)
        return m > 0
    return Q.cor(cores, tol=6)


def trocar(Q, img, cores, q=None):
    """O vinílico da foto na final `img` (BGR uint8), no vinílico da base (`cores`); devolve a imagem nova e a máscara
    do que mudou."""
    import final3840_casaa as FA
    import final3840_casab as F
    import um_pav_casaa_1111 as U
    q = q or VINILICO_FOTO
    qv = dict(copy.deepcopy(U.PISOS_1111E["vinilico"]), regua_foto_m=q["regua_m"])
    H, W = img.shape[:2]
    k = Q.px_m
    I = img.astype(np.float32)
    par = U.dilatar(FA.paredes_pdf(Q) > 0.3, 1)
    pdf = U._objetos_pdf(Q, q["camadas_pdf"], q["pdf_folga_px"])
    mat = mascara_vinilico(Q, cores)
    f = 2 * q["fechar_px"] + 1
    mat = cv2.morphologyEx(mat.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((f, f), np.uint8)) > 0
    mat &= ~par
    nI = I / np.maximum(I.sum(axis=2, keepdims=True), 1)
    # os vãos das portas com o vinílico do render (na chapada, preto)
    qa = q["vao"]
    ref = np.median(I[mat & ~pdf], axis=0)
    rv = I.mean(axis=2) / max(float(ref.mean()), 1.0)
    cand = U.dilatar(mat, qa["px"]) & ~mat & ~par & (Q.chapada <= 20).all(axis=2)
    cand &= (np.abs(nI - ref / ref.sum()).max(axis=2) < qa["croma"]) & (rv > qa["r"][0]) & (rv < qa["r"][1])
    mat |= cand & ndimage.binary_propagation(mat, mask=mat | cand)
    # o texto e os riscos escuros sobre o piso
    qt = q["texto"]
    L0 = F.luz_robusta(img, mat & ~pdf, 0.5 * k, desvio=q["desvio"])
    # as peças do PDF que a final não desenha (só o piso por cima, como o quadrado da circulação do Térreo da Casa D)
    # entram como piso
    qp = q["peca_piso"]
    nL0 = L0 / np.maximum(L0.sum(axis=2, keepdims=True), 1)
    igual = (np.abs(I - L0).max(axis=2) < qp["desvio"]) & (np.abs(nI - nL0).max(axis=2) < qp["croma"])
    npc, labp = cv2.connectedComponents((pdf & mat).astype(np.uint8), connectivity=8)
    if npc > 1:
        tot = np.bincount(labp.ravel(), minlength=npc)
        ig = np.bincount(labp.ravel(), weights=igual.ravel().astype(np.float64), minlength=npc)
        piso_pdf = np.zeros(npc, bool)
        piso_pdf[1:] = (ig[1:] / np.maximum(tot[1:], 1) > qp["fracao"]) & (tot[1:] >= qp["area_min"])
        pdf = pdf & ~piso_pdf[labp]
        L0 = F.luz_robusta(img, mat & ~pdf, 0.5 * k, desvio=q["desvio"])
    lum, lum0 = I.mean(axis=2), np.maximum(L0.mean(axis=2), 1)
    cinza = (I.max(axis=2) - I.min(axis=2)) / np.maximum(I.max(axis=2), 1) < qt["croma"] * 4
    nucleo = mat & ~pdf & (lum < qt["escuro"] * lum0) & cinza
    nc, lab, st, _ = cv2.connectedComponentsWithStats(nucleo.astype(np.uint8), 8)
    ok = np.zeros(nc, bool)
    ok[1:] = np.maximum(st[1:, cv2.CC_STAT_WIDTH], st[1:, cv2.CC_STAT_HEIGHT]) <= qt["lado_max"]
    nucleo = ok[lab]
    texto = U.dilatar(nucleo, qt["folga_px"]) & mat & ~pdf
    # o piso: o que tem o tom do piso do lugar (ou a sombra dele)
    L = F.luz_robusta(img, mat & ~pdf & ~texto, 0.5 * k, desvio=q["desvio"])
    nL = L / np.maximum(L.sum(axis=2, keepdims=True), 1)
    err = np.abs(nI - nL).max(axis=2)
    r = cv2.GaussianBlur(lum, (0, 0), 0.8) / np.maximum(L.mean(axis=2), 1)
    dev = np.abs(I - L).max(axis=2)
    piso = mat & ~pdf & ~texto & (err < q["croma"]) & ((dev < q["desvio"]) | ((r > q["sombra_min"]) & (r < 1.0)))
    # os fiapos do piso antigo que o filtro deixa (um veio claro de 1 px) entram: buracos pequenos, fora do texto
    buraco = mat & ~pdf & ~piso & ~texto
    nb, labb, stb, _ = cv2.connectedComponentsWithStats(buraco.astype(np.uint8), 8)
    peq = np.zeros(nb, bool)
    peq[1:] = stb[1:, cv2.CC_STAT_AREA] <= q["fiapo_px"]
    piso |= peq[labb]
    piso |= texto
    perto = cv2.GaussianBlur(U.dilatar(mat & ~piso, int(round(q["perto_m"] * k))).astype(np.float32), (0, 0), 3.0)
    S = np.where(r < 0.985, np.clip(r / 0.985, q["sombra_min"] * 0.8, 1.0), 1.0)
    S = 1 - (1 - S) * perto
    S[texto] = 1.0
    Lg = F.luz_robusta(img, piso & ~texto, q["luz_m"] * k, desvio=q["desvio"])
    # a cobertura do texto contra o piso antigo, e a cor dele
    a_txt = np.zeros((H, W), np.float32)
    cor_txt = np.zeros((H, W, 3), np.float32)
    nt, labt = cv2.connectedComponents(texto.astype(np.uint8), connectivity=8)
    for i in range(1, nt):
        m_i = labt == i
        nu = m_i & nucleo
        if not nu.any():
            continue
        v = lum[nu]
        tl = float(np.percentile(v, 10))
        esc = nu & (lum <= np.percentile(v, 30))
        cor = I[esc].mean(axis=0) if esc.any() else I[nu].mean(axis=0)
        a = np.clip((lum0[m_i] - lum[m_i]) / np.maximum(lum0[m_i] - tl, 1.0), 0, 1)
        a = np.where(a < qt["alfa_min"], 0.0, a)
        a_txt[m_i] = a
        cor_txt[m_i] = cor
    out = I.copy()
    rng = np.random.default_rng(q["semente"])
    nc, lab, st, _ = cv2.connectedComponentsWithStats(mat.astype(np.uint8), 8)
    feitos = 0
    for i in range(1, nc):
        x, y, w, h, area = st[i]
        if area < 400:
            continue
        m = (lab[y:y + h, x:x + w] == i) & piso[y:y + h, x:x + w]
        if m.sum() < 200:
            continue
        med = np.median(Lg[y:y + h, x:x + w][m & ~texto[y:y + h, x:x + w]], axis=0)
        Lr = Lg[y:y + h, x:x + w] * (1 - q["plano"]) + med[None, None] * q["plano"]
        deitado = q["direcao"] == "h"
        if q["direcao"] == "auto":
            g = cv2.cvtColor(img[y:y + h, x:x + w], cv2.COLOR_BGR2GRAY).astype(np.float32)
            gx = cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3)
            gy = cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3)
            mm = m & ~texto[y:y + h, x:x + w]
            deitado = float((gy[mm] ** 2).sum()) >= float((gx[mm] ** 2).sum())
        if deitado:
            T = U._reguas_amostra(h, w, k, qv, rng)
        else:
            T = np.ascontiguousarray(U._reguas_amostra(w, h, k, qv, rng).transpose(1, 0, 2))
        novo = T * (Lr.mean(axis=2, keepdims=True) / max(float(med.mean()), 1.0)) * S[y:y + h, x:x + w, None]
        at = a_txt[y:y + h, x:x + w, None] * m[..., None]
        novo = novo * (1 - at) + cor_txt[y:y + h, x:x + w] * at
        al = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.5) * m
        reg = out[y:y + h, x:x + w]
        reg[:] = reg * (1 - al[..., None]) + novo * al[..., None]
        feitos += 1
    out = np.clip(np.round(out), 0, 255).astype(np.uint8)
    print(f"    vinílico da foto (régua de {q['regua_m'] * 100:.0f} cm): {feitos} ambientes, {int(piso.sum())} px de "
          f"piso, {int(texto.sum())} px de texto e riscos mantidos por cima")
    return out, piso


def antes_depois(planta, antes, depois, max_lado=2400, folga=40):
    """O antes e depois do vinílico (o retângulo do que mudou, com folga), em renders/ da casa:
    POE642_Casa<X>_PH_<pavimento>_vinilico_foto_antes_depois.jpg."""
    casa, chave, final, _ = PLANTAS[planta]
    d = np.abs(antes.astype(np.int16) - depois.astype(np.int16)).max(axis=2) > 6
    ys, xs = np.nonzero(d)
    H, W = d.shape
    x0, x1 = max(int(xs.min()) - folga, 0), min(int(xs.max()) + folga, W)
    y0, y1 = max(int(ys.min()) - folga, 0), min(int(ys.max()) + folga, H)
    a, b = antes[y0:y1, x0:x1], depois[y0:y1, x0:x1]
    lado = (x1 - x0) <= (y1 - y0) * 1.3
    junto = np.hstack([a, np.full((a.shape[0], 12, 3), 255, np.uint8), b]) if lado else \
        np.vstack([a, np.full((12, a.shape[1], 3), 255, np.uint8), b])
    k = min(2.0, max_lado / max(junto.shape[:2]))
    junto = cv2.resize(junto, None, fx=k, fy=k, interpolation=cv2.INTER_LANCZOS4 if k > 1 else cv2.INTER_AREA)
    arq = Path(final).parent / f"POE642_Casa{casa}_PH_{chave}_vinilico_foto_antes_depois.jpg"
    cv2.imwrite(str(arq), junto, [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"    {arq.name}")
    return arq


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("planta", choices=sorted(PLANTAS))
    ap.add_argument("--antes", type=Path, help="a imagem de partida (por padrão, a final da planta)")
    ap.add_argument("--saida", type=Path)
    ap.add_argument("--antes_depois", action="store_true", help="grava o antes e depois em renders/ da casa")
    a = ap.parse_args()
    casa, chave, final, cores = PLANTAS[a.planta]
    Q = quadro(casa, chave)
    img = cv2.imread(str(a.antes or final))
    out, _ = trocar(Q, img, cores)
    cv2.imwrite(str(a.saida or final), out)
    print(f"    {a.saida or final}")
    if a.antes_depois:
        antes_depois(a.planta, img, out)


if __name__ == "__main__":
    main()

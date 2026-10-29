#!/usr/bin/env python3
"""As cortinas franzidas nas finais de todas as casas (usuário, 27/10/26, vendo as do Térreo da Casa C: "adote esses
modelos de cortinas para as todas as casas. corrija as cortinas das casas A, B, E.").

Desde 27/10, `blocos.cortina` fechada é o pano franzido (`blocos.pano_franzido`: o lado do vidro quase reto, o do
ambiente em ondas, as pregas em luz e sombra, a dobra da frente e a sombra curta), e o pano antigo, a linha fina em
zigue-zague, ficou em `blocos.cortina_ondulada`. As finais já aprovadas (o 1º Pavimento da Casa A, o Térreo das Casas B
e D, o Térreo e o 1º Pavimento da Casa E) trocam só o pano, sem rodar de novo os motores: cada pano antigo sai do lugar
exato em que a rotina daquela planta o pôs (os mesmos trechos do PDF, o mesmo eixo, a mesma peça; o lugar do pano antigo é
refeito com o piso logo à frente dele, no ambiente) e o pano franzido entra no mesmo eixo. O trilho fica o que está; o
resto da imagem não muda. A Casa C usa o pano franzido no próprio motor (`final3840_casac.cortinas_t`).

O lado do vidro: o pano franzido não é simétrico (o lado reto e o trilho vão para o vidro), e o motor das Casas B e D
supunha o vidro sempre em cima nas cortinas horizontais. No Térreo da Casa D, 8 delas (as das fachadas de baixo) têm o
vidro embaixo: `ajustes_casab.trechos_cortina_b` agora lê o lado no PDF (`lado_vidro_pdf`, o traço comprido da parede
mais perto), e onde ele difere do que a final tem a peça antiga sai inteira (pano e trilho) e entra a nova, com o trilho
do lado certo.

Uso (da pasta POE642_CasaA/scripts/), um pavimento por vez:
  python3 cortinas_franzidas.py A-1Pavimento | B-Terreo | D-Terreo | E-Terreo | E-1Pavimento [--antes <png>]
A final é regravada no lugar (`--antes` guarda uma cópia da anterior).
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(RAIZ / "_blocos"))

# o pano antigo sai pelo que ele ocupava (alfa acima de `limiar`), um pouco alargado onde a final veio de 2000 px
# (`folga_px`), sem tocar no trilho; o piso que entra é o do ambiente, a `desloca_m` do eixo; os panos que viram de lado
# a menos de `janela_m` um do outro, no mesmo eixo, são da mesma janela e dividem o trilho; o px que não é piso
# (`piso_dif`) vem de outro ponto (`outros`, ver `tirar`)
TROCA = {"k": 8, "limiar": 0.02, "desloca_m": 0.20, "trilho_alfa": 0.05, "janela_m": 1.2, "piso_dif": 60,
         "outros": [(0.12, 0.0), (0.30, 0.0), (0.20, 0.30), (0.20, -0.30), (0.40, 0.0), (0.20, 0.60), (0.20, -0.60)]}
FINAIS = {"A-1Pavimento": RAIZ / "POE642_CasaA/renders/POE642_CasaA_PH_1Pavimento_v7_final_rotulos.png",
          "B-Terreo": RAIZ / "POE642_CasaB/renders/POE642_CasaB_PH_Terreo_final_rotulos.png",
          "D-Terreo": RAIZ / "POE642_CasaD/renders/POE642_CasaD_PH_Terreo_final_rotulos.png",
          "E-Terreo": RAIZ / "POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_final.png",
          "E-1Pavimento": RAIZ / "POE642_CasaE/renders/POE642_CasaE_PH_1Pavimento_v1_final.png"}
FOLGA_PX = {"A-1Pavimento": 1, "B-Terreo": 0, "D-Terreo": 0, "E-Terreo": 1, "E-1Pavimento": 1}


def pegada(forma, cor, a, eixo, inicio, k, vidro):
    from retoque_terreo_casae import pousar_cortina
    m = np.zeros(forma, np.uint8)
    pousar_cortina(m, np.full_like(cor, 255.0), a, eixo, inicio, k, vidro)
    return m[..., 0].astype(np.float32) / 255


def tirar(out, mascara, vidro, px_m):
    """Refaz os px de `mascara` com o piso do ambiente, a `desloca_m` dali para o lado oposto ao vidro. O que não é piso
    (mais de `piso_dif` da mediana do que veio: um arranjo de flores, um móvel junto à cortina) não entra: aquele px vem
    de outro ponto (`outros`: (m para dentro, m ao longo)) e, se nenhum for piso, do inpaint."""
    q = TROCA
    ys, xs = np.nonzero(mascara)
    if not len(ys):
        return
    fonte = out.copy()
    H, W = out.shape[:2]

    def amostra(dentro_m, ao_longo_m=0.0):
        d, l = dentro_m * px_m, ao_longo_m * px_m
        dx, dy = {"esquerda": (d, l), "direita": (-d, l), "cima": (l, d), "baixo": (l, -d)}[vidro]
        yy = np.clip(ys + int(round(dy)), 0, H - 1)
        xx = np.clip(xs + int(round(dx)), 0, W - 1)
        return fonte[yy, xx].astype(np.float32), ~mascara[yy, xx]

    cor, ok = amostra(q["desloca_m"])
    ref = np.median(cor[ok], axis=0) if ok.any() else np.median(cor, axis=0)
    ruim = ~ok | (np.abs(cor - ref).max(axis=1) > q["piso_dif"])
    for dentro_m, ao_longo_m in q["outros"]:
        if not ruim.any():
            break
        c2, ok2 = amostra(dentro_m, ao_longo_m)
        bom = ruim & ok2 & (np.abs(c2 - ref).max(axis=1) <= q["piso_dif"])
        cor[bom] = c2[bom]
        ruim &= ~bom
    out[ys, xs] = np.clip(cor, 0, 255).astype(np.uint8)
    if ruim.any():
        m = np.zeros((H, W), np.uint8)
        m[ys[ruim], xs[ruim]] = 255
        out[...] = cv2.inpaint(np.ascontiguousarray(out), m, 3, cv2.INPAINT_TELEA)


def trocar(out, trechos, px_m, folga_px=0):
    """trechos: (vidro, eixo, início, fim) em px de `out` (vidro esquerda/direita: o eixo é um x; cima/baixo, um y), na
    orientação em que a rotina da planta os pousou. O trilho fica; só o pano troca."""
    import blocos
    from retoque_terreo_casae import pousar_cortina
    q = TROCA
    k = q["k"]
    for vidro, eixo, t0, t1 in trechos:
        comp = (t1 - t0) / px_m
        c0, a0 = blocos.cortina_ondulada(comp, px_m * k, com_trilho=False)
        velho = pegada(out.shape, c0, a0, eixo, t0, k, vidro) > q["limiar"]
        if folga_px:
            ct, at = blocos.cortina_ondulada(comp, px_m * k, com_pano=False)
            trilho = pegada(out.shape, ct, at, eixo, t0, k, vidro) > q["trilho_alfa"]
            velho = cv2.dilate(velho.astype(np.uint8), np.ones((2 * folga_px + 1,) * 2, np.uint8)).astype(bool) & ~trilho
        tirar(out, velho, vidro, px_m)
        cor, a = blocos.pano_franzido(comp, px_m * k)
        pousar_cortina(out, cor, a, eixo, t0, k, vidro)
    return len(trechos)


def virar(out, trechos, px_m, antigo):
    """Os panos de uma janela (o mesmo eixo; trechos como em `trocar`, com o vidro certo) que a final pousou com o vidro
    em `antigo`, o lado oposto: saem os panos e o trilho, que corre de ponta a ponta da janela (do 1º início ao último
    fim), e entram, do lado certo, o trilho e os panos franzidos."""
    import blocos
    from retoque_terreo_casae import pousar_cortina
    q = TROCA
    k = q["k"]
    vidro = trechos[0][0]
    eixo = float(np.mean([t[1] for t in trechos]))
    a0, a1 = min(t[2] for t in trechos), max(t[3] for t in trechos)
    for _, ex, t0, t1 in trechos:
        c0, al0 = blocos.cortina_ondulada((t1 - t0) / px_m, px_m * k, com_trilho=False)
        tirar(out, pegada(out.shape, c0, al0, ex, t0, k, antigo) > q["limiar"], vidro, px_m)
    ct, at = blocos.cortina_ondulada((a1 - a0) / px_m, px_m * k, com_pano=False)
    tirar(out, pegada(out.shape, ct, at, eixo, a0, k, antigo) > q["limiar"], vidro, px_m)
    pousar_cortina(out, ct, at, eixo, a0, k, vidro)
    for _, ex, t0, t1 in trechos:
        cor, a = blocos.pano_franzido((t1 - t0) / px_m, px_m * k)
        pousar_cortina(out, cor, a, ex, t0, k, vidro)
    return len(trechos)


def px_m_de(p2q):
    (a, b), (c, d) = p2q(0, 0), p2q(56.69, 0)
    return float(np.hypot(c - a, d - b))


def casa_b_ou_d(chave_casa, out):
    """As Casas B e D: os trechos de `ajustes_casab.trechos_cortina_b` no quadro da prancha, pousados como em
    `cortinas_b` (os horizontais na imagem transposta). As finais foram feitas com o vidro dos horizontais sempre em cima
    ('esquerda' na imagem transposta); os que o PDF põe embaixo viram."""
    import final3840_casab as F
    if chave_casa == "D":
        import final3840_casad as D
        D.contexto_d()
    Q = F.Quadro("Terreo")
    with F.em_quadro(Q):
        trechos = F.B.trechos_cortina_b("Terreo")
    n = 0
    janelas = []
    for o, vidro, ex, e0, e1 in trechos:
        img = out if o == "v" else out.transpose(1, 0, 2)
        v = vidro if o == "v" else {"cima": "esquerda", "baixo": "direita"}[vidro]
        if o == "h" and vidro == "baixo":
            # os panos da mesma janela (o mesmo eixo, a menos de `janela_m` um do outro) dividem o trilho
            j = janelas[-1] if janelas else None
            if j and abs(j[-1][1] - ex) < 3 and e0 - j[-1][3] < TROCA["janela_m"] * Q.px_m:
                j.append((v, ex, e0, e1))
            else:
                janelas.append([(v, ex, e0, e1)])
        else:
            n += trocar(img, [(v, ex, e0, e1)], Q.px_m)
    for j in janelas:
        n += virar(out.transpose(1, 0, 2), j, Q.px_m, "esquerda")
    return n


def casa_a_1pav(out):
    import final3840_casab as F
    import final3840_casaa as FA
    Q = FA.QuadroA("1Pavimento")
    with F.em_quadro(Q):
        trechos = F.AJ.trechos_cortina_1pav()
    return trocar(out, [(v, ex, e0, e1) for v, ex, e0, e1 in trechos], Q.px_m, FOLGA_PX["A-1Pavimento"])


def casa_e_terreo(out):
    import pymupdf
    import retoque_terreo_casae as T
    from opcoes_1pav_casae import quadro_pdf
    cfg = json.loads(T.CONFIG.read_text())
    pg = pymupdf.open(T.PDF)[cfg["pavimentos"]["Terreo"]["pagina"]]
    at, lt = cv2.imread(str(T.BASE), cv2.IMREAD_GRAYSCALE).shape
    hb, wb = cv2.imread(str(T.BASE_SEM_TELA), cv2.IMREAD_GRAYSCALE).shape
    p2q = quadro_pdf(pg, cfg, lt, at, wb, hb, out.shape[1])
    trechos = []
    for c in T.CORTINAS["conjuntos"]:
        vertical = c["vidro"] in ("direita", "esquerda")
        ep = c["trilho"][0]
        for pp0, pp1 in c["panos"]:
            if vertical:
                (e, t0), (_, t1) = p2q(ep, pp0), p2q(ep, pp1)
            else:
                (t0, e), (t1, _) = p2q(pp0, ep), p2q(pp1, ep)
            trechos.append((c["vidro"], e, t0, t1))
    return trocar(out, trechos, px_m_de(p2q), FOLGA_PX["E-Terreo"])


def casa_e_1pav(out):
    import pymupdf
    import retoque_1pav_casae as R
    import opcoes_1pav_casae as O
    cfg = json.loads(R.CONFIG.read_text())
    pg = pymupdf.open(R.PDF)[cfg["pavimentos"]["1Pavimento"]["pagina"]]
    base = cv2.imread(str(O.BASE_CIMA))
    lt, at = base.shape[1], base.shape[0]
    hb, wb = cv2.imread(str(R.BASE_SEM_TELA), cv2.IMREAD_GRAYSCALE).shape
    p2q = O.quadro_pdf(pg, cfg, lt, at, wb, hb, out.shape[1])
    trechos = []
    for pts in R.trechos_cortina(pg):
        xe = float(np.median(pts[:, 0]))
        (ex, ey0), (_, ey1) = p2q(xe, float(pts[:, 1].min())), p2q(xe, float(pts[:, 1].max()))
        trechos.append(("esquerda" if xe < 1700 else "direita", ex, ey0, ey1))
    return trocar(out, trechos, px_m_de(p2q), FOLGA_PX["E-1Pavimento"])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("planta", choices=list(FINAIS))
    ap.add_argument("--antes", type=Path, default=None, help="guarda aqui uma cópia da final anterior")
    a = ap.parse_args()
    arq = FINAIS[a.planta]
    if a.antes:
        shutil.copy(arq, a.antes)
    out = np.ascontiguousarray(cv2.imread(str(arq)))
    casa, pav = a.planta.split("-")
    if casa in ("B", "D"):
        n = casa_b_ou_d(casa, out)
    elif casa == "A":
        n = casa_a_1pav(out)
    elif pav == "Terreo":
        n = casa_e_terreo(out)
    else:
        n = casa_e_1pav(out)
    cv2.imwrite(str(arq), out)
    print(f"    {a.planta}: {n} panos trocados pelo pano franzido -> {arq.name}")


if __name__ == "__main__":
    main()

"""O paisagismo do Térreo da Casa C (13/11, "TEMOS QUE MEXER NA GRAMA E NAS ÁRVORES DA ÁREA EXTERNA DA CASA C. DIMINUIR
DRASTICAMENTE E ALTERAR").

Como no Térreo da Casa B (a escolha de lá: as oliveiras): todo o verde externo (o gramado e as árvores e os arbustos sobre
ele; o verde ligado à borda do lote, os jardins internos ficam) refeito com o gramado da Casa B (a amostra repetida sem
emenda, a luz larga do lugar: as manchas das copas de antes saem) e só 3 oliveiras (`OLIVEIRAS`), com a sombra da copa;
fora do lote (o branco) nada muda.

  python3 paisagismo_terreo_casac_1311.py [--antes <png>] [--saida <png>]
"""

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import biblioteca_1pav_casaa_1211 as B1          # noqa: E402
import paisagismo_terreo_casab_1311 as PB        # noqa: E402
import materiais_terreo_casac_1311 as MT         # noqa: E402

PX_M = B1.PX_M
R = AQUI.parents[1] / "POE642_CasaC" / "renders"
FINAL = R / "POE642_CasaC_PH_Terreo_final_rotulos.png"
FINAL_B = AQUI.parents[1] / "POE642_CasaB" / "renders" / "POE642_CasaB_PH_Terreo_final_rotulos.png"
GRAMA_B = (926, 112, 1593, 237)
# as oliveiras: (centro px, diâmetro px)
# (a do alto à esquerda inteira dentro do lote, entre a divisa e o pátio)
OLIVEIRAS = [((455, 190), 230), ((3360, 1030), 260), ((2980, 1560), 200)]
# `ponto_area`/`ponto_lum`: os pontinhos escuros soltos no gramado (restos dos troncos) entram no gramado; os ralos e
# as caixinhas claras, não
VERDE = {"g_b": 12, "r_g": 15, "lum_max": 150, "sementes_x": 175, "luz_sigma": 45.0, "folga_px": 1,
         "ponto_area": 300, "ponto_lum": 100}
ANTES_DEPOIS = {"planta": (150, 0, 3700, 1880)}


def verde_externo(img, q=VERDE):
    I = img.astype(np.int16)
    lum = I.mean(axis=2)
    # o gramado (o oliva da Casa B: R ~ G, B bem abaixo) e as copas (G > R): G - B alto, R pouco acima de G, escuro;
    # fora o granito (R - G ~ 30), o deck (R - G ~ 45) e os pisos claros
    verde = ((I[..., 1] - I[..., 0]) > q["g_b"]) & ((I[..., 2] - I[..., 1]) < q["r_g"]) & (lum < q["lum_max"])
    verde = cv2.morphologyEx(verde.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    n, lab = cv2.connectedComponents(verde, connectivity=8)
    # o gramado de fora: os componentes que tocam a faixa do lote junto à borda esquerda (o gramado contorna a casa)
    # as sementes: o verde junto à borda do lote (a caixa do que não é branco, 25 px para dentro)
    nb = img.astype(np.int16).min(axis=2) < 240
    ys_, xs_ = np.nonzero(nb)
    X0, Y0, X1, Y1 = xs_.min(), ys_.min(), xs_.max(), ys_.max()
    borda = np.zeros(lab.shape, bool)
    borda[Y0:Y1, X0:X1] = True
    borda[Y0 + 25:Y1 - 25, X0 + 25:X1 - 25] = False
    sementes = np.unique(lab[borda])
    tamanhos = np.bincount(lab.ravel())
    # só o gramado ligado à faixa da esquerda (os jardins de inverno e o jardim 1, cercados de paredes, ficam)
    ok = set(int(i) for i in sementes if i > 0 and tamanhos[i] > 2000)
    m = np.isin(lab, list(ok))
    # os buracos (as copas claras, os troncos) dentro do gramado também
    inv = (~m).astype(np.uint8)
    n2, lab2, st2, _ = cv2.connectedComponentsWithStats(inv, connectivity=4)
    for i in range(1, n2):
        x, y, w, h, a = st2[i]
        if a < 40000 and x > 0 and y > 0 and x + w < m.shape[1] and y + h < m.shape[0]:
            reg = lab2 == i
            # só o que é vegetação (verde ou escuro), não um piso cercado de grama (os pisantes)
            cor = I[reg]
            if np.mean((cor[:, 1] - cor[:, 2]) > 0) > 0.6:
                m |= reg
            elif a < q["ponto_area"] and cor.mean() < q["ponto_lum"]:
                m |= reg
    return m


def aplicar(img, q=VERDE):
    out = img.copy()
    H, W = out.shape[:2]
    m = verde_externo(img)
    B = cv2.imread(str(FINAL_B))
    x0, y0, x1, y1 = GRAMA_B
    T = MT.sem_emenda(B[y0:y1, x0:x1].astype(np.float32), H, W)
    # a luz: a do lugar, bem larga (as copas e as sombras delas não ficam), no tom do gramado da Casa B
    L = img.astype(np.float32).mean(axis=2)
    num = cv2.GaussianBlur(L * m, (0, 0), q["luz_sigma"])
    den = cv2.GaussianBlur(m.astype(np.float32), (0, 0), q["luz_sigma"])
    Lm = num / np.maximum(den, 1e-4)
    r = np.clip(Lm / max(float(np.median(L[m])), 1), 0.85, 1.15)
    a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.7)[..., None] * m[..., None]
    novo = T * r[..., None]
    out = np.clip(np.round(out * (1 - a) + novo * a), 0, 255).astype(np.uint8)
    lote = img.astype(np.float32).mean(axis=2) < 245
    base = out.copy()
    P = PB.ler("oliveira")
    rng = np.random.default_rng(1311)
    for (cx, cy), d in OLIVEIRAS:
        out = PB.pousar(out, P, cx, cy, d, float(rng.uniform(0, 360)), PB.SOMBRA_ARVORE)
    out[~lote] = base[~lote]
    print(f"    gramado: {int(m.sum())} px de verde externo (o gramado, as árvores e os arbustos) refeitos com o gramado "
          f"da Casa B; {len(OLIVEIRAS)} oliveiras")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--antes")
    ap.add_argument("--saida")
    a = ap.parse_args()
    antes = cv2.imread(a.antes or str(FINAL))
    depois = aplicar(antes)
    cv2.imwrite(a.saida or str(FINAL), depois)
    if not a.saida:
        x0, y0, x1, y1 = ANTES_DEPOIS["planta"]
        k = 0.42
        A = cv2.resize(antes[y0:y1, x0:x1], None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
        Bd = cv2.resize(depois[y0:y1, x0:x1], None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
        j = np.vstack([A, np.full((16, A.shape[1], 3), 255, np.uint8), Bd])
        t = np.full((44, j.shape[1], 3), 255, np.uint8)
        cv2.putText(t, "ANTES (em cima) | DEPOIS (embaixo)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (40, 40, 40), 2,
                    cv2.LINE_AA)
        cv2.imwrite(str(R / "POE642_CasaC_PH_Terreo_1311_paisagismo_antes_depois.jpg"), np.vstack([t, j]),
                    [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"    {a.saida or FINAL.name}")


if __name__ == "__main__":
    main()

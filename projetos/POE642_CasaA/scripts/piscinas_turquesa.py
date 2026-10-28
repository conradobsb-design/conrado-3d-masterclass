#!/usr/bin/env python3
"""O tom da piscina de referência em todas as piscinas (usuário, 28/10/26: "APLIQUE O TOM DA PISCINA NO TÉRREO TAMBÉM"
e "APLIQUE ESSE TOM DE PISCINA EM TODAS AS PISCINAS DE TODAS AS CASAS").

O tom é o do Subsolo da Casa E (`final3840_casae.PISCINA_E`, com a vista de cima da sauna do modelo 3D: "NOTE TAMBÉM O
TOM DA PISCINA QUE ADOTAREMOS"): a água turquesa (BGR ~168, 160, 42), as peças de 14,5 cm do Barlavento marcadas como
pastilhas e a rede clara das cáusticas. As piscinas dos Térreos (as das Casas A a D vêm dos renders de 2000 px com o
Barlavento sob a água verde-azulada clara de 15/10; a da Casa E, do retocado dela) trocam só a água, sem rodar de novo os
motores, como as cortinas (`cortinas_franzidas.py`):

- a água é achada pela cor (o miolo azul, `ciano`, em manchas de pelo menos `area_min` px, com os furos fechados) e vai
  até a beira quente (o Bege Bahia, a madeira: o azul abaixo do vermelho em `quente_br`), a até `beira_px` do miolo (a
  faixa clara e quase sem cor que o render deixou junto às bordas, na prainha da Casa D, entra); o que não é água fica
  como está: as bordas, as peças claras e neutras grandes dentro da água (as espreguiçadeiras: o que sobra da abertura
  de `peca_px`), os px de `proteger` (os vidros do Térreo da Casa E, pelo PDF);
- os traços escuros sobre a água (`escuro_rel`: os rótulos, os tracejados de projeção) ficam: cada px deles é separado
  da água antiga (a fração do traço pela luz entre a água de perto e o miolo do traço) e posto sobre a nova, sem halo;
- o desenho da água antiga fica: a luz relativa de cada px (as peças do Barlavento e o rejunte, os degraus da prainha e
  do spa, a sombra curta das bordas) passa ao turquesa com o contraste de `ganho` (o claro das cáusticas antigas, que vira
  rede nova, com `ganho_claro`);
- a sombra curta das beiras na água (`sombra`: força e alcance em px), que com a antiga chega à do Subsolo;
- por cima, a rede de cáusticas do Subsolo (`PISCINA_E["causticas"]`, no claro dele), longe das beiras (`causticas_px`).

Uso (da pasta POE642_CasaA/scripts/), uma planta por vez:
  python3 piscinas_turquesa.py A-Terreo | B-Terreo | C-Terreo | D-Terreo [--antes <png>]
A final é regravada no lugar (`--antes` guarda uma cópia da anterior). O Térreo da Casa E usa a mesma rotina na etapa
"piscina" do motor (`final3840_casae.passos_terreo`).
"""
import argparse
import shutil
import sys
from pathlib import Path

import cv2
import numpy as np
from scipy import ndimage

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
sys.path.insert(0, str(AQUI))

TURQUESA = {"ciano": (22, 22, 100), "area_min": 1500, "beira_px": 8, "quente_br": (-14, -2), "peca_croma": 14,
            "peca_px": 9, "escuro_rel": (-0.40, -0.25), "ganho": 1.5, "ganho_claro": 0.6, "base": (0.45, 1.45),
            "causticas_px": (1.5, 4.0), "sombra": (0.22, 2.2), "px_m": 59.7, "semente": 2850}
FINAIS = {"A-Terreo": RAIZ / "POE642_CasaA/renders/POE642_CasaA_PH_Terreo_final_rotulos.png",
          "B-Terreo": RAIZ / "POE642_CasaB/renders/POE642_CasaB_PH_Terreo_final_rotulos.png",
          "C-Terreo": RAIZ / "POE642_CasaC/renders/POE642_CasaC_PH_Terreo_final_rotulos.png",
          "D-Terreo": RAIZ / "POE642_CasaD/renders/POE642_CasaD_PH_Terreo_final_rotulos.png"}


def causticas(h, w, px_m, semente):
    """A rede clara das cáusticas (0 a 1), a mesma do Subsolo da Casa E (`final3840_casae.agua_e`)."""
    from final3840_casae import PISCINA_E
    q = PISCINA_E
    rng = np.random.default_rng(semente)
    c = np.zeros((h, w), np.float32)
    for esc, f in q["causticas"]:
        n = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), esc * px_m * 0.3)
        n /= max(float(n.std()), 1e-6)
        c += f * np.exp(-(n / q["caustica_larg"]) ** 2)
    return np.clip(cv2.GaussianBlur(c, (0, 0), 0.6), 0, 1)


def turquesa(img, px_m=None, semente=None, q=None, proteger=None):
    """A água de `img` (BGR, uint8) no turquesa da referência; devolve (imagem, m² de água por mancha). `proteger`: os
    px que ficam como estão (bool, do tamanho da imagem: os vidros dentro da água, no Térreo da Casa E)."""
    from final3840_casae import PISCINA_E
    q = q or TURQUESA
    px_m = px_m or q["px_m"]
    semente = q["semente"] if semente is None else semente
    a = img.astype(np.float32)
    b, g, r = a[..., 0], a[..., 1], a[..., 2]
    dbr, dgr, bmin = q["ciano"]
    nucleo = (b - r > dbr) & (g - r > dgr) & (b > bmin)
    n, lab, st, _ = cv2.connectedComponentsWithStats(nucleo.astype(np.uint8), 8)
    out = a.copy()
    areas = []
    Y = a.mean(axis=2)
    alc = q["beira_px"]
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] < q["area_min"]:
            continue
        x, y, w, h = st[i, :4]
        f = alc + 6
        x0, y0, x1, y1 = max(x - f, 0), max(y - f, 0), min(x + w + f, img.shape[1]), min(y + h + f, img.shape[0])
        nu = lab[y0:y1, x0:x1] == i
        reg_ = a[y0:y1, x0:x1]
        bb, gg, rr = b[y0:y1, x0:x1], g[y0:y1, x0:x1], r[y0:y1, x0:x1]
        yy = Y[y0:y1, x0:x1]
        croma = reg_.max(axis=2) - reg_.min(axis=2)
        # a mancha da água: o miolo azul com os furos fechados, até a beira quente (o Bege Bahia, a madeira), a até
        # `beira_px` dele (a faixa clara e quase sem cor que o render deixou junto às bordas, na prainha da Casa D, entra)
        r0 = ndimage.binary_fill_holes(cv2.morphologyEx(nu.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)))
        k = 2 * alc + 1
        viz = cv2.dilate(r0.astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool)
        q0, q1 = q["quente_br"]
        cand = viz & ((bb - rr) > q0)
        nc, lc = cv2.connectedComponents(cand.astype(np.uint8), connectivity=4)
        regiao = np.isin(lc, np.unique(lc[r0 & cand])) & (lc > 0)
        regiao = ndimage.binary_fill_holes(regiao)
        # a fração de água de cada px: 1 por dentro, caindo na passagem para a beira quente
        agua = np.clip(((bb - rr) - q0) / (q1 - q0), 0, 1) * cv2.dilate(regiao.astype(np.uint8), np.ones((3, 3), np.uint8))
        # as peças claras e neutras grandes dentro da água (as espreguiçadeiras) ficam, com o antialias em volta
        neutro = regiao & ~nu & (croma < q["peca_croma"]) & (yy > 140)
        grandes = cv2.morphologyEx(neutro.astype(np.uint8), cv2.MORPH_OPEN, np.ones((q["peca_px"],) * 2, np.uint8)) > 0
        grandes = cv2.dilate(grandes.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & ~nu
        agua *= ~grandes
        if proteger is not None:
            agua *= ~proteger[y0:y1, x0:x1]
        ref_y = float(np.median(yy[nu]))
        rel = yy / max(ref_y, 1.0) - 1
        # os traços escuros sobre a água (os rótulos, os tracejados: mais escuros que `escuro_rel[1]`, com o antialias
        # em volta) são separados da água antiga e postos sobre a nova: em cada px, a fração do traço (`at`, pela luz
        # entre a água antiga de perto e o miolo do traço, o mais escuro a 2 px) fica, e o resto vira a água nova
        e0, e1 = q["escuro_rel"]
        escuro = regiao & (rel < e1)
        sobre = cv2.dilate(escuro.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & regiao & (agua > 0.5)
        limpo = nu & ~sobre
        peso = cv2.GaussianBlur(limpo.astype(np.float32), (0, 0), 5)
        y_ant = cv2.GaussianBlur(np.where(limpo, yy, 0).astype(np.float32), (0, 0), 5) / np.maximum(peso, 1e-3)
        y_ant = np.where(peso > 1e-3, y_ant, ref_y)
        tom_traco = cv2.erode(reg_, np.ones((5, 5), np.uint8))          # o miolo do traço mais perto
        at = np.clip((y_ant - yy) / np.maximum(y_ant - tom_traco.mean(axis=2), 1.0), 0, 1) * sobre
        # o desenho da água antiga, relativo: peças, rejunte, degraus e a sombra das bordas (o claro, menos); sob os
        # traços e na faixa clara das beiras, a água lisa
        rel = np.where(rel < 0, q["ganho"] * rel, q["ganho_claro"] * rel)
        base = np.where(sobre | ~nu & (croma < q["peca_croma"]), 1.0, np.clip(1 + rel, *q["base"]))
        # a sombra curta das beiras e a rede das cáusticas, longe delas
        dist = cv2.distanceTransform((agua > 0.5).astype(np.uint8), cv2.DIST_L2, 5)
        fs, sa = q["sombra"]
        base *= 1 - fs * np.exp(-np.maximum(dist - 0.5, 0) / sa)
        nova = np.float32(PISCINA_E["tom"]) * base[..., None]
        d0, d1 = q["causticas_px"]
        c = causticas(y1 - y0, x1 - x0, px_m, semente + i) * np.clip((dist - d0) / (d1 - d0), 0, 1)
        nova = nova * (1 - c[..., None]) + np.float32(PISCINA_E["claro"]) * c[..., None]
        nova = np.where(sobre[..., None], tom_traco * at[..., None] + nova * (1 - at[..., None]), nova)
        reg = out[y0:y1, x0:x1]
        reg[:] = reg * (1 - agua[..., None]) + nova * agua[..., None]
        areas.append(round(float(agua.sum()) / px_m ** 2, 1))
    return np.clip(np.round(out), 0, 255).astype(np.uint8), areas


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("planta", choices=sorted(FINAIS))
    ap.add_argument("--antes", type=Path, help="guarda aqui uma cópia da final anterior")
    a = ap.parse_args()
    final = FINAIS[a.planta]
    if a.antes:
        shutil.copyfile(final, a.antes)
    img = cv2.imread(str(final))
    novo, areas = turquesa(img)
    cv2.imwrite(str(final), novo)
    print(f"{a.planta}: a água de {len(areas)} piscinas no turquesa da referência ({', '.join(map(str, areas))} m²) "
          f"-> {final.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()

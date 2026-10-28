#!/usr/bin/env python3
"""Leva às finais aprovadas só as faixas dos boxes de uma final refeita pelo motor (pedido de 28/10/26: "melhore a
representação dos box dos chuveiros com folha contínua, sem tracejado. reveja todos os box de todos os ambientes").

Os motores das Casas C, D e E, refeitos da etapa dos boxes, redesenham também as paredes, com o antialias das bordas
1 px diferente do da final aprovada (o código das paredes mudou depois da última rodada completa), e nas Casas C e D
saem antes do turquesa e das bordas da piscina (`piscinas_turquesa.py`). Para que só os boxes mudem, a final aprovada
(a do git, `--antes`) recebe da refeita apenas a faixa de cada box: do vão (`final3840_casaa.vao_box`) com `folga_px` a
mais nas pontas e `meia_px` de cada lado da linha do vidro (a limpeza de `limpa_px`, o vidro e a sombra curta).

Uso (de POE642_CasaA/scripts/):
  git show HEAD:projetos/POE642_CasaC/renders/POE642_CasaC_PH_Terreo_final_rotulos.png > /tmp/c_antes.png
  python3 colar_boxes.py C-Terreo --antes /tmp/c_antes.png --nova <final refeita pelo motor> --saida <final>
"""
import argparse

import cv2
import numpy as np

import ajustes_casaa as AJ
import final3840_casaa as FA
import piscinas_turquesa as PT

FAIXA = {"meia_px": 8, "folga_px": 3}


def boxes_da_planta(planta):
    """Os boxes de correr que o motor da planta desenha com `final3840_casaa.boxes`."""
    Q = PT.quadro(planta)
    if planta == "D-Terreo":
        import final3840_casad as D
        return Q, [dict(b) for b in D.BOXES_TD]
    return Q, AJ.folhas_box(Q.pg)


def mascara(Q, boxes, forma):
    q = FAIXA
    m = np.zeros(forma, bool)
    for b in boxes:
        v0, v1 = FA.vao_box(Q, b)
        hor, meio = b["hor"], b["meio"]
        (x0, y0), (x1, y1) = (Q.p2q(v0, meio), Q.p2q(v1, meio)) if hor else (Q.p2q(meio, v0), Q.p2q(meio, v1))
        if hor:
            c = int(round(y0))
            m[c - q["meia_px"]:c + q["meia_px"] + 1,
              int(np.floor(x0)) - q["folga_px"]:int(np.ceil(x1)) + q["folga_px"]] = True
        else:
            c = int(round(x0))
            m[int(np.floor(y0)) - q["folga_px"]:int(np.ceil(y1)) + q["folga_px"],
              c - q["meia_px"]:c + q["meia_px"] + 1] = True
    return m


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("planta", help="C-Terreo, C-Subsolo, D-Terreo, D-Subsolo, E-Terreo...")
    ap.add_argument("--antes", required=True, help="a final aprovada (PNG)")
    ap.add_argument("--nova", required=True, help="a final refeita pelo motor (PNG)")
    ap.add_argument("--saida", required=True)
    a = ap.parse_args()
    antes, nova = cv2.imread(a.antes), cv2.imread(a.nova)
    Q, boxes = boxes_da_planta(a.planta)
    m = mascara(Q, boxes, antes.shape[:2])
    out = np.where(m[..., None], nova, antes)
    cv2.imwrite(a.saida, out)
    mud = (np.abs(out.astype(int) - antes.astype(int)).max(axis=2) > 0).sum()
    print(f"    {a.planta}: {len(boxes)} boxes, {int(m.sum())} px nas faixas, {mud} px mudados -> {a.saida}")

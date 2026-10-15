#!/usr/bin/env python3
"""Retoques locais, sem IA, no render v1 do Subsolo da Casa D (POE 642).

O render (Nano Banana Pro, 2000 x 1116) saiu fiel no layout, mas aproximou a planta (~2,73 x a
base reduzida a 2000 px). Os retoques são feitos no quadro do render, como no Térreo; no fim, a
imagem vai para o quadro comum das bases (a mesma folha e o mesmo enquadramento do Térreo), para
a planta do Subsolo cair exatamente sob a do Térreo.

Itens (o mapa está em POE642_CasaD/renders/POE642_CasaD_PH_Subsolo_v1_erros.jpg):
1. Depósito: a faixa areia que o motor pôs junto à parede da esquerda (um armário que não existe no
   PDF) vira o granito do piso.
2. Depósito: as juntas de placas gigantes (~1,9 m) e as quatro manchas claras do granito saem; o piso
   fica contínuo, como no DCE 1 e no WC DCE (pedido do usuário).

Uso (da pasta projetos/):
  python3 POE642_CasaA/scripts/retoque_subsolo_casad.py POE642_CasaD/renders/POE642_CasaD_PH_Subsolo_v1_render.webp \
      --saida POE642_CasaD/renders --nome POE642_CasaD_PH_Subsolo_v1_retocado
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent          # projetos/
sys.path.insert(0, str(AQUI))

from retoque_terreo_casad import interpolar, textura  # noqa: E402

# trechos limpos do granito do depósito, entre as juntas do motor (px do render)
GRANITO = [(1110, 60, 1176, 220), (1192, 60, 1326, 220), (1192, 240, 1326, 380)]

FAIXA_DEPOSITO = {
    "ret": (1046, 42, 1132, 257),          # janela: a faixa e um trecho do granito à direita
    "faixa": (1049, 44, 1104, 256),        # a faixa areia, até a sombra da borda direita
    "lum_min": 45,                         # a parede (escura) não entra na luz nem muda
}

JUNTAS_DEPOSITO = {
    "ret": (1046, 42, 1398, 498),          # o depósito inteiro (até a parede da academia)
    "faixas": [(1180, 44, 1185, 497), (1332, 44, 1337, 497),        # juntas verticais (x 1182 e 1334)
               (1100, 226, 1396, 231), (1143, 387, 1373, 392)],     # horizontais (y 228 e 389)
    "manchas": [(1112, 252, 9, 8), (1092, 305, 9, 10), (1130, 305, 9, 9), (1204, 422, 9, 10)],
    "lum": (45, 200),                      # só o granito e as juntas mudam; a parede e os arcos ficam
    "folha": (1141, 479, 1199, 488),       # a folha da porta no fim da escada (com o contorno) não muda
}


def apagar_largo(out, ret, mascara, fontes, sigma=4.0, borda=0.8, lum_min=None, lum_max=None):
    """Como o apagar do Térreo, para áreas largas: a luz do entorno (por canal) vem da convolução
    normalizada em várias escalas (interpolar), que cobre o miolo da máscara; com lum_min, a parede
    (escura) não entra na luz e não muda; com lum_max, peças claras (folhas de porta) não entram na luz."""
    x0, y0, x1, y1 = ret
    h, w = y1 - y0, x1 - x0
    reg = out[y0:y1, x0:x1].astype(np.float32)
    claro = reg.mean(axis=2) > lum_min if lum_min is not None else np.ones((h, w), bool)
    m = cv2.GaussianBlur(mascara.astype(np.float32), (0, 0), borda) if borda else mascara.astype(np.float32)
    m = np.maximum(m, mascara.astype(np.float32)) * claro
    amostra = ~mascara & claro
    if lum_max is not None:
        amostra &= reg.mean(axis=2) < lum_max
    luz = interpolar(reg, amostra, sigma)
    tex = textura(out, fontes, h, w)
    out[y0:y1, x0:x1] = np.clip(reg * (1 - m[..., None]) + tex * luz * m[..., None], 0, 255).astype(np.uint8)
    return out


def faixa_deposito(out):
    q = FAIXA_DEPOSITO
    x0, y0, x1, y1 = q["ret"]
    fx0, fy0, fx1, fy1 = q["faixa"]
    m = np.zeros((y1 - y0, x1 - x0), bool)
    m[fy0 - y0:fy1 - y0, fx0 - x0:fx1 - x0] = True
    out = apagar_largo(out, q["ret"], m, GRANITO, sigma=4.0, borda=0.8, lum_min=q["lum_min"])
    print("    faixa areia do depósito fora; granito no lugar")
    return out


def juntas_deposito(out):
    q = JUNTAS_DEPOSITO
    x0, y0, x1, y1 = q["ret"]
    m = np.zeros((y1 - y0, x1 - x0), np.uint8)
    for fx0, fy0, fx1, fy1 in q["faixas"]:
        m[fy0 - y0:fy1 - y0, fx0 - x0:fx1 - x0] = 1
    for mx, my, mw, mh in q["manchas"]:
        cv2.ellipse(m, (mx + mw // 2 - x0, my + mh // 2 - y0), (mw // 2 + 3, mh // 2 + 3), 0, 0, 360, 1, -1)
    lum = out[y0:y1, x0:x1].astype(np.float32).mean(axis=2)
    m = m.astype(bool) & (lum > q["lum"][0]) & (lum < q["lum"][1])
    fx0, fy0, fx1, fy1 = q["folha"]
    m[fy0 - y0:fy1 - y0, fx0 - x0:fx1 - x0] = False
    out = apagar_largo(out, q["ret"], m, GRANITO, sigma=2.0, borda=0.6, lum_min=q["lum"][0], lum_max=110)
    print(f"    juntas e manchas do depósito fora: {int(m.sum())} px")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("render", type=Path)
    ap.add_argument("--saida", type=Path, default=Path("."))
    ap.add_argument("--nome", required=True)
    args = ap.parse_args()

    orig = cv2.imread(str(args.render))
    out = orig.copy()
    print("[1] depósito: faixa areia inventada")
    out = faixa_deposito(out)
    print("[2] depósito: juntas gigantes e manchas claras")
    out = juntas_deposito(out)

    args.saida.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(args.saida / f"{args.nome}.png"), out)
    alfa = np.where(np.abs(out.astype(int) - orig.astype(int)).max(axis=2) > 0, 255, 0).astype(np.uint8)
    cv2.imwrite(str(args.saida / f"{args.nome}_camada.png"), np.dstack([out, alfa]))
    print(f"[fim] {args.saida / (args.nome + '.png')}; {int((alfa > 0).sum())} px alterados")


if __name__ == "__main__":
    main()

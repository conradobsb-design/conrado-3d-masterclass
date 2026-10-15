#!/usr/bin/env python3
"""Retoques locais, sem IA, no render v1 do Subsolo da Casa D (POE 642).

O render (Nano Banana Pro, 2000 x 1116) saiu fiel no layout, mas aproximou a planta (~2,73 x a
base reduzida a 2000 px). Os retoques são feitos no quadro do render, como no Térreo; no fim, a
imagem vai para o quadro comum das bases (a mesma folha e o mesmo enquadramento do Térreo), para
a planta do Subsolo cair exatamente sob a do Térreo.

Itens (o mapa está em POE642_CasaD/renders/POE642_CasaD_PH_Subsolo_v1_erros.jpg):
1. Depósito: a faixa areia que o motor pôs junto à parede da esquerda (um armário que não existe no
   PDF) vira o granito do piso.

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


def apagar_largo(out, ret, mascara, fontes, sigma=4.0, borda=0.8, lum_min=None):
    """Como o apagar do Térreo, para áreas largas: a luz do entorno (por canal) vem da convolução
    normalizada em várias escalas (interpolar), que cobre o miolo da máscara; com lum_min, a parede
    (escura) não entra na luz e não muda."""
    x0, y0, x1, y1 = ret
    h, w = y1 - y0, x1 - x0
    reg = out[y0:y1, x0:x1].astype(np.float32)
    claro = reg.mean(axis=2) > lum_min if lum_min is not None else np.ones((h, w), bool)
    m = cv2.GaussianBlur(mascara.astype(np.float32), (0, 0), borda) if borda else mascara.astype(np.float32)
    m = np.maximum(m, mascara.astype(np.float32)) * claro
    luz = interpolar(reg, ~mascara & claro, sigma)
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

    args.saida.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(args.saida / f"{args.nome}.png"), out)
    alfa = np.where(np.abs(out.astype(int) - orig.astype(int)).max(axis=2) > 0, 255, 0).astype(np.uint8)
    cv2.imwrite(str(args.saida / f"{args.nome}_camada.png"), np.dstack([out, alfa]))
    print(f"[fim] {args.saida / (args.nome + '.png')}; {int((alfa > 0).sum())} px alterados")


if __name__ == "__main__":
    main()

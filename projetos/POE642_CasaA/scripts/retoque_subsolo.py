#!/usr/bin/env python3
"""Retoque sem IA do render aprovado do Subsolo (v6): o ajuste que ficou pendente.

1. Sauna: o bloco claro no canto de cima à esquerda, encostado no vidro, não é banco, é piso.
   Ele vira o mesmo travertino da sauna, copiado das mesmas linhas logo à direita (os veios são
   horizontais, então a cópia na mesma linha continua as faixas sem emenda). A sombra que o
   bloco fazia no piso sai junto. O banco horizontal, ao longo da parede de baixo, fica.
2. Tom: a imagem fica mais clara e com menos sombra, como a curva "Sombras +" do Camera Raw.
   Os meios-tons sobem um pouco no L do Lab; o preto das paredes e o branco do fundo não mudam,
   e a cor também não.
3. Fundo: o quase-branco (marquinhas que o motor deixou no fundo) vira branco puro.

Uso:
  python retoque_subsolo.py RENDER_SUBSOLO --saida PASTA
"""
import argparse
from pathlib import Path

import cv2
import numpy as np

# px num render de 2000 px de largura
BLOCO_SAUNA = (625, 786, 654, 826)    # x0, y0, x1, y1: bloco claro + a sombra dele no piso
DESLOCAMENTO = 30                     # a fonte é o piso da sauna 30 px à direita, nas mesmas linhas
SOMBRAS = 12.0                        # quanto os meios-tons sobem (em L de 0 a 255)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("render", type=Path)
    ap.add_argument("--saida", type=Path, default=Path("."))
    args = ap.parse_args()

    r = cv2.imread(str(args.render))
    H, W = r.shape[:2]
    e = W / 2000
    out = r.astype(np.float32)

    print("[1] sauna: bloco do canto vira piso")
    x0, y0, x1, y1 = (int(round(v * e)) for v in BLOCO_SAUNA)
    d = int(round(DESLOCAMENTO * e))
    fonte = out[y0:y1, x0 + d:x1 + d].copy()
    alfa = np.ones((y1 - y0, x1 - x0, 1), np.float32)
    borda = max(2, int(round(7 * e)))                 # costura suave só do lado do piso (direita)
    alfa[:, -borda:, 0] = np.linspace(1, 0, borda)[None, :]
    out[y0:y1, x0:x1] = fonte * alfa + out[y0:y1, x0:x1] * (1 - alfa)

    print("[2] tom: menos sombra")
    lab = cv2.cvtColor(np.clip(out, 0, 255).astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32)
    L = lab[..., 0]
    curva = np.sin(np.pi * np.clip((L - 40) / (245 - 40), 0, 1)) * SOMBRAS
    lab[..., 0] = np.clip(L + curva, 0, 255)
    out = cv2.cvtColor(lab.astype(np.uint8), cv2.COLOR_LAB2BGR)

    print("[3] fundo: o quase-branco vira branco puro")
    # o motor deixou marquinhas quase invisíveis no fundo; o entorno esmaecido é mais escuro que isto
    f = out.astype(int)
    quase = (f.min(axis=2) >= 244) & (f.max(axis=2) - f.min(axis=2) <= 6)
    out[quase] = 255

    args.saida.mkdir(parents=True, exist_ok=True)
    caminho = args.saida / "POE642_CasaA_PH_Subsolo_final.png"
    cv2.imwrite(str(caminho), out)
    print(f"[4] {caminho} ({W}x{H})")


if __name__ == "__main__":
    main()

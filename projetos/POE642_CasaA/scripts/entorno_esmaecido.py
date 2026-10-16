#!/usr/bin/env python3
"""Pavimento de baixo esmaecido em volta de um pavimento superior, na base 16:9 (POE 642).

Pedido do usuário (16/10/26, Casa E · 1º Pavimento): vegetação no entorno da residência, com o
Térreo esmaecido em volta, como o contexto do 1º Pavimento da Casa A. O PDF do 1º Pavimento da Casa E
não traz o Térreo, então ele vem do render aprovado do Térreo:
- o render aprovado do pavimento de baixo é levado ao quadro 16:9 comum (SIFT + afim contra a base
  dele, o mesmo `no_quadro_comum` das pranchas), na largura da base de cima;
- fica mais claro e menos saturado (`--clarear`, `--saturacao`): gramado, paisagismo, piscina, deck e
  acessos aparecem como contexto;
- por cima, o pavimento de cima sobreposto integralmente (100% opaco, pedido do usuário: "na parte
  do 1º pavimento, sobrepor integralmente"), na pegada dele: tudo o que não é branco na base dele
  (paredes, pisos, varandas, vazios), fechado e com os furos preenchidos; áreas brancas de fora
  presas na pegada (`--fora`, em px de uma prévia de 2000 px) voltam a mostrar o contexto;
- as linhas tracejadas do lote do pavimento de cima continuam por cima.

Fluxo escolhido para a Casa E (16/10/26): o motor renderiza só o 1º Pavimento em fundo branco (base v3
e prompt v1), e o Térreo esmaecido entra depois, por este script, exato. Com `--base-cima`, a primeira
imagem é o render do pavimento de cima: ele vai ao quadro da base dele (SIFT + afim), e a pegada sai
da base (a geometria do projeto), não do render.

Uso (da pasta POE642_CasaA/scripts/):
  # render do 1º Pavimento (fundo branco) + Térreo esmaecido, na largura da prancha
  python3 entorno_esmaecido.py ../../POE642_CasaE/renders/<render_1Pavimento>.png \\
      ../../POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_retocado.png \\
      ../../POE642_CasaE/bases/POE642_CasaE_BASE_Terreo_v3_texturas_16x9.png \\
      ../../POE642_CasaE/renders/<saida>.png --fora 912 752 1096 816 \\
      --base-cima ../../POE642_CasaE/bases/POE642_CasaE_BASE_1Pavimento_v3_texturas_16x9.png --largura 3840
  # base com o entorno (v4): a primeira imagem é a própria base
  python3 entorno_esmaecido.py ../../POE642_CasaE/bases/POE642_CasaE_BASE_1Pavimento_v3_texturas_16x9.png \\
      ../../POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_retocado.png \\
      ../../POE642_CasaE/bases/POE642_CasaE_BASE_Terreo_v3_texturas_16x9.png \\
      ../../POE642_CasaE/bases/POE642_CasaE_BASE_1Pavimento_v4_entorno_16x9.png --fora 912 752 1096 816
"""
import argparse
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from scipy import ndimage

from rodape_entrega import no_quadro_comum


def pegada(base, fora=()):
    """A pegada do pavimento de cima: o que não é branco, em manchas grandes (sem as linhas
    tracejadas do lote), fechado e com os furos preenchidos."""
    H, W = base.shape[:2]
    nb = base.min(axis=2) < 225
    n, lab, st, _ = cv2.connectedComponentsWithStats(nb.astype(np.uint8), connectivity=8)
    grandes = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > 20000])
    peg = ndimage.binary_fill_holes(cv2.morphologyEx(grandes.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8)))
    k = W / 2000
    branco = base.min(axis=2) >= 245
    for x0, y0, x1, y1 in fora:
        x0, y0, x1, y1 = (int(v * k) for v in (x0, y0, x1, y1))
        peg[y0:y1, x0:x1] &= ~branco[y0:y1, x0:x1]
    return cv2.morphologyEx(peg.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)) > 0


def compor(base, render_baixo, base_baixo, clarear=0.75, saturacao=0.4, fora=(), cima=None, recorte=None):
    """base: a base 16:9 do pavimento de cima (pegada e tracejado); cima: a imagem que vai por cima,
    já no quadro da base (o render do pavimento de cima), ou None para a própria base."""
    H, W = base.shape[:2]
    cima = base if cima is None else cima
    peg = pegada(base, fora)
    t = no_quadro_comum(Image.open(render_baixo).convert("RGB"), base_baixo, "pavimento de baixo", W)
    t = cv2.cvtColor(np.asarray(t), cv2.COLOR_RGB2BGR).astype(np.float32)
    cinza = t.mean(axis=2, keepdims=True)
    t = cinza + (t - cinza) * saturacao
    t = 255 - (255 - t) * (1 - clarear)
    a = cv2.GaussianBlur(peg.astype(np.float32), (0, 0), 1.0)
    a = np.maximum(a, peg)[..., None]
    out = cima.astype(np.float32) * a + t * (1 - a)
    tracejado = (base.min(axis=2) < 225) & ~peg
    out[tracejado] = base[tracejado]
    if recorte is not None:
        # o térreo esmaecido sem a parte que fica atrás do pavimento de cima (transparente), como camada
        camada = np.dstack([np.clip(t, 0, 255), 255 * (1 - a)]).astype(np.uint8)
        cv2.imwrite(str(recorte), camada)
        print(f"    camada do térreo recortado: {recorte}")
    print(f"    pegada do pavimento de cima: {100 * peg.mean():.1f}% da imagem")
    return np.clip(out, 0, 255).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cima", type=Path, help="base 16:9 do pavimento de cima, ou o render dele (com --base-cima)")
    ap.add_argument("render_baixo", type=Path, help="render aprovado do pavimento de baixo")
    ap.add_argument("base_baixo", type=Path, help="base 16:9 do pavimento de baixo (alinhamento)")
    ap.add_argument("saida", type=Path)
    ap.add_argument("--clarear", type=float, default=0.75)
    ap.add_argument("--saturacao", type=float, default=0.4)
    ap.add_argument("--base-cima", type=Path, default=None,
                    help="base 16:9 do pavimento de cima, quando a primeira imagem é o render dele")
    ap.add_argument("--largura", type=int, default=None, help="largura da saída (padrão: a da base)")
    ap.add_argument("--recorte", type=Path, default=None,
                    help="salva também o térreo esmaecido com a área do pavimento de cima transparente (PNG)")
    ap.add_argument("--fora", type=float, nargs=4, action="append", default=[], metavar=("X0", "Y0", "X1", "Y1"),
                    help="área branca de fora presa na pegada (px de uma prévia de 2000 px); pode repetir")
    args = ap.parse_args()
    base = cv2.imread(str(args.base_cima or args.cima))
    W = args.largura or base.shape[1]
    if W != base.shape[1]:
        base = cv2.resize(base, (W, round(base.shape[0] * W / base.shape[1])), interpolation=cv2.INTER_AREA)
    cima = None
    if args.base_cima:
        cima = cv2.cvtColor(np.asarray(no_quadro_comum(Image.open(args.cima).convert("RGB"), args.base_cima,
                                                       "pavimento de cima", W)), cv2.COLOR_RGB2BGR)
    out = compor(base, args.render_baixo, args.base_baixo, args.clarear, args.saturacao, args.fora, cima, args.recorte)
    cv2.imwrite(str(args.saida), out)
    prev = args.saida.with_name(args.saida.stem + "_preview.jpg")
    cv2.imwrite(str(prev), cv2.resize(out, (2000, round(2000 * out.shape[0] / out.shape[1])), interpolation=cv2.INTER_AREA),
                [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"[fim] {args.saida}\n      {prev}")


if __name__ == "__main__":
    main()

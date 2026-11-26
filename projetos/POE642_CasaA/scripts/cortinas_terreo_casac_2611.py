"""Casa C Térreo (26/11): as cortinas do hall de entrada e da sala de estar na C4 bem visível.

Usuário: "substituir as cortinas pela que estamos adotando", "somente substitua as cortinas do hall de entrada e
sala/living" e "sala de estar, retificando". O Térreo da C estava com a C4 de 13/11 (`pedidos_terreo_casac_1311.cortinas`,
o pano de 9 px, que no 12K lê como um ziguezague cinza); o padrão adotado depois é a C4 bem visível de 16/11
(`cortinas_padrao_casad_1611.aplicar`: o linho em ondas a 0,82 com o trilho grafite do lado do vidro, o pano de 0,22 m,
a sombra inteira, até a ponta da parede e 0,15 m além dela onde a parede segue), a mesma das Casas B, D, E e do
1º Pavimento da A. Só nos trilhos do estar e do hall de entrada (`CAIXAS`); os outros ficam.

Como em `um_pav_casaa_2511b.cortinas`: a função roda na final (no quadro da Casa C) e anota cada limpeza e cada pouso;
o 12K repete as mesmas contas na escala dele (as paredes do PDF levadas por `remap`), pelo registro local.

  python3 cortinas_terreo_casac_2611.py
"""
import contextlib
import io
import json
import os
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
sys.path.insert(0, str(Path(__file__).resolve().parent))
import esquadrias_pretas_1911 as EP  # noqa: E402

PLANTA = "C_Terreo"
# os trilhos que mudam: os que caem nestas caixas (px da final): o estar (a janela de baixo e o vidro da direita) e o hall
CAIXAS = [(1880.0, 1600.0, 2140.0, 1665.0),          # estar, a janela de baixo
          (2380.0, 1280.0, 2420.0, 1660.0),          # estar, o vidro da direita (para o jardim)
          (2380.0, 1440.0, 2720.0, 1660.0)]          # hall de entrada (o L de vidro)
_CORT = {}


def _plano():
    """Roda a C4 bem visível na final e guarda o resultado, as limpezas (o, v, A0, A1, S0, S1) e os pousos."""
    if "plano" in _CORT:
        return _CORT["plano"]
    import inspect
    import textwrap
    import cortinas_padrao_casad_1611 as CP
    import pedidos_terreo_casac_1311 as PT
    import biblioteca_terreo_casaa_1211 as BT
    src = textwrap.dedent(inspect.getsource(PT.cortinas))
    alvo = "        alvo[livre_] = fonte[livre_]\n"
    assert alvo in src
    src = src.replace(alvo, alvo + "        _OPS.append((o, v, A0, A1, S0, S1))\n").replace("def cortinas(", "def _cortinas_reg(")
    ops, pousos = [], []
    ns = dict(PT.__dict__)
    ns["_OPS"] = ops
    exec(compile(src, PT.__file__, "exec"), ns)
    orig_c, orig_p = PT.cortinas, BT.pousar

    def pousar(out, P, cx, cy, wt, ht, ang, sombras, px_m, *a, **k):
        pousos.append((P.copy(), cx, cy, wt, ht, ang, [dict(s_) for s_ in sombras], px_m))
        return orig_p(out, P, cx, cy, wt, ht, ang, sombras, px_m, *a, **k)
    PT.cortinas, BT.pousar = ns["_cortinas_reg"], pousar
    try:
        Q = PT.quadro()
        base = cv2.imread(str(EP.PROJ / EP.PLANTAS[PLANTA][0]))
        with contextlib.redirect_stdout(io.StringIO()):
            par = Q.preencher(lambda d: d.get("layer") == "ARQ_PAREDE" and d.get("fill") and max(d["fill"]) < 0.6,
                              ss=2)
            res = CP.aplicar(Q, base.copy(), q=dict(CP.CORTINAS_D, extra=[]))
    finally:
        PT.cortinas, BT.pousar = orig_c, orig_p
    # só os trilhos do estar e do hall
    sel = []
    for i, (P, cx, cy, wt, ht, *_r) in enumerate(pousos):
        if any(a <= cx <= c and b <= cy <= d for a, b, c, d in CAIXAS):
            sel.append(i)
    _CORT["plano"] = (base, res, ops, pousos, (par > 0.3).astype(np.float32), sel)
    return _CORT["plano"]


def cortinas(img, s, origem, idx=None):
    base, res, ops, pousos, par, sel = _plano()
    sel = sel if idx is None else [idx]
    if s < 2:                                      # a final: os px que a função mudou, em volta de cada trilho escolhido
        mud = np.any(res != base, axis=2)
        caixa = np.zeros_like(mud)
        for i in sel:
            P, cx, cy, wt, ht = pousos[i][:5]
            x0, x1 = int(cx - wt / 2 - 12), int(cx + wt / 2 + 12)
            y0, y1 = int(cy - ht / 2 - 12), int(cy + ht / 2 + 12)
            caixa[max(y0, 0):y1, max(x0, 0):x1] = True
        mud &= caixa
        img[mud] = res[mud]
        return img
    for i in sel:
        o, v, A0, A1, S0, S1 = ops[i]
        ia, ib = (0, 1) if o == "v" else (1, 0)
        a0 = int(round((A0 - origem[ia]) * s))
        a1 = int(round((A1 - origem[ia]) * s))
        s0 = int(round((S0 - origem[ib]) * s))
        s1 = int(round((S1 - origem[ib]) * s))
        n = a1 - a0
        im = img if o == "v" else img.transpose(1, 0, 2)
        if not (0 <= s0 < s1 <= im.shape[0] and n > 0 and a0 - n >= 0 and a1 + n <= im.shape[1]):
            continue
        fonte = (im[s0:s1, a1:a1 + n] if v == "esquerda" else im[s0:s1, a0 - n:a0])[:, ::-1].copy()
        rr, cc = np.mgrid[s0:s1, a0:a1].astype(np.float32)
        fx, fy = (cc, rr) if o == "v" else (rr, cc)
        mx = ((fx + 0.5) / s + origem[0] - 0.5).astype(np.float32)
        my = ((fy + 0.5) / s + origem[1] - 0.5).astype(np.float32)
        pq = cv2.remap(par, mx, my, cv2.INTER_LINEAR, borderValue=0) > 0.5
        alvo = im[s0:s1, a0:a1]
        alvo[~pq] = fonte[~pq]
    import biblioteca_terreo_casaa_1211 as BT
    o_ = img.astype(np.float32)
    for i in sel:
        P, cx, cy, wt, ht, ang, sombras, px_m = pousos[i]
        o_ = BT.pousar(o_, P, (cx - origem[0]) * s, (cy - origem[1]) * s, wt * s, ht * s, ang, sombras, px_m * s)
    img[:] = np.clip(np.round(o_), 0, 255).astype(np.uint8)
    return img


def caixas_trilhos():
    _b, _r, ops, pousos, _p, sel = _plano()
    out = {}
    for i in sel:
        P, cx, cy, wt, ht = pousos[i][:5]
        out[i] = (cx - wt / 2 - 20, cy - ht / 2 - 20, cx + wt / 2 + 20, cy + ht / 2 + 20)
    return out


def main():
    c, pav = PLANTA.split("_")
    base = cv2.imread(str(EP.PROJ / EP.PLANTAS[PLANTA][0]))
    cx_ = caixas_trilhos()
    print("trilhos:", {i: tuple(round(v) for v in r) for i, r in cx_.items()})
    for f in EP.PLANTAS[PLANTA]:
        im = cv2.imread(str(EP.PROJ / f))
        im = cortinas(im, 1.0, (0.0, 0.0))
        cv2.imwrite(str(EP.PROJ / f), im)
        if f == EP.PLANTAS[PLANTA][0]:
            novo = im
    pf = EP.PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_entrega.png"
    pr = cv2.imread(str(pf))
    pr[:2160] = novo
    cv2.imwrite(str(pf), pr)
    dz = json.loads((EP.PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[PLANTA]
    for op in os.environ.get("OPCOES", "AB"):
        rel = EP.PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_12K_opcao_{op}.jpg"
        pil = Image.open(rel)
        dpi = pil.info.get("dpi", (743, 743))
        im = cv2.cvtColor(np.array(pil.convert("RGB")), cv2.COLOR_RGB2BGR)
        del pil
        cinza = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        for i, (x0, y0, x1, y1) in cx_.items():
            mapa, cc = EP.registro_12k(base, cinza, dz, (int(x0) - 60, int(y0) - 60, int(x1) + 60, int(y1) + 60))
            A, B = mapa(x0, y0)
            ex_ = (mapa(x0 + 1000.0, y0)[0] - A) / 1000.0
            ey_ = (mapa(x0, y0 + 1000.0)[1] - B) / 1000.0
            sx = (ex_ * (x1 - x0) + ey_ * (y1 - y0)) / ((x1 - x0) + (y1 - y0))
            im = cortinas(im, sx, (x0 - A / sx, y0 - B / sx), i)
            print(f"   {op}: cortina {i} (registro {cc:.3f}, escala {sx:.3f})")
        Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).save(rel, quality=95, subsampling=0, dpi=dpi)
        del im, cinza


if __name__ == "__main__":
    main()

"""Térreo da Casa E, 17/11 ("Troque o freezer da área gourmet para a linha inox da biblioteca"): no módulo que avança da
bancada de trás da gourmet (`pedidos_terreo_casae_1611.GOURMET["geladeira_pt"]`), a caixa de inox lisa e lavada de hoje
sai e entra a geladeira inox G2 da biblioteca (`POE642_CasaA/biblioteca-objetos/02-terreo/cozinha/geladeira-inox.png`,
a mesma das cozinhas da B e da D), no retângulo do módulo, com a frente (o friso e os 2 puxadores) para a gourmet e a
sombra curta; no pé, a faixa clara antiga atrás dos puxadores e os 2 risquinhos claros sob o armário ao lado vão ao
piso marrom. Na final e direto nos 12K A e B (o afim afinado na caixa).

  python3 geladeira_gourmet_casae_1711.py doze [--opcao AB]     (antes da final: a final de antes é a referência)
  python3 geladeira_gourmet_casae_1711.py final
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import danae_foto as DF                                     # noqa: E402
from correcoes_terreo_casab_1611 import Mapa                # noqa: E402
from instalacao_terreo_casad_1711 import _pousar, _remenda  # noqa: E402
import correcoes_terreo_casab_1611 as CB                    # noqa: E402

RAIZ = AQUI.parents[1]
FINAL = RAIZ / "POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_final.png"
DOZE = RAIZ / "POE642_CasaE/entrega/POE642_CasaE_PH_Terreo_12K_opcao_{}.jpg"
PNG = RAIZ / "POE642_CasaA/biblioteca-objetos/02-terreo/cozinha/geladeira-inox.png"
# o módulo (px da final: entre a bancada da cuba e o armário liso, da parede ao pé) e a caixa do afim local
Q = {"modulo": (1345.5, 601.0, 1393.5, 649.6), "sombra": 0.28, "caixa": (1300, 570, 1440, 680),
     "contorno": (78, 80, 84), "contorno_px": 0.35,
     # o piso no pé: a faixa clara antiga atrás dos puxadores e os 2 risquinhos claros sob o armário ao lado
     "limpa": [((1345.0, 645.2, 1394.2, 652.0), (0.0, 8.0)), ((1394.2, 644.0, 1441.0, 647.6), (0.0, 7.0))]}


def _png():
    P = cv2.imread(str(PNG), cv2.IMREAD_UNCHANGED)
    a = P[..., 3].astype(np.float32) / 255
    ys, xs = np.nonzero(a > 0.02)
    P = P[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return P[..., :3], P[..., 3].astype(np.float32) / 255


def aplicar(img, m, q=Q):
    out = img.copy()
    for r, d in q["limpa"]:
        _remenda(out, m, r, [d], None)
    rgb, a = _png()
    _pousar(out, rgb, a, m.ret(q["modulo"]), q["sombra"], m.s)
    # o contorno fino do corpo (sem os puxadores), para a peça se ler como as geladeiras da B e da D
    x0, y0, x1, y1 = q["modulo"]
    corpo = (x0, y0, x1, y0 + (y1 - y0) * 0.905)
    CB.pintar(out, m, [(corpo, "contorno", q["contorno"], q["contorno_px"])])
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("acao", choices=("final", "doze"))
    ap.add_argument("--opcao", default="AB")
    ap.add_argument("--saida")
    a = ap.parse_args()
    fin = cv2.imread(str(FINAL))
    if a.acao == "final":
        cv2.imwrite(a.saida or str(FINAL), aplicar(fin, Mapa()))
        print("    gourmet: a geladeira inox G2 da biblioteca no módulo, a frente para a gourmet")
        return
    from PIL import Image
    for op in a.opcao:
        f = Path(str(DOZE).format(op))
        img = cv2.imread(str(f))
        M = DF.afim_12k(fin, img)
        mp = Mapa(float(np.hypot(M[0, 0], M[1, 0])), (float(M[0, 2]), float(M[1, 2])))
        mp.ref = fin
        out = aplicar(img, mp.local(img, Q["caixa"]))
        dpi = int(round(out.shape[1] / (420 / 25.4)))
        dest = a.saida.format(op) if a.saida else str(f)
        Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB)).save(dest, quality=95, subsampling=0, dpi=(dpi, dpi))
        print(f"    {Path(dest).name}")


if __name__ == "__main__":
    main()

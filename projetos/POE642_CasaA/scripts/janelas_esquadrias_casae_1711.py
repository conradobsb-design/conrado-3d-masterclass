"""As esquadrias das janelas de correr da cozinha e do serviço do Térreo da Casa E (17/11, usuário: "FALTOU AS ESQUADRIAS
DA JANELA DA COZINHA"), na final e direto nos 12K A e B.

As janelas tinham sido redesenhadas (`cozinha_servico_terreo_casae_1711.janelas`) só com o vão e as folhas em vidro
claro. Agora entram as peças de esquadria do PDF (ARQ_PAREDE, os brancos de cada vão): os marcos nas duas pontas do
vão (2,4 px, de face a face) e os montantes nas pontas de cada folha (4,8 x 3,0 px), em grafite, com o fio escuro;
os vidros de cada folha (as duas lâminas de 1,5 px) no vidro claro com o fio fino, a linha do meio entre elas.

  python3 janelas_esquadrias_casae_1711.py doze [--opcao AB]     (antes da final: a final de antes é a referência)
  python3 janelas_esquadrias_casae_1711.py final
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import correcoes_terreo_casab_1611 as CB                    # noqa: E402
import danae_foto as DF                                     # noqa: E402
from correcoes_terreo_casab_1611 import Mapa                # noqa: E402

RAIZ = AQUI.parents[1]
FINAL = RAIZ / "POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_final.png"
DOZE = RAIZ / "POE642_CasaE/entrega/POE642_CasaE_PH_Terreo_12K_opcao_{}.jpg"

# as peças do PDF (px da final), por janela: marcos, montantes, vidros
JANELAS = {
    "cozinha": {"caixa": (1650, 460, 1890, 520),
                "marcos": [(1676.3, 482.9, 1678.7, 494.9), (1859.0, 482.9, 1861.4, 494.9)],
                "montantes": [(1678.7, 482.9, 1683.5, 485.9), (1737.2, 482.9, 1742.0, 485.9),
                              (1737.2, 485.9, 1742.0, 488.9), (1795.7, 485.9, 1800.5, 488.9),
                              (1795.7, 488.9, 1800.5, 491.9), (1854.2, 488.9, 1859.0, 491.9)],
                "vidros": [(1683.5, 482.9, 1737.2, 485.9), (1742.0, 485.9, 1795.7, 488.9),
                           (1800.5, 488.9, 1854.2, 491.9)]},
    "serviço": {"caixa": (1970, 535, 2150, 585),
                "marcos": [(1992.8, 554.6, 1995.2, 563.5), (2121.7, 554.6, 2124.1, 563.5)],
                "montantes": [(1995.2, 554.6, 1999.9, 557.5), (2056.1, 554.6, 2060.8, 557.5),
                              (2056.1, 557.5, 2060.8, 560.5), (2117.0, 557.5, 2121.7, 560.5)],
                "vidros": [(1999.9, 554.6, 2056.1, 557.5), (2060.8, 557.5, 2117.0, 560.5)]},
}
COR = {"grafite": (58, 60, 64), "fio": (34, 35, 38), "fio_px": 0.35, "vidro": (226, 229, 232),
       "vidro_fio": (120, 123, 128), "vidro_fio_px": 0.3, "meio": (150, 153, 158), "meio_px": 0.3}


def janela(out, m, q, c=COR):
    pecas = []
    for r in q["vidros"]:
        x0, y0, x1, y1 = r
        ym = (y0 + y1) / 2
        pecas += [(r, "ret", c["vidro"], 0), (r, "contorno", c["vidro_fio"], c["vidro_fio_px"]),
                  ((x0, ym - c["meio_px"] / 2, x1, ym + c["meio_px"] / 2), "ret", c["meio"], 0)]
    for r in q["marcos"] + q["montantes"]:
        pecas += [(r, "ret", c["grafite"], 0), (r, "contorno", c["fio"], c["fio_px"])]
    CB.pintar(out, m, pecas)


def aplicar(img, mp):
    out = img.copy()
    for nome, q in JANELAS.items():
        m = mp.local(out, q["caixa"]) if mp.ref is not None else mp
        janela(out, m, q)
        print(f"    janela da {nome}: os marcos e os montantes em grafite, os vidros com a linha do meio")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("acao", choices=("final", "doze"))
    ap.add_argument("--opcao", default="AB")
    ap.add_argument("--entrada")
    ap.add_argument("--saida")
    a = ap.parse_args()
    fin = cv2.imread(a.entrada or str(FINAL))
    if a.acao == "final":
        cv2.imwrite(a.saida or str(FINAL), aplicar(fin, Mapa()))
        return
    from PIL import Image
    for op in a.opcao:
        f = Path(str(DOZE).format(op))
        img = cv2.imread(str(f))
        M = DF.afim_12k(fin, img)
        mp = Mapa(float(np.hypot(M[0, 0], M[1, 0])), (float(M[0, 2]), float(M[1, 2])))
        mp.ref = fin
        out = aplicar(img, mp)
        dpi = int(round(out.shape[1] / (420 / 25.4)))
        dest = a.saida.format(op) if a.saida else str(f)
        Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB)).save(dest, quality=95, subsampling=0, dpi=(dpi, dpi))
        print(f"    {Path(dest).name}")


if __name__ == "__main__":
    main()

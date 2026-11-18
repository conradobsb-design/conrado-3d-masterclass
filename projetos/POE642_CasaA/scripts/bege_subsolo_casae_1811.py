"""Subsolo da Casa E, 18/11 (usuário: "VAMOS DIMUNIR AS MANCHAS DO PISO BEGE BAHIA, IGUALMENTE IFZEMOS NAS OUTRAS
CASAS"): as manchas do Bege Bahia a 35%, a fórmula das outras casas (`pedidos_subsolo_casac_1311.bege`, como no Térreo
da E, `bege_garagem_terreo_casae_1711.bege`), pela legenda 232 do quadro: a circulação, o depósito e a casa de máquinas
de 5,83 m²; fora o WC DCE 2 (a mesma legenda, outro piso).

Na final é o passo `bege_manchas` de `pedidos_subsolo_casae_1811` (antes dos rótulos), para as rodadas seguintes; nos
12K A (Inter) e B (Kalam), direto: os campos da final de antes (o piso, o tom das manchas, as arestas) pelo afim global
com o desvio local mediano de caixas com desenho, e a fórmula na escala do 12K, em blocos (as letras e as linhas escuras
medidas no próprio 12K).

  python3 bege_subsolo_casae_1811.py doze [--opcao AB]     (antes de refazer a final: a final de antes é a referência)
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import bege_garagem_terreo_casae_1711 as BG                 # noqa: E402
from correcoes_terreo_casab_1611 import Mapa                # noqa: E402

RAIZ = AQUI.parents[1]
FINAL = RAIZ / "POE642_CasaE/renders/POE642_CasaE_PH_Subsolo_v1_final.png"
DOZE = RAIZ / "POE642_CasaE/entrega/POE642_CasaE_PH_Subsolo_12K_opcao_{}.jpg"

BEGE_FORA = [(1855, 486, 1952, 640)]                      # o WC DCE 2 (px)
PLANTA = (850, 295, 2095, 1115)                           # a legenda 232 fora da planta (os desenhos do quadro) não entra
# caixas com desenho para o desvio local do afim no 12K: a escada, as portas do depósito, o DCE e o WC DCE 2, o elevador
CAIXAS_AFIM = [(1140, 400, 1470, 495), (1755, 340, 1835, 455), (1640, 480, 1960, 640), (1945, 715, 2055, 820)]


def campos(Q, img):
    guarda = BG.BEGE_FORA, BG._fora_moveis, Q.chapada
    BG.BEGE_FORA, BG._fora_moveis = BEGE_FORA, (lambda: [])
    ch = Q.chapada.copy()
    x0, y0, x1, y1 = PLANTA
    fora = np.ones(ch.shape[:2], bool)
    fora[y0:y1, x0:x1] = False
    ch[fora & np.all(ch == 232, axis=2)] = (0, 0, 1)
    Q.chapada = ch
    try:
        return BG.campos(Q, img)
    finally:
        BG.BEGE_FORA, BG._fora_moveis, Q.chapada = guarda


def bege_manchas(Q, img):
    """O passo da final (`pedidos_subsolo_casae_1811`)."""
    out = img.copy()
    BG.bege(out, Mapa(), campos(Q, img))
    return out


def main():
    import danae_foto as DF
    import final3840_casae as FE
    from PIL import Image
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("acao", choices=("doze",))
    ap.add_argument("--opcao", default="AB")
    ap.add_argument("--ref", help="a final de antes (a referência dos 12K)")
    ap.add_argument("--saida")
    a = ap.parse_args()
    fin = cv2.imread(a.ref or str(FINAL))
    cp = campos(FE.QuadroE("Subsolo"), fin)
    guarda = BG.CAIXAS_AFIM
    BG.CAIXAS_AFIM = CAIXAS_AFIM
    try:
        for op in a.opcao:
            f = Path(str(DOZE).format(op))
            img = cv2.imread(str(f))
            M = DF.afim_12k(fin, img)
            mp = Mapa(float(np.hypot(M[0, 0], M[1, 0])), (float(M[0, 2]), float(M[1, 2])))
            mp.ref = fin
            out = img.copy()
            BG.bege(out, mp, cp)
            dpi = int(round(out.shape[1] / (420 / 25.4)))
            dest = a.saida.format(op) if a.saida else str(f)
            Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB)).save(dest, quality=95, subsampling=0,
                                                                       dpi=(dpi, dpi))
            print(f"    {Path(dest).name}")
    finally:
        BG.CAIXAS_AFIM = guarda


if __name__ == "__main__":
    main()

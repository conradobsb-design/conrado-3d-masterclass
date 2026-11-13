"""As peças geradas no Higgsfield para o Térreo da Casa B (13/11), recortadas para a biblioteca.

A biblioteca não tinha geladeira, recamier, banco estofado de closet nem cortina; o usuário pediu ("NÃO TEMOS
MOBILIÁRIO DE REFRIGERADOR?" / "OK. GERE NO HIGGSFIELDS"; "TAMBÉM QUERIA UM MOBILIARIO PARA CORTINAS GERADO NO
HIGGSFIELD"; "PRECISO TROCAR OS RECAMIERS DA SUITE MASTER TAMBÉM", depois "GOSTO DO RECAMIER COM MAIS GLAMOUR"; "NO
CLOSET MASTER TEM UM BANCO ESTOFADO QUE PRECISA SER REPRESENTADO COMO BANCO ESTOFADO") e escolheu, entre 4 variantes de
cada (gpt_image_2, vista de cima, fundo branco), "G2, R7, B1, C4":
  - geladeira: job 9f2879f5 (inox escovado, os puxadores na frente, embaixo no PNG);
  - recamier: o R7 (job 66656fd6, mais comprido que o PDF: "CUIDADO COM A PROPORÇÃO DO RECAMIER E MESA LATERAL") trocado
    a pedido ("PODEMOS USAR OUTRO MODELO DE RECAMIER QUE TENHA AS MESMAS DIMENSÕES DO ORIGINAL?") pelo R11, gerado na
    medida do original, 0,70 x 1,50 m (job 1c8a44b5: veludo champanhe em gomos, o encosto curvo em L, o rolo e o filete
    de latão);
  - banco estofado do closet: job 85a49f2f (linho greige, capitonê em grade);
  - cortina: job c42ba4d3 (linho off-white em ondas, o trilho grafite em cima).
O fundo branco ligado à borda sai (o alfa pela distância ao branco, só na beira; a cor sem o branco misturado), e o PNG
é recortado ao alfa:
  python3 pecas_higgsfield_1311.py <pasta com as saídas do Higgsfield>
grava `PECAS` na biblioteca (`biblioteca-objetos/...`).
"""

import sys
from pathlib import Path

import cv2
import numpy as np

BIB = Path(__file__).resolve().parent.parent / "biblioteca-objetos"
PECAS = {"9f2879f5": "02-terreo/cozinha/geladeira-inox.png",
         "1c8a44b5": "03-primeiro-pavimento/suite-master/recamier-veludo-champanhe.png",
         "85a49f2f": "03-primeiro-pavimento/closet-master/banco-estofado-capitone.png",
         "c42ba4d3": "02-terreo/cortinas/cortina-linho-onda.png"}


def recorte(im):
    """(BGRA): o fundo branco ligado à borda sai; na beira, o alfa pela distância ao branco e a cor sem o branco."""
    im = im.astype(np.float32)
    d = 255 - im.min(axis=2)
    bg = (d <= 8).astype(np.uint8)
    _, lab = cv2.connectedComponents(bg)
    borda = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    fundo = np.isin(lab, list(borda))
    a = (~fundo).astype(np.float32)
    perto = cv2.dilate(fundo.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool) & ~fundo
    a[perto] = np.clip((d[perto] - 4) / 22, 0, 1)
    m = a > 0.02
    cor = im.copy()
    cor[m] = np.clip((im[m] - (1 - a[m, None]) * 255) / a[m, None], 0, 255)
    cor[~m] = 0
    P = np.dstack([cor, a * 255])
    ys, xs = np.nonzero(a > 0.02)
    return np.clip(np.round(P[ys.min():ys.max() + 1, xs.min():xs.max() + 1]), 0, 255).astype(np.uint8)


def main():
    pasta = Path(sys.argv[1])
    for job, rel in PECAS.items():
        arq = next(pasta.glob(f"*{job}*.png"))
        P = recorte(cv2.imread(str(arq)))
        dest = BIB / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(dest), P)
        print(f"    {rel}: {P.shape[1]} x {P.shape[0]} (job {job})")


if __name__ == "__main__":
    main()

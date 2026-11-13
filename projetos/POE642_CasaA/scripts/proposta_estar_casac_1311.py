"""As opções para o estar da Casa C (o conjunto da esquerda; 13/11, "GERE OPÇÕES PARA O ESTAR DA CASA C", "ANTES DO 12K,
FAÇA AS OPÇÕES PARA O ESTAR").

O conjunto da esquerda do estar ainda era o do render (as 2 poltronas, o sofá de 3 lugares, o de 2 lugares e meio, as 2
mesas de centro). Três estilos gerados em 2K no Higgsfield (gpt_image_2, o fundo tirado; em
`biblioteca-objetos/02-terreo/sala-de-estar/propostas-estar-c/`), cada um com o sofá de 3, o de 2,5, a poltrona e a mesa
de centro:
- **E1:** linho off-white, poltronas de couro caramelo com madeira, mesas de freijó.
- **E2:** linho greige com almofadas de veludo oliva, poltronas de veludo oliva arredondadas, mesas de travertino.
- **E3:** bouclé areia com almofadas terracota, poltronas de linho terracota, mesas de nogueira escura.
Cada peça no retângulo do PDF (o giro pela frente de cada uma: as poltronas viradas para a direita, o sofá de 3 para
cima, o de 2,5 para a esquerda), sem deformar (a maior escala que cabe), com a sombra curta; as de antes saem (o tapete
ou o travertino de uma amostra, no tom do entorno); as mesinhas seixo nas pontas do sofá ficam.

  python3 proposta_estar_casac_1311.py              (a folha da proposta)
  python3 proposta_estar_casac_1311.py --aplicar E1 (aplica na final)
"""

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import biblioteca_terreo_casaa_1211 as BT        # noqa: E402
import biblioteca_1pav_casaa_1211 as B1          # noqa: E402
import paisagismo_terreo_casab_1311 as PJ        # noqa: E402

PX_M = B1.PX_M
BIB = AQUI.parent / "biblioteca-objetos" / "02-terreo" / "sala-de-estar" / "propostas-estar-c"
CASA_C = AQUI.parents[1] / "POE642_CasaC"
R = CASA_C / "renders"
FINAL = R / "POE642_CasaC_PH_Terreo_final_rotulos.png"
NOMES = {"E1": "E1: linho off-white, poltronas de couro caramelo, mesas de freijo",
         "E2": "E2: linho greige e veludo oliva, mesas de travertino",
         "E3": "E3: boucle areia e linho terracota, mesas de nogueira"}
# (peça, retângulo do PDF (px), giro): o giro põe a frente do PNG (embaixo) para o lado certo
PECAS = [("poltrona", (1685.0, 1362.4, 1742.0, 1430.1), 90.0, "movel"),
         ("poltrona", (1685.0, 1452.0, 1742.0, 1519.6), 90.0, "movel"),
         ("sofa3", (1758.0, 1532.5, 1966.9, 1598.2), 180.0, "movel"),
         ("sofa2", (1979.4, 1376.5, 2033.2, 1513.8), -90.0, "movel"),
         ("mesa", (1796.6, 1401.1, 1916.0, 1436.9), 0.0, "mesa"),
         ("mesa", (1796.6, 1442.9, 1916.0, 1478.7), 0.0, "mesa")]
TAPETE = (1713.3, 1342.2, 2011.9, 1551.2)
AMOSTRAS = {"tapete": (1758, 1490, 1798, 1526), "travertino": (1780, 1604, 1940, 1632)}
# a caixa do conjunto (o tapete de antes, as peças e as sombras): refeita inteira; as mesinhas seixo ficam
CAIXA = (1680, 1336, 2042, 1606)
SEIXOS = [(1718, 1532, 1750, 1588), (1974, 1528, 2008, 1584)]
FOLGA_PX = 3
RECORTE = (1650, 1310, 2070, 1640)


def ler(estilo, peca):
    return cv2.imread(str(BIB / f"{estilo.lower()}_{peca}.png"), cv2.IMREAD_UNCHANGED).astype(np.float32)


def aplicar(img, estilo, q_esticar=1.25):
    """O conjunto da esquerda refeito: o travertino em toda a caixa do conjunto (fora as mesinhas seixo), o tapete inteiro
    no retângulo do PDF (o de antes passava dele à esquerda, em degrau), as peças por cima."""
    out = img.copy()
    H, W = out.shape[:2]
    bx0, by0, bx1, by1 = CAIXA
    caixa = np.zeros((H, W), bool)
    caixa[by0:by1, bx0:bx1] = True
    seixo = np.zeros((H, W), bool)
    for x0, y0, x1, y1 in SEIXOS:
        seixo[y0:y1, x0:x1] = True
    I = img.astype(np.int16)
    seixo &= (I[..., 2] - I[..., 0]) > 35                 # só o marrom das mesinhas
    seixo = cv2.dilate(seixo.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    sel = caixa & ~seixo
    x0, y0, x1, y1 = AMOSTRAS["travertino"]
    out = PJ.preencher(out, sel, img[y0:y1, x0:x1].copy(), anel_px=6, nao=caixa)
    # o tapete: a lã da amostra (repetida sem emenda) no tom dela, a borda suave e a sombra rente
    import materiais_terreo_casac_1311 as MT
    tx0, ty0, tx1, ty1 = TAPETE
    X0, Y0, X1, Y1 = int(tx0) - 6, int(ty0) - 6, int(np.ceil(tx1)) + 6, int(np.ceil(ty1)) + 6
    ax0, ay0, ax1, ay1 = AMOSTRAS["tapete"]
    T = MT.sem_emenda(img[ay0:ay1, ax0:ax1].astype(np.float32), Y1 - Y0, X1 - X0)
    xs = np.arange(X0, X1) + 0.5
    ys = np.arange(Y0, Y1) + 0.5
    cx = np.clip(np.minimum(xs + 0.5, tx1) - np.maximum(xs - 0.5, tx0), 0, 1)
    cy = np.clip(np.minimum(ys + 0.5, ty1) - np.maximum(ys - 0.5, ty0), 0, 1)
    a = np.outer(cy, cx).astype(np.float32)
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    for sb in BT.SOMBRAS["tapete"]:
        sh = cv2.GaussianBlur(a, (0, 0), max(0.3, sb["sig"] * PX_M))
        Ms = np.float32([[1, 0, sb["dx"] * PX_M], [0, 1, sb["dy"] * PX_M]])
        sh = cv2.warpAffine(sh, Ms, (sh.shape[1], sh.shape[0]), flags=cv2.INTER_LINEAR, borderValue=0)
        reg *= (1 - sb["forca"] * sh * (1 - a))[..., None]
    reg = reg * (1 - a[..., None]) + T * a[..., None]
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    out[seixo] = img[seixo]
    for peca, (x0, y0, x1, y1), giro, sombra in PECAS:
        P = ler(estilo, peca)
        h, w = P.shape[:2]
        L, D = (x1 - x0, y1 - y0) if giro in (0.0, 180.0) else (y1 - y0, x1 - x0)
        # na medida do PDF; se a proporção do PNG for outra, cada lado estica no máximo `q_esticar` (o resto fica
        # menor que o PDF, sem deformar mais)
        kL, kD = L / w, D / h
        k0 = min(kL, kD)
        kL, kD = min(kL, k0 * q_esticar), min(kD, k0 * q_esticar)
        o = BT.pousar(out.astype(np.float32), P, (x0 + x1) / 2, (y0 + y1) / 2, w * kL, h * kD, giro,
                      BT.SOMBRAS[sombra], PX_M)
        out = np.clip(np.round(o), 0, 255).astype(np.uint8)
    out[seixo] = img[seixo]
    return out


def folha(img):
    x0, y0, x1, y1 = RECORTE
    k = 2.0
    blocos = [("HOJE (o render)", img)] + [(NOMES[e], aplicar(img, e)) for e in ("E1", "E2", "E3")]
    ims = []
    for t, im in blocos:
        c = cv2.resize(im[y0:y1, x0:x1], None, fx=k, fy=k, interpolation=cv2.INTER_CUBIC)
        topo = np.full((44, c.shape[1], 3), 255, np.uint8)
        cv2.putText(topo, t, (8, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (40, 40, 40), 2, cv2.LINE_AA)
        ims.append(np.vstack([topo, c]))
    g = 14
    linha = lambda a, b: np.hstack([a, np.full((a.shape[0], g, 3), 255, np.uint8), b])
    f = np.vstack([linha(ims[0], ims[1]), np.full((g, ims[0].shape[1] * 2 + g, 3), 255, np.uint8), linha(ims[2], ims[3])])
    topo = np.full((56, f.shape[1], 3), 255, np.uint8)
    cv2.putText(topo, "POE 642 - Casa C - Terreo - estar (o conjunto da esquerda): opcoes para escolher", (10, 38),
                cv2.FONT_HERSHEY_SIMPLEX, 0.85, (30, 30, 30), 2, cv2.LINE_AA)
    arq = R / "POE642_CasaC_PH_Terreo_1311_proposta_estar.jpg"
    cv2.imwrite(str(arq), np.vstack([topo, f]), [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"    {arq.name} {f.shape[1]}x{f.shape[0] + 56}")


def antes_depois(antes, depois, estilo):
    """O recorte do estar (`RECORTE`), antes e depois, lado a lado."""
    x0, y0, x1, y1 = RECORTE
    k = 2.0
    a = cv2.resize(antes[y0:y1, x0:x1], None, fx=k, fy=k, interpolation=cv2.INTER_CUBIC)
    b = cv2.resize(depois[y0:y1, x0:x1], None, fx=k, fy=k, interpolation=cv2.INTER_CUBIC)
    j = np.hstack([a, np.full((a.shape[0], 16, 3), 255, np.uint8), b])
    t = np.full((44, j.shape[1], 3), 255, np.uint8)
    cv2.putText(t, f"ANTES | DEPOIS ({NOMES[estilo]})", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (40, 40, 40), 2,
                cv2.LINE_AA)
    arq = R / f"POE642_CasaC_PH_Terreo_1311_estar_{estilo}_antes_depois.jpg"
    cv2.imwrite(str(arq), np.vstack([t, j]), [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"    {arq.name}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--aplicar", choices=["E1", "E2", "E3"])
    ap.add_argument("--antes")
    a = ap.parse_args()
    img = cv2.imread(a.antes or str(FINAL))
    if a.aplicar:
        depois = aplicar(img, a.aplicar)
        cv2.imwrite(str(FINAL), depois)
        print(f"    {FINAL.name}: o estar {a.aplicar}")
        antes_depois(img, depois, a.aplicar)
        return
    folha(img)


if __name__ == "__main__":
    main()

"""Casa A Térreo, revisão do usuário de 25/11 (com os recortes do 12K).

1. "corrigir falha no muro": a pecinha clara (um trinco/portão do render) no muro de baixo, onde o caminho de pedra
   portuguesa encosta, sai — o muro e o caminho logo ao lado entram no lugar.
2. "remover os traços pretos da área de jardim": no JARDIM (4,79 m²) junto ao WC e ao banho varanda, a linha de projeção
   tracejada do PDF (DOC_LINHAS, y = 1643) virou traços pretos na borda da grama, sob as janelas: sai (a grama logo
   abaixo entra no lugar).
3. "completar a folha de box até a parede": o box do BANHO VARANDA vai de parede a parede no PDF (o trilho de 1618,2 a
   1696,4); a folha de vidro do render parava em ~1684: o vidro (a mesma linha clara: a linha menos o piso dela, nas
   mesmas colunas) segue até o revestimento da parede, somada ao piso de lá.
4. "refazer soleira e portas da área de gás": a soleira (a barra branca grossa, com a ponta inclinada passando do vão)
   vira um retângulo limpo no vão do PDF (1706,6–1769,3 x 1634,1–1643,0), no tom claro de hoje e com as arestas finas;
   as duas portas (abertas a 90°, como no PDF: 2,4 x 26,7 px a partir da soleira) são redesenhadas em chapa (o perfil
   cinza claro) com a linha fina, quina a quina com a soleira; o desenho antigo sai (o piso de pedra ao lado), e a
   linha de projeção tracejada sob a soleira também.
5. "refazer portas de correr da área de serviço": o vão (1778,2–1909,6 x 1631,1–1643,0) recebe a mesma soleira e as
   duas folhas do PDF são desenhadas no padrão (perfil cinza claro, vidro claro, linha fina): a da esquerda no trilho de
   dentro, a da direita no de fora.

Final, prancha e 12K A e B (cada item pelo registro local).

  python3 terreo_casaa_2511.py
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
sys.path.insert(0, str(Path(__file__).resolve().parent))
import esquadrias_pretas_1911 as EP  # noqa: E402
import vidros_claros_1911 as VC  # noqa: E402
from subsolo_casaa_juncao_portas_2511 import copiar  # noqa: E402

PLANTA = "A_Terreo"

MURO = [((2843.5, 1921.5, 2869.5, 1941.5), (-32.0, 0.0))]
JARDIM = [((1480.0, 1643.1, 1696.0, 1646.4), (0.0, 4.5))]
BOX = dict(linhas=(1563.4, 1568.2), ref=(1652.0, 1668.0), fim=1696.4)
SOLEIRA_GAS = (1706.6, 1634.1, 1769.3, 1643.0)
GAS_PAREDE = [(1769.3, 1633.0, 1772.5, 1643.0)]          # a ponta da barra antiga sobre a parede: parede
GAS_APAGA = [((1706.9, 1643.2, 1712.6, 1673.5), (0.0, 30.0)),
             ((1763.2, 1643.2, 1769.0, 1673.5), (0.0, 30.0)),
             ((1712.4, 1643.1, 1763.4, 1645.8), (0.0, 4.5))]     # a linha de projeção tracejada sob a soleira
GAS_FOLHAS = [[(1708.2, 1643.0, 1710.6, 1669.7)], [(1765.2, 1643.0, 1767.6, 1669.7)]]
SOLEIRA_CORRER = (1778.2, 1631.1, 1909.6, 1643.0)
CORRER_FOLHAS = [[(1780.6, 1637.1, 1846.3, 1640.0)], [(1841.5, 1640.0, 1907.2, 1643.0)]]

ITENS = {   # caixa (px da final) do registro local de cada item
    "muro": (2830.0, 1915.0, 2885.0, 1945.0),
    "jardim": (1478.0, 1630.0, 1712.0, 1660.0),
    "box": (1612.0, 1540.0, 1702.0, 1580.0),
    "gas": (1700.0, 1628.0, 1776.0, 1676.0),
    "correr": (1768.0, 1626.0, 1914.0, 1650.0),
}


def P_(escala, origem):
    return lambda x, y: (int(round((x - origem[0]) * escala)), int(round((y - origem[1]) * escala)))


def tom_soleira(img, escala, origem):
    """O tom claro da soleira de hoje (o miolo da barra do GÁS)."""
    P = P_(escala, origem)
    a0, b0 = P(1715.0, 1637.0)
    a1, b1 = P(1760.0, 1641.0)
    return np.median(img[b0:b1, a0:a1].reshape(-1, 3).astype(np.float32), axis=0)


def soleira(img, caixa, cor, escala, origem):
    """Um retângulo limpo no tom `cor`, com a aresta fina (um pouco mais escura) em cima e embaixo."""
    x0, y0, x1, y1 = caixa
    ss = 4
    A0, B0 = int(np.floor((x0 - origem[0]) * escala)) - 1, int(np.floor((y0 - origem[1]) * escala)) - 1
    A1, B1 = int(np.ceil((x1 - origem[0]) * escala)) + 1, int(np.ceil((y1 - origem[1]) * escala)) + 1
    H, W = B1 - B0, A1 - A0
    m = np.zeros((H * ss, W * ss), np.uint8)
    pa = lambda x, y: (int(round(((x - origem[0]) * escala - A0) * ss)), int(round(((y - origem[1]) * escala - B0) * ss)))
    cv2.rectangle(m, pa(x0, y0), tuple(v - 1 for v in pa(x1, y1)), 255, -1)
    a = cv2.resize(m, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    e = max(1, int(round(0.3 * escala * ss)))
    borda = np.zeros_like(m)
    (u0, v0), (u1, v1) = pa(x0, y0), pa(x1, y1)
    borda[v0:v0 + e, u0:u1] = 255
    borda[v1 - e:v1, u0:u1] = 255
    b = cv2.resize(borda, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    reg = img[B0:B1, A0:A1].astype(np.float32)
    novo = np.broadcast_to(cor[None, None], reg.shape) * (1 - 0.18 * b[..., None])
    img[B0:B1, A0:A1] = np.clip(reg * (1 - a[..., None]) + novo * a[..., None], 0, 255).astype(np.uint8)
    return img


def parede(img, caixas, escala, origem):
    P = P_(escala, origem)
    for x0, y0, x1, y1 in caixas:
        A0, B0 = P(x0, y0)
        A1, B1 = P(x1, y1)
        # o cinza da parede logo à direita
        c0, d0 = P(x1 + 1.0, y0)
        c1, d1 = P(x1 + 3.0, y1)
        cor = np.median(img[d0:d1, c0:c1].reshape(-1, 3), axis=0)
        reg = img[B0:B1, A0:A1]
        claro = reg.astype(np.float32).mean(2) > float(cor.mean()) + 30
        reg[claro] = cor
    return img


def box(img, escala, origem):
    """O vidro do box (a linha clara do render) segue até a parede: a contribuição da linha (a linha menos o piso, numa
    faixa dela) é somada ao piso das colunas onde ela falta."""
    P = P_(escala, origem)
    _, B0 = P(0, BOX["linhas"][0])
    _, B1 = P(0, BOX["linhas"][1])
    r0, _ = P(BOX["ref"][0], 0)
    r1, _ = P(BOX["ref"][1], 0)
    fim, _ = P(BOX["fim"], 0)
    linha = img[B0:B1, r0:r1].astype(np.float32).mean(1)
    # o piso sob a linha, nas mesmas colunas: entre a linha de cima e a de baixo da faixa (fora da linha)
    cima = img[B0 - 1, r0:r1].astype(np.float32).mean(0)
    baixo = img[B1, r0:r1].astype(np.float32).mean(0)
    t = np.linspace(0, 1, B1 - B0, dtype=np.float32)[:, None]
    piso_ref = cima[None] * (1 - t) + baixo[None] * t
    delta = linha - piso_ref
    dd = float((delta ** 2).sum()) or 1.0

    def forca(c):
        """quanto da linha já há na coluna `c` (contra o piso dela, entre a linha de cima e a de baixo)"""
        col = img[B0:B1, c].astype(np.float32)
        base = img[B0 - 1, c].astype(np.float32)[None] * (1 - t) + img[B1, c].astype(np.float32)[None] * t
        return col, float(np.clip(((col - base) * delta).sum() / dd, 0, 1))
    # onde a linha acaba hoje
    x = r1
    while x < fim and forca(x)[1] >= 0.5:
        x += 1
    ini = max(x - 1, r1)
    for c in range(ini, fim):
        col, f = forca(c)
        img[B0:B1, c] = np.clip(col + (1 - f) * delta, 0, 255).astype(np.uint8)
    print(f"      box: o vidro acabava em {origem[0] + ini / escala:.1f}; segue até {BOX['fim']}")
    return img


def item(img, nome, escala=1.0, origem=(0.0, 0.0)):
    if nome == "muro":
        for c, d in MURO:
            img = copiar(img, c, d, escala, origem)
    elif nome == "jardim":
        for c, d in JARDIM:
            img = copiar(img, c, d, escala, origem)
    elif nome == "box":
        img = box(img, escala, origem)
    elif nome in ("gas", "correr"):
        cor = tom_soleira(img, escala, origem) if nome == "gas" else TOM[0]
        traco = 0.5 if escala <= 1.5 else min(0.5, EP.TRACO_12K / escala)
        if nome == "gas":
            TOM[0] = cor
            for c, d in GAS_APAGA:
                img = copiar(img, c, d, escala, origem)
            img = parede(img, GAS_PAREDE, escala, origem)
            img = soleira(img, SOLEIRA_GAS, cor, escala, origem)
            vidro = VC.VIDRO
            VC.VIDRO = VC.PERFIL                               # as portas do abrigo de gás: chapa, sem vidro
            for f in GAS_FOLHAS:
                img = VC.redesenhar(img, f, escala=escala, origem=origem, traco=traco, inpaint=False)
            VC.VIDRO = vidro
        else:
            img = soleira(img, SOLEIRA_CORRER, cor, escala, origem)
            for f in CORRER_FOLHAS:
                img = VC.redesenhar(img, f, escala=escala, origem=origem, traco=traco, inpaint=False)
    return img


TOM = [None]


def main():
    c, pav = PLANTA.split("_")
    base = cv2.imread(str(EP.PROJ / EP.PLANTAS[PLANTA][0]))
    for f in EP.PLANTAS[PLANTA]:
        im = cv2.imread(str(EP.PROJ / f))
        for nome in ITENS:
            im = item(im, nome)
        cv2.imwrite(str(EP.PROJ / f), im)
        if f == EP.PLANTAS[PLANTA][0]:
            novo = im
    pf = EP.PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_entrega.png"
    pr = cv2.imread(str(pf))
    pr[:2160] = novo
    cv2.imwrite(str(pf), pr)
    dz = json.loads((EP.PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[PLANTA]
    for op in "AB":
        rel = EP.PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_12K_opcao_{op}.jpg"
        pil = Image.open(rel)
        dpi = pil.info.get("dpi", (743, 743))
        im = cv2.cvtColor(np.array(pil.convert("RGB")), cv2.COLOR_RGB2BGR)
        del pil
        cinza = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        for nome, (x0, y0, x1, y1) in ITENS.items():
            mapa, cc = EP.registro_12k(base, cinza, dz, (int(x0) - 80, int(y0) - 80, int(x1) + 80, int(y1) + 80))
            A, B = mapa(x0, y0)
            sx = (mapa(x0 + 1000.0, y0)[0] - A) / 1000.0
            im = item(im, nome, sx, (x0 - A / sx, y0 - B / sx))
            print(f"   {op}: {nome} (registro {cc:.3f}, escala {sx:.3f})")
        Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).save(rel, quality=95, subsampling=0, dpi=dpi)
        del im, cinza


if __name__ == "__main__":
    main()

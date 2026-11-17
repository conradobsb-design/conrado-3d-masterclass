"""As bancadas de Dekton Danae sem as falhas da troca automática, planta a planta (16/11; Térreo da Casa A, usuário:
"CORRIJA A BANCADA DA COZINHA REMOVENDO FALHAS, AINDA NA CASA A"; Térreo da Casa B: "VAMOS CORRIGIR AS FALHAS NAS
BANCADAS DE DEKTON DO TERREO DA CASA B").

A troca pela foto oficial (`danae_foto.trocar`, commit 949e551) achou a pedra pelo desenho de antes e deixou três
falhas no Térreo da Casa A:
  - a ilha: a pedra entrou no assento das 3 banquetas (o creme liso delas passou no teste do tom);
  - a bancada da pia: a "luz de antes" (o anel molhado do desenho, mais escuro) ficou como um retângulo escuro, de
    borda irregular, em volta e abaixo das cubas; no 12K, o granulado do desenho ficou em volta das cubas;
  - a bancada em L do serviço: só a perna da esquerda virou foto; a faixa das cubas ficou com o Danae desenhado;
  e, nas três, pontinhos claros soltos (os grãos claros da chapa, na escala da planta, liam como sujeira).
No Térreo da Casa B, as mesmas falhas: o L da cozinha só com a metade esquerda da faixa das cubas na foto (entre as
cubas, à direita delas e a perna do L no desenho antigo, com a emenda reta), a bancada dos tanques só acima das cubas,
um resto do desenho junto ao cooktop da ilha e os pontinhos claros (também na bancada da parede do serviço).

Aqui as bancadas são refeitas pela geometria delas (`BANCADAS`, px da final de 3840, medidas nos perfis da pedra), sem
depender da detecção: em cada janela (`JANELA`) volta a imagem de antes da troca (as banquetas e o resto voltam
inteiros); dentro do retângulo da bancada, a foto da chapa (`danae_foto.textura`, os veios no comprido, sem os
pontinhos: `sem_pontinhos`) numa luz só; as peças por cima (cubas com as torneiras, o cooktop) ficam, achadas na imagem
de antes pela cor (o inox neutro, o cooktop escuro; a pedra é quente), em componentes grandes (a caixa da cuba e a
torneira presa nela). Na final e direto nos
12K entregues (opções A e B, a partir dos 12K de antes da troca; o afim por SIFT de `danae_foto.afim_12k`).

  python3 danae_bancadas_1611.py final <planta> --antes <final de antes da troca> [--saida <png>]
  python3 danae_bancadas_1611.py doze  <planta> --antes <final de antes da troca> --doze_antes <12K de antes, {}=A|B>

  planta: A_Terreo, B_Terreo, D_Terreo (as chaves de `BANCADAS`; as finais e os 12K em `danae_foto.PLANTAS` e `DOZE_K`)
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
from scipy import ndimage

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import danae_foto as DF                          # noqa: E402

# os retângulos de pedra de cada bancada (x0, y0, x1, y1, px da final, fim exclusivo) e a janela que volta de antes
BANCADAS = {
    "A_Terreo": {
        "ilha da cozinha": {"rets": [(1940, 1247, 2047, 1317)], "janela": (1922, 1222, 2066, 1334), "semente": 11},
        "bancada da pia": {"rets": [(2117, 1232, 2150, 1520)], "janela": (2104, 1218, 2163, 1532), "semente": 12},
        "bancada do serviço (L)": {"rets": [(1708, 1453, 1739, 1541), (1708, 1453, 1826, 1491)],
                                    "janela": (1698, 1444, 1834, 1550), "semente": 13}},
    "B_Terreo": {
        "ilha da cozinha": {"rets": [(1645, 1394, 1714, 1564)], "janela": (1636, 1385, 1723, 1573), "semente": 21},
        # a janela do L em dois retângulos (um só pegava o pé da ilha e o devolvia ao desenho antigo)
        "bancada das cubas da cozinha (L)": {"rets": [(1552, 1632, 1821, 1671), (1787, 1544, 1821, 1671)],
                                             "janela": [(1544, 1624, 1828, 1676), (1779, 1538, 1828, 1676)],
                                             "semente": 22},
        # (17/11, usuário: "ENTRE A PAREDE E A BANCADA TEM UM ERRO") a pedra até a face da parede (a tira cinza do PDF,
        # x 2051,9 a 2054,3, lia como um vão), sem achar peças nela
        "bancada da parede do serviço": {"rets": [(2052, 1372, 2081, 1487)], "janela": (2045, 1363, 2090, 1496),
                                         "semente": 23, "pecas": False},
        "bancada dos tanques": {"rets": [(2200, 1463, 2239, 1562)], "janela": (2191, 1449, 2246, 1570),
                                "semente": 24}},
    # (17/11, usuário: "SIM, CONFIRA AS BANCADAS DA CASA D") as torneiras esmaecidas, a faixa do granulado antigo sob as
    # cubas da pia e os pontinhos claros da ilha
    "D_Terreo": {
        "bancada da pia da cozinha": {"rets": [(1814, 373, 2039, 411)], "janela": (1808, 372, 2045, 416),
                                      "semente": 31},
        "ilha da cozinha": {"rets": [(1879, 481, 2026, 548)], "janela": (1872, 474, 2033, 554), "semente": 32},
        "bancada da área de serviço": {"rets": [(2287, 373, 2458, 411)], "janela": (2285, 372, 2462, 416),
                                       "semente": 33}},
}
NEUTRO = 12.0           # R - B abaixo disso não é pedra (o inox, o branco da borda das cubas)
PECA_MIN = 120          # px da final: o que não é pedra e é maior que isso é peça (cuba, torneira, cooktop)
PONTINHO = 9.0          # a luz acima da mediana local que vira pontinho (sai)


def sem_pontinhos(T, esc=1.0):
    """A chapa sem os grãos claros soltos: o que passa `PONTINHO` da mediana em volta volta à mediana."""
    k = max(3, int(round(3 * esc)) | 1)
    med = cv2.medianBlur(np.clip(T, 0, 255).astype(np.uint8), k).astype(np.float32)
    claro = (T.mean(axis=2) - med.mean(axis=2)) > PONTINHO
    claro = cv2.dilate(claro.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    return np.where(claro[..., None], med, T)


def pecas(antes, ret, esc=1.0):
    """As peças por cima da pedra no retângulo (na imagem de antes): o que não é pedra, em componentes grandes; de cada
    um, a caixa do miolo (a cuba sem a torneira, aberta) e o próprio componente (a torneira)."""
    x0, y0, x1, y1 = ret
    sub = cv2.GaussianBlur(antes[y0:y1, x0:x1].astype(np.float32), (0, 0), 0.6 * esc)
    # a pedra é quente (no desenho, o R ~28 acima do B, também no molhado mais escuro); o inox das cubas e das
    # torneiras é neutro, o cooktop é escuro
    lum = sub.mean(axis=2)
    nao = ((sub[..., 2] - sub[..., 0]) < NEUTRO) | (lum < 95) | (lum > 236)
    nao = cv2.morphologyEx(nao.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    nao = ndimage.binary_fill_holes(nao)
    lab, n = ndimage.label(nao)
    out = np.zeros(nao.shape, bool)
    for i in range(1, n + 1):
        c = lab == i
        if c.sum() < PECA_MIN * esc * esc:
            continue
        k = max(3, int(round(5 * esc)))
        miolo = cv2.morphologyEx(c.astype(np.uint8), cv2.MORPH_OPEN, np.ones((k, k), np.uint8)) > 0
        if miolo.any():
            ys, xs = np.nonzero(miolo)
            c = c.copy()
            c[ys.min():ys.max() + 1, xs.min():xs.max() + 1] = True
        out |= c
    m = int(round(0.3 * esc))                 # sem folga na final (o anel do granulado antigo não fica); 1 px no 12K
    return cv2.dilate(out.astype(np.uint8), np.ones((2 * m + 1, 2 * m + 1), np.uint8)) > 0 if m else out


def refazer(img, antes, bancadas, px_m, esc=1.0, mapa=None):
    """`img` com cada bancada refeita: a janela de `antes` e, nos retângulos (fora das peças), a foto numa luz só.
    `mapa(x, y)` leva px da final ao da imagem (o 12K); sem ele, a própria final."""
    out = img.copy()
    mp = mapa or (lambda x, y: (x, y))
    H, W = img.shape[:2]
    for nome, q in bancadas.items():
        janelas = q["janela"] if isinstance(q["janela"], list) else [q["janela"]]
        for j in janelas:
            jx0, jy0 = mp(*j[:2])
            jx1, jy1 = mp(*j[2:])
            jx0, jy0 = max(int(round(jx0)), 0), max(int(round(jy0)), 0)
            jx1, jy1 = min(int(round(jx1)), W), min(int(round(jy1)), H)
            out[jy0:jy1, jx0:jx1] = antes[jy0:jy1, jx0:jx1]
        rets = []
        for r in q["rets"]:
            a0, b0 = mp(*r[:2])
            a1, b1 = mp(*r[2:])
            rets.append((int(np.ceil(a0)), int(np.ceil(b0)), int(np.floor(a1)), int(np.floor(b1))))
        X0, Y0 = min(r[0] for r in rets), min(r[1] for r in rets)
        X1, Y1 = max(r[2] for r in rets), max(r[3] for r in rets)
        pedra = np.zeros((Y1 - Y0, X1 - X0), bool)
        for x0, y0, x1, y1 in rets:
            pedra[y0 - Y0:y1 - Y0, x0 - X0:x1 - X0] = True
        if q.get("pecas", True):
            pedra &= ~pecas(antes, (X0, Y0, X1, Y1), esc)
        hh, ww = Y1 - Y0, X1 - X0
        T = sem_pontinhos(DF.textura(hh, ww, px_m, deitada=ww >= hh, semente=q["semente"]), esc)
        a_ = cv2.GaussianBlur(pedra.astype(np.float32), (0, 0), 0.45 * esc)
        a_ = np.where(pedra, np.maximum(a_, 0.6), 0.0)[..., None]
        sub = out[Y0:Y1, X0:X1].astype(np.float32)
        out[Y0:Y1, X0:X1] = np.clip(np.round(sub * (1 - a_) + T * a_), 0, 255).astype(np.uint8)
        print(f"    {nome}: {int(pedra.sum())} px de pedra refeitos ({len(rets)} retângulo(s)), as peças por cima ficam")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("acao", choices=("final", "doze"))
    ap.add_argument("planta", choices=tuple(BANCADAS))
    ap.add_argument("--antes", required=True, help="a final do Térreo de antes da troca do Danae (949e551^)")
    ap.add_argument("--doze_antes", help="o 12K de antes da troca ({} = A ou B)")
    ap.add_argument("--opcao", default="AB")
    ap.add_argument("--saida")
    a = ap.parse_args()
    antes = cv2.imread(a.antes)
    FINAL, DOZE, ban = DF.PLANTAS[a.planta], DF.DOZE_K[a.planta], BANCADAS[a.planta]
    if a.acao == "final":
        img = cv2.imread(str(FINAL))
        out = refazer(img, antes, ban, DF.PX_M)
        cv2.imwrite(a.saida or str(FINAL), out)
        return
    for op in a.opcao:
        f = Path(str(DOZE).format(op))
        doze = cv2.imread(str(f))
        doze_antes = cv2.imread(a.doze_antes.format(op))
        print(f"  {f.name}: {doze.shape[1]}x{doze.shape[0]}")
        M = DF.afim_12k(antes, doze_antes)
        s = float(np.hypot(M[0, 0], M[1, 0]))

        def mapa(x, y, M=M):
            p = M @ np.float32([x, y, 1])
            return float(p[0]), float(p[1])
        out = refazer(doze, doze_antes, ban, DF.PX_M * s, esc=s, mapa=mapa)
        # como a montagem do 12K: JPG 95 sem subamostragem de cor, 743 dpi na A3
        from PIL import Image
        dpi = int(round(out.shape[1] / (420 / 25.4)))
        Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB)).save(a.saida.format(op) if a.saida else str(f),
                                                                   quality=95, subsampling=0, dpi=(dpi, dpi))


if __name__ == "__main__":
    main()

"""Casa A Térreo: a transparência das escadas no tom da escada (25/11).

Usuário: "corrija a transparência no tom da escada. na parte que sobe e está com transparência deve ser refeita"
(a escada SOBE PARA O 1º PAVIMENTO, sobre o JARDIM de 17,46 m²) e "refazer a transparência da escada" (a escada
DESCE PARA O SUBSOLO, junto ao spa).

- Escada do jardim: depois do corte (o resto do 1º lance, o patamar e o 2º lance) aparecia a grama com as linhas dos
  degraus. Passa ao tom da escada: o tom dos degraus cheios (a mediana) com o desenho deles por cima, transparente
  (`VISTA`, a regra da escada principal da Casa E e da escada do Subsolo da Casa A), e um leve da grama por baixo
  (`FUNDO`, desfocada, sem as linhas antigas). O desenho é o perfil de uma faixa limpa dos degraus cheios (sem a seta
  e a descrição: a mediana coluna a coluna), repetido no passo dos degraus do PDF (17,9 px da final): as quinas caem
  nos degraus do PDF e nada se repete na vertical. No patamar, o miolo de um degrau (sem quinas).
- Escada do Subsolo: os degraus depois da diagonal estavam brancos. Passam ao mesmo tratamento, com o desenho do 1º
  degrau cheio (o miolo) e uma quina fina e suave em cada degrau, no passo do PDF, sem o branco por baixo; a borda
  branca de cima e de baixo também.

Final (e a manuscrita), prancha e 12K A e B (registro local).

  python3 escadas_terreo_casaa_2511.py
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

PLANTA = "A_Terreo"
VISTA = 0.55          # o desenho dos degraus por cima do tom
FUNDO = 0.15          # o que aparece por baixo (transparência)
PASSO = 17.9          # o passo dos degraus no PDF (px da final)

ESCADAS = {
    "jardim": dict(
        caixa=(2255.9, 914.6, 2488.7, 1081.8),
        # a parte transparente: a caixa (sem o contorno claro) menos o 1º lance até o corte (a diagonal do PDF, com o
        # símbolo de quebra) e menos o jardim entre os lances
        vazio=[[(2363.1, 915.4), (2487.9, 915.4), (2487.9, 1081.0), (2256.7, 1081.0), (2256.7, 1011.8),
                (2418.6, 1011.8), (2418.6, 985.4), (2399.2, 985.4), (2383.3, 954.4), (2374.3, 954.4),
                (2388.2, 946.4), (2379.3, 946.4)]],
        faixa=(2255.9, 916.5, 2363.4, 933.0),             # degraus cheios limpos (acima da seta e da descrição)
        patamar=(2417.1, 2488.7),                         # sem quinas
        verde=(2366.0, 936.0, 2396.0, 962.0),             # junto à quebra do corte: o que ainda for grama entra
        fundo=FUNDO,
        quinas=None,
    ),
    "subsolo": dict(
        caixa=(903.5, 1057.9, 1082.6, 1129.5),
        vazio=[[(920.6, 1057.3), (1083.2, 1057.3), (1083.2, 1130.1), (954.6, 1130.1)]],   # depois da diagonal
        faixa=(905.0, 1060.0, 919.9, 1082.0),             # o miolo do 1º degrau cheio, acima da seta (o tom)
        quinas=(921.4, 1082.6),                           # perfil desenhado: só o tom e uma quina fina por degrau
        patamar=None,
        verde=None,
        fundo=0.0,                                        # por baixo era branco: só o tom da escada
    ),
}


def aplicar(img, nome, escala=1.0, origem=(0.0, 0.0)):
    e = ESCADAS[nome]
    P = lambda x, y: ((x - origem[0]) * escala, (y - origem[1]) * escala)
    a0, b0 = P(*e["caixa"][:2])
    a1, b1 = P(*e["caixa"][2:])
    A0, B0, A1, B1 = int(np.floor(a0)), int(np.floor(b0)), int(np.ceil(a1)), int(np.ceil(b1))
    reg = img[B0:B1, A0:A1].astype(np.float32)
    H, W = reg.shape[:2]
    # o vazio (a parte transparente): os polígonos, com 8x de amostragem
    k = 8
    m = np.zeros((H * k, W * k), np.uint8)
    for poli in e["vazio"]:
        pts = np.array([[(P(x, y)[0] - A0) * k, (P(x, y)[1] - B0) * k] for x, y in poli])
        cv2.fillPoly(m, [np.round(pts).astype(np.int32)], 255)
    a = cv2.resize(m, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    if e["verde"]:
        r = reg.astype(np.float32)
        c0, d0 = P(*e["verde"][:2])
        c1, d1 = P(*e["verde"][2:])
        sub = np.zeros((H, W), bool)
        sub[max(int(d0) - B0, 0):int(d1) - B0, max(int(c0) - A0, 0):int(c1) - A0] = True
        verde = sub & (r[..., 1] - r[..., 0] > 20) & (r[..., 1] >= r[..., 2] - 2)       # oliva: G bem acima de B, G ~ R
        verde = cv2.dilate(verde.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & sub
        a = np.maximum(a, verde.astype(np.float32))
    # o desenho dos degraus cheios: a faixa limpa, repetida no passo dos degraus
    f0, g0 = P(e["faixa"][0], e["faixa"][1])
    f1, g1 = P(e["faixa"][2], e["faixa"][3])
    F0, G0, F1, G1 = int(round(f0)), int(round(g0)), int(round(f1)), int(round(g1))
    faixa = img[G0:G1, F0:F1].astype(np.float32)
    med = np.median(faixa.reshape(-1, 3), axis=0)
    periodo = PASSO * escala
    nper = max(1, int((F1 - F0) // periodo))
    largura = nper * periodo
    xs = np.arange(A0, A1, dtype=np.float32)
    xsrc = F0 + np.mod(xs - f0, largura)
    if e["patamar"]:
        p0, p1 = P(e["patamar"][0], 0)[0], P(e["patamar"][1], 0)[0]
        meio = (f0 + 0.15 * periodo, f0 + 0.85 * periodo)                  # o miolo de um degrau (sem quina)
        no_pat = (xs >= p0 + 0.6 * escala) & (xs <= p1)
        L = meio[1] - meio[0]
        u = np.mod(xs[no_pat] - p0, 2 * L)
        xsrc[no_pat] = meio[0] + np.where(u > L, 2 * L - u, u)          # espelhada (sem emenda nem quina)
    # o perfil dos degraus (a mediana da faixa, coluna a coluna): cada degrau é uma tábua de tom constante no
    # comprimento, com as quinas; repetido no passo, sem repetir nada na vertical (sem emendas)
    perfil = np.median(faixa, axis=0)
    xi = np.clip(np.round(xsrc).astype(int) - F0, 0, faixa.shape[1] - 1)
    tex = np.broadcast_to(perfil[xi][None, :, :], (H, W, 3))
    if e["quinas"]:
        # o tom do degrau cheio com uma quina fina e suave em cada degrau (no passo do PDF)
        q0, q1 = e["quinas"]
        xf = origem[0] + (xs + 0.5) / escala                                # px da final
        d = np.abs(np.mod(xf - q0 + PASSO / 2, PASSO) - PASSO / 2)
        w = np.exp(-(d / 0.45) ** 2) * (xf >= q0 - 0.5) * (xf <= q1 + 0.5)
        tex = np.broadcast_to((med[None, :] * (1 - 0.22 * w[:, None]))[None, :, :], (H, W, 3))
    novo = med[None, None] + VISTA * (tex - med[None, None])
    fundo = cv2.GaussianBlur(reg, (0, 0), 2.0 * escala)                    # o que está por baixo, sem as linhas
    novo = (1 - e["fundo"]) * novo + e["fundo"] * fundo
    out = reg * (1 - a[..., None]) + novo * a[..., None]
    img[B0:B1, A0:A1] = np.clip(np.round(out), 0, 255).astype(np.uint8)
    print(f"      {nome}: {int((a > 0.5).sum())} px transparentes refeitos, tom {med.round()}")
    return img


def main():
    c, pav = PLANTA.split("_")
    base = cv2.imread(str(EP.PROJ / EP.PLANTAS[PLANTA][0]))
    for f in EP.PLANTAS[PLANTA]:
        im = cv2.imread(str(EP.PROJ / f))
        for nome in ESCADAS:
            im = aplicar(im, nome)
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
        for nome, e in ESCADAS.items():
            x0, y0, x1, y1 = e["caixa"]
            mapa, cc = EP.registro_12k(base, cinza, dz, (int(x0) - 80, int(y0) - 80, int(x1) + 80, int(y1) + 80))
            A, B = mapa(x0, y0)
            sx = (mapa(x0 + 1000.0, y0)[0] - A) / 1000.0
            im = aplicar(im, nome, sx, (x0 - A / sx, y0 - B / sx))
            print(f"   {op}: {nome} (registro {cc:.3f}, escala {sx:.3f})")
        Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).save(rel, quality=95, subsampling=0, dpi=dpi)
        del im, cinza


if __name__ == "__main__":
    main()

"""Térreo da Casa E, 17/11, na final e direto nos 12K A (Inter) e B (Kalam): a escada do deck para o jardim na ordem dos
níveis (usuário: "esse último degrau está abaixo do penúltimo"; com a imagem do PDF: "os números estão localizados nos
cantos de cada degrau, sendo o 1 mais baixo e o 11 o mais alto"; e "o degrau 11 está sobre o banco bronze, mas deveria
estar sob ele").

No PDF (ARQ_CONTRAPISO) os degraus são 10 retângulos que se sobrepõem, desenhados do mais alto (junto ao deck) para o
mais baixo: cada um cobria os de cima, e o render seguiu essa ordem. A composição certa é a dos níveis, o 1 embaixo e
o 11 (o deck) em cima: cada degrau por cima dos mais baixos.

- o 4 (o patamar de baixo, à direita) por cima do 1 (o patamar do jardim, à esquerda): o canto do 1 sai de cima do 4 (a
  borda e o tracinho branco) e o 4 segue inteiro, o piso dele no lugar (`sobre1`, o próprio 4 de logo ao lado).
- os degraus 2 e 3 (sobre o 1) e 5 e 6 (sobre o 4), que ficavam escondidos, aparecem: o piso do patamar um pouco mais
  escuro, no tom dos degraus 7 e 8 do render (`tom`), a sombra curta à esquerda de cada degrau mais alto (a do render
  nos degraus 7 a 10) e um fio de borda leve em cima e embaixo.
- os bancos de bronze (ARQ_ELEMENTOS FIXOS) por cima de tudo, no retângulo do PDF: o de cima avança sobre o degrau 10
  (que estava por cima dele) e sobre a grama até a face do PDF; o de baixo, até a face do PDF (o render parava na borda
  do deck).

  python3 escada_deck_terreo_casae_1711.py doze [--opcao AB]     (antes da final: a final de antes é a referência)
  python3 escada_deck_terreo_casae_1711.py final
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
from janela_pia_casaa_1611 import alfa_ret                  # noqa: E402

RAIZ = AQUI.parents[1]
FINAL = RAIZ / "POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_final.png"
DOZE = RAIZ / "POE642_CasaE/entrega/POE642_CasaE_PH_Terreo_12K_opcao_{}.jpg"

# px da final (bordas); o 4 no render fica ~1 px para dentro do PDF (562.1, 1138.6): a borda de agora, a que segue
ESCADA = {
    "caixa": (440, 970, 840, 1670),
    # o 4 sobre o 1: o piso do 4 (o de 44 px à direita, 8 abaixo) no canto que era do 1, até a face do 4
    "sobre1": [(563.1, 1140.1, 603.5, 1377.5), (603.5, 1143.0, 608.5, 1377.5)], "fonte": (44, 8),
    # os degraus que aparecem: [retângulos visíveis] (o de cima tirado)
    "pequenos": {2: [(514.7, 1102.3, 538.6, 1332.1), (538.6, 1102.3, 578.5, 1120.5)],
                 3: [(538.6, 1120.5, 563.1, 1349.9), (563.1, 1120.5, 602.5, 1140.1)],
                 5: [(633.8, 1220.6, 657.6, 1450.3), (657.6, 1220.6, 697.7, 1238.5)],
                 6: [(657.6, 1238.5, 681.8, 1468.3), (681.8, 1238.5, 705.0, 1256.6)]},
    "tom": 0.95,
    # a sombra à esquerda de cada degrau mais alto, no mais baixo: (x da face, y0, y1)
    "sombras": [(514.7, 1102.3, 1332.1), (538.6, 1120.5, 1349.9), (563.1, 1140.1, 1374.4),
                (633.8, 1220.6, 1450.3), (657.6, 1238.5, 1468.3)],
    # o perfil da sombra (a dos degraus 7 a 10 do render): o quanto escurece a d px da face
    "sombra_d": (0.0, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 8.0),
    "sombra_k": (0.118, 0.117, 0.107, 0.093, 0.05, 0.034, 0.024, 0.015, 0.0),
    # os fios leves: ("h", y, x0, x1) | ("v", x, y0, y1)
    "fios": [("h", 1102.3, 514.7, 578.5), ("h", 1332.1, 514.7, 538.6), ("v", 578.5, 1102.3, 1120.5),
             ("h", 1120.5, 538.6, 602.5), ("h", 1349.9, 538.6, 563.1), ("h", 1140.1, 563.1, 602.5),
             ("h", 1220.6, 633.8, 697.7), ("h", 1450.3, 633.8, 657.6), ("v", 697.7, 1220.6, 1238.5),
             ("h", 1238.5, 657.6, 705.0), ("h", 1468.3, 657.6, 681.8)],
    "fio_k": 0.035,
    # os bancos: (o retângulo a cobrir, até a face do PDF; o deslocamento da fonte, o próprio banco à direita)
    "bancos": [((769.8, 1125.5, 784.5, 1318.3), (15, 0)), ((778.6, 1484.0, 790.0, 1657.7), (12, 0))],
}


def _grade(m, caixa):
    """A caixa (px da final) na imagem: o recorte e as coordenadas da final (bordas) do centro de cada px."""
    X0, Y0, X1, Y1 = m.reti(caixa)
    U = (np.arange(X0, X1, dtype=np.float32) - m.t[0]) / m.s + 0.5
    V = (np.arange(Y0, Y1, dtype=np.float32) - m.t[1]) / m.s + 0.5
    return (X0, Y0, X1, Y1), U, V


def _alfa(m, X0, Y0, forma, rets):
    a = np.zeros(forma, np.float32)
    for r in rets:
        rm = m.ret(r)
        a += alfa_ret((rm[0] - X0, rm[1] - Y0, rm[2] - X0, rm[3] - Y0), forma)
    return np.clip(a, 0, 1)                       # os retângulos de cada peça são vizinhos, sem sobreposição


def _ponta(v, a, b, s):
    """1 dentro de [a, b] (px da final), com a borda suave de 1 px da imagem."""
    k = 0.5 / s
    return np.clip((v - a) / (2 * k) + 0.5, 0, 1) * np.clip((b - v) / (2 * k) + 0.5, 0, 1)


def escada(out, mp, q=ESCADA):
    m = mp.local(out, q["caixa"]) if mp.ref is not None else mp
    s = m.s
    (X0, Y0, X1, Y1), U, V = _grade(m, q["caixa"])
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    forma = reg.shape[:2]
    # 1. o 4 sobre o 1
    dx, dy = int(round(q["fonte"][0] * s)), int(round(q["fonte"][1] * s))
    fonte = out[Y0 + dy:Y1 + dy, X0 + dx:X1 + dx].astype(np.float32)
    a = _alfa(m, X0, Y0, forma, q["sobre1"])[..., None]
    reg = reg * (1 - a) + fonte * a
    # 2. os degraus que aparecem, no tom dos degraus do render
    fator = np.ones(forma, np.float32)
    for rets in q["pequenos"].values():
        fator *= 1 - _alfa(m, X0, Y0, forma, rets) * (1 - q["tom"])
    # 3. as sombras à esquerda de cada degrau mais alto
    for xf, y0, y1 in q["sombras"]:
        d = xf - U[None, :]
        k = np.interp(d, q["sombra_d"], q["sombra_k"], left=0.0, right=0.0) * (d > -0.5 / s)
        fator *= 1 - k * _ponta(V, y0, y1, s)[:, None]
    # 4. os fios leves de borda
    sig = 0.6
    for tipo, c, a0, a1 in q["fios"]:
        if tipo == "h":
            g = np.exp(-((V - c) ** 2) / (2 * sig ** 2))[:, None] * _ponta(U, a0, a1, s)[None, :]
        else:
            g = np.exp(-((U - c) ** 2) / (2 * sig ** 2))[None, :] * _ponta(V, a0, a1, s)[:, None]
        fator *= 1 - q["fio_k"] * g
    reg = reg * fator[..., None]
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    # 5. os bancos de bronze por cima, até a face do PDF (o próprio banco, deslocado, linha a linha)
    for r, (bx, by) in q["bancos"]:
        rm = m.ret(r)
        x0, y0 = int(np.floor(rm[0])) - 1, int(np.floor(rm[1])) - 1
        x1, y1 = int(np.ceil(rm[2])) + 1, int(np.ceil(rm[3])) + 1
        a = alfa_ret((rm[0] - x0, rm[1] - y0, rm[2] - x0, rm[3] - y0), (y1 - y0, x1 - x0))[..., None]
        ddx, ddy = int(round(bx * s)), int(round(by * s))
        alvo = out[y0:y1, x0:x1].astype(np.float32)
        f = out[y0 + ddy:y1 + ddy, x0 + ddx:x1 + ddx].astype(np.float32)
        out[y0:y1, x0:x1] = np.clip(np.round(alvo * (1 - a) + f * a), 0, 255).astype(np.uint8)
    print("    escada do deck: os degraus na ordem dos níveis (1 embaixo, 11 em cima) e os bancos por cima")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("acao", choices=("final", "doze"))
    ap.add_argument("--opcao", default="AB")
    ap.add_argument("--entrada")
    ap.add_argument("--saida")
    a = ap.parse_args()
    fin = cv2.imread(a.entrada or str(FINAL))
    if a.acao == "final":
        out = fin.copy()
        escada(out, Mapa())
        cv2.imwrite(a.saida or str(FINAL), out)
        return
    from PIL import Image
    for op in a.opcao:
        f = Path(str(DOZE).format(op))
        img = cv2.imread(str(f))
        M = DF.afim_12k(fin, img)
        mp = Mapa(float(np.hypot(M[0, 0], M[1, 0])), (float(M[0, 2]), float(M[1, 2])))
        mp.ref = fin
        out = img.copy()
        escada(out, mp)
        dpi = int(round(out.shape[1] / (420 / 25.4)))
        dest = a.saida.format(op) if a.saida else str(f)
        Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB)).save(dest, quality=95, subsampling=0, dpi=(dpi, dpi))
        print(f"    {Path(dest).name}")


if __name__ == "__main__":
    main()

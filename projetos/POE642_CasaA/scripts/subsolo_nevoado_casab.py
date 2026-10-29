"""Casa B, Subsolo: as partes do PDF fora do subsolo, nevoadas (29/10/26).

Pedido do usuário, vendo o Subsolo antes do OK da Casa B: "preciso que represente nevoado as partes que constam no pdf,
correspondente fora do subsolo. o resto do terreno permanece hachurado."

O PDF do Subsolo desenha, fora do subsolo, peças do Térreo: a pedra grande e as 6 lajes da descida (ARQ_CONTRAPISO, o
bege a 50%), o deck em L abaixo da ducha (ARQ_CONTRAPISO) e os 8 degraus da escada que desce ao deck (ARQ_ESCADAS E
RAMPAS). Os dois PDFs têm as mesmas coordenadas e os dois quadros, o mesmo enquadramento (`Quadro.p2q`): essas peças
saem da final do Térreo, sem as letras D das escadas, no nublado do Térreo nas plantas de cima
(`entorno_esmaecido.NUBLADO`: desfoque leve, 80% da saturação, 70% de branco), recortadas pelo contorno delas no PDF do
Subsolo. A escada da ducha e o deck da ducha são do Subsolo e ficam como estão; o resto do lote continua na hachura.

Uso (uma vez, sobre a final de f6ea4b6; o Térreo é a final atual, com as pedras na ordem da descida):
  python3 subsolo_nevoado_casab.py [--antes <png>] [--terreo <png>] [--saida <png>]
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import final3840_casab as F                     # noqa: E402
import final3840_casad as D                     # noqa: E402
from entorno_esmaecido import NUBLADO           # noqa: E402

RENDERS = F.B.CASA_B / "renders"
SUBSOLO_B = RENDERS / "POE642_CasaB_PH_Subsolo_final_rotulos.png"
TERREO_B = RENDERS / "POE642_CasaB_PH_Terreo_final_rotulos.png"

# As peças do Térreo no PDF do Subsolo (o rect de cada preenchimento, em pt) e as do Subsolo que encostam nelas e ficam
# (os 5 degraus da escada da ducha, que avançam 1,7 pt sobre a pedra grande, e o deck da ducha).
NEVOADO_SB = {
    "pecas_pt": [(251.4, 793.6, 517.9, 1064.6), (194.8, 807.8, 251.4, 977.9), (163.5, 830.5, 206.1, 1034.6),
                 (279.8, 901.3, 347.8, 1133.8), (336.5, 929.7, 370.5, 1122.4), (370.5, 912.7, 427.2, 1162.1),
                 (413.0, 975.0, 447.0, 1145.1),
                 (447.0, 963.7, 732.2, 1264.2)]
                + [(x0, 963.7, x1, 1071.4) for x0, x1 in [(728.8, 752.2), (752.2, 775.6), (775.6, 799.0), (799.0, 822.3),
                                                          (822.3, 845.7), (845.7, 869.1), (869.1, 892.5), (892.5, 917.6)]],
    "ficam_pt": [(516.2, 793.6, 534.9, 881.5), (534.9, 793.6, 551.9, 881.5), (551.9, 793.6, 568.9, 881.5),
                 (568.9, 793.6, 585.9, 881.5), (585.9, 793.6, 602.9, 881.5), (602.9, 793.6, 787.2, 963.7)],
    "ss": 4,
    # as letras D do Térreo (F.LETRA_F, cinza 45): o px escuro e neutro, em manchas do tamanho de uma letra
    "letra": {"escuro_max": 120, "neutro_max": 30, "lado_max_px": 30, "folga_px": 2, "raio_px": 3},
}


def _desenhos(Q, rets, tol=0.15):
    ds = []
    for alvo in rets:
        ach = [d for d in Q.desenhos if d.get("fill") is not None
               and max(abs(a - b) for a, b in zip(tuple(d["rect"]), alvo)) <= tol]
        assert ach, f"peça {alvo} não achada no PDF do Subsolo"
        ds.append(ach[0])
    return ds


def _sem_letras(t, caixa, q):
    """O Térreo sem as letras D das escadas: as manchas de px escuros e neutros do tamanho de uma letra, pintadas com o
    entorno (inpaint)."""
    x0, y0, x1, y1 = caixa
    r = t[y0:y1, x0:x1]
    escuro = (r.max(axis=2) < q["escuro_max"]) & (r.max(axis=2).astype(int) - r.min(axis=2) < q["neutro_max"])
    n, lab, st, _ = cv2.connectedComponentsWithStats(cv2.dilate(escuro.astype(np.uint8), np.ones((5, 5), np.uint8)))
    m = np.zeros(escuro.shape, np.uint8)
    for i in range(1, n):
        if st[i, 2] <= q["lado_max_px"] and st[i, 3] <= q["lado_max_px"]:
            m[(lab == i) & escuro] = 255
    m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * q["folga_px"] + 1,) * 2))
    out = t.copy()
    out[y0:y1, x0:x1] = cv2.inpaint(r, m, q["raio_px"], cv2.INPAINT_TELEA)
    return out, int((m > 0).sum())


def _nublar(t, W):
    n = NUBLADO
    t = cv2.GaussianBlur(t.astype(np.float32), (0, 0), n["desfoque"] * W / 3840)
    cinza = t.mean(axis=2, keepdims=True)
    t = cinza + (t - cinza) * n["saturacao"]
    return 255 - (255 - t) * (1 - n["clarear"])


def nevoado_sb(Q, img, terreo, q=NEVOADO_SB):
    pecas, ficam = _desenhos(Q, q["pecas_pt"]), _desenhos(Q, q["ficam_pt"])
    X0, Y0, X1, Y1 = D._caixa_px(Q, [d["rect"] for d in pecas], folga=(6, 6))
    w, h, ss = X1 - X0, Y1 - Y0, q["ss"]
    m = D._mascara_pdf(Q, pecas, X0, Y0, w, h, ss)
    m[D._mascara_pdf(Q, ficam, X0, Y0, w, h, ss) > 0] = 0
    a = cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32)[..., None] / 255
    t, n_letra = _sem_letras(terreo, (X0, Y0, X1, Y1), q["letra"])
    nv = _nublar(t[Y0:Y1, X0:X1], Q.W)
    out = img.copy()
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg * (1 - a) + nv * a), 0, 255).astype(np.uint8)
    print(f"    {len(pecas)} peças do Térreo no PDF do Subsolo, nevoadas ({int((a[..., 0] > 0.5).sum())} px), sem as "
          f"letras D ({n_letra} px); a escada e o deck da ducha ficam")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--antes", default=str(SUBSOLO_B))
    ap.add_argument("--terreo", default=str(TERREO_B))
    ap.add_argument("--saida", default=str(SUBSOLO_B))
    a = ap.parse_args()
    Q = F.Quadro("Subsolo")
    img, terreo = cv2.imread(a.antes), cv2.imread(a.terreo)
    assert img.shape == terreo.shape == (Q.H, Q.W, 3)
    cv2.imwrite(a.saida, nevoado_sb(Q, img, terreo))
    print("ok:", a.saida)

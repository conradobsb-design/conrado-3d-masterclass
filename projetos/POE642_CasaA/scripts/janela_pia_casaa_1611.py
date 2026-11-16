"""A janela da pia da cozinha do Térreo da Casa A, nítida (16/11, usuário: "CORRIJA A JANELA EM FRENTE A BANCADA DA
COZINHA").

A janela já estava no padrão das janelas da Casa A (`pedidos_terreo_casaa_2910.janelas_ta`, o da janela da garagem: o
vão no cinza do peitoril com as faces num fio escuro, cada folha em vidro claro com o contorno fino e a sombra curta).
Na final ela lia certa, mas no 12K saiu borrada da ampliação: as folhas em faixas moles, um bloco manchado no
encontro das duas folhas, as faces sumindo e um pontinho laranja na quina de baixo; por fora, junto à face, a sombra
velha da folha de baixo e a borda clara da ampliação.

Aqui ela é desenhada de novo pela geometria do PDF (`JANELA`, px da final, a ARQ_PAREDE do Térreo): o vão de 2151,4 a
2163,3 (de 1314,6 a 1520,6) e as duas folhas de correr desencontradas (a de cima do lado da pia, de 1317,0 a 1420,0; a
de baixo do lado de fora, de 1415,2 a 1518,2), com as cores do padrão (`pedidos_terreo_casaa_2910.JANELAS_TA`). O
desenho é por cobertura exata de cada px (retângulos alinhados aos eixos), na escala de cada imagem: na final e direto
nos 12K A e B (o afim da final ao 12K por SIFT, `danae_foto.afim_12k`), sem passar pela ampliação.

  python3 janela_pia_casaa_1611.py final [--saida <png>]
  python3 janela_pia_casaa_1611.py doze [--opcao AB] [--saida <jpg com {}>]
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import danae_foto as DF                          # noqa: E402
from pedidos_terreo_casaa_2910 import JANELAS_TA  # noqa: E402

FINAL = DF.PLANTAS["A_Terreo"]
DOZE = DF.DOZE_K["A_Terreo"]
JANELA = {"vao": (2151.4, 1314.6, 2163.3, 1520.6),
          "folhas": [(2157.4, 1317.0, 2160.3, 1420.0), (2160.3, 1415.2, 2163.3, 1518.2)],
          # o piso de fora junto à face (a sombra velha da folha, a borda clara do 12K e o pontinho laranja da quina
          # de baixo): o piso de `fora_dx` px à direita
          "fora": (2163.5, 1314.6, 2168.5, 1523.0), "fora_dx": 6.0}


def cobertura(a, b, n):
    """A fração de cada px [i, i+1) de 0..n-1 coberta pelo intervalo [a, b)."""
    i = np.arange(n, dtype=np.float64)
    return np.clip(np.minimum(b, i + 1) - np.maximum(a, i), 0, 1)


def alfa_ret(r, forma):
    x0, y0, x1, y1 = r
    h, w = forma
    return (cobertura(y0, y1, h)[:, None] * cobertura(x0, x1, w)[None, :]).astype(np.float32)


def alfa_contorno(r, larg, forma):
    x0, y0, x1, y1 = r
    e = larg / 2
    a = np.zeros(forma, np.float32)
    for q in ((x0 - e, y0 - e, x0 + e, y1 + e), (x1 - e, y0 - e, x1 + e, y1 + e),
              (x0 - e, y0 - e, x1 + e, y0 + e), (x0 - e, y1 - e, x1 + e, y1 + e)):
        a = np.maximum(a, alfa_ret(q, forma))
    return a


def compor(reg, a, cor):
    return reg * (1 - a[..., None]) + np.float32(cor) * a[..., None]


def desenhar(img, s=1.0, t=(0.0, 0.0), q=JANELA, p=JANELAS_TA):
    """A janela em `img`, com a final levada a ela por u' = s (u - 1/2) + t + 1/2 (px de borda; s = 1, t = 0: a final)."""
    def m(r):
        return tuple(s * (v - 0.5) + t[i % 2] + 0.5 for i, v in enumerate(r))
    vao = m(q["vao"])
    folga = int(np.ceil(13 * s)) + 2                # cobre o piso de fora e a fonte dele
    X0, Y0 = int(np.floor(vao[0])) - folga, int(np.floor(vao[1])) - folga
    X1, Y1 = int(np.ceil(vao[2])) + folga, int(np.ceil(vao[3])) + folga
    out = img.copy()
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    forma = reg.shape[:2]
    loc = lambda r: (r[0] - X0, r[1] - Y0, r[2] - X0, r[3] - Y0)       # noqa: E731
    # o piso de fora junto à face: o de `fora_dx` px à direita
    qx0, qy0, qx1, qy1 = (int(round(v)) for v in loc(m(q["fora"])))
    d = int(round(q["fora_dx"] * s))
    reg[qy0:qy1, qx0:qx1] = reg[qy0:qy1, qx0 + d:qx1 + d]
    # o vão no cinza do peitoril, com as faces num fio escuro
    av = alfa_ret(loc(vao), forma)
    reg = compor(reg, av, p["peitoril"])
    # a sombra curta das folhas no peitoril
    folhas = [loc(m(f)) for f in q["folhas"]]
    af = np.zeros(forma, np.float32)
    for f in folhas:
        af = np.maximum(af, alfa_ret(f, forma))
    sh = cv2.GaussianBlur(np.roll(np.roll(af, int(round(0.7 * s)), 0), int(round(0.7 * s)), 1), (0, 0), 0.7 * s)
    reg = reg * (1 - (p["sombra"] * sh * av * (1 - af))[..., None])
    reg = compor(reg, alfa_contorno(loc(vao), p["face_px"] * s, forma), p["face"])
    # as folhas: o vidro claro com o contorno fino (a de baixo por cima, como no PDF)
    for f in folhas:
        reg = compor(reg, alfa_ret(f, forma), p["vidro"])
        reg = compor(reg, alfa_contorno(f, p["vidro_px"] * s, forma), p["vidro_contorno"])
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("acao", choices=("final", "doze"))
    ap.add_argument("--opcao", default="AB")
    ap.add_argument("--saida")
    a = ap.parse_args()
    final = cv2.imread(str(FINAL))
    if a.acao == "final":
        cv2.imwrite(a.saida or str(FINAL), desenhar(final))
        print(f"    a janela da pia: o vão e as 2 folhas do PDF, nítidos -> {a.saida or FINAL.name}")
        return
    from PIL import Image
    for op in a.opcao:
        f = Path(str(DOZE).format(op))
        doze = cv2.imread(str(f))
        M = DF.afim_12k(final, doze)
        s = float(np.hypot(M[0, 0], M[1, 0]))
        out = desenhar(doze, s, (float(M[0, 2]), float(M[1, 2])))
        dpi = int(round(out.shape[1] / (420 / 25.4)))
        dest = a.saida.format(op) if a.saida else str(f)
        Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB)).save(dest, quality=95, subsampling=0, dpi=(dpi, dpi))
        print(f"    {Path(dest).name}: a janela da pia redesenhada na escala do 12K ({s:.4f}x)")


if __name__ == "__main__":
    main()

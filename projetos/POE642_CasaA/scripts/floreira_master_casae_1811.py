"""A floreira do banho master da Casa E (1º Pavimento) com menos plantas, bem distribuídas (usuário, 18/11: "melhore a
representação das plantas, com menos plantas e bem distribuidas, na suite master"): 3 costelas-de-adão 4K da
biblioteca (`banho-master/costela-de-adao-4k.png`, Higgsfield, recortada do fundo branco) sobre a terra escura,
espaçadas por igual no comprido da floreira, cada uma num giro, com a sombra curta na terra. Grava a peça na biblioteca
(`banho-master/floreira-3-costelas-4k.png`, na proporção da caixa da floreira na final, 34 x 82 px).

  python3 floreira_master_casae_1811.py
"""
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
BIB = AQUI.parents[1] / "POE642_CasaE/biblioteca-objetos/03-primeiro-pavimento/banho-master"
FLOREIRA = {"planta": BIB / "costela-de-adao-4k.png", "saida": BIB / "floreira-3-costelas-4k.png",
            "caixa": (34, 82), "largura": 640, "terra": (44, 58, 76), "terra_ruido": 9.0, "pedrisco": 0.035,
            "plantas": [(1 / 6, 0.0, False), (0.5, 128.0, True), (5 / 6, 247.0, False)], "lado": 0.76,
            "sombra": 0.45, "semente": 1815}


def main(q=FLOREIRA):
    W = q["largura"]
    H = int(round(W * q["caixa"][1] / q["caixa"][0]))
    rng = np.random.default_rng(q["semente"])
    # a terra: o tom escuro com o grão e alguns pedriscos claros
    base = np.float32(q["terra"])[None, None] * np.ones((H, W, 1), np.float32)
    n1 = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 2.0)
    n2 = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 9.0)
    out = base + (q["terra_ruido"] * (n1 / n1.std()) + 0.6 * q["terra_ruido"] * (n2 / n2.std()))[..., None]
    k = rng.random((H, W)) < q["pedrisco"] / 40
    ped = cv2.GaussianBlur(cv2.dilate(k.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(np.float32), (0, 0), 1.2)
    out = out * (1 - 0.8 * ped[..., None]) + np.float32((150, 160, 168))[None, None] * 0.8 * ped[..., None]
    P = cv2.imread(str(q["planta"]), cv2.IMREAD_UNCHANGED).astype(np.float32)
    lado = int(round(q["lado"] * W))
    for fy, giro, espelho in q["plantas"]:
        Pp = P[:, ::-1] if espelho else P
        Pp = cv2.resize(Pp, (lado, lado), interpolation=cv2.INTER_AREA)
        M = cv2.getRotationMatrix2D((lado / 2, lado / 2), giro, 1.0)
        Pp = cv2.warpAffine(Pp, M, (lado, lado), flags=cv2.INTER_LINEAR, borderValue=0)
        # o centro pela massa das folhas (a planta não é redonda)
        mx = float((Pp[..., 3] * np.arange(lado)[None, :]).sum() / max(Pp[..., 3].sum(), 1))
        my = float((Pp[..., 3] * np.arange(lado)[:, None]).sum() / max(Pp[..., 3].sum(), 1))
        cx, cy = W / 2, fy * H
        x0, y0 = int(round(cx - mx)), int(round(cy - my))
        a = np.zeros((H, W), np.float32)
        cor = np.zeros((H, W, 3), np.float32)
        xa, ya, xb, yb = max(x0, 0), max(y0, 0), min(x0 + lado, W), min(y0 + lado, H)
        a[ya:yb, xa:xb] = Pp[ya - y0:yb - y0, xa - x0:xb - x0, 3] / 255
        cor[ya:yb, xa:xb] = Pp[ya - y0:yb - y0, xa - x0:xb - x0, :3]
        sb = cv2.GaussianBlur(cv2.warpAffine(a, np.float32([[1, 0, -0.02 * W], [0, 1, 0.025 * W]]), (W, H)), (0, 0),
                              0.02 * W)
        out *= (1 - q["sombra"] * sb * (1 - a))[..., None]
        out = out * (1 - a[..., None]) + cor * a[..., None]
    cv2.imwrite(str(q["saida"]), np.clip(np.round(out), 0, 255).astype(np.uint8), [cv2.IMWRITE_PNG_COMPRESSION, 9])
    print(f"-> {q['saida']} ({W} x {H})")


if __name__ == "__main__":
    main()

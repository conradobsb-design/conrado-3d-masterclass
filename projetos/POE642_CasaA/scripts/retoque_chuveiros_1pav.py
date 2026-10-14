#!/usr/bin/env python3
"""Retoque sem IA dos chuveiros de teto do 1º Pavimento (render do v7_ajuste).

O motor acertou a planta, mas errou os chuveiros de teto. No banho master, as duas placas
saíram enormes, uma em cima da banheira e outra no meio do piso, e a área de banho ficou
com uma ducha redonda. No banho 3, a placa foi para a frente da bacia, e a ducha redonda
com braço ficou na área de banho. Este script corrige só isso, com precisão de pixel:

1. alinha o render da v7 (sem as placas grandes) ao render a corrigir (SIFT + afim);
2. troca as placas grandes pelo mesmo trecho do render da v7 (banheira e piso inteiros);
3. apaga as duchas redondas com braço (inpaint);
4. desenha placas finas de 30 cm nas posições das placas cinza da base v3, alinhada ao render.

Saída: o PNG final e um PNG transparente só com as alterações, para usar como camada no
Photoshop.

Uso:
  python retoque_chuveiros_1pav.py RENDER_AJUSTE RENDER_V7 BASE_V3_16x9 --saida PASTA

Os retângulos de correção estão em px de um render com 2000 px de largura; o script
reescala para o tamanho real do arquivo.
"""
import argparse
from pathlib import Path

import cv2
import numpy as np

# px num render de 2000 px de largura (o do v7_ajuste)
PLACAS_GRANDES = [(1110, 211, 1146, 248),   # banho 3: placa na frente da bacia
                  (755, 773, 792, 811),     # master: placa em cima da banheira
                  (823, 773, 861, 811)]     # master: placa no meio do piso
DUCHAS = [(1155, 190, 1176, 209),           # banho 3: ducha, braço e suporte (a moldura da janela fica)
          (735, 822, 760, 840)]             # master: ducha e braço vindo da esquerda

# placas cinza da base v3 (prévia de 1800 px, ver config_bases.json) e o lado de 30 cm
PLACAS_BASE_VIS = {"banho 3": (1058.79, 232.47),
                   "master esq": (632.2, 862.18),
                   "master dir": (670.85, 862.18)}
LADO_VIS = 9.66                    # 30 cm na prévia de 1800 px (1 m = 32,21)
BASE_LARGURA_SEM_MARGEM = 6001     # base antes da margem 16:9
LARGURA_VIS = 1800


def afim(origem, destino, n=8000, razao=0.72, tol=2.5):
    """Afim origem -> destino por SIFT + RANSAC (as duas em BGR)."""
    sift = cv2.SIFT_create(n)
    g1 = cv2.cvtColor(origem, cv2.COLOR_BGR2GRAY)
    g2 = cv2.cvtColor(destino, cv2.COLOR_BGR2GRAY)
    k1, d1 = sift.detectAndCompute(g1, None)
    k2, d2 = sift.detectAndCompute(g2, None)
    bons = [a for a, b in cv2.BFMatcher().knnMatch(d1, d2, k=2) if a.distance < razao * b.distance]
    src = np.float32([k1[m.queryIdx].pt for m in bons])
    dst = np.float32([k2[m.trainIdx].pt for m in bons])
    A, inl = cv2.estimateAffine2D(src, dst, ransacReprojThreshold=tol)
    res = np.linalg.norm(src @ A[:, :2].T + A[:, 2] - dst, axis=1)[inl.ravel() == 1]
    print(f"    {int(inl.sum())} pontos, erro mediano {np.median(res):.2f} px")
    return np.vstack([A, [0, 0, 1]])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("render_ajuste", type=Path, help="render a corrigir (v7_ajuste)")
    ap.add_argument("render_v7", type=Path, help="render da v7, sem as placas grandes")
    ap.add_argument("base", type=Path, help="bases/POE642_CasaA_BASE_1Pavimento_v3_16x9.png")
    ap.add_argument("--saida", type=Path, default=Path("."))
    args = ap.parse_args()

    r = cv2.imread(str(args.render_ajuste))
    v7 = cv2.imread(str(args.render_v7))
    base = cv2.imread(str(args.base))
    H, W = r.shape[:2]
    e = W / 2000
    v7 = cv2.resize(v7, (W, H), interpolation=cv2.INTER_AREA) if v7.shape[:2] != (H, W) else v7

    print("[1] alinhando o render da v7 ao render a corrigir")
    A_v7 = afim(v7, r)
    print("[1] alinhando a base ao render da v7")
    s = W / base.shape[1]
    base_red = cv2.resize(base, (W, round(base.shape[0] * s)), interpolation=cv2.INTER_AREA)
    T = A_v7 @ afim(base_red, v7, n=10000, razao=0.75) @ np.diag([s, s, 1])  # base em px reais -> render

    out = r.copy()
    v7_al = cv2.warpAffine(v7, A_v7[:2], (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    alterado = np.zeros((H, W), np.uint8)

    print("[2] placas grandes -> trecho do render da v7")
    m = np.zeros((H, W), np.uint8)
    for x0, y0, x1, y1 in PLACAS_GRANDES:
        m[int(y0 * e):int(y1 * e), int(x0 * e):int(x1 * e)] = 1
    f = cv2.GaussianBlur(cv2.dilate(m, np.ones((3, 3), np.uint8)).astype(np.float32), (0, 0), 1.2 * e)[..., None]
    out = (out * (1 - f) + v7_al * f).astype(np.uint8)
    alterado |= m

    print("[3] duchas redondas com braço -> inpaint")
    mi = np.zeros((H, W), np.uint8)
    for x0, y0, x1, y1 in DUCHAS:
        x0, y0, x1, y1 = int(x0 * e), int(y0 * e), int(x1 * e), int(y1 * e)
        reg = out[y0:y1, x0:x1].astype(int)
        piso = np.median(reg.reshape(-1, 3), axis=0)
        mk = (np.abs(reg - piso).max(axis=2) > 22).astype(np.uint8)
        mi[y0:y1, x0:x1] |= cv2.dilate(mk, np.ones((3, 3), np.uint8))
    out = cv2.inpaint(out, mi * 255, 4, cv2.INPAINT_TELEA)
    alterado |= mi

    print("[4] placas finas de 30 cm nas posições da base")
    k = BASE_LARGURA_SEM_MARGEM / LARGURA_VIS
    margem = (base.shape[1] - BASE_LARGURA_SEM_MARGEM) / 2
    lado = LADO_VIS * k * np.sqrt(abs(np.linalg.det(T[:2, :2])))
    ss = 8
    camada = np.zeros((H, W), np.float32)
    for nome, (xv, yv) in PLACAS_BASE_VIS.items():
        cx, cy = (T @ np.array([xv * k + margem, yv * k, 1]))[:2]
        n = int(np.ceil(lado)) + 4
        x0, y0 = int(np.floor(cx - n / 2)), int(np.floor(cy - n / 2))
        big = np.zeros((n * ss, n * ss, 4), np.float32)
        c, h = ((cx - x0) * ss, (cy - y0) * ss), lado * ss / 2
        p0 = (int(round(c[0] - h)), int(round(c[1] - h)))
        p1 = (int(round(c[0] + h)), int(round(c[1] + h)))
        cv2.rectangle(big, p0, p1, (231, 233, 233, 1.0), -1)                                  # face prata bem clara
        cv2.rectangle(big, p0, p1, (160, 163, 165, 1.0), max(1, int(round(0.7 * ss))))       # contorno fino
        for i in range(5):                                                                   # furinhos 5 x 5
            for j in range(5):
                px = p0[0] + (i + 1) * (p1[0] - p0[0]) / 6
                py = p0[1] + (j + 1) * (p1[1] - p0[1]) / 6
                cv2.circle(big, (int(px), int(py)), max(1, int(round(0.28 * ss))), (185, 188, 190, 1.0), -1, cv2.LINE_AA)
        small = cv2.resize(big, (n, n), interpolation=cv2.INTER_AREA)
        a = small[..., 3:4]
        reg = out[y0:y0 + n, x0:x0 + n].astype(np.float32)
        out[y0:y0 + n, x0:x0 + n] = (reg * (1 - a) + small[..., :3] * a).astype(np.uint8)
        camada[y0:y0 + n, x0:x0 + n] = np.maximum(camada[y0:y0 + n, x0:x0 + n], small[..., 3])
        print(f"    {nome}: centro ({cx:.1f}, {cy:.1f}), lado {lado:.1f} px")

    args.saida.mkdir(parents=True, exist_ok=True)
    final = args.saida / "POE642_CasaA_PH_1Pavimento_v7_final.png"
    cv2.imwrite(str(final), out)
    alfa = np.maximum(cv2.dilate(alterado, np.ones((3, 3), np.uint8)).astype(np.float32), camada)
    cv2.imwrite(str(args.saida / "POE642_CasaA_PH_1Pavimento_v7_final_camada.png"),
                np.dstack([out, (alfa * 255).astype(np.uint8)]))
    dif = (np.abs(out.astype(int) - r.astype(int)).max(axis=2) > 3).sum()
    print(f"[5] {final} ({W}x{H}); {dif} px alterados, só nos dois banhos")


if __name__ == "__main__":
    main()

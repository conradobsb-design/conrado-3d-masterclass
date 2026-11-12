"""Os chuveiros do 1º Pavimento da Casa A desenhados em planta (12/11).

Usuário, vendo a prancha do 1º Pavimento com as peças da biblioteca: "OS CHUVEIROS PRECISAM SER REFEITOS. ESTÃO MUITO
APAGADOS". Os PNG da biblioteca (`chuveiro-quadrado`, `chuveiro-quadrado-parede`, `chuveiro-redondo-parede`) são fotos
de cromado claro: reduzidos a 12 px sobre o travertino claro, viram um quadrado cinza-claro liso (os furos somem), e o
redondo de parede é foto em perspectiva (sai oval). Aqui eles são desenhados vistos de cima, nítidos em qualquer escala
(a final e o 12K usam o mesmo PNG), com a luz do alto à direita, como as sombras da planta:
  - a placa em inox escovado médio (o cinza que se lê sobre o travertino), com o degradê da luz;
  - o chanfro da borda (claro em cima e à direita, escuro embaixo e à esquerda) e o contorno escuro fino;
  - o crivo um pouco mais escuro, com a grade de furos (quadrado) ou os anéis de furos (redondo);
  - nos de parede, o braço em tubo (o brilho do lado da luz) e a canopla na parede.
Grava os PNG na biblioteca, ao lado dos originais, com o sufixo `-planta`:
  python3 chuveiros_planta_casaa_1211.py
"""

from pathlib import Path

import cv2
import numpy as np

BIB = Path(__file__).resolve().parent.parent / "biblioteca-objetos" / "03-primeiro-pavimento"
L = 480                          # o lado da placa no PNG (px)
C = {"placa_claro": 196.0, "placa_escuro": 128.0, "crivo": 112.0, "furo": 58.0, "furo_brilho": 150.0,
     "chanfro_luz": 238.0, "chanfro_sombra": 74.0, "contorno": 46.0, "tinta": (1.00, 1.00, 0.97)}
Q = {"chanfro": 0.075, "contorno": 0.018, "crivo_marg": 0.17, "raio_canto": 0.07, "furos": 6, "furo_r": 0.024}
BRACO = {"larg": 0.14, "comp": 1.35, "canopla": (0.34, 0.20)}


def _canto_arredondado(h, w, r):
    m = np.zeros((h, w), np.uint8)
    r = int(round(r))
    cv2.rectangle(m, (r, 0), (w - 1 - r, h - 1), 255, -1)
    cv2.rectangle(m, (0, r), (w - 1, h - 1 - r), 255, -1)
    for cx, cy in ((r, r), (w - 1 - r, r), (r, h - 1 - r), (w - 1 - r, h - 1 - r)):
        cv2.circle(m, (cx, cy), r, 255, -1, cv2.LINE_AA)
    return m.astype(np.float32) / 255


def _dist(forma, marg=4):
    """A distância à borda da forma (com margem: a forma encosta na borda do quadro)."""
    m = cv2.copyMakeBorder((forma > 0.5).astype(np.uint8), marg, marg, marg, marg, cv2.BORDER_CONSTANT, value=0)
    return cv2.distanceTransform(m, cv2.DIST_L2, 5)[marg:-marg, marg:-marg]


def _chanfro(forma, larg):
    """A borda chanfrada: (fator de luz -1 a 1, peso 0 a 1) pela normal da borda; a luz vem do alto à direita."""
    d = _dist(forma)
    peso = np.clip(1 - d / larg, 0, 1) * (forma > 0.02)
    gy, gx = np.gradient(cv2.GaussianBlur(d, (0, 0), larg * 0.35, borderType=cv2.BORDER_CONSTANT))
    n = np.hypot(gx, gy) + 1e-6
    # a normal para fora é -grad(d); a luz vem de (+x, -y)
    luz = (-gx / n) * 0.7071 + (gy / n) * 0.7071
    return np.clip(luz, -1, 1), peso


def _cor(cinza):
    t = np.float32(C["tinta"])
    return np.clip(cinza[..., None] * t[None, None], 0, 255)


def placa(redonda=False):
    """A placa vista de cima, (cor BGR, alfa) em L x L."""
    h = w = L
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    if redonda:
        forma = np.zeros((h, w), np.uint8)
        cv2.circle(forma, (w // 2, h // 2), w // 2 - 1, 255, -1, cv2.LINE_AA)
        forma = forma.astype(np.float32) / 255
    else:
        forma = _canto_arredondado(h, w, Q["raio_canto"] * L)
    # o degradê da luz: claro no alto à direita, escuro embaixo à esquerda (o inox escovado, com o risco fino)
    t = ((xx / w) + (1 - yy / h)) / 2
    g = C["placa_escuro"] + (C["placa_claro"] - C["placa_escuro"]) * t
    rng = np.random.default_rng(7)
    risco = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), sigmaX=L * 0.04, sigmaY=0.6)
    g = g + 5.0 * risco / (risco.std() + 1e-6)
    # o crivo: um pouco mais escuro, com os furos
    m = Q["crivo_marg"] * L
    if redonda:
        crivo = np.zeros((h, w), np.uint8)
        cv2.circle(crivo, (w // 2, h // 2), int(w / 2 - m), 255, -1, cv2.LINE_AA)
        crivo = crivo.astype(np.float32) / 255
    else:
        crivo = _canto_arredondado(int(h - 2 * m), int(w - 2 * m), Q["raio_canto"] * L * 0.6)
        crivo = cv2.copyMakeBorder(crivo, int(m), h - int(m) - crivo.shape[0], int(m), w - int(m) - crivo.shape[1],
                                   cv2.BORDER_CONSTANT, value=0)
    gc = C["crivo"] + 0.35 * (g - C["crivo"])
    g = g * (1 - crivo) + gc * crivo
    furos = np.zeros((h, w), np.uint8)
    brilho = np.zeros((h, w), np.uint8)
    r = max(2, int(round(Q["furo_r"] * L)))
    if redonda:
        R0 = w / 2 - m
        pts = [(w / 2, h / 2)]
        for k, rr in enumerate((0.30, 0.58, 0.84)):
            n = (6, 12, 18)[k]
            for i in range(n):
                a = 2 * np.pi * (i + 0.5 * (k % 2)) / n
                pts.append((w / 2 + rr * R0 * np.cos(a), h / 2 + rr * R0 * np.sin(a)))
    else:
        n = Q["furos"]
        passo = (w - 2 * m) / n
        pts = [(m + passo * (i + 0.5), m + passo * (j + 0.5)) for i in range(n) for j in range(n)]
    for px, py in pts:
        cv2.circle(furos, (int(round(px)), int(round(py))), r, 255, -1, cv2.LINE_AA)
        cv2.circle(brilho, (int(round(px + 0.45 * r)), int(round(py - 0.45 * r))), max(1, r // 3), 255, -1,
                   cv2.LINE_AA)
    f, bl = furos.astype(np.float32) / 255, brilho.astype(np.float32) / 255
    g = g * (1 - f) + C["furo"] * f
    g = g * (1 - 0.5 * bl * f) + C["furo_brilho"] * 0.5 * bl * f
    # a canaleta em volta do crivo (a sombra fina da borda dele)
    anel = np.clip(cv2.GaussianBlur(crivo, (0, 0), L * 0.006) - crivo, 0, 1) * 2.2
    g = g * (1 - 0.35 * np.clip(anel, 0, 1))
    # o chanfro da borda e o contorno
    luz, peso = _chanfro(forma, Q["chanfro"] * L)
    alvo = np.where(luz > 0, C["chanfro_luz"], C["chanfro_sombra"])
    kk = np.abs(luz) * peso * 0.85
    g = g * (1 - kk) + alvo * kk
    d = _dist(forma)
    cont = np.clip(1 - d / (Q["contorno"] * L), 0, 1) * (forma > 0.02)
    g = g * (1 - cont) + C["contorno"] * cont
    return _cor(g), forma


def braco(comp_px):
    """O braço em tubo e a canopla, vistos de cima: a canopla no alto (na parede), o tubo descendo até a placa."""
    lw = BRACO["larg"] * L
    cw, ch = BRACO["canopla"][0] * L, BRACO["canopla"][1] * L
    h, w = int(round(comp_px)), int(round(max(cw, lw) + 4))
    alfa = np.zeros((h, w), np.float32)
    g = np.zeros((h, w), np.float32)
    xx = np.arange(w, dtype=np.float32)[None, :].repeat(h, 0)
    cx = w / 2
    # o tubo: cilindro com o brilho do lado da luz (direita)
    u = (xx - cx) / (lw / 2)
    tubo = (np.abs(u) <= 1).astype(np.float32)
    perfil = 132 + 85 * np.exp(-((u - 0.35) / 0.28) ** 2) - 55 * np.clip(-u, 0, 1) ** 1.5
    borda = np.clip((np.abs(u) - 0.78) / 0.22, 0, 1)
    perfil = perfil * (1 - borda) + C["contorno"] * 1.4 * borda
    alfa = np.maximum(alfa, tubo)
    g = np.where(tubo > 0, perfil, g)
    # a canopla na parede (alto do PNG): o quadradinho com o chanfro
    can = np.zeros((h, w), np.float32)
    x0, x1 = int(round(cx - cw / 2)), int(round(cx + cw / 2))
    can[0:int(round(ch)), max(0, x0):min(w, x1)] = 1
    lz, pz = _chanfro(can, 0.25 * ch)
    gcan = 150 + 25 * (1 - np.arange(h, dtype=np.float32)[:, None] / max(1, ch))
    alvo = np.where(lz > 0, C["chanfro_luz"], C["chanfro_sombra"])
    gcan = gcan * (1 - np.abs(lz) * pz * 0.8) + alvo * np.abs(lz) * pz * 0.8
    g = np.where(can > 0, gcan, g)
    alfa = np.maximum(alfa, can)
    return g, alfa


def com_braco(redonda):
    cor, a = placa(redonda)
    gb, ab = braco(BRACO["comp"] * L)
    w = cor.shape[1]
    # o braço centrado em cima da placa, entrando um pouco nela (por baixo da placa)
    hb = gb.shape[0]
    entra = int(0.30 * L)
    H = hb + L - entra
    out_c = np.zeros((H, w, 3), np.float32)
    out_a = np.zeros((H, w), np.float32)
    x0 = (w - gb.shape[1]) // 2
    out_c[:hb, x0:x0 + gb.shape[1]] = _cor(gb)
    out_a[:hb, x0:x0 + gb.shape[1]] = ab
    y0 = hb - entra
    ap = a[..., None]
    out_c[y0:] = out_c[y0:] * (1 - ap) + cor * ap
    out_a[y0:] = np.maximum(out_a[y0:], a)
    return out_c, out_a


def gravar(nome, cor, a, marg=8):
    cor = cv2.copyMakeBorder(cor, marg, marg, marg, marg, cv2.BORDER_CONSTANT, value=0)
    a = cv2.copyMakeBorder(a, marg, marg, marg, marg, cv2.BORDER_CONSTANT, value=0)
    P = np.dstack([cor, a * 255])
    P[..., :3] *= (a[..., None] > 0)
    arq = BIB / f"{nome}.png"
    cv2.imwrite(str(arq), np.clip(np.round(P), 0, 255).astype(np.uint8))
    print(f"    {arq} {P.shape[1]}x{P.shape[0]}")


def main():
    cor, a = placa(False)
    for pasta in ("banho-master", "banho-3"):
        gravar(f"{pasta}/chuveiro-quadrado-planta", cor, a)
    cor, a = com_braco(False)
    for pasta in ("banho-1", "banho-2"):
        gravar(f"{pasta}/chuveiro-quadrado-parede-planta", cor, a)
    cor, a = com_braco(True)
    gravar("banho-de-servico/chuveiro-redondo-parede-planta", cor, a)


if __name__ == "__main__":
    main()

"""Casa A Térreo, revisão do usuário de 25/11 (3ª leva, com os recortes do 12K).

1. "corrija as falhas no tapete" (a VARANDA, o tapete cinza sob o sofá curvo de teca e a mesinha redonda): no canto de
   cima, à direita, o tapete tinha um retângulo mais claro (a borda de cima um degrau abaixo) e uma sombra diagonal solta
   entre a mesinha e o sofá. Esse canto recebe o próprio tapete da mesma linha, mais à esquerda (as listras e a borda de
   cima seguem retas); a mesinha e o sofá ficam (só os pixels cinza do tapete e do piso mudam).
2. "remova esse contorno de linhas do mobiliário" (o aparador de madeira clara da SALA DE JANTAR, junto à planta e à
   parede de baixo): a moldura (a linha escura por fora, a faixa clara por dentro e o risco de baixo) sai; o aparador
   fica num tom sólido só, o do miolo dele.
3. "corrija a representação dessas portas" (a cozinha, a circulação, o B. MOTORISTA e o Q. MOTORISTA) e "corrija o piso e
   essas falhas" (o Q. MOTORISTA junto à porta da direita): em volta de cada folha havia folhas antigas sobrepostas
   (contornos deslocados, a folha de ripado branca com o puxador na cozinha, sombras de folhas, o tampo escuro da parede
   passando da face, a peça cinza solta no Q. MOTORISTA e o piso liso entre a folha e a parede). Em volta de cada folha,
   fora das paredes do PDF, entra o piso da mesma linha (ou da mesma coluna, na porta deitada do B. MOTORISTA) logo ao
   lado; depois cada folha do PDF é desenhada no padrão das esquadrias (perfil cinza claro, vidro claro e a linha fina),
   no lugar e no tamanho do PDF.

Final, prancha e 12K A e B (cada item pelo registro local).

  python3 terreo_casaa_2511c.py
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

PLANTA = "A_Terreo"

TAPETE = dict(caixa=(1690.0, 395.8, 1742.0, 434.0), dx=-46.0,
              sofa=((1711.0, 395.5), (1740.0, 441.0)),     # a borda de fora da madeira do sofá (descendo)
              mesinha=(1707.5, 391.0, 10.5))               # a mesinha redonda (centro e raio)
APARADOR = dict(busca=(1925.0, 1068.0, 2130.0, 1104.0), fundo=1104.3)
# as portas: a folha do PDF (x0, y0, x1, y1), a caixa do que sai e o deslocamento da fonte do piso (dx, dy)
PORTAS = {
    "cozinha": dict(folha=(1868.1, 1247.5, 1870.5, 1334.0), caixa=(1855.0, 1243.0, 1872.6, 1338.0), desloc=(-19.0, 0.0),
                    pintar=[(1864.5, 1295.2, 1868.1, 1296.7)], parede_ref=(1873.5, 1270.0, 1879.5, 1290.0)),
    "cozinha_dir": dict(folha=(2163.6, 1208.6, 2166.0, 1280.3), caixa=(2153.6, 1160.0, 2170.5, 1290.0),
                        desloc=(18.0, 0.0)),
    "b_motorista": dict(folha=(2235.6, 1251.9, 2238.0, 1305.7), caixa=(2230.5, 1246.0, 2246.5, 1305.5),
                        desloc=(-17.0, 0.0), nivel=(1238.0, 1245.0)),
    "q_motorista": dict(folha=(2522.2, 1251.9, 2524.6, 1305.7), caixa=(2516.5, 1234.0, 2534.0, 1305.5),
                        desloc=(-18.0, 0.0)),
    "b_motorista_correr": dict(folha=(2342.5, 1294.3, 2384.3, 1296.7), caixa=(2340.5, 1290.5, 2388.5, 1299.5),
                               desloc=(0.0, -10.0)),
}
# o Q. MOTORISTA no 12K: o piso em faixas (liso, texturizado, liso); o texturizado (o das cozinhas) vai para o quarto todo
QMOT = dict(quarto=(2394.5, 1117.5, 2533.5, 1305.0), faixa=(2462.0, 2495.0), letras=(1248.0, 1294.0), sobe=62.0,
            cama=(2394.0, 1117.0, 2449.5, 1233.0), armario=(2498.0, 1117.0, 2534.5, 1225.0))
SO_12K = {"piso_qmot"}
ITENS = {
    "tapete": (1660.0, 380.0, 1760.0, 460.0),
    "aparador": (1920.0, 1060.0, 2135.0, 1110.0),
    "portas_cozinha": (1850.0, 1235.0, 1890.0, 1345.0),
    "portas_circulacao": (2140.0, 1150.0, 2260.0, 1320.0),
    "portas_motorista": (2330.0, 1225.0, 2545.0, 1320.0),
    "piso_qmot": (2380.0, 1110.0, 2545.0, 1315.0),
}
GRUPO = {"portas_cozinha": ["cozinha"], "portas_circulacao": ["cozinha_dir", "b_motorista"],
         "portas_motorista": ["q_motorista", "b_motorista_correr"]}

_PAREDES = None


def paredes():
    """As paredes do PDF (os preenchimentos de ARQ_PAREDE), em px da final."""
    global _PAREDES
    if _PAREDES is None:
        Q = EP.quadro(PLANTA)
        _PAREDES = []
        for e in Q.desenhos:
            if e["layer"] == "ARQ_PAREDE" and e["type"] == "f":
                r = e["rect"]
                x0, y0 = Q.p2q(r.x0, r.y0)
                x1, y1 = Q.p2q(r.x1, r.y1)
                _PAREDES.append((min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)))
    return _PAREDES


def P_(escala, origem):
    return lambda x, y: (int(round((x - origem[0]) * escala)), int(round((y - origem[1]) * escala)))


def tapete(img, escala, origem):
    """O canto do tapete: à esquerda da madeira do sofá e fora da mesinha, tudo (o tapete, o retângulo claro, a sombra
    solta e o piso acima da borda) recebe o tapete da mesma linha mais à esquerda; a mesinha e o sofá ficam."""
    t = TAPETE
    P = P_(escala, origem)
    A0, B0 = P(t["caixa"][0], t["caixa"][1])
    A1, B1 = P(t["caixa"][2], t["caixa"][3])
    d = int(round(t["dx"] * escala))
    reg = img[B0:B1, A0:A1].astype(np.float32)
    src = img[B0:B1, A0 + d:A1 + d].astype(np.float32)
    H, W = reg.shape[:2]
    xs = origem[0] + (np.arange(A0, A1) + 0.5) / escala
    ys = origem[1] + (np.arange(B0, B1) + 0.5) / escala
    X, Y = np.meshgrid(xs, ys)
    (ax, ay), (bx, by) = t["sofa"]
    lado = (bx - ax) * (Y - ay) - (by - ay) * (X - ax)          # > 0: à esquerda da linha do sofá (descendo)
    cx, cy, cr = t["mesinha"]
    ok = (lado > 0) & (np.hypot(X - cx, Y - cy) > cr)
    b_, r_ = reg[..., 0], reg[..., 2]
    madeira = cv2.dilate(((r_ - b_) > 45).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    ok &= ~madeira
    a = ok.astype(np.float32)
    m = max(1, int(round(1.5 * escala)))
    a[:, :m] *= np.linspace(0, 1, m, dtype=np.float32)[None, :]
    a[-m:] *= np.linspace(1, 0, m, dtype=np.float32)[:, None]
    a = cv2.GaussianBlur(a, (0, 0), max(0.5, 0.35 * escala)) * ok
    img[B0:B1, A0:A1] = np.clip(reg * (1 - a[..., None]) + src * a[..., None], 0, 255).astype(np.uint8)
    print(f"      tapete: {int((a > 0.5).sum())} px refeitos")
    return img


def aparador(img, escala, origem):
    """O aparador num tom sólido: a madeira achada na busca (a maior mancha amadeirada), o retângulo dela até o pé, no
    tom do miolo; a borda com o piso fica suave."""
    v = APARADOR
    P = P_(escala, origem)
    A0, B0 = P(v["busca"][0], v["busca"][1])
    A1, B1 = P(v["busca"][2], v["fundo"])
    reg = img[B0:B1, A0:A1].astype(np.float32)
    madeira = (((reg[..., 2] - reg[..., 0]) > 28) & (reg.mean(2) > 100)).astype(np.uint8)
    madeira = cv2.morphologyEx(madeira, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(madeira)
    i = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    x, y, w, h = st[i, :4]
    # o retângulo: as colunas e linhas com madeira na maior parte (sem as pontas soltas)
    col = (lab == i).mean(0)
    lin = (lab == i).mean(1)
    xs = np.where(col > 0.5 * col.max())[0]
    ys = np.where(lin > 0.5 * lin.max())[0]
    x0, x1, y0 = xs.min(), xs.max() + 1, ys.min()
    y1 = reg.shape[0]
    mx, my = max(2, int(round(2.5 * escala))), max(2, int(round(2.5 * escala)))
    miolo = reg[y0 + my:y1 - my, x0 + mx:x1 - mx].reshape(-1, 3)
    cor = np.median(miolo, axis=0)
    # um leve da textura do miolo (o desvio suavizado), sem as linhas
    novo = np.empty_like(reg[y0:y1, x0:x1])
    novo[:] = cor
    a = np.zeros(reg.shape[:2], np.float32)
    a[y0:y1, x0:x1] = 1.0
    a = cv2.GaussianBlur(a, (0, 0), max(0.4, 0.3 * escala))
    a[y0:y1, x0:x1] = np.maximum(a[y0:y1, x0:x1], 0.0)
    alvo = reg.copy()
    alvo[y0:y1, x0:x1] = novo
    # fora do retângulo, onde a borda suaviza, a cor sólida entra só pela máscara suavizada
    fora = np.ones(reg.shape[:2], bool)
    fora[y0:y1, x0:x1] = False
    alvo[fora] = cor
    out = reg * (1 - a[..., None]) + alvo * a[..., None]
    img[B0:B1, A0:A1] = np.clip(out, 0, 255).astype(np.uint8)
    X0 = origem[0] + (A0 + x0) / escala
    X1 = origem[0] + (A0 + x1) / escala
    Y0 = origem[1] + (B0 + y0) / escala
    print(f"      aparador: ({X0:.1f}, {Y0:.1f}) a ({X1:.1f}, {v['fundo']}); tom {cor.round()}")
    return img


def porta(img, nome, escala, origem):
    p = PORTAS[nome]
    P = P_(escala, origem)
    x0, y0, x1, y1 = p["caixa"]
    A0, B0 = P(x0, y0)
    A1, B1 = P(x1, y1)
    H, W = B1 - B0, A1 - A0
    dx, dy = int(round(p["desloc"][0] * escala)), int(round(p["desloc"][1] * escala))
    reg = img[B0:B1, A0:A1].astype(np.float32)
    src = img[B0 + dy:B1 + dy, A0 + dx:A1 + dx].astype(np.float32)
    if p.get("nivel"):      # a sombra do piso rente à parede: a fonte leva o tom de cada coluna, medido logo acima
        n0, n1 = P(0, p["nivel"][0])[1], P(0, p["nivel"][1])[1]
        alvo = img[n0:n1, A0:A1].astype(np.float32).mean(0)
        fonte = img[n0:n1, A0 + dx:A1 + dx].astype(np.float32).mean(0)
        src = src * np.clip(alvo / np.maximum(fonte, 1.0), 0.8, 1.2)[None, :, :]
    # as paredes: o cinza escuro grosso (as linhas finas, como os contornos antigos, saem na abertura) dentro das
    # paredes do PDF (com folga de 1,5 px)
    escuro = ((reg.mean(2) < 95) & (reg.max(2) - reg.min(2) < 35)).astype(np.uint8)
    k = max(2, int(round(1.6 * escala)))
    grosso = cv2.morphologyEx(escuro, cv2.MORPH_OPEN, np.ones((k, k), np.uint8)).astype(bool)
    pdf = np.zeros((H, W), np.uint8)
    for wx0, wy0, wx1, wy1 in paredes():
        if wx1 < x0 - 2 or wx0 > x1 + 2 or wy1 < y0 - 2 or wy0 > y1 + 2:
            continue
        a0, b0 = P(wx0 - 0.8, wy0 - 0.8)
        a1, b1 = P(wx1 + 0.8, wy1 + 0.8)
        pdf[max(b0 - B0, 0):max(b1 - B0, 0), max(a0 - A0, 0):max(a1 - A0, 0)] = 1
    parede = grosso & pdf.astype(bool)
    parede = cv2.dilate(parede.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    a = (~parede).astype(np.float32)
    m = max(1, int(round(0.8 * escala)))
    if dx:          # a fonte vem de um lado: esfuma em cima e embaixo (as estruturas horizontais seguem) e do lado dela
        a[:m] *= np.linspace(0, 1, m, dtype=np.float32)[:, None]
        a[-m:] *= np.linspace(1, 0, m, dtype=np.float32)[:, None]
        mh = max(1, int(round(2.0 * escala)))
        if dx < 0:
            a[:, :mh] *= np.linspace(0, 1, mh, dtype=np.float32)[None, :]
        else:
            a[:, -mh:] *= np.linspace(1, 0, mh, dtype=np.float32)[None, :]
    else:
        a[:, :m] *= np.linspace(0, 1, m, dtype=np.float32)[None, :]
        a[:, -m:] *= np.linspace(1, 0, m, dtype=np.float32)[None, :]
    a *= ~parede
    img[B0:B1, A0:A1] = np.clip(reg * (1 - a[..., None]) + src * a[..., None], 0, 255).astype(np.uint8)
    if p.get("pintar"):     # a peça fina de parede do PDF (o batente) num retângulo limpo, no cinza da parede ao lado
        r0, s0 = P(p["parede_ref"][0], p["parede_ref"][1])
        r1, s1 = P(p["parede_ref"][2], p["parede_ref"][3])
        cor = np.median(img[s0:s1, r0:r1].reshape(-1, 3), axis=0)
        for px0, py0, px1, py1 in p["pintar"]:
            c0, d0 = P(px0, py0)
            c1, d1 = P(px1, py1)
            img[d0:d1, c0:c1] = cor.astype(np.uint8)
    traco = 0.5 if escala <= 1.5 else min(0.5, EP.TRACO_12K / escala)
    img = VC.redesenhar(img, [p["folha"]], escala=escala, origem=origem, traco=traco, inpaint=False)
    print(f"      porta {nome}: {int((a > 0.5).sum())} px de piso; folha {p['folha']}")
    return img


def piso_qmot(img, escala, origem):
    """O piso do Q. MOTORISTA (12K): fora da faixa texturizada, o piso recebe a própria faixa, espelhada em tiras da
    largura dela (as listras horizontais seguem); nas linhas do rótulo, a faixa vem de mais acima. A cama, o armário, as
    letras, as paredes e a folha da porta ficam."""
    v = QMOT
    P = P_(escala, origem)
    A0, B0 = P(v["quarto"][0], v["quarto"][1])
    A1, B1 = P(v["quarto"][2], v["quarto"][3])
    F0, F1 = P(v["faixa"][0], 0)[0], P(v["faixa"][1], 0)[0]
    Wf = F1 - F0
    H, W = B1 - B0, A1 - A0
    reg = img[B0:B1, A0:A1].astype(np.float32)
    xs = np.arange(A0, A1)
    u = np.mod(xs - F0, 2 * Wf)
    sx = F0 + np.where(u < Wf, u, 2 * Wf - 1 - u)                   # a faixa espelhada
    ys = np.arange(B0, B1)
    yf = origem[1] + (ys + 0.5) / escala
    sobe = int(round(v["sobe"] * escala))
    sy = np.where((yf >= v["letras"][0]) & (yf <= v["letras"][1]), ys - sobe, ys)
    src = img[sy[:, None], sx[None, :]].astype(np.float32)
    L = reg.mean(2)
    proteg = (L < 75) | (L > 165)                                     # paredes, linhas, letras, a folha nova
    letras = cv2.dilate((L > 185).astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    proteg |= letras
    for nome in ("cama", "armario"):
        c0, d0 = P(v[nome][0], v[nome][1])
        c1, d1 = P(v[nome][2], v[nome][3])
        proteg[max(d0 - B0, 0):max(d1 - B0, 0), max(c0 - A0, 0):max(c1 - A0, 0)] = True
    na_faixa = (xs >= F0 + 2) & (xs < F1 - 2)
    alvo = ~proteg & ~na_faixa[None, :]
    a = cv2.GaussianBlur(alvo.astype(np.float32), (0, 0), max(0.5, 0.5 * escala)) * alvo
    img[B0:B1, A0:A1] = np.clip(reg * (1 - a[..., None]) + src * a[..., None], 0, 255).astype(np.uint8)
    print(f"      piso do Q. MOTORISTA: {int((a > 0.5).sum())} px")
    return img


def item(img, nome, escala=1.0, origem=(0.0, 0.0)):
    if nome == "tapete":
        return tapete(img, escala, origem)
    if nome == "aparador":
        return aparador(img, escala, origem)
    if nome == "piso_qmot":
        return piso_qmot(img, escala, origem)
    for p in GRUPO[nome]:
        img = porta(img, p, escala, origem)
    return img


def main():
    c, pav = PLANTA.split("_")
    base = cv2.imread(str(EP.PROJ / EP.PLANTAS[PLANTA][0]))
    for f in EP.PLANTAS[PLANTA]:
        im = cv2.imread(str(EP.PROJ / f))
        for nome in ITENS:
            if nome not in SO_12K:
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
            mapa, cc = EP.registro_12k(base, cinza, dz, (int(x0) - 60, int(y0) - 60, int(x1) + 60, int(y1) + 60))
            A, B = mapa(x0, y0)
            sx = (mapa(x0 + 1000.0, y0)[0] - A) / 1000.0
            im = item(im, nome, sx, (x0 - A / sx, y0 - B / sx))
            print(f"   {op}: {nome} (registro {cc:.3f}, escala {sx:.3f})")
        Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).save(rel, quality=95, subsampling=0, dpi=dpi)
        del im, cinza


if __name__ == "__main__":
    main()

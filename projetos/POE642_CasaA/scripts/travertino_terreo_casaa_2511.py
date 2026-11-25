"""Casa A Térreo: o travertino bruto novo (25/11).

Usuário: "vamos revisar o piso de travertino bruto. traga me 3 opções para utilizar, pois o que está inserido não ficou
bom". As 3 texturas (vista de cima, sem juntas) saíram do Higgsfield (`_texturas/travertino_opcoes_2511`) e foram
aplicadas na varanda, nas salas e no jantar (`renders/POE642_CasaA_PH_Terreo_2511_travertino_opcoes.jpg`). Escolhas:
"vamos usar esse nos pisos onde for travertino bruto" (a opção 2, travertino Navona marfim, veio suave) e "esse tom para
bancadas no travertino" (a opção 3, travertino em corte transversal, o fiorito).

- Piso: o travertino da final é o creme claro de Lab ~ (225, 130, 135) (varanda, salas, jantar, halls, escritório,
  lavabo, banhos, lavatório e área gourmet; o Bege Bahia da piscina e do pergolado é mais amarelo e fica). Esses px, nos
  corpos grandes, recebem a textura da opção 2 (1,2 m por quadro, espelhada, as faixas do veio na horizontal) vezes a
  luz do lugar (a luminância do piso antigo, bem desfocada, relativa à mediana): as sombras dos móveis ficam; o
  tracejado, os rótulos, os móveis e as paredes ficam (não têm a cor do piso). A cama do Q. MOTORISTA e a escada caracol
  (claras) ficam de fora; os restos do piso antigo junto às paredes e às bancadas (mais claros ou mais acinzentados)
  entram pela borda (`borda_velha`). No 12K, o mesmo teste de cor, só perto do piso achado na final (o mapa de `doze_k.json`).
- Bancada: a do lavabo (a única de travertino do Térreo) recebe a textura da opção 3 vezes a luz dela (a cuba esculpida
  com a sombra da bacia junto); a torneira (cinza) fica.

Final, prancha e 12K A e B.

  python3 travertino_terreo_casaa_2511.py
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
TEX = EP.PROJ / "_texturas/travertino_opcoes_2511"
PISO = dict(textura="travertino_opcao_2.png", m=1.2, ref=(225.0, 130.0, 135.0), peso=(0.35, 1.6, 1.6), lim=9.0,
            lim_borda=12.0, area_min=3000, luz_sig=4.0,
            fora=[(2392.0, 1115.0, 2451.0, 1235.0),      # a cama do Q. MOTORISTA
                  (1905.0, 1560.0, 1995.0, 1650.0)])     # a escada caracol
BANCADAS = [dict(caixa=(2316.0, 410.0, 2345.5, 515.5), textura="travertino_opcao_3.png", m=0.6)]   # lavabo
PX_M = 59.7059


def tex_tile(nome, lado):
    T = cv2.imread(str(TEX / nome)).astype(np.float32)
    T = cv2.resize(T, (lado, lado), interpolation=cv2.INTER_AREA)
    T2 = np.concatenate([T, T[:, ::-1]], 1)
    return np.concatenate([T2, T2[::-1]], 0)            # espelhada: sem emenda


def textura_em(T2, X, Y):
    """A textura espelhada nas coordenadas (px da imagem) X (colunas) e Y (linhas)."""
    p = T2.shape[0]
    return T2[np.mod(Y, p)[:, None], np.mod(X, p)[None, :]]


def mascara_cor(img):
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    dE = np.sqrt(((lab - np.float32(PISO["ref"])) ** 2 * np.float32(PISO["peso"])).sum(2))
    return dE


def borda_velha(img, m, dE, escala):
    """Os restos do piso antigo junto às paredes e às bancadas (mais claros ou mais acinzentados que o miolo, fora do teste
    estrito): perto do piso achado (6 px da final), no creme do travertino antigo (b de Lab < 138: as almofadas creme
    passam de 139) e claros (o tapete cinza e as sombras fortes ficam)."""
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    r = max(1, int(round(6 * escala)))
    perto = cv2.dilate(m.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))).astype(bool)
    return perto & (dE < 14.0) & (lab[..., 2] < 138) & (lab[..., 0] > 175)


def mascara_final(img):
    dE = mascara_cor(img)
    c = (dE < PISO["lim"]).astype(np.uint8)
    c = cv2.morphologyEx(c, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(c, 8)
    keep = np.zeros(n, bool)
    keep[1:] = st[1:, cv2.CC_STAT_AREA] > PISO["area_min"]
    m = keep[lab]
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8)).astype(bool) & (dE < PISO["lim_borda"])
    m |= borda_velha(img, m, dE, 1.0)
    for x0, y0, x1, y1 in PISO["fora"]:
        m[int(y0):int(y1), int(x0):int(x1)] = False
    return m


def piso(img, m, escala, X0=0, Y0=0, T2=None):
    """O piso novo nos px m (a imagem é um recorte que começa em X0, Y0 no sistema de px da imagem inteira)."""
    L = img.astype(np.float32).mean(2)
    sig = PISO["luz_sig"] * escala
    w = cv2.GaussianBlur(m.astype(np.float32), (0, 0), sig)
    Lb = cv2.GaussianBlur(np.where(m, L, 0).astype(np.float32), (0, 0), sig) / np.maximum(w, 1e-3)
    med = np.median(Lb[m]) if m.any() else 1.0
    sh = Lb / med
    H, W = m.shape
    TT = textura_em(T2, np.arange(X0, X0 + W), np.arange(Y0, Y0 + H))
    novo = TT * sh[..., None]
    a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), max(0.5, 0.35 * escala)) * m
    return np.clip(img * (1 - a[..., None]) + novo * a[..., None], 0, 255).astype(np.uint8), med


def bancadas(img, escala, origem):
    for bnc in BANCADAS:
        x0, y0, x1, y1 = bnc["caixa"]
        A0, B0 = int(round((x0 - origem[0]) * escala)), int(round((y0 - origem[1]) * escala))
        A1, B1 = int(round((x1 - origem[0]) * escala)), int(round((y1 - origem[1]) * escala))
        reg = img[B0:B1, A0:A1].astype(np.float32)
        quente = (reg[..., 2] - reg[..., 0]) > 15                       # a pedra (a torneira é cinza)
        L = reg.mean(2)
        sh = L / max(float(np.median(L[quente])), 1.0)
        T2 = tex_tile(bnc["textura"], max(8, int(round(bnc["m"] * PX_M * escala))))
        TT = textura_em(T2, np.arange(A1 - A0), np.arange(B1 - B0))
        a = cv2.GaussianBlur(quente.astype(np.float32), (0, 0), max(0.4, 0.3 * escala)) * quente
        img[B0:B1, A0:A1] = np.clip(reg * (1 - a[..., None]) + TT * sh[..., None] * a[..., None], 0, 255).astype(np.uint8)
    return img


def main():
    c, pav = PLANTA.split("_")
    base = cv2.imread(str(EP.PROJ / EP.PLANTAS[PLANTA][0]))
    m_final = mascara_final(base)
    T2f = tex_tile(PISO["textura"], int(round(PISO["m"] * PX_M)))
    for f in EP.PLANTAS[PLANTA]:
        im = cv2.imread(str(EP.PROJ / f))
        m = mascara_final(im)
        im, med = piso(im, m, 1.0, T2=T2f)
        im = bancadas(im, 1.0, (0.0, 0.0))
        cv2.imwrite(str(EP.PROJ / f), im)
        if f == EP.PLANTAS[PLANTA][0]:
            novo = im
        print(f, "piso:", int(m.sum()), "px")
    pf = EP.PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_entrega.png"
    pr = cv2.imread(str(pf))
    pr[:2160] = novo
    cv2.imwrite(str(pf), pr)
    dz = json.loads((EP.PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[PLANTA]
    s, x0, y0 = dz["s"], dz["x0"], dz["y0"]
    perto = cv2.dilate(m_final.astype(np.uint8), np.ones((7, 7), np.uint8))
    T2k = tex_tile(PISO["textura"], int(round(PISO["m"] * PX_M * s)))
    for op in "AB":
        rel = EP.PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_12K_opcao_{op}.jpg"
        pil = Image.open(rel)
        dpi = pil.info.get("dpi", (743, 743))
        im = cv2.cvtColor(np.array(pil.convert("RGB")), cv2.COLOR_RGB2BGR)
        del pil
        H, W = im.shape[:2]
        faixa, sobra = 1400, 120
        tot = 0
        for b0 in range(0, H, faixa):
            r0, r1 = max(0, b0 - sobra), min(H, b0 + faixa + sobra)
            reg = im[r0:r1].copy()
            M = np.float32([[s, 0, -x0 * s], [0, s, -y0 * s - r0]])
            pm = cv2.warpAffine(perto, M, (W, r1 - r0), flags=cv2.INTER_NEAREST).astype(bool)
            dE = mascara_cor(reg)
            m = pm & (dE < PISO["lim"])
            m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)).astype(bool)
            m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)).astype(bool) & pm & (dE < PISO["lim_borda"])
            m |= borda_velha(reg, m, dE, s) & pm
            novo_r, _ = piso(reg, m, s, X0=0, Y0=r0, T2=T2k)
            a, bb = b0 - r0, min(b0 + faixa, H) - r0
            im[b0:min(b0 + faixa, H)] = novo_r[a:bb]
            tot += int(m[a:bb].sum())
            del reg, novo_r, m, dE, pm
        cinza = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        for bnc in BANCADAS:
            bx0, by0, bx1, by1 = bnc["caixa"]
            mapa, cc = EP.registro_12k(base, cinza, dz, (int(bx0) - 60, int(by0) - 60, int(bx1) + 60, int(by1) + 60))
            A, B = mapa(bx0, by0)
            sx = (mapa(bx0 + 1000.0, by0)[0] - A) / 1000.0
            im = bancadas(im, sx, (bx0 - A / sx, by0 - B / sx))
        del cinza
        Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).save(rel, quality=95, subsampling=0, dpi=dpi)
        print(rel.name, "piso:", tot, "px")
        del im


if __name__ == "__main__":
    main()

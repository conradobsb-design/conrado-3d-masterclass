"""Casa C Térreo (26/11): o piso de travertino refeito, sem os poros cinza do piso antigo.

Usuário (vendo o Térreo da Casa C): "não gostei muito do piso - refazer o piso travertino". O travertino já é o Navona
marfim aprovado na Casa A (`travertino_casas_2511.py`, 25/11), mas lá a máscara do piso só pega o px no tom do piso
(dE < `lim`): os poros cinza do piso antigo (manchinhas cinza-azuladas de 1 a 4 px da final, que no 12K viram borrões)
ficaram como "objeto" por cima da pedra nova. Aqui o mesmo piso (a mesma textura, nas mesmas coordenadas, a mesma luz
do lugar) é refeito com a máscara completada: os buracos pequenos dentro do piso (até `poro_area` px da final, mais
claros que as letras e quase sem cor) entram como piso. Ficam as letras e os números dos rótulos (escuros), as linhas e
os pontos pretos, os tracejados (nas caixas de `PROTEGER`: a claraboia da varanda master e a do box do BH master 1),
os móveis, os tapetes e as paredes.

Final, prancha e 12K A e B (no 12K, perto do piso achado na final, pelo mapa de `doze_k.json`, como em 25/11).

  python3 travertino_casac_2611.py
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
sys.path.insert(0, str(Path(__file__).resolve().parent))
import esquadrias_pretas_1911 as EP          # noqa: E402
import travertino_terreo_casaa_2511 as TV    # noqa: E402
import travertino_casas_2511 as TC           # noqa: E402

PLANTA = "C_Terreo"
PORO = dict(area=14.0, L_min=105.0, croma_max=16.0, anel=0.75)
PROTEGER = [(728.0, 248.0, 960.0, 300.0),          # a claraboia tracejada da varanda master
            (742.0, 346.0, 902.0, 364.0)]          # o tracejado do box do BH master 1


def _protegidos(shape, escala, x0=0.0, y0=0.0, r0=0):
    p = np.zeros(shape, bool)
    for a, b, c, d in PROTEGER:
        A, B = int((a - x0) * escala), int((b - y0) * escala) - r0
        C, D = int((c - x0) * escala) + 1, int((d - y0) * escala) + 1 - r0
        A, C = max(A, 0), min(C, shape[1])
        B, D = max(B, 0), min(D, shape[0])
        if C > A and D > B:
            p[B:D, A:C] = True
    return p


def poros(img, m, area_lim, prot):
    """Os buracos pequenos da máscara do piso, claros e sem cor (os poros do piso antigo)."""
    buraco = (~m).astype(np.uint8)
    n, lb, st, _ = cv2.connectedComponentsWithStats(buraco, 8)
    if n <= 1:
        return np.zeros_like(m)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    L = lab[..., 0]
    croma = np.hypot(lab[..., 1] - 128.0, lab[..., 2] - 128.0)
    area = st[:, cv2.CC_STAT_AREA].astype(np.float64)
    ok = (area <= area_lim)
    ok[0] = False
    # a média de L e da croma por componente
    somaL = np.bincount(lb.ravel(), weights=L.ravel(), minlength=n)
    somaC = np.bincount(lb.ravel(), weights=croma.ravel(), minlength=n)
    minL = np.full(n, 255.0)
    np.minimum.at(minL, lb.ravel(), L.ravel())
    medL = somaL / np.maximum(area, 1)
    medC = somaC / np.maximum(area, 1)
    ok &= (medL > PORO["L_min"]) & (minL > PORO["L_min"] - 25) & (medC < PORO["croma_max"])
    # o anel em volta: quase todo piso (um buraco no meio do travertino, não a borda de uma peça)
    k = np.ones((3, 3), np.uint8)
    cand = ok[lb]
    anel = (cv2.dilate(cand.astype(np.uint8), k) > 0) & ~cand
    lb_d = cv2.dilate(np.where(cand, lb, 0).astype(np.float32), k).astype(np.int64)
    tot = np.bincount(lb_d[anel], minlength=n).astype(np.float64)
    noM = np.bincount(lb_d[anel & m], minlength=n).astype(np.float64)
    ok &= (noM / np.maximum(tot, 1)) >= PORO["anel"]
    p = ok[lb] & ~prot
    return p


def aplicar():
    c, pav = PLANTA.split("_")
    Q = EP.quadro(PLANTA)
    reg = TC.regiao(Q)
    base = cv2.imread(str(EP.PROJ / EP.PLANTAS[PLANTA][0]))
    ref = TC.referencia(base, reg)
    m_final = TC.mascara_final(base, reg, ref)
    lado = int(round(TV.PISO["m"] * Q.px_m))
    T2f = TC.tex(lado)
    novo = None
    for f in EP.PLANTAS[PLANTA]:
        im = cv2.imread(str(EP.PROJ / f))
        m = TC.mascara_final(im, reg, ref) if f != EP.PLANTAS[PLANTA][0] else m_final
        p = poros(im, m, PORO["area"], _protegidos(m.shape, 1.0))
        print(f"   final: poros {int(p.sum())} px")
        im, _ = TV.piso(im, m | p, 1.0, T2=T2f)
        cv2.imwrite(str(EP.PROJ / f), im)
        if novo is None:
            novo = im
    pf = EP.PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_entrega.png"
    pr = cv2.imread(str(pf))
    pr[:2160] = novo
    cv2.imwrite(str(pf), pr)
    dz = json.loads((EP.PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[PLANTA]
    s, x0, y0 = dz["s"], dz["x0"], dz["y0"]
    perto = cv2.dilate(m_final.astype(np.uint8), np.ones((7, 7), np.uint8))
    lado_k = int(round(TV.PISO["m"] * Q.px_m * s))
    T2k = TC.tex(lado_k)
    for op in "AB":
        rel = EP.PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_12K_opcao_{op}.jpg"
        pil = Image.open(rel)
        dpi = pil.info.get("dpi", (743, 743))
        im = cv2.cvtColor(np.array(pil.convert("RGB")), cv2.COLOR_RGB2BGR)
        del pil
        H, W = im.shape[:2]
        faixa, sobra = 1400, 120
        tot = totp = 0
        for b0 in range(0, H, faixa):
            r0, r1 = max(0, b0 - sobra), min(H, b0 + faixa + sobra)
            sub = im[r0:r1].copy()
            M = np.float32([[s, 0, -x0 * s], [0, s, -y0 * s - r0]])
            pm = cv2.warpAffine(perto, M, (W, r1 - r0), flags=cv2.INTER_NEAREST).astype(bool)
            if not pm.any():
                continue
            d, lab = TC.dE(sub, ref)
            m = pm & (d < TC.P["lim"])
            m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)).astype(bool)
            m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)).astype(bool)
            m &= pm & (d < TC.P["lim_borda"])
            m |= TC.borda_velha(m, d, lab, ref, s) & pm
            prot = _protegidos(m.shape, s, x0, y0, r0)
            p = poros(sub, m, PORO["area"] * s * s, prot) & pm
            novo_r, _ = TV.piso(sub, m | p, s, X0=0, Y0=r0, T2=T2k)
            a, bb = b0 - r0, min(b0 + faixa, H) - r0
            im[b0:min(b0 + faixa, H)] = novo_r[a:bb]
            tot += int(m[a:bb].sum())
            totp += int(p[a:bb].sum())
            del sub, novo_r, m, d, lab, pm
        Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).save(rel, quality=95, subsampling=0, dpi=dpi)
        print(f"   {rel.name}: piso {tot} px, poros {totp} px")
        del im


if __name__ == "__main__":
    aplicar()

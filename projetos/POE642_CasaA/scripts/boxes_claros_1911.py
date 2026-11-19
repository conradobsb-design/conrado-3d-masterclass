"""Os boxes no vidro claro (19/11, conferência planta a planta).

Usuário: "garanta que as esquadrias tenham contorno fino preto. já os vidros e boxes, devem ser claros." (e, em 14/11:
"ESSE É O ESTILO DE BOX DE CHUVEIRO ... PARA TODOS OS BANHEIROS. NADA DE ESQUADRIA PRETA").

Na conferência, os boxes que ainda estavam como um traço escuro (o cinza da parede, de 12/11) passam ao box padrão
(`final3840_casab.BOXES_VIDRO`): a faixa de vidro claro de 2,4 px, as duas faces em fio cinza de 0,45 px e a sombra
curta. O traço escuro sai (a faixa de vidro o cobre; o que sobra em volta é preenchido pelo piso do lado).

Cada box é dado por uma caixa de busca (px da final) e o eixo; o centro e o comprimento do traço (de face a face das
paredes) são achados na própria final. Vale na final (e nas variantes), na prancha e nos 12K A e B (pelo registro de
`piscinas_sobrias_1911.registro_12k`).

  python3 boxes_claros_1911.py A_Subsolo [--antes_depois]
"""
import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
AQUI = Path(__file__).resolve().parent
PROJ = AQUI.parents[1]
sys.path.insert(0, str(AQUI))

VIDRO = {"vidro": (218, 214, 204), "face": (104, 108, 112), "face_px": 0.45, "larg_px": 2.6, "sombra": 0.20}
# (caixa de busca x0, y0, x1, y1 em px da final; "h" ou "v"): o traço do box passa dentro da caixa, de parede a parede
BOXES = {
    "A_Subsolo": [((1100, 936, 1200, 952), "h"),      # BH serv.
                  ((1380, 1566, 1485, 1582), "h"),    # a ducha da sauna
                  ((1630, 1505, 1646, 1640), "v")],   # BH fem.
}


def achar(img, caixa, eixo, lum_max=150):
    """O traço escuro na caixa: (centro, início, fim) no eixo; o comprimento só onde o traço é fino (fora da parede)."""
    x0, y0, x1, y1 = caixa
    lum = img.astype(np.float32).mean(2)
    if eixo == "h":
        prof = lum[y0:y1, x0:x1].mean(1)
        c = y0 + int(np.argmin(prof))
        lado = (lum[c - 4, :] > lum_max) & (lum[c + 4, :] > lum_max)    # fora da parede: claro acima e abaixo
        linha = (lum[c, :] < lum_max) & lado
        xs = np.nonzero(linha[x0 - 40:x1 + 40])[0] + x0 - 40
        return c + 0.5, float(xs.min()), float(xs.max() + 1)
    prof = lum[y0:y1, x0:x1].mean(0)
    c = x0 + int(np.argmin(prof))
    if prof[c - x0 + 1] < prof[c - x0 - 1] and prof[c - x0 + 1] < 150:
        cc = c + 1.0                                     # o traço de 2 px: o centro entre as duas colunas
    else:
        cc = c + 0.5
    lado = (lum[:, int(cc) - 4] > lum_max) & (lum[:, int(cc) + 4] > lum_max)
    linha = (lum[:, int(cc)] < lum_max) & lado
    ys = np.nonzero(linha[y0 - 40:y1 + 40])[0] + y0 - 40
    return cc, float(ys.min()), float(ys.max() + 1)


def desenhar(img, box, escala=1.0, origem=(0.0, 0.0), q=VIDRO):
    """O box claro em `img` (BGR uint8), com o box em px da final levado à grade de `img` (escala, origem)."""
    eixo, c, a, b = box
    ss = 8
    larg = q["larg_px"] * escala

    def P(v, o):
        return (v - o) * escala
    if eixo == "h":
        cx0, cx1 = P(a, origem[0]), P(b, origem[0])
        cy = P(c, origem[1])
        u0, u1, v0, v1 = cx0, cx1, cy - larg / 2, cy + larg / 2
    else:
        cy0, cy1 = P(a, origem[1]), P(b, origem[1])
        cx = P(c, origem[0])
        u0, u1, v0, v1 = cx - larg / 2, cx + larg / 2, cy0, cy1
    m_ = int(np.ceil(4 * escala)) + 2
    X0, Y0 = max(int(u0) - m_, 0), max(int(v0) - m_, 0)
    X1, Y1 = min(int(np.ceil(u1)) + m_, img.shape[1]), min(int(np.ceil(v1)) + m_, img.shape[0])
    w, h = X1 - X0, Y1 - Y0
    reg = img[Y0:Y1, X0:X1].copy()
    # o traço escuro que fica fora da faixa: o piso do lado (inpaint) só nos px escuros perto do eixo
    lum = reg.astype(np.float32).mean(2)
    perto = np.zeros((h, w), np.uint8)
    e = 1.6 * escala
    cv2.rectangle(perto, (int(u0 - X0 - e), int(v0 - Y0 - e)), (int(u1 - X0 + e), int(v1 - Y0 + e)), 1, -1)
    escuro = ((lum < 150) & (perto > 0)).astype(np.uint8)
    if escuro.any():
        reg = cv2.inpaint(reg, escuro, max(2, int(round(2 * escala))), cv2.INPAINT_TELEA)
    m = np.zeros((h * ss, w * ss), np.uint8)
    c0, r0, c1, r1 = [int(round(v * ss)) for v in (u0 - X0, v0 - Y0, u1 - X0, v1 - Y0)]
    cv2.rectangle(m, (c0, r0), (c1 - 1, r1 - 1), 255, -1)
    lt = max(1, int(round(q["face_px"] * escala * ss)))
    faces = np.zeros_like(m)
    if eixo == "h":
        faces[r0:r0 + lt, c0:c1] = 255
        faces[r1 - lt:r1, c0:c1] = 255
    else:
        faces[r0:r1, c0:c0 + lt] = 255
        faces[r0:r1, c1 - lt:c1] = 255

    def reduzir(x):
        return cv2.resize(x.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)
    av, af = reduzir(m), reduzir(faces)
    out = reg.astype(np.float32)
    d = 0.9 * escala
    sb = cv2.GaussianBlur(cv2.warpAffine(av, np.float32([[1, 0, -d], [0, 1, d]]), (w, h)), (0, 0), 0.8 * escala)
    out *= (1 - q["sombra"] * sb * (1 - av))[..., None]
    out = out * (1 - av[..., None]) + np.float32(q["vidro"]) * av[..., None]
    out = out * (1 - af[..., None]) + np.float32(q["face"]) * af[..., None]
    img[Y0:Y1, X0:X1] = np.clip(np.round(out), 0, 255).astype(np.uint8)
    return img


def finais(planta):
    import esquadrias_pretas_1911 as EP
    return EP.PLANTAS[planta]


def aplicar(planta, so_antes_depois=False):
    import piscinas_sobrias_1911 as PS
    c, pav = planta.split("_")
    fs = finais(planta)
    base = cv2.imread(str(PROJ / fs[0]))
    boxes = []
    for caixa, eixo in BOXES[planta]:
        cc, a, b = achar(base, caixa, eixo)
        boxes.append((eixo, cc, a, b))
        print(f"   box {eixo} em {cc:.1f}, de {a:.0f} a {b:.0f}")
    novo = base.copy()
    for bx in boxes:
        novo = desenhar(novo, bx)
    if so_antes_depois:
        return base, novo, boxes
    cv2.imwrite(str(PROJ / fs[0]), novo)
    for f in fs[1:]:
        im = cv2.imread(str(PROJ / f))
        for bx in boxes:
            im = desenhar(im, bx)
        cv2.imwrite(str(PROJ / f), im)
    pf = PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_entrega.png"
    pr = cv2.imread(str(pf))
    pr[:2160] = novo
    cv2.imwrite(str(pf), pr)
    dz = json.loads((PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[planta]
    xs = [v for bx in boxes for v in ((bx[2], bx[3]) if bx[0] == "h" else (bx[1],))]
    ys = [v for bx in boxes for v in ((bx[1],) if bx[0] == "h" else (bx[2], bx[3]))]
    caixa = (max(int(min(xs)) - 80, 0), max(int(min(ys)) - 80, 0), int(max(xs)) + 80, int(max(ys)) + 80)
    for op in "AB":
        f = PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_12K_opcao_{op}.jpg"
        pil = Image.open(f)
        dpi = pil.info.get("dpi", (743, 743))
        im = cv2.cvtColor(np.array(pil.convert("RGB")), cv2.COLOR_RGB2BGR)
        del pil
        mapa, cc = PS.registro_12k(base, cv2.cvtColor(im, cv2.COLOR_BGR2GRAY), dz, caixa)
        X0, Y0 = mapa(0.0, 0.0)
        X1, _ = mapa(1000.0, 0.0)
        s = (X1 - X0) / 1000.0
        for bx in boxes:
            im = desenhar(im, bx, escala=s, origem=(-X0 / s, -Y0 / s))
        Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).save(f, quality=95, subsampling=0, dpi=dpi)
        print(f"   {f.name} registro {cc:.4f}")
        del im
    return base, novo, boxes


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("planta")
    ap.add_argument("--antes_depois", action="store_true")
    a = ap.parse_args()
    antes, depois, boxes = aplicar(a.planta, a.antes_depois)
    tiles = []
    for eixo, cc, a0, b0 in boxes:
        if eixo == "h":
            X0, X1, Y0, Y1 = int(a0) - 15, int(b0) + 15, int(cc) - 18, int(cc) + 18
        else:
            X0, X1, Y0, Y1 = int(cc) - 18, int(cc) + 18, int(a0) - 15, int(b0) + 15
        p = np.hstack([antes[Y0:Y1, X0:X1], np.full((Y1 - Y0, 3, 3), 255, np.uint8), depois[Y0:Y1, X0:X1]]) \
            if eixo == "h" else np.hstack([antes[Y0:Y1, X0:X1], np.full((Y1 - Y0, 3, 3), 255, np.uint8),
                                           depois[Y0:Y1, X0:X1]])
        k = min(5.0, 700 / max(p.shape[:2]))
        tiles.append(cv2.resize(p, None, fx=k, fy=k, interpolation=cv2.INTER_CUBIC))
    W = max(t.shape[1] for t in tiles)
    fo = np.vstack([cv2.copyMakeBorder(t, 0, 12, 0, W - t.shape[1], cv2.BORDER_CONSTANT, value=(255, 255, 255))
                    for t in tiles])
    out = PROJ / f"POE642_Casa{a.planta[0]}/renders/POE642_Casa{a.planta[0]}_PH_{a.planta[2:]}_1911_boxes_claros_antes_depois.jpg"
    cv2.imwrite(str(out), fo, [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(out)

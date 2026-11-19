"""A água das piscinas mais sóbria, no padrão da Casa E (19/11).

Cliente (Miro, nos Térreos de A a E): "Deixar o tom de azul para a piscina mais sóbrio. Ver exemplo." e, no topo do
quadro, "Usar como referência essa planta baixa para o tom da piscina e a escala e cor da grama.". Usuário: "Vamos
usar o tom de sóbrio que a gente fez na casa E como padrão para todas as piscinas. Que tenham profundidade, né?
Diferentemente das prainhas, do spa, que as partes claras e rasas mantêm-se." e "Opção 2 é a melhor e atende ao
cliente! Fiquemos com ela!" (a amostra `renders/POE642_CasaA_PH_Terreo_1911_piscina_tons_proposta.jpg`).

Só a parte funda da água muda (a opção 2: o matiz 28° para o azul-acinzentado, a saturação pela metade, a
luminosidade a 75%); a prainha, o banco do spa e as outras partes claras e rasas ficam como estão:
- a água: os pixels azul-esverdeados (HSV, matiz 140°-220°, saturação e luminosidade mínimas) nos corpos grandes
  (≥ 4000 px na escala da prancha), o que deixa de fora cadeiras, tapetes e outros objetos azuis;
- a parte funda: a luminosidade suavizada (sigma 10 px na prancha) abaixo do limiar de Otsu da própria água, com uma
  transição suave (logística) entre o fundo e o raso;
- o pastilhado, os reflexos, as bordas e os rótulos ficam (só a cor da água funda muda).

Nos Térreos de A, B, C e D (a água era a mesma, a opção C de 11/11): a final com rótulos (e a B da D), a prancha de
entrega e os 12K A e B (no 12K, o recorte da piscina pelo mapa de `POE642_Book/checklist/dados/doze_k.json`). A Casa E
é o padrão e fica como está. Depois: `pdf_entrega.py` de cada casa, `book_entrega.py` e `conferencia_cliente.py`.

  python3 piscinas_sobrias_1911.py              # as 4 plantas
  python3 piscinas_sobrias_1911.py --antes_depois
"""
import argparse
import json
import subprocess
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
AQUI = Path(__file__).resolve().parent
PROJ = AQUI.parents[1]
CASAS = "ABCD"
OPCAO2 = {"dh": 28, "fs": 0.5, "fv": 0.75}
ANTES = "daba07e"   # o último commit com a água de antes (para o --antes_depois)


# a parte funda de cada planta, em px da prancha (x0, y0, x1, y1, lados): os retângulos da água funda, lidos na
# prancha; o que cai fora da água (a pedra, o deck) sai pela máscara da água. Os `lados` são as divisas com a água rasa
# (l, t, r, b): só elas precisam de precisão e se ajustam sozinhas à linha da mudança de tom (na prancha e no 12K).
FUNDO = {
    "A": [(1080, 495, 1345, 866, "b"),            # piscina (a prainha embaixo)
          (946, 898, 1052, 1016, "ltrb")],        # spa (o banco em volta)
    "B": [(740, 895, 886, 1120, ""),              # piscina, o braço de cima
          (622, 1110, 895, 1372, "r"),            # piscina, o corpo (a prainha à direita)
          (926, 938, 1045, 1062, "ltrb")],        # spa
    "C": [(635, 1474, 1107, 1650, "t"),           # piscina (os degraus e a prainha em cima)
          (960, 1340, 1061, 1441, "ltrb")],       # spa
    "D": [(905, 497, 1096, 980, "r"),             # piscina (a prainha à direita)
          (1144, 849, 1233, 937, "ltrb")],        # spa
}


# os degraus entre a prainha e a parte funda (só na Casa C): x de começo e fim e as linhas de cima de cada degrau (a
# sombra do espelho), a última é o começo da parte funda. O usuário (19/11): "Nessa piscina que tem degraus, tem que
# ter um degradê acinzentado... vai escurecendo de forma proporcional, que vai ficando mais fundo... degrau a degrau."
# Cada degrau leva uma fração igual da opção 2: 1/5, 2/5, 3/5 e 4/5 (a prainha 0, o fundo 1).
DEGRAUS = {"C": (653, 915, [1427, 1439, 1451, 1463, 1475])}


def agua(img, escala=1.0):
    """A água: os pixels azul-esverdeados nos corpos grandes, com os furos (os reflexos brancos e os rótulos)
    fechados."""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    H, S, V = [hsv[..., i] for i in range(3)]
    m = ((H >= 70) & (H <= 110) & (S >= 25) & (V >= 60)).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    keep = np.zeros(n, bool)
    keep[1:] = st[1:, cv2.CC_STAT_AREA] >= 4000 * escala * escala
    m = keep[lab].astype(np.uint8)
    k = max(3, int(5 * escala) | 1)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8))
    # os reflexos que encostam na pedra (entalhes pequenos na beira da água) se fecham; os furos (o que não é água e
    # não se liga à borda do recorte) entram
    fora = np.pad(1 - m, 1, constant_values=1)
    ff = fora.copy()
    cv2.floodFill(ff, np.zeros((ff.shape[0] + 2, ff.shape[1] + 2), np.uint8), (0, 0), 2)
    furo = (ff[1:-1, 1:-1] == 1)
    return (m | furo).astype(np.uint8)


def ajustar(V, ret, escala):
    """Leva cada lado marcado à linha onde o tom sobe do fundo (escuro) para o raso (claro)."""
    x0, y0, x1, y1, lados = ret
    R = int(round(6 * escala)) + 2
    Vf = cv2.GaussianBlur(V.astype(np.float32), (0, 0), max(0.8, 0.8 * escala))
    for lado in lados:
        if lado in "tb":
            a, b = int(x0 + 0.15 * (x1 - x0)), int(x1 - 0.15 * (x1 - x0))
            c = y1 if lado == "b" else y0
            ps = np.arange(max(c - R, 1), min(c + R, V.shape[0] - 1))
            prof = Vf[ps[0] - 1:ps[-1] + 2, a:b].mean(1)
        else:
            a, b = int(y0 + 0.15 * (y1 - y0)), int(y1 - 0.15 * (y1 - y0))
            c = x1 if lado == "r" else x0
            ps = np.arange(max(c - R, 1), min(c + R, V.shape[1] - 1))
            prof = Vf[a:b, ps[0] - 1:ps[-1] + 2].mean(0)
        g = prof[2:] - prof[:-2]               # V(p+1) - V(p-1)
        if lado in "lt":
            g = -g
        k = int(np.argmax(g))
        p = int(ps[k])
        if lado == "b":
            y1 = p
        elif lado == "t":
            y0 = p + 1
        elif lado == "r":
            x1 = p
        else:
            x0 = p + 1
    return x0, y0, x1, y1


def peso_fundo(img, rets, escala=1.0):
    """1 na água funda, 0 no raso; 1 px (na prancha) de esfumado nas divisas com o raso."""
    M = agua(img, escala)
    V = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)[..., 2]
    R = np.zeros(M.shape, np.float32)
    finais = []
    for ret in rets:
        x0, y0, x1, y1 = ajustar(V, ret, escala)
        finais.append((x0, y0, x1, y1))
        R[max(y0, 0):max(y1, 0), max(x0, 0):max(x1, 0)] = 1
    w = cv2.GaussianBlur(R, (0, 0), 0.7 * escala) * M
    return w, M, finais


def sobria(img, rets, escala=1.0, q=OPCAO2):
    w, M, finais = peso_fundo(img, rets, escala)
    return aplicar(img, w, q), finais


def aplicar(img, w, q=OPCAO2):
    """A opção 2 com o peso w (0 = como está, 1 = a opção 2 inteira)."""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 0] = np.mod(hsv[..., 0] + q["dh"] / 2 * w, 180)
    hsv[..., 1] *= 1 - (1 - q["fs"]) * w
    hsv[..., 2] *= 1 - (1 - q["fv"]) * w
    return cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)


def recorte(img, rets, escala=1.0, margem=30):
    """Muda só o recorte em volta das piscinas (os retângulos em coordenadas do recorte)."""
    a0 = max(int(min(r[0] for r in rets) - margem * escala), 0)
    b0 = max(int(min(r[1] for r in rets) - margem * escala), 0)
    a1 = min(int(max(r[2] for r in rets) + margem * escala), img.shape[1])
    b1 = min(int(max(r[3] for r in rets) + margem * escala), img.shape[0])
    loc = [(x0 - a0, y0 - b0, x1 - a0, y1 - b0, l) for x0, y0, x1, y1, l in rets]
    novo, finais = sobria(img[b0:b1, a0:a1], loc, escala)
    return (a0, b0, a1, b1), novo, [(x0 + a0, y0 + b0, x1 + a0, y1 + b0) for x0, y0, x1, y1 in finais]


def registro_12k(pr, cinza12, dz, box):
    """O ajuste fino da prancha para o 12K em volta das piscinas (o mapa de `doze_k.json` mais uma afim pequena
    achada por ECC): devolve a função que leva (x, y) da prancha a (X, Y) do 12K."""
    s = dz["s"]
    x0, y0, x1, y1 = box
    a = cv2.cvtColor(pr[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY).astype(np.float32)
    X0, Y0, X1, Y1 = [int(round((v - d) * s)) for v, d in zip(box, (dz["x0"], dz["y0"]) * 2)]
    b = cv2.resize(cinza12[Y0:Y1, X0:X1], (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA).astype(np.float32)
    a, b = cv2.GaussianBlur(a, (0, 0), 1.5), cv2.GaussianBlur(b, (0, 0), 1.5)
    W = np.eye(2, 3, dtype=np.float32)
    cc, W = cv2.findTransformECC(a, b, W, cv2.MOTION_AFFINE,
                                 (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-6), None, 5)

    def f(x, y):
        u, v = W @ np.array([x - x0, y - y0, 1.0])
        return X0 + u * (X1 - X0) / (x1 - x0), Y0 + v * (Y1 - Y0) / (y1 - y0)
    return f, cc


def peso_degraus(forma, x0, x1, ys, escala=1.0):
    n = len(ys) - 1
    w = np.zeros(forma, np.float32)
    for k in range(n):
        w[max(int(round(ys[k])), 0):max(int(round(ys[k + 1])), 0), max(int(round(x0)), 0):max(int(round(x1)), 0)] = (k + 1) / (n + 1)
    return cv2.GaussianBlur(w, (0, 0), 0.7 * escala)


def degrade(img, x0, x1, ys, escala=1.0, margem=30):
    """O degradê degrau a degrau, só na água (o recorte em volta dos degraus)."""
    a0, b0 = max(int(x0 - margem * escala), 0), max(int(ys[0] - margem * escala), 0)
    a1, b1 = min(int(x1 + margem * escala), img.shape[1]), min(int(ys[-1] + margem * escala), img.shape[0])
    cr = img[b0:b1, a0:a1]
    w = peso_degraus(cr.shape[:2], x0 - a0, x1 - a0, [y - b0 for y in ys], escala) * agua(cr, escala)
    img[b0:b1, a0:a1] = aplicar(cr, w)


def degraus(c):
    """O degradê nos degraus da planta c: prancha, finais e 12K A e B (pulado se já feito)."""
    if c not in DEGRAUS:
        return
    x0, x1, ys = DEGRAUS[c]
    ent = PROJ / f"POE642_Casa{c}/entrega"
    ren = PROJ / f"POE642_Casa{c}/renders"
    prancha = ent / f"POE642_Casa{c}_PH_Terreo_entrega.png"
    pr = cv2.imread(str(prancha))
    ult = cv2.cvtColor(pr[ys[-2] + 3:ys[-1] - 3, x0 + 15:x1 - 15], cv2.COLOR_BGR2HSV)[..., 1]
    if np.median(ult) < 65:      # o último degrau já desbotado (saturação ~49; antes ~81)
        print(c, "degraus já feitos; nada feito")
        return
    orig = pr.copy()
    degrade(pr, x0, x1, ys)
    cv2.imwrite(str(prancha), pr)
    print(c, "degraus:", prancha.name)
    for f in (ren / f"POE642_Casa{c}_PH_Terreo_final_rotulos.png", ren / f"POE642_Casa{c}_PH_Terreo_final_rotulos_B.png"):
        if f.exists():
            im = cv2.imread(str(f))
            degrade(im, x0, x1, ys)
            cv2.imwrite(str(f), im)
            print("  ", f.name)
    dz = json.loads((PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[f"{c}_Terreo"]
    caixa_reg = (x0 - 40, ys[0] - 160, x1 + 200, ys[-1] + 180)
    for op in "AB":
        f = ent / f"POE642_Casa{c}_PH_Terreo_12K_opcao_{op}.jpg"
        pil = Image.open(f)
        dpi = pil.info.get("dpi", (743, 743))
        im = cv2.cvtColor(np.array(pil.convert("RGB")), cv2.COLOR_RGB2BGR)
        del pil
        mapa, cc = registro_12k(orig, cv2.cvtColor(im, cv2.COLOR_BGR2GRAY), dz, caixa_reg)
        xm = (x0 + x1) / 2
        X0 = mapa(x0, (ys[0] + ys[-1]) / 2)[0]
        X1 = mapa(x1, (ys[0] + ys[-1]) / 2)[0]
        Ys = [mapa(xm, y)[1] for y in ys]
        degrade(im, X0, X1, Ys, escala=dz["s"])
        Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).save(f, quality=95, subsampling=0, dpi=dpi)
        print("  ", f.name, "registro", round(cc, 4))
        del im


def planta(c, antes_depois=False):
    ent = PROJ / f"POE642_Casa{c}/entrega"
    ren = PROJ / f"POE642_Casa{c}/renders"
    prancha = ent / f"POE642_Casa{c}_PH_Terreo_entrega.png"
    pr = cv2.imread(str(prancha))
    if antes_depois:
        antes = cv2.imdecode(np.frombuffer(subprocess.run(
            ["git", "show", f"{ANTES}:projetos/POE642_Casa{c}/entrega/{prancha.name}"], cwd=PROJ,
            capture_output=True, check=True).stdout, np.uint8), cv2.IMREAD_COLOR)
        a0, b0, a1, b1 = recorte(antes, FUNDO[c])[0]
        return antes[b0:b1, a0:a1], pr[b0:b1, a0:a1]
    x0, y0, x1, y1 = FUNDO[c][0][:4]
    sat = cv2.cvtColor(pr[y0 + 20:y1 - 20, x0 + 20:x1 - 20], cv2.COLOR_BGR2HSV)[..., 1]
    if np.median(sat) < 60:      # a água funda já está sóbria (saturação ~17%; a de antes era ~33%)
        print(c, "já está sóbria; nada feito")
        return
    orig = pr.copy()
    (a0, b0, a1, b1), novo, finais = recorte(pr, FUNDO[c])
    print(c, "prancha:", finais)
    pr[b0:b1, a0:a1] = novo
    cv2.imwrite(str(prancha), pr)
    for f in (ren / f"POE642_Casa{c}_PH_Terreo_final_rotulos.png", ren / f"POE642_Casa{c}_PH_Terreo_final_rotulos_B.png"):
        if f.exists():
            im = cv2.imread(str(f))
            (x0, y0, x1, y1), n2, fin = recorte(im, FUNDO[c])
            im[y0:y1, x0:x1] = n2
            cv2.imwrite(str(f), im)
            print("  ", f.name, fin)
    # no 12K as bordas são suaves: valem as divisas achadas na prancha, levadas ao 12K pelo registro (sem reajuste)
    dz = json.loads((PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[f"{c}_Terreo"]
    s = dz["s"]
    for op in "AB":
        f = ent / f"POE642_Casa{c}_PH_Terreo_12K_opcao_{op}.jpg"
        pil = Image.open(f)
        dpi = pil.info.get("dpi", (743, 743))
        im = cv2.cvtColor(np.array(pil.convert("RGB")), cv2.COLOR_RGB2BGR)
        del pil
        mapa, cc = registro_12k(orig, cv2.cvtColor(im, cv2.COLOR_BGR2GRAY), dz, (a0, b0, a1, b1))
        rets = []
        for x0, y0, x1, y1 in finais:
            X0, Y0 = mapa(x0, y0)
            X1, Y1 = mapa(x1, y1)
            rets.append((int(round(X0)), int(round(Y0)), int(round(X1)), int(round(Y1)), ""))
        (x0, y0, x1, y1), n2, _ = recorte(im, rets, escala=s)
        im[y0:y1, x0:x1] = n2
        Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).save(f, quality=95, subsampling=0, dpi=dpi)
        print("  ", f.name, "registro", round(cc, 4))
        del im
    print(c, "ok:", prancha.name)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--antes_depois", action="store_true")
    ap.add_argument("--casas", default=CASAS)
    a = ap.parse_args()
    if a.antes_depois:
        from PIL import ImageDraw, ImageFont
        F = ImageFont.truetype(str(PROJ / "POE642_CasaA/entrega/assets/fontes/Poppins-Medium.ttf"), 30)
        linhas = []
        for c in a.casas:
            antes, depois = planta(c, True)
            h = 520
            r = lambda im: cv2.resize(im, (int(im.shape[1] * h / im.shape[0]), h), interpolation=cv2.INTER_AREA)
            linhas.append((c, r(antes), r(depois)))
        W = max(x.shape[1] + y.shape[1] for _, x, y in linhas) + 120
        pg = Image.new("RGB", (W, len(linhas) * 600 + 40), "white")
        d = ImageDraw.Draw(pg)
        for i, (c, x, y) in enumerate(linhas):
            yy = 20 + i * 600
            d.text((30, yy), f"CASA {c} – TÉRREO · antes  |  depois",
                   fill=(28, 28, 30), font=F)
            pg.paste(Image.fromarray(cv2.cvtColor(x, cv2.COLOR_BGR2RGB)), (30, yy + 50))
            pg.paste(Image.fromarray(cv2.cvtColor(y, cv2.COLOR_BGR2RGB)), (60 + x.shape[1], yy + 50))
        out = PROJ / "POE642_CasaA/renders/POE642_Casas_ABCD_PH_Terreo_1911_piscinas_sobrias_antes_depois.jpg"
        pg.save(out, quality=90)
        print(out)
    else:
        for c in a.casas:
            planta(c)
            degraus(c)

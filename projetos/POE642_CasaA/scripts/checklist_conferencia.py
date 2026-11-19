"""Checklist de conferência, uma página por planta (19/11, usuário: "Abre para mim em uma folha todas as recomendações
feitas para o subsolo da casa A [...] Consolide em uma página tudo que eles colocaram e ao lado dessas recomendações
você vai [...] plotar o 3D do subsolo [...] Às vezes aparece um pedido de recomendação que vai valer para todas as
outras casas [...] Essas têm que constar em todos esses checklists [...] elencar as recomendações, enumerá-las [...]
trazer também uma imagem do miro [...] e ao lado vai ter o 3D").

Uma página A3 deitada por planta, para conferir ao lado do 12K aberto:
- à esquerda, a lista numerada com a caixinha de marcar: C1.. as recomendações do cliente no Miro para esta planta
  (vermelho), G1.. as que valem para todas as plantas (verde: do cliente ou suas); em cada uma, a fala e o que olhar no
  12K;
- à direita, em cima, a planta do 3D (a planta baixa colorida do escritório de arquitetura, no mesmo giro da nossa);
  embaixo, a imagem do Miro e a nossa planta entregue com os números de cada item no lugar.

Os dados de cada planta estão em `POE642_Book/checklist/dados/<casa>_<pav>.json`.

  python3 checklist_conferencia.py A Subsolo
"""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
PROJ = AQUI.parents[1]
SAIDA = PROJ / "POE642_Book" / "checklist"
DADOS = SAIDA / "dados"
PRANCHA = "POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{p}_entrega.png"
NOME = {"Subsolo": "Subsolo", "Terreo": "Térreo", "1Pavimento": "1º Pavimento"}
FD = "/usr/share/fonts/opentype/inter/"
W, H = 3508, 2480                                     # A3 deitada a 300 dpi
MARG = 80
COR = {"C": (196, 32, 36), "G": (34, 128, 74)}
CINZA = (105, 105, 105)


def fonte(nome, t):
    return ImageFont.truetype(FD + nome, t)


def quebra(txt, f, larg, d):
    linhas, cur = [], ""
    for w in txt.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) > larg and cur:
            linhas.append(cur)
            cur = w
        else:
            cur = t
    return linhas + [cur]


def marca(d, cx, cy, txt, cor, r, f):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=cor, outline="white", width=max(2, r // 7))
    d.text((cx, cy + 1), txt, fill="white", font=f, anchor="mm")


def caber(img, w, h):
    k = min(w / img.shape[1], h / img.shape[0])
    return cv2.resize(img, None, fx=k, fy=k, interpolation=cv2.INTER_AREA if k < 1 else cv2.INTER_CUBIC), k


def pil(img):
    return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))


def blocos(q, d, t, larg):
    """Cada item em linhas: (id, [(texto, fonte, cor)], altura)."""
    fq, fc, ft = fonte("Inter-Italic.otf", t), fonte("Inter-Regular.otf", int(t * 0.9)), fonte("Inter-Medium.otf", int(t * 0.8))
    passo = int(t * 1.32)
    rr = int(t * 0.95)
    xt = 2 * rr + 46
    out = []
    for it in q["itens"]:
        ls = [(ln, fq, (30, 30, 30)) for ln in quebra(f"“{it['fala']}”", fq, larg - xt, d)]
        orig = it["origem"] + (" · vale para todas as plantas" if it.get("todas") and it["id"].startswith("C") else "")
        ls += [(ln, ft, COR["G"] if "todas" in orig else CINZA) for ln in quebra(orig, ft, larg - xt, d)]
        ls += [(ln, fc, (70, 70, 70)) for ln in quebra("No 12K: " + it["conferir"], fc, larg - xt, d)]
        out.append((it["id"], ls, len(ls) * passo))
    return out, passo, rr, xt


def pagina(casa, pav):
    q = json.loads((DADOS / f"{casa}_{pav}.json").read_text())
    pg = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(pg)
    d.text((MARG, MARG - 12), f"Casa {casa} · {NOME[pav]} · checklist de conferência", fill=(25, 25, 25),
           font=fonte("Inter-SemiBold.otf", 56))
    fs = fonte("Inter-Regular.otf", 27)
    d.text((MARG, MARG + 66), "Abra o 12K ao lado e confira item a item; marque a caixinha do que estiver aplicado. "
           "Os números estão no lugar de cada item na planta (embaixo, à direita).", fill=CINZA, font=fs)
    lx = MARG
    for k, txt in (("C", "recomendação do cliente no Miro para esta planta"),
                   ("G", "vale para todas as plantas (do cliente ou sua)")):
        d.ellipse((lx, MARG + 120, lx + 28, MARG + 148), fill=COR[k])
        d.text((lx + 40, MARG + 134), txt, fill=(60, 60, 60), font=fs, anchor="lm")
        lx += 40 + d.textlength(txt, font=fs) + 70
    topo = MARG + 200
    # ---------------------------------------------------------------- à direita: o 3D, o Miro e a nossa planta
    rx0, rx1 = 1770, W - MARG
    rw = rx1 - rx0
    ft = fonte("Inter-SemiBold.otf", 30)
    fr = fonte("Inter-Regular.otf", 23)
    tres = cv2.imread(str(PROJ / q["tres_d"]["arquivo"]))
    x0, y0, x1, y1 = q["tres_d"]["recorte"]
    tres = tres[y0:y1, x0:x1]
    if q["tres_d"].get("giro") == "anti-horario":
        tres = cv2.rotate(tres, cv2.ROTATE_90_COUNTERCLOCKWISE)
    t3, _ = caber(tres, rw, 1080)
    d.text((rx0, topo), "Planta do 3D", fill=(25, 25, 25), font=ft)
    d.text((rx0 + 230, topo + 4), q["tres_d"]["legenda"], fill=CINZA, font=fr)
    py = topo + 48
    pg.paste(pil(t3), (rx0, py))
    d.rectangle((rx0 - 1, py - 1, rx0 + t3.shape[1], py + t3.shape[0]), outline=(220, 220, 220), width=2)
    y2 = py + t3.shape[0] + 50
    # o Miro (a imagem, ou o aviso de que falta)
    mw = 700
    d.text((rx0, y2), "Miro", fill=(25, 25, 25), font=ft)
    my = y2 + 48
    mh = H - MARG - my
    miro = q.get("miro", {})
    if miro.get("arquivo") and (PROJ / miro["arquivo"]).exists():
        mi, _ = caber(cv2.imread(str(PROJ / miro["arquivo"])), mw, mh)
        pg.paste(pil(mi), (rx0, my))
    else:
        d.rectangle((rx0, my, rx0 + mw, my + min(mh, 560)), fill=(246, 246, 246), outline=(210, 210, 210), width=2)
        fa = fonte("Inter-Regular.otf", 25)
        yy = my + 30
        for ln in quebra(miro.get("aviso", "Sem a imagem do Miro."), fa, mw - 60, d):
            d.text((rx0 + 30, yy), ln, fill=(90, 90, 90), font=fa)
            yy += 36
    # a nossa planta, com os números
    px0 = rx0 + mw + 50
    d.text((px0, y2), "Planta entregue (onde fica cada item)", fill=(25, 25, 25), font=ft)
    pr = cv2.imread(str(PROJ / PRANCHA.format(c=casa, p=pav)))
    a0, b0, a1, b1 = q["recorte_prancha"]
    pl, k = caber(pr[b0:b1, a0:a1], rx1 - px0, mh)
    pli = pil(pl)
    dp = ImageDraw.Draw(pli)
    fm = fonte("Inter-Bold.otf", 19)
    for it in q["itens"]:
        for x, y in it.get("pontos") or []:
            cx, cy = (x - a0) * k, (y - b0) * k
            if 0 <= cx <= pli.width and 0 <= cy <= pli.height:
                marca(dp, cx, cy, it["id"], COR[it["id"][0]], 21, fm)
    pg.paste(pli, (px0, my))
    d.rectangle((px0 - 1, my - 1, px0 + pli.width, my + pli.height), outline=(220, 220, 220), width=2)
    # ---------------------------------------------------------------- à esquerda: a lista, em 2 colunas
    lw = (rx0 - 80 - MARG - 80) // 2
    cols = [(MARG, lw), (MARG + lw + 80, lw)]
    secs = [("C", "Recomendações do Miro para esta planta"), ("G", "Valem para todas as plantas")]
    for t in range(30, 15, -1):
        bl, passo, rr, xt = blocos(q, d, t, lw)
        fsec = fonte("Inter-SemiBold.otf", int(t * 1.05))
        # simula o fluxo
        c, y, ok, pos = 0, topo, True, []
        ultimo = None
        for (iid, ls, h) in bl:
            sec = iid[0]
            hs = int(t * 2.2) if sec != ultimo else 0
            while y + hs + h > H - MARG:
                c += 1
                if c >= len(cols):
                    ok = False
                    break
                y = topo
            if not ok:
                break
            pos.append((c, y, hs, sec != ultimo, iid, ls))
            y += hs + h + int(t * 0.75)
            ultimo = sec
        if ok:
            break
    fid = fonte("Inter-Bold.otf", int(t * 0.72))
    nomes = dict(secs)
    for c, y, hs, novo, iid, ls in pos:
        x, larg = cols[c]
        if novo:
            d.text((x, y), nomes[iid[0]], fill=COR[iid[0]], font=fsec)
            d.line((x, y + int(t * 1.45), x + larg, y + int(t * 1.45)), fill=COR[iid[0]], width=2)
        yy = y + hs
        cb = int(t * 0.85)
        d.rectangle((x, yy + 4, x + cb, yy + 4 + cb), outline=(60, 60, 60), width=3)
        marca(d, x + cb + 18 + rr, yy + rr - 2, iid, COR[iid[0]], rr, fid)
        for i, (ln, f, cor) in enumerate(ls):
            d.text((x + xt + cb, yy + i * passo), ln, fill=cor, font=f)
    d.text((W - MARG, H - 36), "POE 642 · plantas humanizadas · checklist de conferência", fill=(150, 150, 150),
           font=fonte("Inter-Regular.otf", 22), anchor="rm")
    SAIDA.mkdir(parents=True, exist_ok=True)
    out = SAIDA / f"POE642_Checklist_Casa{casa}_{pav}.jpg"
    pg.save(out, quality=92)
    print(out, f"(corpo {t})")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("casa")
    ap.add_argument("pav")
    a = ap.parse_args()
    pagina(a.casa, a.pav)

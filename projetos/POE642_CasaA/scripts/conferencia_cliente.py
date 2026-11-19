"""Conferência dos pedidos do Miro, a versão para o cliente (19/11, usuário: "A ideia é que esse arquivo de solicitação
de alterações, baseado no Miro, eu possa ser enviado para o cliente também [...] para que ele também faça essa
conferência [...] eu quero mostrar para eles que a gente seguiu fielmente aquilo que eles pediram").

Uma página A3 deitada por planta, na identidade das pranchas (Poppins, os logotipos da Paulo Octávio e da New Air):
- à esquerda, cada pedido do cliente no Miro para esta planta, com as palavras dele, o que foi feito e o detalhe da
  planta humanizada (recortado do 12K) e a caixinha "conferido"; depois, os pedidos gerais dele que valem para todas
  as plantas. Só entram os pedidos do cliente (`"cliente": true`): os padrões internos ficam na versão de conferência
  interna (`checklist_conferencia.py`);
- à direita, a imagem do Miro, a planta de layout do projeto (a do 3D, no mesmo giro da nossa) e a planta humanizada
  com os números no lugar de cada pedido.

Os dados são os mesmos da conferência interna: `POE642_Book/checklist/dados/<casa>_<pav>.json` (por item: `fala`,
`como`, `detalhe` em px da prancha; o 12K pelo `doze_k`: px do 12K = (px da prancha - x0, y0) * s).

  python3 conferencia_cliente.py A Subsolo
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
ASSETS = PROJ / "POE642_CasaA" / "entrega" / "assets"
PRANCHA = "POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{p}_entrega.png"
NOME = {"Subsolo": "SUBSOLO", "Terreo": "TÉRREO", "1Pavimento": "1º PAVIMENTO"}
W, H = 3508, 2480                                     # A3 deitada a 300 dpi
MARG = 90
TINTA = (28, 28, 30)
CINZA = (110, 110, 112)
LINHA = (225, 222, 216)
ACENTO = (150, 118, 82)                               # o bronze das pranchas
COR = {"C": (176, 40, 40), "G": (38, 110, 80)}


def F(peso, t):
    return ImageFont.truetype(str(ASSETS / "fontes" / f"Poppins-{peso}.ttf"), t)


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


def logos(pg, x1, yc, alt):
    po = Image.open(ASSETS / "logo_paulo_octavio.png").convert("RGB")
    po = po.resize((round(po.width * alt / po.height), alt), Image.LANCZOS)
    na = Image.open(ASSETS / "logo_new_air.png").convert("RGBA")
    na = na.resize((round(na.width * alt * 0.9 / na.height), round(alt * 0.9)), Image.LANCZOS)
    x = x1 - po.width
    pg.paste(po, (x, yc - po.height // 2))
    x -= 60 + na.width
    pg.paste(na, (x, yc - na.height // 2), na)


def pagina(casa, pav):
    q = json.loads((DADOS / f"{casa}_{pav}.json").read_text())
    itens = [it for it in q["itens"] if it.get("cliente")]
    pg = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(pg)
    # ---------------------------------------------------------------- o cabeçalho
    d.text((MARG, MARG - 10), f"CASA {casa} – {NOME[pav]}", fill=TINTA, font=F("Medium", 62))
    d.text((MARG, MARG + 84), "CONFERÊNCIA DOS PEDIDOS FEITOS NO MIRO", fill=ACENTO, font=F("Regular", 30))
    logos(pg, W - MARG, MARG + 55, 92)
    d.line((MARG, MARG + 150, W - MARG, MARG + 150), fill=TINTA, width=3)
    fi = F("Light", 27)
    d.text((MARG, MARG + 172), "Cada pedido feito no Miro para esta planta, com as suas palavras, o que foi feito e o detalhe da "
           "planta humanizada. Os números mostram onde está cada pedido na planta.", fill=CINZA, font=fi)
    topo = MARG + 250
    # ---------------------------------------------------------------- à direita: Miro, layout do projeto, a planta
    rx0, rx1 = 2250, W - MARG
    rw = rx1 - rx0
    ft = F("Medium", 27)
    fr = F("Light", 21)
    y = topo
    d.text((rx0, y), "MIRO", fill=TINTA, font=ft)
    y += 46
    miro = q.get("miro", {})
    if miro.get("arquivo") and (PROJ / miro["arquivo"]).exists():
        mi, _ = caber(cv2.imread(str(PROJ / miro["arquivo"])), rw, 560)
        pg.paste(pil(mi), (rx0, y))
        y += mi.shape[0] + 46
    else:
        d.rectangle((rx0, y, rx1, y + 300), fill=(247, 246, 243), outline=LINHA, width=2)
        d.text(((rx0 + rx1) // 2, y + 150), "[ imagem do quadro do Miro desta planta ]", fill=(150, 150, 150),
               font=F("Light", 26), anchor="mm")
        y += 300 + 46
    d.text((rx0, y), "PLANTA DE LAYOUT DO PROJETO", fill=TINTA, font=ft)
    y += 40
    d.text((rx0, y), "referência do escritório de arquitetura, no mesmo giro da planta humanizada", fill=CINZA, font=fr)
    y += 40
    t3 = q["tres_d"]
    tres = cv2.imread(str(PROJ / t3["arquivo"]))
    a, b, c, e = t3["recorte"]
    tres = tres[b:e, a:c]
    if t3.get("giro") == "anti-horario":
        tres = cv2.rotate(tres, cv2.ROTATE_90_COUNTERCLOCKWISE)
    im3, _ = caber(tres, rw, 760)
    pg.paste(pil(im3), (rx0, y))
    d.rectangle((rx0 - 1, y - 1, rx0 + im3.shape[1], y + im3.shape[0]), outline=LINHA, width=2)
    y += im3.shape[0] + 46
    d.text((rx0, y), "PLANTA HUMANIZADA", fill=TINTA, font=ft)
    y += 46
    pr = cv2.imread(str(PROJ / PRANCHA.format(c=casa, p=pav)))
    a0, b0, a1, b1 = q["recorte_prancha"]
    pl, k = caber(pr[b0:b1, a0:a1], rw, H - MARG - 40 - y)
    pli = pil(pl)
    dp = ImageDraw.Draw(pli)
    fm = F("SemiBold", 17)
    for it in itens:
        for x, yy in it.get("pontos") or []:
            cx, cy = (x - a0) * k, (yy - b0) * k
            if 0 <= cx <= pli.width and 0 <= cy <= pli.height:
                marca(dp, cx, cy, it["id"], COR[it["id"][0]], 20, fm)
    pg.paste(pli, (rx0, y))
    d.rectangle((rx0 - 1, y - 1, rx0 + pli.width, y + pli.height), outline=LINHA, width=2)
    # ---------------------------------------------------------------- à esquerda: os pedidos
    dz = q["doze_k"]
    doze = cv2.imread(str(PROJ / dz["arquivo"]))
    lx0, lx1 = MARG, rx0 - 110
    dw, dh = 470, 222                                 # o detalhe de cada pedido
    tx1 = lx1 - dw - 50
    secs = {"C": "PEDIDOS PARA ESTA PLANTA", "G": "PEDIDOS GERAIS (VALEM PARA TODAS AS PLANTAS)"}
    n = len(itens)
    nsec = len({it["id"][0] for it in itens})
    for t in range(34, 17, -1):
        fq, fc, fl = F("Regular", t), F("Light", int(t * 0.92)), F("Medium", int(t * 0.62))
        passo = int(t * 1.42)
        blocos = []
        for it in itens:
            larg = tx1 - (lx0 + 150)
            lq = quebra(f"“{it['fala']}”", fq, larg, d)
            lc = quebra(it["como"], fc, larg, d)
            h = int(t * 0.95) + len(lq) * passo + int(t * 0.95) + len(lc) * int(passo * 0.95)
            blocos.append((lq, lc, max(h, dh)))
        total = sum(h for *_, h in blocos) + n * 34 + nsec * 76
        if total <= H - MARG - 40 - topo:
            break
    ultimo = None
    y = topo
    for it, (lq, lc, h) in zip(itens, blocos):
        sec = it["id"][0]
        if sec != ultimo:
            d.text((lx0, y), secs[sec], fill=COR[sec], font=F("Medium", 28))
            d.line((lx0, y + 46, lx1, y + 46), fill=COR[sec], width=2)
            y += 76
            ultimo = sec
        marca(d, lx0 + 34, y + 34, it["id"], COR[sec], 32, F("SemiBold", 24))
        cb = 34
        d.rectangle((lx0 + 17, y + 90, lx0 + 17 + cb, y + 90 + cb), outline=(80, 80, 80), width=3)
        d.text((lx0 + 34, y + 90 + cb + 10), "conferido", fill=CINZA, font=F("Light", 17), anchor="mt")
        x = lx0 + 150
        yy = y
        d.text((x, yy), "PEDIDO NO MIRO", fill=CINZA, font=fl)
        yy += int(t * 0.95)
        for ln in lq:
            d.text((x, yy), ln, fill=TINTA, font=fq)
            yy += passo
        d.text((x, yy), "O QUE FOI FEITO", fill=CINZA, font=fl)
        yy += int(t * 0.95)
        for ln in lc:
            d.text((x, yy), ln, fill=(70, 70, 70), font=fc)
            yy += int(passo * 0.95)
        # o detalhe da planta humanizada, do 12K
        a0, b0, a1, b1 = it["detalhe"]
        s = dz["s"]
        X0, Y0 = int((a0 - dz["x0"]) * s), int((b0 - dz["y0"]) * s)
        X1, Y1 = int((a1 - dz["x0"]) * s), int((b1 - dz["y0"]) * s)
        det, _ = caber(doze[max(Y0, 0):Y1, max(X0, 0):X1], dw, dh)
        dx = lx1 - det.shape[1]
        pg.paste(pil(det), (dx, y))
        d.rectangle((dx - 1, y - 1, dx + det.shape[1], y + det.shape[0]), outline=LINHA, width=2)
        y += h + 34
        d.line((lx0, y - 17, lx1, y - 17), fill=(238, 236, 232), width=2)
    d.text((W - MARG, H - 40), "POE 642 · PLANTAS HUMANIZADAS · CONFERÊNCIA DOS PEDIDOS", fill=(160, 160, 160),
           font=F("Light", 20), anchor="rm")
    SAIDA.mkdir(parents=True, exist_ok=True)
    out = SAIDA / f"POE642_Conferencia_Casa{casa}_{pav}.jpg"
    pg.save(out, quality=92)
    pg.save(out.with_suffix(".pdf"), resolution=300)
    print(out, f"(corpo {t})")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("casa")
    ap.add_argument("pav")
    a = ap.parse_args()
    pagina(a.casa, a.pav)

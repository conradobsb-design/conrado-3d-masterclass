"""O levantamento dos ajustes de todas as plantas (18/11, usuário, com o levantamento do Subsolo da Casa E: "eu preciso
de um desse para todas as plantas. Inclusive com os ajustes que eu pedi para fazer. Precisa constar os ajustes feitos a
pedido do cliente (das recomendações no miro) e o que eu adicionei. para cada planta, uma página.").

Uma página A3 deitada por planta (Casas A a E: 12 plantas), no modelo do levantamento do Subsolo da E: à esquerda a
planta entregue (as 2160 linhas de cima da prancha de entrega, recortada na planta) com as marcas numeradas; à direita
a lista dos itens. A cor diz a origem: vermelho, pedido do cliente (as notas e recomendações do Miro, os post-its);
azul, pedido do usuário (os ajustes e acréscimos dele, os padrões que ele definiu para todas as casas, o mobiliário da
biblioteca que ele aprovou). Os itens de cada casa estão em `POE642_Book/levantamento/dados/casa_<X>.json`
({"casa", "plantas": {pav: {"recorte", "itens": [{"n", "origem", "texto", "pontos"}]}}}; pontos em px da prancha).

  python3 levantamento_ajustes.py            # as 12 páginas (JPG) e o PDF único
  python3 levantamento_ajustes.py --casa E   # só as da Casa E (e o PDF com o que houver)
"""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
PROJ = AQUI.parents[1]
SAIDA = PROJ / "POE642_Book" / "levantamento"
DADOS = SAIDA / "dados"
PRANCHA = "POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{p}_entrega.png"
CASAS = [("A", ["Subsolo", "Terreo", "1Pavimento"]), ("B", ["Subsolo", "Terreo"]), ("C", ["Subsolo", "Terreo"]),
         ("D", ["Subsolo", "Terreo"]), ("E", ["Subsolo", "Terreo", "1Pavimento"])]
NOME = {"Subsolo": "Subsolo", "Terreo": "Térreo", "1Pavimento": "1º Pavimento"}
DATA = "18/11/2026"

FD = "/usr/share/fonts/opentype/inter/"
W, H = 3508, 2480                                     # A3 deitada a 300 dpi
MARG = 90
PLANTA_W = 2120                                       # a área da planta (à esquerda)
COR = {"cliente": (196, 32, 36), "voce": (28, 92, 170)}
LEGENDA = {"cliente": "pedido do cliente (notas e recomendações do Miro)",
           "voce": "pedido seu (ajustes e acréscimos)"}


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


def marca(d, cx, cy, n, cor, r, f):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=cor, outline="white", width=max(2, r // 7))
    d.text((cx, cy + 1), str(n), fill="white", font=f, anchor="mm")


def fluir(itens, d, f, cols, passo, entre, rr):
    """Distribui os itens pelas colunas [(x, y0, y1, larg)], na ordem; None se não couberem."""
    pos, c, y = [], 0, cols[0][1] if cols else 0
    for it in itens:
        while c < len(cols):
            x, y0, y1, larg = cols[c]
            ls = quebra(it["texto"], f, larg - 2 * rr - 18, d)
            h = max(len(ls) * passo, passo + 8)
            if y + h <= y1:
                pos.append((x, y, ls))
                y += h + entre
                break
            c += 1
            if c < len(cols):
                y = cols[c][1]
        else:
            return None
    return pos


def pagina(casa, pav, q):
    pr = cv2.imread(str(PROJ / PRANCHA.format(c=casa, p=pav)))
    if pr is None:
        raise SystemExit(f"sem a prancha da Casa {casa}, {pav}")
    x0, y0, x1, y1 = (int(v) for v in q["recorte"])
    x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, pr.shape[1]), min(y1, 2160)
    rec = pr[y0:y1, x0:x1]
    alt_max = H - MARG - 260
    k = min(PLANTA_W / rec.shape[1], alt_max / rec.shape[0])
    pl = cv2.resize(rec, None, fx=k, fy=k, interpolation=cv2.INTER_AREA if k < 1 else cv2.INTER_CUBIC)
    pl = Image.fromarray(cv2.cvtColor(pl, cv2.COLOR_BGR2RGB))
    dp = ImageDraw.Draw(pl)
    r = 22
    fnum = fonte("Inter-Bold.otf", 25)
    fnum2 = fonte("Inter-Bold.otf", 21)
    for it in q["itens"]:
        for x, y in it.get("pontos") or []:
            cx, cy = (x - x0) * k, (y - y0) * k
            if 0 <= cx <= pl.width and 0 <= cy <= pl.height:
                marca(dp, cx, cy, it["n"], COR[it["origem"]], r, fnum if it["n"] < 10 else fnum2)
    pg = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(pg)
    d.text((MARG, MARG - 10), f"Casa {casa} · {NOME[pav]} · ajustes feitos", fill=(25, 25, 25),
           font=fonte("Inter-SemiBold.otf", 58))
    fsub = fonte("Inter-Regular.otf", 30)
    nc = sum(it["origem"] == "cliente" for it in q["itens"])
    nv = len(q["itens"]) - nc
    d.text((MARG, MARG + 70), f"Registro do que foi feito na planta entregue, até {DATA}: {len(q['itens'])} itens "
           f"({nc} do cliente, {nv} seus).", fill=(95, 95, 95), font=fsub)
    lx = MARG
    for o in ("cliente", "voce"):
        d.ellipse((lx, MARG + 128, lx + 30, MARG + 158), fill=COR[o])
        d.text((lx + 42, MARG + 143), LEGENDA[o], fill=(60, 60, 60), font=fsub, anchor="lm")
        lx += 42 + d.textlength(LEGENDA[o], font=fsub) + 70
    py = MARG + 200
    pg.paste(pl, (MARG, py))
    d.rectangle((MARG - 1, py - 1, MARG + pl.width, py + pl.height), outline=(225, 225, 225), width=2)
    # a lista, no maior corpo que couber: a coluna à direita da planta e, se sobrar altura embaixo da planta, mais duas
    # colunas ali (a lista continua nelas, na ordem dos números)
    lx = MARG + PLANTA_W + 80
    topo, fundo = MARG + 200, H - MARG
    cols = [(lx, topo, fundo, W - MARG - lx)]
    yb = py + pl.height + 70
    if fundo - yb >= 280:
        lc = (pl.width - 80) // 2
        cols += [(MARG, yb, fundo, lc), (MARG + lc + 80, yb, fundo, lc)]
    for t in range(36, 15, -1):
        f = fonte("Inter-Regular.otf", t)
        passo, entre, rr = int(t * 1.36), int(t * 0.55), int(t * 0.62)
        pos = fluir(q["itens"], d, f, cols, passo, entre, rr)
        if pos is not None:
            break
    fn = fonte("Inter-Bold.otf", int(t * 0.8))
    for it, (x, y, ls) in zip(q["itens"], pos):
        marca(d, x + rr, y + rr + 2, it["n"], COR[it["origem"]], rr, fn)
        for i, ln in enumerate(ls):
            d.text((x + 2 * rr + 18, y + i * passo), ln, fill=(30, 30, 30), font=f)
    d.text((W - MARG, H - 40), "POE 642 · plantas humanizadas · levantamento dos ajustes", fill=(150, 150, 150),
           font=fonte("Inter-Regular.otf", 22), anchor="rs")
    return pg


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--casa")
    a = ap.parse_args()
    SAIDA.mkdir(parents=True, exist_ok=True)
    paginas = []
    for casa, pavs in CASAS:
        arq = DADOS / f"casa_{casa}.json"
        if not arq.exists():
            print(f"    Casa {casa}: sem dados ({arq.name})")
            continue
        dados = json.loads(arq.read_text(encoding="utf-8"))["plantas"]
        for pav in pavs:
            if pav not in dados:
                print(f"    Casa {casa}, {pav}: sem dados")
                continue
            if a.casa and casa != a.casa:
                pg = Image.open(SAIDA / f"POE642_Levantamento_Casa{casa}_{pav}.jpg")
            else:
                pg = pagina(casa, pav, dados[pav])
                pg.save(SAIDA / f"POE642_Levantamento_Casa{casa}_{pav}.jpg", quality=92, dpi=(300, 300))
                print(f"    Casa {casa}, {pav}: {len(dados[pav]['itens'])} itens")
            paginas.append(pg.convert("RGB"))
    if paginas:
        pdf = SAIDA / "POE642_Levantamento_Ajustes.pdf"
        paginas[0].save(pdf, save_all=True, append_images=paginas[1:], resolution=300.0, quality=88)
        print(f"    {pdf} ({len(paginas)} páginas, {pdf.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()

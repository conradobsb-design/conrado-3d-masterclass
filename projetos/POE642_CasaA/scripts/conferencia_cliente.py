"""Conferência dos pedidos do Miro, uma por planta: a versão para o cliente e a interna (19/11).

Usuário: "A ideia é que esse arquivo de solicitação de alterações, baseado no Miro, eu possa ser enviado para o cliente
também [...] para que ele também faça essa conferência [...] eu quero mostrar para eles que a gente seguiu fielmente
aquilo que eles pediram"; antes: "elencar as recomendações, enumerá-las [...] trazer também uma imagem do miro [...] e ao
lado vai ter o 3D"; "Às vezes aparece um pedido de recomendação que vai valer para todas as outras casas [...] Essas têm
que constar em todos esses checklists"; e, sobre os padrões do escritório, "Sim" (entram como "melhorias aplicadas em
todas as plantas").

Folhas A3 deitadas, na identidade das pranchas (Poppins, os logotipos da Paulo Octávio e da New Air):
- 1ª folha: à direita, a planta de layout do projeto (a do PDF do escritório de arquitetura, no mesmo quadro da nossa:
  a base `POE642_Casa<X>/bases/..._v1_16x9.png`) e a planta humanizada com o número de cada pedido no lugar (e a imagem
  do Miro, se houver); à esquerda, os pedidos;
- cada pedido: o número, a caixinha "conferido", a fala do cliente no Miro, o que foi feito e o detalhe da planta
  humanizada recortado do 12K (opção A);
- depois, os pedidos gerais do cliente (valem para todas as plantas: constam em todas as folhas, com o que foi feito
  nesta) e as melhorias aplicadas em todas as plantas;
- o que não cabe vai para as folhas de continuação, em duas colunas.

Dados (`POE642_Book/checklist/dados/`):
- `itens/<casa>_<pav>.json`: os pedidos do cliente desta planta (`fala`, `como`, `conferir`, `pontos` em px da prancha,
  `geral`, `g` = o id do pedido geral quando `geral`, `status`, `obs`);
- `gerais.json`: os pedidos gerais (`id`, `fala`, `origem`, `como`: o texto padrão, quando a planta não tem o seu);
- `melhorias.json`: os padrões do escritório, para o cliente;
- `doze_k.json`: o 12K de cada planta na prancha (px do 12K = (px da prancha - (x0, y0)) * s);
- `planos.json`: o recorte da prancha (`recorte`) e a imagem do Miro (`miro`), por planta.

  python3 conferencia_cliente.py A Subsolo          # uma planta (versão do cliente)
  python3 conferencia_cliente.py A Subsolo --interno
  python3 conferencia_cliente.py --todas [--interno] # as 12 e o PDF único
"""
import argparse
import glob
import json
from pathlib import Path

import cv2
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
PROJ = AQUI.parents[1]
SAIDA = PROJ / "POE642_Book" / "checklist"
DADOS = SAIDA / "dados"
ASSETS = PROJ / "POE642_CasaA" / "entrega" / "assets"
PRANCHA = "POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{p}_entrega.png"
NOME = {"Subsolo": "SUBSOLO", "Terreo": "TÉRREO", "1Pavimento": "1º PAVIMENTO"}
PLANTAS = [("A", "Subsolo"), ("A", "Terreo"), ("A", "1Pavimento"), ("B", "Subsolo"), ("B", "Terreo"),
           ("C", "Subsolo"), ("C", "Terreo"), ("D", "Subsolo"), ("D", "Terreo"), ("E", "Subsolo"), ("E", "Terreo"),
           ("E", "1Pavimento")]
W, H = 3508, 2480                                     # A3 deitada a 300 dpi
MARG = 90
TINTA = (28, 28, 30)
CINZA = (110, 110, 112)
LINHA = (225, 222, 216)
ACENTO = (150, 118, 82)                               # o bronze das pranchas
COR = {"C": (176, 40, 40), "G": (38, 110, 80), "M": (150, 118, 82)}
DW, DH = 440, 205                                     # o detalhe de cada pedido
RX0 = 2250                                            # a coluna das plantas na 1ª folha
TOPO = MARG + 250
BASE = H - MARG - 40
ROTULO = {"nao_feito": "NÃO FEITO", "parcial": "PARCIAL"}


def F(peso, t):
    return ImageFont.truetype(str(ASSETS / "fontes" / f"Poppins-{peso}.ttf"), t)


FQ, FC, FL, FK = F("Regular", 29), F("Light", 27), F("Medium", 19), F("Light", 17)
FI, FS = F("Light", 26), F("Medium", 28)
FG, FGC = F("Regular", 27), F("Light", 25)


def quebra(txt, f, larg, d):
    linhas = []
    for par in txt.split("\n"):
        cur = ""
        for w in par.split():
            t = (cur + " " + w).strip()
            if d.textlength(t, font=f) > larg and cur:
                linhas.append(cur)
                cur = w
            else:
                cur = t
        linhas.append(cur)
    return linhas


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


def resumo(fala):
    """A nota sem o texto literal transcrito (só o resumo) ou uma marcação sem texto."""
    return fala.startswith("[sem o texto literal]") or fala.startswith("(")


def aspas(fala):
    if resumo(fala):
        t = fala.replace("[sem o texto literal]", "").strip().strip("()").strip()
        return t[:1].upper() + t[1:]
    return " / ".join(f"“{f.strip()}”" for f in fala.split(" / "))


# ------------------------------------------------------------------------------------------------ os dados
def ler(nome, padrao=None):
    f = DADOS / nome
    return json.loads(f.read_text()) if f.exists() else padrao


def qual_geral(it, gerais):
    """O id do pedido geral de que o item trata (pelo `g` ou pelas `chaves` na fala), ou None."""
    if it.get("g"):
        return it["g"]
    fala = it["fala"].lower()
    for g in gerais:
        if any(c.lower() in fala for c in g.get("chaves", [])):
            return g["id"]
    return None


def onde_geral(gerais):
    """Em que plantas o cliente escreveu cada pedido geral no Miro."""
    onde = {}
    for c, p in PLANTAS:
        f = DADOS / "itens" / f"{c}_{p}.json"
        if not f.exists():
            continue
        for it in json.loads(f.read_text())["itens"]:
            g = qual_geral(it, gerais)
            if g and (c, p) not in onde.setdefault(g, []):
                onde[g].append((c, p))
    out = {}
    for g, lst in onde.items():
        casas = {}
        for c, p in lst:
            casas.setdefault(c, []).append(NOME[p].capitalize().replace("º pavimento", "º Pavimento"))
        out[g] = "no Miro em: " + "; ".join(f"Casa {c}, " + " e ".join(ps) for c, ps in casas.items())
    return out


def dados_planta(casa, pav, interno):
    itens = (ler(f"itens/{casa}_{pav}.json") or {"itens": []})["itens"]
    gerais = ler("gerais.json", [])
    plano = ler("planos.json", {}).get(f"{casa}_{pav}", {})
    if "recorte" not in plano:
        lev = json.loads((PROJ / "POE642_Book/levantamento/dados" / f"casa_{casa}.json").read_text())
        plano["recorte"] = lev["plantas"][pav]["recorte"]
    pedidos, desta = [], {}
    for it in itens:
        g = qual_geral(it, gerais)
        if g:
            desta.setdefault(g, []).append(it)
        elif interno or (it.get("status", "feito") != "nao_feito" and it["fala"].strip() not in ("?", "")):
            pedidos.append(dict(it))                       # o cliente não vê o que não foi feito nem o "?" solto
    for n, it in enumerate(pedidos, 1):
        it["id"] = f"C{n}"
    gs = []
    origem = onde_geral(gerais)
    for g in gerais:
        if g.get("so") and f"{casa}_{pav}" not in g["so"]:
            continue
        aqui = desta.get(g["id"], [])
        como = " ".join(a["como"] for a in aqui) if aqui else plano.get("gerais", {}).get(g["id"], g["como"])
        pts = [p for a in aqui for p in a.get("pontos") or []]
        st = [a for a in aqui if a.get("status", "feito") != "feito"]
        gs.append({"id": g["id"], "fala": g["fala"], "origem": origem.get(g["id"], ""), "como": como, "pontos": pts,
                   "conferir": " ".join(a.get("conferir", "") for a in aqui), "status": st[0]["status"] if st else "feito",
                   "obs": " ".join(a.get("obs", "") for a in st)})
    return plano, pedidos, gs, ler("melhorias.json", [])


def retangulo(pts, area):
    """O recorte do detalhe em px da prancha, em volta dos pontos, na proporção do quadro do detalhe."""
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    if max(xs) - min(xs) > 700 or max(ys) - min(ys) > 380:
        xs, ys = xs[:1], ys[:1]
    a0, b0, a1, b1 = min(xs) - 80, min(ys) - 60, max(xs) + 80, max(ys) + 60
    w, h = max(a1 - a0, 300), max(b1 - b0, 150)
    if w / h > DW / DH:
        h = w * DH / DW
    else:
        w = h * DW / DH
    cx, cy = (a0 + a1) / 2, (b0 + b1) / 2
    a0, b0 = cx - w / 2, cy - h / 2
    x0, y0, x1, y1 = area
    a0 = min(max(a0, x0), x1 - w)
    b0 = min(max(b0, y0), y1 - h)
    return [a0, b0, a0 + w, b0 + h]


# ------------------------------------------------------------------------------------------------ os blocos
class Folha:
    def __init__(self, casa, pav, n):
        self.pg = Image.new("RGB", (W, H), "white")
        self.d = ImageDraw.Draw(self.pg)
        d = self.d
        cont = "" if n == 1 else "  (continuação)"
        d.text((MARG, MARG - 10), f"CASA {casa} – {NOME[pav]}{cont}", fill=TINTA, font=F("Medium", 62))
        d.text((MARG, MARG + 84), "CONFERÊNCIA DOS PEDIDOS FEITOS NO MIRO", fill=ACENTO, font=F("Regular", 30))
        logos(self.pg, W - MARG, MARG + 55, 92)
        d.line((MARG, MARG + 150, W - MARG, MARG + 150), fill=TINTA, width=3)
        if n == 1:
            d.text((MARG, MARG + 172), "Cada pedido feito no Miro para esta planta, com as suas palavras, o que foi "
                   "feito e o detalhe da planta humanizada. Os números mostram onde está cada pedido na planta.",
                   fill=CINZA, font=FI)


def bloco_secao(titulo, cor):
    def desenhar(fl, x, y, w, so_medir=False):
        if not so_medir:
            fl.d.text((x, y), titulo, fill=cor, font=FS)
            fl.d.line((x, y + 46, x + w, y + 46), fill=cor, width=2)
        return 76
    return desenhar


def bloco_pedido(it, doze, dz, interno):
    cor = COR[it["id"][0]]

    def desenhar(fl, x, y, w, so_medir=False):
        d = fl.d
        tx, tw = x + 120, w - 120 - DW - 40
        lq = quebra(aspas(it["fala"]), FQ, tw, d)
        lc = quebra(it["como"], FC, tw, d)
        yy = y + 28 + len(lq) * 41 + 10 + 28 + len(lc) * 38
        extra = []
        if interno:
            if it.get("conferir"):
                extra.append(("NO 12K: " + it["conferir"], (38, 110, 80)))
            if it.get("status", "feito") != "feito":
                extra.append((f"{ROTULO.get(it['status'], it['status'].upper())}: {it.get('obs', '')}", (196, 32, 36)))
            if it.get("obs") and it.get("status", "feito") == "feito":
                extra.append(("OBS.: " + it["obs"], (196, 32, 36)))
        le = [(ln, c) for t, c in extra for ln in quebra(t, FK if False else F("Light", 24), tw, d)]
        yy += 8 + len(le) * 34 if le else 0
        a0, b0, a1, b1 = it["detalhe"]
        s = dz["s"]
        X0, Y0 = int((a0 - dz["x0"]) * s), int((b0 - dz["y0"]) * s)
        X1, Y1 = int((a1 - dz["x0"]) * s), int((b1 - dz["y0"]) * s)
        h = max(yy - y, DH, 160)
        if so_medir:
            return h + 34
        marca(d, x + 36, y + 36, it["id"], cor, 34, F("SemiBold", 24))
        cb = 34
        d.rectangle((x + 19, y + 92, x + 19 + cb, y + 92 + cb), outline=(80, 80, 80), width=3)
        d.text((x + 36, y + 92 + cb + 10), "conferido", fill=CINZA, font=FK, anchor="mt")
        yy = y
        d.text((tx, yy), "PEDIDO NO MIRO" + (" (EM RESUMO)" if resumo(it["fala"]) else ""), fill=CINZA, font=FL)
        yy += 28
        for ln in lq:
            d.text((tx, yy), ln, fill=TINTA, font=FQ)
            yy += 41
        yy += 10
        d.text((tx, yy), "O QUE FOI FEITO", fill=CINZA, font=FL)
        yy += 28
        for ln in lc:
            d.text((tx, yy), ln, fill=(70, 70, 70), font=FC)
            yy += 38
        yy += 8
        for ln, c in le:
            d.text((tx, yy), ln, fill=c, font=F("Light", 24))
            yy += 34
        det = doze[max(Y0, 0):max(Y1, 1), max(X0, 0):max(X1, 1)]
        if det.size:
            det, _ = caber(det, DW, DH)
            dx = x + w - det.shape[1]
            fl.pg.paste(pil(det), (dx, y))
            d.rectangle((dx - 1, y - 1, dx + det.shape[1], y + det.shape[0]), outline=LINHA, width=2)
        d.line((x, y + h + 17, x + w, y + h + 17), fill=(238, 236, 232), width=2)
        return h + 34
    return desenhar


def bloco_geral(g, interno):
    def desenhar(fl, x, y, w, so_medir=False):
        d = fl.d
        tx, tw = x + 120, w - 120
        lq = quebra(aspas(g["fala"]), FG, tw, d)
        lc = quebra("Nesta planta: " + g["como"], FGC, tw, d)
        extra = []
        if interno and g.get("conferir"):
            extra += quebra("NO 12K: " + g["conferir"], F("Light", 24), tw, d)
        if interno and g.get("status", "feito") != "feito":
            extra += quebra(f"{ROTULO.get(g['status'], g['status'].upper())}: {g.get('obs', '')}", F("Light", 24), tw, d)
        h = max(len(lq) * 38 + 6 + len(lc) * 35 + len(extra) * 33, 116)
        if so_medir:
            return h + 34
        marca(d, x + 36, y + 30, g["id"], COR["G"], 30, F("SemiBold", 22))
        d.rectangle((x + 19, y + 74, x + 53, y + 108), outline=(80, 80, 80), width=3)
        yy = y
        for ln in lq:
            d.text((tx, yy), ln, fill=TINTA, font=FG)
            yy += 38
        yy += 6
        for ln in lc:
            d.text((tx, yy), ln, fill=(70, 70, 70), font=FGC)
            yy += 35
        for ln in extra:
            d.text((tx, yy), ln, fill=(38, 110, 80) if ln.startswith("NO 12K") else (196, 32, 36), font=F("Light", 24))
            yy += 33
        d.line((x, y + h + 16, x + w, y + h + 16), fill=(238, 236, 232), width=2)
        return h + 34
    return desenhar


def bloco_melhorias(mel, ncol=None, corpo=26):
    def desenhar(fl, x, y, w, so_medir=False):
        d = fl.d
        f = F("Light", corpo)
        nc = ncol or (2 if w > 1800 else 1)
        cw = (w - (nc - 1) * 50) // nc
        passo = int(corpo * 1.38)
        linhas = [quebra(m, f, cw - 50, d) for m in mel]
        por = -(-len(mel) // nc)
        cols = [linhas[i * por:(i + 1) * por] for i in range(nc)]
        hc = [sum(len(ls) * passo + 12 for ls in c) for c in cols]
        h = 112 + max(hc)
        if so_medir:
            return h + 20
        d.text((x, y), "MELHORIAS APLICADAS EM TODAS AS PLANTAS", fill=COR["M"], font=FS)
        d.text((x, y + 44), "o padrão de representação do escritório, além dos pedidos", fill=CINZA, font=F("Light", 22))
        d.line((x, y + 84, x + w, y + 84), fill=COR["M"], width=2)
        for i, c in enumerate(cols):
            yy = y + 100
            cx = x + i * (cw + 50)
            for ls in c:
                q = int(corpo * 0.9)
                d.rectangle((cx, yy + 6, cx + q, yy + 6 + q), outline=(80, 80, 80), width=3)
                for ln in ls:
                    d.text((cx + q + 22, yy), ln, fill=(70, 70, 70), font=f)
                    yy += passo
                yy += 12
        return h + 20
    return desenhar


# ------------------------------------------------------------------------------------------------ a 1ª folha
def plantas(fl, casa, pav, plano, pedidos, gs, interno):
    d = fl.d
    rx0, rx1 = RX0, W - MARG
    rw = rx1 - rx0
    ft = F("Medium", 27)
    fr = F("Light", 21)
    a0, b0, a1, b1 = plano["recorte"]
    y = TOPO
    miro = plano.get("miro")
    tem_miro = bool(miro) and (PROJ / miro).exists()
    nimg = 2 + tem_miro
    hdisp = BASE - TOPO - nimg * 92
    hmax = hdisp / nimg if tem_miro else hdisp / 2
    if tem_miro:
        d.text((rx0, y), "MIRO", fill=TINTA, font=ft)
        y += 46
        mi, _ = caber(cv2.imread(str(PROJ / miro)), rw, hmax)
        fl.pg.paste(pil(mi), (rx0, y))
        y += mi.shape[0] + 46
    elif interno:
        d.text((rx0, y), "MIRO: sem a imagem (quadro sem acesso nesta sessão)", fill=(196, 32, 36), font=fr)
        y += 46
    # a planta de layout do projeto: a base do PDF, no mesmo quadro de 3840 x 2160 da prancha
    fb = plano.get("base") or sorted(glob.glob(str(PROJ / f"POE642_Casa{casa}/bases/POE642_Casa{casa}_BASE_{pav}_v*_16x9.png")))[0]
    bi = cv2.imread(str(PROJ / fb) if not str(fb).startswith("/") else fb)
    k = bi.shape[1] / 3840
    tres = bi[int(b0 * k):int(b1 * k), int(a0 * k):int(a1 * k)]
    d.text((rx0, y), "PLANTA DE LAYOUT DO PROJETO", fill=TINTA, font=ft)
    d.text((rx0, y + 38), "a do escritório de arquitetura, no mesmo enquadramento da planta humanizada", fill=CINZA,
           font=fr)
    y += 84
    im3, _ = caber(tres, rw, hmax)
    fl.pg.paste(pil(im3), (rx0, y))
    d.rectangle((rx0 - 1, y - 1, rx0 + im3.shape[1], y + im3.shape[0]), outline=LINHA, width=2)
    y += im3.shape[0] + 46
    d.text((rx0, y), "PLANTA HUMANIZADA", fill=TINTA, font=ft)
    d.text((rx0, y + 38), "os números mostram onde está cada pedido", fill=CINZA, font=fr)
    y += 84
    pr = cv2.imread(str(PROJ / PRANCHA.format(c=casa, p=pav)))
    pl, k = caber(pr[b0:b1, a0:a1], rw, BASE - y)
    pli = pil(pl)
    dp = ImageDraw.Draw(pli)
    r = 19
    fm = F("SemiBold", 16)
    for it in list(pedidos) + list(gs):
        for x, yy in it.get("pontos") or []:
            cx, cy = (x - a0) * k, (yy - b0) * k
            if 0 <= cx <= pli.width and 0 <= cy <= pli.height:
                marca(dp, cx, cy, it["id"], COR[it["id"][0]], r, fm)
    fl.pg.paste(pli, (rx0, y))
    d.rectangle((rx0 - 1, y - 1, rx0 + pli.width, y + pli.height), outline=LINHA, width=2)
    return y + pli.height + 70


def pagina(casa, pav, interno=False):
    plano, pedidos, gs, mel = dados_planta(casa, pav, interno)
    dz = ler("doze_k.json")[f"{casa}_{pav}"]
    doze = cv2.imread(str(PROJ / dz["arquivo"]))
    area = (dz["x0"], dz["y0"], dz["x0"] + doze.shape[1] / dz["s"], dz["y0"] + doze.shape[0] / dz["s"])
    for it in pedidos:
        if not it.get("detalhe"):
            it["detalhe"] = retangulo(it["pontos"], area) if it.get("pontos") else list(plano["recorte"])
    blocos = [bloco_secao("PEDIDOS NO MIRO PARA ESTA PLANTA", COR["C"])]
    blocos += [bloco_pedido(it, doze, dz, interno) for it in pedidos]
    if gs:
        blocos.append(bloco_secao("PEDIDOS GERAIS NO MIRO (VALEM PARA TODAS AS PLANTAS)", COR["G"]))
        blocos += [bloco_geral(g, interno) for g in gs]
    # o fluxo: a 1ª folha numa coluna à esquerda; as de continuação em duas
    folhas = [Folha(casa, pav, 1)]
    yr = plantas(folhas[0], casa, pav, plano, pedidos, gs, interno)
    cw2 = (W - 2 * MARG - 100) // 2
    # (x, largura, topo): na 1ª folha, a coluna da esquerda e o que sobra embaixo das plantas
    colunas = lambda n: ([(MARG, RX0 - 110 - MARG, TOPO), (RX0, W - MARG - RX0, yr)] if n == 1 else
                         [(MARG, cw2, MARG + 190), (MARG + cw2 + 100, cw2, MARG + 190)])
    # as melhorias: no espaço embaixo das plantas, se couberem (1 ou 2 colunas); senão, no fim
    if mel:
        x1, w1, t1 = colunas(1)[1]
        for bm in (bloco_melhorias(mel, 1, 25), bloco_melhorias(mel, 2, 23)):
            if t1 + bm(folhas[0], x1, t1, w1, True) <= BASE:
                bm(folhas[0], x1, t1, w1)
                yr = BASE + 1                                          # a coluna da direita fica cheia
                break
        else:
            blocos.append(bloco_melhorias(mel))
    nf, ci, y = 1, 0, TOPO
    i = 0
    while i < len(blocos):
        x, w, t0 = colunas(nf)[ci]
        h = blocos[i](folhas[-1], x, y, w, True)
        if blocos[i].__qualname__.startswith("bloco_secao") and i + 1 < len(blocos):
            h += blocos[i + 1](folhas[-1], x, y, w, True)            # o título não fica sozinho no pé da coluna
        if y + h > BASE and (y > t0 or BASE - t0 < 0.9 * (BASE - TOPO)):
            ci += 1
            if ci >= len(colunas(nf)):
                nf += 1
                ci = 0
                folhas.append(Folha(casa, pav, nf))
            y = colunas(nf)[ci][2]
            continue
        y += blocos[i](folhas[-1], x, y, w)
        i += 1
    saidas = []
    suf = "_interna" if interno else ""
    for n, fl in enumerate(folhas, 1):
        fl.d.text((W - MARG, H - 40), f"POE 642 · PLANTAS HUMANIZADAS · CONFERÊNCIA DOS PEDIDOS · CASA {casa} – "
                  f"{NOME[pav]} · FOLHA {n}/{len(folhas)}", fill=(160, 160, 160), font=F("Light", 20), anchor="rm")
        out = SAIDA / ("interna" if interno else "cliente") / f"POE642_Conferencia_Casa{casa}_{pav}{suf}_{n}.jpg"
        out.parent.mkdir(parents=True, exist_ok=True)
        fl.pg.save(out, quality=90)
        saidas.append(out)
    print(f"Casa {casa} {pav}: {len(pedidos)} pedidos, {len(gs)} gerais, {len(folhas)} folha(s)")
    return [fl.pg for fl in folhas], saidas


def pdf(paginas, out):
    paginas[0].save(out, save_all=True, append_images=paginas[1:], resolution=300, quality=85)
    print(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("casa", nargs="?")
    ap.add_argument("pav", nargs="?")
    ap.add_argument("--todas", action="store_true")
    ap.add_argument("--interno", action="store_true")
    a = ap.parse_args()
    lista = PLANTAS if a.todas else [(a.casa, a.pav)]
    todas = []
    for c, p in lista:
        pgs, _ = pagina(c, p, a.interno)
        todas += pgs
    if a.todas:
        nome = "POE642_Conferencia_Pedidos_Miro" + ("_interna" if a.interno else "") + ".pdf"
        pdf(todas, SAIDA / nome)

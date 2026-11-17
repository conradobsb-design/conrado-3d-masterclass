"""As portas de giro da Casa E no padrão da Casa D (17/11; levantamento aprovado: "pode aplicar"; e, na porta do BH
gourmet: "garanta que a porta esteja quina a quina com a parede. e que em volta dela não haja piso escuro."), no Térreo
(final e direto nos 12K A e B) e no 1º Pavimento (final).

Cada porta vem do PDF (`pedidos_terreo_casac_1311.portas_pdf`: o arco da ARQ_PAREDE com a folha, o retângulo branco
fino): a parede (as duas faces), o vão (as pontas) e a folha aberta a 90° (o lado e a ponta da dobradiça). Por porta:

1. em volta da folha, do lado do ambiente (a folha e 4 px a mais de cada lado, até a face da parede), o que não é piso
   volta ao piso de logo adiante, no sentido do ambiente (`_destoa_porta`: a folha cinza de antes, os restos brancos do
   batente, o piso escuro (a sombra velha); a parede, escura e sem cor, não entra);
2. a ponta da parede do lado da dobradiça avança até a face da folha (o marco do PDF vira parede): a folha encosta quina
   a quina na ponta da parede;
3. a folha no retângulo do PDF, na madeira clara das portas da Casa D (`um_pav_casaa_1111.RETOQUES_1111F["folha"]`: o
   tom, o veio no comprido, o fio escuro do contorno e a sombra curta).

A pivotante da entrada (a de 2499, 1350, ajustada em 16/11) fica. As soleiras ficam (a do BH gourmet saiu antes, a
pedido).

  python3 portas_casae_1711.py doze [--opcao AB]            (o Térreo; antes da final: a final de antes é a referência)
  python3 portas_casae_1711.py final [--pav Terreo|1Pavimento]
"""
import argparse
import contextlib
import io
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import danae_foto as DF                                     # noqa: E402
import correcoes_terreo_casab_1611 as CB                    # noqa: E402
import instalacao_terreo_casad_1711 as ID                   # noqa: E402
from correcoes_terreo_casab_1611 import Mapa                # noqa: E402
from janela_pia_casaa_1611 import alfa_ret                  # noqa: E402

RAIZ = AQUI.parents[1]
FINAIS = {"Terreo": RAIZ / "POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_final.png",
          "1Pavimento": RAIZ / "POE642_CasaE/renders/POE642_CasaE_PH_1Pavimento_v1_final.png"}
DOZE = RAIZ / "POE642_CasaE/entrega/POE642_CasaE_PH_Terreo_12K_opcao_{}.jpg"

FOLHA = {"madeira": (134, 166, 202), "contorno": (58, 72, 92), "contorno_alfa": 0.95, "contorno_px": 0.45,
         "veio": 0.05, "sombra": 0.28, "sombra_px": (-0.8, 1.0, 0.9), "parede": (80, 80, 80)}
PULAR = ("porta em (2499, 1350)",)
# no Térreo a folha de antes estava longe da ponta (o marco do PDF no render): a folha encosta na ponta de parede do
# render; no 1º Pavimento a folha de antes está no lugar do PDF e o resto branco do batente fica entre ela e a ponta:
# a ponta de parede avança até a face da folha (o padrão da Casa D), cobrindo o resto
MODO = {"Terreo": "encosta_folha", "1Pavimento": "estende_parede"}
# a ordem das fontes de piso: no granito do Térreo, para o ambiente; no 1º Pavimento (as réguas de madeira deitadas),
# ao longo da folha primeiro (a régua continua)
ORDEM = {"Terreo": "ambiente", "1Pavimento": "ao_longo"}                 # a pivotante da entrada (e a dela vista no PDF do 1º Pavimento)
# a caixa da limpeza: `folga` px de cada lado da folha (até a face da parede: a faixa de piso escuro entre a parede e a
# folha entra), `ponta` px além da ponta; o piso vem de `desloc` px adiante, para o ambiente (além da folha de antes)
LIMPA = {"folga": 7.0, "ponta": 5.0, "desloc": 14.0}
# os ajustes porta a porta (o nome de `portas_pdf`, px da imagem): "limpa" (a caixa), "sentidos" (as fontes, em ordem)
AJUSTES = {"Terreo": {
    # o DCE: a barra bege do batente de antes, junto ao armário, também sai
    "porta em (2287, 609)": {"extra_render": [(2257.9, 585.0, 2265.0, 629.0)]},
    # o BH gourmet: a mancha clara na ponta da parede (a sobra do remendo da soleira) também
    "porta em (1421, 523)": {"extra_render": [(1445.5, 496.0, 1456.0, 512.0)]},
    # o WC DCE 1: a folha não aparecia (só a soleira); nada a limpar (o piso claro do WC fica)
    "porta em (2416, 603)": {"limpa": None}},
    "1Pavimento": {}}
# as 3 portas do Térreo cuja folha no PDF é a de veneziana (em pedaços: as pontas cheias, o miolo estreito), fora de
# `portas_pdf`: a folha (o retângulo inteiro), a ponta da parede até a face dela, a limpeza e as fontes de piso
EXTRAS = {"Terreo": {
    "porta em (2190, 534)": {"folha": (2209.9, 512.2, 2212.3, 556.6), "parede": (2212.3, 554.6, 2213.9, 563.5),
                             "limpa": (2205.5, 509.0, 2216.5, 554.6),
                             "sentidos": [(-14.0, 0.0), (-14.0, 11.0), (-14.0, -11.0)], "deitada": False},
    "porta em (2054, 459)": {"folha": (2030.1, 435.1, 2032.5, 482.9), "parede": (2027.1, 425.0, 2030.1, 435.1),
                             "limpa": (2025.5, 435.1, 2037.0, 486.0), "sentidos": [(14.0, 0.0)], "deitada": False},
    "porta em (1984, 399)": {"folha": (2005.3, 375.4, 2007.7, 423.2), "parede": (2007.7, 423.2, 2010.7, 433.4),
                             "limpa": (2000.0, 372.0, 2011.0, 423.2), "sentidos": [(-14.0, 0.0)], "deitada": False}},
    "1Pavimento": {}}


def _imagem(p, deitada):
    """A porta de `portas_pdf` (deitada: na imagem transposta) em px da imagem: a folha, a ponta de parede que avança
    até a face dela, a caixa da limpeza e o sentido do ambiente."""
    xa, xb = p["parede"]
    yt, yb = p["topo"], p["base"]
    fx0, fy0, fx1, fy1 = p["folha"]
    q = dict(LIMPA, **p.get("ajuste", {}))
    f, pt = q["folga"], q["ponta"]
    e = 0.6                                           # a ponta de parede cobre o antisserrilhado da soleira
    if p["dobra"] == "topo":
        parede = (xa - e, yt, xb + e, fy0)
        sentido = (0.0, q["desloc"])
    else:
        parede = (xa - e, fy1, xb + e, yb)
        sentido = (0.0, -q["desloc"])
    m0 = q.get("margem", 1.2)                         # longe da face da parede: a soleira e o fio dela ficam
    if p["lado"] < 0:
        limpa = (fx0 - pt, fy0 - f, xa - m0, fy1 + f)
    else:
        limpa = (xb + m0, fy0 - f, fx1 + pt, fy1 + f)
    folha = (fx0, fy0, fx1, fy1)
    # no vão junto à dobradiça, só o cinza da folha de antes (a ponta dela sobre a soleira ou junto à face): o vão de
    # logo adiante no lugar
    if p["dobra"] == "topo":
        vao, sv = (xa - 1.5, yt - 0.5, xb + 1.5, yt + 8.0), (0.0, 10.0)
    else:
        vao, sv = (xa - 1.5, yb - 8.0, xb + 1.5, yb + 0.5), (0.0, -10.0)
    if deitada:
        t = lambda r: (r[1], r[0], r[3], r[2])          # noqa: E731
        res = {"folha": t(folha), "parede": t(parede), "limpa": t(limpa), "sentidos": [sentido[::-1]],
               "vao": t(vao), "sentido_vao": sv[::-1], "deitada": True}
    else:
        res = {"folha": folha, "parede": parede, "limpa": limpa, "sentidos": [sentido], "vao": vao,
               "sentido_vao": sv, "deitada": False}
    for k in ("limpa", "sentidos", "extra_render"):
        if k in p.get("ajuste", {}):
            res[k] = p["ajuste"][k]
    return res


def _parede_pdf(Q, janela, k=4):
    """A máscara das paredes do PDF (ARQ_PAREDE, o cinza) na janela (px da final), `k` vezes maior."""
    x0, y0, x1, y1 = janela
    m = np.zeros(((y1 - y0) * k, (x1 - x0) * k), np.uint8)
    for d in Q.desenhos:
        if d.get("layer") != "ARQ_PAREDE" or not d.get("fill") or min(d["fill"]) > 0.5:
            continue
        r = d["rect"]
        a, b = Q.p2q(r.x0, r.y0), Q.p2q(r.x1, r.y1)
        if max(a[0], b[0]) < x0 or min(a[0], b[0]) > x1 or max(a[1], b[1]) < y0 or min(a[1], b[1]) > y1:
            continue
        for c in Q.caminhos(d):
            pts = np.round((np.asarray(c, np.float64) - [x0, y0]) * k).astype(np.int32)
            cv2.fillPoly(m, [pts], 1)
    return m.astype(np.float32)


def desvio(Q, img, janela, k=4, raio=4.0):
    """O desvio (dx, dy) do render ao PDF perto da porta: o deslocamento que mais casa as paredes do PDF com as da
    imagem (o cinza 80), em passos de 1/k px, até `raio` px."""
    x0, y0, x1, y1 = janela
    pdf = _parede_pdf(Q, janela, k)
    reg = img[y0:y1, x0:x1].astype(np.int16)
    par = (np.abs(reg - 80).max(axis=2) <= 14).astype(np.float32)
    par = cv2.resize(par, (pdf.shape[1], pdf.shape[0]), interpolation=cv2.INTER_LINEAR)
    R = int(raio * k)
    melhor, arg = -1.0, (0, 0)
    pp = np.pad(pdf, R)
    for dy in range(-R, R + 1):
        for dx in range(-R, R + 1):
            v = float((pp[R - dy:R - dy + pdf.shape[0], R - dx:R - dx + pdf.shape[1]] * par).sum())
            if v > melhor:
                melhor, arg = v, (dx, dy)
    return arg[0] / k, arg[1] / k


def desvio_vao(img, p):
    """O desvio do render ao PDF medido no próprio vão (no espaço da porta: a imagem transposta para as deitadas):
    as faces da parede logo além da ponta da dobradiça (dx: a mediana de 5 linhas, a 3 a 7 px da ponta; os fios
    escuros de dentro da parede não partem a corrida; numa quina, a face que continua além da janela não conta) e a
    ponta dela, vinda de dentro do vão (dy)."""
    xa, xb = p["parede"]
    yt, yb = p["topo"], p["base"]
    par = (np.abs(img.astype(np.int16) - 80).max(axis=2) <= 14)
    topo = p["dobra"] == "topo"
    x0, x1 = int(np.floor(xa)) - 8, int(np.ceil(xb)) + 8
    dxs = []
    for k in range(3, 8):
        yw = int(round(yt - k)) if topo else int(round(yb + k))
        perfil = par[yw, x0:x1].astype(np.uint8)
        perfil = cv2.morphologyEx(perfil[None, :], cv2.MORPH_CLOSE, np.ones((1, 3), np.uint8))[0] > 0
        idx = np.nonzero(perfil)[0]
        if len(idx) < 4:
            continue
        grupos = np.split(idx, np.nonzero(np.diff(idx) > 1)[0] + 1)
        g = max(grupos, key=len)
        lados = []
        if g[0] > 0:
            lados.append(x0 + g[0] - xa)
        if g[-1] < len(perfil) - 1:
            lados.append(x0 + g[-1] + 1 - xb)
        if lados:
            dxs.append(float(np.mean(lados)))
    if not dxs:
        return 0.0, None
    dx = float(np.median(dxs))
    xc = int(round((xa + xb) / 2 + dx))
    yc = int(round((yt + yb) / 2))
    col = par[:, xc - 1:xc + 2].mean(axis=1) > 0.5
    if topo:
        y = yc
        while y > yc - 80 and not col[y]:
            y -= 1
        ponta = float(y + 1)
        ok = abs(ponta - yt) <= 5
    else:
        y = yc
        while y < yc + 80 and not col[y]:
            y += 1
        ponta = float(y)
        ok = abs(ponta - yb) <= 5
    if abs(dx) > 4 or not ok:
        return 0.0, None
    return float(dx), ponta


def _mover(r, d):
    return None if r is None else (r[0] + d[0], r[1] + d[1], r[2] + d[0], r[3] + d[1])


def portas(pav, img=None):
    import final3840_casae as FE
    import pedidos_terreo_casac_1311 as PT
    with contextlib.redirect_stdout(io.StringIO()):
        Q = FE.QuadroE(pav)
    em_pe, deitadas, _ = PT.portas_pdf(Q, dict(PT.PORTAS, r_min=20, r_max=80))
    res = {}
    imgT = None if img is None else np.ascontiguousarray(img.transpose(1, 0, 2))
    for lista, dt in ((em_pe, False), (deitadas, True)):
        for p in lista:
            if p["nome"] in PULAR:
                continue
            if img is not None:
                # a porta no lugar do render: as faces da parede (dx) e a folha encostada na ponta de parede que
                # o render tem (quina a quina, sem o marco do PDF: a parede não muda, a soleira fica inteira)
                dx, ponta = desvio_vao(imgT if dt else img, p)
                fx0, fy0, fx1, fy1 = p["folha"]
                xa, xb = p["parede"]
                yt, yb = p["topo"], p["base"]
                dy = 0.0
                if ponta is not None:
                    folga = (fy0 - ponta) if p["dobra"] == "topo" else (ponta - fy1)
                    if MODO[pav] == "estende_parede" and folga > 0:
                        if p["dobra"] == "topo":       # a parede da ponta do render até a face da folha
                            yt = ponta
                        else:
                            yb = ponta
                    elif p["dobra"] == "topo":
                        dy, yt = ponta - fy0, ponta
                    else:
                        dy, yb = ponta - fy1, ponta
                p = dict(p, parede=(xa + dx, xb + dx), topo=yt, base=yb,
                         folha=(fx0 + dx, fy0 + dy, fx1 + dx, fy1 + dy), desvio=(dx, dy))
            nome = p["nome"]
            if dt:
                a, b = nome[nome.index("(") + 1:nome.index(")")].split(", ")
                nome = f"porta em ({b}, {a})"
            p = dict(p, ajuste=AJUSTES[pav].get(nome, {}))
            res[nome] = _imagem(p, dt)
            if "desvio" in p:
                d = p["desvio"]
                res[nome]["desvio"] = (d[1], d[0]) if dt else d
    res.update(EXTRAS[pav])
    if img is not None:                              # as de veneziana: o desvio pelo casamento das paredes
        for nome in EXTRAS[pav]:
            p = res[nome]
            rs = [r for r in (p["limpa"], p["folha"], p["parede"]) if r is not None]
            jan = (int(min(r[0] for r in rs)) - 20, int(min(r[1] for r in rs)) - 20,
                   int(max(r[2] for r in rs)) + 20, int(max(r[3] for r in rs)) + 20)
            d = desvio(Q, img, jan)
            res[nome] = dict(p, limpa=_mover(p["limpa"], d), folha=_mover(p["folha"], d),
                             parede=_mover(p["parede"], d), desvio=d)
    return res


def _destoa_porta(med, lim=5.0, neutro=False):
    """O que não é piso na caixa da folha: o cinza da folha de antes e os restos brancos (pouca cor, claros), o piso
    escuro ou claro demais (com cor, longe do tom `med` do piso de fora da caixa); a parede (escura, sem cor) fica.
    No piso sem cor (os banhos claros), o tom basta: o que se afasta dele, fora a parede."""
    def f(reg):
        L = reg.mean(axis=2)
        cr = reg.max(axis=2) - reg.min(axis=2)
        if neutro:
            return (L > 105) & (np.abs(L - med) > max(lim, 6.0))
        cinza = (cr < 14) & (L > 105)
        mancha = (cr >= 14) & (L > 60) & (np.abs(L - med) > lim)
        return cinza | mancha
    return f


def _cinza(reg):
    L = reg.mean(axis=2)
    cr = reg.max(axis=2) - reg.min(axis=2)
    return (cr < 14) & (L > 105)


def _vao(out, m, r, d):
    """O vão junto à dobradiça (a ponta da folha de antes sobre a soleira, os fios dela, o toco junto à face): o que
    não é parede vem do vão de logo adiante, na mesma linha (a soleira ou o piso), se lá não for cinza nem parede."""
    s = m.s
    rm = m.ret(r)
    X0, Y0, X1, Y1 = int(np.floor(rm[0])), int(np.floor(rm[1])), int(np.ceil(rm[2])), int(np.ceil(rm[3]))
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    parede = np.abs(reg.mean(axis=2) - 80) <= 8
    dx, dy = int(round(d[0] * s)), int(round(d[1] * s))
    F = out[Y0 + dy:Y1 + dy, X0 + dx:X1 + dx].astype(np.float32)
    LF = F.mean(axis=2)
    cinzaF = _cinza(F) & (LF < 200)                    # o piso claro sem cor dos banhos não é a folha
    ok = ~parede & ~cinzaF & ~(np.abs(LF - 80) <= 8)
    a = alfa_ret((rm[0] - X0, rm[1] - Y0, rm[2] - X0, rm[3] - Y0), reg.shape[:2]) * ok
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg * (1 - a[..., None]) + F * a[..., None]), 0, 255).astype(np.uint8)


def _remendo(out, m, r, ds, marca_f, med, tol=6.0, neutro=False):
    """Os px marcados na caixa r (px da final) recebem o piso deslocado do 1º d de ds que caia em piso de verdade (com
    cor e no tom `med` ± `tol`: a borda das letras, a parede e a folha de antes não servem)."""
    s = m.s
    rm = m.ret(r)
    X0, Y0, X1, Y1 = int(np.floor(rm[0])), int(np.floor(rm[1])), int(np.ceil(rm[2])), int(np.ceil(rm[3]))
    A = alfa_ret((rm[0] - X0, rm[1] - Y0, rm[2] - X0, rm[3] - Y0), (Y1 - Y0, X1 - X0))
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    k = max(1, int(round(0.5 * s)))
    marca = cv2.dilate(marca_f(reg).astype(np.uint8), np.ones((2 * k + 1, 2 * k + 1), np.uint8)) > 0
    # a parede e o antisserrilhado dela (1 px em volta) ficam: a face continua reta
    Lr, cr_ = reg.mean(axis=2), reg.max(axis=2) - reg.min(axis=2)
    kp = max(1, int(round(1.0 * s)))
    par = cv2.dilate(((np.abs(Lr - 80) <= 12) & (cr_ < 14)).astype(np.uint8), np.ones((2 * kp + 1, 2 * kp + 1), np.uint8))
    branco = Lr > (med + 12 if neutro else 225)      # o resto branco do batente encostado na parede sai mesmo assim
    marca &= ~(par > 0) | branco
    novo, feito = reg.copy(), np.zeros(marca.shape, bool)
    for d in ds:
        dx, dy = int(round(d[0] * s)), int(round(d[1] * s))
        F = out[Y0 + dy:Y1 + dy, X0 + dx:X1 + dx].astype(np.float32)
        if F.shape != reg.shape:
            continue
        LF, cF = F.mean(axis=2), F.max(axis=2) - F.min(axis=2)
        bom = (np.abs(LF - med) < tol) & (((cF >= 14) & (not neutro)) | (neutro & (cF < 20)))
        bom = cv2.erode(bom.astype(np.uint8), np.ones((2 * k + 1, 2 * k + 1), np.uint8)) > 0
        ok = marca & ~feito & bom
        novo[ok], feito = F[ok], feito | ok
    # o que sobrou marcado (nenhuma fonte limpa): o piso em volta (o inpaint, já com o resto refeito) e o grão da 1ª
    # fonte
    resto = marca & ~feito
    if resto.any():
        base = np.clip(novo, 0, 255).astype(np.uint8)
        inp = cv2.inpaint(base, resto.astype(np.uint8) * 255, max(3, int(round(3 * s))), cv2.INPAINT_TELEA)
        dx, dy = int(round(ds[0][0] * s)), int(round(ds[0][1] * s))
        F = out[Y0 + dy:Y1 + dy, X0 + dx:X1 + dx].astype(np.float32)
        if F.shape == reg.shape:
            # o grão só de piso de verdade (as letras de um rótulo na fonte não entram), limitado
            LF, cF = F.mean(axis=2), F.max(axis=2) - F.min(axis=2)
            bomF = (((cF >= 14) | neutro) & (np.abs(LF - med) < tol)).astype(np.float32)[..., None]
            grao = np.clip((F - cv2.GaussianBlur(F, (0, 0), 1.5 * s)) * bomF, -12, 12)
        else:
            grao = 0.0
        enche = cv2.GaussianBlur(inp.astype(np.float32), (0, 0), 0.8 * s) + grao
        novo[resto] = enche[resto]
        feito = feito | resto
    a = A * feito
    if s > 1.5:
        a = A * np.clip(cv2.GaussianBlur(feito.astype(np.float32), (0, 0), 0.35 * s) * 1.6, 0, 1)
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg * (1 - a[..., None]) + novo * a[..., None]), 0, 255).astype(np.uint8)


def folha(out, m, r, deitada, semente, q=FOLHA):
    s = m.s
    rm = m.ret(r)
    g = int(np.ceil(3 * s)) + 2
    X0, Y0 = int(np.floor(rm[0])) - g, int(np.floor(rm[1])) - g
    X1, Y1 = int(np.ceil(rm[2])) + g, int(np.ceil(rm[3])) + g
    forma = (Y1 - Y0, X1 - X0)
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    loc = (rm[0] - X0, rm[1] - Y0, rm[2] - X0, rm[3] - Y0)
    a = alfa_ret(loc, forma)
    c = q["contorno_px"] * s
    a_in = alfa_ret((loc[0] + c, loc[1] + c, loc[2] - c, loc[3] - c), forma)
    borda = np.clip(a - a_in, 0, 1) * q["contorno_alfa"]
    # a sombra curta, fora da folha
    sx, sy, sg = q["sombra_px"]
    M = np.float32([[1, 0, sx * s], [0, 1, sy * s]])
    sb = cv2.GaussianBlur(cv2.warpAffine(a, M, (forma[1], forma[0])), (0, 0), sg * s)
    reg *= (1 - q["sombra"] * sb * (1 - a))[..., None]
    # a madeira com o veio no comprido
    rng = np.random.default_rng(semente)
    n = rng.normal(0, 1, forma).astype(np.float32)
    sl, sc = 6.0 * s, 0.6 * s
    n = cv2.GaussianBlur(n, (0, 0), sigmaX=sc if deitada else sl, sigmaY=sl if deitada else sc)
    n = 1 + q["veio"] * n / max(float(n.std()), 1e-6)
    cor = np.float32(q["madeira"])[None, None] * n[..., None]
    reg = reg * (1 - a[..., None]) + cor * a[..., None]
    reg = reg * (1 - borda[..., None]) + np.float32(q["contorno"]) * borda[..., None]
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)


# px do render: o ponto branco na face da parede junto à porta da área descoberta (a ponta do tracejado)
PINTA_PAREDE = {"Terreo": [(2215.6, 536.5, 2217.0, 540.0)], "1Pavimento": []}


def pinta_parede(out, mp, pav):
    for r in PINTA_PAREDE[pav]:
        c = (int(r[0]) - 20, int(r[1]) - 20, int(r[2]) + 20, int(r[3]) + 20)
        m = mp.local(out, c) if mp.ref is not None else mp
        CB.pintar(out, m, [(r, "ret", FOLHA["parede"], 0)])


def aplicar(img, mp, pav, so=None, ref=None):
    out = img.copy()
    ps = portas(pav, ref if ref is not None else img)
    for i, (nome, p) in enumerate(sorted(ps.items())):
        if so and nome not in so:
            continue
        x0, y0, x1, y1 = p["limpa"] or p["folha"]
        caixa = (int(x0) - 25, int(y0) - 25, int(x1) + 25, int(y1) + 25)
        m = mp.local(out, caixa) if mp.ref is not None else mp
        if p["limpa"] is None:
            CB.pintar(out, m, [(p["parede"], "ret", FOLHA["parede"], 0)])
            folha(out, m, p["folha"], p["deitada"], 1711 + i)
            print(f"    {nome}: a folha quina a quina com a ponta da parede")
            continue
        # as fontes: a do ambiente, mais adiante nela, e ao longo da folha (dos dois lados), na ordem
        d0 = p["sentidos"][0]
        fx0, fy0, fx1, fy1 = p["folha"]
        ao_longo = (30.0, 0.0) if (fx1 - fx0) > (fy1 - fy0) else (0.0, 30.0)
        if ORDEM[pav] == "ao_longo":
            sentidos = [ao_longo, (-ao_longo[0], -ao_longo[1])] + list(p["sentidos"]) + [(d0[0] * 1.8, d0[1] * 1.8)]
        else:
            sentidos = list(p["sentidos"]) + [(d0[0] * 1.8, d0[1] * 1.8), ao_longo, (-ao_longo[0], -ao_longo[1])]
        # o tom do piso: o da 1ª fonte (fora da caixa)
        rm = m.reti(p["limpa"])
        ddx, ddy = int(round(d0[0] * m.s)), int(round(d0[1] * m.s))
        F = out[rm[1] + ddy:rm[3] + ddy, rm[0] + ddx:rm[2] + ddx].astype(np.float32)
        LF, cF = F.mean(axis=2), F.max(axis=2) - F.min(axis=2)
        neutro = float(np.median(cF)) < 14
        sel = (LF > 105) if neutro else (cF >= 14)
        amostra = LF[sel] if sel.sum() > 10 else LF.ravel()
        med = float(np.median(amostra))
        # a variação do próprio piso (as réguas de madeira variam de tom; o granito e o mármore, pouco)
        q1, q3 = np.percentile(amostra, [25, 75])
        lim = max(5.0, 2.0 * (q3 - q1) / 1.35)
        _remendo(out, m, p["limpa"], sentidos, _destoa_porta(med, lim, neutro), med, tol=max(6.0, lim),
                 neutro=neutro)
        for r in p.get("extra_render", []):
            _remendo(out, m, r, sentidos, _destoa_porta(med, lim, neutro), med, tol=max(6.0, lim), neutro=neutro)
        if "vao" in p:
            _vao(out, m, p["vao"], p["sentido_vao"])
        CB.pintar(out, m, [(p["parede"], "ret", FOLHA["parede"], 0)])
        folha(out, m, p["folha"], p["deitada"], 1711 + i)
        print(f"    {nome} (desvio {p.get('desvio', (0, 0))}): a folha quina a quina com a ponta da parede, sem o "
              f"piso escuro em volta")
    if not so:
        pinta_parede(out, mp, pav)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("acao", choices=("final", "doze", "lista"))
    ap.add_argument("--pav", default="Terreo")
    ap.add_argument("--opcao", default="AB")
    ap.add_argument("--entrada")
    ap.add_argument("--saida")
    ap.add_argument("--so")
    a = ap.parse_args()
    so = a.so.split(";") if a.so else None
    if a.acao == "lista":
        for nome, p in sorted(portas(a.pav, cv2.imread(str(FINAIS[a.pav]))).items()):
            print(nome, {k: (tuple(round(v, 1) for v in w) if isinstance(w, tuple) else w) for k, w in p.items()})
        return
    fin = cv2.imread(a.entrada or str(FINAIS[a.pav]))
    if a.acao == "final":
        cv2.imwrite(a.saida or str(FINAIS[a.pav]), aplicar(fin, Mapa(), a.pav, so))
        return
    from PIL import Image
    for op in a.opcao:
        f = Path(str(DOZE).format(op))
        img = cv2.imread(str(f))
        M = DF.afim_12k(fin, img)
        mp = Mapa(float(np.hypot(M[0, 0], M[1, 0])), (float(M[0, 2]), float(M[1, 2])))
        mp.ref = fin
        out = aplicar(img, mp, "Terreo", so, ref=fin)
        dpi = int(round(out.shape[1] / (420 / 25.4)))
        dest = a.saida.format(op) if a.saida else str(f)
        Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB)).save(dest, quality=95, subsampling=0, dpi=(dpi, dpi))
        print(f"    {Path(dest).name}")


if __name__ == "__main__":
    main()

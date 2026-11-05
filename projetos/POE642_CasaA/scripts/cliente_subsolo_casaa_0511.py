r"""Casa A, Subsolo: as alterações do cliente de 05/11/26, sobre a final de c1f7ff5.

Pedidos do cliente, cada um com o recorte da planta do Subsolo (e o resumo do usuário):
1. "Diminuir a escala da grama";
2. "Colocar a seta na escada e a descrição - Sobe para o Deck." (usuário: "Adicionar a seta no sentido e descrever
   'Sobe', em vez da letra S, apenas", e, com o recorte do triângulo cheio na escada: "seta na escada é assim");
3. "Tirar a representação do deck e da piscina superior. Deixar apenas o subsolo mesmo.";
4. "Representar as prateleiras com uma cor neutra única, sem textura" (o depósito);
5. "Deixar sem hachura. Deixar na cor branca. Sem fundo." (o entorno);
6. depois (usuário, com o recorte da madeira da academia): "remover essas linhas" (a projeção clara junto à parede de
   baixo).

Os itens 3 e 5 são um passo só (`fundo_branco_cs`): fora da pegada do Subsolo, tudo branco. Cada item é um passo aqui,
sobre a final; a ordem conta (o branco primeiro, porque a borda da pegada desfaz a hachura de antes pela conta dela).

Uso (uma vez, sobre a final de c1f7ff5):
  python3 cliente_subsolo_casaa_0511.py [--antes <png>] [--saida <png>]
"""
import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import ajustes_casaa as AJ                      # noqa: E402
import final3840_casaa as FA                    # noqa: E402
import pedidos_terreo_casaa_2910 as PT          # noqa: E402

FINAL_SUB = FA.CASA / "renders" / "POE642_CasaA_PH_Subsolo_final_rotulos.png"


# ----------------------------------------------------------------------------------------------------------------------
# 3 e 5. Só o Subsolo, em branco em volta. A pegada é a de R2 (`ajustes_casaa.SUBSOLO_R2`: os pisos e as paredes do
# Subsolo no PDF, a escada do deck e o gramado), levada ao quadro pelo mesmo afim da final (`rotulos_casaa.final_imagem`).
# Fora dela saem a hachura do lote, o contorno do lote e as peças do Térreo nevoadas (o deck, a piscina, o spa, os
# pisantes e as espreguiçadeiras). Nos px da borda (a pegada entre 0 e 1), a final é a mistura do Subsolo com a hachura
# (`ajustes_casaa.subsolo_hachurado`); a hachura sai pela conta dela (as mesmas diagonais), e no lugar entra o branco.
def pegada_quadro():
    from PIL import Image
    import rotulos_casaa as R
    q = R.PAVIMENTOS["Subsolo"]
    cfg = json.loads(R.CONFIG.read_text())
    base = (R.CONFIG.parent / cfg["entrega"]["pasta_bases"] / cfg["entrega"]["pavimentos"]["Subsolo"]["base"]).resolve()
    _, peg = R.no_quadro_fixo(Image.open(R.CASA / q["render"]).convert("RGB"),
                              Image.open(R.CASA / q["aprovada"]).convert("RGB"), base, "Subsolo",
                              mascara=cv2.imread(str(R.CASA / q["pegada"]), cv2.IMREAD_GRAYSCALE))
    return peg.astype(np.float32) / 255


def fundo_branco_cs(Q, img, p):
    h = AJ.SUBSOLO_R2["hachura"]
    H, W = img.shape[:2]
    s = h["passo_m"] * Q.px_m
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    fr = np.mod((xx + yy) / np.sqrt(2), s)
    a = np.clip(h["largura_px"] / 2 + 0.5 - np.minimum(fr, s - fr), 0, 1)[..., None]
    fundo = 255 * (1 - a) + np.float32(h["cor"]) * a
    out = img.astype(np.float32) + (255 - fundo) * (1 - p[..., None])
    out[p <= 0.001] = 255
    print(f"    entorno em branco: {int((p < 0.5).sum())} px fora da pegada (sem a hachura, o lote e o nevoado do Térreo)")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# A borda da pegada: ela passa uns px do desenho do Subsolo (o anel das paredes do render e a caixa das linhas da escada),
# e ali ficavam uma faixa azulada (o nevoado da piscina, acima da parede de cima e à esquerda do banho de serviço) e uma
# faixa clara com os riscos da hachura (em cima e à esquerda dos degraus). O desenho é o do PDF: as peças cheias da
# ARQ_CONTRAPISO e da ARQ_PAREDE na caixa do Subsolo (as de `SUBSOLO_R2`), os degraus (`DEGRAUS_A`, com o trecho
# esmaecido depois do corte) e a grama (o verde, crescido `grama_px`). Fora dele, só o que é sobra vira branco (na
# cobertura do desenho): o claro (`claro_min`) neutro (a hachura, `neutro_max`) ou azulado (o nevoado, B acima de R);
# o Bege do pátio, a grama e as paredes ficam.
BORDA_CS = {"grama_px": 3, "claro_min": 140, "neutro_max": 20, "azul": 5}


def borda_cs(Q, img, p):
    q = BORDA_CS
    r2 = AJ.SUBSOLO_R2
    cx0, cy0, cx1, cy1 = r2["caixa_pt"]
    core = Q.preencher(lambda d: d.get("layer") in r2["camadas"] and cx0 <= d["rect"].x0 and d["rect"].x1 <= cx1
                       and cy0 <= d["rect"].y0 and d["rect"].y1 <= cy1)
    x0, y0, x1, y1 = GRAMA_CS["caixa"]
    ri = img[y0:y1, x0:x1].astype(np.int32)
    verde = np.zeros(p.shape, np.uint8)
    verde[y0:y1, x0:x1] = (ri[..., 1] > ri[..., 2] + GRAMA_CS["verde"]) & (ri[..., 1] > ri[..., 0] + GRAMA_CS["verde"])
    k = 2 * q["grama_px"] + 1
    verde = cv2.dilate(verde, np.ones((k, k), np.uint8)).astype(bool)
    desenho = np.maximum(np.maximum(core, FA.ret_aa(Q, FA.DEGRAUS_A["pt"])), p * verde)
    i16 = img.astype(np.int16)
    sobra = ((p > 0.001) & (desenho < 0.5) & (i16.min(axis=2) >= q["claro_min"])
             & ((i16.max(axis=2) - i16.min(axis=2) <= q["neutro_max"]) | (i16[..., 0] > i16[..., 2] + q["azul"])))
    out = img.copy()
    d3 = desenho[..., None]
    out[sobra] = np.clip(np.round(img.astype(np.float32) * d3 + 255 * (1 - d3)), 0, 255).astype(np.uint8)[sobra]
    print(f"    borda: {int(sobra.sum())} px de sobra (o nevoado e a hachura) fora do desenho do Subsolo, em branco")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# Depois (o cliente, com o recorte do pátio: "Deixar a representação do Bege Bahia menos manchado (para melhor
# representação)"): o Bege Bahia dos pisos (pátio, circulação, depósito e banho de serviço) é a luz do lugar vezes o
# desenho da foto da biblioteca, D = T / média(T) (`final3840_casab.piso_textura`, "bege", com a máscara e a semente de
# `final3840_casaa.PISOS_A`; refeito aqui, ele bate com a final px a px). O desenho troca por 1 + `forca` (D - 1): as
# manchas com menos contraste, e a luz, as sombras e o tom ficam. Onde a marca sob o armário foi tirada
# (`final3840_casaa.MARCAS_BEGE`), o desenho é o do trecho ao lado, na mesma mistura. Os objetos pintados depois do
# piso (rótulos, portas, soleiras, prateleiras) ficam de fora: os px em que a final dividida pelo desenho foge da luz
# em volta (`desvio`), com `folga_px`.
# Depois (usuário, com o recorte do depósito: "vamos corrigir esse erro no L da prateleira. tem um borrão antigo do
# material anterior"): junto às prateleiras ficava a borda do freijó misturada ao piso (os px de cobertura parcial) e a
# faixa de piso de fora da suavização, com a sombra antiga. Na faixa das prateleiras (a cobertura delas crescida
# `faixa_px`), o piso é refeito pelo modelo: a luz de cada canal no piso limpo em volta (sem a faixa, normalizada em
# `sig_px`) vezes o desenho suavizado. As prateleiras e a sombra curta delas são pintadas de novo depois
# (`prateleiras_cs`).
BEGE_CS = {"forca": 0.45, "sig_px": 4.0, "desvio": 0.06, "folga_px": 2, "faixa_px": 5}


def faixa_prateleiras(Q, folga_px):
    c = np.zeros((Q.H, Q.W), np.float32)
    for r, _ in FA.DEPOSITO["pecas"]:
        c = np.maximum(c, FA.ret_aa(Q, r))
    k = 2 * folga_px + 1
    return cv2.dilate((c > 0).astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool)


def bege_cs(Q, img):
    sys.path.insert(0, str(FA.A.RAIZ / "_texturas"))
    from texturas import textura
    q = BEGE_CS
    pb = FA.PISOS_A["Bege Bahia"]
    Q.ini = FA.inicial(Q)
    m = FA.mascara_piso(Q, pb["rets"])
    ys, xs = np.nonzero(m)
    y0, x0, y1, x1 = ys.min(), xs.min(), ys.max() + 1, xs.max() + 1
    T = textura("bege_bahia", Q.px_m, y1 - y0, x1 - x0, semente=pb["semente"]).astype(np.float32)
    D = np.ones((Q.H, Q.W, 3), np.float32)
    D[y0:y1, x0:x1] = T / T.reshape(-1, 3).mean(axis=0)
    for mk in FA.MARCAS_BEGE:
        a0, b0, a1, b1 = mk["q"]
        dx, dy = mk["desloc"]
        a = np.zeros((b1 - b0, a1 - a0), np.float32)
        a[3:-3, 3:-3] = 1
        a = (cv2.GaussianBlur(a, (0, 0), 1.5) * m[b0:b1, a0:a1])[..., None]
        D[b0:b1, a0:a1] = D[b0:b1, a0:a1] * (1 - a) + D[b0 + dy:b1 + dy, a0 + dx:a1 + dx] * a
    cur = img.astype(np.float32)
    luz = (cur / D).mean(axis=2)
    w = m.astype(np.float32)
    L = cv2.GaussianBlur(luz * w, (0, 0), q["sig_px"]) / np.maximum(cv2.GaussianBlur(w, (0, 0), q["sig_px"]), 1e-3)
    obj = ~m | (np.abs(luz - L) > q["desvio"] * L)
    k = 2 * q["folga_px"] + 1
    ok = m & ~cv2.dilate(obj.astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool)
    Dn = 1 + q["forca"] * (D - 1)
    out = img.copy()
    out[ok] = np.clip(np.round(cur[ok] * Dn[ok] / D[ok]), 0, 255).astype(np.uint8)
    # a faixa das prateleiras: o piso pelo modelo (a luz de cada canal no piso limpo em volta)
    faixa = faixa_prateleiras(Q, q["faixa_px"]) & m
    limpo = (ok & ~faixa).astype(np.float32)
    den = np.maximum(cv2.GaussianBlur(limpo, (0, 0), q["sig_px"]), 1e-3)
    luz_c = np.stack([cv2.GaussianBlur((cur[..., c] / D[..., c]) * limpo, (0, 0), q["sig_px"]) / den
                      for c in range(3)], axis=2)
    out[faixa] = np.clip(np.round(luz_c[faixa] * Dn[faixa]), 0, 255).astype(np.uint8)
    print(f"    Bege Bahia: as manchas a {q['forca']:.0%} do contraste ({int(ok.sum())} px; "
          f"{int((m & ~ok & ~faixa).sum())} px de objetos e bordas ficam); na faixa das prateleiras, o piso refeito "
          f"({int(faixa.sum())} px)")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 6. A projeção clara da academia (a linha em U junto à parede de baixo, `final3840_casaa.projecao_academia`): ela foi
# pintada sobre a madeira com a cobertura de cada px vezes `forca` (0,75), então a madeira de baixo volta pela conta
# inversa, nos px que não são parede (a parede de baixo foi redesenhada depois, por cima da ponta das linhas: ali, só
# o px da borda dela que não ficou escuro, acima de `parede_lum`).
PROJECAO_CS = {"parede_lum": 110}


def projecao_cs(Q, img):
    q = FA.PROJECAO_ACADEMIA
    x0, y0, x1, y1 = q["pt"]
    e = q["larg_px"] / FA.PT_PX
    a = np.zeros((Q.H, Q.W), np.float32)
    for r in ((x0, y0, x1, y0 + e), (x0, y0, x0 + e, y1), (x1 - e, y0, x1, y1)):
        a = np.maximum(a, FA.ret_aa(Q, r))
    a *= q["forca"]
    parede = cv2.dilate((FA.paredes_pdf(Q) > 0.02).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    m = (a > 0) & (~parede | (img.astype(np.float32).mean(axis=2) > PROJECAO_CS["parede_lum"]))
    a3 = a[..., None]
    volta = (img.astype(np.float32) - np.float32(q["cor"]) * a3) / (1 - a3)
    out = img.copy()
    out[m] = np.clip(np.round(volta[m]), 0, 255).astype(np.uint8)
    print(f"    academia: sem a projeção clara junto à parede de baixo ({int(m.sum())} px de madeira de volta)")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 4. As prateleiras do depósito (os dois braços de `final3840_casaa.DEPOSITO`, que eram em freijó com o veio): uma cor
# neutra só, sem textura, no mesmo desenho, sobre o piso refeito na faixa delas (`bege_cs`), com a sombra curta delas no
# Bege Bahia de novo (a de `armarios_deposito`: `sombra`, 1,4 px, sigma 1,4).
PRATELEIRAS_CS = {"cor": (186, 191, 195)}         # BGR: o cinza quente claro (RGB ~195, 191, 186)


def prateleiras_cs(Q, img):
    rs = [r for r, _ in FA.DEPOSITO["pecas"]]
    caixa = (min(r[0] for r in rs), min(r[1] for r in rs), max(r[2] for r in rs), max(r[3] for r in rs))
    tl = FA.tela(np.ascontiguousarray(img.copy()), Q, caixa, folga=6)
    m = np.max([tl.ret(r) for r in rs], axis=0)                 # o L numa peça só (sem a sombra de um braço no outro)
    FA.sombra_q(tl, m, forca=FA.DEPOSITO["sombra"], dist=1.4, sigma=1.4)
    tl.pintar(m, PRATELEIRAS_CS["cor"])
    out = tl.gravar()
    print(f"    depósito: as {len(FA.DEPOSITO['pecas'])} prateleiras numa cor neutra só, sem textura")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 1. A grama (o gramado ao pé da escada do deck; era a grama do Térreo de 2000 px, ampliada, em manchas grandes e
# borradas): a grama da biblioteca de texturas (`texturas.textura("grama")`) tecida de novo na resolução da prancha, na
# metade da escala real (`escala`), no tom mediano da grama de antes. Só no verde da caixa dele (fechado e sem furos);
# na borda da pegada, a grama nova com o branco de fora na mesma proporção. Depois (usuário, com o recorte de uma grama
# verde-oliva acinzentada: "traga o tom da grama para mais próximo dessa referência"): o tom mediano é o da referência
# (`tom`), menos saturado e mais claro que o de antes (RGB ~106, 119, 71).
GRAMA_CS = {"caixa": (700, 1110, 1100, 1660), "escala": 0.5, "semente": 5, "desfoque": 0.5, "verde": 8,
            "tom": (101, 127, 121)}                       # BGR: o verde-oliva acinzentado (RGB ~121, 127, 101)


def grama_cs(Q, img, p):
    from scipy import ndimage
    sys.path.insert(0, str(FA.A.RAIZ / "_texturas"))
    from texturas import textura
    q = GRAMA_CS
    x0, y0, x1, y1 = q["caixa"]
    reg = img[y0:y1, x0:x1].astype(np.float32)
    ri = reg.astype(np.int32)
    verde = (ri[..., 1] > ri[..., 2] + q["verde"]) & (ri[..., 1] > ri[..., 0] + q["verde"])
    verde = ndimage.binary_fill_holes(cv2.morphologyEx(verde.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)))
    pr = p[y0:y1, x0:x1]
    alvo = np.float32(q["tom"])
    T = textura("grama", Q.px_m * q["escala"], y1 - y0, x1 - x0, semente=q["semente"]).astype(np.float32)
    T = cv2.GaussianBlur(T, (0, 0), q["desfoque"])
    T = T * (alvo / np.median(T[verde], axis=0))
    novo = T * pr[..., None] + 255 * (1 - pr[..., None])
    out = img.copy()
    sub = out[y0:y1, x0:x1]
    sub[verde] = np.clip(np.round(novo[verde]), 0, 255).astype(np.uint8)
    print(f"    grama: a da biblioteca na metade da escala ({int(verde.sum())} px), no verde-oliva da referência")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# Depois (usuário: "suavize também os degraus da escada"): os degraus em Bege Bahia (`final3840_casaa.degraus_bege`) são o
# tom de cada degrau e o sombreamento de subida vezes o desenho da foto, 1 + forca (T / média(T) - 1), na janela da tela
# dos degraus (`DEGRAUS_A`); depois do corte, esmaecidos para o branco (`esmaecer`). O desenho, refeito igual, troca por
# 1 + forca `forca` (T / média(T) - 1), a mesma fração do piso (`BEGE_CS`): o tom, a sombra dos espelhos e o trecho
# esmaecido ficam. As duas linhas de baixo vieram de 4 px acima (`pedidos_terreo_casaa_2910.grama_escada_ta`), e o
# desenho delas também; a linha da grama (misturada) e os px da borda dos degraus ficam como estão.
def degraus_cs(Q, img):
    sys.path.insert(0, str(FA.A.RAIZ / "_texturas"))
    from texturas import textura
    q = FA.DEGRAUS_A
    g = PT.GRAMA_ESCADA_TA
    tl = FA.tela(img.copy(), Q, q["pt"], folga=2)
    T = textura("bege_bahia", Q.px_m, tl.h, tl.w, semente=q["semente"]).astype(np.float32)
    Tn = T / T.reshape(-1, 3).mean(axis=0) - 1
    yi = int(np.floor(Q.p2q(0, g["linha_pt"])[1]))
    for r in range(yi - g["acima_px"], yi):
        Tn[r - tl.y0] = Tn[r - tl.y0 - g["desloc_px"]]
    fator = (1 + q["forca"] * BEGE_CS["forca"] * Tn) / (1 + q["forca"] * Tn)
    X, Y = tl.grade()
    (cx0, cy0), (cx1, cy1) = q["corte"]
    alem = (X < cx0 + (cx1 - cx0) / (cy1 - cy0) * (Y - cy0))[..., None]
    e = q["esmaecer"]
    reg = tl.reg
    base = np.where(alem, (reg - 255 * e) / (1 - e), reg) * fator
    novo = np.where(alem, base * (1 - e) + 255 * e, base)
    dentro = tl.reduzir(tl.ret(q["pt"])) >= 0.999
    dentro[yi - tl.y0:] = False
    out = img.copy()
    sub = out[tl.y0:tl.y1, tl.x0:tl.x1]
    sub[dentro] = np.clip(np.round(novo[dentro]), 0, 255).astype(np.uint8)
    print(f"    degraus: as manchas do Bege Bahia a {BEGE_CS['forca']:.0%} do contraste ({int(dentro.sum())} px)")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 2. A escada do deck: no lugar do S (`final3840_casaa.ESCADA_A`, na origem do texto do PDF, no pátio), a seta e a
# descrição. A seta é o triângulo cheio no degrau de baixo, com a ponta para onde a escada sobe (à esquerda), como no
# recorte do usuário; a descrição, "SOBE PARA O DECK", em caixa alta como os rótulos e o S de antes, na mesma fonte, cor
# e corpo do S, em duas linhas (usuário: "quebre a linha em 'Sobe para o / Deck'"), alinhada à esquerda, com o meio do
# bloco na altura do triângulo. O S sai com o pátio das mesmas colunas, `desloc_s` px abaixo (a sombra do espelho do 1º
# degrau corre na vertical, então ela continua igual).
ESCADA_CS = {"triangulo": [(1062.0, 1094.0), (1076.0, 1086.0), (1076.0, 1102.0)], "cor_seta": (30, 30, 30), "ss": 8,
             "texto": ("SOBE PARA O", "DECK"), "origem_px": (1088.0, 1090.0), "entrelinha_px": 20, "desloc_s": 18}


def _alfa_texto(texto, fonte, corpo, ox, oy, caixa):
    from PIL import Image, ImageDraw
    X0, Y0, W, H = caixa
    tela_t = Image.new("L", (W * 4, H * 4), 0)
    ImageDraw.Draw(tela_t).text(((ox - X0) * 4, (oy - Y0) * 4), texto, font=fonte, fill=255, anchor="ls")
    return np.asarray(tela_t.resize((W, H), Image.LANCZOS), np.float32) / 255


def escada_cs(Q, img):
    from PIL import ImageFont
    from rodape_entrega import FONTES
    e = FA.ESCADA_A
    q = ESCADA_CS
    out = img.copy()
    fonte = ImageFont.truetype(str(FONTES / e["fonte"]), e["corpo_px"] * 4)
    # o S de antes: a mesma caixa e a mesma conta de `final3840_casaa.escada`
    ox, oy = Q.p2q(*e["origem"])
    W = H = e["corpo_px"] * 3
    X0, Y0 = int(ox) - 4, int(oy) - e["corpo_px"] * 2
    s_ = cv2.dilate((_alfa_texto(e["texto"], fonte, e["corpo_px"], ox, oy, (X0, Y0, W, H)) > 0.01).astype(np.uint8),
                    np.ones((3, 3), np.uint8)).astype(bool)
    ys, xs = np.nonzero(s_)
    d = q["desloc_s"]
    out[ys + Y0, xs + X0] = img[ys + Y0 + d, xs + X0]
    # a seta: o triângulo cheio, antisserrilhado
    k = q["ss"]
    pts = np.float32(q["triangulo"])
    bx0, by0 = np.floor(pts.min(axis=0)).astype(int) - 2
    bx1, by1 = np.ceil(pts.max(axis=0)).astype(int) + 3
    m = np.zeros(((by1 - by0) * k, (bx1 - bx0) * k), np.uint8)
    cv2.fillPoly(m, [np.int32(np.round((pts - [bx0, by0]) * k))], 255, cv2.LINE_AA)
    a = cv2.resize(m.astype(np.float32) / 255, (bx1 - bx0, by1 - by0), interpolation=cv2.INTER_AREA)[..., None]
    reg = out[by0:by1, bx0:bx1].astype(np.float32)
    out[by0:by1, bx0:bx1] = np.clip(np.round(reg * (1 - a) + np.float32(q["cor_seta"]) * a), 0, 255).astype(np.uint8)
    # a descrição, linha a linha
    tx, ty = q["origem_px"]
    for i, linha in enumerate(q["texto"]):
        ly = ty + i * q["entrelinha_px"]
        W, H = int(fonte.getlength(linha) / 4) + 12, e["corpo_px"] * 3
        X0, Y0 = int(tx) - 4, int(ly) - e["corpo_px"] * 2
        a = _alfa_texto(linha, fonte, e["corpo_px"], tx, ly, (X0, Y0, W, H))[..., None]
        reg = out[Y0:Y0 + H, X0:X0 + W].astype(np.float32)
        out[Y0:Y0 + H, X0:X0 + W] = np.clip(np.round(reg * (1 - a) + np.float32(e["cor_texto"]) * a), 0,
                                            255).astype(np.uint8)
    print(f"    escada: o S saiu; a seta (triângulo cheio) no degrau de baixo e \"{' / '.join(q['texto'])}\" no lugar "
          "do S")
    return out


# ----------------------------------------------------------------------------------------------------------------------
ANTES_DEPOIS_CS = {"Subsolo": {"planta": (640, 780, 2440, 1700), "escada_grama": (700, 1020, 1300, 1660),
                               "deposito": (1330, 855, 1890, 1065), "academia_linhas": (1500, 1440, 1900, 1530)}}


def cliente_subsolo_cs(img):
    Q = FA.QuadroA("Subsolo")
    p = pegada_quadro()
    img = fundo_branco_cs(Q, img, p)
    img = borda_cs(Q, img, p)
    img = projecao_cs(Q, img)
    img = bege_cs(Q, img)
    img = prateleiras_cs(Q, img)
    img = grama_cs(Q, img, p)
    img = degraus_cs(Q, img)
    return escada_cs(Q, img)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--antes", default=str(FINAL_SUB))
    ap.add_argument("--saida", default=str(FINAL_SUB))
    a = ap.parse_args()
    antes = cv2.imread(a.antes)
    out = cliente_subsolo_cs(antes)
    cv2.imwrite(a.saida, out)
    print(f"    {a.saida}")
    if Path(a.saida).resolve() == FINAL_SUB.resolve():
        PT.antes_depois_pedidos_ta("Subsolo", antes, out, caixas=ANTES_DEPOIS_CS, sufixo="0511")

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
# Depois (usuário, 10/11/26, com o recorte do Térreo marcado "Usar essa cor padronizada para as prateleiras e armários":
# "USAR ESSE TOM DE COR PARA PRATELEIRA DO DEPÓSITO. ELA VAI SER PADRÃO PARA OS ARMARIOS E PRATELEIRAS DA CASA A."): o
# tom do armário comprido junto ao lavabo do Térreo (a mediana do miolo dele na final do Térreo, RGB 208, 178, 156,
# quase liso), ainda numa cor só, sem textura. Antes era o cinza quente claro (RGB ~195, 191, 186).
PRATELEIRAS_CS = {"cor": (156, 178, 208)}         # BGR (RGB 208, 178, 156)


def prateleiras_cs(Q, img):
    rs = [r for r, _ in FA.DEPOSITO["pecas"]]
    caixa = (min(r[0] for r in rs), min(r[1] for r in rs), max(r[2] for r in rs), max(r[3] for r in rs))
    tl = FA.tela(np.ascontiguousarray(img.copy()), Q, caixa, folga=6)
    m = np.max([tl.ret(r) for r in rs], axis=0)                 # o L numa peça só (sem a sombra de um braço no outro)
    FA.sombra_q(tl, m, forca=FA.DEPOSITO["sombra"], dist=1.4, sigma=1.4)
    tl.pintar(m, PRATELEIRAS_CS["cor"])
    out = tl.gravar()
    print(f"    depósito: as {len(FA.DEPOSITO['pecas'])} prateleiras numa cor só, sem textura, RGB {PRATELEIRAS_CS['cor'][::-1]}")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 1. A grama (o gramado ao pé da escada do deck; era a grama do Térreo de 2000 px, ampliada, em manchas grandes e
# borradas): a grama da biblioteca de texturas (`texturas.textura("grama")`) tecida de novo na resolução da prancha, na
# metade da escala real (`escala`), no tom mediano da grama de antes. Só no verde da caixa dele (fechado e sem furos);
# na borda da pegada, a grama nova com o branco de fora na mesma proporção. Depois (usuário, com o recorte de uma grama
# verde-oliva acinzentada: "traga o tom da grama para mais próximo dessa referência"): o tom mediano é o da referência
# (`tom`), menos saturado e mais claro que o de antes (RGB ~106, 119, 71).
# Depois (usuário, 07/11/26, com a planta de um quintal: "USE ESSA ESCALA E COR DE GRAMA. USAREMOS ESSA GRAMA COMO
# PADRÃO PARA AS DEMAIS"): a grama padrão da biblioteca (`texturas.textura("grama_padrao")`, tecida do gramado da
# referência, a 62 px/m medidos nela), na escala real e na cor dela (RGB ~79, 75, 39), sem retoque de tom nem desfoque.
GRAMA_CS = {"caixa": (700, 1110, 1100, 1660), "textura": "grama_padrao", "escala": 1.0, "semente": 5, "desfoque": 0.0,
            "verde": 8, "tom": None}                      # tom None: a cor da própria textura


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
    T = textura(q["textura"], Q.px_m * q["escala"], y1 - y0, x1 - x0, semente=q["semente"]).astype(np.float32)
    if q["desfoque"]:
        T = cv2.GaussianBlur(T, (0, 0), q["desfoque"])
    if q["tom"] is not None:
        T = T * (np.float32(q["tom"]) / np.median(T[verde], axis=0))
    novo = T * pr[..., None] + 255 * (1 - pr[..., None])
    out = img.copy()
    sub = out[y0:y1, x0:x1]
    sub[verde] = np.clip(np.round(novo[verde]), 0, 255).astype(np.uint8)
    print(f"    grama: a {q['textura']} da biblioteca, escala {q['escala']} ({int(verde.sum())} px), "
          f"{'na cor dela' if q['tom'] is None else 'no tom ' + str(q['tom'])}")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# A sauna (usuário, 07/11/26, com uma referência anotada: "Quando tiver dois tons muito parecidos. Fazer esse jogo de cores
# para destacar o que está mais em cima e mais embaixo"; "FAÇA ESSE JOGO DE TOM NO BANCO DA SAUNA, POIS TANTO O BANCO
# QUANTO O PISO DA SAUNA SÃO EM TRAVERTINO BRUTO"). Corrigido em 10/11/26 (usuário: "O TOM MAIS ESCURO É EM CIMA (NO
# BANCO), NÃO NO PISO DA SAUNA. ESSA É A REGRA, NA PARTE DE CIMA, SE FOR O MESMO MATERIAL, O TOM FICA MAIS ESCURO."):
# o banco (`final3840_casaa.SAUNA`, o mais alto) mais escuro que o piso (`banco_sobre_piso` x o tom do piso, canal a
# canal: o mesmo tom do travertino, os veios e a quina como estavam) e o piso da sauna (o mais baixo; `piso_px`, entre
# os vidros, a parede da direita e a frente do banco) no tom dele (`piso`, 1: como o dos banhos); ao longo da frente do
# banco, no piso, a sombra de contato um pouco mais larga (`contato`: força e px). Na versão de 07/11 era o contrário
# (o banco 1,03 x o piso e o piso a 0,93).
SAUNA_CS = {"banco_sobre_piso": 0.90, "piso": 1.0, "piso_px": (1197.0, 1514.0, 1378.0, None), "contato": (0.14, 5.0),
            "aresta_px": 2}


def _cobertura(forma, x0, y0, x1, y1):
    """A fração de cada px (0..1) dentro do retângulo (px, bordas fracionárias)."""
    H, W = forma
    cx = np.clip(np.minimum(np.arange(W) + 1, x1) - np.maximum(np.arange(W), x0), 0, 1)
    cy = np.clip(np.minimum(np.arange(H) + 1, y1) - np.maximum(np.arange(H), y0), 0, 1)
    return (cy[:, None] * cx[None, :]).astype(np.float32)


def sauna_cs(Q, img):
    q = SAUNA_CS
    (bx0, by0), (bx1, by1) = Q.p2q(*FA.SAUNA["pt"][:2]), Q.p2q(*FA.SAUNA["pt"][2:])
    px0, py0, px1, _ = q["piso_px"]
    forma = img.shape[:2]
    f = img.astype(np.float32)
    banco = _cobertura(forma, bx0, by0, bx1, by1)
    piso = _cobertura(forma, px0, py0, px1, by0)
    lum = f.mean(axis=2)
    m_piso = (piso > 0.99) & (lum > 150)                          # o piso sem o texto do rótulo
    m_banco = _cobertura(forma, bx0, by0 + q["aresta_px"], bx1, by1) > 0.99
    tom_piso, tom_banco = f[m_piso].mean(axis=0), f[m_banco].mean(axis=0)
    k = tom_piso * q["banco_sobre_piso"] / tom_banco
    out = f * (1 + (k - 1) * banco[..., None])
    out *= (1 + (q["piso"] - 1) * piso)[..., None]
    # a sombra de contato no piso, logo acima da frente do banco
    Y = np.arange(forma[0], dtype=np.float32)[:, None] + 0.5
    d = by0 - Y
    s = q["contato"][0] * np.clip(1 - d / q["contato"][1], 0, 1) * (d > 0)
    out *= (1 - s * _cobertura(forma, bx0, 0, bx1, forma[0]))[..., None]
    out = np.clip(np.round(out), 0, 255).astype(np.uint8)
    print(f"    sauna: o banco de RGB {tuple(int(c) for c in tom_banco[::-1])} para "
          f"{tuple(int(c) for c in (tom_banco * k)[::-1])}, o piso de {tuple(int(c) for c in tom_piso[::-1])} para "
          f"{tuple(int(c) for c in (tom_piso * q['piso'])[::-1])}, com a sombra de contato")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# Depois (usuário, 10/11/26, com os recortes do JPG em 12K das pontas da parede entre a academia e o BH. FEM./BH. MASC. e
# da parede do BH. SERV.: "CORRIGIR ESSA FALHA NA PAREDE (NO PORTAL)"). Nos portais, o PDF tem o marco da porta: o
# batente (uma faixa de ~2 px no vão, junto à ponta da parede) e as guarnições (4,2 x 1,2 px, saindo das duas faces da
# parede). A folha da porta não é desenhada, e esses restos ficavam na ponta da parede como um risco escuro e uma faixa
# irregular, que a IA da ampliação transformou num pé inclinado. Nos portais apontados (`portais`, px da final), em volta
# das peças brancas do marco no PDF (ARQ_PAREDE cheias de branco, com o maior lado até `peca_max_px`, crescidas
# `folga_px` e mais `ponta_px`), a ponta é desenhada de novo: o piso por baixo vem do piso vizinho, copiado de `passo_px`
# em `passo_px` para longe da peça de parede mais perto (só de px de piso, claros), para manter a textura; a
# parede, das peças cinza do PDF (o cinza da final, `cor_parede`), com o contorno escuro das outras faces (`contorno`:
# largura e cor), em supersampling `ss`; a borda da área refeita, esfumada (`borda_px`). A ponta fica reta, no desenho do PDF.
# No BH. SERV., a face esquerda da parede (do nicho ao portal) tinha um traço esverdeado a 1 px da face, que a IA tinha
# feito ondulado e com um ponto escuro (o risco de 5 px da linha do nicho, saindo da parede): ela é refeita também
# (`faixas`: a caixa, em px da final, e as linhas onde fica como está, a do vidro do box); o contorno ao lado do vão de
# recolhimento (a peça branca grande da parede) é o mesmo das faces cinza.
PORTAIS_CS = {"portais": {"bh_serv": (1182, 984, 1208, 1048), "bh_fem": (1486, 1494, 1562, 1521),
                          "bh_masc": (1798, 1494, 1873, 1521)},
              "faixas": {"bh_serv": [((1183.5, 884.7, 1190.1, 992.2), [(941.5, 947.5)])]},
              "peca_max_px": 20.0, "folga_px": 1.5, "ponta_px": 2.0, "passo_px": 6, "piso_min": 140, "cor_parede": 80,
              "contorno": (1.0, 45), "ss": 8, "borda_px": 0.7, "margem_px": 24, "vidro_min": 145}


def _pecas_parede(Q, caixa):
    """As peças cheias da ARQ_PAREDE na caixa (px): (cinza, brancas pequenas, brancas grandes), como (x0, y0, x1, y1)."""
    X0, Y0, X1, Y1 = caixa
    cinza, brancas, vaos = [], [], []
    for d in Q.desenhos:
        if d.get("layer") != "ARQ_PAREDE" or d["type"] != "f" or not d.get("fill"):
            continue
        for c in Q.caminhos(d):
            c = np.asarray(c)
            if len(c) < 3:
                continue
            r = (c[:, 0].min(), c[:, 1].min(), c[:, 0].max(), c[:, 1].max())
            if r[2] < X0 or r[0] > X1 or r[3] < Y0 or r[1] > Y1:
                continue
            f = d["fill"]
            if min(f) > 0.95:
                (brancas if max(r[2] - r[0], r[3] - r[1]) <= PORTAIS_CS["peca_max_px"] else vaos).append(r)
            elif abs(f[0] - 0.36) < 0.02:
                cinza.append(r)
    return cinza, brancas, vaos


def portais_cs(Q, img, rotulos=None):
    """`rotulos`: o alfa dos rótulos (px que ficam como estão)."""
    q = PORTAIS_CS
    out = img.copy()
    Hi, Wi = img.shape[:2]
    ss, mg = q["ss"], q["margem_px"]
    notas = []
    for nome, caixa in q["portais"].items():
        faixas = q["faixas"].get(nome, [])
        x0s = [caixa[0]] + [int(np.floor(f[0][0])) - 2 for f in faixas]
        y0s = [caixa[1]] + [int(np.floor(f[0][1])) - 2 for f in faixas]
        x1s = [caixa[2]] + [int(np.ceil(f[0][2])) + 2 for f in faixas]
        y1s = [caixa[3]] + [int(np.ceil(f[0][3])) + 2 for f in faixas]
        X0, Y0 = max(min(x0s) - mg, 0), max(min(y0s) - mg, 0)                  # a janela, com margem para a cópia
        X1, Y1 = min(max(x1s) + mg, Wi), min(max(y1s) + mg, Hi)
        h, w = Y1 - Y0, X1 - X0
        cinza, brancas, vaos = _pecas_parede(Q, (X0, Y0, X1, Y1))
        brancas = [r for r in brancas if r[2] >= caixa[0] and r[0] <= caixa[2] and r[3] >= caixa[1] and r[1] <= caixa[3]]

        def sup(rets):
            m = np.zeros((h * ss, w * ss), np.uint8)
            for (x0, y0, x1, y1) in rets:
                a, b = int(round((x0 - X0) * ss)), int(round((x1 - X0) * ss))
                c, d = int(round((y0 - Y0) * ss)), int(round((y1 - Y0) * ss))
                m[max(c, 0):max(d, 0), max(a, 0):max(b, 0)] = 1
            return m
        # as peças brancas grandes: só o vão de recolhimento dentro de uma faixa ganha o contorno da parede; as
        # outras (a divisória de vidro dos banhos) ficam como estão, fora da área refeita e da cópia
        vaos_faixa = [v for v in vaos if any(v[0] < f[0][2] and v[2] > f[0][0] and v[1] < f[0][3] and v[3] > f[0][1]
                                             for f in faixas)]
        U, corpo = sup(cinza), sup(cinza + vaos_faixa)
        aV = sup(vaos).reshape(h, ss, w, ss).mean(axis=(1, 3))
        r = int(round(q["contorno"][0] * ss))
        O = cv2.dilate(corpo, np.ones((2 * r + 1, 2 * r + 1), np.uint8)) & (1 - corpo)
        aU = U.reshape(h, ss, w, ss).mean(axis=(1, 3))
        aO = O.reshape(h, ss, w, ss).mean(axis=(1, 3))
        aC = corpo.reshape(h, ss, w, ss).mean(axis=(1, 3))
        # o marco (as peças brancas pequenas, crescidas) e a área refeita: em volta dele e as faixas
        marco = np.zeros((h, w), np.float32)
        f_ = q["folga_px"]
        for (x0, y0, x1, y1) in brancas:
            marco = np.maximum(marco, _cobertura((h, w), x0 - X0 - f_, y0 - Y0 - f_, x1 - X0 + f_, y1 - Y0 + f_))
        k = int(np.ceil(q["ponta_px"])) * 2 + 1
        refazer = cv2.dilate((marco > 0.05).astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool)
        dentro = np.zeros((h, w), bool)
        dentro[caixa[1] - Y0:caixa[3] - Y0, caixa[0] - X0:caixa[2] - X0] = True
        refazer &= dentro
        for (fx0, fy0, fx1, fy1), fica in faixas:
            fx = _cobertura((h, w), fx0 - X0, fy0 - Y0, fx1 - X0, fy1 - Y0) > 0.5
            for (ly0, ly1) in fica:
                fx[int(np.floor(ly0 - Y0)):int(np.ceil(ly1 - Y0)), :] = False
            refazer |= fx & (aC < 0.5)
        refazer &= ~(aV > 0.02) | (aC > 0.02)
        # os vidros desenhados na final (os boxes e as divisórias: cinza frio, claro) ficam como estão
        jf = out[Y0:Y1, X0:X1].astype(np.int32)
        frio = ((jf[..., 0] - jf[..., 2]) >= -3) & ((jf[..., 1] - jf[..., 2]) >= -3) & (jf.mean(axis=2) >= q["vidro_min"])
        refazer &= ~(frio & (aC < 0.02))
        if rotulos is not None:
            refazer &= ~(rotulos[Y0:Y1, X0:X1] > 0.02)
        # o piso por baixo: copiado do piso vizinho, para longe da peça de parede mais perto (no eixo em que o px está
        # fora dela; nos cantos, no eixo da maior distância), só de px de piso (fora da parede, do marco e da área
        # refeita, e claros: `piso_min`, para não copiar linhas)
        jan = out[Y0:Y1, X0:X1]
        lum = jan.astype(np.float32).mean(axis=2)
        livre = (aC + aO < 0.02) & (aV < 0.02) & ~(marco > 0.05) & ~refazer & (lum > q["piso_min"])
        if rotulos is not None:
            livre &= ~(rotulos[Y0:Y1, X0:X1] > 0.0)
        fundo = jan.astype(np.float32).copy()
        passo = q["passo_px"]
        corpos = cinza + vaos_faixa
        ys, xs = np.nonzero(refazer)
        for y, x in zip(ys, xs):
            px, py = X0 + x + 0.5, Y0 + y + 0.5

            def fora(g):
                return (max(g[0] - px, 0, px - g[2]), max(g[1] - py, 0, py - g[3]))
            g = min(corpos, key=lambda g: sum(v * v for v in fora(g)))
            ox, oy = fora(g)
            if ox == 0 and oy == 0:
                continue
            if ox >= oy:
                dx, dy = (1 if px > g[2] else -1), 0
            else:
                dx, dy = 0, (1 if py > g[3] else -1)
            for m in range(1, 8):
                sx, sy = x + dx * passo * m, y + dy * passo * m
                if not (0 <= sx < w and 0 <= sy < h):
                    break
                if livre[sy, sx]:
                    fundo[y, x] = jan[sy, sx]
                    break
        cp, (lc, cc) = q["cor_parede"], q["contorno"]
        novo = fundo * (1 - aU - aO)[..., None] + cp * aU[..., None] + cc * aO[..., None]
        novo = np.where((aC - aU)[..., None] > 0.02, jan, novo)                 # o vão de recolhimento fica como está
        peso = cv2.GaussianBlur(refazer.astype(np.float32), (0, 0), q["borda_px"])[..., None]
        out[Y0:Y1, X0:X1] = np.clip(np.round(jan * (1 - peso) + novo * peso), 0, 255).astype(np.uint8)
        notas.append(f"{nome}: {len(brancas)} peças do marco, {int(refazer.sum())} px refeitos")
    print("    portais: as pontas das paredes refeitas sem o marco: " + "; ".join(notas))
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
# Depois (usuário, com o recorte das duas bicicletas ergométricas: "ficou faltando o pedal do lado direito da bicleta
# ergométrica. vemos o pedal do lado esquerdo de cada uma delas, mas não o direito"): em cada bicicleta, o pé de vela
# com o pedal de baixo (`caixa`, px da final, logo abaixo do quadro) é girado 180° em torno do eixo do pedivela (`eixo2`:
# o dobro do eixo, no meio do quadro e na coluna do pé de vela) e pousado do outro lado, como num pedivela de verdade.
# A peça é o escuro (`escuro`) ligado do pé de vela e do pedal, com a borda esfumada (`borda_sig`; a sombra do quadro em
# volta do pé de vela fica de fora), na cor dos px mais escuros dele (abaixo do quantil `cor_q`); depois, a sombra
# curta dos aparelhos (`final3840_casaa.APARELHOS["sombra"]`: força, distância e desfoque, para baixo e à esquerda).
PEDAIS_CS = {"pecas": [((1510, 1347, 1531, 1361), (3039, 2685)), ((1508, 1407, 1529, 1421), (3036, 2806))],
             "escuro": 80, "borda_sig": 0.6, "cor_q": 30}


def pedais_cs(Q, img):
    q = PEDAIS_CS
    forca, dist, sig = FA.APARELHOS["sombra"]
    out = img.astype(np.float32)
    for (x0, y0, x1, y1), (sx, sy) in q["pecas"]:
        reg = img[y0:y1, x0:x1].astype(np.float32)
        lum = reg.mean(axis=2)
        n, lab, st, _ = cv2.connectedComponentsWithStats((lum < q["escuro"]).astype(np.uint8))
        miolo = lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
        a = np.clip(cv2.GaussianBlur(miolo.astype(np.float32), (0, 0), q["borda_sig"]) * 1.25, 0, 1)
        cor = np.median(reg[miolo & (lum <= np.percentile(lum[miolo], q["cor_q"]))], axis=0)
        A = a[::-1, ::-1]
        h, w = A.shape
        X0, Y0 = sx - (x1 - 1), sy - (y1 - 1)
        dst = out[Y0:Y0 + h, X0:X0 + w]
        out[Y0:Y0 + h, X0:X0 + w] = dst * (1 - A[..., None]) + cor * A[..., None]
        # a sombra curta da peça nova, numa janela com folga
        f = int(np.ceil(dist + 3 * sig)) + 1
        S = np.zeros((h + 2 * f, w + 2 * f), np.float32)
        S[f:f + h, f:f + w] = A
        Af = S.copy()
        S = cv2.GaussianBlur(cv2.warpAffine(S, np.float32([[1, 0, -dist], [0, 1, dist]]), S.shape[::-1]), (0, 0), sig)
        win = out[Y0 - f:Y0 + h + f, X0 - f:X0 + w + f]
        out[Y0 - f:Y0 + h + f, X0 - f:X0 + w + f] = win * (1 - forca * S * (1 - Af))[..., None]
    print(f"    academia: o pedal do outro lado nas {len(q['pecas'])} bicicletas ergométricas (o de baixo girado 180°)")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
ANTES_DEPOIS_CS = {"Subsolo": {"planta": (640, 780, 2440, 1700), "escada_grama": (700, 1020, 1300, 1660),
                               "deposito": (1330, 855, 1890, 1065), "academia_linhas": (1500, 1440, 1900, 1530),
                               "bicicletas": (1440, 1295, 1590, 1445)}}
# os antes e depois de 10/11/26 (os portais e a sauna), contra a final de 32959cc
ANTES_DEPOIS_1011 = {"Subsolo": {"portais_bh_fem_masc": (1470, 1480, 1890, 1540), "portal_bh_serv": (1150, 960, 1240, 1060),
                                 "sauna": (1180, 1490, 1420, 1650), "prateleiras_deposito": (1330, 855, 1890, 1065)}}


def cliente_subsolo_cs(img):
    Q = FA.QuadroA("Subsolo")
    p = pegada_quadro()
    img = fundo_branco_cs(Q, img, p)
    img = borda_cs(Q, img, p)
    img = projecao_cs(Q, img)
    img = pedais_cs(Q, img)
    img = bege_cs(Q, img)
    img = prateleiras_cs(Q, img)
    img = grama_cs(Q, img, p)
    img = sauna_cs(Q, img)
    img = degraus_cs(Q, img)
    img = escada_cs(Q, img)
    # depois (usuário, 10/11/26): "PARA BANHO USE BH."; "CENTRALIZE "SAUNA" DENTRO DO AMBIENTE"; "CENTRALIZE TODOS OS
    # RÓTULOS" (`rotulos_subsolo_casaa`: a especificação dos rótulos, gravada para a opção manuscrita e a ampliação)
    import rotulos_subsolo_casaa as RS
    img = RS.aplicar(Q, img)
    # depois (10/11/26, "CORRIGIR ESSA FALHA NA PAREDE (NO PORTAL)"): as pontas das paredes nos portais, por último, com
    # os rótulos já no lugar e fora da área refeita (o "m²" do BH. SERV. encosta na faixa da parede)
    rot = np.max([a for a, _ in RS.camadas(Q, RS.ler_spec(), img.shape[:2])], axis=0)
    return portais_cs(Q, img, rotulos=rot)


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

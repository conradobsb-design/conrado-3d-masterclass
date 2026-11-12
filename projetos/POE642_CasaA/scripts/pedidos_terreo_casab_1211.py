#!/usr/bin/env python3
"""Térreo da Casa B: os pedidos de 12/11 (usuário, com os recortes da prancha), sobre a final instalada (a de 21fa118).

Pedidos: "Fazer as mesmas mudanças que foram apontadas no subsolo da casa A e que cabem para essa casa"; "Melhorar
representação das portas de giro. Encostar nas paredes."; "Colocar a seta e descrição em todas as escadas"; no deck de
cima, "Inserir uma linha para indicar a posição de instalação do chuveiro."; na prainha, "Colocar uma textura nas
espreguiçadeiras"; nas bancadas da área gourmet, "Geral: Não precisa representar os armários inferiores ou superiores."
(e um "?" na ponta da parede do BH gourmet da esquerda); na floreira do lavatório gourmet, "tirar as plantas coloridas e
colocar com o espaçamento igual entre elas"; "Representar a churrasqueira"; "Cor da ilha é no Dekton Danae"; "Trocar o
marrom do piso por essa opção. Para deixar o marrom mais uniforme com o restante da casa e mais sóbrio." e "As bancadas
que são em marrom tabaco podem permanecer no tom mais escuro para contrastar com o piso."; "Demarcar melhor o perímetro
da casa"; "Tirar o nome shaft"; no closet master, "Representar como banco estofado." e os cantos do guarda-roupa em U
marcados; "Melhorar o X tracejado" (os dois X da varanda); no estar da varanda, "Representar como mesa de centro e não
como banco estofado", "Tirar o contorno dos mobiliários" e "Tirar a representação desse amadeirado em cima do sofá.
Deixar apenas a mesa que encaixa no sofá."; "representar o gramado da casa A em todas as demais casas, nos seus
respectivos terreos"; "São 5 banquetas altas. Colocar em um tom que destaque do piso."; no serviço, "Cor da bancada é no
marrom tabaco" (BH serviço e BH motorista), "Não tem soleira. E encostar as portas nas paredes." (louceiro e despensa),
"Representar a cor de armário e prateleira igual o indicado da casa A. Sem textura. Uma cor neutra e sólida.", "Cor da
bancada é no Dekton Danae" (a bancada e os tanques da área de serviço), "Aqui são duas máquinas de lavar roupa. Tirar
essa representação de armário. Ou bancada, a bancada não passa por cima.", "Melhorar representação da porta. Encostar na
parede." (área de serviço, quarto de serviço, depósito e quarto do motorista); no jardim de 4,62 m², "Diminuir a escala e
quantidade de vegetação"; no pergolado da entrada, "Deixar as linhas do pergolado tracejadas mais finas e mais claras.
Deixar tudo na mesma cor, preto ou branco."; na entrada, "Centralizar a seta com a abertura da porta, usando este modelo
de seta." e "Representar uma soleira na entrada igual a casa C"; e "Trocar essa representação do jardim de inverno. Usar
a mesma do interior da casa A."

Um passo por grupo de pedidos (`PASSOS`), na ordem; `--de`/`--ate` para refazer um trecho, `--passos <pasta>` para
gravar cada um. Coordenadas em px do quadro de 3840 (o mesmo do PDF, `final3840_casab.Quadro("Terreo")`).
"""
import argparse
import contextlib
import io
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from scipy import ndimage

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import final3840_casab as F                      # noqa: E402
import final3840_casaa as FA                     # noqa: E402
import final3840_casaa_terreo as T               # noqa: E402

B = F.B
RAIZ = FA.A.RAIZ
RENDERS = B.CASA_B / "renders"
FINAL = RENDERS / "POE642_CasaB_PH_Terreo_final_rotulos.png"


def dilatar(m, px):
    if px <= 0:
        return m.astype(bool)
    return cv2.dilate(m.astype(np.uint8), np.ones((2 * px + 1, 2 * px + 1), np.uint8)).astype(bool)


def fechar(m, k):
    return cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((k, k), np.uint8)).astype(bool)


def nconv(a, m, sig):
    m = m.astype(np.float32)
    num = cv2.GaussianBlur(a * (m[..., None] if a.ndim == 3 else m), (0, 0), sig)
    den = cv2.GaussianBlur(m, (0, 0), sig)
    if a.ndim == 3:
        den = den[..., None]
    return num / np.maximum(den, 1e-4)


def texto_claro(img, regiao, q):
    """As letras claras dos rótulos sobre um piso escuro. As manchas claras (acima de `lum`, de `area` px ou mais) que,
    juntas na horizontal (`junta` px), formam uma linha de `n_min` manchas ou mais, de `larg_min` px de largura ou mais e
    até `alt_max` px de altura, são linhas de texto (as pintas do granito ficam soltas); nelas, todo px acima de
    `lum_linha` é letra (o I, a vírgula, o ², os dois-pontos e as letras do corpo pequeno), crescido `cresce` px."""
    lum = img.astype(np.float32).mean(axis=2)
    c = (lum > q["lum"]) & regiao
    n, lab, st, _ = cv2.connectedComponentsWithStats(c.astype(np.uint8), 8)
    pequenas = [i for i in range(1, n) if q["area"] <= st[i, cv2.CC_STAT_AREA] <= q["area_max"]
                and st[i, cv2.CC_STAT_HEIGHT] <= q["alt_letra"]]
    ok = np.isin(lab, pequenas)                      # as letras (as peças claras grandes, prateleiras e bancadas, não)
    jx, jy = q["junta"]
    blob = cv2.dilate(ok.astype(np.uint8), np.ones((2 * jy + 1, 2 * jx + 1), np.uint8))
    nb, labb, stb, _ = cv2.connectedComponentsWithStats(blob, 8)
    # o número de manchas por linha (não de px)
    nman = np.zeros(nb, int)
    for i in pequenas:
        if True:
            y, x = st[i, cv2.CC_STAT_TOP], st[i, cv2.CC_STAT_LEFT]
            ys, xs = np.nonzero(lab[y:y + st[i, 3], x:x + st[i, 2]] == i)
            nman[labb[y + ys[0], x + xs[0]]] += 1
    linhas = np.isin(labb, [b for b in range(1, nb) if nman[b] >= q["n_min"] and stb[b, cv2.CC_STAT_WIDTH] >= q["larg_min"]
                             and stb[b, cv2.CC_STAT_HEIGHT] <= q["alt_max"]])
    linhas = dilatar(linhas, 1)
    return dilatar(linhas & (lum > q["lum_linha"]), q["cresce"])


# ----------------------------------------------------------------------------------------------------------------------
# 1. O piso marrom (cliente, com a amostra: "Trocar o marrom do piso por essa opção. Para deixar o marrom mais uniforme com
# o restante da casa e mais sóbrio."; "As bancadas que são em marrom tabaco podem permanecer no tom mais escuro para
# contrastar com o piso."): o granito do piso da Casa B (o marrom tabaco da base, BGR 50, 66, 90: cozinha, louceiro,
# despensa, serviço, quarto e BH de serviço, área de serviço descoberta, depósito e bloco do motorista) na amostra do
# cliente (a mesma da Casa A, `terreo_casaa_1011.PISO_MARROM_TA`), tecida por image quilting, com a luz da final (só o
# que escurece além de `limiar`: as sombras de contato); as peças (claras, sem cor ou fora do marrom, e as cheias da base:
# bancadas, armários) ficam, e a borda delas é refeita pela fração da peça; as letras dos rótulos (brancas) ficam.
MARROM_TB = {"cor": (50, 66, 90), "fechar": 3, "lum_obj": 150, "croma_obj": 16, "rb_obj": 20, "area_obj": 60,
             "buraco_max": 600, "anel_px": 2, "mediana": 5, "sig_luz": 1.4, "sig_base_m": 0.8, "limiar": 0.07,
             "p_px": 40, "sobra": 12, "semente": 1211,
             "texto": {"lum": 150, "area": 3, "area_max": 220, "alt_letra": 16, "junta": (5, 1), "n_min": 4, "larg_min": 15, "alt_max": 22,
                       "lum_linha": 118, "cresce": 1}}


def _cache(nome, fazer):
    """O resultado de `fazer()` guardado em $CACHE_TB/<nome>.npy (o tecido da amostra leva minutos)."""
    import os
    pasta = os.environ.get("CACHE_TB")
    if not pasta:
        return fazer()
    arq = Path(pasta) / f"{nome}.npy"
    if arq.exists():
        return np.load(arq)
    r = fazer()
    arq.parent.mkdir(parents=True, exist_ok=True)
    np.save(arq, r)
    return r


def marrom_tb(Q, img, q=MARROM_TB):
    import terreo_casaa_1011 as TC
    im = img.astype(np.float32)
    ch = fechar(np.all(Q.chapada == np.uint8(q["cor"]), axis=2), q["fechar"])
    regiao = dilatar(ch, 3)
    f = cv2.GaussianBlur(im, (0, 0), 0.6)
    lum, croma = f.mean(axis=2), f.max(axis=2) - f.min(axis=2)
    rb = f[..., 2] - f[..., 0]
    cand = regiao & ((lum > q["lum_obj"]) | (croma < q["croma_obj"]) | (rb < q["rb_obj"]))
    obj = T.manchas(cand, q["area_obj"], q["buraco_max"])
    txt = texto_claro(img, regiao, q["texto"])
    obj |= txt
    obj |= dilatar(T.pecas_cheias(Q), 1) & regiao
    obj |= (FA.paredes_pdf(Q) > 0.5) & regiao
    nucleo = cv2.erode(obj.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    piso = ch & ~dilatar(obj, q["anel_px"] - 1)
    anel = ch & ~piso & ~nucleo
    # a luz do piso antigo, sem as pintas
    L = cv2.medianBlur(np.clip(im.mean(axis=2), 0, 255).astype(np.uint8), q["mediana"]).astype(np.float32)
    mf = piso.astype(np.float32)
    perto = T.nconv2(L, mf, q["sig_luz"], onde=piso | anel)
    base = T.nconv2(L, mf, q["sig_base_m"] * Q.px_m, onde=piso | anel)
    sh = np.clip(perto / np.maximum(base, 1) + q["limiar"], 0, 1)
    # o tecido da amostra, no tom dela
    A = TC.amostra_piso()
    tom = A.reshape(-1, 3).mean(axis=0)
    ys, xs = np.nonzero(regiao)                 # (a caixa fixa, para o tecido guardado servir de uma rodada à outra)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    Tq = _cache(f"marrom_{y1 - y0}x{x1 - x0}_{q['semente']}",
                lambda: TC.tecido(TC.variantes(A), y1 - y0, x1 - x0, q["p_px"], q["sobra"], q["semente"]))
    Tq = Tq / Tq.reshape(-1, 3).mean(axis=0) * tom
    N = im.copy()
    N[y0:y1, x0:x1] = Tq * sh[y0:y1, x0:x1, None]
    out = im.copy()
    out[piso] = N[piso]
    # o px da borda das peças: a fração da peça sobre o piso novo
    G = nconv(cv2.medianBlur(img, q["mediana"]).astype(np.float32), mf, 2.0)
    _, (iy, ix) = ndimage.distance_transform_edt(~nucleo, return_indices=True)
    C = im[iy, ix]
    d = C - G
    den = (d * d).sum(axis=2)
    a = np.clip(((im - G) * d).sum(axis=2) / np.maximum(den, 1e-3), 0, 1)
    a = np.where(den < 400, (np.abs(im - C).sum(axis=2) < np.abs(im - G).sum(axis=2)).astype(np.float32), a)
    novo_anel = a[..., None] * C + (1 - a[..., None]) * N
    out[anel] = novo_anel[anel]
    print(f"    piso marrom: a amostra do cliente (tom BGR {tuple(int(round(v)) for v in tom)}) em "
          f"{piso.sum() / Q.px_m ** 2:.1f} m², com a luz da final; {int(anel.sum())} px de borda refeitos pela fração da "
          f"peça; {int(txt.sum())} px de letras dos rótulos ficam")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
# 2. As bancadas e os armários (cliente/usuário, 12/11):
#  - "Cor da ilha é no Dekton Danae": a ilha da cozinha (a peça da base, sem o cooktop) no Dekton Danae da Casa A
#    (`terreo_casaa_1011.danae`), com a borda um tom abaixo; o cooktop fica;
#  - "Cor da bancada é no Dekton Danae" (área de serviço): a bancada da esquerda inteira (o quadrado cinza de cima era o
#    eletrodoméstico sob a bancada, que não aparece) e a dos tanques, em volta das cubas;
#  - "Aqui são duas máquinas de lavar roupa. Tirar essa representação de armário. Ou bancada, a bancada não passa por
#    cima.": no lugar da bancada de cima, à direita, o piso e as duas máquinas (vistas de cima: o tampo branco com a
#    sombra curta, o painel de comando junto à parede e o botão);
#  - "Cor da bancada é no marrom tabaco" (BH serviço e BH motorista): a pedra da ilha gourmet (o marrom tabaco escuro),
#    tecida na bancada, sem a cuba;
#  - "Representar a cor de armário e prateleira igual o indicado da casa A. Sem textura. Uma cor neutra e sólida."
#    (louceiro e despensa): as prateleiras em U no tom padrão (RGB 208, 178, 156), lisas, com a face de fora um tom abaixo;
#  - "Geral: Não precisa representar os armários inferiores ou superiores.": na bancada da pia da área gourmet, o
#    tracejado, as divisões dos módulos e a faixa do armário de cima saem (a pedra da ilha gourmet, tecida de ponta a
#    ponta, menos a cuba); no nicho da esquerda (a peça cinza), o tracejado sai.
BANCADAS_TB = {"ilha_coz": (1655, 1420), "cooktop_coz": (1694, 1500),
               "serv_esq": (2066, 1430), "tanques_px": (2199, 1462, 2242, 1566), "maquinas_px": (2190, 1371, 2242, 1461),
               "maquinas": [(2203, 1376, 2238, 1413), (2203, 1419, 2238, 1456)],
               "tabaco": [(1844, 1530), (2936, 1561)], "cuba_claro": 16, "cuba_croma": 20,
               "prateleiras": [(1840, 1430), (1990, 1482)], "cor_prateleira": (156, 178, 208), "face": 0.86,
               "pia_gourmet_px": (1297, 1485, 1538, 1528), "cuba_gourmet_px": (1365, 1495, 1405, 1523),
               "fonte_tabaco_px": (1418, 1325, 1546, 1381), "nicho_tracejado_px": (1116, 1500, 1203, 1509),
               "semente": 1212}


def _peca(Q, ponto, cor=(255, 255, 255)):
    """A peça da base chapada (cor `cor`) que contém o ponto, com os furos."""
    m = np.all(Q.chapada == np.uint8(cor), axis=2).astype(np.uint8)
    n, lab, _, _ = cv2.connectedComponentsWithStats(m, 4)
    x, y = ponto
    return ndimage.binary_fill_holes(lab == lab[y, x])


def _tabaco(img, fonte, h, w, semente):
    """A pedra marrom tabaco (a da ilha gourmet), tecida em h x w."""
    import terreo_casaa_1011 as TC
    x0, y0, x1, y1 = fonte
    A = img[y0:y1, x0:x1].astype(np.float32)
    return TC.tecido(TC.variantes(A), h, w, 16, 5, semente)


def _pintar(out, m, cor, face=None):
    """Pinta a máscara `m` com `cor` (imagem ou cor); a borda de 1 px um tom abaixo (`face`)."""
    if np.ndim(cor) == 1:
        cor = np.broadcast_to(np.float32(cor), out.shape).copy()
    out[m] = cor[m]
    if face:
        b = m & ~cv2.erode(m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        out[b] = cor[b] * face


def _maquina(out, r, ss=8):
    """A máquina de lavar vista de cima: o tampo branco, de cantos arredondados, com a luz da esquerda, o painel de
    comando junto à parede (à direita) e o botão; a sombra curta."""
    import pedidos_terreo_casaa_2910 as P
    x0, y0, x1, y1 = r
    X0, Y0 = int(x0) - 4, int(y0) - 4
    w, h = int(x1 - x0) + 9, int(y1 - y0) + 9
    mk = P._ret_arred((x0, y0, x1, y1), 2.2, X0, Y0, h, w, ss)
    al = cv2.resize(mk, (w, h), interpolation=cv2.INTER_AREA)
    sb = cv2.GaussianBlur(cv2.warpAffine(al, np.float32([[1, 0, -1.2], [0, 1, 1.4]]), (w, h)), (0, 0), 1.4)
    reg = out[Y0:Y0 + h, X0:X0 + w]
    reg *= (1 - 0.32 * sb * (1 - al))[..., None]
    xx = (np.arange(w * ss, dtype=np.float32)[None, :] / ss + X0)
    rel = np.clip((xx - x0) / (x1 - x0), 0, 1)
    cor = np.float32((232, 233, 233))[None, None] * (1.02 - 0.06 * rel)[..., None] * np.ones((h * ss, 1, 1), np.float32)
    painel = (xx > x1 - 0.22 * (x1 - x0)) * np.ones((h * ss, 1), np.float32)
    cor = cor * (1 - 0.10 * painel[..., None])
    out = P._pintar(out, X0, Y0, w, h, ss, mk, cor)
    borda = np.clip(mk - cv2.erode(mk, np.ones((5, 5), np.uint8)), 0, 1) * 0.55
    out = P._pintar(out, X0, Y0, w, h, ss, borda, np.float32((150, 152, 154))[None, None] * np.ones_like(borda)[..., None])
    bt = np.zeros((h * ss, w * ss), np.float32)
    cx, cy = ((x1 - 0.11 * (x1 - x0)) - X0) * ss, ((y0 + y1) / 2 - Y0) * ss
    cv2.circle(bt, (int(cx), int(cy)), int(1.3 * ss), 1.0, -1, cv2.LINE_AA)
    out = P._pintar(out, X0, Y0, w, h, ss, bt, np.float32((170, 172, 175))[None, None] * np.ones_like(bt)[..., None])
    return out


def bancadas_tb(Q, img, q=BANCADAS_TB):
    import terreo_casaa_1011 as TC
    out = img.astype(np.float32)
    s = q["semente"]
    H, W = out.shape[:2]
    # a ilha da cozinha, sem o cooktop
    ilha = _peca(Q, q["ilha_coz"]) & ~dilatar(_peca(Q, q["cooktop_coz"]), 1)
    _pintar(out, ilha, TC.danae(H, W, s), TC.DANAE["borda"])
    # a bancada da esquerda da área de serviço (inteira)
    esq = _peca(Q, q["serv_esq"])
    _pintar(out, esq, TC.danae(H, W, s + 1), TC.DANAE["borda"])
    # a bancada dos tanques: a pedra clara em volta das cubas (o que não é cuba nem parede)
    x0, y0, x1, y1 = q["tanques_px"]
    reg = out[y0:y1, x0:x1]
    I = reg.astype(np.int16)
    pedra = (np.abs(I - np.median(I.reshape(-1, 3), axis=0)).max(axis=2) < 26) & (reg.mean(axis=2) > 150) & \
            ((I[..., 2] - I[..., 0]) > 12)
    m = np.zeros((H, W), bool)
    m[y0:y1, x0:x1] = pedra
    _pintar(out, m, TC.danae(H, W, s + 2))
    # as duas máquinas de lavar, sem a bancada: o piso (o marrom novo, das colunas de logo à esquerda) e as máquinas
    x0, y0, x1, y1 = q["maquinas_px"]
    larg = x1 - x0
    out[y0:y1, x0:x1] = out[y0:y1, x0 - larg - 3:x1 - larg - 3][:, ::-1]
    for r in q["maquinas"]:
        out = _maquina(out, r)
    # as bancadas em marrom tabaco (BH serviço e BH motorista), sem a cuba
    for k, pt in enumerate(q["tabaco"]):
        m = _peca(Q, pt)
        # a cuba (e a torneira sobre ela): o branco mais claro que a pedra, a maior mancha, com os furos, crescida
        L = img.astype(np.float32).mean(axis=2)
        I = img.astype(np.int16)
        cr = I.max(axis=2) - I.min(axis=2)
        claro = m & (L > np.median(L[m]) + q["cuba_claro"]) & (cr < q["cuba_croma"])
        n, lab, st, _ = cv2.connectedComponentsWithStats(claro.astype(np.uint8), 8)
        if n > 1:
            i = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
            m &= ~dilatar(ndimage.binary_fill_holes(lab == i), 2)
        ys, xs = np.nonzero(m)
        a0, a1, b0, b1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        T_ = _tabaco(img, q["fonte_tabaco_px"], a1 - a0, b1 - b0, s + 10 + k)
        big = np.zeros_like(out)
        big[a0:a1, b0:b1] = T_
        _pintar(out, m, big, 0.86)
    # as prateleiras do louceiro e da despensa: a cor padrão, lisa
    for pt in q["prateleiras"]:
        _pintar(out, _peca(Q, pt), q["cor_prateleira"], q["face"])
    # a bancada da pia gourmet sem os armários: a pedra de ponta a ponta, menos a cuba
    x0, y0, x1, y1 = q["pia_gourmet_px"]
    T_ = _tabaco(img, q["fonte_tabaco_px"], y1 - y0, x1 - x0, s + 20)
    par = FA.paredes_pdf(Q)[y0:y1, x0:x1] > 0.5
    m = ~par
    c0, d0, c1, d1 = q["cuba_gourmet_px"]
    m[d0 - y0:d1 - y0, c0 - x0:c1 - x0] = False
    reg = out[y0:y1, x0:x1]
    reg[m] = T_[m]
    # o nicho da esquerda: o tracejado escuro sai (as linhas de cima e de baixo do tracejado)
    x0, y0, x1, y1 = q["nicho_tracejado_px"]
    reg = img[y0:y1, x0:x1]
    esc = (reg.astype(np.float32).mean(axis=2) < 100).astype(np.uint8)
    out[y0:y1, x0:x1] = cv2.inpaint(reg, cv2.dilate(esc, np.ones((3, 3), np.uint8)) * 255, 3, cv2.INPAINT_TELEA)
    print("    bancadas: a ilha da cozinha, a bancada e os tanques da área de serviço em Dekton Danae; as duas máquinas de "
          "lavar sem bancada; as do BH serviço e do BH motorista em marrom tabaco; as prateleiras do louceiro e da "
          "despensa lisas, na cor padrão; a bancada da pia gourmet sem os armários (tracejado e divisões) e o nicho sem "
          "o tracejado")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
# 3. A área gourmet: a churrasqueira (usuário, no módulo da direita da bancada da pia, acima do BH gourmet da direita:
# "Representar a churrasqueira") no desenho da Casa A (`terreo_casaa_1011.BANCADAS_TA`: o aro de inox, a grelha escura
# com as barras, o contorno e a sombra curta), no meio do módulo; as banquetas (cliente: "São 5 banquetas altas. Colocar
# em um tom que destaque do piso."): as 4 do render saem
# (no lugar delas, o travertino tecido de um trecho limpo logo acima) e entram 5, espaçadas por igual ao longo da ilha, a banqueta de linho da biblioteca virada para a ilha, parcialmente
# sob o tampo, no tom `tom` (bem mais escuro que o travertino), com a sombra curta; o resto do tracejado sobre a cuba
# da pia sai.
GOURMET_TB = {"churrasqueira_px": (1480.0, 1495.0, 1526.0, 1522.0), "inox": (190, 193, 196), "grelha": (40, 40, 42),
              "barra": (96, 98, 100), "barra_px": (1.0, 4.0), "aro_px": 3.0, "sombra": (0.30, 1.2, 1.4),
              "zona_px": (1298, 1294, 1548, 1321), "x_px": (1324.0, 1522.0), "n": 5, "y_px": 1311.0, "d_m": 0.42,
              "tom": (112, 132, 160), "sombra_b": (0.24, 0.05, 0.06), "cuba_px": (1365, 1499, 1406, 1510),
              "fonte_piso_px": (1300, 1268, 1404, 1294),
              "semente": 1213}


def _ret_alfa(r, X0, Y0, w, h, ss=8):
    m = np.zeros((h * ss, w * ss), np.uint8)
    a, b, c, d = ((r[0] - X0) * ss, (r[1] - Y0) * ss, (r[2] - X0) * ss, (r[3] - Y0) * ss)
    cv2.rectangle(m, (int(round(a)), int(round(b))), (int(round(c)) - 1, int(round(d)) - 1), 255, -1)
    return cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)


def gourmet_tb(Q, img, q=GOURMET_TB):
    import pedidos_terreo_casaa_2910 as P
    sys.path.insert(0, str(RAIZ / "_blocos"))
    import blocos
    out = img.copy()
    # o tracejado sobre a cuba da pia
    x0, y0, x1, y1 = q["cuba_px"]
    reg = out[y0:y1, x0:x1]
    esc = (reg.astype(np.float32).mean(axis=2) < 120).astype(np.uint8)
    out[y0:y1, x0:x1] = cv2.inpaint(reg, cv2.dilate(esc, np.ones((3, 3), np.uint8)) * 255, 3, cv2.INPAINT_TELEA)
    # a churrasqueira
    of = out.astype(np.float32)
    r = q["churrasqueira_px"]
    X0, Y0 = int(r[0]) - 6, int(r[1]) - 6
    w, h = int(r[2] - r[0]) + 13, int(r[3] - r[1]) + 13
    m = _ret_alfa(r, X0, Y0, w, h)
    fs, dd, sg = q["sombra"]
    sb = cv2.GaussianBlur(cv2.warpAffine(m, np.float32([[1, 0, -dd], [0, 1, dd]]), (w, h)), (0, 0), sg) * fs
    reg = of[Y0:Y0 + h, X0:X0 + w]
    reg *= (1 - sb * (1 - m))[..., None]
    reg[:] = reg * (1 - m[..., None]) + np.float32(q["inox"]) * m[..., None]
    a = q["aro_px"]
    g = _ret_alfa((r[0] + a, r[1] + a, r[2] - a, r[3] - a), X0, Y0, w, h)
    reg[:] = reg * (1 - g[..., None]) + np.float32(q["grelha"]) * g[..., None]
    larg, passo = q["barra_px"]
    xx = np.arange(w, dtype=np.float32) + X0 + 0.5
    barras = ((np.mod(xx - r[0], passo) < larg)[None, :] & (g > 0.5))
    reg[barras] = np.float32(q["barra"])
    borda = np.clip(m - cv2.erode(m, np.ones((2, 2), np.uint8)), 0, 1) * 0.4
    reg[:] = reg * (1 - borda[..., None]) + np.float32((110, 112, 114)) * borda[..., None]
    out = np.clip(np.round(of), 0, 255).astype(np.uint8)
    # as banquetas
    tampo = Q.preencher(lambda d: d.get("layer") == "ARQ_BANCADAS" and d.get("fill"), fs=False)
    x0, y0, x1, y1 = q["zona_px"]
    zona = np.zeros(img.shape[:2], bool)
    zona[y0:y1, x0:x1] = True
    zona &= tampo < 0.5
    # o travertino tecido de um trecho limpo logo acima (só espelhado, para os veios seguirem deitados), no lugar das
    # banquetas antigas, com a borda esfumada
    import terreo_casaa_1011 as TC
    sys.path.insert(0, str(RAIZ / "_texturas"))
    import texturas
    a0, b0, a1, b1 = q["fonte_piso_px"]
    A = out[b0:b1, a0:a1].astype(np.float32)
    Tt = texturas.quilting([A, A[:, ::-1].copy(), A[::-1].copy()], y1 - y0, x1 - x0, p=14, sobra=5,
                           rng=np.random.default_rng(q["semente"]))[:y1 - y0, :x1 - x0]
    Tt = Tt / Tt.reshape(-1, 3).mean(axis=0) * A.reshape(-1, 3).mean(axis=0)
    pz = cv2.GaussianBlur(zona.astype(np.float32), (0, 0), 1.0)[y0:y1, x0:x1, None] * zona[y0:y1, x0:x1, None]
    pz = np.maximum(pz, zona[y0:y1, x0:x1, None] * cv2.erode(zona.astype(np.uint8), np.ones((3, 3), np.uint8))[y0:y1, x0:x1, None])
    reg = out[y0:y1, x0:x1].astype(np.float32)
    out[y0:y1, x0:x1] = np.clip(np.round(reg * (1 - pz) + Tt * pz), 0, 255).astype(np.uint8)
    cor, al = blocos.bloco("banqueta_linho", q["d_m"] * Q.px_m / 0.45)
    cor, al = cv2.rotate(cor, cv2.ROTATE_180), cv2.rotate(al, cv2.ROTATE_180)
    al = np.clip(al, 0, 1).astype(np.float32)
    cor = cor.astype(np.float32)
    med = np.median(cor[al > 0.8], axis=0)
    cor = cor / med * np.float32(q["tom"])
    h, w = al.shape
    fs, dm, sm = q["sombra_b"]
    d_, sig = dm * Q.px_m, sm * Q.px_m
    of = out.astype(np.float32)
    for cx in np.linspace(*q["x_px"], q["n"]):
        cy = q["y_px"]
        f = int(np.ceil(d_ + 4 * sig)) + 2
        X0, Y0 = int(cx - w / 2) - f, int(cy - h / 2) - f
        Wr, Hr = w + 2 * f, h + 2 * f
        Mt = np.float32([[1, 0, cx - w / 2 - X0], [0, 1, cy - h / 2 - Y0]])
        livre = 1 - tampo[Y0:Y0 + Hr, X0:X0 + Wr]
        a_ = cv2.warpAffine(al, Mt, (Wr, Hr), flags=cv2.INTER_LINEAR)
        c = cv2.warpAffine(cor, Mt, (Wr, Hr), flags=cv2.INTER_LINEAR)
        sb = cv2.GaussianBlur(cv2.warpAffine(a_, np.float32([[1, 0, -d_], [0, 1, d_]]), (Wr, Hr)), (0, 0), sig) * fs
        a_ = a_ * livre
        reg = of[Y0:Y0 + Hr, X0:X0 + Wr]
        reg *= (1 - sb * livre * (1 - a_))[..., None]
        of[Y0:Y0 + Hr, X0:X0 + Wr] = reg * (1 - a_[..., None]) + c * a_[..., None]
    print(f"    área gourmet: a churrasqueira no módulo da direita da bancada da pia; {q['n']} banquetas altas no tom "
          f"BGR {q['tom']}, parcialmente sob o tampo da ilha; o tracejado sobre a cuba fora")
    return np.clip(np.round(of), 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
# 4. Os decks (da Casa A, "Fazer as mesmas mudanças"; regra [11/11] "Deck em madeira nova"): os três decks da Casa B (o de
# cima, o da esquerda da piscina e o de baixo, de 43,95 m²) no deck do Térreo da Casa A (`terreo_casaa_1011.
# deck_madeira_ta`: réguas de 20 cm no sentido do PDF, peças de 1,6 a 3,4 m, o tom de madeira nova, veio, bisel, juntas e
# topos discretos), com a luz da final; o banco em L de bronze fica. O chuveiro do deck de cima fica (os px dele, neutros,
# na caixa `chuveiro_px`), e o rótulo DECK volta pelo alfa dele (o escuro sobre a madeira antiga, recomposto sobre a
# nova); as letras D das escadas que caem no deck saem (o triângulo e a descrição entram no passo das escadas).
# E a linha da instalação do chuveiro (usuário, com a linha desenhada embaixo do deck de cima: "Inserir uma linha para
# indicar a posição de instalação do chuveiro."): na divisa entre o deck de cima e o de baixo (a borda de baixo do deck
# do chuveiro e do canteiro de grama ao lado, y `linha_px`), de ponta a ponta, no cinza das paredes; o braço do chuveiro
# desce até ela.
DECK_TB = {"cores": [(99, 136, 174), (99, 136, 173), (76, 106, 138)], "chuveiro_px": (844, 738, 878, 776),
           "texto": {"escuro": 95, "area": 3, "area_max": 260, "alt_letra": 16, "junta": (5, 1), "n_min": 3,
                     "larg_min": 12, "alt_max": 22, "cor": (28, 28, 28)},
           "linha_px": (673.0, 775.0, 897.0, 777.6), "cor_linha": (80, 80, 80),
           "braco_px": (860.0, 761.0, 862.0, 775.5), "cor_braco": (176, 178, 180)}


def _linhas_texto(m_txt, q):
    """As linhas de texto (as manchas pequenas juntas na horizontal), como em `texto_claro`."""
    n, lab, st, _ = cv2.connectedComponentsWithStats(m_txt.astype(np.uint8), 8)
    pequenas = [i for i in range(1, n) if q["area"] <= st[i, cv2.CC_STAT_AREA] <= q["area_max"]
                and st[i, cv2.CC_STAT_HEIGHT] <= q["alt_letra"]]
    ok = np.isin(lab, pequenas)
    jx, jy = q["junta"]
    blob = cv2.dilate(ok.astype(np.uint8), np.ones((2 * jy + 1, 2 * jx + 1), np.uint8))
    nb, labb, stb, _ = cv2.connectedComponentsWithStats(blob, 8)
    nman = np.zeros(nb, int)
    for i in pequenas:
        y, x = st[i, cv2.CC_STAT_TOP], st[i, cv2.CC_STAT_LEFT]
        ys, xs = np.nonzero(lab[y:y + st[i, 3], x:x + st[i, 2]] == i)
        nman[labb[y + ys[0], x + xs[0]]] += 1
    return dilatar(np.isin(labb, [b for b in range(1, nb) if nman[b] >= q["n_min"] and
                                  stb[b, cv2.CC_STAT_WIDTH] >= q["larg_min"] and stb[b, cv2.CC_STAT_HEIGHT] <= q["alt_max"]]), 1)


def deck_tb(Q, img, q=DECK_TB):
    import terreo_casaa_1011 as TC
    D = np.zeros(img.shape[:2], bool)
    for c in q["cores"]:
        D |= np.all(Q.chapada == np.uint8(c), axis=2)
    D = fechar(D, 3)
    # o texto escuro sobre o deck (o rótulo DECK): o alfa contra a madeira de perto
    lum = img.astype(np.float32).mean(axis=2)
    qt = q["texto"]
    linhas = _linhas_texto(D & (lum < qt["escuro"]), qt) & D
    fundo = cv2.medianBlur(img, 9).astype(np.float32).mean(axis=2)
    L_t = float(np.mean(qt["cor"]))
    alfa = np.clip((fundo - lum) / np.maximum(fundo - L_t, 1), 0, 1) * linhas
    # sem o texto (pelo entorno), para a luz da final não levar as letras
    base = cv2.inpaint(img, (dilatar(linhas & (alfa > 0.05), 1) * 255).astype(np.uint8), 3, cv2.INPAINT_TELEA)
    guarda = TC.rotulos_na_imagem
    TC.rotulos_na_imagem = lambda *a, **k: []
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            novo = TC.deck_madeira_ta(Q, base, q=dict(TC.DECK_TA, cores=q["cores"]))
    finally:
        TC.rotulos_na_imagem = guarda
    out = novo.astype(np.float32)
    # o chuveiro fica (os px neutros na caixa dele)
    x0, y0, x1, y1 = q["chuveiro_px"]
    reg = img[y0:y1, x0:x1].astype(np.int16)
    neutro = ((reg.max(axis=2) - reg.min(axis=2)) < 22) & (reg.mean(axis=2) > 120)
    neutro = dilatar(neutro, 1)
    out[y0:y1, x0:x1][neutro] = img[y0:y1, x0:x1][neutro]
    # o rótulo de volta
    out = out * (1 - alfa[..., None]) + np.float32(qt["cor"]) * alfa[..., None]
    # a linha da instalação do chuveiro e o braço até ela
    H, W = img.shape[:2]
    for r, cor in ((q["linha_px"], q["cor_linha"]), (q["braco_px"], q["cor_braco"])):
        X0, Y0 = int(r[0]) - 2, int(r[1]) - 2
        w, h = int(r[2] - r[0]) + 5, int(r[3] - r[1]) + 5
        a = _ret_alfa(r, X0, Y0, w, h)[..., None]
        out[Y0:Y0 + h, X0:X0 + w] = out[Y0:Y0 + h, X0:X0 + w] * (1 - a) + np.float32(cor) * a
    print(f"    decks: a madeira nova da Casa A em {D.sum() / Q.px_m ** 2:.1f} m², o chuveiro e o rótulo de volta; a linha da "
          f"instalação do chuveiro na divisa dos dois decks")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
# 5. As portas de giro (usuário: "Melhorar representação das portas de giro. Encostar nas paredes."; nas do louceiro e da
# despensa, "Não tem soleira. E encostar as portas nas paredes."; e nas da área de serviço, do quarto de serviço, do
# depósito, do quarto e do BH do motorista e da adega). As 21 folhas de abrir do PDF (as peças brancas finas da
# ARQ_PAREDE, `folhas`), uma a uma, pela regra [10/11] (a porta ligada à ponta da parede, vértice com vértice):
#  - o marco (as peças brancas pequenas da ARQ_PAREDE, o batente no vão e as guarnições) sai, e a ponta da parede do
#    lado da dobradiça avança até a face da folha (`cliente_subsolo_casaa_0511.portais_cs`, a ponte de `_ligar_folha`,
#    como no Térreo e no 1º Pavimento da Casa A), no cinza das paredes; a caixa de cada porta é a linha do vão (as peças
#    do marco que cruzam a faixa da ponta da folha). A folha entre a área gourmet e a cozinha (1,25 m, sem marco no PDF)
#    fica como está;
#  - a folha de novo, na madeira clara das folhas do 1º Pavimento da Casa A (`um_pav_casaa_1111.RETOQUES_1111F["folha"]`),
#    no retângulo do PDF, com o veio no comprido, o contorno e a sombra curta; a antiga sai antes (o piso do lado de fora
#    dela, `desloc_px`);
#  - no louceiro e na despensa, a soleira sai (o piso de cada lado, `sem_soleira`).
PORTAS_TB = {"folhas": {
    "banho_1": (1922.6, 480.9, 1925.0, 528.7), "closet_master": (1496.6, 517.9, 1551.5, 520.3),
    "suite_1": (2230.1, 597.3, 2232.5, 651.1), "suite_2": (2256.4, 597.3, 2258.8, 651.1),
    "banho_2": (2657.9, 602.5, 2705.7, 604.8), "sala_intima": (1830.9, 721.8, 1884.7, 724.2),
    "suite_3": (2347.4, 721.9, 2401.2, 724.3), "lavabo": (2328.6, 845.1, 2331.0, 898.8),
    "banho_3": (2535.5, 851.1, 2577.3, 853.5), "adega": (2259.4, 1218.3, 2261.7, 1278.0),
    "cozinha": (2126.5, 1297.4, 2180.2, 1299.8), "deposito": (2801.2, 1362.2, 2843.0, 1364.6),
    "quarto_motorista": (2801.2, 1401.9, 2843.0, 1404.3), "louceiro": (1924.1, 1370.5, 1926.5, 1412.3),
    "despensa": (1947.4, 1370.5, 1949.8, 1412.3), "area_servico": (2095.2, 1370.5, 2097.5, 1424.3),
    "bh_motorista": (2958.5, 1504.9, 2960.9, 1540.7),
    "bh_servico": (1866.8, 1506.4, 1902.6, 1508.8), "quarto_servico": (2001.1, 1506.4, 2042.9, 1508.8),
    "bh_gourmet_dir": (1436.9, 1545.2, 1484.6, 1547.6), "bh_gourmet_esq": (1162.2, 1546.7, 1210.0, 1549.1)},
    "faixa_px": 12, "toca_px": 2.0, "desloc_px": 10, "limpa_px": 3.2, "ss": 8, "semente": 1214,
    # as caixas à mão onde a faixa pega peças de outra porta (no banho 2, a porta de correr de baixo)
    "caixas_px": {"banho_2": (2640, 548, 2662, 614)},
    "sem_soleira": [(1885, 1360, 1926, 1374), (1949, 1360, 1989, 1374)],
    "resto_croma": 16, "resto_lum": (100, 236), "resto_folga_px": 4, "resto_entre_px": 4, "miolo_px": 3,
    "miolo_area": 40}


def _caixa_porta(Q, f, q):
    """A linha do vão da folha f: as peças do marco (brancas pequenas da ARQ_PAREDE) na faixa da ponta da folha que toca
    o marco (a dobradiça), até um comprimento de folha para cada lado; devolve (caixa, ponta)."""
    import cliente_subsolo_casaa_0511 as CS
    x0, y0, x1, y1 = f
    vert = (y1 - y0) > (x1 - x0)
    L = max(x1 - x0, y1 - y0)
    k = q["faixa_px"]
    melhor = None
    pontas = ((y0, "cima"), (y1, "baixo")) if vert else ((x0, "esq"), (x1, "dir"))
    for v, nome in pontas:
        cx = (x0 - L - 6, v - k, x1 + L + 6, v + k) if vert else (v - k, y0 - L - 6, v + k, y1 + L + 6)
        _, brancas, _ = CS._pecas_parede(Q, tuple(int(round(c)) for c in cx))
        brancas = [b for b in brancas if b[0] >= cx[0] and b[2] <= cx[2] and b[1] >= cx[1] and b[3] <= cx[3]]
        toca = [b for b in brancas if (abs(b[3] - v) < q["toca_px"] or abs(b[1] - v) < q["toca_px"]) if vert] if vert \
            else [b for b in brancas if abs(b[2] - v) < q["toca_px"] or abs(b[0] - v) < q["toca_px"]]
        if toca and (melhor is None or len(toca) > len(melhor[2])):
            melhor = (brancas, nome, toca)
    brancas, nome, _ = melhor
    c = (min(b[0] for b in brancas) - 2, min(b[1] for b in brancas) - 2, max(b[2] for b in brancas) + 2,
         max(b[3] for b in brancas) + 2)
    return tuple(int(round(v)) for v in c), nome


def _folha_madeira(Q, out, f, rng, ss=8):
    """A folha (retângulo f, px) na madeira clara das folhas do 1º Pavimento da Casa A."""
    import pedidos_terreo_casaa_2910 as P
    import um_pav_casaa_1111 as U
    qf = U.RETOQUES_1111F["folha"]
    fx0, fy0, fx1, fy1 = f
    FX0, FY0 = int(np.floor(fx0)) - 3, int(np.floor(fy0)) - 3
    fw, fh = int(np.ceil(fx1)) + 3 - FX0, int(np.ceil(fy1)) + 3 - FY0
    mk = P._ret_arred((fx0, fy0, fx1, fy1), qf["raio_px"], FX0, FY0, fh, fw, ss)
    al = cv2.resize(mk, (fw, fh), interpolation=cv2.INTER_AREA)
    sx, sy, sg = qf["sombra_px"]
    sb = cv2.GaussianBlur(cv2.warpAffine(al, np.float32([[1, 0, sx], [0, 1, sy]]), (fw, fh)), (0, 0), sg)
    r_ = out[FY0:FY0 + fh, FX0:FX0 + fw].astype(np.float32)
    r_ *= (1 - qf["sombra"] * sb * (1 - al))[..., None]
    out[FY0:FY0 + fh, FX0:FX0 + fw] = np.clip(np.round(r_), 0, 255).astype(np.uint8)
    vert = (fy1 - fy0) > (fx1 - fx0)
    sx_, sy_ = (0.6 * ss, 6.0 * ss) if vert else (6.0 * ss, 0.6 * ss)
    n_ = cv2.GaussianBlur(rng.normal(0, 1, mk.shape).astype(np.float32), (0, 0), sigmaX=sx_, sigmaY=sy_)
    n_ = 1 + qf["veio"] * n_ / max(float(n_.std()), 1e-6)
    out = P._pintar(out, FX0, FY0, fw, fh, ss, mk, np.float32(qf["madeira"])[None, None] * n_[..., None])
    borda = np.clip(mk - cv2.erode(mk, np.ones((5, 5), np.uint8)), 0, 1) * qf["contorno_alfa"]
    return P._pintar(out, FX0, FY0, fw, fh, ss, borda, np.float32(qf["contorno"])[None, None] * np.ones_like(borda)[..., None])


def _restos_marco(out, caixas, q):
    I = out.astype(np.int16)
    lum = out.astype(np.float32).mean(axis=2)
    cr = I.max(axis=2) - I.min(axis=2)
    frio = (cr < q["resto_croma"]) & (lum > q["resto_lum"][0]) & (lum < q["resto_lum"][1]) & (I[..., 0] >= I[..., 2] - 4)
    parede = np.abs(I - 80).max(axis=2) <= 8
    folhas = np.zeros(out.shape[:2], bool)
    for x0, y0, x1, y1 in q["folhas"].values():
        folhas[int(np.floor(y0 - 1.5)):int(np.ceil(y1 + 1.5)), int(np.floor(x0 - 1.5)):int(np.ceil(x1 + 1.5))] = True
    g = q["resto_folga_px"]
    total = 0
    for x0, y0, x1, y1 in caixas.values():
        X0, Y0, X1, Y1 = x0 - g, y0 - g, x1 + g, y1 + g
        r = frio[Y0:Y1, X0:X1] & ~folhas[Y0:Y1, X0:X1]
        pw = parede[Y0:Y1, X0:X1]
        k = q["resto_entre_px"]
        # entre duas paredes (na horizontal ou na vertical, até k px de cada lado): parede
        esq = np.zeros_like(r)
        dir_ = np.zeros_like(r)
        cim = np.zeros_like(r)
        bai = np.zeros_like(r)
        for d in range(1, k + 1):
            esq[:, d:] |= pw[:, :-d]
            dir_[:, :-d] |= pw[:, d:]
            cim[d:] |= pw[:-d]
            bai[:-d] |= pw[d:]
        entre = r & ((esq & dir_) | (cim & bai))
        # e qualquer px (de qualquer cor, fora das folhas) preso entre duas paredes a até `miolo_px`, em manchas pequenas
        # (os pontinhos e filetes claros que sobraram dentro das pontas e das pontes)
        m = q["miolo_px"]
        e2, d2, c2, b2 = (np.zeros_like(r) for _ in range(4))
        for d in range(1, m + 1):
            e2[:, d:] |= pw[:, :-d]
            d2[:, :-d] |= pw[:, d:]
            c2[d:] |= pw[:-d]
            b2[:-d] |= pw[d:]
        miolo = ~pw & ~folhas[Y0:Y1, X0:X1] & ((e2 & d2) | (c2 & b2))
        n, lab, st, _ = cv2.connectedComponentsWithStats(miolo.astype(np.uint8), 8)
        miolo = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] <= q["miolo_area"]])
        entre |= miolo
        reg = out[Y0:Y1, X0:X1]
        reg[entre] = 80
        resto = r & ~entre
        if resto.any():
            reg[:] = cv2.inpaint(reg, cv2.dilate(resto.astype(np.uint8), np.ones((3, 3), np.uint8)) * 255, 2,
                                 cv2.INPAINT_TELEA)
        total += int(r.sum())
    print(f"    portas: {total} px de restos do marco antigo limpos")
    return out


def portas_tb(Q, img, q=PORTAS_TB):
    import cliente_subsolo_casaa_0511 as CS
    out = img.copy()
    caixas = {}
    for nome, f in q["folhas"].items():
        caixas[nome] = q["caixas_px"].get(nome) or _caixa_porta(Q, f, q)[0]
    # a folha antiga sai: o piso do lado de fora dela (o lado com menos parede), `desloc_px` adiante
    lum = img.astype(np.float32).mean(axis=2)
    I = img.astype(np.int16)
    parede = (np.abs(I - 80).max(axis=2) <= 6)
    e = q["limpa_px"]
    d = q["desloc_px"]
    for nome, (x0, y0, x1, y1) in q["folhas"].items():
        vert = (y1 - y0) > (x1 - x0)
        a0, a1 = int(np.floor(x0 - e)), int(np.ceil(x1 + e))
        b0, b1 = int(np.floor(y0 - e)), int(np.ceil(y1 + e))
        if vert:
            esq = parede[b0:b1, a0 - 9:a0].sum()
            dir_ = parede[b0:b1, a1:a1 + 9].sum()
            dx, dy = (d if esq > dir_ else -d), 0
        else:
            cima = parede[b0 - 9:b0, a0:a1].sum()
            baixo = parede[b1:b1 + 9, a0:a1].sum()
            dx, dy = 0, (d if cima > baixo else -d)
        yy, xx = np.mgrid[b0:b1, a0:a1]
        ok = ~parede[yy, xx]
        out[yy[ok], xx[ok]] = out[yy[ok] + dy, xx[ok] + dx]
    # os marcos fora e as pontas das paredes até as folhas
    antes = CS.PORTAIS_CS
    CS.PORTAIS_CS = dict(antes, portais=caixas, faixas={}, cor_parede=80, contorno=(0.0, 80), piso_min=70)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            out = CS.portais_cs(Q, out)
    finally:
        CS.PORTAIS_CS = antes
    # os restos do marco antigo (o desenho do motor era mais largo que o do PDF): na caixa de cada porta, o cinza frio e
    # claro (fora das folhas) entre duas paredes vira parede; o resto, pelo entorno
    out = _restos_marco(out, caixas, q)
    # louceiro e despensa sem soleira: o piso de cada lado (a metade de cima do de cima, a de baixo do de baixo)
    for x0, y0, x1, y1 in q["sem_soleira"]:
        h = y1 - y0
        meio = y0 + h // 2
        out[y0:meio, x0:x1] = out[y0 - h:meio - h, x0:x1]
        out[meio:y1, x0:x1] = out[meio + h:y1 + h, x0:x1]
    # as folhas
    rng = np.random.default_rng(q["semente"])
    for nome, f in q["folhas"].items():
        out = _folha_madeira(Q, out, f, rng)
    print(f"    portas: {len(q['folhas'])} folhas de abrir em madeira clara, vértice com vértice com a ponta da parede "
          f"(marcos fora); louceiro e despensa sem soleira")
    return out


# ----------------------------------------------------------------------------------------------------------------------
PASSOS = [("marrom", marrom_tb), ("bancadas", bancadas_tb), ("gourmet", gourmet_tb), ("deck", deck_tb), ("portas", portas_tb)]


def correcoes(img, de=None, ate=None, salvar_passos=None):
    with contextlib.redirect_stdout(io.StringIO()):
        Q = F.Quadro("Terreo")
    nomes = [n for n, _ in PASSOS]
    i0 = nomes.index(de) if de else 0
    i1 = nomes.index(ate) + 1 if ate else len(nomes)
    out = img
    for nome, f in PASSOS[i0:i1]:
        print(f"  [{nome}]", flush=True)
        out = f(Q, out)
        if salvar_passos:
            Path(salvar_passos).mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(Path(salvar_passos) / f"passo_{nome}.png"), out)
    return out


# Os antes e depois (contra a final de partida, a de 21fa118): a planta inteira e os trechos, em
# `renders/POE642_CasaB_PH_Terreo_1211_<trecho>_antes_depois.jpg` da Casa B (px da final: x0, y0, x1, y1).
ANTES_DEPOIS_TB = {"planta": (280, 60, 3560, 1900)}


def antes_depois_tb(antes, depois, q=ANTES_DEPOIS_TB, max_lado=2400):
    pasta = RENDERS
    for nome, (x0, y0, x1, y1) in q.items():
        a, d = antes[y0:y1, x0:x1], depois[y0:y1, x0:x1]
        lado = (x1 - x0) <= (y1 - y0) * 1.3
        junto = np.hstack([a, np.full((a.shape[0], 12, 3), 255, np.uint8), d]) if lado else \
            np.vstack([a, np.full((12, a.shape[1], 3), 255, np.uint8), d])
        k = min(3.0, max_lado / max(junto.shape[:2]))
        junto = cv2.resize(junto, None, fx=k, fy=k, interpolation=cv2.INTER_LANCZOS4 if k > 1 else cv2.INTER_AREA)
        arq = pasta / f"POE642_CasaB_PH_Terreo_1211_{nome}_antes_depois.jpg"
        cv2.imwrite(str(arq), junto, [cv2.IMWRITE_JPEG_QUALITY, 90])
        print(f"    {arq.name}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--antes", type=Path, default=FINAL, help="a final de partida (padrão: a instalada)")
    ap.add_argument("--saida", type=Path, default=None, help="padrão: grava por cima da final")
    ap.add_argument("--de", default=None)
    ap.add_argument("--ate", default=None)
    ap.add_argument("--passos", type=Path, default=None)
    ap.add_argument("--antes_depois", action="store_true", help="grava os antes e depois (ANTES_DEPOIS_TB)")
    a = ap.parse_args()
    img = cv2.imread(str(a.antes))
    out = correcoes(img, a.de, a.ate, a.passos)
    cv2.imwrite(str(a.saida or FINAL), out)
    print(f"    {a.saida or FINAL}")
    if a.antes_depois:
        antes_depois_tb(img, out)

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


# As escadas (usuário: "Colocar a seta e descrição em todas as escadas"): o D de cada uma sai (os px escuros da letra
# recebem os do mesmo degrau, de `copia` (a faixa de deslocamentos verticais) px acima ou abaixo) e entra o triângulo cheio da Casa A
# (`terreo_casaa_1011.seta_tri`, 15 x 17 px) no degrau de cima, com a ponta para onde se desce, e a descrição em duas
# linhas no corpo dos rótulos (11 px, `ESCADAS_TA["corpo_desc_px"]`), em cinza 45, ao lado, no piso livre: a de 6
# degraus desce da pedra grande para o deck da ducha, no Subsolo; a de 9, da varanda para o deck em L; os blocos de pedra
# descem do deck em L para o jardim (o triângulo de 22/10, `final3840_casab.BLOCOS_F`, com a ponta na borda do deck; o D
# deles saiu com a madeira nova do deck, `deck_tb`).
ESCADAS_TB = {
    "seis": {"letra_px": (680, 643), "tri_px": (680.6, 643.6), "dir": (1, 0), "texto": ("DESCE PARA O", "SUBSOLO"),
             "txt_px": (665.0, 643.6), "alinhar": "direita", "copia": (16, 40)},
    "nove": {"letra_px": (1080, 833), "tri_px": (1080.3, 833.0), "dir": (-1, 0), "texto": ("DESCE PARA O", "DECK"),
             "txt_px": (1096.0, 833.0), "alinhar": "esquerda", "copia": (-42, -18)},
    "blocos": {"letra_px": None, "tri_px": (608.0, 917.6), "dir": (-1, 0), "texto": ("DESCE PARA O", "JARDIM"),
               "txt_px": (623.0, 917.6), "alinhar": "esquerda"},
    "caixa_letra": (11, 13), "escuro": 30, "cor": (45, 45, 45)}


def escadas_tb(Q, img, q=ESCADAS_TB):
    import terreo_casaa_1011 as TC
    out = np.ascontiguousarray(img.copy())
    lum = cv2.cvtColor(out, cv2.COLOR_BGR2GRAY).astype(np.float32)
    bx, by = q["caixa_letra"]
    for nome in ("seis", "nove", "blocos"):
        e = q[nome]
        if e["letra_px"] is None:
            continue
        cx, cy = e["letra_px"]
        caixa = lum[cy - by:cy + by + 1, cx - bx:cx + bx + 1]
        m = np.zeros(lum.shape, bool)
        m[cy - by:cy + by + 1, cx - bx:cx + bx + 1] = caixa < np.median(caixa) - q["escuro"]
        m = dilatar(m, 2)
        ys, xs = np.nonzero(m)
        # o degrau tem gradiente e manchas: entre os deslocamentos verticais de `copia` (no mesmo degrau), o de anel
        # (os 3 px em volta) mais parecido com o daqui, acertado pela média do anel
        anel = dilatar(m, 3) & ~m
        ay, ax = np.nonzero(anel)
        aqui = out[ay, ax].astype(np.float32)
        dx, dy, delta = min(((0, d, aqui.mean(0) - out[ay + d, ax].astype(np.float32).mean(0))
                             for d in range(e["copia"][0], e["copia"][1] + 1)),
                            key=lambda t: float(((aqui - t[2] - out[ay + t[1], ax]) ** 2).mean()))
        out[ys, xs] = np.clip(out[ys + dy, xs + dx].astype(np.float32) + delta, 0, 255).astype(np.uint8)
        print(f"    escada {nome}: o D sai ({int(m.sum())} px)")
    out = out.astype(np.float32)
    for nome in ("seis", "nove", "blocos"):
        e = q[nome]
        out = TC.triangulo(out, TC.seta_tri(*e["tri_px"], e["dir"]))
        out = TC._texto_escada(out, e["texto"], *e["txt_px"], e["alinhar"], q["cor"])
    print("    escadas: o triângulo e a descrição nas 3 (DESCE PARA O SUBSOLO, DESCE PARA O DECK, DESCE PARA O JARDIM)")
    return np.clip(out, 0, 255).astype(np.uint8)


# A entrada (como a da Casa A, `terreo_casaa_1011.soleiras_ta` e `entrada_ta`): "Representar uma soleira na entrada
# igual a casa C": no vão da porta pivotante do PDF (o ARQ_CONTRAPISO de x 2526,6 a 2538,5 px e de y 985,4 a 1155), de
# batente a batente, a faixa da soleira da entrada da Casa C (`casa_c`: a face de 1 px do lado de dentro, a pedra lisa
# clara, a face de 2 px do lado de fora), esticada no comprimento do vão; a folha da porta pivotante (`folha_y`, a barra
# cinza aberta a 90°) fica por cima; os batentes do PDF (as peças brancas de 955,6 a 985,4 e de 1155 a 1182,5) na cor
# das paredes, como os das Casas A e C. "Centralizar a seta com a abertura da porta, usando este modelo de seta": a
# seta de 1,5 m do hall (`final3840_casab.SETA_B`) sai, com o travertino refeito (`pedidos_terreo_casaa_2910.piso_refeito`,
# das `fontes_px` do mesmo hall); entra o triângulo cheio das escadas (18 x 21 px, como o da Casa A), com a ponta para
# dentro da casa, no centro da abertura, a `recuo_px` da soleira.
ENTRADA_TB = {"soleira_px": (2527, 986, 2539, 1155), "folha_y": (1011, 1016),
              "casa_c": "_texturas/originais/soleira_entrada_casac.png",
              "batentes_px": [(2526, 955, 2540, 986), (2526, 1155, 2540, 1183)], "parede": (80, 80, 80),
              "seta_px": (2553, 1104, 2658, 1147), "seta_lum": 120,
              "fontes_px": [(2560, 950, 2690, 1000), (2600, 1146, 2690, 1178)], "semente": 1214,
              "abertura_px": (985.4, 1155.0), "recuo_px": 16.0, "comp": 18.0, "larg": 21.0}


def entrada_tb(Q, img, q=ENTRADA_TB):
    import pedidos_terreo_casaa_2910 as P
    import terreo_casaa_1011 as TC
    out = np.ascontiguousarray(img.copy())
    # a soleira de batente a batente, sob a folha da porta
    x0, y0, x1, y1 = q["soleira_px"]
    c = cv2.imread(str(RAIZ / q["casa_c"]))
    out[y0:y1, x0:x1] = cv2.resize(c, (x1 - x0, y1 - y0), interpolation=cv2.INTER_LINEAR)
    f0, f1 = q["folha_y"]
    out[f0:f1, x0:x1] = img[f0:f1, x0:x1]
    for b0, c0, b1, c1 in q["batentes_px"]:
        out[c0:c1, b0:b1] = np.uint8(q["parede"])
    # a seta antiga sai
    sx0, sy0, sx1, sy1 = q["seta_px"]
    zona = np.zeros(out.shape[:2], bool)
    zona[sy0:sy1, sx0:sx1] = out[sy0:sy1, sx0:sx1].astype(np.float32).mean(axis=2) < q["seta_lum"]
    zona = dilatar(zona, 3)
    out = P.piso_refeito(out, zona, q["semente"], dict(P.PISO_TA, fontes_px=q["fontes_px"]))
    # o triângulo no centro da abertura, com a ponta para dentro
    a0, a1 = q["abertura_px"]
    cy = (a0 + a1) / 2
    cx = x1 + q["recuo_px"] + q["comp"] / 2
    out = TC.triangulo(out.astype(np.float32), TC.seta_tri(cx, cy, (-1, 0), q["comp"], q["larg"]))
    print(f"    entrada: a soleira da Casa C de batente a batente (sob a folha da porta), os batentes na cor da parede; "
          f"sem a seta antiga ({int(zona.sum())} px de travertino refeito); o triângulo no centro da abertura (y = {cy:.0f} px)")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# Os tracejados:
# - o lote (usuário: "remover o tracejado", no de cima; "remover o tracejado vertical", no da direita; "remover", na
#   ponta do muro de baixo que passava do lote): o retângulo tracejado de fora do lote (acima do muro de cima, nas
#   laterais e abaixo do muro de baixo) sai para o fundo branco; o tracejado da borda da direita (`dir_px`: as colunas
#   da linha, de cima a baixo do lote) sai, com o lote fechando reto em `borda_x` (o conteúdo das colunas da linha vem
#   das `dir_px[2]` colunas à esquerda); e o muro de baixo para em `borda_x`, como o de cima;
# - os X (usuário: "Melhorar o X tracejado", nos dois shafts pequenos da varanda e do living; e "Tirar o nome shaft"):
#   os três shafts (`shafts_px`, o vão claro entre as paredes) no fundo claro, sem o X torto e sem o nome, com o X
#   tracejado de canto a canto dos shafts do 1º Pavimento da Casa A (`um_pav_casaa_1111.SHAFTS_1P`: fino, simétrico, um
#   traço cruzando o centro, preto), como o do Subsolo da Casa B;
# - o pergolado (usuário: "Deixar as linhas do pergolado tracejadas mais finas e mais claras. Deixar tudo na mesma cor,
#   preto ou branco."): os traços antigos (pretos no piso e brancos na grama e no jardim, de 1,5 px) saem aqui, antes da
#   grama e do jardim novos (`pergolado_tb` os desenha de novo no fim, finos e numa cor só).
TRACEJADOS_TB = {"lote_px": (297, 93, 3512, 1890), "fundo": (254, 254, 254), "dir_px": (3509, 3512, 4),
                 "borda_x": 3512, "muro_baixo_y": (1870, 1896),
                 "shafts_px": [(1564, 742, 1592, 771), (1563, 1252, 1591, 1278), (1734, 533, 1821, 552)],
                 "perg_larg_px": 4.0, "perg_dif": 14, "perg_raio": 3}


def _segs_pergolado(Q):
    cb = F.B.COBERTURA_B
    z = cb["zona"]
    segs = []
    for d in Q.desenhos:
        r, w = d["rect"], d.get("width") or 0
        if d["type"] == "s" and d.get("layer") == cb["camada"] and round(w, 2) == cb["larg_pdf"] \
                and min(r.width, r.height) <= 0.3 and max(r.width, r.height) <= cb["traco_max"] \
                and z[0] <= r.x0 and r.x1 <= z[2] and z[1] <= r.y0 and r.y1 <= z[3]:
            segs += [(it[1].x, it[1].y, it[2].x, it[2].y) for it in d["items"] if it[0] == "l"]
    # fora: o que corre sobre parede (como em `final3840_casab.projecoes_r8`)
    pe = cv2.dilate((Q.preencher(lambda d: d.get("layer") == "ARQ_PAREDE" and d.get("fill"), ss=2) > 0.3)
                    .astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    fica = []
    for t in segs:
        (u0, v0), (u1, v1) = Q.p2q(t[0], t[1]), Q.p2q(t[2], t[3])
        if not pe[int((v0 + v1) / 2), int((u0 + u1) / 2)]:
            fica.append(t)
    return fica


def _x_shaft(out, rect):
    """O X tracejado de canto a canto de `um_pav_casaa_1111.SHAFTS_1P`, no fundo claro (out em float32)."""
    import um_pav_casaa_1111 as U
    q = U.SHAFTS_1P
    x0, y0, x1, y1 = rect
    out[y0:y1, x0:x1] = np.float32(q["fundo"])
    ss, r = 8, q["recuo_px"]
    X0, Y0 = x0 - 2, y0 - 2
    w, h = (x1 - x0) + 4, (y1 - y0) + 4
    M = np.zeros((h * ss, w * ss), np.uint8)
    passo = q["traco_px"] + q["vao_px"]
    for (ax, ay), (bx, by) in (((x0 + r, y0 + r), (x1 - r, y1 - r)), ((x1 - r, y0 + r), (x0 + r, y1 - r))):
        cx, cy = (ax + bx) / 2, (ay + by) / 2
        L = np.hypot(bx - ax, by - ay) / 2
        ux, uy = (bx - ax) / (2 * L), (by - ay) / (2 * L)
        kmax = int(np.ceil(L / passo)) + 1
        for kk in range(-kmax, kmax + 1):
            t0 = max(kk * passo - q["traco_px"] / 2, -L)
            t1 = min(kk * passo + q["traco_px"] / 2, L)
            if t1 - t0 < 0.4:
                continue
            p0 = ((cx + ux * t0 - X0) * ss, (cy + uy * t0 - Y0) * ss)
            p1 = ((cx + ux * t1 - X0) * ss, (cy + uy * t1 - Y0) * ss)
            cv2.line(M, tuple(int(round(v)) for v in p0), tuple(int(round(v)) for v in p1), 255,
                     max(1, int(round(q["x_px"] * ss))), cv2.LINE_AA)
    al = cv2.resize(M.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)
    al *= U._cobertura((x0, y0, x1, y1), X0, Y0, w, h)
    reg = out[Y0:Y0 + h, X0:X0 + w]
    out[Y0:Y0 + h, X0:X0 + w] = reg * (1 - al[..., None]) + np.float32(q["x"]) * al[..., None]


def tracejados_tb(Q, img, q=TRACEJADOS_TB):
    out = np.ascontiguousarray(img.copy())
    H, W = out.shape[:2]
    lum = out.astype(np.float32).mean(axis=2)
    # fora do lote: os traços (finos) para o fundo
    lx0, ly0, lx1, ly1 = q["lote_px"]
    fora = np.ones((H, W), bool)
    fora[ly0:ly1, lx0:lx1 + 2] = False
    fora[ly0:ly1, :lx0] = False                      # na lateral esquerda, só acima e abaixo do lote (a pedra encosta)
    marca = fora & (lum < 250)
    n, lab, st, _ = cv2.connectedComponentsWithStats(marca.astype(np.uint8), connectivity=8)
    tira = np.isin(lab, [i for i in range(1, n) if min(st[i, 2], st[i, 3]) <= 8])
    out[tira] = np.uint8(q["fundo"])
    # a borda da direita: sem o tracejado, o lote fechando reto
    a, b, k = q["dir_px"]
    bx = q["borda_x"]
    yt, yb = ly0 + 13, q["muro_baixo_y"][0]
    out[yt:yb, a:b] = out[yt:yb, a - k:b - k]
    out[yt:yb, bx:bx + 4] = np.uint8(q["fundo"])
    # o muro de baixo até a borda do lote
    m0, m1 = q["muro_baixo_y"]
    out[m0:m1, bx:] = np.uint8(q["fundo"])
    # o pergolado antigo sai (os traços que fogem do fundo em volta, dentro da faixa dos traços do PDF)
    segs = _segs_pergolado(Q)
    S = 4
    geo = np.zeros((H * 1, W * 1), np.uint8)
    for t in segs:
        (u0, v0), (u1, v1) = Q.p2q(t[0], t[1]), Q.p2q(t[2], t[3])
        cv2.line(geo, (int(round(u0)), int(round(v0))), (int(round(u1)), int(round(v1))), 1,
                 int(round(q["perg_larg_px"])))
    geo = dilatar(geo.astype(bool), 1)
    med = cv2.medianBlur(out, 9).astype(np.float32)
    dif = np.abs(out.astype(np.float32) - med).max(axis=2)
    # (as paredes cheias do PDF; `paredes_pdf` também tem os traços do pergolado, que são da ARQ_PAREDE)
    par = cv2.dilate((Q.preencher(lambda d: d.get("layer") == "ARQ_PAREDE" and d.get("fill"), ss=2) > 0.3)
                     .astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    velho = geo & (dif > q["perg_dif"]) & ~par
    velho = dilatar(velho, 2) & geo & ~par
    out = cv2.inpaint(out, (velho * 255).astype(np.uint8), q["perg_raio"], cv2.INPAINT_TELEA)
    # os X dos shafts
    o = out.astype(np.float32)
    for r in q["shafts_px"]:
        _x_shaft(o, r)
    out = np.clip(np.round(o), 0, 255).astype(np.uint8)
    print(f"    tracejados: o retângulo tracejado de fora do lote ({int(tira.sum())} px) e o da borda da direita saem; o muro "
          f"de baixo para na borda do lote; o pergolado antigo sai ({len(segs)} traços, {int(velho.sum())} px); os "
          f"{len(q['shafts_px'])} shafts no fundo claro com o X de canto a canto (sem o nome SHAFT)")
    return out


# O pergolado de novo (no fim, sobre a grama e o jardim novos): os traços do PDF (`_segs_pergolado`), finos
# (`larg_px`) e numa cor só (`cor`, o preto dos X dos shafts, mais claro que o de antes), sobre o piso, a grama e o jardim.
PERGOLADO_TB = {"larg_px": 0.85, "cor": (60, 60, 60)}


def pergolado_tb(Q, img, q=PERGOLADO_TB):
    import final3840_casaa_terreo as FT
    segs = _segs_pergolado(Q)
    pq = dict(FT.PROJ, larg_px=q["larg_px"], preto=q["cor"], branco=q["cor"])
    out, _ = FT.preto_branco(Q, img, segs, pq)
    par = Q.preencher(lambda d: d.get("layer") == "ARQ_PAREDE" and d.get("fill") and max(d["fill"]) < 0.6, ss=2) > 0.5
    out[par] = img[par]
    print(f"    pergolado: {len(segs)} traços do PDF, de {q['larg_px']} px, todos em cinza {q['cor'][0]}")
    return out


# O mobiliário do estar da varanda e do living (usuário, com os recortes):
# - "Tirar o contorno dos mobiliários" (os dois sofás, o pufe, as mesas): o desenho cinza do PDF sobre as peças (o
#   contorno de fora, as divisões dos módulos e as almofadas em traço) sai; o estofado fica o tecido da própria peça,
#   tecido de novo (`quilting` de um trecho limpo dela, `fonte_px`), com as divisões e as almofadas só como vincos
#   suaves (`vinco`: o traço antigo desfocado, escurecendo pouco) e a borda levemente mais escura (`borda`); a sombra
#   no piso, a de antes;
# - "Tirar a representação desse amadeirado em cima do sofá. Deixar apenas a mesa que encaixa no sofá.": a barra de
#   madeira sobre o sofá da varanda (`barra_px`) sai (o sofá continua sob ela, com as divisões dos módulos); a mesinha
#   que encaixa nele (`mesinha_px`) fica;
# - "Representar como mesa de centro e não como banco estofado": a peça branca acima da mesa de centro da varanda vira
#   mesa, retangular, na madeira da mesa ao lado (tecida do miolo dela), com a borda um pouco mais escura e sem o
#   contorno; a mesa ao lado, sem o contorno também;
# - "Tirar a representação do pé da mesa" (a mesa em gota do living): a cruz do pé e o contorno saem, com a madeira
#   da própria mesa.
MOVEIS_TB = {
    "estofados": {
        "sofa_varanda": {"rets": [(1212, 942, 1441, 1059)], "fonte_px": (1397, 948, 1433, 1027),
                         "barra_px": (1245, 1028, 1430, 1050), "divisoes_x": [1300, 1391],
                         "mesinha_px": (1357, 1046, 1384, 1075)},
        "sofa_living": {"rets": [(1756, 748, 2028, 820), (1955, 748, 2028, 870)], "fonte_px": (1963, 823, 2001, 865),
                        "mesinha_px": (1726, 791, 1765, 821)},
        # o pufe girado: o quadrilátero do PDF (ARQ_LAYOUT HUMANIZAÇÃO), com 1 px a mais para o contorno
        "pufe": {"poli_px": [(1193, 862), (1231, 900), (1210, 921), (1172, 883)], "fonte_px": (1397, 948, 1433, 1027)}},
    "madeiras": {
        "mesa_varanda": {"ret": (1291, 876, 1378, 913), "fonte_px": (1298, 881, 1371, 908)},
        "mesa_nova": {"ret": (1319, 835, 1407, 872), "fonte_px": (1298, 881, 1371, 908)},
        "mesa_gota": {"auto_px": (1788, 852, 1914, 936), "fonte_px": (1812, 872, 1846, 892), "folga": 1}},
    "linha_dif": 22, "vinco": (1.3, 0.09), "borda": (2, 0.07), "borda_madeira": (1, 0.14), "p_px": 12,
    "semente": 1215}


def _mascara_auto(img, caixa):
    x0, y0, x1, y1 = caixa
    r = img[y0:y1, x0:x1].astype(np.float32)
    esc = (r.mean(axis=2) < 178) & ((r.max(axis=2) - r.min(axis=2)) < 30)
    m = ndimage.binary_fill_holes(ndimage.binary_closing(esc, np.ones((3, 3))))
    lab, n = ndimage.label(m)
    t = ndimage.sum(np.ones(m.shape), lab, range(1, n + 1))
    M = np.zeros(img.shape[:2], bool)
    M[y0:y1, x0:x1] = lab == (int(np.argmax(t)) + 1)
    return M


def _tecido(img, fonte, h, w, q, semente):
    sys.path.insert(0, str(RAIZ / "_texturas"))
    import texturas
    a, b, c, d = fonte
    f_ = img[b:d, a:c]
    fontes = [f_, np.ascontiguousarray(f_[:, ::-1]), np.ascontiguousarray(f_[::-1])]
    return texturas.quilting(fontes, h, w, p=q["p_px"], sobra=max(3, q["p_px"] // 3),
                             rng=np.random.default_rng(semente))[:h, :w].astype(np.float32)


def moveis_tb(Q, img, q=MOVEIS_TB):
    out = img.astype(np.float32)
    lum = img.astype(np.float32).mean(axis=2)
    H, W = lum.shape
    sem = q["semente"]
    for nome, e in q["estofados"].items():
        if "rets" in e:
            M = np.zeros((H, W), bool)
            for x0, y0, x1, y1 in e["rets"]:
                M[y0:y1, x0:x1] = True
        elif "poli_px" in e:
            m8 = np.zeros((H, W), np.uint8)
            cv2.fillPoly(m8, [np.int32(np.round(e["poli_px"]))], 1)
            M = dilatar(m8.astype(bool), 1)
        else:
            M = _mascara_auto(img, e["auto_px"])
        fica = np.zeros((H, W), bool)
        if "mesinha_px" in e:
            x0, y0, x1, y1 = e["mesinha_px"]
            fica[y0:y1, x0:x1] = True
        a, b, c, d = e["fonte_px"]
        med = float(np.median(lum[b:d, a:c]))
        linhas = M & (lum < med - q["linha_dif"]) & ~fica
        if "barra_px" in e:
            x0, y0, x1, y1 = e["barra_px"]
            # sob a barra, só as divisões dos módulos continuam (`divisoes_x`)
            linhas[y0:y1, x0:x1] = False
            for xd in e["divisoes_x"]:
                linhas[y0:y1, xd] = True
        borda = M & ~ndimage.binary_erosion(M, iterations=q["borda"][0])
        ys, xs = np.nonzero(M)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        tec = _tecido(img, e["fonte_px"], y1 - y0, x1 - x0, q, sem)
        sem += 1
        reg = out[y0:y1, x0:x1]
        m = (M & ~fica)[y0:y1, x0:x1]
        reg[m] = tec[m]
        # os vincos: o traço de dentro (sem a borda) desfocado; a borda, um pouco mais escura
        sig, k = q["vinco"]
        v = cv2.GaussianBlur((linhas & ~borda).astype(np.float32), (0, 0), sig)
        bd = cv2.GaussianBlur(borda.astype(np.float32), (0, 0), 0.7)
        f = 1 - k * np.clip(v * 1.6, 0, 1) - q["borda"][1] * bd
        sel = M & ~fica
        out[sel] *= f[sel][:, None]
        print(f"    {nome}: sem o contorno ({int(linhas.sum())} px de traço), o tecido de novo"
              + (", sem a barra de madeira (a mesinha fica)" if "barra_px" in e else ""))
    for nome, e in q["madeiras"].items():
        if "ret" in e:
            M = np.zeros((H, W), bool)
            x0, y0, x1, y1 = e["ret"]
            M[y0:y1, x0:x1] = True
        else:
            M = _mascara_auto(img, e["auto_px"])
            if e.get("folga"):
                M = dilatar(M, e["folga"])
        ys, xs = np.nonzero(M)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        tec = _tecido(img, e["fonte_px"], y1 - y0, x1 - x0, q, sem)
        sem += 1
        reg = out[y0:y1, x0:x1]
        m = M[y0:y1, x0:x1]
        reg[m] = tec[m]
        n_b, k_b = q["borda_madeira"]
        borda = M & ~ndimage.binary_erosion(M, iterations=n_b)
        out[borda] *= 1 - k_b
        print(f"    {nome}: madeira sem o contorno" + (" e sem a cruz do pé" if nome == "mesa_gota" else ""))
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# Os guarda-roupas em U e em L (usuário: "corrigir a ligação dos armários, sem divisão", no closet master; "nesse
# armário também, remover a divisão." e "remover a divisão do armário.", nas suítes): cada um redesenhado como uma peça
# só, no desenho do 1º Pavimento da Casa A (`um_pav_casaa_1111._closet`: o fundo bege que escurece junto às portas, os
# cabides de través até o canto, o cabideiro de metal se encontrando no meio do canto, a moldura ocre só por fora), nos
# trechos do PDF de `ajustes_casab.GUARDA_ROUPAS_B` (pt), cada um sem o canto, e os cantos à parte. O da suíte 1 junto à
# circulação, de um trecho só, fica.
CLOSETS_TB = {
    "closet master": {"trechos": [((1059.3, 773.8, 1096.2, 918.3), "direita"), ((1096.2, 918.3, 1317.3, 952.4), "cima"),
                                  ((1317.3, 773.8, 1351.3, 918.3), "esquerda")],
                      "cantos": [(1059.3, 918.3, 1096.2, 952.4), (1317.3, 918.3, 1351.3, 952.4)]},
    "suíte 1": {"trechos": [((1617.8, 736.9, 1651.8, 807.8), "direita"), ((1651.8, 807.8, 1807.7, 844.6), "cima")],
                "cantos": [(1617.8, 807.8, 1651.8, 844.6)]},
    "suíte 2": {"trechos": [((2295.2, 572.5, 2332.1, 739.8), "esquerda"), ((2332.1, 538.5, 2391.6, 572.5), "baixo")],
                "cantos": [(2295.2, 538.5, 2332.1, 572.5)]},
    "suíte 3": {"trechos": [((2108.1, 924.0, 2142.2, 1079.9), "direita"), ((2142.2, 1079.9, 2278.2, 1111.1), "cima")],
                "cantos": [(2108.1, 1079.9, 2142.2, 1111.1)]},
    "semente": 1216}


def closets_tb(Q, img, q=CLOSETS_TB):
    import um_pav_casaa_1111 as U
    out = np.ascontiguousarray(img.copy())
    rng = np.random.default_rng(q["semente"])
    qa = dict(U.CLOSETS_1P)
    nomes = [k for k in q if k != "semente"]
    for n in nomes:
        out = U._closet(Q, out, q[n], qa, rng)
    print(f"    guarda-roupas: {', '.join(nomes)} numa peça só, sem a divisão no canto, os cabides se encontrando")
    return out


# O banco do closet master (usuário: "Representar como banco estofado."): a peça de madeira do meio do closet vira o
# banco estofado da varanda da Casa A (`pedidos_terreo_casaa_2910.banco_estofado_ta`: o quadro de madeira castanho com a
# sombra no piso e o assento de linho com volume e duas costuras), no retângulo da peça (`px`, com a sombra antiga dentro).
BANCO_CLOSET_TB = {"px": (1340, 624, 1451, 670), "quadro_pt": 1.0, "costuras": (1 / 3, 2 / 3), "semente": 1217,
                   "banco": {"linho": (196, 209, 219), "almofada": (150, 172, 196), "madeira": "castanho",
                             "volume_m": 0.06, "volume": 0.16, "vinco": 0.30, "vinco_px": 0.8, "trama": 0.02,
                             "almofada_volume": 0.22, "almofadas_pt": []}}


def banco_closet_tb(Q, img, q=BANCO_CLOSET_TB):
    import pedidos_terreo_casaa_2910 as P
    x0, y0, x1, y1 = q["px"]
    (a, b), (c, d) = Q.q2p(x0, y0), Q.q2p(x1, y1)
    k = q["quadro_pt"]
    bq = dict(q["banco"], quadro_pt=(a + k, b + k, c - k, d - k),
              costuras_x_pt=tuple(a + (c - a) * t for t in q["costuras"]))
    out = P.banco_estofado_ta(Q, np.ascontiguousarray(img.copy()), (a, b, c, d), bq, q["semente"])
    print("    closet master: a peça do meio como banco estofado (quadro de madeira e assento de linho com duas costuras)")
    return out


# As espreguiçadeiras da prainha (usuário: "Colocar uma textura nas espreguiçadeiras"): o tampo off-white das duas (as
# de `revisao_casab_2910.espreguicadeiras_tb`, dentro da água) ganha a textura de um tecido náutico: a trama fina
# (`trama`: ruído de 0,6 px), as manchas largas (`manchas`: ruído de 3 px) e o tom levemente quente (`tom`), só nos px do
# tampo (claros e neutros, dentro de `caixas_px`); o vinco, o aro e a água ficam.
ESPREG_TB = {"caixas_px": [(925, 1145, 1047, 1195), (925, 1222, 1047, 1272)], "lum_min": 214, "croma_max": 18,
             "trama": (0.6, 0.032), "manchas": (3.0, 0.02), "tom": (0.985, 0.995, 1.01), "semente": 1218}


def espreguicadeiras_tb(Q, img, q=ESPREG_TB):
    out = img.astype(np.float32)
    rng = np.random.default_rng(q["semente"])
    n = 0
    for x0, y0, x1, y1 in q["caixas_px"]:
        reg = out[y0:y1, x0:x1]
        tampo = (reg.mean(axis=2) >= q["lum_min"]) & ((reg.max(axis=2) - reg.min(axis=2)) <= q["croma_max"])
        tampo = ndimage.binary_opening(tampo, np.ones((2, 2)))
        h, w = tampo.shape
        f = np.ones((h, w), np.float32)
        for sig, forca in (q["trama"], q["manchas"]):
            r_ = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), sig)
            f += forca * r_ / max(float(r_.std()), 1e-6)
        a = cv2.GaussianBlur(tampo.astype(np.float32), (0, 0), 0.5)
        novo = reg * f[..., None] * np.float32(q["tom"])[None, None, :]
        reg[:] = reg * (1 - a[..., None]) + novo * a[..., None]
        n += int(tampo.sum())
    print(f"    espreguiçadeiras: a textura de tecido no tampo das duas ({n} px)")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# As folhas amadeiradas (usuário: "melhorar a representação do amadeirado, com suas respectivas folhas", na fachada da
# esquerda da suíte master e na fachada de cima): os painéis de madeira de correr do lado de fora das portas de vidro,
# folha por folha como no PDF (as peças brancas de 3 px da ARQ_PAREDE no trilho de fora; cada folha num trilho, em
# degrau), no desenho das folhas do 1º Pavimento da Casa A (`um_pav_casaa_1111.FOLHAS_1P`: ripado de nogueira, as ripas
# marcadas, o veio no comprido, a luz, o contorno de cada folha e a sombra curta para fora). Antes, a faixa entre a face
# de fora e a folha de vidro do mesmo vão (a madeira contínua de antes e o tom salmão entre os trilhos) recebe o piso de
# fora, de logo depois da faixa (`folga_fonte_px`). (`folhas`: a folha de madeira, a de vidro do mesmo vão e o lado de
# fora: "x-" à esquerda, "y-" em cima, "x+" à direita; px do quadro.)
FOLHAS_TB = {"folhas": [
    ((956.2, 395.5, 959.2, 508.9), (965.2, 395.5, 968.1, 508.9), "x-"),
    ((959.2, 513.7, 962.2, 627.2), (968.1, 513.7, 971.1, 627.2), "x-"),
    ((962.2, 631.9, 965.2, 745.4), (971.1, 631.9, 974.1, 745.4), "x-"),
    ((1569.4, 316.7, 1689.7, 319.7), (1569.4, 328.6, 1689.7, 331.6), "y-"),
    ((1694.5, 319.7, 1814.8, 322.7), (1694.5, 331.6, 1814.8, 334.6), "y-"),
    ((1948.6, 316.7, 2089.5, 319.7), (1948.6, 331.6, 2088.3, 334.6), "y-"),
    ((2094.3, 319.7, 2235.2, 322.7), (2093.1, 328.6, 2232.8, 331.6), "y-"),
    ((2244.7, 319.7, 2385.6, 322.7), (2256.1, 331.6, 2391.3, 334.6), "y-"),
    ((2390.4, 316.7, 2531.3, 319.7), (2396.1, 328.6, 2531.3, 331.6), "y-"),
    ((2651.9, 628.4, 2654.9, 724.8), (2640.0, 628.4, 2643.0, 724.8), "x+"),
    ((2654.9, 729.6, 2657.9, 826.0), (2643.0, 729.6, 2646.0, 826.0), "x+")],
    "folga_fonte_px": 4, "folga_px": 0.5, "semente": 1219}


def folhas_tb(Q, img, q=FOLHAS_TB):
    import um_pav_casaa_1111 as U
    qa = U.FOLHAS_1P
    out = img.copy()
    rng = np.random.default_rng(q["semente"])
    # 1. a faixa entre a face de fora e o vidro, com o piso de fora
    for (wx0, wy0, wx1, wy1), (gx0, gy0, gx1, gy1), lado in q["folhas"]:
        if lado == "x-":
            a, b = int(np.floor(min(wx0, 9e9) - 0.5)), int(np.floor(gx0))
            y0, y1 = int(np.floor(wy0)), int(np.ceil(wy1))
            d = (b - a) + q["folga_fonte_px"]
            out[y0:y1, a:b] = out[y0:y1, a - d:b - d]
        elif lado == "x+":
            a, b = int(np.ceil(gx1)), int(np.ceil(wx1 + 0.5))
            y0, y1 = int(np.floor(wy0)), int(np.ceil(wy1))
            d = (b - a) + q["folga_fonte_px"]
            out[y0:y1, a:b] = out[y0:y1, a + d:b + d]
        else:
            a, b = int(np.floor(wy0 - 0.5)), int(np.floor(gy0))
            x0, x1 = int(np.floor(wx0)), int(np.ceil(wx1))
            d = (b - a) + q["folga_fonte_px"]
            out[a:b, x0:x1] = out[a - d:b - d, x0:x1]
    # 2. as folhas, cada uma com o ripado, o contorno e a sombra para fora
    o = out.astype(np.float32)
    f = q["folga_px"]
    for (wx0, wy0, wx1, wy1), _, lado in q["folhas"]:
        vert = lado in ("x-", "x+")
        r = (wx0 - f, wy0, wx1 + f, wy1) if vert else (wx0, wy0 - f, wx1, wy1 + f)
        X0, Y0 = int(np.floor(r[0])) - 4, int(np.floor(r[1])) - 4
        X1, Y1 = int(np.ceil(r[2])) + 4, int(np.ceil(r[3])) + 4
        w, h = X1 - X0, Y1 - Y0
        reg = o[Y0:Y1, X0:X1]
        A = U._cobertura(r, X0, Y0, w, h)
        dx, dy = {"x-": (-1.0, 0.6), "x+": (1.0, 0.6), "y-": (-0.6, -1.0)}[lado]
        sb = cv2.GaussianBlur(cv2.warpAffine(A, np.float32([[1, 0, dx], [0, 1, dy]]), (w, h)), (0, 0), 0.9)
        reg *= (1 - qa["sombra"] * sb * (1 - A))[..., None]
        ys = (np.arange(h, dtype=np.float32) + Y0 + 0.5)[:, None] * np.ones((1, w), np.float32)
        xs = (np.arange(w, dtype=np.float32) + X0 + 0.5)[None, :] * np.ones((h, 1), np.float32)
        veio = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0),
                                sigmaX=0.6 if vert else 6.0, sigmaY=6.0 if vert else 0.6)
        veio /= max(float(veio.std()), 1e-6)
        rel = np.clip(((xs - r[0]) / max(r[2] - r[0], 1e-3)) if vert else ((ys - r[1]) / max(r[3] - r[1], 1e-3)), 0, 1)
        luz = 1 + qa["luz"] * (rel - 0.5) * (-1 if lado in ("x-", "y-") else 1)
        cor = np.float32(qa["madeira"])[None, None] * (luz * (1 + qa["veio"] * veio))[..., None]
        fase = np.mod((ys - r[1]) if vert else (xs - r[0]), qa["ripa_px"])
        jt = np.clip(1 - np.abs(fase - qa["junta_px"] / 2) / (qa["junta_px"] / 2 + 0.5), 0, 1) * qa["junta_forca"]
        cor = cor * (1 - jt[..., None]) + np.float32(qa["junta"]) * jt[..., None]
        cp = qa["contorno_px"]
        dentro = U._cobertura((r[0] + cp, r[1] + cp, r[2] - cp, r[3] - cp), X0, Y0, w, h)
        reg[:] = reg * (1 - A[..., None]) + cor * A[..., None]
        borda = np.clip(A - dentro, 0, 1)[..., None]
        reg[:] = reg * (1 - borda) + np.float32(qa["contorno"]) * borda
    print(f"    folhas amadeiradas: {len(q['folhas'])} folhas de correr de madeira (suíte master, fachada de cima e "
          f"suíte 3) folha por folha, em ripado de nogueira, com a faixa entre elas e o vidro no piso de fora")
    return np.clip(np.round(o), 0, 255).astype(np.uint8)


# O gramado (usuário: "representar o gramado da casa A em todas as demais casas, nos seus respectivos terreos"; "OBS
# GERAL: No terreno não precisa representar muitas árvores, pra não ficar muito poluído e acabar afetando um futuro
# projeto de paisagismo. Representar arbustos que são menores."): o gramado do Térreo da Casa A (`terreo_casaa_1011.
# gramado_ta`): a grama do Subsolo (`texturas.textura("grama_padrao")`, na escala) no gramado do lote (o verde do PDF na
# base chapada, `verde_pdf`, onde o render está verde, sem os jardins internos), e o paisagismo B de `paisagismo.py`
# (a grama realista, os maciços de arbustos pequenos só nos cantos, ~14% do gramado), com 3 plantas como na Casa A: as
# duas árvores pequenas nos cantos de cima e de baixo da esquerda e a palmeira no canto de cima da direita
# (`plantas`: nome, centro px, copa m, raio do maciço m), sem as árvores e os arbustos do render.
GRAMADO_TB = {"verde_pdf": (80, 145, 110), "lote_px": (300, 106, 3510, 1875), "fechar": 5, "area_min": 3000,
              "verde": -4, "verde_azul": 10, "muro_px": 6,
              # o canteiro de grama junto à escada de 6 degraus (branco na base, verde no render)
              "extra_px": [(672, 690, 758, 776)],
              "fora_px": [(2378, 1183, 2526, 1292)],                       # o jardim de 4,62 m² (no passo dos jardins)
              "semente": 1220, "suave": 0.7, "paisagismo": "B",
              "plantas": [("arvore_3", (430, 230), 3.0, 2.1), ("palmeira", (3390, 230), 3.8, 2.5),
                          ("arvore_2", (430, 1760), 3.0, 2.1)]}


def _gramado_mascara_tb(Q, img, q):
    x0, y0, x1, y1 = q["lote_px"]
    lote = np.zeros(img.shape[:2], bool)
    lote[y0:y1, x0:x1] = True
    for a, b, c, d in q["fora_px"]:
        lote[b:d, a:c] = False
    pdf = cv2.morphologyEx(np.all(Q.chapada == np.uint8(q["verde_pdf"]), axis=2).astype(np.uint8), cv2.MORPH_CLOSE,
                           np.ones((q["fechar"], q["fechar"]), np.uint8)).astype(bool) & lote
    n, lab, st, _ = cv2.connectedComponentsWithStats(pdf.astype(np.uint8), 8)
    m = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= q["area_min"]])
    # junto aos muros e às bordas, o verde do render que passa uns px da base entra
    I = img.astype(np.int16)
    vr = (I[..., 1] >= I[..., 2] + q["verde"]) & (I[..., 1] >= I[..., 0] + q["verde_azul"]) & lote
    for _ in range(q["muro_px"]):
        m |= dilatar(m, 1) & vr
    for a, b, c, d in q.get("extra_px", []):
        caixa = np.zeros(m.shape, bool)
        caixa[b:d, a:c] = True
        m |= caixa & vr
    return m


def gramado_tb(Q, img, q=GRAMADO_TB):
    sys.path.insert(0, str(RAIZ / "_texturas"))
    from texturas import textura
    import paisagismo as PG
    m = _gramado_mascara_tb(Q, img, q)
    ys, xs = np.nonzero(m)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    G = _cache(f"grama_{y1 - y0}x{x1 - x0}_{q['semente']}",
               lambda: textura("grama_padrao", Q.px_m, y1 - y0, x1 - x0, semente=q["semente"]).astype(np.float32))
    novo = img.astype(np.float32).copy()
    novo[y0:y1, x0:x1] = G
    out = T.F.pousar(img.astype(np.float32), novo, m, suave=q["suave"])
    out, _ = PG.paisagismo(out, m, Q.px_m, q["lote_px"], q["plantas"], q["paisagismo"])
    print(f"    gramado: a grama da Casa A em {m.sum() / Q.px_m ** 2:.0f} m² do lote, sem as árvores do render; o "
          f"paisagismo {q['paisagismo']} com {len(q['plantas'])} plantas nos cantos e arbustos pequenos")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# Os jardins e a vegetação de dentro (usuário, no jardim de inverno de 10,89 m² e no jardim de 4,62 m²: "Diminuir a
# escala e quantidade de vegetação no jardim de inverno." e "Trocar essa representação do jardim de inverno. Usar a
# mesma do interior da casa A.", com as setas para os dois jardins e para a planta em vaso do hall; na floreira do
# lavatório gourmet: "tirar as plantas coloridas e colocar com o espaçamento igual entre elas"):
# - os dois jardins como o jardim de 4,79 m² da Casa A (`terreo_casaa_1011.GRAMADO_TA["jardim_479"]`): a grama do
#   gramado (`texturas.textura("grama_padrao")`), com a sombra de contato junto às paredes, e poucas plantas da
#   biblioteca em tamanhos diferentes e menores (`plantas`: nome, centro px, copa m), só dentro do jardim (o verde do PDF
#   na base chapada, `chapada`); os rótulos brancos ficam; no de inverno, o X tracejado dos painéis volta fino e claro
#   (`terreo_casaa_1011.FINOS_TA`), como os dos vazios da Casa A;
# - a planta em vaso do hall (a costela-de-adão): sai, com o travertino refeito, e entra uma palmeira pequena, como as
#   dos jardins;
# - a floreira do lavatório gourmet: a terra de novo e `n` arbustos verdes iguais (o arbusto da biblioteca de
#   `paisagismo.py`, num verde só), com o mesmo espaço entre eles.
JARDINS_TB = {
    "jardins": {
        "inverno": {"caixa_px": (2030, 735, 2250, 945), "x_doc": True, "rotulo_px": (2070, 803, 2215, 846),
                    "plantas": [("palmeira_1", (2078, 772), 0.9), ("palmeira_3", (2203, 902), 0.7),
                                ("arbusto_3", (2072, 905), 0.45)]},
        "jardim_462": {"caixa_px": (2345, 1186, 2542, 1279), "rotulo_px": (2440, 1243, 2512, 1276),
                       "plantas": [("palmeira_3", (2408, 1214), 0.7), ("arbusto_3", (2410, 1268), 0.42)]}},
    "contato": (0.20, 3.0), "semente": 1221,
    "vaso": {"caixa_px": (2455, 942, 2526, 1008), "lum": 175, "planta": ("palmeira_3", (2489, 975), 0.75),
             "fontes_px": [(2560, 950, 2690, 1000), (2380, 1030, 2510, 1100)]},
    "floreira": {"px": (1225, 1651, 1423, 1680), "n": 7, "d_m": 0.40, "terra": (34, 44, 56), "terra_ruido": 0.18,
                 "verde": (60, 102, 88)}}


def jardins_tb(Q, img, q=JARDINS_TB):
    sys.path.insert(0, str(RAIZ / "_texturas"))
    from texturas import textura
    import json as _json
    import paisagismo as PG
    import pedidos_terreo_casaa_2910 as P
    import terreo_casaa_1011 as TC
    import final3840_casaa_terreo as FT
    out = img.astype(np.float32)
    rng = np.random.default_rng(q["semente"])
    sombra = _json.loads((RAIZ / "_texturas" / "texturas.json").read_text())["vegetacao"]["sombra"]
    for nome, e in q["jardins"].items():
        x0, y0, x1, y1 = e["caixa_px"]
        # o jardim: a caixa sem as paredes e as esquadrias do PDF
        M = np.zeros(img.shape[:2], bool)
        M[y0:y1, x0:x1] = True
        # sem as paredes (as cheias escuras do PDF) e sem as esquadrias desenhadas (os fios claros e neutros, fora dos
        # traços do X antigo, que saem)
        M &= ~dilatar(Q.preencher(lambda d: d.get("layer") in ("ARQ_PAREDE", "EST_PILAR") and d.get("fill")
                                  and max(d["fill"]) < 0.6, ss=2) > 0.3, 1)
        I = img.astype(np.int16)
        geo = np.zeros(img.shape[:2], np.uint8)
        if e.get("x_doc"):
            for _, _, ss in FT.cadeias_tracejadas(Q, ["DOC_LINHAS E PROJEÇÕES"], min_n=2, min_ext=20):
                for s_ in ss:
                    (u0, v0), (u1, v1) = Q.p2q(s_[0], s_[1]), Q.p2q(s_[2], s_[3])
                    cv2.line(geo, (int(round(u0)), int(round(v0))), (int(round(u1)), int(round(v1))), 1, 2)
        claros = (I.mean(axis=2) > 150) & ((I.max(axis=2) - I.min(axis=2)) < 22) & M & ~dilatar(geo.astype(bool), 2)
        n_, lab_, st_, _ = cv2.connectedComponentsWithStats(claros.astype(np.uint8), 8)
        fios = np.isin(lab_, [i for i in range(1, n_) if max(st_[i, 2], st_[i, 3]) >= 25])   # os fios longos
        M &= ~dilatar(fios, 1)
        # as letras do rótulo (brancas, na caixa do rótulo), sem os traços do X antigo que passam por ela
        a0, b0, a1, b1 = e["rotulo_px"]
        txt = np.zeros(img.shape[:2], bool)
        txt[b0:b1, a0:a1] = ((I.mean(axis=2) > 185) & ((I.max(axis=2) - I.min(axis=2)) < 35))[b0:b1, a0:a1]
        if e.get("x_doc"):
            branco = txt.copy()
            txt &= ~geo.astype(bool)
            # as letras cortadas pelo traço se fecham (o px do traço sob a letra também é branco)
            txt = ndimage.binary_closing(txt, np.ones((3, 3))) & branco | txt
        txt = dilatar(txt, 1) & (I.mean(axis=2) > 120)
        h, w = y1 - y0, x1 - x0
        G = textura("grama_padrao", Q.px_m, h, w, semente=q["semente"] + len(nome)).astype(np.float32)
        # a sombra de contato junto às paredes
        dist = cv2.distanceTransform(M[y0:y1, x0:x1].astype(np.uint8), cv2.DIST_L2, 5)
        k, alc = q["contato"]
        G *= (1 - k * np.exp(-dist / alc))[..., None]
        reg = out[y0:y1, x0:x1]
        mm = M[y0:y1, x0:x1]
        reg[mm] = G[mm]
        # as plantas, só dentro do jardim
        tmp = out.copy()
        for pl, (cx, cy), d in e["plantas"]:
            TC._pousar(tmp, pl, cx, cy, d, Q.px_m)
        a = cv2.GaussianBlur(cv2.erode(M.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(np.float32), (0, 0), 0.6)
        out = tmp * a[..., None] + out * (1 - a[..., None])
        # os rótulos de volta
        out[txt] = img[txt]
        if e.get("x_doc"):
            segs = []
            for _, _, ss in FT.cadeias_tracejadas(Q, ["DOC_LINHAS E PROJEÇÕES"], min_n=2, min_ext=20):
                for s_ in ss:
                    u, v = Q.p2q((s_[0] + s_[2]) / 2, (s_[1] + s_[3]) / 2)
                    if x0 <= u <= x1 and y0 <= v <= y1:
                        segs.append(s_)
            fq = TC.FINOS_TA
            pq = dict(FT.PROJ, larg_px=fq["larg_px"], preto=fq["escuro"], branco=fq["claro"], limiar=fq["limiar"])
            o8 = np.clip(np.round(out), 0, 255).astype(np.uint8)
            novo, _ = FT.preto_branco(Q, o8, segs, pq)
            tapa = dilatar(txt, TC.FINOS_TA["folga_rotulo"])          # o X não passa sobre o rótulo (como na Casa A)
            novo[tapa] = o8[tapa]
            out = novo.astype(np.float32)
        print(f"    jardim {nome}: a grama da Casa A e {len(e['plantas'])} plantas menores"
              + (f"; o X dos painéis fino e claro" if e.get("x_doc") else ""))
    # a planta em vaso do hall: sai (o travertino refeito) e entra a palmeira pequena
    v = q["vaso"]
    x0, y0, x1, y1 = v["caixa_px"]
    o8 = np.clip(np.round(out), 0, 255).astype(np.uint8)
    zona = np.zeros(img.shape[:2], bool)
    reg = o8[y0:y1, x0:x1].astype(np.int16)
    zona[y0:y1, x0:x1] = (reg.mean(axis=2) < v["lum"]) | ((reg[..., 1] - reg[..., 2]) > 4)
    zona = dilatar(ndimage.binary_fill_holes(zona), 3)
    zona[:y0 - 2], zona[y1 + 2:], zona[:, :x0 - 2], zona[:, x1 + 2:] = False, False, False, False
    o8 = P.piso_refeito(o8, zona, q["semente"] + 7, dict(P.PISO_TA, fontes_px=v["fontes_px"]))
    out = o8.astype(np.float32)
    pl, (cx, cy), d = v["planta"]
    TC._pousar(out, pl, cx, cy, d, Q.px_m)
    # a floreira do lavatório gourmet
    f = q["floreira"]
    x0, y0, x1, y1 = f["px"]
    h, w = y1 - y0, x1 - x0
    terra = np.float32(f["terra"])[None, None] * (1 + f["terra_ruido"] * PG.ruido((h, w), 2.0, rng))[..., None]
    out[y0:y1, x0:x1] = terra
    cor0, al0, d0 = PG._sprite("arbusto")
    var = PG._tingir(cor0, al0, f["verde"])
    dpx = f["d_m"] * Q.px_m
    passo = w / f["n"]
    pecas = []
    for i in range(f["n"]):
        c, a = PG._colocar(var, al0, d0, dpx, rng.uniform(0, 360))
        pecas.append((c, a, x0 + passo * (i + 0.5), (y0 + y1) / 2, dpx))
    lim = np.zeros(img.shape[:2], np.float32)
    lim[y0:y1, x0:x1] = 1
    out = PG._camada(out, pecas, lim, sombra)
    print(f"    hall: a planta em vaso trocada pela palmeira pequena; floreira do lavatório gourmet: {f['n']} arbustos "
          f"verdes iguais, com o mesmo espaço entre eles")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# O perímetro (usuário: "Demarcar melhor o perímetro da casa", como no Subsolo, `pedidos_subsolo_casab_1211.
# perimetro_sb`): onde o piso da casa (o ARQ_CONTRAPISO do PDF: a calçada de travertino em volta, a varanda, os decks, a
# piscina e a área de serviço descoberta) encosta no gramado e ali não há parede, um traço no cinza das paredes, de
# `larg_px`, do lado de fora (na grama); os pisantes e os blocos de pedra, o acesso da garagem e os pisantes da entrada
# (`fora_px`) não são a casa.
PERIMETRO_TB = {"larg_px": 2, "cor": (80, 80, 80), "longe_parede_px": 4,
                "fora_px": [(2700, 960, 3520, 1160), (2130, 1240, 3520, 1880), (290, 580, 700, 1000)]}


def perimetro_tb(Q, img, q=PERIMETRO_TB):
    m = _gramado_mascara_tb(Q, img, GRAMADO_TB)
    cp = Q.preencher(lambda d: d.get("layer") == "ARQ_CONTRAPISO" and d.get("fill"), ss=2) > 0.5
    par = Q.preencher(lambda d: d.get("layer") in ("ARQ_PAREDE", "EST_PILAR") and d.get("fill")
                      and max(d["fill"]) < 0.6, ss=2) > 0.3
    k = q["larg_px"]
    faixa = cv2.dilate(cp.astype(np.uint8), np.ones((2 * k + 1, 2 * k + 1), np.uint8)).astype(bool) & ~cp & m
    faixa &= ~dilatar(par, q["longe_parede_px"])
    for a, b, c, d in q["fora_px"]:
        faixa[b:d, a:c] = False
    out = img.copy()
    out[faixa] = np.uint8(q["cor"])
    print(f"    perímetro: {int(faixa.sum())} px de traço ({k} px, cinza das paredes) onde o piso da casa encosta na grama")
    return out


# ----------------------------------------------------------------------------------------------------------------------
PASSOS = [("marrom", marrom_tb), ("bancadas", bancadas_tb), ("gourmet", gourmet_tb), ("deck", deck_tb), ("portas", portas_tb),
          ("escadas", escadas_tb), ("entrada", entrada_tb),
          ("tracejados", tracejados_tb), ("moveis", moveis_tb), ("closets", closets_tb), ("banco", banco_closet_tb),
          ("espreguicadeiras", espreguicadeiras_tb), ("folhas", folhas_tb),
          ("gramado", gramado_tb), ("jardins", jardins_tb), ("perimetro", perimetro_tb),
          ("pergolado", pergolado_tb)]


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
ANTES_DEPOIS_TB = {"planta": (280, 60, 3560, 1900), "escadas_decks": (290, 560, 1210, 1110),
                   "varanda_living": (1150, 720, 2060, 1100), "suite_master_closet": (890, 290, 1660, 800),
                   "suites_fachada": (1560, 290, 2720, 960), "jardins_entrada": (2010, 700, 2730, 1310),
                   "gourmet": (1060, 1270, 1720, 1700), "cozinha_servico": (1600, 1270, 3000, 1720),
                   "piscina": (680, 1100, 1220, 1500)}


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

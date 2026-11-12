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
# (depois, usuário: "representar o pontilhado em preto também, deixando as linhas do pergolado mais finas e mais claras,
# tudo na mesma cor": no cinza, o trecho sobre a grama sumia) em preto, em todo o pergolado (no piso e na grama), fino.
PERGOLADO_TB = {"larg_px": 0.8, "cor": (22, 22, 22)}


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


# A água entre os vidros (usuário, no recorte da borda da piscina junto ao deck: "Corrigir o tom da água entre os
# vidros"): o canal entre os dois vidros da borda esquerda da piscina (`canal_px`) ficou no turquesa saturado de antes
# da água C; ele vai ao tom da água da piscina ao lado (`ref_px`, sem os brilhos acima de `brilho_lum`): a média e o
# desvio de cada canal casados com os dela (o desvio a `contraste`), com o desenho da água do canal mantido; os fios
# escuros dos vidros (abaixo de `vidro_lum`) ficam.
VIDROS_AGUA_TB = {"canal_px": (747, 907, 764, 1093), "ref_px": (768, 915, 800, 1085), "brilho_lum": 190,
                  "vidro_lum": 60, "contraste": 0.85}


def vidros_agua_tb(Q, img, q=VIDROS_AGUA_TB):
    out = img.astype(np.float32)
    x0, y0, x1, y1 = q["canal_px"]
    a0, b0, a1, b1 = q["ref_px"]
    ref = out[b0:b1, a0:a1].reshape(-1, 3)
    ref = ref[ref.mean(axis=1) < q["brilho_lum"]]
    reg = out[y0:y1, x0:x1]
    m = reg.mean(axis=2) >= q["vidro_lum"]
    px = reg[m]
    mu_s, sd_s = px.mean(axis=0), np.maximum(px.std(axis=0), 1e-3)
    mu_r, sd_r = ref.mean(axis=0), ref.std(axis=0)
    reg[m] = (px - mu_s) / sd_s * sd_r * q["contraste"] + mu_r
    print(f"    água entre os vidros: o canal do turquesa (BGR {np.round(mu_s).astype(int).tolist()}) ao tom da piscina "
          f"(BGR {np.round(mu_r).astype(int).tolist()}), {int(m.sum())} px")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# O "?" do usuário na ponta das paredes do BH gourmet da esquerda (usuário, 12/11: "deve ser um defeito a ser
# removido"): a caixa cinza no nicho entre as duas paredes, acima do BH (no PDF, o retângulo do "Ref." com o tracejado
# de armário, que a base desenhava como um inox), sai; o nicho fica no travertino da varanda (`pedidos_terreo_casaa_2910.
# piso_refeito`, das `fontes_px` de logo acima e ao lado), só fora das paredes.
DEFEITO_TB = {"nicho_px": (1110, 1474, 1210, 1528), "fontes_px": [(1115, 1418, 1205, 1470), (1222, 1478, 1290, 1525)],
              "semente": 1222}


def defeito_tb(Q, img, q=DEFEITO_TB):
    import pedidos_terreo_casaa_2910 as P
    x0, y0, x1, y1 = q["nicho_px"]
    par = cv2.dilate((Q.preencher(lambda d: d.get("layer") in ("ARQ_PAREDE", "EST_PILAR") and d.get("fill")
                                  and max(d["fill"]) < 0.6, ss=2) > 0.3).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    I = img.astype(np.int16)
    escuro = (I.mean(axis=2) < 92) & ((I.max(axis=2) - I.min(axis=2)) < 14)          # as paredes desenhadas
    zona = np.zeros(img.shape[:2], bool)
    zona[y0:y1, x0:x1] = True
    zona &= ~par & ~dilatar(escuro & par, 1)
    out = P.piso_refeito(img, zona, q["semente"], dict(P.PISO_TA, fontes_px=q["fontes_px"]))
    print(f"    BH gourmet da esquerda: a caixa cinza do nicho sai ({int(zona.sum())} px de travertino refeito)")
    return out


# As floreiras das janelas (usuário: "Deixar o tom da vegetação dos jardins nas janelas diferente do terreno"; e, com a
# imagem de referência: "para floreira use como inspiração um trecho da imagem anexa"): as 4 floreiras da fachada de
# cima (`floreiras_px`: o miolo verde de cada caixa) recebem a folhagem do trecho da referência (`ref`: a floreira em pé
# da imagem do quintal, folhagem fina verde-escura com flores brancas miúdas), deitada, na escala da planta (`escala`:
# a referência a ~97 px/m levada aos 59,7 px/m do quadro), tecida por image quilting; a borda de dentro da caixa com a
# sombra de contato (`contato`).
FLOREIRAS_TB = {"floreiras_px": [(1253, 315, 1316, 336), (1481, 315, 1544, 336), (1839, 315, 1926, 335),
                                 (2666, 315, 2753, 334)],
                "ref": "_texturas/originais/floreira_flores_brancas_ref.png", "ref_cols": (3, 48), "escala": 0.75, "p_px": 10,
                # a folhagem mais viva que a da referência reduzida (que fica parda): o matiz para o verde, a saturação
                # e o brilho acima; e as flores brancas miúdas salpicadas (`flores`: por px², raio px, alfa)
                "matiz": 6, "sat": 1.45, "brilho": 1.18, "flores": (0.018, 0.55, 0.85), "cor_flor": (232, 240, 242),
                "contato": (0.30, 1.6), "caixa_lum": 95, "semente": 1223}


def floreiras_tb(Q, img, q=FLOREIRAS_TB):
    sys.path.insert(0, str(RAIZ / "_texturas"))
    import texturas
    ref = cv2.imread(str(RAIZ / q["ref"]))[:, q["ref_cols"][0]:q["ref_cols"][1]]        # sem a borda da floreira
    ref = cv2.resize(ref, None, fx=q["escala"], fy=q["escala"], interpolation=cv2.INTER_AREA)
    deitada = np.ascontiguousarray(np.rot90(ref))
    fontes = [deitada, np.ascontiguousarray(deitada[::-1]), np.ascontiguousarray(deitada[:, ::-1])]
    out = img.astype(np.float32)
    I = img.astype(np.int16)
    for i, (x0, y0, x1, y1) in enumerate(q["floreiras_px"]):
        h, w = y1 - y0, x1 - x0
        rng = np.random.default_rng(q["semente"] + i)
        tec = texturas.quilting(fontes, h, w, p=q["p_px"], sobra=max(3, q["p_px"] // 3), rng=rng)[:h, :w]
        hsv = cv2.cvtColor(np.clip(tec, 0, 255).astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[..., 0] = np.clip(hsv[..., 0] + q["matiz"], 0, 179)
        hsv[..., 1] = np.clip(hsv[..., 1] * q["sat"], 0, 255)
        hsv[..., 2] = np.clip(hsv[..., 2] * q["brilho"], 0, 255)
        tec = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32)
        dens, raio, alfa = q["flores"]
        fl = np.zeros((h * 4, w * 4), np.float32)
        for _ in range(int(dens * h * w)):
            cx, cy = rng.uniform(1, w - 1), rng.uniform(1, h - 1)
            cv2.circle(fl, (int(cx * 4), int(cy * 4)), max(1, int(round(raio * 4 * rng.uniform(0.8, 1.3)))), 1.0, -1,
                       cv2.LINE_AA)
        fl = cv2.resize(fl, (w, h), interpolation=cv2.INTER_AREA)[..., None] * alfa
        tec = tec * (1 - fl) + np.float32(q["cor_flor"]) * fl
        reg = I[y0:y1, x0:x1]
        # o miolo: o que não é a caixa (cinza escuro e neutro)
        miolo = ~((reg.mean(axis=2) < q["caixa_lum"]) & ((reg.max(axis=2) - reg.min(axis=2)) < 12))
        miolo = ndimage.binary_fill_holes(ndimage.binary_closing(miolo, np.ones((3, 3))))
        dist = cv2.distanceTransform(miolo.astype(np.uint8), cv2.DIST_L2, 3)
        k, alc = q["contato"]
        tec *= (1 - k * np.exp(-(dist - 1) / alc))[..., None]
        a = cv2.GaussianBlur(miolo.astype(np.float32), (0, 0), 0.5)[..., None]
        out[y0:y1, x0:x1] = out[y0:y1, x0:x1] * (1 - a) + tec * a
    print(f"    floreiras das janelas: {len(q['floreiras_px'])} com a folhagem verde-escura e as flores brancas da "
          f"referência")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# As manchas do Bege Bahia nas escadas (usuário: "reduzir as manchas do bege bahia nas escadas"; no Subsolo da Casa B e
# na Casa A, as manchas a 45%): nos blocos de pedra em cascata (a pedra grande e as lajes, `final3840_casab.BLOCOS_F`) e
# na escada de 6 degraus (`escada6_px`), a banda média da textura (as manchas: o que fica entre o desfoque fino `fino_px`
# e o largo `largo_px`, este medido só dentro da pedra) cai para `forca` do que era; o grão fino e a luz larga ficam. Junto
# às bordas de cada bloco e de cada degrau (`borda_px`: a sombra curta de um bloco sobre o de baixo e o bocel) e nas
# letras e triângulos (escuros), nada muda.
BEGE_ESCADAS_TB = {"escada6_px": (671, 597, 762, 690), "bocels_x": [690.5, 708.4, 726.3, 744.2], "forca": 0.45,
                   "fino_px": 1.2, "largo_px": 14.0, "borda_px": 4, "escuro_lum": 130}


def bege_escadas_tb(Q, img, q=BEGE_ESCADAS_TB):
    H, W = img.shape[:2]
    bq = F.BLOCOS_F
    cx0, cy0, cx1, cy1 = bq["caixa_pt"]
    blocos = [d for d in Q.desenhos if d.get("layer") == "ARQ_CONTRAPISO" and d["type"] == "f" and d.get("fill")
              and len(d["items"]) == 4 and cx0 <= d["rect"].x0 and d["rect"].x1 <= cx1 and cy0 <= d["rect"].y0
              and d["rect"].y1 <= cy1]
    pedra = np.zeros((H, W), np.uint8)
    bordas = np.zeros((H, W), np.uint8)
    for d in blocos:
        for c in Q.caminhos(d):
            if len(c) >= 3:
                pts = np.int32(np.round(c))
                cv2.fillPoly(pedra, [pts], 1)
                cv2.polylines(bordas, [pts], True, 1, 1)
    x0, y0, x1, y1 = q["escada6_px"]
    pedra[y0:y1, x0:x1] = 1
    cv2.rectangle(bordas, (x0, y0), (x1 - 1, y1 - 1), 1, 1)
    for xb in q["bocels_x"]:
        bordas[y0:y1, int(round(xb)) - 1:int(round(xb)) + 1] = 1
    I = img.astype(np.float32)
    lum = I.mean(axis=2)
    # só a pedra que se vê (o bege claro: sem a grama, a madeira e o que está por cima)
    Iq = img.astype(np.int16)
    bege = (pedra > 0) & (lum > 150) & ((Iq[..., 2] - Iq[..., 0]) < 60)
    M = bege.astype(np.float32)
    fino = cv2.GaussianBlur(I, (0, 0), q["fino_px"])
    num = cv2.GaussianBlur(I * M[..., None], (0, 0), q["largo_px"])
    den = cv2.GaussianBlur(M, (0, 0), q["largo_px"])[..., None]
    largo = num / np.maximum(den, 1e-3)
    banda = fino - largo
    protege = dilatar(bordas > 0, q["borda_px"]) | dilatar(lum < q["escuro_lum"], 2)
    w = bege & ~protege
    w = cv2.GaussianBlur(w.astype(np.float32), (0, 0), 1.2) * bege
    out = I - (1 - q["forca"]) * banda * w[..., None]
    print(f"    Bege Bahia das escadas: as manchas a {q['forca']:.0%} em {int(bege.sum())} px ({len(blocos)} blocos e a "
          f"escada de 6 degraus), sem mexer nas bordas, nas sombras curtas e nas letras")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# Os ralos (usuário, com o recorte dos tanques: "adicionar ralos das pias"): o ralo cromado da Casa A
# (`terreo_casaa_1011._ralos`: o aro cromado com a sombra curta, o miolo escuro e o contorno fino) em cada cuba das
# pias: as duas da pia da cozinha, a da pia gourmet e as dois tanques da área de serviço, no meio da cuba, longe da
# bica da torneira (`ralos_px`: centro e raio, px do quadro).
RALOS_TB = {"ralos_px": [(1672.5, 1642.0, 2.6), (1720.5, 1642.0, 2.6), (1385.5, 1500.5, 2.6),
                         (2213.0, 1487.0, 2.6), (2213.0, 1540.0, 2.6)]}


def ralos_tb(Q, img, q=RALOS_TB):
    import terreo_casaa_1011 as TC
    ralos_pt = [(*Q.q2p(x, y), r / FA.PT_PX) for x, y, r in q["ralos_px"]]
    out = np.clip(np.round(TC._ralos(Q, np.ascontiguousarray(img.copy()), ralos_pt)), 0, 255).astype(np.uint8)
    print(f"    ralos: {len(ralos_pt)} (pia da cozinha, pia gourmet, tanques)")
    return out


# A porta de duas folhas da área de serviço (usuário, no recorte: "feche as portas"; "Não precisa representar as portas
# abertas."): as duas folhas abertas a 90° (`abertas_px`, com os marcos e a sombra) saem para o granito do piso (as
# linhas de `copia_dy` px abaixo ou acima, no mesmo piso); o vão do PDF (a peça branca da ARQ_PAREDE na linha da parede,
# `vao_px`) fica no piso de logo ao lado (`vao_dx`); e as duas folhas fechadas, cada uma da sua ponta de parede até o
# meio do vão, no meio da espessura da parede, na madeira clara das outras portas (`_folha_madeira`).
FECHADAS_TB = {"abertas_px": [((2157, 1573, 2206, 1586), 14), ((2157, 1656, 2206, 1668), -14)],
               "vao_px": (2203, 1576, 2216, 1666), "vao_dx": -18,
               "vao_pdf": (2204.1, 1573.6, 2216.1, 1666.1), "larg_folha": 2.4, "semente": 1224}


def portas_fechadas_tb(Q, img, q=FECHADAS_TB):
    out = np.ascontiguousarray(img.copy())
    for (x0, y0, x1, y1), dy in q["abertas_px"]:
        out[y0:y1, x0:x1] = out[y0 + dy:y1 + dy, x0:x1]
    x0, y0, x1, y1 = q["vao_px"]
    out[y0:y1, x0:x1] = out[y0:y1, x0 + q["vao_dx"]:x1 + q["vao_dx"]]
    a, b, c, d = q["vao_pdf"]
    xm, lf = (a + c) / 2, q["larg_folha"]
    meio = (b + d) / 2
    rng = np.random.default_rng(q["semente"])
    for f in ((xm - lf / 2, b, xm + lf / 2, meio), (xm - lf / 2, meio, xm + lf / 2, d)):
        out = _folha_madeira(Q, out, f, rng)
    print("    porta de duas folhas da área de serviço: as folhas abertas saem; as duas fechadas no vão")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# A cozinha e os BH de serviço e do motorista (usuário, com os recortes):
# - "corrija os erros do cooktop": o Danae da ilha tinha entrado nas bocas da direita do cooktop (os furos da peça da
#   base) e deixado um anel cinza em volta; o tampo em volta (`cooktop_px` e `folga_px`) volta ao Danae da ilha (o
#   mesmo campo, a mesma semente) e o cooktop de inox da biblioteca (`cooktop_inox_5_90`, 5 bocas, os botões para a
#   direita) é posto de novo no retângulo do PDF, como em `ajustes_casab.cooktops_b`;
# - "alterar a cor da bancada para dekton danae" (a bancada da pia da cozinha, das duas cubas): a pedra escura de ponta
#   a ponta (com o retorno em L junto à parede da direita e o módulo das cubas, sem as linhas dele) no Dekton Danae da
#   ilha, com a face um tom abaixo; as cubas, as torneiras e os ralos ficam;
# - "alterar para o tom de madeira padrão de armario" (a peça clara junto ao nome COZINHA): a cor padrão dos armários e
#   prateleiras (a do louceiro e da despensa), lisa, com a face um tom abaixo;
# - "melhorar a representação da cuba e o contorno da bancada em marrom granito" (BH serviço e BH motorista): a bancada
#   refeita no marrom tabaco (tecido da ilha gourmet), com o contorno fino um tom abaixo e a sombra curta no piso; a
#   cuba de semiencaixe em louça branca da Casa A (`final3840_casaa.cuba_branca`: a aba, a bacia da borda ao fundo, a
#   válvula), no retângulo do PDF (a parte que passa da bancada sobre o piso, com o piso de logo ao lado por baixo); a
#   torneira cromada (a canopla na ponta da parede e a bica sobre a bacia), pelo desenho do PDF.
COZINHA_TB = {"cooktop_px": (1678.7, 1472.8, 1708.6, 1525.3), "folga_px": 4, "giro": 270,
              "ilha_semente": 1212,
              "pia_comps_px": (1545, 1550, 1830, 1670), "pia_lum": 98, "pia_modulo_px": (1644, 1632, 1754, 1667),
              "cubas_px": [(1653.6, 1634.5, 1691.8, 1660.7), (1701.4, 1634.5, 1739.6, 1660.7)],
              "torneiras_px": [(1671, 1650, 1676, 1665), (1719, 1650, 1724, 1665)], "pia_semente": 1225,
              "armario_px": (1791.3, 1373.3, 1822.0, 1401.7),
              "banhos": [{"bancada_px": (1831, 1499, 1855, 1564.6), "cuba_px": (1838.2, 1519.9, 1861.9, 1543.7),
                          "torneira_px": (1840.1, 1530.3, 1850.4, 1533.3), "base": "inicio", "piso_dx": 14, "piso_dy": 0},
                         {"bancada_px": (2904, 1554, 2968, 1577), "cuba_px": (2923.7, 1545.5, 2947.5, 1569.3),
                          "torneira_px": (2934.1, 1557.1, 2937.1, 1567.4), "base": "fim", "piso_dx": 0, "piso_dy": -12}],
              "tabaco_contorno": (30, 40, 54), "semente": 1226}


def _pt(Q, r):
    (a, b), (c, d) = Q.q2p(r[0], r[1]), Q.q2p(r[2], r[3])
    return (min(a, c), min(b, d), max(a, c), max(b, d))


def cozinha_tb(Q, img, q=COZINHA_TB):
    import terreo_casaa_1011 as TC
    sys.path.insert(0, str(RAIZ / "_blocos"))
    import blocos
    out = img.astype(np.float32)
    H, W = out.shape[:2]
    par = Q.preencher(lambda d: d.get("layer") in ("ARQ_PAREDE", "EST_PILAR") and d.get("fill")
                      and max(d["fill"]) < 0.6, ss=2) > 0.3
    danae_ilha = TC.danae(H, W, q["ilha_semente"])
    # 1. o cooktop
    r = q["cooktop_px"]
    g = q["folga_px"]
    X0, Y0, X1, Y1 = int(np.floor(r[0])) - g, int(np.floor(r[1])) - g, int(np.ceil(r[2])) + g, int(np.ceil(r[3])) + g
    out[Y0:Y1, X0:X1] = danae_ilha[Y0:Y1, X0:X1]
    cb, ab = blocos.bloco("cooktop_inox_5_90", Q.px_m)
    for _ in range(q["giro"] // 90):
        cb, ab = cv2.rotate(cb, cv2.ROTATE_90_CLOCKWISE), cv2.rotate(ab, cv2.ROTATE_90_CLOCKWISE)
    w, h = int(round(r[2] - r[0])) + 1, int(round(r[3] - r[1])) + 1
    cb = cv2.resize(cb, (w, h), interpolation=cv2.INTER_AREA)
    ab = cv2.resize(ab, (w, h), interpolation=cv2.INTER_AREA)
    out = F.B.pousar_rgba(out, cb, ab, (r[0] + r[2]) / 2, (r[1] + r[3]) / 2).astype(np.float32)
    # 2. a bancada da pia da cozinha em Danae
    x0, y0, x1, y1 = q["pia_comps_px"]
    I = img.astype(np.int16)
    L = img.astype(np.float32).mean(axis=2)
    caixa = np.zeros((H, W), bool)
    caixa[y0:y1, x0:x1] = True
    esc = (L < q["pia_lum"]) & ((I[..., 2] - I[..., 0]) > 12) & ~par & caixa
    esc = ndimage.binary_opening(esc, np.ones((3, 3)))
    a0, b0, a1, b1 = q["pia_modulo_px"]
    mod = np.zeros((H, W), bool)
    mod[b0:b1, a0:a1] = True
    lab, n = ndimage.label(esc | mod)
    pia = np.isin(lab, np.unique(lab[mod & (lab > 0)]))
    pia = ndimage.binary_fill_holes(ndimage.binary_closing(pia, np.ones((3, 3)))) & ~par
    cubas = np.zeros((H, W), bool)
    for c in q["cubas_px"]:
        cubas |= _ret_px_bool(H, W, c)
    # os pontinhos do granito antigo junto às bordas da bancada (escuros, colados nela)
    for _ in range(3):
        pia |= dilatar(pia, 1) & (L < 100) & ~par & caixa & ~cubas
    pia &= ~cubas
    for c0, d0, c1, d1 in q["torneiras_px"]:
        t = np.zeros((H, W), bool)
        t[d0:d1, c0:c1] = True
        pia &= ~(t & ((I.max(axis=2) - I.min(axis=2)) < 22) & (L > 95))
    _pintar(out, pia, TC.danae(H, W, q["pia_semente"]), TC.DANAE["borda"])
    # 3. o armário junto ao nome COZINHA, na cor padrão
    m = _ret_px_bool(H, W, q["armario_px"])
    _pintar(out, m, BANCADAS_TB["cor_prateleira"], BANCADAS_TB["face"])
    # 4. as bancadas e as cubas dos BH de serviço e do motorista
    import final3840_casaa as FAa
    o8 = np.clip(np.round(out), 0, 255).astype(np.uint8)
    for k, bh in enumerate(q["banhos"]):
        cuba = _ret_px_bool(H, W, bh["cuba_px"])
        bx0, by0, bx1, by1 = (int(round(v)) for v in bh["bancada_px"])
        antes_par = o8[par].copy()
        # o piso por baixo da parte da cuba que passa da bancada
        fora = cuba.copy()
        fora[by0:by1, bx0:bx1] = False
        ys2, xs2 = np.nonzero(dilatar(fora, 2) & ~par)
        if len(ys2):
            o8[ys2, xs2] = o8[ys2 + bh["piso_dy"], xs2 + bh["piso_dx"]]
        # a bancada: o marrom tabaco, o contorno e a sombra
        rb = _pt(Q, bh["bancada_px"])
        tl = FAa.tela(o8, Q, rb, folga=4)
        mb = tl.ret(rb, 0.2)
        FAa.sombra_q(tl, mb, forca=0.24, dist=0.9, sigma=0.9)
        T_ = _tabaco(img, BANCADAS_TB["fonte_tabaco_px"], tl.h, tl.w, q["semente"] + k)
        tl.pintar(mb, T_)
        tl.contorno(mb, 0.5, q["tabaco_contorno"])
        o8 = tl.gravar()
        o8[par] = antes_par                                   # as paredes ficam
        # a cuba e a torneira
        o8 = FAa.cuba_branca(Q, o8, _pt(Q, bh["cuba_px"]))
        t0, t1, t2, t3 = _pt(Q, bh["torneira_px"])
        horiz = (t2 - t0) >= (t3 - t1)
        tl = FAa.tela(o8, Q, (t0, t1, t2, t3), folga=4)
        if horiz:
            ym = (t1 + t3) / 2
            bica = (t0, ym - 0.55, t2, ym + 0.55)
            base = (t0, ym) if bh["base"] == "inicio" else (t2, ym)
            ponta = (t2, ym) if bh["base"] == "inicio" else (t0, ym)
        else:
            xm = (t0 + t2) / 2
            bica = (xm - 0.55, t1, xm + 0.55, t3)
            base = (xm, t1) if bh["base"] == "inicio" else (xm, t3)
            ponta = (xm, t3) if bh["base"] == "inicio" else (xm, t1)
        mb_ = tl.ret(bica, 0.5)
        FAa.sombra_q(tl, mb_, forca=0.30, dist=0.8, sigma=0.7)
        tl.pintar(mb_, FAa.CROMO["meio"])
        tl.contorno(mb_, 0.3, FAa.CROMO["contorno"])
        for (cx, cy), rr, cor in ((base, 1.5, FAa.CROMO["meio"]), (ponta, 0.8, FAa.CROMO["escuro"])):
            v = tl.vazia()
            px_, py_ = tl.pt(cx, cy)
            cv2.circle(v, (int(px_), int(py_)), int(rr * FA.PT_PX * 8), 255, -1, cv2.LINE_AA)
            tl.pintar(v, cor)
            tl.contorno(v, 0.3, FAa.CROMO["contorno"])
        o8 = tl.gravar()
    print("    cozinha: o cooktop de novo (5 bocas, sem o Danae nas bocas da direita); a bancada da pia em Dekton Danae; o "
          "armário junto ao nome no tom padrão; BH serviço e BH motorista: a bancada em marrom tabaco com o contorno e a "
          "cuba de louça branca com a torneira cromada")
    return o8


def _ret_px_bool(H, W, r):
    m = np.zeros((H, W), bool)
    m[int(round(r[1])):int(round(r[3])), int(round(r[0])):int(round(r[2]))] = True
    return m


# As portas quina a quina (usuário, com os recortes: "melhorar a representação da porta. encoste na parede, quina a
# quina. remova batentes e adicione a parede no lugar dos batentes."; "não há batentes, apenas parede. porta com a quina
# da parede, quina a quina. corrija. revise todas as portas e corrija erros nas paredes."; "remova todos os batentes e
# faça parede."): em cada porta de giro (as de `PORTAS_TB` e a do corredor da adega, `extras`), pelo PDF:
# - a dobradiça é a ponta da folha junto à parede; o eixo da parede é o perpendicular à folha;
# - do lado da dobradiça, a parede (a espessura dela, a faixa das paredes cheias do PDF na ponta) vai da ponta dela até
#   a face da folha: a folha encosta na quina da parede, sem o batente no meio;
# - do outro lado, a parede vem até o comprimento da folha (o vão livre igual à folha);
# - os batentes (o branco e o cinza claro dos marcos nas pontas) ficam sob a parede nova; o que sobra fora dela, junto
#   às pontas, sai pelo entorno;
# - a folha antiga da porta do corredor da adega (cinza, fina, solta) sai, e entra a folha de madeira clara das outras.
QUINA_TB = {"extras": {"corredor_adega": (2042.9, 1210.2, 2080.8, 1212.6)},
            "velhas_px": {"corredor_adega": [((2043, 1208, 2081, 1214), (0, 7)), ((2030, 1208, 2043, 1214), (0, 12))]},
            "fora": ["bh_gourmet_dir_x"], "busca_px": 70, "sobra_px": 6, "parede": (80, 80, 80),
            "resto_lum": 150, "resto_croma": 14, "resto_px": 4, "semente": 1227}


def _quina_porta(W, f):
    """Para a folha f (px): as paredes novas [(x0, y0, x1, y1)] (px, fracionário) do lado da dobradiça e do outro."""
    x0, y0, x1, y1 = f
    horiz = (x1 - x0) >= (y1 - y0)
    L = max(x1 - x0, y1 - y0)
    H, Wd = W.shape
    melhor = None
    for ponta in (0, 1):
        if horiz:
            xe = x0 if ponta == 0 else x1
            px_ = xe - 1.5 if ponta == 0 else xe + 1.5            # para dentro da faixa da parede
            c = int(np.floor(px_))
            if not (0 <= c < Wd):
                continue
            col = W[:, c]
            # a parede acima e abaixo da folha, na coluna
            up = next((r for r in range(int(np.floor(y0)) - 1, int(y0) - 70, -1) if col[r]), None)
            dn = next((r for r in range(int(np.ceil(y1)), int(y1) + 70) if col[r]), None)
        else:
            ye = y0 if ponta == 0 else y1
            py_ = ye - 1.5 if ponta == 0 else ye + 1.5
            c = int(np.floor(py_))
            if not (0 <= c < H):
                continue
            row = W[c, :]
            up = next((r for r in range(int(np.floor(x0)) - 1, int(x0) - 70, -1) if row[r]), None)
            dn = next((r for r in range(int(np.ceil(x1)), int(x1) + 70) if row[r]), None)
        d_up = (y0 if horiz else x0) - (up + 1) if up is not None else 1e9
        d_dn = dn - (y1 if horiz else x1) if dn is not None else 1e9
        d = min(d_up, d_dn)
        if melhor is None or d < melhor[0]:
            melhor = (d, ponta, c, up, dn, d_up <= d_dn)
    d, ponta, c, up, dn, lado_up = melhor
    if d > 25:
        return []
    # a espessura da parede: a faixa contínua de parede, na ponta (a linha logo além dela, dentro da parede)
    if horiz:
        r_ = up if lado_up else dn
        linha = W[r_, :]
    else:
        r_ = up if lado_up else dn
        linha = W[:, r_]
    a = b = c
    while a - 1 >= 0 and linha[a - 1]:
        a -= 1
    while b + 1 < len(linha) and linha[b + 1]:
        b += 1
    c0, c1 = float(a), float(b + 1)
    novas = []
    if horiz:
        if lado_up:
            novas.append((c0, up + 1 - 6, c1, y0))
            if dn is not None and y0 + L < dn:
                novas.append((c0, y0 + L, c1, dn + 6))
        else:
            novas.append((c0, y1, c1, dn + 6))
            if up is not None and y1 - L > up + 1:
                novas.append((c0, up + 1 - 6, c1, y1 - L))
    else:
        if lado_up:
            novas.append((up + 1 - 6, c0, x0, c1))
            if dn is not None and x0 + L < dn:
                novas.append((x0 + L, c0, dn + 6, c1))
        else:
            novas.append((x1, c0, dn + 6, c1))
            if up is not None and x1 - L > up + 1:
                novas.append((up + 1 - 6, c0, x1 - L, c1))
    return novas


def quina_tb(Q, img, q=QUINA_TB):
    import um_pav_casaa_1111 as U
    out = img.copy()
    W = Q.preencher(lambda d: d.get("layer") in ("ARQ_PAREDE", "EST_PILAR") and d.get("fill")
                    and max(d["fill"]) < 0.6, ss=2) > 0.5
    # a folha antiga da porta do corredor da adega
    for nome, rets in q["velhas_px"].items():
        for (a0, b0, a1, b1), (dx, dy) in rets:
            out[b0:b1, a0:a1] = out[b0 + dy:b1 + dy, a0 + dx:a1 + dx]
    folhas = dict(PORTAS_TB["folhas"], **q["extras"])
    o = out.astype(np.float32)
    H, Wd = W.shape
    contas, todas = [], []
    for nome, f in folhas.items():
        novas = _quina_porta(W, f)
        contas.append(f"{nome} {len(novas)}")
        for r in novas:
            X0, Y0 = int(np.floor(r[0])) - 1, int(np.floor(r[1])) - 1
            X1, Y1 = int(np.ceil(r[2])) + 1, int(np.ceil(r[3])) + 1
            a = U._cobertura(r, X0, Y0, X1 - X0, Y1 - Y0)[..., None]
            o[Y0:Y1, X0:X1] = o[Y0:Y1, X0:X1] * (1 - a) + np.float32(q["parede"]) * a
            todas.append(r)
    out = np.clip(np.round(o), 0, 255).astype(np.uint8)
    # os restos claros e neutros dos marcos, colados às paredes novas e fora delas
    I = out.astype(np.int16)
    claro = (I.mean(axis=2) > q["resto_lum"]) & ((I.max(axis=2) - I.min(axis=2)) < q["resto_croma"])
    perto = np.zeros((H, Wd), bool)
    nova = np.zeros((H, Wd), bool)
    for r in todas:
        e = q["resto_px"]
        perto[int(r[1]) - e:int(np.ceil(r[3])) + e, int(r[0]) - e:int(np.ceil(r[2])) + e] = True
        nova[int(round(r[1])):int(round(r[3])), int(round(r[0])):int(round(r[2]))] = True
    resto = claro & perto & ~nova
    n_, lab, st, _ = cv2.connectedComponentsWithStats(resto.astype(np.uint8), 8)
    resto = np.isin(lab, [i for i in range(1, n_) if st[i, 4] <= 40])
    out = cv2.inpaint(out, (dilatar(resto, 1) * 255).astype(np.uint8), 3, cv2.INPAINT_TELEA)
    # as folhas de novo por cima (a madeira clara), e a nova do corredor da adega
    rng = np.random.default_rng(q["semente"])
    for nome, f in folhas.items():
        out = _folha_madeira(Q, out, f, rng)
    print(f"    quina a quina: {len(folhas)} portas, {len(todas)} trechos de parede no lugar dos batentes "
          f"({int(resto.sum())} px de resto de marco); " + ", ".join(contas))
    return out


# As linhas do tapete da suíte master (usuário: "remova essas linhas vermelhas do tapete"): os dois fios laranja que
# atravessam o tapete da cama (restos do desenho antigo das mesinhas e da cabeceira) saem: no retângulo do tapete
# (`tapete_px`), os px quentes (vermelho acima do azul em `quente`) viram o tapete de logo acima e abaixo (inpaint).
TAPETE_TB = {"tapete_px": (1020, 585, 1197, 700), "quente": 40, "lum_min": 100}


def tapete_tb(Q, img, q=TAPETE_TB):
    x0, y0, x1, y1 = q["tapete_px"]
    I = img.astype(np.int16)
    m = np.zeros(img.shape[:2], bool)
    reg = I[y0:y1, x0:x1]
    m[y0:y1, x0:x1] = ((reg[..., 2] - reg[..., 0]) > q["quente"]) & (reg.mean(axis=2) > q["lum_min"])
    # só os fios (as corridas horizontais de 9 px ou mais, de 1 a 2 px de altura), não as mesinhas nem a madeira
    hz = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((1, 9), np.uint8)).astype(bool)
    alto = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((4, 1), np.uint8)).astype(bool)
    fios = hz & ~dilatar(alto, 1)
    out = cv2.inpaint(img, (dilatar(fios, 1) * 255).astype(np.uint8), 2, cv2.INPAINT_TELEA)
    print(f"    tapete da suíte master: os fios laranja saem ({int(fios.sum())} px)")
    return out


# As poltronas do living (usuário: "faça o mesmo que fizemos na casa A com as poltronas. apenas o revestimento do
# encosto em terracota"): o encosto das duas (o C em vinho, de 29/10) no terracota da sala da Casa A (`sala_1111.
# SALA_1111["terracota"]`), com a luz de cada px (a do vinho, relativa à média dele) e a borda antisserrilhada pela
# fração de vinho (o vermelho acima do verde, entre o do fundo, `rg_fundo`, e o do vinho); o assento e os braços ficam.
POLTRONAS_TB = {"caixas_px": [(1690, 838, 1740, 893), (1690, 909, 1740, 964)], "rg_fundo": 12}


def poltronas_tb(Q, img, q=POLTRONAS_TB):
    import sala_1111 as SL
    out = img.astype(np.float32)
    terra = np.float32(SL.SALA_1111["terracota"])
    n = 0
    for x0, y0, x1, y1 in q["caixas_px"]:
        reg = out[y0:y1, x0:x1]
        I = reg
        rg = I[..., 2] - I[..., 1]
        vinho = (rg > 30) & (I[..., 2] > I[..., 0] + 15) & (I.mean(axis=2) < 150)
        W = I[vinho].mean(axis=0)
        Lw = float(W.mean())
        a = np.clip((rg - q["rg_fundo"]) / max(float(W[2] - W[1]) - q["rg_fundo"], 1e-3), 0, 1)
        a *= dilatar(vinho, 1)
        L = np.clip(I.mean(axis=2) / Lw, 0.55, 1.1)
        alvo = I + (terra - W)[None, None, :] * L[..., None]
        reg[:] = I * (1 - a[..., None]) + alvo * a[..., None]
        n += int(vinho.sum())
    print(f"    poltronas do living: o encosto em terracota ({n} px), assento e braços como estavam")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# O sofá do living (usuário: "traga realismo para esse sofá"): o sofá em L peça a peça, no desenho do sofá em L da sala
# íntima do 1º Pavimento da Casa A (`um_pav_casaa_1111.sala_intima_1p`): a base com a costura funda entre as peças, o
# encosto alto ao longo da parede e do lado do canto, as almofadas do encosto com o vinco, os assentos (os dois módulos
# do PDF, o canto e a chaise) separados pela costura, o braço da ponta, cada peça com volume (a borda arredondada mais
# escura do lado oposto à luz) e a trama do bouclé creme; três almofadas soltas (terracota, como os encostos das
# poltronas, e areia) com a sombra curta; a sombra macia do sofá no tapete. A mesinha e a luminária da ponta ficam.
# E a mesa de centro em gota (usuário: "corrija os erros de acabamento dessa mesa de centro. tem uns pontos pretos que
# precisam ser removidos."): os pontos escuros da borda dela (o resto do contorno antigo, `escuro_lum`) saem pelo
# entorno, e a borda da madeira fica lisa, um tom abaixo.
SOFA_LIVING_TB = {
    "pegada_px": [(1756.0, 749.0, 1955.0, 820.0), (1955.0, 749.0, 2027.0, 869.0)],
    "bracos_px": [(1756.0, 749.0, 1764.5, 820.0)],
    "encosto_px": [(1764.5, 749.0, 2027.0, 758.0), (2018.0, 758.0, 2027.0, 869.0)],
    "almof_encosto_px": [((1764.5, 758.0, 2018.0, 767.0), ("y", 762.5)), ((2009.0, 767.0, 2018.0, 869.0), ("x", 2013.5))],
    "assento_px": [(1764.5, 767.0, 1855.0, 820.0), (1855.0, 767.0, 1955.0, 820.0), (1955.0, 767.0, 2009.0, 820.0),
                   (1955.0, 820.0, 2009.0, 869.0)],
    "soltas": [((1782.0, 774.0), (22.0, 10.0), -8.0, "terracota"), ((1938.0, 774.5), (21.0, 10.0), 7.0, "areia"),
               ((2001.5, 790.0), (10.0, 22.0), -6.0, "terracota")],
    "creme": (200, 214, 226), "base": 0.78, "terracota": (66, 100, 166), "areia": (150, 176, 198),
    "volume": 0.20, "volume_px": 3.2, "luz": 0.07, "vinco": 0.16, "vinco_px": 0.8, "trama": 0.035,
    "almofada_volume": 0.30, "almofada_px": 2.6, "semente": 1228,
    "mesinha_px": (1724, 789, 1768, 824),
    "mesa_gota": {"caixa_px": (1786, 850, 1916, 940), "escuro_lum": 120, "anel_px": 3}}


def sofa_living_tb(Q, img, q=SOFA_LIVING_TB):
    import final3840_casad as D
    import pedidos_terreo_casaa_2910 as P
    import um_pav_casaa_1111 as U
    out = img.copy()
    ss, k = 8, Q.px_m
    rng = np.random.default_rng(q["semente"])
    par = FA.paredes_pdf(Q) > 0.3
    X0 = int(np.floor(min(r[0] for r in q["pegada_px"]))) - 24
    Y0 = int(np.floor(min(r[1] for r in q["pegada_px"]))) - 24
    X1 = int(np.ceil(max(r[2] for r in q["pegada_px"]))) + 24
    Y1 = int(np.ceil(max(r[3] for r in q["pegada_px"]))) + 24
    w, h = X1 - X0, Y1 - Y0

    def ret(r, raio):
        return P._ret_arred(r, raio, X0, Y0, h, w, ss)

    def red(M):
        return cv2.resize(M, (w, h), interpolation=cv2.INTER_AREA)
    sofa = np.zeros((h * ss, w * ss), np.float32)
    for r in q["pegada_px"]:
        sofa = np.maximum(sofa, ret(r, 2.0))
    # a sombra macia no tapete e no piso
    a = red(sofa)
    luz = np.ones((h, w), np.float32)
    for sd in D.SOMBRA_JOGOS_D:
        dm = np.float32([[1, 0, sd["dx_m"] * k], [0, 1, sd["dy_m"] * k]])
        luz *= 1 - cv2.GaussianBlur(cv2.warpAffine(a, dm, (w, h), flags=cv2.INTER_LINEAR), (0, 0),
                                    sd["sig_m"] * k) * sd["forca"]
    livre = (~par[Y0:Y1, X0:X1]).astype(np.float32)
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    reg *= (1 - (1 - luz) * (1 - a) * livre)[..., None]
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    # a base e as peças
    creme = np.float32(q["creme"])
    tr = cv2.GaussianBlur(rng.normal(0, 1, sofa.shape).astype(np.float32), (0, 0), 0.4 * ss)
    tr2 = cv2.GaussianBlur(rng.normal(0, 1, sofa.shape).astype(np.float32), (0, 0), 1.6 * ss)
    trama = (1 + q["trama"] * tr / max(float(tr.std()), 1e-6)) * (1 + 0.6 * q["trama"] * tr2 / max(float(tr2.std()), 1e-6))
    out = P._pintar(out, X0, Y0, w, h, ss, sofa, creme[None, None] * (q["base"] * trama)[..., None])
    yy, xx = np.mgrid[0:h * ss, 0:w * ss].astype(np.float32)
    px, py = (xx + 0.5) / ss + X0, (yy + 0.5) / ss + Y0
    folga = 0.35

    def peca(r, raio, claro=1.0, vinco=None):
        M = ret((r[0] + folga, r[1] + folga, r[2] - folga, r[3] - folga), raio)
        f = U._volume(M > 0.5, ss, q["volume"], q["volume_px"], q["luz"]) * claro * trama
        if vinco:
            eixo, v = vinco
            f *= 1 - q["vinco"] * np.exp(-(((px if eixo == "x" else py) - v) / q["vinco_px"]) ** 2)
        return P._pintar(out, X0, Y0, w, h, ss, M, creme[None, None] * f[..., None])
    for r in q["encosto_px"]:
        out = peca(r, 1.8, 1.03)
    for r, vinco in q["almof_encosto_px"]:
        out = peca(r, 2.0, 0.97, vinco)
    for r in q["assento_px"]:
        out = peca(r, 2.4, 1.0)
    for r in q["bracos_px"]:
        out = peca(r, 2.6, 1.04)
    for c, tam, ang, cor in q["soltas"]:
        M = U._ret_girado(c, tam, ang, 1.9, X0, Y0, h, w, ss)
        a = red(M)
        sh = cv2.GaussianBlur(cv2.warpAffine(a, np.float32([[1, 0, -1.0], [0, 1, 1.0]]), (w, h)), (0, 0), 1.0)
        reg = out[Y0:Y1, X0:X1].astype(np.float32)
        reg *= (1 - 0.35 * sh * (1 - a))[..., None]
        out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
        f = U._volume(M > 0.5, ss, q["almofada_volume"], q["almofada_px"], q["luz"]) * trama
        out = P._pintar(out, X0, Y0, w, h, ss, M, np.float32(q[cor])[None, None] * f[..., None])
    # a mesinha da ponta por cima do sofá (como estava)
    mx0, my0, mx1, my1 = q["mesinha_px"]
    out[my0:my1, mx0:mx1] = img[my0:my1, mx0:mx1]
    # a mesa de centro em gota, redesenhada: a forma suavizada e antisserrilhada, a madeira dela por dentro (sem os
    # pontos escuros) e o tapete limpo em volta
    g = q["mesa_gota"]
    x0, y0, x1, y1 = g["caixa_px"]
    I = out.astype(np.int16)
    caixa = np.zeros(out.shape[:2], bool)
    caixa[y0:y1, x0:x1] = True
    madeira = caixa & ((I[..., 2] - I[..., 0]) > 35) & (I.mean(axis=2) > 120)
    madeira = ndimage.binary_fill_holes(ndimage.binary_closing(madeira, np.ones((5, 5))))
    lab, n = ndimage.label(madeira)
    t = ndimage.sum(np.ones(madeira.shape), lab, range(1, n + 1))
    madeira = lab == (int(np.argmax(t)) + 1)
    escuro = dilatar(madeira, g["anel_px"]) & (I.mean(axis=2) < g["escuro_lum"]) & caixa
    # a madeira de dentro, sem os pontos escuros
    dentro = ndimage.binary_erosion(madeira, iterations=2)
    sujo = (madeira & ~dentro) | (madeira & (I.mean(axis=2) < g["escuro_lum"]))
    wood = cv2.inpaint(out, (dilatar(sujo, 1) * 255).astype(np.uint8), 3, cv2.INPAINT_TELEA).astype(np.float32)
    # o fundo (o tapete) no anel da mesa e nos pontos
    anel = dilatar(madeira, g["anel_px"] + 1)
    bg8 = out.copy()
    U._anel(bg8, madeira, g["anel_px"] + 2, 3, np.zeros(madeira.shape, bool))
    bg = bg8.astype(np.float32)
    # a forma suavizada, em 8x, antisserrilhada
    k8 = 8
    Mbig = cv2.resize(madeira.astype(np.float32), None, fx=k8, fy=k8, interpolation=cv2.INTER_LINEAR)
    Mbig = cv2.GaussianBlur(Mbig, (0, 0), 1.6 * k8) > 0.5
    alfa = cv2.resize(Mbig.astype(np.float32), (out.shape[1], out.shape[0]), interpolation=cv2.INTER_AREA)
    borda = np.clip(alfa - cv2.erode(alfa, np.ones((3, 3), np.uint8)), 0, 1)
    wood *= (1 - 0.10 * borda)[..., None]
    o = out.astype(np.float32)
    zona = dilatar(anel, 2)
    o[zona] = (bg * (1 - alfa[..., None]) + wood * alfa[..., None])[zona]
    out = np.clip(np.round(o), 0, 255).astype(np.uint8)
    print(f"    sofá do living: em L, peça a peça (encosto, almofadas, 4 assentos, braço, 3 almofadas soltas), com a "
          f"sombra macia; mesa de centro em gota sem os pontos pretos da borda ({int(escuro.sum())} px)")
    return out


# As cadeiras das escrivaninhas (usuário: "revise as cadeiras das escrivaninhas e traga mais realismo para elas. se for
# o caso, substitua-as."): as três do render (suíte master, suíte 1, suíte 2) eram o recorte branco chapado com o aro
# cinza; saem (o vinílico em volta, `terreo_casaa_1011._tapar_rotulo`: o trecho do mesmo piso, sem móvel nem parede,
# que melhor casa o anel) e entra a cadeira de madeira e linho da biblioteca (`final3840_casad._cadeira_bloco`, a da
# escrivaninha da suíte 3 do 1º Pav da Casa A), virada para a mesa, 1/3 sob o tampo, com a sombra curta do tampo
# sobre ela. Mesa e cadeira do PDF (ARQ_LAYOUT HUMANIZAÇÃO / ARQ_MOBILIÁRIO, px); `meio`: o centro da cadeira no outro
# eixo.
CADEIRAS_TB = {"cadeiras": [{"nome": "suíte master", "mesa_px": (1204.0, 388.3, 1233.8, 510.6),
                             "velha_px": (1178.8, 453.1, 1224.9, 497.2), "frente": (1, 0), "meio": 475.2},
                            {"nome": "suíte 1", "mesa_px": (2031.0, 582.4, 2171.3, 612.2),
                             "velha_px": (2056.8, 561.5, 2094.9, 602.0), "frente": (0, 1), "meio": 2075.9},
                            {"nome": "suíte 2", "mesa_px": (2248.9, 362.2, 2281.1, 517.5),
                             "velha_px": (2261.5, 379.9, 2302.0, 416.9), "frente": (-1, 0), "meio": 398.4}],
               "folga_px": 4, "croma_max": 40, "aro_px": 2, "busca_px": 70}


def cadeiras_tb(Q, img, q=CADEIRAS_TB):
    import final3840_casad as D
    import terreo_casaa_1011 as TC
    import um_pav_casaa_1111 as U
    H, W = img.shape[:2]
    rf = F.ROTULOS_F
    out = img.copy()
    moveis = Q.preencher(lambda d: d.get("layer") in rf["obstaculos"] and d.get("layer") != "ARQ_PAREDE", ss=2) > 0.05
    par = Q.preencher(lambda d: d.get("layer") in ("ARQ_PAREDE", "EST_PILAR") and d.get("fill")
                      and max(d["fill"]) < 0.6, ss=2) > 0.3
    I = img.astype(np.int16)
    croma = I.max(axis=2) - I.min(axis=2)
    # 1. a cadeira velha sai (o que dela aparece fora do tampo, com o aro)
    for c in q["cadeiras"]:
        g = q["folga_px"]
        x0, y0, x1, y1 = c["velha_px"]
        caixa = np.zeros((H, W), bool)
        caixa[int(y0) - g:int(np.ceil(y1)) + g, int(x0) - g:int(np.ceil(x1)) + g] = True
        mx0, my0, mx1, my1 = c["mesa_px"]
        mesa = np.zeros((H, W), bool)
        mesa[int(np.floor(my0)):int(np.ceil(my1)), int(np.floor(mx0)):int(np.ceil(mx1))] = True
        velha = caixa & ~mesa & ~par & (croma < q["croma_max"])
        n, lab, st, _ = cv2.connectedComponentsWithStats(velha.astype(np.uint8), 8)
        velha = np.isin(lab, [i for i in range(1, n) if st[i, 4] >= 30])
        zona = dilatar(velha, q["aro_px"]) & caixa & ~mesa & ~par
        # o piso do quarto: a cor do PDF do vinílico em volta (fora da cadeira e da mesa)
        anel = dilatar(caixa, 6) & ~caixa & ~mesa & ~moveis & ~par
        ch = Q.chapada.reshape(-1, 3)[anel.ravel()]
        cores, nn = np.unique(ch, axis=0, return_counts=True)
        piso = cores[np.argmax(nn)]
        outro = np.any(Q.chapada != piso, axis=2) & ~zona
        proibido = dilatar(moveis | par, 2) | outro
        with contextlib.redirect_stdout(io.StringIO()):
            out, _ = TC._tapar_rotulo(out, zona, proibido, np.zeros((H, W, 3), np.uint8),
                                      dict(TC.ROTULOS_1111, busca_px=q["busca_px"]))
        c["_tirada"] = int(zona.sum())
    # 2. a cadeira da biblioteca, virada para a mesa, 1/3 sob o tampo, com a sombra curta do tampo
    of = out.astype(np.float32)
    k = Q.px_m
    qc = D.MOVEIS_TD["cadeira"]
    D_px = qc["m"] * k
    s_ = D.F.PECAS["sombra"]
    for c in q["cadeiras"]:
        mx0, my0, mx1, my1 = c["mesa_px"]
        X0, Y0 = int(np.floor(mx0)), int(np.floor(my0))
        X1, Y1 = int(np.ceil(mx1)), int(np.ceil(my1))
        mesa_a = np.zeros((H, W), np.float32)
        mesa_a[Y0:Y1, X0:X1] = U._cobertura((mx0, my0, mx1, my1), X0, Y0, X1 - X0, Y1 - Y0)
        fx, fy = c["frente"]
        recuo = D_px * (0.5 - qc["sob"])
        if fx:
            ccx = (mx0 - recuo) if fx > 0 else (mx1 + recuo)
            ccy = c["meio"]
        else:
            ccx = c["meio"]
            ccy = (my0 - recuo) if fy > 0 else (my1 + recuo)
        cor, a = D._cadeira_bloco(Q, (fx, fy), contorno=qc["contorno"])
        D._pousar(of, cor, a, ccx, ccy, k, cobre=mesa_a)
        d_ = s_["dist_m"] * k
        sb = cv2.GaussianBlur(cv2.warpAffine(mesa_a, np.float32([[1, 0, -d_], [0, 1, d_]]), (W, H)), (0, 0),
                              s_["sig_m"] * k) * s_["forca"]
        cad_a = np.zeros((H, W), np.float32)
        h_, w_ = a.shape
        ty, tx = int(round(ccy - h_ / 2)), int(round(ccx - w_ / 2))
        cad_a[ty:ty + h_, tx:tx + w_] = a
        of *= (1 - sb * np.clip(cad_a, 0, 1) * (1 - mesa_a))[..., None]
        c["_centro"] = (round(float(ccx), 1), round(float(ccy), 1))
    out = np.clip(np.round(of), 0, 255).astype(np.uint8)
    for c in q["cadeiras"]:
        print(f"      {c['nome']}: a cadeira chapada sai ({c['_tirada']} px de vinílico refeito); a de madeira e linho "
              f"em {c['_centro']}, virada para a mesa {c['frente']}")
    print(f"    cadeiras das escrivaninhas: {len(q['cadeiras'])} trocadas pela de madeira e linho da biblioteca, 1/3 sob "
          f"o tampo, com a sombra curta dele")
    return out


# O estar da varanda pela IA (usuário: "vamos trazer mais realismo para esses mobiliarios, preservando-os, mas trazendo
# do 3D para a planta humanizada. use o higgsfield", com o recorte do estar da varanda): o recorte de 400 x 320 px
# (`caixa_px`, 5:4) foi ao Nano Banana Pro (Higgsfield) 4x maior, com o pedido de manter enquadramento, escala, lugar,
# tamanho e cor de cada peça e só trazer o realismo do 3D visto de cima (sofá com as almofadas e o encosto embaixo,
# virado para as mesas de centro; poltronas e pufes em bouclé; mesas em carvalho; luz difusa, sombras curtas); a
# variante escolhida, alinhada ao recorte por ECC afim (borda do tapete, texto e piso), está em `ia_png` (2x). Entra só
# o tapete e as peças (os retângulos do PDF, ARQ_MOBILIÁRIO / ARQ_LAYOUT HUMANIZAÇÃO / o tapete, com `folga_px` para
# a sombra curta), a borda esfumada em `funde_px`; o tom da IA casado ao piso de volta (ganho por canal no anel).
VARANDA_IA_TB = {"ia_png": RENDERS / "ia" / "POE642_CasaB_Terreo_varanda_estar_nbp_alinhado.png",
                 "caixa_px": (1112, 776, 1512, 1096),
                 "pecas_px": [(1211.4, 942.3, 1439.3, 1056.6), (1321.8, 834.9, 1405.4, 867.7),
                              (1293.5, 876.7, 1377.1, 909.5), (1358.0, 1038.1, 1381.9, 1073.9),
                              (1457.0, 821.5, 1508.1, 873.0), (1451.9, 907.1, 1503.1, 958.6),
                              (1117.2, 909.7, 1173.3, 965.0), (1172.3, 862.2, 1231.1, 921.0)],
                 "pecas_pdf": [64428, 66870, 67242, 66895, 66910, 67076, 67267, 71961],
                 "tapete_px": (1187.3, 801.7, 1485.9, 1010.6), "folga_px": 10, "cresce_px": 2, "peca_ab_min": 6.0, "peca_l_min": 8.0,
                 "ganho_lim": (0.95, 1.2), "ganho_de": {3: 1}, "sombra_min": 0.78, "piso_lab_max": 7.0, "sombra_px": 7.0,
                 "grao_px": (1114, 985, 1196, 1094)}


def varanda_ia_tb(Q, img, q=VARANDA_IA_TB):
    """Peça a peça: na silhueta de cada peça (a do PDF, antisserrilhada, + `cresce_px`, somada ao que a IA desenhou como
    peça dentro da caixa dela), a IA com o ganho daquela peça (a mediana dela no original sobre a da IA: o tom de antes
    fica); no tapete, a IA com o ganho do tapete; no piso em volta (até `folga_px`), o piso original limpo dos restos das
    peças velhas (o que foge do tom do travertino, refeito só do piso em volta) com a sombra da IA como razão."""
    x0, y0, x1, y1 = q["caixa_px"]
    w, h = x1 - x0, y1 - y0
    ia = cv2.resize(cv2.imread(str(q["ia_png"])), (w, h), interpolation=cv2.INTER_AREA).astype(np.float32)
    reg = img[y0:y1, x0:x1].astype(np.float32)

    def ret(r, d=0, enc=0):
        m = np.zeros((h, w), bool)
        a, b, c, e = r
        m[max(0, int(b - y0 - d) + enc):int(np.ceil(e - y0 + d)) - enc,
          max(0, int(a - x0 - d) + enc):int(np.ceil(c - x0 + d)) - enc] = True
        return m
    zona = ret(q["tapete_px"], d=q["folga_px"])
    for r in q["pecas_px"]:
        zona |= ret(r, d=q["folga_px"])
    tap_b = ret(q["tapete_px"], d=1)
    tap = np.clip(cv2.GaussianBlur(tap_b.astype(np.float32), (0, 0), 0.6), 0, 1)
    # o piso da IA e o que nela é peça
    lab = cv2.cvtColor(np.clip(ia / 255, 0, 1), cv2.COLOR_BGR2LAB)
    caixas = np.zeros((h, w), bool)
    for r in q["pecas_px"]:
        caixas |= ret(r, d=4)
    piso_ia = zona & ~caixas & ~tap_b
    pf = np.median(lab[piso_ia], axis=0)
    # peça: cor diferente do piso, ou mais clara que ele; a sombra (mais escura, no mesmo tom) não é peça (usuário:
    # "corrija a sombra dessa poltrona": a sombra da IA contada como peça deixava a beira em degrau)
    dab = np.hypot(lab[..., 1] - pf[1], lab[..., 2] - pf[2])
    obj_ia = (dab > q["peca_ab_min"]) | (lab[..., 0] - pf[0] > q["peca_l_min"])
    # as silhuetas
    sil = []
    for i, r in zip(q["pecas_pdf"], q["pecas_px"]):
        dd = Q.desenhos[i]
        cov = Q.preencher(lambda d, dd=dd: d is dd, ss=4)[y0:y1, x0:x1].astype(np.float32)
        k = 2 * q["cresce_px"] + 1
        cov = cv2.dilate(cov, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
        oi = (obj_ia & ret(r, d=4) & ~tap_b).astype(np.uint8)
        oi = cv2.morphologyEx(oi, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8)).astype(np.float32)
        sil.append(np.clip(cv2.GaussianBlur(np.maximum(cov, oi), (0, 0), 0.6), 0, 1))
    S = np.stack(sil)
    peso = S.max(axis=0)
    # os ganhos: cada peça na própria silhueta (sem a beira), o tapete no trecho livre
    livre_tap = ret(q["tapete_px"], enc=4)
    for sk in sil:
        livre_tap &= ~(cv2.dilate((sk > 0.01).astype(np.uint8), np.ones((17, 17), np.uint8)) > 0)
    g_tap = np.median(reg[livre_tap], axis=0) / np.median(ia[livre_tap], axis=0)
    ganhos = []
    for sk in sil:
        dentro = cv2.erode((sk > 0.99).astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
        ganhos.append(np.clip(np.median(reg[dentro], axis=0) / np.maximum(np.median(ia[dentro], axis=0), 1),
                              *q["ganho_lim"]))
    for k, kk in q.get("ganho_de", {}).items():
        ganhos[k] = ganhos[kk]
    G = np.stack(ganhos)[S.argmax(axis=0)]
    # o piso original limpo: buraco = peças, tapete e o que foge do travertino na zona; refeito só do piso em volta
    lab0 = cv2.cvtColor(np.clip(reg / 255, 0, 1), cv2.COLOR_BGR2LAB)
    p0 = np.median(lab0[~zona & (reg.mean(axis=2) > 150)], axis=0)
    resto = zona & (np.sqrt(((lab0 - p0) ** 2).sum(axis=2)) > q["piso_lab_max"])
    buraco = zona & (resto | (peso > 0.01) | tap_b)
    buraco = cv2.dilate(buraco.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    limpo = cv2.inpaint(np.clip(reg, 0, 255).astype(np.uint8), buraco.astype(np.uint8), 5,
                        cv2.INPAINT_TELEA).astype(np.float32)
    # o grão do travertino no refeito: o detalhe fino de um trecho limpo do mesmo piso (`grao_px`), rebatido
    gx0, gy0, gx1, gy1 = q["grao_px"]
    gr = img[gy0:gy1, gx0:gx1].astype(np.float32)
    gr = gr - cv2.GaussianBlur(gr, (0, 0), 2.0)
    gh, gw = gr.shape[:2]
    rep = np.tile(np.concatenate([np.concatenate([gr, gr[:, ::-1]], 1), np.concatenate([gr[::-1], gr[::-1, ::-1]], 1)], 0),
                  (h // (2 * gh) + 1, w // (2 * gw) + 1, 1))[:h, :w]
    limpo = np.where(buraco[..., None], limpo + np.clip(rep, -14, 6), limpo)
    anel = zona & (peso < 0.99) & (tap < 0.99)
    # a sombra da IA, que some com a distância à peça (zero na borda da zona)
    sombra = np.clip(lab[..., 0] / pf[0], q["sombra_min"], 1.0)
    dobj = cv2.distanceTransform(((peso < 0.5) & (tap < 0.5)).astype(np.uint8), cv2.DIST_L2, 3)
    sombra = 1 - (1 - sombra) * np.clip(1 - dobj / q["sombra_px"], 0, 1) ** 1.5
    base = np.where(anel[..., None], limpo * sombra[..., None], reg)
    base = base * (1 - tap[..., None]) + ia * g_tap[None, None, :] * tap[..., None]
    o = base * (1 - peso[..., None]) + ia * G * peso[..., None]
    out = img.copy()
    out[y0:y1, x0:x1] = np.clip(np.round(o), 0, 255).astype(np.uint8)
    print(f"    estar da varanda: o tapete e {len(sil)} peças da IA (Nano Banana Pro, alinhada ao recorte) nas "
          f"silhuetas, cada uma no tom dela (ganhos {[round(float(np.mean(v)), 3) for v in ganhos]}, tapete "
          f"{round(float(np.mean(g_tap)), 3)}); a sombra da IA sobre o piso original limpo "
          f"({int((resto & ~(peso > 0.01) & ~tap_b).sum())} px de resto das peças velhas)")
    return out

# O estar do living pela IA (usuário: "vamos substituir por um sofá mais realista que seja semelhante ao proposto, bem
# como a mesa lateral e a luminária de parede? traga-me duas opções para aprovar."; "opção A, pode instalar"; e, sobre a
# opção B: "gostei da poltrona assim, gostei da sombra da mesa de centro assim, gostei da mesa lateral assim e da
# luminária de parede. pode aplicar?"). Três camadas do Nano Banana Pro (Higgsfield), cada uma alinhada ao seu recorte
# (`caixa_px`, a IA volta no mesmo enquadramento; o ajuste fino, translação e escala pela correlação dos gradientes
# fora das peças, já está na `ia_png`, em 2x):
#   1. o sofá em L da opção A (bouclé off-white), na pegada do PDF (`SOFA_LIVING_TB`);
#   2. a mesa lateral de travertino e a arandela preta da opção B (linho greige; o sofá dela não entra), nas silhuetas do
#      PDF (78383, 63984);
#   3. as 2 poltronas e a mesa de centro: o recorte maior do estar (com o sofá A já posto) foi de novo à IA, com a opção
#      B de referência, para as poltronas inteiras em terracota (concha e assento) e a mesa de centro sem o contorno
#      cinza, com a sombra macia no tapete (a opção B corta a 1ª poltrona na borda e deixa a 2ª de fora); silhuetas do
#      PDF 64047, 64139 e 64285, e em volta, até `sombra_px`, a sombra da IA esmaecendo para fora;
#   4. o banco trançado aos pés do estar (usuário: "melhore o aspecto com realismo desse banco trançado. me apresente duas
#      opções para aprovar"; "OPÇÃO BANCO b"): a opção B, estrutura de nogueira e trama de cordão de papel off-white, na
#      silhueta do PDF (67349), metade sobre o tapete e metade sobre o travertino, com a sombra curta da IA.
# Em cada camada: cada peça + `cresce_px`, somada ao que a IA desenhou como peça encostado nela (o que foge do fundo
# original limpo, sem contar a sombra); no tom da IA com o ganho do fundo (piso e tapete fora das peças, original sobre
# IA); o que da peça antiga sobra fora da nova volta ao fundo limpo; o que uma camada anterior já pôs fica (a mesa
# lateral do PDF entra sob o braço do sofá); as linhas escuras de fora das peças antigas (o caixilho do vidro) ficam.
LIVING_IA_TB = {"camadas": [
    {"nome": "sofá (opção A)", "ia_png": RENDERS / "ia" / "POE642_CasaB_Terreo_living_sofa_nbp_opA_alinhado.png",
     "caixa_px": (1700, 722, 2064, 927), "pecas": ["sofa"]},
    {"nome": "mesa lateral e arandela (opção B)",
     "ia_png": RENDERS / "ia" / "POE642_CasaB_Terreo_living_sofa_nbp_opB_alinhado.png",
     "caixa_px": (1700, 722, 2064, 927), "pecas": [78383, 63984]},
    {"nome": "poltronas e mesa de centro (no estilo da opção B)",
     "ia_png": RENDERS / "ia" / "POE642_CasaB_Terreo_living_estar_nbp_alinhado.png",
     "caixa_px": (1660, 805, 1980, 985), "pecas": [64047, 64139, 64285], "sombra_px": 7.0},
    {"nome": "banco trançado (opção B: nogueira e cordão off-white)",
     "ia_png": RENDERS / "ia" / "POE642_CasaB_Terreo_opcao_bancoB_nbp_alinhado.png",
     "caixa_px": (1740, 920, 1990, 1061), "pecas": [67349], "sombra_px": 4.0}],
    "cresce_px": 2, "perto_px": 4, "peca_ab_min": 7.0, "peca_l_min": 9.0, "ganho_lim": (0.92, 1.08), "linha_lum": 110,
    "fora_px": [(2034, 722, 2064, 927), (1810, 970, 1920, 1010)]}


def _living_pdf(Q, peca, x0, y0, w, h):
    import um_pav_casaa_1111 as U
    if peca == "sofa":
        cov = np.zeros((h, w), np.float32)
        for r in SOFA_LIVING_TB["pegada_px"]:
            cov = np.maximum(cov, U._cobertura(r, x0, y0, w, h))
        return cov
    chave = (id(Q), peca)
    if chave not in _SIL_CACHE:
        dd = Q.desenhos[peca]
        _SIL_CACHE[chave] = Q.preencher(lambda d, dd=dd: d is dd, ss=4)
    return _SIL_CACHE[chave][y0:y0 + h, x0:x0 + w].astype(np.float32)


_SIL_CACHE = {}


def _living_camada(Q, img, cam, q, feito):
    x0, y0, x1, y1 = cam["caixa_px"]
    w, h = x1 - x0, y1 - y0
    ia = cv2.resize(cv2.imread(str(cam["ia_png"])), (w, h), interpolation=cv2.INTER_AREA).astype(np.float32)
    # o que a IA inventou fora do PDF, refeito da própria IA `dx` px ao lado (px do quadro)
    for a, b, c, e, dx in cam.get("remendos_ia", ()):
        ia[b - y0:e - y0, a - x0:c - x0] = ia[b - y0:e - y0, a - x0 + dx:c - x0 + dx].copy()
    # uma faixa da IA esticada na largura do PDF (linhas b-e, colunas de a0-a1 para c0-c1, px do quadro)
    for b, e, a0, a1, c0, c1 in cam.get("estica_ia", ()):
        faixa = ia[b - y0:e - y0, a0 - x0:a1 - x0].copy()
        ia[b - y0:e - y0, c0 - x0:c1 - x0] = cv2.resize(faixa, (c1 - c0, e - b), interpolation=cv2.INTER_LINEAR)
    reg = img[y0:y1, x0:x1].astype(np.float32)
    fixo = feito[y0:y1, x0:x1].copy()
    for peca in cam.get("protege", ()):
        fixo = np.maximum(fixo, _living_pdf(Q, peca, x0, y0, w, h))

    def ret(r, d=0):
        m = np.zeros((h, w), bool)
        a, b, c, e = r
        m[max(0, int(b - y0 - d)):max(0, int(np.ceil(e - y0 + d))), max(0, int(a - x0 - d)):max(0, int(np.ceil(c - x0 + d)))] = True
        return m

    def cresce(cov, d):
        k = 2 * int(d) + 1
        return cv2.dilate(cov, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    pdf, caixas = [], []
    for peca in cam["pecas"]:
        cov = _living_pdf(Q, peca, x0, y0, w, h) * (1 - fixo)
        ys, xs = np.nonzero(cov > 0.01)
        pdf.append(cov)
        caixas.append((xs.min() + x0, ys.min() + y0, xs.max() + 1 + x0, ys.max() + 1 + y0))
    velho = np.zeros((h, w), bool)
    for p in pdf:
        velho |= cresce((p > 0.01).astype(np.uint8), 2) > 0
    velho &= fixo < 0.01
    # o fundo original limpo (sem as peças antigas)
    limpo = cv2.inpaint(np.clip(reg, 0, 255).astype(np.uint8), (cresce(velho.astype(np.uint8), 1) * 255).astype(np.uint8),
                        5, cv2.INPAINT_TELEA).astype(np.float32)
    # o ganho do fundo: piso e tapete fora de todas as peças do estar (e fora do jardim e da grelha de baixo)
    est = np.ones((h, w), bool)
    for c in q["camadas"]:
        for peca in c["pecas"]:
            cv_ = _living_pdf(Q, peca, x0, y0, w, h)
            if cv_.max() > 0:
                est &= ~(cresce((cv_ > 0.01).astype(np.uint8), 12) > 0)
    for r in q["fora_px"]:
        est &= ~ret(r, d=4)
    claro = est & (reg.mean(axis=2) > 150) & ((reg.max(axis=2) - reg.min(axis=2)) < 40)
    # sem tapete nem piso claro (os quartos de piso marrom): o piso todo fora das peças, sem as linhas escuras
    est = claro if claro.sum() >= 200 else est & (reg.mean(axis=2) > q["linha_lum"])
    g = np.clip(np.median(reg[est], axis=0) / np.maximum(np.median(ia[est], axis=0), 1), *q["ganho_lim"])
    iag = ia * g[None, None, :]
    # o que a IA desenhou como peça perto de cada silhueta: foge do fundo limpo em cor, ou é mais claro que ele (a
    # sombra, mais escura no mesmo tom, não é peça); só o que encosta na silhueta do PDF
    lab_i = cv2.cvtColor(np.clip(iag / 255, 0, 1), cv2.COLOR_BGR2LAB)
    lab_f = cv2.cvtColor(np.clip(limpo / 255, 0, 1), cv2.COLOR_BGR2LAB)
    dab = np.hypot(lab_i[..., 1] - lab_f[..., 1], lab_i[..., 2] - lab_f[..., 2])
    obj = (dab > q["peca_ab_min"]) | (lab_i[..., 0] - lab_f[..., 0] > q["peca_l_min"])
    # onde a peça da IA é menor que a silhueta do PDF (os cantos da cama junto à cabeceira e aos criados-mudos), a
    # silhueta pegaria o piso escuro ou a sombra da IA: nesses retângulos (`corta_px`, px do quadro) volta o fundo limpo
    cortado = np.zeros((h, w), bool)
    for r in cam.get("corta_px", ()):
        cortado |= ret(r)
    sil = []
    for p, r in zip(pdf, caixas):
        cov = cresce(p, q["cresce_px"]) * ~cortado
        oi = (obj & ~cortado & ret(r, d=q["perto_px"])).astype(np.uint8)
        oi = cv2.morphologyEx(oi, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8)) > 0
        nucleo = cov > 0.5
        lab, n = ndimage.label(oi | nucleo)
        oi &= np.isin(lab, np.unique(lab[nucleo]))
        sil.append(np.clip(cv2.GaussianBlur(np.maximum(cov, oi.astype(np.float32)), (0, 0), 0.6), 0, 1))
    peso = np.stack(sil).max(axis=0)
    # a sombra da IA em volta (só na camada que pede), esmaecendo até `sombra_px`
    if cam.get("sombra_px"):
        dist = cv2.distanceTransform((peso < 0.5).astype(np.uint8), cv2.DIST_L2, 3)
        anel = np.clip(1 - dist / cam["sombra_px"], 0, 1) ** 1.5
        peso = np.maximum(peso, anel)
    peso[cortado] = 0
    # as linhas escuras de fora das peças antigas (o caixilho do vidro, a parede) e o que as camadas anteriores puseram
    linha = ~velho & (reg.mean(axis=2) < q["linha_lum"]) & (peso < 0.99)
    peso[linha] = 0
    peso *= 1 - fixo
    # o que da peça antiga sobra fora da nova: o fundo limpo
    resto = velho & (peso < 0.5)
    base = np.where(resto[..., None], limpo, reg)
    o = base * (1 - peso[..., None]) + iag * peso[..., None]
    out = img.copy()
    out[y0:y1, x0:x1] = np.clip(np.round(o), 0, 255).astype(np.uint8)
    pg = np.zeros(feito.shape, np.float32)
    pg[y0:y1, x0:x1] = np.where(peso > 0.5, 1.0, 0.0)
    print(f"      {cam['nome']}: {len(pdf)} peça(s), ganho do fundo {[round(float(v), 3) for v in g]}, "
          f"{int(resto.sum())} px da peça antiga refeitos do fundo")
    return out, pg


def living_ia_tb(Q, img, q=LIVING_IA_TB):
    out = img.copy()
    feito = np.zeros(img.shape[:2], np.float32)
    for cam in q["camadas"]:
        out, pg = _living_camada(Q, out, cam, q, feito)
        feito = np.maximum(feito, pg)
    print(f"    estar do living: o sofá da opção A; a mesa lateral, a arandela, as 2 poltronas, a mesa de centro e o banco com "
          f"a sombra no estilo da opção B (Nano Banana Pro, nas silhuetas do PDF)")
    return out


# O estar da varanda, 2ª passada pela IA (usuário, sobre o sofá: "mantenha o realismo, mas corrija a posição do encosto e
# adicione o encosto para o outro lado também. Ao aplicar o realismo, não podemos alterar a composição e dimensões
# existentes no PDF base. A opção do sofá permite as pessoas ficarem sentadas tanto viradas para TV quanto para as mesas
# do gourmet"; e, sobre as duas poltronas terracota: "melhore o aspecto com mais realismo nessas poltronas"). Duas
# camadas do Nano Banana Pro, como as do living (`_living_camada`):
#   1. o sofá de dois lados (PDF 64428): o recorte foi à IA com o desenho do PDF do sofá ao lado, na mesma escala, de
#      referência: o encosto fino no meio dos dois módulos, as almofadas de encosto e os assentos dos dois lados (virados
#      para a TV e para as mesas do gourmet) e o módulo da direita, pufe inteiro, sem encosto; o contorno do PDF; a mesa
#      lateral de carvalho (66895) fica a de antes (`protege`);
#   2. as 2 poltronas giradas (66910, 67076): a concha terracota estofada e o assento off-white em bouclé, no giro e no
#      tamanho delas, com as poltronas do living de referência de tecido; a sombra curta da IA em volta.
ESTAR_VARANDA_TB = {"camadas": [
    {"nome": "sofá de dois lados da varanda", "ia_png": RENDERS / "ia" / "POE642_CasaB_Terreo_varanda_sofa2lados_nbp_alinhado.png",
     "caixa_px": (1180, 935, 1470, 1098), "pecas": [64428], "protege": [66895],
     # a tábua de madeira que a IA pôs no fim do assento de baixo do 2º módulo (não há no PDF): o assento e a fresta
     # atrás da almofada vêm do 1º módulo, 89 px à esquerda (a largura do módulo)
     "remendos_ia": [(1360, 1029, 1391, 1057, -89), (1385, 1000, 1391, 1029, -89)]},
    {"nome": "poltronas terracota da varanda", "ia_png": RENDERS / "ia" / "POE642_CasaB_Terreo_varanda_poltronas_nbp_alinhado.png",
     "caixa_px": (1380, 790, 1556, 1010), "pecas": [66910, 67076], "sombra_px": 5.0}],
    "cresce_px": 2, "perto_px": 3, "peca_ab_min": 7.0, "peca_l_min": 9.0, "ganho_lim": (0.92, 1.08), "linha_lum": 110,
    "fora_px": []}


def estar_varanda_tb(Q, img, q=ESTAR_VARANDA_TB):
    out = img.copy()
    feito = np.zeros(img.shape[:2], np.float32)
    for cam in q["camadas"]:
        out, pg = _living_camada(Q, out, cam, q, feito)
        feito = np.maximum(feito, pg)
    print("    estar da varanda: o sofá de dois lados pelo desenho do PDF e as 2 poltronas terracota realistas "
          "(Nano Banana Pro, nas silhuetas do PDF)")
    return out


# As camas pela IA (usuário: "altere as camas para camas mais realistas, mantendo o tom do jogo de cama. me apresente 2
# opções de camas, tanto para camas de casal quanto de solteiro para aprovar."; "gostei da cama com a cabeceira cinza e o
# jogo de cama com metalessa"; "já atualize o sofá na frente da cama de casal com realismo e os bancos/sofá onde tem,
# também, em frente as camas"; "na suíte 3, não há banco e nem sofá em frente a cama de casal"). A combinação aprovada (a
# cabeceira e a base estofadas em linho cinza claro da opção A; a colcha matelassê branca, as almofadas e a peseira de
# veludo bordô da opção B; sem estrutura de madeira) foi ao Nano Banana Pro quarto a quarto, com o recorte da planta e a
# combinação de referência, cada cama no lado da cabeceira do PDF; com ela, o que há aos pés da cama, em linho cinza
# claro/greige: o banco com 2 rolos da suíte master, o sofá de 2 lugares da suíte 1 (encosto à direita, assento para a
# cama) e os 2 bancos estofados da suíte 2. Cada camada alinhada ao seu recorte (`caixa_px`, `renders/ia/
# POE642_CasaB_Terreo_cama_<quarto>_nbp_alinhado.png`) e posta pelo `_living_camada` nas silhuetas do PDF, com a sombra
# curta da IA em volta; os criados-mudos ficam os de antes (`protege`).
CAMAS_TB = {"camadas": [
    {"nome": "suíte master: cama e banco aos pés", "ia_png": RENDERS / "ia" / "POE642_CasaB_Terreo_cama_master_nbp_alinhado.png",
     "caixa_px": (995, 575, 1215, 795), "pecas": [77941, 63289], "protege": [78321, 78337], "sombra_px": 4.0,
     # a cabeceira da IA (x 1049-1162) esticada na largura da cabeceira do PDF (1036-1175, atrás dos criados-mudos);
     # acima dela, entre a cama e os criados-mudos, o piso de antes (a IA pôs ali a sombra escura)
     "estica_ia": [(752, 765, 1049, 1162, 1036, 1175)],
     "corta_px": [(1034, 738, 1050, 752), (1161, 738, 1178, 752)]},
    {"nome": "suíte 1: cama e sofá aos pés", "ia_png": RENDERS / "ia" / "POE642_CasaB_Terreo_cama_s1_nbp_alinhado.png",
     "caixa_px": (1925, 362, 2140, 522), "pecas": [77600, 77674], "protege": [77620, 77647], "sombra_px": 4.0,
     # entre a cabeceira e os criados-mudos redondos a IA pôs o piso de madeira dela (o tapete do PDF começa antes)
     "corta_px": [(1944, 379, 1983, 384), (1944, 499, 1983, 506)]},
    {"nome": "suíte 2: 2 camas de solteiro e os bancos aos pés",
     "ia_png": RENDERS / "ia" / "POE642_CasaB_Terreo_cama_s2_nbp_alinhado.png",
     "caixa_px": (2368, 333, 2552, 563), "pecas": [77500, 77520, 71845, 71850], "protege": [71840], "sombra_px": 4.0},
    {"nome": "suíte 3: cama (sem banco nem sofá)", "ia_png": RENDERS / "ia" / "POE642_CasaB_Terreo_cama_s3_nbp_alinhado.png",
     "caixa_px": (2440, 692, 2600, 852), "pecas": [77560], "sombra_px": 4.0},
    {"nome": "quarto de serviço: cama", "ia_png": RENDERS / "ia" / "POE642_CasaB_Terreo_cama_serv_nbp_alinhado.png",
     "caixa_px": (1900, 1590, 2050, 1674), "pecas": [77881], "sombra_px": 4.0},
    {"nome": "quarto do motorista: cama", "ia_png": RENDERS / "ia" / "POE642_CasaB_Terreo_cama_mot_nbp_alinhado.png",
     "caixa_px": (2832, 1372, 2986, 1458), "pecas": [77921], "protege": [63266], "sombra_px": 4.0}],
    "cresce_px": 2, "perto_px": 3, "peca_ab_min": 7.0, "peca_l_min": 9.0, "ganho_lim": (0.92, 1.08), "linha_lum": 110,
    "fora_px": []}


def camas_ia_tb(Q, img, q=CAMAS_TB):
    out = img.copy()
    feito = np.zeros(img.shape[:2], np.float32)
    for cam in q["camadas"]:
        out, pg = _living_camada(Q, out, cam, q, feito)
        feito = np.maximum(feito, pg)
    print("    camas: cabeceira estofada cinza e colcha matelassê com o bordô em todas as camas, e o banco e o sofá aos "
          "pés das camas realistas (Nano Banana Pro, nas silhuetas do PDF)")
    return out


# As poltronas da varanda (usuário: "ainda está diferente do que eu esperava. segue o que eu espero dessas poltronas",
# com as poltronas de concha terracota e assento branco, de frente e a 45°): as duas poltronas da direita do estar da
# varanda, que a IA fez inteiras em creme, saem no modelo das poltronas do living (a concha do encosto e dos braços em
# terracota, o assento branco): a poltrona do living (`modelo_pdf`, a silhueta do PDF) é recortada da própria planta,
# girada e escalada até cobrir a silhueta do PDF de cada poltrona da varanda (o giro de maior sobreposição) e posta no
# lugar dela, 1 px maior na beira (sem sobrar o creme da IA); a sombra curta da IA em volta fica.
POLTRONAS_VAR_TB = {"modelo_pdf": 64047, "alvos_pdf": [66910, 67076], "passo_grau": 3}


def _silhueta_pdf(Q, i, ss=4):
    dd = Q.desenhos[i]
    return Q.preencher(lambda d, dd=dd: d is dd, ss=ss).astype(np.float32)


def poltronas_varanda_tb(Q, img, q=POLTRONAS_VAR_TB):
    H, W = img.shape[:2]
    am = _silhueta_pdf(Q, q["modelo_pdf"])
    ys, xs = np.nonzero(am > 0.01)
    x0, y0, x1, y1 = xs.min() - 2, ys.min() - 2, xs.max() + 3, ys.max() + 3
    a_s = am[y0:y1, x0:x1]
    c_s = img[y0:y1, x0:x1].astype(np.float32)
    # a cor da beira: a do px de dentro mais perto (sem o fundo misturado)
    dentro = a_s > 0.9
    _, (iy, ix) = ndimage.distance_transform_edt(~dentro, return_indices=True)
    c_s = c_s[iy, ix]
    hs, ws = a_s.shape
    cys, cxs = ndimage.center_of_mass(a_s)
    out = img.astype(np.float32)
    feitos = []
    for i in q["alvos_pdf"]:
        at = _silhueta_pdf(Q, i)
        cyt, cxt = ndimage.center_of_mass(at)
        esc = float(np.sqrt(at.sum() / a_s.sum()))

        def pos(ang):
            M = cv2.getRotationMatrix2D((cxs, cys), ang, esc)
            M[0, 2] += cxt - cxs
            M[1, 2] += cyt - cys
            return M

        def iou(ang):
            r = cv2.warpAffine(a_s, pos(ang), (W, H), flags=cv2.INTER_LINEAR)
            return float(np.minimum(r, at).sum() / max(np.maximum(r, at).sum(), 1e-6))
        angs = np.arange(0, 360, q["passo_grau"])
        melhor = max(angs, key=iou)
        finos = np.arange(melhor - q["passo_grau"], melhor + q["passo_grau"] + 0.01, 0.5)
        melhor = max(finos, key=iou)
        M = pos(melhor)
        a_r = cv2.warpAffine(a_s, M, (W, H), flags=cv2.INTER_LINEAR)
        c_r = cv2.warpAffine(c_s, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        a_r = np.clip(cv2.dilate(a_r, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))), 0, 1)[..., None]
        out = out * (1 - a_r) + c_r * a_r
        feitos.append((i, round(float(melhor), 1), round(iou(melhor), 3)))
    out = np.clip(np.round(out), 0, 255).astype(np.uint8)
    print(f"    poltronas da varanda: as 2 no modelo das poltronas do living (concha terracota, assento branco), "
          f"giradas pela silhueta do PDF {[(g, f'IoU {v}') for _, g, v in feitos]}")
    return out


# Os brises junto ao jardim de 4,62 m² (usuário: "corrija os brises"): as 11 lâminas giradas da ARQ_ELEMENTOS FIXOS
# tinham virado divisas escuras borradas, com o tracejado do pergolado por cima. A faixa entre o jardim e o piso da
# garagem é refeita (as lâminas velhas e os restos escuros saem, `caixa_px`), o tracejado do pergolado volta só nela, e
# as lâminas entram desenhadas como em `final3840_casab.brises` (alumínio grafite, a aresta da luz, o contorno fino e a
# sombra curta).
BRISES_TB = {"caixa_px": (2342, 1279, 2574, 1297), "escuro_lum": 135, "cresce_px": 2}


def brises_tb(Q, img, q=BRISES_TB):
    import final3840_casaa_terreo as FT
    x0, y0, x1, y1 = q["caixa_px"]
    H, W = img.shape[:2]
    ds = F.brises_pdf(Q)
    lam = np.zeros((H, W), np.uint8)
    for d in ds:
        for c in Q.caminhos(d):
            if len(c) >= 3:
                cv2.fillPoly(lam, [np.int32(np.round(c))], 1)
    k = 2 * q["cresce_px"] + 1
    lam = cv2.dilate(lam, np.ones((k, k), np.uint8)) > 0
    caixa = np.zeros((H, W), bool)
    caixa[y0:y1, x0:x1] = True
    escuro = img.astype(np.float32).mean(axis=2) < q["escuro_lum"]
    buraco = caixa & (lam | escuro)
    buraco = cv2.dilate(buraco.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    buraco &= caixa
    out = cv2.inpaint(img, buraco.astype(np.uint8), 4, cv2.INPAINT_TELEA)
    # o tracejado do pergolado, de novo, só na faixa
    segs = _segs_pergolado(Q)
    pq = dict(FT.PROJ, larg_px=PERGOLADO_TB["larg_px"], preto=PERGOLADO_TB["cor"], branco=PERGOLADO_TB["cor"])
    com, _ = FT.preto_branco(Q, out, segs, pq)
    out[buraco] = com[buraco]
    out = np.clip(np.round(F.brises(Q, out, ds)), 0, 255).astype(np.uint8)
    print(f"    brises: {len(ds)} lâminas do PDF redesenhadas (grafite, aresta de luz, contorno fino, sombra curta); "
          f"{int(buraco.sum())} px da faixa refeitos, com o tracejado do pergolado de volta")
    return out


# A prateleira da despensa (usuário: "corrija o erro na prateleira da despensa"): o dente claro da prateleira da direita
# sobre o piso (e a linha da beira da prateleira interrompida ali) sai: o trecho (`dente_px`) vem das mesmas colunas
# `dy` px acima, onde o piso e a beira estão inteiros.
DESPENSA_TB = {"dente_px": (2006, 1417, 2022, 1432), "dy": -14}


def despensa_tb(Q, img, q=DESPENSA_TB):
    x0, y0, x1, y1 = q["dente_px"]
    dy = q["dy"]
    out = img.copy()
    src = img[y0 + dy:y1 + dy, x0:x1].astype(np.float32)
    h, w = y1 - y0, x1 - x0
    a = np.ones((h, w), np.float32)
    for k in range(2):                                   # 2 px de transição em cima e embaixo
        a[k, :] = a[h - 1 - k, :] = (k + 1) / 3
    reg = img[y0:y1, x0:x1].astype(np.float32)
    out[y0:y1, x0:x1] = np.clip(np.round(reg * (1 - a[..., None]) + src * a[..., None]), 0, 255).astype(np.uint8)
    print(f"    despensa: o dente da prateleira da direita refeito ({w} x {h} px)")
    return out


# Os pontos estranhos (usuário: "remova o ponto preto. o ponto de interrogação significa algo estranho a ser
# deletado", com o recorte do chuveiro do banho master): o puxador escuro da porta de vidro do box, que saía 5 px para
# o piso como um ponto preto e cortava a dobradiça branca; o trecho vem das mesmas colunas `dy` px acima.
# E (usuário: "remova o vestígio da cuba referente ao tracejado branco, bem na lateral. esse erro precisa sair"): na
# cuba da pia gourmet, a aba branca saindo da borda da direita (o resto do tracejado branco do armário) e o risco branco
# que cruzava a borda: a borda vertical vem da linha limpa `linha` (a mesma nas colunas da borda) e o granito ao lado,
# de `dy` px abaixo.
PONTOS_TB = {"remendos": [{"nome": "puxador do box do banho master", "px": (1542, 395, 1558, 400), "dy": -6},
                          {"nome": "aba branca da cuba da pia gourmet (borda)", "px": (1399, 1497, 1404, 1512),
                           "linha": 1513},
                          {"nome": "aba branca da cuba da pia gourmet (granito)", "px": (1404, 1497, 1409, 1512),
                           "dy": 14},
                          # (usuário: "desse banho gourmet, remova o ponto preto ... está dentro do box à direita"): o
                          # botão escuro do registro do chuveiro do BH gourmet da esquerda; o piso de 9 px acima e a
                          # beira do registro da linha limpa logo acima do botão
                          {"nome": "botão escuro do registro do BH gourmet da esquerda (piso)", "px": (1203, 1633, 1208, 1641),
                           "dy": -9},
                          {"nome": "botão escuro do registro do BH gourmet da esquerda (beira)", "px": (1208, 1633, 1212, 1641),
                           "linha": 1631},
                          # (usuário: "volte o registro da ducha à direita. deve ficar igual ao registro do lado
                          # esquerdo"): o registro da ducha da direita do banho master vira o espelho do da esquerda (a
                          # barra creme junto à parede e o botão para dentro do box); x da direita = `espelho_x` - x
                          {"nome": "registro da ducha da direita do banho master (espelho do da esquerda)",
                           "px": (1546, 378, 1558, 417), "espelho_x": 2797}]}


def pontos_tb(Q, img, q=PONTOS_TB):
    out = img.copy()
    for r in q["remendos"]:
        x0, y0, x1, y1 = r["px"]
        if "linha" in r:
            out[y0:y1, x0:x1] = img[r["linha"], x0:x1][None, :, :]
        elif "espelho_x" in r:
            xs = r["espelho_x"] - np.arange(x0, x1)
            out[y0:y1, x0:x1] = img[y0:y1][:, xs]
        else:
            out[y0:y1, x0:x1] = img[y0 + r["dy"]:y1 + r["dy"], x0:x1]
    print(f"    pontos: {', '.join(r['nome'] for r in q['remendos'])} fora")
    return out


# As pedras do acesso (usuário: "corrija os contornos das pedras", com o recorte dos pisantes da entrada sobre a grama):
# as 9 pedras tinham a beira serrilhada (degraus de 1 px, o dente no canto da primeira). Cada uma volta como o
# retângulo do PDF (ARQ_CONTRAPISO, px), com a cobertura subpixel na beira (antisserrilhada), o miolo dela mesma
# (`inset_px` para dentro, rebatido até a beira) e o aro fino da Casa A (`terreo_casaa_1011`, `R_PEDRAS`: 0,86 no 1º px
# e 0,95 no 2º); em volta, os px claros que sobravam na grama (até `anel_px`) viram a grama mais perto, para fora.
# Topo e base iguais nas 9 (a fiada alinhada).
PEDRAS_TB = {"rets_px": [(2709.19, 2950.14), (2959.59, 3019.43), (3028.97, 3088.81), (3097.28, 3157.12),
                         (3167.18, 3227.55), (3235.49, 3296.39), (3304.75, 3363.98), (3373.78, 3433.84),
                         (3442.65, 3502.6)],
             "y_px": (973.4, 1152.5), "inset_px": 4, "aro": (0.86, 0.95), "anel_px": 4, "busca_px": 12}


def pedras_tb(Q, img, q=PEDRAS_TB):
    import terreo_casaa_1011 as TC
    import um_pav_casaa_1111 as U
    H, W = img.shape[:2]
    out = img.copy()
    y0, y1 = q["y_px"]
    ins = q["inset_px"]
    # 1. a grama em volta sem os restos claros da beira velha (a grama mais perto, para fora)
    pedra = np.zeros((H, W), bool)
    for x0, x1 in q["rets_px"]:
        pedra[int(np.ceil(y0)):int(np.floor(y1)), int(np.ceil(x0)):int(np.floor(x1))] = True
    an, R = q["anel_px"], q["busca_px"]
    grama = TC._grama_px(img)
    zona = dilatar(pedra, an + 1) & ~pedra & ~grama
    ys, xs = np.nonzero(zona)
    trocados = 0
    for y, x in zip(ys, xs):
        # a direção para fora: da pedra mais perto
        dx = dy = 0
        for x0, x1 in q["rets_px"]:
            if x0 - an - 2 <= x <= x1 + an + 2:
                dx = -1 if x < x0 else (1 if x > x1 else 0)
                dy = -1 if y < y0 else (1 if y > y1 else 0)
                if dx or dy:
                    break
        if not (dx or dy):
            continue
        for k in range(1, R + 1):
            yy, xx = y + dy * k, x + dx * k
            if 0 <= yy < H and 0 <= xx < W and not pedra[yy, xx] and grama[yy, xx] and not zona[yy, xx]:
                out[y, x] = img[yy, xx]
                trocados += 1
                break
    # 2. cada pedra: o miolo dela rebatido até a beira, o aro fino e a cobertura subpixel do retângulo
    of = out.astype(np.float32)
    for x0, x1 in q["rets_px"]:
        X0, Y0 = int(np.floor(x0)) - 1, int(np.floor(y0)) - 1
        X1, Y1 = int(np.ceil(x1)) + 1, int(np.ceil(y1)) + 1
        mx0, my0 = int(np.ceil(x0)) + ins, int(np.ceil(y0)) + ins
        mx1, my1 = int(np.floor(x1)) - ins, int(np.floor(y1)) - ins
        miolo = img[my0:my1, mx0:mx1].astype(np.float32)
        tex = cv2.copyMakeBorder(miolo, my0 - Y0, Y1 - my1, mx0 - X0, X1 - mx1, cv2.BORDER_REFLECT)
        yy, xx = np.mgrid[Y0:Y1, X0:X1].astype(np.float32) + 0.5
        d = np.minimum.reduce([xx - x0, x1 - xx, yy - y0, y1 - yy])          # px até a beira (dentro > 0)
        c0, c1 = q["aro"]
        aro = np.where(d < 1, c0, np.where(d < 2, c0 + (c1 - c0) * (d - 1), np.where(d < 3, c1 + (1 - c1) * (d - 2), 1)))
        tex *= aro[..., None]
        a = U._cobertura((x0, y0, x1, y1), X0, Y0, X1 - X0, Y1 - Y0)[..., None]
        of[Y0:Y1, X0:X1] = of[Y0:Y1, X0:X1] * (1 - a) + tex * a
    out = np.clip(np.round(of), 0, 255).astype(np.uint8)
    print(f"    pedras do acesso: {len(q['rets_px'])} retângulos do PDF com a beira antisserrilhada e o aro fino da "
          f"Casa A (topo e base alinhados); {trocados} px claros da beira velha viram grama")
    return out


# Os rótulos (usuário: "centralize todos os rótulos e deixe-os alinhados"; "deixe os rótulos alinhados", com os
# recortes): cada rótulo atual é achado na imagem (o desenho dele na fonte da prancha, `retoque_1pav_casae.
# rotulos_ambientes`, em cada corpo e quebra, casado por correlação com o mapa do texto escuro ou claro, ±`busca_px` do
# ponto do PDF) e sai com o piso de baixo (`terreo_casaa_1011._tapar_rotulo`, linha a linha, do mesmo piso ao lado),
# junto com os pontinhos soltos em volta dele (os restos de texto de até `resto_area` px, como o "'" antes do "A:");
# volta no meio do piso livre do ambiente (o recinto do PDF, fechado pelas esquadrias, sem os objetos das camadas de
# obstáculo, com `margem_px`), no corpo da regra (onde não cabe livre, cai a 0,85 e a 0,72); os ambientes da mesma faixa
# (`alinhar`) ficam com o meio do texto na mesma altura (a mediana dos meios), quando ali o texto cabe livre. A cor, preta
# ou branca pelo fundo. Ficam os da água, os dos jardins e o ELEVADOR (`manter`); `centros`: o meio pedido (px).
ROTULOS_TB = {"manter": ("SPA", "PISCINA", "PRAINHA", "JARDIM DE INVERNO", "JARDIM", "ELEVADOR"),
              "busca_px": 260, "margem_px": 4, "raio_px": 70, "corpos": (1.0, 0.85, 0.72, 0.62), "resto_area": 8,
              "alinhar": [("BANHO MASTER", "BANHO 1", "BANHO 2"), ("SUÍTE MASTER", "SUÍTE 1", "SUÍTE 2"),
                          ("SALA ÍNTIMA", "CIRCULAÇÃO"), ("LIVING/JANTAR", "HALL INTERNO", "HALL", "VARANDA/GOURMET"),
                          ("LOUCEIRO", "DESPENSA", "ÁREA DE SERVIÇO"), ("BH SERVIÇO", "QUARTO SERVIÇO"),
                          ("BANHO GOURMET", "LAVATÓRIO GOURMET")],
              # as colunas (o meio do texto na mesma vertical)
              "alinhar_x": [("DEPÓSITO", "QUARTO MOTORISTA", "BH MOTORISTA")],
              "centros": {},
              # a faixa fica na altura (ou no eixo) deste rótulo, que não sai do lugar (usuário: "alinhe sala intima com
              # circulação": a CIRCULAÇÃO no meio do corredor, a SALA ÍNTIMA desce até ela)
              "ancoras": ("CIRCULAÇÃO",),
              # onde o ambiente é apertado demais para o corpo da faixa: fica no lugar e no corpo achados (só a cor
              # refeita pelo piso novo)
              "no_lugar": ("BH SERVIÇO",),
              # o meio pedido (px) e, se preciso, o corpo e a cor; a altura é a da faixa (usuário: "coloque o rótulo da
              # varanda/gourmet mais a direita sem ficar na sombra do sofá, mas alinhado com o rótulo do living": entre a
              # sombra do sofá, em x 1446, e a linha da varanda, em x 1553, cabe a 0,92; "corrija o rótulo do louceiro
              # para cor branca e centralizado": no meio do piso marrom, entre a prateleira e a parede)
              # (usuário: "suba mais esse rótulo", o da COZINHA): no meio do piso livre acima da ilha, no eixo da cozinha
              "fixos": {"VARANDA/GOURMET": {"cx": 1498.5, "corpo": 0.92}, "LOUCEIRO": {"cx": 1897.5, "cor": (255, 255, 255)},
                        "COZINHA": {"cx": 1692.0, "fundo": 1354.0}},
              # os ambientes abertos para o terreno (o recinto do PDF vaza): o piso livre nesta caixa (px)
              "recorte_px": {"DECK": (667, 1380, 1094, 1702), "HALL": (2545, 945, 2705, 1180),
                             "GARAGEM": (2390, 1296, 2850, 1366)}}


def _rotulo_alfa(Q, r1, opc, desvio=(0.0, 0.0)):
    import retoque_1pav_casae as R1
    esc = Q.W / 2000
    nome = r1[0]
    cx, cy = Q.p2q(*r1[2])
    tela = np.full((Q.H, Q.W, 3), 128, np.uint8)
    aj = [(nome, (cx / esc, cy / esc), (desvio[0] / esc, desvio[1] / esc), dict(opc, cor=(0, 0, 0)))]
    t = R1.rotulos_ambientes(tela, [r1], Q.p2q, escala_desvio=esc, granito=None, ajustes=aj, halo=None)
    return np.clip((128 - t.astype(np.float32).mean(axis=2)) / 128, 0, 1)


def _achar_rotulos(Q, img, rot, q):
    import retoque_1pav_casae as R1
    L = img.astype(np.float32).mean(axis=2)
    med = cv2.medianBlur(img, 9).astype(np.float32).mean(axis=2)
    mapas = {"escuro": np.clip((med - L) / 60, 0, 1).astype(np.float32),
             "claro": np.clip((L - med) / 60, 0, 1).astype(np.float32)}
    base = R1.ROTULOS["escala"]
    achados = []
    for r1 in rot:
        palavras = r1[1][0][0].split()
        cands = []
        for f in (1.0, 0.9, 0.85, 0.8, 0.72, 0.62):
            cands.append({"corpo": base * f})
            if len(palavras) >= 2:
                meio = (len(palavras) + 1) // 2
                cands.append({"corpo": base * f, "quebra": [" ".join(palavras[:meio]), " ".join(palavras[meio:])]})
        melhor = None
        for opc in cands:
            a = _rotulo_alfa(Q, r1, opc)
            ys, xs = np.nonzero(a > 0.05)
            x0, y0, x1, y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
            T = a[y0:y1, x0:x1].astype(np.float32)
            R = q["busca_px"]
            sx0, sy0, sx1, sy1 = max(0, x0 - R), max(0, y0 - R), min(Q.W, x1 + R), min(Q.H, y1 + R)
            for nm, M in mapas.items():
                sc = cv2.matchTemplate(M[sy0:sy1, sx0:sx1], T, cv2.TM_CCORR_NORMED)
                _, v, _, loc = cv2.minMaxLoc(sc)
                if melhor is None or v > melhor[0]:
                    melhor = (v, nm, opc, (sx0 + loc[0] - x0, sy0 + loc[1] - y0))
        v, nm, opc, (dx, dy) = melhor
        alfa = _rotulo_alfa(Q, r1, opc, (dx, dy))
        achados.append({"r1": r1, "nota": v, "tom": nm, "opc": opc, "alfa": alfa, "desvio": (dx, dy)})
    return achados


def rotulos_tb(Q, img, q=ROTULOS_TB):
    import retoque_1pav_casae as R1
    import terreo_casaa_1011 as TC
    rf = F.ROTULOS_F
    rot = F.textos_rotulos(F.B.rotulos_casab(Q.pg, Q.p2q2000))
    rot = [r for r in rot if r[0] not in q["manter"]]
    achados = _achar_rotulos(Q, img, rot, q)
    out = img.copy()
    # 1. os rótulos saem (com os pontinhos soltos em volta)
    L = img.astype(np.float32).mean(axis=2)
    med = cv2.medianBlur(img, 9).astype(np.float32).mean(axis=2)
    marca = np.abs(med - L) > 30
    texto = np.zeros(L.shape, bool)
    for a in achados:
        m = a["alfa"] > 0.03
        ys, xs = np.nonzero(m)
        caixa = np.zeros(L.shape, bool)
        caixa[ys.min() - 5:ys.max() + 6, xs.min() - 5:xs.max() + 6] = True
        n, lab, st, _ = cv2.connectedComponentsWithStats((marca & caixa & ~m).astype(np.uint8), 8)
        restos = np.isin(lab, [i for i in range(1, n) if st[i, 4] <= q["resto_area"]])
        texto |= dilatar(m, 1) | dilatar(restos, 1)
    moveis = Q.preencher(lambda d: d.get("layer") in rf["obstaculos"] and d.get("layer") != "ARQ_PAREDE", ss=2) > 0.05
    par = Q.preencher(lambda d: d.get("layer") in ("ARQ_PAREDE", "EST_PILAR") and d.get("fill")
                      and max(d["fill"]) < 0.6, ss=2) > 0.3
    proibido = dilatar(texto, 2) | moveis | par
    with contextlib.redirect_stdout(io.StringIO()):
        out, _ = TC._tapar_rotulo(out, texto & ~par, proibido, Q.chapada, TC.ROTULOS_1111)
    # 2. o meio do piso livre de cada ambiente
    busca = []
    for a in achados:
        ys, xs = np.nonzero(a["alfa"] > 0.03)
        busca.append(((xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2))
    amb = F.ambientes_rotulos(Q, busca, todas=True)
    obst = Q.preencher(lambda d: d.get("layer") in rf["obstaculos"], ss=2, fs=True) > 0.05
    tr = np.zeros(obst.shape, np.uint8)
    for d in Q.desenhos:
        if d.get("layer") in rf["obstaculos"] and d.get("layer") != "ARQ_PAREDE" and d["type"] == "s":
            for c in Q.caminhos(d):
                cv2.polylines(tr, [np.int32(np.round(c))], False, 1, 2)
    obst |= tr.astype(bool)
    for r in F.TERREO["carros_pt"]:
        x0_, y0_, x1_, y1_ = F.ret_q(Q, r)
        obst[y0_:y1_ + 1, x0_:x1_ + 1] = True
    k = 2 * q["margem_px"] + 1
    obst = cv2.dilate(obst.astype(np.uint8), np.ones((k, k), np.uint8)) > 0
    I_obst = cv2.integral(obst.astype(np.uint8))

    def soma(I, a0, b0, a1, b1):
        a0, b0, a1, b1 = max(a0, 0), max(b0, 0), min(a1, Q.W), min(b1, Q.H)
        return int(I[b1, a1] - I[b0, a1] - I[b1, a0] + I[b0, a0])
    base = R1.ROTULOS["escala"]
    planos = []
    for i, a in enumerate(achados):
        r1 = a["r1"]
        nome = r1[0]
        reg = amb == i + 1
        rc = q["recorte_px"].get(nome)
        if rc is not None:
            reg = np.zeros_like(reg)
            reg[rc[1]:rc[3], rc[0]:rc[2]] = True
            reg &= ~par
        livre = reg & ~obst
        if livre.sum() < 50:
            livre = reg
        ry, rx = np.nonzero(livre)
        tx, ty = (q["centros"][nome] if nome in q["centros"] else (rx.mean(), ry.mean()))
        planos.append({"i": i, "nome": nome, "reg": reg, "alvo": (float(tx), float(ty))})
    # 3. a caixa do texto de cada um em cada corpo (relativa ao ponto do PDF) e o teste de lugar livre
    caixas = {}

    def caixa(k_, fc):
        if (k_, fc) not in caixas:
            r1 = achados[k_]["r1"]
            quebra = {kk: vv for kk, vv in achados[k_]["opc"].items() if kk == "quebra"}
            opc = dict(quebra, corpo=base * fc)
            a0_ = _rotulo_alfa(Q, r1, opc)
            ys, xs = np.nonzero(a0_ > 0.05)
            caixas[(k_, fc)] = (opc, xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
        return caixas[(k_, fc)]

    def cabe(p_, fc, tx, fundo, eixo, raio):
        """O canto (x0, y0) da caixa livre mais perto de (tx, fundo) (fundo: a linha de baixo do texto), andando só no
        `eixo` (None: em volta)."""
        opc, bx0, by0, bx1, by1 = caixa(p_["i"], fc)
        w, h = bx1 - bx0, by1 - by0
        I_reg = p_["I_reg"]
        for rr in range(0, raio + 1):
            if eixo == "x":
                anel = [(0, 0)] if rr == 0 else [(rr, 0), (-rr, 0)]
            elif eixo == "y":
                anel = [(0, 0)] if rr == 0 else [(0, rr), (0, -rr)]
            else:
                anel = [(0, 0)] if rr == 0 else [(int(round(rr * np.cos(t))), int(round(rr * np.sin(t))))
                                                 for t in np.linspace(0, 2 * np.pi, max(8, int(2 * np.pi * rr)),
                                                                      endpoint=False)]
            for ox, oy in anel:
                x0_, y0_ = int(round(tx - w / 2 + ox)), int(round(fundo - h + oy))
                if soma(I_obst, x0_, y0_, x0_ + w, y0_ + h) == 0 and \
                        w * h - soma(I_reg, x0_, y0_, x0_ + w, y0_ + h) == 0:
                    return x0_, y0_
        return None
    for p_ in planos:
        p_["I_reg"] = cv2.integral(p_["reg"].astype(np.uint8))
        _, _, by0, _, by1 = caixa(p_["i"], 1.0)
        p_["fundo"] = p_["alvo"][1] + (by1 - by0) / 2              # a linha de baixo do texto no meio do piso livre
    # 4. as faixas: a altura (ou a vertical) em que mais rótulos cabem livres, no corpo da regra
    for grupo, eixo in [(g_, "x") for g_ in q["alinhar"]] + [(g_, "y") for g_ in q.get("alinhar_x", [])]:
        ps = [p_ for p_ in planos if p_["nome"] in grupo and p_["nome"] not in q.get("no_lugar", ())]
        if len(ps) < 2:
            continue
        if eixo == "x":
            vals = [p_["fundo"] for p_ in ps]
        else:
            vals = [p_["alvo"][0] for p_ in ps]
        med = float(np.median(vals))
        anc = [p_ for p_ in ps if p_["nome"] in q.get("ancoras", ())]
        if anc:
            med = anc[0]["fundo"] if eixo == "x" else anc[0]["alvo"][0]
        melhor = None
        for v in np.arange(min(vals) - 10, max(vals) + 11, 1.0):
            n_ok = sum(1 for p_ in ps if cabe(p_, 1.0, p_["alvo"][0] if eixo == "x" else v,
                                              v if eixo == "x" else p_["fundo"], eixo, q["raio_px"]) is not None)
            nota = (n_ok, -abs(v - med))
            if melhor is None or nota > melhor[0]:
                melhor = (nota, v)
        for p_ in ps:
            p_["alinhado"] = (p_["alvo"][0], melhor[1]) if eixo == "x" else (melhor[1], p_["fundo"])
            p_["eixo"] = eixo
    # 5. o desenho: no corpo da regra, na faixa (ou no meio do piso livre, ou no livre mais perto dele)
    for p_ in planos:
        r1 = achados[p_["i"]]["r1"]
        if p_["nome"] in q.get("fixos", {}):
            fx_ = q["fixos"][p_["nome"]]
            fc = fx_.get("corpo", 1.0)
            opc, bx0, by0, bx1, by1 = caixa(p_["i"], fc)
            fundo = fx_.get("fundo") or (p_["alinhado"][1] if p_.get("eixo") == "x" else p_["fundo"])
            x0_, y0_ = int(round(fx_["cx"] - (bx1 - bx0) / 2)), int(round(fundo - (by1 - by0)))
            dx, dy = x0_ - bx0, y0_ - by0
            cor = fx_.get("cor") or F.cor_do_fundo(out, x0_, y0_, x0_ + bx1 - bx0, y0_ + by1 - by0)
            esc = Q.W / 2000
            cx, cy = Q.p2q(*r1[2])
            out = R1.rotulos_ambientes(out, [r1], Q.p2q, escala_desvio=esc, granito=None,
                                       ajustes=[(r1[0], (cx / esc, cy / esc), (dx / esc, dy / esc), dict(opc, cor=cor))],
                                       halo=None)
            print(f"      {r1[0]}: fixo, caixa ({x0_}, {y0_})-({x0_ + bx1 - bx0}, {y0_ + by1 - by0}), corpo {fc}")
            continue
        if p_["nome"] in q.get("no_lugar", ()):
            a_ = achados[p_["i"]]
            ys, xs = np.nonzero(a_["alfa"] > 0.05)
            cor = F.cor_do_fundo(out, xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
            esc = Q.W / 2000
            cx, cy = Q.p2q(*r1[2])
            dx, dy = a_["desvio"]
            out = R1.rotulos_ambientes(out, [r1], Q.p2q, escala_desvio=esc, granito=None,
                                       ajustes=[(r1[0], (cx / esc, cy / esc), (dx / esc, dy / esc),
                                                 dict(a_["opc"], cor=cor))], halo=None)
            print(f"      {r1[0]}: no lugar achado ({xs.min()}, {ys.min()})-({xs.max() + 1}, {ys.max() + 1}), "
                  f"corpo {a_['opc']['corpo'] / base:.2f}")
            continue
        res = None
        for fc in q["corpos"]:
            tentativas = ([(p_["alinhado"], p_["eixo"])] if "alinhado" in p_ else []) + [((p_["alvo"][0], p_["fundo"]), None)]
            for (tx, fundo), eixo in tentativas:
                c_ = cabe(p_, fc, tx, fundo, eixo, q["raio_px"])
                if c_:
                    res = (fc, c_, eixo)
                    break
            if res:
                break
        if res is None:                                      # sem lugar livre: na faixa (ou no meio), no corpo da regra
            opc, bx0, by0, bx1, by1 = caixa(p_["i"], q["corpos"][0])
            tx, fundo = p_.get("alinhado", (p_["alvo"][0], p_["fundo"]))
            res = (q["corpos"][0], (int(round(tx - (bx1 - bx0) / 2)), int(round(fundo - (by1 - by0)))), "?")
        fc, (x0_, y0_), eixo = res
        opc, bx0, by0, bx1, by1 = caixa(p_["i"], fc)
        dx, dy = x0_ - bx0, y0_ - by0
        cor = F.cor_do_fundo(out, x0_, y0_, x0_ + bx1 - bx0, y0_ + by1 - by0)
        esc = Q.W / 2000
        cx, cy = Q.p2q(*r1[2])
        out = R1.rotulos_ambientes(out, [r1], Q.p2q, escala_desvio=esc, granito=None,
                                   ajustes=[(r1[0], (cx / esc, cy / esc), (dx / esc, dy / esc), dict(opc, cor=cor))],
                                   halo=None)
        print(f"      {r1[0]}: achado (nota {achados[p_['i']]['nota']:.2f}); caixa ({x0_}, {y0_})-({x0_ + bx1 - bx0}, "
              f"{y0_ + by1 - by0}), corpo {fc}" + {"x": ", na faixa", "y": ", na coluna", "?": ", sem lugar livre",
                                                   None: ""}[eixo])
    print(f"    rótulos: {len(achados)} no meio do piso livre, alinhados por faixa ({len(q['alinhar'])} faixas)")
    return out


# A cozinha, depois dos rótulos (usuário: "corrija esses erros na bancada da cozinha"; "suba mais esse rótulo e corrija o
# erro na bancada da ilha da cozinha"): (1) a beira esquerda da perna vertical da bancada em L (PDF 24219, x 1786,2, de
# y 1552,7 a 1630,3) tinha o tracejado do armário antigo: o piso marrom vem das colunas `piso_dx` px à esquerda, a
# bancada das `bancada_dx` px à direita, e a coluna da beira é a mistura das duas na cobertura do PDF; (2) a mancha clara
# à direita da ilha, junto ao rótulo antigo da COZINHA (o remendo do rótulo puxou a pedra da ilha para o piso): a faixa
# vem de `dy` px abaixo, com a beira da ilha.
BANCADA_COZINHA_TB = {"beira_x": 1786.2, "beira_y": (1553, 1630), "piso_cols": (1782, 1786), "bancada_cols": (1787, 1791),
              "piso_dx": -7, "bancada_dx": 6,
              "remendos": [{"nome": "mancha clara à direita da ilha", "px": (1715, 1391, 1723, 1413), "dy": 24}]}


def bancada_cozinha_tb(Q, img, q=BANCADA_COZINHA_TB):
    out = img.copy()
    y0, y1 = q["beira_y"]
    a0, a1 = q["piso_cols"]
    b0, b1 = q["bancada_cols"]
    out[y0:y1, a0:a1] = img[y0:y1, a0 + q["piso_dx"]:a1 + q["piso_dx"]]
    out[y0:y1, b0:b1] = img[y0:y1, b0 + q["bancada_dx"]:b1 + q["bancada_dx"]]
    xb = int(np.floor(q["beira_x"]))
    c = 1 - (q["beira_x"] - xb)
    mist = (1 - c) * img[y0:y1, xb + q["piso_dx"]].astype(np.float32) + c * img[y0:y1, xb + q["bancada_dx"]].astype(np.float32)
    out[y0:y1, xb] = np.clip(np.round(mist), 0, 255).astype(np.uint8)
    for r in q["remendos"]:
        x0, ry0, x1, ry1 = r["px"]
        out[ry0:ry1, x0:x1] = img[ry0 + r["dy"]:ry1 + r["dy"], x0:x1]
    print(f"    cozinha: a beira da bancada em L sem o tracejado (x {q['beira_x']}, y {y0}-{y1}); "
          f"{', '.join(r['nome'] for r in q['remendos'])} fora")
    return out


# ----------------------------------------------------------------------------------------------------------------------
PASSOS = [("marrom", marrom_tb), ("bancadas", bancadas_tb), ("gourmet", gourmet_tb), ("deck", deck_tb), ("portas", portas_tb),
          ("bege_escadas", bege_escadas_tb), ("escadas", escadas_tb), ("entrada", entrada_tb),
          ("tracejados", tracejados_tb), ("moveis", moveis_tb), ("closets", closets_tb), ("banco", banco_closet_tb),
          ("espreguicadeiras", espreguicadeiras_tb), ("folhas", folhas_tb),
          ("gramado", gramado_tb), ("jardins", jardins_tb), ("perimetro", perimetro_tb),
          ("pergolado", pergolado_tb), ("vidros_agua", vidros_agua_tb),
          ("defeito", defeito_tb), ("floreiras", floreiras_tb), ("ralos", ralos_tb),
          ("portas_fechadas", portas_fechadas_tb), ("cozinha", cozinha_tb),
          ("quina", quina_tb), ("tapete", tapete_tb),
          ("poltronas", poltronas_tb), ("sofa_living", sofa_living_tb),
          ("cadeiras", cadeiras_tb), ("varanda_ia", varanda_ia_tb), ("poltronas_varanda", poltronas_varanda_tb),
          ("estar_varanda", estar_varanda_tb), ("living_ia", living_ia_tb), ("camas_ia", camas_ia_tb),
          ("pedras", pedras_tb), ("brises", brises_tb), ("despensa", despensa_tb), ("pontos", pontos_tb),
          ("rotulos", rotulos_tb), ("bancada_cozinha", bancada_cozinha_tb)]


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
                   "piscina": (680, 1100, 1220, 1500), "pergolado_jardim": (2320, 1160, 2880, 1310),
                   "portas_closet_sala": (1440, 480, 1660, 620)}


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

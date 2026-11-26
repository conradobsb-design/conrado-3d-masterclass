"""Casa B Térreo, 6ª leva de 26/11: os tapetes da varanda e do living com duas bordas, o sofá da suíte 1 sem a sombra e
a poltrona redonda da varanda pela da biblioteca.

- **Tapetes da varanda e do living** ("corrija o contorno do tapete e deixe duas bordas de tapetes apenas"; "corrija as
  falhas do tapete e remova as linhas de contorno, deixando duas bordas de tapete"; "corrija aqui e afine essa borda
  do tapete"; "as poltronas não possuem vãos"): os dois vinham com a linha técnica do PDF por fora, uma faixa de
  travertino entre ela e o tapete e a beira do tapete irregular (no 12K, retalhos e pontinhos). Agora cada tapete vai
  até o contorno do PDF (varanda 1185 a 1487 x 801 a 1006; living 1715 a 2015 x 787 a 997) e tem só duas bordas: a de
  fora e a de dentro de uma barra fina de 3 px (5 cm) no próprio tecido, um pouco mais escura. A linha técnica sai (o
  travertino de logo fora no lugar, sem copiar as letras do rótulo "DESCE PARA O" ao lado; embaixo da varanda, 13 px,
  por causa dos restos do 12K), a beira do campo é refeita com o campo de logo para dentro e a barra com o campo de
  mais para dentro, escurecido. As peças por cima ficam inteiras (sofás, mesas e banco pela caixa; as poltronas pelo
  casco da cor delas, sem vãos). No living o campo inteiro é tecido de novo (de um trecho limpo). Na varanda (listras
  horizontais): as manchas soltas do campo saem pela mediana da própria linha (na final, também a fileira de
  marquinhas junto à borda de cima), e o pufe branco, que cai sobre a beira esquerda, é achado na imagem (o tampo claro,
  a lateral sombreada até a linha escura e os cantos arredondados); no 12K a ponta de cima dele vinha misturada ao
  piso (bege): ela vem da ponta limpa, espelhada no eixo curto; em volta dele as linhas do tapete vêm do campo limpo à
  direita e o travertino à esquerda do piso de mais à esquerda, com a sombra curta do pufe para baixo e à esquerda.
- **Sofá da suíte 1** ("remova o sombreamento do sofá"): o assento (as duas almofadas, 2090,5 a 2118,5 x 394,5 a
  486,5) tinha a sombra larga das almofadas de encosto (até L 90). Cada px vai para o tom do próprio sofá (a mediana do
  braço de cima, 3% mais baixa) pela razão da cor média em volta dele (2,5 px, só sobre o tecido): a costura entre as
  almofadas e as dobras ficam, a sombra sai.
- **Poltrona redonda da varanda** ("melhorar a representação dessa poltrona"): o disco claro com o encosto em faixa, à
  esquerda do tapete da varanda, vira a poltrona de leitura da biblioteca (bouclé, a do escritório da Casa A) no lugar
  e no giro dela (centro 1147 x 936,5; o encosto para baixo e à esquerda, a frente para o tapete), 50 px (0,83 m) de
  fundo, no off-white do pufe e do sofá; o piso em volta no travertino novo e a sombra curta para baixo e à esquerda.

Final, prancha e 12K A e B (pelo registro local).

  python3 terreo_casab_2611f.py [item ...]
"""
import os
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
sys.path.insert(0, str(Path(__file__).resolve().parent))
import esquadrias_pretas_1911 as EP  # noqa: E402
import vetor_2511 as V               # noqa: E402
import um_pav_casaa_2511c as C       # noqa: E402
import um_pav_casaa_2511d as DD      # noqa: E402
import terreo_casab_2611b as B       # noqa: E402
import terreo_casaa_2511g as G       # noqa: E402
import terreo_casaa_2511d as D       # noqa: E402
import terreo_casab_2611 as B0       # noqa: E402,F401  (o travertino desta planta: D.DZ_S)

PLANTA = "B_Terreo"
DZ = B.DZ
TAPETES = {
    "tapete_varanda": dict(ret=(1185.0, 801.0, 1487.0, 1006.0), borda=3.0, beira=9.0, anel=(4.0, 4.0, 4.0, 13.0), tom=0.84,
                           campo=None, salto=0.0, linhas=True, fonte_linhas=(1240.0, 1286.0),
                           fonte_piso=(1150.0, 1166.0), med_lim=6,
                           objetos=[([(1220.6, 911.1), (1173.7, 878.8), (1191.9, 852.5), (1238.7, 884.8)], "branco"),
                                    ((1317.0, 833.0, 1407.0, 871.0), "caixa"), ((1289.0, 872.0, 1378.0, 910.0), "caixa"),
                                    ((1207.5, 937.0, 1445.5, 1006.5), "caixa"), ((1215.5, 1006.5, 1445.5, 1019.0), "caixa"),
                                    ((1446.0, 816.0, 1502.0, 882.0), "poltrona"),
                                    ((1446.0, 898.0, 1502.0, 964.0), "poltrona")]),
    "tapete_living": dict(ret=(1715.0, 787.0, 2015.0, 997.0), borda=3.0, beira=9.0, anel=4.0, tom=0.84,
                          campo=(1925.0, 880.0, 2005.0, 985.0), salto=0.0, linhas=False,
                          objetos=[((1722.5, 789.5, 1755.0, 822.0), "caixa"), ((1735.0, 758.0, 1760.0, 786.0), "caixa"),
                                   ((1754.0, 740.0, 2026.0, 822.5), "caixa"),
                                   ((1952.0, 815.0, 2026.0, 872.5), "caixa"),
                                   ((1696.0, 834.0, 1748.0, 897.0), "poltrona"),
                                   ((1696.0, 905.0, 1748.0, 968.0), "poltrona"),
                                   ((1795.0, 860.0, 1905.0, 930.0), "mesa"),
                                   ((1809.0, 969.0, 1921.0, 1009.0), "caixa")]),
}
POLTRONA = dict(png=EP.PROJ / "POE642_CasaA/biblioteca-objetos/02-terreo/escritorio/poltrona-leitura.png",
                centro=(1147.0, 936.5), alto=50.0, giro=131.3, raio=36.0, desvio=(-2.5, 2.5), xmax=1179.5,
                sombra=0.26, cor=(229.0, 234.0, 239.0))
SOFA = dict(ret=(2090.5, 394.5, 2118.5, 486.5), sig=2.5, ref=(2093.0, 386.0, 2116.0, 391.0), fator=0.97)


def _protecao(reg, jan, s, origem, objetos):
    """As peças por cima do tapete: as caixas inteiras; as poltronas, o pufe e a mesa pelo casco da cor deles."""
    H, W = reg.shape[:2]
    Lr = reg.mean(2)
    sat = reg.max(2) - reg.min(2)
    prot = np.zeros((H, W), np.float32)
    for caixa, tipo in objetos:
        if tipo == "branco":                     # o pufe: a silhueta achada na própria imagem, com a folga
            mm = _pufe(reg, jan, s, origem, caixa)
            prot = np.maximum(prot, mm.astype(np.float32))
            continue
        cx = V.cob([V.ret(*caixa)], jan, s, origem) > 0.5
        if tipo == "caixa":
            mm = cx
        else:
            if tipo == "poltrona":
                cor = cx & (sat > 60)
            elif tipo == "mesa":
                cor = cx & (sat > 35) & (Lr < 205)
            else:
                cor = cx & (Lr > 228) & (sat < 22)
            n, lab, st, _ = cv2.connectedComponentsWithStats(cor.astype(np.uint8))
            mm = np.zeros((H, W), bool)
            if n > 1:
                i = 1 + int(np.argmax(st[1:, 4]))
                pts = np.argwhere(lab == i)[:, ::-1].astype(np.int32)
                casco = np.zeros((H, W), np.uint8)
                cv2.fillConvexPoly(casco, cv2.convexHull(pts), 1)
                mm = casco > 0
        folga = {"caixa": 0.0, "poltrona": 0.8, "mesa": 1.0}[tipo]
        if folga:
            kd = max(3, int(round(folga * s)) * 2 + 1)
            mm = cv2.dilate(mm.astype(np.uint8), np.ones((kd, kd), np.uint8)) > 0
        prot = np.maximum(prot, mm.astype(np.float32))
    return prot


def _pufe_geo(reg, jan, s, origem, poli):
    """O pufe na imagem. O tecido branco (L > 226) ligado ao meio do retângulo de referência dá o retângulo girado
    mínimo do tampo claro (o pufe está mais girado que a referência e, no 12K, um pouco fora do lugar); a lateral
    sombreada dele, para baixo e à esquerda, vai até onde o tom cai abaixo de 165 (a linha escura rente ao tapete),
    medida no próprio pufe. A silhueta é esse retângulo esticado até a lateral, com os cantos arredondados (4,5 px).
    No 12K uma das pontas veio misturada ao piso (bege): `sd` diz qual (-1 ou 1; 0 se nenhuma). Devolve a silhueta, o
    retângulo (ou None), sd, o eixo comprido (ex, ey) e o meio comprimento."""
    H, W = reg.shape[:2]
    cx = sum(x for x, _ in poli) / len(poli)
    cy = sum(y for _, y in poli) / len(poli)
    perto = V.cob([[(cx + 1.8 * (x - cx), cy + 1.8 * (y - cy)) for x, y in poli]], jan, s, origem) > 0.5
    Lb = cv2.GaussianBlur(reg.mean(2), (0, 0), 0.5 * s)
    sat = cv2.GaussianBlur(reg.max(2) - reg.min(2), (0, 0), 0.5 * s)
    branco = (perto & (Lb > 226) & (sat < 20)).astype(np.uint8)
    ka = max(3, int(round(0.6 * s)) * 2 + 1)
    branco = cv2.morphologyEx(branco, cv2.MORPH_OPEN, np.ones((ka, ka), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(branco)
    meio = V.cob([[(cx + 0.35 * (x - cx), cy + 0.35 * (y - cy)) for x, y in poli]], jan, s, origem) > 0.5
    ids = np.unique(lab[meio & (lab > 0)])
    if n < 2 or len(ids) == 0:
        return V.cob([poli], jan, s, origem) > 0.5, None, 0, (1.0, 0.0), 1.0
    i = ids[np.argmax(st[ids, 4])]
    pts = np.argwhere(lab == i)[:, ::-1].astype(np.float32)
    ret = cv2.minAreaRect(pts)
    bp = cv2.boxPoints(ret)
    e1, e2 = bp[1] - bp[0], bp[2] - bp[1]
    el, ec = (e1, e2) if np.hypot(*e1) >= np.hypot(*e2) else (e2, e1)
    Lh, hw = float(np.hypot(*el) / 2.0), float(np.hypot(*ec) / 2.0)
    ex, ey = el / (2 * Lh)
    nx, ny = -ey, ex
    if ny < 0:
        nx, ny = -nx, -ny                       # a normal para baixo (a lateral sombreada)
    (rcx, rcy) = ret[0]
    Lp = cv2.GaussianBlur(reg.mean(2), (0, 0), 0.4 * s)
    bordas = []
    for uu in np.linspace(-0.6, 0.6, 13):
        px, py = rcx + uu * Lh * ex, rcy + uu * Lh * ey
        for d in np.arange(hw, hw + 12.0 * s, 0.25 * s):
            X, Y = int(round(px + d * nx)), int(round(py + d * ny))
            if not (0 <= X < W and 0 <= Y < H):
                break
            if Lp[Y, X] < 165:
                bordas.append(d)
                break
    de = float(np.median(bordas)) - 0.5 * s if len(bordas) >= 4 else hw + 6.0 * s
    de = max(de, hw)
    # a beira de cima (clara) do tampo: onde o tom cai abaixo de 226 (o retângulo mínimo do branco passa dela)
    topo = []
    for uu in np.linspace(-0.6, 0.6, 13):
        px, py = rcx + uu * Lh * ex, rcy + uu * Lh * ey
        for d in np.arange(0.0, hw + 4.0 * s, 0.25 * s):
            X, Y = int(round(px - d * nx)), int(round(py - d * ny))
            if not (0 <= X < W and 0 <= Y < H):
                break
            if Lp[Y, X] < 226:
                topo.append(d)
                break
    hu = float(np.median(topo)) - 0.25 * s if len(topo) >= 4 else hw
    hu = min(max(hu, hw - 3.0 * s), hw)
    c = np.array([rcx, rcy], np.float32)
    E = np.array([ex, ey], np.float32)
    N = np.array([nx, ny], np.float32)
    poly = np.array([c - Lh * E - hu * N, c + Lh * E - hu * N, c + Lh * E + de * N, c - Lh * E + de * N])
    m = np.zeros((H, W), np.uint8)
    cv2.fillConvexPoly(m, np.round(poly).astype(np.int32), 1)
    r = max(1, int(round(4.5 * s)))
    el_ = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))
    sil = cv2.morphologyEx(m, cv2.MORPH_OPEN, el_) > 0
    Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
    u = (X - rcx) * ex + (Y - rcy) * ey
    ke = max(3, int(round(1.5 * s)) * 2 + 1)
    miolo = cv2.erode(sil.astype(np.uint8), np.ones((ke, ke), np.uint8)) > 0
    bege = miolo & ((reg.max(2) - reg.min(2)) > 24)        # o piso aparecendo
    a, b = int((bege & (u < 0)).sum()), int((bege & (u > 0)).sum())
    sd = 0 if max(a, b) < 0.02 * miolo.sum() else (-1 if a > b else 1)
    return sil, ret, sd, (ex, ey), Lh


def _pufe(reg, jan, s, origem, poli, lados=True):
    """O pufe: a silhueta e, com `lados`, a folga de 1 px em volta dela (a beira macia do tecido), menos na beira de
    cima da ponta suja (lá a folga seria o tapete de antes, ou o espelhado)."""
    sil, ret, sd, (ex, ey), Lh = _pufe_geo(reg, jan, s, origem, poli)
    if not lados:
        return sil
    kd = max(3, int(round(1.0 * s)) * 2 + 1)
    m = cv2.dilate(sil.astype(np.uint8), np.ones((kd, kd), np.uint8)) > 0
    if ret is not None and sd:
        H, W = reg.shape[:2]
        (rcx, rcy) = ret[0]
        nx, ny = -ey, ex
        if ny < 0:
            nx, ny = -nx, -ny
        Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
        u = (X - rcx) * ex + (Y - rcy) * ey
        v = (X - rcx) * nx + (Y - rcy) * ny
        m &= sil | ~((sd * u > 0) & (v < 0))
    return m


def _limpa_pufe(out, reg, jan, s, origem, poli):
    """O pufe branco: no 12K uma das pontas do tampo veio misturada ao piso (manchas bege e cinzas). Essa ponta (de 20%
    do comprimento para fora) vem da outra ponta, limpa, espelhada no eixo curto do pufe (a luz das beiras compridas
    fica a mesma), com a emenda esfumada; fora da silhueta espelhada, o tapete e o piso são refeitos depois. Se as
    manchas forem poucas (a final), nada muda."""
    H, W = reg.shape[:2]
    sil, ret, sd, (ex, ey), Lh = _pufe_geo(reg, jan, s, origem, poli)
    if ret is None or sd == 0:
        return out
    (rcx, rcy) = ret[0]
    Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
    u = (X - rcx) * ex + (Y - rcy) * ey
    mx = (X - 2 * u * ex).astype(np.float32)
    my = (Y - 2 * u * ey).astype(np.float32)
    esp = cv2.remap(out.astype(np.float32), mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    tampo = _pufe(reg, jan, s, origem, poli)
    w = np.clip((sd * u - 0.2 * Lh) / (0.15 * Lh), 0, 1) * tampo
    w = np.clip(cv2.GaussianBlur(w.astype(np.float32), (0, 0), 0.3 * s), 0, 1) * tampo
    return out * (1 - w[..., None]) + esp * w[..., None]


def _linhas_pufe(out, P, Pb, xs, ys, q, s):
    """No tapete listrado, as linhas em volta do pufe (que cai sobre a beira esquerda): cada linha do tapete que o pufe
    toca, do contorno até 3 px depois do pufe, recebe a mesma linha do campo limpo à direita (`fonte_linhas`),
    espelhada (as listras são horizontais e seguem)."""
    x0, y0, x1, y1 = q["ret"]
    fx0, fx1 = q["fonte_linhas"]
    src = np.where((xs >= fx0) & (xs <= fx1))[0]
    n = len(src)
    if n < 4 or not Pb.any():
        return out
    rr = np.where(Pb.any(axis=1))[0]
    r0 = max(rr.min() - int(round(4 * s)), 0)
    r1 = min(rr.max() + int(round(10 * s)), len(ys) - 1)        # a sombra antiga, para baixo
    linhas = [r for r in range(r0, r1 + 1) if y0 <= ys[r] < y1]
    cc = np.where(Pb.any(axis=0))[0]
    cmax = min(cc.max() + int(round(3 * s)), src[0] - 1)
    alvo = np.where((xs >= x0) & (np.arange(len(xs)) <= cmax))[0]
    # do fim da zona para a esquerda: a fonte espelhada de trás para frente (o px logo antes de cmax vem da beira
    # esquerda da fonte)
    d = cmax - alvo
    k = d % (2 * n)
    k = np.where(k < n, k, 2 * n - 1 - k)
    col = src[k]
    for r in linhas:
        livre = P[r, alvo] < 0.5
        out[r, alvo[livre]] = out[r, col[livre]]
    # o travertino logo à esquerda do tapete, nas linhas em que o pufe passa do contorno (com a sombra antiga dele):
    # a mesma linha do piso de mais à esquerda (`fonte_piso`, os veios são horizontais), espelhada
    if q.get("fonte_piso"):
        fora = Pb[:, xs < x0]
        if fora.any():
            rr = np.where(fora.any(axis=1))[0]
            r0 = max(rr.min() - int(round(2 * s)), 0)
            r1 = min(rr.max() + int(round(8 * s)), len(ys) - 1)
            px0, px1 = q["fonte_piso"]
            srcp = np.where((xs >= px0) & (xs <= px1))[0]
            npp = len(srcp)
            alvo = np.where((xs > px1) & (xs < x0))[0]
            if npp >= 4 and len(alvo):
                d = alvo - (srcp[-1] + 1)
                k = d % (2 * npp)
                k = np.where(k < npp, npp - 1 - k, k - npp)
                col = srcp[k]
                for r in range(r0, r1 + 1):
                    livre = P[r, alvo] < 0.5
                    out[r, alvo[livre]] = out[r, col[livre]]
    return out


def _espelhar(linha, ok, banda, passo, nmin, lim):
    """Preenche os px `banda` (índices em ordem, do mais de dentro para o mais de fora) da linha 1D com o trecho válido
    logo depois dela (no sentido de quem vem de dentro: j -= passo), espelhado; procura até `lim` px; devolve a linha
    e se deu certo."""
    n = len(linha)
    j = banda[0] - passo
    run = []
    busca = 0
    curto = max(3, nmin // 2)
    while 0 <= j < n and busca < lim:
        if ok[j]:
            run.append(j)
            if len(run) >= max(len(banda), nmin):
                break
        elif run:
            if len(run) >= curto:
                break
            run = []
        j -= passo
        busca += 1
    if len(run) < curto:
        return linha, False
    m = len(run)
    for d, b in enumerate(banda):
        k = d % (2 * m)
        k = k if k < m else 2 * m - 1 - k
        linha[b] = linha[run[k]]
    return linha, True


def _faixas(out, ok, P, linhas_banda, cols, eixo, passo, nmin, lim):
    """Para cada coluna (eixo 0) ou linha (eixo 1) em `cols`, a banda `linhas_banda` refeita com o espelho."""
    for c in cols:
        if eixo == 0:
            lin, okl, pl = out[:, c].copy(), ok[:, c], P[:, c]
        else:
            lin, okl, pl = out[c].copy(), ok[c], P[c]
        ordem = linhas_banda[::-1] if passo < 0 else linhas_banda
        nova, feito = _espelhar(lin.copy(), okl, list(ordem), passo, nmin, lim)
        if not feito:
            continue
        sel = np.zeros(len(lin), bool)
        sel[linhas_banda] = True
        sel &= pl < 0.5
        if eixo == 0:
            out[sel, c] = nova[sel]
            ok[sel, c] = True
        else:
            out[c, sel] = nova[sel]
            ok[c, sel] = True


def _resto(out, ok, falta):
    """Os px que ficaram sem fonte: em cada linha, cada trecho que falta com o trecho válido ao lado, espelhado."""
    H, W = falta.shape
    for i in np.where(falta.any(1))[0]:
        f = falta[i]
        j = 0
        while j < W:
            if not f[j]:
                j += 1
                continue
            k = j
            while k < W and f[k]:
                k += 1
            n = k - j
            for lado in (-1, +1):
                run = []
                t = j - 1 if lado < 0 else k
                while 0 <= t < W and ok[i, t] and len(run) < n:
                    run.append(t)
                    t += lado
                if len(run) >= 3:
                    m = len(run)
                    alvo = list(range(j, k)) if lado < 0 else list(range(k - 1, j - 1, -1))
                    for d, b in enumerate(alvo):
                        kk = d % (2 * m)
                        kk = kk if kk < m else 2 * m - 1 - kk
                        out[i, b] = out[i, run[kk]]
                        ok[i, b] = True
                    break
            j = k


def _tapete(nome):
    def f(img, s, origem, q=TAPETES[nome]):
        x0, y0, x1, y1 = q["ret"]
        m = 24.0
        jan, reg = C._reg(img, (x0 - m, y0 - m, x1 + m, y1 + m), s, origem, folga=0)
        xs, ys = V.coords(jan, s, origem)
        H, W = reg.shape[:2]
        b, B = q["borda"], q["borda"] + q["beira"]
        ge, gt, gd, gb = q["anel"] if isinstance(q["anel"], tuple) else (q["anel"],) * 4
        g = max(ge, gt, gd, gb)
        out = reg.copy()
        # o pufe limpo primeiro (a ponta misturada ao piso, no 12K): a proteção e o tapete vêm depois dele
        for caixa, tipo in q["objetos"]:
            if tipo == "branco":
                out = _limpa_pufe(out, reg, jan, s, origem, caixa)
        P = _protecao(reg, jan, s, origem, q["objetos"])
        nmin = max(3, int(round(4 * s)))
        # 0) no living, o campo inteiro de novo: o tecido costurado de um trecho limpo, com a luz do tapete de antes
        if q["campo"] is not None:
            img2 = img.copy()
            img2 = G.refazer(img2, s, origem, [(q["ret"], "")], textura=("quilt", q["campo"]), tol=0.06,
                             luz_sig=8.0, pena=0.0)
            _, reg2 = C._reg(img2, (x0 - m, y0 - m, x1 + m, y1 + m), s, origem, folga=0)
            dentro = V.cob([V.ret(*q["ret"])], jan, s, origem)
            # a sombra curta das peças no campo novo
            Ms = np.float32([[1, 0, -0.8 * s], [0, 1, 1.0 * s]])
            sb = cv2.GaussianBlur(cv2.warpAffine(P, Ms, (W, H)), (0, 0), 1.0 * s) * (1 - P)
            reg2 = reg2 * (1 - 0.16 * sb)[..., None]
            a = (dentro * (1 - P))[..., None]
            out = out * (1 - a) + reg2 * a
        # 0b) no tapete listrado, as manchas soltas do campo: cada px fora do tom da própria linha (a mediana de 9 px
        # para cada lado) recebe essa mediana
        if q.get("linhas"):
            from scipy.ndimage import median_filter
            w = max(5, int(round(9 * s)) * 2 + 1)
            dentro = (V.cob([V.ret(*q["ret"])], jan, s, origem) > 0.5) & (P < 0.5)
            med = np.stack([median_filter(out[..., c], size=(1, w)) for c in range(3)], -1)
            dif = np.abs(out.mean(2) - med.mean(2))
            mancha = cv2.dilate(((dif > (q.get("med_lim", 14) if s < 1.5 else 14)) & dentro).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
            mancha &= dentro
            # só onde a janela da mediana não pega peça nenhuma
            longe = cv2.dilate((P > 0.05).astype(np.uint8), np.ones((3, w), np.uint8)) == 0
            mancha &= longe
            out[mancha] = med[mancha]
        # 1) a beira (do contorno até B px para dentro): o campo de logo para dentro, espelhado, linha a linha
        cx_in = np.where((xs >= x0 + B) & (xs < x1 - B))[0]
        cy_in = np.where((ys >= y0 + B) & (ys < y1 - B))[0]
        ok = np.zeros((H, W), bool)
        ok[np.ix_(cy_in, cx_in)] = True
        ok &= P < 0.5
        topo = np.where((ys >= y0) & (ys < y0 + B))[0]
        base = np.where((ys >= y1 - B) & (ys < y1))[0]
        esq = np.where((xs >= x0) & (xs < x0 + B))[0]
        dir_ = np.where((xs >= x1 - B) & (xs < x1))[0]
        rows_R = np.where((ys >= y0) & (ys < y1))[0]
        sl = q.get("salto", 0.0)
        okv = ok.copy()
        if sl:
            okv[np.where((ys >= y0 + B) & (ys < y0 + B + sl))[0]] = False
            okv[np.where((ys >= y1 - B - sl) & (ys < y1 - B))[0]] = False
        lim = int(round((B + sl + 10) * s))
        _faixas(out, okv, P, topo, cx_in, 0, -1, nmin, lim)
        _faixas(out, okv, P, base, cx_in, 0, +1, nmin, lim)
        ok |= okv & ~ok & (P < 0.5)
        _faixas(out, ok, P, esq, cy_in, 1, -1, nmin, lim)
        _faixas(out, ok, P, dir_, cy_in, 1, +1, nmin, lim)
        banda = np.zeros((H, W), bool)
        banda[np.ix_(rows_R, np.where((xs >= x0) & (xs < x1))[0])] = True
        banda[np.ix_(cy_in, cx_in)] = False
        _resto(out, ok, banda & ~ok & (P < 0.5))
        # 1b) em volta do pufe (no tapete listrado), as linhas inteiras do campo limpo à direita
        Pb = np.zeros((H, W), bool)
        for caixa, tipo in q["objetos"]:
            if tipo == "branco":
                Pb |= _pufe(reg, jan, s, origem, caixa)
        if q.get("fonte_linhas") and Pb.any():
            out = _linhas_pufe(out, P, Pb, xs, ys, q, s)
        # 2) fora (o anel da linha técnica): o piso de logo fora, espelhado
        okf = np.ones((H, W), bool)
        okf[np.ix_(np.where((ys >= y0 - gt) & (ys < y1 + gb))[0], np.where((xs >= x0 - ge) & (xs < x1 + gd))[0])] = False
        okf &= P < 0.5
        letras = (reg.mean(2) < 150).astype(np.uint8)   # nem as letras dos rótulos de fora (o piso só)
        kl = max(3, int(round(1.5 * s)) * 2 + 1)
        okf &= cv2.dilate(letras, np.ones((kl, kl), np.uint8)) == 0
        cx_g = np.where((xs >= x0 - ge) & (xs < x1 + gd))[0]
        rows_g = np.where((ys >= y0) & (ys < y1))[0]
        _faixas(out, okf, P, np.where((ys >= y0 - gt) & (ys < y0))[0], cx_g, 0, +1, nmin, lim)
        _faixas(out, okf, P, np.where((ys >= y1) & (ys < y1 + gb))[0], cx_g, 0, -1, nmin, lim)
        _faixas(out, okf, P, np.where((xs >= x0 - ge) & (xs < x0))[0], rows_g, 1, +1, nmin, lim)
        _faixas(out, okf, P, np.where((xs >= x1) & (xs < x1 + gd))[0], rows_g, 1, -1, nmin, lim)
        # 3) a barra: as b px de fora do tapete, um pouco mais escuras e menos saturadas (as duas bordas)
        A = V.cob([V.ret(*q["ret"])], jan, s, origem)
        Ain = V.cob([V.ret(x0 + b, y0 + b, x1 - b, y1 - b)], jan, s, origem)
        fx = np.clip(A - Ain, 0, 1) * (1 - P)
        cinza = out.mean(2, keepdims=True)
        barra = (0.7 * out + 0.3 * cinza) * q["tom"]
        out = out * (1 - fx[..., None]) + barra * fx[..., None]
        # 4) a sombra curta do pufe (para baixo e à esquerda, como a de antes) no tapete e na beira refeitos
        if Pb.any():
            Ms = np.float32([[1, 0, -1.0 * s], [0, 1, 1.2 * s]])
            sb = cv2.GaussianBlur(cv2.warpAffine(Pb.astype(np.float32), Ms, (W, H)), (0, 0), 1.0 * s) * (1 - P)
            e = 20.0 if q.get("fonte_piso") else g
            ag = V.cob([V.ret(x0 - e, y0 - g, x1 + g, y1 + g)], jan, s, origem)
            out = out * (1 - 0.28 * sb * ag)[..., None]
        return C._gravar(img, jan, out)
    return f


def sofa_suite1(img, s, origem, q=SOFA):
    """O assento do sofá da suíte 1 sem a sombra das almofadas de encosto: cada px vai para o tom do próprio sofá (a
    mediana do braço de cima, 3% mais baixa), pela razão da cor média em volta dele (2,5 px, só sobre o tecido: as
    costuras e as dobras ficam, a sombra larga sai)."""
    x0, y0, x1, y1 = q["ret"]
    jan, reg = C._reg(img, (x0 - 3, y0 - 3, x1 + 3, y1 + 3), s, origem, folga=0)
    a = V.cob([V.ret(*q["ret"])], jan, s, origem)
    dentro = a > 0.99
    L = reg.mean(2)
    Lg = cv2.GaussianBlur(L, (0, 0), 4.0 * s)
    tecido = (dentro & (L > Lg - 18)).astype(np.float32)          # sem as costuras e a divisão das almofadas
    sig = q["sig"] * s
    den = cv2.GaussianBlur(tecido, (0, 0), sig)
    loc = np.stack([cv2.GaussianBlur(reg[..., c] * tecido, (0, 0), sig) for c in range(3)], -1) / np.maximum(den, 1e-3)[..., None]
    # o tom do próprio sofá (o braço de cima, fora da sombra), um pouco mais baixo
    jr, rr = C._reg(img, q["ref"], s, origem, folga=0)
    alvo = np.median(rr.reshape(-1, 3), axis=0) * q["fator"]
    ganho = np.clip(alvo[None, None, :] / np.maximum(loc, 1.0), 0.9, 2.6)
    novo = reg * ganho
    pena = np.clip(cv2.GaussianBlur(a, (0, 0), 0.6 * s), 0, 1) * (a > 0.01)
    reg = reg * (1 - pena[..., None]) + novo * pena[..., None]
    return C._gravar(img, jan, reg)


def poltrona_redonda(img, s, origem, q=POLTRONA):
    """A poltrona redonda branca à esquerda do tapete da varanda (o disco claro com o encosto em faixa) pela poltrona
    de leitura da biblioteca (bouclé, a mesma do escritório da Casa A), no lugar e no giro dela (o encosto para baixo e
    à esquerda, a frente para o tapete), 50 px (≈ 0,83 m) de fundo, no off-white do pufe e do sofá; o piso em volta (a
    poltrona velha e a sombra dela, um disco de 36 px até antes do tapete) no travertino novo; a sombra curta para
    baixo e à esquerda."""
    cx, cy = q["centro"]
    R = q["raio"]
    zx, zy = cx + q["desvio"][0], cy + q["desvio"][1]
    zona = [(min(zx + R * np.cos(a), q["xmax"]), zy + R * np.sin(a)) for a in np.linspace(0, 2 * np.pi, 72, endpoint=False)]
    img = D.refazer_piso(img, s, origem, [zona], objetos=(), sombra=0.0)
    T = cv2.imread(str(q["png"]), cv2.IMREAD_UNCHANGED).astype(np.float32)
    al = T[..., 3] / 255.0
    ys, xs = np.where(al > 0.05)
    T, al = T[ys.min():ys.max() + 1, xs.min():xs.max() + 1], al[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    # o off-white dos brancos da varanda (o pufe, o sofá): a cor média da peça levada a `cor`, a sombra dela fica
    m = al > 0.5
    T[..., :3] *= (np.array(q["cor"], np.float32) / T[..., :3][m].mean(0))[None, None, :]
    T[..., :3] = np.clip(T[..., :3], 0, 255)
    k = q["alto"] * s / T.shape[0]
    pc = ((T.shape[1] - 1) / 2.0, (T.shape[0] - 1) / 2.0)
    jan = V.janela(img, (cx - 34, cy - 34, cx + 34, cy + 34), s, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    H, W = reg.shape[:2]
    tx, ty = (cx - origem[0]) * s - 0.5 - X0, (cy - origem[1]) * s - 0.5 - Y0
    M = cv2.getRotationMatrix2D(pc, q["giro"], k)
    M[0, 2] += tx - pc[0]
    M[1, 2] += ty - pc[1]
    if k < 1:                                           # reduzir antes de girar (sem serrilhado)
        T2 = cv2.resize(np.dstack([T[..., :3] * al[..., None], al]), None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
        pc2 = ((T2.shape[1] - 1) / 2.0, (T2.shape[0] - 1) / 2.0)
        M = cv2.getRotationMatrix2D(pc2, q["giro"], 1.0)
        M[0, 2] += tx - pc2[0]
        M[1, 2] += ty - pc2[1]
    else:
        T2 = np.dstack([T[..., :3] * al[..., None], al])
    w = cv2.warpAffine(T2, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    a = np.clip(w[..., 3], 0, 1)
    cor = w[..., :3] / np.maximum(a, 1e-4)[..., None]
    # a sombra curta (para baixo e à esquerda, como a do pufe e a de antes)
    Ms = np.float32([[1, 0, -1.2 * s], [0, 1, 1.4 * s]])
    sb = cv2.GaussianBlur(cv2.warpAffine(a, Ms, (W, H)), (0, 0), 1.5 * s) * (1 - a)
    reg = reg * (1 - q["sombra"] * sb)[..., None]
    reg = reg * (1 - a[..., None]) + cor * a[..., None]
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return img


FUNC = {"sofa_suite1": sofa_suite1}
ITENS = {"sofa_suite1": (2065.0, 380.0, 2130.0, 510.0)}
for _n, _q in TAPETES.items():
    FUNC[_n] = _tapete(_n)
    ITENS[_n] = (_q["ret"][0] - 20, _q["ret"][1] - 20, _q["ret"][2] + 20, _q["ret"][3] + 20)
FUNC["poltrona_redonda"] = poltrona_redonda
ITENS["poltrona_redonda"] = (1095.0, 895.0, 1195.0, 985.0)


def item(img, nome, escala=1.0, origem=(0.0, 0.0)):
    return FUNC[nome](img, escala, origem)


def main(so=None):
    c, pav = PLANTA.split("_")
    base = cv2.imread(str(EP.PROJ / EP.PLANTAS[PLANTA][0]))
    nomes = [n for n in ITENS if not so or n in so]
    for f in EP.PLANTAS[PLANTA]:
        im = cv2.imread(str(EP.PROJ / f))
        for nome in nomes:
            im = item(im, nome)
        cv2.imwrite(str(EP.PROJ / f), im)
        if f == EP.PLANTAS[PLANTA][0]:
            novo = im
    pf = EP.PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_entrega.png"
    pr = cv2.imread(str(pf))
    pr[:2160] = novo
    cv2.imwrite(str(pf), pr)
    for op in os.environ.get("OPCOES", "AB"):
        rel = EP.PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_12K_opcao_{op}.jpg"
        pil = Image.open(rel)
        dpi = pil.info.get("dpi", (743, 743))
        im = cv2.cvtColor(np.array(pil.convert("RGB")), cv2.COLOR_RGB2BGR)
        del pil
        cinza = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        for nome in nomes:
            sx, org, cc = DD._registro(base, cinza, DZ, ITENS[nome])
            im = item(im, nome, sx, org)
            print(f"   {op}: {nome} (registro {cc:.3f}, escala {sx:.3f})")
        Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).save(rel, quality=95, subsampling=0, dpi=dpi)
        del im, cinza


if __name__ == "__main__":
    main(sys.argv[1:] or None)

"""A revisão do 12K do Térreo da Casa C de 14/11 (os recortes do usuário, um a um).

Entra no fim de `revisao_terreo_casac_1311.aplicar` (a final de `ANTES_COMMIT` de lá, as etapas de 13/11 e estas), em px
da final de 3840:
- **"CORRIJA - DESCE PARA O JARDIM"** (`descricao_deck`): a descrição da escada estreita, no deck, passa de "DESCE PARA O
  / SUBSOLO" a "DESCE PARA O / JARDIM"; a 2ª linha sai (o deck da mesma fileira de réguas, `dx` ao lado) e volta escrita
  na mesma letra, no mesmo centro e na mesma linha de base (`pedidos_terreo_casac_1311._escada`).
- **"CORRIJA FALHA NO BANCO"** (`banco_deck`): os dois dentes claros na borda de baixo do braço de cima do banco em L
  do deck saem (as colunas do banco e das réguas logo ao lado).
- **"LIMPE VESTÍGIOS BRANCOS NO JARDIM"** (`vestigios_jardim`): os 3 trechos de traço branco e preto (2 px) na grama
  junto ao braço da esquerda do banco viram grama (a grama de `dx` px à esquerda).
- **"O CANO DO CHUVEIRO VAI ATÉ A PAREDE"** (`cano_ducha`): o braço do chuveiro do pisante (`final3840_casac.
  CHUVEIRO_C`) tinha ficado sob a grama nova; volta cromado, da placa até o muro (a face de cima do muro achada na
  coluna do braço), com a canopla no muro.
- **"REMOVER ESSES TRAÇOS PRETOS DE DENTRO DA PISCINA"** (`piscina`): os traços pretos de 1 px (o tracejado do PDF) na
  borda de baixo do spa e no canto de baixo da piscina: cada trecho escuro da linha vira a cor da própria borda, pela
  interpolação entre os px de cada lado dele.
- **"NÃO HÁ ESSA BORDA, SOMENTE O PISO"** (`pivotantes_fora`): os dois painéis pivotantes junto à bancada da ilha da
  gourmet (`pedidos_terreo_casac_1311.pivotantes`) saem; o travertino da varanda gourmet (o de `dx` px à esquerda) vai
  até o fio da bancada.
- **"ADICIONANDO UM FILETE DIVIDINDO O JARDIM DO PISO. EM LINHA RETA"** (`filete_jardim1`): o fim do jardim 1 (a grama
  com a borda serrilhada e o verde manchando o piso) em linha reta, de parede a parede; logo abaixo, o filete de Bege
  Bahia de 5 cm (`revisao_terreo_casac_1311.filete_garagem`: a amostra da calçada, os fios das duas arestas e a sombrinha
  no piso).
- **"CORRIJA O INTERIOR DESSE BOX. APENAS O TRACEJADO DA CLARABOIA E O RESTANTE PISO"** (`box_bhm2`): o box do BH
  master 2 com um piso só (o travertino do próprio box, sem a faixa escura de cima nem o piso mais claro e as manchas
  dentro da claraboia), o chuveiro e o vidro ficam, e o tracejado cinza fino da claraboia de novo por cima.
- **"REMOVA ESSES RISCOS EM FRENTE A CORTINA E SOBRE O MÓVEL"** e **"... NO CANTO DO QUARTO 2"** (`tracos_cortina`): os
  tiquinhos pretos logo abaixo da cortina, sobre os guarda-roupas dos quartos 3 e 2, saem (o guarda-roupa de `dy` px
  abaixo, o veio em pé).
- **"CORRIJA O CONTORNO DO TAPETE ... EM FRENTE AO PUFF"** (`tapete_q1`): o fio de baixo do tapete do quarto 1, que
  falhava em frente ao pufe, contínuo (a cor do fio de cada lado).
- **"CORRIJA A FALHA AO REDOR DO COOKTOP"** (`cooktop`): a moldura marrom (a bancada antiga) em volta do vidro preto vira
  um fio de inox escuro, e a tira com o botão branco à esquerda e o toco à direita viram o Danae da ilha.
- **"O RÓTULO PRECISA SER REESCRITO PARA FICAR LEGÍVEL E O PISO CORRIGIDO"** (`louceiro1`): o rótulo do louceiro 1
  (pequeno, ilegível no 12K, e o "A:" trocado por um retângulo cinza) sai e volta no corpo do LOUCEIRO 2, nome em Inter
  SemiBold e área em Regular, no meio do louceiro; e **"PAREDE FINA ... NA COR DE PAREDE E NÃO OCRE"**: a parede fina
  entre o louceiro e o armário da cozinha no cinza das paredes, até a parede do louceiro.
- **"CORRIJA FALHA NO PISO RENTE A PORTA DE CORRER E NA PAREDE"** (`porta_circulacao`): a faixa mais clara do piso ao
  longo da porta de correr da circulação vira o travertino do lado, e a ponta da parede de cima termina reta.
- **"REMOVA ESSES BATENTES DA PORTA DO LOUCEIRO 2"** (`batentes_louceiro2`): os dois batentes viram parede; a folha
  (54 px) fica quina com quina com a parede, do vão inteiro.
- **"MELHORE ESSE ENTORNO DO SOFÁ E DOS VASOS DE PLANTAS"** (`entorno_estar`): em volta dos vasos, o retângulo do PDF
  recortado da final antiga (o desenho velho da planta e o halo cinza) vira travertino, com a sombra curta das folhas; em
  volta do sofá curvo, a sombra dupla vira a sombra curta do contorno dele (o sofá refeito pela mesma conta do
  `mobiliario_terreo_casac_1311.estar`).
- O aparador do hall chegou a ir para o cinza da foto ("ESSE APARADOR TEM O TOM CINZA CONFORME FOTO") e voltou ao freijó
  ("deixe como estava em vez do cinza").
"""

import contextlib
import io
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

# (o deck que tapa as linhas de antes: o de `dy` px abaixo, 4 réguas de 12 px, as juntas na mesma fase)
DESC_DECK = {"escada": 1, "linha": 1, "novo": "JARDIM", "dy": 48, "halo_px": 4}
BANCO_DECK = {"y": (1092, 1103), "trechos": [(744, 756, 12), (774, 794, -19)]}
JARDIM_DECK = {"x": (627, 635), "y": (1098, 1293), "dx": -9, "claro": 140}
CANO = {"busca_px": (1820, 1870), "muro_cinza": (80, 14)}
PISCINA = {"zonas": [(924, 1471, 1095, 1478), (958, 1631, 1096, 1639)], "escuro": 75}
PIVOT = {"x": (1221, 1230), "y": (978, 1161), "dx": -10}
FILETE_J1 = {"y": 977.0, "x": (1121.0, 1230.0), "larg_m": 0.05, "grama": (968, 977), "grama_dy": -6,
             "piso": (979, 987), "piso_dy": 8}
BOX_BHM2 = {"ret": (809, 907, 888, 967), "amostra": (813, 915, 840, 961), "chuveiro": (839, 927, 860, 949),
            "porta": (809, 963, 846, 967), "clara": (868.4, 907.2, 888.1, 966.9)}
TRACOS_CORTINA = [(1184, 347, 1207, 357, 8), (1680, 347, 1698, 358, 9)]
TAPETE_Q1 = {"x": (2016, 2061), "linhas": (565, 566), "amostra_x": [(2000, 2014), (2062, 2116)]}
COOKTOP = {"caixa": (2286, 414, 2332, 458), "vidro_max": 60, "fio": (66, 66, 68), "danae_dx": -8, "ilha_x": 2326}
# (o louceiro 1 vai de x 2200 à porta de correr em 2254: o rótulo cabe com 0,68 do corpo do LOUCEIRO 2; no 12K ele
# volta nítido, `rotulos_12k`, onde antes o Topaz o embaralhava)
LOUCEIRO1 = {"apaga": (2201, 660, 2252, 687), "apaga_dy": -26, "centro_x": 2226.5, "base": 672.0,
             "ref": "LOUCEIRO 2", "largura_ref": 65.0, "escala": 0.68, "entrelinha": 15.0, "cor": (20, 20, 20),
             "parede": (2170, 627, 2205, 631)}
PORTA_CIRC = {"faixa": (2285, 715, 2292, 834), "dx": 10, "parede": (2282, 705, 2292, 714), "piso": (2282, 714, 2292, 716)}
BATENTES_L2 = [{"ret": (2394, 811, 2401, 822), "coluna": 2390}, {"ret": (2453, 811, 2458, 821), "coluna": 2460}]
ESTAR_ENTORNO = {"amostra": (2215, 1606, 2295, 1640), "vaso_folga": 14, "sofa_folga": 10, "cortina_x": 2384, "plantas_antes": (2290, 1528, 2384, 1636),
                 "vasos": [("sala-intima/vaso-folhagem-a", (2357.0, 1563.0), 52.0),
                           ("sala-intima/vaso-folhagem-b", (2330.0, 1601.0), 50.0)]}
TAPETE_ESTAR = {"png": "02-terreo/sala-de-estar/tapete-redondo-render-v2.png", "miolo": 0.68, "luz_sigma": 2.0,
                "luz_min": 0.55}


def _pena(m, s=0.8):
    m = m.astype(np.float32)
    return np.maximum(m, cv2.GaussianBlur(m, (0, 0), s)) if s > 0 else m


def _misturar(out, x0, y0, novo, alfa):
    reg = out[y0:y0 + novo.shape[0], x0:x0 + novo.shape[1]].astype(np.float32)
    a = alfa[..., None] if alfa.ndim == 2 else alfa
    out[y0:y0 + novo.shape[0], x0:x0 + novo.shape[1]] = np.clip(np.round(reg * (1 - a) + novo * a), 0, 255
                                                                 ).astype(np.uint8)


def _textura(img, amostra, H, W, ref=None):
    import materiais_terreo_casac_1311 as MT
    ax0, ay0, ax1, ay1 = amostra
    T = MT.sem_emenda(img[ay0:ay1, ax0:ax1].astype(np.float32), H, W)
    if ref is not None:                          # o tom médio do lugar
        T = T - T.reshape(-1, 3).mean(axis=0) + ref
    return T


def descricao_deck(img, q=DESC_DECK):
    import final3840_casaa as FA
    import pedidos_terreo_casac_1311 as PT
    from PIL import ImageFont
    from rodape_entrega import FONTES
    from cliente_subsolo_casaa_0511 import _alfa_texto
    e = FA.ESCADA_A
    fonte = ImageFont.truetype(str(FONTES / e["fonte"]), e["corpo_px"] * 4)
    esc = PT.ESCADAS[q["escada"]]

    def alfa(txt, i):
        lw = fonte.getlength(txt) / 4
        tx, ly = esc["centro_x"] - lw / 2, esc["base_y"] + i * PT.PS.ENTRELINHA
        W, H = int(lw) + 12, e["corpo_px"] * 3
        X0, Y0 = int(tx) - 4, int(ly) - e["corpo_px"] * 2
        return _alfa_texto(txt, fonte, e["corpo_px"], tx, ly, (X0, Y0, W, H)), X0, Y0
    out = img.copy()
    # as duas linhas de antes e o halo claro em volta delas (a caixa do texto e mais `halo_px`) saem: o deck de `dy`
    # abaixo (as juntas das réguas na mesma fase)
    h = q["halo_px"]
    for i, txt in enumerate(esc["texto"]):
        a, X0, Y0 = alfa(txt, i)
        ys, xs = np.nonzero(a > 0.02)
        x0, y0, x1, y1 = X0 + xs.min() - h, Y0 + ys.min() - h, X0 + xs.max() + 1 + h, Y0 + ys.max() + 1 + h
        src = img[y0 + q["dy"]:y1 + q["dy"], x0:x1].astype(np.float32)
        volta = np.concatenate([img[y0 - 3:y0, x0:x1].reshape(-1, 3), img[y1:y1 + 3, x0:x1].reshape(-1, 3)]).astype(np.float32)
        volta_src = np.concatenate([img[y0 - 3 + q["dy"]:y0 + q["dy"], x0:x1].reshape(-1, 3),
                                    img[y1 + q["dy"]:y1 + 3 + q["dy"], x0:x1].reshape(-1, 3)]).astype(np.float32)
        src += (np.median(volta, axis=0) - np.median(volta_src, axis=0))[None, None]
        m = np.ones((y1 - y0, x1 - x0), np.float32)
        m[[0, -1], :] = 0.5
        m[:, [0, -1]] = 0.5
        _misturar(out, x0, y0, src, m)
    novo = list(esc["texto"])
    novo[q["linha"]] = q["novo"]
    for i, txt in enumerate(novo):
        a, X0, Y0 = alfa(txt, i)
        out = PT.PS._pintar(out, a, X0, Y0, e["cor_texto"])
    print(f"    deck: \"{novo[0]} / {novo[1]}\" (era \"{esc['texto'][1]}\"), sem o halo claro de antes")
    return out


def banco_deck(img, q=BANCO_DECK):
    out = img.copy()
    y0, y1 = q["y"]
    for x0, x1, dx in q["trechos"]:
        out[y0:y1, x0:x1] = img[y0:y1, x0 + dx:x1 + dx]
    print(f"    deck: o banco sem os {len(q['trechos'])} dentes claros na borda de baixo do braço de cima")
    return out


def vestigios_jardim(img, q=JARDIM_DECK):
    out = img.copy()
    x0, x1 = q["x"]
    y0, y1 = q["y"]
    reg = img[y0:y1, x0:x1].astype(np.int16)
    claro = reg.max(axis=2).max(axis=1) > q["claro"]
    linhas = np.nonzero(cv2.dilate(claro.astype(np.uint8)[:, None], np.ones((5, 1), np.uint8))[:, 0])[0] + y0
    dx = q["dx"]
    for y in linhas:
        out[y, x0:x1] = img[y, x0 + dx:x1 + dx]
    print(f"    jardim do deck: {int(claro.sum())} linhas de traço branco na grama fora")
    return out


def cano_ducha(Q, img, q=CANO):
    import final3840_casaa as FA
    import final3840_casac as C
    c = C.CHUVEIRO_C
    out = img.copy()
    (ax, ay), (bx, by) = Q.p2q(c["braco"][0], c["braco"][1]), Q.p2q(c["braco"][2], c["braco"][3])
    xm = int(round((ax + bx) / 2))
    v, tol = q["muro_cinza"]
    y_muro = None
    for y in range(*q["busca_px"]):
        if (np.abs(img[y, xm - 3:xm + 4].astype(np.int16) - v).max() <= tol):
            y_muro = y
            break
    # px -> pt na vertical (a escala do quadro)
    (_, p0), (_, p1) = Q.p2q(0, 0), Q.p2q(0, 100)
    k = (p1 - p0) / 100
    y_pt = (y_muro - p0) / k
    _, d1 = c["ducha"][1], c["ducha"][3]
    br = (c["braco"][0], d1 - 0.3, c["braco"][2], y_pt)
    cp = (c["canopla"][0], y_pt - 0.6, c["canopla"][2], y_pt)
    caixa = (cp[0], br[1], cp[2], cp[3])
    tl = FA.tela(out, Q, caixa, folga=5)
    b = tl.ret(br, 0.5)
    FA.sombra_q(tl, b, forca=0.30, dist=0.9, sigma=0.8)
    tl.pintar(b, FA.CROMO["escuro"])
    tl.pintar(tl.ret(((br[0] + br[2]) / 2 - 0.2, br[1], (br[0] + br[2]) / 2 + 0.25, br[3])), FA.CROMO["claro"])
    k_ = tl.ret(cp, 0.5)
    tl.pintar(k_, FA.CROMO["meio"])
    tl.contorno(k_, 0.3, FA.CROMO["contorno"])
    out = tl.gravar()
    print(f"    chuveiro do pisante: o braço cromado da placa até o muro (y {y_muro} px), com a canopla")
    return out


def piscina(img, q=PISCINA):
    out = img.copy()
    n = 0
    for x0, y0, x1, y1 in q["zonas"]:
        reg = out[y0:y1, x0:x1].astype(np.float32)
        esc = img[y0:y1, x0:x1].max(axis=2) < q["escuro"]
        for v in range(reg.shape[0]):
            e = esc[v]
            if not e.any():
                continue
            xs = np.arange(e.size)
            bons = ~e
            for ch in range(3):
                reg[v, e, ch] = np.interp(xs[e], xs[bons], reg[v, bons, ch])
            n += int(e.sum())
        out[y0:y1, x0:x1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    print(f"    piscina: {n} px de traço preto na borda do spa e no canto de baixo da piscina, na cor da borda")
    return out


def pivotantes_fora(img, q=PIVOT):
    out = img.copy()
    x0, x1 = q["x"]
    y0, y1 = q["y"]
    src = img[y0:y1, x0 + q["dx"]:x1 + q["dx"]].astype(np.float32)
    a = np.ones((y1 - y0, x1 - x0), np.float32)
    a[:, 0] = 0.5
    _misturar(out, x0, y0, src, a)
    print("    gourmet: os 2 painéis pivotantes junto à ilha fora; o travertino até o fio da bancada")
    return out


def filete_jardim1(Q, img, q=FILETE_J1):
    import revisao_terreo_casac_1311 as RT
    import materiais_terreo_casac_1311 as MT
    out = img.copy()
    x0, x1 = int(q["x"][0]), int(np.ceil(q["x"][1]))
    # a grama até a linha: o que não é verde nas linhas de cima vem de `grama_dy` acima
    g0, g1 = q["grama"]
    I = img.astype(np.int16)
    verde = (I[..., 1] > I[..., 0] + 8) & (I[..., 1] >= I[..., 2] - 5) & (I.sum(axis=2) < 400)
    for y in range(g0, g1):
        for x in range(x0, x1):
            if not verde[y, x]:
                out[y, x] = out[y + q["grama_dy"], x]
    # o piso logo abaixo, sem o verde: as linhas de `piso_dy` abaixo
    p0, p1 = q["piso"]
    out[p0:p1, x0:x1] = img[p0 + q["piso_dy"]:p1 + q["piso_dy"], x0:x1]
    out[g1:p0, x0:x1] = img[p1 + q["piso_dy"] - (p0 - g1):p1 + q["piso_dy"], x0:x1]
    # o filete (a conta de `filete_garagem`, a mesma pedra, os fios e a sombra)
    fq = dict(RT.FILETE_G, y=q["y"] + q["larg_m"] * Q.px_m / 2, x=q["x"], larg_m=q["larg_m"],
              pontos=(0, 0, 1, 1))
    w_ = q["larg_m"] * Q.px_m
    ya, yb = fq["y"] - w_ / 2, fq["y"] + w_ / 2
    X0, Y0 = int(np.floor(q["x"][0])) - 1, int(np.floor(ya)) - 3
    W, H = int(np.ceil(q["x"][1])) + 2 - X0, int(np.ceil(yb)) + 5 - Y0
    ss = fq["ss"]
    cx = RT._cob(q["x"][0], q["x"][1], W, X0, ss)
    a = np.outer(RT._cob(ya, yb, H, Y0, ss), cx)
    fx0, fy0, fx1, fy1 = fq["fonte"]
    T = MT.sem_emenda(img[fy0:fy1, fx0:fx1].astype(np.float32), H, W)
    o = out.astype(np.float32)
    reg = o[Y0:Y0 + H, X0:X0 + W]
    sb = np.outer(RT._cob(yb, yb + fq["sombra_px"], H, Y0, ss), cx)
    reg *= (1 - fq["sombra"] * sb)[..., None]
    reg[:] = reg * (1 - a[..., None]) + T * a[..., None]
    f = fq["fio_px"] / 2
    fio = np.outer(RT._cob(ya - f, ya + f, H, Y0, ss) + RT._cob(yb - f, yb + f, H, Y0, ss), cx)
    fio = np.clip(fio, 0, 1) * fq["fio_alfa"]
    reg[:] = reg * (1 - fio[..., None]) + np.float32(fq["fio"]) * fio[..., None]
    print(f"    jardim 1: a grama em linha reta até y {q['y']:.0f} e o filete de Bege Bahia ({w_:.1f} px) de parede a "
          "parede, com os fios e a sombrinha")
    return np.clip(np.round(o), 0, 255).astype(np.uint8)


def box_bhm2(img, q=BOX_BHM2):
    import pedidos_terreo_casac_1311 as PT
    out = img.copy()
    x0, y0, x1, y1 = q["ret"]
    H, W = y1 - y0, x1 - x0
    ax0, ay0, ax1, ay1 = q["amostra"]
    ref = img[ay0:ay1, ax0:ax1].reshape(-1, 3).astype(np.float32).mean(axis=0)
    T = _textura(img, q["amostra"], H, W, ref)
    m = np.ones((H, W), np.float32)
    for r in (q["chuveiro"], q["porta"]):
        rx0, ry0, rx1, ry1 = r
        m[max(0, ry0 - y0):ry1 - y0, max(0, rx0 - x0):rx1 - x0] = 0
    m = cv2.GaussianBlur(m, (0, 0), 0.8) * m + (m > 0) * 0          # a pena só para dentro
    m[:, 0] = np.minimum(m[:, 0], 0.6)
    _misturar(out, x0, y0, T, m)
    # o tracejado da claraboia, cinza e fino, de novo
    tr = PT.TRACO
    cx0, cy0, cx1, cy1 = q["clara"]
    X0, Y0, X1, Y1 = int(cx0) - 12, int(cy0) - 12, int(np.ceil(cx1)) + 13, int(np.ceil(cy1)) + 13
    ss = tr["ss"]
    M = np.zeros(((Y1 - Y0) * ss, (X1 - X0) * ss), np.uint8)
    for p0, p1 in (((cx0, cy0), (cx1, cy0)), ((cx1, cy0), (cx1, cy1)), ((cx1, cy1), (cx0, cy1)), ((cx0, cy1), (cx0, cy0))):
        PT._tracejado(M, p0, p1, X0, Y0, tr, ss)
    a = cv2.resize(M.astype(np.float32) / 255, (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA)
    out = PT.PS._pintar(out, a, X0, Y0, tr["cor"])
    print("    box do BH master 2: um piso só (o travertino do box), o chuveiro, e o tracejado da claraboia")
    return out


def tracos_cortina(img, qs=TRACOS_CORTINA):
    out = img.copy()
    n = 0
    for x0, y0, x1, y1, dy in qs:
        reg = img[y0:y1, x0:x1].astype(np.float32).mean(axis=2)
        med = float(np.median(img[y0 + dy:y1 + dy, x0:x1].astype(np.float32).mean(axis=2)))
        esc = cv2.dilate((reg < 0.72 * med).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
        ys, xs = np.nonzero(esc)
        out[ys + y0, xs + x0] = img[ys + y0 + dy, xs + x0]
        n += int(esc.sum())
    print(f"    cortinas dos quartos 3 e 2: {n} px dos traços pretos sobre os guarda-roupas fora")
    return out


def tapete_q1(img, q=TAPETE_Q1):
    out = img.copy()
    x0, x1 = q["x"]
    for y in range(q["linhas"][0], q["linhas"][1] + 1):
        am = np.concatenate([img[y, a:b] for a, b in q["amostra_x"]]).astype(np.float32)
        out[y, x0:x1] = np.round(np.median(am, axis=0)).astype(np.uint8)
    print("    quarto 1: o fio de baixo do tapete contínuo em frente ao pufe")
    return out


def cooktop(img, q=COOKTOP):
    out = img.copy()
    X0, Y0, X1, Y1 = q["caixa"]
    reg = img[Y0:Y1, X0:X1]
    I = reg.astype(np.int16)
    vidro = (I.max(axis=2) < q["vidro_max"]).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(vidro)
    i = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    gx, gy, gw, gh = st[i, :4]
    v = np.zeros_like(vidro)
    v[gy:gy + gh, gx:gx + gw] = 1                     # o retângulo do vidro
    fio = cv2.dilate(v, np.ones((3, 3), np.uint8)) & (1 - v)
    marrom = (I[..., 2] > I[..., 0] + 14) | (I.max(axis=2) > 200)
    resto = marrom & (cv2.dilate(v, np.ones((11, 11), np.uint8)) > 0) & (fio == 0) & (v == 0)
    resto = cv2.dilate(resto.astype(np.uint8), np.ones((3, 3), np.uint8)) & (1 - v) & (1 - fio)
    resto[:, q["ilha_x"] - X0:] = 0                  # a borda da ilha e o piso marrom da cozinha ficam
    dx = q["danae_dx"]
    esq = resto.copy()
    esq[:, gx + gw // 2:] = 0
    ys, xs = np.nonzero(esq)
    for y, x in zip(ys, xs):
        out[Y0 + y, X0 + x] = img[Y0 + y, X0 + x + dx]
    dir_ = (resto > 0) & (esq == 0)
    if dir_.any():
        sub = np.ascontiguousarray(out[Y0:Y1, X0:X1])
        m = (dir_ | (fio > 0) | (v > 0)).astype(np.uint8) * 255
        pint = cv2.inpaint(sub, m, 3, cv2.INPAINT_TELEA)
        sub[dir_] = pint[dir_]
        out[Y0:Y1, X0:X1] = sub
    ys, xs = np.nonzero(fio)
    out[Y0 + ys, X0 + xs] = np.uint8(q["fio"])
    print(f"    cozinha: o cooktop com o fio de inox escuro em volta do vidro; {int(resto.sum())} px da moldura e da tira "
          "marrom no Danae")
    return out


def _alfa_linha(txt, fonte, cx, base, X0, Y0, W, H):
    from PIL import Image, ImageDraw
    t = Image.new("L", (W * 4, H * 4), 0)
    ImageDraw.Draw(t).text(((cx - X0) * 4, (base - Y0) * 4), txt, font=fonte, fill=255, anchor="ms")
    return np.asarray(t.resize((W, H), Image.LANCZOS), np.float32) / 255


def louceiro1_rotulo(q=LOUCEIRO1):
    """As linhas do rótulo do louceiro 1 (texto, fonte, corpo em px da final, centro x, base), para a final e o 12K."""
    from PIL import ImageFont
    from rodape_entrega import FONTES
    f = ImageFont.truetype(str(FONTES / "Inter-SemiBold.otf"), 400)
    corpo = 400 * q["largura_ref"] / f.getlength(q["ref"]) * q["escala"]
    b0 = q["base"]
    return [("LOUCEIRO 1", str(FONTES / "Inter-SemiBold.otf"), corpo, q["centro_x"], b0),
            ("A: 2,41 m²", str(FONTES / "Inter-Regular.otf"), corpo, q["centro_x"], b0 + q["entrelinha"] * q["escala"])]


def louceiro1_apaga(img, q=LOUCEIRO1):
    out = img.copy()
    x0, y0, x1, y1 = q["apaga"]
    dy = q["apaga_dy"]
    out[y0:y1, x0:x1] = img[y0 + dy:y1 + dy, x0:x1]
    return out


def desenhar_linhas(out, linhas, cor, s=1.0, X0=0.0, Y0=0.0):
    """As linhas (texto, fonte, corpo, cx, base em px da final) na escala `s` a partir de (X0, Y0)."""
    from PIL import ImageFont
    for txt, fonte, corpo, cx, base in linhas:
        f = ImageFont.truetype(fonte, int(round(corpo * s * 4)))
        u, v = (cx - X0) * s, (base - Y0) * s
        W, H = int(f.getlength(txt) / 4) + 24, int(corpo * s * 2) + 12
        bx, by = int(u - W / 2), int(v - corpo * s * 1.4) - 4
        a = _alfa_linha(txt, f, u, v, bx, by, W, H)
        _misturar(out, bx, by, np.full((H, W, 3), cor, np.float32), a)
    return out


def louceiro1(img, q=LOUCEIRO1):
    out = img.copy()
    # a parede fina, no cinza das paredes
    px0, py0, px1, py1 = q["parede"]
    out[py0:py1, px0:px1] = 80
    # o rótulo de antes (e o retângulo cinza do "A:") sai: o piso de `apaga_dy` acima; volta no corpo do LOUCEIRO 2
    out = louceiro1_apaga(out, q)
    linhas = louceiro1_rotulo(q)
    out = desenhar_linhas(out, linhas, q["cor"])
    print(f"    louceiro 1: a parede fina no cinza das paredes; o rótulo reescrito ({linhas[0][2]:.1f} px de corpo)")
    return out


def rotulos_12k():
    """Os rótulos que o 12K redesenha nítidos sobre a saída do Topaz (a entrada do Topaz vai sem eles)."""
    return [{"apaga": louceiro1_apaga, "linhas": louceiro1_rotulo(), "cor": LOUCEIRO1["cor"]}]


def porta_circulacao(img, q=PORTA_CIRC):
    out = img.copy()
    x0, y0, x1, y1 = q["faixa"]
    src = img[y0:y1, x0 + q["dx"]:x1 + q["dx"]].astype(np.float32)
    a = np.ones((y1 - y0, x1 - x0), np.float32)
    a[:, 0] = 0.5
    _misturar(out, x0, y0, src, a)
    x0, y0, x1, y1 = q["parede"]
    out[y0:y1, x0:x1] = 80
    x0, y0, x1, y1 = q["piso"]
    out[y0:y1, x0:x1] = img[y0 + 5:y1 + 5, x0 + q["dx"]:x1 + q["dx"]]
    print("    circulação: o piso ao longo da porta de correr sem a faixa clara; a ponta da parede reta")
    return out


def batentes_louceiro2(img, qs=BATENTES_L2):
    out = img.copy()
    for b in qs:
        x0, y0, x1, y1 = b["ret"]
        out[y0:y1, x0:x1] = img[y0:y1, b["coluna"]][:, None]
    # o pontinho escuro sob o batente da esquerda
    out[822:825, 2394:2402] = img[826:829, 2394:2402]
    print("    louceiro 2: os 2 batentes viram parede; a folha quina com quina, do vão inteiro")
    return out


def _sombra(reg, a, sombras, px_m, onde):
    for s in sombras:
        sh = cv2.GaussianBlur(a, (0, 0), max(0.3, s["sig"] * px_m))
        Ms = np.float32([[1, 0, s["dx"] * px_m], [0, 1, s["dy"] * px_m]])
        sh = cv2.warpAffine(sh, Ms, (sh.shape[1], sh.shape[0]), flags=cv2.INTER_LINEAR, borderValue=0)
        reg *= (1 - s["forca"] * sh * onde)[..., None]
    return reg


def _estar_pecas(Q):
    """As poses das peças do estar (as mesmas contas de `mobiliario_terreo_casac_1311.estar`) e os alfas delas."""
    import mobiliario_terreo_casac_1311 as MB
    E = MB.ESTAR
    sh = (Q.H, Q.W)
    with contextlib.redirect_stdout(io.StringIO()):
        _, ms = MB.contorno(Q, [E["sofa"]])
        Ps = MB.ler("sala-de-estar/sofa-curvo-render-casa-a")
        cx, cy, (iou, g, wt, ht) = MB.encaixar(Q, Ps, ms)
        al = {"sofa": MB.RT._alfa_peca(Ps, cx, cy, wt, ht, g, sh)}
        x0, y0, x1, y1 = MB.RT.caixa_pdf(Q, E["mesa_centro"])
        Pm = MB.ler("sala-de-estar/mesa-centro-seixo-render-v2")
        d = x1 - x0
        al["mesa"] = MB.RT._alfa_peca(Pm, (x0 + x1) / 2, (y0 + y1) / 2, d, d * Pm.shape[0] / Pm.shape[1], 0.0, sh)
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        Po = MB.ler("sala-de-estar/poltrona-oliva-render-v2")
        oliva = []
        for i in E["oliva"]:
            a0, b0, a1, b1 = MB.RT.caixa_pdf(Q, i)
            hh = b1 - b0
            oliva.append(MB.RT._alfa_peca(Po, (a0 + a1) / 2, (b0 + b1) / 2, hh * Po.shape[1] / Po.shape[0], hh, 0.0, sh))
        al["oliva"] = np.maximum(*oliva)
        _, mc = MB.contorno(Q, [E["creme"]])
        ys, xs = np.nonzero(mc)
        pc = np.array([xs.mean(), ys.mean()])
        gc = MB.frente(np.array([mx, my]) - pc)
        a0, b0, a1, b1 = MB.RT.caixa_pdf(Q, E["creme"])
        lado = 0.80 * max(a1 - a0, b1 - b0)
        Pc = MB.ler("sala-de-estar/poltrona-creme-madeira-render")
        al["creme"] = MB.RT._alfa_peca(Pc, pc[0], pc[1], lado * Pc.shape[1] / Pc.shape[0], lado, gc, sh)
        pose_creme = (pc[0], pc[1], lado, gc)
        ap = []
        for i in E["apoio"]:
            a0, b0, a1, b1 = MB.RT.caixa_pdf(Q, i)
            D = ((a1 - a0) + (b1 - b0)) / 2
            ap.append(MB.RT._alfa_peca(MB.ler("sala-de-estar/mesa-apoio-escura"), (a0 + a1) / 2, (b0 + b1) / 2, D, D,
                                       0.0, sh))
        al["apoio"] = np.maximum.reduce(ap)
    return al, pose_creme


def entorno_estar(Q, img, q=ESTAR_ENTORNO):
    import mobiliario_terreo_casac_1311 as MB
    E = MB.ESTAR
    with contextlib.redirect_stdout(io.StringIO()):
        par = MB.BS.quieto(MB.FA.paredes_pdf, Q) > 0.3
        _, tap = MB.contorno(Q, [E["tapete"]])
        _, vaso = MB.contorno(Q, [E["vaso"]])
    al, _ = _estar_pecas(Q)
    a_sofa = al["sofa"]
    sofa = a_sofa > 0.02
    ys, xs = np.nonzero(vaso)
    vx0, vy0, vx1, vy1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    perto_vaso = np.zeros_like(vaso)
    f = q["vaso_folga"]
    perto_vaso[vy0 - f:vy1 + f, vx0 - f:vx1 + f] = True
    rx0, ry0, rx1, ry1 = q["plantas_antes"]
    perto_vaso[ry0:ry1, rx0:rx1] = True
    anel_sofa = MB.RT.dilatar(sofa, q["sofa_folga"]) & ~sofa
    zona = (perto_vaso | anel_sofa) & ~sofa & ~tap & ~MB.RT.dilatar(par, 1)
    zona[:, q["cortina_x"]:] = False
    # o travertino: a amostra limpa do estar, sem emenda, no tom do piso logo em volta da zona
    ys, xs = np.nonzero(zona)
    X0, Y0, X1, Y1 = xs.min() - 2, ys.min() - 2, xs.max() + 3, ys.max() + 3
    anel = MB.RT.dilatar(zona, 6) & ~MB.RT.dilatar(zona, 2) & ~sofa & ~tap & ~par
    anel[:, q["cortina_x"]:] = False
    ref = np.median(img[anel].astype(np.float32), axis=0)
    T = _textura(img, q["amostra"], Y1 - Y0, X1 - X0, ref)
    m = _pena(zona[Y0:Y1, X0:X1], 0.8)
    out = img.copy()
    _misturar(out, X0, Y0, T, m)
    # a sombra do sofá (a mesma do `pousar`), só na zona
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    reg = _sombra(reg, a_sofa[Y0:Y1, X0:X1].astype(np.float32), MB.BT.SOMBRAS["movel"], Q.px_m, m)
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    # os vasos da biblioteca (a folhagem da sala íntima da Casa A, aprovada no hall), nos centros das plantas de antes
    for nome, (cx, cy), D in q["vasos"]:
        out = MB.pousar(out, MB.ler(nome), cx, cy, D, D, 0.0, "baixa", par)
    print(f"    estar: {int(zona.sum())} px em volta do sofá curvo e dos vasos no travertino (o desenho velho, o halo e a "
          f"sombra dupla fora), a sombra do sofá; {len(q['vasos'])} vasos de folhagem da biblioteca")
    return out


def _tapete_textura(a_tap, q=None):
    """O miolo do tapete manchado da biblioteca esticado uma vez sobre a caixa do tapete do PDF (a textura, a caixa)."""
    q = q or TAPETE_ESTAR
    ys, xs = np.nonzero(a_tap > 0.01)
    X0, Y0, X1, Y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    H, W = Y1 - Y0, X1 - X0
    P = cv2.imread(str(AQUI.parents[0] / "biblioteca-objetos" / q["png"]), cv2.IMREAD_UNCHANGED)
    h, w = P.shape[:2]
    lado = int(min(h, w) * q["miolo"])
    my, mx = (h - lado) // 2, (w - lado) // 2
    M = P[my:my + lado, mx:mx + lado, :3].astype(np.float32)
    k = max(H, W) / lado
    M = cv2.resize(M, (int(np.ceil(lado * k)), int(np.ceil(lado * k))), interpolation=cv2.INTER_CUBIC)
    oy, ox = (M.shape[0] - H) // 2, (M.shape[1] - W) // 2
    return M[oy:oy + H, ox:ox + W], (X0, Y0, X1, Y1)


def tapete_estar(Q, img, q=TAPETE_ESTAR):
    """O tapete manchado da biblioteca (`tapete-redondo-render-v2`, o da Casa A) no contorno orgânico do tapete do PDF
    da Casa C: o miolo do redondo (o quadrado inscrito, sem a borda) esticado uma vez sobre a caixa do tapete, sem
    repetir; a luz, as sombras das peças e o grão do tapete de antes (a razão à lã lisa) e as peças por cima ficam."""
    import mobiliario_terreo_casac_1311 as MB
    E = MB.ESTAR
    with contextlib.redirect_stdout(io.StringIO()):
        a_tap, tap = MB.contorno(Q, [E["tapete"]])
    al, _ = _estar_pecas(Q)
    F = np.maximum.reduce([np.clip(v, 0, 1) for v in al.values()])
    T, (X0, Y0, X1, Y1) = _tapete_textura(a_tap, q)
    H, W = Y1 - Y0, X1 - X0
    a = a_tap[Y0:Y1, X0:X1].astype(np.float32)
    f = F[Y0:Y1, X0:X1]
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    livre = (a > 0.98) & (f < 0.02)
    la = reg.mean(axis=2)
    la_suave = cv2.GaussianBlur(la, (0, 0), q["luz_sigma"])
    la_ref = float(np.median(la[livre]))
    s_ = np.clip(la_suave / la_ref, q["luz_min"], 1.08)
    s_[a <= 0.98] = 1.0
    lisa = np.median(reg[livre], axis=0)
    T = T - T.reshape(-1, 3).mean(axis=0) + np.float32(q["tom"]) if q.get("tom") else T
    novo = reg + (a * (1 - f))[..., None] * (T - lisa[None, None]) * s_[..., None]
    out = img.copy()
    out[Y0:Y1, X0:X1] = np.clip(np.round(novo), 0, 255).astype(np.uint8)
    print(f"    estar: o tapete manchado da biblioteca no contorno orgânico do PDF ({W}x{H} px), as peças por cima")
    return out


# (14/11, "REPRESENTE ESSA POLTRONA COM A ALMOFADA", a foto de uma poltrona curva de linho greige com uma almofada
# redonda marrom) a poltrona creme de madeira do estar troca pela curva de bouclé greige com a almofada redonda de veludo
# marrom (gerada em 2K no Higgsfield, `gpt_image_2_6`, vista de cima, o fundo tirado), na mesma pose (o centro, o lado e
# o giro de `mobiliario_terreo_casac_1311.estar`); por baixo, o tapete manchado e o travertino refeitos
# (14/11, "AUMENTE O TAMANHO PROPORCIONALMENTE DA ALMOFADA E POLTRONA, CONFORME DEMAIS ALMOFADAS") `escala` 1,25: a
# poltrona no tamanho do símbolo do PDF (53 px; o lado da creme era 0,80 dele) e a almofada franzida no diâmetro das
# almofadas redondas do sofá curvo (19,6 px)
POLTRONA_CURVA = {"png": "sala-de-estar/poltrona-curva-boucle-almofada", "folga_px": 7, "escala": 1.25,
                  "amostra": (2215, 1606, 2295, 1640)}


def _trocar_peca(Q, img, chave, png, cx, cy, wt, ht, g, sombra, folga_px, amostra, mais=()):
    """A peça `chave` do estar sai (a zona dela com `folga_px`, fora das outras peças): por baixo, o tapete manchado onde
    há tapete e o travertino fora dele; a peça nova (`png`) pousa no centro, no tamanho e no giro dados."""
    import mobiliario_terreo_casac_1311 as MB
    E = MB.ESTAR
    with contextlib.redirect_stdout(io.StringIO()):
        par = MB.BS.quieto(MB.FA.paredes_pdf, Q) > 0.3
        a_tap, _ = MB.contorno(Q, [E["tapete"]])
    al, _ = _estar_pecas(Q)
    velha = al[chave] > 0.02
    outras = np.maximum.reduce([np.clip(v, 0, 1) for k, v in al.items() if k != chave]) > 0.02
    zona = MB.RT.dilatar(velha, folga_px) & ~outras & ~par
    ys, xs = np.nonzero(zona)
    X0, Y0, X1, Y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    T, (tx0, ty0, tx1, ty1) = _tapete_textura(a_tap)
    fundo_tap = np.zeros((Y1 - Y0, X1 - X0, 3), np.float32)
    sy0, sx0 = max(Y0, ty0), max(X0, tx0)
    sy1, sx1 = min(Y1, ty1), min(X1, tx1)
    if sy1 > sy0 and sx1 > sx0:
        fundo_tap[sy0 - Y0:sy1 - Y0, sx0 - X0:sx1 - X0] = T[sy0 - ty0:sy1 - ty0, sx0 - tx0:sx1 - tx0]
    anel = MB.RT.dilatar(zona, 5) & ~zona & ~outras & ~par & (a_tap < 0.02)
    ref = np.median(img[anel].astype(np.float32), axis=0) if anel.any() else None
    trav = _textura(img, amostra, Y1 - Y0, X1 - X0, ref)
    at = np.clip(a_tap[Y0:Y1, X0:X1], 0, 1)[..., None]
    fundo = fundo_tap * at + trav * (1 - at)
    out = img.copy()
    _misturar(out, X0, Y0, fundo, _pena(zona[Y0:Y1, X0:X1], 0.6))
    P = MB.ler(png)
    for pcx, pcy, pwt, pht, pg in ((cx, cy, wt, ht, g),) + tuple(mais):
        out = MB.pousar(out, P, pcx, pcy, pwt, pht, pg, sombra, par)
    return out


def poltrona_creme(Q, img, q=POLTRONA_CURVA):
    import mobiliario_terreo_casac_1311 as MB
    _, (cx, cy, lado, g) = _estar_pecas(Q)
    P = MB.ler(q["png"])
    L = lado * q["escala"]
    out = _trocar_peca(Q, img, "creme", q["png"], cx, cy, L * P.shape[1] / P.shape[0], L, g, "movel", q["folga_px"],
                       q["amostra"])
    print(f"    estar: a poltrona curva de bouclé greige com a almofada redonda marrom no lugar da creme (giro {g:.0f}°)")
    return out


# (14/11, "A MESA DE CENTRO É NESSE MODELO, REDONDA. REPRESENTE ASSIM COM ADORNO SOBRE ELA", a foto de uma mesa redonda
# de nogueira com o tampo em três gomos) a mesa seixo troca pela redonda de nogueira em três gomos, com o vaso de galhos
# secos e os livros de linho por cima (gerada em 2K no Higgsfield, `gpt_image_2_6`, o fundo tirado), no centro do
# retângulo do PDF, o diâmetro na média dos lados dele (`escala`)
MESA_REDONDA = {"png": "sala-de-estar/mesa-centro-redonda-nogueira-adorno", "escala": 1.05, "folga_px": 6,
                "amostra": (2215, 1606, 2295, 1640)}


def mesa_centro(Q, img, q=MESA_REDONDA):
    import mobiliario_terreo_casac_1311 as MB
    x0, y0, x1, y1 = MB.RT.caixa_pdf(Q, MB.ESTAR["mesa_centro"])
    D = (x1 - x0 + y1 - y0) / 2 * q["escala"]
    out = _trocar_peca(Q, img, "mesa", q["png"], (x0 + x1) / 2, (y0 + y1) / 2, D, D, 0.0, "mesa", q["folga_px"],
                       q["amostra"])
    print(f"    estar: a mesa de centro redonda de nogueira em três gomos, com o adorno ({D:.0f} px de diâmetro)")
    return out


# (14/11, "MESINHAS TOM CINZA METÁLICO") as mesinhas seixo nas pontas do sofá do conjunto da esquerda
# (`proposta_estar_casac_1311.SEIXOS`, px) no cinza metálico da foto (BGR, a mediana), com a luz delas (um pouco mais de
# contraste, o brilho do metal)
MESINHAS = {"rets": [(1716, 1530, 1752, 1590), (1972, 1526, 2010, 1586)], "cor": (138, 139, 141), "gama": 1.25,
            "marrom": 25}


def mesinhas_cinza(img, q=MESINHAS):
    out = img.copy()
    n = 0
    for x0, y0, x1, y1 in q["rets"]:
        reg = img[y0:y1, x0:x1]
        I = reg.astype(np.int16)
        m = (I[..., 2] - I[..., 0]) > q["marrom"]
        Y = reg.astype(np.float32) @ np.float32([0.114, 0.587, 0.299])
        r = (Y / max(float(np.median(Y[m])), 1.0)) ** q["gama"]
        o = reg.astype(np.float32)
        novo = np.float32(q["cor"])[None, None] * r[..., None]
        o[m] = novo[m]
        out[y0:y1, x0:x1] = np.clip(np.round(o), 0, 255).astype(np.uint8)
        n += int(m.sum())
    print(f"    estar: as mesinhas seixo em cinza metálico ({n} px)")
    return out


# (14/11, "O TOM DESSAS DUAS POLTRONAS DEVE SER O DA IMAGEM", a foto de uma poltrona de linho greige; depois, "essas
# poltronas precisam ficar perfeitas") as 2 poltronas oliva do estar trocam pela poltrona de linho greige com pés de
# nogueira (gerada em 2K no Higgsfield, `gpt_image_2_6`, o fundo tirado), nas mesmas poses (o centro e a altura do
# retângulo do PDF, viradas para a mesa); antes, a oliva recolorida (os fios escuros do desenho dela apareciam)
OLIVA_GREIGE = {"png": "sala-de-estar/poltrona-greige-linho-pes-nogueira", "folga_px": 6, "escala": 1.0,
                "amostra": (2215, 1606, 2295, 1640)}


def poltronas_oliva(Q, img, q=OLIVA_GREIGE):
    import mobiliario_terreo_casac_1311 as MB
    P = MB.ler(q["png"])
    poses = []
    for i in MB.ESTAR["oliva"]:
        a0, b0, a1, b1 = MB.RT.caixa_pdf(Q, i)
        hh = (b1 - b0) * q["escala"]
        poses.append(((a0 + a1) / 2, (b0 + b1) / 2, hh * P.shape[1] / P.shape[0], hh, 0.0))
    out = _trocar_peca(Q, img, "oliva", q["png"], *poses[0], "movel", q["folga_px"], q["amostra"], mais=poses[1:])
    print("    estar: as 2 poltronas oliva trocadas pela de linho greige com pés de nogueira")
    return out


# (14/11, "ENCOSTO E ASSENTO DAS CADEIRAS EM AZUL NO TOM DA IMAGEM ANEXA", a foto de uma cadeira estofada azul-marinho)
# o tecido das 10 cadeiras do jantar (o encosto oliva e o assento caramelo) no azul-marinho da foto (BGR, o tom médio
# de cada parte), com a luz de cada uma (a razão da luminância à mediana, ** `gama`); a madeira e os fios escuros ficam
JANTAR_AZUL = {"encosto": (92, 54, 32), "assento": (104, 64, 38), "sat_min": 45, "val_min": 45, "gama": 0.9,
               "matiz_encosto": (22, 45)}


def cadeiras_jantar(Q, img, q=JANTAR_AZUL):
    import mobiliario_terreo_casac_1311 as MB
    J = MB.JANTAR
    with contextlib.redirect_stdout(io.StringIO()):
        a_mesa, _ = MB.RT.mascara_pdf(Q, [J["mesa"]])
        P = MB.ler("sala-de-jantar/cadeira-jantar-oliva-render")
        ca = np.zeros(img.shape[:2], np.float32)
        for i, g in J["cadeiras"]:
            x0, y0, x1, y1 = MB.RT.caixa_pdf(Q, i)
            wt = J["larg"]
            ht = wt * P.shape[0] / P.shape[1]
            ca = np.maximum(ca, MB.RT._alfa_peca(P, (x0 + x1) / 2, (y0 + y1) / 2, wt, ht, g, img.shape[:2]))
    m = (ca > 0.5) & (a_mesa < 0.01)
    ys, xs = np.nonzero(m)
    X0, Y0, X1, Y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    reg = img[Y0:Y1, X0:X1]
    hsv = cv2.cvtColor(reg, cv2.COLOR_BGR2HSV).astype(np.int16)
    mm = m[Y0:Y1, X0:X1] & (hsv[..., 1] >= q["sat_min"]) & (hsv[..., 2] >= q["val_min"])
    h0, h1 = q["matiz_encosto"]
    enc = mm & (hsv[..., 0] >= h0) & (hsv[..., 0] <= h1)          # o oliva (matiz OpenCV 22-45)
    ass = mm & ~enc                                                 # o caramelo
    Y = reg.astype(np.float32) @ np.float32([0.114, 0.587, 0.299])
    out = img.copy()
    o = out[Y0:Y1, X0:X1].astype(np.float32)
    for parte, cor in ((enc, q["encosto"]), (ass, q["assento"])):
        if not parte.any():
            continue
        r = (Y / max(float(np.median(Y[parte])), 1.0)) ** q["gama"]
        novo = np.float32(cor)[None, None] * r[..., None]
        o[parte] = novo[parte]
    # a borda do tecido (o antisserrilhado) acompanha: a vizinhança de 1 px, metade
    borda = (cv2.dilate(mm.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0) & ~mm & m[Y0:Y1, X0:X1]
    o[borda] = o[borda] * 0.5 + (np.float32(q["encosto"]) * (Y[borda] / 120.0)[:, None]) * 0.5
    out[Y0:Y1, X0:X1] = np.clip(np.round(o), 0, 255).astype(np.uint8)
    print(f"    jantar: o encosto ({int(enc.sum())} px) e o assento ({int(ass.sum())} px) das 10 cadeiras em azul-marinho")
    return out


# (14/11, "ESSE APARADOR TEM O TOM CINZA CONFORME FOTO", a foto de um aparador laqueado cinza-fendi; depois, vendo o
# resultado com pontos do freijó soltos: "deixe como estava em vez do cinza", fora do `aplicar`) a madeira do
# aparador do hall (`revisao_terreo_casac_1311.APARADOR`, o freijó do PNG) no cinza da foto (BGR, a mediana), com a luz
# dela; os objetos (o vaso, os livros, a tigela) ficam
APARADOR_CINZA = {"cor": (112, 120, 130), "gama": 0.8, "matiz": (5, 28), "sat_min": 85, "val_max": 225, "folga_px": 2}


def aparador_cinza(img, q=APARADOR_CINZA):
    import revisao_terreo_casac_1311 as RT
    x0, y0, x1, y1 = RT.APARADOR["ret"]
    f = q["folga_px"]
    X0, Y0, X1, Y1 = int(x0) - f, int(y0) - f, int(np.ceil(x1)) + f, int(np.ceil(y1)) + f
    reg = img[Y0:Y1, X0:X1]
    hsv = cv2.cvtColor(reg, cv2.COLOR_BGR2HSV).astype(np.int16)
    mad = (hsv[..., 0] >= q["matiz"][0]) & (hsv[..., 0] <= q["matiz"][1]) & (hsv[..., 1] >= q["sat_min"]) & \
        (hsv[..., 2] <= q["val_max"])
    # os objetos (a tigela de travertino, os livros, o vaso) e uma volta de 1 px ficam fora
    n, lab, st, _ = cv2.connectedComponentsWithStats(mad.astype(np.uint8))
    mad = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= 200])
    Y = reg.astype(np.float32) @ np.float32([0.114, 0.587, 0.299])
    r = (Y / max(float(np.median(Y[mad])), 1.0)) ** q["gama"]
    o = reg.astype(np.float32)
    novo = np.float32(q["cor"])[None, None] * r[..., None]
    o[mad] = novo[mad]
    out = img.copy()
    out[Y0:Y1, X0:X1] = np.clip(np.round(o), 0, 255).astype(np.uint8)
    print(f"    hall: o aparador no cinza da foto ({int(mad.sum())} px de madeira), os objetos por cima")
    return out


ANTES_DEPOIS_COMMIT = "2497eb0"
ANTES_DEPOIS = {"deck": (600, 985, 1125, 1300), "chuveiro_pisante": (1140, 1780, 1240, 1860),
                "piscina": (900, 1440, 1100, 1645), "gourmet_jardim1": (1100, 830, 1250, 1170),
                "box_bh_master2": (795, 895, 900, 980), "cortinas_quartos": (1160, 320, 1720, 380),
                "tapete_quarto1": (1990, 545, 2130, 640), "cozinha_louceiros": (2150, 380, 2480, 900),
                "circulacao": (2255, 690, 2320, 850), "estar": (1660, 1330, 2420, 1645), "jantar": (2060, 920, 2260, 1200),
                "hall_aparador": (2290, 1185, 2490, 1250), "escrivaninhas": (1170, 500, 2180, 760),
                "quarto1_criado": (2085, 340, 2180, 440)}


def antes_depois(antes, depois, R):
    for nome, (x0, y0, x1, y1) in ANTES_DEPOIS.items():
        a, b = antes[y0:y1, x0:x1], depois[y0:y1, x0:x1]
        k = min(4.0, 1600 / max(a.shape[:2]))
        sz = (int(a.shape[1] * k), int(a.shape[0] * k))
        a = cv2.resize(a, sz, interpolation=cv2.INTER_CUBIC)
        b = cv2.resize(b, sz, interpolation=cv2.INTER_CUBIC)
        j = np.vstack([a, np.full((16, sz[0], 3), 255, np.uint8), b]) if sz[0] > sz[1] * 1.3 else \
            np.hstack([a, np.full((sz[1], 16, 3), 255, np.uint8), b])
        t = np.full((44, j.shape[1], 3), 255, np.uint8)
        cv2.putText(t, "ANTES | DEPOIS" if sz[0] <= sz[1] * 1.3 else "ANTES (em cima) | DEPOIS (embaixo)", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (40, 40, 40), 2, cv2.LINE_AA)
        cv2.imwrite(str(R / f"POE642_CasaC_PH_Terreo_1411_{nome}_antes_depois.jpg"), np.vstack([t, j]),
                    [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"    antes e depois (14/11): {', '.join(ANTES_DEPOIS)}")


# (14/11, "preencheu o vão entre o criado mudo e a cama, com criado mudo?", a cabeceira do quarto 1) entre o criado
# redondo e o lado da cama havia uma faixa escura de 3 px (a sombra da cama, dura, até a parede) que com o lençol branco
# lia como uma peça a mais: as linhas `linhas` viram o vinílico do quarto (as de `fonte_y`, logo acima do criado, na
# mesma coluna), com a sombra curta da cama no piso (`sombra`, da linha de cima para a da cama)
CRIADO_Q1 = {"x": (2119, 2163), "linhas": (399, 404), "fonte_y": 351, "sombra": (0.0, 0.04, 0.10, 0.18, 0.26)}


def criado_q1(img, q=CRIADO_Q1):
    out = img.copy()
    x0, x1 = q["x"]
    y0, y1 = q["linhas"]
    fy = q["fonte_y"]
    reg = img[fy:fy + (y1 - y0), x0:x1].astype(np.float32)
    reg *= (1 - np.float32(q["sombra"]))[:, None, None]
    # o criado redondo e a sombra dele ficam (o escuro dele acima da faixa não muda: só as linhas da faixa)
    out[y0:y1, x0:x1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    print("    quarto 1: o vão entre o criado e a cama no vinílico, com a sombra curta da cama (sem a faixa escura)")
    return out


# (14/11, "ESSAS DUAS POLTRONAS DEVEM TER O ESTILO E TOM DE COR DA IMAGEM 2", proposta P1 escolhida e "clareie um pouco o
# azul marinho das poltronas, para que possamos ver os contornos dela e a base nogueira") as 2 poltronas de couro
# caramelo do conjunto da esquerda (`proposta_estar_casac_1311.PECAS`) trocam pela P1 (azul-marinho, braço rolado, base de
# nogueira; gerada em 2K no Higgsfield) com o tecido azul clareado (`clarear`: o brilho, HSV, e um pouco menos de
# saturação), a madeira igual; por baixo, o tapete liso do conjunto onde ele está (x >= `tapete_x0`) e o travertino fora
POLTRONAS_AZUIS = {"png": "sala-de-estar/poltrona-azul-p1-clara", "fonte": "propostas-estar-c/poltrona-azul-p1.png",
                   "clarear": 1.45, "sat": 0.85, "matiz": (95, 135), "folga_px": 8,
                   "tapete_x0": 1713.3, "tapete_y": (1342.2, 1551.2),
                   "amostra_tapete": (1758, 1490, 1798, 1526), "amostra_trav": (1780, 1604, 1940, 1632)}


def poltrona_azul_png(q=POLTRONAS_AZUIS):
    """O PNG da P1 com o azul clareado (gravado na biblioteca; refeito se a fonte mudar)."""
    bib = AQUI.parents[0] / "biblioteca-objetos" / "02-terreo" / "sala-de-estar"
    P = cv2.imread(str(bib / q["fonte"]), cv2.IMREAD_UNCHANGED)
    hsv = cv2.cvtColor(P[..., :3], cv2.COLOR_BGR2HSV).astype(np.float32)
    azul = (hsv[..., 0] >= q["matiz"][0]) & (hsv[..., 0] <= q["matiz"][1]) & (hsv[..., 1] > 50)
    hsv[..., 2] = np.where(azul, np.clip(hsv[..., 2] * q["clarear"], 0, 255), hsv[..., 2])
    hsv[..., 1] = np.where(azul, hsv[..., 1] * q["sat"], hsv[..., 1])
    P[..., :3] = cv2.cvtColor(np.round(hsv).astype(np.uint8), cv2.COLOR_HSV2BGR)
    cv2.imwrite(str(bib / (q["png"].split("/")[-1] + ".png")), P)


def poltronas_azuis(Q, img, q=POLTRONAS_AZUIS):
    import mobiliario_terreo_casac_1311 as MB
    import proposta_estar_casac_1311 as PE
    poltrona_azul_png(q)
    with contextlib.redirect_stdout(io.StringIO()):
        par = MB.BS.quieto(MB.FA.paredes_pdf, Q) > 0.3
    out = img.copy()
    P = MB.ler(q["png"])
    for peca, (x0, y0, x1, y1), g, _ in PE.PECAS:
        if peca != "poltrona":
            continue
        f = q["folga_px"]
        X0, Y0, X1, Y1 = int(x0) - f, int(y0) - f, int(np.ceil(x1)) + f, int(np.ceil(y1)) + f
        H, W = Y1 - Y0, X1 - X0
        ss = 8
        at = np.outer(RT_cob(q["tapete_y"][0], q["tapete_y"][1], H, Y0, ss), RT_cob(q["tapete_x0"], 1e9, W, X0, ss))
        # o tom de cada um: o tapete logo à direita da zona, o travertino logo à esquerda
        ref_t = np.median(img[Y0:Y1, X1 + 2:X1 + 8].reshape(-1, 3).astype(np.float32), axis=0)
        ref_v = np.median(img[Y0:Y1, X0 - 8:X0 - 2].reshape(-1, 3).astype(np.float32), axis=0)
        Tt = _textura(img, q["amostra_tapete"], H, W, ref_t)
        Tv = _textura(img, q["amostra_trav"], H, W, ref_v)
        fundo = Tt * at[..., None] + Tv * (1 - at[..., None])
        m = np.ones((H, W), np.float32)
        m[[0, -1], :] = 0.5
        m[:, [0, -1]] = 0.5
        _misturar(out, X0, Y0, fundo, m)
        out = MB.pousar(out, P, (x0 + x1) / 2, (y0 + y1) / 2, y1 - y0, x1 - x0, g, "movel", par)
    print("    estar: as 2 poltronas de couro caramelo trocadas pela P1 azul-marinho (clareada), com a base de nogueira")
    return out


def RT_cob(a0, a1, n, o, ss):
    import revisao_terreo_casac_1311 as RT
    return RT._cob(a0, a1, n, o, ss)


def aplicar(Q, out):
    out = descricao_deck(out)
    out = banco_deck(out)
    out = vestigios_jardim(out)
    out = cano_ducha(Q, out)
    out = piscina(out)
    out = pivotantes_fora(out)
    out = filete_jardim1(Q, out)
    out = box_bhm2(out)
    out = tracos_cortina(out)
    out = tapete_q1(out)
    out = cooktop(out)
    out = louceiro1(out)
    out = porta_circulacao(out)
    out = batentes_louceiro2(out)
    out = tapete_estar(Q, out)
    out = poltrona_creme(Q, out)
    out = mesa_centro(Q, out)
    out = entorno_estar(Q, out)
    out = mesinhas_cinza(out)
    out = poltronas_oliva(Q, out)
    out = cadeiras_jantar(Q, out)
    out = criado_q1(out)
    out = poltronas_azuis(Q, out)
    # (o aparador cinza saiu: "deixe como estava em vez do cinza"; `aparador_cinza` fica, sem uso)
    return out

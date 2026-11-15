"""A revisão do Térreo da Casa C de 15/11 (os recortes do usuário, um a um), no fim de `revisao_terreo_casac_1411.aplicar`.

Em px da final de 3840:
- **"FALTOU A REPRESENTAÇÃO DO ARMARIO DENTRO DO ESCRITÓRIO NO TOM QUE DEFINIMOS"** (`armarios_pdf`): o armário em L do
  escritório (DOC_LINHAS 88846, embaixo, e 88851, à direita) na cor dos armários da cozinha
  (`revisao_terreo_casac_1311.COZINHA["cor_armario"]`), lisa, com a borda um tom abaixo e a sombra curta.
- **"ESSE ARMARIO DA CIRCULAÇÃO É NO TOM QUE DEFINIMOS, NÃO FREIJÓ"**, **"ESSE ARMARIO TAMBÉM NA COR QUE DEFINIMOS E O DO
  LOUCEIRO"** (`armarios_px`): o armário comprido da circulação, o da circulação junto ao jantar (o dos arcos nas pontas)
  e o L inteiro do louceiro 2 (até a parede da direita) na mesma cor (a madeira de cada um, achada pelo tom, vira a cor
  lisa, com a face um tom abaixo só no contorno de fora; cada retângulo para no fio do contorno, e o fio, a sombra e os
  arcos ficam).
- **"BANCADA E CUBA DO LAVABO EM GRANITO MARROM"** (`lavabo_bancada`): as 3 peças da bancada do lavabo (ARQ_BANCADAS) no
  marrom tabaco (o mesmo da área de serviço, `revisao_terreo_casac_1311.BANCADA_SERV`); na peça da cuba, a cuba esculpida
  no mesmo granito, com a luz dela (a razão da luminância, suavizada); a torneira fica; o fio da borda nos lados livres.
- **"PORTA DO LAVABO É NO TOM ESCURO DE PONTA A PONTA"** (`lavabo_porta`): a ponta clara da folha (x 2466 a 2475) com o
  perfil da folha escura.
- **"CORRIGIR PAREDE ... UMA MARCAÇÃO QUE NÃO FOI COMPLETADA COM PAREDE"** (`louceiro2_parede`): a parede de dentro do
  louceiro 2 (ARQ_PAREDE 2282,3 a 2291,3) até o canto de cima (o quadrinho de madeira no canto vira parede).
- **"MELHORE A REPRESENTAÇÃO DAS CORTINAS NESSAS REGIÕES"** (`cortinas_estar`): nas duas janelas do estar junto ao
  gramado, a cortina C4 (`regras_terreo_casab_1311.cortina_desenho`) só nos trechos do PDF (ARQ_MOBILIÁRIO: dois em cada
  janela), num linho um tom abaixo e com a sombra inteira, para ler no travertino claro; o resto do trilho e a cortina
  apagada de antes, com os pontinhos cinzas da borda dela, saem (o travertino do lugar; a planta e o vidro ficam).
- **"USE O MESMO MODELO DE PLANTAS ... UTILIZE O DE CIMA DUPLICADO"**: em `revisao_terreo_casac_1411.ESTAR_ENTORNO`.
- **"USE O TOM DE GRAMA MAIS SÓBRIO"** (`jardins_inverno`): a grama dos dois jardins de inverno (o verde ligado ao rótulo)
  no tom do gramado do lote (a média e o desvio de L, a e b casados com os dele, `forca`); o X e os rótulos ficam.
- **"USE O MESMO TOM DA BANCADA COMO SOLEIRA DAS JANELAS DA COZINHA"** (`soleiras_cozinha`): a faixa marrom entre as
  janelas e a bancada da cozinha no Dekton Danae da bancada (`terreo_casaa_1011.danae`).
- **"CORRIJA A MESINHA REDONDA, COM TOM NOGUEIRA, NA SUITE MASTER"** (`mesinha_master`): a mesa de apoio redonda do PDF
  (88686) em nogueira (o tampo da mesa de centro redonda de nogueira da biblioteca), com a borda e a sombra curta; a
  mesinha de antes (maior que o círculo, com a sombra) sai antes, pelo vinílico de um trecho limpo do quarto.
- **"MELHORE O ASPECTO DA REPRESENTAÇÃO DA SOLEIRA DA JANELA DO ESCRITÓRIO"** (`escritorio_janela`): no vão da parede
  (x 2713,7 a 2800,3), a soleira no bege das soleiras da Casa C, lisa, com os fios das arestas (antes, um trilho
  metálico); os batentes em parede; a folha de correr do PDF (x 2684 a 2774, logo dentro) em vidro claro, sem o preto.
- **"COMPLETE O BOX ATÉ ENCOSTAR NA PAREDE DO BH. EXTERNO"** (`box_bh_externo`): o vidro do box até a parede de baixo
  (sem as 2 colunas do fundo escuro do rótulo).
- **"REMOVA ESSES RESTOS DE PISO ANTIGO"** (acima da janela do quarto de serviço e ao lado da bancada) e **"REMOVA OS
  RESÍDUOS DE PISO ANTIGO NESSA ÁREA ENTRE A COZINHA E ÁREA DE SERVIÇO"** (`restos_piso`): os pontinhos que destoam do
  piso marrom (mais claros ou mais escuros que a mediana do lugar) saem por inpaint; as paredes, a folha de correr e
  as soleiras ficam; a faixa escura do piso antigo no vão entre a cozinha e a área de serviço vira o piso do lado
  (`faixa_cozinha_servico`, com as bordas esfumadas).
- **"CORRIJA O FUNDO DESSE RÓTULO. TEM QUE SER PISO!"** (CLOSET MASTER 2, opção B): em `rotulos_kalam_casac.apagar`, a
  referência do piso é o de dentro da própria linha (entre as letras), não a volta (que pegava o guarda-roupa).
- **"CORRIJA ESSA ÁREA DE CIRCULAÇÃO ENTRE BH. MASTER 2 E CLOSET MASTER 2. AQUI É PISO VINÍLICO. NÃO TEM PAREDE! E TEM
  SOLEIRAS EM AMBAS ENTRADAS"** (`circulacao_master2`): o vão entre as duas portas (x 816,4 a 888,1, da suíte até a
  parede de baixo) no vinílico da suíte (as réguas na mesma fase), sem o pedaço de parede de cima; as soleiras nos vãos
  das portas do BH master 2 e do closet master 2; os batentes em parede.
- **"AO LADO DO VASO É UMA PAREDE FINA E CURTA"** (`parede_bh_master2`): a peça clara junto à bacia do BH master 2
  (ARQ_BANCADAS 49565/49566) vira parede, no cinza das paredes.
- **"ESTÁ FALTANDO UM APARADOR EMBAIXO DA TV NA PAREDE DO QUARTO 1"** (`aparador_quarto1`): o aparador do PDF (88594) em
  freijó (o das escrivaninhas), com a borda e a sombra curta; a TV por cima.
"""

import contextlib
import io
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
PAREDE = 80

ARMARIOS_PDF = [(88846,), (88851,)]
# (cada retângulo para no fio do contorno: o fio e a sombra de fora ficam como estão; o louceiro 2 é o L inteiro, o braço
# de baixo até a parede da direita)
ARMARIOS_PX = {"circulação": (1660, 670, 2168, 711), "circulação, jantar": (2094, 819, 2215, 847),
               "louceiro 2": (2284, 816, 2466, 921)}
MADEIRA_HSV = {"h": (5, 25), "s": (40, 165), "v": (105, 238)}
LAVABO = {"pecas": [(2365.9, 1028.5, 2396.3, 1071.7), (2365.9, 1071.7, 2398.7, 1144.6), (2365.9, 1144.6, 2396.3, 1187.9)],
          "cuba": 1, "gama": 0.9, "torneira": (10, 115), "contorno": (30, 40, 54), "contorno_alfa": 0.5, "ss": 8,
          "parede_x": 2365.9}
LAVABO_PORTA = {"cols": (2466, 2476), "rows": (1172, 1178), "fonte_x": 2440}
LOUCEIRO2_PAREDE = {"x": (2284.0, 2291.3), "y": (818, 835)}
CORTINAS_ESTAR = {"trechos": [("h", "direita", 1458.35, 2390.4, 2498.7), ("h", "direita", 1458.35, 2591.4, 2699.7),
                              ("v", "direita", 2385.75, 1462.4, 1525.4), ("v", "direita", 2385.75, 1578.0, 1640.4)],
                  "limpa": [(2386, 1450, 2703, 1461), (2379, 1462, 2388, 1642)], "limpa_lum": 100, "limpa_croma": 30,
                  "tom": 0.88,
                  "amostra": (2215, 1606, 2295, 1640)}
JARDINS = {"nomes": ("JARDIM DE INVERNO", "JARDIM DE INVERNO 2"), "gramado": (2440, 1490, 2760, 1650), "forca": 0.85}
SOLEIRAS_COZINHA = {"ret": (2194, 247, 2418, 262), "marrom": 22, "semente": 1316}
MESINHA = {"pdf": 88686, "png": "02-terreo/sala-de-estar/mesa-centro-redonda-nogueira-adorno.png",
           "patch": (0.16, 0.56, 0.40, 0.80), "borda": 0.78, "antiga_r": 13.5, "anel": (13.5, 17.0), "busca": 40}
ESCRITORIO = {"vao": (2713.7, 918.3, 2800.3, 931.1), "batentes": [(2710.7, 918.3, 2713.7, 931.1),
                                                                  (2800.3, 918.3, 2803.6, 931.1)],
              "folha": (2684.0, 931.4, 2774.0, 933.8), "limpa": (2680, 931, 2802, 936), "limpa_dy": 6,
              "soleira_amostra": (746, 846, 752, 888), "fio": 0.85, "ss": 8}
# (de x 2898: as colunas 2896 e 2897 da linha 790 são o fundo escuro do rótulo BH EXTERNO)
BOX_BH_EXT = {"x": (2898, 2907), "linha_fonte": 790, "y": (800, 812)}
RESTOS = [(2515, 483, 2562, 494), (2636, 483, 2658, 494), (2477, 340, 2488, 356)]
# a faixa escura do piso antigo no vão entre a cozinha e a área de serviço (entre o arremate branco de cima, y 300, e o de
# baixo, y 370; a folha de correr começa em x 2473): o piso da cozinha logo à esquerda (`dx`), com as bordas esfumadas
# (e a coluna da borda direita da faixa, acima da folha de correr, pelo piso da área de serviço logo à direita)
FAIXA_COZ_SERV = [{"ret": (2459, 302, 2473, 369), "dx": -14, "esfuma": (3, 1)},
                  {"ret": (2471, 302, 2476, 346), "dx": 5, "esfuma": (1, 1)}]
CIRC_M2 = {"vao": (816.4, 826.0, 888.1, 898.3), "fonte_y": (740, 826),
           "soleiras": [(809.3, 840.6, 816.4, 893.2), (888.1, 840.6, 895.3, 893.2)],
           "paredes": [(807.5, 838.6, 816.4, 840.6), (807.5, 893.2, 816.4, 895.3), (888.1, 838.6, 897.1, 840.6),
                       (888.1, 893.2, 897.1, 895.3), (809.3, 828.4, 816.4, 838.6), (888.1, 828.4, 895.3, 838.6)],
           "ss": 8}
PAREDE_BHM2 = {"ret": (758.0, 949.6, 760.4, 968.7), "limpa": (756, 946, 763, 967), "dx": 6, "ss": 8}
APARADOR_Q1 = {"ret": (1924.1, 351.9, 1942.0, 471.3), "tv_lum": 112, "tv_croma": 26, "borda": 0.84, "ss": 8}


def _cob(a0, a1, n, o, ss):
    xs = np.arange(n * ss) / ss + o + 0.5 / ss
    return cv2.resize(((xs >= a0) & (xs < a1)).astype(np.float32)[None], (n, 1), interpolation=cv2.INTER_AREA)[0]


def _ret_alfa(r, X0, Y0, W, H, ss=8):
    x0, y0, x1, y1 = r
    return np.outer(_cob(y0, y1, H, Y0, ss), _cob(x0, x1, W, X0, ss)).astype(np.float32)


def _pinta_ret(out, r, cor, folga=2):
    """O retângulo r (px, fracionário) pintado com `cor` (BGR ou imagem do tamanho da caixa) pela cobertura."""
    x0, y0, x1, y1 = r
    X0, Y0 = int(np.floor(x0)) - folga, int(np.floor(y0)) - folga
    W, H = int(np.ceil(x1)) + folga - X0, int(np.ceil(y1)) + folga - Y0
    a = _ret_alfa(r, X0, Y0, W, H)[..., None]
    reg = out[Y0:Y0 + H, X0:X0 + W].astype(np.float32)
    c = np.float32(cor) if np.ndim(cor) == 1 else cor
    out[Y0:Y0 + H, X0:X0 + W] = np.clip(np.round(reg * (1 - a) + c * a), 0, 255).astype(np.uint8)
    return out


def _sombra(a, W, H, dx=-1.0, dy=1.3, s=1.1):
    sb = cv2.GaussianBlur(cv2.warpAffine(a, np.float32([[1, 0, dx], [0, 1, dy]]), (W, H)), (0, 0), s)
    return sb * (1 - a)


def armarios_pdf(Q, img, ids=ARMARIOS_PDF):
    import revisao_terreo_casac_1311 as RT
    q = RT.COZINHA
    out = img.astype(np.float32)
    H, W = img.shape[:2]
    n = 0
    for grupo in ids:
        a, m = RT.MB.RT.mascara_pdf(Q, list(grupo))
        a = a.astype(np.float32)
        out *= (1 - q["sombra"] * _sombra(a, W, H))[..., None]
        borda = m & ~cv2.erode(m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        cor = np.float32(q["cor_armario"])[None, None] * np.where(borda, q["face"], 1.0)[..., None]
        out = out * (1 - a[..., None]) + cor * a[..., None]
        n += int(m.sum())
    print(f"    escritório: o armário em L na cor dos armários ({n} px)")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def _madeira(reg, q=MADEIRA_HSV):
    hsv = cv2.cvtColor(reg, cv2.COLOR_BGR2HSV).astype(np.int16)
    return ((hsv[..., 0] >= q["h"][0]) & (hsv[..., 0] <= q["h"][1]) & (hsv[..., 1] >= q["s"][0])
            & (hsv[..., 1] <= q["s"][1]) & (hsv[..., 2] >= q["v"][0]) & (hsv[..., 2] <= q["v"][1]))


def armarios_px(img, rs=ARMARIOS_PX):
    import revisao_terreo_casac_1311 as RT
    from scipy import ndimage
    q = RT.COZINHA
    out = img.copy()
    for nome, (x0, y0, x1, y1) in rs.items():
        reg = img[y0:y1, x0:x1]
        m = _madeira(reg)
        m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8)) > 0
        n, lab, st, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8), connectivity=4)
        if n < 2:
            print(f"    {nome}: sem madeira achada")
            continue
        grandes = [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= 0.25 * st[1:, cv2.CC_STAT_AREA].max()]
        cheio = ndimage.binary_fill_holes(np.isin(lab, grandes))
        m = cheio & _madeira(reg)
        # a face mais escura só no contorno de fora (os arcos e os traços de dentro ficam sem a moldura em volta)
        borda = m & ~cv2.erode(cheio.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        o = reg.astype(np.float32)
        o[m] = np.float32(q["cor_armario"])
        o[borda] = np.float32(q["cor_armario"]) * q["face"]
        out[y0:y1, x0:x1] = np.clip(np.round(o), 0, 255).astype(np.uint8)
        print(f"    {nome}: o armário na cor dos armários ({int(m.sum())} px)")
    return out


def lavabo_bancada(img, q=LAVABO):
    import revisao_terreo_casac_1311 as RT
    import pedidos_terreo_casab_1211 as PB2
    qs = RT.BANCADA_SERV
    ps = q["pecas"]
    X0, Y0 = int(np.floor(min(p[0] for p in ps))) - 2, int(np.floor(min(p[1] for p in ps))) - 2
    X1, Y1 = int(np.ceil(max(p[2] for p in ps))) + 3, int(np.ceil(max(p[3] for p in ps))) + 3
    W, H = X1 - X0, Y1 - Y0
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    imgB = cv2.imread(str(qs["final_b"]))
    with contextlib.redirect_stdout(io.StringIO()):
        T = PB2._tabaco(imgB, qs["fonte"], H, W, qs["semente"]).astype(np.float32)
    a = np.zeros((H, W), np.float32)
    for p in ps:
        a = np.maximum(a, _ret_alfa(p, X0, Y0, W, H))
    # a cuba: a luz da cuba esculpida (a razão à mediana da peça, suavizada) sobre o granito
    ac = _ret_alfa(ps[q["cuba"]], X0, Y0, W, H)
    lum = cv2.GaussianBlur(reg.mean(axis=2), (0, 0), 0.7)
    med = float(np.median(lum[ac > 0.99]))
    luz = np.clip(lum / max(med, 1.0), 0.45, 1.25) ** q["gama"]
    luz = np.where(ac > 0, luz, 1.0)
    novo = T * luz[..., None]
    # a torneira (o cromado: pouco croma, claro) fica
    I = reg.astype(np.int16)
    croma = I.max(axis=2) - I.min(axis=2)
    torn = (ac > 0.99) & (croma < q["torneira"][0]) & (reg.mean(axis=2) > q["torneira"][1])
    torn = cv2.dilate(torn.astype(np.uint8), np.ones((2, 2), np.uint8)) > 0
    al = a * ~torn
    o = reg * (1 - al[..., None]) + novo * al[..., None]
    # o fio da borda nos lados livres (não junto à parede da esquerda)
    miolo = np.zeros_like(a)
    for p in ps:
        miolo = np.maximum(miolo, _ret_alfa((p[0], p[1] + 1, p[2] - 1, p[3] - 1), X0, Y0, W, H))
    fio = np.clip(a - miolo, 0, 1) * q["contorno_alfa"]
    o = o * (1 - fio[..., None]) + np.float32(q["contorno"]) * fio[..., None]
    out = img.copy()
    out[Y0:Y1, X0:X1] = np.clip(np.round(o), 0, 255).astype(np.uint8)
    print(f"    lavabo: a bancada e a cuba em granito marrom tabaco ({int((a > 0.5).sum())} px), a torneira fica")
    return out


def lavabo_porta(img, q=LAVABO_PORTA):
    out = img.copy()
    c0, c1 = q["cols"]
    r0, r1 = q["rows"]
    out[r0:r1, c0:c1] = img[r0:r1, q["fonte_x"]][:, None]
    print("    lavabo: a folha da porta escura de ponta a ponta")
    return out


def louceiro2_parede(img, q=LOUCEIRO2_PAREDE):
    out = _pinta_ret(img.copy(), (q["x"][0], q["y"][0], q["x"][1], q["y"][1]), (PAREDE, PAREDE, PAREDE), folga=1)
    print("    louceiro 2: a parede de dentro até o canto de cima")
    return out


def _travertino(img, amostra, H, W, ref):
    import materiais_terreo_casac_1311 as MT
    ax0, ay0, ax1, ay1 = amostra
    T = MT.sem_emenda(img[ay0:ay1, ax0:ax1].astype(np.float32), H, W)
    return T - T.reshape(-1, 3).mean(axis=0) + ref


def cortinas_estar(img, q=CORTINAS_ESTAR):
    import regras_terreo_casab_1311 as RTB
    import biblioteca_terreo_casaa_1211 as BT
    out = img.copy()
    # o trilho e a cortina apagada de antes: o travertino do lugar (o claro e pouco colorido e também os pontinhos
    # cinzas da borda da cortina velha; a planta, o vaso e o vidro, e 2 px em volta deles, ficam)
    for x0, y0, x1, y1 in q["limpa"]:
        reg = out[y0:y1, x0:x1]
        I = reg.astype(np.int16)
        objeto = ((I.max(axis=2) - I.min(axis=2)) >= q["limpa_croma"]) | (I.mean(axis=2) < q["limpa_lum"])
        claro = ~(cv2.dilate(objeto.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0)
        volta = img[max(0, y0 - 14):y0 - 2, x0:x1].reshape(-1, 3) if y1 - y0 < x1 - x0 else \
            img[y0:y1, x0 - 14:x0 - 4].reshape(-1, 3)
        Iv = volta.astype(np.int16)
        ok = (Iv.mean(axis=1) > 165) & ((Iv.max(axis=1) - Iv.min(axis=1)) < 45)
        ref = np.median(volta[ok].astype(np.float32), axis=0)
        T = _travertino(img, q["amostra"], y1 - y0, x1 - x0, ref)
        o = reg.astype(np.float32)
        o[claro] = T[claro]
        out[y0:y1, x0:x1] = np.clip(np.round(o), 0, 255).astype(np.uint8)
    qc = dict(RTB.CORTINAS_TB)
    o_ = out.astype(np.float32)
    for o, v, ex, t0, t1 in q["trechos"]:
        P, cx, cy, wt, ht = RTB.cortina_desenho({"o": o, "v": v, "ex": ex, "t0": t0, "t1": t1}, qc)
        P = P.copy()
        P[..., :3] *= q["tom"]
        o_ = BT.pousar(o_, P, cx, cy, wt, ht, 0.0, BT.SOMBRAS["movel"], BT.PX_M if hasattr(BT, "PX_M") else 59.706)
    print(f"    estar: as cortinas C4 só nos {len(q['trechos'])} trechos do PDF, num linho um tom abaixo, com a sombra")
    return np.clip(np.round(o_), 0, 255).astype(np.uint8)


def jardins_inverno(Q, img, q=JARDINS):
    import final3840_casab as F
    import final3840_casac as C
    rot = F.textos_rotulos(C.B.rotulos_casab(Q.pg, Q.p2q2000))
    I = img.astype(np.int16)
    verde = (I[..., 1] > I[..., 2] + 4) & (I[..., 1] > I[..., 0] + 4) & (I.mean(axis=2) < 200)
    verde = cv2.morphologyEx(verde.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    _, lab, _, _ = cv2.connectedComponentsWithStats(verde, connectivity=8)
    gx0, gy0, gx1, gy1 = q["gramado"]
    g = cv2.cvtColor(img[gy0:gy1, gx0:gx1], cv2.COLOR_BGR2LAB).reshape(-1, 3).astype(np.float32)
    gm, gs = g.mean(axis=0), g.std(axis=0)
    lab_img = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    comp = np.zeros(img.shape[:2], bool)
    feitos = []
    for r in rot:
        if r[0] not in q["nomes"]:
            continue
        cx, cy = [int(round(v)) for v in Q.p2q(*r[2])]
        janela = lab[cy - 40:cy + 40, cx - 60:cx + 60]
        ids, cont = np.unique(janela[janela > 0], return_counts=True)
        if not len(ids):
            continue
        m = lab == int(ids[np.argmax(cont)])
        L = lab_img[m]
        novo = (L - L.mean(axis=0)) / np.maximum(L.std(axis=0), 1e-3) * gs + gm
        lab_img[m] = L * (1 - q["forca"]) + novo * q["forca"]
        comp |= m
        feitos.append((r[0], int(m.sum())))
    o = cv2.cvtColor(np.clip(np.round(lab_img), 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)
    out = np.where(comp[..., None], o, img)
    print(f"    jardins de inverno: a grama no tom do gramado do lote ({', '.join(f'{n} {a} px' for n, a in feitos)})")
    return out


def soleiras_cozinha(img, q=SOLEIRAS_COZINHA):
    import terreo_casaa_1011 as TC
    out = img.copy()
    x0, y0, x1, y1 = q["ret"]
    reg = img[y0:y1, x0:x1]
    I = reg.astype(np.int16)
    marrom = ((I[..., 2] - I[..., 0]) > q["marrom"]) & (I.mean(axis=2) < 170)
    marrom = cv2.morphologyEx(marrom.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8)) > 0
    H, W = img.shape[:2]
    danae = TC.danae(H, W, q["semente"])[y0:y1, x0:x1]
    o = reg.copy()
    o[marrom] = danae[marrom]
    out[y0:y1, x0:x1] = o
    print(f"    cozinha: a soleira das janelas no Dekton Danae da bancada ({int(marrom.sum())} px)")
    return out


def _png_mesinha(q=MESINHA, lado=256):
    P = cv2.imread(str(AQUI.parents[0] / "biblioteca-objetos" / q["png"]), cv2.IMREAD_UNCHANGED)
    h, w = P.shape[:2]
    a0, b0, a1, b1 = q["patch"]
    patch = P[int(b0 * h):int(b1 * h), int(a0 * w):int(a1 * w), :3]
    patch = cv2.resize(patch, (lado, lado), interpolation=cv2.INTER_CUBIC).astype(np.float32)
    yy, xx = np.mgrid[0:lado, 0:lado].astype(np.float32) + 0.5
    r = np.hypot(xx - lado / 2, yy - lado / 2)
    R = lado / 2 - 1
    alfa = np.clip(R - r + 0.5, 0, 1)
    borda = np.clip((r - (R - lado * 0.035)) / (lado * 0.035), 0, 1) * alfa
    luz = 1.0 + 0.08 * ((xx - lado / 2) - (yy - lado / 2)) / lado
    cor = patch * luz[..., None]
    cor = cor * (1 - borda[..., None]) + cor * q["borda"] * borda[..., None]
    return np.dstack([cor, alfa * 255]).astype(np.float32)


def _apaga_mesinha_antiga(img, cx, cy, q=MESINHA):
    """A mesinha de antes (maior que o círculo do PDF, com a sombra) sai: o disco de raio `antiga_r` vira o vinílico de
    um trecho limpo do mesmo quarto, o que melhor casa com o anel em volta (as réguas seguem)."""
    r0 = q["antiga_r"]
    a0, a1 = q["anel"]
    B = q["busca"]
    R = int(np.ceil(a1)) + 1
    X, Y = int(round(cx)), int(round(cy))
    yy, xx = np.mgrid[-R:R + 1, -R:R + 1].astype(np.float32)
    r = np.hypot(xx + X - cx, yy + Y - cy)
    anel = (r >= a0) & (r <= a1)
    disco = r <= r0 + 1
    alvo = img[Y - R:Y + R + 1, X - R:X + R + 1].astype(np.float32)
    ref = np.median(alvo[anel], axis=0)
    melhor, d_ok = None, None
    for dy in range(-B, B + 1):
        for dx in range(-B, B + 1):
            if np.hypot(dx, dy) < 2 * a1:
                continue
            f = img[Y + dy - R:Y + dy + R + 1, X + dx - R:X + dx + R + 1].astype(np.float32)
            # a fonte toda no vinílico (nada de móvel, cortina ou parede no disco)
            if (np.abs(f[disco] - ref).max(axis=1) > 34).mean() > 0.01:
                continue
            e = float(((f[anel] - alvo[anel]) ** 2).mean())
            if melhor is None or e < melhor:
                melhor, d_ok = e, (dx, dy)
    if d_ok is None:
        print("    suíte master: sem trecho limpo para apagar a mesinha antiga")
        return img
    dx, dy = d_ok
    f = img[Y + dy - R:Y + dy + R + 1, X + dx - R:X + dx + R + 1].astype(np.float32)
    a = np.clip((r0 + 0.75 - r) / 1.5, 0, 1)[..., None]
    out = img.copy()
    out[Y - R:Y + R + 1, X - R:X + R + 1] = np.clip(np.round(alvo * (1 - a) + f * a), 0, 255).astype(np.uint8)
    return out


def mesinha_master(Q, img, q=MESINHA):
    import revisao_terreo_casac_1311 as RT
    import mobiliario_terreo_casac_1311 as MB
    x0, y0, x1, y1 = RT.MB.RT.caixa_pdf(Q, q["pdf"])
    D = ((x1 - x0) + (y1 - y0)) / 2
    img = _apaga_mesinha_antiga(img, (x0 + x1) / 2, (y0 + y1) / 2, q)
    with contextlib.redirect_stdout(io.StringIO()):
        par = MB.BS.quieto(MB.FA.paredes_pdf, Q) > 0.3
    out = MB.pousar(img, _png_mesinha(q), (x0 + x1) / 2, (y0 + y1) / 2, D, D, 0.0, "baixa", par)
    print(f"    suíte master: a mesinha redonda em nogueira ({D:.1f} px)")
    return out


def escritorio_janela(img, q=ESCRITORIO):
    import revisao_terreo_casac_1311 as RT
    out = img.copy()
    # a faixa logo dentro (a folha preta de antes): o vinílico de logo abaixo
    lx0, ly0, lx1, ly1 = q["limpa"]
    out[ly0:ly1, lx0:lx1] = img[ly0 + q["limpa_dy"]:ly1 + q["limpa_dy"], lx0:lx1]
    # a soleira: o bege das soleiras, lisa, com os fios das arestas
    sx0, sy0, sx1, sy1 = q["soleira_amostra"]
    bege = np.median(img[sy0:sy1, sx0:sx1].reshape(-1, 3).astype(np.float32), axis=0)
    out = _pinta_ret(out, q["vao"], bege)
    x0, y0, x1, y1 = q["vao"]
    for yy in (y0, y1 - 0.6):
        out = _pinta_ret(out, (x0, yy, x1, yy + 0.6), bege * q["fio"], folga=1)
    for b in q["batentes"]:
        out = _pinta_ret(out, b, (PAREDE, PAREDE, PAREDE), folga=1)
    # a folha de correr em vidro claro (as faces finas)
    vb = __import__("final3840_casab").BOXES_VIDRO
    f = q["folha"]
    out = _pinta_ret(out, f, vb["vidro"], folga=1)
    fp = vb["face_px"]
    for r in ((f[0], f[1], f[2], f[1] + fp), (f[0], f[3] - fp, f[2], f[3]), (f[0], f[1], f[0] + fp, f[3]),
              (f[2] - fp, f[1], f[2], f[3])):
        out = _pinta_ret(out, r, vb["face"], folga=1)
    print("    escritório: a soleira da janela lisa no bege das soleiras, os batentes em parede, a folha em vidro claro")
    return out


def box_bh_externo(img, q=BOX_BH_EXT):
    out = img.copy()
    x0, x1 = q["x"]
    y0, y1 = q["y"]
    out[y0:y1, x0:x1] = img[q["linha_fonte"], x0:x1][None]
    print("    BH externo: o vidro do box até a parede de baixo")
    return out


def restos_piso(img, rs=RESTOS):
    out = img.copy()
    n = 0
    for x0, y0, x1, y1 in rs:
        reg = np.ascontiguousarray(out[y0:y1, x0:x1])
        I = reg.astype(np.int16)
        lum = I.mean(axis=2)
        croma = I.max(axis=2) - I.min(axis=2)
        parede = np.abs(I - PAREDE).max(axis=2) <= 14
        piso = (~parede) & (croma > 14)
        med = cv2.medianBlur(reg, 7).astype(np.int16).mean(axis=2)
        ruim = piso & (np.abs(lum - med) > 18)
        # a folha de correr e as peças cinzas (pouco croma) ficam
        ruim &= croma > 10
        ruim = cv2.dilate(ruim.astype(np.uint8), np.ones((3, 3), np.uint8)) & (~parede).astype(np.uint8) & \
            (croma > 10).astype(np.uint8)
        if ruim.any():
            out[y0:y1, x0:x1] = cv2.inpaint(reg, ruim * 255, 3, cv2.INPAINT_TELEA)
            n += int(ruim.sum())
    print(f"    quarto de serviço e cozinha/área de serviço: {n} px de restos do piso antigo fora")
    return out


def faixa_cozinha_servico(img, qs=FAIXA_COZ_SERV):
    out = img.copy()
    for q in qs:
        out = _faixa(out, q)
    x0, x1 = qs[0]["ret"][0], max(q["ret"][2] for q in qs)
    print(f"    cozinha/área de serviço: a faixa do piso antigo no vão (x {x0} a {x1}) no piso do lado")
    return out


def _faixa(img, q):
    out = img.copy()
    x0, y0, x1, y1 = q["ret"]
    dx, (ee, ed) = q["dx"], q["esfuma"]
    fonte = img[y0:y1, x0 + dx:x1 + dx].astype(np.float32)
    a = np.ones(x1 - x0, np.float32)
    for i in range(ee):
        a[i] = (i + 1) / (ee + 1)
    for i in range(ed):
        a[-1 - i] = (i + 1) / (ed + 1)
    o = img[y0:y1, x0:x1].astype(np.float32) * (1 - a[None, :, None]) + fonte * a[None, :, None]
    out[y0:y1, x0:x1] = np.clip(np.round(o), 0, 255).astype(np.uint8)
    return out


def circulacao_master2(img, q=CIRC_M2):
    out = img.copy()
    x0, y0, x1, y1 = q["vao"]
    X0, Y0, X1, Y1 = int(np.floor(x0)) - 1, int(np.floor(y0)), int(np.ceil(x1)) + 1, int(np.ceil(y1))
    # o passo das réguas do vinílico da suíte (a autocorrelação das linhas)
    fy0, fy1 = q["fonte_y"]
    col = img[fy0:fy1, X0 + 3:X1 - 3].astype(np.float32).mean(axis=(1, 2))
    col = col - col.mean()
    ac = np.array([np.dot(col[:-k], col[k:]) / (len(col) - k) for k in range(4, 30)])
    passo = 4 + int(np.argmax(ac))
    d = passo * int(np.ceil((Y1 - Y0) / passo))
    while Y0 - d < fy0:
        d -= passo
    fonte = img[Y0 - d:Y1 - d, X0:X1].astype(np.float32)
    a = _ret_alfa((x0, y0, x1, y1), X0, Y0, X1 - X0, Y1 - Y0)[..., None]
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg * (1 - a) + fonte * a), 0, 255).astype(np.uint8)
    for p in q["paredes"]:
        out = _pinta_ret(out, p, (PAREDE, PAREDE, PAREDE), folga=1)
    bege = np.median(img[846:888, 746:752].reshape(-1, 3).astype(np.float32), axis=0)
    for s in q["soleiras"]:
        out = _pinta_ret(out, s, bege, folga=1)
        sx0, sy0, sx1, sy1 = s
        for xx in (sx0, sx1 - 0.6):
            out = _pinta_ret(out, (xx, sy0, xx + 0.6, sy1), bege * 0.86, folga=1)
    print(f"    circulação do BH master 2 e do closet master 2: o vinílico da suíte (réguas de {passo} px), sem a parede; "
          f"as soleiras nas duas portas")
    return out


def parede_bh_master2(img, q=PAREDE_BHM2):
    out = img.copy()
    lx0, ly0, lx1, ly1 = q["limpa"]
    out[ly0:ly1, lx0:lx1] = img[ly0:ly1, lx0 + q["dx"]:lx1 + q["dx"]]
    out = _pinta_ret(out, q["ret"], (PAREDE, PAREDE, PAREDE), folga=1)
    print("    BH master 2: a parede fina e curta junto à bacia")
    return out


def aparador_quarto1(img, q=APARADOR_Q1):
    import revisao_terreo_casac_1311 as RT
    import materiais_terreo_casac_1311 as MT
    import biblioteca_terreo_casaa_1211 as BT
    x0, y0, x1, y1 = q["ret"]
    X0, Y0 = int(np.floor(x0)) - 6, int(np.floor(y0)) - 6
    W, H = int(np.ceil(x1)) + 7 - X0, int(np.ceil(y1)) + 7 - Y0
    reg = img[Y0:Y0 + H, X0:X0 + W].astype(np.float32)
    I = reg.astype(np.int16)
    a = _ret_alfa(q["ret"], X0, Y0, W, H)
    tv = (I.mean(axis=2) < q["tv_lum"]) & ((I.max(axis=2) - I.min(axis=2)) < q["tv_croma"]) & (a > 0.5)
    parede = np.abs(I - PAREDE).max(axis=2) <= 12
    fx0, fy0, fx1, fy1 = RT.ESCRIVANINHAS["fonte"]
    A = np.ascontiguousarray(np.rot90(img[fy0:fy1, fx0:fx1].astype(np.float32)))
    T = MT.sem_emenda(A, H, W)
    dentro = _ret_alfa((x0 + 1, y0 + 1, x1 - 1, y1 - 1), X0, Y0, W, H)
    T = T * (q["borda"] + (1 - q["borda"]) * dentro)[..., None]
    for sb in BT.SOMBRAS["mesa"]:
        sh = cv2.GaussianBlur(a, (0, 0), max(0.3, sb["sig"] * RT.PX_M))
        Ms = np.float32([[1, 0, sb["dx"] * RT.PX_M], [0, 1, sb["dy"] * RT.PX_M]])
        sh = cv2.warpAffine(sh, Ms, (W, H), flags=cv2.INTER_LINEAR, borderValue=0)
        reg *= (1 - sb["forca"] * sh * (1 - a) * ~parede)[..., None]
    al = (a * ~parede * ~tv)[..., None]
    reg = reg * (1 - al) + T * al
    out = img.copy()
    out[Y0:Y0 + H, X0:X0 + W] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    print(f"    quarto 1: o aparador em freijó embaixo da TV ({x1 - x0:.0f} x {y1 - y0:.0f} px), a TV por cima")
    return out


ANTES_DEPOIS = {"armario_escritorio": (2560, 900, 2830, 1200), "armario_circulacao": (1640, 640, 2240, 860),
                "louceiro2": (2250, 780, 2440, 910), "lavabo": (2340, 1010, 2490, 1200),
                "cortinas_estar": (2280, 1420, 2720, 1660), "jardins_inverno": (1700, 840, 2060, 1220),
                "cozinha_janelas": (2180, 230, 2430, 300), "mesinha_master": (780, 620, 900, 720),
                "escritorio_janela": (2670, 900, 2820, 950), "bh_externo": (2860, 730, 2970, 830),
                "qto_servico": (2460, 440, 2740, 560), "cozinha_servico": (2430, 260, 2520, 420),
                "circulacao_master2": (760, 760, 1010, 1000), "parede_bh_master2": (700, 920, 790, 990),
                "aparador_quarto1": (1900, 330, 2010, 500)}
ANTES_DEPOIS_COMMIT = "77cbb38"


def antes_depois(antes, depois, R):
    for nome, (x0, y0, x1, y1) in ANTES_DEPOIS.items():
        a, b = antes[y0:y1, x0:x1], depois[y0:y1, x0:x1]
        k = min(5.0, 1500 / max(a.shape[:2]))
        sz = (int(a.shape[1] * k), int(a.shape[0] * k))
        a = cv2.resize(a, sz, interpolation=cv2.INTER_CUBIC)
        b = cv2.resize(b, sz, interpolation=cv2.INTER_CUBIC)
        lado = sz[0] <= sz[1] * 1.3
        j = np.hstack([a, np.full((sz[1], 16, 3), 255, np.uint8), b]) if lado else \
            np.vstack([a, np.full((16, sz[0], 3), 255, np.uint8), b])
        t = np.full((44, j.shape[1], 3), 255, np.uint8)
        cv2.putText(t, "ANTES | DEPOIS" if lado else "ANTES (em cima) | DEPOIS (embaixo)", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (40, 40, 40), 2, cv2.LINE_AA)
        cv2.imwrite(str(R / f"POE642_CasaC_PH_Terreo_1511_{nome}_antes_depois.jpg"), np.vstack([t, j]),
                    [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"    antes e depois (15/11): {', '.join(ANTES_DEPOIS)}")


def aplicar(Q, out):
    out = armarios_pdf(Q, out)
    out = armarios_px(out)
    out = lavabo_bancada(out)
    out = lavabo_porta(out)
    out = louceiro2_parede(out)
    out = cortinas_estar(out)
    out = jardins_inverno(Q, out)
    out = soleiras_cozinha(out)
    out = mesinha_master(Q, out)
    out = escritorio_janela(out)
    out = box_bh_externo(out)
    out = restos_piso(out)
    out = faixa_cozinha_servico(out)
    out = circulacao_master2(out)
    out = parede_bh_master2(out)
    out = aparador_quarto1(out)
    return out

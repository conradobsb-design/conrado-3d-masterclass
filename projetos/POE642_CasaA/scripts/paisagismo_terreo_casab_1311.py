"""O paisagismo do Térreo da Casa B (13/11): a proposta, para o OK (nada é gravado na final).

Usuário: "USE OUTRO TIPO DE ARVORE NO TERREO DA CASA B. USE OUTRAS PLANTAS TAMBÉM." e "ME APRESENTE UMA PROPOSTA COM
PAISAGISMO NAS DUAS LATERAIS DAS PEDRAS, FORMANDO UM CAMINHO EM PEDRAS COM A COSTELA DE ADÃO. QUERO VER ANTES DE VOCÊ
APLICAR." As peças vistas de cima, geradas no Higgsfield (gpt_image_2, o fundo tirado no removedor do Higgsfield), estão
em `biblioteca-objetos/02-terreo/paisagismo/`: oliveira, ipê-amarelo, pau-ferro, quaresmeira, costela-de-adão (touceira
e faixa), filodendro xanadu, moreia, agave attenuata, palmeira-ráfis.
- **Árvores (`ARVORES`):** as 3 de hoje (a copa e o anel de arbustos redondos; a da direita com a palmeira no meio)
  saem (o gramado do lote, `GRAMA_PX`, no tom do entorno) e entra a árvore nova no mesmo centro, com a sombra da copa;
  a folha das árvores mostra as 4 no canto de cima à esquerda.
- **Caminho de pedras (`CAMINHO`):** a costela-de-adão nas duas laterais das 8 pedras (e da pedra grande do hall),
  touceiras de ~1,2 m que se sobrepõem, viradas e espelhadas ao acaso, as folhas passando um pouco sobre a borda das
  pedras; P1 direto no gramado, P2 num canteiro de terra escura com a borda reta.
- **Outras plantas (`PLANTAS`):** no jardim de inverno, palmeira-ráfis e filodendro xanadu; no hall, o agave; no jardim
  junto à garagem, moreia e filodendro; na floreira do lavatório gourmet, moreias no lugar das bolas de buxinho.

  python3 paisagismo_terreo_casab_1311.py
grava `POE642_CasaB/renders/POE642_CasaB_PH_Terreo_1311_paisagismo_proposta_{1_planta,2_arvores,3_caminho,4_plantas}.jpg`.
"""

import json
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import biblioteca_terreo_casaa_1211 as BT        # noqa: E402
import biblioteca_1pav_casaa_1211 as B1          # noqa: E402

PX_M = B1.PX_M
BIB = AQUI.parent / "biblioteca-objetos" / "02-terreo" / "paisagismo"
CASA_B = AQUI.parents[1] / "POE642_CasaB"
R = CASA_B / "renders"
FINAL = R / "POE642_CasaB_PH_Terreo_final_rotulos.png"
SEMENTE = 1311

SOMBRA_ARVORE = [{"dx": -0.30, "dy": 0.30, "sig": 0.22, "forca": 0.42}, {"dx": -0.06, "dy": 0.06, "sig": 0.06,
                                                                          "forca": 0.20}]
SOMBRA_PLANTA = [{"dx": -0.06, "dy": 0.06, "sig": 0.05, "forca": 0.34}, {"dx": 0.0, "dy": 0.0, "sig": 0.02,
                                                                          "forca": 0.12}]
GRAMA_PX = (640, 120, 860, 250)                    # um trecho limpo do gramado do lote
# as árvores de hoje: (centro, raio da mancha de hoje, diâmetro da nova) px
ARVORES = [((437, 240), 160, 300), ((3360, 240), 168, 300), ((440, 1742), 160, 290)]
# a copa nova (4,5 m) afastada da divisa do lote (a sombra não escurece o muro): (deslocamento do centro, diâmetro)
ARVORES_NOVAS = [((14, 16), 270), ((-14, 16), 270), ((14, -10), 265)]
ARVORE_REC = "oliveira"
OPCOES_ARVORE = ["oliveira", "ipe-amarelo", "pau-ferro", "quaresmeira"]
NOMES = {"oliveira": "Oliveira", "ipe-amarelo": "Ipê-amarelo", "pau-ferro": "Pau-ferro", "quaresmeira": "Quaresmeira",
         "costela-de-adao": "Costela-de-adão", "filodendro-xanadu": "Filodendro xanadu", "moreia": "Moreia",
         "agave": "Agave attenuata", "palmeira-rafis": "Palmeira-ráfis"}
# o caminho: as pedras (px) e os canteiros dos dois lados (x0, x1, y do centro das touceiras)
CAMINHO = {"pedras_y": (974, 1153), "cima": (2836, 3500, 944), "baixo": (2716, 3500, 1183), "diam_px": (66, 80),
           "passo_px": 44, "passo_canteiro_px": 60, "jitter_px": 6, "canteiro_px": 34,
           "terra_px": (1228, 1650, 1420, 1688)}
# as outras plantas: (caixa onde estão as de hoje, superfície da troca (o deslocamento da fonte), [(cx, cy, planta,
# diâmetro px)])
PLANTAS = {
    "jardim_inverno": ((2042, 738, 2238, 932), (0, 0), [(2075, 770, "palmeira-rafis", 62), (2068, 904, "filodendro-xanadu", 52),
                                                        (2204, 900, "palmeira-rafis", 62)]),
    "hall": ((2452, 940, 2536, 1010), (0, 72), [(2500, 976, "agave", 50)]),
    "jardim_garagem": ((2342, 1192, 2440, 1275), (0, 0), [(2385, 1214, "moreia", 50), (2378, 1258, "filodendro-xanadu", 40)]),
    "floreira_lavatorio": ((1226, 1648, 1424, 1690), (0, 0), [(1240 + 29 * i, 1668, "moreia", 34) for i in range(7)]),
}
VERDE = {"g_r": 6, "g_b": 4, "sat": 28}


def ler(nome):
    return cv2.imread(str(BIB / f"{nome}.png"), cv2.IMREAD_UNCHANGED).astype(np.float32)


def pousar(out, P, cx, cy, d, ang=0.0, sombras=SOMBRA_PLANTA, espelho=False):
    if espelho:
        P = np.ascontiguousarray(P[:, ::-1])
    h, w = P.shape[:2]
    k = d / max(h, w)
    o = BT.pousar(out.astype(np.float32), P, cx, cy, w * k, h * k, ang, sombras, PX_M)
    return np.clip(np.round(o), 0, 255).astype(np.uint8)


def textura(fonte, h, w):
    """A textura `fonte` (h0 x w0 x 3) espelhada em vaivém até h x w."""
    T = np.concatenate([fonte, fonte[:, ::-1]], axis=1)
    T = np.concatenate([T, T[::-1]], axis=0)
    return np.tile(T, (h // T.shape[0] + 1, w // T.shape[1] + 1, 1))[:h, :w]


def preencher(out, m, fonte, anel_px=10, nao=None, sig=14.0):
    """Os px de `m` com a textura `fonte`, no tom local do entorno (a média do anel em volta, estendida)."""
    ys, xs = np.nonzero(m)
    X0, Y0, X1, Y1 = xs.min() - anel_px * 3, ys.min() - anel_px * 3, xs.max() + anel_px * 3 + 1, ys.max() + anel_px * 3 + 1
    X0, Y0 = max(X0, 0), max(Y0, 0)
    sub = out[Y0:Y1, X0:X1].astype(np.float32)
    mm = m[Y0:Y1, X0:X1]
    anel = (cv2.dilate(mm.astype(np.uint8), np.ones((2 * anel_px + 1,) * 2, np.uint8)) > 0) & ~mm
    if nao is not None:                                       # o que não serve de tom (o branco da prancha)
        anel &= ~nao[Y0:Y1, X0:X1]
    T = textura(fonte.astype(np.float32), Y1 - Y0, X1 - X0)
    num = cv2.GaussianBlur(sub * anel[..., None], (0, 0), sig)
    den = cv2.GaussianBlur(anel.astype(np.float32), (0, 0), sig)[..., None]
    med = np.median(sub[anel].reshape(-1, 3), axis=0) if anel.any() else sub.reshape(-1, 3).mean(axis=0)
    # longe do anel (o miolo de um buraco grande), o tom mediano do anel
    w_ = np.clip(den / 0.05, 0, 1)
    alvo = (num / np.maximum(den, 1e-4)) * w_ + med[None, None] * (1 - w_)
    Tm = cv2.GaussianBlur(T, (0, 0), sig)
    novo = T * alvo / np.maximum(Tm, 1)
    a = cv2.GaussianBlur(mm.astype(np.float32), (0, 0), 1.2 * sig / 14.0)[..., None]
    sub = sub * (1 - a) + novo * a
    out[Y0:Y1, X0:X1] = np.clip(np.round(sub), 0, 255).astype(np.uint8)
    return out


def arvores(out, especie, rng):
    x0, y0, x1, y1 = GRAMA_PX
    grama = out[y0:y1, x0:x1].copy()
    H, W = out.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    base = out.copy()
    lote = out.astype(np.float32).mean(axis=2) < 150            # o lote (fora fica o branco da prancha)
    P = ler(especie)
    for ((cx, cy), r, _), ((dx, dy), d) in zip(ARVORES, ARVORES_NOVAS):
        m = ((xx - cx) ** 2 + (yy - cy) ** 2 <= r * r) & lote
        out = preencher(out, m, grama, nao=~lote)
        out = pousar(out, P, cx + dx, cy + dy, d, float(rng.uniform(0, 360)), SOMBRA_ARVORE)
    out[~lote] = base[~lote]                                    # a copa e a sombra não passam para a margem
    return out


def caminho(out, rng, canteiro=False, q=CAMINHO):
    P = ler("costela-de-adao")
    ya, yb = q["pedras_y"]
    if canteiro:
        tx0, ty0, tx1, ty1 = q["terra_px"]
        terra = out[ty0:ty1, tx0:tx1].copy()
        c = q["canteiro_px"]
        for x0, x1, yc in (q["cima"], q["baixo"]):
            m = np.zeros(out.shape[:2], bool)
            m[int(yc - c):int(yc + c), x0 - 8:x1 + 4] = True
            m[ya:yb, :] = False
            sub = out[m].astype(np.float32)
            T = textura(terra.astype(np.float32), out.shape[0], out.shape[1])
            o = out.astype(np.float32)
            o[m] = T[m]
            # a borda reta do canteiro: o fio escuro e a sombra curta para dentro
            borda = m & ~(cv2.erode(m.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0)
            o[borda] *= 0.80
            out = np.clip(o, 0, 255).astype(np.uint8)
            del sub
    for x0, x1, yc in (q["cima"], q["baixo"]):
        xs = np.arange(x0 + 20, x1 - 10, q["passo_canteiro_px"] if canteiro else q["passo_px"])
        for i, x in enumerate(xs):
            d = float(rng.uniform(*q["diam_px"]))
            y = yc + rng.uniform(-q["jitter_px"], q["jitter_px"])
            out = pousar(out, P, float(x + rng.uniform(-6, 6)), float(y), d, float(rng.uniform(0, 360)),
                         SOMBRA_PLANTA, bool(rng.integers(0, 2)))
    return out


def plantas(out, rng):
    for nome, (caixa, desloc, novas) in PLANTAS.items():
        x0, y0, x1, y1 = caixa
        sub = out[y0:y1, x0:x1].astype(np.int16)
        b, g, r_ = sub[..., 0], sub[..., 1], sub[..., 2]
        verde = (g - r_ > VERDE["g_r"]) & (g - b > VERDE["g_b"]) & ((sub.max(axis=2) - sub.min(axis=2)) > VERDE["sat"])
        verde = cv2.morphologyEx(verde.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        verde = cv2.dilate(verde, np.ones((7, 7), np.uint8)) > 0
        m = np.zeros(out.shape[:2], bool)
        m[y0:y1, x0:x1] = verde
        if nome in ("jardim_inverno", "jardim_garagem"):
            # o gramado do próprio jardim: um trecho sem planta dentro da caixa
            livre = ~verde
            ys, xs = np.nonzero(livre)
            fy, fx = int(np.median(ys)), int(np.median(xs))
            fonte = out[y0 + max(fy - 20, 0):y0 + fy + 20, x0 + max(fx - 20, 0):x0 + fx + 20].copy()
        elif nome == "floreira_lavatorio":
            fonte = out[1650:1656, 1226:1424].copy()                # a terra entre as bolas e a borda de cima
            m &= ~(cv2.dilate((out.astype(np.int16).mean(axis=2) < 60).astype(np.uint8), np.ones((1, 1), np.uint8)) > 0)
        else:
            dx, dy = desloc
            fonte = out[y0 + dy:y1 + dy, x0 + dx:x1 + dx].copy()
        if m.any():
            out = preencher(out, m, fonte, anel_px=6)
        for cx, cy, planta, d in novas:
            out = pousar(out, ler(planta), cx, cy, d, float(rng.uniform(0, 360)), SOMBRA_PLANTA,
                          bool(rng.integers(0, 2)))
    return out


def proposta(base, especie=ARVORE_REC, canteiro=False):
    rng = np.random.default_rng(SEMENTE)
    out = base.copy()
    out = arvores(out, especie, rng)
    out = caminho(out, rng, canteiro)
    out = plantas(out, rng)
    return out


# ----------------------------------------------------------------------------------------------------------------------
def _titulo(img, txt, sub=None, h=54):
    topo = np.full((h + (30 if sub else 0), img.shape[1], 3), 255, np.uint8)
    cv2.putText(topo, txt, (12, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.95, (40, 40, 40), 2, cv2.LINE_AA)
    if sub:
        cv2.putText(topo, sub, (12, 72), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (90, 90, 90), 1, cv2.LINE_AA)
    return np.vstack([topo, img])


def _rec(img, c, k):
    x0, y0, x1, y1 = c
    return cv2.resize(img[y0:y1, x0:x1], None, fx=k, fy=k, interpolation=cv2.INTER_CUBIC)


def _lado(ims, gap=14):
    h = max(i.shape[0] for i in ims)
    ims = [np.pad(i, ((0, h - i.shape[0]), (0, 0), (0, 0)), constant_values=255) for i in ims]
    out = [ims[0]]
    for i in ims[1:]:
        out += [np.full((h, gap, 3), 255, np.uint8), i]
    return np.hstack(out)


def _pilha(ims, gap=14):
    w = max(i.shape[1] for i in ims)
    ims = [np.pad(i, ((0, 0), (0, w - i.shape[1]), (0, 0)), constant_values=255) for i in ims]
    out = [ims[0]]
    for i in ims[1:]:
        out += [np.full((gap, w, 3), 255, np.uint8), i]
    return np.vstack(out)


def folhas(base):
    rec = proposta(base)
    # 1. a planta inteira: hoje e a proposta (oliveira, o caminho P1, as outras plantas)
    k = 0.5
    a = _titulo(cv2.resize(base[60:1960, 260:3580], None, fx=k, fy=k, interpolation=cv2.INTER_AREA), "HOJE")
    b = _titulo(cv2.resize(rec[60:1960, 260:3580], None, fx=k, fy=k, interpolation=cv2.INTER_AREA),
                "PROPOSTA: oliveiras nos 3 cantos, caminho com costela-de-adao (P1), outras plantas")
    f1 = _titulo(_pilha([a, b]), "POE 642 - Casa B - Terreo - paisagismo (proposta para aprovar; nada aplicado)")
    # 2. as árvores: o canto de cima à esquerda com cada opção
    c = (250, 60, 640, 430)
    ims = [_titulo(_rec(base, c, 1.4), "HOJE")]
    for esp in OPCOES_ARVORE:
        o = arvores(base.copy(), esp, np.random.default_rng(SEMENTE))
        ims.append(_titulo(_rec(o, c, 1.4), NOMES[esp] + (" (recomendada)" if esp == ARVORE_REC else "")))
    f2 = _titulo(_pilha([_lado(ims[:3]), _lado(ims[3:])]), "Arvores: a mesma especie nos 3 cantos do lote",
                 "Oliveira: copa cinza-esverdeada, contrasta com o gramado escuro; Ipe e Quaresmeira: florada; "
                 "Pau-ferro: copa leve")
    # 3. o caminho: hoje, P1 (no gramado) e P2 (no canteiro)
    c = (2680, 880, 3530, 1250)
    p1 = proposta(base)
    p2 = proposta(base, canteiro=True)
    f3 = _titulo(_pilha([_titulo(_rec(base, c, 1.15), "HOJE"),
                         _titulo(_rec(p1, c, 1.15), "P1: costela-de-adao nas duas laterais, direto no gramado (recomendada)"),
                         _titulo(_rec(p2, c, 1.15), "P2: costela-de-adao num canteiro de terra escura com borda reta")]),
                 "Caminho de pedras com costela-de-adao nas duas laterais")
    # 4. as outras plantas
    blocos = [("Jardim de inverno: palmeira-rafis e filodendro xanadu", (2030, 728, 2250, 942), 2.0),
              ("Hall: agave attenuata", (2445, 935, 2560, 1015), 3.0),
              ("Jardim junto a garagem: moreia e filodendro", (2330, 1185, 2560, 1285), 2.4),
              ("Floreira do lavatorio gourmet: moreias", (1210, 1636, 1440, 1700), 2.4)]
    linhas = []
    for txt, c, k in blocos:
        linhas.append(_titulo(_lado([_titulo(_rec(base, c, k), "HOJE"), _titulo(_rec(rec, c, k), "PROPOSTA")]), txt))
    f4 = _titulo(_pilha(linhas), "Outras plantas")
    for n, f in (("1_planta", f1), ("2_arvores", f2), ("3_caminho", f3), ("4_plantas", f4)):
        arq = R / f"POE642_CasaB_PH_Terreo_1311_paisagismo_proposta_{n}.jpg"
        cv2.imwrite(str(arq), f, [cv2.IMWRITE_JPEG_QUALITY, 88])
        print(f"    {arq.name} {f.shape[1]}x{f.shape[0]}")


# ----------------------------------------------------------------------------------------------------------------------
# A aplicação (13/11, "OLIVEIRA, HOJE E PODE APLICAR AS OUTRAS PLANTAS"): as oliveiras nos 3 cantos e as outras plantas;
# o caminho de pedras fica como hoje. Chamado no `regras_terreo_casab_1311.aplicar`; no 12K (`pecas_12k`), o chão de
# cada região refeito com a textura da própria saída do Topaz e as plantas nítidas na escala dele.
REG_MASCARA = R / "POE642_CasaB_PH_Terreo_12K_paisagismo_mascara.png"
SOMBRAS = {"arvore": SOMBRA_ARVORE, "planta": SOMBRA_PLANTA}


def _pousar_it(out, it, s=1.0, X0=0.0, Y0=0.0):
    P = ler(it["png"])
    if it["espelho"]:
        P = np.ascontiguousarray(P[:, ::-1])
    h, w = P.shape[:2]
    k = it["d"] / max(h, w)
    o = BT.pousar(out.astype(np.float32), P, (it["cx"] - X0) * s, (it["cy"] - Y0) * s, w * k * s, h * k * s,
                  it["giro"], SOMBRAS[it["sombra"]], PX_M * s)
    return np.clip(np.round(o), 0, 255).astype(np.uint8)


def mancha_arvore(base, cx, cy, r, folga=50):
    """A árvore de hoje inteira (a copa e o anel de arbustos, que não é redondo): o que não é gramado (o gramado tem
    G - R < 0 e R - B ~ 42) ligado ao miolo, mais o círculo; fora a linha cinza do muro e o branco da prancha."""
    H, W = base.shape[:2]
    X0, Y0, X1, Y1 = max(cx - r - folga, 0), max(cy - r - folga, 0), min(cx + r + folga, W), min(cy + r + folga, H)
    sub = base[Y0:Y1, X0:X1].astype(np.int16)
    L = sub.mean(axis=2)
    cinza = (sub.max(axis=2) - sub.min(axis=2)) < 10
    fora = (L >= 150) | cinza
    folha = (((sub[..., 1] - sub[..., 2]) > 3) | ((sub[..., 2] - sub[..., 0]) < 36)) & ~fora
    folha = cv2.morphologyEx(folha.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    folha = cv2.morphologyEx(folha, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    yy, xx = np.mgrid[Y0:Y1, X0:X1]
    circ = (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r
    nucleo = (xx - cx) ** 2 + (yy - cy) ** 2 <= (0.6 * r) ** 2
    n, lab = cv2.connectedComponents(folha, connectivity=8)
    ok = np.unique(lab[nucleo & (folha > 0)])
    m = np.isin(lab, ok[ok > 0])
    m = cv2.dilate(m.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
    m = (m | circ) & ~fora
    out = np.zeros((H, W), bool)
    out[Y0:Y1, X0:X1] = m
    return out


def aplicar(out, reg, especie=ARVORE_REC):
    rng = np.random.default_rng(SEMENTE)              # a mesma sequência da proposta (os mesmos giros)
    base = out.copy()
    H, W = out.shape[:2]
    rot = np.zeros((H, W), np.uint8)
    regioes, itens = [], []
    yy, xx = np.mgrid[0:H, 0:W]
    lote = base.astype(np.float32).mean(axis=2) < 150
    x0, y0, x1, y1 = GRAMA_PX
    grama = out[y0:y1, x0:x1].copy()
    for ((cx, cy), r, _), ((dx, dy), d) in zip(ARVORES, ARVORES_NOVAS):
        m = mancha_arvore(base, cx, cy, r)
        nao = ~lote | ((base.astype(np.int16).max(axis=2) - base.astype(np.int16).min(axis=2)) < 10)
        out = preencher(out, m, grama, nao=nao)
        regioes.append({"fonte": list(GRAMA_PX), "branco": True})
        rot[m] = len(regioes)
        it = {"png": especie, "cx": cx + dx, "cy": cy + dy, "d": d, "giro": float(rng.uniform(0, 360)),
              "espelho": False, "sombra": "arvore", "margem": True}
        out = _pousar_it(out, it)
        itens.append(it)
    out[~lote] = base[~lote]                                    # a copa e a sombra não passam para a margem
    caminho(out.copy(), rng)                                    # (só para a sequência; o caminho fica como hoje)
    for nome, (caixa, desloc, novas) in PLANTAS.items():
        x0, y0, x1, y1 = caixa
        sub = out[y0:y1, x0:x1].astype(np.int16)
        b, g, r_ = sub[..., 0], sub[..., 1], sub[..., 2]
        verde = (g - r_ > VERDE["g_r"]) & (g - b > VERDE["g_b"]) & ((sub.max(axis=2) - sub.min(axis=2)) > VERDE["sat"])
        verde = cv2.morphologyEx(verde.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        verde = cv2.dilate(verde, np.ones((7, 7), np.uint8)) > 0
        m = np.zeros(out.shape[:2], bool)
        m[y0:y1, x0:x1] = verde
        if nome in ("jardim_inverno", "jardim_garagem"):
            ys, xs = np.nonzero(~verde)
            fy, fx = int(np.median(ys)), int(np.median(xs))
            fr = [x0 + max(fx - 20, 0), y0 + max(fy - 20, 0), x0 + fx + 20, y0 + fy + 20]
        elif nome == "floreira_lavatorio":
            fr = [1226, 1650, 1424, 1656]
            m &= ~(out.astype(np.int16).mean(axis=2) < 60)
        else:
            fr = [x0 + desloc[0], y0 + desloc[1], x1 + desloc[0], y1 + desloc[1]]
        if m.any():
            out = preencher(out, m, out[fr[1]:fr[3], fr[0]:fr[2]].copy(), anel_px=6)
            regioes.append({"fonte": fr, "branco": False, "anel_px": 6})
            rot[m] = len(regioes)
        for cx, cy, planta, d in novas:
            it = {"png": planta, "cx": float(cx), "cy": float(cy), "d": float(d), "giro": float(rng.uniform(0, 360)),
                  "espelho": bool(rng.integers(0, 2)), "sombra": "planta", "margem": False}
            out = _pousar_it(out, it)
            itens.append(it)
    cv2.imwrite(str(REG_MASCARA), rot)
    reg["paisagismo"] = {"regioes": regioes, "plantas": itens}
    print(f"    paisagismo: as {len(ARVORES)} árvores de hoje viraram {NOMES[especie].lower()}s; "
          f"{len(itens) - len(ARVORES)} plantas novas (jardim de inverno, hall, jardim da garagem, floreira do "
          "lavatório); o caminho de pedras como hoje")
    return out


def pecas_12k(out, base, s, X0, Y0, reg_json):
    """No 12K: cada região do chão refeita com a textura da saída do Topaz (`base`), no tom do entorno, e as plantas
    nítidas na escala dele."""
    if not reg_json.exists() or not REG_MASCARA.exists():
        return out
    pj = json.loads(reg_json.read_text()).get("paisagismo")
    if not pj:
        return out
    rot = cv2.imread(str(REG_MASCARA), cv2.IMREAD_GRAYSCALE)
    Hh, Wh = out.shape[:2]
    for i, rg in enumerate(pj["regioes"], 1):
        ys, xs = np.nonzero(rot == i)
        if not len(ys):
            continue
        fx0, fy0, fx1, fy1 = xs.min() - 8, ys.min() - 8, xs.max() + 9, ys.max() + 9
        U0, V0 = max(int(np.floor((fx0 - X0) * s)), 0), max(int(np.floor((fy0 - Y0) * s)), 0)
        U1, V1 = min(int(np.ceil((fx1 - X0) * s)), Wh), min(int(np.ceil((fy1 - Y0) * s)), Hh)
        Mw = np.array([[1 / s, 0, U0 / s + X0 - fx0], [0, 1 / s, V0 / s + Y0 - fy0]], np.float64)
        z = (rot[fy0:fy1, fx0:fx1] == i).astype(np.float32)
        m = cv2.warpAffine(z, Mw, (U1 - U0, V1 - V0), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP) > 0.3
        m = cv2.dilate(m.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
        a, b_, c, d = rg["fonte"]
        fonte = base[int((b_ - Y0) * s):int((d - Y0) * s), int((a - X0) * s):int((c - X0) * s)].copy()
        anel = int(round(rg.get("anel_px", 10) * s))
        mg = 3 * anel + 4
        A0, B0 = max(U0 - mg, 0), max(V0 - mg, 0)
        A1, B1 = min(U1 + mg, Wh), min(V1 + mg, Hh)
        sub = out[B0:B1, A0:A1]
        mm = np.zeros(sub.shape[:2], bool)
        mm[V0 - B0:V1 - B0, U0 - A0:U1 - A0] = m
        if rg["branco"]:
            bb = base[B0:B1, A0:A1].astype(np.int16)
            nao = (bb.mean(axis=2) >= 150) | ((bb.max(axis=2) - bb.min(axis=2)) < 10)
        else:
            nao = None
        if nao is not None:
            mm &= ~nao
        if mm.any():
            preencher(sub, mm, fonte, anel_px=anel, nao=nao, sig=14.0 * s)
    for it in pj["plantas"]:
        if it["margem"]:
            antes = out.copy()
        out = _pousar_it(out, it, s, X0, Y0)
        if it["margem"]:
            r = int(it["d"] * s * 0.75) + int(0.6 * PX_M * s)
            cx, cy = int((it["cx"] - X0) * s), int((it["cy"] - Y0) * s)
            A0, B0, A1, B1 = max(cx - r, 0), max(cy - r, 0), min(cx + r, Wh), min(cy + r, Hh)
            branco = base[B0:B1, A0:A1].astype(np.float32).mean(axis=2) >= 200
            out[B0:B1, A0:A1][branco] = antes[B0:B1, A0:A1][branco]
    print(f"    paisagismo no 12K: {len(pj['regioes'])} regiões do chão refeitas da saída do Topaz, "
          f"{len(pj['plantas'])} plantas nítidas")
    return out


if __name__ == "__main__":
    folhas(cv2.imread(str(FINAL)))

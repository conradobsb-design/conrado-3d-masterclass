r"""Casa E, Térreo: as notas do cliente (Miro, "Revisão das Plantas 2") e os padrões de todas as casas (16/11/26).

A análise está em `POE642_CasaE/POE642_CasaE_analise_notas_e_padroes_1611.md`. O usuário: "siga as recomendações em
todas as perguntas e aplique no térreo"; "TRACEJADOS CONFORME O CLIENTE PEDE"; "PISCINA MAIS SOBRIA"; "3. SIM 4. SIM
5. SIM 6. CONFORME RECOMENDAÇÃO 7. CONFORME RECOMENDAÇÃO 8. CONFORME RECOMENDAÇÃO".

Parte da final do Térreo do commit `ANTES_COMMIT` (a de 11/11), sem os rótulos (`final3840_casae.sem_rotulos`, com os
ajustes de 28/10), e faz um passo por item, na ordem de `PASSOS`; os rótulos voltam no fim, no padrão de 16/11.

Uso (de POE642_CasaA/scripts/):
  python3 pedidos_terreo_casae_1611.py [--ate <passo>] [--de <passo> --cache <pasta>] [--saida <png>]
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import final3840_casae as FE                    # noqa: E402
import terreo_casaa_1011 as TA                  # noqa: E402

CASA = FE.CASA
R = CASA / "renders"
FINAL = R / "POE642_CasaE_PH_Terreo_v1_final.png"
RAIZ_GIT = AQUI.parents[2]
ANTES_COMMIT = "b6b56f0"
# a final sem as descrições das escadas e sem os rótulos (`--sem_textos`): a entrada da opção B do 12K
SEM_TEXTOS = False


def antes_img():
    """A final do Térreo do commit de base (lida do git: a final em disco é regravada aqui)."""
    import subprocess
    rel = FINAL.relative_to(RAIZ_GIT).as_posix()
    dados = subprocess.run(["git", "-C", str(RAIZ_GIT), "show", f"{ANTES_COMMIT}:{rel}"], capture_output=True,
                           check=True).stdout
    return cv2.imdecode(np.frombuffer(dados, np.uint8), cv2.IMREAD_COLOR)


def u8(a):
    return np.clip(np.round(a), 0, 255).astype(np.uint8)


def dil(m, px):
    return cv2.dilate(m.astype(np.uint8), np.ones((2 * px + 1, 2 * px + 1), np.uint8)).astype(bool)


# ----------------------------------------------------------------------------------------------------------------------
# 0. A base: a final sem os rótulos (eles voltam no fim, no padrão de 16/11)
def base(Q, img):
    limpa, _ = FE.sem_rotulos("Terreo", img, novos=True)
    return limpa


# ----------------------------------------------------------------------------------------------------------------------
# 1. A margem (regra de 16/11, "Sem o tracejado do limite do terreno"; cliente, Térreo 2: "Tirar todo o contorno
# tracejado"): fora do lote (o gramado vai de x 271 a 3455 e de y 5 a 1809), tudo branco: saem as linhas cinza
# tracejadas do lote (em x 3554 e y 2051) e a faixa de baixo; o muro de baixo termina junto com a grama (em x 3455).
MARGEM = {"lote_px": (271, 5, 3456, 1810)}


def margem(Q, img, q=MARGEM):
    out = img.copy()
    x0, y0, x1, y1 = q["lote_px"]
    fora = np.ones(out.shape[:2], bool)
    fora[y0:y1, x0:x1] = False
    out[fora] = 255
    print(f"    margem: {int((np.abs(img.astype(int) - 255).max(axis=2)[fora] > 6).sum())} px fora do lote em branco "
          "(o tracejado do lote e o muro de baixo além da grama)")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 2. Os tracejados (cliente, Térreo 2 e 3; o usuário: "TRACEJADOS CONFORME O CLIENTE PEDE"): saem todos os tracejados
# de projeção da final (`final3840_casae._tracos_te`: o L da laje do espaço gourmet e da varanda, a faixa de cima, a laje
# da garagem e os X do hall e da área de serviço descoberta, com as linhas deles), com o piso do mesmo material ao lado.
# No fim (`tracejados_finos`), voltam só os X dos vazios, finos e cinza, e as linhas da garagem, contínuas e cinza.
TRACEJADOS = {"limpa_px": 3}


def materiais(Q):
    return TA.materiais(Q)


def tracejados(Q, img, q=TRACEJADOS):
    import copy
    qq = copy.deepcopy(FE.TRACEJADOS_TE)
    qq["vaos"]["limpa_px"] = q["limpa_px"]
    qq["vaos"]["media"] = True
    FE.paredes_pdf(Q)
    mat = materiais(Q)
    fonte = np.ones(img.shape[:2], bool)
    out = FE._limpa_tracos(Q, img, [(0, 0, Q.W, Q.H)], q=qq, fonte=fonte, mesmo=mat)
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 3. O gramado (cliente, Térreo G3: "No terreno não precisa representar muitas árvores [...] Representar arbustos que são
# menores"; Subsolo A 6: "grama mais sóbria"): o verde externo refeito com o gramado da Casa B, como nas Casas C e D
# (`paisagismo_terreo_casac_1311.aplicar`), com 3 oliveiras (centro px, diâmetro px) e arbustos baixos junto aos muros
# (nome, centro px, diâmetro m).
OLIVEIRAS = [((520, 190), 230), ((3290, 640), 240), ((520, 1640), 190)]


def gramado(Q, img):
    import paisagismo_terreo_casac_1311 as PC
    guarda = PC.OLIVEIRAS
    PC.OLIVEIRAS = OLIVEIRAS
    try:
        return PC.aplicar(img)
    finally:
        PC.OLIVEIRAS = guarda


# ----------------------------------------------------------------------------------------------------------------------
# 4. O Bege Bahia menos manchado (regra de 10/11, "em todas as plantas de todas as casas"; Subsolo A 4): na chapada 232
# (o deck, a varanda, os pisantes, o acesso), as manchas a 45% do contraste, a luz, as sombras e o tom iguais
# (`terreo_casaa_1011.bege_ta`, sem a busca dos rótulos da Casa A: aqui eles já saíram). O WC DCE, que divide a
# chapada 232, vai ao piso dos banhos (passo `wc_dce`).
BEGE = dict(TA.BEGE_TA, fora_px=[(2370, 470, 2490, 650)])


def bege(Q, img, q=BEGE):
    import final3840_casaa_terreo as T
    im = img.astype(np.float32)
    B = T.F.fechar(np.all(Q.chapada == np.uint8(q["chapada"]), axis=2), 5)
    B &= ~(FE.paredes_pdf(Q) > 0.3)
    for x0, y0, x1, y1 in q["fora_px"]:
        B[y0:y1, x0:x1] = False
    f = cv2.GaussianBlur(im, (0, 0), 0.7)
    lum, croma = f.mean(axis=2), f.max(axis=2) - f.min(axis=2)
    verde = f[..., 1] > f[..., 2] + 4
    obj = T.manchas(B & ((croma < q["croma_obj"]) | (lum < q["lum_obj"]) | verde), q["area_obj"], 4000)
    obj = dil(obj, 1)
    piso = B & ~obj
    ys, xs = np.nonzero(B)
    y0, y1 = max(ys.min() - 30, 0), min(ys.max() + 31, Q.H)
    x0, x1 = max(xs.min() - 30, 0), min(xs.max() + 31, Q.W)
    sub = img[y0:y1, x0:x1].copy()
    fora = ~piso[y0:y1, x0:x1]
    sub = cv2.inpaint(sub, (fora * 255).astype(np.uint8), 5, cv2.INPAINT_TELEA)
    tom = cv2.medianBlur(sub, q["mediana_px"]).astype(np.float32)
    tom = cv2.GaussianBlur(tom, (0, 0), 1.5)
    tl = tom.mean(axis=2)
    gx, gy = cv2.Sobel(tl, cv2.CV_32F, 1, 0, ksize=3), cv2.Sobel(tl, cv2.CV_32F, 0, 1, ksize=3)
    aresta = dil(np.hypot(gx, gy) / 8 > q["aresta"], q["aresta_px"])
    D = im[y0:y1, x0:x1] / np.maximum(tom, 1)
    novo = tom * (1 + q["forca"] * (D - 1))
    m = (piso[y0:y1, x0:x1] & ~aresta).astype(np.float32)
    m = cv2.GaussianBlur(m, (0, 0), 0.8) * piso[y0:y1, x0:x1]
    out = im.copy()
    out[y0:y1, x0:x1] = im[y0:y1, x0:x1] * (1 - m[..., None]) + novo * m[..., None]
    print(f"    Bege Bahia: as manchas a {q['forca']:.0%} do contraste em {piso.sum() / Q.px_m ** 2:.0f} m²")
    return u8(out)


# ----------------------------------------------------------------------------------------------------------------------
# 5. O piso marrom (a nota da Casa D, Subsolo 2: "usar para o piso marrom tabaco a referência [...] para dar destaque
# para as bancadas e o marrom do piso ficar mais sóbrio"; a amostra do cliente da Casa A, 10/11): no granito do piso (a
# chapada (50, 66, 90): circulações, gourmet, lavabo e banho gourmet, cozinha, serviço, DCE, garagem; e o gás e a
# despensa, brancos na chapada), a amostra tecida, com a luz da final; as peças ficam (o que é claro, sem cor ou fora do
# marrom, e os preenchimentos brancos do PDF), e a borda delas é refeita pela fração (`terreo_casaa_1011.piso_marrom_ta`,
# sem os rótulos e a caracol da Casa A).
MARROM = dict(TA.PISO_MARROM_TA, chapada=(50, 66, 90), extra_px=[(1952, 418, 2026, 468), (2228, 706, 2372, 812)])


def marrom_mascara(Q, q=MARROM):
    import final3840_casaa_terreo as T
    ch = T.F.fechar(np.all(Q.chapada == np.uint8(q["chapada"]), axis=2), 5)
    for x0, y0, x1, y1 in q["extra_px"]:
        ch[y0:y1, x0:x1] |= ~(FE.paredes_pdf(Q)[y0:y1, x0:x1] > 0.3)
    return ch


def marrom(Q, img, q=MARROM):
    import final3840_casaa_terreo as T
    from scipy import ndimage
    im = img.astype(np.float32)
    ch = marrom_mascara(Q, q)
    regiao = dil(ch, 3)
    f = cv2.GaussianBlur(im, (0, 0), 0.6)
    lum, croma = f.mean(axis=2), f.max(axis=2) - f.min(axis=2)
    rb = f[..., 2] - f[..., 0]
    cand = regiao & ((lum > q["lum_obj"]) | (croma < q["croma_obj"]) | (rb < q["rb_obj"]))
    obj = T.manchas(cand, q["area_obj"], q["buraco_max"])
    cheias = T.pecas_cheias(Q).copy()
    for x0, y0, x1, y1 in q["extra_px"]:
        cheias[y0:y1, x0:x1] = False
    obj |= dil(cheias, 1) & regiao
    obj |= (FE.paredes_pdf(Q) > 0.5) & regiao
    nucleo = cv2.erode(obj.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    piso = ch & ~dil(obj, q["anel_px"] - 1)
    anel = ch & ~piso & ~nucleo
    L = cv2.medianBlur(np.clip(im.mean(axis=2), 0, 255).astype(np.uint8), q["mediana"]).astype(np.float32)
    mf = piso.astype(np.float32)
    perto = T.nconv2(L, mf, q["sig_luz"], onde=piso | anel)
    base_ = T.nconv2(L, mf, q["sig_base_m"] * Q.px_m, onde=piso | anel)
    sh = np.clip(perto / np.maximum(base_, 1) + q["limiar"], 0, 1)
    A = TA.amostra_piso(q)
    tom = A.reshape(-1, 3).mean(axis=0)
    ys, xs = np.nonzero(piso | anel)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    Tq = TA.tecido(TA.variantes(A), y1 - y0, x1 - x0, q["p_px"], q["sobra"], q["semente"])
    Tq = Tq / Tq.reshape(-1, 3).mean(axis=0) * tom
    N = im.copy()
    N[y0:y1, x0:x1] = Tq * sh[y0:y1, x0:x1, None]
    out = im.copy()
    out[piso] = N[piso]
    G = TA.nconv(cv2.medianBlur(img, q["mediana"]).astype(np.float32), mf, 2.0)
    _, (iy, ix) = ndimage.distance_transform_edt(~nucleo, return_indices=True)
    C = im[iy, ix]
    d = C - G
    den = (d * d).sum(axis=2)
    a = np.clip(((im - G) * d).sum(axis=2) / np.maximum(den, 1e-3), 0, 1)
    a = np.where(den < 400, (np.abs(im - C).sum(axis=2) < np.abs(im - G).sum(axis=2)).astype(np.float32), a)
    novo_anel = a[..., None] * C + (1 - a[..., None]) * N
    out[anel] = novo_anel[anel]
    print(f"    piso marrom: a amostra do cliente em {piso.sum() / Q.px_m ** 2:.1f} m², com a luz da final; "
          f"{int(anel.sum())} px de borda refeitos pela fração da peça")
    return u8(out)


# ----------------------------------------------------------------------------------------------------------------------
# 6. O travertino da Casa D (cliente, Térreo 25: "Colocar textura do travertino igual da casa D"): no piso de travertino
# (a chapada (202, 217, 220): living e jantar, circulação, hall, escritório, lavabo, adega), o Travertino Romano levigado
# da biblioteca da Casa D (`04-materiais/pisos-internos/travertino-romano-levigado.png`, 3,6 m de lado), no tom do
# living da final da Casa D (`ref_d_px`), com a luz da final; os veios verticais do travertino antigo saem. As peças
# ficam: a chapada já tira os móveis do PDF; o que o render desenha além deles (as bordas, os vidros, as linhas das
# esquadrias e das cortinas, as plantas) é o que foge do piso de perto (`dist`), junto às bordas (`borda_px`) ou em
# manchas grossas (`grosso_px`, que os veios finos não formam); a borda delas é refeita pela fração.
TRAVERTINO = {"png": "POE642_CasaD/biblioteca-objetos/04-materiais/pisos-internos/travertino-romano-levigado.png",
              "lado_m": 3.6, "ref_d": "POE642_CasaD/renders/POE642_CasaD_PH_Terreo_final_rotulos.png",
              "ref_d_px": (1822, 1000, 1898, 1300), "chapada": (202, 217, 220), "dist": 24, "dist_borda": 20,
              "borda_px": 7, "grosso_px": 4, "mediana": 9, "sig_luz": 1.4, "sig_base_m": 0.8, "limiar": 0.06}


def textura_travertino(Q, h, w, q=TRAVERTINO, tom=None):
    raiz = FE.RAIZ
    A = cv2.imread(str(raiz / q["png"])).astype(np.float32)
    lado = int(round(q["lado_m"] * Q.px_m))
    A = cv2.resize(A, (lado, lado), interpolation=cv2.INTER_AREA)
    if tom is None:
        x0, y0, x1, y1 = q["ref_d_px"]
        ref = cv2.imread(str(raiz / q["ref_d"]))[y0:y1, x0:x1].astype(np.float32)
        tom = ref.reshape(-1, 3).mean(axis=0)
    A = A / A.reshape(-1, 3).mean(axis=0) * np.float32(tom)
    reps = (h // lado + 2, w // lado + 2, 1)
    return np.tile(A, reps)[:h, :w]


def trocar_piso(Q, img, ch, T_full, q, nome):
    """O piso `ch` (bool) trocado pela textura `T_full` (a imagem inteira), com a luz da final; as peças que o render
    desenha sobre ele ficam (`q`: dist, dist_borda, borda_px, grosso_px, mediana, sig_luz, sig_base_m, limiar)."""
    import final3840_casaa_terreo as T
    from scipy import ndimage
    im = img.astype(np.float32)
    sub = cv2.inpaint(img, ((~ch) * 255).astype(np.uint8), 5, cv2.INPAINT_TELEA)
    med = cv2.medianBlur(sub, 21).astype(np.float32)
    dist = np.sqrt(((im - med) ** 2).sum(axis=2))
    k = 2 * q["borda_px"] + 1
    borda = cv2.dilate((~ch).astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool)
    g = q["grosso_px"]
    grosso = cv2.morphologyEx((dist > q["dist"]).astype(np.uint8), cv2.MORPH_OPEN, np.ones((g, g), np.uint8)).astype(bool)
    obj = ch & ((borda & (dist > q["dist_borda"])) | grosso)
    obj = T.manchas(obj, 12, 400)
    nucleo = obj.copy()
    obj = dil(obj, 1) & ch
    piso = ch & ~obj
    anel = obj & ~nucleo
    L = cv2.medianBlur(np.clip(im.mean(axis=2), 0, 255).astype(np.uint8), q["mediana"]).astype(np.float32)
    mf = piso.astype(np.float32)
    perto = T.nconv2(L, mf, q["sig_luz"], onde=piso | anel)
    base_ = T.nconv2(L, mf, q["sig_base_m"] * Q.px_m, onde=piso | anel)
    sh = np.clip(perto / np.maximum(base_, 1) + q["limiar"], 0, 1)
    N = T_full * sh[..., None]
    out = im.copy()
    out[piso] = N[piso]
    G = TA.nconv(sub.astype(np.float32), mf, 2.0)
    _, (iy, ix) = ndimage.distance_transform_edt(~nucleo, return_indices=True)
    C = im[iy, ix]
    d = C - G
    den = (d * d).sum(axis=2)
    a = np.clip(((im - G) * d).sum(axis=2) / np.maximum(den, 1e-3), 0, 1)
    novo_anel = a[..., None] * C + (1 - a[..., None]) * N
    out[anel] = novo_anel[anel]
    print(f"    {nome}: {piso.sum() / Q.px_m ** 2:.1f} m² trocados, com a luz da final; {int(nucleo.sum())} px de peças do "
          f"render ficam, {int(anel.sum())} px de borda pela fração")
    return u8(out)


def travertino(Q, img, q=TRAVERTINO):
    import final3840_casaa_terreo as T
    ch = T.F.fechar(np.all(Q.chapada == np.uint8(q["chapada"]), axis=2), 5) & ~(FE.paredes_pdf(Q) > 0.3)
    return trocar_piso(Q, img, ch, textura_travertino(Q, Q.H, Q.W, q), q, "travertino da Casa D")


# ----------------------------------------------------------------------------------------------------------------------
# 7. As bancadas (cliente, Térreo 4, 5, 8, 10, 13, 14 e 15; a regra de 10/11, "bancadas em Dekton Danae" na ilha e na
# pia da cozinha e nos tanques, e o marrom tabaco nas outras, mais escuro que o piso): cada bancada do PDF (pt) pintada
# no material dela, com a face um tom abaixo; as cubas e os cooktops do PDF (`ficam`, pt) e o que o render desenha
# sobre a pedra (torneiras, sombras: o que foge muito da pedra de antes) ficam.
# - Dekton Danae (`terreo_casaa_1011.danae`): a ilha da gourmet (13), a ilha e a pia da cozinha e os tanques (14);
# - marrom tabaco (o granito antigo do piso da Casa E, tecido de `marrom_tabaco_px` da final de antes): a bancada de trás
#   da gourmet (10), a da área de serviço junto à despensa (15), a do WC DCE (4) e o criado do DCE (5);
# - travertino (o da Casa D, um tom abaixo do piso): a bancada do BH gourmet (8).
BANCADAS = {
    "danae": [(990.6, 901.1, 1251.2, 963.9), (1474.7, 805.0, 1644.8, 878.8), (1392.8, 696.3, 1726.1, 734.4),
              (1734.6, 761.5, 1843.3, 802.3)],
    "marrom": [(918.2, 798.4, 1153.9, 839.1), (1901.7, 897.6, 1984.0, 931.6), (2202.4, 788.0, 2230.6, 823.9),
               (2120.0, 752.0, 2144.0, 772.0)],
    "travertino": [(1163.3, 759.8, 1252.7, 784.2)],
    "ficam": [(1153.1, 904.3, 1203.0, 932.7), (1563.7, 806.7, 1613.6, 835.0), (1559.8, 704.8, 1596.1, 729.8),
              (1523.0, 704.8, 1559.3, 729.8), (1754.2, 769.7, 1790.1, 800.0), (1791.4, 769.7, 1827.3, 800.0),
              (1058.0, 809.4, 1094.3, 834.3), (2205.7, 795.1, 2225.6, 817.8)],
    "marrom_tabaco_px": (2550, 330, 2950, 460), "face": 0.86, "dist": 60, "trav_tom": 0.94, "semente": 1616}


def _cob_pt(Q, r):
    import final3840_casaa as FA
    return FA.ret_aa(Q, r)


def _tecido_px(img, caixa, h, w, semente):
    x0, y0, x1, y1 = caixa
    return TA.tecido(TA.variantes(img[y0:y1, x0:x1].astype(np.float32)), h, w, 16, 5, semente)


def bancadas(Q, img, q=BANCADAS):
    import final3840_casaa_terreo as T
    par = FE.paredes_pdf(Q) > 0.5
    antes = antes_img()
    out = img.astype(np.float32)
    ficam = np.zeros(par.shape, bool)
    for r in q["ficam"]:
        ficam |= dil(_cob_pt(Q, r) > 0.05, 1)
    rng = np.random.default_rng(q["semente"])
    n = 0
    for tipo in ("danae", "marrom", "travertino"):
        for r in q[tipo]:
            a = _cob_pt(Q, r) * ~par
            m = a > 0.5
            ys, xs = np.nonzero(a > 0.01)
            if not len(ys):
                continue
            y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
            h, w = y1 - y0, x1 - x0
            if tipo == "danae":
                Tx = TA.danae(h, w, int(rng.integers(1 << 30)))
            elif tipo == "marrom":
                Tx = _tecido_px(antes, q["marrom_tabaco_px"], h, w, int(rng.integers(1 << 30)))[:h, :w]
            else:
                Tx = textura_travertino(Q, h, w) * q["trav_tom"]
            reg = img[y0:y1, x0:x1].astype(np.float32)
            # o que o render desenha sobre a pedra e foge muito dela (torneiras, cubas, sombras fortes) fica
            pedra = np.median(reg[m[y0:y1, x0:x1]], axis=0)
            fora = np.sqrt(((reg - pedra) ** 2).sum(axis=2)) > q["dist"]
            fora = T.manchas(fora, 8, 200)
            fica = ficam[y0:y1, x0:x1] | fora
            mm = m[y0:y1, x0:x1]
            borda = mm & ~cv2.erode(mm.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
            Tx = Tx * np.where(borda, q["face"], 1.0)[..., None]
            aa = a[y0:y1, x0:x1] * ~fica
            out[y0:y1, x0:x1] = reg * (1 - aa[..., None]) + Tx * aa[..., None]
            n += 1
    print(f"    bancadas: {len(q['danae'])} em Dekton Danae (ilhas, pia da cozinha, tanques), {len(q['marrom'])} em "
          f"marrom tabaco (gourmet, serviço, WC DCE, criado do DCE), {len(q['travertino'])} em travertino (BH gourmet)")
    return u8(out)


# ----------------------------------------------------------------------------------------------------------------------
# 8. Os armários lisos (cliente, Térreo 12 e 16: "Aqui é um armário"; "Representar os armários e prateleiras sem textura.
# Com cor sólida e neutra"; a regra de 16/11, "os outros armários [...] em cor sólida definida na casa A"): na cor dos
# armários das Casas C e D (`revisao_terreo_casac_1311.COZINHA`), lisos, com a face um tom abaixo e a sombra curta;
# px do quadro.
ARMARIOS = {"cozinha (esquerda)": (1593, 765, 1683, 809), "cozinha (direita)": (1792, 765, 1871, 809),
            "adega (em cima)": (2083, 709, 2129, 742), "despensa (L, embaixo)": (2227, 787, 2373, 810),
            "despensa (L, lado)": (2347, 717, 2373, 810), "louceiro": (1890, 912, 2205, 951),
            "escritório": (2298, 920, 2468, 948), "DCE": (2236, 556, 2264, 612)}


def armarios(Q, img, q=ARMARIOS):
    import revisao_terreo_casac_1311 as RC
    import revisao_terreo_casac_1511 as R15
    c = RC.COZINHA
    par = FE.paredes_pdf(Q) > 0.5
    o = img.astype(np.float32)
    H, W = par.shape
    for nome, (x0, y0, x1, y1) in q.items():
        a = np.zeros((H, W), np.float32)
        a[y0:y1, x0:x1] = 1.0
        a *= ~par
        m = a > 0.5
        o *= (1 - c["sombra"] * R15._sombra(a, W, H))[..., None]
        borda = m & ~cv2.erode(m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        cor = np.float32(c["cor_armario"])[None, None] * np.where(borda, c["face"], 1.0)[..., None]
        o = o * (1 - a[..., None]) + cor * a[..., None]
    print(f"    armários lisos, na cor dos armários das Casas C e D: {', '.join(q)}")
    return u8(o)


# ----------------------------------------------------------------------------------------------------------------------
# 9. O WC DCE (cliente, Térreo 4: "Cor do piso desse Banheiro é no mesmo cinza usado na casa D. A bancada é no marrom
# tabaco. Representar melhor a cuba e a torneira"; o usuário: "3. SIM"): o piso dos banhos da Casa D (a mesma amostra
# limpa do banho 1 da final da Casa D que o WC DCE dela recebeu em 16/11, sem emenda), com a luz da final; a cuba compacta
# da biblioteca (com a torneira) na cuba do PDF, sobre a bancada em marrom tabaco (passo `bancadas`).
WC_DCE = {"caixa_px": (2372, 474, 2490, 650), "amostra": ("POE642_CasaD/renders/POE642_CasaD_PH_Terreo_final_rotulos.png",
                                                           (1128, 1553, 1190, 1620)),
          "cuba_pt": (2205.7, 795.1, 2225.6, 817.8), "cuba": "banho-do-motorista/cuba-compacta"}


def wc_dce(Q, img, q=WC_DCE):
    import final3840_casaa_terreo as T
    import materiais_terreo_casac_1311 as MT
    import mobiliario_terreo_casac_1311 as MB
    ch = T.F.fechar(np.all(Q.chapada == 232, axis=2), 3) & ~(FE.paredes_pdf(Q) > 0.3)
    x0, y0, x1, y1 = q["caixa_px"]
    caixa = np.zeros(ch.shape, bool)
    caixa[y0:y1, x0:x1] = True
    ch &= caixa
    # fora do piso: a bancada (com a cuba), que vai em marrom tabaco
    for r in BANCADAS["marrom"][2:3]:
        ch &= ~dil(_cob_pt(Q, r) > 0.05, 1)
    arq, (ax0, ay0, ax1, ay1) = q["amostra"]
    A = cv2.imread(str(FE.RAIZ / arq))[ay0:ay1, ax0:ax1].astype(np.float32)
    Tf = np.zeros((Q.H, Q.W, 3), np.float32)
    Tf[y0:y1, x0:x1] = MT.sem_emenda(A, y1 - y0, x1 - x0)
    out = trocar_piso(Q, img, ch, Tf, TRAVERTINO, "WC DCE no piso dos banhos da Casa D")
    par = FE.paredes_pdf(Q) > 0.5
    P = MB.ler(q["cuba"])
    (cx0, cy0), (cx1, cy1) = Q.p2q(q["cuba_pt"][0], q["cuba_pt"][1]), Q.p2q(q["cuba_pt"][2], q["cuba_pt"][3])
    wt, ht = abs(cx1 - cx0), abs(cy1 - cy0)
    giro = 90.0 if (wt < ht) != (P.shape[1] < P.shape[0]) else 0.0
    if giro:
        wt, ht = ht, wt
    out = MB.pousar(out, P, (cx0 + cx1) / 2, (cy0 + cy1) / 2, wt, ht, giro, "baixa", par)
    print("    WC DCE: a cuba compacta da biblioteca, com a torneira, sobre a bancada em marrom tabaco")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 10. A bancada de trás da gourmet e o lavabo gourmet (cliente, Térreo 6, 7, 9, 11 e 12):
# - "Aqui tem a churrasqueira": a grelha da Casa A no módulo da esquerda do PDF (`churrasqueira_pt`), como nas Casas A e D;
# - "Aqui é uma geladeira": o refrigerador inox da biblioteca no módulo que avança (`geladeira_pt`), a frente para a
#   gourmet, como na gourmet da Casa D;
# - "Aqui é um armário": o módulo da ponta (`armario_pt`) liso, na cor dos armários;
# - "Faltou a torneira lateral": a torneira de parede do PDF na bancada do lavabo gourmet (`torneira_pt`), cromada;
# - "Tirar a soleira": a soleira da porta do lavabo gourmet (`soleira_px`) sai, com o piso marrom do lado de fora.
GOURMET = {"churrasqueira_pt": (924.0, 800.0, 993.0, 837.5), "grelha_px": 62.0,
           "geladeira_pt": (1156.7, 798.3, 1201.7, 843.3), "armario_pt": (1203.3, 798.3, 1246.7, 836.7),
           "torneira_pt": (830.3, 724.0, 830.3, 733.0), "torneira_larg_px": 2.6,
           "soleira_px": (1080, 527, 1094, 589), "soleira_desloc": -14}


def torneira(out, p0, p1, larg, ss=8):
    """A torneira de parede vista de cima: a canopla redonda em p0 e a bica cromada até p1 (px), com a sombra curta."""
    x0, y0 = min(p0[0], p1[0]) - 8, min(p0[1], p1[1]) - 8
    x1, y1 = max(p0[0], p1[0]) + 8, max(p0[1], p1[1]) + 8
    X0, Y0, X1, Y1 = int(x0), int(y0), int(np.ceil(x1)), int(np.ceil(y1))
    h, w = (Y1 - Y0) * ss, (X1 - X0) * ss
    bica = np.zeros((h, w), np.uint8)
    a = (int((p0[0] - X0) * ss), int((p0[1] - Y0) * ss))
    b = (int((p1[0] - X0) * ss), int((p1[1] - Y0) * ss))
    cv2.line(bica, a, b, 255, int(larg * ss), cv2.LINE_AA)
    cano = np.zeros((h, w), np.uint8)
    cv2.circle(cano, a, int(larg * 0.85 * ss), 255, -1, cv2.LINE_AA)
    al_b = cv2.resize(bica, (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    al_c = cv2.resize(cano, (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    al = np.maximum(al_b, al_c)
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    sombra = np.roll(np.roll(cv2.GaussianBlur(al, (0, 0), 1.0), 2, axis=0), -1, axis=1)
    reg *= (1 - 0.28 * sombra)[..., None]
    # o cromado: claro no meio, escuro nas beiras (a distância ao eixo)
    brilho = cv2.GaussianBlur(cv2.erode(al, np.ones((2, 2), np.uint8)), (0, 0), 0.6)
    cor = (np.float32((120, 122, 125)) + np.float32((105, 105, 104)) * np.clip(brilho, 0, 1)[..., None])
    reg = reg * (1 - al[..., None]) + cor * al[..., None]
    out = out.copy()
    out[Y0:Y1, X0:X1] = u8(reg)
    return out


def gourmet(Q, img, q=GOURMET):
    import mobiliario_terreo_casac_1311 as MB
    import revisao_terreo_casac_1311 as RC
    import revisao_terreo_casac_1511 as R15
    par = FE.paredes_pdf(Q) > 0.5
    out = img.copy()
    # a churrasqueira
    (a, b), (c, d) = Q.p2q(*q["churrasqueira_pt"][:2]), Q.p2q(*q["churrasqueira_pt"][2:])
    P = MB.ler("area-gourmet/grelha-churrasqueira")
    wt = q["grelha_px"]
    out = MB.pousar(out, P, (a + c) / 2, (b + d) / 2, wt, wt * P.shape[0] / P.shape[1], 0.0, "baixa", par)
    # a geladeira
    (a, b), (c, d) = Q.p2q(*q["geladeira_pt"][:2]), Q.p2q(*q["geladeira_pt"][2:])
    P = MB.ler("cozinha/geladeira-inox")
    out = MB.pousar(out, P, (a + c) / 2, (b + d) / 2, c - a - 1, d - b - 1, 0.0, "movel", par)
    # o armário
    cz = RC.COZINHA
    al = _cob_pt(Q, q["armario_pt"]) * ~par
    m = al > 0.5
    o = out.astype(np.float32)
    o *= (1 - cz["sombra"] * R15._sombra(al, Q.W, Q.H))[..., None]
    borda = m & ~cv2.erode(m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    cor = np.float32(cz["cor_armario"])[None, None] * np.where(borda, cz["face"], 1.0)[..., None]
    out = u8(o * (1 - al[..., None]) + cor * al[..., None])
    # a soleira do lavabo gourmet sai: o piso de logo ao lado (fora das paredes)
    x0, y0, x1, y1 = q["soleira_px"]
    dx = q["soleira_desloc"]
    fonte = out[y0:y1, x0 + dx:x1 + dx].copy()
    reg = out[y0:y1, x0:x1]
    p = par[y0:y1, x0:x1]
    reg[~p] = fonte[~p]
    out[y0:y1, x0:x1] = reg
    # a torneira lateral do lavabo gourmet
    p0, p1 = Q.p2q(*q["torneira_pt"][:2]), Q.p2q(*q["torneira_pt"][2:])
    out = torneira(out, p0, p1, q["torneira_larg_px"])
    print("    gourmet: a churrasqueira no módulo da esquerda, o refrigerador inox no módulo que avança, o armário liso "
          "na ponta; o lavabo gourmet com a torneira lateral e sem a soleira")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 11. A piscina, a prainha e o spa (cliente, Térreo 19 a 22; o usuário: "PISCINA MAIS SOBRIA"):
# - a água mais sóbria: o turquesa da opção C perde metade da saturação (`sat`) e vai um pouco para o cinza-esverdeado da
#   foto do cliente da Casa A; o desenho (o Barlavento, as ondinhas e o brilho) fica;
# - a diferença de profundidade (21): a parte funda (a piscina e o miolo do spa, os px mais escuros da água) mais escura
#   (`funda`), a rasa (a prainha e o banco do spa) clara, e o degrau entre elas com a sombra do lado fundo (`degrau`);
# - "Aqui é parede" (19): as duas faixas brancas do PDF na borda esquerda (`paredes_pt`), que o render fazia de vidro,
#   no cinza das paredes;
# - a borda lisa em alto-relevo (regra de 16/11) e sem a linha clara em volta do spa (22): a faixa de Bege Bahia em volta
#   da água (`borda_px`), lisa, um tom abaixo do deck, com a quina junto à água um pouco mais clara
#   (`pedidos_terreo_casad_1611._bege_levigado`), só sobre o Bege Bahia da chapada.
PISCINA = {"paredes_pt": [(501.4, 1108.1, 509.4, 1277.4), (532.6, 1108.1, 541.0, 1277.4)], "parede": (80, 80, 80),
           "sat": 0.5, "tinta": (0.97, 1.0, 1.03), "funda": 0.86, "rasa": 1.0, "degrau": (0.82, 4.0),
           "borda_px": 18, "fio_deck": 0.97, "rotulos": ("PISCINA", "PRAINHA", "SPA"), "resto_croma": 7, "quina": 1.03, "beira_agua": 0.86}


def agua_e(Q):
    import piscinas_turquesa as PT
    import final3840_casaa as FA
    a = np.zeros((Q.H, Q.W), np.float32)
    for r in PT.BORDAS["E-Terreo"]["agua"]:
        r = r[0] if isinstance(r[0], (list, tuple)) else r
        a = np.maximum(a, FA.ret_aa(Q, r))
    return a


def piscina(Q, img, q=PISCINA):
    import final3840_casaa_terreo as T
    import pedidos_terreo_casad_1611 as PD
    a = agua_e(Q)
    ag = a > 0.5
    # os restos dos rótulos de antes na água (o texto turquesa que a conta inversa deixou): nas caixas deles, o que tem
    # mais cor que a água de perto sai pelos vizinhos
    img = img.copy()
    cr = img.astype(np.int16).max(axis=2) - img.astype(np.int16).min(axis=2)
    crm = cv2.medianBlur(np.clip(cr, 0, 255).astype(np.uint8), 9).astype(np.int16)
    resto = np.zeros(ag.shape, bool)
    for x0, y0, x1, y1 in FE.caixas_rotulos("Terreo", q["rotulos"]):
        caixa = np.zeros(ag.shape, bool)
        caixa[y0 - 4:y1 + 4, x0 - 4:x1 + 4] = True
        resto |= caixa & ag & (cr - crm > q["resto_croma"])
    resto = dil(resto, 1) & ag
    img = cv2.inpaint(img, resto.astype(np.uint8), 3, cv2.INPAINT_TELEA)
    im = img.astype(np.float32)
    # a funda e a rasa pela luz da água (Otsu dentro dela), suavizada
    L = cv2.GaussianBlur(im.mean(axis=2), (0, 0), 6)
    v = np.clip(L[ag], 0, 255).astype(np.uint8)
    lim, _ = cv2.threshold(v.reshape(-1, 1), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    funda = (L < lim) & ag
    funda = cv2.morphologyEx(funda.astype(np.uint8), cv2.MORPH_OPEN, np.ones((9, 9), np.uint8)).astype(bool)
    wf = cv2.GaussianBlur(funda.astype(np.float32), (0, 0), 1.2)
    lum = im.mean(axis=2, keepdims=True)
    novo = lum + (im - lum) * q["sat"]
    novo = novo * np.float32(q["tinta"])
    novo = novo * (q["funda"] * wf + q["rasa"] * (1 - wf))[..., None]
    # o degrau: a sombra no lado fundo, junto à rasa
    rasa = ag & ~funda
    d = cv2.distanceTransform((~rasa).astype(np.uint8), cv2.DIST_L2, 3)
    f, alc = q["degrau"]
    sombra = np.where(funda, 1 - (1 - f) * np.clip(1 - d / alc, 0, 1), 1.0)
    novo = novo * sombra[..., None]
    out = im * (1 - a[..., None]) + novo * a[..., None]
    # a borda lisa de Bege Bahia em volta da água (só sobre o Bege Bahia da chapada)
    bege = T.F.fechar(np.all(Q.chapada == 232, axis=2), 3) & ~(FE.paredes_pdf(Q) > 0.3)
    w = q["borda_px"]
    perto = cv2.dilate(ag.astype(np.uint8), np.ones((2 * w + 1, 2 * w + 1), np.uint8)) > 0
    capa = perto & ~ag & bege
    ys, xs = np.nonzero(capa)
    Y0, Y1, X0, X1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    Tb = PD._bege_levigado(Y1 - Y0, X1 - X0, PD.BORDA_PISCINA)
    reg = out[Y0:Y1, X0:X1]
    m = capa[Y0:Y1, X0:X1]
    agr = ag[Y0:Y1, X0:X1]
    fora = m & (cv2.dilate((~m & ~agr).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0)
    quina = m & (cv2.dilate(agr.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0)
    Tb = Tb * np.where(fora, q["fio_deck"], 1.0)[..., None] * np.where(quina, q["quina"], 1.0)[..., None]
    reg[m] = Tb[m]
    beira = agr & (cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0)
    reg[beira] *= q["beira_agua"]
    # as duas faixas da borda esquerda, parede
    for r in q["paredes_pt"]:
        ap = _cob_pt(Q, r)[..., None]
        out = out * (1 - ap) + np.float32(q["parede"]) * ap
    print(f"    piscina: a água mais sóbria (saturação a {q['sat']:.0%}), a funda mais escura que a rasa com a sombra do "
          f"degrau; a borda lisa de Bege Bahia ({w / Q.px_m:.2f} m), sem a linha clara do spa; as duas faixas da borda "
          "esquerda em parede")
    return u8(out)


# ----------------------------------------------------------------------------------------------------------------------
# 12. As escadas (cliente, Térreo G1: "Colocar a seta em todas as escadas"; 17 e 18: "Não deixar os degraus cortados
# branco. Deixar transparente mas na mesma cor da escada. Exemplo casa C"; as regras de 10/11 e 12/11, o triângulo, a
# descrição e o S/D sob a seta):
# - os degraus cortados (o branco da escada da gourmet e da do living) no tom dos degraus de antes do corte, sob um véu
#   claro (`veu`), com os degraus marcados como estavam (`relevo`);
# - o triângulo cheio no 1º degrau de quem chega por este pavimento, logo acima da letra S/D que já está nele, com a ponta
#   no sentido do percurso; a descrição em duas linhas, no corpo das descrições (preto no piso claro, branco no granito).
ESCADAS = {"cortadas": [(1151, 412, 1457, 483), (1875, 961, 2218, 1048)], "branco_lum": 222, "branco_croma": 16,
           "veu": 0.35, "veu_cor": (234, 236, 236), "relevo": 1.6,
           "setas": [
               # (centro do triângulo px, direção, texto, (x, y meio), alinhar, cor)
               ((1159.5, 430.0), (1, 0), ("DESCE PARA O", "SUBSOLO"), (1304.0, 392.0), "centro", (236, 236, 236)),
               ((2207.0, 986.0), (-1, 0), ("SOBE PARA O", "1º PAVIMENTO"), (1866.0, 1004.0), "direita", (20, 20, 20)),
               ((774.0, 1352.0), (-1, 0), ("DESCE PARA O", "JARDIM"), (622.0, 1462.0), "centro", (20, 20, 20))],
           "tri": (13.0, 15.0), "tri_cor": (30, 30, 30)}


def alfa_escada(txt, x, y, al, forma):
    return TA.alfa_texto(txt, x, y, al, corpo=TA.ESCADAS_TA["corpo_desc_px"], forma=forma)


def escadas(Q, img, q=ESCADAS):
    out = img.astype(np.float32)
    for x0, y0, x1, y1 in q["cortadas"]:
        reg = out[y0:y1, x0:x1]
        lum = reg.mean(axis=2)
        croma = reg.max(axis=2) - reg.min(axis=2)
        branco = (lum > q["branco_lum"]) & (croma < q["branco_croma"])
        branco = cv2.morphologyEx(branco.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8)).astype(bool)
        degrau = ~branco & (lum > 120)
        tom = np.median(reg[degrau], axis=0)
        alvo = tom * (1 - q["veu"]) + np.float32(q["veu_cor"]) * q["veu"]
        lb = np.median(lum[branco])
        sh = 1 + q["relevo"] * (lum / max(lb, 1) - 1)
        novo = alvo[None, None] * sh[..., None]
        a = cv2.GaussianBlur(branco.astype(np.float32), (0, 0), 0.5) * branco
        out[y0:y1, x0:x1] = reg * (1 - a[..., None]) + novo * a[..., None]
    for (tx, ty), d, txt, (x, y), al, cor in q["setas"]:
        out = TA.triangulo(out, TA.seta_tri(tx, ty, d, *q["tri"]), q["tri_cor"])
    # as descrições vão no fim, com os rótulos (`descricoes_escadas`): escritas aqui, o piso que o mobiliário refaz em
    # volta (o jantar, junto ao SOBE PARA O 1º PAVIMENTO) tirava a luz das letras e deixava uma mancha cinza reta
    print(f"    escadas: os degraus cortados de {len(q['cortadas'])} escadas no tom delas, sob um véu claro; o triângulo "
          f"nas {len(q['setas'])} escadas (as descrições vão com os rótulos: {'; '.join(' '.join(s[2]) for s in q['setas'])})")
    return u8(out)


# ----------------------------------------------------------------------------------------------------------------------
# 13. Peças soltas:
# - o guarda-corpo do deck (cliente, Térreo 1: "Representar o guarda-corpo", na borda do deck junto ao gramado; o PDF não
#   o desenha): a lâmina de vidro do padrão da Casa A (o vidro claro, as faces finas, o brilho e a sombra curta) na borda
#   de baixo do deck e da varanda, onde eles encontram o gramado, da floreira em L até a parede do living (`guarda_px`);
# - a seta da entrada (cliente, Térreo 27: "Centralizar a seta com a abertura da porta, usando este modelo de seta"): a
#   seta de linha sai (o Bege Bahia de logo abaixo) e entra o triângulo cheio das Casas C e D, no meio do vão da pivotante
#   (y 1408, entre os batentes do PDF), apontando para dentro;
# - o jardim de inverno (cliente, Térreo 24: "Diminuir tamanho e quantidade"): como o jardim de 4,79 m² da Casa A, a
#   grama no tom do gramado e poucas plantas menores (`jardim_plantas`: nome, centro px, diâmetro m);
# - a mesa do jantar (cliente, Térreo 23: "Mudar o amadeirado dessa mesa"): em nogueira, como as mesas da Casa D.
SOLTAS = {"guarda_px": (1111.0, 1643.6, 1580.0, 1646.0),
          "seta_velha_px": (2497, 1392, 2592, 1424), "seta_desloc": 34, "seta_px": (2513.0, 1408.1), "seta": (18.0, 21.0),
          "jardim_px": (1878, 1049, 2217, 1123), "jardim_chapada": (58, 122, 79),
          "jardim_plantas": [("filodendro-xanadu", (1935, 1086), 0.55), ("moreia", (2160, 1088), 0.5)],
          "mesa": {"pdf": 86965, "cor": (50, 76, 112), "gama": 0.9, "sat_min": 25, "lum_max": 185},
          "folhas_px": (1876, 1123, 2219, 1141)}


def soltas(Q, img, q=SOLTAS):
    import final3840_casaa_terreo as T
    import materiais_terreo_casac_1311 as MT
    import paisagismo_terreo_casac_1311 as PC
    import paisagismo_terreo_casab_1311 as PB
    import pedidos_terreo_casad_1611b as PD2
    out = img.copy()
    # o guarda-corpo
    x0, y0, x1, y1 = q["guarda_px"]
    r = (*Q.q2p(x0, y0), *Q.q2p(x1, y1))
    out = u8(TA.vidro_laminas(Q, out, [r], TA.ESCADAS_TA["jardim"]["vidro"]))
    # a seta da entrada
    x0, y0, x1, y1 = q["seta_velha_px"]
    d = q["seta_desloc"]
    out[y0:y1, x0:x1] = out[y0 + d:y1 + d, x0:x1]
    o = out.astype(np.float32)
    o = TA.triangulo(o, TA.seta_tri(*q["seta_px"], (-1, 0), *q["seta"]))
    out = u8(o)
    # o jardim de inverno
    jx0, jy0, jx1, jy1 = q["jardim_px"]
    ji = np.zeros(out.shape[:2], bool)
    ji[jy0:jy1, jx0:jx1] = True
    ji &= T.F.fechar(np.all(Q.chapada == np.uint8(q["jardim_chapada"]), axis=2), 3) & ~(FE.paredes_pdf(Q) > 0.3)
    B = cv2.imread(str(PC.FINAL_B))
    gx0, gy0, gx1, gy1 = PC.GRAMA_B
    G = MT.sem_emenda(B[gy0:gy1, gx0:gx1].astype(np.float32), jy1 - jy0, jx1 - jx0)
    reg = out[jy0:jy1, jx0:jx1].astype(np.float32)
    m = ji[jy0:jy1, jx0:jx1]
    reg[m] = G[m]
    out[jy0:jy1, jx0:jx1] = u8(reg)
    base_ = out.copy()
    rng = np.random.default_rng(1624)
    for nome, (cx, cy), dm in q["jardim_plantas"]:
        out = PB.pousar(out, PB.ler(nome), cx, cy, dm * Q.px_m, float(rng.uniform(0, 360)))
    out[~ji] = base_[~ji]
    # as folhas do jardim antigo que passavam da borda, sobre o travertino: a faixa logo abaixo do jardim recebe o
    # piso de logo abaixo dela
    fx0, fy0, fx1, fy1 = q["folhas_px"]
    faixa = ~ji[fy0:fy1, fx0:fx1] & ~(FE.paredes_pdf(Q)[fy0:fy1, fx0:fx1] > 0.3)
    ys, xs = np.nonzero(faixa)
    out[fy0 + ys, fx0 + xs] = out[fy0 + ys + (fy1 - fy0), fx0 + xs]
    # e as que passavam dos lados (poucos px verdes junto às pontas): pelos vizinhos
    lx0, ly0, lx1, ly1 = jx0 - 14, jy0 - 4, jx1 + 14, jy1 + 4
    reg = out[ly0:ly1, lx0:lx1].astype(np.int16)
    verde = dil((reg[..., 1] > reg[..., 2] + 6) & ~ji[ly0:ly1, lx0:lx1], 1) & ~ji[ly0:ly1, lx0:lx1]
    if verde.any():
        out[ly0:ly1, lx0:lx1] = cv2.inpaint(np.ascontiguousarray(out[ly0:ly1, lx0:lx1]), verde.astype(np.uint8), 3,
                                            cv2.INPAINT_TELEA)
    # a mesa do jantar (só a madeira: a cor quente e mais escura que o piso)
    mq = q["mesa"]
    import regras_terreo_casab_1311 as RT
    x0, y0, x1, y1 = RT.caixa_pdf(Q, mq["pdf"])
    X0, Y0, X1, Y1 = int(np.floor(x0)), int(np.floor(y0)), int(np.ceil(x1)), int(np.ceil(y1))
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    rr = reg.astype(np.int16)
    madeira = (rr[..., 2] - rr[..., 0] >= mq["sat_min"]) & (rr.mean(axis=2) > 60) & (rr.mean(axis=2) < mq["lum_max"])
    madeira &= ~dil(rr[..., 1] > rr[..., 2] - 4, 2)
    L = reg.mean(axis=2)
    med = float(np.median(L[madeira]))
    rel = np.clip(L / max(med, 1.0), 0.5, 1.6) ** mq["gama"]
    novo = np.float32(mq["cor"])[None, None] * rel[..., None]
    reg[madeira] = novo[madeira]
    out[Y0:Y1, X0:X1] = u8(reg)
    print("    o guarda-corpo de vidro na borda do deck e da varanda junto ao gramado; o triângulo da entrada no meio do "
          "vão da porta; o jardim de inverno na grama, com 3 plantas menores; a mesa do jantar em nogueira")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 13b. As cortinas no padrão de todas as casas (16/11, "O padrão das casas é a C4, bem visível";
# `cortinas_padrao_casad_1611.aplicar`, o da Casa D): o linho em ondas com o trilho grafite nos trechos do PDF (o vidro de
# baixo do living e o do escritório) e, fora deles, no vidro da esquerda do living (`extra`: o vidro, x da face, o
# trecho), onde a cortina de linha fina de antes (`velha_px`) sai antes, com o piso de logo ao lado.
# (16/11, "Revise todas as cortinas e adote o padrão que escolhemos": a C4, "os painéis da mesma janela num trilho só,
# de parede a parede") os dois trechos do PDF na fachada de baixo do living (x 1595 a 1770 e 1921 a 2096, na mesma linha
# do vidro, sem parede entre eles) viram um trilho só, de parede a parede
CORTINAS = {"velha_px": (1590, 912, 1599, 1537), "desloc": 10, "extra": [("v", "esquerda", 1581.0, 912.0, 1536.0)],
            "unir": [("h", "baixo", 1542.1)]}


def cortinas(Q, img, q=CORTINAS):
    import cortinas_padrao_casad_1611 as CP
    import pedidos_terreo_casac_1311 as PT
    out = img.copy()
    x0, y0, x1, y1 = q["velha_px"]
    d = q["desloc"]
    out[y0:y1, x0:x1] = out[y0:y1, x0 + d:x1 + d]
    orig = PT.C.trechos_cortina_tc

    def unidos(*a, **k):
        tr = orig(*a, **k)
        novo = []
        for o, v, ex in q["unir"]:
            mesmos = [t for t in tr if t[0] == o and t[1] == v and abs(t[2] - ex) < 2]
            if len(mesmos) > 1:
                tr = [t for t in tr if t not in mesmos]
                novo.append((o, v, ex, min(t[3] for t in mesmos), max(t[4] for t in mesmos)))
        return list(tr) + novo
    PT.C.trechos_cortina_tc = unidos
    try:
        return CP.aplicar(Q, out, q=dict(CP.CORTINAS_D, extra=q["extra"]))
    finally:
        PT.C.trechos_cortina_tc = orig


# ----------------------------------------------------------------------------------------------------------------------
# 14. Os rótulos no padrão de todas as casas (16/11, `rotulos_padrao_casad_1611`): Inter Regular, o nome e a área em
# duas linhas (15 px entre as bases), um corpo só (10,95 px; `pequeno`, 9,6 px, só onde não cabe), no meio do piso livre
# de cada ambiente, as fileiras vizinhas pela mesma base. A cor pelo fundo (o escuro 20 nos pisos claros, o claro 236 no
# granito, no gramado e na água funda): a mediana da luz do fundo na caixa do texto. (nome, linhas, (meio x, base da 1ª
# linha) px, corpo)
ROTULOS = [
    # usuário, 16/11: "RÓTULOS CENTRALIZADOS E PADRONIZADOS." Todos no corpo `normal`; cada um no meio do piso livre do
    # ambiente (fora dos objetos e do box), e as fileiras e colunas vizinhas alinhadas: JARDIM, CIRCULAÇÃO (social) e
    # LOUCEIRO no eixo 2047; ÁREA DE SERVIÇO DESCOBERTA e ÁREA DE SERVIÇO no 2085; JARDIM e ESCRITÓRIO na base 1090 (entre
    # as cadeiras novas e a poltrona do escritório);
    # CIRCULAÇÃO e GARAGEM na 858; DCE e WC DCE 1 na 596; DESPENSA e CPD na 752 (ELEVADOR na base da 2ª linha deles);
    # PISCINA e PRAINHA na 1014. Os abertos (circulações de cima, varanda, deck) ficam no ponto do PDF. Só o WC DCE 1
    # (0,79 m livre fora do box) não cabe a linha no `normal`: vai no `wc`, com ~4 px de folga.
    ("CIRCULAÇÃO GOURMET", ("CIRCULAÇÃO GOURMET", "A: 57,04 m²"), (1515.0, 352.0), "normal"),
    ("CIRCULAÇÃO (serviço)", ("CIRCULAÇÃO", "A: 67,87 m²"), (2105.0, 352.0), "normal"),
    ("LAVABO GOURMET", ("LAVABO GOURMET", "A: 6,71 m²"), (1108.0, 550.0), "normal"),
    ("BH GOURMET", ("BH GOURMET", "A: 5,92 m²"), (1370.0, 523.0), "normal"),
    ("ÁREA GOURMET", ("ÁREA GOURMET", "A: 39,78 m²"), (1297.0, 674.0), "normal"),
    ("GÁS", ("GÁS",), (1984.0, 449.0), "normal"),
    ("ÁREA DE SERVIÇO DESCOBERTA", ("ÁREA DE SERVIÇO DESCOBERTA", "A: 8,17 m²"), (2085.0, 501.0), "normal"),
    ("DCE", ("DCE", "A: 6,08 m²"), (2326.0, 596.0), "normal"),
    ("WC DCE 1", ("WC DCE 1", "A: 3,04 m²"), (2422.5, 596.0), "wc"),
    ("COZINHA", ("COZINHA", "A: 31,27 m²"), (1770.0, 728.0), "normal"),
    ("ÁREA DE SERVIÇO", ("ÁREA DE SERVIÇO", "A: 16,34 m²"), (2085.0, 651.0), "normal"),
    ("ELEVADOR", ("ELEVADOR",), (2002.0, 767.0), "normal"),
    ("ADEGA", ("ADEGA", "A: 2,59 m²"), (2150.0, 792.0), "normal"),
    ("DESPENSA", ("DESPENSA", "A: 3,92 m²"), (2286.0, 752.0), "normal"),
    ("CPD", ("CPD", "A: 2,56 m²"), (2430.0, 752.0), "normal"),
    ("GARAGEM", ("GARAGEM", "A: 64,54 m²"), (2765.0, 858.0), "normal"),
    ("CIRCULAÇÃO (social)", ("CIRCULAÇÃO", "A: 21,23 m²"), (2047.0, 858.0), "normal"),
    ("LOUCEIRO", ("LOUCEIRO", "A: 3,71 m²"), (2047.0, 930.0), "normal"),
    ("JARDIM", ("JARDIM", "A: 7,08 m²"), (2047.0, 1090.0), "normal"),
    ("LIVING E SALA DE JANTAR", ("LIVING E SALA DE JANTAR", "A: 89,87 m²"), (1910.0, 1229.0), "normal"),
    ("ESCRITÓRIO", ("ESCRITÓRIO", "A: 13,59 m²"), (2380.0, 1090.0), "normal"),
    ("CIRCULAÇÃO (escritório)", ("CIRCULAÇÃO", "A: 7,11 m²"), (2244.0, 1160.0), "normal"),
    ("LAVABO", ("LAVABO", "A: 6,21 m²"), (2382.0, 1246.0), "normal"),
    ("HALL DE ENTRADA", ("HALL DE ENTRADA", "A: 16,63 m²"), (2351.0, 1452.0), "normal"),
    ("VARANDA", ("VARANDA", "A: 78,14 m²"), (1300.0, 1192.0), "normal"),
    ("DECK", ("DECK", "A: 44,67 m²"), (975.0, 1442.0), "normal"),
    ("PISCINA", ("PISCINA", "A: 14,14 m²"), (837.0, 1014.0), "normal"),
    ("PRAINHA", ("PRAINHA", "A: 7,61 m²"), (1055.0, 1014.0), "normal"),
    ("SPA", ("SPA", "A: 6,5 m²"), (1055.0, 1197.0), "normal"),
]
CORPOS = {"normal": (10.95, 15.0), "pequeno": (9.6, 13.1), "wc": (9.0, 12.3)}
ESCURO, CLARO = (20, 20, 20), (236, 236, 236)


def linhas_rotulo(r):
    from rodape_entrega import FONTES
    nome, ls, (cx, b0), tam = r
    corpo, e = CORPOS[tam]
    f = str(FONTES / "Inter-Regular.otf")
    return [(tx, f, corpo, cx, b0 + i * e) for i, tx in enumerate(ls)]


def alfa_rotulo(r, forma):
    import revisao_terreo_casac_1411 as R14
    a = R14.desenhar_linhas(np.zeros((*forma, 3), np.float32), linhas_rotulo(r), (255, 255, 255))
    return np.clip(a[..., 0] / 255, 0, 1)


def caixas_rotulos(forma, nomes=None, folga=0):
    cx = {}
    for r in ROTULOS:
        if nomes is not None and r[0] not in nomes:
            continue
        ys, xs = np.nonzero(alfa_rotulo(r, forma) > 0.02)
        cx[r[0]] = (xs.min() - folga, ys.min() - folga, xs.max() + 1 + folga, ys.max() + 1 + folga)
    return cx


def cor_rotulo(r, img, lum=None):
    """Escuro no piso claro, claro no escuro (a mediana da luz na caixa do rótulo, antes dele)."""
    lum = cv2.GaussianBlur(img.astype(np.float32).mean(axis=2), (0, 0), 3) if lum is None else lum
    a = alfa_rotulo(r, img.shape[:2])
    ys, xs = np.nonzero(a > 0.02)
    fundo = float(np.median(lum[ys.min() - 3:ys.max() + 4, xs.min() - 3:xs.max() + 4]))
    return ESCURO if fundo > 125 else CLARO


def descricoes_escadas(out, q=ESCADAS):
    for _, _, txt, (x, y), al, cor in q["setas"]:
        out = TA.compor(out, alfa_escada(txt, x, y, al, out.shape[:2]), cor)
    return out


def rotulos(Q, img):
    import revisao_terreo_casac_1411 as R14
    if SEM_TEXTOS:                               # a opção B do 12K: os textos voltam na Kalam (`ampliacao_12k_casae`)
        print("    rótulos e descrições das escadas: fora (a final sem textos, entrada da opção B do 12K)")
        return img
    out = descricoes_escadas(img.astype(np.float32))
    lum = cv2.GaussianBlur(img.astype(np.float32).mean(axis=2), (0, 0), 3)
    escuros = []
    for r in ROTULOS:
        cor = cor_rotulo(r, img, lum)
        if cor == CLARO:
            escuros.append(r[0])
        out = R14.desenhar_linhas(out, linhas_rotulo(r), cor)
    print(f"    rótulos: {len(ROTULOS)} no padrão (Inter, 2 linhas, um corpo; 9 px só no WC DCE 1), em claro sobre o fundo "
          f"escuro ({', '.join(escuros)}) e em escuro nos outros")
    return u8(out)


# ----------------------------------------------------------------------------------------------------------------------
# 15. Os tracejados que voltam (cliente, Térreo 3 e 26; o usuário: "TRACEJADOS CONFORME O CLIENTE PEDE"): só os dos
# vazios, finos e cinza (o desenho do Térreo da Casa A, 10/11: ~0,9 px, cinza 112 no piso claro e 205 no escuro): o X do
# hall com a linha da esquerda, o X da área de serviço descoberta com a linha de baixo; os traços param em volta dos
# rótulos que caem neles (como o X do shaft da Casa B) e não passam sobre os móveis e as paredes. As linhas da laje da
# garagem (3: "Representar essas linhas na cor cinza ou preta sem ser tracejada"), contínuas, finas e em cinza escuro,
# fora do bloco do DCE.
FINOS = {"x_px": [((2227, 1328), (2476, 1576)), ((2476, 1328), (2227, 1549)), ((2227, 1328), (2227, 1549)),
                  ((1954, 468), (2217, 538)), ((2217, 435), (1954, 538)), ((1954, 538), (2217, 538))],
         "traco_px": 9.0, "vao_px": 4.5, "larg_px": 0.9, "escuro": (112, 112, 112), "claro": (205, 205, 205),
         "limiar": 125, "folga_rotulo": 7, "rotulos": ("HALL DE ENTRADA", "ÁREA DE SERVIÇO DESCOBERTA"),
         "garagem_px": [((2490.0, 485.9), (3037.6, 485.9)), ((3037.6, 485.9), (3037.6, 909.8)),
                        ((3037.6, 909.8), (2490.0, 909.8))], "garagem_larg": 1.0, "garagem_cor": (62, 62, 62),
         "obj_dist": 34}


def _alfa_segmentos(forma, segs, larg, ss=8):
    """O alfa (com antialias) de segmentos [(p0, p1)] em px."""
    H, W = forma
    pts = np.float32([p for s in segs for p in s])
    x0, y0 = np.floor(pts.min(axis=0)).astype(int) - 3
    x1, y1 = np.ceil(pts.max(axis=0)).astype(int) + 4
    m = np.zeros(((y1 - y0) * ss, (x1 - x0) * ss), np.uint8)
    for p0, p1 in segs:
        a = (int(round((p0[0] - x0) * ss)), int(round((p0[1] - y0) * ss)))
        b = (int(round((p1[0] - x0) * ss)), int(round((p1[1] - y0) * ss)))
        cv2.line(m, a, b, 255, max(1, int(round(larg * ss))), cv2.LINE_AA)
    al = np.zeros((H, W), np.float32)
    al[y0:y1, x0:x1] = cv2.resize(m.astype(np.float32) / 255, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)
    return al


def _tracejar(p0, p1, traco, vao):
    p0, p1 = np.float32(p0), np.float32(p1)
    L = float(np.hypot(*(p1 - p0)))
    d = (p1 - p0) / max(L, 1e-6)
    segs, t = [], 0.0
    while t < L:
        t1 = min(L, t + traco)
        segs.append((tuple(p0 + d * t), tuple(p0 + d * t1)))
        t = t1 + vao
    return segs


def tracejados_finos(Q, img, q=FINOS):
    import final3840_casaa_terreo as T
    par = dil(FE.paredes_pdf(Q) > 0.3, 1)
    im = img.astype(np.float32)
    med = cv2.medianBlur(img, 15).astype(np.float32)
    obj = T.manchas(np.sqrt(((im - med) ** 2).sum(axis=2)) > q["obj_dist"], 20, 400)
    obj = dil(obj, 2)
    caixa_rot = np.zeros(par.shape, bool)
    for x0, y0, x1, y1 in caixas_rotulos(img.shape[:2], q["rotulos"], q["folga_rotulo"]).values():
        caixa_rot[y0:y1, x0:x1] = True
    segs = [s for p0, p1 in q["x_px"] for s in _tracejar(p0, p1, q["traco_px"], q["vao_px"])]
    a = _alfa_segmentos(par.shape, segs, q["larg_px"]) * ~par * ~caixa_rot * ~obj
    lum = cv2.GaussianBlur(med.mean(axis=2), (0, 0), 2)
    cor = np.where((lum > q["limiar"])[..., None], np.float32(q["escuro"]), np.float32(q["claro"]))
    out = im * (1 - a[..., None]) + cor * a[..., None]
    ag = _alfa_segmentos(par.shape, q["garagem_px"], q["garagem_larg"]) * ~par
    out = out * (1 - ag[..., None]) + np.float32(q["garagem_cor"]) * ag[..., None]
    print("    tracejados: os X do hall e da área de serviço descoberta finos e cinza, abertos sob os rótulos; as "
          "linhas da laje da garagem contínuas, finas, em cinza escuro")
    return u8(out)


# ----------------------------------------------------------------------------------------------------------------------
# O antes e depois (a final de `ANTES_COMMIT` e a nova), por trecho: `renders/POE642_CasaE_PH_Terreo_1611_<nome>_
# antes_depois.jpg`; a planta inteira com o antes em cima e o depois embaixo, os trechos lado a lado.
ANTES_DEPOIS = {"planta": (250, 0, 3600, 1830), "gourmet": (930, 380, 1480, 800), "cozinha_servico": (1580, 420, 2500, 830),
                "living_jantar": (1580, 820, 2480, 1560), "piscina_deck": (600, 880, 1180, 1680),
                "varanda": (1150, 880, 1600, 1680), "hall_escritorio": (2270, 900, 2660, 1600),
                "garagem": (2400, 280, 3600, 1000)}


def antes_depois(antes, depois, q=ANTES_DEPOIS):
    from PIL import Image, ImageDraw, ImageFont
    F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
    for nome, (x0, y0, x1, y1) in q.items():
        A = Image.fromarray(antes[y0:y1, x0:x1, ::-1])
        D = Image.fromarray(depois[y0:y1, x0:x1, ::-1])
        if nome == "planta":
            k = 1800 / A.width
            A, D = (im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS) for im in (A, D))
            out = Image.new("RGB", (A.width, A.height * 2 + 100), "white")
            dr = ImageDraw.Draw(out)
            dr.text((10, 8), "ANTES (11/11)", fill=(20, 20, 20), font=F)
            out.paste(A, (0, 44))
            dr.text((10, A.height + 56), "DEPOIS (16/11)", fill=(20, 20, 20), font=F)
            out.paste(D, (0, A.height + 96))
        else:
            k = min(1700 / (2 * A.width), 900 / A.height, 3.0)
            A, D = (im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS) for im in (A, D))
            out = Image.new("RGB", (A.width * 2 + 20, A.height + 44), "white")
            dr = ImageDraw.Draw(out)
            dr.text((8, 8), "ANTES", fill=(20, 20, 20), font=F)
            dr.text((A.width + 28, 8), "DEPOIS", fill=(20, 20, 20), font=F)
            out.paste(A, (0, 44))
            out.paste(D, (A.width + 20, 44))
        out.save(R / f"POE642_CasaE_PH_Terreo_1611_{nome}_antes_depois.jpg", quality=90)
    print(f"    antes e depois: {', '.join(q)}")


# ----------------------------------------------------------------------------------------------------------------------
# 17. O mobiliário pela biblioteca da Casa E (16/11, a proposta aprovada: "1. SIM 2. SIM 3. COMO HOJE 4. ENTRAM AS 2"):
# `mobiliario_terreo_casae_1611`.
def mobiliario(Q, img):
    import mobiliario_terreo_casae_1611 as ME
    return ME.aplicar(Q, img)


# 18. O Dekton Danae da foto oficial (16/11, "APLIQUE EM TODAS AS CASAS"): `danae_foto.trocar` sobre o Danae desenhado.
def danae(Q, img):
    import danae_foto as DF
    out, reg = DF.trocar(img, planta="E_Terreo")
    print(f"    danae: a foto oficial em {cv2.connectedComponents(reg.astype(np.uint8))[0] - 1} bancadas")
    return out


# 19. As portas (quina a quina), as soleiras e as esquadrias (16/11, a revisão: "Prossiga"): `portas_terreo_casae_1611`.
def portas(Q, img):
    import portas_terreo_casae_1611 as PT
    return PT.aplicar(Q, img)


# ----------------------------------------------------------------------------------------------------------------------
PASSOS = [("base", base), ("margem", margem), ("tracejados", tracejados), ("gramado", gramado), ("bege", bege),
          ("marrom", marrom),
          ("travertino", travertino),
          ("bancadas", bancadas), ("armarios", armarios), ("wc_dce", wc_dce),
          ("gourmet", gourmet), ("piscina", piscina),
          ("escadas", escadas), ("soltas", soltas), ("cortinas", cortinas),
          ("tracejados_finos", tracejados_finos), ("mobiliario", mobiliario), ("danae", danae), ("portas", portas), ("rotulos", rotulos)]


def rodar(img, de=None, ate=None, cache=None):
    Q = FE.QuadroE("Terreo")
    out = img.copy()
    ativo = de is None
    for nome, f in PASSOS:
        if nome == de:
            ativo = True
            if cache:
                anterior = PASSOS[[p[0] for p in PASSOS].index(nome) - 1][0]
                out = cv2.imread(str(Path(cache) / f"passo_{anterior}.png"))
        if not ativo:
            continue
        print(f"  {nome}")
        out = f(Q, out)
        if cache:
            cv2.imwrite(str(Path(cache) / f"passo_{nome}.png"), out)
        if nome == ate:
            break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--de")
    ap.add_argument("--ate")
    ap.add_argument("--cache")
    ap.add_argument("--saida")
    ap.add_argument("--antes_depois", help="só grava o antes e depois desta final (png) contra a de ANTES_COMMIT")
    ap.add_argument("--sem_textos", action="store_true",
                    help="sem as descrições das escadas e os rótulos (a entrada da opção B do 12K; use com --saida)")
    a = ap.parse_args()
    global SEM_TEXTOS
    SEM_TEXTOS = a.sem_textos
    if a.antes_depois:
        antes_depois(antes_img(), cv2.imread(a.antes_depois))
        return
    if a.cache:
        Path(a.cache).mkdir(parents=True, exist_ok=True)
    out = rodar(antes_img(), a.de, a.ate, a.cache)
    cv2.imwrite(a.saida or str(FINAL), out)


if __name__ == "__main__":
    main()

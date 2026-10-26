#!/usr/bin/env python3
"""A final da Casa B refeita na resolução da prancha (3840 px, ~59,7 px/m).

Pedidos do usuário (22/10/26), vendo a prancha do Térreo: "TEM MUITOS BORRÕES NA IMAGEM. MOBÍLIAS DESGASTADAS E MAL
DESENHADAS. PRECISO QUE REVISE ITEM A ITEM E DEIXE A IMAGEM COM OS CONTORNOS PERFEITOS", e depois, item a item: os dois
pilares redondos em cinza; os rótulos sem sobrepor os objetos; cubas, pias e tanques melhores e a pedra sem borrão; o
chuveiro e o contorno do deck; os borrões do piso e dos degraus; por fim, as bancadas no tom areia, as cubas em branco
e as pedras humanizadas.

Tudo o que os ajustes (`ajustes_casab.py`) desenhavam em 2000 px e a final ampliava para 3840 px saía mole: a grama,
as árvores, as texturas dos pisos, os móveis do motor, as louças, as peças da biblioteca. Aqui, cada item é redesenhado
direto no quadro da prancha, pelo PDF (que é vetor) e pela base chapada da legenda (6905 px):
- os pisos, na máscara exata da legenda, com a textura da biblioteca na escala e a luz do lugar suavizada;
- a vegetação, as mesmas plantas da biblioteca nos mesmos lugares, desenhadas na escala da prancha;
- os móveis, os tapetes e as louças, pelo próprio desenho do PDF, na ordem de pintura dele: cada peça no contorno exato,
  com a cor do material, volume suave, o traço fino e a sombra curta (luz do alto à direita);
- as bancadas em pedra tom areia (a foto do Bege Bahia da biblioteca) com as cubas brancas; as peças da biblioteca
  (camas, guarda-roupas, carros, cooktops, banquetas, inox, adega, elevador); as paredes, os pilares, as esquadrias, as
  cortinas (depois das esquadrias), as escadas e as projeções;
- por fim, os rótulos, cada um no lugar livre mais perto do seu, sem tocar objeto nenhum.
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import ajustes_casab as B                       # noqa: E402

AJ = B.AJ
A = B.A


# ----------------------------------------------------------------------------------------------------------------------
# O quadro da prancha
class Quadro:
    """O pavimento no quadro de 3840 px: o PDF (pg, p2q), a escala, a base chapada (nearest) e o afim render -> quadro."""

    def __init__(self, chave):
        import pymupdf
        from opcoes_1pav_casae import quadro_pdf
        B.contexto()
        self.chave = chave
        q = self.q = B.PAVIMENTOS_B[chave]
        cfg = self.cfg = json.loads(B.CONFIG_B.read_text())
        self.base = (B.CASA_B / cfg["entrega"]["pasta_bases"] / cfg["entrega"]["pavimentos"][chave]["base"]).resolve()
        self.pg = pymupdf.open(B.RAIZ / "_pdfs_cliente" / q["pdf"])[cfg["pavimentos"][chave]["pagina"]]
        at, lt = cv2.imread(str(self.base), cv2.IMREAD_GRAYSCALE).shape
        hb, wb = cv2.imread(str(B.CASA_B / q["sem_tela"]), cv2.IMREAD_GRAYSCALE).shape
        self.W = A.LARGURA
        self.H = round(at * self.W / lt)
        self.p2q = quadro_pdf(self.pg, cfg, lt, at, wb, hb, self.W)
        self.p2q2000 = quadro_pdf(self.pg, cfg, lt, at, wb, hb, 2000)
        (a, b), (c, d) = self.p2q(0, 0), self.p2q(56.69, 0)
        self.px_m = float(np.hypot(c - a, d - b))
        ch = cv2.imread(str(B.CASA_B / q["chapada"]))
        self.chapada = cv2.resize(ch, (self.W, self.H), interpolation=cv2.INTER_NEAREST)
        self._desenhos = None

    def q2p(self, x, y):
        """quadro (px) -> pt do PDF (o p2q é afim)."""
        (a, b), (c, d), (e, f) = self.p2q(0, 0), self.p2q(100, 0), self.p2q(0, 100)
        M = np.array([[(c - a) / 100, (e - a) / 100], [(d - b) / 100, (f - b) / 100]])
        return tuple(np.linalg.solve(M, np.array([x - a, y - b])))

    @property
    def desenhos(self):
        if self._desenhos is None:
            self._desenhos = self.pg.get_drawings()
        return self._desenhos

    def cor(self, cores, tol=6, area_min_m2=0.0):
        m = np.zeros((self.H, self.W), bool)
        ch = self.chapada.astype(np.int32)
        for c in cores:
            m |= np.abs(ch - np.array(c)).max(axis=2) <= tol
        if area_min_m2 > 0:
            n, lab, st, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8), 8)
            m = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= area_min_m2 * self.px_m ** 2])
        return m

    def caminhos(self, d):
        return [np.float64(c) for c in AJ.caminhos_pdf(d, self.p2q)]

    def preencher(self, filtro, ss=4, fs=True):
        """A máscara (0 a 1, com antialias) dos preenchimentos do PDF que passam no filtro."""
        m = np.zeros((self.H * ss, self.W * ss), np.uint8)
        for d in self.desenhos:
            if d["type"] in (("f", "fs") if fs else ("f",)) and filtro(d):
                for c in self.caminhos(d):
                    if len(c) >= 3:
                        cv2.fillPoly(m, [np.int32(np.round(c * ss))], 255)
        return cv2.resize(m, (self.W, self.H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255


def afim_render(Q, ajustes_png, aprovada_png):
    """O afim (2 x 3) que leva a imagem de ajustes (2000 px) ao quadro, o mesmo do `no_quadro_fixo` (guardado em cache)."""
    cache = B.CACHE / f"{Q.chave}_afim_render.json"
    if cache.exists():
        return np.array(json.loads(cache.read_text()))
    base = cv2.imread(str(Q.base))
    W, H = Q.W, Q.H
    base_red = cv2.resize(base, (W, H), interpolation=cv2.INTER_AREA)
    ap = cv2.imread(str(aprovada_png))
    esc = W / ap.shape[1]
    apw = cv2.resize(ap, (W, round(ap.shape[0] * esc)), interpolation=cv2.INTER_LANCZOS4)
    sift = cv2.SIFT_create(12000)
    k1, d1 = sift.detectAndCompute(cv2.cvtColor(base_red, cv2.COLOR_BGR2GRAY), None)
    k2, d2 = sift.detectAndCompute(cv2.cvtColor(apw, cv2.COLOR_BGR2GRAY), None)
    bons = [a for a, b in cv2.BFMatcher().knnMatch(d1, d2, k=2) if a.distance < 0.75 * b.distance]
    src = np.float32([k1[m.queryIdx].pt for m in bons])
    dst = np.float32([k2[m.trainIdx].pt for m in bons])
    Am, _ = cv2.estimateAffine2D(src, dst, ransacReprojThreshold=2.5)
    Ai = cv2.invertAffineTransform(Am)
    M = Ai @ np.array([[esc, 0, 0], [0, esc, 0], [0, 0, 1]])        # render px -> quadro px
    B.CACHE.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(M.tolist()))
    return M


def quadro_inicial(Q):
    """A imagem de ajustes levada ao quadro (como na final antiga), em cache."""
    from PIL import Image
    q = Q.q
    aj = B.CASA_B / q["render"]
    cache = B.CACHE / f"{Q.chave}_quadro_inicial.png"
    if cache.exists() and cache.stat().st_mtime > aj.stat().st_mtime:
        return cv2.imread(str(cache))
    ajustes = cv2.imread(str(aj))
    if Q.chave == "Terreo":
        aprovada = Image.open(B.CASA_B / q["aprovada"]).convert("RGB")
        img = A.no_quadro_fixo(Image.fromarray(cv2.cvtColor(ajustes, cv2.COLOR_BGR2RGB)), aprovada, Q.base, Q.chave)
    else:
        orig = cv2.imread(str(B.CASA_B / q["original"]))
        nitida = cv2.resize(orig, (Q.W, Q.H), interpolation=cv2.INTER_AREA)
        ap = cv2.imread(str(B.CASA_B / q["aprovada"]))
        mudou = (np.abs(ajustes.astype(int) - ap.astype(int)).max(axis=2) > 0).astype(np.uint8)
        mudou = cv2.dilate(mudou, np.ones((3, 3), np.uint8))
        mq = cv2.resize(mudou.astype(np.float32), (Q.W, Q.H), interpolation=cv2.INTER_LINEAR)
        mq = np.clip(cv2.GaussianBlur(mq, (0, 0), 0.8) * 1.5, 0, 1)[..., None]
        amp = cv2.resize(ajustes, (Q.W, Q.H), interpolation=cv2.INTER_LANCZOS4)
        img = np.clip(nitida * (1 - mq) + amp * mq, 0, 255).astype(np.uint8)
    B.CACHE.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(cache), img)
    return img


# ----------------------------------------------------------------------------------------------------------------------
# 1. Os pisos, na máscara exata da legenda (base chapada), com a textura na escala da prancha
def luz_robusta(img, m, sig, desvio=35):
    """A luz larga do lugar (média normalizada, raio sig) só com os px do material: o que foge da mediana (móveis,
    sombras, plantas, traços) não entra."""
    from texturas_escala import nconv
    if not m.any():
        return img.astype(np.float32)
    med = np.median(img[m], axis=0)
    bom = m & (np.abs(img.astype(np.float32) - med).max(axis=2) < desvio)
    return nconv(img.astype(np.float32), bom.astype(np.float32), sig)


def fechar(m, k):
    return cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((k, k), np.uint8)).astype(bool)


def pousar(img, novo, m, suave=0.6):
    a = m.astype(np.float32)
    if suave:
        a = cv2.GaussianBlur(a, (0, 0), suave) * m        # sem sangrar para fora da máscara
    a = a[..., None]
    return img * (1 - a) + novo * a


PISOS = {
    "Terreo": [
        # (nome, cores BGR da base chapada, fechar px, textura, força, raio da luz em m)
        ("travertino", [(202, 217, 220), (202, 218, 221)], 5, "travertino", 1.6, 3.0),
        ("vinílico", [(124, 162, 200)], 5, "vinilico", None, 1.0),
        ("granito", [(50, 66, 90)], 5, "granito", None, 1.5),
        ("deck", [(99, 136, 174), (76, 106, 138)], 5, "deck", None, None),
        ("pedra portuguesa", [(85, 138, 185)], 3, "pedra", None, 1.5),
        ("grama", [(80, 145, 110)], 3, "grama", None, 3.0),
    ],
    "Subsolo": [
        ("travertino", [(202, 217, 220), (201, 217, 220)], 5, "travertino", 1.6, 3.0),
        ("Bege Bahia", [(232, 232, 232)], 5, "bege", None, 1.5),
        ("vinílico", [(124, 162, 200)], 5, "vinilico", None, 1.0),
        ("deck", [(99, 136, 174), (76, 106, 138)], 5, "deck", None, None),
    ],
}


def piso_textura(Q, img, m, nome, forca, sig_m, semente, bruto=None):
    """O material `nome` na máscara m, na escala da prancha. bruto: no travertino, o estilo do travertino bruto da Casa A
    (`final3840_casaa.TRAVERTINO`: "piso" ou "bancada"), com os veios horizontais e os poros, na luz do próprio piso."""
    sys.path.insert(0, str(B.RAIZ / "_texturas"))
    from texturas import textura
    import fontes_procedurais as F
    px_m = Q.px_m
    ys, xs = np.nonzero(m)
    y0, x0, y1, x1 = ys.min(), xs.min(), ys.max() + 1, xs.max() + 1
    h, w = y1 - y0, x1 - x0
    novo = img.astype(np.float32).copy()
    if nome == "deck":
        out, _ = B.deck_madeira(img, m, px_m, luz_local=False)
        return out.astype(np.float32)
    if nome == "pedra":
        from texturas_escala import trocar_pedra_portuguesa
        out, _ = trocar_pedra_portuguesa(img.astype(np.uint8), m, px_m, fonte="leque", sombra_limiar=1e-3)
        return out.astype(np.float32)
    L = luz_robusta(img, m, sig_m * px_m)
    if nome == "travertino" and bruto:
        import final3840_casaa as FA
        D = FA.travertino_bruto(Q, h, w, semente, forca=forca, **FA.TRAVERTINO[bruto])[..., None]
    elif nome == "travertino":
        T = textura("travertino", px_m, h, w, semente=semente).astype(np.float32)
        det = cv2.GaussianBlur(T, (0, 0), 0.6) / np.maximum(cv2.GaussianBlur(T, (0, 0), 3.0 * px_m), 1)
        D = 1 + forca * (det - 1)
    elif nome == "granito":
        T = F.granito_referencia(h, w, px_m, semente=semente).astype(np.float32)
        D = T / T.reshape(-1, 3).mean(axis=0)
    elif nome == "bege":
        T = textura("bege_bahia", px_m, h, w, semente=semente).astype(np.float32)
        D = T / T.reshape(-1, 3).mean(axis=0)
    elif nome == "grama":
        T = cv2.GaussianBlur(textura("grama", px_m, h, w, semente=semente).astype(np.float32), (0, 0), 0.5)
        D = T / T.reshape(-1, 3).mean(axis=0)
    elif nome == "vinilico":
        from retoque_1pav_casae import reguas_vinilico
        # o veio fino ao longo das réguas (o da foto da biblioteca vinha em retalhos e as réguas saíam em blocos)
        rr = np.random.default_rng(semente)
        veio = cv2.GaussianBlur(rr.normal(0, 1, (h, w)).astype(np.float32), (0, 0), sigmaX=0.30 * px_m, sigmaY=0.7)
        veio = 1 + 0.035 * veio / max(veio.std(), 1e-6)
        D = reguas_vinilico(h, w, px_m, veio, np.ones((h, w), bool), np.random.default_rng(semente))[..., None]
    else:
        raise ValueError(nome)
    novo[y0:y1, x0:x1] = L[y0:y1, x0:x1] * D
    return novo


def ret_q(Q, r):
    (a, b), (c, d) = Q.p2q(r[0], r[1]), Q.p2q(r[2], r[3])
    return int(np.floor(min(a, c))), int(np.floor(min(b, d))), int(np.ceil(max(a, c))), int(np.ceil(max(b, d)))


# Os arcos das portas (R3: sem arcos) estão na base chapada como linha tracejada (usuário, 22/10/26, na porta da suíte 3:
# "TEM UM ERRO NESSA PORTA"): as pintas escuras ao longo do arco que saiu. Duas causas: o preto do traço fica fora do
# piso (para não cobrir as paredes), e ali ficava o render; e os px de antialias do traço sobre o vinílico, marrom-escuros
# (45, 68, 91), caem na tolerância do granito (50, 66, 90) e viravam granito. Agora: os arcos do PDF (os traços de 0,57
# pt da ARQ_PAREDE só de curvas, num quadrado de 20 a 70 pt), com `largura_px` de folga, entram no piso em volta; e em
# cada material saem as manchas soltas (`SOLTOS_F`: menos de `area_px` e a mais de `folga_px` de uma mancha grande do
# mesmo material) que outro piso cobre no fechamento: são antialias de traço com a cor de outro piso, não piso.
ARCOS_F = {"camada": "ARQ_PAREDE", "larg_pdf": 0.57, "lado_pt": (20.0, 70.0), "largura_px": 4}
SOLTOS_F = {"area_px": 40, "folga_px": 2}


def soltos(m):
    """As manchas soltas de `m` (bool)."""
    q = SOLTOS_F
    n, lab, st, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8), 8)
    grande = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= q["area_px"]])
    k = 2 * q["folga_px"] + 1
    perto = cv2.dilate(grande.astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool)
    return m & ~grande & ~perto


def arcos_porta(Q):
    q = ARCOS_F
    m = np.zeros((Q.H, Q.W), np.uint8)
    n = 0
    for d in Q.desenhos:
        r = d["rect"]
        if d.get("layer") == q["camada"] and d["type"] == "s" and abs((d.get("width") or 0) - q["larg_pdf"]) < 0.02 \
                and d["items"] and all(it[0] == "c" for it in d["items"]) \
                and q["lado_pt"][0] < max(r.width, r.height) < q["lado_pt"][1] and abs(r.width - r.height) < 3:
            for c in Q.caminhos(d):
                cv2.polylines(m, [np.int32(np.round(c))], False, 1, q["largura_px"])
            n += 1
    return m.astype(bool), n


def pisos(Q, img, incluir=None, dentro=None, bruto=None):
    """incluir: {nome do piso: [retângulos em pt]} onde o branco da base (uma peça que sai, como os carros) também é
    aquele piso. dentro: só nesta máscara (a pegada do Subsolo). bruto: {nome do piso: estilo do travertino bruto}."""
    out = img.astype(np.float32)
    incluir = incluir or {}
    branco = Q.cor([(255, 255, 255)], tol=3)
    arcos, n_arcos = arcos_porta(Q)
    preto = Q.cor([(17, 17, 17), (0, 0, 0)], tol=20) & ~arcos         # as paredes; o traço dos arcos é do piso
    print(f"    arcos das portas: {n_arcos} do PDF, no piso em volta (sem restos do arco do render)")
    mascaras, soltas = [], []
    for nome, cores, k, *_ in PISOS[Q.chave]:
        m = Q.cor(cores, tol=6)
        soltas.append(soltos(m))
        for r in incluir.get(nome, []):
            x0, y0, x1, y1 = ret_q(Q, r)
            m[y0:y1, x0:x1] |= branco[y0:y1, x0:x1]
        if k:
            m = fechar(m, k) & ~preto                  # as linhas finas da base, não as paredes
        if dentro is not None:
            m &= dentro
        mascaras.append(m)
    n_soltos = 0
    for i, (nome, cores, k, tex, forca, sig) in enumerate(PISOS[Q.chave]):
        m = mascaras[i]
        if not m.any():
            continue
        # a mancha solta só sai onde outro piso a cobre no fechamento (o antialias do arco sobre o vinílico); junto a
        # uma peça (o carro sobre a pedra portuguesa) ela fica, porque ali não há outro piso
        outros = np.zeros_like(m)
        for j, mj in enumerate(mascaras):
            if j != i:
                outros |= mj
        solto = soltas[i] & outros
        n_soltos += int(solto.sum())
        # a textura na máscara inteira (o mesmo desenho de sempre); só não é pousada nas manchas soltas
        novo = piso_textura(Q, out, m, tex, forca, sig, 700 + i,
                            **({"bruto": bruto[nome]} if bruto and nome in bruto else {}))
        out = pousar(out, novo, m & ~solto, suave=0.5)
        print(f"    piso {nome}" + (" bruto (veios e poros)" if bruto and nome in bruto else "")
              + f": {int(m.sum())} px, a {Q.px_m:.1f} px/m")
    print(f"    {n_soltos} px de manchas soltas da legenda (antialias de traço com a cor de outro piso) ficam com o piso "
          f"em volta")
    return np.clip(out, 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
# 2. Os móveis, os tapetes e as louças pelo próprio desenho do PDF
CAMADAS_PECAS = ("ARQ_MOBILIÁRIO", "ARQ_LAYOUT HUMANIZAÇÃO", "ARQ_LOUÇAS E METAIS", "ARQ - Marcenaria")
PECAS = {
    "ss": 2,
    "tapete_m2": 4.0,                  # preenchimento grande e simples (até 5 vértices), que não é cama: tapete
    "sombra": {"dist_m": 0.035, "sig_m": 0.03, "forca": 0.30},     # a luz do alto à direita: sombra para baixo e à esq.
    "volume": {"larg_m": 0.06, "objeto": 0.07, "louca": 0.10},     # o escurecido junto à borda de cada peça
    "traco": {"cor": (92, 92, 94), "forca": 0.80, "tapete": 0.35, "trama": 0.18, "larg_px": 0.75, "grosso_px": 1.0,
              "louca": 0.50, "aro": 0.28},     # nas louças, o traço mais leve; o aro de dentro da cuba, quase só o tom
    "trama": {"raio_m": 0.10, "densidade": 0.22},                  # traços muito juntos: hachura (tapete, palha)
    "madeira": {"croma": 14, "veio": 0.035},
    "tapete_linho": (205, 212, 220),   # BGR: o tapete que o render não desenhou (a cor dele saía a do piso)
    "tecido": 0.012,
    # as louças (usuário, 22/10/26: "MELHORE AS REPRESENTAÇÕES DE CUBAS, PIAS, TANQUES" e "CUBAS EM BRANCO"): todas em
    # cerâmica branca, também as cubas da cozinha, do gourmet e do bar; os detalhes miúdos (ralos, válvulas,
    # torneiras) em metal; a cuba funda com a sombra interna do lado da luz (em cima e à direita)
    "louca": {"ceramica": (241, 242, 243), "inox": (196, 199, 202), "metal": (150, 152, 156), "metal_m2": 0.004,
              "sombra_int": {"dist_m": 0.06, "sig_m": 0.03, "forca": 0.30}},
    # os móveis humanizados (usuário, 22/10/26, no estar da varanda gourmet: "VAMOS HUMANIZAR ESSES MOBILIÁRIOS. SEM QUE
    # ELES PERCAM AS CARACTERÍSTICAS"): nas zonas (pt), a mesma forma, a mesma cor e o mesmo lugar de cada peça do PDF,
    # mas os estofados com volume de almofada (a borda cai mais e mais largo), a trama fina do bouclé e o traço do PDF
    # mais leve (o desenho técnico das almofadas e das poltronas ficava pesado); a madeira com o veio mais marcado
    "humanizar": {"zonas_pt": {"Terreo": [(971.0, 948.0, 1304.0, 1290.0)]}, "volume": 0.24, "larg_m": 0.12,
                  "boucle": 0.040, "traco": 0.30, "veio": 0.06,
                  # a sombra um pouco maior das peças, e o vinco: sob cada traço do PDF nos estofados, a sombra suave
                  # da dobra do tecido (o desenho das almofadas e das poltronas fica, mas em relevo)
                  "sombra": {"dist_m": 0.06, "sig_m": 0.045, "forca": 0.12}, "vinco": 0.18, "vinco_sig_px": 1.0},
    # as marcações técnicas sobre os tampos (usuário, 22/10/26, na mesa de jantar do living: "REMOVA ESSAS MARCAÇÕES
    # TÉCNICAS SOBRE O TAMPO DA MESA"): no PDF, os cantos tracejados em laranja da ARQ_MOBILIÁRIO (na mesa de jantar,
    # no aparador abaixo dela e nas mesas redondas da varanda, que já vêm da biblioteca) não entram; nem as duas
    # elipses da ARQ_LAYOUT HUMANIZAÇÃO no meio da mesa de jantar (`fora_pt`)
    "marcas": {"cores": [(0.97, 0.27, 0.03)], "fora_pt": {"Terreo": [(1625.0, 1298.0, 1662.0, 1325.0)]}},
}


def _poligonos(Q, d, ss):
    return [np.int32(np.round(c * ss)) for c in Q.caminhos(d) if len(c) >= 2]


def _fechado(c):
    return len(c) >= 4 and np.hypot(*(c[0] - c[-1])) < 1.0


def pecas_pdf(Q, img, amostra, fora=(), camas=(), inox=(), ss=None):
    """Os móveis, os tapetes e as louças do PDF, na ordem de pintura do PDF. `amostra` é a imagem de onde sai a cor de
    cada peça (o render levado ao quadro); `fora` são retângulos (pt) cujos desenhos não entram (as peças da biblioteca
    que vão por cima, os carros, as plantas); `camas`, os retângulos das camas (não são tapetes)."""
    q = PECAS
    ss = ss or q["ss"]
    H, W = Q.H, Q.W
    px = Q.px_m * ss

    def dentro(r, caixas):
        return any(c[0] - 1 <= r.x0 and r.x1 <= c[2] + 1 and c[1] - 1 <= r.y0 and r.y1 <= c[3] + 1 for c in caixas)
    def onda_cortina(d):
        r = d["rect"]
        return d["type"] == "s" and abs((d.get("width") or 0) - 0.85) < 0.05 and any(it[0] == "c" for it in d["items"]) \
            and 4.0 < max(r.width, r.height) < 8.0 and min(r.width, r.height) < 3.5
    def marca(d):
        cor = d.get("color")
        return (cor is not None and any(max(abs(a - b) for a, b in zip(cor, c)) < 0.02 for c in q["marcas"]["cores"])) \
            or dentro(d["rect"], q["marcas"]["fora_pt"].get(Q.chave, []))
    ds = [d for d in Q.desenhos if d.get("layer") in CAMADAS_PECAS and not dentro(d["rect"], fora)
          and not onda_cortina(d) and not marca(d)]
    ds.sort(key=lambda d: d.get("seqno", 0))
    # 1. o mapa de quem está por cima (o índice do último preenchimento em cada px) e o dos traços
    topo = np.full((H * ss, W * ss), -1, np.int32)
    traco = np.full((H * ss, W * ss), -1, np.int32)
    grosso = np.zeros((H * ss, W * ss), np.uint8)
    tipo = {}
    for i, d in enumerate(ds):
        polys = _poligonos(Q, d, ss)
        if not polys:
            continue
        preenche = d["type"] in ("f", "fs") or (d["type"] == "s" and all(_fechado(p) for p in polys)
                                                 and sum(abs(cv2.contourArea(p)) for p in polys) >= (0.12 * px) ** 2)
        if preenche:
            cv2.fillPoly(topo, [p for p in polys if len(p) >= 3], i)
            area = sum(abs(cv2.contourArea(np.float32(p))) for p in polys) / px ** 2
            r = d["rect"]
            cama = any(abs(r.x0 - c[0]) < 3 and abs(r.y0 - c[1]) < 3 for c in camas) or dentro(r, camas)
            if area >= q["tapete_m2"] and len(d["items"]) <= 5 and not cama:
                tipo[i] = "tapete"
            elif d.get("layer") == "ARQ_LOUÇAS E METAIS" and area < 1.5:
                tipo[i] = "metal" if area < q["louca"]["metal_m2"] else ("inox" if dentro(r, inox) else "louca")
            else:
                tipo[i] = "objeto"
        if d["type"] in ("s", "fs"):
            w = d.get("width") or 0.2
            for p in polys:
                cv2.polylines(traco, [p], False, i, 1)
                if w >= 0.4:
                    cv2.polylines(grosso, [p], False, 1, 1)
    # 2. a cor de cada peça: a mediana (Lab) do render no miolo do que dela aparece
    topo1 = topo[::ss, ::ss]
    lab = cv2.cvtColor(amostra, cv2.COLOR_BGR2LAB).astype(np.float32)
    cores = {}
    idx = np.unique(topo1[topo1 >= 0])
    for i in idx:
        m = (topo1 == i).astype(np.uint8)
        miolo = cv2.erode(m, np.ones((5, 5), np.uint8)).astype(bool)
        if miolo.sum() < 12:
            miolo = m.astype(bool)
        cores[i] = np.median(lab[miolo], axis=0)
    # 3. a imagem das peças em ss: cor, volume (escurecido junto à borda), veio da madeira, trama do tecido
    rng = np.random.default_rng(642)
    cor_lab = np.zeros((len(ds), 3), np.float32)
    k_vol = np.zeros(len(ds), np.float32)
    madeira = np.zeros(len(ds), bool)
    vertical = np.zeros(len(ds), bool)
    linho = cv2.cvtColor(np.uint8([[q["tapete_linho"]]]), cv2.COLOR_BGR2LAB)[0, 0].astype(np.float32)
    for i in idx:
        c = cores[i]
        t = tipo.get(i, "objeto")
        if t == "tapete" and (np.hypot(c[1] - 128, c[2] - 128) > 14 or c[0] < 175):
            c = cores[i] = linho
        elif t in ("louca", "inox", "metal"):
            bgr = q["louca"]["ceramica" if t == "louca" else t]
            c = cores[i] = cv2.cvtColor(np.uint8([[bgr]]), cv2.COLOR_BGR2LAB)[0, 0].astype(np.float32)
        cor_lab[i] = c
        k_vol[i] = q["volume"]["louca"] if t in ("louca", "inox", "metal") else \
            (0.0 if t == "tapete" else q["volume"]["objeto"])
        croma = np.hypot(c[1] - 128, c[2] - 128)
        madeira[i] = t == "objeto" and croma >= q["madeira"]["croma"] and c[2] > c[1] + 4 and c[0] < 215
        r = ds[i]["rect"]
        vertical[i] = r.height > r.width
    # as peças das zonas humanizadas (os estofados e a madeira)
    hz = q["humanizar"]
    zonas = hz["zonas_pt"].get(Q.chave, [])
    na_zona = np.array([dentro(ds[i]["rect"], zonas) for i in range(len(ds))], bool)
    estofado = na_zona & np.array([tipo.get(i) == "objeto" for i in range(len(ds))]) & ~madeira
    larg_i = np.full(len(ds), q["volume"]["larg_m"] * px, np.float32)
    k_vol = np.where(estofado, hz["volume"], k_vol).astype(np.float32)
    larg_i[estofado] = hz["larg_m"] * px
    T = np.maximum(topo, 0)
    C = cor_lab[T]                                                   # (H ss, W ss, 3) em Lab
    borda = np.zeros_like(topo, np.uint8)
    borda[:, 1:] |= (topo[:, 1:] != topo[:, :-1]).astype(np.uint8)
    borda[1:, :] |= (topo[1:, :] != topo[:-1, :]).astype(np.uint8)
    dist = cv2.distanceTransform((1 - borda).astype(np.uint8), cv2.DIST_L2, 3)
    fator = 1 - k_vol[T] * (1 - np.minimum(1, dist / larg_i[T])) ** 2
    ruido_h = cv2.GaussianBlur(rng.normal(0, 1, topo.shape).astype(np.float32), (0, 0), sigmaX=0.25 * px, sigmaY=0.6)
    ruido_v = cv2.GaussianBlur(rng.normal(0, 1, topo.shape).astype(np.float32), (0, 0), sigmaX=0.6, sigmaY=0.25 * px)
    ruido_h /= max(ruido_h.std(), 1e-6)
    ruido_v /= max(ruido_v.std(), 1e-6)
    veio = np.where(vertical[T], ruido_v, ruido_h)
    fator *= np.where(madeira[T], 1 + np.where(na_zona[T], hz["veio"], q["madeira"]["veio"]) * veio, 1.0)
    if estofado.any():                                               # a trama fina do bouclé nos estofados das zonas
        bou = cv2.GaussianBlur(rng.normal(0, 1, topo.shape).astype(np.float32), (0, 0), 0.6)
        fator *= np.where(estofado[T] & (topo >= 0), 1 + hz["boucle"] * bou / max(bou.std(), 1e-6), 1.0)
        del bou
    trama = cv2.GaussianBlur(rng.normal(0, 1, topo.shape).astype(np.float32), (0, 0), 0.7)
    louca_t = np.array([tipo.get(i) in ("louca", "inox", "metal") for i in range(len(ds))])
    fator *= np.where(louca_t[T], 1.0, 1 + q["tecido"] * trama / max(trama.std(), 1e-6))   # a louça é lisa
    # a sombra interna das louças: o que fica logo abaixo e à esquerda de outra peça (a borda da cuba, do lado da luz)
    si = q["louca"]["sombra_int"]
    louca_i = louca_t
    d_ = max(1, int(round(si["dist_m"] * px)))
    viz = np.full_like(topo, -1)
    viz[d_:, :-d_] = topo[:-d_, d_:]                    # o px acima e à direita
    beira = ((viz != topo) & (viz >= 0) & louca_i[T] & louca_i[np.maximum(viz, 0)] & (topo >= 0)).astype(np.float32)
    fator *= 1 - si["forca"] * cv2.GaussianBlur(beira, (0, 0), si["sig_m"] * px) * louca_i[T]
    # a bacia (a louça dentro de outra, com 40 a 95% da área dela: a cuba, o tanque, a cuba redonda do bar), pela
    # geometria, porque no PDF o aro costuma ser pintado depois e cobre a bacia: a sombra interna em toda a borda do
    # lado da luz, mesmo onde o aro é fino, e o fundo um tom abaixo
    ls_ = [(i, ds[i]["rect"]) for i, d in enumerate(ds) if d.get("layer") == "ARQ_LOUÇAS E METAIS"
           and d["type"] in ("f", "fs") and tipo.get(i) == "louca"]
    bac = np.zeros(topo.shape, np.uint8)
    nb = 0
    for i, r in ls_:
        if any(j != i and c.x0 - 0.5 <= r.x0 and r.x1 <= c.x1 + 0.5 and c.y0 - 0.5 <= r.y0 and r.y1 <= c.y1 + 0.5
               and 0.4 <= (r.width * r.height) / max(c.width * c.height, 1e-6) <= 0.95 for j, c in ls_):
            cv2.fillPoly(bac, [p for p in _poligonos(Q, ds[i], ss) if len(p) >= 3], 1)
            nb += 1
    bac &= (topo >= 0) & louca_i[T]
    acima = np.zeros_like(bac)
    acima[d_:, :-d_] = bac[:-d_, d_:]                   # a bacia no px acima e à direita
    bb = ((bac == 1) & (acima == 0)).astype(np.float32)
    fator *= 1 - si["forca"] * cv2.GaussianBlur(bb, (0, 0), si["sig_m"] * px) * bac
    fator *= np.where(bac == 1, 0.97, 1.0)
    C[..., 0] = np.clip(C[..., 0] * fator, 0, 255)
    del ruido_h, ruido_v, veio, trama, dist
    rgb = cv2.cvtColor(np.clip(C, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR).astype(np.float32)
    del C
    def reduzir(a):
        return cv2.resize(a, (W, H), interpolation=cv2.INTER_AREA)
    # as plantas do PDF (vasos): onde o render é verde, a peça não é pintada lisa; vira uma planta da biblioteca
    plantas = []
    for i in idx:
        c = cores[i]
        if tipo.get(i) == "objeto" and c[1] < 122 and c[2] > 128 and ds[i].get("layer") == "ARQ_LAYOUT HUMANIZAÇÃO":
            tipo[i] = "planta"
            r = ds[i]["rect"]
            plantas.append(((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2, max(r.width, r.height) / 56.69))
    planta_i = np.array([tipo.get(i) == "planta" for i in range(len(ds))])
    tapete_i = np.array([tipo.get(i) == "tapete" for i in range(len(ds))])
    eh_tapete = (topo >= 0) & tapete_i[T]
    eh_obj = (topo >= 0) & ~tapete_i[T] & ~planta_i[T]
    a_tap = reduzir(eh_tapete.astype(np.float32))[..., None]
    a_obj = reduzir(eh_obj.astype(np.float32))[..., None]
    a_tot = np.maximum(a_tap + a_obj, 1e-6)
    cor = reduzir(rgb * (topo >= 0)[..., None]) / a_tot
    del rgb
    # 4. a composição: o piso, os tapetes, a sombra curta dos objetos, os objetos
    out = img.astype(np.float32)
    out = out * (1 - a_tap) + cor * a_tap
    s = q["sombra"]
    d_ = s["dist_m"] * Q.px_m
    Mx = np.float32([[1, 0, -d_], [0, 1, d_]])
    sombra = cv2.GaussianBlur(cv2.warpAffine(a_obj[..., 0], Mx, (W, H)), (0, 0), s["sig_m"] * Q.px_m) * s["forca"]
    out *= (1 - sombra * (1 - a_obj[..., 0]))[..., None]
    out = out * (1 - a_obj) + cor * a_obj
    if estofado.any():                                               # as zonas humanizadas: sombra maior e os vincos
        zs = hz["sombra"]
        zz = reduzir((na_zona[T] & (topo >= 0) & ~tapete_i[T]).astype(np.float32))
        dz = zs["dist_m"] * Q.px_m
        sz = cv2.GaussianBlur(cv2.warpAffine(zz, np.float32([[1, 0, -dz], [0, 1, dz]]), (W, H)), (0, 0),
                              zs["sig_m"] * Q.px_m) * zs["forca"]
        out *= (1 - sz * (1 - a_obj[..., 0]))[..., None]
        vz = (traco >= topo) & (traco >= 0) & estofado[np.maximum(topo, 0)] & (topo >= 0)   # só os traços à vista
        vinco = cv2.GaussianBlur(reduzir(vz.astype(np.float32)), (0, 0), hz["vinco_sig_px"])
        out *= (1 - hz["vinco"] * np.clip(vinco * 3, 0, 1))[..., None]
        del vz
    # 5. os traços que aparecem (os desenhados depois do preenchimento por cima), com antialias
    vis = (traco >= 0) & (traco >= topo) & ~planta_i[np.maximum(traco, 0)] & ~(planta_i[T] & (topo >= 0))
    trama_m = reduzir(vis.astype(np.float32))
    k = int(round(q["trama"]["raio_m"] * Q.px_m)) * 2 + 1
    dens = cv2.blur(trama_m, (k, k))
    t = q["traco"]
    sob_tapete = reduzir(((traco >= 0) & tapete_i[np.maximum(traco, 0)]).astype(np.float32)) > 0.3
    # o traço das louças: mais leve; o aro de dentro da cuba (o traço logo dentro de outra louça), quase só o tom
    rl = [ds[i]["rect"] for i in idx if tipo.get(i) in ("louca", "inox", "metal")]
    f_i = np.full(len(ds), t["forca"], np.float32)
    for i, d in enumerate(ds):
        if d.get("layer") != "ARQ_LOUÇAS E METAIS" or d["type"] not in ("s", "fs"):
            continue
        r = d["rect"]
        if any(c.x0 - 1 <= r.x0 and r.x1 <= c.x1 + 1 and c.y0 - 1 <= r.y0 and r.y1 <= c.y1 + 1 for c in rl):
            f_i[i] = t["louca"]
            if any(0.5 <= min(r.x0 - c.x0, r.y0 - c.y0, c.x1 - r.x1, c.y1 - r.y1) and
                   max(r.x0 - c.x0, r.y0 - c.y0, c.x1 - r.x1, c.y1 - r.y1) <= 3.5 for c in rl):
                f_i[i] = t["aro"]
    f_i = np.where(na_zona & np.array([d.get("layer") != "ARQ_LOUÇAS E METAIS" for d in ds]), hz["traco"], f_i)
    kk = np.ones((max(1, round(t["larg_px"] * ss)),) * 2, np.uint8)
    vis_aa = cv2.dilate(vis.astype(np.uint8), kk)
    f_hi = cv2.dilate(np.where(vis, f_i[np.maximum(traco, 0)], 0).astype(np.float32), kk)
    den = reduzir(vis_aa.astype(np.float32))
    f_tr = reduzir(f_hi * vis_aa) / np.maximum(den, 1e-6)          # a força de cada traço, com o antialias
    forca = np.where(dens > q["trama"]["densidade"], t["trama"], np.where(sob_tapete, t["tapete"], f_tr))
    a_tr = np.clip(den * 1.4, 0, 1) * forca
    g_aa = reduzir((cv2.dilate(grosso, np.ones((2, 2), np.uint8)) & vis).astype(np.float32))
    a_tr = np.maximum(a_tr, np.clip(g_aa * 1.6, 0, 1) * f_tr)
    out = out * (1 - a_tr[..., None]) + np.float32(t["cor"]) * a_tr[..., None]
    n_tap = int(sum(1 for i in idx if tipo.get(i) == "tapete"))
    nt = {t: sum(1 for i in idx if tipo.get(i) == t) for t in ("louca", "inox", "metal")}
    print(f"    peças do PDF: {len(idx)} preenchimentos ({n_tap} tapetes, {nt['louca']} em louça, {nt['inox']} em inox, "
          f"{nt['metal']} metais, {int(madeira[idx].sum())} em madeira), "
          f"{int((traco >= 0).sum() / ss)} px de traço; sombra curta para baixo e à esquerda; "
          f"{len(plantas)} plantas em vaso da biblioteca")
    out = np.clip(out, 0, 255).astype(np.uint8)
    return plantas_em_vaso(Q, out, plantas)


VASOS = {"nome": "costela_de_adao", "d_min_m": 0.6}


def plantas_em_vaso(Q, img, plantas):
    """As plantas que o PDF desenha soltas no piso (vasos): a planta da biblioteca, no tamanho do desenho, com a sombra."""
    import json as _json
    from retoque_terreo_casae import pousar_planta
    if not plantas:
        return img
    sombra = _json.loads((B.RAIZ / "_texturas" / "texturas.json").read_text())["vegetacao"]["sombra"]
    out = img.astype(np.float32)
    for k, (px_, py_, d_m) in enumerate(plantas):
        d_m = max(d_m, VASOS["d_min_m"])
        cor, al, d_px = B.planta_sprite(VASOS["nome"], d_m, Q.px_m)
        for _ in range(k % 4):
            cor, al = cv2.rotate(cor, cv2.ROTATE_90_CLOCKWISE), cv2.rotate(al, cv2.ROTATE_90_CLOCKWISE)
        x, y = Q.p2q(px_, py_)
        pousar_planta(out, cor, al, x, y, d_px, sombra)
    return np.clip(out, 0, 255).astype(np.uint8)


# Os vasos sanitários com a tampa fechada (usuário, 22/10/26: "TODOS OS SANITÁRIOS PRECISAM TER A SUA RESPECTIVA
# TAMPA"): no PDF, os vasos suspensos são o "D" branco da ARQ_LOUÇAS E METAIS (0,51 x 0,35 m, com a abertura e o ralo
# à mostra; os de 0,55 x 0,38 m já trazem a tampa, em traço). O "D" se separa das cubas e das máquinas pela forma: o
# centro de massa fica puxado para o lado reto, o da parede. Em todos, a tampa entra igual: o contorno do vaso recuado
# `recuo_m`, da linha da dobradiça (`dobradica`, fração do comprimento a partir da parede, logo à frente dos
# parafusos) até a frente, em louça branca com volume suave, o traço fino das louças e a sombra curta sobre o aro.
TAMPAS_F = {"longo_m": (0.45, 0.62), "curto_m": (0.30, 0.42), "assimetria": 0.02, "dobradica": 0.17,
            "recuo_m": 0.012, "ss": 8, "volume": (0.94, 0.05), "traco": 0.55,
            "sombra": {"dx_m": -0.006, "dy_m": 0.008, "sig_m": 0.006, "forca": 0.25}}


def vasos_sanitarios(Q):
    """Os vasos do PDF: (desenho, lado da parede: "esq", "dir", "cima" ou "baixo")."""
    q = TAMPAS_F
    ls = [d for d in Q.desenhos if d.get("layer") == "ARQ_LOUÇAS E METAIS" and d["type"] in ("f", "fs")]
    vasos = []
    for d in ls:
        r = d["rect"]
        curto, longo = sorted((r.width / 56.69, r.height / 56.69))
        if not (q["longo_m"][0] <= longo <= q["longo_m"][1] and q["curto_m"][0] <= curto <= q["curto_m"][1]):
            continue
        if any(e is not d and r.contains(e["rect"]) and e["rect"].width * e["rect"].height > 0.15 * r.width * r.height
               for e in ls):                                                     # a cuba, com a bacia dentro
            continue
        pts = np.vstack([c for c in Q.caminhos(d) if len(c) >= 3]).astype(np.float32)
        m = cv2.moments(pts)
        (x0, y0), (x1, y1) = Q.p2q(r.x0, r.y0), Q.p2q(r.x1, r.y1)
        deitado = x1 - x0 > y1 - y0
        desvio = (m["m10"] / m["m00"] - (x0 + x1) / 2 if deitado else m["m01"] / m["m00"] - (y0 + y1) / 2) \
            / max(x1 - x0, y1 - y0)
        if abs(desvio) >= q["assimetria"]:
            vasos.append((d, ("esq" if desvio < 0 else "dir") if deitado else ("cima" if desvio < 0 else "baixo")))
    return vasos


def tampas_vasos(Q, img):
    q, k = TAMPAS_F, TAMPAS_F["ss"]
    t = PECAS["traco"]
    out = img.astype(np.float32)
    vasos = vasos_sanitarios(Q)
    for d, lado in vasos:
        r = d["rect"]
        (x0, y0), (x1, y1) = Q.p2q(r.x0, r.y0), Q.p2q(r.x1, r.y1)
        X0, Y0, X1, Y1 = int(x0) - 3, int(y0) - 3, int(np.ceil(x1)) + 4, int(np.ceil(y1)) + 4
        w, h = X1 - X0, Y1 - Y0
        corpo = np.zeros((h * k, w * k), np.uint8)
        cv2.fillPoly(corpo, [np.int32(np.round((c - (X0, Y0)) * k)) for c in Q.caminhos(d) if len(c) >= 3], 255)
        rc = max(1, int(round(q["recuo_m"] * Q.px_m * k)))
        tampa = cv2.erode(corpo, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * rc + 1,) * 2))
        f = q["dobradica"]                                    # a linha da dobradiça: a tampa só da frente dela
        if lado == "esq":
            tampa[:, :int(round((x0 + f * (x1 - x0) - X0) * k))] = 0
        elif lado == "dir":
            tampa[:, int(round((x1 - f * (x1 - x0) - X0) * k)):] = 0
        elif lado == "cima":
            tampa[:int(round((y0 + f * (y1 - y0) - Y0) * k))] = 0
        else:
            tampa[int(round((y1 - f * (y1 - y0) - Y0) * k)):] = 0

        def reduzir(a):
            return cv2.resize(a.astype(np.float32), (w, h), interpolation=cv2.INTER_AREA)
        a_c, a_t = reduzir(corpo / 255.0), reduzir(tampa / 255.0)
        reg = out[Y0:Y1, X0:X1]
        s = q["sombra"]                                       # a sombra curta da tampa sobre o aro do vaso
        M = np.float32([[1, 0, s["dx_m"] * Q.px_m * k], [0, 1, s["dy_m"] * Q.px_m * k]])
        sb = reduzir(cv2.GaussianBlur(cv2.warpAffine(tampa / 255.0, M, (w * k, h * k)), (0, 0),
                                      s["sig_m"] * Q.px_m * k))
        reg *= (1 - s["forca"] * sb * (1 - a_t) * a_c)[..., None]
        v0, vl = q["volume"]                                  # louça branca, um tom abaixo junto à borda
        dist = cv2.distanceTransform(tampa, cv2.DIST_L2, 5) / (Q.px_m * k)
        tom = (v0 + (1 - v0) * np.clip(dist / vl, 0, 1)) * (tampa / 255.0)
        cor = np.float32(PECAS["louca"]["ceramica"])
        reg[:] = reg * (1 - a_t[..., None]) + reduzir(tom)[..., None] * cor
        lt = max(1, int(round(t["larg_px"] * k)))             # o traço fino das louças no contorno da tampa
        anel = tampa & ~cv2.erode(tampa, np.ones((lt, lt), np.uint8))
        a_l = np.clip(reduzir(anel / 255.0) * 1.4, 0, 1) * q["traco"]
        reg[:] = reg * (1 - a_l[..., None]) + np.float32(t["cor"]) * a_l[..., None]
    print(f"    vasos: a tampa fechada nos {len(vasos)} vasos sanitários do PDF, da dobradiça à frente")
    return np.clip(out, 0, 255).astype(np.uint8)


# Os vasos na cor pedida (usuário, 26/10/26, no Subsolo: "banho sauna: sanitário marrom"): o vaso do PDF já desenhado
# em louça (`pecas_pdf`, `tampas_vasos`), tingido no contorno exato do PDF: cada px leva a cor da louça pedida na luz
# dele relativa à cerâmica branca (o volume, a tampa, o aro e o traço ficam, no tom da cor). A cor é a dos vasos marrons
# da Casa A (`final3840_casaa.BANHOS["vaso_marrom"]`). Cada vaso: o retângulo (pt) da louça e a cor.
VASOS_COR = {"Subsolo": [((1140.8, 914.0, 1169.9, 934.0), "marrom")],
             "cores": {"marrom": (66, 88, 120)}, "folga_px": 1, "teto": 1.08}


def vasos_cor(Q, img):
    q = VASOS_COR
    out = img.astype(np.float32)
    ref = float(np.mean(PECAS["louca"]["ceramica"]))
    for r, nome in q.get(Q.chave, []):
        a = Q.preencher(lambda d: d.get("layer") == "ARQ_LOUÇAS E METAIS" and r[0] - 0.5 <= d["rect"].x0
                        and d["rect"].x1 <= r[2] + 0.5 and r[1] - 0.5 <= d["rect"].y0 and d["rect"].y1 <= r[3] + 0.5)
        k = 2 * q["folga_px"] + 1
        m = np.maximum(a, cv2.dilate(a, np.ones((k, k), np.uint8)) * 0.85)[..., None]
        t = np.clip(out.mean(axis=2, keepdims=True) / ref, 0, q["teto"])
        out = out * (1 - m) + np.float32(q["cores"][nome]) * t * m
    print(f"    vasos: {len(q.get(Q.chave, []))} tingido(s) na cor pedida, no contorno do PDF")
    return np.clip(out, 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
# 3. As bancadas em pedra tom areia, humanizada, no contorno do PDF (usuário, 22/10/26: "TROQUE O CINZA DAS BANCADAS PELO
# TOM AREIA", "CUBAS EM BRANCO", "PRECISO QUE AS PEDRAS ESTEJAM HUMANIZADAS"): a foto do Bege Bahia da biblioteca (a
# placa real, com as nuvens de 10 a 20 cm), na escala da prancha e levada ao tom areia, em toda peça da ARQ_BANCADAS
# (as brancas, as bege do Subsolo, como a cuba esculpida e o banco da sauna, e os frisos escuros); a textura é reduzida
# da amostra de 320 px/m, nunca ampliada, e não leva desfoque (a pedra não borra). As cubas das bancadas são os
# retângulos da ARQ_BANCADAS com o aro fino (as tiras de até 3,5 cm) nos quatro lados: louça branca, com a bacia de
# cantos arredondados, a sombra interna do lado da luz, o aro e a sombra curta.
BANCADAS_F = {"lado_min_m": 0.08, "volume": 0.06, "larg_m": 0.03, "contorno": (104, 112, 120), "forca": 0.8,
              "pedra": "bege_bahia", "tom": (198, 217, 233),       # BGR: o areia (a média da placa levada a ele)
              "contraste": 0.8,                                     # as nuvens da placa, um pouco mais calmas
              "cuba": {"aro_max_m": 0.035, "lado_min_m": 0.20, "area_max_m2": 0.6, "cobre": 0.8, "folga_pt": 1.5,
                       "aro_pt": 1.2, "recuo": 0.12, "raio_m": 0.035},
              # E9 (26/10/26: "Se a bancada e o piso forem da mesma cor, deixar a bancada mais marcada do que o piso"):
              # a borda fina no tom escurecido da própria pedra e a sombra curta no piso (luz do alto à direita), como
              # nas bancadas da Casa A; ligada planta a planta, com o OK do usuário (`bancadas(..., borda=...)`)
              "borda_e9": {"mult": 0.62, "larg_px": 0.7, "sombra": {"dist_m": 0.02, "sig_m": 0.022, "forca": 0.34}},
              # a pedra e a cuba por banho, planta a planta, com o pedido do usuário (`bancadas(..., pedra=, cuba=)`):
              # "granito", o granito marrom das Casas B a D (`fontes_procedurais.granito_referencia`); a cuba esculpida
              # em travertino bruto, clara (`cuba_travertino`)
              "cuba_travertino": {"tom": (206, 220, 234), "semente": 2760, "raio_pt": 1.6, "aro_pt": 2.0,
                                  "raio_bacia_pt": 4.5, "valvula_pt": 1.1,
                                  "desenho": {"veio": 0.012, "faixa": 0.025, "poros": 8, "poro_esc": 0.07},
                                  "borda": 1.03, "quina": 0.07, "quina_px": 0.9,
                                  "bacia": {"fundo": 0.95, "sombra": 0.22, "luz": 0.05, "alc_px": 3.5, "calma": 0.6},
                                  "sombra": {"dist_px": 1.0, "sig_px": 1.0, "forca": 0.28},
                                  "contorno": (146, 160, 176), "contorno_bacia": (158, 172, 188), "larg": 0.35}}


def cubas_bancada(Q):
    """As cubas da ARQ_BANCADAS: os retângulos (4 vértices) com uma tira fina encostada em cada um dos quatro lados (o
    aro do PDF, por dentro ou por fora do lado), cobrindo ao menos `cobre` dele. Devolve os retângulos (pt)."""
    c = BANCADAS_F["cuba"]
    rets = {(round(d["rect"].x0, 1), round(d["rect"].y0, 1), round(d["rect"].x1, 1), round(d["rect"].y1, 1))
            for d in Q.desenhos if d.get("layer") == "ARQ_BANCADAS" and d["type"] in ("f", "fs") and d.get("fill")
            and len(d["items"]) == 4}
    fino, f = c["aro_max_m"] * 56.69, c["folga_pt"]
    tiras = [r for r in rets if min(r[2] - r[0], r[3] - r[1]) <= fino]

    def tem_tira(r, k):
        x0, y0, x1, y1 = r
        for t in tiras:
            if k in (0, 2):                            # os lados verticais (esquerdo, direito)
                x = x0 if k == 0 else x1
                cob = min(t[3], y1) - max(t[1], y0)
                if t[3] - t[1] > t[2] - t[0] and t[0] - f <= x <= t[2] + f and cob >= c["cobre"] * (y1 - y0):
                    return True
            else:                                      # os horizontais (em cima, embaixo)
                y = y0 if k == 1 else y1
                cob = min(t[2], x1) - max(t[0], x0)
                if t[2] - t[0] > t[3] - t[1] and t[1] - f <= y <= t[3] + f and cob >= c["cobre"] * (x1 - x0):
                    return True
        return False
    cubas = []
    for r in rets:
        w, h = (r[2] - r[0]) / 56.69, (r[3] - r[1]) / 56.69
        if min(w, h) < c["lado_min_m"] or w * h > c["area_max_m2"]:
            continue
        if all(tem_tira(r, k) for k in range(4)):
            cubas.append(r)
    return sorted(cubas)


def _ret_arredondado(forma, x0, y0, x1, y1, raio):
    """A máscara (uint8) do retângulo de cantos arredondados (coordenadas já na escala da máscara)."""
    m = np.zeros(forma, np.uint8)
    raio = int(max(0, min(raio, (x1 - x0) / 2 - 1, (y1 - y0) / 2 - 1)))
    cv2.rectangle(m, (int(x0 + raio), int(y0 + raio)), (int(x1 - raio), int(y1 - raio)), 255, -1)
    if raio > 0:
        m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * raio + 1, 2 * raio + 1)))
    return m


def cuba_travertino(Q, out, r):
    """A cuba esculpida em travertino bruto no retângulo r (pt, por fora do aro do PDF), clara e polida (usuário, 26/10/26:
    "melhore a representação da cuba esculpida com o marmore travertino, mais claro"): a peça um pouco mais clara que o
    piso, com o desenho calmo do travertino bruto (poucos poros); a borda larga (`aro_pt`) com a quina clara do lado da
    luz (em cima e à direita) e a escura do outro; a bacia de cantos bem arredondados, funda: a parede de cima e da
    direita na sombra, a de baixo e da esquerda na luz, o fundo um pouco mais escuro e mais liso; o contorno fino no tom
    da pedra, a válvula cromada no meio e a sombra curta da peça na bancada (para baixo e à esquerda)."""
    import final3840_casaa as FA
    from retoque_subsolo_casae import SS
    q = BANCADAS_F["cuba_travertino"]
    base = np.clip(out, 0, 255).astype(np.uint8)
    tl = FA.tela(base.copy(), Q, r, folga=6)
    m = tl.ret(r, q["raio_pt"])
    s = q["sombra"]
    tl.sombra(m, dx=-s["dist_px"], dy=s["dist_px"], sigma=s["sig_px"], forca=s["forca"])
    D = FA.travertino_bruto(Q, tl.h, tl.w, q["semente"], **q["desenho"])
    G = np.float32(q["tom"]) * D[..., None]
    X, Y = tl.grade()
    # a borda, com a quina: clara perto dos lados de cima e da direita, escura perto dos de baixo e da esquerda
    x0, y0, x1, y1 = r
    d_m = cv2.resize(cv2.distanceTransform(m, cv2.DIST_L2, 5) / SS, (tl.w, tl.h), interpolation=cv2.INTER_AREA)
    faixa = np.clip(1 - d_m / q["quina_px"], 0, 1)
    luz = np.where(np.minimum(Y - y0, x1 - X) < np.minimum(y1 - Y, X - x0), 1.0, -1.0)
    tl.pintar_img(m, G * (q["borda"] * (1 + q["quina"] * faixa * luz))[..., None])
    # a bacia
    e, bq = q["aro_pt"], q["bacia"]
    bx0, by0, bx1, by1 = x0 + e, y0 + e, x1 - e, y1 - e
    b = tl.ret((bx0, by0, bx1, by1), q["raio_bacia_pt"])
    d_b = cv2.resize(cv2.distanceTransform(b, cv2.DIST_L2, 5) / SS, (tl.w, tl.h), interpolation=cv2.INTER_AREA)
    parede = np.exp(-d_b / bq["alc_px"])
    lado = np.clip(((X - bx0) / (bx1 - bx0) + (by1 - Y) / (by1 - by0)) / 2, 0, 1)        # 1 no alto à direita
    prof = bq["fundo"] * (1 - bq["sombra"] * parede * lado) * (1 + bq["luz"] * parede * (1 - lado))
    Gb = np.float32(q["tom"]) * (1 + bq["calma"] * (D - 1))[..., None]
    tl.pintar_img(b, Gb * prof[..., None])
    tl.contorno(b, q["larg"], q["contorno_bacia"])
    tl.contorno(m, q["larg"], q["contorno"])
    # a válvula, no meio da bacia
    v = tl.vazia()
    cx, cy = tl.pt((bx0 + bx1) / 2, (by0 + by1) / 2)
    cv2.circle(v, (int(cx), int(cy)), int(q["valvula_pt"] * FA.PT_PX * SS), 255, -1, cv2.LINE_AA)
    tl.pintar(v, FA.CROMO["meio"])
    tl.contorno(v, 0.3, FA.CROMO["contorno"])
    novo = tl.gravar()
    muda = np.any(novo != base, axis=2)
    out[muda] = novo[muda]
    return out


def bancadas(Q, img, borda=None, pedra=None, cuba=None):
    sys.path.insert(0, str(B.RAIZ / "_texturas"))
    from texturas import textura
    q = BANCADAS_F
    a = Q.preencher(lambda d: d.get("layer") == "ARQ_BANCADAS" and d.get("fill") and not no_banco_sauna(Q, d["rect"]),
                    fs=False)
    cubas = cubas_bancada(Q)
    e_ = q["cuba"]["aro_pt"]
    if cuba is not None:            # a cuba esculpida é a peça inteira, com o aro: sem a pedra da bancada (e a borda dela)
        import final3840_casaa as FA
        for r in cubas:
            a *= 1 - FA.ret_aa(Q, (r[0] - e_, r[1] - e_, r[2] + e_, r[3] + e_))
    n, lab, st, _ = cv2.connectedComponentsWithStats((a > 0.5).astype(np.uint8), 8)
    out = img.astype(np.float32)
    pecas = 0
    for i in range(1, n):
        x, y, w, h, area = st[i]
        comp = lab == i
        (_, _), (r1, r2), _ = cv2.minAreaRect(np.argwhere(comp)[:, ::-1].astype(np.float32))
        if min(r1, r2) < q["lado_min_m"] * Q.px_m:
            continue
        f = 6 if borda else 2
        x0, y0, x1, y1 = max(0, x - f), max(0, y - f), min(Q.W, x + w + f), min(Q.H, y + h + f)
        reg = (slice(y0, y1), slice(x0, x1))
        al = a[reg] * cv2.dilate(comp.astype(np.uint8), np.ones((3, 3), np.uint8))[reg]
        if pedra == "granito":
            import fontes_procedurais as FP
            tex = FP.granito_referencia(y1 - y0, x1 - x0, Q.px_m, semente=900 + i).astype(np.float32)
        else:
            tex = textura(q["pedra"], Q.px_m, y1 - y0, x1 - x0, semente=900 + i).astype(np.float32)
            med = tex.reshape(-1, 3).mean(axis=0)
            tex = (med + q["contraste"] * (tex - med)) * (np.float32(q["tom"]) / med)  # a placa, no tom areia
        d = cv2.distanceTransform((al > 0.5).astype(np.uint8), cv2.DIST_L2, 3)
        tex *= (1 - q["volume"] * (1 - np.minimum(1, d / (q["larg_m"] * Q.px_m))) ** 2)[..., None]
        if borda:
            s = borda["sombra"]
            d_ = s["dist_m"] * Q.px_m
            sb = cv2.GaussianBlur(cv2.warpAffine(al, np.float32([[1, 0, -d_], [0, 1, d_]]), al.shape[::-1]), (0, 0),
                                  s["sig_m"] * Q.px_m) * s["forca"]
            out[reg] *= (1 - sb * (1 - al))[..., None]
            tex *= (1 - (1 - borda["mult"]) * np.clip(borda["larg_px"] + 1 - d, 0, 1))[..., None]
        out[reg] = out[reg] * (1 - al[..., None]) + tex * al[..., None]
        pecas += 1
    # as cubas: louça branca, a bacia de cantos arredondados recuada do aro, a sombra interna do lado da luz
    lq, c = PECAS["louca"], q["cuba"]
    sem_traco = np.zeros((Q.H, Q.W), np.uint8)          # onde o traço do PDF não entra: o aro duplo vira um contorno só
    for r in cubas:
        x0, y0, x1, y1 = ret_q(Q, (r[0] - c["aro_pt"], r[1] - c["aro_pt"], r[2] + c["aro_pt"], r[3] + c["aro_pt"]))
        if cuba is not None:                            # a cuba pedida (a esculpida em pedra), no lugar da louça
            out = cuba(Q, out, (r[0] - c["aro_pt"], r[1] - c["aro_pt"], r[2] + c["aro_pt"], r[3] + c["aro_pt"]))
            sem_traco[y0:y1, x0:x1] = 1
            continue
        ss_ = 4
        forma = ((y1 - y0 + 8) * ss_, (x1 - x0 + 8) * ss_)
        (fx0, fy0), (fx1, fy1) = Q.p2q(r[0] - c["aro_pt"], r[1] - c["aro_pt"]), Q.p2q(r[2] + c["aro_pt"], r[3] + c["aro_pt"])
        X0, Y0 = x0 - 4, y0 - 4
        m = _ret_arredondado(forma, (fx0 - X0) * ss_, (fy0 - Y0) * ss_, (fx1 - X0) * ss_, (fy1 - Y0) * ss_,
                             0.012 * Q.px_m * ss_)
        al = cv2.resize(m, (x1 - x0 + 8, y1 - y0 + 8), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
        e_ = c["recuo"] * min(fx1 - fx0, fy1 - fy0)
        bac = _ret_arredondado(forma, (fx0 - X0 + e_) * ss_, (fy0 - Y0 + e_) * ss_, (fx1 - X0 - e_) * ss_,
                               (fy1 - Y0 - e_) * ss_, c["raio_m"] * Q.px_m * ss_)
        ab = cv2.resize(bac, al.shape[::-1], interpolation=cv2.INTER_AREA).astype(np.float32) / 255
        reg = out[Y0:y1 + 4, X0:x1 + 4]
        cor = np.empty_like(reg)
        cor[:] = np.float32(lq["ceramica"])
        si = lq["sombra_int"]
        d_ = si["dist_m"] * Q.px_m
        fora = 1 - cv2.warpAffine(ab, np.float32([[1, 0, -d_], [0, 1, d_]]), ab.shape[::-1], borderValue=0)
        fora = cv2.GaussianBlur(fora, (0, 0), si["sig_m"] * Q.px_m)
        cor *= (1 - si["forca"] * fora * ab)[..., None]
        cor *= (1 - 0.02 * ab)[..., None]                                  # o fundo da bacia, quase do tom do aro
        # o contorno da bacia, fino (antialias)
        gb = cv2.morphologyEx(bac, cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8))
        lb = cv2.resize(gb, al.shape[::-1], interpolation=cv2.INTER_AREA).astype(np.float32)[..., None] / 255 * 0.55
        cor = cor * (1 - lb) + np.float32(PECAS["traco"]["cor"]) * lb
        # sombra curta da cuba na pedra
        d2 = 0.025 * Q.px_m
        sb = cv2.GaussianBlur(cv2.warpAffine(al, np.float32([[1, 0, -d2], [0, 1, d2]]), al.shape[::-1]), (0, 0),
                              0.02 * Q.px_m) * (1 - al) * 0.25
        reg = reg * (1 - sb)[..., None]
        reg = reg * (1 - al[..., None]) + cor * al[..., None]
        ga = cv2.morphologyEx(m, cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8))
        la = cv2.resize(ga, al.shape[::-1], interpolation=cv2.INTER_AREA).astype(np.float32)[..., None] / 255 * 0.7
        out[Y0:y1 + 4, X0:x1 + 4] = reg * (1 - la) + np.float32(PECAS["traco"]["cor"]) * la
        sem_traco[Y0:y1 + 4, X0:x1 + 4] |= cv2.dilate((al > 0.02).astype(np.uint8), np.ones((3, 3), np.uint8))
    # o contorno fino de cada peça (o traço do PDF)
    ss = 4
    m = np.zeros((Q.H * ss, Q.W * ss), np.uint8)
    for d in Q.desenhos:
        if d.get("layer") == "ARQ_BANCADAS" and d["type"] in ("s", "fs"):
            for c in _poligonos(Q, d, ss):
                cv2.polylines(m, [c], False, 255, max(1, round(0.7 * ss)))
    t = cv2.resize(m, (Q.W, Q.H), interpolation=cv2.INTER_AREA).astype(np.float32)[..., None] / 255 * q["forca"]
    t *= (1 - sem_traco)[..., None]
    out = out * (1 - t) + np.float32(q["contorno"]) * t
    print(f"    bancadas: {pecas} peças em " + ("granito marrom" if pedra == "granito" else f"{q['pedra']} no tom areia")
          + f", a {Q.px_m:.1f} px/m, com o contorno do PDF"
          + (", a borda no tom escurecido da pedra e a sombra curta (E9)" if borda else "") +
          f"; {len(cubas)} cubas " + ("esculpidas na pedra pedida" if cuba else "em louça branca"))
    return np.clip(out, 0, 255).astype(np.uint8)


# Os bancos da sauna em travertino (usuário, 22/10/26: "AS PEDRAS DA SAUNA, EM FORMA DE BANCOS, SÃO EM TRAVERTINE"). No
# PDF do Subsolo, o retângulo bege da ARQ_CONTRAPISO (2,95 x 1,00 m) com os dois níveis: o de trás, junto à parede (a peça
# de 0,50 m da ARQ_BANCADAS, que sai das bancadas), e o da frente; a tira de 4 cm entre os dois é o espelho. O travertino
# da biblioteca, com o veio ao longo dos bancos e no tom do piso da sauna, logo à frente (seção 3: "na pedra do próprio
# piso, com linha fina e sombra discreta entre os níveis"): o nível de trás um pouco mais claro, a linha fina no espelho
# e na frente, e a sombra discreta no nível da frente, junto ao espelho.
SAUNA_F = {"Subsolo": {"pt": (798.5, 895.7, 965.8, 952.4), "espelho_pt": (924.0, 926.3),
                       "piso_pt": (805.0, 875.0, 960.0, 892.0)},
           "alto": 1.04, "baixo": 1.0, "linha": (118, 124, 130), "larg_px": 0.9, "forca_linha": 0.75,
           "sombra": {"larg_m": 0.05, "forca": 0.12}, "veio": 1.6, "semente": 733}


def no_banco_sauna(Q, r):
    q = SAUNA_F.get(Q.chave)
    return bool(q) and q["pt"][0] - 0.5 <= r.x0 and r.x1 <= q["pt"][2] + 0.5 and q["pt"][1] - 0.5 <= r.y0 \
        and r.y1 <= q["pt"][3] + 0.5


def bancos_sauna(Q, img, bruto=None):
    sys.path.insert(0, str(B.RAIZ / "_texturas"))
    from texturas import textura
    from retoque_terreo_casae import linha_aa
    q, b = SAUNA_F, SAUNA_F[Q.chave]
    a = Q.preencher(lambda d: d.get("layer") == "ARQ_CONTRAPISO" and d.get("fill") and
                    all(abs(v - w) < 0.5 for v, w in zip((d["rect"].x0, d["rect"].y0, d["rect"].x1, d["rect"].y1),
                                                         b["pt"])), fs=False)
    x0, y0, x1, y1 = ret_q(Q, b["pt"])
    x0, y0, x1, y1 = x0 - 2, y0 - 2, x1 + 2, y1 + 2
    px0, py0, px1, py1 = ret_q(Q, b["piso_pt"])
    cor = np.median(img[py0:py1, px0:px1].reshape(-1, 3).astype(np.float32), axis=0)   # o travertino do piso
    if bruto:                                                          # o travertino bruto (veios e poros), como o piso
        import final3840_casaa as FA
        T = cor * FA.travertino_bruto(Q, y1 - y0, x1 - x0, q["semente"], forca=q["veio"], **FA.TRAVERTINO[bruto])[
            ..., None]
    else:
        T = textura("travertino", Q.px_m, y1 - y0, x1 - x0, semente=q["semente"]).astype(np.float32)
        det = cv2.GaussianBlur(T, (0, 0), 0.6) / np.maximum(cv2.GaussianBlur(T, (0, 0), 3.0 * Q.px_m), 1)
        T = cor * (1 + q["veio"] * (det - 1))                          # o veio na força do piso (`piso_textura`)
    ye0 = Q.p2q(b["pt"][0], b["espelho_pt"][0])[1] - y0
    ye1 = Q.p2q(b["pt"][0], b["espelho_pt"][1])[1] - y0
    yy = np.arange(y1 - y0, dtype=np.float32)[:, None]
    fator = np.where(yy >= ye1, q["alto"], q["baixo"])                 # o nível de trás, um pouco mais claro
    s = q["sombra"]                                                    # e a sombra discreta na frente do espelho
    fator = fator * np.where(yy < ye0, 1 - s["forca"] * np.exp(-(ye0 - yy) / (s["larg_m"] * Q.px_m)), 1.0)
    novo = T * fator[..., None]
    reg = img[y0:y1, x0:x1].astype(np.float32)
    al = a[y0:y1, x0:x1, None]
    reg = reg * (1 - al) + novo * al
    # a linha fina no espelho (meio da tira) e na frente do banco
    ym = (ye0 + ye1) / 2
    yf = Q.p2q(b["pt"][0], b["pt"][1])[1] - y0
    xa, xb = Q.p2q(b["pt"][0], 0)[0] - x0, Q.p2q(b["pt"][2], 0)[0] - x0
    ln = np.maximum(linha_aa(reg.shape[:2], [(xa, ym), (xb, ym)], q["larg_px"]),
                    linha_aa(reg.shape[:2], [(xa, yf), (xb, yf)], q["larg_px"]))[..., None] * q["forca_linha"]
    reg = reg * (1 - ln) + np.float32(q["linha"]) * ln
    out = img.copy()
    out[y0:y1, x0:x1] = np.clip(reg, 0, 255).astype(np.uint8)
    print(f"    sauna: os bancos ({b['pt'][2] - b['pt'][0]:.0f} x {b['pt'][3] - b['pt'][1]:.0f} pt) no travertino "
          + ("bruto (veios e poros)" if bruto else "da biblioteca")
          + ", no tom do piso, com o espelho em linha fina e a sombra discreta")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 4. As peças da biblioteca, pelas mesmas rotinas dos ajustes, agora no quadro da prancha
class em_quadro:
    """As rotinas dos ajustes (que leem o PDF por `pdf_pavimento`, a escala por `px_por_m` e a base por `base_terreo`)
    passam a desenhar no quadro da prancha; os parâmetros delas em px de 2000 são levados à escala."""

    def __init__(self, Q):
        self.Q = Q

    def __enter__(self):
        Q = self.Q
        self.salvo = (AJ.pdf_pavimento, B.px_por_m, AJ.base_terreo, dict(AJ.CORTINAS_1PAV))
        pdf, base = AJ.pdf_pavimento, AJ.base_terreo
        AJ.pdf_pavimento = lambda c: (Q.pg, Q.p2q) if c == Q.chave else pdf(c)
        B.px_por_m = lambda c: Q.px_m

        def base_q(forma, c="Terreo"):
            if c == Q.chave:
                return cv2.resize(Q.chapada, (forma[1], forma[0]), interpolation=cv2.INTER_NEAREST)
            return base(forma, c)
        AJ.base_terreo = base_q
        e = Q.W / 2000
        c = AJ.CORTINAS_1PAV
        AJ.CORTINAS_1PAV = dict(c, dentro=round(c["dentro"] * e), seguidos=round(c["seguidos"] * e),
                                limpar=dict(c["limpar"], meia=round(c["limpar"]["meia"] * e),
                                            linhas=tuple(round(v * e) for v in c["limpar"]["linhas"])))
        return self

    def __exit__(self, *_):
        AJ.pdf_pavimento, B.px_por_m, AJ.base_terreo, AJ.CORTINAS_1PAV = self.salvo


# As 4 banquetas da bancada gourmet: no PDF são os círculos da ARQ_LAYOUT HUMANIZAÇÃO (só traço) nesta caixa (pt). Os
# círculos ficam fora das peças do PDF (sairiam como aros transparentes por cima da pedra) e as `banqueta_linho` da
# biblioteca (0,40 m, viradas para a bancada) pousam no centro de cada um, com a sombra curta das peças (os `centros`
# da `BANQUETAS_B` são px do render de 2000 e não valem no quadro). Elas entram por baixo do tampo (usuário, 22/10/26:
# "AS BANQUETAS DEVEM APARECER PARCIALMENTE, ATRÁS DA BANCADA"): a pedra da ARQ_BANCADAS cobre a parte delas que fica
# sob ela, e a sombra não cai sobre o tampo.
BANQUETAS_PT = (1135.0, 1455.0, 1315.0, 1492.0)


def centros_banquetas(Q):
    x0, y0, x1, y1 = BANQUETAS_PT
    rs = [d["rect"] for d in Q.desenhos if d.get("layer") == "ARQ_LAYOUT HUMANIZAÇÃO" and x0 <= d["rect"].x0
          and d["rect"].x1 <= x1 and y0 <= d["rect"].y0 and d["rect"].y1 <= y1]
    rs.sort(key=lambda r: r.x0)
    grupos = []
    for r in rs:                                       # um círculo por grupo: os traços seguidos em x
        if grupos and r.x0 <= grupos[-1][2] + 2.0:
            g = grupos[-1]
            grupos[-1] = [min(g[0], r.x0), min(g[1], r.y0), max(g[2], r.x1), max(g[3], r.y1)]
        else:
            grupos.append([r.x0, r.y0, r.x1, r.y1])
    return [tuple(Q.p2q((g[0] + g[2]) / 2, (g[1] + g[3]) / 2)) for g in grupos]


def banquetas(Q, img):
    sys.path.insert(0, str(B.RAIZ / "_blocos"))
    import blocos
    q, s = B.BANQUETAS_B, PECAS["sombra"]
    cor, al = blocos.bloco("banqueta_linho", q["d_m"] * Q.px_m / 0.45)
    for _ in range(q["giro"] // 90):
        cor, al = cv2.rotate(cor, cv2.ROTATE_90_CLOCKWISE), cv2.rotate(al, cv2.ROTATE_90_CLOCKWISE)
    al = np.clip(al, 0, 1).astype(np.float32)
    h, w = al.shape
    d_ = s["dist_m"] * Q.px_m
    out = img.astype(np.float32)
    tampo = Q.preencher(lambda d: d.get("layer") == "ARQ_BANCADAS" and d.get("fill"), fs=False)
    cs = centros_banquetas(Q)
    for cx, cy in cs:
        # a peça em posição subpixel (translação pura), num recorte com folga para a sombra
        f = int(np.ceil(d_ + 4 * s["sig_m"] * Q.px_m)) + 2
        X0, Y0 = int(cx - w / 2) - f, int(cy - h / 2) - f
        Wr, Hr = w + 2 * f, h + 2 * f
        Mt = np.float32([[1, 0, cx - w / 2 - X0], [0, 1, cy - h / 2 - Y0]])
        livre = 1 - tampo[Y0:Y0 + Hr, X0:X0 + Wr]                   # o que o tampo não cobre
        a = cv2.warpAffine(al, Mt, (Wr, Hr), flags=cv2.INTER_LINEAR)
        c = cv2.warpAffine(cor.astype(np.float32), Mt, (Wr, Hr), flags=cv2.INTER_LINEAR)
        sb = cv2.GaussianBlur(cv2.warpAffine(a, np.float32([[1, 0, -d_], [0, 1, d_]]), (Wr, Hr)), (0, 0),
                              s["sig_m"] * Q.px_m) * s["forca"] * livre
        a = a * livre
        reg = out[Y0:Y0 + Hr, X0:X0 + Wr]
        reg *= (1 - sb * (1 - a))[..., None]
        out[Y0:Y0 + Hr, X0:X0 + Wr] = reg * (1 - a[..., None]) + c * a[..., None]
    print(f"    bancada gourmet: {len(cs)} banquetas de linho da biblioteca ({q['d_m']:.2f} m) nos círculos do PDF, "
          f"com a sombra curta das peças, entrando sob o tampo")
    return np.clip(out, 0, 255).astype(np.uint8)


# As cortinas vêm depois das esquadrias (usuário, 22/10/26: "CORRIJA A CORTINA QUE ESTÁ DUPLICADA"): a limpeza das
# esquadrias espelha o piso de junto do vidro sobre a faixa dele, e a cortina, desenhada antes, ia junto; saía duplicada
# (duas fileiras de ondas à esquerda da sala íntima e as ondas cruzadas à direita). Agora o espelho só leva o piso, e a
# `cortinas_b` limpa os tracinhos da cortina antiga do render junto ao vidro antes de desenhar a da biblioteca.
# As ondinhas do PDF que marcam o pano também vêm riscadas de leve no piso desde a base (a luz do render as trazia); o
# espelho das esquadrias as levava para junto do vidro, entre o trilho e a cortina nova. Antes das esquadrias elas
# saem (`ondas_fora`): perto do traço (pelos caminhos do PDF, com folga), o px que destoa da mediana do piso da mesma
# linha (as réguas correm na horizontal nesses ambientes; a onda é minoria na janela) toma o valor dela. Piso é o
# material da base chapada em volta do traço (os pisos têm cor; vidro, parede e móvel são cinza ou branco); a parede
# preta onde o pano encosta fica (os pontinhos escuros da onda são soltos e saem).
ONDAS_F = {"folga_px": 2, "faixa_px": 8, "janela_px": 12, "tol": 6, "cromia": 20, "destoa": 6, "parede": 50}


def ondas_fora(Q, img):
    q = ONDAS_F
    m = np.zeros((Q.H, Q.W), np.uint8)
    for d in Q.desenhos:
        if B.onda_cortina_b(d):
            for c in Q.caminhos(d):
                cv2.polylines(m, [np.int32(np.round(c * 8))], False, 255, 1, cv2.LINE_8, shift=3)
    m = cv2.dilate(m, np.ones((2 * q["folga_px"] + 1,) * 2, np.uint8)) > 0
    with em_quadro(Q):
        trechos = B.trechos_cortina_b(Q.chave)
    out = img.copy()
    f, j = q["faixa_px"], q["janela_px"]
    n = 0
    for o, _, ex, e0, e1 in trechos:
        a0, a1, c0, c1 = int(e0) - f, int(np.ceil(e1)) + f + 1, int(ex) - f, int(np.ceil(ex)) + f + 1
        y0, y1, x0, x1 = (a0, a1, c0 - j, c1 + j) if o == "v" else (c0, c1, a0 - j, a1 + j)
        ch = Q.chapada[y0:y1, x0:x1].astype(np.int32)
        cor = (ch.max(axis=2) - ch.min(axis=2)) > q["cromia"]
        cores, conta = np.unique(ch[cor], axis=0, return_counts=True)
        piso = np.abs(ch - cores[conta.argmax()]).max(axis=2) <= q["tol"]
        reg = img[y0:y1, x0:x1].astype(np.int32)
        um = np.ones((3, 3), np.uint8)
        parede = cv2.dilate(cv2.morphologyEx((reg.mean(axis=2) < q["parede"]).astype(np.uint8), cv2.MORPH_OPEN, um), um)
        mk = m[y0:y1, x0:x1] & cv2.dilate(piso.astype(np.uint8), um).astype(bool) & ~parede.astype(bool)
        mk[:, :j], mk[:, -j:] = False, False
        for yy, xx in zip(*np.nonzero(mk)):
            v = piso[yy, xx - j:xx + j + 1]
            if v.sum() >= 5:
                ref = np.median(reg[yy, xx - j:xx + j + 1][v], axis=0)
                if np.abs(reg[yy, xx] - ref).max() > q["destoa"]:
                    out[y0 + yy, x0 + xx] = ref
                    n += 1
    print(f"    ondas do PDF: {n} px das {len(trechos)} cortinas voltam a ser piso antes do espelho das esquadrias")
    return out


def cortinas(Q, img):
    with em_quadro(Q):
        out = np.ascontiguousarray(B.cortinas_b(np.ascontiguousarray(img.copy()), Q.chave))
    return out


# A cama da suíte master e o banco aos pés dela (usuário, 22/10/26: "VAMOS REPRESENTAR MELHOR ESSA CAMA E SEU COBRE
# LEITO. ESTÁ FALTANDO O BANCO QUE ESTÁ ACIMA DA CAMA"). No PDF a cama é um polígono só (ARQ_LOUÇAS E METAIS): o colchão,
# o cobre-leito dobrado em rolo junto aos travesseiros (mais largo que a cama, caindo dos lados) e a placa da cabeceira;
# a roupa de cama da biblioteca ia só no colchão e a sobra do rolo saía em dois "calombos" brancos. Agora tudo sai da
# silhueta do PDF, por faixas (pt, da cabeceira, embaixo, aos pés): a placa, o lençol com os dois travesseiros cinza e
# as duas almofadas bordô (nas posições do PDF), o rolo do cobre-leito (sombreado como tecido enrolado) e o cobre-leito
# em matelassê off-white (o pesponto em losangos, as rugas e a queda nas bordas), com a peseira bordô atravessada nos
# pés. O banco estava no PDF na camada DOC_TEXTOS, que as peças não leem: entra estofado em linho greige, com os três
# assentos, as costuras tracejadas do PDF e os dois rolos laterais, cada um com volume e a sombra curta no tapete.
CAMA_MASTER_F = {
    "cama_pt": (863.1, 838.0, 994.2, 952.4), "banco_pt": (877.5, 791.9, 979.7, 833.8), "ss": 8,
    "placa_y": 947.4, "lencol_y": 919.5, "rolo_y": (895.8, 920.8),
    "travesseiros": [(885.0, 934.0, 925.5, 947.6), (927.5, 934.0, 969.0, 947.6)],
    "almofadas": [(890.5, 915.0, 925.0, 935.0), (928.0, 915.0, 962.0, 935.0)],
    "peseira_y": (847.0, 866.0),
    "cores": {"branco": (244, 244, 246), "matelasse": (236, 237, 239), "cinza": (214, 213, 216),
              "bordo": (85, 81, 118), "placa": (176, 182, 188), "linho": (170, 180, 192), "traco": (120, 120, 124)},
    "banco": {"assentos_x": (912.2, 945.2), "costura_pt": 1.7, "rolos": [(882.0, 795.8, 896.8, 829.7),
                                                                       (960.3, 795.8, 975.0, 829.7)]},
    "sombra": {"dist_m": 0.035, "sig_m": 0.03, "forca": 0.30},
}


def cama_master(Q, img):
    q, k = CAMA_MASTER_F, CAMA_MASTER_F["ss"]
    c = {n: np.float32(v) for n, v in q["cores"].items()}
    cx0, cy0, cx1, cy1 = q["cama_pt"]
    bx0, by0, bx1, by1 = q["banco_pt"]
    X0, Y0, X1, Y1 = ret_q(Q, (min(cx0, bx0) - 6, by0 - 6, max(cx1, bx1) + 6, cy1 + 6))
    w, h = X1 - X0, Y1 - Y0
    rng = np.random.default_rng(64)
    xs = X0 + (np.arange(w * k) + 0.5) / k
    ys = Y0 + (np.arange(h * k) + 0.5) / k
    (ox, oy), (ex, ey) = Q.p2q(0, 0), Q.p2q(1, 1)
    xpt = ((xs - ox) / (ex - ox))[None, :]                      # pt de cada coluna e linha, em ss
    ypt = ((ys - oy) / (ey - oy))[:, None]

    def poli(d):
        m = np.zeros((h * k, w * k), np.uint8)
        cv2.fillPoly(m, [np.int32(np.round((cc - (X0, Y0)) * k)) for cc in Q.caminhos(d) if len(cc) >= 3], 255)
        return m.astype(np.float32) / 255

    def ret(r, raio_pt=0.0):
        m = np.zeros((h * k, w * k), np.uint8)
        (a0, b0), (a1, b1) = Q.p2q(r[0], r[1]), Q.p2q(r[2], r[3])
        rr = int(round(raio_pt * Q.px_m / 56.69 * k))
        return _ret_arredondado(m.shape, (a0 - X0) * k, (b0 - Y0) * k, (a1 - X0) * k, (b1 - Y0) * k, rr) \
            .astype(np.float32) / 255

    def ruido(sig):
        n_ = cv2.GaussianBlur(rng.normal(0, 1, (h * k, w * k)).astype(np.float32), (0, 0), sig * Q.px_m * k)
        return n_ / max(n_.std(), 1e-6)

    def volume(m, larg_m, forca):
        d_ = cv2.distanceTransform((m > 0.5).astype(np.uint8), cv2.DIST_L2, 5) / (Q.px_m * k)
        return 1 - forca * (1 - np.minimum(1, d_ / larg_m)) ** 2

    def sombra(m, forca=None):
        s_ = q["sombra"]
        d_ = s_["dist_m"] * Q.px_m * k
        return cv2.GaussianBlur(cv2.warpAffine(m, np.float32([[1, 0, -d_], [0, 1, d_]]), (w * k, h * k)), (0, 0),
                                s_["sig_m"] * Q.px_m * k) * (forca or s_["forca"])

    cama = next(d for d in Q.desenhos if d.get("layer") == "ARQ_LOUÇAS E METAIS" and d["type"] == "f"
                and max(abs(a - b) for a, b in zip(d["rect"], q["cama_pt"])) < 0.5)
    banco = next(d for d in Q.desenhos if d.get("layer") == "DOC_TEXTOS" and d["type"] == "f"
                 and max(abs(a - b) for a, b in zip(d["rect"], q["banco_pt"])) < 0.5)
    P, Bm = poli(cama), poli(banco)
    base = cv2.resize(img[Y0:Y1, X0:X1].astype(np.float32), (w * k, h * k), interpolation=cv2.INTER_LINEAR)
    # o fundo (o tapete) sem a cama do PDF: a mediana em volta, com a sombra curta do conjunto
    fora = cv2.dilate(((P + Bm) > 0.01).astype(np.uint8), np.ones((3 * k, 3 * k), np.uint8)) == 0
    fundo = np.median(base[fora], axis=0)
    out = np.where(((P + Bm) > 0.01)[..., None], fundo, base)
    out *= (1 - sombra(np.maximum(P, Bm)) * (1 - np.maximum(P, Bm)))[..., None]
    rug = 1 + 0.010 * ruido(0.18) + 0.006 * ruido(0.05)
    # 1. a placa da cabeceira e o lençol
    placa = P * (ypt >= q["placa_y"])
    out = out * (1 - placa[..., None]) + c["placa"] * volume(placa, 0.01, 0.15)[..., None] * placa[..., None]
    lencol = P * (ypt >= q["lencol_y"]) * (ypt < q["placa_y"])
    out = out * (1 - lencol[..., None]) + c["branco"] * (rug * volume(lencol, 0.05, 0.08))[..., None] * lencol[..., None]
    # 2. os travesseiros cinza (atrás) e as almofadas bordô (na frente), com volume e a sombra curta
    for lista, cor, vol in ((q["travesseiros"], c["cinza"], 0.16), (q["almofadas"], c["bordo"], 0.20)):
        for r in lista:
            m = ret(r, 4.0) * P
            out *= (1 - sombra(m, 0.22) * (1 - m))[..., None]
            tex = volume(m, 0.06, vol) * (1 + 0.008 * ruido(0.03))
            out = out * (1 - m[..., None]) + cor * tex[..., None] * m[..., None]
            if cor is c["bordo"]:                             # o vivo da almofada, um tom acima, junto à borda
                anel = m * (1 - cv2.erode(m, np.ones((int(0.6 * k), int(0.6 * k)), np.uint8)))
                out = out * (1 - 0.35 * anel[..., None]) + cor * 1.25 * 0.35 * anel[..., None]
    # 3. o cobre-leito: matelassê off-white (o pesponto em losangos de 12 cm, as rugas, a queda nas bordas)
    corpo = P * (ypt < q["rolo_y"][0])
    passo = 0.12 * 56.69
    u, v = (xpt + ypt) / passo, (xpt - ypt) / passo
    pesp = np.maximum(np.exp(-((u - np.round(u)) * passo / 0.35) ** 2), np.exp(-((v - np.round(v)) * passo / 0.35) ** 2))
    tecido = (1 - 0.045 * pesp) * (1 + 0.014 * ruido(0.15) + 0.006 * ruido(0.04)) * volume(corpo, 0.07, 0.12)
    out = out * (1 - corpo[..., None]) + c["matelasse"] * tecido[..., None] * corpo[..., None]
    # a peseira bordô atravessada nos pés, com as dobras e a sombra nas duas bordas
    pe0, pe1 = q["peseira_y"]
    pes = corpo * (ypt >= pe0) * (ypt < pe1)
    dob = 1 + 0.10 * cv2.GaussianBlur(rng.normal(0, 1, (1, w * k)).astype(np.float32), (0, 0), 0.05 * Q.px_m * k)
    dob = dob / max(dob.std(), 1e-6) * 0.0 + dob
    out *= (1 - 0.16 * corpo * (np.exp(-np.clip(ypt - pe1, 0, None) / 1.2) * (ypt >= pe1) +
                                np.exp(-np.clip(pe0 - ypt, 0, None) / 0.8) * (ypt < pe0)))[..., None]
    out = out * (1 - pes[..., None]) + c["bordo"] * (dob * volume(pes, 0.04, 0.18) * (1 + 0.02 * ruido(0.03)))[..., None] \
        * pes[..., None]
    # 4. o rolo do cobre-leito (tecido enrolado: claro no meio, mais escuro nas bordas), com a sombra no lençol
    r0, r1 = q["rolo_y"]
    rolo = P * (ypt >= r0) * (ypt < r1)
    cil = 0.80 + 0.20 * np.sin(np.pi * np.clip((ypt - r0) / (r1 - r0), 0, 1)) ** 0.7
    rugas = 1 + 0.03 * cv2.GaussianBlur(rng.normal(0, 1, (1, w * k)).astype(np.float32), (0, 0), 0.04 * Q.px_m * k) \
        / 0.3
    out *= (1 - sombra(rolo, 0.25) * (1 - rolo))[..., None]
    out = out * (1 - rolo[..., None]) + c["matelasse"] * (cil * np.clip(rugas, 0.9, 1.1) * volume(rolo, 0.03, 0.10)
                                                          )[..., None] * rolo[..., None]
    # as almofadas da frente por cima do rolo (como no PDF)
    for r in q["almofadas"]:
        m = ret(r, 4.0) * P * (ypt >= r1 - 2.0)
        out = out * (1 - m[..., None]) + c["bordo"] * volume(ret(r, 4.0), 0.06, 0.20)[..., None] * m[..., None]
    # 5. o contorno fino da cama
    lt = max(1, int(round(0.5 * k)))
    anel = P * (1 - cv2.erode(P, np.ones((lt, lt), np.uint8)))
    out = out * (1 - 0.55 * anel[..., None]) + c["traco"] * 0.55 * anel[..., None]
    # 6. o banco: linho greige estofado, os três assentos, as costuras tracejadas e os rolos laterais
    bq = q["banco"]
    tex_b = volume(Bm, 0.05, 0.16) * (1 + 0.025 * ruido(0.012))
    xa, xb = bq["assentos_x"]
    for xc in (xa, xb):                                         # o assento cai junto às costuras
        tex_b *= 1 - 0.10 * np.exp(-((xpt - xc) / 1.6) ** 2)
    out = out * (1 - Bm[..., None]) + c["linho"] * tex_b[..., None] * Bm[..., None]
    for r in bq["rolos"]:
        m = ret(r, 3.0)
        cx_ = (r[0] + r[2]) / 2
        cil_b = 0.82 + 0.18 * np.cos(np.clip((xpt - cx_) / ((r[2] - r[0]) / 2), -1, 1) * np.pi / 2)
        out *= (1 - sombra(m, 0.20) * (1 - m))[..., None]
        out = out * (1 - m[..., None]) + c["linho"] * 1.04 * (cil_b * volume(m, 0.02, 0.08))[..., None] * m[..., None]
    cm = np.zeros((h * k, w * k), np.uint8)
    e = bq["costura_pt"]

    def tracejado(pa, pb):
        (ua, va), (ub, vb) = Q.p2q(*pa), Q.p2q(*pb)
        comp = np.hypot(ub - ua, vb - va)
        t = 0.0
        while t < comp:
            t1 = min(comp, t + 0.035 * Q.px_m)
            cv2.line(cm, (int((ua + (ub - ua) * t / comp - X0) * k), int((va + (vb - va) * t / comp - Y0) * k)),
                     (int((ua + (ub - ua) * t1 / comp - X0) * k), int((va + (vb - va) * t1 / comp - Y0) * k)), 255,
                     max(1, int(0.45 * k)), cv2.LINE_AA)
            t = t1 + 0.02 * Q.px_m
    for pa, pb in (((bx0 + e, by0 + e), (bx1 - e, by0 + e)), ((bx0 + e, by1 - e), (bx1 - e, by1 - e)),
                   ((bx0 + e, by0 + e), (bx0 + e, by1 - e)), ((bx1 - e, by0 + e), (bx1 - e, by1 - e)),
                   ((xa, by0 + e), (xa, by1 - e)), ((xb, by0 + e), (xb, by1 - e))):
        tracejado(pa, pb)
    am = cm.astype(np.float32) / 255 * 0.45
    out = out * (1 - am[..., None]) + c["traco"] * 0.8 * am[..., None]
    lt = max(1, int(round(0.55 * k)))
    anel = Bm * (1 - cv2.erode(Bm, np.ones((lt, lt), np.uint8)))
    out = out * (1 - 0.6 * anel[..., None]) + c["traco"] * 0.7 * 0.6 * anel[..., None]
    res = img.copy()
    res[Y0:Y1, X0:X1] = np.clip(cv2.resize(out, (w, h), interpolation=cv2.INTER_AREA), 0, 255).astype(np.uint8)
    print("    suíte master: a cama na silhueta do PDF (placa, lençol, travesseiros, almofadas bordô, o rolo e o cobre-leito "
          "em matelassê com a peseira) e o banco estofado aos pés (da DOC_TEXTOS), com as costuras e os rolos")
    return res


# O desenho sobre a mesa redonda do hall interno (usuário, 22/10/26: "PRECISO DO DESENHO SOBRE A MESA"): no PDF, o
# tampo de 1,80 m tem o anel da borda, os cinco painéis arredondados em volta e o círculo do meio com a peça de centro
# (ARQ_MOBILIÁRIO e ARQ_LAYOUT HUMANIZAÇÃO). As linhas são finas e juntas, e as peças as liam como hachura (quase
# apagadas); o círculo da peça de centro ficava sob o tampo. Entram por cima, em linha fina nítida, com o relevo leve
# (a sombra de 0,6 px para baixo e à esquerda de cada linha).
MESA_HALL_F = {"pt": (1855.0, 1180.0, 1965.0, 1290.0), "camadas": ("ARQ_MOBILIÁRIO", "ARQ_LAYOUT HUMANIZAÇÃO"),
               "cor": (104, 104, 108), "forca": 0.70, "larg_px": 0.6, "relevo": 0.12, "ss": 8}


def desenho_mesa(Q, img):
    q, k = MESA_HALL_F, MESA_HALL_F["ss"]
    import pymupdf
    z = pymupdf.Rect(*q["pt"])
    X0, Y0, X1, Y1 = ret_q(Q, q["pt"])
    w, h = X1 - X0, Y1 - Y0
    m = np.zeros((h * k, w * k), np.uint8)
    n = 0
    lw = max(1, int(round(q["larg_px"] * k)))
    for d in Q.desenhos:
        if d.get("layer") in q["camadas"] and d["type"] in ("s", "fs") and z.contains(d["rect"]):
            for cc in Q.caminhos(d):
                cv2.polylines(m, [np.int32(np.round((cc - (X0, Y0)) * k))], False, 255, lw, cv2.LINE_AA)
            n += 1
    a = cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)
    rel = cv2.warpAffine(a, np.float32([[1, 0, -0.6], [0, 1, 0.6]]), (w, h))
    out = img.astype(np.float32)
    reg = out[Y0:Y1, X0:X1]
    reg *= (1 - q["relevo"] * rel * (1 - a))[..., None]
    al = np.clip(a * 1.3, 0, 1) * q["forca"]
    reg[:] = reg * (1 - al[..., None]) + np.float32(q["cor"]) * al[..., None]
    print(f"    mesa do hall interno: o desenho do tampo ({n} traços do PDF) por cima, em linha fina com relevo leve")
    return np.clip(out, 0, 255).astype(np.uint8)


def biblioteca(Q, img):
    out = np.ascontiguousarray(img.copy())
    with em_quadro(Q):
        if Q.chave == "Terreo":
            out = B.guarda_roupas_terreo(out)
            out = B.camas_b(out, "Terreo", B.CAMAS_B)
            out = cama_master(Q, out)
            out = B.cooktops_b(out)
            out = banquetas(Q, out)
            out = B.inox_terreo(out)
            out = B.adega_b(out)
            out = B.elevador_cabine(out)
    return out


# Os vidros dos boxes: no PDF, os grupos de traços retos e paralelos da ARQ_LOUÇAS E METAIS (as duas folhas de correr,
# 7 ou mais traços a menos de 4 pt um do outro), de 0,75 m ou mais. Nos banhos de piso em granito marrom (BH serviço e
# BH motorista), o vidro sai como faixa cinza-clara, bem visível (usuário, 22/10/26: "PRECISO QUE OS BOXES DOS BANHOS
# ONDE TEM PISO MARROM GRANITO EM CINZA CLARO. TEM QUE ESTAR VISÍVEL"); nos pisos claros fica o vidro das peças.
BOXES_F = {"junto_pt": 4.0, "n_min": 7, "comp_min_m": 0.75, "granito": (50, 66, 90), "granito_min": 0.3,
           "cor": (204, 206, 208), "larg_extra_px": 1.2}


def duchas_box(Q, boxes):
    """O lado do chuveiro de cada box: o centro (pt) da ducha do PDF (o quadrado de ~20 cm da ARQ_LOUÇAS E METAIS) que
    fica ao lado do vidro, a até 100 pt dele (ou None)."""
    qs = [d["rect"] for d in Q.desenhos if d.get("layer") == "ARQ_LOUÇAS E METAIS" and d["type"] in ("f", "fs")
          and 7 <= d["rect"].width <= 14 and 7 <= d["rect"].height <= 14 and abs(d["rect"].width - d["rect"].height) < 2]
    out = []
    for x0, y0, x1, y1, hor in boxes:
        melhor = None
        for r in qs:
            cx, cy = (r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2
            d_ = abs(cy - (y0 + y1) / 2) if hor else abs(cx - (x0 + x1) / 2)
            ao_lado = (x0 - 5 <= cx <= x1 + 5) if hor else (y0 - 5 <= cy <= y1 + 5)
            if ao_lado and d_ < 100 and (melhor is None or d_ < melhor[0]):
                melhor = (d_, (cx, cy))
        out.append(melhor[1] if melhor else None)
    return out


def vidros_box(Q):
    """Os vidros de box do PDF: [(x0, y0, x1, y1, deitado)] em pt."""
    q = BOXES_F
    ls = [d["rect"] for d in Q.desenhos if d.get("layer") == "ARQ_LOUÇAS E METAIS" and d["type"] == "s"
          and len(d["items"]) == 1 and d["items"][0][0] == "l"
          and ((d["rect"].width >= 20 and d["rect"].height < 0.3) or (d["rect"].height >= 20 and d["rect"].width < 0.3))]
    grupos = []
    for r in sorted(ls, key=lambda r: (r.height > r.width, r.y0, r.x0)):
        hor = r.width > r.height
        for g in grupos:
            if g[5] != hor:
                continue
            if (hor and abs(r.y0 - g[6]) <= q["junto_pt"] and r.x0 <= g[2] + 2 and r.x1 >= g[0] - 2) or \
                    (not hor and abs(r.x0 - g[6]) <= q["junto_pt"] and r.y0 <= g[3] + 2 and r.y1 >= g[1] - 2):
                g[0], g[1], g[2], g[3] = min(g[0], r.x0), min(g[1], r.y0), max(g[2], r.x1), max(g[3], r.y1)
                g[4] += 1
                break
        else:
            grupos.append([r.x0, r.y0, r.x1, r.y1, 1, hor, r.y0 if hor else r.x0])
    return [(g[0], g[1], g[2], g[3], g[5]) for g in grupos
            if g[4] >= q["n_min"] and max(g[2] - g[0], g[3] - g[1]) >= q["comp_min_m"] * 56.69]


def boxes_granito(Q, img):
    from retoque_terreo_casae import linha_aa
    q = BOXES_F
    gran = Q.cor([q["granito"]], tol=8)
    out = img.astype(np.float32)
    n = 0
    for x0, y0, x1, y1, hor in vidros_box(Q):
        a0, b0, a1, b1 = ret_q(Q, (x0, y0, x1, y1))
        if gran[b0 - 4:b1 + 5, a0 - 4:a1 + 5].mean() < q["granito_min"]:
            continue
        (ax, ay), (bx, by) = Q.p2q(x0, y0), Q.p2q(x1, y1)
        if hor:
            pts, larg = [(ax, (ay + by) / 2), (bx, (ay + by) / 2)], (by - ay) + q["larg_extra_px"]
        else:
            pts, larg = [((ax + bx) / 2, ay), ((ax + bx) / 2, by)], (bx - ax) + q["larg_extra_px"]
        al = linha_aa((Q.H, Q.W), pts, larg)[..., None]
        out = out * (1 - al) + np.float32(q["cor"]) * al
        n += 1
    print(f"    {n} vidros de box no granito em cinza claro")
    return np.clip(out, 0, 255).astype(np.uint8)


# As soleiras (R13; usuário, 22/10/26: "CORRIGIR AS SOLEIRAS"): as da final vinham dos ajustes de 2000 px, ampliadas,
# moles, com a borda borrada e restos em volta. Agora, no quadro da prancha: os vãos de porta que o PDF deixa em branco
# (`ajustes_casab.vaos_brancos`: o branco da legenda entre as paredes, junto à ponta de um arco de porta; onde o piso
# atravessa o vão, não há soleira), cada um ajustado às faces e às pontas das paredes do PDF (o desenho vetorial, em
# 8 x), em Bege Bahia na escala (a foto da biblioteca, no tom do Bege Bahia da referência), nítido, com as duas faces
# da parede em traço cinza fino. As portas e os batentes vêm por cima, nas esquadrias.
SOLEIRAS_F = {"ss": 8, "janela_pt": 14.0, "procura_m": 0.20, "forca": 0.5, "linha": (150, 152, 154), "linha_px": 0.6,
              "folga_pt": 0.0, "semente": 7, "limpa_px": 3}


def _soleira_no_pdf(Q, r):
    """O vão r (pt, aproximado) ajustado às paredes do PDF: (x0, y0, x1, y1) no quadro, em px fracionários."""
    q = SOLEIRAS_F
    k = q["ss"]
    hor = (r[2] - r[0]) >= (r[3] - r[1])
    w0, h0, w1, h1 = ret_q(Q, (r[0] - q["janela_pt"], r[1] - q["janela_pt"], r[2] + q["janela_pt"],
                               r[3] + q["janela_pt"]))
    m = np.zeros(((h1 - h0) * k, (w1 - w0) * k), np.uint8)
    for d in Q.desenhos:
        if d.get("layer") in ("ARQ_PAREDE", "ARQ_ELEMENTOS FIXOS", "EST_PILAR") and d["type"] in ("f", "fs") \
                and d.get("fill") and max(d["fill"]) < 0.6:
            rr = d["rect"]
            if rr.x1 < r[0] - q["janela_pt"] or rr.x0 > r[2] + q["janela_pt"] or rr.y1 < r[1] - q["janela_pt"] \
                    or rr.y0 > r[3] + q["janela_pt"]:
                continue
            for c in Q.caminhos(d):
                if len(c) >= 3:
                    cv2.fillPoly(m, [np.int32(np.round((c - (w0, h0)) * k))], 1)
    (ax, ay), (bx, by) = Q.p2q(r[0], r[1]), Q.p2q(r[2], r[3])
    cx, cy = ((ax + bx) / 2 - w0) * k, ((ay + by) / 2 - h0) * k
    if not hor:                                                    # tudo como deitado; no fim, volta
        m, cx, cy, ax, ay, bx, by = m.T, cy, cx, ay, ax, by, bx
    L = (bx - ax) * k
    pr = q["procura_m"] * Q.px_m * k
    xl0, xl1 = int(max(0, cx - L / 2 - pr)), int(max(1, cx - L / 2 + pr / 4))
    xr0, xr1 = int(min(m.shape[1] - 1, cx + L / 2 - pr / 4)), int(min(m.shape[1], cx + L / 2 + pr))
    lin_e, lin_d = m[:, xl0:xl1].any(axis=1), m[:, xr0:xr1].any(axis=1)
    # a faixa da parede só perto da espessura do vão (uma parede que chega de lado não a engrossa)
    e_ = (by - ay) * k / 2 + 0.05 * Q.px_m * k
    perto = np.zeros(m.shape[0], bool)
    perto[max(0, int(cy - e_)):int(cy + e_) + 1] = True
    lin_e, lin_d = lin_e & perto, lin_d & perto
    faixa = lin_e & lin_d if (lin_e & lin_d).any() else (lin_e | lin_d)
    linhas = np.nonzero(faixa)[0]
    if not len(linhas):
        return None
    # a faixa contínua mais perto do centro do vão
    cortes = np.split(linhas, np.nonzero(np.diff(linhas) > 1)[0] + 1)
    faixa = min(cortes, key=lambda g: min(abs(g[0] - cy), abs(g[-1] - cy), 0 if g[0] <= cy <= g[-1] else 1e9))
    t0, t1 = faixa[0], faixa[-1] + 1
    meio = m[t0 + (t1 - t0) // 4:t1 - (t1 - t0) // 4 or t1]
    col = meio.any(axis=0)
    esq = np.nonzero(col[:int(cx)])[0]
    dir_ = np.nonzero(col[int(cx):])[0]
    x0 = (esq[-1] + 1) if len(esq) else cx - L / 2
    x1 = (int(cx) + dir_[0]) if len(dir_) else cx + L / 2
    if abs((x1 - x0) - L) > 0.35 * max(L, 1):                      # sem as duas pontas claras: fica o vão aproximado
        x0, x1 = cx - L / 2, cx + L / 2
    caixa = (x0 / k, t0 / k, x1 / k, t1 / k)
    if not hor:
        caixa = (caixa[1], caixa[0], caixa[3], caixa[2])
    return caixa[0] + w0, caixa[1] + h0, caixa[2] + w0, caixa[3] + h0


def soleiras(Q, img):
    sys.path.insert(0, str(B.RAIZ / "_texturas"))
    from texturas import textura
    from retoque_terreo_casae import BEGE
    q = SOLEIRAS_F
    k = q["ss"]
    vaos = B.vaos_brancos(Q.chave)
    out = img.astype(np.float32)
    feitas = []
    for i, r in enumerate(vaos):
        cx_ = _soleira_no_pdf(Q, r)
        if cx_ is None:
            continue
        x0, y0, x1, y1 = cx_
        X0, Y0, X1, Y1 = int(np.floor(x0)) - 2, int(np.floor(y0)) - 2, int(np.ceil(x1)) + 2, int(np.ceil(y1)) + 2
        h, w = Y1 - Y0, X1 - X0
        mk = np.zeros((h * k, w * k), np.uint8)
        u0, v0, u1, v1 = (int(round((x0 - X0) * k)), int(round((y0 - Y0) * k)), int(round((x1 - X0) * k)),
                          int(round((y1 - Y0) * k)))
        mk[v0:v1, u0:u1] = 255
        fk = np.zeros_like(mk)
        e = max(1, int(round(q["linha_px"] * k)))
        if (x1 - x0) >= (y1 - y0):                                 # as faces da parede: os lados compridos
            fk[v0:v0 + e, u0:u1] = 255
            fk[v1 - e:v1, u0:u1] = 255
        else:
            fk[v0:v1, u0:u0 + e] = 255
            fk[v0:v1, u1 - e:u1] = 255
        al = cv2.resize(mk.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None]
        fl = cv2.resize(fk.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None]
        T = textura("bege_bahia", Q.px_m, h, w, semente=q["semente"] + i).astype(np.float32)
        T = (1 + q["forca"] * (T / T.reshape(-1, 3).mean(axis=0) - 1)) * np.float32(BEGE["tom"])
        reg = out[Y0:Y1, X0:X1]
        reg = reg * (1 - al) + T * al
        out[Y0:Y1, X0:X1] = reg * (1 - fl) + np.float32(q["linha"]) * fl
        feitas.append((x0, y0, x1, y1))
    print(f"    soleiras: {len(feitas)} de {len(vaos)} vãos brancos do PDF, nas faces das paredes, em Bege Bahia nítido")
    return np.clip(out, 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
# 5. As paredes pretas e os pilares (os redondos em cinza)
# Os muros na sequência das portas de correr da área de serviço descoberta (usuário, 22/10/26: "NA SEQUÊNCIA DAS PORTAS
# DE CORRER, EXISTE MURO (EM PRETO)"): no PDF, cada lateral tem a porta de correr no alto e, dela até o muro de divisa,
# um trecho fino da ARQ_ELEMENTOS FIXOS em branco, que saía como uma linha cinza na grama. É muro: entra em preto, na
# espessura do caixilho da porta (pt), do fim da folha até o muro de divisa.
# E10 (26/10/26: "Representar as paredes em planta com uma tonalidade de um cinza escuro e os pilares no preto"; o
# usuário escolheu o cinza 80): `paredes(..., cor=PAREDES_F["cinza"])`, planta a planta, com o OK dele; os pilares
# retangulares seguem no preto (`cor`).
PAREDES_F = {"cor": (8, 8, 8), "cinza": (80, 80, 80), "camadas": ("ARQ_PAREDE", "ARQ_ELEMENTOS FIXOS"),
             "pilar_redondo": {"cor": (128, 128, 130), "contorno": (62, 62, 64), "larg_px": 1.1},
             "muros_pt": {"Terreo": [(1609.25, 1884.96, 1613.78, 2009.68), (1903.93, 1884.96, 1908.46, 2009.68)]},
             # os brises da faixa de baixo do jardim do hall (as 11 lâminas giradas da ARQ_ELEMENTOS FIXOS nesta caixa):
             # em vez do preto das paredes, alumínio grafite com a aresta da luz mais clara, o contorno fino e a
             # sombra curta no travertino (usuário, 22/10/26: "OS BRISES BEM DESENHADOS")
             "brises": {"caixa_pt": {"Terreo": (2105.0, 1438.0, 2320.0, 1458.0)}, "cor": (66, 66, 68),
                        "contorno": (24, 24, 26), "contorno_px": 0.6, "luz": 0.18,
                        "sombra": {"dist_m": 0.04, "sig_m": 0.025, "forca": 0.35}},
             # o guarda-corpo de vidro em L da varanda da suíte master (usuário, 22/10/26: "FALTOU A REPRESENTAÇÃO DO
             # GUARDA-CORPO EM L DA VARANDA EM VIDRO"): no PDF, as lâminas brancas de 2 cm da ARQ_ELEMENTOS FIXOS na
             # borda do travertino (pt), que nenhuma etapa desenhava; entram como os vidros das esquadrias (o vidro
             # claro, as duas faces em linha fina, o brilho no meio), com 2,4 px no mínimo para aparecer, e a sombra curta.
             # Depois (usuário: "NO GUARDA CORPO, TEM UMA FALHA LOGO PERTO DA DOBRA, NA QUINA, E ESTÁ FALTANDO O FECHAMENTO
             # DESSE GUARDA CORPO NO LADO DIREITO"): entra a terceira lâmina do PDF, em pé à direita, da quina até a
             # parede (527,16 pt); cada lâmina passa `ponta_px` das pontas, para as quinas fecharem sem dente; e no lábio
             # do travertino por fora do vidro da esquerda (`labio_pt`, os 2,3 pt da laje além do vidro, da face de cima
             # do vidro até 25 pt abaixo da quina: em cima a legenda não tem o lábio, a grama encosta no vidro; mais
             # abaixo, junto ao deck, as juntas das tábuas não podem virar lábio), os px escuros da legenda junto à
             # quina (`labio_dif` abaixo da mediana da coluna) ficam no tom do lábio.
             "guarda_corpo": {"pt": {"Terreo": [(732.77, 489.75, 1054.22, 490.88), (732.77, 489.75, 733.91, 941.02),
                                                (1053.09, 489.75, 1054.22, 527.16)]},
                              "labio_pt": {"Terreo": [(730.51, 489.75, 732.77, 515.0)]}, "labio_dif": 40,
                              "ponta_px": 0.6,
                              "vidro": (226, 219, 206), "alfa": 0.95, "contorno": (96, 100, 104), "larg_min_px": 2.4,
                              "linha_px": 0.6, "brilho": 0.5, "sombra": 0.18}}


def brises_pdf(Q):
    cx = PAREDES_F["brises"]["caixa_pt"].get(Q.chave)
    if cx is None:
        return []
    return [d for d in Q.desenhos if d.get("layer") == "ARQ_ELEMENTOS FIXOS" and d["type"] in ("f", "fs")
            and d.get("fill") and max(d["fill"]) < 0.5 and len(d["items"]) == 4 and cx[0] <= d["rect"].x0
            and d["rect"].x1 <= cx[2] and cx[1] <= d["rect"].y0 and d["rect"].y1 <= cx[3]]


def brises(Q, img, ds):
    q, ss = PAREDES_F["brises"], 8
    out = img.astype(np.float32)
    s = q["sombra"]
    for d in ds:
        X0, Y0, X1, Y1 = ret_q(Q, d["rect"])
        X0, Y0, X1, Y1 = X0 - 4, Y0 - 4, X1 + 5, Y1 + 5
        w, h = X1 - X0, Y1 - Y0
        m = np.zeros((h * ss, w * ss), np.uint8)
        polys = [np.round((c - (X0, Y0)) * ss).astype(np.int32) for c in Q.caminhos(d) if len(c) >= 3]
        cv2.fillPoly(m, polys, 255)
        mf = m.astype(np.float32) / 255

        def reduzir(x):
            return cv2.resize(x.astype(np.float32), (w, h), interpolation=cv2.INTER_AREA)
        a = reduzir(mf)
        d_ = s["dist_m"] * Q.px_m * ss
        sb = reduzir(cv2.GaussianBlur(cv2.warpAffine(mf, np.float32([[1, 0, -d_], [0, 1, d_]]), (w * ss, h * ss)),
                                      (0, 0), s["sig_m"] * Q.px_m * ss)) * s["forca"]
        reg = out[Y0:Y1, X0:X1]
        reg *= (1 - sb * (1 - a))[..., None]
        # a aresta do lado da luz (em cima e à direita) um pouco mais clara
        luz = mf - cv2.warpAffine(mf, np.float32([[1, 0, -1.2 * ss], [0, 1, 1.2 * ss]]), (w * ss, h * ss))
        cor = np.float32(q["cor"]) * (1 + q["luz"] * reduzir(np.clip(luz, 0, 1)))[..., None]
        reg[:] = reg * (1 - a[..., None]) + cor * a[..., None]
        lt = max(1, int(round(q["contorno_px"] * ss)))
        anel = m & ~cv2.erode(m, np.ones((lt, lt), np.uint8))
        al = np.clip(reduzir(anel / 255.0) * 1.3, 0, 1)
        reg[:] = reg * (1 - al[..., None]) + np.float32(q["contorno"]) * al[..., None]
    return out


def guarda_corpo(Q, img):
    q, ss = PAREDES_F["guarda_corpo"], 8
    rs = q["pt"].get(Q.chave, [])
    out = img.astype(np.float32)
    for r in q["labio_pt"].get(Q.chave, []):                # o lábio do travertino por fora do vidro, sem falha
        X0, Y0, X1, Y1 = ret_q(Q, r)
        for x in range(X0, X1):
            col = out[Y0:Y1, x]
            lum = col.mean(axis=1)
            ruim = lum < np.median(lum) - q["labio_dif"]
            if ruim.any() and (~ruim).any():
                col[ruim] = np.median(col[~ruim], axis=0)
    for r in rs:
        (x0, y0), (x1, y1) = Q.p2q(r[0], r[1]), Q.p2q(r[2], r[3])
        deitado = x1 - x0 > y1 - y0
        if deitado and y1 - y0 < q["larg_min_px"]:
            c_ = (y0 + y1) / 2
            y0, y1 = c_ - q["larg_min_px"] / 2, c_ + q["larg_min_px"] / 2
        if not deitado and x1 - x0 < q["larg_min_px"]:
            c_ = (x0 + x1) / 2
            x0, x1 = c_ - q["larg_min_px"] / 2, c_ + q["larg_min_px"] / 2
        if deitado:                                          # as pontas passam um pouco, para as quinas fecharem
            x0, x1 = x0 - q["ponta_px"], x1 + q["ponta_px"]
        else:
            y0, y1 = y0 - q["ponta_px"], y1 + q["ponta_px"]
        X0, Y0, X1, Y1 = int(x0) - 3, int(y0) - 3, int(np.ceil(x1)) + 4, int(np.ceil(y1)) + 4
        w, h = X1 - X0, Y1 - Y0
        m = np.zeros((h * ss, w * ss), np.uint8)
        a0, b0, a1, b1 = [int(round(v * ss)) for v in (x0 - X0, y0 - Y0, x1 - X0, y1 - Y0)]
        cv2.rectangle(m, (a0, b0), (a1 - 1, b1 - 1), 255, -1)
        lt = max(1, int(round(q["linha_px"] * ss)))
        bordas = np.zeros_like(m)
        if deitado:
            bordas[b0:b0 + lt, a0:a1] = 255
            bordas[b1 - lt:b1, a0:a1] = 255
        else:
            bordas[b0:b1, a0:a0 + lt] = 255
            bordas[b0:b1, a1 - lt:a1] = 255

        def reduzir(x):
            return cv2.resize(x.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)
        av, ab = reduzir(m), reduzir(bordas)
        reg = out[Y0:Y1, X0:X1]
        sb = cv2.GaussianBlur(cv2.warpAffine(av, np.float32([[1, 0, -0.7], [0, 1, 0.7]]), (w, h)), (0, 0), 0.5)
        reg *= (1 - q["sombra"] * sb * (1 - av))[..., None]
        al = av[..., None] * q["alfa"]
        reg[:] = reg * (1 - al) + np.float32(q["vidro"]) * al
        reg[:] = reg * (1 - ab[..., None]) + np.float32(q["contorno"]) * ab[..., None]
        meio = np.zeros_like(m)                                  # o brilho do vidro, uma linha clara no meio
        if deitado:
            c_ = (b0 + b1) // 2
            meio[c_ - lt // 2:c_ + lt // 2 + 1, a0 + lt:a1 - lt] = 255
        else:
            c_ = (a0 + a1) // 2
            meio[b0 + lt:b1 - lt, c_ - lt // 2:c_ + lt // 2 + 1] = 255
        am = reduzir(meio)[..., None] * q["brilho"]
        reg[:] = reg * (1 - am) + 250 * am
    return out, len(rs)


def paredes(Q, img, cor=None):
    q = PAREDES_F
    bs = brises_pdf(Q)
    ids = {id(d) for d in bs}
    a = Q.preencher(lambda d: d.get("layer") in q["camadas"] and d.get("fill") and max(d["fill"]) < 0.5
                    and id(d) not in ids, ss=4)
    muros = q["muros_pt"].get(Q.chave, [])
    if muros:
        ss = 8
        m = np.zeros((Q.H * ss, Q.W * ss), np.uint8)
        for r in muros:
            (x0, y0), (x1, y1) = Q.p2q(r[0], r[1]), Q.p2q(r[2], r[3])
            cv2.rectangle(m, (round(x0 * ss), round(y0 * ss)), (round(x1 * ss) - 1, round(y1 * ss) - 1), 255, -1)
        a = np.maximum(a, cv2.resize(m, (Q.W, Q.H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255)
    out = img.astype(np.float32)
    out, ng = guarda_corpo(Q, out)                           # antes do preto: a ponta que encosta na parede fica sob ele
    out = out * (1 - a[..., None]) + np.float32(cor or q["cor"]) * a[..., None]
    # pilares: os redondos (usuário, 22/10/26: "EXISTEM DOIS PILARES REPRESENTADOS POR BOLAS. PRECISAMOS DEIXAR EM
    # CINZA PARA DESTACÁ-LOS"), em cinza médio com o contorno escuro fino; os retangulares, pretos como as paredes
    pr = q["pilar_redondo"]
    n = 0
    for d in Q.desenhos:
        if d.get("layer") != "EST_PILAR" or d["type"] not in ("f", "fs"):
            continue
        r = d["rect"]
        redondo = abs(r.width - r.height) < 1 and len(d["items"]) > 8
        (cx, cy), (ex, _) = Q.p2q((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2), Q.p2q(r.x1, (r.y0 + r.y1) / 2)
        ss = 8
        m = np.zeros((Q.H * 0 + 64 * ss, 64 * ss), np.uint8)
        rad = (ex - cx)
        X0, Y0 = int(cx) - 32, int(cy) - 32
        if redondo:
            cv2.circle(m, (round((cx - X0) * ss), round((cy - Y0) * ss)), round(rad * ss), 255, -1, cv2.LINE_AA)
            borda = np.zeros_like(m)
            cv2.circle(borda, (round((cx - X0) * ss), round((cy - Y0) * ss)), round((rad - pr["larg_px"] / 2) * ss), 255,
                       max(1, round(pr["larg_px"] * ss)), cv2.LINE_AA)
            af = cv2.resize(m, (64, 64), interpolation=cv2.INTER_AREA).astype(np.float32)[..., None] / 255
            ab = cv2.resize(borda, (64, 64), interpolation=cv2.INTER_AREA).astype(np.float32)[..., None] / 255
            reg = out[Y0:Y0 + 64, X0:X0 + 64]
            reg = reg * (1 - af) + np.float32(pr["cor"]) * af
            out[Y0:Y0 + 64, X0:X0 + 64] = reg * (1 - ab) + np.float32(pr["contorno"]) * ab
        else:
            for c in Q.caminhos(d):
                cv2.fillPoly(m, [np.int32(np.round((c - (X0, Y0)) * ss))], 255)
            af = cv2.resize(m, (64, 64), interpolation=cv2.INTER_AREA).astype(np.float32)[..., None] / 255
            out[Y0:Y0 + 64, X0:X0 + 64] = out[Y0:Y0 + 64, X0:X0 + 64] * (1 - af) + np.float32(q["cor"]) * af
        n += 1
    out = brises(Q, out, bs)
    print(f"    paredes {'em cinza ' + str(cor[0]) if cor else 'pretas'} no contorno do PDF; {len(muros)} muros na sequência de portas de correr; {n} pilares (os "
          f"redondos em cinza, com o contorno fino); {len(bs)} brises em grafite; {ng} trechos de guarda-corpo de vidro")
    return np.clip(out, 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
# 6. Os carros (R12): o mesmo modelo prata, agora pousado no quadro da prancha, com a borda limpa e a sombra curta
def carros(Q, img, M):
    """M: o afim render (2000 px) -> quadro. O modelo é o carro do meio do render (como em `ajustes_casab.carros_b`)."""
    from scipy import ndimage
    q = B.CARROS_B
    r = dict(AJ.CARROS_A["r12"], modelo=q["modelo"], centros_pdf=q["centros_pdf"])
    ap = cv2.imread(str(B.CASA_B / Q.q["aprovada"]))
    wx0, wy0, wx1, wy1 = q["janela"]
    reg = ap[wy0:wy1, wx0:wx1].astype(np.float32)
    car = (reg[..., 2] - reg[..., 0]) < q["neutro"]
    m = cv2.morphologyEx(car.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((q["fecho"],) * 2, np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    ids = sorted([i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= q["area_min"]
                  and st[i, cv2.CC_STAT_WIDTH] >= 40 and st[i, cv2.CC_STAT_HEIGHT] >= 100], key=lambda i: cen[i, 0])
    sil = ndimage.binary_fill_holes(lab == ids[q["modelo"]])
    sil = cv2.erode(sil.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)     # sem o anel do piso antigo
    qa = AJ.CARROS_A
    Y = reg.mean(axis=2)
    lanterna = (reg[..., 2] - reg[..., 0] > qa["lanterna"][0]) & (reg[..., 2] > qa["lanterna"][1]) & \
        (reg[..., 2] - reg[..., 1] > qa["lanterna"][0])
    pq, alvo = r["quantis"]
    fonte = np.percentile(Y[sil & ~lanterna], pq)
    Yn = np.interp(Y, fonte, alvo)
    prata = np.where((sil & ~lanterna)[..., None], Yn[..., None] * np.float32(r["tom"]), reg)
    ys, xs = np.nonzero(sil)
    y0, y1 = ys.min(), ys.max() + 1
    comp = y1 - y0
    f0, f1 = r["faixa_largura"]
    larguras = sil[int(y0 + f0 * comp):int(y0 + f1 * comp)].sum(axis=1)
    larg = float(np.median(larguras[larguras > 0]))
    sx, sy = r["largura_m"] * Q.px_m / larg, r["comprimento_m"] * Q.px_m / comp
    cx, cy = float(xs.mean()), (y0 + y1) / 2
    alfa0 = cv2.GaussianBlur(sil.astype(np.float32), (0, 0), 0.6)
    out = img.astype(np.float32)
    s = PECAS["sombra"]
    for px_, py_ in r["centros_pdf"]:
        tx, ty = Q.p2q(px_, py_)
        Mw = np.float32([[sx, 0, tx - sx * cx], [0, sy, ty - sy * cy]])
        a = cv2.warpAffine(alfa0, Mw, (Q.W, Q.H), flags=cv2.INTER_LINEAR)
        c = cv2.warpAffine(prata, Mw, (Q.W, Q.H), flags=cv2.INTER_CUBIC)
        c = cv2.addWeighted(c, 1.5, cv2.GaussianBlur(c, (0, 0), 1.2), -0.5, 0)     # o detalhe ampliado, mais firme
        d_ = 0.08 * Q.px_m
        Ms = np.float32([[1, 0, -d_], [0, 1, d_]])
        sb = cv2.GaussianBlur(cv2.warpAffine(a, Ms, (Q.W, Q.H)), (0, 0), 0.06 * Q.px_m) * (1 - a) * 0.38
        out *= (1 - sb)[..., None]
        out = out * (1 - a[..., None]) + c * a[..., None]
    print(f"    garagem (R12): {len(r['centros_pdf'])} carros prata de {r['comprimento_m']:.2f} x {r['largura_m']:.2f} m "
          f"no quadro da prancha, com a borda limpa e a sombra curta")
    return np.clip(out, 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
# 7. A vegetação: as mesmas plantas da biblioteca nos mesmos lugares, desenhadas na escala da prancha
def plantas_do_gramado():
    """As plantas que `ajustes_casaa.vegetacao_a` pôs no gramado (no render de 2000 px): refaz o mesmo sorteio (mesma
    semente, mesma ordem) e devolve (x, y, nome, d_m * escala) de cada uma, as menores primeiro."""
    from retoque_terreo_casae import VEGETACAO, sprite_referencia
    ve, q = VEGETACAO, AJ.VEG_A
    _, p2r = AJ.pdf_pavimento("Terreo")
    forma = None
    (a, b), (c, d) = p2r(0, 0), p2r(56.69, 0)
    px_m = float(np.hypot(c - a, d - b))
    aprovada = cv2.imread(str(AJ.APROVADAS["Terreo"]))
    forma = aprovada.shape[:2]
    gramado, _, planta, _, _, _ = AJ.gramado_plantas(aprovada)
    verde = gramado.copy()
    n, lab, st, _ = cv2.connectedComponentsWithStats((planta & verde).astype(np.uint8), 8)
    planta = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= q["mancha_min"]])
    dv = cv2.distanceTransform(verde.astype(np.uint8), cv2.DIST_L2, 5)
    rng = np.random.default_rng(ve["semente"])
    n, lab = cv2.connectedComponents(planta.astype(np.uint8))
    postas = []
    for i in range(1, n):
        m = lab == i
        ocup = np.zeros(forma, np.uint8)
        for nome, dm, chance in ve["catalogo"]:
            r = dm * px_m / 2
            cand = np.argwhere(m & (dv >= ve["folga_copa"] * r))
            rng.shuffle(cand)
            for y, x in cand:
                if ocup[y, x] or rng.random() > chance:
                    continue
                if any(np.hypot(x - px, y - py) < ve["afastar"] * (r + pr) for px, py, pr, _ in postas):
                    continue
                postas.append((x, y, r, nome))
                cv2.circle(ocup, (int(x), int(y)), int(r * 0.8), 1, -1)
    res = []
    dms = {}
    for x, y, r, nome in sorted(postas, key=lambda t: t[2]):
        if nome not in dms:
            dms[nome] = sprite_referencia(nome, px_m)[2]
        esc = 2 * r / (dms[nome] * px_m) * float(rng.uniform(*ve["escala"]))
        res.append((float(x), float(y), nome, dms[nome] * esc))
    return res


# Os dois jardins (usuário, 22/10/26). O de inverno: "TEMOS VIDRO EM CIMA E EMBAIXO E PORTAS DE VIDRO NA LATERAL ESQUERDA.
# NOTE QUE O PISO EM TRAVERTINO ESTÁ PRESENTE NAS BORDAS. SEM CORES QUENTES, APENAS VERDE"; o do hall: "VAMOS MELHORAR
# AS BORDAS DO TRAVERTINO [...] NA PARTE DE BAIXO DO JARDIM, PRECISAMOS DO TRAVERTINO E OS BRISES BEM DESENHADOS".
# - Jardim de inverno (refeito; usuário: "NÃO HÁ ESSA MOLDURA DE TRAVERTINO. É SOMENTE NA LATERAL ESQUERDA. TEM FOLHAS
#   DE VIDRO EM CIMA E EMBAIXO. SENDO EM CIMA RENTE AO VINILICO. NA LATERAL ESQUERDA, TEMOS AS DUAS FOLHAS DE VIDRO DE
#   CORRER E DEPOIS TRAVERTINO, JÁ PROXIMO AO BRAÇO DO SOFÁ E RENTE AO TAPETE"): o canteiro é a sala inteira, sem borda,
#   do vidro de cima (o da ARQ_PAREDE, encostado no vinílico) ao vidro de baixo e da parede da direita às folhas de
#   correr (a de dentro até 1042,5 pt, a de fora daí para baixo), e as plantas não passam dele. O travertino fica só do
#   lado de fora das portas, na sala, entre elas, o braço do sofá e o tapete (o piso da legenda, como já estava).
# - Jardim do hall: o canteiro no retângulo exato entre a parede, o vidro e a linha do travertino (antes, a mancha do
#   verde da legenda, com as plantas saindo dela), e a faixa de baixo, até a pedra portuguesa, em travertino, sob os
#   brises (que a etapa `paredes` desenha).
# Nos dois, só plantas verdes da biblioteca (sem a planta com flores nem a comigo-ninguém-pode, de miolo creme), a
# forração mais fechada e o chão do canteiro em verde-escuro, para não aparecer terra marrom.
JARDINS_F = {
    "travertino": {"forca": 1.6, "ref_m": 0.6},
    "terra": (38, 54, 40), "terra_ruido": 0.10,
    "forracao": {"nomes": ["arbusto_1", "arbusto_2", "arbusto_3"], "d_m": (0.40, 0.55), "passo_m": 0.32, "tom": 0.92},
    # a faixa do hall logo abaixo do vidro de baixo: dois borrões escuros do render, sem nada no PDF, voltam a travertino
    "limpar_pt": [(1816.18, 1122.6, 2006.1, 1132.0)],
    # o canteiro: a sala, entre a face de baixo do vidro de cima e a de cima do vidro de baixo, e as faixas até as
    # folhas de correr (a de dentro, de 968,8 a 1042,5 pt; a de fora, de 1042,5 a 1111,67 pt); as plantas, na primeira
    "inverno": {"canteiro_pt": [(1816.18, 925.15, 2006.1, 1115.07), (1813.34, 968.8, 1816.18, 1111.67),
                                (1810.51, 1042.5, 1813.34, 1111.67)], "transbordo_m": 0.0, "semente": 21,
                "plantas": [("costela_de_adao", 0.95, (0.25, 0.25), 0), ("planta_folhas_largas", 0.90, (0.75, 0.22), 90),
                            ("palmeira_2", 1.30, (0.50, 0.52), 0), ("planta_folhas_largas", 0.85, (0.24, 0.78), 180),
                            ("costela_de_adao", 0.90, (0.77, 0.80), 270), ("palmeira_3", 0.80, (0.52, 0.88), 0),
                            ("arbusto_2", 0.75, (0.86, 0.50), 90), ("arbusto_1", 0.75, (0.14, 0.52), 0)]},
    "hall": {"canteiro_pt": (2108.15, 1360.55, 2289.56, 1439.92), "faixa_pt": (2108.15, 1439.92, 2316.6, 1450.9),
             "transbordo_m": 0.0, "semente": 23,
             "plantas": [("costela_de_adao", 0.85, (0.14, 0.45), 0), ("planta_folhas_largas", 0.80, (0.40, 0.40), 90),
                         ("palmeira_3", 0.80, (0.66, 0.50), 0), ("costela_de_adao", 0.75, (0.88, 0.42), 180),
                         ("arbusto_2", 0.60, (0.28, 0.72), 0), ("arbusto_1", 0.55, (0.78, 0.74), 90)]},
}


def ret_aa_q(Q, r, ss=8):
    """O retângulo r (pt) no quadro, com antialias (0 a 1)."""
    (x0, y0), (x1, y1) = Q.p2q(r[0], r[1]), Q.p2q(r[2], r[3])
    m = np.zeros((Q.H * ss, Q.W * ss), np.uint8)
    cv2.rectangle(m, (round(x0 * ss), round(y0 * ss)), (round(x1 * ss) - 1, round(y1 * ss) - 1), 255, -1)
    return cv2.resize(m, (Q.W, Q.H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255


def travertino_em(Q, img, a, semente, ref_pt=None):
    """O travertino da biblioteca em `a` (0 a 1), no tom do travertino da legenda em volta (a mediana dele a até
    `ref_m`): ali dentro o render tinha plantas, então a luz do lugar não serve. Com `ref_pt` (retângulo em pt), o tom
    é a mediana da imagem ali (quando o travertino da legenda em volta é outra coisa, como o jardim de inverno)."""
    sys.path.insert(0, str(B.RAIZ / "_texturas"))
    from texturas import textura
    q = JARDINS_F["travertino"]
    m = a > 0.01
    ys, xs = np.nonzero(m)
    y0, x0, y1, x1 = ys.min(), xs.min(), ys.max() + 1, xs.max() + 1
    if ref_pt is not None:
        ref = ret_aa_q(Q, ref_pt) > 0.99
    else:
        k = 2 * int(q["ref_m"] * Q.px_m) + 1
        trav = Q.cor([c for n, cs, *_ in PISOS["Terreo"] if n == "travertino" for c in cs])
        ref = trav & ~m & cv2.dilate(m.astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool)
    L = np.median(img[ref].reshape(-1, 3), axis=0).astype(np.float32)
    T = textura("travertino", Q.px_m, y1 - y0, x1 - x0, semente=semente).astype(np.float32)
    det = cv2.GaussianBlur(T, (0, 0), 0.6) / np.maximum(cv2.GaussianBlur(T, (0, 0), 3.0 * Q.px_m), 1)
    out = img.astype(np.float32)
    al = a[y0:y1, x0:x1, None]
    out[y0:y1, x0:x1] = out[y0:y1, x0:x1] * (1 - al) + L * (1 + q["forca"] * (det - 1)) * al
    return out


def alfa_canteiros(Q):
    """Os dois jardins de `JARDINS_F` (0 a 1, no quadro): o de inverno, a sala inteira até os vidros e as folhas de
    correr, e o do hall."""
    q = JARDINS_F
    return np.max([ret_aa_q(Q, r) for r in q["inverno"]["canteiro_pt"] + [q["hall"]["canteiro_pt"]]], axis=0)


# O que volta como estava depois do espelho das esquadrias, além dos canteiros (pt). Usuário, 22/10/26, sobre o sofá do
# living junto às portas de correr do jardim de inverno: "TEM DUAS LINHAS EM DESTAQUE. UMA DELAS SERIA UMA LINHA SUAVE
# DO BRAÇO DO SOFÁ, QUE TERMINA ANTES. E A LINHA DA DIREITA NÃO EXISTE": a faixa do espelho das folhas de correr
# (~5 px de cada lado) pegava a borda do sofá, a 5 px da porta, e a copiava junto à porta (a linha da direita), levava
# a linha de baixo do braço até a porta e apagava o fim da borda junto à folha de baixo. Volta a faixa entre o sofá e a
# porta: até a face da porta (1807,67 pt) junto à folha de fora (de 1037,97 pt para baixo) e até 1808,6 pt em cima,
# onde o trilho de fora está vazio (o piso segue até a folha de dentro).
# E a faixa entre a borda do sofá (1802,8 pt) e a porta, da parede ao pé do sofá, em travertino, como no PDF ("DEPOIS
# TRAVERTINO, JÁ PROXIMO AO BRAÇO DO SOFÁ"): o render deixava ali o tecido do sofá, que parecia ir até a porta. O tom
# vem do travertino logo abaixo, entre o tapete e a porta (`ref_pt`); o da legenda em volta é o jardim de inverno.
# Também a faixa logo abaixo da folha aberta da porta da suíte 3 (usuário: "TEM UM ERRO NESSA PORTA"): o espelho da
# folha (911,9 a 914,1 pt) pegava o topo do guarda-roupa, 7 px abaixo, e o copiava sob a folha (o bege com a borda ocre).
# Começa a 0,6 pt da face do batente (2108,1 pt): a coluna dele é a do batente que as esquadrias redesenham.
ESQUADRIAS_F = {"de_volta_pt": {"Terreo": [(1795.0, 929.68, 1808.6, 1037.97), (1795.0, 1037.97, 1807.67, 1113.94),
                                           (2108.7, 914.85, 2159.2, 921.0)]},
                "travertino_pt": {"Terreo": [(1803.85, 929.68, 1808.6, 1037.97), (1803.85, 1037.97, 1807.67, 1052.0)]},
                "ref_pt": {"Terreo": (1793.0, 1058.0, 1806.5, 1108.0)}}


def esquadrias_terreo(Q, img):
    """As esquadrias da final (`ondas_fora` e o espelho das ajustes) e, por cima, os canteiros e as faixas de
    `ESQUADRIAS_F` como estavam: o espelho da faixa de cada vidro (`esquadria_limpar`) troca o px escuro de um lado
    pelo do outro (para não copiar parede preta), e nas folhagens escuras junto ao vidro isso trazia o vinílico e o
    travertino para dentro do jardim, em pintas; junto ao sofá do living, copiava a borda dele. Os vidros e as folhas
    ficam fora dessas áreas, então nada deles se perde."""
    out = B.esquadrias_final(ondas_fora(Q, img), Q.chave, Q.pg, Q.p2q, Q.px_m)
    mudou = np.abs(out.astype(np.int16) - img.astype(np.int16)).max(axis=2) > 12
    ac = alfa_canteiros(Q)
    rs = ESQUADRIAS_F["de_volta_pt"].get(Q.chave, [])
    af = np.max([ret_aa_q(Q, r) for r in rs], axis=0) if rs else np.zeros_like(ac)
    print(f"    canteiros: {int((mudou & (ac > 0.5)).sum())} px que o espelho dos vidros mudou dentro dos jardins voltam "
          f"ao que eram; junto às portas de correr do jardim de inverno e sob a folha da porta da suíte 3, "
          f"{int((mudou & (af > 0.5)).sum())} px (a borda do sofá e o topo do guarda-roupa copiados)")
    a = np.maximum(ac, af)[..., None]
    out = out * (1 - a) + img.astype(np.float32) * a
    rs = ESQUADRIAS_F["travertino_pt"].get(Q.chave, [])
    if rs:
        out = travertino_em(Q, out, np.max([ret_aa_q(Q, r) for r in rs], axis=0), 760,
                            ref_pt=ESQUADRIAS_F["ref_pt"][Q.chave])
        print("    a faixa entre o sofá do living e as portas de correr do jardim de inverno em travertino")
    return np.clip(out, 0, 255).astype(np.uint8)


def jardins(Q, img):
    q = JARDINS_F
    out = img.astype(np.float32)
    comum = {"terra": q["terra"], "terra_ruido": q["terra_ruido"], "forracao": q["forracao"]}
    # o jardim de inverno: o canteiro na sala inteira, dos vidros às folhas de correr, sem borda de travertino
    ji = q["inverno"]
    for i, r in enumerate(q["limpar_pt"]):
        out = travertino_em(Q, out, ret_aa_q(Q, r), 750 + i)
    a_ji = np.max([ret_aa_q(Q, r) for r in ji["canteiro_pt"]], axis=0)
    # o jardim do hall: a faixa dos brises em travertino; o canteiro no retângulo do PDF
    jh = q["hall"]
    out = travertino_em(Q, out, ret_aa_q(Q, jh["faixa_pt"]), 742)
    out = np.clip(out, 0, 255).astype(np.uint8)
    with em_quadro(Q):
        for nome, a, r, cfg in (("jardim de inverno", a_ji, ji["canteiro_pt"][0], ji),
                                ("jardim de 4,62 m² do hall", ret_aa_q(Q, jh["canteiro_pt"]), jh["canteiro_pt"], jh)):
            x0, y0, x1, y1 = ret_q(Q, r)
            out = B.canteiro(out, a, (x0, y0, x1, y1), dict(comum, plantas=cfg["plantas"],
                                                           transbordo_m=cfg["transbordo_m"], semente=cfg["semente"]),
                             Q.px_m, nome)
    print("    jardins: o de inverno na sala inteira, dos vidros às folhas de correr, sem borda de travertino; "
          "a faixa dos brises do jardim do hall em travertino; só plantas verdes")
    return out


def vegetacao(Q, img, M):
    import json as _json
    from retoque_terreo_casae import sprite_referencia, pousar_planta
    out = img.astype(np.float32)
    sombra = _json.loads((B.RAIZ / "_texturas" / "texturas.json").read_text())["vegetacao"]["sombra"]
    verde = Q.cor([BORDAS_GRAMA], tol=10)
    fundo = out.copy()
    cache = {}
    plantas = plantas_do_gramado()
    for x, y, nome, d_m in plantas:
        X, Y = M @ np.array([x, y, 1.0])
        if nome not in cache:
            cache[nome] = sprite_referencia(nome, Q.px_m)
        cor, a_, dm = cache[nome]
        esc = d_m / dm
        cor_e = cv2.resize(cor, None, fx=esc, fy=esc, interpolation=cv2.INTER_AREA if esc < 1 else cv2.INTER_CUBIC)
        a_e = np.clip(cv2.resize(a_, None, fx=esc, fy=esc, interpolation=cv2.INTER_AREA if esc < 1 else cv2.INTER_CUBIC),
                      0, 1)
        cor_e = np.clip(cv2.addWeighted(cor_e, 1.6, cv2.GaussianBlur(cor_e, (0, 0), 1.4), -0.6, 0), 0, 255)
        pousar_planta(fundo, cor_e, a_e, X, Y, d_m * Q.px_m, sombra)
    al = cv2.GaussianBlur(verde.astype(np.float32), (0, 0), 0.6)[..., None]
    out = out * (1 - al) + fundo * al                       # a copa e a sombra só no gramado
    print(f"    vegetação do gramado: {len(plantas)} plantas da biblioteca, nos mesmos lugares, na escala da prancha")
    out = np.clip(out, 0, 255).astype(np.uint8)
    # os canteiros: a floreira, pela rotina dos ajustes, e os dois jardins (`jardins`), no quadro
    with em_quadro(Q):
        out = B.floreira(out)
    return jardins(Q, out)


BORDAS_GRAMA = (80, 145, 110)


# ----------------------------------------------------------------------------------------------------------------------
# 8. As escadas (R14), as projeções, o chuveiro do deck e o banco do deck
# Os degraus em Bege Bahia (usuário, 22/10/26: "E OS DEGRAUS EM PEDRA BEGE BAHIA NA LATERAL ESQUERDA DA IMAGEM???"): as
# duas escadas externas da esquerda (a de 6 degraus, da pedra grande para a ducha, e a de 9, da varanda para o deck em L),
# nos degraus exatos do PDF (os preenchimentos da ARQ_ESCADAS E RAMPAS), na foto do Bege Bahia da biblioteca, no tom e no
# contraste dela (regra da seção 18); por cima, as linhas da R14 (bocéis, sombra curta e o triângulo). Sai a mediana de
# antes (`escadas_b`), que limpava os degraus do motor e borrava a pedra.
DEGRAUS_F = {"pedra": "bege_bahia", "semente": 760}


def degraus_bege(Q, img, escadas):
    sys.path.insert(0, str(B.RAIZ / "_texturas"))
    from texturas import textura
    from retoque_terreo_casae import escada_linhas
    a = Q.preencher(lambda d: d.get("layer") == "ARQ_ESCADAS E RAMPAS" and d.get("fill"), fs=False)
    out = img.astype(np.float32)
    for k, e in enumerate(escadas):
        x0, y0, x1, y1 = ret_q(Q, e["pdf"])
        x0, y0, x1, y1 = x0 - 2, y0 - 2, x1 + 2, y1 + 2
        al = a[y0:y1, x0:x1, None]
        tex = textura(DEGRAUS_F["pedra"], Q.px_m, y1 - y0, x1 - x0, semente=DEGRAUS_F["semente"] + k).astype(np.float32)
        out[y0:y1, x0:x1] = out[y0:y1, x0:x1] * (1 - al) + tex * al
    out = np.clip(out, 0, 255).astype(np.uint8)
    for e in escadas:
        out = escada_linhas(out, None, e, p2r=Q.p2q)
    print(f"    {len(escadas)} escada(s) nos degraus do PDF em Bege Bahia, com as linhas da R14")
    return out


# As escadas sem linhas (E3, E8; usuário, 26/10/26, no Subsolo da Casa A: "não precisa constar linhas, mas sim sombras
# denotando que o sentido é de subida"; E3: "Colocar o sentido nas escadas (S / D), em vez de triângulo"): os degraus do
# PDF em Bege Bahia, como em `degraus_bege`, sem os bocéis da R14 nem o triângulo, marcados pelo sombreamento das escadas
# aprovadas da Casa A: cada degrau um pouco mais claro que o de baixo (`tom`, do 1º, do lado do `inicio`, ao último) e a
# sombra curta do espelho do de cima no de baixo (`espelho`: força e alcance em px), mais a do 1º degrau no piso de onde
# ela sobe (`piso`). A letra do PDF (S ou D) em Inter SemiBold, cinza quase preto, centrada no 1º degrau quando a origem
# do texto do PDF cai fora da escada (como no Térreo da Casa A).
ESCADA_SOMBRA = {"tom": (0.84, 1.0), "tom_degrau": 0.02, "espelho": (0.34, 2.4), "piso": (0.30, 2.6), "semente": 761}
LETRA_F = {"fonte": "Inter-SemiBold.otf", "corpo_px": 17, "cor": (45, 45, 45)}


def letra(Q, out, texto, centro_q):
    """A letra do sentido da escada, centrada num ponto do quadro (px)."""
    from PIL import Image, ImageDraw, ImageFont
    from rodape_entrega import FONTES
    q = LETRA_F
    fonte = ImageFont.truetype(str(FONTES / q["fonte"]), q["corpo_px"] * 4)
    ox, oy = centro_q
    W = H = q["corpo_px"] * 3
    X0, Y0 = int(ox) - W // 2, int(oy) - H // 2
    t = Image.new("L", (W * 4, H * 4), 0)
    ImageDraw.Draw(t).text(((ox - X0) * 4, (oy - Y0) * 4), texto, font=fonte, fill=255, anchor="mm")
    a = np.asarray(t.resize((W, H), Image.LANCZOS), np.float32)[..., None] / 255
    reg = out[Y0:Y0 + H, X0:X0 + W].astype(np.float32)
    out[Y0:Y0 + H, X0:X0 + W] = np.clip(reg * (1 - a) + np.float32(q["cor"]) * a, 0, 255).astype(np.uint8)
    return out


def escada_sombreada(Q, img, e, texto):
    sys.path.insert(0, str(B.RAIZ / "_texturas"))
    from texturas import textura
    q = ESCADA_SOMBRA
    pt_px = Q.px_m / 56.69
    a = Q.preencher(lambda d: d.get("layer") == "ARQ_ESCADAS E RAMPAS" and d.get("fill"), fs=False)
    ex0, ey0, ex1, ey1 = e["pdf"]
    x0, y0, x1, y1 = ret_q(Q, e["pdf"])
    x0, y0, x1, y1 = x0 - 2, y0 - 2, x1 + 2, y1 + 2
    al = a[y0:y1, x0:x1]
    h, w = al.shape
    tex = textura(DEGRAUS_F["pedra"], Q.px_m, h, w, semente=DEGRAUS_F["semente"]).astype(np.float32)
    # os degraus pelos bocéis do PDF, do 1º (do lado do `inicio`) ao último; X em pt de cada px
    (ax, _), (bx, _) = Q.p2q(0, 0), Q.p2q(100, 0)
    X = (np.arange(x0, x1) + 0.5 - ax) / ((bx - ax) / 100)
    bordas = [ex0] + list(e["bocels"]) + [ex1]
    k = np.clip(np.searchsorted(bordas, X) - 1, 0, len(bordas) - 2)
    n = len(bordas) - 1
    direita = e["inicio"] == "direita"
    i = (n - 1 - k) if direita else k                                      # 0 = o 1º degrau
    rng = np.random.default_rng(q["semente"])
    tons = 1 + rng.uniform(-q["tom_degrau"], q["tom_degrau"], n)
    t0, t1 = q["tom"]
    f = (t0 + (t1 - t0) * i / max(n - 1, 1)) * tons[i]
    fs, alc = q["espelho"]
    esp = np.array(bordas)[k if direita else k + 1]                        # o espelho do degrau de cima
    dist = ((X - esp) if direita else (esp - X)) * pt_px
    f = f * np.where(i < n - 1, 1 - fs * np.exp(-np.maximum(dist, 0) / alc), 1.0)
    out = img.astype(np.float32)
    reg = out[y0:y1, x0:x1]
    # a sombra do espelho do 1º degrau no piso de onde a escada sobe
    fp, ap = q["piso"]
    xb = ex1 if direita else ex0
    dp = ((X - xb) if direita else (xb - X)) * pt_px
    sp = np.where(dp > 0, fp * np.exp(-dp / ap), 0.0)[None, :]
    linhas = (np.arange(y0, y1) + 0.5 >= Q.p2q(0, ey0)[1]) & (np.arange(y0, y1) + 0.5 <= Q.p2q(0, ey1)[1])
    reg *= (1 - sp * linhas[:, None] * (1 - al))[..., None]
    reg[:] = reg * (1 - al[..., None]) + tex * f[None, :, None] * al[..., None]
    out = np.clip(out, 0, 255).astype(np.uint8)
    b = bordas[-2:] if direita else bordas[:2]
    out = letra(Q, out, texto, Q.p2q((b[0] + b[1]) / 2, (ey0 + ey1) / 2))
    print(f"    escada {e['nome']}: {n} degraus em Bege Bahia, sem linhas e sem triângulo, com o sombreamento de "
          f"subida; o {texto} do PDF no 1º degrau")
    return out


# Os boxes (E5: "Representar os boxes."; R10: o vidro contínuo e visível, nunca só o traço): cada vidro de box do PDF
# (`vidros_box`) fora do granito (no granito, a faixa cinza-clara de `boxes_granito`) como as folhas dos boxes da Casa A:
# a faixa de vidro na largura do PDF, com as duas faces em linha fina e a sombra curta (luz do alto à direita). São
# vidros fixos, sem o trilho de correr.
BOXES_VIDRO = {"vidro": (218, 214, 204), "face": (104, 108, 112), "face_px": 0.45, "larg_min_px": 2.4, "sombra": 0.20,
               "ss": 8}


def boxes_vidro(Q, img):
    q, ss = BOXES_VIDRO, BOXES_VIDRO["ss"]
    gran = Q.cor([BOXES_F["granito"]], tol=8)
    out = img.astype(np.float32)
    n = 0
    for x0, y0, x1, y1, hor in vidros_box(Q):
        a0, b0, a1, b1 = ret_q(Q, (x0, y0, x1, y1))
        if gran[b0 - 4:b1 + 5, a0 - 4:a1 + 5].mean() >= BOXES_F["granito_min"]:
            continue
        (u0, v0), (u1, v1) = Q.p2q(x0, y0), Q.p2q(x1, y1)
        if hor and v1 - v0 < q["larg_min_px"]:
            v0, v1 = (v0 + v1 - q["larg_min_px"]) / 2, (v0 + v1 + q["larg_min_px"]) / 2
        if not hor and u1 - u0 < q["larg_min_px"]:
            u0, u1 = (u0 + u1 - q["larg_min_px"]) / 2, (u0 + u1 + q["larg_min_px"]) / 2
        X0, Y0, X1, Y1 = int(u0) - 4, int(v0) - 4, int(np.ceil(u1)) + 5, int(np.ceil(v1)) + 5
        w, h = X1 - X0, Y1 - Y0
        m = np.zeros((h * ss, w * ss), np.uint8)
        c0, r0, c1, r1 = [int(round(v * ss)) for v in (u0 - X0, v0 - Y0, u1 - X0, v1 - Y0)]
        cv2.rectangle(m, (c0, r0), (c1 - 1, r1 - 1), 255, -1)
        lt = max(1, int(round(q["face_px"] * ss)))
        faces = np.zeros_like(m)
        if hor:
            faces[r0:r0 + lt, c0:c1] = 255
            faces[r1 - lt:r1, c0:c1] = 255
        else:
            faces[r0:r1, c0:c0 + lt] = 255
            faces[r0:r1, c1 - lt:c1] = 255

        def reduzir(x):
            return cv2.resize(x.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)
        av, af = reduzir(m), reduzir(faces)
        reg = out[Y0:Y1, X0:X1]
        sb = cv2.GaussianBlur(cv2.warpAffine(av, np.float32([[1, 0, -0.9], [0, 1, 0.9]]), (w, h)), (0, 0), 0.8)
        reg *= (1 - q["sombra"] * sb * (1 - av))[..., None]
        reg[:] = reg * (1 - av[..., None]) + np.float32(q["vidro"]) * av[..., None]
        reg[:] = reg * (1 - af[..., None]) + np.float32(q["face"]) * af[..., None]
        n += 1
    print(f"    boxes: {n} vidros contínuos do PDF, com as faces finas e a sombra curta")
    return np.clip(out, 0, 255).astype(np.uint8)


# A pedra grande e as lajes que descem dela (usuário, 22/10/26, apontando a área à esquerda do deck: "AQUI SÃO
# DEGRAUS"): no PDF são 7 blocos retangulares de pedra (ARQ_CONTRAPISO, os de 4 lados nesta caixa) sobrepostos em
# cascata: o patamar no alto da escada de 6 degraus e as 6 lajes em volta dele. A legenda os dava como travertino, e a
# imagem saía um piso liso só. Agora cada bloco é uma peça de Bege Bahia (a foto da biblioteca, uma semente e um tom
# levemente diferente por peça), como os degraus das escadas, na ordem de pintura do PDF: o bloco de cima leva a linha
# fina do bocel no contorno e deixa a sombra curta para baixo e à esquerda (a luz do alto à direita) no de baixo e na
# grama. Roda antes da escada de 6 degraus, que começa sobre a borda do patamar.
# E o triângulo da R14 descendo do deck para a laje da direita, a que sai da pedra grande para a grama junto ao deck
# (usuário, 22/10/26: "ADICIONE O TRIANGULO DESCENDO NESSE DEGRAU"; depois, com o lugar marcado na imagem: "O
# TRIÂNGULO É ONDE EU APONTEI"): no deck, com a ponta junto à borda direita da laje (447 pt), a 1097,7 pt de altura,
# apontando para ela (para a esquerda), no tamanho e na cor dos triângulos das escadas
# (`retoque_terreo_casae.ESCADA_LINHAS["triangulo"]`). Cada um: (x, y da ponta, em pt; o sentido para onde aponta).
BLOCOS_F = {"caixa_pt": (150.0, 780.0, 520.0, 1170.0), "pedra": "bege_bahia", "semente": 780, "ss": 4, "tom": 0.025,
            "bocel": 0.78, "bocel_m": 0.012, "sombra": {"dist_m": 0.05, "sig_m": 0.04, "forca": 0.32},
            "triangulos_pt": [(448.5, 1097.7, "esquerda")]}


def degraus_blocos(Q, img):
    sys.path.insert(0, str(B.RAIZ / "_texturas"))
    from texturas import textura
    q, k = BLOCOS_F, BLOCOS_F["ss"]
    cx0, cy0, cx1, cy1 = q["caixa_pt"]
    blocos = sorted([d for d in Q.desenhos if d.get("layer") == "ARQ_CONTRAPISO" and d["type"] == "f" and d.get("fill")
                     and len(d["items"]) == 4 and cx0 <= d["rect"].x0 and d["rect"].x1 <= cx1 and cy0 <= d["rect"].y0
                     and d["rect"].y1 <= cy1], key=lambda d: d.get("seqno", 0))
    X0, Y0, X1, Y1 = ret_q(Q, q["caixa_pt"])
    w, h = X1 - X0, Y1 - Y0
    out = img.astype(np.float32)
    reg = out[Y0:Y1, X0:X1]
    rng = np.random.default_rng(q["semente"])
    s = q["sombra"]
    d_ = s["dist_m"] * Q.px_m * k
    lb = max(1, int(round(q["bocel_m"] * Q.px_m * k)))

    def reduzir(a):
        return cv2.resize(a.astype(np.float32), (w, h), interpolation=cv2.INTER_AREA)
    for i, d in enumerate(blocos):
        m = np.zeros((h * k, w * k), np.uint8)
        cv2.fillPoly(m, [np.int32(np.round((c - (X0, Y0)) * k)) for c in Q.caminhos(d) if len(c) >= 3], 255)
        mf = m.astype(np.float32) / 255
        a = reduzir(mf)
        sb = reduzir(cv2.GaussianBlur(cv2.warpAffine(mf, np.float32([[1, 0, -d_], [0, 1, d_]]), (w * k, h * k)),
                                      (0, 0), s["sig_m"] * Q.px_m * k)) * s["forca"]
        reg *= (1 - sb * (1 - a))[..., None]
        tex = textura(q["pedra"], Q.px_m, h, w, semente=q["semente"] + i).astype(np.float32)
        tex *= 1 + q["tom"] * rng.uniform(-1, 1)
        reg[:] = reg * (1 - a[..., None]) + tex * a[..., None]
        anel = m & ~cv2.erode(m, np.ones((lb, lb), np.uint8))
        reg *= (1 - (1 - q["bocel"]) * reduzir(anel / 255.0))[..., None]
    from retoque_terreo_casae import ESCADA_LINHAS
    t = ESCADA_LINHAS["triangulo"]
    for xp, yp, sentido in q["triangulos_pt"]:
        dx, dy = {"esquerda": (-1, 0), "direita": (1, 0), "cima": (0, -1), "baixo": (0, 1)}[sentido]
        xa, ya = xp - dx * t["altura_pt"], yp - dy * t["altura_pt"]          # o meio da base, atrás da ponta
        b = t["base_pt"] / 2
        pts = [(xp, yp), (xa - dy * b, ya - dx * b), (xa + dy * b, ya + dx * b)]
        m = np.zeros((h * k, w * k), np.uint8)
        cv2.fillPoly(m, [np.int32(np.round([(np.array(Q.p2q(x, y)) - (X0, Y0)) * k for x, y in pts]))], 255)
        tri = reduzir(m / 255.0)[..., None]
        reg[:] = reg * (1 - tri) + np.float32(t["cor"]) * tri
    print(f"    degraus em blocos: os {len(blocos)} blocos de pedra do PDF à esquerda do deck em Bege Bahia, cada um com "
          f"o bocel e a sombra curta sobre o de baixo; {len(q['triangulos_pt'])} triângulo(s) da R14 descendo do deck para a laje")
    return np.clip(out, 0, 255).astype(np.uint8)


def escadas_projecoes(Q, img):
    out = np.ascontiguousarray(img.copy())
    with em_quadro(Q):
        pa = AJ.PROJECOES_A
        AJ.PROJECOES_A = dict(pa, larg_px=pa["larg_px"] * Q.W / 2000)
        try:
            out = degraus_blocos(Q, out)                                  # a pedra grande e as lajes em cascata
            out = degraus_bege(Q, out, B.ESCADAS_T)                     # as duas do Térreo: a de 6 e a de 9 degraus
            out, n = B.linhas_pdf(out, "Terreo", B.PROJ_T["zonas"], B.PROJ_T["camada"])
        finally:
            AJ.PROJECOES_A = pa
    print(f"    escadas (R14) e projeções do PDF ({n} traços) no quadro da prancha")
    return out


CHUVEIRO_DECK = {"ducha": (690.8, 930.4, 702.0, 941.6), "braco": (695.6, 934.9, 697.1, 957.2),
                 "canopla": (693.6, 955.6, 699.2, 958.2)}
# O banco em L do deck em bronze fosco (usuário, 22/10/26: "O BANCO EM L DO DECK É EM BRONZE FOSCO"): a cor chapada do
# bronze, escovado de leve no sentido de cada braço, a quina do lado da luz (em cima e à direita) um pouco mais clara e a
# do outro lado um pouco mais escura, o contorno fino e a sombra curta no deck.
BANCO_DECK = {"cor_base": (60, 90, 122), "bronze": (62, 84, 104), "escovado": 0.010, "quina": 0.10, "quina_px": 1.6,
              "contorno": (40, 50, 60), "larg_px": 0.9}


def deck_detalhes(Q, img):
    """O chuveiro do deck (usuário, 22/10/26: "MELHORE A REPRESENTAÇÃO DO CHUVEIRO"): a ducha quadrada, o braço e a
    canopla do PDF, cromados (`retoque_subsolo_casae.chuveiro`). O banco em L do deck (a madeira mais escura da legenda),
    em bronze fosco (`BANCO_DECK`), com o contorno fino e a sombra curta."""
    from retoque_subsolo_casae import chuveiro
    q = BANCO_DECK
    out = img.copy()
    m = Q.cor([q["cor_base"]], tol=6)
    m = fechar(m, 3)
    if m.any():
        n, lab, st, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8), 8)
        novo = out.astype(np.float32)
        for i in range(1, n):
            if st[i, cv2.CC_STAT_AREA] < 200:
                continue
            mi = lab == i
            # cada braço do L: o escovado corre ao longo dele (na horizontal no braço deitado, na vertical no em pé)
            hor = cv2.morphologyEx(mi.astype(np.uint8), cv2.MORPH_OPEN, np.ones((1, int(1.0 * Q.px_m)), np.uint8)) > 0
            rng = np.random.default_rng(23)
            ru = rng.normal(0, 1, (Q.H, Q.W)).astype(np.float32)
            esc_h = cv2.GaussianBlur(ru, (0, 0), sigmaX=0.4 * Q.px_m, sigmaY=0.5)
            esc_v = cv2.GaussianBlur(ru, (0, 0), sigmaX=0.5, sigmaY=0.4 * Q.px_m)
            esc = np.where(hor, esc_h / max(esc_h.std(), 1e-6), esc_v / max(esc_v.std(), 1e-6))
            f = 1 + q["escovado"] * esc
            # a quina: mais clara do lado da luz (o vizinho de cima e da direita fora do banco), mais escura do outro
            u8 = mi.astype(np.uint8)
            k = max(1, int(round(q["quina_px"])))
            luz = u8 & (1 - cv2.warpAffine(u8, np.float32([[1, 0, -k], [0, 1, k]]), (Q.W, Q.H)))
            somb = u8 & (1 - cv2.warpAffine(u8, np.float32([[1, 0, k], [0, 1, -k]]), (Q.W, Q.H)))
            f += q["quina"] * (cv2.GaussianBlur(luz.astype(np.float32), (0, 0), 0.6)
                               - cv2.GaussianBlur(somb.astype(np.float32), (0, 0), 0.6))
            novo[mi] = (np.float32(q["bronze"])[None, :] * f[mi][:, None])
            del ru, esc_h, esc_v, esc
            # sombra curta no deck e o contorno fino
            a = mi.astype(np.float32)
            d_ = 0.03 * Q.px_m
            sb = cv2.GaussianBlur(cv2.warpAffine(a, np.float32([[1, 0, -d_], [0, 1, d_]]), (Q.W, Q.H)), (0, 0),
                                  0.025 * Q.px_m) * (1 - a) * 0.3
            novo *= (1 - sb)[..., None]
            borda = cv2.morphologyEx(mi.astype(np.uint8), cv2.MORPH_GRADIENT, np.ones((2, 2), np.uint8)).astype(bool) & mi
            novo[borda] = novo[borda] * 0.4 + np.float32(q["contorno"]) * 0.6
        out = np.clip(novo, 0, 255).astype(np.uint8)
    c = CHUVEIRO_DECK
    if Q.chave == "Terreo":
        out = chuveiro(out, Q.p2q, c["ducha"], c["braco"], c["canopla"])
    print("    deck: o banco em L em bronze fosco, com o contorno e a sombra; o chuveiro cromado do PDF")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# A final inteira
TERREO = {
    "carros_pt": [(2370, 1525, 2500, 1800), (2220, 1530, 2350, 1800), (2060, 1532, 2192, 1805)],
    "inox_pt": [],                     # as cubas da cozinha, do gourmet e do bar: brancas ("CUBAS EM BRANCO")
    "chuveiro_deck_pt": (688.0, 928.0, 704.0, 960.0),
}


ETAPAS = B.CACHE / "final3840"


def final_3840(chave, salvar=True, de=None):
    """A final de 3840 px com os rótulos. de: recomeça desta etapa, com a anterior do cache (`ETAPAS`)."""
    import time
    import retoque_1pav_casae as R1
    Q = Quadro(chave)
    ini = quadro_inicial(Q)
    M = afim_render(Q, B.CASA_B / Q.q["render"], B.CASA_B / Q.q["aprovada"])
    t = TERREO
    img = ini
    ETAPAS.mkdir(parents=True, exist_ok=True)
    if chave == "Subsolo":
        passos = passos_subsolo(Q, ini)
    else:
        passos = passos_terreo(Q, ini, M, t)
    nomes = [n for n, _ in passos]
    i0 = nomes.index(de) if de else 0
    if i0 > 0:
        img = cv2.imread(str(ETAPAS / f"{chave}_{nomes[i0 - 1]}.png"))
    for nome, f in passos[i0:]:
        t0 = time.time()
        img = f(img)
        print(f"  [{nome}] {time.time() - t0:.0f} s", flush=True)
        cv2.imwrite(str(ETAPAS / f"{chave}_{nome}.png"), img)
    if salvar:
        nome = B.CASA_B / "renders" / f"POE642_CasaB_PH_{chave}_final_rotulos.png"
        cv2.imwrite(str(nome), img)
        print(f"    {nome} {img.shape[1]}x{img.shape[0]}")
    return Q, img


def passos_subsolo(Q, ini):
    chave = "Subsolo"
    pq = B.CASA_B / "renders" / "POE642_CasaB_PH_Subsolo_pegada_mascara.png"
    peg = cv2.resize(cv2.imread(str(pq), cv2.IMREAD_GRAYSCALE), (Q.W, Q.H), interpolation=cv2.INTER_LINEAR)
    dentro = peg > 127
    AJ.SUBSOLO_R2 = dict(AJ.SUBSOLO_R2, terreo=B.CASA_B / "renders" / "POE642_CasaB_PH_Terreo_final_rotulos.png")
    c = B.CHUVEIRO_DUCHA

    def biblioteca_s(im):
        from retoque_subsolo_casae import chuveiro
        return chuveiro(np.ascontiguousarray(im.copy()), Q.p2q, c["ducha"], c["braco"], c["canopla"])

    def escadas_s(im):
        # a escada de 6 degraus (a de 9 é do Térreo e fica na hachura): os degraus do PDF em Bege Bahia, sem linhas,
        # com o sombreamento de subida e o S do PDF (auditoria de 26/10, E3 e E8)
        return escada_sombreada(Q, np.ascontiguousarray(im.copy()), B.ESCADAS_S[0], "S")

    def rotulos_s(im):
        # o rótulo do shaft (no PDF, fora da lista dos ambientes), como no Térreo da Casa A (auditoria de 26/10)
        import retoque_1pav_casae as R1
        rot = B.rotulos_casab(Q.pg, Q.p2q2000) + [r for r in R1.rotulos_pdf(Q.pg) if r[0] == "SHAFT"]
        return rotulos(Q, im, rot, Q.q["ajustes"], granito=A.granito(im, Q.q.get("granito_lum_max", 125)))
    # Pedido do usuário (26/10/26): "banho sauna: sanitário marrom, cuba esculpida em mármore travertino bruto e pedra
    # da bancada da cuba em granito marrom; banho serviço: cuba branca, pedra da pia em marrom granito, sanitário
    # branco" (as duas bancadas do Subsolo em granito marrom, a cuba da ARQ_BANCADAS em travertino, o vaso do BH sauna
    # marrom). Auditoria de 26/10 (aprovada pelo usuário: "ok, aplique a lista"): as bancadas com a borda e a sombra (E9), os
    # boxes em vidro contínuo (E5), as paredes em cinza 80 (E10), a escada sem linhas com o S (E3, E8) e os rótulos
    # (CIRCULAÇÃO de 2,23 m² no corpo do PDF, longe das paredes, e o SHAFT; E7). Depois: "melhore o aspecto do marmore
    # travertino bruto": o piso de travertino (sauna, BH sauna, depósito) e os bancos da sauna no travertino bruto da
    # Casa A aprovado (`final3840_casaa.travertino_bruto`: os veios horizontais e os poros), na luz e no tom de antes
    return [
        ("pisos", lambda im: pisos(Q, im, dentro=dentro, bruto={"travertino": "piso"})),
        ("bancadas", lambda im: bancadas(Q, im, borda=BANCADAS_F["borda_e9"], pedra="granito", cuba=cuba_travertino)),
        ("sauna", lambda im: bancos_sauna(Q, im, bruto="bancada")),
        ("pecas", lambda im: pecas_pdf(Q, im, ini, fora=[c["ducha"]] and [(c["ducha"][0] - 3, c["ducha"][1] - 3,
                                                                          c["canopla"][2] + 3, c["ducha"][3] + 3)])),
        ("tampas", lambda im: tampas_vasos(Q, im)),
        ("vasos", lambda im: vasos_cor(Q, im)),
        ("biblioteca", biblioteca_s),
        ("boxes", lambda im: boxes_vidro(Q, im)),
        ("paredes", lambda im: paredes(Q, im, cor=PAREDES_F["cinza"])),
        ("soleiras", lambda im: soleiras(Q, im)),
        ("esquadrias", lambda im: B.esquadrias_final(im, chave, Q.pg, Q.p2q, Q.px_m, parede=PAREDES_F["cinza"])),
        ("escadas", escadas_s),
        ("hachura", lambda im: AJ.subsolo_hachurado(im, peg.astype(np.float32) / 255, Q.px_m)),
        ("rotulos", rotulos_s),
    ]


def passos_terreo(Q, ini, M, t):
    chave = "Terreo"
    return [
        ("pisos", lambda im: pisos(Q, im, incluir={"pedra portuguesa": t["carros_pt"]})),
        ("bordas", lambda im: B.bordas_grama(im, chave)),
        ("vegetacao", lambda im: vegetacao(Q, im, M)),
        ("bancadas", lambda im: bancadas(Q, im)),
        ("pecas", lambda im: pecas_pdf(Q, im, ini, fora=t["carros_pt"] + [t["chuveiro_deck_pt"], BANQUETAS_PT],
                                      camas=[c[1] for c in B.CAMAS_B["camas"]], inox=t["inox_pt"])),
        ("tampas", lambda im: desenho_mesa(Q, tampas_vasos(Q, im))),
        ("biblioteca", lambda im: biblioteca(Q, im)),
        ("carros", lambda im: carros(Q, im, M)),
        ("deck", lambda im: deck_detalhes(Q, im)),
        ("boxes", lambda im: boxes_granito(Q, im)),
        ("paredes", lambda im: paredes(Q, im)),
        ("soleiras", lambda im: soleiras(Q, im)),
        ("esquadrias", lambda im: esquadrias_terreo(Q, im)),
        ("cortinas", lambda im: cortinas(Q, im)),
        ("escadas", lambda im: escadas_projecoes(Q, im)),
        ("cobertura", lambda im: B.cobertura_final(im, Q.pg, Q.p2q)),
        ("rotulos", lambda im: rotulos(Q, im, B.rotulos_casab(Q.pg, Q.p2q2000), Q.q["ajustes"],
                                       granito=A.granito(im, Q.q.get("granito_lum_max", 125)))),
    ]



# ----------------------------------------------------------------------------------------------------------------------
# 9. Os rótulos (usuário, 22/10/26: "MELHORE OS RÓTULOS E NÃO OS SOBREPONHA OS OBJETOS"; depois: "RÓTULOS NÃO PODEM TER
# SOMBRA. USE A COR PRETA OU BRANCA, A DEPENDER DO FUNDO. E OS RÓTULOS DEVEM ESTAR DENTRO DE SEUS RESPECTIVOS
# AMBIENTES"): cada um no lugar livre mais perto do ponto do PDF, sem tocar móvel, tapete, louça, bancada, parede,
# esquadria, escada nem outro rótulo, dentro de `raio_m` e sempre dentro do seu ambiente; as opções de corpo e quebra
# dos ajustes à mão continuam valendo. Sem halo nem sombra: o texto é preto ou branco, o que contrasta mais com o fundo
# (a luminância relativa do fundo da caixa, pela conta do WCAG).
ROTULOS_F = {"raio_m": 3.0, "passo_px": 2, "folga_px": 2,
             "corpos": (1.0, 0.85, 0.72, 0.62),     # o corpo cai (fração do da regra) onde o texto não cabe livre
             "livres": ("JARDIM DE INVERNO", "JARDIM"),          # os jardins: o texto vai sobre as plantas, em branco
             "corpo_custo": 2000,          # o custo de descer o corpo (x a fração): o corpo cheio vale mais que a distância
             "obstaculos": ("ARQ_MOBILIÁRIO", "ARQ_LAYOUT HUMANIZAÇÃO", "ARQ_LOUÇAS E METAIS", "ARQ - Marcenaria",
                            "ARQ_BANCADAS", "ARQ_PAREDE", "ARQ_ESCADAS E RAMPAS", "ARQ_ELEMENTOS FIXOS", "EST_PILAR"),
             # os ambientes: as paredes do PDF (os preenchimentos escuros), com os vãos entre trechos alinhados (portas e
             # passagens) fechados até `vao_max_m`; parede é o trecho de até `parede_max_m` de espessura
             "vao_max_m": 2.0, "parede_max_m": 0.40,
             "preto": (20, 20, 20), "branco": (250, 250, 250),
             # o nome escrito (usuário, 22/10/26: "PODE ESCREVER ASSIM 'BH. GOURMET', E NÃO PRECISA FICAR DENTRO DO
             # BOX") e o ponto (pt) de onde a busca parte, no lugar do ponto do PDF ("O RÓTULO DA PRAINHA PODE FICAR
             # ABAIXO DAS DUAS ESPREGUIÇADEIRAS")
             "textos": {"BANHO GOURMET": "BH. GOURMET"},
             "pontos": {"Terreo": {"PRAINHA": (816.8, 1470.0)}}}


def ambientes_rotulos(Q, ancoras, f=2):
    """O ambiente de cada rótulo (imagem int32: i + 1 no ambiente do ponto i, 0 nas paredes). As paredes são os
    preenchimentos escuros da ARQ_PAREDE, dos elementos fixos e dos pilares; os vãos entre dois trechos de parede
    alinhados (a porta, a passagem sem porta, como a da circulação do Subsolo para a garagem) fecham até `vao_max_m`.
    Vidros e folhas de porta não dividem o ambiente (antes, a folha aberta cortava o banho ao meio); o vidro do box,
    sim, e o lado do chuveiro (`duchas_box`) fica fora de todos os ambientes: o rótulo nunca vai para dentro do box
    (o ponto do PDF que cai nele passa ao piso seco mais perto do mesmo banho). Cada região livre é repartida entre os
    pontos do PDF que caem nela, pela distância andando por dentro."""
    q = ROTULOS_F
    par = (Q.preencher(lambda d: d.get("layer") in ("ARQ_PAREDE", "ARQ_ELEMENTOS FIXOS", "EST_PILAR") and d.get("fill")
                       and max(d["fill"]) < 0.6, ss=1) > 0.3).astype(np.uint8)
    t = int(round(q["parede_max_m"] * Q.px_m))
    k = int(round(q["vao_max_m"] * Q.px_m))
    deitada = par & (1 - cv2.morphologyEx(par, cv2.MORPH_OPEN, np.ones((t + 1, 1), np.uint8)))   # fina na vertical
    em_pe = par & (1 - cv2.morphologyEx(par, cv2.MORPH_OPEN, np.ones((1, t + 1), np.uint8)))     # fina na horizontal
    vaos = cv2.morphologyEx(deitada, cv2.MORPH_CLOSE, np.ones((1, k), np.uint8)) | \
        cv2.morphologyEx(em_pe, cv2.MORPH_CLOSE, np.ones((k, 1), np.uint8))
    boxes = vidros_box(Q)
    box = np.zeros_like(par)
    for x0, y0, x1, y1, _ in boxes:
        a0, b0, a1, b1 = ret_q(Q, (x0, y0, x1, y1))
        box[b0:b1 + 1, a0:a1 + 1] = 1
    barreira = cv2.dilate(par | vaos | box, np.ones((3, 3), np.uint8))
    sem_box = cv2.dilate(par | vaos, np.ones((3, 3), np.uint8))
    # a repartição: as frentes saem de cada ponto ao mesmo tempo, pelo livre (em 1/f da resolução)
    def reduz(b):
        return cv2.resize((1 - b).astype(np.float32), (Q.W // f, Q.H // f), interpolation=cv2.INTER_AREA) > 0.99
    livre, livre0 = reduz(barreira), reduz(sem_box)
    _, comp = cv2.connectedComponents(livre.astype(np.uint8), connectivity=4)
    _, comp0 = cv2.connectedComponents(livre0.astype(np.uint8), connectivity=4)
    ly, lx = np.nonzero(livre)
    for ducha in duchas_box(Q, boxes):                                 # o lado do chuveiro sai do livre
        if ducha is None:
            continue
        dx_, dy_ = Q.p2q(*ducha)
        j = int(np.argmin((lx - dx_ / f) ** 2 + (ly - dy_ / f) ** 2))
        livre[comp == comp[ly[j], lx[j]]] = False
    lab = np.zeros(livre.shape, np.int32)
    ys, xs = np.nonzero(livre)
    for i, (x, y) in enumerate(ancoras):
        # o ponto (ou o livre mais perto dele, de preferência no mesmo banho: o seco, se o ponto caiu no box)
        y0_, x0_ = min(int(y / f), livre.shape[0] - 1), min(int(x / f), livre.shape[1] - 1)
        c0 = comp0[y0_, x0_]
        mesmo = comp0[ys, xs] == c0 if c0 else np.zeros(len(xs), bool)
        cand = np.nonzero(mesmo)[0] if mesmo.any() else np.arange(len(xs))
        j = cand[int(np.argmin((xs[cand] - x / f) ** 2 + (ys[cand] - y / f) ** 2))]
        lab[ys[j], xs[j]] = i + 1
    cruz = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    while True:
        viz = cv2.dilate(lab.astype(np.float32), cruz).astype(np.int32)
        novo = (lab == 0) & livre & (viz > 0)
        if not novo.any():
            break
        lab[novo] = viz[novo]
    return cv2.resize(lab, (Q.W, Q.H), interpolation=cv2.INTER_NEAREST)


def textos_rotulos(rot):
    """Os rótulos com o nome escrito de `ROTULOS_F["textos"]` (o nome da lista fica, para os ajustes), na mesma linha e
    no mesmo centro do nome do PDF."""
    from PIL import ImageFont
    from rodape_entrega import FONTES
    import retoque_1pav_casae as R1
    f = ImageFont.truetype(str(FONTES / f"Inter-{R1.ROTULOS['fonte']}.otf"), 100)
    novos = []
    for nome, linhas, ponto, caixa in rot:
        t = ROTULOS_F["textos"].get(nome)
        if t and linhas and linhas[0][0] == nome:
            texto, tam, (ox, oy) = linhas[0]
            ox += (f.getlength(texto) - f.getlength(t)) * tam / 100 / 2
            linhas = [(t, tam, (ox, oy))] + list(linhas[1:])
        novos.append((nome, linhas, ponto, caixa))
    return novos


def cor_do_fundo(img, x0, y0, x1, y1):
    """Preto ou branco, o que contrasta mais com o fundo da caixa (luminância relativa, WCAG)."""
    q = ROTULOS_F
    reg = img[max(0, y0):y1, max(0, x0):x1].reshape(-1, 3).astype(np.float32) / 255
    c = np.where(reg <= 0.04045, reg / 12.92, ((reg + 0.055) / 1.055) ** 2.4)
    lum = float((0.0722 * c[:, 0] + 0.7152 * c[:, 1] + 0.2126 * c[:, 2]).mean())   # BGR
    return q["preto"] if (lum + 0.05) / 0.05 >= 1.05 / (lum + 0.05) else q["branco"]


def _caixa_texto(Q, rot1, opc):
    """A caixa exata (relativa ao ponto do PDF, em px) do rótulo desenhado pela `rotulos_ambientes`."""
    import retoque_1pav_casae as R1
    nome, linhas, (pcx, pcy), caixa = rot1
    cx, cy = Q.p2q(pcx, pcy)
    (x0, y0), (x1, y1) = Q.p2q(caixa.x0, caixa.y0), Q.p2q(caixa.x1, caixa.y1)
    m = int(max(x1 - x0, y1 - y0) * 2 + 80)
    X0, Y0 = int(cx) - m, int(cy) - m
    tela = np.full((2 * m, 2 * m, 3), 128, np.uint8)

    def p2l(x, y):
        a, b = Q.p2q(x, y)
        return a - X0, b - Y0
    esc = Q.W / 2000
    # o centro do ajuste vai em px de 2000 da tela (a `rotulos_ambientes` o compara na largura da imagem que recebe);
    # na escala da prancha, as opções (corpo, quebra) não casavam e a caixa saía sempre a do corpo padrão
    et = tela.shape[1] / 2000
    aj = [(nome, ((cx - X0) / et, (cy - Y0) / et), (0.0, 0.0), opc)]
    t = R1.rotulos_ambientes(tela, [rot1], p2l, escala_desvio=esc, ajustes=aj)
    ys, xs = np.nonzero(np.abs(t.astype(int) - 128).max(axis=2) > 3)
    if not len(xs):
        return -10, -5, 10, 5
    return xs.min() + X0 - cx, ys.min() + Y0 - cy, xs.max() + 1 + X0 - cx, ys.max() + 1 + Y0 - cy


def rotulos(Q, img, rot, ajustes_manuais, granito=None):
    """Cada rótulo no lugar livre mais perto do ponto do PDF: a caixa exata do texto não pode tocar objeto nenhum, nem
    outro rótulo, e fica dentro do seu ambiente (`ambientes_rotulos`); onde não há lugar, o corpo cai (até 62% do da
    regra) e, por fim, fica onde toca menos, mas sempre dentro do ambiente. A cor é a do fundo (`cor_do_fundo`)."""
    import retoque_1pav_casae as R1
    q = ROTULOS_F
    obst = Q.preencher(lambda d: d.get("layer") in q["obstaculos"], ss=2, fs=True) > 0.05
    tr = np.zeros((Q.H, Q.W), np.uint8)
    for d in Q.desenhos:
        if d.get("layer") in q["obstaculos"] and d["type"] == "s":
            for c in Q.caminhos(d):
                cv2.polylines(tr, [np.int32(np.round(c))], False, 1, 2)
    obst |= tr.astype(bool)
    k = 2 * q["folga_px"] + 1
    obst = cv2.dilate(obst.astype(np.uint8), np.ones((k, k), np.uint8))
    I_obst = cv2.integral(obst)
    # os ambientes: o que não é parede, esquadria nem porta (os arcos e as folhas do PDF fecham as portas)
    rot = textos_rotulos(rot)
    pontos = q["pontos"].get(Q.chave, {})
    busca = [Q.p2q(*pontos[r[0]]) if r[0] in pontos else Q.p2q(r[2][0], r[2][1]) for r in rot]
    amb = ambientes_rotulos(Q, busca)
    esc = Q.W / 2000

    def soma(I, x0, y0, x1, y1):
        x0, y0, x1, y1 = max(0, x0), max(0, y0), min(Q.W, x1), min(Q.H, y1)
        if x1 <= x0 or y1 <= y0:
            return 10 ** 9
        return int(I[y1, x1] - I[y0, x1] - I[y1, x0] + I[y0, x0])
    ocupado = np.zeros((Q.H, Q.W), np.uint8)
    novos = []
    R = int(q["raio_m"] * Q.px_m)
    for i_rot, rot1 in enumerate(rot):
        nome, linhas, (pcx, pcy), caixa = rot1
        cx, cy = Q.p2q(pcx, pcy)
        opc = {}
        for n, (axx, ayy), d_, *extra in ajustes_manuais:
            if n == nome and np.hypot(cx - axx * esc, cy - ayy * esc) < 25 * esc:
                opc = dict(extra[0]) if extra and isinstance(extra[0], dict) else ({"corpo": extra[0]} if extra else {})
        if nome in q["livres"]:
            novos.append((nome, (cx / esc, cy / esc), (0.0, 0.0), dict(opc, cor=q["branco"])))   # sobre as plantas
            continue
        dentro = (amb == i_rot + 1).astype(np.uint8)                # o ambiente do rótulo (`ambientes_rotulos`)
        sx, sy = busca[i_rot][0] - cx, busca[i_rot][1] - cy          # de onde a busca parte (o ponto do PDF ou o pedido)
        I_dentro = cv2.integral(dentro)
        I_ocup = cv2.integral(ocupado)
        melhor = None
        corpo0 = opc.get("corpo", R1.ROTULOS["escala"])
        palavras = rot1[1][0][0].split()                            # o nome escrito
        opcoes = []
        for fc in q["corpos"]:
            opcoes.append((fc, dict(opc, corpo=corpo0 * fc)))
            if len(palavras) >= 2 and "quebra" not in opc:            # o nome em duas linhas, no mesmo corpo
                meio = (len(palavras) + 1) // 2
                opcoes.append((fc - 0.05, dict(opc, corpo=corpo0 * fc,
                                               quebra=[" ".join(palavras[:meio]), " ".join(palavras[meio:])])))
        for fc, o2 in opcoes:
            bx0, by0, bx1, by1 = _caixa_texto(Q, rot1, o2)
            w, h = bx1 - bx0, by1 - by0
            for r_ in range(0, R + 1, q["passo_px"]):
                anel = [(0, 0)] if r_ == 0 else [(int(round(r_ * np.cos(t))), int(round(r_ * np.sin(t))))
                                                  for t in np.linspace(0, 2 * np.pi, max(8, int(2 * np.pi * r_ / 3)),
                                                                       endpoint=False)]
                anel = [(int(round(sx)) + ax_, int(round(sy)) + ay_) for ax_, ay_ in anel]
                for dx, dy in anel:
                    x0_, y0_ = int(round(cx + bx0 + dx)), int(round(cy + by0 + dy))
                    x1_, y1_ = x0_ + int(round(w)), y0_ + int(round(h))
                    fora_amb = w * h - soma(I_dentro, x0_, y0_, x1_, y1_)
                    toca = soma(I_obst, x0_, y0_, x1_, y1_)
                    sobre = soma(I_ocup, x0_, y0_, x1_, y1_)
                    custo = (10 ** 9 if sobre else 0) + 10 ** 7 * fora_amb + 100 * toca + r_ + \
                        q["corpo_custo"] * (1 - fc)
                    if melhor is None or custo < melhor[0]:
                        melhor = (custo, dx, dy, (x0_, y0_, x1_, y1_), o2, toca, fora_amb)
                if melhor[5] == 0 and melhor[6] == 0 and melhor[0] < 10 ** 7:
                    break
            if melhor[5] == 0 and melhor[6] == 0:
                break
        custo, dx, dy, (x0_, y0_, x1_, y1_), o2, toca, fora_amb = melhor
        ocupado[max(0, y0_ - 6):y1_ + 6, max(0, x0_ - 6):x1_ + 6] = 1
        o2 = dict(o2, cor=cor_do_fundo(img, x0_, y0_, x1_, y1_))      # preto ou branco, pelo fundo
        novos.append((nome, (cx / esc, cy / esc), (dx / esc, dy / esc), o2))
        if toca or fora_amb:
            print(f"    rótulo {nome}: sem lugar totalmente livre (toca {toca} px; fora do ambiente {fora_amb} px)")
    out = R1.rotulos_ambientes(img, rot, Q.p2q, escala_desvio=esc, granito=granito, ajustes=novos,
                               cor_granito=R1.ROTULOS["branco"], halo=None)
    nb = sum(1 for n in novos if n[3].get("cor") == q["branco"])
    print(f"    {len(rot)} rótulos no lugar livre mais perto do PDF, dentro do ambiente, sem halo: "
          f"{len(rot) - nb} pretos e {nb} brancos, pelo fundo")
    return out



if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pavimento", choices=list(B.PAVIMENTOS_B))
    ap.add_argument("--de", default=None, help="recomeça desta etapa (pisos, bordas, vegetacao, bancadas, pecas, ...)")
    a = ap.parse_args()
    final_3840(a.pavimento, de=a.de)

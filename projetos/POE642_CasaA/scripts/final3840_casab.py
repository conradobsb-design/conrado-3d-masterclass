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


def piso_textura(Q, img, m, nome, forca, sig_m, semente):
    """O material `nome` na máscara m, na escala da prancha."""
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
    if nome == "travertino":
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


def pisos(Q, img, incluir=None, dentro=None):
    """incluir: {nome do piso: [retângulos em pt]} onde o branco da base (uma peça que sai, como os carros) também é
    aquele piso. dentro: só nesta máscara (a pegada do Subsolo)."""
    out = img.astype(np.float32)
    incluir = incluir or {}
    branco = Q.cor([(255, 255, 255)], tol=3)
    for i, (nome, cores, k, tex, forca, sig) in enumerate(PISOS[Q.chave]):
        m = Q.cor(cores, tol=6)
        for r in incluir.get(nome, []):
            x0, y0, x1, y1 = ret_q(Q, r)
            m[y0:y1, x0:x1] |= branco[y0:y1, x0:x1]
        if k:
            m = fechar(m, k) & ~Q.cor([(17, 17, 17), (0, 0, 0)], tol=20)   # as linhas finas da base, não as paredes
        if dentro is not None:
            m &= dentro
        if not m.any():
            continue
        novo = piso_textura(Q, out, m, tex, forca, sig, 700 + i)
        out = pousar(out, novo, m, suave=0.5)
        print(f"    piso {nome}: {int(m.sum())} px, a {Q.px_m:.1f} px/m")
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
    ds = [d for d in Q.desenhos if d.get("layer") in CAMADAS_PECAS and not dentro(d["rect"], fora)
          and not onda_cortina(d)]
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
    T = np.maximum(topo, 0)
    C = cor_lab[T]                                                   # (H ss, W ss, 3) em Lab
    borda = np.zeros_like(topo, np.uint8)
    borda[:, 1:] |= (topo[:, 1:] != topo[:, :-1]).astype(np.uint8)
    borda[1:, :] |= (topo[1:, :] != topo[:-1, :]).astype(np.uint8)
    dist = cv2.distanceTransform((1 - borda).astype(np.uint8), cv2.DIST_L2, 3)
    larg = q["volume"]["larg_m"] * px
    fator = 1 - k_vol[T] * (1 - np.minimum(1, dist / larg)) ** 2
    ruido_h = cv2.GaussianBlur(rng.normal(0, 1, topo.shape).astype(np.float32), (0, 0), sigmaX=0.25 * px, sigmaY=0.6)
    ruido_v = cv2.GaussianBlur(rng.normal(0, 1, topo.shape).astype(np.float32), (0, 0), sigmaX=0.6, sigmaY=0.25 * px)
    ruido_h /= max(ruido_h.std(), 1e-6)
    ruido_v /= max(ruido_v.std(), 1e-6)
    veio = np.where(vertical[T], ruido_v, ruido_h)
    fator *= np.where(madeira[T], 1 + q["madeira"]["veio"] * veio, 1.0)
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
                       "aro_pt": 1.2, "recuo": 0.12, "raio_m": 0.035}}


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


def bancadas(Q, img):
    sys.path.insert(0, str(B.RAIZ / "_texturas"))
    from texturas import textura
    q = BANCADAS_F
    a = Q.preencher(lambda d: d.get("layer") == "ARQ_BANCADAS" and d.get("fill") and not no_banco_sauna(Q, d["rect"]),
                    fs=False)
    n, lab, st, _ = cv2.connectedComponentsWithStats((a > 0.5).astype(np.uint8), 8)
    out = img.astype(np.float32)
    pecas = 0
    for i in range(1, n):
        x, y, w, h, area = st[i]
        comp = lab == i
        (_, _), (r1, r2), _ = cv2.minAreaRect(np.argwhere(comp)[:, ::-1].astype(np.float32))
        if min(r1, r2) < q["lado_min_m"] * Q.px_m:
            continue
        x0, y0, x1, y1 = max(0, x - 2), max(0, y - 2), min(Q.W, x + w + 2), min(Q.H, y + h + 2)
        reg = (slice(y0, y1), slice(x0, x1))
        al = a[reg] * cv2.dilate(comp.astype(np.uint8), np.ones((3, 3), np.uint8))[reg]
        tex = textura(q["pedra"], Q.px_m, y1 - y0, x1 - x0, semente=900 + i).astype(np.float32)
        med = tex.reshape(-1, 3).mean(axis=0)
        tex = (med + q["contraste"] * (tex - med)) * (np.float32(q["tom"]) / med)  # o desenho da placa, no tom areia
        d = cv2.distanceTransform((al > 0.5).astype(np.uint8), cv2.DIST_L2, 3)
        tex *= (1 - q["volume"] * (1 - np.minimum(1, d / (q["larg_m"] * Q.px_m))) ** 2)[..., None]
        out[reg] = out[reg] * (1 - al[..., None]) + tex * al[..., None]
        pecas += 1
    # as cubas: louça branca, a bacia de cantos arredondados recuada do aro, a sombra interna do lado da luz
    lq, c = PECAS["louca"], q["cuba"]
    cubas = cubas_bancada(Q)
    sem_traco = np.zeros((Q.H, Q.W), np.uint8)          # onde o traço do PDF não entra: o aro duplo vira um contorno só
    for r in cubas:
        x0, y0, x1, y1 = ret_q(Q, (r[0] - c["aro_pt"], r[1] - c["aro_pt"], r[2] + c["aro_pt"], r[3] + c["aro_pt"]))
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
    print(f"    bancadas: {pecas} peças em {q['pedra']} no tom areia, a {Q.px_m:.1f} px/m, com o contorno do PDF; "
          f"{len(cubas)} cubas em louça branca")
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


def bancos_sauna(Q, img):
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
    T = textura("travertino", Q.px_m, y1 - y0, x1 - x0, semente=q["semente"]).astype(np.float32)
    det = cv2.GaussianBlur(T, (0, 0), 0.6) / np.maximum(cv2.GaussianBlur(T, (0, 0), 3.0 * Q.px_m), 1)
    T = cor * (1 + q["veio"] * (det - 1))                              # o veio na força do piso (`piso_textura`)
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
    print(f"    sauna: os bancos ({b['pt'][2] - b['pt'][0]:.0f} x {b['pt'][3] - b['pt'][1]:.0f} pt) no travertino da "
          f"biblioteca, no tom do piso, com o espelho em linha fina e a sombra discreta")
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


def biblioteca(Q, img):
    out = np.ascontiguousarray(img.copy())
    with em_quadro(Q):
        if Q.chave == "Terreo":
            out = B.guarda_roupas_terreo(out)
            out = B.camas_b(out, "Terreo", B.CAMAS_B)
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
PAREDES_F = {"cor": (8, 8, 8), "camadas": ("ARQ_PAREDE", "ARQ_ELEMENTOS FIXOS"),
             "pilar_redondo": {"cor": (128, 128, 130), "contorno": (62, 62, 64), "larg_px": 1.1}}


def paredes(Q, img):
    q = PAREDES_F
    a = Q.preencher(lambda d: d.get("layer") in q["camadas"] and d.get("fill") and max(d["fill"]) < 0.5, ss=4)
    out = img.astype(np.float32)
    out = out * (1 - a[..., None]) + np.float32(q["cor"]) * a[..., None]
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
    print(f"    paredes pretas no contorno do PDF; {n} pilares (os redondos em cinza, com o contorno fino)")
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
    # os canteiros (jardim de inverno, jardim do hall, floreira), pelas mesmas rotinas, no quadro
    jh = B.JARDIM_HALL
    X, Y = M @ np.array([jh["ponto"][0], jh["ponto"][1], 1.0])
    B.JARDIM_HALL = dict(jh, ponto=(int(round(X)), int(round(Y))))
    try:
        with em_quadro(Q):
            out = B.jardim_inverno(out)
            out = B.jardim_hall(out)
            out = B.floreira(out)
    finally:
        B.JARDIM_HALL = jh
    return out


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


def escadas_projecoes(Q, img):
    out = np.ascontiguousarray(img.copy())
    with em_quadro(Q):
        pa = AJ.PROJECOES_A
        AJ.PROJECOES_A = dict(pa, larg_px=pa["larg_px"] * Q.W / 2000)
        try:
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
        # a escada de 6 degraus (a de 9 é do Térreo e fica na hachura): os degraus do PDF em Bege Bahia e as linhas da
        # R14 (`retoque_terreo_casae.escada_linhas`), no quadro da prancha
        return degraus_bege(Q, np.ascontiguousarray(im.copy()), B.ESCADAS_S[:1])
    return [
        ("pisos", lambda im: pisos(Q, im, dentro=dentro)),
        ("bancadas", lambda im: bancadas(Q, im)),
        ("sauna", lambda im: bancos_sauna(Q, im)),
        ("pecas", lambda im: pecas_pdf(Q, im, ini, fora=[c["ducha"]] and [(c["ducha"][0] - 3, c["ducha"][1] - 3,
                                                                          c["canopla"][2] + 3, c["ducha"][3] + 3)])),
        ("tampas", lambda im: tampas_vasos(Q, im)),
        ("biblioteca", biblioteca_s),
        ("paredes", lambda im: paredes(Q, im)),
        ("soleiras", lambda im: soleiras(Q, im)),
        ("esquadrias", lambda im: B.esquadrias_final(im, chave, Q.pg, Q.p2q, Q.px_m)),
        ("escadas", escadas_s),
        ("hachura", lambda im: AJ.subsolo_hachurado(im, peg.astype(np.float32) / 255, Q.px_m)),
        ("rotulos", lambda im: rotulos(Q, im, B.rotulos_casab(Q.pg, Q.p2q2000), Q.q["ajustes"],
                                       granito=A.granito(im, Q.q.get("granito_lum_max", 125)))),
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
        ("tampas", lambda im: tampas_vasos(Q, im)),
        ("biblioteca", lambda im: biblioteca(Q, im)),
        ("carros", lambda im: carros(Q, im, M)),
        ("deck", lambda im: deck_detalhes(Q, im)),
        ("boxes", lambda im: boxes_granito(Q, im)),
        ("paredes", lambda im: paredes(Q, im)),
        ("soleiras", lambda im: soleiras(Q, im)),
        ("esquadrias", lambda im: B.esquadrias_final(ondas_fora(Q, im), chave, Q.pg, Q.p2q, Q.px_m)),
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

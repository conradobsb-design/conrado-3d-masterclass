#!/usr/bin/env python3
"""A final do Subsolo da Casa A refeita na resolução da prancha (3840 px, ~59,7 px/m), pelo motor das Casas B a D.

Pedidos do usuário (26/10/26), no Subsolo da Casa A:
- "Melhore o aspecto do Mármore travertino bruto em suas respectivas áreas" (o hall, a sauna com a antessala e os
  banhos feminino e masculino; o pátio é Bege Bahia desde o item 11 de 19/10);
- "Melhore a representação do banco em mármore travertino bruto da sauna";
- "Note que você usou o travertino na área do elevador. [...] deveria ter um elevador, assim como fizemos em outras
  casas" (a cabine de aço, como nas Casas B a D, com a soleira em inox);
- "Melhore a representação dos chuveiros"; "Melhore a representação dos armários do depósito - em marcenaria";
  "Melhore a representação das folhas contínuas dos boxes";
- "E faça os ajustes da auditoria" (as especificações de 26/10, `auditoria_2610.py`): as paredes em cinza 80 (resposta
  do usuário) e os pilares em preto; a escada com o S do PDF e a linha de percurso, os degraus demarcados; o rótulo do
  banho de serviço fora do box; a madeira da academia na escala das Casas B a D;
- "Cubas dos banhos de serviço em marrom granito: Mantem a bancada das cubas em mármore travertino bruto. Sanitarios
  em marrom, não branco. A parede que divide os banhos masculino e feminino deve ser representado como parede em
  cinza 80." (os banhos feminino e masculino: as cubas em granito marrom, a bancada em travertino bruto mais marcado
  que o piso, os vasos em marrom; a divisória entre os dois passa a parede, ao contrário do item 94 de 19/10);
- "Já o banho serviço tem piso em mármore bege bahia; cuba branca, bancada da cuba em marrom granito e chuveiro bem
  representado." e "louças de metais" (as louças e os metais do banho de serviço, nítidos, pelo PDF; o vaso dele
  fica branco, que não foi pedido em marrom).

A imagem de partida é a final aprovada do Subsolo no quadro de 3840 px, sem os rótulos (`rotulos_casaa.final_imagem`:
o ajuste levado ao quadro, com a hachura do Térreo fora da pegada). Cada item é redesenhado ali, pelo PDF (vetor) e
pela base chapada da legenda (6905 px), com as rotinas do `final3840_casab.py` e do `retoque_subsolo_casae.py`.

Uso (da pasta POE642_CasaA/scripts/):
  python3 final3840_casaa.py                 # a final do Subsolo com os rótulos
  python3 final3840_casaa.py --de banhos     # recomeça de uma etapa (as anteriores ficam em cache)
  python3 final3840_casaa.py --ate pisos     # para numa etapa (a final só é gravada quando todas rodam)
  python3 final3840_casaa.py --de rotulos --antes antes.png   # e os antes e depois de cada pedido
Saída: `renders/POE642_CasaA_PH_Subsolo_final_rotulos.png`, que vai ao `rodape_entrega.py --no-quadro`.
"""
import argparse
import json
import os
import sys
import tempfile
import time
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import final3840_casab as F                     # noqa: E402

B, AJ, A = F.B, F.AJ, F.A                        # A e AJ são os módulos da Casa A (rotulos_casaa, ajustes_casaa)
CASA = AQUI.parent
ETAPAS = Path(os.environ.get("POE642_CACHE", tempfile.gettempdir())) / "poe642_casaa_etapas"


# ----------------------------------------------------------------------------------------------------------------------
# O quadro da prancha, com os caminhos da Casa A (o `F.Quadro` aponta para a Casa B)
class QuadroA(F.Quadro):
    def __init__(self, chave):
        import pymupdf
        from opcoes_1pav_casae import quadro_pdf
        self.chave = chave
        q = self.q = A.PAVIMENTOS[chave]
        cfg = self.cfg = json.loads(A.CONFIG.read_text())
        self.base = (A.CONFIG.parent / cfg["entrega"]["pasta_bases"] / cfg["entrega"]["pavimentos"][chave]["base"]).resolve()
        self.pg = pymupdf.open(A.RAIZ / "_pdfs_cliente" / q["pdf"])[cfg["pavimentos"][chave]["pagina"]]
        at, lt = cv2.imread(str(self.base), cv2.IMREAD_GRAYSCALE).shape
        hb, wb = cv2.imread(str(A.CASA / q["sem_tela"]), cv2.IMREAD_GRAYSCALE).shape
        self.W = A.LARGURA
        self.H = round(at * self.W / lt)
        self.p2q = quadro_pdf(self.pg, cfg, lt, at, wb, hb, self.W)
        self.p2q2000 = quadro_pdf(self.pg, cfg, lt, at, wb, hb, 2000)
        (a, b), (c, d) = self.p2q(0, 0), self.p2q(56.69, 0)
        self.px_m = float(np.hypot(c - a, d - b))
        # a base 16:9 da entrega é a própria base chapada da legenda (as cores do prompt)
        self.chapada = cv2.resize(cv2.imread(str(self.base)), (self.W, self.H), interpolation=cv2.INTER_NEAREST)
        self._desenhos = None

    def q2p(self, x, y):
        """quadro (px) -> pt do PDF (o p2q é afim)."""
        (a, b), (c, d), (e, f) = self.p2q(0, 0), self.p2q(100, 0), self.p2q(0, 100)
        M = np.array([[(c - a) / 100, (e - a) / 100], [(d - b) / 100, (f - b) / 100]])
        return tuple(np.linalg.solve(M, np.array([x - a, y - b])))


PT_PX = 59.70590031258779 / 56.69                  # px do quadro por pt do PDF
ESC_E = PT_PX / 0.5483                              # o px do quadro sobre o px do render da Casa E (as peças do retoque)


def tela(out, Q, caixa_pt, folga=4):
    """A `Tela` do retoque da Casa E no quadro da prancha (SS = 8): o raio dos cantos em pt na escala daqui."""
    from retoque_subsolo_casae import Tela, SS

    class TelaA(Tela):
        def ret(self, r, raio_pt=0.0):
            m = self.vazia()
            (a, b), (c, d) = self.pt(r[0], r[1]), self.pt(r[2], r[3])
            a, b, c, d = (int(round(v)) for v in (a, b, c, d))
            rr = int(min(round(raio_pt * PT_PX * SS), (c - a) // 2, (d - b) // 2))
            if rr <= 0:
                cv2.rectangle(m, (a, b), (c, d), 255, -1)
                return m
            cv2.rectangle(m, (a + rr, b), (c - rr, d), 255, -1)
            cv2.rectangle(m, (a, b + rr), (c, d - rr), 255, -1)
            for cx, cy in ((a + rr, b + rr), (c - rr, b + rr), (a + rr, d - rr), (c - rr, d - rr)):
                cv2.circle(m, (cx, cy), rr, 255, -1)
            return m

        def poli(self, pts_pt):
            m = self.vazia()
            cv2.fillPoly(m, [np.int32(np.round([self.pt(x, y) for x, y in pts_pt]))], 255)
            return m

        def caminhos(self, d):
            """Os subcaminhos de um desenho do PDF, preenchidos (SS)."""
            m = self.vazia()
            for c in AJ.caminhos_pdf(d, self.pt):
                if len(c) >= 3:
                    cv2.fillPoly(m, [np.int32(np.round(c))], 255)
            return m

        def linha(self, pts_pt, larg_px):
            m = self.vazia()
            cv2.polylines(m, [np.int32(np.round([self.pt(x, y) for x, y in pts_pt]))], False, 255,
                          max(1, int(round(larg_px * SS))), cv2.LINE_AA)
            return m

        def pintar_img(self, m, cor_img, forca=1.0):
            """Pinta com uma imagem de cor (h x w x 3, na resolução de saída) na máscara."""
            a = self.reduzir(m)[..., None] * forca
            self.reg = self.reg * (1 - a) + cor_img * a

        def grade(self):
            """As coordenadas (pt do PDF) do centro de cada px da janela: (X, Y), h x w."""
            ys, xs = np.mgrid[0:self.h, 0:self.w].astype(np.float64)
            (a, b) = Q.q2p(self.x0 + 0.5, self.y0 + 0.5)
            (c, d) = Q.q2p(self.x0 + 1.5, self.y0 + 1.5)
            return a + xs * (c - a), b + ys * (d - b)

    return TelaA(out, Q.p2q, caixa_pt, folga=folga)


def sombra_q(tl, m, forca=0.28, dist=1.15, sigma=1.35):
    """A sombra curta das peças (luz do alto à direita), em px do quadro."""
    tl.sombra(m, dx=-dist, dy=dist, sigma=sigma, forca=forca)


def ret_aa(Q, r):
    """O retângulo r (pt) no quadro, com a cobertura exata de cada px (0 a 1)."""
    (x0, y0), (x1, y1) = Q.p2q(r[0], r[1]), Q.p2q(r[2], r[3])
    x0, x1 = sorted((x0, x1))
    y0, y1 = sorted((y0, y1))
    px = np.arange(Q.W, dtype=np.float32)
    py = np.arange(Q.H, dtype=np.float32)
    cx = np.clip(np.minimum(px + 1, x1) - np.maximum(px, x0), 0, 1)
    cy = np.clip(np.minimum(py + 1, y1) - np.maximum(py, y0), 0, 1)
    return cy[:, None] * cx[None, :]


def paredes_pdf(Q):
    """O que não é piso (0 a 1): as paredes, as esquadrias e as folhas das portas (os preenchimentos da ARQ_PAREDE,
    escuros e claros) e os traços retos dela; os arcos das portas (só curvas) não, porque não aparecem (R3)."""
    if getattr(Q, "_paredes", None) is not None:
        return Q._paredes
    ss = 4
    m = (Q.preencher(lambda d: d.get("layer") == "ARQ_PAREDE", ss=ss) * 255).astype(np.uint8)
    tr = np.zeros((Q.H * ss, Q.W * ss), np.uint8)
    for d in Q.desenhos:
        if d.get("layer") == "ARQ_PAREDE" and d["type"] == "s" and all(it[0] == "l" for it in d["items"]):
            for c in Q.caminhos(d):
                cv2.polylines(tr, [np.int32(np.round(c * ss))], False, 255, max(1, round(0.6 * ss)))
    tr = cv2.resize(tr, (Q.W, Q.H), interpolation=cv2.INTER_AREA)
    Q._paredes = np.maximum(m, tr).astype(np.float32) / 255
    return Q._paredes


def inicial(Q):
    """A final aprovada do Subsolo no quadro, sem os rótulos (com a hachura do Térreo fora da pegada), em cache."""
    ETAPAS.mkdir(parents=True, exist_ok=True)
    c = ETAPAS / f"{Q.chave}_ini.png"
    if c.exists():
        return cv2.imread(str(c))
    img = A.final_imagem(Q.chave)[0]
    cv2.imwrite(str(c), img)
    return img


# ----------------------------------------------------------------------------------------------------------------------
# 1. Os pisos (pedidos 1 e 7 de 26/10; E11), nos preenchimentos da ARQ_CONTRAPISO (pt), sem as paredes, as esquadrias e
# as folhas das portas que a final mostra (`nao_piso`). Tudo o que fica nos banhos, na sauna, no hall e no banho de
# serviço é redesenhado depois (bancadas, louças, chuveiros, boxes, o banco), então o piso passa por baixo de tudo ali.
# - o travertino bruto (hall, sauna, antessala, banhos feminino e masculino; pedido 1): a foto da biblioteca na escala
#   da prancha, como nas Casas B a D, no creme delas (a sauna da Casa B, RGB ~228, 216, 204; a da Casa A estava rosada,
#   ~207, 191, 177), com os veios horizontais longos e os poros pequenos do travertino bruto (`travertino_bruto`);
# - o Bege Bahia (pátio, circulação, depósito e o banho de serviço, que era Barlavento): a foto da biblioteca no tom das
#   Casas B a D (`C.TONS_C`); no banho de serviço, a luz vem da circulação e do pátio (o verde do Barlavento não entra);
# - a madeira da academia (E11): as réguas do vinílico das Casas B a D (~10 a 12 cm, com as emendas), no tom do carvalho
#   claro aprovado; os aparelhos ficam os da final (achados na própria imagem: pretos ou cromados, sem a cor da
#   madeira), com a sombra curta de novo; a projeção junto à parede de baixo (DOC_LINHAS) volta na linha clara de antes.
# A ordem conta: o retângulo do pátio no PDF entra na sauna, e o travertino vem por cima.
PISOS_A = {
    "Bege Bahia": {"rets": [(918.5, 1049.5, 1017.8, 1230.9), (1017.8, 1049.5, 1666.9, 1230.9),
                            (907.2, 1219.6, 1156.7, 1786.5)],
                   "textura": "bege", "forca": None, "sig_m": 1.5, "semente": 2611,
                   "tom": (187, 211, 230)},                                 # BGR, o de `C.TONS_C`
    "madeira": {"rets": [(1156.7, 1230.9, 1666.9, 1664.6)], "textura": "vinilico", "forca": None, "sig_m": 1.0,
                "semente": 2612},
    "travertino": {"rets": [(1666.9, 1230.9, 2021.2, 1384.0), (1017.8, 1656.1, 1196.3, 1786.5),
                            (1196.3, 1656.1, 1281.4, 1786.5), (1281.4, 1656.1, 1491.1, 1786.5),
                            (1491.1, 1656.1, 1666.9, 1786.5)],
                   "textura": "travertino", "forca": 1.6, "sig_m": 3.0, "semente": 2610,
                   "tom": (204, 216, 228)},                                 # BGR, a sauna da Casa B
}
# o travertino bruto: a foto da biblioteca (força 1,6, como nas Casas B a D) com os veios horizontais (`veio`: o fio
# fino, ~2,5 cm de altura e ~35 cm de comprimento; `faixa`: as faixas largas, ~8 cm por ~90 cm) e os poros (por m²,
# 1 a 4 cm, alongados no veio, `poro_esc` mais escuros)
TRAVERTINO = {"piso": {"veio": 0.012, "faixa": 0.02, "poros": 10, "poro_esc": 0.08},
              "bancada": {"veio": 0.02, "faixa": 0.035, "poros": 22, "poro_esc": 0.14}}
# o que é peça na final (paredes, vidros, batentes): os px neutros (o piso tem cor: travertino, Bege Bahia, Barlavento,
# madeira); a peça do PDF que a final mostra como piso (as folhas das portas que a base tirou) vira piso
NEUTRO = {"croma_max": 16, "fracao": 0.5}
# os preenchimentos da ARQ_BANCADAS que ficam como estão (o nicho na parede entre o banho de serviço e a circulação) e
# a soleira de Bege Bahia da academia para o hall (pente fino de 21/10, R13; a do elevador vira inox, `ELEVADOR`)
BANCADAS_FICAM = [(1008.1, 1082.1, 1013.8, 1099.1)]
SOLEIRAS_FICAM = [(1655.55, 1232.34, 1666.89, 1371.24)]
APARELHOS = {"croma_max": 26, "lum_max": 95, "area_min": 60, "borda_px": 22, "sombra": (0.30, 1.4, 1.6)}   # força, dist, sigma
PROJECAO_ACADEMIA = {"pt": (1377.8, 1627.8, 1576.2, 1650.4), "cor": (200, 210, 220), "larg_px": 1.4, "forca": 0.75}


def _dentro(r, a):
    return a[0] >= r[0] - 0.5 and a[1] >= r[1] - 0.5 and a[2] <= r[2] + 0.5 and a[3] <= r[3] + 0.5


def nao_piso(Q):
    """O que não é piso (bool): cada peça da ARQ_PAREDE (preenchimento ou traço reto) que a final mostra (mais da metade
    dos px dela neutros na imagem de partida, `NEUTRO`), com 1 px de folga; e o nicho da ARQ_BANCADAS."""
    if getattr(Q, "_nao_piso", None) is not None:
        return Q._nao_piso
    q = NEUTRO
    ini = Q.ini.astype(np.int16)
    neutro = (ini.max(axis=2) - ini.min(axis=2)) <= q["croma_max"]
    ss = 4
    out = np.zeros((Q.H, Q.W), np.float32)
    n_tira = 0
    for d in Q.desenhos:
        if d.get("layer") != "ARQ_PAREDE":
            continue
        reta = d["type"] == "s" and all(it[0] == "l" for it in d["items"])
        if d["type"] not in ("f", "fs") and not reta:
            continue
        cs = Q.caminhos(d)
        if not cs:
            continue
        pts = np.vstack(cs)
        x0, y0 = np.floor(pts.min(axis=0)).astype(int) - 2
        x1, y1 = np.ceil(pts.max(axis=0)).astype(int) + 3
        x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, Q.W), min(y1, Q.H)
        if x1 <= x0 or y1 <= y0:
            continue
        m = np.zeros(((y1 - y0) * ss, (x1 - x0) * ss), np.uint8)
        for c in cs:
            p_ = np.int32(np.round((c - (x0, y0)) * ss))
            if reta:
                cv2.polylines(m, [p_], False, 255, max(1, round(0.6 * ss)))
            elif len(c) >= 3:
                cv2.fillPoly(m, [p_], 255)
        a = cv2.resize(m, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
        dentro = a > 0.5
        if not dentro.any():
            dentro = a > 0.1
        r = d["rect"]
        if any(_dentro(z, (r.x0, r.y0, r.x1, r.y1)) for z in PORTAS_VIDRO["refaz_pt"]):
            n_tira += 1                                       # redesenhada depois (`portas_vidro`)
            continue
        if dentro.any() and neutro[y0:y1, x0:x1][dentro].mean() < q["fracao"]:
            n_tira += 1                                       # a final mostra piso ali
            continue
        out[y0:y1, x0:x1] = np.maximum(out[y0:y1, x0:x1], a)
    par = cv2.dilate((out > 0.05).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    fica = Q.preencher(lambda d: d.get("layer") == "ARQ_BANCADAS" and any(
        _dentro(r, tuple(d["rect"])) for r in BANCADAS_FICAM), ss=4) > 0.02
    for r in SOLEIRAS_FICAM:
        fica |= ret_aa(Q, r) > 0.02
    Q._nao_piso = par | fica
    print(f"    {n_tira} peças da ARQ_PAREDE que a final mostra como piso (as folhas tiradas pela base) viram piso")
    return Q._nao_piso


def mascara_piso(Q, rets, fora=None):
    """Os retângulos (pt) sem o que não é piso (e sem `fora`, bool)."""
    m = np.zeros((Q.H, Q.W), np.float32)
    for r in rets:
        m = np.maximum(m, ret_aa(Q, r))
    out = (m > 0.5) & ~nao_piso(Q)
    if fora is not None:
        out &= ~fora
    return out


def aparelhos(Q, ini):
    """Os aparelhos da academia na imagem de partida: pretos ou cromados (sem a cor da madeira), sem os pingos."""
    from scipy import ndimage
    q = APARELHOS
    r = F.ret_q(Q, PISOS_A["madeira"]["rets"][0])
    reg = ini[r[1]:r[3], r[0]:r[2]].astype(np.int16)
    croma = reg.max(axis=2) - reg.min(axis=2)
    m = ((croma < q["croma_max"]) | (reg.mean(axis=2) < q["lum_max"])).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    h, w = m.shape
    b = q["borda_px"]
    m = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= q["area_min"]
                      and st[i, cv2.CC_STAT_LEFT] > b and st[i, cv2.CC_STAT_TOP] > b
                      and st[i, cv2.CC_STAT_LEFT] + st[i, cv2.CC_STAT_WIDTH] < w - b
                      and st[i, cv2.CC_STAT_TOP] + st[i, cv2.CC_STAT_HEIGHT] < h - b])
    m = ndimage.binary_fill_holes(m)
    out = np.zeros((Q.H, Q.W), bool)
    out[r[1]:r[3], r[0]:r[2]] = cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    return out & ~nao_piso(Q)


def travertino_bruto(Q, h, w, semente, veio, faixa, poros, poro_esc, forca=1.6):
    """O desenho do travertino bruto (média ~1), h x w px: a foto da biblioteca, os veios e os poros."""
    sys.path.insert(0, str(A.RAIZ / "_texturas"))
    from texturas import textura
    px_m = Q.px_m
    rng = np.random.default_rng(semente)
    T = textura("travertino", px_m, h, w, semente=semente).astype(np.float32)
    det = cv2.GaussianBlur(T, (0, 0), 0.6) / np.maximum(cv2.GaussianBlur(T, (0, 0), 3.0 * px_m), 1)
    D = 1 + forca * (det.mean(axis=2) - 1)
    v = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), sigmaX=0.35 * px_m, sigmaY=0.025 * px_m)
    v2 = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), sigmaX=0.9 * px_m, sigmaY=0.08 * px_m)
    D = D + veio * v / max(v.std(), 1e-6) + faixa * v2 / max(v2.std(), 1e-6)
    n = int(poros * h * w / px_m ** 2)
    P = np.zeros((h * 4, w * 4), np.float32)
    for x, y, c, e in zip(rng.uniform(0, w * 4, n), rng.uniform(0, h * 4, n), rng.uniform(2, 9, n),
                          rng.uniform(0.4, 1.0, n)):
        cv2.ellipse(P, (int(x), int(y)), (int(c), 2), 0, 0, 360, float(e), -1, cv2.LINE_AA)
    P = cv2.resize(P, (w, h), interpolation=cv2.INTER_AREA)
    return D * (1 - poro_esc * np.clip(P * 4, 0, 1))


def piso_travertino(Q, img, m, p, estilo="piso"):
    """O travertino bruto na máscara m: a luz larga do lugar no tom `p["tom"]`, vezes o desenho."""
    ys, xs = np.nonzero(m)
    y0, x0, y1, x1 = ys.min(), xs.min(), ys.max() + 1, xs.max() + 1
    L = F.luz_robusta(img, m, p["sig_m"] * Q.px_m)
    L = L * (np.float32(p["tom"]) / np.maximum(np.median(L[m], axis=0), 1.0))
    D = travertino_bruto(Q, y1 - y0, x1 - x0, p["semente"], forca=p["forca"], **TRAVERTINO[estilo])
    novo = img.astype(np.float32).copy()
    novo[y0:y1, x0:x1] = L[y0:y1, x0:x1] * D[..., None]
    return novo


def projecao_academia(Q, img):
    q = PROJECAO_ACADEMIA
    x0, y0, x1, y1 = q["pt"]
    e = q["larg_px"] / PT_PX
    a = np.zeros((Q.H, Q.W), np.float32)
    for r in ((x0, y0, x1, y0 + e), (x0, y0, x0 + e, y1), (x1 - e, y0, x1, y1)):   # embaixo é a parede
        a = np.maximum(a, ret_aa(Q, r))
    a = a[..., None] * q["forca"]
    return img * (1 - a) + np.float32(q["cor"]) * a


def pisos(Q, img, ini):
    Q.ini = ini
    out = img.astype(np.float32)
    ap = aparelhos(Q, ini)
    for nome, p in PISOS_A.items():
        m = mascara_piso(Q, p["rets"], fora=ap if nome == "madeira" else None)
        if nome == "travertino":
            novo = piso_travertino(Q, out, m, p)
        else:
            novo = F.piso_textura(Q, out, m, p["textura"], p["forca"], p["sig_m"], p["semente"])
            if p.get("tom") is not None:
                novo = novo * (np.float32(p["tom"]) / np.maximum(np.median(novo[m], axis=0), 1.0))
        out = F.pousar(out, novo, m, suave=0)
        if nome == "madeira":
            # a sombra curta dos aparelhos no piso novo e a projeção junto à parede de baixo
            f, dist, sig = APARELHOS["sombra"]
            s = cv2.warpAffine(ap.astype(np.float32), np.float32([[1, 0, -dist], [0, 1, dist]]), (Q.W, Q.H))
            s = cv2.GaussianBlur(s, (0, 0), sig) * m
            out *= (1 - f * s)[..., None]
            out = projecao_academia(Q, out)
        print(f"    {nome}: {m.sum() / Q.px_m ** 2:.1f} m² ({p['textura']}, na escala da prancha)")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
# 2. Os banhos (pedidos 4, 6 e 8 a 10 de 26/10), na geometria do PDF (pt), desenhados na resolução da prancha:
# - banhos feminino e masculino: a bancada em travertino bruto, mais marcada que o piso do mesmo travertino (E9: o
#   desenho do travertino mais forte, o tom um pouco mais fundo, a borda fina no tom escurecido da pedra e a sombra
#   curta); a cuba em granito marrom (a borda polida, a bacia mais funda com a sombra por dentro, a válvula), com a
#   torneira cromada na prateleira de trás; o vaso em louça marrom (no contorno do PDF, com o volume e o tampo); a
#   válvula de descarga cromada na parede;
# - banho de serviço: a bancada em granito marrom (o polígono do PDF, com o recorte da cuba), a cuba de semiencaixe
#   branca, a torneira cromada, o vaso branco (não foi pedido em marrom) e a descarga;
# - os chuveiros (antessala, banho feminino e banho de serviço): a placa quadrada cromada com os furinhos e o brilho da
#   luz do alto à direita, o braço cromado com o brilho no eixo e a canopla na parede, com a sombra curta; no banho de
#   serviço a ducha do PDF tem só 7 cm e vira a placa de 19 cm das outras, no mesmo centro;
# - os boxes (pedido 6): as duas folhas de vidro de correr do PDF inteiras (`AJ.folhas_box`), cada uma uma faixa de
#   vidro de 1,3 px com as faces finas, um pouco mais afastadas que no PDF (lá ficam a 0,85 pt e viravam uma linha só),
#   com a sombra curta, e o trilho tracejado no vão até a parede.
GRANITO_CUBA = {"rim": 1.10, "bacia": 0.80, "sombra_bacia": (0.35, 2.2), "contorno": (34, 44, 58), "larg": 0.45}
CROMO = {"escuro": (122, 126, 130), "meio": (190, 193, 196), "claro": (238, 240, 242), "contorno": (88, 92, 96)}
BANHOS = {
    "trav_bancada": {"tom": (172, 190, 210), "borda": 0.62, "larg": 0.7, "sombra": 0.42, "semente": 2620},
    "fem_masc": [
        {"nome": "feminino", "bancada": (1293.9, 1746.8, 1380.6, 1775.2),
         "cuba": (1307.2, 1748.5, 1366.1, 1775.2), "bacia": (1308.3, 1749.7, 1365.0, 1768.4),
         "torneira": (1335.6, 1762.9, 1337.7, 1771.0), "base": (1336.65, 1771.2, 1.6),
         "vaso": (1396.1, 1746.1, 1416.1, 1775.2), "descarga": (1402.4, 1773.9, 1409.8, 1775.2)},
        {"nome": "masculino", "bancada": (1557.5, 1746.8, 1654.4, 1775.2),
         "cuba": (1573.3, 1748.5, 1639.7, 1775.2), "bacia": (1574.5, 1749.7, 1638.5, 1768.4),
         "torneira": (1606.3, 1762.9, 1608.4, 1771.0), "base": (1607.35, 1771.2, 1.6),
         "vaso": (1518.0, 1746.1, 1538.0, 1775.2), "descarga": (1524.3, 1773.9, 1531.7, 1775.2)},
    ],
    "vaso_marrom": {"louca": (66, 88, 120), "contorno": (30, 40, 54), "tampo": (98, 124, 158)},   # BGR
    "servico": {"bancada": (929.9, 1168.6, 952.6, 1219.6), "cuba": (936.7, 1182.8, 959.3, 1205.4),
                "torneira": (941.0, 1193.2, 948.4, 1194.9), "base": (939.9, 1194.1, 1.5),
                "vaso": (929.9, 1135.2, 961.0, 1156.5), "descarga": (929.9, 1142.7, 932.3, 1149.0)},
    "chuveiros": [
        {"nome": "antessala", "ducha": (1233.3, 1747.7, 1244.5, 1758.9), "braco": (1238.2, 1752.2, 1239.6, 1774.6),
         "canopla": (1236.9, 1773.9, 1240.9, 1775.2)},
        {"nome": "banho feminino", "ducha": (1457.2, 1747.7, 1468.4, 1758.9), "braco": (1462.1, 1752.2, 1463.5, 1774.6),
         "canopla": (1460.8, 1773.9, 1464.8, 1775.2)},
        {"nome": "banho de serviço", "ducha": (933.4, 1086.6, 944.2, 1097.4), "braco": (929.9, 1091.4, 938.8, 1092.7),
         "canopla": (929.9, 1090.0, 931.2, 1094.1)},
    ],
    "box": {"vidro": (218, 214, 204), "face": (104, 108, 112), "larg_px": 1.5, "afasta_px": 0.9, "face_px": 0.45,
            "sombra": 0.20, "trilho": (150, 152, 154), "trilho_px": 0.7, "trilho_min_pt": 1.5},
}


def _granito(Q, tl, semente):
    import fontes_procedurais as FP
    return FP.granito_referencia(tl.h, tl.w, Q.px_m, semente=semente).astype(np.float32)


def bancada_pedra(Q, out, r, textura, borda_mult, larg_px, sombra, poli=None):
    """Uma bancada (ret r em pt ou o polígono `poli`) com a textura dada (h x w x 3 da janela), a borda fina no tom
    escurecido da própria pedra e a sombra curta."""
    tl = tela(out, Q, r, folga=6)
    m = tl.poli(poli) if poli is not None else tl.ret(r)
    sombra_q(tl, m, forca=sombra)
    tl.pintar_img(m, textura(tl))
    k = max(1, int(round(larg_px * 8)))
    borda = m & ~cv2.erode(m, np.ones((k, k), np.uint8))
    tl.pintar_img(borda, tl.reg * borda_mult)
    return tl.gravar()


def cuba_granito(Q, out, c, semente):
    """A cuba em granito marrom: a borda polida, a bacia mais funda com a sombra por dentro (no alto e à direita, a luz
    vem de lá), a prateleira de trás, a válvula cromada."""
    q = GRANITO_CUBA
    tl = tela(out, Q, c["cuba"], folga=4)
    G = _granito(Q, tl, semente)
    m = tl.ret(c["cuba"], 1.2)
    tl.pintar_img(m, G * q["rim"])
    b = tl.ret(c["bacia"], 2.6)
    # a bacia: mais funda, com a sombra das bordas de cima e da direita por dentro
    dist = cv2.distanceTransform(b, cv2.DIST_L2, 5) / 8
    X, Y = tl.grade()
    x0, y0, x1, y1 = c["bacia"]
    lado = np.clip(((X - x0) / (x1 - x0) + (y1 - Y) / (y1 - y0)) / 2, 0, 1)        # 1 no alto à direita
    f, alc = q["sombra_bacia"]
    d_out = cv2.resize(dist.astype(np.float32), (tl.w, tl.h), interpolation=cv2.INTER_AREA)
    prof = 1 - f * np.clip(1 - d_out / alc, 0, 1) * (0.45 + 0.55 * lado)
    tl.pintar_img(b, G * q["bacia"] * prof[..., None])
    tl.contorno(b, q["larg"], q["contorno"])
    tl.contorno(m, q["larg"], q["contorno"])
    # a válvula, no meio da bacia
    v = tl.vazia()
    cx, cy = tl.pt((x0 + x1) / 2, (y0 + y1) / 2)
    cv2.circle(v, (int(cx), int(cy)), int(1.1 * PT_PX * 8), 255, -1, cv2.LINE_AA)
    tl.pintar(v, CROMO["meio"])
    tl.contorno(v, 0.35, CROMO["contorno"])
    return tl.gravar()


def torneira(Q, out, bico, base):
    """A torneira cromada: a base redonda (cx, cy, raio em pt) e o bico (ret em pt), com o brilho e a sombra curta."""
    bx, by, br = base
    caixa = (min(bico[0], bx - br), min(bico[1], by - br), max(bico[2], bx + br), max(bico[3], by + br))
    tl = tela(out, Q, caixa, folga=4)
    m = tl.ret(bico, 0.7)
    sombra_q(tl, m, forca=0.30, dist=0.9, sigma=0.8)
    tl.pintar(m, CROMO["escuro"])
    x0, y0, x1, y1 = bico
    if (x1 - x0) >= (y1 - y0):
        tl.pintar(tl.ret((x0, y0 + (y1 - y0) * 0.15, x1, (y0 + y1) / 2), 0.4), CROMO["claro"])
    else:
        tl.pintar(tl.ret(((x0 + x1) / 2, y0, x1 - (x1 - x0) * 0.15, y1), 0.4), CROMO["claro"])
    tl.contorno(m, 0.3, CROMO["contorno"])
    b = tl.vazia()
    cx, cy = tl.pt(bx, by)
    cv2.circle(b, (int(cx), int(cy)), int(br * PT_PX * 8), 255, -1, cv2.LINE_AA)
    sombra_q(tl, b, forca=0.25, dist=0.8, sigma=0.7)
    tl.pintar(b, CROMO["meio"])
    hl = tl.vazia()
    cv2.circle(hl, (int(cx + 0.3 * br * PT_PX * 8), int(cy - 0.3 * br * PT_PX * 8)), int(0.45 * br * PT_PX * 8), 255, -1,
               cv2.LINE_AA)
    tl.pintar(hl, CROMO["claro"], 0.8)
    tl.contorno(b, 0.3, CROMO["contorno"])
    return tl.gravar()


def placa_cromada(Q, out, r, raio_pt=0.5):
    """Uma peça cromada pequena na parede (a descarga, a canopla): o cromo com o brilho e o contorno fino."""
    tl = tela(out, Q, r, folga=3)
    m = tl.ret(r, raio_pt)
    sombra_q(tl, m, forca=0.25, dist=0.8, sigma=0.7)
    tl.pintar(m, CROMO["meio"])
    x0, y0, x1, y1 = r
    if (x1 - x0) >= (y1 - y0):
        tl.pintar(tl.ret((x0 + 0.3, y0, x1 - 0.3, (y0 + y1) / 2)), CROMO["claro"], 0.7)
    else:
        tl.pintar(tl.ret(((x0 + x1) / 2, y0 + 0.3, x1, y1 - 0.3)), CROMO["claro"], 0.7)
    tl.contorno(m, 0.3, CROMO["contorno"])
    return tl.gravar()


def vaso(Q, out, caixa, parede, cores=None):
    """O vaso do `retoque_subsolo_casae` na escala da prancha, em louça branca ou nas `cores` dadas (marrom)."""
    import retoque_subsolo_casae as R
    guardar = (R.LOUCA, R.LOUCA_CONTORNO, R.VASO, R.SOMBRA)
    try:
        R.SOMBRA = {k: v * (ESC_E if k != "forca" else 1) for k, v in R.SOMBRA.items()}
        R.VASO = dict(R.VASO, recuo=R.VASO["recuo"] * ESC_E, volume=(R.VASO["volume"][0], R.VASO["volume"][1] * ESC_E),
                      volume_tampo=(R.VASO["volume_tampo"][0], R.VASO["volume_tampo"][1] * ESC_E))
        if cores:
            R.LOUCA, R.LOUCA_CONTORNO = cores["louca"], cores["contorno"]
            R.VASO = dict(R.VASO, cor_tampo=cores["tampo"])
        return R.vaso(out, Q.pg, Q.p2q, caixa, parede)
    finally:
        R.LOUCA, R.LOUCA_CONTORNO, R.VASO, R.SOMBRA = guardar


def cuba_branca(Q, out, c):
    """A cuba de semiencaixe em louça branca: a aba, a bacia da borda ao fundo, a válvula."""
    from retoque_terreo_casab import BACIA_BORDA, BACIA_FUNDO, LOUCA, LOUCA_CONTORNO
    tl = tela(out, Q, c, folga=4)
    m = tl.ret(c, 3.0)
    sombra_q(tl, m, forca=0.30)
    tl.pintar(m, LOUCA)
    x0, y0, x1, y1 = c
    for i in range(7):
        k = i / 6
        cor = tuple(BACIA_BORDA[j] * (1 - k) + BACIA_FUNDO[j] * k for j in range(3))
        ins = 2.2 + k * 3.2
        tl.pintar(tl.ret((x0 + ins, y0 + ins, x1 - ins, y1 - ins), max(0.8, 3.0 - k * 1.5)), cor)
    tl.contorno(m, 0.45, LOUCA_CONTORNO)
    tl.contorno(tl.ret((x0 + 2.2, y0 + 2.2, x1 - 2.2, y1 - 2.2), 2.4), 0.35, (196, 199, 201))
    v = tl.vazia()
    cx, cy = tl.pt((x0 + x1) / 2, (y0 + y1) / 2)
    cv2.circle(v, (int(cx), int(cy)), int(1.1 * PT_PX * 8), 255, -1, cv2.LINE_AA)
    tl.pintar(v, CROMO["meio"])
    tl.contorno(v, 0.3, CROMO["contorno"])
    return tl.gravar()


def chuveiro(Q, out, c):
    """O chuveiro visto de cima: o braço cromado (com o brilho no eixo) até a canopla na parede e a placa quadrada
    cromada, com o brilho da luz do alto à direita, os furinhos e a sombra curta."""
    caixa = tuple(f(c[k][i] for k in ("ducha", "braco", "canopla"))
                  for i, f in ((0, min), (1, min), (2, max), (3, max)))
    tl = tela(out, Q, caixa, folga=5)
    b = tl.ret(c["braco"], 0.5)
    sombra_q(tl, b, forca=0.30, dist=0.9, sigma=0.8)
    tl.pintar(b, CROMO["escuro"])
    x0, y0, x1, y1 = c["braco"]
    if (x1 - x0) >= (y1 - y0):
        tl.pintar(tl.ret((x0, (y0 + y1) / 2 - 0.25, x1, (y0 + y1) / 2 + 0.2)), CROMO["claro"])
    else:
        tl.pintar(tl.ret(((x0 + x1) / 2 - 0.2, y0, (x0 + x1) / 2 + 0.25, y1)), CROMO["claro"])
    cp = tl.ret(c["canopla"], 0.5)
    tl.pintar(cp, CROMO["meio"])
    tl.contorno(cp, 0.3, CROMO["contorno"])
    d = tl.ret(c["ducha"], 1.6)
    sombra_q(tl, d, forca=0.34, dist=1.2, sigma=1.1)
    X, Y = tl.grade()
    x0, y0, x1, y1 = c["ducha"]
    u = np.clip((X - x0) / (x1 - x0), 0, 1)
    v = np.clip((y1 - Y) / (y1 - y0), 0, 1)
    t = (u + v) / 2                                                       # 1 no canto de cima à direita
    cor = np.float32(CROMO["escuro"]) * (1 - t[..., None]) + np.float32(CROMO["claro"]) * t[..., None]
    tl.pintar_img(d, cor)
    # o miolo um pouco rebaixado e os furinhos
    ins = 1.6
    mi = tl.ret((x0 + ins, y0 + ins, x1 - ins, y1 - ins), 1.0)
    tl.pintar(mi, CROMO["meio"], 0.55)
    furos = tl.vazia()
    n = 5
    for i in range(n):
        for j in range(n):
            fx = x0 + ins + 0.9 + (x1 - x0 - 2 * ins - 1.8) * i / (n - 1)
            fy = y0 + ins + 0.9 + (y1 - y0 - 2 * ins - 1.8) * j / (n - 1)
            px_, py_ = tl.pt(fx, fy)
            cv2.circle(furos, (int(px_), int(py_)), int(0.38 * PT_PX * 8), 255, -1, cv2.LINE_AA)
    tl.pintar(furos, CROMO["escuro"], 0.75)
    tl.contorno(mi, 0.3, (150, 154, 158))
    tl.contorno(d, 0.45, CROMO["contorno"])
    return tl.gravar()


def boxes(Q, out):
    q = BANHOS["box"]
    n = 0
    for box in AJ.folhas_box(Q.pg):
        meio = box["meio"]
        lado = q["afasta_px"] / PT_PX
        e = q["larg_px"] / PT_PX / 2
        for k, f in enumerate(sorted(box["folhas"], key=lambda f: (f[1] + f[3]) / 2 if box["hor"] else (f[0] + f[2]) / 2)):
            c = meio + (-lado if k == 0 else lado) / 2 * 1.0
            r = (f[0], c - e, f[2], c + e) if box["hor"] else (c - e, f[1], c + e, f[3])
            tl = tela(out, Q, r, folga=5)
            m = tl.ret(r)
            sombra_q(tl, m, forca=q["sombra"], dist=0.9, sigma=0.8)
            tl.pintar(m, q["vidro"])
            tl.contorno(m, q["face_px"], q["face"])
            out = tl.gravar()
            n += 1
        for a0, a1 in box["trilho"]:
            if a1 - a0 < q["trilho_min_pt"]:
                continue
            w = q["trilho_px"] / PT_PX / 2
            r = (a0, meio - w, a1, meio + w) if box["hor"] else (meio - w, a0, meio + w, a1)
            tl = tela(out, Q, r, folga=3)
            tl.pintar(tl.ret(r), q["trilho"], 0.85)
            out = tl.gravar()
    print(f"    boxes: {n} folhas de vidro contínuas do PDF, com as faces finas, a sombra curta e o trilho no vão")
    return out


def banhos(Q, img):
    q = BANHOS
    out = np.ascontiguousarray(img.copy())
    tb = q["trav_bancada"]
    for i, c in enumerate(q["fem_masc"]):
        def textura(tl, r=c["bancada"], s=tb["semente"] + i):
            D = travertino_bruto(Q, tl.h, tl.w, s, **TRAVERTINO["bancada"])
            return np.float32(tb["tom"]) * D[..., None]
        out = bancada_pedra(Q, out, c["bancada"], textura, tb["borda"], tb["larg"], tb["sombra"])
        out = cuba_granito(Q, out, c, 2630 + i)
        out = torneira(Q, out, c["torneira"], c["base"])
        out = vaso(Q, out, c["vaso"], "baixo", q["vaso_marrom"])
        out = placa_cromada(Q, out, c["descarga"])
        print(f"    banho {c['nome']}: bancada em travertino bruto, cuba em granito marrom, torneira, vaso marrom")
    sv = q["servico"]
    d = next(d for d in Q.desenhos if d.get("layer") == "ARQ_BANCADAS" and d["type"] in ("f", "fs")
             and _dentro((sv["bancada"][0] - 0.2, sv["bancada"][1] - 0.2, sv["bancada"][2] + 0.2, sv["bancada"][3] + 0.2),
                         tuple(d["rect"])) and abs(d["rect"].width - (sv["bancada"][2] - sv["bancada"][0])) < 0.5)
    poli = [(p.x, p.y) for it in d["items"] for p in it[1:] if hasattr(p, "x")]
    out = bancada_pedra(Q, out, sv["bancada"], lambda tl: _granito(Q, tl, 2640), 0.62, 0.6, 0.34, poli=poli)
    out = cuba_branca(Q, out, sv["cuba"])
    out = torneira(Q, out, sv["torneira"], sv["base"])
    out = vaso(Q, out, sv["vaso"], "esquerda")
    out = placa_cromada(Q, out, sv["descarga"])
    print("    banho de serviço: bancada em granito marrom (o polígono do PDF), cuba branca, torneira, vaso branco")
    for c in q["chuveiros"]:
        out = chuveiro(Q, out, c)
    print(f"    {len(q['chuveiros'])} chuveiros: a placa cromada com os furinhos, o braço e a canopla")
    return boxes(Q, out)


# ----------------------------------------------------------------------------------------------------------------------
# 3. O banco da sauna em travertino bruto (pedido 2): o retângulo do PDF (o banco de um nível, junto à parede de baixo),
# no travertino mais marcado das bancadas, com o veio no comprido do banco; a frente com a quina boleada (a linha clara
# logo dentro e a aresta no tom escurecido da pedra) e a sombra de contato no piso ao longo dela, para o banco ler
# como peça alta e não como piso.
SAUNA = {"pt": (1017.8, 1741.2, 1187.8, 1775.2), "tom": (180, 197, 216), "aresta": 0.66, "larg": 0.7,
         "boleado": 1.07, "boleado_px": 1.2, "contato": (0.26, 3.0), "semente": 2650}


def banco_sauna(Q, img):
    q = SAUNA
    x0, y0, x1, y1 = q["pt"]
    tl = tela(np.ascontiguousarray(img.copy()), Q, q["pt"], folga=8)
    m = tl.ret(q["pt"])
    # a sombra de contato no piso, ao longo da frente (em cima)
    Xg, Yg = tl.grade()
    d = (y0 - Yg) * PT_PX                                                   # px acima da frente
    f, alc = q["contato"]
    s = f * np.clip(1 - d / alc, 0, 1) * (d > 0) * ((Xg >= x0) & (Xg <= x1))
    tl.reg *= (1 - s)[..., None]
    D = travertino_bruto(Q, tl.h, tl.w, q["semente"], **TRAVERTINO["bancada"])
    tl.pintar_img(m, np.float32(q["tom"]) * D[..., None])
    e = q["boleado_px"] / PT_PX
    bol = tl.ret((x0, y0 + 0.5 / PT_PX, x1, y0 + e))
    tl.pintar_img(bol, tl.reg * q["boleado"])
    tl.pintar(tl.ret((x0, y0, x1, y0 + q["larg"] / PT_PX)), tuple(c * q["aresta"] for c in q["tom"]))
    print("    sauna: banco em travertino bruto, com a quina boleada na frente e a sombra de contato")
    return tl.gravar()


# ----------------------------------------------------------------------------------------------------------------------
# 4. O elevador (pedido 3): a cabine de aço como nas Casas B a D, no desenho do PDF (INS_INSTALAÇÕES HIDRÁULICAS): as
# paredes da cabine em aço escovado claro, o piso de aço escovado com o brilho no meio, o quadro fino do painel, o X
# fraco do poço, os corrimãos nas três paredes sem porta, as folhas telescópicas da porta (à esquerda, no PDF) em inox
# e a soleira em inox escovado no vão da parede (de 2012,7 pt até a cabine), com as faces da parede em cinza fino.
ELEVADOR = {"externo": (2026.3, 1290.5, 2102.2, 1369.8), "interno": (2030.9, 1295.0, 2097.6, 1365.2),
            "vao": (2026.3, 1313.2, 2030.9, 1347.1),
            "folhas": [(2027.5, 1296.2, 2029.2, 1313.2), (2027.5, 1310.3, 2029.2, 1327.3),
                       (2027.5, 1333.0, 2029.2, 1349.9), (2027.5, 1347.1, 2029.2, 1364.1)],
            "soleira": (2012.72, 1311.71, 2026.3, 1348.56),
            "parede": (184, 186, 189), "piso": (198, 200, 203), "poco": (112, 115, 118), "inox_folha": (206, 208, 211),
            "contorno": (70, 73, 76), "quadro": (128, 131, 134), "corrimao": (226, 228, 230), "x": (160, 163, 166),
            "escovado": 2.2, "brilho": 14.0, "anel": (2021.22, 1285.0, 2106.5, 1374.0), "semente": 2660}


def elevador(Q, img):
    q = ELEVADOR
    O, I = q["externo"], q["interno"]
    tl = tela(np.ascontiguousarray(img.copy()), Q, (q["soleira"][0], q["anel"][1], q["anel"][2], q["anel"][3]), folga=6)
    rng = np.random.default_rng(q["semente"])
    X, Y = tl.grade()
    # o aço escovado (o fio na vertical) com o brilho largo no meio
    fio = cv2.GaussianBlur(rng.normal(0, 1, (1, tl.w)).astype(np.float32), (0, 0), 1.2)
    fio = np.repeat(fio / max(fio.std(), 1e-6), tl.h, axis=0)
    cx, cy = (I[0] + I[2]) / 2, (I[1] + I[3]) / 2
    r = np.hypot((X - cx) / (I[2] - I[0]), (Y - cy) / (I[3] - I[1]))
    luz = q["brilho"] * np.clip(1 - 2 * r, 0, 1)
    def aco(base):
        return np.float32(base)[None, None] + (q["escovado"] * fio + luz)[..., None]
    # o poço em volta da cabine (o PDF o tem em branco; ficava o travertino antigo), depois a cabine
    tl.pintar(tl.ret(q["anel"]), q["poco"])
    mo = tl.ret(O)
    sombra_q(tl, mo, forca=0.22)
    tl.pintar_img(mo, aco(q["parede"]))
    mi = tl.ret(I)
    tl.pintar_img(mi, aco(q["piso"]))
    # o quadro do painel do piso e o X fraco do poço
    k = 2.4
    tl.contorno(tl.ret((I[0] + k, I[1] + k, I[2] - k, I[3] - k)), 0.5, q["quadro"])
    xs = tl.vazia()
    for (a, b), (c, d) in (((I[0] + k, I[1] + k), (I[2] - k, I[3] - k)), ((I[0] + k, I[3] - k), (I[2] - k, I[1] + k))):
        cv2.line(xs, tuple(int(v) for v in tl.pt(a, b)), tuple(int(v) for v in tl.pt(c, d)), 255,
                 max(1, int(0.5 * 8)), cv2.LINE_AA)
    tl.pintar(xs, q["x"], 0.45)
    # os corrimãos: em cima, à direita e embaixo, a 1,2 pt da parede, com as pontas redondas
    w = 1.5
    for rr in ((I[0] + 12, I[1] + 1.2, I[2] - 12, I[1] + 1.2 + w), (I[2] - 1.2 - w, I[1] + 12, I[2] - 1.2, I[3] - 12),
               (I[0] + 12, I[3] - 1.2 - w, I[2] - 12, I[3] - 1.2)):
        mc = tl.ret(rr, w / 2)
        sombra_q(tl, mc, forca=0.28, dist=0.8, sigma=0.7)
        tl.pintar(mc, q["corrimao"])
        tl.contorno(mc, 0.35, q["contorno"])
    # a porta: o vão escuro do poço e as folhas telescópicas em inox
    tl.pintar(tl.ret(q["vao"]), q["poco"])
    for f in q["folhas"]:
        mf = tl.ret(f)
        tl.pintar(mf, q["inox_folha"])
        tl.contorno(mf, 0.35, q["contorno"])
    tl.contorno(mi, 0.45, q["quadro"])
    tl.contorno(mo, 0.5, q["contorno"])
    # a soleira em inox escovado, com as faces da parede (os lados compridos) em cinza fino
    s_ = tl.ret(q["soleira"])
    tl.pintar_img(s_, aco((198, 199, 200)) - luz[..., None])
    sx0, sy0, sx1, sy1 = q["soleira"]
    for rr in ((sx0, sy0, sx1, sy0 + 0.6 / PT_PX), (sx0, sy1 - 0.6 / PT_PX, sx1, sy1)):
        tl.pintar(tl.ret(rr), (128, 130, 132))
    print("    elevador: a cabine de aço (paredes, piso escovado, painel, corrimãos, folhas da porta) e a soleira em inox")
    return tl.gravar()


# ----------------------------------------------------------------------------------------------------------------------
# 5. Os armários do depósito em marcenaria (pedido 5): os dois retângulos da DOC_LINHAS E PROJEÇÕES (o braço de cima,
# de 0,50 m, junto à parede de cima, e o da direita, de 0,70 m, junto à parede da direita), até o teto, sem a diagonal
# (como os armários até o teto da Casa A): a madeira natural com o veio no comprido de cada braço, os módulos das portas
# (~55 cm) em traço fino, a linha da frente das portas a 2 cm da face livre, o contorno fino nas faces livres e a sombra
# curta no Bege Bahia.
DEPOSITO = {"pecas": [((1156.7, 1060.8, 1615.9, 1089.2), "h", "baixo"), ((1615.9, 1060.8, 1655.6, 1219.6), "v", "esquerda")],
            "madeira": (112, 150, 190), "veio": 0.07, "tom_modulo": 0.035, "modulo_m": 0.55, "frente_m": 0.02,
            "junta": (66, 88, 112), "junta_px": 0.55, "contorno": (52, 66, 82), "contorno_px": 0.6, "sombra": 0.32,
            "semente": 2670}


def armarios_deposito(Q, img):
    q = DEPOSITO
    out = np.ascontiguousarray(img.copy())
    rng = np.random.default_rng(q["semente"])
    for r, eixo, frente in q["pecas"]:
        tl = tela(out, Q, r, folga=6)
        m = tl.ret(r)
        sombra_q(tl, m, forca=q["sombra"], dist=1.4, sigma=1.4)
        # o veio no comprido da peça
        if eixo == "h":
            v = cv2.GaussianBlur(rng.normal(0, 1, (tl.h, tl.w)).astype(np.float32), (0, 0), sigmaX=0.6 * Q.px_m,
                                 sigmaY=0.012 * Q.px_m)
        else:
            v = cv2.GaussianBlur(rng.normal(0, 1, (tl.h, tl.w)).astype(np.float32), (0, 0), sigmaX=0.012 * Q.px_m,
                                 sigmaY=0.6 * Q.px_m)
        D = 1 + q["veio"] * v / max(v.std(), 1e-6)
        # os módulos das portas, cada um no seu tom
        X, Y = tl.grade()
        x0, y0, x1, y1 = r
        comp = (x1 - x0) if eixo == "h" else (y1 - y0)
        n = max(1, int(round(comp / (q["modulo_m"] * 56.69))))
        passo = comp / n
        idx = np.clip(((X - x0) if eixo == "h" else (Y - y0)) // passo, 0, n - 1).astype(int)
        tons = 1 + rng.uniform(-q["tom_modulo"], q["tom_modulo"], n)
        D *= tons[idx]
        tl.pintar_img(m, np.float32(q["madeira"]) * D[..., None])
        juntas = tl.vazia()
        for i in range(1, n):
            a = (x0 if eixo == "h" else y0) + i * passo
            p0, p1 = ((a, y0), (a, y1)) if eixo == "h" else ((x0, a), (x1, a))
            cv2.line(juntas, tuple(int(v) for v in tl.pt(*p0)), tuple(int(v) for v in tl.pt(*p1)), 255,
                     max(1, int(round(q["junta_px"] * 8))), cv2.LINE_AA)
        # a linha da frente das portas, a 2 cm da face livre
        fm = q["frente_m"] * 56.69
        lf = {"baixo": ((x0, y1 - fm), (x1, y1 - fm)), "esquerda": ((x0 + fm, y0), (x0 + fm, y1))}[frente]
        cv2.line(juntas, tuple(int(v) for v in tl.pt(*lf[0])), tuple(int(v) for v in tl.pt(*lf[1])), 255,
                 max(1, int(round(q["junta_px"] * 8))), cv2.LINE_AA)
        tl.pintar(juntas & m, q["junta"], 0.8)
        tl.contorno(m, q["contorno_px"], q["contorno"])
        out = tl.gravar()
        print(f"    depósito: armário em marcenaria ({comp / 56.69:.2f} m, {n} módulos de porta)")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 5b. As portas de vidro de correr da academia (pergunta do usuário, 26/10/26: "as portas de vidro de correr que fecham a
# academia estão bem representadas?"; não estavam: desenhadas em 2000 px e ampliadas, saíam como uma linha cinza borrada,
# sem as folhas, os planos, os montantes nem os batentes). Redesenhadas na resolução da prancha, pelo PDF (ARQ_PAREDE),
# como a regra da porta de correr (seção 4): os batentes em quadradinhos brancos com o contorno cinza; cada folha na
# espessura do PDF (~5 cm), o caixilho claro de alumínio com o vidro na linha do meio e o contorno fino escuro, nos dois
# planos do PDF; os montantes nas pontas das folhas; a sombra curta. Do pátio: 4 folhas em 2 trilhos (as das pontas no
# de fora, as do meio no de dentro), fechadas; o piso do pátio passa por baixo (sem soleira, R13). Do hall: 2 folhas
# desencontradas sobre a soleira de Bege Bahia, refeita nítida, com as faces da parede em cinza fino (R13).
PORTAS_VIDRO = {
    "refaz_pt": [(1144.8, 1233.0, 1151.4, 1654.1)],          # as folhas do pátio: o piso do pátio refeito por baixo
    "portas": [
        {"nome": "do pátio", "batentes": [(1145.3, 1230.9, 1156.7, 1233.2), (1145.3, 1653.9, 1156.7, 1656.1)],
         "folhas": [((1145.3, 1233.2, 1148.2, 1340.6), "y"), ((1148.2, 1336.1, 1151.0, 1443.5), "y"),
                    ((1148.2, 1443.5, 1151.0, 1551.0), "y"), ((1145.3, 1546.4, 1148.2, 1653.9), "y")],
         "montante_pt": 4.5},
        {"nome": "do hall", "soleira": (1655.55, 1232.34, 1666.89, 1371.24),
         "batentes": [(1660.4, 1230.9, 1666.9, 1233.2), (1655.6, 1230.9, 1660.4, 1232.3),
                      (1660.4, 1370.4, 1666.9, 1372.7), (1655.6, 1371.2, 1660.4, 1372.7)],
         "folhas": [((1662.6, 1233.2, 1664.9, 1301.8), "y"), ((1660.4, 1301.8, 1662.6, 1370.4), "y")],
         "montante_pt": 0.6},
    ],
    "aluminio": (232, 234, 235), "vidro": (204, 200, 190), "contorno": (88, 91, 94), "contorno_px": 0.4,
    "batente": (240, 241, 242), "batente_contorno": (120, 123, 126), "sombra": 0.22,
    "soleira": {"forca": 0.5, "linha": (150, 152, 154), "linha_px": 0.5, "semente": 7}}


def soleira_bege(Q, out, r):
    """A soleira de Bege Bahia (R13) na resolução da prancha: a foto da biblioteca no tom das Casas B a D, nítida, com as
    faces da parede (os lados compridos) em cinza fino."""
    q = PORTAS_VIDRO["soleira"]
    sys.path.insert(0, str(A.RAIZ / "_texturas"))
    from texturas import textura
    tl = tela(out, Q, r, folga=3)
    T = textura("bege_bahia", Q.px_m, tl.h, tl.w, semente=q["semente"]).astype(np.float32)
    T = (1 + q["forca"] * (T / T.reshape(-1, 3).mean(axis=0) - 1)) * np.float32(PISOS_A["Bege Bahia"]["tom"])
    tl.pintar_img(tl.ret(r), T)
    x0, y0, x1, y1 = r
    e = q["linha_px"] / PT_PX
    faces = ((x0, y0, x0 + e, y1), (x1 - e, y0, x1, y1)) if (y1 - y0) >= (x1 - x0) else \
        ((x0, y0, x1, y0 + e), (x0, y1 - e, x1, y1))
    for f in faces:
        tl.pintar(tl.ret(f), q["linha"])
    return tl.gravar()


def portas_vidro(Q, img):
    q = PORTAS_VIDRO
    out = np.ascontiguousarray(img.copy())
    for p in q["portas"]:
        if "soleira" in p:
            out = soleira_bege(Q, out, p["soleira"])
        caixa = tuple(f(v) for f, v in zip((min, min, max, max), zip(*([r for r, _ in p["folhas"]] + p["batentes"]))))
        tl = tela(out, Q, caixa, folga=5)
        for b in p["batentes"]:
            m = tl.ret(b)
            tl.pintar(m, q["batente"])
            tl.contorno(m, q["contorno_px"], q["batente_contorno"])
        for (x0, y0, x1, y1), eixo in p["folhas"]:
            m = tl.ret((x0, y0, x1, y1))
            sombra_q(tl, m, forca=q["sombra"], dist=0.9, sigma=0.8)
            tl.pintar(m, q["aluminio"])
            # o vidro na linha do meio, entre os montantes
            k = p["montante_pt"]
            xm = (x0 + x1) / 2
            w = max(0.35, (x1 - x0) * 0.22)
            tl.pintar(tl.ret((xm - w, y0 + k, xm + w, y1 - k)), q["vidro"])
            for yy in (y0 + k, y1 - k):                               # os montantes: o traço no fim do vidro
                tl.pintar(tl.ret((x0, yy - 0.2, x1, yy + 0.2)), q["contorno"], 0.7)
            tl.contorno(m, q["contorno_px"], q["contorno"])
        out = tl.gravar()
        print(f"    porta de correr {p['nome']}: {len(p['folhas'])} folhas de vidro nos planos do PDF e "
              f"{len(p['batentes'])} batentes" + (", sobre a soleira de Bege Bahia refeita" if "soleira" in p else ""))
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 6. As paredes (E10; resposta do usuário: cinza 80) nos preenchimentos escuros da ARQ_PAREDE, com antialias; a divisória
# entre os banhos feminino e masculino entra como parede (pedido de 26/10: "deve ser representado como parede em cinza
# 80"; até aqui era uma divisória clara, item 94 de 19/10). Antes, o preto das paredes antigas que passa do PDF (a franja
# de 1 a 3 px) é refeito com o que está em volta, para a borda nova não sair com um fio preto. Pilares: no Subsolo da
# Casa A não há pilar solto (os da EST - Pilar estão dentro das paredes).
PAREDES_A = {"cor": (80, 80, 80), "divisoria": (1490.0, 1664.6, 1500.8, 1775.2), "escuro": 48, "croma": 12,
             "folga_px": 3}


def paredes(Q, img):
    q = PAREDES_A
    a = Q.preencher(lambda d: d.get("layer") == "ARQ_PAREDE" and d.get("fill") is not None and max(d["fill"]) < 0.5,
                    ss=4)
    a = np.maximum(a, ret_aa(Q, q["divisoria"]))
    k = 2 * q["folga_px"] + 1
    perto = cv2.dilate((a > 0.02).astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool)
    im = img.astype(np.int16)
    preto = (im.max(axis=2) < q["escuro"]) & ((im.max(axis=2) - im.min(axis=2)) <= q["croma"])
    M = perto & preto
    ys, xs = np.nonzero(perto)
    y0, y1, x0, x1 = max(ys.min() - 8, 0), ys.max() + 9, max(xs.min() - 8, 0), xs.max() + 9
    out = img.copy()
    out[y0:y1, x0:x1] = cv2.inpaint(img[y0:y1, x0:x1], M[y0:y1, x0:x1].astype(np.uint8), 3, cv2.INPAINT_TELEA)
    out = out.astype(np.float32) * (1 - a[..., None]) + np.float32(q["cor"]) * a[..., None]
    print(f"    paredes em cinza {q['cor'][0]} no contorno do PDF (com a divisória dos banhos); "
          f"{int((M & (a < 0.5)).sum())} px da franja preta antiga refeitos")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
# 7. A escada do deck para o pátio (E3, E8): sai o triângulo (R14); entram os traços da ARQ_ESCADAS E RAMPAS do PDF em
# cinza-escuro (~85), mais marcados que o bocel de 19/10 (os degraus, o contorno, a linha de percurso com a bolinha no
# degrau 1, a marca de corte e o tracejado depois dela), e o S do PDF (o sentido: sobe do pátio para o deck) em Inter
# SemiBold, cinza quase preto, na origem do texto do PDF.
ESCADA_A = {"camada": "ARQ_ESCADAS E RAMPAS", "caixa_pt": (733.0, 1228.0, 912.0, 1302.0), "cor": (85, 85, 85),
            "larg_px": 0.9, "triangulo_q": (1052, 1078, 1088, 1110), "triangulo_lum": 125,
            "texto": "S", "origem": (914.0, 1267.6), "fonte": "Inter-SemiBold.otf", "corpo_px": 17, "cor_texto": (45, 45, 45)}


def escada(Q, img):
    from PIL import Image, ImageDraw, ImageFont
    q = ESCADA_A
    out = img.copy()
    # o triângulo antigo: os px escuros na caixa dele, refeitos com o degrau em volta
    x0, y0, x1, y1 = q["triangulo_q"]
    reg = out[y0:y1, x0:x1]
    tri = (reg.astype(np.float32).mean(axis=2) < q["triangulo_lum"]).astype(np.uint8)
    tri = cv2.dilate(tri, np.ones((5, 5), np.uint8))
    out[y0:y1, x0:x1] = cv2.inpaint(reg, tri, 4, cv2.INPAINT_TELEA)
    # os traços do PDF
    tl = tela(out, Q, q["caixa_pt"], folga=6)
    m = tl.vazia()
    n = 0
    cx0, cy0, cx1, cy1 = q["caixa_pt"]
    for d in Q.desenhos:
        if d.get("layer") != q["camada"] or d["type"] != "s":
            continue
        r = d["rect"]
        if not (r.x0 >= cx0 and r.x1 <= cx1 and r.y0 >= cy0 and r.y1 <= cy1):
            continue
        for c in AJ.caminhos_pdf(d, tl.pt):
            cv2.polylines(m, [np.int32(np.round(c))], False, 255, max(1, int(round(q["larg_px"] * 8))), cv2.LINE_AA)
        n += 1
    tl.pintar(m, q["cor"])
    out = tl.gravar()
    # o S
    from rodape_entrega import FONTES
    fonte = ImageFont.truetype(str(FONTES / q["fonte"]), q["corpo_px"] * 4)
    ox, oy = Q.p2q(*q["origem"])
    W = H = q["corpo_px"] * 3
    X0, Y0 = int(ox) - 4, int(oy) - q["corpo_px"] * 2
    tela_t = Image.new("L", (W * 4, H * 4), 0)
    ImageDraw.Draw(tela_t).text(((ox - X0) * 4, (oy - Y0) * 4), q["texto"], font=fonte, fill=255, anchor="ls")
    a = np.asarray(tela_t.resize((W, H), Image.LANCZOS), np.float32)[..., None] / 255
    reg = out[Y0:Y0 + H, X0:X0 + W].astype(np.float32)
    out[Y0:Y0 + H, X0:X0 + W] = np.clip(reg * (1 - a) + np.float32(q["cor_texto"]) * a, 0, 255).astype(np.uint8)
    print(f"    escada: sem o triângulo; {n} traços do PDF em cinza {q['cor'][0]} e o {q['texto']} na origem do PDF")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 8. Os rótulos (E7, R6, R7), pelo motor das Casas B a D (`F.rotulos`): cada um no lugar livre mais perto do PDF, sem
# tocar objeto nenhum, dentro do ambiente, em preto ou branco pelo fundo. Os boxes da Casa A são as duas folhas do PDF
# (`AJ.folhas_box`, que o `F.vidros_box` não acha: lá o box tem 7 traços ou mais), com o trilho até a parede; o lado do
# chuveiro sai dos ambientes. O BANHO SERV. parte do piso seco junto à porta (o rótulo do PDF fica no box).
ROTULOS_A = {"pontos": {"BANHO SERV.": (984.0, 1190.0)}, "trilho_junto_pt": 8.0}


def vidros_box_a(Q):
    out = []
    for b in AJ.folhas_box(Q.pg):
        a0, a1 = b["span"]
        for s0, s1 in sorted(b["trilho"]):
            if s0 <= a1 + ROTULOS_A["trilho_junto_pt"] and s1 > a1:
                a1 = s1
        for s0, s1 in sorted(b["trilho"], reverse=True):
            if s1 >= a0 - ROTULOS_A["trilho_junto_pt"] and s0 < a0:
                a0 = s0
        m = b["meio"]
        out.append((a0, m - 0.6, a1, m + 0.6, True) if b["hor"] else (m - 0.6, a0, m + 0.6, a1, False))
    return out


def duchas_box_a(Q, boxes):
    centros = [((c["ducha"][0] + c["ducha"][2]) / 2, (c["ducha"][1] + c["ducha"][3]) / 2) for c in BANHOS["chuveiros"]]
    out = []
    for x0, y0, x1, y1, hor in boxes:
        cand = [(abs(cy - (y0 + y1) / 2) if hor else abs(cx - (x0 + x1) / 2), (cx, cy)) for cx, cy in centros
                if ((x0 - 5 <= cx <= x1 + 5) if hor else (y0 - 5 <= cy <= y1 + 5))]
        cand = [c for c in cand if c[0] < 100]
        out.append(min(cand)[1] if cand else None)
    return out


def rotulos(Q, img):
    import retoque_1pav_casae as R1
    q = A.PAVIMENTOS[Q.chave]
    rot = [r for r in R1.rotulos_pdf(Q.pg) if r[0] in q.get("incluir", ()) or not any(f in r[0] for f in A.FORA)]
    guardar = (F.vidros_box, F.duchas_box, dict(F.ROTULOS_F["pontos"]))
    preencher = Q.preencher
    # a divisória dos banhos agora é parede (no PDF é ARQ_BANCADAS branca): para os ambientes e para os obstáculos
    sonda = {"layer": "ARQ_PAREDE", "fill": (0.36, 0.36, 0.36), "type": "f"}

    def preencher_com_divisoria(filtro, ss=4, fs=True):
        m = preencher(filtro, ss=ss, fs=fs)
        return np.maximum(m, ret_aa(Q, PAREDES_A["divisoria"])) if filtro(sonda) else m
    try:
        F.vidros_box, F.duchas_box = vidros_box_a, duchas_box_a
        F.ROTULOS_F["pontos"][Q.chave] = ROTULOS_A["pontos"]
        Q.preencher = preencher_com_divisoria
        return F.rotulos(Q, img, rot, q["ajustes"], granito=None)
    finally:
        F.vidros_box, F.duchas_box = guardar[0], guardar[1]
        F.ROTULOS_F["pontos"] = guardar[2]
        Q.preencher = preencher


def passos_subsolo(Q, ini):
    return [
        ("pisos", lambda im: pisos(Q, im, ini)),
        ("banhos", lambda im: banhos(Q, im)),
        ("sauna", lambda im: banco_sauna(Q, im)),
        ("elevador", lambda im: elevador(Q, im)),
        ("deposito", lambda im: armarios_deposito(Q, im)),
        ("portas", lambda im: portas_vidro(Q, im)),
        ("paredes", lambda im: paredes(Q, im)),
        ("escada", lambda im: escada(Q, im)),
        ("rotulos", lambda im: rotulos(Q, im)),
    ]


# O antes e o depois de cada pedido (a final aprovada até aqui, com os rótulos, e a nova), recortes no quadro (px)
ANTES_DEPOIS = {"planta": (860, 820, 2420, 1680), "banhos_sauna": (1180, 1490, 1900, 1660),
                "porta_patio": (1300, 1040, 1400, 1530), "porta_hall": (1840, 1040, 1920, 1235),
                "banho_servico": (1080, 850, 1350, 1070), "elevador_hall": (1860, 1040, 2400, 1235),
                "deposito": (1330, 855, 1890, 1065), "academia": (1340, 1055, 1890, 1520),
                "escada": (880, 1040, 1110, 1150)}


def antes_depois(antes, depois, chave="Subsolo", max_lado=1800):
    for nome, (x0, y0, x1, y1) in ANTES_DEPOIS.items():
        a, d = antes[y0:y1, x0:x1], depois[y0:y1, x0:x1]
        lado = (x1 - x0) <= (y1 - y0) * 1.3
        junto = np.hstack([a, np.full((a.shape[0], 12, 3), 255, np.uint8), d]) if lado else \
            np.vstack([a, np.full((12, a.shape[1], 3), 255, np.uint8), d])
        k = min(3.0, max_lado / max(junto.shape[:2]))
        junto = cv2.resize(junto, None, fx=k, fy=k, interpolation=cv2.INTER_LANCZOS4 if k > 1 else cv2.INTER_AREA)
        arq = CASA / "renders" / f"POE642_CasaA_PH_{chave}_2610_{nome}_antes_depois.jpg"
        cv2.imwrite(str(arq), junto, [cv2.IMWRITE_JPEG_QUALITY, 90])
        print(f"    {arq.name}")


def final_3840(chave="Subsolo", salvar=True, de=None, ate=None):
    """A final de 3840 px com os rótulos. de: recomeça desta etapa (a anterior vem do cache); ate: para nela."""
    Q = QuadroA(chave)
    ini = inicial(Q)
    passos = passos_subsolo(Q, ini)
    nomes = [n for n, _ in passos]
    i0 = nomes.index(de) if de else 0
    i1 = nomes.index(ate) + 1 if ate else len(passos)
    img = cv2.imread(str(ETAPAS / f"{chave}_{nomes[i0 - 1]}.png")) if i0 > 0 else ini
    for nome, f in passos[i0:i1]:
        t0 = time.time()
        img = f(img)
        print(f"  [{nome}] {time.time() - t0:.0f} s", flush=True)
        cv2.imwrite(str(ETAPAS / f"{chave}_{nome}.png"), img)
    if salvar and ate is None and i1 == len(passos):
        nome = CASA / "renders" / f"POE642_CasaA_PH_{chave}_final_rotulos.png"
        cv2.imwrite(str(nome), img)
        print(f"    {nome} {img.shape[1]}x{img.shape[0]}")
    return Q, img


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("chave", nargs="?", default="Subsolo", choices=["Subsolo"])
    ap.add_argument("--de")
    ap.add_argument("--ate")
    ap.add_argument("--antes", help="a final aprovada antes destes pedidos (PNG): gera os antes e depois")
    a = ap.parse_args()
    Q, img = final_3840(a.chave, de=a.de, ate=a.ate)
    if a.antes:
        antes_depois(cv2.imread(a.antes), img, a.chave)

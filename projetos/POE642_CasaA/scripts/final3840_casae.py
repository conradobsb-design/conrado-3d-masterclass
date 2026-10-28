#!/usr/bin/env python3
"""As finais da Casa E (Subsolo, Térreo e 1º Pavimento) com a auditoria de 26/10, na resolução da prancha (3840 px).

Pedido do usuário (28/10/26), depois de aprovar o Térreo da Casa D: "PODE COMEÇAR COM O SUBSOLO, NA SEQUENCIA O TERREO
E DEPOIS O PRIMEIRO PAVIMENTO. VOU DORMIR AGORA E QUERO QUE ELENQUE AS ALTERAÇÕES, APLIQUE-AS E AMANHÃ CEDO EU VALIDO."
A lista de cada planta é a auditoria de 26/10 (`auditoria_2610.py`, mapas `POE642_CasaE/renders/..._auditoria_2610.jpg`)
com as regras já aprovadas nas Casas A a D (`POE642_REGRAS.md`, seção 19): paredes em cinza 80 e pilares pretos (E10),
as escadas sem linhas e sem triângulo, com o sombreamento e o S/D do PDF (E3, E8), os armários cortados com cabides (E2),
os boxes em vidro contínuo (E5), os rótulos fora dos objetos e do box (E7), as bancadas mais marcadas que o piso (E9) e
os pisos nas texturas e escalas das Casas B a D (E11).

A imagem de partida é a final aprovada de cada pavimento (`renders/POE642_CasaE_PH_<pav>_v1_final.png` no commit
`PAV_E[...]["aprovada"]`, lida do git, porque a final é regravada aqui), sem os rótulos:
eles são escritos de novo no fim, pela mesma rotina (`retoque_1pav_casae.rotulos_ambientes`), e saem da final pela conta
inversa da composição (`sem_rotulos`): a mesma rotina sobre um quadro preto e um branco dá o alfa e a cor de cada px do
texto; o fundo é tirado do px da final e, onde o texto cobre quase tudo, refeito pelos vizinhos.

Uso (da pasta POE642_CasaA/scripts/):
  python3 final3840_casae.py Subsolo              # a final do Subsolo com os rótulos
  python3 final3840_casae.py Subsolo --de rotulos # recomeça de uma etapa (as anteriores ficam em cache)
Saída: `POE642_CasaE/renders/POE642_CasaE_PH_<pav>_v1_final.png`, que vai ao `rodape_entrega.py --no-quadro`.
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

B, AJ = F.B, F.AJ
RAIZ = AQUI.parent.parent
CASA = RAIZ / "POE642_CasaE"
ETAPAS = Path(os.environ.get("POE642_CACHE", tempfile.gettempdir())) / "poe642_casae_etapas"
LARGURA = 3840

PAV_E = {
    "Subsolo": {"pdf": "642 - SUBSOLO - CASA E.pdf", "base": "POE642_CasaE_BASE_Subsolo_v3_texturas_16x9.png",
                "chapada": "POE642_CasaE_BASE_Subsolo_v2_16x9.png", "sem_tela": "POE642_CasaE_BASE_Subsolo_v2.png",
                "final": "POE642_CasaE_PH_Subsolo_v1_final.png", "aprovada": "4caa265"},
    "Terreo": {"pdf": "642 - TÉRREO - CASA E.pdf", "base": "POE642_CasaE_BASE_Terreo_v3_texturas_16x9.png",
               "chapada": "POE642_CasaE_BASE_Terreo_v2_16x9.png", "sem_tela": "POE642_CasaE_BASE_Terreo_v2.png",
               "final": "POE642_CasaE_PH_Terreo_v1_final.png", "aprovada": "3ddcc46"},
    "1Pavimento": {"pdf": "642 - 1º PAVIMENTO - CASA E.pdf", "base": "POE642_CasaE_BASE_1Pavimento_v3_texturas_16x9.png",
                   "chapada": "POE642_CasaE_BASE_1Pavimento_v2_16x9.png",
                   "sem_tela": "POE642_CasaE_BASE_1Pavimento_v2.png",
                   "final": "POE642_CasaE_PH_1Pavimento_v1_final.png", "aprovada": "3ddcc46"},
}


# ----------------------------------------------------------------------------------------------------------------------
# O quadro da prancha, com os caminhos da Casa E (o `F.Quadro` aponta para a Casa B)
class QuadroE(F.Quadro):
    def __init__(self, chave):
        import pymupdf
        from opcoes_1pav_casae import quadro_pdf
        self.chave = chave
        q = self.q = PAV_E[chave]
        cfg = self.cfg = json.loads((CASA / "config_bases.json").read_text())
        self.base = CASA / "bases" / q["base"]
        self.pg = pymupdf.open(RAIZ / "_pdfs_cliente" / q["pdf"])[cfg["pavimentos"][chave]["pagina"]]
        at, lt = cv2.imread(str(self.base), cv2.IMREAD_GRAYSCALE).shape
        hb, wb = cv2.imread(str(CASA / "bases" / q["sem_tela"]), cv2.IMREAD_GRAYSCALE).shape
        self.W = LARGURA
        self.H = round(at * self.W / lt)
        self.p2q = quadro_pdf(self.pg, cfg, lt, at, wb, hb, self.W)
        (a, b), (c, d) = self.p2q(0, 0), self.p2q(56.69, 0)
        self.px_m = float(np.hypot(c - a, d - b))
        self.chapada = cv2.resize(cv2.imread(str(CASA / "bases" / q["chapada"])), (self.W, self.H),
                                  interpolation=cv2.INTER_NEAREST)
        self._desenhos = None

    def q2p(self, x, y):
        """quadro (px) -> pt do PDF (o p2q é afim)."""
        (a, b), (c, d), (e, f) = self.p2q(0, 0), self.p2q(100, 0), self.p2q(0, 100)
        M = np.array([[(c - a) / 100, (e - a) / 100], [(d - b) / 100, (f - b) / 100]])
        return tuple(np.linalg.solve(M, np.array([x - a, y - b])))


# ----------------------------------------------------------------------------------------------------------------------
# Os rótulos: os de cada pavimento, como as finais aprovadas os escrevem (`rotulos`), com os ajustes desta rodada
# (`AJUSTES_E`: nome, centro do rótulo do PDF em px de 2000 e o desvio em px de 2000[, opções]), que substituem os de
# mesmo nome
AJUSTES_E = {"Subsolo": [], "Terreo": [], "1Pavimento": []}


def _rotulos_pav(chave):
    """(rótulos, ajustes, granito?) da rotina aprovada de cada pavimento."""
    import retoque_1pav_casae as R1
    if chave == "Subsolo":
        import retoque_subsolo_casae as S
        q = S.ROTULOS
        from PIL import ImageFont
        from rodape_entrega import FONTES
        import pymupdf
        Q = QuadroE(chave)
        rot = [r for r in R1.rotulos_pdf(Q.pg) if not any(f in r[0] for f in q["fora"])]
        for nome, (cx, cy), tam in q.get("extras", []):
            larg = ImageFont.truetype(str(FONTES / "Inter-Regular.otf"), 100).getlength(nome) * tam / 100
            caixa = pymupdf.Rect(cx - larg / 2, cy - 0.5 * tam, cx + larg / 2, cy + 0.5 * tam)
            rot.append((nome, [(nome, tam, (cx - larg / 2, cy + 0.36 * tam))], (cx, cy), caixa))
        return Q, rot, list(q["ajustes"]), S.GRANITO["legenda"]
    if chave == "Terreo":
        import retoque_terreo_casae as T
        q = T.ROTULOS
        Q = QuadroE(chave)
        rot = [r for r in R1.rotulos_pdf(Q.pg) if not any(f in r[0] for f in q["fora"])]
        return Q, rot, list(q["ajustes"]), T.ARCOS["granito"]
    Q = QuadroE(chave)
    return Q, R1.rotulos_pdf(Q.pg), list(R1.ROTULOS["ajustes"]), None


def escrever_rotulos(chave, img, novos=True, so=None, sem_ajustes=()):
    """Os rótulos do pavimento na imagem, como na final aprovada (novos=False) ou com os ajustes desta rodada.
    so: só os rótulos com esses nomes; sem_ajustes: os ajustes desta rodada com esses nomes ficam fora (a final de antes)."""
    import retoque_1pav_casae as R1
    Q, rot, aj, leg = _rotulos_pav(chave)
    meus = [a for a in AJUSTES_E[chave] if a[0] not in sem_ajustes]
    if novos and meus:
        nomes = {a[0] for a in meus}
        aj = [a for a in aj if a[0] not in nomes] + meus
    if so is not None:
        rot = [r for r in rot if r[0] in so]
    kw = {}
    if leg is not None:
        kw = {"granito": np.abs(Q.chapada.astype(int) - np.array(leg)).max(axis=2) <= 6,
              "cor_granito": R1.ROTULOS["branco"]}
    return R1.rotulos_ambientes(img, rot, Q.p2q, escala_desvio=Q.W / 2000, ajustes=aj, **kw)


def sem_rotulos(chave, final, novos=False, sem_ajustes=()):
    """A final sem os rótulos: a composição dos rótulos (out = cor * a + fundo * (1 - a)) desfeita px a px; onde o
    alfa passa de 0,8, o fundo vem dos vizinhos (inpaint de 3 px). `novos`: os rótulos com os ajustes desta rodada
    (menos os de `sem_ajustes`)."""
    H, W = final.shape[:2]
    vp = escrever_rotulos(chave, np.zeros((H, W, 3), np.uint8), novos=novos, sem_ajustes=sem_ajustes).astype(np.float32)
    vb = escrever_rotulos(chave, np.full((H, W, 3), 255, np.uint8), novos=novos,
                          sem_ajustes=sem_ajustes).astype(np.float32)
    a = np.clip(1 - (vb - vp).mean(axis=2) / 255, 0, 1)
    ca = vp
    f = final.astype(np.float32)
    fundo = (f - ca) / np.maximum(1 - a, 1e-3)[..., None]
    out = np.where(a[..., None] > 0.004, fundo, f)
    out = np.clip(np.round(out), 0, 255).astype(np.uint8)
    cheio = cv2.dilate((a > 0.8).astype(np.uint8), np.ones((3, 3), np.uint8))
    out = cv2.inpaint(out, cheio, 3, cv2.INPAINT_TELEA)
    print(f"    rótulos tirados da final: {int((a > 0.004).sum())} px ({int(cheio.sum())} refeitos pelos vizinhos)")
    return out, a


def caixas_rotulos(chave, nomes, **kw):
    """As caixas (x0, y0, x1, y1, em px da final) do texto dos rótulos `nomes`, como escritos (todas as linhas)."""
    Q = QuadroE(chave)
    caixas = []
    for nome in nomes:
        v = escrever_rotulos(chave, np.zeros((Q.H, Q.W, 3), np.uint8), so=(nome,), **kw)
        ys, xs = np.nonzero(v.max(axis=2) > 8)
        caixas.append((int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1))
    return caixas


def final_aprovada(chave):
    """A final aprovada antes desta rodada, lida do git (commit `aprovada` de PAV_E): a final do pavimento é regravada
    por este script."""
    import subprocess
    q = PAV_E[chave]
    rel = (CASA / "renders" / q["final"]).relative_to(RAIZ.parent)
    dados = subprocess.run(["git", "show", f"{q['aprovada']}:{rel.as_posix()}"], cwd=RAIZ.parent, check=True,
                           capture_output=True).stdout
    return cv2.imdecode(np.frombuffer(dados, np.uint8), cv2.IMREAD_COLOR)


def inicial(chave):
    """A final aprovada do pavimento sem os rótulos (em cache)."""
    ETAPAS.mkdir(parents=True, exist_ok=True)
    c = ETAPAS / f"{chave}_ini.png"
    if c.exists():
        return cv2.imread(str(c))
    final = final_aprovada(chave)
    img, _ = sem_rotulos(chave, final)
    cv2.imwrite(str(c), img)
    return img


# ----------------------------------------------------------------------------------------------------------------------
# E11: os pisos nas texturas e escalas das Casas B a D (`F.piso_textura`: a foto da biblioteca na escala da prancha, na
# luz larga do lugar), na mancha da legenda (base chapada). As peças ficam as da final: as do PDF (as camadas de móveis,
# louças, bancadas e marcenaria, preenchidas) e o que a final mostra diferente do piso, sem ser sombra (`_pecas_final`);
# a sombra antiga sai com o piso velho e cada peça ganha a sombra curta de novo (luz do alto à direita).
LINHAS_FICAM = ("DOC_LINHAS E PROJEÇÕES", "ARQ_ELEMENTOS FIXOS")
CAMADAS_OBJ = ("ARQ_ MOB COMUM", "ARQ_LOUÇAS E METAIS", "ARQ_BANCADAS", "ARQ_LAYOUT HUMANIZAÇÃO", "ARQ_MARCENARIA",
               "ARQ_MOBILIÁRIO", "ARQ - Marcenaria", "INS_INSTALAÇÕES HIDRÁULICAS")
PECAS_E = {"max_m2": 6.0, "linha_longa_m": 1.2, "desvio": 30, "croma": 0.03, "escuro": 0.62, "sombra_min": 0.30, "claro": 1.35,
           "area_min": 25, "junto_px": 4, "borda_px": 2, "borda_desvio": 14, "camadas_tracos": ("ARQ_ MOB COMUM",),
           "sombra": (0.26, 1.15, 1.35)}                     # força, distância e sigma (px) da sombra curta


def objetos_pdf(Q, caixa_q=None, camadas=CAMADAS_OBJ):
    """As peças do PDF (bool): os preenchimentos e os traços das camadas de objetos, cheios por dentro (fechados), sem
    as linhas compridas (as réguas e os contornos de ambiente) nem as peças maiores que `max_m2`."""
    q = PECAS_E
    ss = 2
    m = np.zeros((Q.H * ss, Q.W * ss), np.uint8)
    tr = np.zeros_like(m)
    lim = q["max_m2"] * 56.69 ** 2
    for d in Q.desenhos:
        if d.get("layer") not in camadas:
            continue
        r = d["rect"]
        if r.width * r.height > lim:
            continue
        if max(r.width, r.height) > q["linha_longa_m"] * 56.69 and min(r.width, r.height) < 1.0:
            continue
        for c in Q.caminhos(d):
            p = np.int32(np.round(c * ss))
            if caixa_q is not None:
                x0, y0, x1, y1 = caixa_q
                if p[:, 0].max() < x0 * ss or p[:, 0].min() > x1 * ss or p[:, 1].max() < y0 * ss or p[:, 1].min() > y1 * ss:
                    continue
            if d["type"] in ("f", "fs") and len(c) >= 3:
                cv2.fillPoly(m, [p], 255)
            cv2.polylines(tr, [p], False, 255, max(1, round(0.8 * ss)))
    from scipy import ndimage
    tr = cv2.morphologyEx(tr, cv2.MORPH_CLOSE, np.ones((3 * ss, 3 * ss), np.uint8))
    tr = ndimage.binary_fill_holes(tr > 0).astype(np.uint8) * 255
    m = cv2.resize(np.maximum(m, tr), (Q.W, Q.H), interpolation=cv2.INTER_AREA) > 60
    return m


def _piso_e_peca(Q, ini, legenda, perto=None):
    """(luz larga do piso, px com a cor do piso: o piso, a sombra e o reflexo dele, px que é peça: outra cor ou muito
    escuro, fugindo da luz do piso). Junto às peças do PDF (`perto`), o px muito escuro (`escuro`) é da peça (os ferros
    escuros dos aparelhos); longe delas, a sombra do render pode ser mais escura (`sombra_min`)."""
    q = PECAS_E
    L = F.luz_robusta(ini, legenda, 0.8 * Q.px_m)
    f = ini.astype(np.float32)
    dev = np.abs(f - L).max(axis=2) > q["desvio"]
    cf = f / np.maximum(f.sum(axis=2, keepdims=True), 1)
    cl = L / np.maximum(L.sum(axis=2, keepdims=True), 1)
    dc = np.abs(cf - cl).max(axis=2)
    raz = f.mean(axis=2) / np.maximum(L.mean(axis=2), 1)
    lim = q["escuro"] if perto is None else np.where(perto, q["escuro"], q["sombra_min"])
    piso = (dc < q["croma"]) & (raz > lim) & (raz < q["claro"])
    peca = dev & ~piso
    return L, piso, peca


def _pecas_final(Q, ini, legenda, pdf, perto=None):
    """O que a final mostra diferente do piso e não é sombra nem reflexo (bool), na mancha `legenda`: o px que foge da
    luz larga do piso (`desvio`) com outra cor (a sombra e o reflexo do render são o piso mais escuro ou mais claro, na
    mesma cromaticidade, e saem com ele) ou muito escuro; manchas de
    `area_min` px ou mais, ou junto às peças do PDF."""
    q = PECAS_E
    _, _, obj = _piso_e_peca(Q, ini, legenda, perto)
    obj &= legenda
    n, lab, st, _ = cv2.connectedComponentsWithStats(obj.astype(np.uint8), 8)
    perto = cv2.dilate(pdf.astype(np.uint8), np.ones((2 * q["junto_px"] + 1,) * 2, np.uint8)).astype(bool)
    toca = np.zeros(n, bool)
    toca[np.unique(lab[perto & obj])] = True
    ok = (st[:, cv2.CC_STAT_AREA] >= q["area_min"]) | toca
    ok[0] = False
    return ok[lab]


def troca_piso(Q, img, ini, legenda, textura, tom, sig_m, semente, fora=None, forca=None, pecas=None, fora_pecas=None):
    """O piso `textura` na mancha da legenda, sem as peças; devolve (imagem, máscara do piso novo, peças). As peças do
    PDF desenhadas só em traço nas camadas `camadas_tracos` (os aparelhos da academia: o render os pôs um pouco fora do
    traço) contam só onde a final não mostra a cor do piso."""
    q = PECAS_E
    if getattr(Q, "_pdf_obj", None) is None:
        Q._pdf_obj = (objetos_pdf(Q, camadas=tuple(c for c in CAMADAS_OBJ if c not in q["camadas_tracos"])),
                      objetos_pdf(Q, camadas=q["camadas_tracos"]))
    solido, tracos = Q._pdf_obj
    perto = cv2.dilate((solido | tracos).astype(np.uint8), np.ones((2 * q["junto_px"] + 1,) * 2, np.uint8)).astype(bool)
    _, piso, _ = _piso_e_peca(Q, ini, legenda, perto)
    pdf = solido | (tracos & ~piso)
    pec = (pdf & legenda) | _pecas_final(Q, ini, legenda, solido | tracos, perto)
    if pecas is not None:
        pec |= pecas & legenda
    # a borda das peças (a passagem para o piso, a quina mais escura de um pufe de madeira) vai junto com elas: o px a
    # até `borda_px` de uma peça que ainda foge da luz do piso (`borda_desvio`)
    L, _, _ = _piso_e_peca(Q, ini, legenda, perto)
    k = 2 * q["borda_px"] + 1
    foge = np.abs(ini.astype(np.float32) - L).max(axis=2) > q["borda_desvio"]
    pec |= cv2.dilate(pec.astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool) & foge & legenda
    if fora_pecas is not None:
        pec &= ~fora_pecas
    m = legenda & ~pec & ~paredes_pdf(Q, folga=1) & ~linhas_pdf(Q)
    if fora is not None:
        m &= ~fora
    novo = piso_textura_e(Q, img, m, textura, forca, sig_m, semente)
    if tom is not None:
        novo = novo * (np.float32(tom) / np.maximum(np.median(novo[m], axis=0), 1.0))
    out = F.pousar(img.astype(np.float32), novo, m, suave=0)
    f, dist, sig = PECAS_E["sombra"]
    s = cv2.warpAffine((pec & legenda).astype(np.float32), np.float32([[1, 0, -dist], [0, 1, dist]]), (Q.W, Q.H))
    s = cv2.GaussianBlur(s, (0, 0), sig) * m
    out *= (1 - f * s)[..., None]
    return np.clip(np.round(out), 0, 255).astype(np.uint8), m, pec


def linhas_pdf(Q):
    """Os traços que ficam por cima dos pisos (bool, com 2 px de folga): as projeções e as linhas da DOC_LINHAS E
    PROJEÇÕES (o tracejado das lajes, os X dos vazios) e os elementos fixos."""
    if getattr(Q, "_linhas", None) is None:
        ss = 2
        m = np.zeros((Q.H * ss, Q.W * ss), np.uint8)
        for d in Q.desenhos:
            if d.get("layer") in LINHAS_FICAM and d["type"] == "s":
                for c in Q.caminhos(d):
                    cv2.polylines(m, [np.int32(np.round(c * ss))], False, 255, max(1, round(0.8 * ss)))
        m = cv2.resize(m, (Q.W, Q.H), interpolation=cv2.INTER_AREA) > 30
        Q._linhas = cv2.dilate(m.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    return Q._linhas


def pecas_cobertas(Q, q=None):
    """Os seqnos das peças escuras pequenas (até `coberta_max_pt2`) que o PDF cobre depois, em pelo menos `coberta` da
    área, com um branco da mesma camada: no desenho elas não aparecem (os dentes de 1,7 pt junto aos vidros)."""
    q = q or PAREDES_E
    if getattr(Q, "_cobertas", None) is None:
        brancos = [d for d in Q.desenhos if d.get("layer") in q["camadas"] and d["type"] in ("f", "fs") and d.get("fill")
                   and min(d["fill"]) > 0.9]
        Q._cobertas = set()
        for d in Q.desenhos:
            if d.get("layer") not in q["camadas"] or d["type"] not in ("f", "fs") or d.get("fill") is None or \
                    max(d["fill"]) >= 0.5:
                continue
            r = d["rect"]
            if (r[2] - r[0]) * (r[3] - r[1]) > q["coberta_max_pt2"]:
                continue
            ss = 16
            w, h = max(1, int(np.ceil((r[2] - r[0]) * ss))), max(1, int(np.ceil((r[3] - r[1]) * ss)))
            m = np.zeros((h, w), np.uint8)
            for c in Q.caminhos(d):
                if len(c) >= 3:
                    cv2.fillPoly(m, [np.int32(np.round((np.array([Q.q2p(*v) for v in c]) - (r[0], r[1])) * ss))], 1)
            if not m.any():
                continue
            wb = np.zeros_like(m)
            for b in brancos:
                rb = b["rect"]
                if b.get("seqno", 0) > d.get("seqno", 0) and b.get("layer") == d.get("layer") and rb[0] < r[2] and \
                        rb[2] > r[0] and rb[1] < r[3] and rb[3] > r[1]:
                    for c in Q.caminhos(b):
                        if len(c) >= 3:
                            cv2.fillPoly(wb, [np.int32(np.round((np.array([Q.q2p(*v) for v in c]) - (r[0], r[1])) * ss))], 1)
            if (m & wb).sum() >= q["coberta"] * m.sum():
                Q._cobertas.add(d.get("seqno"))
    return Q._cobertas


def paredes_pdf(Q, folga=0):
    """As paredes do PDF (bool): os preenchimentos escuros da ARQ_PAREDE, com `folga` px."""
    if getattr(Q, "_par", None) is None:
        Q._par = Q.preencher(lambda d: d.get("layer") == "ARQ_PAREDE" and d.get("fill") is not None
                             and max(d["fill"]) < 0.5, ss=4)
    m = Q._par > 0.05
    if folga:
        m = cv2.dilate(m.astype(np.uint8), np.ones((2 * folga + 1,) * 2, np.uint8)).astype(bool)
    return m


def legenda(Q, cores, tol=4, fechar=5, dentro=None, area_min=300):
    """A mancha da legenda (bool), fechada, sem as manchas menores que `area_min` px (os px soltos da base que caem na
    cor de um piso: o tracejado do lote, as soleiras pequenas, que ficam como estão)."""
    m = Q.cor(cores, tol=tol)
    m = F.fechar(m, fechar) if fechar else m
    if dentro is not None:
        m &= dentro
    if area_min:
        n, lab, st, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8), 8)
        ok = st[:, cv2.CC_STAT_AREA] >= area_min
        ok[0] = False
        m = ok[lab]
    return m


# ----------------------------------------------------------------------------------------------------------------------
# E10: as paredes em cinza 80 e os pilares em preto. As paredes são os preenchimentos escuros da ARQ_PAREDE e da
# ARQ_ELEMENTOS FIXOS (os muros, como nas Casas B a D; os brises dela, em madeira na final, ficam) que a final mostra escuros (`escuro_min` dos px num anel de 2 px; os que a final mostra como vidro, folha ou piso ficam como estão),
# pintados em cinza no contorno do PDF; antes, o preto antigo a até `folga_px` deles (a franja de 1 a 3 px que passa do
# PDF) é refeito pelo que está em volta, como no Subsolo da Casa A (`final3840_casaa.paredes`). O preto que sobra além
# da franja, até 15 px das paredes do PDF (paredes do render mais grossas que o desenho), vai ao mesmo cinza pela conta do
# alfa contra o piso de perto; o lote e o quadro, mais longe, ficam.
#
# As paredes limpas (usuário, 28/10/26: "CORRIJA A REPRESENTAÇÃO DAS PAREDES" e "CORRIJA ESSA IMPERFEIÇÃO NA PAREDE. NÃO
# ESSE DENTE"): as peças entram todas numa máscara só, desenhada em 4x e reduzida uma vez (antes, cada peça vinha com o
# antialias dela e a junta de duas peças vizinhas, a 50% de cada lado, deixava ver o fundo: os fios claros e escuros
# dentro das paredes, nos encontros dos tocos e nas diagonais das pontas); a peça escura que o PDF cobre depois com
# um branco da mesma camada (`pecas_cobertas`: `coberta` da área sob os brancos de seqno maior), se for pequena (até
# `coberta_max_pt2`: as peças grandes sob os brancos, como as pontas das paredes sob as bordas da piscina, são parede na
# final) e se a final já a mostra clara, sai como no desenho: os dentes de 1,7 pt embaixo da parede da academia, junto
# ao vidro da piscina, onde a borda e o degrau da piscina passam por cima (`PISCINA_E["dentes"]`); e a franja escura do render que passa do
# contorno (`franja`: até `folga_px` fora da parede, mais escura que `franja[0]` e com croma até `franja[1]`) é
# refeita pelo piso em volta, como o preto; e, no Subsolo (`ini`), também a sobra cinza da parede antiga do render, que
# era ~1 px mais larga que o preenchimento do PDF e deixava um contorno irregular e um chapéu claro nos tocos ("A PAREDE
# AQUI NÃO ESTÁ PERFEITA. PRECISO DELA RETA E SEM DENTE"; "ESSA PAREDE DA SAUNA TEM UM DENTE TAMBÉM").
PAREDES_E = {"cor": (80, 80, 80), "camadas": ("ARQ_PAREDE", "ARQ_ELEMENTOS FIXOS"), "escuro": 48, "croma": 12, "folga_px": 3, "escuro_min": 0.25,
             "coberta": 0.9, "coberta_max_pt2": 10.0, "franja": (64, 22), "sobra": 0.88,
             "pilar_cor": (8, 8, 8), "pilar_camadas": ("EST - Pilar", "EST_PILAR")}


def paredes_e(Q, img, q=None, extra=None, pilares=True, sempre=(), ini=None, tirar=(), por=(), brancos=()):
    """`extra`: a máscara (0 a 1) de outras paredes, somada por cima, ou um filtro dos desenhos do PDF, que entram na
    mesma máscara das paredes (sem a conta do escuro). `sempre`: caixas (pt) onde toda peça escura do PDF é parede, mesmo
    onde a final a mostra clara (a piscina do Subsolo, onde o render pintou água sobre as pontas das paredes). `ini`: a
    final aprovada sem os rótulos; com ela, a sobra da parede antiga do render em volta da nova (os px a até `folga_px`
    que nenhuma etapa redesenhou e que são mais escuros que o piso de perto, `sobra`) sai também, refeita pelo piso.
    `tirar`: retângulos (pt) cujas peças escuras de dentro saem; `por`: retângulos (pt) que entram na parede (os dentes
    das pontas de parede trocados pela face reta); `brancos`: retângulos (pt) que o PDF pinta de branco por cima da
    parede, depois dela (o contorno de baixo da piscina, `PISCINA_E["contorno"]`): saem da máscara e ficam como estão."""
    q = q or PAREDES_E
    im = img.astype(np.int16)
    preto = (im.max(axis=2) < q["escuro"]) & ((im.max(axis=2) - im.min(axis=2)) <= q["croma"])
    ss = 4
    filtro_extra = extra if callable(extra) else None
    cobertas = pecas_cobertas(Q, q)
    n_ok = n_fora = n_coberta = 0
    pecas = []
    for d in Q.desenhos:
        if d["type"] not in ("f", "fs") or d.get("fill") is None or max(d["fill"]) >= 0.5:
            continue
        de_extra = filtro_extra is not None and filtro_extra(d)
        if d.get("layer") not in q["camadas"] and not de_extra:
            continue
        cs = [c for c in Q.caminhos(d) if len(c) >= 3]
        if not cs:
            continue
        pts = np.vstack(cs)
        x0, y0 = np.floor(pts.min(axis=0)).astype(int) - 3
        x1, y1 = np.ceil(pts.max(axis=0)).astype(int) + 4
        x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, Q.W), min(y1, Q.H)
        if x1 <= x0 or y1 <= y0:
            continue
        m = np.zeros(((y1 - y0) * ss, (x1 - x0) * ss), np.uint8)
        for c in cs:
            cv2.fillPoly(m, [np.int32(np.round((c - (x0, y0)) * ss))], 255)
        if not m.any():
            continue
        # a peça pequena que o PDF cobre depois com um branco da mesma camada, e que a final já mostra clara, não
        # aparece no desenho (onde a final mostra parede, ela fica)
        if d.get("seqno") in cobertas:
            ad = cv2.resize(m, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
            if preto[y0:y1, x0:x1][ad > 0.5].mean() < 0.5:
                n_coberta += 1
                continue
        r = d["rect"]
        if any(r[0] >= c[0] - 0.01 and r[2] <= c[2] + 0.01 and r[1] >= c[1] - 0.01 and r[3] <= c[3] + 0.01
               for c in tirar):
            continue
        livre = any(r[0] >= c[0] and r[2] <= c[2] and r[1] >= c[1] and r[3] <= c[3] for c in sempre)
        if not de_extra and not livre:
            ad = cv2.resize(m, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
            anel = cv2.dilate((ad > 0.05).astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
            if preto[y0:y1, x0:x1][anel].mean() < q["escuro_min"]:
                n_fora += 1
                continue
        pecas.append(cs)
        n_ok += 1
    for r in por:
        (u0, v0), (u1, v1) = Q.p2q(r[0], r[1]), Q.p2q(r[2], r[3])
        pecas.append([np.float32([(u0, v0), (u1, v0), (u1, v1), (u0, v1)])])
    # todas as peças numa máscara só (em 4x, por faixas), reduzida uma vez: sem as juntas entre as peças
    a = np.zeros((Q.H, Q.W), np.float32)
    faixa = 256
    for fy in range(0, Q.H, faixa):
        fy1 = min(Q.H, fy + faixa)
        m = np.zeros(((fy1 - fy) * ss, Q.W * ss), np.uint8)
        for cs in pecas:
            for c in cs:
                if c[:, 1].max() >= fy - 1 and c[:, 1].min() <= fy1 + 1:
                    cv2.fillPoly(m, [np.int32(np.round((c - (0, fy)) * ss))], 255)
        a[fy:fy1] = cv2.resize(m, (Q.W, fy1 - fy), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    if extra is not None and not callable(extra):
        a = np.maximum(a, extra)
    if brancos:
        bx0, by0, bx1, by1 = F.ret_q(Q, (min(r[0] for r in brancos), min(r[1] for r in brancos),
                                         max(r[2] for r in brancos), max(r[3] for r in brancos)))
        bx0, by0, bx1, by1 = bx0 - 2, by0 - 2, bx1 + 2, by1 + 2
        a[by0:by1, bx0:bx1] = np.clip(a[by0:by1, bx0:bx1] - _ret_pdf(Q, brancos, bx0, by0, bx1 - bx0, by1 - by0), 0, 1)
    k = 2 * q["folga_px"] + 1
    perto = cv2.dilate((a > 0.02).astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool)
    franja = perto & (a < 0.5) & (im.max(axis=2) < q["franja"][0]) & ((im.max(axis=2) - im.min(axis=2)) <= q["franja"][1])
    M = perto & (preto | franja)
    n_sobra = 0
    if ini is not None:
        # a sobra da parede antiga: o render a fazia ~1 px mais larga que o preenchimento do PDF (e com um chapéu claro
        # nas pontas); os px que ficaram como na final aprovada e mais escuros que o piso claro de perto
        igual = np.abs(im - ini.astype(np.int16)).max(axis=2) <= 2
        lum = im.mean(axis=2).astype(np.float32)
        claro = cv2.dilate(np.where(a < 0.02, lum, 0).astype(np.float32), np.ones((7, 7), np.uint8))
        sobra = perto & (a < 0.5) & igual & (lum < q["sobra"] * claro) & ~M
        n_sobra = int(sobra.sum())
        M |= sobra
    # o fundo de toda a parede (e do antialias dela) vem do piso de fora, não do preto ou do cinza antigo de dentro: a
    # borda sai regular
    out = cv2.inpaint(img, (M | (a > 0.02)).astype(np.uint8), 3, cv2.INPAINT_TELEA)
    out = out.astype(np.float32) * (1 - a[..., None]) + np.float32(q["cor"]) * a[..., None]
    # o preto que sobra longe do PDF: o alfa contra o piso de perto (a mediana dos px claros num raio de 4 px)
    resto = preto & ~perto & cv2.dilate((a > 0.02).astype(np.uint8), np.ones((31, 31), np.uint8)).astype(bool)
    n_resto = int(resto.sum())
    if n_resto:
        zona = cv2.dilate(resto.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
        claro = ~cv2.dilate((preto | (a > 0.02)).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        fundo = F.luz_robusta(out, claro & cv2.dilate(zona.astype(np.uint8), np.ones((11, 11), np.uint8)).astype(bool),
                              3.0, desvio=255)
        f = out
        lum, lf = f.mean(axis=2), np.maximum(fundo.mean(axis=2), 1)
        al = np.clip((lf - lum) / np.maximum(lf - 6, 1), 0, 1)
        novo = fundo * (1 - al[..., None]) + np.float32(q["cor"]) * al[..., None]
        out = np.where(zona[..., None], novo, out)
    if pilares:
        ap = Q.preencher(lambda d: d.get("layer") in q["pilar_camadas"] and d.get("fill") is not None
                         and max(d["fill"]) < 0.5, ss=4)
        out = out * (1 - ap[..., None]) + np.float32(q["pilar_cor"]) * ap[..., None]
    print(f"    paredes em cinza {q['cor'][0]} no contorno do PDF, numa máscara só (sem juntas): {n_ok} peças ({n_fora} "
          f"que a final mostra claras ficam; {n_coberta} cobertas por um branco do PDF saem); "
          f"{int((M & (a < 0.5)).sum())} px da franja escura refeitos ({n_sobra} da sobra da parede antiga); "
          f"{n_resto} px pretos fora do PDF ao cinza")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
# E3, E8: as escadas sem linhas e sem triângulo (R14): os degraus do PDF na pedra da escada (`textura`, no tom `tom`),
# marcados só pelo sombreamento das escadas aprovadas (`F.ESCADA_SOMBRA`: cada degrau um pouco mais claro que o de
# baixo, de 0,84 a 1, e a sombra curta de cada espelho no degrau de baixo; a do 1º degrau no piso de onde ela sobe); o
# trecho depois do corte do PDF nevoado, sem a linha de corte (no lugar dela, só uma sombra suave sobre os degraus de
# antes, como no Subsolo aprovado da Casa D); a letra S ou D do PDF em Inter SemiBold, cinza quase preto, centrada no
# 1º degrau de quem chega pelo pavimento (o sentido é o do triângulo da final aprovada: seção 18 das regras).
def escada_e(Q, img, e, ss=8):
    sys.path.insert(0, str(RAIZ / "_texturas"))
    from texturas import textura
    s = F.ESCADA_SOMBRA
    ex0, ey0, ex1, ey1 = e["pdf"]
    x0, y0, x1, y1 = F.ret_q(Q, (ex0 - 8, ey0 - 1, ex1 + 8, ey1 + 1))
    h, w = y1 - y0, x1 - x0
    (ax, ay), (bx, _), (_, cy) = Q.p2q(0, 0), Q.p2q(100, 0), Q.p2q(0, 100)
    X = np.repeat(((np.arange(x0, x1) + 0.5 - ax) / ((bx - ax) / 100))[None, :], h, axis=0)
    Y = np.repeat(((np.arange(y0, y1) + 0.5 - ay) / ((cy - ay) / 100))[:, None], w, axis=1)
    a = F.ret_aa_q(Q, e["pdf"])[y0:y1, x0:x1][..., None]
    bordas = [ex0] + list(e["bocels"]) + [ex1]
    n = len(bordas) - 1
    k = np.clip(np.searchsorted(bordas, X) - 1, 0, n - 1)
    direita = e["inicio"] == "direita"
    i = (n - 1 - k) if direita else k                                      # 0 = o 1º degrau
    rng = np.random.default_rng(e.get("semente", 2805))
    tons = 1 + rng.uniform(-s["tom_degrau"], s["tom_degrau"], n)
    t0, t1 = s["tom"]
    f = (t0 + (t1 - t0) * i / max(n - 1, 1)) * tons[i]
    fs, alc = s["espelho"]
    pt_px = Q.px_m / 56.69
    esp = np.array(bordas)[k if direita else k + 1]
    dist = ((X - esp) if direita else (esp - X)) * pt_px
    f = f * np.where(i < n - 1, 1 - fs * np.exp(-np.maximum(dist, 0) / alc), 1.0)
    if e["textura"] == "travertino_e":
        # o travertino bruto em estratos (pedidos de 28/10), com o veio no comprido de cada degrau
        novo = travertino_e(Q, h, w, e.get("semente", 2805), vertical=True)[..., None] * np.float32(e["tom"]) * f[..., None]
    else:
        T = textura(e["textura"], Q.px_m, h, w, semente=e.get("semente", 2805)).astype(np.float32)
        det = cv2.GaussianBlur(T, (0, 0), 0.6) / np.maximum(cv2.GaussianBlur(T, (0, 0), 3.0 * Q.px_m), 1)
        novo = (1 + e.get("forca", 1.0) * (det - 1)) * np.float32(e["tom"]) * f[..., None]
    depois = np.zeros((h, w, 1), np.float32)
    if e.get("corte"):
        c0, c1 = e["corte"][0], e["corte"][-1]
        lado = e["apos"]                                                    # o lado da escada depois do corte
        extremo = ex0 - 10 if lado == "esquerda" else ex1 + 10
        pts = [c0, c1, (extremo, c1[1] + (3 if c1[1] > c0[1] else -3)), (extremo, c0[1] + (-3 if c1[1] > c0[1] else 3))]
        m = np.zeros((h * ss, w * ss), np.uint8)
        cv2.fillPoly(m, [np.int32(np.round((np.float32([Q.p2q(x, y) for x, y in pts]) - (x0, y0)) * ss))], 255)
        depois = cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None]
        nv = e["nevoa"]
        nevoa = cv2.GaussianBlur(novo, (0, 0), nv["sigma_px"]) * (1 - nv["branco"]) + 255 * nv["branco"]
        novo = novo * (1 - depois) + nevoa * depois
    out = img.astype(np.float32)
    reg = out[y0:y1, x0:x1]
    # a sombra do espelho do 1º degrau no piso de onde a escada sobe (fora da escada)
    fp, ap = s["piso"]
    xb = ex1 if direita else ex0
    dp = ((X - xb) if direita else (xb - X)) * pt_px
    faixa = (Y >= ey0) & (Y <= ey1)
    sp = np.where((dp > 0) & faixa, fp * np.exp(-dp / ap), 0.0)[..., None]
    reg[:] = reg * (1 - sp * (1 - a))
    reg[:] = reg * (1 - a) + novo * a
    if e.get("corte") and e.get("sombra_corte"):
        sc = e["sombra_corte"]
        c0, c1 = e["corte"][0], e["corte"][-1]
        ml = np.zeros((h * ss, w * ss), np.uint8)
        cv2.line(ml, tuple(np.int32(np.round((np.float32(Q.p2q(*c0)) - (x0, y0)) * ss))),
                 tuple(np.int32(np.round((np.float32(Q.p2q(*c1)) - (x0, y0)) * ss))), 255, ss, cv2.LINE_AA)
        al = cv2.resize(ml.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)
        d = cv2.distanceTransform((al < 0.5).astype(np.uint8), cv2.DIST_L2, 5)
        fc = 1 - sc["forca"] * np.exp(-d / sc["alc_px"]) * (1 - depois[..., 0]) * a[..., 0]
        reg[:] = reg * fc[..., None]
    out = np.clip(out, 0, 255).astype(np.uint8)
    no_alto = e.get("letra_no_alto", False)                               # o D no degrau de cima, de onde se desce
    b = bordas[-2:] if direita != no_alto else bordas[:2]
    if e.get("letra"):
        out = F.letra(Q, out, e["letra"], Q.p2q((b[0] + b[1]) / 2, (ey0 + ey1) / 2))
    print(f"    escada {e['nome']}: {n} degraus em {e['textura']}, sem linhas e sem triângulo, com o sombreamento "
          f"{'de descida' if no_alto else 'de subida'}; {'o trecho depois do corte nevoado; ' if e.get('corte') else ''}"
          + (f"o {e['letra']} no degrau {'de cima' if no_alto else '1'}" if e.get("letra") else "sem a letra"))
    return out


# E2: o armário cortado com os cabides (R11, como os closets das Casas A a D e o DCE 1 da Casa D): o guarda-roupa aberto
# (`elementos.guarda_roupa`), no retângulo do PDF, com as portas para o lado `lado` (o do ambiente)
def armario_cabides(Q, img, r, lado, semente=57, nome="armário"):
    sys.path.insert(0, str(RAIZ / "_texturas"))
    from elementos import guarda_roupa
    from retoque_1pav_casae import GUARDA_ROUPAS
    S = 4
    x0, y0, x1, y1 = r
    (u0, v0), (u1, v1) = Q.p2q(x0, y0), Q.p2q(x1, y1)
    comp, prof = max(x1 - x0, y1 - y0) / 56.69, min(x1 - x0, y1 - y0) / 56.69
    cor, alfa = guarda_roupa(comp, prof, Q.px_m * S, semente=semente, miolo=GUARDA_ROUPAS["miolo"],
                             moldura=GUARDA_ROUPAS["moldura"], barra=True)
    k = {"baixo": 0, "direita": 1, "cima": 2, "esquerda": 3}[lado]
    if (x1 - x0) < (y1 - y0) and k in (0, 2):
        k += 1
    cor, alfa = np.ascontiguousarray(np.rot90(cor, k)), np.ascontiguousarray(np.rot90(alfa, k))
    X0, Y0, X1, Y1 = int(np.floor(u0)), int(np.floor(v0)), int(np.ceil(u1)), int(np.ceil(v1))
    tw, th = int(round((u1 - u0) * S)), int(round((v1 - v0) * S))
    ox, oy = int(round((u0 - X0) * S)), int(round((v0 - Y0) * S))
    grande = np.zeros(((Y1 - Y0) * S, (X1 - X0) * S, 3), np.float32)
    ag = np.zeros(grande.shape[:2], np.float32)
    grande[oy:oy + th, ox:ox + tw] = cv2.resize(cor, (tw, th), interpolation=cv2.INTER_AREA)
    ag[oy:oy + th, ox:ox + tw] = cv2.resize(alfa, (tw, th), interpolation=cv2.INTER_AREA)
    cr = cv2.resize(grande, (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA)
    ar = cv2.resize(ag, (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA)[..., None]
    out = img.astype(np.float32)
    out[Y0:Y1, X0:X1] = out[Y0:Y1, X0:X1] * (1 - ar) + cr
    print(f"    {nome}: o armário com os cabides e o cabideiro ({comp:.2f} x {prof:.2f} m), as portas para {lado}")
    return np.clip(out, 0, 255).astype(np.uint8)


# E9: a bancada mais marcada que o piso: a borda fina no tom escurecido da própria pedra (só nas faces livres, longe da
# parede) e a sombra curta no piso (luz do alto à direita); a pedra, a cuba e a torneira ficam as da final
BANCADA_E9 = {"borda": 0.70, "larg_px": 0.8, "sombra": (0.30, 1.3, 1.5)}


def bancada_e9(Q, img, r, nome="bancada", q=None):
    q = q or BANCADA_E9
    ss = 8
    x0, y0, x1, y1 = r
    X0, Y0, X1, Y1 = F.ret_q(Q, (x0 - 6, y0 - 6, x1 + 6, y1 + 6))
    h, w = Y1 - Y0, X1 - X0
    (u0, v0), (u1, v1) = Q.p2q(x0, y0), Q.p2q(x1, y1)
    m = np.zeros((h * ss, w * ss), np.uint8)
    cv2.rectangle(m, (round((u0 - X0) * ss), round((v0 - Y0) * ss)), (round((u1 - X0) * ss) - 1, round((v1 - Y0) * ss) - 1),
                  255, -1)
    a = cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)
    lb = max(1, int(round(q["larg_px"] * ss)))
    mb = np.zeros_like(m)
    cv2.rectangle(mb, (round((u0 - X0) * ss) + lb // 2, round((v0 - Y0) * ss) + lb // 2),
                  (round((u1 - X0) * ss) - 1 - lb // 2, round((v1 - Y0) * ss) - 1 - lb // 2), 255, lb)
    ab = cv2.resize(mb.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)
    par = paredes_pdf(Q, folga=1)[Y0:Y1, X0:X1]
    ab = ab * ~cv2.dilate(par.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    out = img.astype(np.float32)
    reg = out[Y0:Y1, X0:X1]
    pedra = np.median(reg[a > 0.9], axis=0)
    f, dist, sig = q["sombra"]
    s = cv2.warpAffine(a, np.float32([[1, 0, -dist], [0, 1, dist]]), (w, h))
    s = cv2.GaussianBlur(s, (0, 0), sig) * (1 - a) * ~par
    reg *= (1 - f * s)[..., None]
    reg[:] = reg * (1 - ab[..., None]) + (pedra * q["borda"]) * ab[..., None]
    print(f"    {nome}: a borda no tom escurecido da pedra e a sombra curta (E9)")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# E5: o box de correr em vidro contínuo (como os boxes das Casas A a D, `final3840_casaa.boxes`): as duas folhas do PDF
# (`AJ.folhas_box`), cada uma uma faixa de vidro com as faces finas e a sombra curta, fechadas, de parede a parede, sem
# o trilho tracejado (28/10), só nos boxes dentro de `caixa_pt`
def box_e(Q, img, caixa_pt, nome="box"):
    import final3840_casaa as FA
    x0, y0, x1, y1 = caixa_pt
    todos = AJ.folhas_box
    try:
        AJ.folhas_box = lambda pg: [b for b in todos(pg) if all(x0 <= f[0] and f[2] <= x1 and y0 <= f[1] and f[3] <= y1
                                                                for f in b["folhas"])]
        out = FA.boxes(Q, np.ascontiguousarray(img.copy()))
    finally:
        AJ.folhas_box = todos
    print(f"    ({nome})")
    return out


# E3, E8: os degraus em blocos (os retângulos sobrepostos da ARQ_CONTRAPISO, como os blocos em cascata das Casas B e D):
# cada bloco em Bege Bahia no tom do piso em volta, sem o contorno, o de baixo um pouco mais escuro e com a sombra curta
# do de cima; a letra no bloco de cima (de onde se desce)
def blocos_e(Q, img, q):
    sys.path.insert(0, str(RAIZ / "_texturas"))
    from texturas import textura
    cx0, cy0, cx1, cy1 = q["caixa_pt"]
    blocos = [d for d in Q.desenhos if d.get("layer") == "ARQ_CONTRAPISO" and d["type"] == "f" and d.get("fill")
              and cx0 <= d["rect"].x0 and d["rect"].x1 <= cx1 and cy0 <= d["rect"].y0 and d["rect"].y1 <= cy1
              and d["rect"].width * d["rect"].height > 200]
    blocos.sort(key=lambda d: d.get("seqno", 0), reverse=q.get("inverter", False))
    k = 4
    X0, Y0, X1, Y1 = F.ret_q(Q, q["caixa_pt"])
    w, h = X1 - X0, Y1 - Y0
    out = img.astype(np.float32)
    reg = out[Y0:Y1, X0:X1]
    bege = legenda(Q, [(232, 232, 232)])
    perto = np.zeros_like(bege)
    perto[max(Y0 - 60, 0):Y1 + 60, max(X0 - 60, 0):X1 + 60] = True
    tom = np.median(img[bege & perto].reshape(-1, 3), axis=0)              # o Bege Bahia em volta da escada
    s = q["sombra"]
    d_ = s["dist_m"] * Q.px_m * k

    def reduzir(a):
        return cv2.resize(a.astype(np.float32), (w, h), interpolation=cv2.INTER_AREA)
    # a ordem do alto para baixo: o bloco de cima é o `topo` (o último desenhado cobre os outros no PDF)
    n = len(blocos)
    for i, d in enumerate(blocos):
        m = np.zeros((h * k, w * k), np.uint8)
        cv2.fillPoly(m, [np.int32(np.round((c - (X0, Y0)) * k)) for c in Q.caminhos(d) if len(c) >= 3], 255)
        mf = m.astype(np.float32) / 255
        a = reduzir(mf)
        nivel = i if q["topo_primeiro"] else n - 1 - i                    # 0 = o bloco de cima
        sb = reduzir(cv2.GaussianBlur(cv2.warpAffine(mf, np.float32([[1, 0, -d_], [0, 1, d_]]), (w * k, h * k)),
                                      (0, 0), s["sig_m"] * Q.px_m * k)) * s["forca"]
        T = textura("bege_bahia", Q.px_m, h, w, semente=q["semente"] + i).astype(np.float32)
        T = T / T.reshape(-1, 3).mean(axis=0) * tom * (1 - q["tom"] * nivel)
        if q["topo_primeiro"]:
            # os de baixo vêm depois e cobrem os de cima: a sombra do de cima cai sobre eles, não aqui
            reg[:] = reg * (1 - a[..., None]) + T * a[..., None]
            continue
        reg *= (1 - sb * (1 - a))[..., None]
        reg[:] = reg * (1 - a[..., None]) + T * a[..., None]
    if q["topo_primeiro"]:
        # as sombras: cada bloco desenhado antes (mais alto) faz sombra sobre os depois dele, onde eles o cobrem
        for i, d in enumerate(blocos[:-1]):
            m = np.zeros((h * k, w * k), np.uint8)
            cv2.fillPoly(m, [np.int32(np.round((c - (X0, Y0)) * k)) for c in Q.caminhos(d) if len(c) >= 3], 255)
            de_baixo = np.zeros_like(m)
            for d2 in blocos[i + 1:]:
                cv2.fillPoly(de_baixo, [np.int32(np.round((c - (X0, Y0)) * k)) for c in Q.caminhos(d2) if len(c) >= 3], 255)
            visivel = (m > 0) & (de_baixo == 0)
            sb = cv2.GaussianBlur(cv2.warpAffine(visivel.astype(np.float32), np.float32([[1, 0, -d_], [0, 1, d_]]),
                                                 (w * k, h * k)), (0, 0), s["sig_m"] * Q.px_m * k) * (de_baixo > 0)
            reg *= (1 - s["forca"] * reduzir(sb))[..., None]
    out = np.clip(out, 0, 255).astype(np.uint8)
    if q.get("letra"):
        out = F.letra(Q, out, q["letra"], Q.p2q(*q["letra_pt"]))
    print(f"    {q['nome']}: {n} blocos de pedra do PDF em Bege Bahia, sem contorno, cada um com a sombra curta do de "
          f"cima; " + (f"o {q['letra']} no bloco de cima" if q.get("letra") else "sem a letra"))
    return out


# E4: a seta da entrada principal, como a do Térreo da Casa A (`final3840_casaa_terreo.seta`: cheia, preta, de 1,5 m,
# apontando para a esquerda, com a ponta em `ponta`, px do quadro)
def seta_e(Q, img, ponta):
    import final3840_casaa_terreo as FT
    guarda = FT.SETA
    FT.SETA = dict(guarda, ponta=ponta)
    try:
        return FT.seta(Q, img)
    finally:
        FT.SETA = guarda


# ----------------------------------------------------------------------------------------------------------------------
# O Subsolo (auditoria de 26/10, mapa `renders/POE642_CasaE_PH_Subsolo_auditoria_2610.jpg`, e as regras aprovadas nos
# Subsolos das Casas A a D):
# 1. E11: os pisos nas texturas e escalas das Casas B a D: o vinílico da academia nas réguas do 1º Pavimento e das Casas
#    B a D, no tom dele; o granito do DCE e da casa de máquinas de baixo no granito de referência das Casas B a D (o do
#    Térreo da Casa E, RGB ~116, 87, 68; era o Marrom Tabaco escuro, ~83, 59, 52); o Bege Bahia (circulação, depósito,
#    casa de máquinas da direita e WC DCE 2) na foto da biblioteca no tom das Casas B a D; o travertino (sauna, ambiente,
#    vestiário) no travertino bruto em estratos (`TRAVERTINO_E`, pedidos de 28/10; antes, a foto da biblioteca);
# 2. E3, E8: a escada da circulação sem as linhas e sem o triângulo: os 17 degraus no travertino, com o sombreamento de
#    subida da direita para a esquerda (o sentido do triângulo aprovado em 20/10: "subindo da direita para esquerda, com
#    a parte da direita viva"), o trecho depois do corte do PDF (à esquerda) nevoado, sem a linha de corte, e o S do PDF
#    no 1º degrau (o da direita);
# 3. E2: o armário do DCE (o retângulo com a diagonal da ARQ_LAYOUT HUMANIZAÇÃO, junto à parede de baixo) com os
#    cabides, aberto para o quarto;
# 4. E9: a bancada do WC DCE 2 com a borda no tom escurecido da pedra e a sombra curta;
# 5. E10: as paredes em cinza 80 (não há pilares no Subsolo; os da EST - Pilar são do Térreo, fora da pegada);
# 6. E7: o rótulo do WC DCE 2 fora da área do chuveiro: no meio do piso seco, entre a porta, a bancada e o vaso, no corpo
#    0,85 do PDF.
# Pedidos de 28/10, vendo a final do Subsolo (usuário: "MELHORE O ASPECTO DO MARMORE TRAVERTINO"; no vestiário, "PISO EM
# MARMORE TRAVERTINO BRUTO"; e a referência da sauna, a vista de cima do modelo 3D): o travertino bruto em estratos
# aprovado nas Casas C e D (`final3840_casac.travertino_estratos`, com os veios marcados e os poros abertos da Casa D,
# `final3840_casad.TRAVERTINO_BRUTO_D`), sem o tom quente das faixas (puxava para o rosado), no creme claro da
# referência; os veios correm na vertical, como na sauna da referência (`vertical`). Antes, era a foto da biblioteca
# borrada, quase lisa e rosada. Nos pisos da sauna, do ambiente e do vestiário, nos degraus da escada da circulação e
# nos bancos da sauna (`sauna_e`).
TRAVERTINO_E = {"tom": (204, 222, 233), "base": 1.0, "amp": 1.3, "finas": 1.0, "poros": 8.0, "poro_esc": 0.2,
                "vertical": True, "luz_m": 3.0}                                                          # tom em BGR


def travertino_e(Q, h, w, semente, vertical=None, amp=None, finas=None):
    """O desenho do travertino bruto em estratos (h x w, média ~1), com os veios na vertical (`vertical`) ou deitados."""
    import final3840_casac as C
    q = TRAVERTINO_E
    v = q["vertical"] if vertical is None else vertical
    hh, ww = (w, h) if v else (h, w)
    D = C.travertino_estratos(Q, hh, ww, semente, base=q["base"], poros=q["poros"], poro_esc=q["poro_esc"],
                              amp=q["amp"] if amp is None else amp, finas=q["finas"] if finas is None else finas,
                              quente=False)
    return np.ascontiguousarray(D.T) if v else D


def piso_textura_e(Q, img, m, nome, forca, sig_m, semente):
    """`F.piso_textura`, e o travertino bruto em estratos (`travertino_e`) na luz larga do próprio piso, no tom dele."""
    if nome != "travertino_e":
        return F.piso_textura(Q, img, m, nome, forca, sig_m, semente)
    ys, xs = np.nonzero(m)
    y0, x0, y1, x1 = ys.min(), xs.min(), ys.max() + 1, xs.max() + 1
    L = F.luz_robusta(img, m, sig_m * Q.px_m)
    L = L / np.maximum(np.median(L[m], axis=0), 1.0)
    novo = img.astype(np.float32).copy()
    novo[y0:y1, x0:x1] = L[y0:y1, x0:x1] * np.float32(TRAVERTINO_E["tom"]) * \
        travertino_e(Q, y1 - y0, x1 - x0, semente)[..., None]
    return novo


PISOS_SUB_E = [("granito", [(50, 66, 90)], "granito", (68, 87, 116), 1.5, 2801, None),
               ("vinílico", [(79, 120, 168)], "vinilico", None, 1.0, 2802, None),
               ("Bege Bahia", [(232, 232, 232)], "bege", (187, 211, 230), 1.5, 2803, None),
               ("travertino", [(202, 217, 220)], "travertino_e", None, TRAVERTINO_E["luz_m"], 2804, None)]
ESCADA_SUB_E = {"nome": "da circulação", "pdf": (972.0, 617.0, 1261.2, 685.0),
                "bocels": [972.0 + 17.0 * k for k in range(1, 17)], "inicio": "direita", "apos": "esquerda",
                "corte": [(1073.8, 616.4), (1108.1, 685.0)], "nevoa": {"branco": 0.72, "sigma_px": 1.2},
                "sombra_corte": {"forca": 0.30, "alc_px": 4.0}, "textura": "travertino_e", "tom": TRAVERTINO_E["tom"],
                "forca": 1.0, "letra": "S", "semente": 2805}
ARMARIO_DCE_E = {"pt": (1439.8, 795.5, 1507.8, 829.6), "lado": "cima"}
BANCADA_WC_DCE2 = (1697.6, 693.5, 1726.1, 729.1)
# a casa de máquinas da direita (5,83 m²) no corpo 0,85 e no centro do cômodo (entre as paredes e da soleira à parede
# de baixo: usuário, 28/10/26, "CENTRALIZE O RÓTULO PARA NÃO ENCOSTAR NAS BORDAS"; no corpo 1,0 o nome ia de parede a
# parede)
AJUSTES_E["Subsolo"] = [("CASA DE MÁQUINAS", (1043.4, 335.8), (0, -22.5), 0.85),
                        ("WC DCE 2", (986.5, 310.9), (-3.9, -30.0), 0.85),
                        # o ELEVADOR no centro da cabine, no corpo do PDF (usuário, 28/10/26: "CENTRALIZE O RÓTULO"; no
                        # ponto do PDF e no corpo 1,3 ele ia à direita e encostava no contorno da cabine)
                        ("ELEVADOR", (1044.65, 400.14), (-3.9, -1.3), 1.0)]


def pisos_e(Q, img, specs, ficam=(), zonas=None, incluir=None):
    """ficam: peças da final que o PDF não desenha e que têm a cor do piso (círculos: centro e raio em px do quadro).
    zonas: onde as peças antigas saem e o piso passa por inteiro, também nos buracos da legenda (os aparelhos da
    academia, que são desenhados depois). incluir: {nome do piso: bool} entra na legenda dele, sem as peças antigas
    (as zonas das portas, refeitas depois)."""
    from scipy import ndimage
    ini = img.copy()
    out = img.copy()
    extra = np.zeros((Q.H, Q.W), np.uint8)
    for cx, cy, r in ficam:
        cv2.circle(extra, (int(round(cx)), int(round(cy))), int(round(r)), 1, -1)
    for nome, cores, tex, tom, sig, sem, forca in specs:
        leg = legenda(Q, cores)
        fora = None
        if zonas is not None and (leg & zonas).any():
            leg |= ndimage.binary_fill_holes(leg) & zonas
            fora = zonas
        if incluir and nome in incluir:
            leg |= incluir[nome]
            fora = incluir[nome] if fora is None else (fora | incluir[nome])
        out, m, _ = troca_piso(Q, out, ini, leg, tex, tom, sig, sem, forca=forca, pecas=extra.astype(bool),
                               fora_pecas=fora)
        print(f"    {nome}: {m.sum() / Q.px_m ** 2:.1f} m² ({tex}, na escala da prancha)")
    return out


def _ret_local(Q, r, X0, Y0, w, h, ss=8):
    """O retângulo r (pt) na janela (X0, Y0, w x h) do quadro, com antialias (0 a 1)."""
    (x0, y0), (x1, y1) = Q.p2q(r[0], r[1]), Q.p2q(r[2], r[3])
    m = np.zeros((h * ss, w * ss), np.uint8)
    cv2.rectangle(m, (round((x0 - X0) * ss), round((y0 - Y0) * ss)), (round((x1 - X0) * ss) - 1, round((y1 - Y0) * ss) - 1),
                  255, -1)
    return cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255


def _ret_pdf(Q, rs, X0, Y0, w, h, ss=4):
    """Os retângulos rs (pt) na janela, rasterizados como os preenchimentos do PDF (`Q.preencher` e as peças de
    `paredes_e`: fillPoly a `ss` x, com o mesmo arredondamento), para que uma borda comum com eles caia no mesmo subpixel
    e a subtração não deixe linha."""
    m = np.zeros((h * ss, w * ss), np.uint8)
    for r in rs:
        c = np.float32([Q.p2q(r[0], r[1]), Q.p2q(r[2], r[1]), Q.p2q(r[2], r[3]), Q.p2q(r[0], r[3])]) - (X0, Y0)
        cv2.fillPoly(m, [np.int32(np.round(c * ss))], 255)
    return cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255


def _uniao(Q, rs, X0, Y0, w, h, ss=8):
    """Os retângulos rs (pt) juntos na janela, numa máscara só (em `ss` x, reduzida uma vez: sem a junta a 50% entre
    retângulos vizinhos, que deixava ver o fundo)."""
    m = np.zeros((h * ss, w * ss), np.uint8)
    for r in rs:
        (x0, y0), (x1, y1) = Q.p2q(r[0], r[1]), Q.p2q(r[2], r[3])
        cv2.rectangle(m, (round((x0 - X0) * ss), round((y0 - Y0) * ss)),
                      (round((x1 - X0) * ss) - 1, round((y1 - Y0) * ss) - 1), 255, -1)
    return cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255


# A piscina (usuário, 28/10/26: "AS BORDAS EXISTENTES DA PISCINA SÃO EM MARMORE BEGE BAHIA. ESSA BORDA É QUASE
# IMPERCEPTÍVEL NA VISTA."; e, com a referência da sauna: "NOTE TAMBÉM O TOM DA PISCINA QUE ADOTAREMOS"; "TEM UM DEGRAU
# NO MESMO NIVEL DO PISO DA SAUNA E VAI ATÉ A BORDA DO VIDRO, FORMANDO UM BANCO DENTRO DA PISCINA, MAS AINDA DENTRO DO
# AMBIENTE DA SAUNA"). Antes, a água era um ciano claro e lavado, as bordas um bege pálido que se perdia nele, e a
# faixa entre as duas partes da piscina e a borda junto à sauna (os brancos da ARQ_PAREDE do PDF) iam como água.
# - a água (os preenchimentos azuis da ARQ_CONTRAPISO) no turquesa da referência: as peças de 14,5 cm do Barlavento (o
#   revestimento da legenda, `fontes_procedurais.barlavento`), cada uma num tom um pouco diferente, a variação larga do
#   fundo e as cáusticas (a rede clara da luz na água); antes, o Barlavento ia sob uma água verde-azulada clara;
# - as bordas (os brancos da ARQ_PAREDE em volta da água, fora da sauna) em Bege Bahia, no tom dos pisos de Bege Bahia,
#   com a quina marcada (um fio escuro na beira) e a sombra curta da borda na água;
# - dentro da sauna, a faixa de cima da piscina interna (do vidro até a sauna) e a da beira junto ao piso da sauna são
#   o degrau no nível do piso da sauna, em travertino (o desenho e o tom do piso), com a quina e a sombra na água;
# - o vidro (os painéis da ARQ_PAREDE entre a piscina, a academia e a piscina interna) redesenhado fino por cima.
PISCINA_E = {"caixa_pt": (688.0, 675.0, 1004.0, 1124.0), "agua_fill": (0.5, 0.87, 1.0),
             "tom": (168, 160, 42), "claro": (204, 226, 168),                       # BGR: turquesa e o claro da luz
             "peca_cm": 14.5, "pastilha_var": 0.06, "fundo": 0.07,
             "causticas": [(0.32, 0.55), (0.13, 0.35)], "caustica_larg": 0.22,
             "bege": [(694.2, 679.3, 705.6, 1118.7), (705.6, 679.3, 807.6, 690.7), (796.3, 690.7, 812.2, 968.5)],
             # sem a divisória entre a piscina e a parte de baixo (usuário, 28/10/26: "REMOVA ESSA DIVISÓRIA DA
             # PISCINA"): a faixa branca do PDF vira água, contínua, até a coluna de Bege Bahia; a coluna desce até o
             # fundo do degrau da sauna e as duas bordas se juntam no vidro numa quina só ("JUNTE AS BORDAS, FORMANDO
             # APENAS UMA QUINA")
             "agua_extra": [(705.6, 957.1, 796.3, 968.5)],
             # os dentes de 1,7 pt embaixo da parede da academia, junto ao vidro, que o PDF cobre de branco: a borda e
             # o degrau passam por cima deles (sem eles, a parede é reta)
             "dentes": [(807.6, 957.1, 812.2, 958.8), (815.0, 957.1, 819.0, 958.8)],
             "tom_bege": (190, 213, 231), "semente_bege": 2831,
             # o contorno de baixo (revisão de 28/10, item 1, OK do usuário): no PDF, a faixa branca da borda (os
             # brancos da ARQ_PAREDE pintados depois do cinza, por cima dele) desce pela esquerda até o fim, passa sob a
             # parede de baixo, sobe em degrau e segue sob a parte da direita até o degrau da sauna; ia como parede
             # (cinza, num bloco grosso). Em Bege Bahia, como o resto da borda; a parede fica só nas faixas cinza do
             # desenho (entre a água e a borda). `fundo_pt`: a janela da piscina desce até o fim dele
             # (nas coordenadas exatas do PDF: as bordas comuns com a parede caem no mesmo subpixel, `_ret_pdf`)
             "contorno": [(694.2426, 1091.0795, 705.5812, 1130.0304), (705.5812, 1118.6918, 807.6286, 1130.0304),
                          (796.29, 1096.1309, 807.6286, 1118.6918), (807.6286, 1096.1309, 888.915, 1107.4695)],
             "fundo_pt": 1132.0, "franja": 0.88,
             "degrau": [(815.0, 957.1, 890.0, 968.5), (877.6, 968.5, 890.0, 1096.1)],     # +1,1 pt: junta fechada
             "vidros": [(812.2, 693.5, 815.0, 945.8), (812.2, 957.1, 815.0, 1090.3)],
             "vidro": {"cor": (208, 214, 212), "alfa": 0.55, "fio": (118, 124, 126), "larg_fio": 0.45},
             "quina": 0.70, "sombra": (0.34, 2.2), "ciano": 10, "semente": 2830}


def agua_e(Q, h, w, semente):
    """A água da piscina (h x w x 3, BGR) no tom da referência: as pastilhas, o fundo e as cáusticas."""
    import fontes_procedurais as FP
    q = PISCINA_E
    rng = np.random.default_rng(semente)
    px = Q.px_m
    # as peças do Barlavento (o revestimento da legenda do cliente, 14,5 cm), com o contraste das pastilhas da referência
    T = FP.barlavento(h, w, cm_por_px=100.0 / px, peca_cm=q["peca_cm"], semente=semente).mean(axis=2)
    base = 1 + q["pastilha_var"] * (T - 1) / max(float(T.std()), 1e-6)
    lf = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), 0.9 * px)
    base *= 1 + q["fundo"] * lf / max(float(lf.std()), 1e-6)
    c = np.zeros((h, w), np.float32)
    for esc, f in q["causticas"]:
        n = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), esc * px * 0.3)
        n /= max(float(n.std()), 1e-6)
        c += f * np.exp(-(n / q["caustica_larg"]) ** 2)
    c = np.clip(cv2.GaussianBlur(c, (0, 0), 0.6), 0, 1)
    agua = np.float32(q["tom"]) * base[..., None]
    return agua * (1 - c[..., None]) + np.float32(q["claro"]) * c[..., None]


def piscina_e(Q, img):
    sys.path.insert(0, str(RAIZ / "_texturas"))
    from texturas import textura
    q = PISCINA_E
    X0, Y0, X1, Y1 = F.ret_q(Q, q["caixa_pt"])
    h0 = Y1 - Y0                                            # a água e o degrau: os desenhos na janela de antes
    Y1 = F.ret_q(Q, q["caixa_pt"][:3] + (q["fundo_pt"],))[3]
    w, h = X1 - X0, Y1 - Y0
    out = img.astype(np.float32)
    reg = out[Y0:Y1, X0:X1]
    # a água: os azuis da ARQ_CONTRAPISO, sem as bordas, o degrau e os vidros
    ss = 4
    m = np.zeros((h * ss, w * ss), np.uint8)
    for d in Q.desenhos:
        if d.get("layer") == "ARQ_CONTRAPISO" and d["type"] in ("f", "fs") and d.get("fill") and \
                np.allclose(d["fill"], q["agua_fill"], atol=0.02):
            for c in Q.caminhos(d):
                if len(c) >= 3:
                    cv2.fillPoly(m, [np.int32(np.round((c - (X0, Y0)) * ss))], 255)
    for r in q.get("agua_extra", []):                       # na mesma máscara (sem junta com a água do PDF)
        (x0, y0), (x1, y1) = Q.p2q(r[0], r[1]), Q.p2q(r[2], r[3])
        cv2.rectangle(m, (round((x0 - X0) * ss), round((y0 - Y0) * ss)),
                      (round((x1 - X0) * ss) - 1, round((y1 - Y0) * ss) - 1), 255, -1)
    agua = cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    par = paredes_pdf(Q)[Y0:Y1, X0:X1].astype(np.float32)
    folga = 0.8                                             # pt: o antialias dos dentes também passa (a parede cobre o de cima)
    par = par * (1 - _uniao(Q, [(a - folga, b - folga, c + folga, d + folga) for a, b, c, d in q["dentes"]], X0, Y0, w, h))
    # o contorno de baixo: o branco do PDF por cima da parede (a borda inteira, a parede só onde ela não passa)
    # (junto dele, a parede pela área do PDF, não pela máscara de >5 %: senão a linha da emenda com a coluna de cima e as
    # beiras do contorno ficavam em parte como parede)
    cont = _ret_pdf(Q, q["contorno"], X0, Y0, w, h)
    junto =cv2.dilate((cont > 0).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    par = np.clip(np.where(junto, Q._par[Y0:Y1, X0:X1], par) - cont, 0, 1)
    bege = np.maximum(np.clip(_uniao(Q, q["bege"], X0, Y0, w, h) - par, 0, 1), cont)
    degrau = np.clip(_uniao(Q, q["degrau"], X0, Y0, w, h) - par, 0, 1)
    vidro = _uniao(Q, q["vidros"], X0, Y0, w, h)
    agua = np.clip(agua - bege - degrau - vidro - par, 0, 1)
    # a sombra curta das bordas, do degrau e das paredes na água (a luz do alto à direita: mais forte junto à beira)
    beira = np.clip(bege + degrau + par, 0, 1)
    dist = cv2.distanceTransform((beira < 0.5).astype(np.uint8), cv2.DIST_L2, 5)
    fs, alc = q["sombra"]
    sombra = 1 - fs * np.exp(-dist / alc)
    A = np.pad(agua_e(Q, h0, w, q["semente"]), ((0, h - h0), (0, 0), (0, 0)), mode="edge") * sombra[..., None]
    # as bordas em Bege Bahia (a foto da biblioteca, no tom dos pisos de Bege Bahia)
    T = textura("bege_bahia", Q.px_m, h, w, semente=q["semente_bege"]).astype(np.float32)
    Bg = T / T.reshape(-1, 3).mean(axis=0) * np.float32(q["tom_bege"])
    # o degrau da sauna no travertino do piso dela (o tom da mediana do piso de travertino em volta)
    trav = legenda(Q, [(202, 217, 220)])[Y0:Y1, X0:X1]
    tom_t = np.median(reg[trav], axis=0) if trav.any() else np.float32(TRAVERTINO_E["tom"])
    Tt = np.pad(travertino_e(Q, h0, w, q["semente"] + 7), ((0, h - h0), (0, 0)), mode="edge")[..., None] * tom_t
    # a franja do render em volta do contorno de baixo (a parede antiga, preta e borrada, passava ~2 px dele): refeita
    # pelo fundo de fora antes da borda, como a sobra da parede antiga em `paredes_e`
    cm = cont > 0.02
    lum = reg.mean(axis=2)
    perto = cv2.dilate(cm.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool) & ~cm & (agua < 0.02) & \
        (bege < 0.02) & (degrau < 0.02) & (par < 0.02)
    claro = cv2.dilate(np.where(perto, lum, 0).astype(np.float32), np.ones((7, 7), np.uint8))
    franja = perto & (lum < q["franja"] * claro)
    fundo = cv2.inpaint(np.clip(reg, 0, 255).astype(np.uint8), (franja | cm).astype(np.uint8), 3, cv2.INPAINT_TELEA)
    sob = franja | cm                                       # na beira do contorno, o fundo de fora sob o antialias
    reg[sob] = fundo[sob].astype(np.float32)
    print(f"    piscina: o contorno de baixo em Bege Bahia ({cont.sum() / Q.px_m ** 2:.2f} m²), {int(franja.sum())} px da "
          f"franja da parede antiga refeitos")
    reg[:] = reg * (1 - agua[..., None]) + A * agua[..., None]
    reg[:] = reg * (1 - bege[..., None]) + Bg * bege[..., None]
    reg[:] = reg * (1 - degrau[..., None]) + Tt * degrau[..., None]
    # a quina das bordas e do degrau: um fio escuro na beira da água
    quina = np.clip(cv2.dilate(agua, np.ones((3, 3), np.uint8)) * np.clip(bege + degrau, 0, 1), 0, 1) * (agua < 0.5)
    reg *= (1 - (1 - q["quina"]) * quina)[..., None]
    # o vidro fino: o painel claro e os dois fios
    v = q["vidro"]
    vf = np.zeros((h * 8, w * 8), np.uint8)
    for r in q["vidros"]:
        (x0, y0), (x1, y1) = Q.p2q(r[0], r[1]), Q.p2q(r[2], r[3])
        for xx in (x0, x1):
            cv2.line(vf, (round((xx - X0) * 8), round((y0 - Y0) * 8)), (round((xx - X0) * 8), round((y1 - Y0) * 8)), 255,
                     max(1, round(v["larg_fio"] * 8)))
    fio = cv2.resize(vf, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    reg[:] = reg * (1 - v["alfa"] * vidro[..., None]) + np.float32(v["cor"]) * v["alfa"] * vidro[..., None]
    reg[:] = reg * (1 - fio[..., None]) + np.float32(v["fio"]) * fio[..., None]
    # o ciano da água antiga que sobrou nas beiradas (a borda da sauna, os cantos): refeito pelos vizinhos
    r8 = np.clip(reg, 0, 255).astype(np.uint8)
    b_, g_, r_ = [r8[..., i].astype(np.int16) for i in range(3)]
    ciano = (b_ - r_ > q["ciano"]) & (g_ - r_ > q["ciano"] - 5) & (agua < 0.5) & (vidro < 0.05)
    ciano &= cv2.dilate((agua > 0.5).astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool) | \
        cv2.dilate(((bege + degrau) > 0.5).astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    reg[:] = cv2.inpaint(r8, ciano.astype(np.uint8), 2, cv2.INPAINT_TELEA).astype(np.float32) * ciano[..., None] + \
        reg * ~ciano[..., None]
    print(f"    piscina: o ciano antigo nas beiradas, {int(ciano.sum())} px refeitos")
    print(f"    piscina: a água no turquesa da referência ({agua.sum() / Q.px_m ** 2:.1f} m², pastilhas e cáusticas); "
          f"as bordas em Bege Bahia ({bege.sum() / Q.px_m ** 2:.1f} m²) e o degrau da sauna em travertino "
          f"({degrau.sum() / Q.px_m ** 2:.2f} m²) com a quina e a sombra na água; os vidros finos")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# Os bancos da sauna em degraus (usuário, 28/10/26, com a referência: "OBSERVE QUE OS DEGRAUS EM FORMA DE BANCO NO
# MARMORE TRAVERTINO DENTRO DA SAUNA TEM DENTES APARENTES PARA DIZER QUAL DEGRAU ESTÁ ACIMA E OUTRO ABAIXO, DEIXANDO
# CLARO OS NÍVEIS"): os dois bancos do PDF (os brancos da ARQ_ELEMENTOS FIXOS: o de baixo, junto ao piso, e o de cima,
# encostado na parede) no travertino do piso, com o veio no comprido; o de cima um pouco mais claro (mais alto, mais
# luz). Os dentes: na beira de cada nível, a quina clara do degrau de cima, o fio escuro do espelho e a sombra curta
# no degrau (ou no piso) de baixo; nas pontas, junto ao degrau da piscina (no nível do piso), o mesmo, e a sombra dos
# dois bancos sobre ele (a luz do alto à direita).
SAUNA_E = {"bancos": [(888.9, 1021.3, 999.8, 1055.5), (888.9, 1055.5, 999.8, 1089.8)], "luz": (1.0, 1.075),
           "quina": 1.10, "fio": 0.50, "sombra": (0.38, 2.6), "ponta": {"desloc_px": (2.0, 4.0), "forca": 0.45, "sig": 0.9},
           "semente": 2834}


def sauna_e(Q, img):
    q = SAUNA_E
    (bx0, by0, bx1, by1), (cx0, cy0, cx1, cy1) = q["bancos"]
    X0, Y0, X1, Y1 = F.ret_q(Q, (bx0 - 20, by0 - 20, cx1 + 4, cy1 + 4))
    w, h = X1 - X0, Y1 - Y0
    out = img.astype(np.float32)
    reg = out[Y0:Y1, X0:X1]
    trav = legenda(Q, [(202, 217, 220)])[Y0:Y1, X0:X1]
    tom = np.median(reg[trav], axis=0) if trav.any() else np.float32(TRAVERTINO_E["tom"])
    niveis = [_ret_local(Q, r, X0, Y0, w, h) for r in q["bancos"]]
    for k, (a, f) in enumerate(zip(niveis, q["luz"])):
        T = travertino_e(Q, h, w, q["semente"] + k, vertical=False)[..., None] * tom * f
        reg[:] = reg * (1 - a[..., None]) + T * a[..., None]
    # os dentes: a beira de cada nível (a de cima de cada banco, de frente para o de baixo, e a ponta da esquerda)
    pt_px = Q.px_m / 56.69

    def fio_h(y_pt, x0_pt, x1_pt, larg=0.9):
        (u0, v), (u1, _) = Q.p2q(x0_pt, y_pt), Q.p2q(x1_pt, y_pt)
        m = np.zeros((h * 8, w * 8), np.uint8)
        cv2.line(m, (round((u0 - X0) * 8), round((v - Y0) * 8)), (round((u1 - X0) * 8), round((v - Y0) * 8)), 255,
                 max(1, round(larg * 8)))
        return cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255

    def fio_v(x_pt, y0_pt, y1_pt, larg=0.9):
        (u, v0), (_, v1) = Q.p2q(x_pt, y0_pt), Q.p2q(x_pt, y1_pt)
        m = np.zeros((h * 8, w * 8), np.uint8)
        cv2.line(m, (round((u - X0) * 8), round((v0 - Y0) * 8)), (round((u - X0) * 8), round((v1 - Y0) * 8)), 255,
                 max(1, round(larg * 8)))
        return cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    fs, alc = q["sombra"]
    (u0, _), (u1, _) = Q.p2q(bx0, by0), Q.p2q(bx1, by0)
    faixa = np.clip(np.minimum(xx - (u0 - X0) + 0.5, (u1 - X0) - xx + 0.5), 0, 1)       # só no comprido dos bancos
    # a sombra curta no nível de baixo, junto ao espelho do de cima: no piso diante do banco de baixo e no banco de
    # baixo diante do de cima
    for y_pt, baixo in ((by0, None), (cy0, niveis[0])):
        _, v = Q.p2q(bx0, y_pt)
        d = (v - Y0) - yy
        s = np.where(d > 0, fs * np.exp(-d / alc), 0) * faixa
        s *= (1 - np.clip(niveis[0] + niveis[1], 0, 1)) if baixo is None else baixo
        reg *= (1 - s)[..., None]
    # na ponta da esquerda, a sombra de cada banco sobre o degrau da piscina, para a esquerda e para baixo, mais longa no
    # banco mais alto: o perfil dos dentes
    p = q["ponta"]
    alto = np.clip(niveis[0] + niveis[1], 0, 1)
    sh = np.zeros((h, w), np.float32)
    for a, dpx in zip(niveis, p["desloc_px"]):
        sh = np.maximum(sh, cv2.warpAffine(a, np.float32([[1, 0, -dpx], [0, 1, dpx * 0.5]]), (w, h)))
    sh = cv2.GaussianBlur(sh, (0, 0), p["sig"]) * (1 - alto) * (xx < (u0 - X0))
    reg *= (1 - p["forca"] * sh)[..., None]
    # o fio escuro do espelho e a quina clara logo dentro do degrau de cima
    for y_pt in (by0, cy0):
        f = fio_h(y_pt, bx0, bx1)
        reg[:] = reg * (1 - f[..., None]) + reg * q["fio"] * f[..., None]
        fq = fio_h(y_pt + 1.0 / pt_px, bx0, bx1, 0.8)
        reg *= (1 + (q["quina"] - 1) * fq)[..., None]
    f = fio_v(bx0, by0, cy1)
    reg[:] = reg * (1 - f[..., None]) + reg * q["fio"] * f[..., None]
    fq = fio_v(bx0 + 1.0 / pt_px, by0, cy1, 0.8)
    reg *= (1 + (q["quina"] - 1) * fq)[..., None]
    print("    sauna: os dois bancos em degrau no travertino do piso (o de cima mais claro), com os dentes (a quina, o fio "
          "do espelho e a sombra curta no nível de baixo) e a sombra das pontas no degrau da piscina")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# Os aparelhos da academia (usuário, 28/10/26: "MELHORE A REPRESENTAÇÃO DOS APARELHOS DE ACADEMIA E O CONTORNO DO PISO EM
# VOLTA DESSES APARELHOS"). Até aqui ficavam os do render (borrados, serrilhados, um pouco fora do PDF, com restos da
# sombra antiga e lascas escuras no vinílico em volta). Agora são desenhados pelo PDF, na resolução da prancha: cada
# peça dos blocos (os preenchimentos brancos da ARQ_ MOB COMUM, na ordem do PDF, divididos pelos traços em células) num
# material pela forma e pelo aparelho (`_material_ap`): estrutura grafite, tubos, estofado preto, borracha, cromado, o
# alumínio das laterais da esteira, a lona dela e o painel; cada célula com o volume do material (o bisel com a luz do
# alto à direita, o cilindro, a almofada) e os traços do PDF por cima, finos; as bolas de pilates como esferas. Embaixo
# de cada aparelho, o vinílico novo inteiro (`pisos_e`: nas `zonas`, as peças antigas saem e o piso passa) e a sombra
# curta e macia do aparelho.
ACADEMIA_E = {
    "aparelhos": [("elíptico de cima", (863.6, 709.0, 949.6, 747.4), "eliptico"),
                  ("elíptico de baixo", (863.6, 760.5, 949.6, 799.0), "eliptico"),
                  ("esteira de cima", (859.1, 819.4, 954.9, 857.9), "esteira"),
                  ("esteira de baixo", (859.1, 884.6, 954.9, 923.2), "esteira"),
                  ("bolas e acessórios", (1019.0, 689.0, 1111.0, 741.0), "bolas"),
                  ("barra de parede", (1137.1, 693.5, 1222.1, 705.3), "barra"),
                  ("estação de musculação", (1178.7, 779.0, 1283.2, 895.9), "estacao"),
                  ("barra de alongamento junto ao DCE", (1449.3, 845.4, 1503.1, 850.5), "alongamento"),
                  ("suporte de halteres", (1691.3, 845.1, 1720.9, 935.8), "halteres"),
                  ("supino com barra", (1400.2, 981.1, 1497.7, 1057.6), "supino"),
                  ("banco regulável", (1546.2, 973.9, 1575.4, 1057.7), "banco")],
    "bolas": [(1045.5, 714.9, 19.4), (1083.9, 714.9, 19.4)],                       # centro e raio (pt)
    # a barra de alongamento junto ao DCE (revisão de 28/10, item 2; usuário: "NÃO É TV É UMA BARRA COM BARRAS AO MEIO
    # PARA ALONGAMENTO"): ia só a barra do meio, escura, e parecia uma TV solta no vinílico. Agora, a moldura do PDF (a
    # ARQ_MARCENARIA em volta, presa na parede) em madeira, e as barras do meio (a ARQ_ MOB COMUM) cromadas, cada uma
    # como um tubo
    "moldura": {"alongamento": ("ARQ_MARCENARIA", (1440.8, 838.1, 1508.8, 855.1), "madeira")},
    "zona_m": 0.45, "ss": 6, "folga_pt": 1.0,
    "materiais": {                                            # BGR, o volume e o brilho
        "estrutura": ((72, 74, 78), "bisel", 0.0), "tubo": ((80, 82, 86), "cilindro", 0.25),
        "estofado": ((42, 42, 45), "almofada", 0.0), "borracha": ((36, 36, 38), "bisel", 0.0),
        "cromo": ((178, 180, 184), "cilindro", 0.55), "aluminio": ((156, 158, 162), "bisel", 0.0),
        "lona": ((38, 38, 40), "lona", 0.0), "painel": ((54, 56, 60), "bisel", 0.0), "tela": ((92, 74, 54), "plano", 0.0),
        "botao": ((150, 152, 155), "plano", 0.0), "bola": ((198, 200, 202), "esfera", 0.0),
        "madeira": ((104, 152, 196), "bisel", 0.0)},
    "traco": {"cor": (26, 26, 28), "alfa": 0.55, "larg_px": 0.35, "alfa_bola": 0.18},
    "bisel": (0.40, 0.9), "sombra": [(2.2, 1.6, 0.40), (3.5, 4.0, 0.14)]}       # (desloc px, sigma px, força)


def _material_ap(tipo, c, maior):
    """O material da célula c (área, espessura e comprimento em m, centro relativo à caixa) no aparelho `tipo`."""
    a, e, L, cx = c["area"], c["esp"], c["comp"], c["cx"]
    if tipo == "esteira":
        if maior:
            return "lona"
        if e < 0.1 and L > 0.55:
            return "aluminio"
        if cx < 0.3 and a < 0.0012:
            return "botao"
        if cx < 0.3 and a < 0.03:
            return "tela" if 0.01 < a < 0.03 and c["quadrado"] else "painel"
        return "estrutura"
    if tipo == "eliptico":
        return "tubo" if e < 0.045 and L > 0.15 else "estrutura"
    if tipo == "estacao":
        if a > 0.035 and e > 0.1:
            return "estofado"
        return "tubo" if e < 0.04 and L > 0.12 else "estrutura"
    if tipo == "supino":
        if L > 1.0 and e < 0.04:
            return "cromo"
        if cx < 0.13 or cx > 0.87:
            return "borracha"
        return "estofado" if a > 0.05 else "estrutura"
    if tipo == "banco":
        return "estofado" if a > 0.012 else "estrutura"
    if tipo == "halteres":
        if e > 0.06 and c["quadrado"]:
            return "borracha"
        return "cromo" if e < 0.035 and L < 0.35 else "estrutura"
    if tipo == "barra":
        return "cromo" if e < 0.03 else "estrutura"
    if tipo == "alongamento":                              # as barras do meio (a moldura vai pela camada dela)
        return "cromo"
    if tipo == "bolas":
        return "borracha" if a > 0.003 else "estrutura"
    return "estrutura"


def _sombreado(modo, cel, d, brilho, q, ss_px_m, bola=None):
    """O fator de luz da célula (d: a distância à borda, px do desenho grande)."""
    luz = np.float32([1.0, -1.0]) / np.sqrt(2)
    if modo == "esfera":
        cx, cy, R, yy, xx = bola
        dx, dy = (xx - cx) / R, (yy - cy) / R
        z = np.sqrt(np.clip(1 - dx ** 2 - dy ** 2, 0, 1))
        L3 = np.float32([0.45, -0.45, 0.77]) / np.linalg.norm([0.45, -0.45, 0.77])
        lam = np.clip(dx * L3[0] + dy * L3[1] + z * L3[2], 0, 1)
        return 0.42 + 0.66 * lam + 0.22 * lam ** 30
    if modo == "plano":
        return np.ones_like(d)
    dmax = max(float(d.max()), 1.0)
    if modo == "cilindro":
        r = np.clip(d / dmax, 0, 1)
        return 0.66 + 0.40 * np.sqrt(r * (2 - r)) + brilho * np.exp(-((r - 0.8) / 0.18) ** 2)
    if modo == "almofada":
        r = np.clip(d / (0.05 * ss_px_m), 0, 1)
        s = 0.80 + 0.30 * r * r * (3 - 2 * r)
        hl = cv2.GaussianBlur(cv2.warpAffine(cel.astype(np.float32), np.float32([[1, 0, 0.03 * ss_px_m], [0, 1, -0.03 * ss_px_m]]),
                                             cel.shape[::-1]), (0, 0), 0.04 * ss_px_m)
        return s + 0.10 * hl
    # bisel (e a lona): a beira que olha para a luz mais clara, a outra mais escura
    f, larg = q["bisel"]
    mb = cv2.GaussianBlur(cel.astype(np.float32), (0, 0), max(larg * ss_px_m / 59.7 * 6, 1.0))
    gy, gx = np.gradient(mb)
    nn = np.sqrt(gx ** 2 + gy ** 2) + 1e-6
    face = -(gx * luz[0] + gy * luz[1]) / nn
    e = np.exp(-d / max(0.012 * ss_px_m, 1.0))
    s = 1 + f * face * e
    if modo == "lona":
        yy = np.arange(cel.shape[0], dtype=np.float32)[:, None]
        xx = np.arange(cel.shape[1], dtype=np.float32)[None, :]
        s = s * (1 + 0.05 * np.sin(2 * np.pi * (xx + 0 * yy) / (0.02 * ss_px_m)))
    return s


def aparelhos_e(Q, img):
    q = ACADEMIA_E
    S = q["ss"]
    out = img.astype(np.float32)
    mats = q["materiais"]
    tr = q["traco"]
    n_cel = 0
    for nome, caixa, tipo in q["aparelhos"]:
        x0p, y0p, x1p, y1p = caixa
        fo = q["folga_pt"]
        pegar = [("ARQ_ MOB COMUM", caixa)]
        mold = q["moldura"].get(tipo)                    # a moldura de outra camada em volta (a barra de alongamento)
        if mold:
            pegar.append(mold[:2])
        ds = sorted([d for camada, (a, b, c, e) in pegar for d in Q.desenhos if d.get("layer") == camada and
                     d["rect"].x0 >= a - fo and d["rect"].x1 <= c + fo and d["rect"].y0 >= b - fo and
                     d["rect"].y1 <= e + fo], key=lambda d: d.get("seqno", 0))
        jx0, jy0 = min(r[1][0] for r in pegar), min(r[1][1] for r in pegar)
        jx1, jy1 = max(r[1][2] for r in pegar), max(r[1][3] for r in pegar)
        X0, Y0, X1, Y1 = F.ret_q(Q, (jx0 - 8, jy0 - 8, jx1 + 8, jy1 + 8))
        w, h = X1 - X0, Y1 - Y0
        W_, H_ = w * S, h * S
        lab = np.zeros((H_, W_), np.int32)
        lin = np.zeros((H_, W_), np.uint8)
        lb = np.zeros((H_, W_), np.uint8)                                    # os traços dentro das bolas
        k = 0
        da_moldura = [False]                                                 # por peça: se é da camada da moldura
        for d in ds:
            cs = [np.int32(np.round((c - (X0, Y0)) * S)) for c in Q.caminhos(d)]
            if d["type"] in ("f", "fs"):
                k += 1
                m = np.zeros((H_, W_), np.uint8)
                cv2.fillPoly(m, [c for c in cs if len(c) >= 3], 1)
                lab[m > 0] = k
                da_moldura.append(bool(mold) and d.get("layer") == mold[0])
            if d["type"] in ("s", "fs"):
                for c in cs:
                    cv2.polylines(lin, [c], False, 255, max(1, round(tr["larg_px"] * S)), cv2.LINE_AA)
        sil = lab > 0
        yy, xx = np.mgrid[0:H_, 0:W_].astype(np.float32)
        bolas = []
        if tipo == "bolas":
            for bx, by, r in q["bolas"]:
                (u, v), (u2, _) = Q.p2q(bx, by), Q.p2q(bx + r, by)
                cx, cy, R = (u - X0) * S, (v - Y0) * S, (u2 - u) * S
                bolas.append((cx, cy, R))
            dentro_b = np.zeros((H_, W_), bool)
            for cx, cy, R in bolas:
                dentro_b |= (xx - cx) ** 2 + (yy - cy) ** 2 <= (R - 0.5 * S) ** 2
            lb = np.where(dentro_b, lin, 0).astype(np.uint8)
            lin = np.where(dentro_b, 0, lin).astype(np.uint8)
        cor = np.zeros((H_, W_, 3), np.float32)
        ss_px_m = Q.px_m * S
        # as células: cada peça dividida pelos traços
        livre = sil & (lin < 128)
        n, cel_lab, st, cen = cv2.connectedComponentsWithStats(livre.astype(np.uint8), 4)
        areas = st[:, cv2.CC_STAT_AREA].astype(np.float64) / ss_px_m ** 2
        maior = int(np.argmax(areas[1:]) + 1) if n > 1 else 0
        for i in range(1, n):
            bx, by, bw, bh = st[i, :4]
            sub = cel_lab[by:by + bh, bx:bx + bw] == i
            d = cv2.distanceTransform(np.pad(sub, 1).astype(np.uint8), cv2.DIST_L2, 5)[1:-1, 1:-1]
            esp = 2 * float(d.max()) / ss_px_m
            c = {"area": areas[i], "esp": esp, "comp": areas[i] / max(esp, 1e-4),
                 "cx": (cen[i][0] / S + X0 - Q.p2q(x0p, y0p)[0]) / max(Q.p2q(x1p, y0p)[0] - Q.p2q(x0p, y0p)[0], 1),
                 "quadrado": 0.6 < bw / max(bh, 1) < 1.6}
            if tipo == "bolas" and bolas:
                ccx, ccy = cen[i]
                bola = next(((bcx, bcy, R) for bcx, bcy, R in bolas if (ccx - bcx) ** 2 + (ccy - bcy) ** 2 <= R ** 2), None)
            else:
                bola = None
            if bola is not None:
                continue                                                     # as bolas vão inteiras, depois
            pecas_cel = lab[by:by + bh, bx:bx + bw][sub]
            if mold and da_moldura[int(np.bincount(pecas_cel).argmax())]:
                mat = mold[2]
            else:
                mat = _material_ap(tipo, c, i == maior and tipo == "esteira")
            base, modo, brilho = mats[mat]
            sh = _sombreado(modo, sub, d, brilho, q, ss_px_m) if min(bw, bh) >= 3 else np.ones(sub.shape, np.float32)
            reg = cor[by:by + bh, bx:bx + bw]
            reg[sub] = (np.float32(base) * sh[..., None])[sub]
            n_cel += 1
        # as bolas: a esfera inteira, com os traços do PDF bem leves por cima
        for cx, cy, R in bolas:
            disco = (xx - cx) ** 2 + (yy - cy) ** 2 <= R ** 2
            base, modo, _ = mats["bola"]
            s = _sombreado("esfera", disco, None, 0, q, ss_px_m, bola=(cx, cy, R, yy, xx))
            cor[disco] = (np.float32(base) * s[..., None])[disco]
            sil |= disco
        # os traços do PDF por cima (nas bolas, bem leves)
        al = (lin.astype(np.float32) / 255) * tr["alfa"] + (lb.astype(np.float32) / 255) * tr["alfa_bola"]
        cor = cor * (1 - al[..., None]) + np.float32(tr["cor"]) * al[..., None]
        a = sil.astype(np.float32)
        # o tamanho da prancha
        A = cv2.resize(a, (w, h), interpolation=cv2.INTER_AREA)
        C = cv2.resize(cor * a[..., None], (w, h), interpolation=cv2.INTER_AREA) / np.maximum(A, 1e-4)[..., None]
        reg = out[Y0:Y1, X0:X1]
        for dpx, sig, f in q["sombra"]:
            s = cv2.GaussianBlur(cv2.warpAffine(A, np.float32([[1, 0, -dpx], [0, 1, dpx]]), (w, h)), (0, 0), sig)
            reg *= (1 - f * s * (1 - A))[..., None]
        reg[:] = reg * (1 - A[..., None]) + C * A[..., None]
    print(f"    academia: {len(q['aparelhos'])} aparelhos desenhados pelo PDF ({n_cel} peças nos materiais, as bolas como "
          f"esferas), com a sombra curta no vinílico novo")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# As portas (usuário, 28/10/26: "VAMOS REVISAR E AJUSTAR REPRESENTAÇÃO DAS PORTAS"). As portas de giro vinham do render:
# tubos cinza arredondados de 8 a 10 px no lugar da folha, sem batentes; a do DCE com um "L" que não existe (uma segunda
# barra rente à soleira); a da sauna quase sumida; as das cabines do vestiário fundidas numa barra só sobre a divisória,
# que também não aparecia (a ARQ - Parede do PDF, fora das paredes de E10). Agora, como as portas aprovadas na Casa D
# (R3, seção 4 das regras): sem arco, a folha na posição e na espessura do PDF, em branco suave com o contorno fino e a
# sombra curta, e os batentes do PDF em branco com o contorno; em volta de cada porta (o quadrante do arco do PDF, do
# lado do cômodo), o piso novo passa inteiro antes (`zonas_portas` nos pisos), sem nada da folha antiga. A porta de
# vidro da ducha do ambiente e o vidro fixo dela como os boxes (o vidro claro com as faces finas e a sombra curta).
PORTAS_E = {
    "giro": [("DCE", (1444.0, 693.5, 1446.3, 738.8), (1444.0, 693.5, 1489.4, 738.8), "granito",
              [(1440.0, 693.5, 1444.0, 694.6), (1489.4, 693.5, 1493.3, 694.6), (1442.6, 685.0, 1444.6, 693.5),
               (1488.8, 685.0, 1490.8, 693.5)]),
             ("WC DCE 2", (1646.7, 697.7, 1692.0, 700.0), (1646.7, 697.7, 1692.0, 743.1), "Bege Bahia",
              [(1646.7, 743.1, 1647.8, 747.1), (1646.7, 693.8, 1647.8, 697.7), (1638.2, 742.5, 1646.7, 744.5),
               (1638.2, 696.3, 1646.7, 698.3)]),
             ("casa de máquinas da direita", (1738.8, 693.5, 1741.1, 738.8), (1738.8, 693.5, 1784.2, 738.8), "Bege Bahia",
              [(1734.8, 693.5, 1738.8, 694.6), (1784.2, 693.5, 1788.1, 694.6), (1737.4, 685.0, 1739.4, 693.5),
               (1783.6, 685.0, 1785.6, 693.5)]),
             ("depósito, folha de cima", (1564.5, 564.7, 1602.6, 567.0), (1564.5, 564.7, 1602.6, 602.8), "Bege Bahia",
              [(1564.5, 561.0, 1565.6, 563.8), (1558.0, 563.1, 1564.5, 565.4)]),
             ("depósito, folha de baixo", (1564.5, 638.6, 1602.6, 640.9), (1564.5, 602.8, 1602.6, 640.9), "Bege Bahia",
              [(1564.5, 641.7, 1565.6, 644.6), (1558.0, 640.2, 1564.5, 642.5)]),
             ("casa de máquinas de baixo", (1352.4, 1107.4, 1354.7, 1152.7), (1309.4, 1107.4, 1354.7, 1152.7), "granito",
              [(1305.4, 1107.4, 1309.4, 1108.5), (1354.7, 1107.4, 1358.7, 1108.5), (1307.9, 1090.3, 1309.9, 1107.4),
               (1354.1, 1090.3, 1356.1, 1107.4)]),
             ("sauna", (1008.9, 961.4, 1048.6, 963.6), (1008.9, 961.4, 1048.6, 1001.1), "travertino",
              [(1008.9, 1001.1, 1010.0, 1005.0), (1008.9, 957.4, 1010.0, 961.4), (1000.4, 1000.5, 1008.9, 1002.5),
               (1000.4, 960.0, 1008.9, 961.9)]),
             ("vestiário", (1147.8, 964.2, 1193.1, 966.5), (1147.8, 964.2, 1193.1, 1009.6), "travertino",
              [(1147.8, 1009.6, 1148.9, 1013.5), (1147.8, 960.2, 1148.9, 964.2), (1139.3, 1009.0, 1147.8, 1011.0),
               (1139.3, 962.8, 1147.8, 964.8)]),
             ("cabine do vaso", (1212.6, 1027.1, 1214.9, 1065.9), (1176.1, 1027.1, 1214.9, 1065.9), "travertino",
              [(1175.6, 1023.7, 1176.8, 1027.1), (1214.2, 1023.7, 1215.3, 1027.1)])],
    # a porta da cabine do chuveiro do vestiário (usuário, 28/10/26: "represente melhor a porta desse ambiente de
    # chuveiro"; "pode fazer aberta mesmo"; "no mesmo padrão que adotamos para as demais"): aberta contra a divisória,
    # como no PDF, no padrão das portas de vidro do Subsolo (a da ducha do ambiente): o vidro fino com as faces e a
    # sombra curta, os batentes brancos na soleira, sem arco. A folha branca colava no traço escuro da divisória e não
    # se lia como porta; o vidro fica na metade de fora da folha do PDF, com o piso entre ele e a divisória
    "vidros": [("ducha do ambiente: a porta", (1026.9, 1022.3, 1028.1, 1061.1), (1026.9, 1022.3, 1065.7, 1061.1), "travertino"),
               ("ducha do ambiente: o vidro fixo", (1009.5, 1021.7, 1026.9, 1022.3), (1009.5, 1019.5, 1026.9, 1024.5),
                "travertino"),
               ("cabine do chuveiro: a porta de vidro, aberta", (1219.5, 1027.1, 1220.9, 1065.9),
                (1218.6, 1027.1, 1257.4, 1065.9), "travertino",
                {"batentes": [(1218.1, 1023.7, 1219.3, 1027.1), (1256.7, 1023.7, 1257.8, 1027.1)]})],
    # as soleiras de Bege Bahia (R13: o vão branco do PDF na espessura da parede, nítido, com as faces finas)
    "soleiras": [(1444.6, 685.0, 1488.8, 693.5), (1638.2, 698.3, 1646.7, 742.5), (1739.4, 685.0, 1783.6, 693.5),
                 (1556.0, 563.1, 1564.5, 642.5), (1309.9, 1090.3, 1354.1, 1107.4), (1176.8, 1023.7, 1214.2, 1027.1),
                 (1219.3, 1023.7, 1256.7, 1027.1)],
    # as portas de vidro de correr da circulação para a academia e a janela de correr do DCE, como as da academia da
    # Casa D (`final3840_casaa.portas_vidro`): a soleira de Bege Bahia no vão, as duas folhas nos planos do PDF (o
    # caixilho de alumínio com o vidro no meio e os montantes) e os batentes
    "correr": [{"nome": "da circulação para a academia, à esquerda", "soleira": (847.3, 685.0, 972.0, 693.5),
                "batentes": [(847.3, 685.0, 849.6, 693.5), (969.8, 685.0, 972.0, 693.5)],
                "folhas": [((849.6, 685.0, 911.9, 687.8), "x"), ((907.4, 687.8, 969.8, 690.7), "x")], "montante_pt": 4.5},
               {"nome": "da circulação para a academia, à direita", "soleira": (1306.5, 685.0, 1431.3, 693.5),
                "batentes": [(1306.5, 685.0, 1308.8, 693.5), (1429.0, 685.0, 1431.3, 693.5)],
                "folhas": [((1308.8, 687.8, 1371.2, 690.7), "x"), ((1366.6, 685.0, 1429.0, 687.8), "x")],
                "montante_pt": 4.5},
               {"nome": "janela do DCE", "soleira": (1493.1, 685.0, 1555.5, 693.5),
                "batentes": [(1493.1, 685.0, 1496.0, 690.7), (1552.6, 685.0, 1555.5, 690.7)],
                "folhas": [((1496.0, 687.8, 1525.7, 690.7), "x"), ((1522.9, 685.0, 1552.6, 687.8), "x")],
                "montante_pt": 2.8}],
    # o piso refeito junto às esquadrias onde o render deixou a peça antiga do lado de dentro (a barra cinza da janela de
    # correr do DCE, embaixo dela, no granito)
    # e o vinílico diante da porta do elevador (revisão de 28/10, item 3): a faixa de 3,6 pt sob a face da parede fica fora
    # da legenda do vinílico (a linha do contrapiso do PDF), e o toco e a mancha escura do render ficavam nela
    "limpar": [("granito", (1493.1, 693.5, 1555.5, 699.5)), ("vinílico", (1750.0, 1006.1, 1810.0, 1017.0))],
    "folha": (238, 238, 236), "contorno": (88, 90, 92), "larg_contorno": 0.5, "sombra": (0.26, 1.0, 0.9),
    "vidro": (218, 214, 204), "vidro_face": (104, 108, 112), "vidro_px": 1.4, "vidro_face_px": 0.45,
    "zona_pt": 5.7}


def zonas_portas(Q):
    """As zonas das portas por piso ({nome do piso: bool}): o quadrante do arco do PDF com `zona_pt` de folga, só do lado
    do cômodo (a parede e a soleira ficam)."""
    q = PORTAS_E
    z = {}
    for item in q["giro"] + q["vidros"]:
        _, f, arco, piso = item[:4]
        x0, y0, x1, y1 = arco
        e = q["zona_pt"]
        zx0, zy0, zx1, zy1 = x0 - e, y0 - e, x1 + e, y1 + e
        if (f[2] - f[0]) < (f[3] - f[1]):                       # a folha em pé: a parede em cima ou embaixo
            if abs(f[1] - y0) < 0.5:
                zy0 = y0 + 0.3
            else:
                zy1 = y1 - 0.3
        elif abs(f[0] - x0) < 0.5 and (f[3] - f[1]) > 1.5:      # deitada: a parede à esquerda ou à direita
            zx0 = x0 + 0.3
        elif (f[3] - f[1]) > 1.5:
            zx1 = x1 - 0.3
        a, b, c, d = F.ret_q(Q, (zx0, zy0, zx1, zy1))
        m = z.setdefault(piso, np.zeros((Q.H, Q.W), bool))
        m[b:d, a:c] = True
    for piso, r in q["limpar"]:
        a, b, c, d = F.ret_q(Q, r)
        z.setdefault(piso, np.zeros((Q.H, Q.W), bool))[b:d, a:c] = True
    return z


def portas_e(Q, img):
    import final3840_casaa as FA
    q = PORTAS_E
    out = np.ascontiguousarray(img.copy())
    for r in q["soleiras"]:
        out = FA.soleira_bege(Q, out, r)
    guarda = FA.PORTAS_VIDRO
    FA.PORTAS_VIDRO = dict(FA.PORTAS_VIDRO, portas=q["correr"])
    try:
        out = FA.portas_vidro(Q, out)
    finally:
        FA.PORTAS_VIDRO = guarda
    fs, dist, sig = q["sombra"]
    for nome, folha, _, _, batentes in q["giro"]:
        caixa = (min(r[0] for r in [folha] + batentes), min(r[1] for r in [folha] + batentes),
                 max(r[2] for r in [folha] + batentes), max(r[3] for r in [folha] + batentes))
        tl = FA.tela(out, Q, caixa, folga=5)
        m = tl.ret(folha)
        FA.sombra_q(tl, m, forca=fs, dist=dist, sigma=sig)
        tl.pintar(m, q["folha"])
        tl.contorno(m, q["larg_contorno"], q["contorno"])
        for b in batentes:
            mb = tl.ret(b)
            tl.pintar(mb, q["folha"])
            tl.contorno(mb, q["larg_contorno"] * 0.8, q["contorno"])
        out = tl.gravar()
    for item in q["vidros"]:
        vidro, extra = item[1], (item[4] if len(item) > 4 else {})
        caixa = vidro
        for r in extra.get("batentes", []):
            caixa = (min(caixa[0], r[0]), min(caixa[1], r[1]), max(caixa[2], r[2]), max(caixa[3], r[3]))
        tl = FA.tela(out, Q, caixa, folga=5)
        x0, y0, x1, y1 = vidro
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        meia = q["vidro_px"] / 2 / FA.PT_PX
        r = (x0, cy - meia, x1, cy + meia) if (x1 - x0) >= (y1 - y0) else (cx - meia, y0, cx + meia, y1)
        m = tl.ret(r)
        FA.sombra_q(tl, m, forca=0.20, dist=0.9, sigma=0.8)
        tl.pintar(m, q["vidro"])
        tl.contorno(m, q["vidro_face_px"], q["vidro_face"])
        for b in extra.get("batentes", []):
            mb = tl.ret(b)
            tl.pintar(mb, q["folha"])
            tl.contorno(mb, q["larg_contorno"] * 0.8, q["contorno"])
        out = tl.gravar()
    print(f"    portas: {len(q['giro'])} folhas de giro na posição e na espessura do PDF (branco suave, contorno fino, "
          f"sombra curta), com os batentes, sem arco; {len(q['soleiras'])} soleiras de Bege Bahia; a porta e o vidro fixo "
          f"da ducha do ambiente e a porta da cabine do chuveiro do vestiário (aberta, como no PDF, com os batentes) em "
          f"vidro fino")
    return out


def zonas_academia(Q):
    """As zonas dos aparelhos, das louças do vestiário e do chuveiro da ducha do ambiente (bool): a caixa de cada um com
    folga, onde o piso novo passa por inteiro (as peças antigas saem; as novas são desenhadas depois)."""
    m = np.zeros((Q.H, Q.W), np.uint8)
    caixas = [(c, ACADEMIA_E["zona_m"]) for _, c, _ in ACADEMIA_E["aparelhos"]] + \
        [(c, VESTIARIO_E["zona_m"]) for c in (VESTIARIO_E["vaso"][0], VESTIARIO_E["chuveiro"]["ducha"],
                                              VESTIARIO_E["chuveiro"]["braco"])]
    caixas.append((DUCHA_AMBIENTE_E["zona"], 0.0))
    for (x0, y0, x1, y1), z in caixas:
        fo = z * 56.69
        a, b, c, d = F.ret_q(Q, (x0 - fo, y0 - fo, x1 + fo, y1 + fo))
        m[b:d, a:c] = 1
    return m.astype(bool)


# O vestiário (usuário, 28/10/26: "VESTIARIO: PISO EM MARMORE TRAVERTINO BRUTO, CUBA ESCULPIDA EM MARMORE TRAVERTINO
# BRUTO, PEDRA DA PIA EM MAGRANITO MARROM TABACO ESCOVADO, VASO SANITÁRIO EM BRANCO E METAIS CROMADOS"): o piso já vem
# no travertino bruto (`TRAVERTINO_E`); a bancada do PDF (ARQ_BANCADAS) no granito Marrom Tabaco escovado: o desenho do
# granito de referência das Casas B a D, calmo (os grãos suavizados, o contraste baixo: o escovado é fosco), no tom do
# Marrom Tabaco escolhido em 15/10 (RGB ~90, 66, 50), com o risco fino do escovado no comprido da bancada, a borda no
# tom escurecido e a sombra curta (E9); a cuba esculpida (`F.cuba_esculpida`) no travertino bruto do piso, um pouco
# mais clara e mais calma; a torneira cromada saindo da parede sobre a bacia; o vaso do PDF em louça branca; o chuveiro
# de teto, o braço e a canopla cromados (`final3840_casaa.chuveiro`).
VESTIARIO_E = {"bancada": (1262.8, 954.3, 1289.5, 1023.7), "cuba": (1266.1, 971.3, 1289.5, 1006.2),
               "torneira": {"bico": (1280.2, 987.9, 1287.4, 989.5), "base": (1287.9, 988.7, 1.3)},
               "vaso": ((1147.8, 1056.8, 1176.9, 1076.8), "esquerda"),
               "chuveiro": {"ducha": (1262.1, 1053.2, 1273.3, 1064.4), "braco": (1266.6, 1058.1, 1288.9, 1059.5),
                            "canopla": (1288.4, 1056.9, 1289.5, 1060.7)},
               "tabaco": {"tom": (50, 64, 88), "contraste": 0.75, "liso_px": 0.5, "escovado": 0.025, "borda": 0.72,
                          "larg_px": 0.8, "sombra": 0.30, "semente": 2840},
               "cuba_tom": (208, 225, 236), "zona_m": 0.10}


# O chuveiro da ducha do ambiente, ao lado da sauna (usuário, 28/10/26: "MELHORE A REPRESENTAÇÃO DO CHUVEIRO, AO LADO
# DA SAUNA"): até aqui ficava o do render (um cálice cinza fora do desenho e uma grelha escura junto à parede). Agora é
# o do PDF (ARQ_LOUÇAS E METAIS), como o do vestiário (`final3840_casaa.chuveiro`): a placa quadrada cromada do
# chuveiro de teto (11 pt, com os furinhos e a luz do alto à direita), o braço cromado descendo até a parede de baixo e
# a canopla nela; embaixo, o travertino do piso inteiro (`zona`, nas zonas de `pisos_e`). O nicho na parede atrás do
# chuveiro (o branco da ARQ_PAREDE na espessura dela, que o render pintou como uma grelha escura) no travertino do piso,
# um pouco mais escuro (`nicho_luz`, recuado), com a sombra curta do fundo e da lateral esquerda.
DUCHA_AMBIENTE_E = {"ducha": (1031.0, 1062.9, 1042.1, 1074.1), "braco": (1035.8, 1067.4, 1037.3, 1089.4),
                    "canopla": (1034.6, 1088.9, 1038.5, 1090.3), "zona": (1024.0, 1058.0, 1048.0, 1090.3),
                    "nicho": (1025.8, 1090.3, 1048.5, 1096.0), "nicho_luz": 0.90, "nicho_sombra": (0.30, 1.3),
                    "semente": 2836}


# O nicho da cabine do chuveiro do vestiário (usuário, 28/10/26, com o OK: "pode corrigir o nicho da cabine da casa
# E"): na parede da direita da cabine, onde o braço do chuveiro chega, o PDF desenha o nicho (o branco da ARQ_PAREDE na
# espessura da parede, com o da ARQ_REVESTIMENTOS na face), que o render pintou como um retângulo de moldura escura.
# Como o da ducha do ambiente: o travertino do piso um pouco mais escuro, com a sombra curta do fundo (à direita) e da
# lateral de cima; o chuveiro da cabine (placa, braço e canopla) vem por cima.
NICHO_CABINE_E = {"nicho": (1289.0, 1048.0, 1295.2, 1070.7), "fundo": "direita", "nicho_luz": 0.90,
                  "nicho_sombra": (0.30, 1.3), "semente": 2841}


def nicho_ducha(Q, img, q=None):
    """O nicho em travertino (`q["nicho"]`, pt), com a sombra curta do fundo e de uma lateral: `fundo` "baixo" (o da
    ducha do ambiente, na parede de baixo: o fundo embaixo e a lateral esquerda) ou "direita" (o da cabine do
    vestiário, na parede da direita: o fundo à direita e a lateral de cima)."""
    q = DUCHA_AMBIENTE_E if q is None else q
    r = q["nicho"]
    direita = q.get("fundo", "baixo") == "direita"
    X0, Y0, X1, Y1 = F.ret_q(Q, (r[0] - 40, r[1] - 40, r[2] + 4, r[3] + 40) if direita else
                             (r[0] - 40, r[1] - 40, r[2] + 40, r[3] + 4))
    w, h = X1 - X0, Y1 - Y0
    out = img.astype(np.float32)
    reg = out[Y0:Y1, X0:X1]
    trav = legenda(Q, [(202, 217, 220)])[Y0:Y1, X0:X1]
    tom = np.median(reg[trav], axis=0) if trav.any() else np.float32(TRAVERTINO_E["tom"])
    a = _ret_local(Q, r, X0, Y0, w, h)
    T = travertino_e(Q, h, w, q["semente"])[..., None] * tom * q["nicho_luz"]
    reg[:] = reg * (1 - a[..., None]) + T * a[..., None]
    # a sombra curta do fundo e da lateral, dentro do nicho
    (u0, v0), (u1, v1) = Q.p2q(r[0], r[1]), Q.p2q(r[2], r[3])
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    if direita:
        d = np.minimum((u1 - X0) - xx, yy - (v0 - Y0))
    else:
        d = np.minimum((v1 - Y0) - yy, xx - (u0 - X0))
    fs, alc = q["nicho_sombra"]
    reg *= (1 - fs * np.exp(-np.maximum(d, 0) / alc) * a)[..., None]
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def vestiario_e(Q, img):
    import final3840_casaa as FA
    import fontes_procedurais as FP
    q = VESTIARIO_E
    t = q["tabaco"]

    def tabaco(tl):
        G = FP.granito_referencia(tl.h, tl.w, Q.px_m, semente=t["semente"]).astype(np.float32)
        G = cv2.GaussianBlur(G, (0, 0), t["liso_px"])
        D = G.mean(axis=2) / max(float(G.mean()), 1.0)
        D = 1 + t["contraste"] * (D - 1)
        rng = np.random.default_rng(t["semente"])
        em_pe = (q["bancada"][3] - q["bancada"][1]) > (q["bancada"][2] - q["bancada"][0])
        esc = cv2.GaussianBlur(rng.normal(0, 1, (tl.h, tl.w)).astype(np.float32), (0, 0),
                               sigmaX=0.4 if em_pe else 6.0, sigmaY=6.0 if em_pe else 0.4)
        D *= 1 + t["escovado"] * esc / max(float(esc.std()), 1e-6)
        return np.float32(t["tom"]) * D[..., None]
    out = FA.bancada_pedra(Q, np.ascontiguousarray(img.copy()), q["bancada"], tabaco, t["borda"], t["larg_px"], t["sombra"])
    # a cuba esculpida no travertino bruto do piso (o desenho em estratos, calmo, no comprido da cuba)
    guarda = (FA.travertino_bruto, F.BANCADAS_F["cuba_travertino"])
    try:
        FA.travertino_bruto = lambda Q_, h, w, semente, **kw: travertino_e(Q_, h, w, semente, vertical=True, amp=0.8,
                                                                            finas=0.4)
        F.BANCADAS_F["cuba_travertino"] = dict(guarda[1], tom=q["cuba_tom"])
        out = F.cuba_esculpida(Q, out, q["cuba"], "travertino")
    finally:
        FA.travertino_bruto, F.BANCADAS_F["cuba_travertino"] = guarda
    out = FA.torneira(Q, out, q["torneira"]["bico"], q["torneira"]["base"])
    out = FA.vaso(Q, out, *q["vaso"])
    out = nicho_ducha(Q, out, NICHO_CABINE_E)
    out = FA.chuveiro(Q, out, q["chuveiro"])
    out = nicho_ducha(Q, out)
    out = FA.chuveiro(Q, out, DUCHA_AMBIENTE_E)
    # a borda e a sombra da bancada e o vaso não passam para a face das paredes (a parede do PDF volta inteira em volta
    # deles, como saiu da etapa das paredes)
    par = paredes_pdf(Q) | (Q.preencher(lambda d: d.get("layer") == "ARQ - Parede" and d.get("fill") is not None
                                        and max(d["fill"]) < 0.5) > 0.05)
    par = cv2.erode(par.astype(np.uint8), np.ones((2, 2), np.uint8)).astype(bool)
    zona = np.zeros_like(par)
    for r in (q["bancada"], q["vaso"][0]):
        a, b, c, d = F.ret_q(Q, (r[0] - 4, r[1] - 4, r[2] + 4, r[3] + 4))
        zona[b:d, a:c] = True
    out[par & zona] = img[par & zona]
    print("    vestiário: a bancada em granito Marrom Tabaco escovado (borda e sombra, E9), a cuba esculpida em travertino "
          "bruto, a torneira cromada, o vaso branco e o chuveiro de teto cromado; o chuveiro da ducha do ambiente "
          "(placa, braço e canopla cromados) pelo PDF; os nichos da parede (o da ducha e o da cabine) em travertino")
    return out


# As paredes do Subsolo (usuário, 28/10/26: "A PAREDE AQUI NÃO ESTÁ PERFEITA. PRECISO DELA RETA E SEM DENTE", no toco
# entre a ducha e o ambiente; "ESSA PAREDE DA SAUNA TEM UM DENTE TAMBÉM QUE PRECISA DE CORREÇÃO"): entram as faixas de
# revestimento das faces (os preenchimentos escuros da ARQ_REVESTIMENTOS, 0,57 pt, que o PDF desenha como parte da
# parede: sem elas o topo do toco saía em degrau e as paredes ficavam mais finas que o desenho); na ponta da parede da
# sauna junto à porta, o dente de 1,4 pt (o encaixe do batente) sai e a face de baixo segue reta até a porta.
# Na porta do elevador (revisão de 28/10, item 3, OK do usuário), os dois batentes do PDF (as tiras cinza de 1,4 pt da
# ARQ_PAREDE que descem da face da parede para a academia), finos e iguais, como na entrada do elevador do Subsolo da
# Casa D: o render só desenhava o da esquerda, um toco marrom largo com uma mancha escura ao lado, e o da direita quase
# sumia (a final os mostrava claros e as peças ficavam de fora). O vinílico em volta deles é refeito antes, nos pisos
# (`PORTAS_E["limpar"]`).
PAREDES_SUB_E = dict(PAREDES_E, camadas=PAREDES_E["camadas"] + ("ARQ_REVESTIMENTOS",),
                     tirar=[(1000.38, 957.12, 1008.89, 958.53)],
                     por=[(999.19, 957.12, 1008.89, 957.68),
                          (1758.7, 1005.3, 1760.1, 1014.1), (1799.8, 1005.3, 1801.2, 1014.1)])


# A borda direita da cabine do elevador sob o rótulo antigo (o ELEVADOR, que agora vai ao centro: o "R" dele cobria a
# borda, e a retirada dos rótulos a deixou borrada ali): as colunas da faixa (`faixa_pt`) refeitas pela mediana das
# linhas logo acima (`molde_pt`), onde a borda é reta.
ELEVADOR_SUB_E = {"faixa_pt": (1803.0, 952.5, 1810.0, 960.5), "molde_pt": (1803.0, 945.5, 1810.0, 951.5)}


def cabine_elevador_e(Q, img):
    q = ELEVADOR_SUB_E
    out = img.copy()
    a, b, c, d = F.ret_q(Q, q["faixa_pt"])
    _, mb, _, md = F.ret_q(Q, q["molde_pt"])
    out[b:d, a:c] = np.median(img[mb:md, a:c].astype(np.float32), axis=0).round().astype(np.uint8)[None]
    print(f"    elevador: a borda da cabine sob o rótulo antigo refeita ({c - a} x {d - b} px)")
    return out


# A parte de baixo da piscina do Subsolo (usuário, 28/10/26: "na parte de baixo da piscina está invertido: a parede é a
# parte de baixo e a borda da piscina a parte de cima"; depois, vendo a troca: "o subsolo ficou horrivel, deixe apenas
# parede na parte de baixo sem borda"): ali o PDF tem um bloco cheio (preto), e o render pôs a parede junto à água e uma
# faixa de Bege Bahia por fora. Na `caixa` (px da final), da linha `topo_y` para baixo, o que era parede ou Bege Bahia
# (com a emenda entre eles) vira parede, no cinza dela; só fica a borda da esquerda, ao lado da água (o px com água a
# até `lado_px` à direita na mesma linha).
PISCINA_BORDA_SUB = {"caixa": (850, 895, 1064, 958), "topo_y": 909, "lado_px": 15, "parede_lum": 95}


def piscina_borda_sub(Q, img, q=None):
    q = q or PISCINA_BORDA_SUB
    x0, y0, x1, y1 = q["caixa"]
    r = img[y0:y1, x0:x1].astype(np.float32)
    lum, rb = r.mean(axis=2), r[..., 2] - r[..., 0]
    agua = (r[..., 0] - r[..., 2] > 40)                                   # o turquesa (B bem acima de R)
    parede = (lum < q["parede_lum"]) & (np.abs(rb) < 12)
    bege = (rb > 15) & (lum > 150) & (lum < 240)
    yy = np.mgrid[y0:y1, x0:x1][0]
    # a parede e o Bege Bahia, com os px da emenda entre eles (a linha antisserrilhada), menos a água
    zona = cv2.morphologyEx((parede | bege).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)).astype(bool)
    zona &= (yy >= q["topo_y"]) & ~agua
    agua_dir = np.zeros_like(agua)                                        # água a até `lado_px` à direita
    for k in range(1, q["lado_px"] + 1):
        agua_dir[:, :-k] |= agua[:, k:]
    nova_parede = zona & ~agua_dir
    out = img.copy()
    out[y0:y1, x0:x1][nova_parede] = np.round(np.median(r[parede & (yy >= q["topo_y"])], axis=0)).astype(np.uint8)
    print(f"    parte de baixo da piscina só em parede: {int((nova_parede & ~parede).sum())} px de Bege Bahia viraram "
          f"parede")
    return out


def passos_subsolo(Q):
    return [
        ("pisos", lambda im: pisos_e(Q, im, PISOS_SUB_E, zonas=zonas_academia(Q), incluir=zonas_portas(Q))),
        ("escada", lambda im: escada_e(Q, im, ESCADA_SUB_E)),
        ("armario", lambda im: armario_cabides(Q, im, ARMARIO_DCE_E["pt"], ARMARIO_DCE_E["lado"], nome="DCE")),
        ("bancada", lambda im: bancada_e9(Q, im, BANCADA_WC_DCE2, nome="WC DCE 2")),
        ("piscina", lambda im: piscina_e(Q, im)),
        ("sauna", lambda im: sauna_e(Q, im)),
        # as cabines do vestiário e a divisória entre elas (a ARQ - Parede, que a E10 não pegava), na mesma máscara
        ("paredes", lambda im: paredes_e(Q, im, q=PAREDES_SUB_E, extra=lambda d: d.get("layer") == "ARQ - Parede",
                                         sempre=[PISCINA_E["caixa_pt"]], ini=inicial("Subsolo"),
                                         tirar=PAREDES_SUB_E["tirar"], por=PAREDES_SUB_E["por"],
                                         brancos=PISCINA_E["contorno"])),
        ("vestiario", lambda im: vestiario_e(Q, im)),
        ("aparelhos", lambda im: aparelhos_e(Q, im)),
        ("portas", lambda im: portas_e(Q, im)),
        ("elevador", lambda im: cabine_elevador_e(Q, im)),
        ("piscina_borda", lambda im: piscina_borda_sub(Q, im)),
        ("rotulos", lambda im: escrever_rotulos("Subsolo", im)),
    ]


# O Térreo (auditoria de 26/10, mapa `renders/POE642_CasaE_PH_Terreo_auditoria_2610.jpg`, e as regras aprovadas nos
# Térreos das Casas A a D):
# 1. E11: o granito (cozinha, serviço, circulações e banho gourmet, DCE, garagem, a faixa de cima) no granito de
#    referência das Casas B a D na resolução da prancha (o tom já era o delas; o desenho vinha do render de 2000 px,
#    largo e borrado); as projeções da DOC_LINHAS ficam por cima;
# 2. E3, E8: as escadas sem linhas e sem triângulo:
#    - a da circulação gourmet (a mesma do Subsolo): o trecho vivo à esquerda, com o sombreamento de descida para a
#      direita, o trecho depois do corte nevoado e o D do PDF no degrau de cima, à esquerda (onde estava o triângulo);
#    - a interna, do jardim: subindo da direita para a esquerda, o S do PDF no 1º degrau (à direita) e o trecho depois
#      do corte (à esquerda) nevoado;
#    - os degraus em blocos à direita do deck: os quatro blocos do PDF em Bege Bahia, sem o contorno, cada um um pouco
#      mais escuro que o de cima e com a sombra curta dele, descendo da direita para a esquerda (aprovado em 20/10), com
#      o D no bloco de cima;
# 3. E2: o armário do DCE (o retângulo com a diagonal junto à parede da esquerda) com os cabides, aberto para o quarto;
# 4. E5: o box de correr do WC DCE 1 nas duas folhas de vidro do PDF, com o trilho no vão (desde 28/10, como todos os
#    boxes, as duas folhas fechadas, de parede a parede, sem o trilho tracejado; e também o do banho gourmet);
# 5. E9: as bancadas do banho gourmet (o granito sobre o granito do piso), do WC DCE 1 e do lavabo com a borda no tom
#    escurecido da pedra e a sombra curta;
# 6. E10: as paredes e os muros em cinza 80; os pilares redondos da varanda em preto;
# 7. E4: a seta da entrada principal, no Bege Bahia de fora, apontando para a porta pivotante do HALL DE ENTRADA;
# 8. E7: o rótulo do WC DCE 1 fora da área do chuveiro, no meio do piso seco, entre o box, o vaso e a bancada.
PISOS_TER_E = [("granito", [(50, 66, 90)], "granito", None, 1.5, 2811, None)]
TRAV_TER = (205, 220, 235)
ESCADAS_TER_E = [
    {"nome": "da circulação gourmet", "pdf": (972.0, 617.0, 1262.9, 685.0),
     "bocels": [972.0 + 17.0 * k for k in range(1, 17)], "inicio": "direita", "apos": "direita",
     "corte": [(1073.8, 616.4), (1108.1, 685.0)], "nevoa": {"branco": 0.72, "sigma_px": 1.2},
     "sombra_corte": {"forca": 0.30, "alc_px": 4.0}, "textura": "travertino", "tom": TRAV_TER, "forca": 1.0,
     "letra": "D", "letra_no_alto": True, "semente": 2812},
    {"nome": "interna, do jardim", "pdf": (1659.2, 1138.5, 1984.0, 1221.4),
     "bocels": [1677.9 + 17.0 * k for k in range(18)], "inicio": "direita", "apos": "esquerda",
     "corte": [(1840.5, 1138.5), (1882.2, 1222.0)], "nevoa": {"branco": 0.72, "sigma_px": 1.2},
     "sombra_corte": {"forca": 0.30, "alc_px": 4.0}, "textura": "travertino", "tom": TRAV_TER, "forca": 1.0,
     "letra": "S", "semente": 2813}]
# no PDF, o bloco de cima (o da direita, junto ao deck) vem primeiro; na planta, o de cima cobre o de baixo: os blocos
# são pintados do último ao primeiro (`inverter`), cada um com a sombra curta sobre os já pintados
BLOCOS_TER_E = {"nome": "degraus em blocos do deck", "caixa_pt": (520.0, 1410.0, 630.0, 1680.0), "topo_primeiro": False,
                "inverter": True,
                "tom": 0.025, "sombra": {"dist_m": 0.05, "sig_m": 0.04, "forca": 0.32}, "semente": 2814,
                "letra": "D", "letra_pt": (614.65, 1528.5)}
ARMARIO_DCE_TER_E = {"pt": (1992.5, 761.5, 2023.7, 823.9), "lado": "direita"}
BOX_WC_DCE1 = (2150.0, 735.0, 2235.0, 750.0)
# o box do banho gourmet (usuário, 28/10: "reveja todos os box de todos os ambientes"): o do retoque
# (`retoque_terreo_casae.box_gourmet`) eram só as duas folhas do PDF, com o vão até a parede de cima vazio; agora, como os
# outros (`box_e`), as duas folhas fechadas, de parede a parede, no vidro claro sobre o granito
BOX_GOURMET_E = (1100.0, 720.0, 1110.0, 790.0)
BANCADAS_TER_E = [("banho gourmet", (1163.3, 759.8, 1252.7, 784.2)), ("WC DCE 1", (2202.4, 788.0, 2230.6, 823.9)),
                  ("lavabo", (2064.0, 1453.3, 2159.3, 1478.7))]
# a seta em frente à porta pivotante do hall (usuário, 28/10/26: "A seta em preto deve ficar em frente a porta, um pouco
# mais acima de onde ela está"): a ponta no meio do vão do PDF, entre os batentes (1488,3 e 1638,6 pt, o meio em 1563,5 pt);
# antes, em y = 1542 px, ela apontava para o vidro fixo abaixo da porta
SETA_TER_E = (2500, 1408)
SETA_TER_E_ANTES = (2500, 1542)
AJUSTES_E["Terreo"] = [("WC DCE 1", (1261.6, 271.3), (-0.9, 32.3), 0.85),  # no meio do piso seco (2177,5 x 780 pt)
                       # fora do X tracejado do hall (usuário, 28/10/26: "o rótulo do hall de entrada não pode ficar sobre
                       # o tracejado"): à direita do cruzamento, no triângulo entre o X e a porta, no corpo de sempre, a
                       # ~10 px do tracejado, das paredes e dos objetos (o lugar livre mais folgado do hall)
                       ("HALL DE ENTRADA", (1220.2, 777.0), (35.4, -20.3))]
# o rótulo da área de serviço descoberta no X tracejado (usuário, 28/10/26, opção A: o X aberto embaixo do rótulo, o
# tracejado parando numa folga em volta do texto e o rótulo no centro, como o X do shaft da Casa B): o centro do bloco
# no cruzamento do X (2060,4 x 496,5 px da final); o vão é `TRACEJADOS_TE["vaos"]`
ROTULO_SERVICO_TE = ("ÁREA DE SERVIÇO DESCOBERTA", (1110.2, 254.4), (-38.6, 3.9))
AJUSTES_E["Terreo"].append(ROTULO_SERVICO_TE)


# A água da piscina, da prainha e do spa no tom da referência do Subsolo (usuário, 28/10/26: "APLIQUE O TOM DA PISCINA
# NO TÉRREO TAMBÉM"), pela rotina das piscinas de todas as casas (`piscinas_turquesa.turquesa`); as duas folhas de vidro
# do lado esquerdo (os traços claros e neutros em pé, de pelo menos `vidro_px` px) ficam como estão.
PISCINA_TER_E = {"vidro_px": 41, "vidro_croma": 14, "vidro_luz": 120, "semente": 2851}


def piscina_terreo_e(Q, img):
    import piscinas_turquesa as PT
    q = PISCINA_TER_E
    a = img.astype(np.int16)
    neutro = ((a.max(axis=2) - a.min(axis=2)) < q["vidro_croma"]) & (a.mean(axis=2) > q["vidro_luz"])
    vidros = cv2.morphologyEx(neutro.astype(np.uint8), cv2.MORPH_OPEN, np.ones((q["vidro_px"], 1), np.uint8))
    vidros = cv2.dilate(vidros, np.ones((3, 3), np.uint8)).astype(bool)
    out, areas = PT.turquesa(img, px_m=Q.px_m, semente=q["semente"], proteger=vidros)
    # as bordas retas no desenho do PDF (usuário, 28/10/26: "aplique nas bordas das outras casas também", depois das da
    # Casa A: "corrija as bordas deixando as perfeitas"): `piscinas_turquesa.bordas_retas`, com a mesma rede das cáusticas
    corpos, _, _, _, _ = PT._bordas_px("E-Terreo", Q)
    rede = PT._rede_quadro(img, [r for c in corpos for r in c], img.shape, px_m=Q.px_m, semente=q["semente"])
    out = PT.bordas_retas(out, corpos, rede=rede, proteger=vidros)
    # as duas bordas em vidro no desenho do vidro da Casa C (usuário, 28/10/26: "faça o mesmo na piscina da casa E, com
    # duas bordas em vidro"): `piscinas_turquesa.vidros_borda`, nas lâminas da ARQ_PAREDE (`VIDROS_BORDA["E-Terreo"]`)
    out = PT.vidros_borda(out, PT._vidros_px("E-Terreo", Q), pontas=True)
    print(f"    piscina: a água no turquesa da referência ({', '.join(map(str, areas))} m²: piscina e prainha, a faixa entre "
          f"os vidros, o spa), com as peças, os degraus e a rede das cáusticas; as bordas retas pelo PDF; as duas bordas "
          f"em vidro no desenho da Casa C")
    return out


# As cortinas no modelo padrão (usuário, 28/10/26: "NO TERREO DA CASA E, VAMOS ALTERAR O MODELO DAS CORTINAS PARA A QUE
# ADOTAMOS COMO PADRÃO"). O pano já era o franzido (`blocos.pano_franzido`, 27/10), mas no travertino claro do Térreo o
# linho quase some e só as sombras das pregas aparecem, como a linha em zigue-zague antiga; e, na janela de baixo do
# living, a corda do render entre o trilho e a primeira folha de vidro ficou. Aqui:
# - "limpar": a corda sai (px do quadro: x0, x1, y0, y1), com o travertino das mesmas colunas `dy` px acima;
# - cada pano sai inteiro (a pegada do pano franzido, `limiar`, com `folga` px) e volta com o piso do ambiente
#   (`cortinas_franzidas.tirar`), e o pano franzido entra no mesmo eixo, com o linho um pouco mais fechado (`linho`), o
#   contorno do tecido mais escuro (`contorno`: largura em px e escurecimento) e a sombra curta no piso mais marcada
#   (`sombra`), para o pano se ler como corpo de tecido no piso claro, como nas casas de piso escuro.
CORTINAS_TER_E = {"limpar": [(1591, 1714, 1546, 1554, -300), (1714, 1847, 1546, 1551, -300)],
                  "limiar": 0.02, "folga": 1, "linho": 0.94, "contorno": (0.7, 0.25), "sombra": 1.8, "k": 8}


def cortinas_terreo_e(Q, img):
    import json
    import pymupdf
    sys.path.insert(0, str(RAIZ / "_blocos"))
    import blocos
    import cortinas_franzidas as CF
    import retoque_terreo_casae as T
    from opcoes_1pav_casae import quadro_pdf
    q = CORTINAS_TER_E
    out = np.ascontiguousarray(img.copy())
    for x0, x1, y0, y1, dy in q["limpar"]:
        out[y0:y1, x0:x1] = img[y0 + dy:y1 + dy, x0:x1]
    cfg = json.loads(T.CONFIG.read_text())
    pg = pymupdf.open(T.PDF)[cfg["pavimentos"]["Terreo"]["pagina"]]
    at, lt = cv2.imread(str(T.BASE), cv2.IMREAD_GRAYSCALE).shape
    hb, wb = cv2.imread(str(T.BASE_SEM_TELA), cv2.IMREAD_GRAYSCALE).shape
    p2q = quadro_pdf(pg, cfg, lt, at, wb, hb, out.shape[1])
    px_m = CF.px_m_de(p2q)
    k = q["k"]
    n = 0
    for c in T.CORTINAS["conjuntos"]:
        vertical = c["vidro"] in ("direita", "esquerda")
        ep = c["trilho"][0]
        for pp0, pp1 in c["panos"]:
            if vertical:
                (eixo, t0), (_, t1) = p2q(ep, pp0), p2q(ep, pp1)
            else:
                (t0, eixo), (t1, _) = p2q(pp0, ep), p2q(pp1, ep)
            comp = (t1 - t0) / px_m
            cor, a = blocos.pano_franzido(comp, px_m * k)
            velho = CF.pegada(out.shape, cor, a, eixo, t0, k, c["vidro"]) > q["limiar"]
            velho = cv2.dilate(velho.astype(np.uint8), np.ones((2 * q["folga"] + 1,) * 2, np.uint8)).astype(bool)
            CF.tirar(out, velho, c["vidro"], px_m)
            tec = (a > 0.6).astype(np.float32)
            lc, esc = q["contorno"]
            r = max(1, int(round(lc * k)))
            borda = tec - cv2.erode(tec, np.ones((2 * r + 1, 2 * r + 1), np.uint8))
            cor = cor * (q["linho"] * (1 - esc * borda))[..., None]
            a = np.where(tec > 0, a, np.clip(a * q["sombra"], 0, 1)).astype(np.float32)
            T.pousar_cortina(out, cor, a, eixo, t0, k, c["vidro"])
            n += 1
    print(f"    cortinas: {n} panos franzidos no modelo padrão, com o contorno do linho e a sombra curta; a corda do render "
          f"junto ao vidro do living fora")
    return out


def passos_terreo(Q):
    return [
        ("pisos", lambda im: pisos_e(Q, im, PISOS_TER_E)),
        ("escadas", lambda im: blocos_e(Q, escada_e(Q, escada_e(Q, im, ESCADAS_TER_E[0]), ESCADAS_TER_E[1]),
                                        BLOCOS_TER_E)),
        ("armario", lambda im: armario_cabides(Q, im, ARMARIO_DCE_TER_E["pt"], ARMARIO_DCE_TER_E["lado"], nome="DCE")),
        ("box", lambda im: boxes_terreo_e(Q, im)),
        ("bancadas", lambda im: _bancadas(Q, im, BANCADAS_TER_E)),
        ("paredes", lambda im: paredes_e(Q, im)),
        ("seta", lambda im: seta_e(Q, im, SETA_TER_E)),
        ("cortinas", lambda im: cortinas_terreo_e(Q, im)),
        ("piscina", lambda im: piscina_terreo_e(Q, im)),
        ("revisao", lambda im: revisao_terreo_e(Q, im)),
        ("tracejados", lambda im: tracejados_pb_te(Q, im)),
        ("poltronas", lambda im: poltronas_living_te(Q, im)),
        ("sofa_varanda", lambda im: sofa_varanda_te(Q, im)),
        ("rotulos", lambda im: escrever_rotulos("Terreo", im)),
    ]


def boxes_terreo_e(Q, img):
    return box_e(Q, box_e(Q, img, BOX_WC_DCE1, nome="WC DCE 1"), BOX_GOURMET_E, nome="banho gourmet")


def _bancadas(Q, img, lista):
    for nome, r in lista:
        img = bancada_e9(Q, img, r, nome=nome)
    return img


# ----------------------------------------------------------------------------------------------------------------------
# A revisão de 28/10/26 do Térreo (usuário: "VAMOS REVISAR O TÉRREO DA CASA E"; os quatro itens aprovados com "pode
# aplicar os 4"), na etapa `revisao`, antes dos rótulos. Vai sobre a final aprovada (`--sobre-final revisao`): a final das
# etapas em cache é anterior aos acertos feitos direto na final.
# 1. A frente da adega: no vão, o render deixou uma faixa cinza borrada e um dente claro no lugar da porta. A faixa do fim
#    das prateleiras ao travertino limpo do hall (`faixa_pt`) volta ao travertino do hall (as linhas logo abaixo, em
#    espelho), com as paredes do PDF por cima, e a porta do PDF entra como as de correr do Subsolo
#    (`final3840_casaa.portas_vidro`): a soleira de Bege Bahia no vão, os três batentes, o vidro fixo da esquerda (a linha
#    do PDF em 1004,6 pt) e as duas folhas de correr nos seus planos, com os montantes.
# 2. Os pisantes (os 9 retângulos da ARQ_CONTRAPISO à direita do acesso; regra de 27/10: a borda reta do PDF): cada um no
#    retângulo do PDF, em Bege Bahia (a foto da biblioteca no tom dos pisantes do render, cada peça com o tom um pouco
#    diferente), com a sombra curta; em volta, onde o render deixou a borda clara e restos da pedra, a grama vizinha. As
#    manchas da vegetação antiga (usuário, 28/10: "essas manchas nas pedras da vegetação antiga precisam ser removidas")
#    saem com eles; na pedra grande do acesso (o Bege Bahia da ARQ_CONTRAPISO à esquerda), as folhas sobre a borda da
#    direita e sobre o canto de baixo também: o que não é pedra (verde ou escuro) nas `faixas` junto à borda vem, em
#    espelho, da pedra mais para dentro, e a borda fica na reta do PDF.
# 3. A curva da pedra portuguesa contra a grama: a borda em degraus do render vai para a curva do PDF (o preenchimento da
#    ARQ_CONTRAPISO), lisa, com antialias. De cada lado da curva, a faixa de `d0_px` vem em espelho de logo além dela (a
#    pedra de dentro, a grama de fora), só onde do lado de fora há grama. A mancha escura junto ao arbusto de cima sai
#    junto (o que não é pedra na faixa de `mancha_px` dentro da curva, em espelho da pedra mais para dentro).
# 4. A projeção da cobertura sobre o granito (perdida em 28/10, 01:47, quando o granito foi refeito; a prancha de 27/10 a
#    tinha): o tracejado cinza do retoque (`retoque_terreo_casae.PROJECOES`, o mesmo que segue na varanda) nas linhas do
#    PDF: a da laje da garagem sobre a circulação (687,8 pt), a borda de cima do granito (516,3 pt) e a lateral direita
#    (2763,5 pt), até a pedra portuguesa; nada sobre as paredes.
REVISAO_TE = {
    "adega": {"faixa_pt": (1854.75, 998.5, 1985.71, 1008.1),
              "portas": [{"nome": "da adega, vidro fixo", "soleira": (1856.45, 1003.61, 1984.01, 1005.31),
                          "batentes": [(1856.45, 1003.61, 1857.58, 1005.31), (1890.47, 1003.61, 1891.6, 1005.31),
                                       (1982.87, 1003.61, 1984.01, 1005.31)],
                          "folhas": [((1857.58, 1004.06, 1890.47, 1005.2), "x")], "montante_pt": 0.0},
                         {"nome": "da adega, folhas de correr", "batentes": [],
                          "folhas": [((1891.6, 1000.77, 1936.95, 1003.04), "x"),
                                     ((1936.95, 1003.04, 1982.87, 1005.31), "x")], "montante_pt": 2.84}]},
    # `faixas`: (x0, y0, x1, y1) em pt, o lado da borda ("dir" ou "baixo") e a largura em px que é refeita (o espelho é
    # sobre a linha a essa distância da borda; a faixa tem o dobro, para a pedra de onde vem o espelho)
    "pisantes": {"bloco": 197, "semente": 2841, "forca": 0.75, "tom_peca": 0.015, "sombra": (0.22, 1.15, 1.35), "folga_px": 7,
                 "faixas": [((2347.0, 1487.4, 2383.69, 1790.5), "dir", 18), ((2340.0, 1762.0, 2383.69, 1790.5), "baixo", 14)]},
    "curva": {"seqno": 35463, "d0_px": 5, "grama_min": 0.5, "mancha_px": 16, "escuro": 140},
    "projecao": {"linhas": [[(1992.5, 687.8), (2763.5, 687.8)],
                            [(1372.9, 516.3), (2763.5, 516.3), (2763.5, 1090.3)]],
                 "traco_pt": 8.5, "vao_pt": 4.25, "larg_px": 1.1, "cor": (150, 151, 150), "forca": 0.85, "ss": 8},
}


def _verde(reg):
    """Grama e vegetação (bool): o verde passa o vermelho e não fica abaixo do azul."""
    r = reg.astype(np.int16)
    return (r[..., 1] > r[..., 2] + 4) & (r[..., 1] >= r[..., 0])


def adega_porta_te(Q, img, q=None):
    import final3840_casaa as FA
    q = q or REVISAO_TE["adega"]
    out = np.ascontiguousarray(img.copy())
    x0, y0, x1, y1 = q["faixa_pt"]
    (u0, v0), (u1, v1) = Q.p2q(x0, y0), Q.p2q(x1, y1)
    a, b, c, d = int(np.floor(u0)), int(np.ceil(v0)), int(np.ceil(u1)), int(np.floor(v1))
    # a faixa volta ao travertino do hall: as linhas logo abaixo dela, em espelho (a linha d - 1 recebe a d)
    out[b:d, a:c] = out[d:2 * d - b, a:c][::-1]
    paredes_pdf(Q)
    par = Q._par[b:d, a:c]
    reg = out[b:d, a:c].astype(np.float32)
    out[b:d, a:c] = np.clip(np.round(reg * (1 - par[..., None]) + np.float32(PAREDES_E["cor"]) * par[..., None]),
                            0, 255).astype(np.uint8)
    guarda = FA.PORTAS_VIDRO
    FA.PORTAS_VIDRO = dict(FA.PORTAS_VIDRO, portas=q["portas"])
    try:
        out = FA.portas_vidro(Q, out)
    finally:
        FA.PORTAS_VIDRO = guarda
    print(f"    adega: a faixa do vão ({c - a} x {d - b} px) no travertino do hall e a porta de vidro de correr do PDF "
          f"(soleira, batentes, vidro fixo e duas folhas)")
    return out


def _espelho_faixa(reg, lado, larg):
    """A faixa de `larg` px junto à borda (`lado`: a borda é a última coluna ou linha de `reg`) em espelho da pedra logo
    para dentro dela (a linha de espelho a `larg` px da borda)."""
    if lado == "dir":
        src = reg[:, -2 * larg:-larg][:, ::-1]
        return np.concatenate([reg[:, :-larg], src], axis=1)
    src = reg[-2 * larg:-larg][::-1]
    return np.concatenate([reg[:-larg], src], axis=0)


def pisantes_te(Q, img, q=None):
    sys.path.insert(0, str(RAIZ / "_texturas"))
    from texturas import textura
    q = q or REVISAO_TE["pisantes"]
    pis = [d for d in Q.desenhos if d.get("layer") == "ARQ_CONTRAPISO" and d["type"] == "f" and d.get("fill")
           and abs(d["fill"][0] - 0.894) < 0.01 and 60 < d["rect"].width < 120 and 120 < d["rect"].height < 200]
    rets = [tuple(d["rect"]) for d in pis]
    bloco = next(d for d in Q.desenhos if d.get("seqno") == q["bloco"])
    fx = [Q.p2q(r[0], r[1]) for r, _, _ in q["faixas"]] + [Q.p2q(r[2], r[3]) for r, _, _ in q["faixas"]]
    fx += [Q.p2q(r[0], r[1]) for r in rets] + [Q.p2q(r[2], r[3]) for r in rets]
    fx = np.array(fx)
    X0, Y0 = (np.floor(fx.min(axis=0)) - 14).astype(int)
    X1, Y1 = (np.ceil(fx.max(axis=0)) + 14).astype(int)
    w, h = X1 - X0, Y1 - Y0
    reg = img[Y0:Y1, X0:X1].copy()
    a_pis = _ret_pdf(Q, rets, X0, Y0, w, h, ss=8)
    ss = 8
    m = np.zeros((h * ss, w * ss), np.uint8)
    for c in Q.caminhos(bloco):
        if len(c) >= 3:
            cv2.fillPoly(m, [np.int32(np.round((c - (X0, Y0)) * ss))], 255)
    a_blk = cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    verde = _verde(reg)
    # as faixas da pedra grande: as manchas (verde ou escuro) e a borda (as 2 últimas colunas ou linhas) em espelho
    faixa = np.zeros((h, w), bool)
    pedra = reg.astype(np.float32).copy()
    n_mancha = 0
    for r, lado, larg in q["faixas"]:
        (u0, v0), (u1, v1) = Q.p2q(r[0], r[1]), Q.p2q(r[2], r[3])
        a, b = int(np.floor(u0)) - X0, int(np.floor(v0)) - Y0
        c, d = int(np.ceil(u1)) - X0, int(np.ceil(v1)) - Y0
        faixa[b:d, a:c] = True
        f = reg[b:d, a:c]
        lum = f.astype(np.float32).mean(axis=2)
        dentro = a_blk[b:d, a:c] > 0.99
        med = np.median(lum[dentro])
        mancha = dentro & (_verde(f) | (lum < med - 25) | (f[..., 1].astype(np.int16) >= f[..., 2].astype(np.int16) - 4))
        mancha = cv2.dilate(mancha.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
        borda = np.zeros_like(mancha)
        if lado == "dir":
            borda[:, -3:] = True
        else:
            borda[-3:] = True
        esp = _espelho_faixa(f.astype(np.float32), lado, larg)
        troca = mancha | borda
        if lado == "dir":
            troca[:, :-larg] = False
        else:
            troca[:-larg] = False
        pedra[b:d, a:c] = np.where(troca[..., None], esp, pedra[b:d, a:c])
        n_mancha += int((mancha & dentro).sum())
    # a grama: tudo o que não é verde perto das pedras (a borda clara, os restos da pedra antiga) e as próprias pedras
    # saem e voltam pela grama vizinha (inpaint)
    k = 2 * q["folga_px"] + 1
    pedras = (a_pis > 0.01) | ((a_blk > 0.01) & faixa)
    perto = cv2.dilate(pedras.astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool) & (a_blk <= 0.5)
    sem = pedras | (perto & ~verde)
    G = cv2.inpaint(reg, sem.astype(np.uint8), 4, cv2.INPAINT_TELEA).astype(np.float32)
    # os pisantes: a foto da biblioteca no tom do render (o miolo dos pisantes antigos, sem as manchas)
    miolo = cv2.erode((a_pis > 0.99).astype(np.uint8), np.ones((17, 17), np.uint8)).astype(bool)
    lum = reg.astype(np.float32).mean(axis=2)
    tom = np.median(reg[miolo & (lum > np.median(lum[miolo]) - 20) & ~verde].reshape(-1, 3), axis=0).astype(np.float32)
    T = textura("bege_bahia", Q.px_m, h, w, semente=q["semente"]).astype(np.float32)
    T = (1 + q["forca"] * (T / T.reshape(-1, 3).mean(axis=0) - 1)) * tom
    rng = np.random.default_rng(q["semente"])
    fs, dist, sig = q["sombra"]
    sb = cv2.GaussianBlur(cv2.warpAffine(a_pis, np.float32([[1, 0, -dist], [0, 1, dist]]), (w, h)), (0, 0), sig) * fs
    out = np.where(sem[..., None], G, reg.astype(np.float32)) * (1 - sb * (1 - a_pis))[..., None]
    for r in rets:
        ai = _ret_pdf(Q, [r], X0, Y0, w, h, ss=8)
        out = out * (1 - ai[..., None]) + T * (1 + rng.uniform(-q["tom_peca"], q["tom_peca"])) * ai[..., None]
    # a pedra grande: nas faixas, a pedra limpa até a reta do PDF; fora delas fica como estava
    blk = (a_blk > 0.01) & faixa
    out = np.where(blk[..., None], out * (1 - a_blk[..., None]) + pedra * a_blk[..., None], out)
    out = np.where(((a_blk > 0.01) & ~faixa)[..., None], reg.astype(np.float32), out)
    res = img.copy()
    res[Y0:Y1, X0:X1] = np.clip(np.round(out), 0, 255).astype(np.uint8)
    print(f"    pisantes: {len(rets)} retângulos do PDF em Bege Bahia (tom {tom.round().astype(int).tolist()}), com a sombra "
          f"curta e a grama em volta; pedra grande do acesso: {n_mancha} px de manchas da vegetação antiga e a borda reta")
    return res


def curva_pedra_te(Q, img, q=None):
    q = q or REVISAO_TE["curva"]
    d = next(d for d in Q.desenhos if d.get("seqno") == q["seqno"])
    cams = AJ.caminhos_pdf(d, Q.p2q, passos=64)
    tudo = np.concatenate(cams)
    X0, Y0 = np.maximum(np.floor(tudo.min(axis=0)).astype(int) - 24, 0)
    X1, Y1 = np.minimum(np.ceil(tudo.max(axis=0)).astype(int) + 24, (Q.W, Q.H))
    w, h = X1 - X0, Y1 - Y0
    ss = 4
    m = np.zeros((h * ss, w * ss), np.uint8)
    for c in cams:
        if len(c) >= 3:
            cv2.fillPoly(m, [np.int32(np.round((c - (X0, Y0)) * ss))], 255)
    a = cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    din = cv2.distanceTransform((m > 0).astype(np.uint8), cv2.DIST_L2, 5)
    dout = cv2.distanceTransform((m == 0).astype(np.uint8), cv2.DIST_L2, 5)
    s = cv2.resize((din - dout) / ss, (w, h), interpolation=cv2.INTER_AREA)       # px, positivo dentro da pedra
    gy, gx = np.gradient(cv2.GaussianBlur(s, (0, 0), 1.5))
    n = np.hypot(gx, gy) + 1e-6
    nx, ny = (gx / n).astype(np.float32), (gy / n).astype(np.float32)               # a normal para dentro
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    d0, dm = q["d0_px"], q["mancha_px"]

    def espelho(fonte, linha):
        """`fonte` em espelho sobre a linha de distância `linha` à curva (positiva dentro da pedra), do lado de cá dela."""
        k = (2 * (linha - s)).astype(np.float32)
        k = np.where((k > 0) if linha > 0 else (k < 0), k, 0).astype(np.float32)
        return cv2.remap(fonte, xs + nx * k, ys + ny * k, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    verde = _verde(img[Y0:Y1, X0:X1])
    fora = (s < -1.5) & (s > -(2 * d0 + 6))
    kk = (2 * d0 + 9, 2 * d0 + 9)
    frac = cv2.boxFilter((verde & fora).astype(np.float32), -1, kk, normalize=False) / \
        np.maximum(cv2.boxFilter(fora.astype(np.float32), -1, kk, normalize=False), 1)
    grama = frac > q["grama_min"]
    perto_grama = cv2.dilate(grama.astype(np.uint8), np.ones((2 * dm + 9,) * 2, np.uint8)).astype(bool)
    # 1. a pedra limpa: o que não é pedra (verde ou escuro: a pedra portuguesa não desce de ~155) a até `mancha_px` da
    #    curva, junto à grama, vem em espelho da pedra mais para dentro
    lum = reg.mean(axis=2)
    mancha = (s > 0) & (s < dm) & (verde | (lum < q["escuro"])) & perto_grama
    mancha = cv2.dilate(mancha.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool) & (s > 0)
    limpa = np.where(mancha[..., None], espelho(reg, dm + 3), reg)
    # 2. as duas faixas junto à curva: a pedra de dentro e a grama de fora, em espelho; onde a grama de fora é estreita
    #    (o espelho cai num pisante), a grama vem da vizinha (inpaint)
    S = espelho(limpa, d0)
    G = espelho(reg, -d0)
    banda = (np.abs(s) < d0 + 1) & grama
    ruim = banda & (a < 0.999) & ~_verde(np.clip(G, 0, 255).astype(np.uint8))
    if ruim.any():
        base = np.clip(np.where((banda & (a < 0.999))[..., None], G, reg), 0, 255).astype(np.uint8)
        G = cv2.inpaint(base, (ruim | (banda & (s > -1))).astype(np.uint8), 3, cv2.INPAINT_TELEA).astype(np.float32)
    novo = S * a[..., None] + G * (1 - a[..., None])
    reg = np.where(banda[..., None], novo, limpa)
    out = img.copy()
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    print(f"    pedra portuguesa: a borda contra a grama na curva do PDF ({int(banda.sum())} px, faixa de {d0} px de cada "
          f"lado; {int(ruim.sum())} px da grama de fora pela vizinha); {int(mancha.sum())} px de mancha junto à curva")
    return out


def _alfa_projecao_te(Q, q=None):
    """O alfa (0 a 1) do tracejado cinza de `projecao_cobertura_te` na janela dele: (alfa, X0, Y0)."""
    q = q or REVISAO_TE["projecao"]
    pts = np.array([Q.p2q(x, y) for linha in q["linhas"] for x, y in linha])
    X0, Y0 = (np.floor(pts.min(axis=0)) - 4).astype(int)
    X1, Y1 = (np.ceil(pts.max(axis=0)) + 5).astype(int)
    w, h, ss = X1 - X0, Y1 - Y0, q["ss"]
    m = np.zeros((h * ss, w * ss), np.uint8)
    lw = max(1, int(round(q["larg_px"] * ss)))
    n = 0
    for linha in q["linhas"]:
        for (ax, ay), (bx, by) in zip(linha[:-1], linha[1:]):
            comp = np.hypot(bx - ax, by - ay)
            t = 0.0
            while t < comp:
                t1 = min(comp, t + q["traco_pt"])
                u = np.subtract(Q.p2q(ax + (bx - ax) * t / comp, ay + (by - ay) * t / comp), (X0, Y0)) * ss
                v = np.subtract(Q.p2q(ax + (bx - ax) * t1 / comp, ay + (by - ay) * t1 / comp), (X0, Y0)) * ss
                cv2.line(m, tuple(int(round(z)) for z in u), tuple(int(round(z)) for z in v), 255, lw, cv2.LINE_AA)
                n += 1
                t = t1 + q["vao_pt"]
    a = cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255 * q["forca"]
    paredes_pdf(Q)
    a *= 1 - np.clip(cv2.dilate(Q._par[Y0:Y1, X0:X1], np.ones((3, 3), np.uint8)), 0, 1)       # nada sobre as paredes
    return a, X0, Y0, n


def projecao_cobertura_te(Q, img, q=None):
    q = q or REVISAO_TE["projecao"]
    a, X0, Y0, n = _alfa_projecao_te(Q, q)
    h, w = a.shape
    Y1, X1 = Y0 + h, X0 + w
    out = img.copy()
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg * (1 - a[..., None]) + np.float32(q["cor"]) * a[..., None]), 0,
                                255).astype(np.uint8)
    print(f"    projeção da cobertura: {len(q['linhas'])} linhas do PDF em tracejado cinza ({n} traços), sobre o granito")
    return out


def seta_rotulo_hall_te(Q, img, desvio_px=38):
    """Sobre a final do Térreo: a seta sai de `SETA_TER_E_ANTES` (o Bege Bahia de `desvio_px` acima, nas mesmas colunas) e
    volta em `SETA_TER_E`; o rótulo do hall vai para o ajuste novo (`AJUSTES_E`), sem mexer nos outros rótulos."""
    import final3840_casaa_terreo as FT
    guarda = FT.SETA
    FT.SETA = dict(guarda, ponta=SETA_TER_E_ANTES)
    try:
        branca = FT.seta(Q, np.full_like(img, 255))
    finally:
        FT.SETA = guarda
    a = (255 - branca.astype(np.float32).mean(axis=2)) / (255 - np.mean(guarda["cor"]))
    m = cv2.dilate((a > 0.01).astype(np.uint8), np.ones((5, 5), np.uint8)).astype(np.float32)
    m = np.maximum(cv2.GaussianBlur(m, (0, 0), 1.0), np.clip(a, 0, 1))
    ys, xs = np.nonzero(m > 0)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    out = img.astype(np.float32)
    fonte = out[y0 - desvio_px:y1 - desvio_px, x0:x1]
    mm = m[y0:y1, x0:x1, None]
    out[y0:y1, x0:x1] = out[y0:y1, x0:x1] * (1 - mm) + fonte * mm
    out = seta_e(Q, np.clip(np.round(out), 0, 255).astype(np.uint8), SETA_TER_E)
    # o rótulo do hall: a final sem os rótulos, os rótulos de novo e, na final, só as caixas do rótulo do hall (a de antes
    # e a nova)
    limpa, _ = sem_rotulos("Terreo", out)
    nova = escrever_rotulos("Terreo", limpa)
    _, rot, aj, _ = _rotulos_pav("Terreo")
    hall = [r for r in rot if r[0] == "HALL DE ENTRADA"]
    import retoque_1pav_casae as R1
    caixa = np.zeros(img.shape[:2], bool)
    for ajs in (aj, aj + [a_ for a_ in AJUSTES_E["Terreo"] if a_[0] == "HALL DE ENTRADA"]):
        b = R1.rotulos_ambientes(np.full_like(img, 255), hall, Q.p2q, escala_desvio=Q.W / 2000, ajustes=ajs)
        caixa |= b.min(axis=2) < 255
    caixa = cv2.dilate(caixa.astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool)
    out = np.where(caixa[..., None], nova, out)
    print(f"    entrada: a seta de y = {SETA_TER_E_ANTES[1]} para y = {SETA_TER_E[1]} px (em frente à porta pivotante); "
          f"o rótulo do hall fora do X tracejado ({int(caixa.sum())} px refeitos)")
    return out


# A borda de baixo da laje da varanda, reta (usuário, 28/10/26: "não existe esse dente. o tracejado é em linha reta"): no
# retoque (`retoque_terreo_casae.PROJECOES`, o L), a linha de baixo seguia a borda da varanda do 1º Pavimento (a
# ARQ_CONTRAPISO dele, em 1694,1 pt) até 1204,5 pt e, dali até a fachada da sala, a face da parede da suíte 3 (1688,5 pt),
# com o degrau de 10 cm entre as duas. A projeção é a borda da laje, uma linha só, em 1694,1 pt:
# - o trecho da direita e o degrau saem: o retângulo deles (de `meia_px` acima da linha antiga a `meia_px` abaixo da nova,
#   de 1204,5 pt até a planta do canto) recebe o piso de `desvio_px` acima, com as emendas de cima e de baixo esfumadas;
# - os traços seguem retos até 1380 pt no ritmo do trecho da esquerda (o retoque começava cada linha num traço: de 983,4
#   pt, traço de 8,5 pt e vão de 4,25 pt), no molde dele: a média dos traços inteiros do trecho da esquerda (o quanto cada
#   px vai para o cinza dos traços, sobre o piso de logo acima e logo abaixo), na mesma fase. A planta do canto fica por
#   cima.
DENTE_VARANDA_TE = {"y_pt": 1694.13, "y_antes_pt": 1688.46, "x_pt": (983.38, 1204.48, 1380.0), "traco_pt": 8.5,
                    "vao_pt": 4.25, "meia_px": 4, "cor": (150, 151, 150), "desvio_px": 16, "suave_px": 2, "poupa_px": 14}


def dente_varanda_te(Q, img, q=None):
    q = q or DENTE_VARANDA_TE
    x0p, xdp, xfp = q["x_pt"]
    px_pt = Q.p2q(100, 0)[0] - Q.p2q(0, 0)[0]
    px_pt /= 100
    (xi, yn), (xd, ya), (xf, _) = Q.p2q(x0p, q["y_pt"]), Q.p2q(xdp, q["y_antes_pt"]), Q.p2q(xfp, q["y_pt"])
    mp, dv, cor = q["meia_px"], q["desvio_px"], np.float32(q["cor"])
    per, tr = (q["traco_pt"] + q["vao_pt"]) * px_pt, q["traco_pt"] * px_pt
    X0, X1 = int(np.floor(xi)) - 2, int(np.ceil(xf)) + 4
    Y0, Y1 = int(np.floor(ya)) - mp - dv - 4, int(np.ceil(yn)) + mp + 8
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    h, w = reg.shape[:2]
    planta = cv2.dilate(_verde(img[Y0:Y1, X0:X1]).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    # o molde dos traços, do trecho da esquerda: o alfa sobre o piso (a média das linhas logo acima e logo abaixo)
    yn_, xi_, xd_ = yn - Y0, xi - X0, xd - X0
    r0, r1 = int(np.floor(yn_)) - mp, int(np.ceil(yn_)) + mp + 1
    piso = 0.5 * (reg[r0 - 6:r0 - 1].mean(axis=0) + reg[r1 + 1:r1 + 6].mean(axis=0))
    alfa = np.clip(((piso[None] - reg[r0:r1]) / np.maximum(piso[None] - cor, 1)).mean(axis=2), 0, 1)
    n = int((xd_ - xi_ - tr) // per) + 1                         # os traços inteiros do trecho da esquerda
    t = np.arange(-2.0, per - 2.0, 0.25)
    molde = np.mean([np.array([np.interp(xi_ + k * per + t, np.arange(w), alfa[j]) for j in range(r1 - r0)])
                     for k in range(n)], axis=0)                 # (linhas, fase)
    # o retângulo do trecho da direita e do degrau, limpo com o piso de `desvio_px` acima
    ya_ = ya - Y0
    c0 = int(np.floor(xd_)) - 1
    l0, l1 = int(np.floor(ya_)) - mp, r1
    fonte = reg[l0 - dv:l1 - dv, c0:]
    lim = reg.copy()
    m = np.ones((l1 - l0, w - c0), np.float32)
    s_ = q["suave_px"]
    for k in range(s_):
        m[k] = m[-1 - k] = (k + 1) / (s_ + 1)
    # a planta do canto e a sombra dela ficam (a folga `poupa_px` em volta das folhas), com a emenda esfumada
    k = 2 * q["poupa_px"] + 1
    poupa = cv2.dilate(planta.astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool)
    m = m * ~(poupa[l0:l1, c0:] | poupa[l0 - dv:l1 - dv, c0:])
    m = np.minimum(m, cv2.GaussianBlur(m, (0, 0), 1.5))
    lim[l0:l1, c0:] = reg[l0:l1, c0:] * (1 - m[..., None]) + fonte * m[..., None]
    # os traços da direita: o molde na fase do trecho da esquerda, do fim dele até 1380 pt
    xs = np.arange(w, dtype=np.float32)
    fase = (xs - xi_) % per
    k_ = np.floor((xs - xi_) / per)
    fim = xf - X0
    a = np.zeros((h, w), np.float32)
    for j in range(r1 - r0):
        v = np.interp(fase, t, molde[j], period=None)
        v = np.where(fase > per - 2.0, np.interp(fase - per, t, molde[j]), v)
        ini = xs + 0.5 >= xd_
        dentro = ini & (xi_ + k_ * per + 0.0 <= fim)
        v = np.where(dentro, v, 0)
        v = np.where(xs > fim + 1, 0, v)
        a[r0 + j] = v
    a *= ~planta
    out = lim * (1 - a[..., None]) + cor * a[..., None]
    res = img.copy()
    res[Y0:Y1, X0:X1] = np.clip(np.round(out), 0, 255).astype(np.uint8)
    print(f"    varanda: a borda de baixo da laje reta em {q['y_pt']} pt, no molde de {n} traços do trecho da esquerda "
          f"(o trecho da direita desceu {yn - ya:.1f} px; o degrau saiu)")
    return res


def revisao_terreo_e(Q, img):
    """Os itens da revisão de 28/10; a projeção da cobertura (item 4) vai em preto ou branco na etapa `tracejados`."""
    out = adega_porta_te(Q, img)
    out = pisantes_te(Q, out)
    out = curva_pedra_te(Q, out)
    return dente_varanda_te(Q, out)


# Os tracejados do Térreo em preto ou branco pelo fundo (usuário, 28/10/26, vendo a borda reta da varanda: "os tracejados
# são ou brancos ou pretos, a depender do fundo"; a R8 de 26/10, como nas Casas A e B, `final3840_casaa_terreo.PROJ`):
# antes, todos em cinza (o do retoque, ampliado de 2000 px, e o da revisão de 28/10 no granito). Agora, nítidos (1,5 px),
# por cima do cinza antigo, nos mesmos traços:
# - as projeções da cobertura do retoque (`retoque_terreo_casae.PROJECOES`), com a borda de baixo da varanda reta
#   (`DENTE_VARANDA_TE`): o L da laje do espaço gourmet + varanda, a laje da garagem e a faixa de cima; traço de 8,5 pt e
#   vão de 4,25 pt, cada trecho começando num traço;
# - as cadeias tracejadas da DOC_LINHAS E PROJEÇÕES (o X do hall com a linha da esquerda; o X da área de serviço
#   descoberta com a linha de cima); as linhas do lote (mais longas que `max_doc_pt`) e o que fica fora dele (acima de
#   `topo_q`) não;
# - nada sobre as paredes: o traço com o meio numa parede do PDF (com `folga_px`) sai, e as paredes voltam por cima;
# - a cor traço a traço, como nas Casas A e B: preto se o fundo em volta (a mediana da luminância numa faixa de
#   `fundo_px`, sem o traço e sem as paredes) passa de `limiar`, branco se não; o fundo de cada traço vai com o dos
#   vizinhos da mesma reta (a mediana de 5), para a cor trocar onde o piso troca (a borda de cima, do Bege Bahia do
#   gourmet para o granito) sem piscar nos traços sobre a divisa de dois fundos.
TRACEJADOS_TE = {"cobertura": {"L: laje do espaço gourmet + varanda": [(1372.9, 518.6), (697.6, 518.6), (697.6, 1090.3),
                                                                     (983.4, 1090.3), (983.4, 1694.13), (1380.0, 1694.13)],
                               "laje da garagem": [(1992.5, 687.8), (2763.5, 687.8), (2763.5, 1090.3), (2207.9, 1090.3)],
                               "faixa de cima": [(1372.9, 516.3), (2763.5, 516.3), (2763.5, 687.8)]},
                 "traco_pt": 8.5, "vao_pt": 4.25, "max_doc_pt": 900, "topo_q": 100, "min_ext_pt": 30, "folga_px": 1,
                 "larg_px": 1.5, "fundo_px": 9, "limiar": 120, "preto": (30, 30, 30), "branco": (250, 250, 250), "ss": 4,
                 # o vão embaixo dos rótulos que caem no tracejado: o bloco do texto + `folga_px`; os traços param na
                 # borda dele (os pedaços com menos de `min_px` saem), e os px das linhas que já estavam ali (`limpa_px`
                 # de cada lado; os cinza do retoque ou os já em preto e branco) ganham o piso ao lado: o mesmo px
                 # deslocado (o primeiro de `deslocs` que cai no granito, fora das linhas e das paredes)
                 "vaos": {"rotulos": (ROTULO_SERVICO_TE[0],), "folga_px": 8, "min_px": 3, "limpa_px": 3,
                          "deslocs": [(0, 8), (0, -8), (0, 12), (0, -12), (0, 16), (0, -16), (0, 22), (0, -22),
                                      (22, 0), (-22, 0), (6, 6), (-6, -6), (6, -6), (-6, 6)]}}


def _tracos_te(Q, q=None):
    """Os trechos tracejados do Térreo: [(nome, [traços (x0, y0, x1, y1) em pt])]."""
    import final3840_casaa_terreo as FT
    q = q or TRACEJADOS_TE
    trechos = []
    for nome, pts in q["cobertura"].items():
        for i, ((ax, ay), (bx, by)) in enumerate(zip(pts[:-1], pts[1:])):
            comp, t, tr = np.hypot(bx - ax, by - ay), 0.0, []
            while t < comp:
                t1 = min(comp, t + q["traco_pt"])
                tr.append((ax + (bx - ax) * t / comp, ay + (by - ay) * t / comp,
                           ax + (bx - ax) * t1 / comp, ay + (by - ay) * t1 / comp))
                t = t1 + q["vao_pt"]
            trechos.append((f"{nome} ({i + 1})", tr))
    doc = FT.cadeias_tracejadas(Q, ["DOC_LINHAS E PROJEÇÕES"], min_ext=q["min_ext_pt"])
    for k, ext, segs in doc:
        tot = sum(e for k2, e, _ in doc if k2[1] == k[1] and abs(k2[2] - k[2]) <= 2)
        if tot > q["max_doc_pt"] or min(Q.p2q(x0, y0)[1] for x0, y0, _, _ in segs) < q["topo_q"]:
            continue
        trechos.append((f"DOC {k[1]:.1f}°", segs))
    return trechos


def _fora_das_caixas(p0, p1, caixas, min_px):
    """As partes do segmento p0-p1 (px) fora das caixas (x0, y0, x1, y1), com pelo menos `min_px`."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    partes = [(0.0, 1.0)]
    for x0, y0, x1, y1 in caixas:
        t0, t1 = 0.0, 1.0                                   # o trecho dentro da caixa (Liang-Barsky)
        for p, d in ((-dx, p0[0] - x0), (dx, x1 - p0[0]), (-dy, p0[1] - y0), (dy, y1 - p0[1])):
            if p == 0:
                if d < 0:
                    t0, t1 = 1.0, 0.0
            elif p < 0:
                t0 = max(t0, d / p)
            else:
                t1 = min(t1, d / p)
        if t0 >= t1:
            continue
        partes = [r for a, b in partes for r in ([(a, b)] if b <= t0 or a >= t1 else
                                                 [x for x in ((a, t0), (t1, b)) if x[1] > x[0]])]
    comp = np.hypot(dx, dy)
    return [((p0[0] + dx * a, p0[1] + dy * a), (p0[0] + dx * b, p0[1] + dy * b)) for a, b in partes
            if (b - a) * comp >= min_px]


def _vaos_te(Q, q=None):
    """As caixas (px da final) dos vãos do tracejado embaixo dos rótulos de `q["vaos"]`, no pavimento dela."""
    v = (q or TRACEJADOS_TE)["vaos"]
    f = v["folga_px"]
    return [(x0 - f, y0 - f, x1 + f, y1 + f)
            for x0, y0, x1, y1 in caixas_rotulos(v.get("pavimento", "Terreo"), v["rotulos"])]


def _limpa_tracos(Q, img, caixas, extra=None, q=None, trechos=None, fonte=None, so_em=None, mesmo=None):
    """Tira das caixas os traços que já estão na imagem: os px das linhas tracejadas (`limpa_px` de cada lado, os vãos
    entre os traços incluídos) e os de `extra` ganham o piso ao lado, o mesmo px deslocado (`deslocs`), tirado de
    `fonte` (máscara; o padrão é o granito do Térreo). `trechos`: as linhas (o padrão são as do Térreo); `so_em`: só
    os px dessa máscara mudam; `mesmo`: o px de fonte tem o mesmo valor desse mapa que o px refeito (o material)."""
    import retoque_terreo_casae as T
    q = q or TRACEJADOS_TE
    v = q["vaos"]
    H, W = img.shape[:2]
    paredes_pdf(Q)
    lin = np.zeros((H, W), np.uint8)
    for _, tracos in (_tracos_te(Q, q) if trechos is None else trechos):
        for t in tracos:
            (u0, v0), (u1, v1) = Q.p2q(t[0], t[1]), Q.p2q(t[2], t[3])
            c = np.hypot(u1 - u0, v1 - v0)
            if c < 1e-6:
                continue
            e = q["vao_pt"] * Q.p2q(1, 0)[0] - q["vao_pt"] * Q.p2q(0, 0)[0]
            ex, ey = (u1 - u0) / c * e, (v1 - v0) / c * e
            cv2.line(lin, (int(round(u0 - ex)), int(round(v0 - ey))), (int(round(u1 + ex)), int(round(v1 + ey))), 1, 1)
    r = v["limpa_px"]
    linhas = cv2.dilate(lin, np.ones((2 * r + 1, 2 * r + 1), np.uint8)).astype(bool)
    dentro = np.zeros((H, W), bool)
    for x0, y0, x1, y1 in caixas:
        dentro[max(int(y0), 0):min(int(np.ceil(y1)), H), max(int(x0), 0):min(int(np.ceil(x1)), W)] = True
    par = cv2.dilate((Q._par > 0.3).astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    if fonte is None:
        fonte = np.abs(Q.chapada.astype(int) - np.array(T.ARCOS["granito"])).max(axis=2) <= 6
    alvo = (linhas | (extra if extra is not None else False)) & dentro & ~par
    if so_em is not None:
        alvo &= so_em
    fonte = fonte & ~par & ~cv2.dilate(linhas.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool) & ~alvo
    if extra is not None:
        fonte &= ~extra
    out = img.copy()
    falta = alvo.copy()

    def valido(ys, xs, dx, dy):
        sy, sx = ys + dy, xs + dx
        ok = (sy >= 0) & (sy < H) & (sx >= 0) & (sx < W)
        ok[ok] = fonte[sy[ok], sx[ok]]
        if mesmo is not None:
            ok[ok] = mesmo[sy[ok], sx[ok]] == mesmo[ys[ok], xs[ok]]
        return ok
    # `media`: primeiro a média dos dois lados (o px deslocado para um lado e para o outro), que segue o degradê do fundo
    if v.get("media"):
        for dx, dy in v["deslocs"]:
            ys, xs = np.nonzero(falta)
            ok = valido(ys, xs, dx, dy) & valido(ys, xs, -dx, -dy)
            ys, xs = ys[ok], xs[ok]
            out[ys, xs] = ((img[ys + dy, xs + dx].astype(np.uint16) + img[ys - dy, xs - dx]) // 2).astype(np.uint8)
            falta[ys, xs] = False
    # `so_media`: sem a cópia de um lado só; o que sobra vai ao inpaint (no fundo liso, o nublado dos vazios)
    for dx, dy in ([] if v.get("so_media") else v["deslocs"]):
        ys, xs = np.nonzero(falta)
        ok = valido(ys, xs, dx, dy)
        out[ys[ok], xs[ok]] = img[ys[ok] + dy, xs[ok] + dx]
        falta[ys[ok], xs[ok]] = False
    if falta.any():
        out = cv2.inpaint(out, falta.astype(np.uint8), 3, cv2.INPAINT_TELEA)
    print(f"    vão do tracejado: {int(alvo.sum())} px dos traços (e das letras) refeitos com o piso ao lado "
          f"({int(falta.sum())} pelos vizinhos)")
    return out


def tracejados_pb_te(Q, img, q=None, vaos=True, trechos=None):
    """`vaos`: os traços param em volta dos rótulos de `q["vaos"]` (o que já estava ali sai). `trechos`: os traços (pt)
    a desenhar, [(nome, [(x0, y0, x1, y1)])], no lugar dos do Térreo (aí a limpeza é de quem chama)."""
    q = q or TRACEJADOS_TE
    paredes_pdf(Q)
    caixas = _vaos_te(Q, q) if vaos else []
    if caixas and trechos is None:
        img = _limpa_tracos(Q, img, caixas, q=q)
    k = 2 * q["folga_px"] + 1
    pe = cv2.dilate((Q._par > 0.3).astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool)
    lum = img.astype(np.float32).mean(axis=2)
    out = img.astype(np.float32)
    S, fp = q["ss"], q["fundo_px"]
    n_p = n_b = n_fora = n_vao = 0
    for nome, tracos in (_tracos_te(Q, q) if trechos is None else trechos):
        fica = []
        for t in tracos:
            (u0, v0), (u1, v1) = Q.p2q(t[0], t[1]), Q.p2q(t[2], t[3])
            if pe[int((v0 + v1) / 2), int((u0 + u1) / 2)]:
                n_fora += 1
                continue
            partes = _fora_das_caixas((u0, v0), (u1, v1), caixas, q["vaos"]["min_px"]) if caixas else \
                [((u0, v0), (u1, v1))]
            n_vao += len(partes) != 1 or partes[0] != ((u0, v0), (u1, v1))
            fica += partes
        if not fica:
            continue
        alfas, fundos = [], []
        for (u0, v0), (u1, v1) in fica:
            bx0, by0 = max(int(min(u0, u1)) - fp, 0), max(int(min(v0, v1)) - fp, 0)
            bx1, by1 = min(int(max(u0, u1)) + fp + 2, Q.W), min(int(max(v0, v1)) + fp + 2, Q.H)
            m = np.zeros(((by1 - by0) * S, (bx1 - bx0) * S), np.uint8)
            cv2.line(m, (int(round((u0 - bx0) * S)), int(round((v0 - by0) * S))),
                     (int(round((u1 - bx0) * S)), int(round((v1 - by0) * S))), 255,
                     max(1, int(round(q["larg_px"] * S))), cv2.LINE_AA)
            a = cv2.resize(m.astype(np.float32) / 255, (bx1 - bx0, by1 - by0), interpolation=cv2.INTER_AREA)
            f = lum[by0:by1, bx0:bx1][(a < 0.02) & ~pe[by0:by1, bx0:bx1]]
            alfas.append((a, bx0, by0, bx1, by1))
            fundos.append(np.median(f) if f.size else 255.0)
        # o fundo de cada traço com o dos vizinhos (mediana de 5): a cor troca onde o piso troca, sem piscar
        fundos = np.array(fundos)
        viz = np.array([np.median(fundos[max(i - 2, 0):i + 3]) for i in range(len(fundos))])
        for (a, bx0, by0, bx1, by1), fv in zip(alfas, viz):
            claro = fv >= q["limiar"]
            cor = np.float32(q["preto"] if claro else q["branco"])
            n_p, n_b = n_p + claro, n_b + (not claro)
            out[by0:by1, bx0:bx1] = out[by0:by1, bx0:bx1] * (1 - a[..., None]) + cor * a[..., None]
    out = np.clip(np.round(out), 0, 255).astype(np.uint8)
    par = Q._par > 0.5
    out[par] = img[par]
    print(f"    tracejados (R8): {n_p} traços em preto (fundo claro) e {n_b} em branco (fundo escuro); {n_fora} sobre "
          f"paredes ficam fora; {n_vao} cortados ou fora no vão dos rótulos")
    return out


def tracejados_sobre_final_te(Q, img):
    """Sobre a final do Térreo: sai o cinza da projeção da revisão de 28/10 (a composição desfeita, pelo alfa dele), a
    borda de baixo da varanda fica reta, e os tracejados vão em preto ou branco por baixo dos rótulos (a final sem eles,
    os traços, os rótulos de novo; na final, só a faixa dos traços)."""
    a, X0, Y0, _ = _alfa_projecao_te(Q)
    h, w = a.shape
    reg = img[Y0:Y0 + h, X0:X0 + w].astype(np.float32)
    cor = np.float32(REVISAO_TE["projecao"]["cor"])
    base = img.copy()
    base[Y0:Y0 + h, X0:X0 + w] = np.clip(np.round((reg - cor * a[..., None]) / (1 - a[..., None])), 0,
                                         255).astype(np.uint8)
    base = dente_varanda_te(Q, base)
    # como no dia (o vão e o rótulo da área de serviço vêm depois, em `vao_rotulo_servico_te`)
    sem = (ROTULO_SERVICO_TE[0],)
    limpa, _ = sem_rotulos("Terreo", base, novos=True, sem_ajustes=sem)
    com = tracejados_pb_te(Q, limpa, vaos=False)
    nova = escrever_rotulos("Terreo", com, sem_ajustes=sem)
    faixa = cv2.dilate((np.abs(com.astype(np.int16) - limpa.astype(np.int16)).max(axis=2) > 0).astype(np.uint8),
                       np.ones((7, 7), np.uint8)).astype(bool)
    out = np.where(faixa[..., None], nova, base)
    print(f"    o cinza da projeção da revisão desfeito ({int((a > 0.01).sum())} px); tracejados em preto ou branco "
          f"({int(faixa.sum())} px refeitos)")
    return out


def vao_rotulo_servico_te(Q, img):
    """Sobre a final do Térreo (depois de `tracejados_final`): o rótulo da ÁREA DE SERVIÇO DESCOBERTA vai ao cruzamento
    do X, e o X se abre em volta dele. A final sem os rótulos (o da área de serviço no lugar de antes); no lugar velho do
    rótulo e no vão, os traços e as letras saem (o piso ao lado, deslocado); os traços voltam, parando no vão, e os
    rótulos, com o da área de serviço no lugar novo. Na final, só essas duas caixas mudam."""
    nome = ROTULO_SERVICO_TE[0]
    x0, y0, x1, y1 = caixas_rotulos("Terreo", [nome], sem_ajustes=(nome,))[0]
    velha = (x0 - 3, y0 - 3, x1 + 3, y1 + 3)
    vaos = _vaos_te(Q)
    limpa, a = sem_rotulos("Terreo", img, novos=True, sem_ajustes=(nome,))
    letras = cv2.dilate((a > 0.8).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    limpa = _limpa_tracos(Q, limpa, [velha] + vaos, extra=letras)
    nova = escrever_rotulos("Terreo", tracejados_pb_te(Q, limpa))
    reg = np.zeros(img.shape[:2], bool)
    for c0, r0, c1, r1 in [velha] + vaos:
        reg[int(r0):int(np.ceil(r1)), int(c0):int(np.ceil(c1))] = True
    out = img.copy()
    out[reg] = nova[reg]
    print(f"    rótulo da área de serviço no cruzamento do X, com o vão em volta ({int(reg.sum())} px refeitos)")
    return out


# As poltronas do living (usuário, 28/10/26: "vamos aplicar essa poltrona da sala íntima do primeiro pavimento da casa e
# em substituição das poltronas a todas as 6 poltronas do terreo"): as 6 bouclé da biblioteca
# (`retoque_terreo_casae.POLTRONAS`: 2 junto à mesa de centro, sobre o tapete, e 4 em X em volta da mesa redonda) dão
# lugar à poltrona da sala íntima do 1º Pavimento, a concha de estofado creme do render, recortada da final dele
# ("modelo": na `caixa`, o estofado claro, luz acima de `lum_min` e R - B abaixo de `rb_max`, fechado pelo envoltório
# convexo, mais a borda sombreada do encosto do lado do vinílico, à direita de `borda_x`; "frente": para onde a abertura
# do assento aponta no recorte). Cada uma vai no centro e no tamanho do PDF (o maior lado), virada para o ponto do PDF (a
# mesa). A bouclé sai antes (a desenhada, como em `retoque_terreo_casae.poltronas`, com `folga_px`), com o halo cinza que
# o retocado deixou em volta, e o buraco recebe o piso limpo de perto (o tapete do tapete, o travertino do travertino).
# Nas 2 sobre o tapete (`no_tapete`, na ordem das bouclé do PDF) sai só a bouclé com `folga_tapete_px` (o disco pegava
# o travertino de fora do tapete). Nas 4 da mesa redonda sai o disco de `raio_mesa` x tamanho (e o da sombra do motor),
# que vai até o travertino limpo além do halo escuro (o halo acaba a ~1,1 x tamanho), menos a mesa (`mesa_folga_px`);
# a sombra da mesa, que estava junto com os halos, é refeita no piso novo (`mesa_sombra`, a de `POLTRONAS["sombra"]`).
# O buraco é coberto por cópia direta do piso deslocado, com a borda esfumada em `esfuma_px` e a diferença de tom do
# anel corrigida (o clone de Poisson puxava o escuro da mesa e do halo para dentro). No tapete, cada material (o tapete
# entre `tapete_lum`, o travertino acima) vem do seu: o tom pelo desfoque do material limpo em volta e o grão em
# ladrilhos (não há trecho limpo de tapete do tamanho do buraco). A borda do tapete no buraco segue o contorno dele
# (`_borda_tapete`, usuário: "precisa aprimorar o contorno do tapete na parte onde incluimos as poltronas, logo atrás
# dela. seguindo a direção correta e dando a impressão de continuidade"): a distância do centro do tapete à borda,
# direção a direção, vinda das direções vizinhas onde a borda some atrás da poltrona.
# A sombra das poltronas novas é a de `POLTRONAS["sombra"]` mais marcada (`sombra`) e um contato curto em volta
# (`sombra_contato`), para a concha creme não sumir no travertino claro.
POLTRONAS_TE = {"modelo": {"caixa": (2070, 1255, 2175, 1355), "lum_min": 205, "rb_max": 40, "borda_rb": 48,
                           "borda_x": 2118, "frente": (-0.86, 0.51)},
                "bloco_velho": "poltrona_boucle", "raio_mesa": 1.15, "sombra_motor": 0.18, "folga_px": 3,
                "no_tapete": (0, 1), "folga_tapete_px": 6, "mesa_folga_px": 0.5, "esfuma_px": 3,
                "mesa_sombra": {"dx": -0.06, "dy": 0.06, "desfoque": 0.06, "opacidade": 0.35},
                "tapete_lum": (185, 213), "tapete_borda_px": 4, "tapete_folga_px": 15, "passo_graus": 0.5, "raio_max_px": 260,
                "suave_graus": 4, "objeto_claro": 238, "busca_max": 5.0,
                "ladrilho_px": 12, "tom_px": 5,
                "busca": (1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.6, 3.0, 3.5, 4.0, 4.5, 5.0),
                "direcoes": (90, 270, 60, 120, 240, 300, 30, 150, 210, 330, 0, 180),
                "sombra": {"dx": -0.06, "dy": 0.06, "desfoque": 0.07, "opacidade": 0.6},
                "sombra_contato": {"dx": 0.0, "dy": 0.0, "desfoque": 0.03, "opacidade": 0.3}}


def _modelo_poltrona_1p(q=None):
    """A poltrona da sala íntima do 1º Pavimento: (cor BGR float32, alfa) recortados da final."""
    q = (q or POLTRONAS_TE)["modelo"]
    f = cv2.imread(str(CASA / "renders" / PAV_E["1Pavimento"]["final"]))
    x0, y0, x1, y1 = q["caixa"]
    r = f[y0:y1, x0:x1].astype(np.float32)
    lum, rb = r.mean(axis=2), r[..., 2] - r[..., 0]
    m = cv2.morphologyEx(((lum > q["lum_min"]) & (rb < q["rb_max"])).astype(np.uint8), cv2.MORPH_OPEN,
                         np.ones((3, 3), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    comp = (lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))).astype(np.uint8)
    cnts, _ = cv2.findContours(comp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    casca = np.zeros_like(comp)
    cv2.fillPoly(casca, [cv2.convexHull(max(cnts, key=cv2.contourArea))], 1)
    xx = np.arange(x0, x1)[None, :]
    borda = cv2.dilate(casca, np.ones((5, 5), np.uint8)).astype(bool) & (rb < q["borda_rb"]) & (xx > q["borda_x"])
    m = casca.astype(bool) | borda
    # a borda antisserrilhada, com a cor do estofado (sem o tapete ou o vinílico de fundo)
    dentro = cv2.erode(m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    _, rot = cv2.distanceTransformWithLabels((~dentro).astype(np.uint8), cv2.DIST_L2, 5,
                                             labelType=cv2.DIST_LABEL_PIXEL)
    ys, xs = np.nonzero(dentro)
    idx = np.zeros(rot.max() + 1, int)
    idx[rot[ys, xs]] = np.arange(len(ys))
    cor = r.copy()
    fora = ~dentro
    cor[fora] = r[ys[idx[rot[fora]]], xs[idx[rot[fora]]]]
    al = np.clip(cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.6), 0, 1) * (cv2.dilate(
        m.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0)
    yy, xx2 = np.nonzero(al > 0.01)
    return cor[yy.min():yy.max() + 1, xx2.min():xx2.max() + 1], al[yy.min():yy.max() + 1, xx2.min():xx2.max() + 1]


def _girar_peca(cor, al, esc, ang):
    h, w = al.shape
    lado = int(np.ceil(max(h, w) * esc * 1.5)) + 4
    M = cv2.getRotationMatrix2D((w / 2, h / 2), float(ang), esc)
    M[0, 2] += lado / 2 - w / 2
    M[1, 2] += lado / 2 - h / 2
    c2 = cv2.warpAffine(cor * al[..., None], M, (lado, lado), flags=cv2.INTER_AREA)
    a2 = cv2.warpAffine(al, M, (lado, lado), flags=cv2.INTER_AREA)
    return c2 / np.maximum(a2, 1e-4)[..., None], a2


def _melhor_desloc(out, L, m, anel, proibido, q, t):
    """O deslocamento (múltiplos do tamanho `t`, nas direções de `q`) do piso que melhor continua o anel em volta do
    buraco `m`: sem px proibidos, sem px de outra peça (a mais de "objeto" níveis da luz do anel), com o veio vertical do
    travertino pesando contra o deslocamento para os lados (`retoque_terreo_casae.POLTRONAS`)."""
    import retoque_terreo_casae as T
    qt = T.POLTRONAS
    H, W = L.shape
    ya, xa = np.nonzero(anel)
    ym, xm = np.nonzero(m)
    ref = np.median(L[ya, xa])
    melhor = None
    for f in q["busca"]:
        for g in q["direcoes"]:
            ox, oy = int(round(f * t * np.cos(np.radians(g)))), int(round(f * t * np.sin(np.radians(g))))
            if min(xa.min() + ox, ya.min() + oy, xm.min() + ox, ym.min() + oy) < 0 or \
                    max(xa.max(), xm.max()) + ox >= W or max(ya.max(), ym.max()) + oy >= H:
                continue
            if proibido[ym + oy, xm + ox].any() or proibido[ya + oy, xa + ox].any():
                continue
            if (np.abs(L[ym + oy, xm + ox] - ref) > qt["objeto"]).mean() > 0.002:
                continue
            custo = np.abs(out[ya + oy, xa + ox] - out[ya, xa]).mean()
            custo += qt["lateral"] * abs(np.cos(np.radians(g)))
            custo += 400 * (np.abs(L[ym + oy, xm + ox] - ref) > qt["fuga"]).mean()
            if melhor is None or custo < melhor[0]:
                melhor = (custo, ox, oy)
    return melhor[1:]


def _borda_tapete(tap, buracos, xx, yy, q):
    """Onde é tapete junto aos buracos (alfa 0 a 1, com `tapete_borda_px` de transição): o contorno do tapete em volta do
    centro dele (o do maior pedaço de `tap`, já limitado ao tapete do PDF com `tapete_folga_px`), direção a direção (de
    `passo_graus`), é a distância ao último px de tapete
    no raio; onde esse px encosta nos `buracos` (as poltronas na borda do tapete), a distância vem das direções vizinhas
    (interpolada no ângulo, depois um desfoque de `suave_graus`), e a borda segue o contorno, sem o dente da peça velha."""
    n, lab, st, cen = cv2.connectedComponentsWithStats(tap.astype(np.uint8))
    k = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
    cx, cy = cen[k]
    exc = cv2.dilate(buracos.astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool)
    H, W = tap.shape
    angs = np.radians(np.arange(0, 360, q["passo_graus"]))
    rs = np.arange(0, q["raio_max_px"], 0.5)
    X = np.clip(np.round(cx + np.outer(np.cos(angs), rs)).astype(int), 0, W - 1)
    Y = np.clip(np.round(cy + np.outer(np.sin(angs), rs)).astype(int), 0, H - 1)
    no_tap, no_exc = (lab[Y, X] == k), exc[Y, X]
    r_b = np.full(len(angs), np.nan)
    for i in range(len(angs)):
        j = np.nonzero(no_tap[i])[0]
        if len(j) == 0:
            continue
        u = j.max()
        if not no_exc[i, max(u - 8, 0):u + 9].any():
            r_b[i] = rs[u]
    ok = ~np.isnan(r_b)
    th = np.degrees(angs)
    r_i = np.interp(th, th[ok], r_b[ok], period=360)
    f = int(round(q["suave_graus"] / q["passo_graus"]))
    r_s = np.convolve(np.r_[r_i[-f:], r_i, r_i[:f]], np.ones(2 * f + 1) / (2 * f + 1), mode="same")[f:-f]
    r_s = np.where(ok, r_i, r_s)
    t = np.degrees(np.arctan2(yy - cy, xx - cx)) % 360
    raio = np.interp(t, th, r_s, period=360)
    sd = raio - np.hypot(xx - cx, yy - cy)
    return np.clip(sd / q["tapete_borda_px"] + 0.5, 0, 1).astype(np.float32)


def _material_por_ladrilhos(out, buraco, livre, q, t):
    """O piso de um material dentro do `buraco`: o tom (o desfoque de `tom_px` só do material limpo em volta, `livre`)
    mais o grão (o que sobra do desfoque de `grao_px`, 3 px se não dado), copiado em ladrilhos de `ladrilho_px` com meia
    sobreposição, cada um do trecho mais perto em que ele cabe todo em `livre` (até `busca_max` x `t`), somados com janela de Hann."""
    H, W = buraco.shape
    s_ = q["tom_px"]
    lv = livre.astype(np.float32)
    peso_tom = cv2.GaussianBlur(lv, (0, 0), s_)[..., None]
    tom = np.where(peso_tom > 1e-3, cv2.GaussianBlur(out * lv[..., None], (0, 0), s_) / np.maximum(peso_tom, 1e-6), out)
    grao = out - cv2.GaussianBlur(out, (0, 0), q.get("grao_px", 3))
    n = q["ladrilho_px"]
    integ = cv2.integral(livre.astype(np.uint8))
    cabe = (integ[n:, n:] - integ[:-n, n:] - integ[n:, :-n] + integ[:-n, :-n]) == n * n   # caixa n x n em (y, x)
    janela = np.outer(np.hanning(n + 2)[1:-1], np.hanning(n + 2)[1:-1]).astype(np.float32)
    soma = np.zeros_like(out)
    peso = np.zeros((H, W), np.float32)
    ys, xs = np.nonzero(buraco)
    R = int(q["busca_max"] * t)
    for y in range(ys.min() - n // 2, ys.max() + 1, n // 2):
        for x in range(xs.min() - n // 2, xs.max() + 1, n // 2):
            if not buraco[max(y, 0):y + n, max(x, 0):x + n].any():
                continue
            y0, x0 = max(y - R, 0), max(x - R, 0)
            vy, vx = np.nonzero(cabe[y0:y + R, x0:x + R])
            k = np.argmin((vy + y0 - y) ** 2 + (vx + x0 - x) ** 2)
            sy, sx = vy[k] + y0, vx[k] + x0
            soma[y:y + n, x:x + n] += grao[sy:sy + n, sx:sx + n] * janela[..., None]
            peso[y:y + n, x:x + n] += janela
    return tom + soma / np.maximum(peso, 1e-6)[..., None]


def _fonte_tom(out, anel, ox, oy):
    """A imagem deslocada de (ox, oy), com o tom corrigido pela mediana do anel."""
    ya, xa = np.nonzero(anel)
    delta = np.median(out[ya, xa], axis=0) - np.median(out[ya + oy, xa + ox], axis=0)
    return np.roll(out, (-oy, -ox), axis=(0, 1)) + delta, delta


def poltronas_living_te(Q, img, q=None):
    """As 6 bouclé do living trocadas pela poltrona da sala íntima do 1º Pavimento (a imagem sem rótulos)."""
    import retoque_terreo_casae as T
    sys.path.insert(0, str(RAIZ / "_blocos"))
    import blocos
    q = q or POLTRONAS_TE
    qt = T.POLTRONAS
    H, W = img.shape[:2]
    px_m = Q.px_m
    pecas = [(np.float32(Q.p2q(*cen)), np.float32(Q.p2q(*alvo)), tam * px_m) for bid, cen, alvo, tam in qt["pecas"]
             if bid == q["bloco_velho"]]
    out = img.astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    # as bouclé desenhadas (como em `T.poltronas`, na final) e o disco com o halo e a sombra
    cv_, av_ = blocos.bloco(q["bloco_velho"], 100)
    fx, fy = qt["frente"][q["bloco_velho"]]
    # a mesa redonda fica (a sombra dela é refeita no fim)
    prot = np.zeros((H, W), bool)
    mesas = []
    for (px, py), rp in qt["proteger"]:
        (cx_, cy_), (ex_, _) = Q.p2q(px, py), Q.p2q(px + rp, py)
        mesas.append((cx_, cy_, abs(ex_ - cx_)))
        prot |= np.hypot(xx - cx_, yy - cy_) < abs(ex_ - cx_) + q["mesa_folga_px"]
    L = out.mean(axis=2)
    mascaras = []
    for i, (cen, alvo, t) in enumerate(pecas):
        ang = np.degrees(np.arctan2(alvo[0] - cen[0], alvo[1] - cen[1]) - np.arctan2(fx, fy))
        _, a2 = _girar_peca(cv_.astype(np.float32), av_.astype(np.float32), t / max(av_.shape), ang)
        lado = a2.shape[0]
        x0, y0 = int(round(cen[0] - lado / 2)), int(round(cen[1] - lado / 2))
        m = np.zeros((H, W), np.uint8)
        m[y0:y0 + lado, x0:x0 + lado] = (a2 > 0.03).astype(np.uint8)
        k = 2 * (q["folga_tapete_px"] if i in q["no_tapete"] else q["folga_px"]) + 1
        m = cv2.dilate(m, np.ones((k, k), np.uint8)).astype(bool)
        if i not in q["no_tapete"]:
            r, sm = q["raio_mesa"] * t, q["sombra_motor"] * t
            m |= (np.hypot(xx - cen[0], yy - cen[1]) < r) | (np.hypot(xx - cen[0] + sm, yy - cen[1] - sm) < r)
        mascaras.append(m & ~prot)
    e = q["esfuma_px"]
    Lb = cv2.GaussianBlur(L, (0, 0), 3.0)
    lo, hi = q["tapete_lum"]
    tap = cv2.morphologyEx(((Lb > lo) & (Lb < hi)).astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    # o tapete do PDF (o branco dos móveis do estar, as linhas fechadas), com folga: o tapete do render fica dentro
    branco = cv2.dilate(np.all(Q.chapada == 255, axis=2).astype(np.uint8), np.ones((3, 3), np.uint8))
    _, lab_b = cv2.connectedComponents(branco)
    c0 = pecas[q["no_tapete"][0]][0]
    k = 2 * q["tapete_folga_px"] + 1
    no_pdf = cv2.dilate((lab_b == lab_b[int(c0[1]), int(c0[0])]).astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool)
    cober = np.zeros((H, W), np.float32)
    for i, ((cen, alvo, t), m) in enumerate(zip(pecas, mascaras)):
        pend = np.logical_or.reduce(mascaras[i:]) | prot
        anel = cv2.dilate(m.astype(np.uint8), np.ones((2 * e + 5,) * 2, np.uint8)).astype(bool) & ~m & ~pend
        if i not in q["no_tapete"]:
            ox, oy = _melhor_desloc(out, L, m, anel, pend, q, t)
            fonte, delta = _fonte_tom(out, anel, ox, oy)
            print(f"      poltrona {i}: fonte deslocada ({ox}, {oy}), correção de tom {np.round(delta, 1)}")
        else:
            # o tapete e o travertino em volta, cada um do seu material; a borda do tapete no buraco segue o contorno
            # do tapete (`_borda_tapete`)
            a_tap = _borda_tapete(tap.astype(bool) & no_pdf, np.logical_or.reduce(mascaras), xx, yy, q)
            fontes = []
            for nome, mat, parte in (("tapete", tap.astype(bool), a_tap > 0.01),
                                     ("travertino", Lb >= hi, a_tap < 0.99)):
                if not (m & parte).any():
                    fontes.append(out)
                    continue
                livre = cv2.erode(mat.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool) & ~pend
                livre &= (L < q["objeto_claro"]) if nome == "travertino" else True
                fontes.append(_material_por_ladrilhos(out, m & parte, livre, q, t))
                print(f"      poltrona {i}, {nome}: grão em ladrilhos de {q['ladrilho_px']} px, tom do anel")
            fonte = fontes[1] * (1 - a_tap[..., None]) + fontes[0] * a_tap[..., None]
        al = cv2.GaussianBlur(cv2.dilate(m.astype(np.uint8), np.ones((2 * e + 1,) * 2, np.uint8)).astype(np.float32),
                              (0, 0), e / 2)[..., None]
        al[pend[..., None] & ~m[..., None]] = 0
        al[m] = 1
        out = out * (1 - al) + fonte * al
        cober = np.maximum(cober, al[..., 0])
    # a sombra da mesa no piso novo
    for cx_, cy_, rm in mesas:
        sm = q["mesa_sombra"]
        d = np.hypot(xx - cx_ - sm["dx"] * 2 * rm, yy - cy_ - sm["dy"] * 2 * rm)
        a = cv2.GaussianBlur(np.clip(rm + 0.5 - d, 0, 1).astype(np.float32), (0, 0), sm["desfoque"] * 2 * rm)
        a *= sm["opacidade"] * cober * ~prot
        out = out * (1 - a[..., None]) + out * 0.4 * a[..., None]
    # a poltrona da sala íntima, no centro, no tamanho e na direção do PDF, com a sombra curta
    cor, al = _modelo_poltrona_1p(q)
    fx, fy = q["modelo"]["frente"]
    for cen, alvo, t in pecas:
        ang = np.degrees(np.arctan2(alvo[0] - cen[0], alvo[1] - cen[1]) - np.arctan2(fx, fy))
        c2, a2 = _girar_peca(cor, al, t / max(al.shape), ang)
        T.pousar_planta(out, c2, a2, float(cen[0]), float(cen[1]), t, q["sombra"])
        T.pousar_planta(out, c2, a2, float(cen[0]), float(cen[1]), t, q["sombra_contato"])
    print(f"    {len(pecas)} poltronas do living no modelo da sala íntima do 1º Pavimento (as bouclé e o halo saíram)")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def poltronas_living_sobre_final_te(Q, img):
    """Sobre a final do Térreo: a final sem os rótulos, as poltronas trocadas, os rótulos de novo; só a área mudada."""
    limpa, _ = sem_rotulos("Terreo", img, novos=True)
    com = poltronas_living_te(Q, limpa)
    nova = escrever_rotulos("Terreo", com)
    mud = cv2.dilate((np.abs(com.astype(np.int16) - limpa.astype(np.int16)).max(axis=2) > 0).astype(np.uint8),
                     np.ones((5, 5), np.uint8)).astype(bool)
    return np.where(mud[..., None], nova, img)


# O sofá da varanda (usuário, 28/10/26: "você consegue substituir o sofá da varanda da casa e pelo sofá da sala íntima do
# primeiro pavimento, deixando apenas a parte horizontal? teria que remover o último módulo do L para dar certo"): o sofá
# em L da sala íntima, recortado da final do 1º Pavimento ("modelo", px dela), só a parte reta: em cada linha, do primeiro
# ao último px do estofado claro (luz acima de `lum_min`, R - B abaixo de `rb_max`; o vinílico e o tapete ficam fora),
# até a frente dos assentos (`frente_y`); a perna do L sai com o módulo do canto, e no lugar dele vai o módulo da
# direita espelhado, com o braço e as almofadas (usuário: "por que não pegar todo o modulo da direita e espelhar para a
# esquerda, usando as almofadas?"). No Térreo, ele vai no fundo do sofá do PDF (`caixa`, px da final: 1,17 m, o do sofá
# anterior), na mesma proporção, centrado no comprimento (usuário: "pode aumentar o sofá para ter a mesma altura,
# preservando a proporcionalidade"), e depois um pouco menor (`fundo_px`, 1,06 m; usuário: "diminua um pouco o tamanho"),
# com o encosto para cima e a beirada do estofado escurecida em `beirada` até `beirada_px`; a sombra leve, como a das
# poltronas, mais fraca (`sombra`, `sombra_contato`; usuário: "jogue um leve efeito de sombra para mostrar que o sofá
# está integrado ao piso"). O sofá antigo sai com a sombra dele e o halo claro de cima (`buraco`, px da final, com a
# borda esfumada em `esfuma_px`): o Bege Bahia de fora, refletido no lado mais perto do retângulo (nos cantos, os dois
# lados misturados junto à diagonal, em `canto_px`).
SOFA_VARANDA_TE = {"modelo": {"caixa": (1846, 1194, 2076, 1270), "lum_min": 185, "rb_max": 45, "frente_y": 1265.5,
                              "modulo_x": (1986, 2076), "meio_x": (1920, 1986), "meio_borda_px": 5,
                              "nitidez": 0.6},
                   "caixa": (1320, 1236, 1522.5, 1306), "buraco": (1303, 1217, 1538, 1315),
                   "esfuma_px": 2, "canto_px": 1.5, "beirada": 0.12, "beirada_px": 2.0, "fundo_px": 63,
                   "sombra": {"dx": -0.06, "dy": 0.06, "desfoque": 0.07, "opacidade": 0.45},
                   "sombra_contato": {"dx": 0.0, "dy": 0.0, "desfoque": 0.03, "opacidade": 0.3}}


def _modelo_sofa_1p(q=None):
    """A parte reta do sofá da sala íntima do 1º Pavimento: (cor BGR float32, alfa), recortados da final."""
    q = (q or SOFA_VARANDA_TE)["modelo"]
    f = cv2.imread(str(CASA / "renders" / PAV_E["1Pavimento"]["final"]))
    x0, y0, x1, y1 = q["caixa"]
    r = f[y0:y1, x0:x1].astype(np.float32)
    h, w = r.shape[:2]
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    claro = (r.mean(axis=2) > q["lum_min"]) & (r[..., 2] - r[..., 0] < q["rb_max"]) & (yy <= q["frente_y"])
    # cada linha cheia entre o primeiro e o último px claro (o assento do canto, à sombra das almofadas, fica)
    m = np.zeros((h, w), bool)
    for i in np.nonzero(claro.any(axis=1))[0]:
        j = np.nonzero(claro[i])[0]
        m[i, j.min():j.max() + 1] = True
    m = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.0) > 0.5
    # a perna do L sai com o módulo do canto: o módulo da direita (`modulo_x`, da costura ao braço, com as almofadas)
    # vai espelhado na esquerda, e o do meio (`meio_x`, entre as costuras) fica entre os dois; a beirada esquerda dele
    # (`meio_borda_px`, com o brilho da costura e a sombra das almofadas do canto) vem da beirada direita, espelhada
    (r0, r1), (m0, m1) = q["modulo_x"], q["meio_x"]
    meio = r[:, m0 - x0:m1 - x0]
    wb = np.clip((q["meio_borda_px"] + 3 - np.arange(m1 - m0)) / 3, 0, 1)[None, :, None]
    meio = meio * (1 - wb) + meio[:, ::-1] * wb
    r = np.concatenate([r[:, r1 - x0 - 1:r0 - x0 - 1:-1], meio, r[:, r0 - x0:r1 - x0]], axis=1)
    m = np.concatenate([m[:, r1 - x0 - 1:r0 - x0 - 1:-1], m[:, m0 - x0:m1 - x0], m[:, r0 - x0:r1 - x0]], axis=1)
    # a borda antisserrilhada, com a cor do estofado (sem o vinílico ou o tapete de fundo)
    dentro = cv2.erode(m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    _, rot = cv2.distanceTransformWithLabels((~dentro).astype(np.uint8), cv2.DIST_L2, 5,
                                             labelType=cv2.DIST_LABEL_PIXEL)
    ys, xs = np.nonzero(dentro)
    idx = np.zeros(rot.max() + 1, int)
    idx[rot[ys, xs]] = np.arange(len(ys))
    cor = r.copy()
    cor[~dentro] = r[ys[idx[rot[~dentro]]], xs[idx[rot[~dentro]]]]
    al = np.clip(cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.6), 0, 1) * (cv2.dilate(
        m.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0)
    yy2, xx2 = np.nonzero(al > 0.01)
    return cor[yy2.min():yy2.max() + 1, xx2.min():xx2.max() + 1], al[yy2.min():yy2.max() + 1, xx2.min():xx2.max() + 1]


def sofa_varanda_te(Q, img, q=None):
    """O sofá da varanda trocado pela parte reta do sofá da sala íntima do 1º Pavimento (a imagem sem rótulos)."""
    import retoque_terreo_casae as T
    q = q or SOFA_VARANDA_TE
    out = img.astype(np.float32)
    H, W = img.shape[:2]
    bx0, by0, bx1, by1 = q["buraco"]
    buraco = np.zeros((H, W), bool)
    buraco[by0:by1, bx0:bx1] = True
    # o piso de cada px do buraco é o de fora, refletido no lado mais perto do retângulo (as faixas que ficam à vista
    # em volta do sofá novo são estreitas: as manchas da pedra seguem sem emenda; o miolo fica sob o sofá)
    # (junto às diagonais dos cantos, os dois lados se misturam pela diferença de distância, em `canto_px`)
    yy, xx = np.mgrid[by0:by1, bx0:bx1]
    d = np.stack([yy - by0, by1 - 1 - yy, xx - bx0, bx1 - 1 - xx]).astype(np.float32)
    fontes = [out[by0 - 1 - (yy - by0), xx], out[by1 + (by1 - 1 - yy), xx],
              out[yy, bx0 - 1 - (xx - bx0)], out[yy, bx1 + (bx1 - 1 - xx)]]
    w = np.exp(-(d - d.min(axis=0)) / q["canto_px"])
    novo = out.copy()
    novo[by0:by1, bx0:bx1] = sum(f * wk[..., None] for f, wk in zip(fontes, w)) / w.sum(axis=0)[..., None]
    al = cv2.GaussianBlur(cv2.erode(buraco.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(np.float32), (0, 0),
                          q["esfuma_px"])[..., None]
    out = out * (1 - al) + novo * al
    cor, al = _modelo_sofa_1p(q)
    x0, y0, x1, y1 = q["caixa"]
    k = q["fundo_px"] / cor.shape[0]                  # no fundo `fundo_px`, na mesma proporção
    w, h = int(round(cor.shape[1] * k)), int(round(cor.shape[0] * k))
    c2 = cv2.resize(cor * al[..., None], (w, h), interpolation=cv2.INTER_AREA)
    a2 = np.clip(cv2.resize(al, (w, h), interpolation=cv2.INTER_AREA), 0, 1)
    c2 = c2 / np.maximum(a2, 1e-4)[..., None]
    c2 = c2 + q["modelo"]["nitidez"] * (c2 - cv2.GaussianBlur(c2, (0, 0), 1.0))
    # a beirada do estofado um pouco mais escura (`beirada`, até `beirada_px` para dentro): o contorno sem sombra no piso
    dd = cv2.distanceTransform((a2 > 0.5).astype(np.uint8), cv2.DIST_L2, 3)
    c2 *= 1 - q["beirada"] * np.clip((q["beirada_px"] - dd) / q["beirada_px"], 0, 1)[..., None]
    # o encosto na linha de trás do PDF, centrado no comprimento do PDF, com a sombra leve das poltronas (`sombra` e
    # `sombra_contato`, medidas em fração do fundo do sofá)
    # (com uma margem em volta, para o desfoque da sombra não ser cortado na caixa do sofá)
    px, py = int(round((x0 + x1) / 2 - w / 2)), int(round(y0))
    mg = int(np.ceil(h * 0.3))
    c2 = np.pad(np.clip(c2, 0, 255), ((mg, mg), (mg, mg), (0, 0)), mode="edge")
    a2 = np.pad(a2, mg)
    for sb in (q["sombra"], q["sombra_contato"]):
        T.pousar_planta(out, c2, a2, px + w / 2, py + h / 2, h, sb)
    print(f"    sofá da varanda: a parte reta do sofá da sala íntima ({cor.shape[1]} x {cor.shape[0]} px) no "
          f"fundo de {h} px ({w} x {h} px: {w / Q.px_m:.2f} x {h / Q.px_m:.2f} m), com a sombra leve")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def sofa_varanda_sobre_final_te(Q, img):
    """Sobre a final do Térreo: a final sem os rótulos, o sofá trocado, os rótulos de novo; só a área mudada."""
    limpa, _ = sem_rotulos("Terreo", img, novos=True)
    com = sofa_varanda_te(Q, limpa)
    nova = escrever_rotulos("Terreo", com)
    mud = cv2.dilate((np.abs(com.astype(np.int16) - limpa.astype(np.int16)).max(axis=2) > 0).astype(np.uint8),
                     np.ones((5, 5), np.uint8)).astype(bool)
    return np.where(mud[..., None], nova, img)


def nublado_tracejados_te(Q, img):
    """Sobre a final do 1º Pavimento: o Térreo nublado sem as projeções do Térreo (como no 1º Pavimento da Casa A): sai
    o tracejado cinza da revisão de 28/10 que tinha entrado no nublado, e a borda de baixo da varanda fica reta, pela
    diferença entre a fonte do nublado em cache e ela sem esse tracejado e com a borda reta (que fica no cache)."""
    QT = QuadroE("Terreo")
    c = ETAPAS / "Terreo_nublado_fonte.png"
    antes = cv2.imread(str(c))
    a, X0, Y0, _ = _alfa_projecao_te(QT)
    h, w = a.shape
    reg = antes[Y0:Y0 + h, X0:X0 + w].astype(np.float32)
    cor = np.float32(REVISAO_TE["projecao"]["cor"])
    depois = antes.copy()
    depois[Y0:Y0 + h, X0:X0 + w] = np.clip(np.round((reg - cor * a[..., None]) / (1 - a[..., None])), 0,
                                           255).astype(np.uint8)
    depois = dente_varanda_te(QT, depois)
    out, _, _ = _trocar_nublado(Q, img, _nublar(antes, Q.W), _nublar(depois, Q.W))
    cv2.imwrite(str(c), depois)
    mud = (np.abs(out.astype(np.int16) - img.astype(np.int16)).max(axis=2) > 2).sum()
    print(f"    o Térreo nublado sem o tracejado cinza da revisão e com a borda da varanda reta: {int(mud)} px mudados")
    return out


# O 1º Pavimento (auditoria de 26/10, mapa `renders/POE642_CasaE_PH_1Pavimento_auditoria_2610.jpg`, e as regras aprovadas
# no 1º Pavimento da Casa A):
# 1. o Térreo nublado em volta refeito a partir do Térreo novo desta rodada (as paredes em cinza 80, o granito, as escadas),
#    sem as letras das escadas, a seta e os rótulos (`terreo_para_nublado`), no mesmo nublado (`entorno_esmaecido.NUBLADO`:
#    70% de branco, 80% da saturação, desfoque leve); só onde a final mostra o Térreo (fora da pegada do 1º Pavimento e
#    nos vazios, onde o X e o vidro ficam por cima);
# 2. E11: o vinílico (suítes, closets, circulação, sala íntima) nas réguas das Casas B a D na resolução da prancha (vinha
#    do retocado de 2000 px, ampliado);
# 3. E3, E8: a escada interna sem as linhas e sem o triângulo: o trecho do 1º Pavimento (à esquerda) com o sombreamento
#    de descida para a direita, o trecho depois do corte (os degraus do Térreo, à direita) nevoado e o D do PDF no degrau
#    de cima, à esquerda (onde estava o triângulo);
# 4. E9: as bancadas dos banhos master, 1, 2, 3 e 4 (claras sobre o porcelanato claro) com a borda no tom escurecido da
#    pedra e a sombra curta;
# 5. E10: as paredes em cinza 80 (não há pilares no 1º Pavimento).
PISOS_1PAV_E = [("vinílico", [(79, 120, 168)], "vinilico", None, 1.0, 2821, None)]
# a mesinha redonda de madeira ao lado do sofá da sala íntima (da final aprovada; o PDF não a desenha) tem a cor do
# vinílico e saía com o piso
FICAM_1PAV_E = [(2097.5, 1222.0, 17.5)]
ESCADA_1PAV_E = dict(ESCADAS_TER_E[1], nome="interna", apos="direita", letra="D", letra_no_alto=True, semente=2822)
BANCADAS_1PAV_E = [("banho master", (1692.9, 655.9, 1726.1, 789.6)), ("banho 1", (2120.1, 1113.0, 2194.4, 1148.0)),
                   ("banho 2", (2120.1, 764.4, 2194.4, 799.3)), ("banho 3", (1330.5, 1339.6, 1402.9, 1371.0)),
                   ("banho 4", (1330.5, 1382.3, 1402.9, 1413.7))]


def terreo_para_nublado():
    """O Térreo novo sem as letras das escadas, a seta e os rótulos: as etapas do Térreo de novo a partir dos pisos, com
    as letras desligadas e a piscina no turquesa (em cache)."""
    c = ETAPAS / "Terreo_nublado_fonte.png"
    if c.exists():
        return cv2.imread(str(c))
    QT = QuadroE("Terreo")
    pisos = ETAPAS / "Terreo_pisos.png"
    img = cv2.imread(str(pisos)) if pisos.exists() else final_3840("Terreo", ate="pisos", salvar=False)
    sem = [dict(e, letra=None) for e in ESCADAS_TER_E]
    img = blocos_e(QT, escada_e(QT, escada_e(QT, img, sem[0]), sem[1]), dict(BLOCOS_TER_E, letra=None))
    img = armario_cabides(QT, img, ARMARIO_DCE_TER_E["pt"], ARMARIO_DCE_TER_E["lado"], nome="DCE")
    img = boxes_terreo_e(QT, img)
    img = _bancadas(QT, img, BANCADAS_TER_E)
    img = paredes_e(QT, img)
    img = piscina_terreo_e(QT, img)
    img = revisao_terreo_e(QT, img)       # a revisão de 28/10 (adega, pisantes, curva, varanda; sem as projeções)
    img = poltronas_living_te(QT, img)    # as poltronas do living no modelo da sala íntima (28/10)
    img = sofa_varanda_te(QT, img)        # o sofá da varanda, a parte reta do sofá da sala íntima (28/10)
    cv2.imwrite(str(c), img)
    return img


def _nublar(t, W):
    """O Térreo no nublado do 1º Pavimento (`entorno_esmaecido.NUBLADO`: desfoque leve, 80% da saturação, 70% de branco)."""
    from entorno_esmaecido import NUBLADO as n
    t = cv2.GaussianBlur(t.astype(np.float32), (0, 0), n["desfoque"] * W / 3840)
    cinza = t.mean(axis=2, keepdims=True)
    t = cinza + (t - cinza) * n["saturacao"]
    return 255 - (255 - t) * (1 - n["clarear"])


def _onde_terreo(Q):
    """Onde a final do 1º Pavimento mostra o Térreo: o contexto (fora da pegada, sem o tracejado do lote; 0 a 1) e os
    vazios (bool), onde o contexto vem multiplicado pelo X e pelo vidro."""
    import opcoes_1pav_casae as O
    from entorno_esmaecido import pegada
    W = Q.W
    base = cv2.imread(str(O.BASE_CIMA))
    H = round(base.shape[0] * W / base.shape[1])
    base = cv2.resize(base, (W, H), interpolation=cv2.INTER_AREA)
    peg = pegada(base, O.FORA)
    a = np.maximum(cv2.GaussianBlur(peg.astype(np.float32), (0, 0), 1.0), peg)
    tracejado = (base.min(axis=2) < 225) & ~peg
    return (1 - a) * ~tracejado, O.mascara_vazios(base) & (a > 0.5)


def _trocar_nublado(Q, img, t_velho, t_novo):
    f = img.astype(np.float32)
    ctx, vaz = _onde_terreo(Q)
    out = f + (t_novo - t_velho) * ctx[..., None]
    raz = t_novo / np.maximum(t_velho, 1)
    out[vaz] = (f * raz)[vaz]
    return np.clip(np.round(out), 0, 255).astype(np.uint8), ctx, vaz


def nublado_novo(Q, img):
    """Troca o Térreo nublado da final (o do retocado de 2000 px, `opcoes_1pav_casae.TERREO`) pelo do Térreo novo, onde a
    final mostra o Térreo: fora da pegada (o px é o contexto antigo) e nos vazios (o contexto multiplicado pelo X e pelo
    vidro: entra a razão novo/antigo)."""
    import opcoes_1pav_casae as O
    from entorno_esmaecido import NUBLADO, contexto_render
    t_velho = contexto_render(O.TERREO, O.BASE_TERREO, Q.W, **NUBLADO)
    out, ctx, vaz = _trocar_nublado(Q, img, t_velho, _nublar(terreo_para_nublado(), Q.W))
    print(f"    o Térreo nublado em volta refeito com o Térreo novo: {int((ctx > 0.5).sum())} px de contexto e "
          f"{int(vaz.sum())} px nos vazios")
    return out


def nublado_revisao_te(Q, img):
    """Sobre a final do 1º Pavimento: o nublado passa a mostrar a revisão de 28/10 do Térreo (os pisantes, a curva da
    pedra portuguesa, o tracejado da projeção; a adega fica sob a pegada). Entra só a diferença entre a fonte do nublado
    em cache (sem a revisão) e ela com a revisão, que fica no cache."""
    c = ETAPAS / "Terreo_nublado_fonte.png"
    antes = cv2.imread(str(c))
    depois = revisao_terreo_e(QuadroE("Terreo"), antes)
    out, ctx, _ = _trocar_nublado(Q, img, _nublar(antes, Q.W), _nublar(depois, Q.W))
    cv2.imwrite(str(c), depois)
    mud = (np.abs(out.astype(np.int16) - img.astype(np.int16)).max(axis=2) > 2).sum()
    print(f"    o Térreo nublado com a revisão de 28/10 do Térreo: {int(mud)} px mudados")
    return out


def nublado_poltronas_te(Q, img):
    """Sobre a final do 1º Pavimento (usuário, 28/10/26: "pode refazer o nublado"): o Térreo nublado passa a mostrar as
    poltronas novas do living (`poltronas_living_te`), no lugar das bouclé. Entra só a diferença entre a fonte do nublado
    em cache e ela com as poltronas trocadas, que fica no cache."""
    c = ETAPAS / "Terreo_nublado_fonte.png"
    antes = cv2.imread(str(c))
    depois = poltronas_living_te(QuadroE("Terreo"), antes)
    out, _, _ = _trocar_nublado(Q, img, _nublar(antes, Q.W), _nublar(depois, Q.W))
    cv2.imwrite(str(c), depois)
    mud = (np.abs(out.astype(np.int16) - img.astype(np.int16)).max(axis=2) > 2).sum()
    print(f"    o Térreo nublado com as poltronas novas do living: {int(mud)} px mudados")
    return out


# Os traços do render no Bege Bahia da varanda grande, rente aos guarda-corpos (usuário, 28/10/26: "CORRIJA ESSES
# RESQUICIOS NO PISO, RENTE AO GUARDA CORPO DA VARANDA DO 1º PAV DA CASA E. NOTE QUE TEM UNS TRAÇOS QUE NÃO FAZEM PARTE DA
# IMAGEM. ESSES TRAÇOS APARECEM NA VERTICAL E NA HORIZONTAL ABAIXO DO VASO"). Em px do quadro:
# - "esq": a linha dupla (um fio claro e um escuro) logo depois do guarda-corpo da esquerda, por trechos (o de cima, junto
#   à planta, e os de baixo): onde a linha aparece (o fio claro mais claro que o escuro em `dif`), a faixa vem do piso
#   logo depois dela, espelhado, na mesma linha;
# - "cantos": no canto de baixo, em volta dos dois vasos e da planta, o piso do render (mais claro e liso, em quadrados) e
#   o fio escuro em L em volta do vaso de baixo (a base quadrada do vaso do render): o piso do canto vem do Bege Bahia da
#   mesma varanda `dy` px acima (as mesmas colunas), com as emendas com o piso de fora esfumadas (`suave`); os vasos e a
#   planta ficam por cima, com a sombra curta (`sombra`: px para a esquerda e para baixo, desfoque, força). No canto de
#   cima, a planta tem a borda clara do render, que num piso novo vira um contorno: lá só sai a linha da esquerda;
# o que é planta (o verde-oliva: o vermelho quase igual ao verde e o azul abaixo dele; as folhas escuras) ou vaso (o
# terracota) fica.
VARANDA_1PAV_E = {"esq": {"x": (1175, 1182), "y": (530, 1531), "dif": 15, "folga": 2},
                  "cantos": [{"px": (1174, 1388, 1318, 1534), "dy": -170, "emendas": ("cima", "direita")}],
                  "suave": 10, "sombra": (3, 2.5, 0.30), "mancha_min": 40}


def _planta_vaso(px):
    a = px.astype(np.int16)
    b, g, r = a[..., 0], a[..., 1], a[..., 2]
    planta = ((r - g < 11) & (g - b > 12)) | ((r + g + b) < 405)
    return planta | ((r - b > 55) & (r - g > 30))


def varanda_1pav_e(Q, img):
    q = VARANDA_1PAV_E
    out = img.copy()
    lum = img.astype(np.float32).mean(axis=2)
    e = q["esq"]
    x0, x1 = e["x"]
    linha = lum[:, x0] - lum[:, x0 + 4] > e["dif"]
    linha[:e["y"][0]] = False
    linha[e["y"][1]:] = False
    linha = cv2.dilate(linha.astype(np.uint8)[:, None], np.ones((2 * e["folga"] + 1, 1), np.uint8))[:, 0] > 0
    n = 0
    espelho = 2 * x1 - np.arange(x0, x1)          # o piso logo depois da faixa, espelhado (sem emenda na borda da faixa)
    for y in np.nonzero(linha)[0]:
        alvo, fonte = img[y, x0:x1], img[y, espelho]
        ok = ~_planta_vaso(alvo) & ~_planta_vaso(fonte)
        out[y, x0:x1][ok] = fonte[ok]
        n += int(ok.sum())
    for c in q["cantos"]:
        a0, b0, a1, b1 = c["px"]
        reg = out[b0:b1, a0:a1].astype(np.float32)
        piso = out[b0 + c["dy"]:b1 + c["dy"], a0:a1].astype(np.float32)
        # a planta e os vasos inteiros (sem os pontinhos do piso que a cor confunde: manchas de menos de `mancha_min`
        # px), com a borda macia
        pv = cv2.morphologyEx(_planta_vaso(img[b0:b1, a0:a1]).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
        nc, lab, st, _ = cv2.connectedComponentsWithStats(pv, 8)
        pv = np.isin(lab, [i for i in range(1, nc) if st[i, cv2.CC_STAT_AREA] >= q["mancha_min"]])
        fica = cv2.GaussianBlur(pv.astype(np.float32), (0, 0), 0.6)
        h, w = fica.shape
        dsx, sig, forca = q["sombra"]
        sb = cv2.GaussianBlur(cv2.warpAffine(fica, np.float32([[1, 0, -dsx], [0, 1, dsx]]), (w, h)), (0, 0), sig) * forca
        piso *= (1 - sb * (1 - fica))[..., None]
        # as emendas com o piso de fora do canto esfumadas
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        dist = {"cima": yy, "baixo": (h - 1) - yy, "direita": (w - 1) - xx}
        borda = np.clip(np.minimum.reduce([dist[e] for e in c["emendas"]]) / q["suave"], 0, 1)
        m = borda * (1 - fica)
        out[b0:b1, a0:a1] = np.clip(reg * (1 - m[..., None]) + piso * m[..., None], 0, 255).astype(np.uint8)
        n += int((m > 0.5).sum())
    print(f"    varanda: {n} px dos traços do render rente aos guarda-corpos refeitos com o Bege Bahia ao lado")
    return out


# Os tracejados do 1º Pavimento em preto ou branco (usuário, 28/10/26: "os tracejados são ou brancos ou pretos, a
# depender do fundo"; para o 1º Pavimento, "pode"): os que estavam em cinza, nos traços do PDF (DOC_LINHAS E
# PROJEÇÕES): os X dos dois vazios, o da escada e o do hall (`retoque_1pav_casae.VAZIOS`, o cinza multiplicado pelo
# Térreo nublado), e os grupos de `retoque_1pav_casae.PROJECOES_1P` (o X do shaft, o desenho da rouparia e os X rasos
# do banho master, sobre o vaso e o box). O cinza sai (o fundo ao lado, deslocado, dentro do mesmo grupo) e o traço
# volta fino (1,5 px), preto no fundo claro e branco no escuro, como no Térreo (`tracejados_pb_te`), por baixo dos
# rótulos. As linhas do lote e a cobertura (ARQ_CONTRAPISO), que a final não desenha, ficam como estão.
# O rótulo da ROUPARIA (usuário, 28/10/26, opção A, como na área de serviço do Térreo): o desenho tracejado para numa
# folga em volta do texto. O rótulo (54 px) é mais largo que o desenho (48 px): a folga é de 4 px (~7 cm), proporcional,
# para que fiquem a borda de cima, a de baixo e o pé das pernas do desenho.
# O Térreo nublado nos vazios (usuário, 28/10/26: "pode"): sem as projeções do Térreo (como no 1º Pavimento da Casa A);
# no vazio do hall aparecia, fraca, a linha da esquerda do X do hall do Térreo. Os traços do Térreo (`_tracos_te`) que
# caem nos vazios saem, só dentro deles (o nublado ao lado, deslocado).
TRACEJADOS_1P = dict(TRACEJADOS_TE, vaos=dict(TRACEJADOS_TE["vaos"], pavimento="1Pavimento", rotulos=("ROUPARIA",),
                                              folga_px=4, limpa_px=3, media=True,
                                              deslocs=[(0, 5), (0, -5), (5, 0), (-5, 0), (0, 8), (0, -8), (8, 0),
                                                       (-8, 0), (4, 4), (-4, -4), (4, -4), (-4, 4), (0, 12), (0, -12),
                                                       (12, 0), (-12, 0), (16, 0), (-16, 0), (0, 16), (0, -16)]),
                     # a fonte do fundo: a caixa do grupo com esta folga (nos vazios, só o vazio), no mesmo material do
                     # PDF que o px refeito (o vinílico no vinílico, o vaso no vaso); na rouparia, o vinílico entre a
                     # lateral do desenho e a perna dele é estreito demais, e o desenho antigo tem um halo escuro do
                     # render a ±3 px do traço (`limpa_px`)
                     fonte_px=10,
                     # nos vazios, a faixa junto à borda (a linha do degrau, o vidro, a sombra da parede) é refeita só
                     # com o fundo ao longo da borda: nas faixas de cima e de baixo, deslocado na horizontal; nas dos
                     # lados, na vertical (o X raso da escada cruza ~15 px da faixa na horizontal)
                     borda_px=10, borda_tol=30,
                     deslocs_linha=[(d * s_, 0) for d in (12, 20, 28, 36, 44, 52) for s_ in (1, -1)],
                     deslocs_coluna=[(0, d * s_) for d in (12, 20, 28, 36) for s_ in (1, -1)],
                     grupos=[("vazio da escada", (1652.9, 1213.9, 1991.0, 1296.5), True),
                             ("vazio do hall", (1985.3, 1479.8, 2237.8, 1728.6), True)]
                     + [(nome, caixa, False) for nome, caixa in (("shaft", (1832.5, 905.5, 1849.0, 997.5)),
                                                                 ("rouparia", (1886.0, 943.0, 1933.5, 990.0)),
                                                                 ("banho master: vaso", (1538.5, 974.0, 1608.0, 997.5)),
                                                                 ("banho master: box", (1615.0, 974.0, 1726.5, 997.5)))])


def _tracos_1p(Q, q=None):
    """Os traços do PDF (pt) de cada grupo do 1º Pavimento, sem os repetidos, na ordem do PDF."""
    import pymupdf
    q = q or TRACEJADOS_1P
    trechos = []
    for nome, caixa, _ in q["grupos"]:
        cx, vistos, tr = pymupdf.Rect(*caixa), set(), []
        for d in Q.desenhos:
            if d.get("layer") != "DOC_LINHAS E PROJEÇÕES" or d["type"] != "s" or d["rect"] not in cx:
                continue
            for it in d["items"]:
                if it[0] == "l":
                    t = (it[1].x, it[1].y, it[2].x, it[2].y)
                    k = tuple(round(v, 1) for v in t)
                    if k not in vistos:
                        vistos.add(k)
                        tr.append(t)
        trechos.append((nome, tr))
    return trechos


def _bordas_vazio(lum, vaz, caixa, k=10, tol=30):
    """As linhas retas da borda do vazio (a linha do degrau, o vidro, a face da parede): as linhas e as colunas a até `k`
    px da borda, dentro da caixa (x0, y0, x1, y1, px), cuja mediana de luz se afasta mais de `tol` da do miolo, com 1 px
    em volta. Devolve (linhas, colunas), máscaras dentro do vazio."""
    x0, y0, x1, y1 = (int(round(v)) for v in caixa)
    sub, l = vaz[y0:y1, x0:x1], lum[y0:y1, x0:x1]
    lin, col = np.zeros_like(vaz), np.zeros_like(vaz)
    ys, xs = np.nonzero(sub)
    if not len(ys):
        return lin, col
    for eixo, (a, b), m in ((0, (ys.min(), ys.max()), lin), (1, (xs.min(), xs.max()), col)):
        med = np.array([np.median(l[i][sub[i]]) if sub[i].any() else np.nan for i in range(sub.shape[0])]) \
            if eixo == 0 else np.array([np.median(l[:, j][sub[:, j]]) if sub[:, j].any() else np.nan
                                        for j in range(sub.shape[1])])
        miolo = np.nanmedian(med[a + k:b - k + 1]) if b - a > 2 * k else np.nanmedian(med)
        for i in list(range(a, min(a + k, b + 1))) + list(range(max(b - k + 1, a), b + 1)):
            if abs(med[i] - miolo) > tol:
                for i2 in (i - 1, i, i + 1):
                    if eixo == 0:
                        m[y0 + i2, x0:x1] = True
                    else:
                        m[y0:y1, x0 + i2] = True
    return lin & vaz, col & vaz


def tracejados_pb_1p(Q, img, q=None):
    """Os tracejados cinza do 1º Pavimento em preto ou branco: o cinza sai e o traço volta fino (a imagem sem rótulos)."""
    q = q or TRACEJADOS_1P
    paredes_pdf(Q)
    trechos = _tracos_1p(Q, q)
    vaz = _onde_terreo(Q)[1]
    lum = img.astype(np.float32).mean(axis=2)
    vazios = {nome for nome, _, vazio in q["grupos"] if vazio}
    # cada vazio, para a limpeza: as linhas retas da borda (a linha do degrau, o vidro, a face da parede), refeitas só ao
    # longo delas (as de cima e de baixo, com o fundo deslocado na horizontal; as dos lados, na vertical), e o resto
    # (o nublado desfocado, a sombra da parede), pela média dos dois lados da faixa e, onde não há, pelo inpaint
    regioes = []
    for nome, caixa, vazio in q["grupos"]:
        if not vazio:
            continue
        (a, b), (c, d) = Q.p2q(*caixa[:2]), Q.p2q(*caixa[2:])
        cx = (a - 3, b - 3, c + 3, d + 3)
        x0, y0, x1, y1 = (int(round(v)) for v in cx)
        m = np.zeros_like(vaz)
        m[y0:y1, x0:x1] = True
        m &= vaz
        lin, col = _bordas_vazio(lum, vaz, cx, k=q["borda_px"], tol=q["borda_tol"])
        lin, col = lin & m, col & m & ~lin
        resto = m & ~lin & ~col
        regioes.append((cx, [(col, col, {"deslocs": q["deslocs_coluna"]}), (lin, lin, {"deslocs": q["deslocs_linha"]}),
                             (resto, resto, {"so_media": True})]))

    def limpa_vazios(im, linhas):
        for cx, partes in regioes:
            for regiao, fonte_r, opc in partes:
                if regiao.any():
                    im = _limpa_tracos(Q, im, [cx], q=dict(q, vaos=dict(q["vaos"], **opc)), trechos=linhas,
                                       fonte=fonte_r, so_em=regiao)
        return im
    # o Térreo nublado nos vazios sem as projeções do Térreo
    QT, terreo = QuadroE("Terreo"), []
    for nome, t in _tracos_te(QT):
        segs = []
        for x0, y0, x1, y1 in t:
            (a, b), (c, d) = QT.p2q(x0, y0), QT.p2q(x1, y1)
            u, v = int((a + c) / 2), int((b + d) / 2)
            if 0 <= v < vaz.shape[0] and 0 <= u < vaz.shape[1] and vaz[v, u]:
                segs.append(tuple(Q.q2p(a, b)) + tuple(Q.q2p(c, d)))
        if segs:
            terreo.append((f"Térreo: {nome}", segs))
    if terreo:
        img = limpa_vazios(img, terreo)
        print("    Térreo nublado nos vazios sem: " + ", ".join(f"{n} ({len(t)} traços)" for n, t in terreo))
    # o X cinza dos vazios
    img = limpa_vazios(img, [(n, t) for n, t in trechos if n in vazios])
    # os outros grupos: o fundo da caixa do grupo com `fonte_px` de folga, no mesmo material do PDF que o px refeito
    caixas, fonte = [], np.zeros(img.shape[:2], bool)
    for nome, caixa, vazio in q["grupos"]:
        if vazio:
            continue
        (a, b), (c, d) = Q.p2q(*caixa[:2]), Q.p2q(*caixa[2:])
        caixas.append((a - 3, b - 3, c + 3, d + 3))
        f = q["fonte_px"]
        fonte[max(int(b) - f, 0):int(np.ceil(d)) + f, max(int(a) - f, 0):int(np.ceil(c)) + f] = True
    ch = Q.chapada.astype(np.int32)
    material = ch[..., 0] * 65536 + ch[..., 1] * 256 + ch[..., 2]
    limpa = _limpa_tracos(Q, img, caixas, q=q, trechos=[(n, t) for n, t in trechos if n not in vazios], fonte=fonte,
                          mesmo=material, so_em=~vaz)
    # o X dos vazios só dentro deles, de canto a canto, como no PDF (as linhas da borda ficam inteiras em volta)
    dentro = cv2.erode(vaz.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    cortados = []
    for nome, t in trechos:
        if nome not in vazios:
            cortados.append((nome, t))
            continue
        novos = []
        for x0, y0, x1, y1 in t:
            (u0, v0), (u1, v1) = Q.p2q(x0, y0), Q.p2q(x1, y1)
            n = max(2, int(np.hypot(u1 - u0, v1 - v0) * 4))
            f = np.linspace(0, 1, n)
            ok = dentro[np.clip(np.round(v0 + (v1 - v0) * f).astype(int), 0, vaz.shape[0] - 1),
                        np.clip(np.round(u0 + (u1 - u0) * f).astype(int), 0, vaz.shape[1] - 1)]
            if ok.sum() < 2:
                continue
            i = np.nonzero(ok)[0]
            fa, fb = f[i[0]], f[i[-1]]
            novos.append((x0 + (x1 - x0) * fa, y0 + (y1 - y0) * fa, x0 + (x1 - x0) * fb, y0 + (y1 - y0) * fb))
        cortados.append((nome, novos))
    print(f"    grupos: " + ", ".join(f"{nome} ({len(t)} traços)" for nome, t in cortados))
    return tracejados_pb_te(Q, limpa, q=q, trechos=cortados)


def tracejados_1p_sobre_final(Q, img):
    """Sobre a final do 1º Pavimento: a final sem os rótulos, os tracejados em preto ou branco, os rótulos de novo; na
    final, só a faixa dos traços (a do cinza tirado incluída)."""
    limpa, _ = sem_rotulos("1Pavimento", img, novos=True)
    com = tracejados_pb_1p(Q, limpa)
    nova = escrever_rotulos("1Pavimento", com)
    faixa = cv2.dilate((np.abs(com.astype(np.int16) - limpa.astype(np.int16)).max(axis=2) > 0).astype(np.uint8),
                       np.ones((7, 7), np.uint8)).astype(bool)
    out = np.where(faixa[..., None], nova, img)
    print(f"    tracejados do 1º Pavimento em preto ou branco ({int(faixa.sum())} px refeitos)")
    return out


# O sofá da sala íntima (usuário, 28/10/26: "corrija a imperfeição no sofá gerada pelo piso"): a borda de cima do encosto
# tinha dois entalhes do render, junto às emendas das almofadas, com o piso entrando no estofado (mais à vista com o
# vinílico novo). Em cada entalhe (x0, x1, y0, y1 em px da final), o topo do encosto e a sombra fina dele sobre o piso vêm
# da mesma linha, das colunas inteiras a `dx` px, com `suave_px` de transição dos lados: a borda fica reta, como no resto
# do encosto (y = 1199 px), e as emendas seguem logo abaixo.
SOFA_1P = {"remendos": [(1911, 1924, 1194, 1203, -14), (1969, 2000, 1194, 1204, -32)], "suave_px": 2}


def sofa_sala_intima_1p(Q, img, q=None):
    q = q or SOFA_1P
    out = img.astype(np.float32)
    s = q["suave_px"]
    for x0, x1, y0, y1, dx in q["remendos"]:
        a = np.ones(x1 - x0, np.float32)
        a[:s] = (np.arange(s) + 1) / (s + 1)
        a[-s:] = a[:s][::-1]
        a = a[None, :, None]
        out[y0:y1, x0:x1] = out[y0:y1, x0:x1] * (1 - a) + img[y0:y1, x0 + dx:x1 + dx].astype(np.float32) * a
    print(f"    sofá da sala íntima: {len(q['remendos'])} entalhes do encosto refeitos com o encosto ao lado")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def _mais_perto(r, fonte, alvo):
    """Cada px de `alvo` com a cor do px de `fonte` mais perto."""
    _, rot = cv2.distanceTransformWithLabels((~fonte).astype(np.uint8), cv2.DIST_L2, 5,
                                             labelType=cv2.DIST_LABEL_PIXEL)
    ys, xs = np.nonzero(fonte)
    idx = np.zeros(rot.max() + 1, int)
    idx[rot[ys, xs]] = np.arange(len(ys))
    out = r.copy()
    k = idx[rot[alvo]]
    out[alvo] = r[ys[k], xs[k]]
    return out


def contorno_peca(img, caixa, semente, corte=None, rb_max=48, lum_min=95, sigma=2.0, piso_rb=50, franja_px=5, piso_lum=140):
    """O contorno de uma peça clara (estofado) sobre o vinílico, alisado: a peça é o que tem R - B abaixo de `rb_max` (o
    vinílico é mais quente) ligado à `semente`, fora do meio-plano `corte` (a*x + b*y + c > 0: o tapete, a mesa), com os
    furos cheios; a silhueta alisada (desfoque de `sigma` px, limiar 0,5) leva os entalhes ao estofado mais perto (2 px
    para dentro) e os calombos e a franja (o que, a até `franja_px` px da peça, não tem cara de vinílico) ao piso mais
    perto (a 3 px da peça, com a sombra de antes); a borda nova vai antisserrilhada. Só muda uma faixa fina em volta."""
    x0, y0, x1, y1 = caixa
    r = img[y0:y1, x0:x1].astype(np.float32)
    h, w = r.shape[:2]
    lum, rb = r.mean(axis=2), r[..., 2] - r[..., 0]
    m = (rb < rb_max) & (lum > lum_min)
    livre = np.ones((h, w), bool)
    if corte is not None:                                  # meio-plano fora: a*x + b*y + c > 0 (px da final)
        a, b, c = corte
        yy, xx = np.mgrid[y0:y1, x0:x1]
        livre = ~(a * xx + b * yy + c > 0)
        m &= livre
    n, lab = cv2.connectedComponents(m.astype(np.uint8))
    m = lab == lab[semente[1] - y0, semente[0] - x0]
    fora = (m.astype(np.uint8) * 255).copy()
    cv2.floodFill(fora, np.zeros((h + 2, w + 2), np.uint8), (0, 0), 255)
    m = m | (fora == 0)
    ms = cv2.GaussianBlur(m.astype(np.float32), (0, 0), sigma) > 0.5

    def mx(a_, k):
        return cv2.dilate(a_.astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool)

    def mn(a_, k):
        return cv2.erode(a_.astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool)
    # A: o estofado (os entalhes com o estofado mais perto, 2 px para dentro); F: o piso (a franja e os calombos com o
    # piso mais perto, a 3 px do estofado, com a sombra de antes)
    A = _mais_perto(r, mn(m, 5), ms & ~mn(m, 5))
    # a franja: junto à peça, o que não tem cara de piso (meio estofado, meio piso)
    piso = (rb >= piso_rb + 2) & (lum < piso_lum)
    franja = mx(m, franja_px * 2 + 1) & ~ms & ~piso & livre
    F = _mais_perto(r, ~mx(m, 7) & ~franja & (rb >= piso_rb) & livre, (~ms & mx(m, 5)) | franja)
    al = np.clip(cv2.GaussianBlur(ms.astype(np.float32), (0, 0), 0.7), 0, 1)[..., None]
    nova = A * al + F * (1 - al)
    # junto ao corte (o tapete, a mesa) nada muda: lá a borda alisada levaria o piso para a quina
    faixa = (mx(m ^ ms, 5) | (mx(ms, 5) & ~mn(ms, 5)) | (mx(m, 5) & ~mn(m, 5)) | mx(franja, 3)) & mn(livre, 5)
    reg = r.copy()
    reg[faixa] = nova[faixa]
    out = img.copy()
    out[y0:y1, x0:x1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return out, m, ms


# A poltrona da suíte master (usuário, 28/10/26: "corrija o contorno do encosto da poltrona da suite master"): o contorno
# do render, girado a 45°, era serrilhado e com calombos, mais à vista no vinílico novo. `contorno_peca` alisa a
# silhueta; o meio-plano acima da reta pela quina de cima (`corte`, de p0 a p1) deixa de fora o tapete e a mesa lateral.
POLTRONA_MASTER_1P = {"caixa": (1419, 776, 1508, 872), "semente": (1458, 825), "corte": ((1446, 786), (1500, 829))}


def poltrona_master_1p(Q, img, q=None):
    q = q or POLTRONA_MASTER_1P
    (ax, ay), (bx, by) = q["corte"]
    a, b = by - ay, -(bx - ax)
    out, m, ms = contorno_peca(img, q["caixa"], q["semente"], corte=(a, b, -(a * ax + b * ay)))
    print(f"    poltrona da suíte master: contorno alisado ({int((m ^ ms).sum())} px trocados de lado)")
    return out


def passos_1pav(Q):
    return [
        ("nublado", lambda im: nublado_novo(Q, im)),
        ("pisos", lambda im: pisos_e(Q, im, PISOS_1PAV_E, FICAM_1PAV_E)),
        ("escada", lambda im: escada_e(Q, im, ESCADA_1PAV_E)),
        ("bancadas", lambda im: _bancadas(Q, im, BANCADAS_1PAV_E)),
        ("paredes", lambda im: paredes_e(Q, im)),
        ("varanda", lambda im: varanda_1pav_e(Q, im)),
        ("sofa", lambda im: sofa_sala_intima_1p(Q, im)),
        ("poltrona_master", lambda im: poltrona_master_1p(Q, im)),
        ("tracejados", lambda im: tracejados_pb_1p(Q, im)),
        ("rotulos", lambda im: escrever_rotulos("1Pavimento", im)),
    ]


PASSOS = {"Subsolo": passos_subsolo, "Terreo": passos_terreo, "1Pavimento": passos_1pav}
# as etapas que só vão sobre a final (`--sobre-final`): numa rodada do zero, o nublado já vem com a revisão do Térreo
SO_SOBRE_FINAL = {"Subsolo": {"piscina_borda": piscina_borda_sub},
                  "1Pavimento": {"nublado_revisao": nublado_revisao_te, "nublado_tracejados": nublado_tracejados_te,
                                 "tracejados_final": tracejados_1p_sobre_final, "sofa": sofa_sala_intima_1p,
                                 "poltrona_master": poltrona_master_1p, "nublado_poltronas": nublado_poltronas_te},
                  "Terreo": {"seta_hall": seta_rotulo_hall_te, "tracejados_final": tracejados_sobre_final_te,
                             "vao_servico": vao_rotulo_servico_te, "poltronas_living": poltronas_living_sobre_final_te,
                             "sofa_varanda": sofa_varanda_sobre_final_te}}


def final_3840(chave, de=None, ate=None, salvar=True):
    Q = QuadroE(chave)
    passos = PASSOS[chave](Q)
    nomes = [n for n, _ in passos]
    ETAPAS.mkdir(parents=True, exist_ok=True)
    i0 = nomes.index(de) if de else 0
    img = inicial(chave) if i0 == 0 else cv2.imread(str(ETAPAS / f"{chave}_{nomes[i0 - 1]}.png"))
    for nome, f in passos[i0:]:
        t = time.time()
        print(f"[{nome}]")
        img = f(img)
        cv2.imwrite(str(ETAPAS / f"{chave}_{nome}.png"), img)
        print(f"    ({time.time() - t:.0f} s)")
        if ate == nome:
            return img
    if salvar:
        gravar_final(chave, img)
    return img


def gravar_final(chave, img):
    destino = CASA / "renders" / PAV_E[chave]["final"]
    cv2.imwrite(str(destino), img)
    cv2.imwrite(str(destino.with_name(destino.stem + "_preview.jpg")),
                cv2.resize(img, (2000, round(2000 * img.shape[0] / img.shape[1])), interpolation=cv2.INTER_AREA),
                [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"[fim] {destino}")


def sobre_final(chave, etapa):
    """Uma etapa aplicada direto na final aprovada (a revisão de 28/10 do Térreo: a final em cache é anterior a ela)."""
    Q = QuadroE(chave)
    f = dict(PASSOS[chave](Q), **{n: (lambda im, g=g: g(Q, im)) for n, g in SO_SOBRE_FINAL.get(chave, {}).items()})[etapa]
    img = cv2.imread(str(CASA / "renders" / PAV_E[chave]["final"]))
    print(f"[{etapa}] sobre a final")
    gravar_final(chave, f(img))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pavimento", choices=list(PAV_E))
    ap.add_argument("--de", default=None)
    ap.add_argument("--ate", default=None)
    ap.add_argument("--sobre-final", default=None, help="aplica só esta etapa, direto na final aprovada")
    args = ap.parse_args()
    if args.sobre_final:
        sobre_final(args.pavimento, args.sobre_final)
    else:
        final_3840(args.pavimento, de=args.de, ate=args.ate)

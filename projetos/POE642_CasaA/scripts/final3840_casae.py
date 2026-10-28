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


def escrever_rotulos(chave, img, novos=True):
    """Os rótulos do pavimento na imagem, como na final aprovada (novos=False) ou com os ajustes desta rodada."""
    import retoque_1pav_casae as R1
    Q, rot, aj, leg = _rotulos_pav(chave)
    if novos and AJUSTES_E[chave]:
        nomes = {a[0] for a in AJUSTES_E[chave]}
        aj = [a for a in aj if a[0] not in nomes] + list(AJUSTES_E[chave])
    kw = {}
    if leg is not None:
        kw = {"granito": np.abs(Q.chapada.astype(int) - np.array(leg)).max(axis=2) <= 6,
              "cor_granito": R1.ROTULOS["branco"]}
    return R1.rotulos_ambientes(img, rot, Q.p2q, escala_desvio=Q.W / 2000, ajustes=aj, **kw)


def sem_rotulos(chave, final):
    """A final sem os rótulos: a composição dos rótulos (out = cor * a + fundo * (1 - a)) desfeita px a px; onde o
    alfa passa de 0,8, o fundo vem dos vizinhos (inpaint de 3 px)."""
    H, W = final.shape[:2]
    vp = escrever_rotulos(chave, np.zeros((H, W, 3), np.uint8), novos=False).astype(np.float32)
    vb = escrever_rotulos(chave, np.full((H, W, 3), 255, np.uint8), novos=False).astype(np.float32)
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
           "area_min": 25, "junto_px": 4, "camadas_tracos": ("ARQ_ MOB COMUM",),
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


def troca_piso(Q, img, ini, legenda, textura, tom, sig_m, semente, fora=None, forca=None, pecas=None):
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
    m = legenda & ~pec & ~paredes_pdf(Q, folga=1) & ~linhas_pdf(Q)
    if fora is not None:
        m &= ~fora
    novo = F.piso_textura(Q, img, m, textura, forca, sig_m, semente)
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
PAREDES_E = {"cor": (80, 80, 80), "camadas": ("ARQ_PAREDE", "ARQ_ELEMENTOS FIXOS"), "escuro": 48, "croma": 12, "folga_px": 3, "escuro_min": 0.25,
             "pilar_cor": (8, 8, 8), "pilar_camadas": ("EST - Pilar", "EST_PILAR")}


def paredes_e(Q, img, q=None, extra=None, pilares=True):
    q = q or PAREDES_E
    im = img.astype(np.int16)
    preto = (im.max(axis=2) < q["escuro"]) & ((im.max(axis=2) - im.min(axis=2)) <= q["croma"])
    ss = 4
    a = np.zeros((Q.H, Q.W), np.float32)
    n_ok = n_fora = 0
    for d in Q.desenhos:
        if d.get("layer") not in q["camadas"] or d.get("fill") is None or max(d["fill"]) >= 0.5:
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
        ad = cv2.resize(m, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
        anel = cv2.dilate((ad > 0.05).astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
        if preto[y0:y1, x0:x1][anel].mean() < q["escuro_min"]:
            n_fora += 1
            continue
        a[y0:y1, x0:x1] = np.maximum(a[y0:y1, x0:x1], ad)
        n_ok += 1
    if extra is not None:
        a = np.maximum(a, extra)
    k = 2 * q["folga_px"] + 1
    perto = cv2.dilate((a > 0.02).astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool)
    M = perto & preto
    out = cv2.inpaint(img, M.astype(np.uint8), 3, cv2.INPAINT_TELEA)
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
    print(f"    paredes em cinza {q['cor'][0]} no contorno do PDF: {n_ok} peças ({n_fora} que a final mostra claras "
          f"ficam); {int((M & (a < 0.5)).sum())} px da franja preta refeitos; {n_resto} px pretos fora do PDF ao cinza")
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
    out = F.letra(Q, out, e["letra"], Q.p2q((b[0] + b[1]) / 2, (ey0 + ey1) / 2))
    print(f"    escada {e['nome']}: {n} degraus em {e['textura']}, sem linhas e sem triângulo, com o sombreamento "
          f"{'de descida' if no_alto else 'de subida'}; {'o trecho depois do corte nevoado; ' if e.get('corte') else ''}"
          f"o {e['letra']} no degrau {'de cima' if no_alto else '1'}")
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
# (`AJ.folhas_box`) inteiras, cada uma uma faixa de vidro com as faces finas e a sombra curta, e o trilho no vão, só nos
# boxes dentro de `caixa_pt`
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
    out = F.letra(Q, out, q["letra"], Q.p2q(*q["letra_pt"]))
    print(f"    {q['nome']}: {n} blocos de pedra do PDF em Bege Bahia, sem contorno, cada um com a sombra curta do de "
          f"cima; o {q['letra']} no bloco de cima")
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
#    vestiário) na foto da biblioteca, no tom do travertino do Térreo;
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
PISOS_SUB_E = [("granito", [(50, 66, 90)], "granito", (68, 87, 116), 1.5, 2801, None),
               ("vinílico", [(79, 120, 168)], "vinilico", None, 1.0, 2802, None),
               ("Bege Bahia", [(232, 232, 232)], "bege", (187, 211, 230), 1.5, 2803, None),
               ("travertino", [(202, 217, 220)], "travertino", (205, 220, 235), 3.0, 2804, 1.6)]
ESCADA_SUB_E = {"nome": "da circulação", "pdf": (972.0, 617.0, 1261.2, 685.0),
                "bocels": [972.0 + 17.0 * k for k in range(1, 17)], "inicio": "direita", "apos": "esquerda",
                "corte": [(1073.8, 616.4), (1108.1, 685.0)], "nevoa": {"branco": 0.72, "sigma_px": 1.2},
                "sombra_corte": {"forca": 0.30, "alc_px": 4.0}, "textura": "travertino", "tom": (205, 220, 235),
                "forca": 1.0, "letra": "S", "semente": 2805}
ARMARIO_DCE_E = {"pt": (1439.8, 795.5, 1507.8, 829.6), "lado": "cima"}
BANCADA_WC_DCE2 = (1697.6, 693.5, 1726.1, 729.1)
AJUSTES_E["Subsolo"] = [("CASA DE MÁQUINAS", (1043.4, 335.8), (0, 0), 1.0),
                        ("WC DCE 2", (986.5, 310.9), (-3.9, -30.0), 0.85)]


def pisos_e(Q, img, specs):
    ini = img.copy()
    out = img.copy()
    for nome, cores, tex, tom, sig, sem, forca in specs:
        leg = legenda(Q, cores)
        out, m, _ = troca_piso(Q, out, ini, leg, tex, tom, sig, sem, forca=forca)
        print(f"    {nome}: {m.sum() / Q.px_m ** 2:.1f} m² ({tex}, na escala da prancha)")
    return out


def passos_subsolo(Q):
    return [
        ("pisos", lambda im: pisos_e(Q, im, PISOS_SUB_E)),
        ("escada", lambda im: escada_e(Q, im, ESCADA_SUB_E)),
        ("armario", lambda im: armario_cabides(Q, im, ARMARIO_DCE_E["pt"], ARMARIO_DCE_E["lado"], nome="DCE")),
        ("bancada", lambda im: bancada_e9(Q, im, BANCADA_WC_DCE2, nome="WC DCE 2")),
        ("paredes", lambda im: paredes_e(Q, im)),
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
# 4. E5: o box de correr do WC DCE 1 nas duas folhas de vidro do PDF, com o trilho no vão;
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
BANCADAS_TER_E = [("banho gourmet", (1163.3, 759.8, 1252.7, 784.2)), ("WC DCE 1", (2202.4, 788.0, 2230.6, 823.9)),
                  ("lavabo", (2064.0, 1453.3, 2159.3, 1478.7))]
SETA_TER_E = (2500, 1542)
AJUSTES_E["Terreo"] = [("WC DCE 1", (1261.6, 271.3), (-0.9, 32.3), 0.85)]  # no meio do piso seco (2177,5 x 780 pt)


def passos_terreo(Q):
    return [
        ("pisos", lambda im: pisos_e(Q, im, PISOS_TER_E)),
        ("escadas", lambda im: blocos_e(Q, escada_e(Q, escada_e(Q, im, ESCADAS_TER_E[0]), ESCADAS_TER_E[1]),
                                        BLOCOS_TER_E)),
        ("armario", lambda im: armario_cabides(Q, im, ARMARIO_DCE_TER_E["pt"], ARMARIO_DCE_TER_E["lado"], nome="DCE")),
        ("box", lambda im: box_e(Q, im, BOX_WC_DCE1, nome="WC DCE 1")),
        ("bancadas", lambda im: _bancadas(Q, im, BANCADAS_TER_E)),
        ("paredes", lambda im: paredes_e(Q, im)),
        ("seta", lambda im: seta_e(Q, im, SETA_TER_E)),
        ("rotulos", lambda im: escrever_rotulos("Terreo", im)),
    ]


def _bancadas(Q, img, lista):
    for nome, r in lista:
        img = bancada_e9(Q, img, r, nome=nome)
    return img


PASSOS = {"Subsolo": passos_subsolo, "Terreo": passos_terreo}


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
        destino = CASA / "renders" / PAV_E[chave]["final"]
        cv2.imwrite(str(destino), img)
        cv2.imwrite(str(destino.with_name(destino.stem + "_preview.jpg")),
                    cv2.resize(img, (2000, round(2000 * img.shape[0] / img.shape[1])), interpolation=cv2.INTER_AREA),
                    [cv2.IMWRITE_JPEG_QUALITY, 90])
        print(f"[fim] {destino}")
    return img


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pavimento", choices=list(PAV_E))
    ap.add_argument("--de", default=None)
    ap.add_argument("--ate", default=None)
    args = ap.parse_args()
    final_3840(args.pavimento, de=args.de, ate=args.ate)

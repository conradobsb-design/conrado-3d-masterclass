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


def paredes_e(Q, img, q=None, extra=None, pilares=True, sempre=(), ini=None, tirar=(), por=()):
    """`extra`: a máscara (0 a 1) de outras paredes, somada por cima, ou um filtro dos desenhos do PDF, que entram na
    mesma máscara das paredes (sem a conta do escuro). `sempre`: caixas (pt) onde toda peça escura do PDF é parede, mesmo
    onde a final a mostra clara (a piscina do Subsolo, onde o render pintou água sobre as pontas das paredes). `ini`: a
    final aprovada sem os rótulos; com ela, a sobra da parede antiga do render em volta da nova (os px a até `folga_px`
    que nenhuma etapa redesenhou e que são mais escuros que o piso de perto, `sobra`) sai também, refeita pelo piso.
    `tirar`: retângulos (pt) cujas peças escuras de dentro saem; `por`: retângulos (pt) que entram na parede (os dentes
    das pontas de parede trocados pela face reta)."""
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
    bege = np.clip(_uniao(Q, q["bege"], X0, Y0, w, h) - par, 0, 1)
    degrau = np.clip(_uniao(Q, q["degrau"], X0, Y0, w, h) - par, 0, 1)
    vidro = _uniao(Q, q["vidros"], X0, Y0, w, h)
    agua = np.clip(agua - bege - degrau - vidro - par, 0, 1)
    # a sombra curta das bordas, do degrau e das paredes na água (a luz do alto à direita: mais forte junto à beira)
    beira = np.clip(bege + degrau + par, 0, 1)
    dist = cv2.distanceTransform((beira < 0.5).astype(np.uint8), cv2.DIST_L2, 5)
    fs, alc = q["sombra"]
    sombra = 1 - fs * np.exp(-dist / alc)
    A = agua_e(Q, h, w, q["semente"]) * sombra[..., None]
    # as bordas em Bege Bahia (a foto da biblioteca, no tom dos pisos de Bege Bahia)
    T = textura("bege_bahia", Q.px_m, h, w, semente=q["semente_bege"]).astype(np.float32)
    Bg = T / T.reshape(-1, 3).mean(axis=0) * np.float32(q["tom_bege"])
    # o degrau da sauna no travertino do piso dela (o tom da mediana do piso de travertino em volta)
    trav = legenda(Q, [(202, 217, 220)])[Y0:Y1, X0:X1]
    tom_t = np.median(reg[trav], axis=0) if trav.any() else np.float32(TRAVERTINO_E["tom"])
    Tt = travertino_e(Q, h, w, q["semente"] + 7)[..., None] * tom_t
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
                  ("prateleira junto ao DCE", (1449.3, 845.4, 1503.1, 850.5), "prateleira"),
                  ("suporte de halteres", (1691.3, 845.1, 1720.9, 935.8), "halteres"),
                  ("supino com barra", (1400.2, 981.1, 1497.7, 1057.6), "supino"),
                  ("banco regulável", (1546.2, 973.9, 1575.4, 1057.7), "banco")],
    "bolas": [(1045.5, 714.9, 19.4), (1083.9, 714.9, 19.4)],                       # centro e raio (pt)
    "zona_m": 0.45, "ss": 6, "folga_pt": 1.0,
    "materiais": {                                            # BGR, o volume e o brilho
        "estrutura": ((72, 74, 78), "bisel", 0.0), "tubo": ((80, 82, 86), "cilindro", 0.25),
        "estofado": ((42, 42, 45), "almofada", 0.0), "borracha": ((36, 36, 38), "bisel", 0.0),
        "cromo": ((178, 180, 184), "cilindro", 0.55), "aluminio": ((156, 158, 162), "bisel", 0.0),
        "lona": ((38, 38, 40), "lona", 0.0), "painel": ((54, 56, 60), "bisel", 0.0), "tela": ((92, 74, 54), "plano", 0.0),
        "botao": ((150, 152, 155), "plano", 0.0), "bola": ((198, 200, 202), "esfera", 0.0)},
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
        ds = sorted([d for d in Q.desenhos if d.get("layer") == "ARQ_ MOB COMUM" and d["rect"].x0 >= x0p - fo
                     and d["rect"].x1 <= x1p + fo and d["rect"].y0 >= y0p - fo and d["rect"].y1 <= y1p + fo],
                    key=lambda d: d.get("seqno", 0))
        X0, Y0, X1, Y1 = F.ret_q(Q, (x0p - 8, y0p - 8, x1p + 8, y1p + 8))
        w, h = X1 - X0, Y1 - Y0
        W_, H_ = w * S, h * S
        lab = np.zeros((H_, W_), np.int32)
        lin = np.zeros((H_, W_), np.uint8)
        lb = np.zeros((H_, W_), np.uint8)                                    # os traços dentro das bolas
        k = 0
        for d in ds:
            cs = [np.int32(np.round((c - (X0, Y0)) * S)) for c in Q.caminhos(d)]
            if d["type"] in ("f", "fs"):
                k += 1
                m = np.zeros((H_, W_), np.uint8)
                cv2.fillPoly(m, [c for c in cs if len(c) >= 3], 1)
                lab[m > 0] = k
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
              [(1175.6, 1023.7, 1176.8, 1027.1), (1214.2, 1023.7, 1215.3, 1027.1)]),
             ("cabine do chuveiro", (1218.6, 1027.1, 1220.8, 1065.9), (1218.6, 1027.1, 1257.4, 1065.9), "travertino",
              [(1218.1, 1023.7, 1219.3, 1027.1), (1256.7, 1023.7, 1257.8, 1027.1)])],
    "vidros": [("ducha do ambiente: a porta", (1026.9, 1022.3, 1028.1, 1061.1), (1026.9, 1022.3, 1065.7, 1061.1), "travertino"),
               ("ducha do ambiente: o vidro fixo", (1009.5, 1021.7, 1026.9, 1022.3), (1009.5, 1019.5, 1026.9, 1024.5),
                "travertino")],
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
    "limpar": [("granito", (1493.1, 693.5, 1555.5, 699.5))],
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
    for nome, vidro, _, _ in q["vidros"]:
        tl = FA.tela(out, Q, vidro, folga=5)
        x0, y0, x1, y1 = vidro
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        meia = q["vidro_px"] / 2 / FA.PT_PX
        r = (x0, cy - meia, x1, cy + meia) if (x1 - x0) >= (y1 - y0) else (cx - meia, y0, cx + meia, y1)
        m = tl.ret(r)
        FA.sombra_q(tl, m, forca=0.20, dist=0.9, sigma=0.8)
        tl.pintar(m, q["vidro"])
        tl.contorno(m, q["vidro_face_px"], q["vidro_face"])
        out = tl.gravar()
    print(f"    portas: {len(q['giro'])} folhas de giro na posição e na espessura do PDF (branco suave, contorno fino, "
          f"sombra curta), com os batentes, sem arco; {len(q['soleiras'])} soleiras de Bege Bahia; a porta e o vidro fixo "
          f"da ducha do ambiente em vidro fino")
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


def nicho_ducha(Q, img):
    q = DUCHA_AMBIENTE_E
    r = q["nicho"]
    X0, Y0, X1, Y1 = F.ret_q(Q, (r[0] - 40, r[1] - 40, r[2] + 40, r[3] + 4))
    w, h = X1 - X0, Y1 - Y0
    out = img.astype(np.float32)
    reg = out[Y0:Y1, X0:X1]
    trav = legenda(Q, [(202, 217, 220)])[Y0:Y1, X0:X1]
    tom = np.median(reg[trav], axis=0) if trav.any() else np.float32(TRAVERTINO_E["tom"])
    a = _ret_local(Q, r, X0, Y0, w, h)
    T = travertino_e(Q, h, w, q["semente"])[..., None] * tom * q["nicho_luz"]
    reg[:] = reg * (1 - a[..., None]) + T * a[..., None]
    # a sombra curta do fundo (embaixo) e da lateral esquerda, dentro do nicho
    (u0, _), (u1, v1) = Q.p2q(r[0], r[1]), Q.p2q(r[2], r[3])
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
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
          "(placa, braço e canopla cromados) pelo PDF, com o nicho da parede em travertino")
    return out


# As paredes do Subsolo (usuário, 28/10/26: "A PAREDE AQUI NÃO ESTÁ PERFEITA. PRECISO DELA RETA E SEM DENTE", no toco
# entre a ducha e o ambiente; "ESSA PAREDE DA SAUNA TEM UM DENTE TAMBÉM QUE PRECISA DE CORREÇÃO"): entram as faixas de
# revestimento das faces (os preenchimentos escuros da ARQ_REVESTIMENTOS, 0,57 pt, que o PDF desenha como parte da
# parede: sem elas o topo do toco saía em degrau e as paredes ficavam mais finas que o desenho); na ponta da parede da
# sauna junto à porta, o dente de 1,4 pt (o encaixe do batente) sai e a face de baixo segue reta até a porta.
PAREDES_SUB_E = dict(PAREDES_E, camadas=PAREDES_E["camadas"] + ("ARQ_REVESTIMENTOS",),
                     tirar=[(1000.38, 957.12, 1008.89, 958.53)], por=[(999.19, 957.12, 1008.89, 957.68)])


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
                                         tirar=PAREDES_SUB_E["tirar"], por=PAREDES_SUB_E["por"])),
        ("vestiario", lambda im: vestiario_e(Q, im)),
        ("aparelhos", lambda im: aparelhos_e(Q, im)),
        ("portas", lambda im: portas_e(Q, im)),
        ("elevador", lambda im: cabine_elevador_e(Q, im)),
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
    print(f"    piscina: a água no turquesa da referência ({', '.join(map(str, areas))} m²: piscina e prainha, a faixa entre "
          f"os vidros, o spa), com as peças, os degraus e a rede das cáusticas; os vidros ficam")
    return out


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
        ("piscina", lambda im: piscina_terreo_e(Q, im)),
        ("rotulos", lambda im: escrever_rotulos("Terreo", im)),
    ]


def _bancadas(Q, img, lista):
    for nome, r in lista:
        img = bancada_e9(Q, img, r, nome=nome)
    return img


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
    img = box_e(QT, img, BOX_WC_DCE1, nome="WC DCE 1")
    img = _bancadas(QT, img, BANCADAS_TER_E)
    img = paredes_e(QT, img)
    img = piscina_terreo_e(QT, img)
    cv2.imwrite(str(c), img)
    return img


def nublado_novo(Q, img):
    """Troca o Térreo nublado da final (o do retocado de 2000 px, `opcoes_1pav_casae.TERREO`) pelo do Térreo novo, onde a
    final mostra o Térreo: fora da pegada (o px é o contexto antigo) e nos vazios (o contexto multiplicado pelo X e pelo
    vidro: entra a razão novo/antigo)."""
    import opcoes_1pav_casae as O
    from entorno_esmaecido import NUBLADO, contexto_render, pegada
    W = Q.W
    base = cv2.imread(str(O.BASE_CIMA))
    H = round(base.shape[0] * W / base.shape[1])
    base = cv2.resize(base, (W, H), interpolation=cv2.INTER_AREA)
    peg = pegada(base, O.FORA)
    a = np.maximum(cv2.GaussianBlur(peg.astype(np.float32), (0, 0), 1.0), peg)
    t_velho = contexto_render(O.TERREO, O.BASE_TERREO, W, **NUBLADO)
    n = NUBLADO
    t = cv2.GaussianBlur(terreo_para_nublado().astype(np.float32), (0, 0), n["desfoque"] * W / 3840)
    cinza = t.mean(axis=2, keepdims=True)
    t = cinza + (t - cinza) * n["saturacao"]
    t_novo = 255 - (255 - t) * (1 - n["clarear"])
    tracejado = (base.min(axis=2) < 225) & ~peg
    f = img.astype(np.float32)
    ctx = (1 - a) * ~tracejado
    out = f + (t_novo - t_velho) * ctx[..., None]
    vaz = O.mascara_vazios(base) & (a > 0.5)
    raz = t_novo / np.maximum(t_velho, 1)
    out[vaz] = (f * raz)[vaz]
    print(f"    o Térreo nublado em volta refeito com o Térreo novo: {int((ctx > 0.5).sum())} px de contexto e "
          f"{int(vaz.sum())} px nos vazios")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def passos_1pav(Q):
    return [
        ("nublado", lambda im: nublado_novo(Q, im)),
        ("pisos", lambda im: pisos_e(Q, im, PISOS_1PAV_E, FICAM_1PAV_E)),
        ("escada", lambda im: escada_e(Q, im, ESCADA_1PAV_E)),
        ("bancadas", lambda im: _bancadas(Q, im, BANCADAS_1PAV_E)),
        ("paredes", lambda im: paredes_e(Q, im)),
        ("rotulos", lambda im: escrever_rotulos("1Pavimento", im)),
    ]


PASSOS = {"Subsolo": passos_subsolo, "Terreo": passos_terreo, "1Pavimento": passos_1pav}


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

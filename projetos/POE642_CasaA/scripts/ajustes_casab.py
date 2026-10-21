#!/usr/bin/env python3
"""Ajustes, sem IA, das plantas da Casa B (POE 642): o pente fino pelas regras (21/10/26).

Pedido do usuário (21/10/26), depois dos mapas do pente fino (`conferencia_casab.py`) e do "ATENÇÃO ÀS ESCALAS":
"PERCORRA TODOS OS AJUSTES DE TODAS AS PLANTAS DA CASA B, SEM ME PERGUNTAR OU PEDIR APROVAÇÃO". Os itens dos mapas
(`renders/POE642_CasaB_PH_<Pavimento>_pente_fino_mapa.jpg`) são feitos um por vez, na ordem de execução de `ITENS`; nos
pontos "a confirmar" vale a proposta dos mapas (registrada no handoff, "Casa B · pente fino pelas regras").

Como a Casa A: as rotinas aprovadas no pente fino da Casa A (`ajustes_casaa.py`) servem à Casa B, que tem a mesma folha,
o mesmo recorte e a mesma escala (imagem de 2000 px, ~31,1 px/m). `contexto()` troca o que é da casa:
- `rotulos_casaa` (CONFIG, CASA, PAVIMENTOS) e `ajustes_casaa` (CASA, APROVADAS, AFIM_QR), para `pdf_pavimento` dar a
  página do PDF da Casa B e o pt -> px da imagem da Casa B;
- `ajustes_casaa.base_terreo`: a base chapada da legenda da Casa B (v2, as cores dos materiais), no quadro da imagem;
- os dicionários de parâmetros das rotinas, com as coordenadas (px de 2000 e pt do PDF) da Casa B.

Imagens de partida (as das pranchas entregues em 14/10/26):
- Térreo: `renders/POE642_CasaB_PH_Terreo_v4_retocado_barlavento.png` (o render retocado, 2000 x 1116);
- Subsolo: `renders/POE642_CasaB_PH_Subsolo_final.png` (6905 px, já no quadro comum), reduzido a 2000 px
  (`..._Subsolo_final_2000.png`) para as rotinas; na final de 3840 px, o que não mudou volta da imagem de 6905 px.
Saída: `renders/POE642_CasaB_PH_<Pavimento>_ajustes.png` (+ `_camada.png`) e um antes/depois por item. Depois,
`--final`: a imagem no quadro de 3840 px com a pedra portuguesa (Térreo), o terreno hachurado (Subsolo) e os rótulos,
que vai ao `rodape_entrega.py --no-quadro` e ao `pdf_entrega.py`.

Uso (da pasta POE642_CasaA/scripts/):
  python3 ajustes_casab.py Terreo            # todos os itens do Térreo
  python3 ajustes_casab.py Terreo --ate t5   # até o item t5 (desenvolvimento; as etapas ficam em cache)
  python3 ajustes_casab.py Terreo --final    # a imagem final com os rótulos
"""
import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np

import rotulos_casaa as A
import ajustes_casaa as AJ

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
CASA_B = RAIZ / "POE642_CasaB"
CONFIG_B = CASA_B / "config_bases.json"
CACHE = Path(__import__("os").environ.get("POE642_CACHE", __import__("tempfile").gettempdir())) / "poe642_casab_etapas"

PAVIMENTOS_B = {
    "Terreo": {"render": "renders/POE642_CasaB_PH_Terreo_ajustes.png",
               "aprovada": "renders/POE642_CasaB_PH_Terreo_v4_retocado_barlavento.png",
               "pdf": "642 - TÉRREO - CASA B.pdf",
               "sem_tela": "bases/POE642_CasaB_BASE_Terreo_v3_texturas.png",
               "chapada": "bases/POE642_CasaB_BASE_Terreo_v2_16x9.png",
               # rótulos (item 8, R6 e R7): (nome, centro no quadro de 2000 px, desvio em px de 2000[, opções])
               "ajustes": [("SUÍTE 3", (1300.3, 382.8), (-39.0, 12.0), {"corpo": 1.0}),       # da cama para o piso
                           ("PRAINHA", (501.7, 617.4), (0.0, 69.0)),                        # da espreguiçadeira
                           ("GARAGEM", (1332.2, 771.9), (0.0, 113.0)),                      # do carro do meio
                           ("BANHO 2", (1408.9, 237.9), (-6.0, 8.0)),                       # da bacia
                           ("QUARTO MOTORISTA", (1504.4, 764.4), (-8.0, 2.0)),              # da luminária
                           ("JARDIM DE INVERNO", (1110.2, 429.8), (0.0, 0.0), {"cor": (255, 255, 255)}),
                           ("JARDIM", (1264.6, 642.3), (0.0, 0.0), {"cor": (255, 255, 255)})]},
    "Subsolo": {"render": "renders/POE642_CasaB_PH_Subsolo_ajustes.png",
                "aprovada": "renders/POE642_CasaB_PH_Subsolo_final_2000.png",
                "original": "renders/POE642_CasaB_PH_Subsolo_final.png",
                "pdf": "642 - SUBSOLO - CASA B.pdf",
                "sem_tela": "bases/POE642_CasaB_BASE_Subsolo_v3_texturas.png",
                "chapada": "bases/POE642_CasaB_BASE_Subsolo_v2_16x9.png",
                "ajustes": [("BH SERVIÇO", (741.0, 216.0), (-4.0, -15.0), {"corpo": 1.0, "quebra": ["BH", "SERVIÇO"]})]},   # da bacia (item 9)
}
# quadro comum de 2000 px -> imagem de partida (SIFT da base 16:9 contra a imagem, como o rodape_entrega): o Térreo é o
# render de 2000 x 1116, deslocado ~4,5 px; o Subsolo é o próprio quadro
AFIM_QR_B = {"Terreo": ((0.999784, 0.000238, 0.185995), (0.000272, 0.999588, -4.48606)),     # 291 pontos, 0,45 px
             "Subsolo": ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0))}


def base_b(forma, chave="Terreo"):
    """A base chapada da legenda da Casa B (v2: as cores dos materiais), levada à imagem pelo quadro comum."""
    base = cv2.imread(str(CASA_B / PAVIMENTOS_B[chave]["chapada"]))
    b2 = cv2.resize(base, (2000, round(base.shape[0] * 2000 / base.shape[1])), interpolation=cv2.INTER_NEAREST)
    return cv2.warpAffine(b2, np.float32(AFIM_QR_B[chave]), (forma[1], forma[0]), flags=cv2.INTER_NEAREST,
                          borderValue=(255, 255, 255))


def contexto():
    """As rotinas da Casa A passam a ler a Casa B."""
    A.CONFIG = CONFIG_B
    A.CASA = CASA_B
    A.PAVIMENTOS = PAVIMENTOS_B
    AJ.CASA = CASA_B
    AJ.APROVADAS = {k: CASA_B / v["aprovada"] for k, v in PAVIMENTOS_B.items()}
    AJ.AFIM_QR = AFIM_QR_B
    AJ.base_terreo = base_b
    AJ.GRAMA_A = dict(AJ.GRAMA_A, lote=GRAMA_B["lote"], amostra=GRAMA_B["amostra"])
    AJ.VEG_A = dict(AJ.VEG_A, **VEG_B)
    AJ.gramado_plantas = gramado_plantas_b
    AJ.GRANITO_A = dict(AJ.GRANITO_A, cor_base=GRANITO_B)
    AJ.PEDRA_A = dict(AJ.PEDRA_A, granito_base=GRANITO_B,
                      mascara=CASA_B / "renders/POE642_CasaB_PH_Terreo_pedra_mascara.png")


def px_por_m(chave):
    _, p2r = AJ.pdf_pavimento(chave)
    (a, b), (c, d) = p2r(0, 0), p2r(56.69, 0)                   # 1 m na escala 1:50 = 56,69 pt
    return float(np.hypot(c - a, d - b))


# ---------------------------------------------------------------------------------------------------------------------
# Peças da Casa B (sem rotina na Casa A). Coordenadas: pt do PDF da Casa B, ou px da imagem de partida (2000).
# ---------------------------------------------------------------------------------------------------------------------
def ret_px(p2r, r):
    (x0, y0), (x1, y1) = p2r(r[0], r[1]), p2r(r[2], r[3])
    return min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)


def ret_aa(forma, r):
    from retoque_terreo_casae import poligono_aa
    x0, y0, x1, y1 = r
    return poligono_aa(forma, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)])


def contorno_aa(forma, r, larg):
    from retoque_terreo_casae import linha_aa
    x0, y0, x1, y1 = r
    return linha_aa(forma, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], larg, fechada=True)


def sombra_de(alfa, px_m, forca=0.35, dist_m=0.05, sig_m=0.04):
    """A sombra curta de uma peça (alfa 0 a 1): para baixo e à esquerda (luz do alto à direita), fora da peça."""
    d = dist_m * px_m
    sh = cv2.warpAffine(alfa, np.float32([[1, 0, -d], [0, 1, d]]), alfa.shape[::-1])
    return np.clip(cv2.GaussianBlur(sh, (0, 0), max(0.5, sig_m * px_m)) * (1 - alfa), 0, 1) * forca


def pousar_rgba(img, cor, a, cx, cy, giro=0):
    """O bloco (BGR, alfa 0 a 1) com o centro em (cx, cy), girado `giro` graus (múltiplos de 90), em img (float32)."""
    for _ in range((giro // 90) % 4):
        cor, a = cv2.rotate(cor, cv2.ROTATE_90_CLOCKWISE), cv2.rotate(a, cv2.ROTATE_90_CLOCKWISE)
    h, w = a.shape
    x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(img.shape[1], x0 + w), min(img.shape[0], y0 + h)
    al = a[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0, None]
    img[Y0:Y1, X0:X1] = img[Y0:Y1, X0:X1] * (1 - al) + cor[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0] * al
    return img


# Térreo 12 (R8, parte 2): o X tracejado que o motor desenhou no hall interno, em volta do pufe (o contorno do jardim de
# inverno repetido um módulo abaixo, com as duas verticais): não está no PDF. As linhas foram achadas no render (Hough);
# o travertino volta copiado de 6 a 12 px ao lado (o veio corre na vertical), e no pufe, inpaint.
HALL_X = {"linhas": [((1057, 487), (1173, 614)), ((1058, 613), (1173, 484)),
                     ((1057.5, 488), (1057.5, 610)), ((1172.5, 488), (1172.5, 610))],
          "y": (488, 610), "faixa": 2.2, "escuro": 5, "desloc": (6, -6, 9, -9, 12, -12)}


def hall_sem_x(out):
    q = HALL_X
    H, W = out.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    perto = np.zeros((H, W), bool)
    for (ax, ay), (bx, by) in q["linhas"]:
        dx, dy = bx - ax, by - ay
        n = np.hypot(dx, dy)
        dist = np.abs((xx - ax) * dy - (yy - ay) * dx) / n
        t = ((xx - ax) * dx + (yy - ay) * dy) / n ** 2
        perto |= (dist <= q["faixa"]) & (t >= -0.02) & (t <= 1.02)
    y0, y1 = q["y"]
    perto[:y0] = False
    perto[y1:] = False
    Y = out.astype(np.float32).mean(axis=2)
    med = cv2.medianBlur(out, 7).astype(np.float32).mean(axis=2)
    m = perto & (med - Y > q["escuro"])
    m = cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & perto
    img = out.copy()
    falta = m.copy()
    for d in q["desloc"]:
        ys, xs = np.nonzero(falta)
        sx = np.clip(xs + d, 0, W - 1)
        ok = ~m[ys, sx] & (np.abs(out[ys, sx].astype(int) - med[ys, xs, None]).max(axis=1) < 18)
        img[ys[ok], xs[ok]] = out[ys[ok], sx[ok]]
        falta[ys[ok], xs[ok]] = False
    if falta.any():
        img = cv2.inpaint(img, falta.astype(np.uint8), 3, cv2.INPAINT_TELEA)
    print(f"    hall: {int(m.sum())} px do X e das verticais tracejadas do motor ({int(falta.sum())} por inpaint)")
    return img


# Térreo 1 (seção 10, R1), jardim de inverno: as plantas do motor (leques de palmeira de ~2,2 m, folhas de ~1,5 m) saem;
# a floreira (o miolo entre os vidros do PDF) fica em terra escura e recebe as plantas da biblioteca, no tamanho real,
# saindo levemente dela. O X tracejado da abertura entra depois, nas projeções (item 12).
JARDIM_INV = {"pt": (1820.5, 932.0, 2002.0, 1120.0), "terra": (52, 62, 74), "terra_ruido": 0.10,
              "plantas": [("costela_de_adao", 0.90, (0.28, 0.25), 0), ("dieffenbachia", 0.95, (0.72, 0.22), 90),
                          ("palmeira_2", 1.30, (0.50, 0.52), 0), ("planta_folhas_largas", 0.85, (0.25, 0.78), 180),
                          ("costela_de_adao", 0.90, (0.76, 0.80), 270), ("planta_flores", 0.70, (0.52, 0.86), 0),
                          ("planta_flores", 0.60, (0.85, 0.50), 90), ("arbusto_2", 0.80, (0.17, 0.52), 0)],
          "transbordo_m": 0.10, "semente": 21,
          "forracao": {"nomes": ["arbusto_1", "arbusto_2", "arbusto_3"], "d_m": (0.40, 0.60), "passo_m": 0.42, "tom": 0.92}}


def planta_sprite(nome, d_m, px_m):
    """(BGR, alfa, diâmetro em px) de uma planta da biblioteca: as da planta de referência (_texturas/vegetacao) ou os
    blocos de paisagismo (_blocos), levada ao diâmetro d_m."""
    import json as _json
    sys.path.insert(0, str(RAIZ / "_texturas"))
    sys.path.insert(0, str(RAIZ / "_blocos"))
    if (RAIZ / "_texturas" / "vegetacao" / f"{nome}.png").exists():
        from retoque_terreo_casae import sprite_referencia
        cor, a, dm = sprite_referencia(nome, px_m)
        f = d_m / dm
    else:
        import blocos
        cor, a = blocos.bloco(nome, px_m)
        f = d_m * px_m / max(a.shape)
    cor = cv2.resize(cor, None, fx=f, fy=f, interpolation=cv2.INTER_AREA)
    a = cv2.resize(a, None, fx=f, fy=f, interpolation=cv2.INTER_AREA)
    return cor.astype(np.float32), np.clip(a, 0, 1).astype(np.float32), d_m * px_m


OBJETOS_PDF = ("ARQ_PAREDE", "ARQ_BANCADAS", "ARQ_LOUÇAS E METAIS", "ARQ_MOBILIÁRIO", "ARQ_LAYOUT HUMANIZAÇÃO",
               "ARQ_ELEMENTOS FIXOS", "ARQ - Marcenaria", "EST_PILAR")


def mascara_pdf(chave, forma, camadas=OBJETOS_PDF, folga=2, filtro=None, ss=4):
    """Os preenchimentos das camadas do PDF (paredes, vidros, louças, bancadas, móveis...) na imagem, com `folga` px."""
    pg, p2r = AJ.pdf_pavimento(chave)
    H, W = forma
    m = np.zeros((H * ss, W * ss), np.uint8)
    for d in pg.get_drawings():
        if d.get("layer") not in camadas or d["type"] not in ("f", "fs") or (filtro and not filtro(d)):
            continue
        for poli in AJ.caminhos_pdf(d, p2r):
            if len(poli) >= 3:
                cv2.fillPoly(m, [np.int32(np.round(np.float64(poli) * ss))], 255)
    m = cv2.resize(m, (W, H), interpolation=cv2.INTER_AREA) > 40
    if folga:
        m = cv2.dilate(m.astype(np.uint8), np.ones((2 * folga + 1,) * 2, np.uint8)).astype(bool)
    return m


def restos_de_folha(img, regiao, base, px_m, alcance_m=0.9, protegido=None):
    """As folhas do motor que passaram para fora de uma floreira ou jardim (regiao: bool, o miolo): na faixa de
    `alcance_m` em volta, os px verdes ou verde-escuros (não as paredes pretas nem o branco) saem por inpaint (a cópia
    do material ao lado, como na Casa A, trazia pedaços dos vidros da floreira)."""
    k = 2 * int(round(alcance_m * px_m)) + 1
    faixa = cv2.dilate(regiao.astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool) & ~regiao
    f = cv2.GaussianBlur(img, (0, 0), 0.6)
    b, g, r = f[..., 0], f[..., 1], f[..., 2]
    lum = f.mean(axis=2)
    folha = faixa & (g >= r - 2) & (g >= b - 4) & (lum < 175) & (lum > 42)
    # e o que foge do material da base na faixa (as folhas acinzentadas, na sombra): por material, a mediana do
    # próprio render na faixa larga; foge quem passa de `desvio` dela (fora as paredes pretas e as linhas da base)
    ch = base.astype(np.int32)
    chave = ch[..., 0] * 65536 + ch[..., 1] * 256 + ch[..., 2]
    larga = cv2.dilate(faixa.astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool) & ~regiao
    for c in np.unique(chave[faixa]):
        mc = chave == c
        if (mc & larga).sum() < 200 or ch[mc][0].max() < 60:
            continue
        med = np.median(f[mc & larga], axis=0)
        foge = faixa & mc & (np.abs(f - med).max(axis=2) > 32) & (lum > 42)
        folha |= foge if protegido is None else foge & ~protegido
    folha = cv2.morphologyEx(folha.astype(np.uint8), cv2.MORPH_OPEN, np.ones((2, 2), np.uint8)).astype(bool)
    folha = cv2.dilate(folha.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & faixa & (lum > 42)
    if folha.any():
        # inpaint: o piso volta liso no tom do lugar, e o desenho dele vem com a troca de textura dos itens de piso
        img = cv2.inpaint(np.clip(img, 0, 255).astype(np.uint8), folha.astype(np.uint8), 3,
                          cv2.INPAINT_TELEA).astype(np.float32)
    return img, int(folha.sum())


def canteiro(out, alfa, caixa, q, px_m, nome):
    """Um canteiro (alfa: o miolo, 0 a 1; caixa: x0, y0, x1, y1 em px) com as plantas da biblioteca no tamanho real: as
    folhas do motor fora dele saem, o miolo fica em terra escura com a forração por baixo e as plantas de `q` por cima,
    saindo até `transbordo_m` dele."""
    import json as _json
    from retoque_terreo_casae import pousar_planta
    x0, y0, x1, y1 = caixa
    H, W = out.shape[:2]
    img = out.astype(np.float32)
    dentro = alfa > 0.5
    # 1. as folhas do motor fora do canteiro (sobre os móveis, os vidros e os pisos em volta)
    img, n_fora = restos_de_folha(img, dentro, AJ.base_terreo((H, W)), px_m,
                                  protegido=mascara_pdf("Terreo", (H, W), folga=1))
    # 2. a terra: o miolo, com um grão leve
    rng = np.random.default_rng(q["semente"])
    gr = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 0.7)
    terra = np.float32(q["terra"])[None, None] * (1 + q["terra_ruido"] * gr / max(gr.std(), 1e-6))[..., None]
    img = img * (1 - alfa[..., None]) + terra * alfa[..., None]
    sombra = _json.loads((RAIZ / "_texturas" / "texturas.json").read_text())["vegetacao"]["sombra"]
    t = max(1, int(round(q["transbordo_m"] * px_m)))
    lim = cv2.GaussianBlur(cv2.dilate(dentro.astype(np.uint8), np.ones((2 * t + 1,) * 2, np.uint8)).astype(np.float32),
                           (0, 0), 0.6)
    fundo = img.copy()
    # 3. a forração: touceiras baixas de 0,4 a 0,6 m numa grade com sorteio, por baixo de tudo
    fx = q["forracao"]
    n = 0
    passo = fx["passo_m"] * px_m
    for cy in np.arange(y0 + passo / 2, y1, passo):
        for cx in np.arange(x0 + passo / 2, x1, passo):
            if not dentro[min(int(cy), H - 1), min(int(cx), W - 1)]:
                continue
            nome_f = fx["nomes"][int(rng.integers(len(fx["nomes"])))]
            cor, al, d_px = planta_sprite(nome_f, float(rng.uniform(*fx["d_m"])), px_m)
            for _ in range(int(rng.integers(4))):
                cor, al = cv2.rotate(cor, cv2.ROTATE_90_CLOCKWISE), cv2.rotate(al, cv2.ROTATE_90_CLOCKWISE)
            pousar_planta(fundo, cor * fx["tom"], al, cx + rng.uniform(-0.3, 0.3) * passo,
                          cy + rng.uniform(-0.3, 0.3) * passo, d_px, sombra)
            n += 1
    # 4. as plantas maiores, as menores primeiro (por baixo)
    for nome_p, d_m, (px_, py_), giro in sorted(q["plantas"], key=lambda p: p[1]):
        cor, al, d_px = planta_sprite(nome_p, d_m, px_m)
        for _ in range(giro // 90):
            cor, al = cv2.rotate(cor, cv2.ROTATE_90_CLOCKWISE), cv2.rotate(al, cv2.ROTATE_90_CLOCKWISE)
        pousar_planta(fundo, cor, al, x0 + px_ * (x1 - x0), y0 + py_ * (y1 - y0), d_px, sombra)
    img = img * (1 - lim[..., None]) + fundo * lim[..., None]
    print(f"    {nome}: {n_fora} px de folhas do motor fora do canteiro refeitos; terra no miolo "
          f"({x1 - x0:.0f} x {y1 - y0:.0f} px), {n} touceiras de forração e {len(q['plantas'])} plantas da biblioteca, "
          f"no tamanho real, saindo até {q['transbordo_m']:.2f} m do canteiro")
    return np.clip(img, 0, 255).astype(np.uint8)


def jardim_inverno(out):
    q = JARDIM_INV
    _, p2r = AJ.pdf_pavimento("Terreo")
    x0, y0, x1, y1 = ret_px(p2r, q["pt"])
    return canteiro(out, ret_aa(out.shape[:2], (x0, y0, x1, y1)), (x0, y0, x1, y1), q, px_por_m("Terreo"),
                    "jardim de inverno")


# Térreo 1 (seção 10, R1), o JARDIM de 4,62 m² do PDF, entre o hall e a garagem: o verde da base, cercado pelo vidro do
# hall, pelas paredes e pelo portão da garagem. As duas plantas do motor (folhas de ~1,9 m) saem; o canteiro fica como o
# jardim de inverno (terra, forração e as plantas da biblioteca no tamanho real). O miolo é a mancha do verde da base ali.
JARDIM_HALL = {"ponto": (1265, 640), "terra": (52, 62, 74), "terra_ruido": 0.10,
               "plantas": [("costela_de_adao", 0.85, (0.14, 0.45), 0), ("planta_folhas_largas", 0.80, (0.40, 0.40), 90),
                           ("dieffenbachia", 0.80, (0.66, 0.50), 0), ("costela_de_adao", 0.75, (0.88, 0.42), 180),
                           ("planta_flores", 0.55, (0.28, 0.72), 0), ("planta_flores", 0.50, (0.78, 0.74), 90)],
               "transbordo_m": 0.08, "semente": 23,
               "forracao": {"nomes": ["arbusto_1", "arbusto_2", "arbusto_3"], "d_m": (0.40, 0.55), "passo_m": 0.40,
                            "tom": 0.92}}


def jardim_hall(out):
    q = JARDIM_HALL
    H, W = out.shape[:2]
    verde = (np.abs(AJ.base_terreo((H, W)).astype(np.int32) - np.array(GRAMA_B["cor_base"])).max(axis=2)
             <= GRAMA_B["tol"]).astype(np.uint8)
    _, lab = cv2.connectedComponents(verde, connectivity=4)
    m = (lab == lab[q["ponto"][1], q["ponto"][0]]).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    ys, xs = np.nonzero(m)
    alfa = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.5)
    return canteiro(out, alfa, (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1), q, px_por_m("Terreo"),
                    "jardim de 4,62 m² do hall")


# Térreo 6 e 1 (R1, R4, seção 10): a grama e a vegetação do gramado na escala da referência, pelas rotinas do pente fino
# da Casa A (`ajustes_casaa.grama_escala` e `vegetacao_a`, itens 7 e 6 de lá): a grama da referência (manchas suaves de 0,5
# a 1 m), com a luz e as sombras do lugar; as manchas de plantas do motor (1,5 a 3 vezes o tamanho real) saem, as folhas
# que passavam do muro, do lote e para os pisos voltam ao material de cada lugar, e entram as plantas da planta de
# referência, no tamanho real, com a copa dentro do verde. O que muda da Casa A:
# - o gramado: lá, o branco do lote na base; aqui, o verde da legenda (#6E9150). `gramado_plantas_b` dá à rotina da Casa A
#   uma base em que o verde é o branco;
# - o lote: o muro (as linhas pretas) só em cima e embaixo (linhas 45-51 e 973-978); dos lados, a linha fina do lote
#   (x 156 e 1829), e fora do lote o branco, com a linha tracejada da divisa (`linhas_da_divisa`), que volta inteira.
GRAMA_B = {"lote": (156, 45, 1830, 979), "amostra": (1500, 390, 1820, 480), "cor_base": (80, 145, 110), "tol": 10}
VEG_B = {"muro": {"cima": ((40, 56), (700, 1000)), "baixo": ((968, 984), (1200, 1600))}, "muro_x": (156, 1830),
         "muro_y": (45, 979)}
_GRAMADO_A = AJ.gramado_plantas


def gramado_plantas_b(out):
    real = AJ.base_terreo

    def base_gramado(forma, chave="Terreo"):
        b2 = real(forma, chave).copy()
        verde = np.abs(b2.astype(np.int32) - np.array(GRAMA_B["cor_base"])).max(axis=2) <= GRAMA_B["tol"]
        b2[b2.min(axis=2) >= 250] = 240
        b2[verde] = 255
        return b2
    AJ.base_terreo = base_gramado
    try:
        return _GRAMADO_A(out)
    finally:
        AJ.base_terreo = real


# a linha tracejada da divisa do terreno, fora do muro (linhas e colunas da imagem): em cima, embaixo e dos lados
DIVISA = {"linhas": (9, 10, 1046, 1047), "colunas": (155, 156, 1866, 1867)}


def linhas_da_divisa(out, orig):
    """A linha tracejada da divisa: onde o ajuste a apagou (as plantas passavam por cima dela, ou o branco de fora do lote
    a levou), volta como era; onde a planta a cobria, pelo padrão do próprio traço, um período (ou mais) adiante."""
    H, W = out.shape[:2]
    my0, my1 = VEG_B["muro_y"]
    o = orig.astype(np.int32)
    limpo = ((o.max(axis=2) - o.min(axis=2) < 12) & (o.mean(axis=2) < 236)) | (o.min(axis=2) >= 248)
    n = 0
    for eixo, idx in ((1, DIVISA["linhas"]), (0, DIVISA["colunas"])):
        for i in idx:
            pega = (lambda m: m[i]) if eixo == 1 else (lambda m: m[:, i])
            lo, lf, li = pega(orig), pega(out), pega(limpo).copy()
            valido = np.ones(len(li), bool)
            if eixo == 0:
                valido[my0 - 1:my1 + 1] = False                 # dentro do lote, a coluna é a borda da grama
            # o período do tracejado (autocorrelação nos trechos limpos)
            v = lo.mean(axis=1).astype(np.float32)
            ok = li & valido
            v = np.where(ok, v - v[ok].mean(), 0)
            ac = np.correlate(v, v, "full")[len(v) - 1:]
            per = int(np.argmax(ac[6:120])) + 6
            mudou = np.abs(lf.astype(int) - lo.astype(int)).max(axis=1) > 0
            volta = mudou & li & valido
            lf[volta] = lo[volta]
            n += int(volta.sum())
            for j in np.nonzero(mudou & ~li & valido)[0]:
                for k in range(1, 80):
                    s_ = next((t for t in (j - k * per, j + k * per) if 0 <= t < len(li) and li[t] and valido[t]), None)
                    if s_ is not None:
                        lf[j] = lo[s_]
                        n += 1
                        break
    return n


def restos_nos_pisos(img, planta, gramado, px_m, alcance_m=2.6, desvio=28):
    """As sobras das plantas do motor nos pisos em volta do gramado (o contorno das folhas e as sombras que a cópia do
    material deixava na pedra e no granito): no alcance das manchas, o que foge da mediana do material (por cor da base)
    sai por inpaint; os objetos do PDF e as paredes ficam. A pedra e o granito são refeitos depois (itens 2 e 3)."""
    H, W = img.shape[:2]
    mx0, mx1 = VEG_B["muro_x"]
    my0, my1 = VEG_B["muro_y"]
    dentro = np.zeros((H, W), bool)
    dentro[my0 + 7:my1 - 6, mx0:mx1] = True
    k = 2 * int(round(alcance_m * px_m)) + 1
    alcance = cv2.dilate(planta.astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool) & ~gramado & dentro
    larga = cv2.dilate(alcance.astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool)
    base = AJ.base_terreo((H, W)).astype(np.int32)
    chave = base[..., 0] * 65536 + base[..., 1] * 256 + base[..., 2]
    protegido = mascara_pdf("Terreo", (H, W), folga=1)
    f = cv2.GaussianBlur(img.astype(np.float32), (0, 0), 0.6)
    b, g, r = f[..., 0], f[..., 1], f[..., 2]
    lum = f.mean(axis=2)
    sobra = np.zeros((H, W), bool)
    for c in np.unique(chave[alcance]):
        mc = chave == c
        if (mc & larga & ~alcance).sum() < 300 or base[mc][0].max() < 60 or base[mc][0].min() >= 250:
            continue
        med = np.median(f[mc & larga & ~alcance], axis=0)
        foge = (np.abs(f - med).max(axis=2) > desvio) | ((g > r + 4) & (g > b + 12))
        sobra |= alcance & mc & foge & (lum > 50)
    sobra &= ~protegido
    sobra = cv2.dilate(sobra.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & alcance & ~protegido
    if sobra.any():
        img = cv2.inpaint(img, sobra.astype(np.uint8), 4, cv2.INPAINT_TELEA)
    return img, int(sobra.sum())


def grama_terreo(out):
    return AJ.grama_escala(out)


def vegetacao_terreo(out):
    aprovada = cv2.imread(str(AJ.APROVADAS["Terreo"]))
    out = AJ.vegetacao_a(out)
    px_m = px_por_m("Terreo")
    gramado, _, planta, _, _, _ = gramado_plantas_b(aprovada)
    n, lab, st, _ = cv2.connectedComponentsWithStats((planta & gramado).astype(np.uint8), 8)
    planta = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= AJ.VEG_A["mancha_min"]])
    out, n_sobra = restos_nos_pisos(out, planta, gramado, px_m)
    # fora do lote: o vulto claro que a sombra das plantas deixava (já quase branco) também sai
    H, W = out.shape[:2]
    mx0, mx1 = VEG_B["muro_x"]
    my0, my1 = VEG_B["muro_y"]
    fora = np.ones((H, W), bool)
    fora[my0:my1, mx0:mx1] = False
    perto = cv2.dilate(planta.astype(np.uint8), np.ones((121, 121), np.uint8)).astype(bool)
    vulto = fora & perto & (out.min(axis=2) >= 200) & (out.min(axis=2) < 255)
    out[vulto] = 255
    n_div = linhas_da_divisa(out, aprovada)
    print(f"    sobras das plantas do motor nos pisos em volta: {n_sobra} px; vulto claro fora do lote: {int(vulto.sum())} "
          f"px; linha tracejada da divisa refeita em {n_div} px")
    return out


class chave_como:
    """As rotinas da Casa A que leem um pavimento fixo (o "1Pavimento" do vinílico, o "Terreo" de várias) passam a ler
    `para` quando pedem `de`."""
    def __init__(self, de, para):
        self.de, self.para = de, para

    def __enter__(self):
        self.pdf, self.base = AJ.pdf_pavimento, AJ.base_terreo
        de, para, pdf, base = self.de, self.para, self.pdf, self.base
        AJ.pdf_pavimento = lambda c: pdf(para if c == de else c)
        AJ.base_terreo = lambda forma, c="Terreo": base(forma, para if c == de else c)
        return self

    def __exit__(self, *_):
        AJ.pdf_pavimento, AJ.base_terreo = self.pdf, self.base


# Térreo 3 (seção 3): o granito marrom da referência do usuário (nuvens suaves e lascas de agregado de vários tamanhos, no
# tom ~118, 89, 69), como o item 10 do pente fino da Casa A (`ajustes_casaa.granito_referencia_a`); muda só a cor do
# granito na legenda da Casa B (#5A4232).
GRANITO_B = (50, 66, 90)


def granito_terreo(out):
    return AJ.granito_referencia_a(out)


# Térreo 4 e Subsolo 3 (R1, seção 3): o travertino na escala, com o veio horizontal de 5 a 20 cm (as estrias verticais
# contínuas de vários metros do motor saem). O desenho é o do travertino aprovado da Casa A (o mesmo do item 7 do
# Subsolo de lá, `ajustes_casaa.TRAV_SUB`: trechos do Térreo da Casa A com os ajustes, tecidos com espelhos para o veio
# ficar na horizontal), na luz do lugar (`retexturizar`, com a força e o raio de lá). O piso é a mancha do travertino da
# legenda (#DCD9CA), menos os objetos do PDF (paredes, louças, bancadas, móveis, com 2 px); o que foge da luz do lugar
# (tapetes, móveis e sombras do render) fica.
TRAV_B = {"cor_base": (202, 217, 220), "tol": 6, "area_min": 1000, "fechar": 3, "folga": 2, "forca": 1.4,
          "sig_m": 1.0, "borda": {"sig": 1.5, "peso": 0.15}}


def travertino_b(out, chave):
    from retoque_bege_bahia_terreo import quilting
    from texturas_escala import retexturizar, nconv
    q, t = TRAV_B, AJ.TRAV_SUB
    H, W = out.shape[:2]
    bb = AJ.base_terreo((H, W), chave).astype(np.int32)
    trav = (np.abs(bb - np.array(q["cor_base"])).max(axis=2) <= q["tol"]).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(trav, 8)
    m = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= q["area_min"]])
    k = q["fechar"]
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((k, k), np.uint8)).astype(bool)
    m &= ~mascara_pdf(chave, (H, W), folga=q["folga"])
    fonte = cv2.imread(str(t["fonte"])).astype(np.float32)
    fontes = [fonte[y0:y1, x0:x1] for x0, y0, x1, y1 in t["trechos"]]
    fontes += [f[:, ::-1] for f in fontes] + [f[::-1] for f in fontes]

    def tecido(h, w):
        return quilting(fontes, h, w, p=t["p"], sobra=t["sobra"], candidatos=t["candidatos"],
                        rng=np.random.default_rng(t["semente"]))[:h, :w]
    px_m = px_por_m(chave)
    antes = out
    out, npx = retexturizar(out, m, "travertino", px_m, forca=q["forca"], sig_m=q["sig_m"], pronta=tecido, fugir=True)
    b = q["borda"]
    novo = (out != antes).any(axis=2) & m
    resto = m & ~novo & (cv2.GaussianBlur(novo.astype(np.float32), (0, 0), b["sig"]) >= b["peso"])
    out[resto] = np.clip(nconv(out.astype(np.float32), novo.astype(np.float32), b["sig"])[resto], 0, 255).astype(np.uint8)
    print(f"    travertino: {npx} px no desenho do travertino aprovado (veio horizontal), a {px_m:.2f} px/m, e "
          f"{int(resto.sum())} px da borda; ficam os objetos do PDF e o que foge da luz do lugar")
    return out


def travertino_terreo(out):
    return travertino_b(out, "Terreo")


# Térreo 5 (R4): o vinílico em réguas de ~20 cm, claras, em tons alternados, deitadas como desenha o PDF, como o item 11
# do 1º Pavimento da Casa A (`ajustes_casaa.vinilico_1pav`, com os números de lá, `retoque_1pav_casae.VINILICO`); muda
# a cor do vinílico na legenda da Casa B (#C8A27C). Suítes, closet master, sala íntima e circulação.
VINILICO_B = (124, 162, 200)


def vinilico_b(out, chave):
    import retoque_1pav_casae as R1P
    cor = R1P.VINILICO["cor_chapada"]
    R1P.VINILICO["cor_chapada"] = VINILICO_B
    try:
        with chave_como("1Pavimento", chave):
            return AJ.vinilico_1pav(out)
    finally:
        R1P.VINILICO["cor_chapada"] = cor


def vinilico_terreo(out):
    return vinilico_b(out, "Terreo")


# Térreo 7 (R12): os três carros do PDF (ARQ_LAYOUT HUMANIZAÇÃO) em prata, iguais, de 4,70 x 1,85 m, alinhados. Como o
# pente fino da Casa A (`ajustes_casaa.carros_r12_a`: o modelo levado ao prata da Casa E pela luminância, na escala, no
# centro de cada carro do PDF, os três na mesma linha, com a sombra curta). O que muda: o piso da garagem é a pedra
# portuguesa (na Casa A, granito), então os carros do motor são achados pelo que não é caramelo (R - B < 35: branco,
# prata e grafite; as lanternas ficam por dentro) e saem para a pedra tecida de trechos limpos do acesso, na luz do lugar
# (a pedra inteira é redesenhada no item 2). O modelo é o carro do meio (o prata).
CARROS_B = {"janela": (1150, 690, 1450, 875), "neutro": 35, "fecho": 7, "area_min": 4000, "folga": 7, "modelo": 1,
            "fontes_pedra": [(1480, 880, 1600, 950), (1640, 880, 1790, 950)],
            "centros_pdf": [(2125.85, 1663.8), (2283.9, 1663.8), (2435.3, 1663.8)]}


def carros_b(out):
    from scipy import ndimage
    from retoque_bege_bahia_terreo import quilting
    from texturas_escala import nconv
    q = CARROS_B
    wx0, wy0, wx1, wy1 = q["janela"]
    reg = out[wy0:wy1, wx0:wx1].astype(np.float32)
    car = (reg[..., 2] - reg[..., 0]) < q["neutro"]
    m = cv2.morphologyEx(car.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((q["fecho"],) * 2, np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    ids = sorted([i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= q["area_min"]
                  and st[i, cv2.CC_STAT_WIDTH] >= 40 and st[i, cv2.CC_STAT_HEIGHT] >= 100], key=lambda i: cen[i, 0])
    sil = [ndimage.binary_fill_holes(lab == i) for i in ids]
    assert len(sil) == len(q["centros_pdf"]), f"{len(sil)} carros achados"
    tudo = np.zeros(m.shape, bool)
    for s_ in sil:
        tudo |= s_
    # a sombra do carro do motor (o caramelo escurecido em volta) sai com ele
    sai = np.zeros(out.shape[:2], bool)
    sai[wy0:wy1, wx0:wx1] = cv2.dilate(tudo.astype(np.uint8), np.ones((2 * q["folga"] + 1,) * 2, np.uint8)) > 0
    im = out.astype(np.float32)
    lum = im.mean(axis=2)
    pedra = (np.abs(AJ.base_terreo(out.shape[:2]).astype(np.int32) - np.array(AJ.PEDRA_A["cor_base"])).max(axis=2) <= 6)
    piso = pedra & ~cv2.dilate(sai.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool) & (lum > 60)
    med = cv2.medianBlur(out, 5).astype(np.float32)
    campo = nconv(med, piso.astype(np.float32), 12)
    fontes = []
    for fx0, fy0, fx1, fy1 in q["fontes_pedra"]:
        f = im[fy0:fy1, fx0:fx1] / cv2.GaussianBlur(med[fy0:fy1, fx0:fx1], (0, 0), 6)
        f = f / f.reshape(-1, 3).mean(axis=0)
        fontes += [np.ascontiguousarray(v) for v in (f, f[:, ::-1], f[::-1, :], f[::-1, ::-1])]
    tex = quilting(fontes, wy1 - wy0, wx1 - wx0, p=14, sobra=5, candidatos=400, rng=np.random.default_rng(653))
    novo = im.copy()
    novo[wy0:wy1, wx0:wx1] = tex[:wy1 - wy0, :wx1 - wx0] * campo[wy0:wy1, wx0:wx1]
    sai &= pedra
    a = (cv2.GaussianBlur(sai.astype(np.float32), (0, 0), 1.0) * sai)[..., None]
    out = np.clip(im * (1 - a) + novo * a, 0, 255).astype(np.uint8)
    print(f"    carros do motor fora: {int(sai.sum())} px de pedra tecida no lugar (com a sombra deles)")
    AJ.CARROS_A = dict(AJ.CARROS_A, janela=q["janela"],
                       r12=dict(AJ.CARROS_A["r12"], modelo=q["modelo"], centros_pdf=q["centros_pdf"]))
    return AJ.carros_r12_a(out, reg, sil[q["modelo"]])


# Térreo 10 (R14): as escadas com a linha suave nos bocéis, a sombra curta no degrau de baixo e o triângulo de 24 x 26 cm
# no topo, apontando a descida, sem traço preto nem seta (`retoque_terreo_casae.escada_linhas`, como a do deck da Casa
# A). No Térreo as duas descem ("D" do PDF): a de 6 degraus da pedra grande (à esquerda) para a ducha do Subsolo, e a de
# 9 degraus da varanda (à direita) para o deck em L. Antes, os traços e as setas do motor saem (mediana em x e em y na
# caixa da escada, como na Casa A). Pisos, bocéis e caixa: os da ARQ_ESCADAS E RAMPAS do PDF (pt).
ESCADAS_T = [{"nome": "de 6 degraus, da pedra grande para a ducha", "pdf": (516.2, 793.6, 602.9, 881.5),
              "bocels": [534.9, 551.9, 568.9, 585.9], "corte": None, "baixo": "direita", "inicio": "esquerda",
              "mediana": (7, 5)},
             {"nome": "de 9 degraus, da varanda para o deck em L", "pdf": (728.8, 963.7, 917.6, 1071.4),
              "bocels": [752.2, 775.6, 799.0, 822.3, 845.7, 869.1, 892.5], "corte": None, "baixo": "esquerda",
              "inicio": "direita", "mediana": (7, 9)}]


def escadas_b(out, chave, escadas):
    from retoque_terreo_casae import escada_linhas
    _, p2r = AJ.pdf_pavimento(chave)
    for e in escadas:
        (a, b), (c, d) = p2r(e["pdf"][0], e["pdf"][1]), p2r(e["pdf"][2], e["pdf"][3])
        x0, y0, x1, y1 = int(np.floor(a)), int(np.floor(b)), int(np.ceil(c)), int(np.ceil(d))
        mx, my = e["mediana"]
        reg = out[y0 - my:y1 + my, x0 - mx:x1 + mx]
        lim = np.empty_like(reg)
        for ch in range(3):                                  # mediana em x (os bocéis), depois em y (a seta)
            c_ = reg[..., ch].astype(np.float32)
            c_ = np.median(np.stack([np.roll(c_, k, axis=1) for k in range(-(mx // 2), mx // 2 + 1)]), axis=0)
            hy = np.stack([np.roll(c_, k, axis=0) for k in range(-(my // 2), my // 2 + 1)])
            lim[..., ch] = np.clip(np.median(hy, axis=0), 0, 255).astype(np.uint8)
        out[y0:y1, x0:x1] = lim[my:my + (y1 - y0), mx:mx + (x1 - x0)]
        out = escada_linhas(out, None, e, p2r=p2r)
    return out


def escadas_terreo(out):
    return escadas_b(out, "Terreo", ESCADAS_T)


# Térreo 9 (R3): as portas sem os arcos do PDF (as ~25 de giro e a pivotante do hall); ficam as folhas e os batentes.
# Como o 1º Pavimento da Casa A (`ajustes_casaa.sem_arcos_pdf`, com a busca de lá, `SEM_ARCOS_1PAV`): o traço sai numa
# faixa de 4 px por inpaint que não puxa a parede nem as linhas retas, e uma segunda passada refaz o arco do render
# fora do lugar do PDF.
def sem_arcos_terreo(out):
    return AJ.sem_arcos_pdf(out, "Terreo", AJ.SEM_ARCOS_1PAV)


# Térreo 11 (R8): os 2 pilares redondos da EST_PILAR, no bloco do motorista (nas paredes do depósito e do banho), em
# preto como as paredes, no diâmetro do PDF (`ajustes_casaa.pilares`; a camada da Casa B é EST_PILAR, e o preto de
# referência vem das paredes do bloco do motorista).
def pilares_terreo(out):
    AJ.PILARES = dict(AJ.PILARES, camada="EST_PILAR", parede=(1452, 680, 1560, 830))
    return AJ.pilares(out)


# Térreo 12 (R8): as projeções do PDF bem visíveis, por cima: no jardim de inverno, os três painéis com o X tracejado
# (DOC_LINHAS E PROJEÇÕES, hoje cobertos pelas plantas). Os traços são os do próprio PDF (cada tracinho é um desenho),
# em cinza, finos, como as projeções da Casa A (`ajustes_casaa.PROJECOES_A`: cor, largura e força); nas paredes pretas
# o traço some. E sai o X que o motor desenhou no hall interno (`hall_sem_x`).
PROJ_T = {"zonas": [(1810.0, 925.0, 2010.0, 1118.0)], "camada": "DOC_LINHAS E PROJEÇÕES"}


def linhas_pdf(out, chave, zonas, camada, ss=8):
    q = AJ.PROJECOES_A
    pg, p2r = AJ.pdf_pavimento(chave)
    h, w = out.shape[:2]
    m = np.zeros((h * ss, w * ss), np.uint8)
    lw = max(1, int(round(q["larg_px"] * ss)))
    n = 0
    for d in pg.get_drawings():
        r = d["rect"]
        if d.get("layer") != camada or d["type"] != "s" or not any(
                z[0] <= r.x0 and r.x1 <= z[2] and z[1] <= r.y0 and r.y1 <= z[3] for z in zonas):
            continue
        for c in AJ.caminhos_pdf(d, p2r):
            cv2.polylines(m, [np.int32(np.round(c * ss))], False, 255, lw, cv2.LINE_AA)
        n += 1
    a = cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA) * q["forca"]
    a *= (out.astype(np.float32).mean(axis=2) >= q["parede"])
    out = np.clip(out * (1 - a[..., None]) + np.float32(q["cor"]) * a[..., None], 0, 255).astype(np.uint8)
    return out, n


def projecoes_terreo(out):
    out = hall_sem_x(out)
    out, n = linhas_pdf(out, "Terreo", PROJ_T["zonas"], PROJ_T["camada"])
    print(f"    jardim de inverno: os três painéis com o X tracejado do PDF por cima das plantas ({n} traços)")
    return out


# Térreo 14 (seção 7): os armários até o teto em marcenaria areia com o veio, sem a diagonal da DOC_LINHAS, com o
# contorno fino nas faces livres (`ajustes_casaa.armarios_ate_o_teto`, a fonte de marcenaria da Casa D). As peças são os
# trechos dos armários do PDF (ARQ_LAYOUT HUMANIZAÇÃO), cada um com a sua diagonal: o closet master em U, os armários em
# L das suítes 1, 2 e 3 e o da suíte 1 junto à circulação. Sem perfil de sombra no piso (o render não fez sombra de móvel
# baixo neles).
ARMARIOS_B = dict(AJ.ARMARIOS_A, pisos=[], pecas=[
    ("closet master, à esquerda", (1059.3, 773.8, 1096.2, 918.3), ["direita"]),
    ("closet master, embaixo", (1059.3, 918.3, 1317.3, 952.4), ["cima"]),
    ("closet master, à direita", (1317.3, 773.8, 1351.3, 952.4), ["esquerda"]),
    ("suíte 1, em pé", (1617.8, 736.9, 1651.8, 807.8), ["direita"]),
    ("suíte 1, deitado", (1617.8, 807.8, 1807.7, 844.6), ["cima"]),
    ("suíte 1, junto à circulação", (1816.2, 816.3, 1932.4, 853.1), ["cima"]),
    ("suíte 2, em pé", (2295.2, 538.5, 2332.1, 739.8), ["esquerda"]),
    ("suíte 2, em cima", (2332.1, 538.5, 2391.6, 572.5), ["baixo"]),
    ("suíte 3, em pé", (2108.1, 924.0, 2142.2, 1111.1), ["direita"]),
    ("suíte 3, embaixo", (2142.2, 1079.9, 2278.2, 1111.1), ["cima"])])
ARMARIOS_B.pop("bancada", None)


def armarios_terreo(out):
    return AJ.armarios_ate_o_teto(out, "Terreo", ARMARIOS_B)


# Térreo 15 (seção 7): os eletrodomésticos em inox (`ajustes_casaa.inox`, com o inox da Casa D): na cozinha, os três
# quadrados sem diagonal à direita da ilha, e o refrigerador ("Ref.") do gourmet. Retângulos do PDF (pt).
INOX_B = [("cozinha", (1560.1, 1566.0, 1605.4, 1611.4), 0), ("cozinha", (1560.1, 1612.8, 1605.4, 1658.2), 1),
          ("cozinha", (1575.2, 1663.9, 1609.2, 1700.7), 2), ("gourmet, refrigerador", (940.3, 1632.7, 1019.6, 1675.2), 3)]


def inox_terreo(out):
    AJ.INOX = dict(AJ.INOX, quadrados=INOX_B)
    return AJ.inox(out)


# Térreo 20 (seções 4 e 18): portas, vidros e janelas finos. Como os vidros do Térreo da Casa A (`ajustes_casaa.vidros_
# finos`, com `retoque_terreo_casae.esquadria_limpar` e `esquadria_desenhar`): o caixilho largo do motor sai (a faixa de
# cada vidro do PDF recebe o piso do seu lado, em espelho) e as peças da ARQ_PAREDE entram finas (vidro claro, folha,
# alumínio e o contorno fino). As zonas são os grupos de vidros do PDF (os brancos da ARQ_PAREDE de até 3,2 pt): as
# janelas da suíte master, das suítes e dos banhos, a adega, o jardim do hall, as portas de correr; fora o elevador (item
# 19) e os portões (item 13).
VIDROS_B = {"fino": 3.2, "comp_min": 8.0, "junto": 3.0, "folga": 2.0,
            "fora": [(1515.0, 760.0, 1600.0, 860.0), (2090.0, 1430.0, 2335.0, 1465.0), (1895.0, 1700.0, 1990.0, 1835.0)]}


def vidros_b(out, chave):
    import retoque_terreo_casae as T
    sys.path.insert(0, str(RAIZ / "_texturas"))
    from texturas import textura
    import pymupdf
    q = VIDROS_B
    pg, p2r = AJ.pdf_pavimento(chave)
    px_m = px_por_m(chave)
    par = [d for d in pg.get_drawings() if d.get("layer") == "ARQ_PAREDE"]
    finos = [d["rect"] for d in par if d["type"] == "f" and d["fill"] and min(d["fill"]) >= 0.9
             and min(d["rect"].width, d["rect"].height) <= q["fino"] and max(d["rect"].width, d["rect"].height)
             >= q["comp_min"] and not any(pymupdf.Rect(f).intersects(d["rect"]) for f in q["fora"])]
    zonas = []
    for r in finos:
        j = q["junto"]
        perto = [z for z in zonas if z.intersects(pymupdf.Rect(r.x0 - j, r.y0 - j, r.x1 + j, r.y1 + j))]
        z = pymupdf.Rect(r)
        for o in perto:
            z |= o
            zonas.remove(o)
        zonas.append(z)
    img = out.astype(np.float32)
    for r in finos:
        T.esquadria_limpar(img, r, p2r)
    for z in zonas:
        T.esquadria_desenhar(img, (z.x0, z.y0, z.x1, z.y1), par, p2r, px_m, textura)
    print(f"    vidros finos: {len(finos)} vidros e folhas do PDF limpos e redesenhados em {len(zonas)} esquadrias")
    return np.clip(img, 0, 255).astype(np.uint8)


def vidros_terreo(out):
    return vidros_b(out, "Terreo")


# Térreo 21 (seção 8): as cortinas de linho off-white nas linhas onduladas do PDF, com o trilho de parede a parede
# (`blocos.cortina`, `retoque_terreo_casae.pousar_cortina`, como as do 1º Pavimento da Casa A). No PDF da Casa B o pano
# é uma cadeia de ondinhas (ARQ_LOUÇAS E METAIS, 0,85 pt, cada uma de ~2 x 6 pt): as encostadas formam um pano. São 10:
# a suíte master (dois panos em pé, vidro à esquerda), a fachada de cima (sala íntima e suítes 1 e 2, deitados, vidro
# em cima) e a suíte 3 (dois panos em pé, vidro à direita). As manchas marrons do motor saem antes (`tracinhos_cortina`).
# Os panos deitados usam as mesmas rotinas na imagem transposta.
CORTINAS_B = {"traco": 0.85, "onda": (4.0, 8.0, 3.5), "vidro_x": 1500.0}


def trechos_cortina_b(chave):
    import pymupdf
    q = CORTINAS_B
    pg, p2r = AJ.pdf_pavimento(chave)
    seg = []
    for d in pg.get_drawings():
        r = d["rect"]
        if d.get("layer") == "ARQ_LOUÇAS E METAIS" and d["type"] == "s" and abs((d.get("width") or 0) - q["traco"]) < 0.05 \
                and any(it[0] == "c" for it in d["items"]) and q["onda"][0] < max(r.width, r.height) < q["onda"][1] \
                and min(r.width, r.height) < q["onda"][2]:
            seg.append((r.height > r.width, pymupdf.Rect(r)))
    grupos = []
    for v, r in seg:
        perto = [g for g in grupos if g[0] == v and g[1].intersects(pymupdf.Rect(r.x0 - 1, r.y0 - 1, r.x1 + 1, r.y1 + 1))]
        z = pymupdf.Rect(r)
        for g in perto:
            z |= g[1]
            grupos.remove(g)
        grupos.append((v, z))
    trechos = []
    for v, r in grupos:
        if v:
            eixo = (r.x0 + r.x1) / 2
            (ex, e0), (_, e1) = p2r(eixo, r.y0), p2r(eixo, r.y1)
            trechos.append(("v", "esquerda" if eixo < q["vidro_x"] else "direita", ex, e0, e1))
        else:
            eixo = (r.y0 + r.y1) / 2
            (e0, ey), (e1, _) = p2r(r.x0, eixo), p2r(r.x1, eixo)
            trechos.append(("h", "cima", ey, e0, e1))
    return sorted(trechos, key=lambda t: (t[0], t[2], t[3]))


def cortinas_b(out, chave):
    from retoque_terreo_casae import pousar_cortina
    sys.path.insert(0, str(RAIZ / "_blocos"))
    import blocos
    q = AJ.CORTINAS_1PAV
    px_m = px_por_m(chave)
    k = q["ss"]
    busca = int(q["busca_m"] * px_m)
    trechos = trechos_cortina_b(chave)
    limpos = 0
    trilhos = []
    for o, vidro, ex, e0, e1 in trechos:
        img = out if o == "v" else out.transpose(1, 0, 2)
        v = vidro if o == "v" else {"cima": "esquerda", "baixo": "direita"}[vidro]
        limpos += AJ.tracinhos_cortina(img, [(v, ex, e0, e1)])
        dentro = int(round(ex)) + (q["dentro"] if v == "esquerda" else -q["dentro"])
        escuro = img[:, dentro].astype(np.float32).mean(axis=1) < q["parede"]

        def ate_parede(y, passo):
            n = 0
            for yy in range(int(round(y)), int(round(y)) + passo * busca, passo):
                n = n + 1 if escuro[yy] else 0
                if n >= q["seguidos"]:
                    return yy - passo * (q["seguidos"] - 1) - passo * 0.5
            return y
        trilhos.append([o, v, ex, ate_parede((e0 + e1) / 2, -1), ate_parede((e0 + e1) / 2, +1)])
    unidos = []
    for o, v, ex, t0, t1 in sorted(trilhos, key=lambda t: (t[0], t[1], round(t[2]), t[3])):
        if unidos and unidos[-1][:2] == [o, v] and abs(unidos[-1][2] - ex) < 3 and t0 < unidos[-1][4] - 2:
            unidos[-1][3], unidos[-1][4] = min(unidos[-1][3], t0), max(unidos[-1][4], t1)
        else:
            unidos.append([o, v, ex, t0, t1])
    for o, v, ex, t0, t1 in unidos:
        img = out if o == "v" else out.transpose(1, 0, 2)
        cor, al = blocos.cortina((t1 - t0) / px_m, px_m * k, com_pano=False)
        pousar_cortina(img, cor, al, ex, t0, k, v)
    for o, vidro, ex, e0, e1 in trechos:
        img = out if o == "v" else out.transpose(1, 0, 2)
        v = vidro if o == "v" else {"cima": "esquerda", "baixo": "direita"}[vidro]
        cor, al = blocos.cortina((e1 - e0) / px_m, px_m * k, com_trilho=False)
        pousar_cortina(img, cor, al, ex, e0, k, v)
    print(f"    cortinas: {limpos} px de manchas do motor fora; {len(trechos)} panos de linho nas ondas do PDF e "
          f"{len(unidos)} trilhos de parede a parede")
    return out


def cortinas_terreo(out):
    out = np.ascontiguousarray(out)
    return cortinas_b(out, "Terreo")


# Térreo 24 (pedidos de 21/10 na Casa A, decididos pela proposta): a roupa de cama da biblioteca nas camas
# (`elementos.roupa_de_cama`, como no 1º Pavimento e no motorista da Casa A), no colchão do PDF (ARQ_LAYOUT HUMANIZAÇÃO;
# a master, ARQ_LOUÇAS E METAIS) menos a borda; a cabeceira do lado do PDF (na Casa B há camas deitadas na planta).
CAMAS_B = {"borda": 1.7, "ss": 4, "semente": 41, "camas": [
    ("suíte master", (877.5, 838.0, 979.4, 947.9), "baixo", "casal"),
    ("suíte 1", (1729.0, 590.9, 1838.5, 700.8), "esq", "casal"),
    ("suíte 2, de cima", (2174.1, 564.0, 2283.0, 617.3), "dir", "solteiro"),
    ("suíte 2, de baixo", (2174.1, 673.4, 2283.0, 726.6), "dir", "solteiro"),
    ("suíte 3", (2216.8, 903.8, 2326.7, 1012.1), "baixo", "casal"),
    ("quarto de serviço", (1702.6, 1757.8, 1810.9, 1804.9), "esq", "solteiro"),
    ("quarto do motorista", (2586.1, 1546.5, 2694.4, 1593.6), "dir", "motorista")]}


def camas_b(out, chave, q):
    sys.path.insert(0, str(RAIZ / "_texturas"))
    import elementos
    _, p2r = AJ.pdf_pavimento(chave)
    px_m = px_por_m(chave)
    k = q["ss"]
    for i, (nome, r, cab, tipo) in enumerate(q["camas"]):
        e = q["borda"]
        (u0, v0), (u1, v1) = p2r(r[0] + e, r[1] + e), p2r(r[2] - e, r[3] - e)
        deitada = cab in ("esq", "dir")
        comp, larg = ((u1 - u0), (v1 - v0)) if deitada else ((v1 - v0), (u1 - u0))
        cor, al = elementos.roupa_de_cama(comp / px_m, larg / px_m, px_m * k, tipo, semente=q["semente"] + i)
        if cab == "dir":
            cor, al = cor[:, ::-1], al[:, ::-1]
        elif cab == "cima":
            cor, al = cv2.rotate(cor, cv2.ROTATE_90_CLOCKWISE)[:, ::-1], cv2.rotate(al, cv2.ROTATE_90_CLOCKWISE)[:, ::-1]
        elif cab == "baixo":
            cor, al = cv2.rotate(cor, cv2.ROTATE_90_COUNTERCLOCKWISE), cv2.rotate(al, cv2.ROTATE_90_COUNTERCLOCKWISE)
        X0, Y0 = int(np.floor(u0)) - 1, int(np.floor(v0)) - 1
        X1, Y1 = int(np.ceil(u1)) + 2, int(np.ceil(v1)) + 2
        tw, th = int(round((u1 - u0) * k)), int(round((v1 - v0) * k))
        cor = cv2.resize(np.ascontiguousarray(cor * al[..., None]), (tw, th), interpolation=cv2.INTER_AREA)
        al = cv2.resize(np.ascontiguousarray(al), (tw, th), interpolation=cv2.INTER_AREA)
        g = np.zeros(((Y1 - Y0) * k, (X1 - X0) * k, 3), np.float32)
        ga = np.zeros(g.shape[:2], np.float32)
        ox, oy = int(round((u0 - X0) * k)), int(round((v0 - Y0) * k))
        g[oy:oy + th, ox:ox + tw] = cor
        ga[oy:oy + th, ox:ox + tw] = al
        pre = cv2.resize(g, (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA)
        a_ = cv2.resize(ga, (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA)
        reg = out[Y0:Y1, X0:X1].astype(np.float32)
        out[Y0:Y1, X0:X1] = np.clip(np.round(reg * (1 - a_[..., None]) + pre), 0, 255).astype(np.uint8)
    print(f"    camas: a roupa de cama da referência nas {len(q['camas'])} camas ("
          + "; ".join(f"{n}, {t}" for n, _, _, t in q["camas"]) + ")")
    return out


def camas_terreo(out):
    return camas_b(out, "Terreo", CAMAS_B)


def boxes_terreo(out):
    return AJ.boxes_continuos(out, "Terreo")


def carrara_terreo(out):
    return AJ.carrara_bancadas(out, "Terreo")


# Térreo 24 (pedido de 21/10 na Casa A): as banquetas de linho da biblioteca (`banqueta_linho`, 0,40 m, como na ilha da
# Casa A) no lugar das quatro do motor, junto à bancada gourmet, viradas para ela; as do motor saem por inpaint.
BANQUETAS_B = {"centros": [(698.8, 679.0), (725.5, 679.0), (751.3, 679.0), (778.0, 679.0)], "d_m": 0.40,
               "caixa": (688, 670, 790, 683), "claro": 215, "giro": 180}


def banquetas_gourmet(out):
    import json as _json
    from retoque_terreo_casae import pousar_planta
    sys.path.insert(0, str(RAIZ / "_blocos"))
    import blocos
    q = BANQUETAS_B
    px_m = px_por_m("Terreo")
    x0, y0, x1, y1 = q["caixa"]
    m = np.zeros(out.shape[:2], np.uint8)
    reg = out[y0:y1, x0:x1].astype(np.float32)
    m[y0:y1, x0:x1] = (reg.mean(axis=2) > q["claro"]) | (reg.mean(axis=2) < 150)
    m = cv2.dilate(m, np.ones((3, 3), np.uint8))
    m[y1:, :] = 0
    out = cv2.inpaint(out, m, 3, cv2.INPAINT_TELEA)
    d_px = q["d_m"] * px_m
    cor, al = blocos.bloco("banqueta_linho", d_px / 0.45)
    for _ in range(q["giro"] // 90):
        cor, al = cv2.rotate(cor, cv2.ROTATE_90_CLOCKWISE), cv2.rotate(al, cv2.ROTATE_90_CLOCKWISE)
    sombra = _json.loads((RAIZ / "_texturas" / "texturas.json").read_text())["vegetacao"]["sombra"]
    img = out.astype(np.float32)
    for cx, cy in q["centros"]:
        pousar_planta(img, cor.astype(np.float32), np.clip(al, 0, 1).astype(np.float32), cx, cy, d_px, sombra)
    print(f"    bancada gourmet: {len(q['centros'])} banquetas de linho da biblioteca ({q['d_m']:.2f} m)")
    return np.clip(img, 0, 255).astype(np.uint8)


# Térreo 23 (R13): as soleiras, porta a porta com o PDF: onde o vão fica em branco (a base, que é o PDF, tem branco entre
# as duas paredes), soleira de Bege Bahia na escala, com as faces da parede em cinza fino (`ajustes_casaa.desenhar_
# soleiras`, com os números de lá); onde o piso atravessa, sem soleira. Os vãos são as manchas brancas da base dentro da
# casa, da espessura da parede, junto à ponta de um arco de porta do PDF; fora os portões da área de serviço (item 13) e
# os vãos de 1 a 2 px (o encontro da pivotante e de uma porta de correr).
SOLEIRAS_B = dict(AJ.SOLEIRAS_A, fora=[], espessura_px=(3, 8), area=(6, 400), perto_px=4,
                  sem=[(1890.0, 1700.0, 1990.0, 1830.0)])


def vaos_brancos(chave):
    from scipy import ndimage
    import pymupdf
    q = SOLEIRAS_B
    forma = (1116, 2000) if chave == "Terreo" else (1125, 2000)
    b = AJ.base_terreo(forma, chave).astype(np.int32)
    branco = b.min(axis=2) >= 250
    grama = np.abs(b - np.array(GRAMA_B["cor_base"])).max(axis=2) <= GRAMA_B["tol"]
    predio = ndimage.binary_fill_holes(cv2.morphologyEx((~branco & ~grama).astype(np.uint8), cv2.MORPH_CLOSE,
                                                        np.ones((9, 9), np.uint8)))
    n, lab, st, _ = cv2.connectedComponentsWithStats((branco & predio).astype(np.uint8), 4)
    pg, p2r = AJ.pdf_pavimento(chave)
    a = np.array(p2r(0, 0))
    inv = np.linalg.inv(np.array([np.array(p2r(100, 0)) - a, np.array(p2r(0, 100)) - a]).T / 100)
    pontas = []
    for d in pg.get_drawings():
        if d.get("layer") == "ARQ_PAREDE" and d["type"] == "s" and max(d["rect"].width, d["rect"].height) >= 12:
            cs = [it for it in d["items"] if it[0] == "c"]
            if cs:
                pontas += [p2r(cs[0][1].x, cs[0][1].y), p2r(cs[-1][4].x, cs[-1][4].y)]
    vaos = []
    e0, e1 = q["espessura_px"]
    t = q["perto_px"]
    for i in range(1, n):
        x, y, w, h, ar = st[i]
        if not (q["area"][0] <= ar <= q["area"][1] and e0 <= min(w, h) <= e1 and max(w, h) >= 8):
            continue
        if not any(x - t <= px <= x + w + t and y - t <= py <= y + h + t for px, py in pontas):
            continue
        p0, p1 = inv @ (np.array([x, y]) - a), inv @ (np.array([x + w, y + h]) - a)
        r = (float(p0[0]), float(p0[1]), float(p1[0]), float(p1[1]))
        if any(pymupdf.Rect(z).intersects(pymupdf.Rect(r)) for z in q["sem"]):
            continue
        vaos.append(r)
    return vaos


def soleiras_terreo(out):
    vaos = vaos_brancos("Terreo")
    out = AJ.desenhar_soleiras(out, "Terreo", dict(SOLEIRAS_B, pdf=vaos))
    print(f"    soleiras: {len(vaos)} vãos brancos do PDF com a soleira de Bege Bahia")
    return out


def paredes_terreo(out):
    return AJ.paredes_perfeitas(out, "Terreo")


# Térreo 2 (R1, seção 3): a pedra portuguesa de 6 a 8 cm em leque, no tom da foto (bege, cinza e rosado), na garagem e no
# acesso (`ajustes_casaa.pedra_leque`, com a cor do granito da Casa B e a máscara da Casa B, que vai à final de 3840 px,
# onde a pedra é redesenhada de novo). Por último, como na Casa A.
PEDRA_B = {"area_min": 2000, "folga": 9}


def pedra_terreo(out):
    """A rotina da Casa A pega a cor da pedra na base em qualquer lugar; na Casa B há pontinhos dela soltos na base (nas
    suítes, junto às paredes), e o vinílico passa no teste do caramelo: a pedra fica só nas manchas grandes da legenda
    (a garagem e o acesso), com folga, e a máscara salva para a final também."""
    q = PEDRA_B
    antes = out.copy()
    novo = AJ.pedra_leque(out)
    pedra = (np.abs(AJ.base_terreo(out.shape[:2]).astype(np.int32) - np.array(AJ.PEDRA_A["cor_base"])).max(axis=2)
             <= AJ.PEDRA_A["tol"]).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(pedra, 8)
    zona = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= q["area_min"]]).astype(np.uint8)
    k = 2 * q["folga"] + 1
    zona = cv2.dilate(zona, np.ones((k, k), np.uint8)).astype(bool)
    novo[~zona] = antes[~zona]
    mq = AJ.PEDRA_A["mascara"]
    m = cv2.imread(str(mq), cv2.IMREAD_GRAYSCALE)
    m[~zona] = 0
    cv2.imwrite(str(mq), m)
    print(f"    pedra só nas manchas grandes da legenda: {int(((novo != antes).any(axis=2)).sum())} px")
    return novo


# ---------------------------------------------------------------------------------------------------------------------
# Subsolo
# ---------------------------------------------------------------------------------------------------------------------
# Subsolo 2 (R1, seção 18): o Bege Bahia da referência (placa de 0,60 m, nuvens de 10 a 20 cm, tom quente ~230, 211,
# 186), na garagem, nas duas circulações e no BH serviço: a rotina do Térreo da Casa A (`bege_referencia_a`: a mancha
# do #E8E8E8 da base, os pontinhos do motor fora, o desenho da biblioteca no tom da foto, com a luz do lugar), lendo o
# Subsolo.
def bege_subsolo_b(out):
    with chave_como("Terreo", "Subsolo"):
        return AJ.bege_referencia_a(out)


def travertino_subsolo_b(out):
    return travertino_b(out, "Subsolo")


# Subsolo 4: a academia, com o piso contínuo: o vinílico em réguas de ~20 cm (como o Térreo, item 5), que leva os
# retângulos de outro tom em volta das bicicletas e do supino à luz do lugar.
def vinilico_subsolo(out):
    return vinilico_b(out, "Subsolo")


# Subsolo 1 e Térreo 6: a ducha e o deck em L ao lado dela (o mesmo nível, os preenchimentos de cinza 0,89 da
# ARQ_CONTRAPISO), na madeira da referência e em cor cheia (o deck em L estava esmaecido, como o resto do Térreo); o
# canto da pedra grande (do nível do Térreo) e os degraus ficam fora.
DECK_SUB = {"cinza": 0.89, "tol": 0.01, "x_min_pt": 440.0}


def deck_subsolo(out):
    q = DECK_SUB
    pg, p2r = AJ.pdf_pavimento("Subsolo")
    H, W = out.shape[:2]
    k = 4
    m = np.zeros((H * k, W * k), np.uint8)
    D = pg.get_drawings()
    for d in D:
        if d.get("layer") == "ARQ_CONTRAPISO" and d["type"] in ("f", "fs") and d.get("fill") and \
                abs(d["fill"][0] - q["cinza"]) <= q["tol"] and d["rect"].x0 >= q["x_min_pt"]:
            for c in AJ.caminhos_pdf(d, p2r):
                cv2.fillPoly(m, [np.int32(np.round(c * k))], 255)
    for d in D:
        fora = (d.get("layer") == "ARQ_CONTRAPISO" and d["rect"].x0 < q["x_min_pt"]) or \
            (d.get("layer") in ("ARQ_ESCADAS E RAMPAS", "ARQ_PAREDE") and d["type"] in ("f", "fs"))
        if fora and d["type"] in ("f", "fs"):
            for c in AJ.caminhos_pdf(d, p2r):
                if len(c) >= 3:
                    cv2.fillPoly(m, [np.int32(np.round(c * k))], 0)
    deck = cv2.resize(m, (W, H), interpolation=cv2.INTER_AREA) > 127
    out, n = deck_madeira(out, deck, px_por_m("Subsolo"), luz_local=False)
    print(f"    ducha e deck em L: {n} px na madeira da referência, em cor cheia (réguas de ~20 cm)")
    return out


# Subsolo 5 e 6 (R14): as escadas que sobem do nível da ducha ("S" do PDF), em cor cheia (estavam esmaecidas): o
# travertino aprovado nos degraus (o mesmo desenho do item 3, na luz média do travertino do Subsolo) e, por cima, as
# linhas da R14 (`escada_linhas`): a de 6 degraus sobe da ducha para a pedra grande (o triângulo no 1º degrau, junto à
# ducha, à direita, apontando para a esquerda), inteira abaixo do plano de corte (1,05 m); a de 9 degraus sobe do deck em
# L para a varanda (o triângulo no 1º degrau, à esquerda, apontando para a direita), cheia até o corte (a 1,20 m, depois
# do 7º degrau, na diagonal) e esmaecida depois, como na Casa A.
ESCADAS_S = [{"nome": "de 6 degraus, da ducha para a pedra grande", "pdf": (516.2, 793.6, 602.9, 881.5),
              "bocels": [534.9, 551.9, 568.9, 585.9], "corte": None, "baixo": "direita", "inicio": "direita"},
             {"nome": "de 9 degraus, do deck em L para a varanda", "pdf": (728.8, 963.7, 917.6, 1071.4),
              "bocels": [752.2, 775.6, 799.0, 822.3, 845.7, 869.1, 892.5],
              "corte": [(892.5, 963.7), (869.1, 1071.4)], "viva": "esquerda", "apos": "esmaecida", "esmaecer": 0.45,
              "baixo": "esquerda", "inicio": "esquerda"}]


def escadas_subsolo(out):
    from retoque_bege_bahia_terreo import quilting
    from retoque_terreo_casae import escada_linhas
    t = AJ.TRAV_SUB
    pg, p2r = AJ.pdf_pavimento("Subsolo")
    H, W = out.shape[:2]
    b = AJ.base_terreo((H, W), "Subsolo").astype(np.int32)
    trav = (np.abs(b - np.array(TRAV_B["cor_base"])).max(axis=2) <= TRAV_B["tol"]) & (out.mean(axis=2) < 245)
    tom = np.median(out[trav].astype(np.float32), axis=0)
    fonte = cv2.imread(str(t["fonte"])).astype(np.float32)
    fontes = [fonte[y0:y1, x0:x1] for x0, y0, x1, y1 in t["trechos"]]
    fontes += [f[:, ::-1] for f in fontes] + [f[::-1] for f in fontes]
    for e in ESCADAS_S:
        (a, bb), (c, d) = p2r(e["pdf"][0], e["pdf"][1]), p2r(e["pdf"][2], e["pdf"][3])
        x0, y0, x1, y1 = int(np.floor(a)), int(np.floor(bb)), int(np.ceil(c)), int(np.ceil(d))
        T = quilting(fontes, y1 - y0, x1 - x0, p=t["p"], sobra=t["sobra"], candidatos=t["candidatos"],
                     rng=np.random.default_rng(t["semente"]))[:y1 - y0, :x1 - x0]
        T = T / T.reshape(-1, 3).mean(axis=0) * tom
        al = ret_aa((H, W), (a, bb, c, d))[y0:y1, x0:x1, None]
        reg = out[y0:y1, x0:x1].astype(np.float32)
        out[y0:y1, x0:x1] = np.clip(reg * (1 - al) + T * al, 0, 255).astype(np.uint8)
        out = escada_linhas(out, None, e, p2r=p2r)
    return out


# Subsolo 2: a circulação de 1,16 m² entre o BH serviço e o depósito (as duas portas abrem para ela) está em branco na
# base e no render, e aberta em cima: o piso dela entra em Bege Bahia, como a outra circulação, na textura e no tom da
# referência (os da soleira, `desenhar_soleiras`), só onde o render está em branco (as folhas e os batentes ficam).
CIRC_SUB = {"pt": (1254.9, 536.8, 1314.4, 591.6), "branco": 238}


def circulacao_subsolo(out):
    sys.path.insert(0, str(RAIZ / "_texturas"))
    from texturas import textura
    from retoque_terreo_casae import BEGE
    q = CIRC_SUB
    _, p2r = AJ.pdf_pavimento("Subsolo")
    px_m = px_por_m("Subsolo")
    x0, y0, x1, y1 = ret_px(p2r, q["pt"])
    X0, Y0, X1, Y1 = int(np.floor(x0)), int(np.floor(y0)), int(np.ceil(x1)), int(np.ceil(y1))
    al = ret_aa(out.shape[:2], (x0, y0, x1, y1))[Y0:Y1, X0:X1]
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    al *= (reg.min(axis=2) >= q["branco"])
    T = textura("bege_bahia", px_m, Y1 - Y0, X1 - X0, semente=5).astype(np.float32)
    T = (1 + 0.5 * (T / T.reshape(-1, 3).mean(axis=0) - 1)) * np.float32(BEGE["tom"])
    out[Y0:Y1, X0:X1] = np.clip(reg * (1 - al[..., None]) + T * al[..., None], 0, 255).astype(np.uint8)
    print(f"    circulação de 1,16 m²: {int((al > 0.5).sum())} px em Bege Bahia")
    return out


def sem_arcos_subsolo(out):
    return AJ.sem_arcos_pdf(out, "Subsolo", AJ.SEM_ARCOS_1PAV)


def vidros_subsolo(out):
    return vidros_b(out, "Subsolo")


def soleiras_subsolo(out):
    vaos = vaos_brancos("Subsolo")
    out = AJ.desenhar_soleiras(out, "Subsolo", dict(SOLEIRAS_B, pdf=vaos))
    print(f"    soleiras: {len(vaos)} vãos brancos do PDF com a soleira de Bege Bahia")
    return out


def paredes_subsolo(out):
    return AJ.paredes_perfeitas(out, "Subsolo")


# Térreo 25 ("a confirmar" na lista; decidido pela proposta): a peça branca comprida abaixo do lavatório gourmet, do lado
# de fora, é uma caixa de paredes finas da ARQ_PAREDE (9 cm) com 40 cm de miolo, junto às janelas: uma floreira. O miolo
# fica em terra e recebe uma fileira de touceiras baixas da biblioteca, no tamanho real, saindo levemente dela; as
# paredes dela ficam pretas com as outras (item 22).
FLOREIRA = {"pt": (1042.3, 1799.1, 1229.4, 1821.7), "terra": (52, 62, 74), "passo_m": 0.42,
            "nomes": ["planta_flores", "arbusto_2", "arbusto_1", "planta_flores", "arbusto_3"], "d_m": (0.42, 0.55),
            "semente": 5}


def floreira(out):
    import json as _json
    from retoque_terreo_casae import pousar_planta
    q = FLOREIRA
    _, p2r = AJ.pdf_pavimento("Terreo")
    px_m = px_por_m("Terreo")
    x0, y0, x1, y1 = ret_px(p2r, q["pt"])
    H, W = out.shape[:2]
    img = out.astype(np.float32)
    a = ret_aa((H, W), (x0, y0, x1, y1))
    rng = np.random.default_rng(q["semente"])
    gr = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 0.7)
    terra = np.float32(q["terra"])[None, None] * (1 + 0.10 * gr / max(gr.std(), 1e-6))[..., None]
    img = img * (1 - a[..., None]) + terra * a[..., None]
    sombra = _json.loads((RAIZ / "_texturas" / "texturas.json").read_text())["vegetacao"]["sombra"]
    passo = q["passo_m"] * px_m
    n = 0
    for i, cx in enumerate(np.arange(x0 + passo / 2, x1 - passo / 4, passo)):
        nome = q["nomes"][i % len(q["nomes"])]
        cor, al, d_px = planta_sprite(nome, float(rng.uniform(*q["d_m"])), px_m)
        for _ in range(int(rng.integers(4))):
            cor, al = cv2.rotate(cor, cv2.ROTATE_90_CLOCKWISE), cv2.rotate(al, cv2.ROTATE_90_CLOCKWISE)
        pousar_planta(img, cor, al, cx, (y0 + y1) / 2 + rng.uniform(-0.1, 0.1) * passo, d_px, sombra)
        n += 1
    print(f"    floreira junto ao lavatório gourmet: terra no miolo ({x1 - x0:.0f} x {y1 - y0:.0f} px) e {n} touceiras")
    return np.clip(img, 0, 255).astype(np.uint8)


# Térreo 18: na sala íntima, a bancada do PDF (ARQ_BANCADAS, 0,56 x 2,40 m, junto ao shaft) com a cuba quadrada (ARQ_LOUÇAS
# E METAIS) e a torneira do lado da parede, no lugar do móvel de madeira com o enfeite que o motor fez. O tampo é o quartzo
# claro das bancadas da cozinha do próprio render (image quilting de trechos limpos), com o contorno fino e a sombra curta.
BANCADA_INTIMA = {"pt": (1362.6, 782.2, 1394.4, 918.3), "cuba_pt": (1367.9, 855.5, 1387.2, 874.8),
                  "fontes_pt": [(1130, 1495, 1160, 1540), (1225, 1495, 1250, 1540)], "contorno": (120, 118, 114),
                  "larg": 0.45, "bloco": "cuba_inox_quadrada", "giro": 90}


def bancada_sala_intima(out):
    import sys as _sys
    _sys.path.insert(0, str(RAIZ / "_blocos"))
    import blocos
    q = BANCADA_INTIMA
    _, p2r = AJ.pdf_pavimento("Terreo")
    px_m = px_por_m("Terreo")
    H, W = out.shape[:2]
    r = ret_px(p2r, q["pt"])
    X0, Y0, X1, Y1 = int(np.floor(r[0])) - 2, int(np.floor(r[1])) - 2, int(np.ceil(r[2])) + 3, int(np.ceil(r[3])) + 3
    fontes = [tuple(int(round(v)) for v in ret_px(p2r, f)) for f in q["fontes_pt"]]
    reg = np.concatenate([out[b:d, a:c].reshape(-1, 3) for a, b, c, d in fontes]).astype(np.float32)
    cor = np.median(reg[reg.mean(axis=1) > np.percentile(reg.mean(axis=1), 50)], axis=0)
    # o quartzo: o tom das bancadas da cozinha, com um grão fino e nuvens leves (o quilting trazia as bordas das fontes)
    rng = np.random.default_rng(7)
    hh, ww = Y1 - Y0, X1 - X0
    nuv = cv2.GaussianBlur(rng.normal(0, 1, (hh, ww)).astype(np.float32), (0, 0), 3.0)
    gra = cv2.GaussianBlur(rng.normal(0, 1, (hh, ww)).astype(np.float32), (0, 0), 0.6)
    tex = cor * (1 + 0.018 * nuv / max(nuv.std(), 1e-6) + 0.012 * gra / max(gra.std(), 1e-6))[..., None]
    img = out.astype(np.float32)
    al = ret_aa((H, W), r)
    # a sombra curta fora do tampo, depois o tampo
    sh = sombra_de(al, px_m, forca=0.30)
    img *= (1 - sh[..., None])
    reg = img[Y0:Y1, X0:X1]
    a_ = al[Y0:Y1, X0:X1, None]
    img[Y0:Y1, X0:X1] = reg * (1 - a_) + tex * a_
    c = contorno_aa((H, W), r, q["larg"])[..., None]
    img = img * (1 - c) + np.float32(q["contorno"]) * c
    # a cuba: o bloco da biblioteca no quadrado do PDF, girado com a torneira para a parede (à esquerda)
    rc = ret_px(p2r, q["cuba_pt"])
    cb, ab = blocos.bloco(q["bloco"], px_m)
    for _ in range(q["giro"] // 90):
        cb, ab = cv2.rotate(cb, cv2.ROTATE_90_CLOCKWISE), cv2.rotate(ab, cv2.ROTATE_90_CLOCKWISE)
    w, h = int(round(rc[2] - rc[0])) + 1, int(round(rc[3] - rc[1])) + 1
    cb = cv2.resize(cb, (w, h), interpolation=cv2.INTER_AREA)
    ab = cv2.resize(ab, (w, h), interpolation=cv2.INTER_AREA)
    img = pousar_rgba(img, cb, ab, (rc[0] + rc[2]) / 2, (rc[1] + rc[3]) / 2)
    print(f"    sala íntima: bancada de quartzo ({r[2] - r[0]:.0f} x {r[3] - r[1]:.0f} px) com a cuba quadrada do PDF")
    return np.clip(img, 0, 255).astype(np.uint8)


# Térreo 19: o elevador. No Térreo, o motor deixou a caixa branca vazia; entra a cabine aprovada do Subsolo da Casa B (a
# mesma das Casas C, D e E), no mesmo quadro (o elevador de um pavimento cai sobre o do outro), com a porta e a soleira.
ELEVADOR = {"pt": (1521.0, 769.0, 1591.5, 853.0)}


def elevador_cabine(out):
    q = ELEVADOR
    _, p2rT = AJ.pdf_pavimento("Terreo")
    _, p2rS = AJ.pdf_pavimento("Subsolo")
    S = cv2.imread(str(AJ.APROVADAS["Subsolo"]))
    x0, y0, x1, y1 = q["pt"]
    pts = [(x0, y0), (x1, y0), (x0, y1)]
    M = cv2.getAffineTransform(np.float32([p2rS(*p) for p in pts]), np.float32([p2rT(*p) for p in pts]))
    H, W = out.shape[:2]
    Sw = cv2.warpAffine(S, M, (W, H), flags=cv2.INTER_CUBIC)
    al = ret_aa((H, W), ret_px(p2rT, q["pt"]))
    img = out.astype(np.float32) * (1 - al[..., None]) + Sw.astype(np.float32) * al[..., None]
    print("    elevador: a cabine do Subsolo, com a porta e a soleira, no mesmo quadro")
    return np.clip(img, 0, 255).astype(np.uint8)


# Térreo 17: a adega. O PDF tem a prateleira de vinhos na parede de baixo (ARQ_BANCADAS, 3,30 x 0,40 m), com três nichos de
# 0,40 m à esquerda (ARQ_REVESTIMENTOS); o motor fez um banco bege. Entra a prateleira em marcenaria areia com o veio, as
# divisões dos nichos em traço fino e as garrafas deitadas, com o gargalo para a parede, como a adega da Casa E.
ADEGA_B = {"pt": (1820.1, 1416.1, 2006.1, 1438.8), "divisoes_pt": [1842.8, 1865.5, 1888.2], "madeira": (160, 186, 206),
           "contorno": (110, 118, 124), "larg": 0.4, "passo": 2.6, "corpo": 6.6, "gargalo": 2.6, "larg_g": 1.9,
           "larg_gargalo": 0.8, "folga": 1.0,
           "vidros": [(26, 40, 28), (20, 32, 48), (30, 24, 46), (24, 34, 26), (22, 30, 40)], "brilho": 0.45,
           "sombra": {"desloc": (-0.5, 0.6), "sigma": 0.5, "forca": 0.35}, "semente": 3}


def adega_b(out):
    from retoque_terreo_casae import SS, linha_aa
    q = ADEGA_B
    _, p2r = AJ.pdf_pavimento("Terreo")
    px_m = px_por_m("Terreo")
    H, W = out.shape[:2]
    r = ret_px(p2r, q["pt"])
    img = out.astype(np.float32)
    al = ret_aa((H, W), r)
    # a marcenaria: o tom areia com o veio no comprido (ruído esticado)
    rng = np.random.default_rng(q["semente"])
    ve = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), sigmaX=9, sigmaY=0.6)
    mad = np.float32(q["madeira"])[None, None] * (1 + 0.06 * ve / max(ve.std(), 1e-6))[..., None]
    sh = sombra_de(al, px_m, forca=0.25)
    img *= (1 - sh[..., None])
    img = img * (1 - al[..., None]) + mad * al[..., None]
    c = contorno_aa((H, W), r, q["larg"])[..., None]
    img = img * (1 - c) + np.float32(q["contorno"]) * c
    for xd in q["divisoes_pt"]:
        (ax, ay), (bx, by) = p2r(xd, q["pt"][1]), p2r(xd, q["pt"][3])
        c = linha_aa((H, W), [(ax, ay), (bx, by)], q["larg"])[..., None]
        img = img * (1 - c) + np.float32(q["contorno"]) * c
    # as garrafas: deitadas, o gargalo junto à parede de baixo, a base para o vão
    x0, y0, x1, y1 = r
    wx0, wy0, wx1, wy1 = int(x0) - 2, int(y0) - 2, int(np.ceil(x1)) + 3, int(np.ceil(y1)) + 3
    h, w = wy1 - wy0, wx1 - wx0
    U = al[wy0:wy1, wx0:wx1]
    reg = img[wy0:wy1, wx0:wx1]
    s_ = q["sombra"]
    p_, cp, gl, f = q["passo"], q["corpo"], q["gargalo"], q["folga"]
    divs = [p2r(xd, y0)[0] for xd in q["divisoes_pt"]]
    n = 0
    x = x0 + f + p_ / 2
    while x < x1 - f:
        if any(abs(x - d) < 1.0 for d in divs):
            x += p_
            continue
        cor = np.float32(q["vidros"][int(rng.integers(len(q["vidros"])))])
        px, py = x, y1 - 0.3
        ux, uy = 0, -1
        pts_g = [(px, py), (px + ux * gl, py + uy * gl)]
        pts_c = [(px + ux * (gl + 0.6), py + uy * (gl + 0.6)), (px + ux * (gl + cp), py + uy * (gl + cp))]
        m = np.zeros((h * SS, w * SS), np.uint8)
        for pts, larg in ((pts_g, q["larg_gargalo"]), (pts_c, q["larg_g"])):
            pp = np.int32(np.round((np.float32(pts) - [wx0, wy0]) * SS))
            cv2.line(m, tuple(pp[0]), tuple(pp[1]), 255, max(1, int(round(larg * SS))), cv2.LINE_AA)
        pp = np.int32(np.round((np.float32([pts_g[1], pts_c[0]]) - [wx0, wy0]) * SS))
        cv2.line(m, tuple(pp[0]), tuple(pp[1]), 255, max(1, int(round((q["larg_g"] + q["larg_gargalo"]) / 2 * SS))),
                 cv2.LINE_AA)
        a_ = cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA) * U
        sh = cv2.GaussianBlur(cv2.warpAffine(a_, np.float32([[1, 0, s_["desloc"][0]], [0, 1, s_["desloc"][1]]]), (w, h)),
                              (0, 0), s_["sigma"]) * (1 - a_)
        reg *= (1 - s_["forca"] * sh)[..., None]
        reg = reg * (1 - a_[..., None]) + cor * a_[..., None]
        bm = np.zeros((h * SS, w * SS), np.uint8)
        pb = np.int32(np.round((np.float32(pts_c) + [0.35, 0] - [wx0, wy0]) * SS))
        cv2.line(bm, tuple(pb[0]), tuple(pb[1]), 255, max(1, int(round(0.3 * SS))), cv2.LINE_AA)
        ab = cv2.resize(bm.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None] * q["brilho"] * U[..., None]
        reg = reg * (1 - ab) + (cor * 0.4 + 255 * 0.6) * ab
        n += 1
        x += p_
    img[wy0:wy1, wx0:wx1] = reg
    print(f"    adega: prateleira de vinhos em marcenaria ({x1 - x0:.0f} x {y1 - y0:.0f} px), 3 nichos e {n} garrafas")
    return np.clip(img, 0, 255).astype(np.uint8)


# Térreo 16: os cooktops do PDF (ARQ_LOUÇAS E METAIS, 0,88 x 0,50 m, 5 bocas): o da bancada gourmet, deitado, e o da ilha da
# cozinha, em pé; o bloco de inox da biblioteca (cooktop_inox_5_90), como nas Casas A e E. Antes, o tampo em volta (o
# retângulo e uma folga, onde o motor desenhou as bocas) volta ao quartzo do próprio tampo, ao lado.
COOKTOPS_B = [{"pt": (1168.1, 1506.8, 1217.9, 1535.1), "giro": 0},
              {"pt": (1473.2, 1624.9, 1501.6, 1674.8), "giro": 90}]


def cooktops_b(out):
    import sys as _sys
    _sys.path.insert(0, str(RAIZ / "_blocos"))
    import blocos
    _, p2r = AJ.pdf_pavimento("Terreo")
    px_m = px_por_m("Terreo")
    H, W = out.shape[:2]
    img = out.astype(np.float32)
    for c in COOKTOPS_B:
        r = ret_px(p2r, c["pt"])
        g = 3
        X0, Y0, X1, Y1 = int(np.floor(r[0])) - g, int(np.floor(r[1])) - g, int(np.ceil(r[2])) + g, int(np.ceil(r[3])) + g
        # o tampo em volta: a mediana do anel de quartzo em volta (sem o desenho do motor), com um grão leve
        anel = np.zeros((H, W), bool)
        anel[Y0 - 3:Y1 + 3, X0 - 3:X1 + 3] = True
        anel[Y0:Y1, X0:X1] = False
        lum = img.mean(axis=2)
        anel &= lum > np.percentile(lum[anel], 40)
        cor = np.median(img[anel], axis=0)
        m = np.zeros((H, W), np.float32)
        m[Y0:Y1, X0:X1] = 1
        m = cv2.GaussianBlur(m, (0, 0), 0.6)
        rng = np.random.default_rng(11)
        gr = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 0.7)
        tampo = cor[None, None] * (1 + 0.012 * gr / max(gr.std(), 1e-6))[..., None]
        img = img * (1 - m[..., None]) + tampo * m[..., None]
        cb, ab = blocos.bloco("cooktop_inox_5_90", px_m)
        for _ in range(c["giro"] // 90):
            cb, ab = cv2.rotate(cb, cv2.ROTATE_90_CLOCKWISE), cv2.rotate(ab, cv2.ROTATE_90_CLOCKWISE)
        w, h = int(round(r[2] - r[0])) + 1, int(round(r[3] - r[1])) + 1
        cb = cv2.resize(cb, (w, h), interpolation=cv2.INTER_AREA)
        ab = cv2.resize(ab, (w, h), interpolation=cv2.INTER_AREA)
        img = pousar_rgba(img, cb, ab, (r[0] + r[2]) / 2, (r[1] + r[3]) / 2)
    print(f"    {len(COOKTOPS_B)} cooktops de inox, 5 bocas, no retângulo do PDF (gourmet deitado, ilha em pé)")
    return np.clip(img, 0, 255).astype(np.uint8)


# Térreo 13 ("a confirmar"; decidido pela regra da seção 4, "portões de correr da área descoberta em alumínio"): os
# portões em zigue-zague da ARQ_ELEMENTOS FIXOS (folhas de 0,25 m, entre o jardim do hall e a garagem e entre a área de
# serviço descoberta e a garagem), em alumínio, finos, com o contorno e a sombra curta, por cima das plantas e do piso.
PORTOES_B = {"zonas_pt": [(2095, 1435, 2330, 1462), (1898, 1808, 1972, 1832)], "aluminio": (196, 198, 200),
             "contorno": (104, 106, 110), "larg": 0.45}


def portoes_b(out):
    q = PORTOES_B
    _, p2r = AJ.pdf_pavimento("Terreo")
    px_m = px_por_m("Terreo")
    H, W = out.shape[:2]
    img = out.astype(np.float32)
    n = 0
    for z in q["zonas_pt"]:
        Z = pymupdf_rect(z)
        m = mascara_pdf("Terreo", (H, W), camadas=("ARQ_ELEMENTOS FIXOS",), folga=0,
                        filtro=lambda d, Z=Z: Z.contains(d["rect"]))
        al = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.5)
        al = np.maximum(al, m)
        img *= (1 - sombra_de(al, px_m, forca=0.30)[..., None])
        img = img * (1 - al[..., None]) + np.float32(q["aluminio"]) * al[..., None]
        borda = (cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & ~cv2.erode(
            m.astype(np.uint8), np.ones((2, 2), np.uint8)).astype(bool)).astype(np.float32)
        borda = cv2.GaussianBlur(borda, (0, 0), 0.4) * 0.7
        img = img * (1 - borda[..., None]) + np.float32(q["contorno"]) * borda[..., None]
        n += 1
    print(f"    portões em zigue-zague de alumínio nas {n} aberturas para a garagem")
    return np.clip(img, 0, 255).astype(np.uint8)


def pymupdf_rect(r):
    import pymupdf
    return pymupdf.Rect(*r)



# Subsolo 1 (R2): só o Subsolo, com o resto do terreno hachurado (o hachurado entra na final, `final_casab`). Pelo PDF
# (decidido pela proposta do pente fino): em cor cheia, o que está no nível do Subsolo, que são os preenchimentos da
# ARQ_CONTRAPISO e da ARQ_PAREDE do prédio, a ducha, o deck em L ao lado dela (o mesmo nível, sem degrau) e as duas
# escadas, que sobem dali (a de 9 degraus inteira; a de 6, até a pedra grande). A pedra grande e as pedras da esquerda
# (os preenchimentos oliva de x < 440 pt), no alto da escada de 6 degraus, são do nível do Térreo e vão para a hachura.
SUBSOLO_B = {"x_min_pt": 440.0, "camadas": ("ARQ_CONTRAPISO", "ARQ_PAREDE"), "escada6_pt": (516.0, 794.0, 604.0, 867.0),
             "escada9_pt": (728.8, 963.7, 917.6, 1071.4), "ss": 4, "fechar": 5, "anel": 2, "parede": 100,
             "incluir_pt": [(1254.9, 536.8, 1314.4, 591.6)],      # a circulação de 1,16 m², aberta em cima
             "mascara": CASA_B / "renders/POE642_CasaB_PH_Subsolo_pegada_mascara.png"}


def so_subsolo_b(out):
    q = SUBSOLO_B
    pg, p2r = AJ.pdf_pavimento("Subsolo")
    H, W = out.shape[:2]
    k = q["ss"]
    m = np.zeros((H * k, W * k), np.uint8)
    n = 0
    for d in pg.get_drawings():
        if d.get("layer") in q["camadas"] and d["type"] in ("f", "fs") and d["rect"].x0 >= q["x_min_pt"] \
                and d["rect"].width > 0.5:
            for c in AJ.caminhos_pdf(d, p2r):
                if len(c) >= 3:
                    cv2.fillPoly(m, [np.int32(np.round(c * k))], 255)
            n += 1
    for r in (q["escada6_pt"], q["escada9_pt"], *q["incluir_pt"]):
        (ax, ay), (bx, by) = p2r(r[0], r[1]), p2r(r[2], r[3])
        cv2.rectangle(m, (int(round(ax * k)), int(round(ay * k))), (int(round(bx * k)), int(round(by * k))), 255, -1)
    # a pedra grande passa por cima do canto do deck em L (ela é do nível do Térreo): o canto sai da pegada
    for d in pg.get_drawings():
        if d.get("layer") == "ARQ_CONTRAPISO" and d["type"] in ("f", "fs") and d["rect"].x0 < q["x_min_pt"]:
            for c in AJ.caminhos_pdf(d, p2r):
                if len(c) >= 3:
                    cv2.fillPoly(m, [np.int32(np.round(c * k))], 0)
    peg = cv2.resize(m.astype(np.float32) / 255, (W, H), interpolation=cv2.INTER_AREA)
    f = q["fechar"]
    peg = np.maximum(peg, cv2.morphologyEx((peg > 0.5).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((f, f), np.uint8)))
    # o que as paredes fecham (o poço do elevador com a cabine e o shaft, brancos na base) também é do Subsolo
    from scipy import ndimage
    peg = np.maximum(peg, ndimage.binary_fill_holes(peg > 0.5).astype(np.float32))
    a = q["anel"]
    perto = cv2.dilate((peg > 0.5).astype(np.uint8), np.ones((2 * a + 1, 2 * a + 1), np.uint8)).astype(bool)
    peg = np.maximum(peg, perto & (out.astype(np.float32).mean(axis=2) < q["parede"]))
    img = out.astype(np.float32) * peg[..., None] + 255 * (1 - peg[..., None])
    cv2.imwrite(str(q["mascara"]), np.round(peg * 255).astype(np.uint8))
    fora = (peg < 0.5) & (out.min(axis=2) < 245)
    print(f"    só o Subsolo (R2): {n} peças do PDF na pegada, mais as duas escadas; {int(fora.sum())} px do Térreo em "
          f"volta viram branco (o terreno hachurado entra na final); pegada em {q['mascara'].name}")
    return np.clip(np.round(img), 0, 255).astype(np.uint8)



# Térreo 6 e Subsolo (madeira da ducha): o deck na madeira da referência (R4), régua a régua, como o item 8 do pente fino da
# Casa A (`ajustes_casaa.deck_referencia`, com os números de lá, `DECK_A`), mas em todas as manchas de deck dadas (na
# Casa A só a maior): no Térreo, os dois decks da piscina; no Subsolo, a ducha e o deck em L. As réguas já estavam na
# escala (~19 cm); muda o tom avermelhado do motor (RGB ~170, 114, 86) para o da referência (~191, 160, 133). As réguas
# ficam deitadas, como no PDF; a luz larga do lugar e as sombras ficam.
def deck_madeira(out, deck, px_m, semente=8, luz_local=True):
    from texturas_escala import nconv
    q = AJ.DECK_A
    ys, xs = np.nonzero(deck)
    x0, y0, x1, y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    w, h = x1 - x0, y1 - y0
    K = q["ss"]
    f = px_m / q["fonte_px_m"] * K
    ref = cv2.imread(str(RAIZ / q["fonte"])).astype(np.float32)
    R = cv2.rotate(cv2.resize(ref, (round(ref.shape[1] * f), round(ref.shape[0] * f)), interpolation=cv2.INTER_CUBIC),
                   cv2.ROTATE_90_COUNTERCLOCKWISE)
    lin = R.mean(axis=(1, 2))
    P = q["regua_px"] * f
    juntas = [int(np.argmin(lin[:int(P) + 1]))]
    while juntas[-1] + 2 * P < len(lin):
        a_, b_ = int(round(juntas[-1] + P - P / 3)), int(round(juntas[-1] + P + P / 3))
        juntas.append(a_ + int(np.argmin(lin[a_:b_ + 1])))
    juntas = [j for j in juntas if j + P + 1 <= len(lin)]
    rng = np.random.default_rng(semente)
    HH, WW = h * K, w * K
    # a foto tem largura limitada: as tiras são emendadas no comprido, com espelho
    while R.shape[1] < WW + 2:
        R = np.concatenate([R, R[:, ::-1]], axis=1)
    T = np.zeros((HH, WW, 3), np.float32)
    y = -rng.uniform(0, P)
    while y < HH:
        b0, b1 = int(round(y)), int(round(y + P))
        tira = R[juntas[rng.integers(len(juntas))]:][:b1 - b0]
        if rng.random() < 0.5:
            tira = tira[:, ::-1]
        off = int(rng.integers(0, R.shape[1] - WW + 1))
        tira = tira[:, off:off + WW]
        s0, s1 = max(0, -b0), min(b1, HH) - b0
        if s1 > s0:
            T[b0 + s0:b0 + s1] = tira[s0:s1]
        y += P
    T = cv2.resize(T, (w, h), interpolation=cv2.INTER_AREA)
    im = out.astype(np.float32)
    mf = deck.astype(np.float32)
    Lg = nconv(im, mf, q["sig_luz_m"] * px_m)
    Lc = nconv(im, mf, q["sig_sombra_m"] * px_m)
    sombra = np.minimum(1.0, ((Lc.mean(axis=2) + 1) / (Lg.mean(axis=2) + 1)) / q["sombra_limiar"])
    luz = Lg / Lg[deck].mean(axis=0)
    if not luz_local:                  # a madeira em cor cheia onde o render estava esmaecido: a luz do lugar não serve
        luz, sombra = np.ones_like(luz), np.ones_like(sombra)
    novo = im.copy()
    novo[y0:y1, x0:x1] = (luz * sombra[..., None])[y0:y1, x0:x1] * T
    alfa = (cv2.GaussianBlur(mf, (0, 0), 0.7) * mf)[..., None]
    return np.clip(im * (1 - alfa) + novo * alfa, 0, 255).astype(np.uint8), int(deck.sum())


def manchas_base(forma, chave, cores, tol=6, area_min=500, fechar=3):
    b = AJ.base_terreo(forma, chave).astype(np.int32)
    m = np.zeros(forma, np.uint8)
    for c in cores:
        m |= (np.abs(b - np.array(c)).max(axis=2) <= tol).astype(np.uint8)
    if fechar:
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((fechar, fechar), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 4)
    return np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= area_min])


DECK_CORES_BGR = [(99, 136, 174), (76, 106, 138)]           # #AE8863 e o traço das réguas #8A6A4C da base


def deck_terreo(out):
    deck = manchas_base(out.shape[:2], "Terreo", DECK_CORES_BGR)
    out, n = deck_madeira(out, deck, px_por_m("Terreo"))
    print(f"    deck: {n} px nos dois decks da piscina, na madeira da referência (réguas de ~20 cm)")
    return out


ITENS = {
    "Terreo": [
        ("01a", "item 1: jardim de inverno com as plantas da biblioteca no tamanho real", jardim_inverno),
        ("01b", "item 1: jardim de 4,62 m² do hall com as plantas da biblioteca no tamanho real", jardim_hall),
        ("25", "item 25: a floreira junto ao lavatório gourmet", floreira),
        ("06a", "item 6: grama da referência", grama_terreo),
        ("01c", "item 1: vegetação do gramado no tamanho real, dentro do lote e fora dos pisos", vegetacao_terreo),
        ("06b", "item 6: deck na madeira da referência", deck_terreo),
        ("03", "item 3: granito marrom da referência", granito_terreo),
        ("04", "item 4: travertino na escala, com o veio horizontal", travertino_terreo),
        ("05", "item 5: vinílico em réguas de ~20 cm", vinilico_terreo),
        ("07", "item 7 (R12): os três carros prata, iguais, de 4,70 x 1,85 m, alinhados", carros_b),
        ("09", "item 9 (R3): portas sem os arcos", sem_arcos_terreo),
        ("10", "item 10 (R14): escadas com os bocéis, a sombra curta e o triângulo", escadas_terreo),
        ("11", "item 11 (R8): os dois pilares redondos em preto", pilares_terreo),
        ("14", "item 14: armários até o teto em marcenaria areia, sem a diagonal", armarios_terreo),
        ("15", "item 15: eletrodomésticos em inox na cozinha e o refrigerador do gourmet", inox_terreo),
        ("18", "item 18: a bancada da sala íntima com a cuba", bancada_sala_intima),
        ("24a", "item 24: quartzito Carrara nas bancadas e na ilha", carrara_terreo),
        ("16", "item 16: cooktops de 5 bocas", cooktops_b),
        ("17", "item 17: a adega com a prateleira de vinhos", adega_b),
        ("19", "item 19: o elevador com a cabine", elevador_cabine),
        ("24b", "item 24: banquetas de linho na bancada gourmet", banquetas_gourmet),
        ("13", "item 13: os portões em zigue-zague", portoes_b),
        ("20", "item 20: portas, vidros e janelas finos", vidros_terreo),
        ("21", "item 21: cortinas de linho com o trilho de parede a parede", cortinas_terreo),
        ("24c", "item 24: a roupa de cama da biblioteca nas camas", camas_terreo),
        ("24d", "item 24: boxes com as duas folhas de vidro contínuas", boxes_terreo),
        ("23", "item 23 (R13): soleiras nos vãos brancos do PDF", soleiras_terreo),
        ("22", "item 22: paredes pretas no contorno do PDF", paredes_terreo),
        ("12", "item 12 (R8): projeções do jardim de inverno por cima; sem o X do hall", projecoes_terreo),
        ("02", "item 2: pedra portuguesa de 7 cm em leque, no tom da foto", pedra_terreo),
    ],
    "Subsolo": [
        ("03", "item 3: travertino na escala, com o veio horizontal", travertino_subsolo_b),
        ("02", "item 2: Bege Bahia da referência (garagem, circulações e BH serviço)", bege_subsolo_b),
        ("02b", "item 2: a circulação de 1,16 m² (branca no PDF) em Bege Bahia", circulacao_subsolo),
        ("04", "item 4: academia com o piso contínuo, em réguas de ~20 cm", vinilico_subsolo),
        ("01a", "item 1: a ducha e o deck em L em cor cheia, na madeira da referência", deck_subsolo),
        ("05-06", "itens 5 e 6 (R14): as escadas de 6 e 9 degraus em cor cheia, com os bocéis e o triângulo",
         escadas_subsolo),
        ("07", "item 7 (R3): portas sem os arcos", sem_arcos_subsolo),
        ("08", "item 8: portas, vidros e janelas finos", vidros_subsolo),
        ("10", "item 10 (R13): soleiras nos vãos brancos do PDF", soleiras_subsolo),
        ("11", "item 11: paredes pretas no contorno do PDF", paredes_subsolo),
        ("01b", "item 1 (R2): só o Subsolo; o resto do terreno sai (hachurado na final)", so_subsolo_b),
    ],
}


def antes_depois(antes, depois, nome, margem=40, max_lado=1800):
    """O antes e o depois do item, lado a lado (ou um sobre o outro), no recorte do que mudou, ampliado."""
    dif = np.abs(depois.astype(int) - antes.astype(int)).max(axis=2) > 0
    if not dif.any():
        return False
    ys, xs = np.nonzero(dif)
    H, W = dif.shape
    x0, y0 = max(xs.min() - margem, 0), max(ys.min() - margem, 0)
    x1, y1 = min(xs.max() + margem + 1, W), min(ys.max() + margem + 1, H)
    a, d = antes[y0:y1, x0:x1], depois[y0:y1, x0:x1]
    lado = (x1 - x0) <= (y1 - y0) * 1.3
    junto = np.hstack([a, np.full((a.shape[0], 12, 3), 255, np.uint8), d]) if lado else \
        np.vstack([a, np.full((12, a.shape[1], 3), 255, np.uint8), d])
    k = min(3.0, max_lado / max(junto.shape[:2]))
    if k > 1:
        junto = cv2.resize(junto, None, fx=k, fy=k, interpolation=cv2.INTER_LANCZOS4)
    elif k < 1:
        junto = cv2.resize(junto, None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
    cv2.imwrite(str(nome), junto, [cv2.IMWRITE_JPEG_QUALITY, 90])
    return True


def rodar(chave, ate=None, de=None, saida=CASA_B / "renders"):
    contexto()
    CACHE.mkdir(parents=True, exist_ok=True)
    orig = cv2.imread(str(AJ.APROVADAS[chave]))
    out = orig.copy()
    itens = ITENS[chave]
    chaves = [n for n, _, _ in itens]
    i0 = 0
    if de is not None:
        i0 = chaves.index(de)
        if i0 > 0:
            out = cv2.imread(str(CACHE / f"{chave}_{chaves[i0 - 1]}.png"))
    for n, desc, f in itens[i0:]:
        print(f"[{chave} {n}] {desc}")
        antes = out.copy()
        out = f(out)
        cv2.imwrite(str(CACHE / f"{chave}_{n}.png"), out)
        nome = saida / f"POE642_CasaB_PH_{chave}_{n}_antes_depois.jpg"
        if antes_depois(antes, out, nome):
            print(f"    {int((np.abs(out.astype(int) - antes.astype(int)).max(axis=2) > 0).sum())} px; {nome.name}")
        if n == ate:
            break
    if ate is None or ate == chaves[-1]:
        nome = CASA_B / PAVIMENTOS_B[chave]["render"]
        cv2.imwrite(str(nome), out)
        alfa = np.where(np.abs(out.astype(int) - orig.astype(int)).max(axis=2) > 0, 255, 0).astype(np.uint8)
        cv2.imwrite(str(nome.with_name(nome.stem + "_camada.png")), np.dstack([out, alfa]))
        print(f"[fim] {nome}; {int((alfa > 0).sum())} px alterados")
    return out



# ---------------------------------------------------------------------------------------------------------------------
# Imagem final (3840 px, no quadro comum) com os rótulos
# ---------------------------------------------------------------------------------------------------------------------
# rótulos: os do PDF que não entram (o "Ref." da geladeira do gourmet e o "SUÍTE 2 · 15,71 m²" solto atrás da suíte
# master, fora de qualquer ambiente; decisão pela proposta do pente fino) e os renomeados (o banho da suíte master
# está como "SUÍTE MASTER · 13,7 m²" no PDF, repetindo o nome do quarto: fica "BANHO MASTER", com a área do PDF)
ROTULOS_FORA = [("Ref.", None), ("SUÍTE 2", (816.5, 536.1))]
ROTULOS_NOMES = [("SUÍTE MASTER", (1196.6, 621.7), "BANHO MASTER")]


def _perto(c, alvo, tol=6.0):
    return alvo is None or (abs(c[0] - alvo[0]) < tol and abs(c[1] - alvo[1]) < tol)


def rotulos_casab(pg, p2q2000):
    import retoque_1pav_casae as R1
    rot = []
    for nome, linhas, centro, caixa in R1.rotulos_pdf(pg):
        if any(f in nome for f in A.FORA):
            continue
        if any(nome == n and _perto(centro, al) for n, al in ROTULOS_FORA):       # centros em pt do PDF
            continue
        for n, al, novo in ROTULOS_NOMES:
            if nome == n and _perto(centro, al):
                linhas = [(novo,) + tuple(linhas[0][1:])] + list(linhas[1:])
                nome = novo
        rot.append((nome, linhas, centro, caixa))
    return rot


def final_casab(chave, salvar=True):
    import pymupdf
    from PIL import Image
    import retoque_1pav_casae as R1
    from opcoes_1pav_casae import quadro_pdf
    from texturas_escala import trocar_pedra_portuguesa
    contexto()
    q = PAVIMENTOS_B[chave]
    cfg = json.loads(CONFIG_B.read_text())
    base = (CASA_B / cfg["entrega"]["pasta_bases"] / cfg["entrega"]["pavimentos"][chave]["base"]).resolve()
    ajustes = cv2.imread(str(CASA_B / q["render"]))
    pg = pymupdf.open(RAIZ / "_pdfs_cliente" / q["pdf"])[cfg["pavimentos"][chave]["pagina"]]
    at, lt = cv2.imread(str(base), cv2.IMREAD_GRAYSCALE).shape
    hb, wb = cv2.imread(str(CASA_B / q["sem_tela"]), cv2.IMREAD_GRAYSCALE).shape
    p2q = quadro_pdf(pg, cfg, lt, at, wb, hb, A.LARGURA)
    p2q2 = quadro_pdf(pg, cfg, lt, at, wb, hb, 2000)
    (a, b), (c, d) = p2q(0, 0), p2q(56.69, 0)
    px_m = float(np.hypot(c - a, d - b))
    W = A.LARGURA
    H = round(at * W / lt)
    if chave == "Terreo":
        aprovada = Image.open(CASA_B / q["aprovada"]).convert("RGB")
        final = A.no_quadro_fixo(Image.fromarray(cv2.cvtColor(ajustes, cv2.COLOR_BGR2RGB)), aprovada, base, chave)
        # a pedra portuguesa redesenhada nos 3840 px (item 2): as pedras de 7 cm em leque, no tom da foto, na máscara do
        # ajuste levada ao quadro (só o miolo; a borda fica com a pedra do ajuste)
        mq = CASA_B / "renders" / "POE642_CasaB_PH_Terreo_pedra_mascara.png"
        if mq.exists():
            m = cv2.imread(str(mq), cv2.IMREAD_GRAYSCALE)
            mfin = A.no_quadro_fixo(Image.fromarray(cv2.cvtColor(ajustes, cv2.COLOR_BGR2RGB)), aprovada, base, chave,
                                    mascara=m)[1]
            final, n = trocar_pedra_portuguesa(final, mfin > 200, px_m, fonte="leque")
            print(f"    pedra portuguesa redesenhada na final: {n} px, a {px_m:.1f} px/m")
    else:
        # o Subsolo: o que não mudou nos ajustes volta da imagem de 6905 px (mais nítida); o que mudou vem dos ajustes
        orig = cv2.imread(str(CASA_B / q["original"]))
        nitida = cv2.resize(orig, (W, H), interpolation=cv2.INTER_AREA)
        ap = cv2.imread(str(CASA_B / q["aprovada"]))
        mudou = (np.abs(ajustes.astype(int) - ap.astype(int)).max(axis=2) > 0).astype(np.uint8)
        mudou = cv2.dilate(mudou, np.ones((3, 3), np.uint8))
        mq = cv2.resize(mudou.astype(np.float32), (W, H), interpolation=cv2.INTER_LINEAR)
        mq = np.clip(cv2.GaussianBlur(mq, (0, 0), 0.8) * 1.5, 0, 1)[..., None]
        amp = cv2.resize(ajustes, (W, H), interpolation=cv2.INTER_LANCZOS4)
        final = np.clip(nitida * (1 - mq) + amp * mq, 0, 255).astype(np.uint8)
        print(f"    Subsolo: {100 * float(mq.mean()):.1f}% do quadro vem dos ajustes; o resto, da imagem de 6905 px")
        pq = CASA_B / "renders" / "POE642_CasaB_PH_Subsolo_pegada_mascara.png"
        # o terreno hachurado vem do Térreo final da Casa B (o lote dele, no mesmo quadro)
        AJ.SUBSOLO_R2 = dict(AJ.SUBSOLO_R2, terreo=CASA_B / "renders" / "POE642_CasaB_PH_Terreo_final_rotulos.png")
        if pq.exists():
            peg = cv2.resize(cv2.imread(str(pq), cv2.IMREAD_GRAYSCALE), (W, H), interpolation=cv2.INTER_LINEAR)
            final = AJ.subsolo_hachurado(final, peg.astype(np.float32) / 255, px_m)
    rot = rotulos_casab(pg, p2q2)
    print(f"    {len(rot)} rótulos: " + ", ".join(r[0] for r in rot))
    final = R1.rotulos_ambientes(final, rot, p2q, escala_desvio=W / 2000,
                                 granito=A.granito(final, q.get("granito_lum_max", 125)), ajustes=q["ajustes"],
                                 cor_granito=R1.ROTULOS["branco"])
    if salvar:
        nome = CASA_B / "renders" / f"POE642_CasaB_PH_{chave}_final_rotulos.png"
        cv2.imwrite(str(nome), final)
        print(f"    {nome} {final.shape[1]}x{final.shape[0]}")
    return final


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pavimento", choices=list(PAVIMENTOS_B))
    ap.add_argument("--ate", default=None, help="para depois deste item")
    ap.add_argument("--de", default=None, help="recomeça deste item, com a etapa anterior do cache")
    ap.add_argument("--final", action="store_true", help="a imagem final no quadro de 3840 px, com os rótulos")
    args = ap.parse_args()
    if args.final:
        final_casab(args.pavimento)
    else:
        rodar(args.pavimento, args.ate, args.de)


if __name__ == "__main__":
    main()

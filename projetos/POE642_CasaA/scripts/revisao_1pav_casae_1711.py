"""1º Pavimento da Casa E, 17/11 (usuário: "Reduzir as manchas do mármore bege Bahia igual ao das outras casas / Vamos
alterar os bancos em frente as camas para um outro modelo da biblioteca. / Corrigir os armários com cabides em L, revendo
dividirias entre eles, como fizemos nas outras casas. / Tracejados em cinza, não pretos. Traços mais finos também."):

  1. `bege`: o Bege Bahia com as manchas a 35%, a rotina das Casas C e D (`pedidos_subsolo_casac_1311.bege`, pela
     legenda 232 do quadro). A bancada da copinha fica de fora (`BEGE_FORA`, px): a legenda só cobre a parte dela à
     esquerda da cuba, e o resto da pedra ficaria com outro desenho.
  2. `closets`: os closets em L (1, 2, 3 e 4) numa peça só, como os da Casa A (`um_pav_casaa_1111._closet`) e os
     contínuos da Casa D (`biblioteca_terreo_casad_1511.CLOSETS_CONTINUOS`): cada trecho sem o canto, o canto à parte,
     os cabides até o canto, o cabideiro se encontrando no meio do canto, a moldura só por fora; sai a lateral entre os
     dois trechos. As peças (pt) são as de `retoque_1pav_casae.GUARDA_ROUPAS`; os dois trechos retos do closet master
     ficam como estão.
  3. `bancos`: os 5 bancos de pé de cama (o estofado bege de 11/11) trocados pelo `banco-k4` da biblioteca da Casa A
     (couro caramelo em três gomos, moldura escura): no retângulo de fora do banco de antes, contorno incluído (px), a
     sombra curta de antes fica; na suíte 3, a cama embaixo, o banco girado 180°.
  4. `tracejados`: os tracejados do PDF (os vazios da escada e do hall, o shaft, a rouparia e as projeções do banho
     master) em cinza e mais finos, como o pergolado da Casa B (`correcoes_terreo_casab_1611.PERGOLADO_BRISES`: cinza
     128, 0,8 px): `final3840_casae.tracejados_1p_sobre_final` com `TRACEJADOS_1P` nesse traço (no fundo escuro, o
     cinza claro de `CINZA_ESCURO`); o traço preto de 1,5 px sai pela limpeza da própria rotina.

Não há 12K do 1º Pavimento da E.

  python3 revisao_1pav_casae_1711.py [--passos bege,closets,bancos,tracejados] [--saida <png>]
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
FINAL = AQUI.parents[1] / "POE642_CasaE/renders/POE642_CasaE_PH_1Pavimento_v1_final.png"
BIBLIOTECA = AQUI.parents[0] / "biblioteca-objetos/03-primeiro-pavimento/bancos-pe-de-cama-propostas"

# 1. a bancada da copinha (px), fora do Bege Bahia
BEGE_FORA = [(1885, 912, 2025, 957)]

# 2. os closets em L (pt): (retângulo, lado das portas) de cada trecho sem o canto, e o canto
CLOSETS = {
    "closet 2": {"trechos": [((1992.5, 798.4, 2026.5, 866.4), "direita"), ((2026.5, 764.4, 2111.6, 798.4), "baixo")],
                 "cantos": [(1992.5, 764.4, 2026.5, 798.4)]},
    "closet 1": {"trechos": [((1992.5, 1147.0, 2026.5, 1215.1), "direita"), ((2026.5, 1113.0, 2111.6, 1147.0), "baixo")],
                 "cantos": [(1992.5, 1113.0, 2026.5, 1147.0)]},
    "closet 4": {"trechos": [((1411.4, 1339.8, 1496.4, 1371.0), "cima"), ((1496.4, 1285.9, 1530.5, 1339.8), "esquerda")],
                 "cantos": [(1496.4, 1339.8, 1530.5, 1371.0)]},
    "closet 3": {"trechos": [((1411.4, 1382.3, 1496.4, 1413.5), "baixo"), ((1496.4, 1413.5, 1530.5, 1467.4), "esquerda")],
                 "cantos": [(1496.4, 1382.3, 1530.5, 1413.5)]},
    "semente": 1711}

# 3. os bancos: o retângulo de fora do banco de antes (px da final, o contorno escuro incluído) e o giro
BANCOS = {"png": BIBLIOTECA / "banco-k4.png", "sombra": 0.0,
          "bancos": [("suíte master", (1502.5, 742.5, 1629.5, 769.0), 0),
                     ("suíte 2", (2350.5, 809.5, 2434.5, 836.0), 0),
                     ("suíte 4", (1464.5, 1019.5, 1548.5, 1045.0), 0),
                     ("suíte 1", (2350.5, 1176.5, 2434.5, 1202.0), 0),
                     ("suíte 3", (1468.5, 1377.5, 1552.5, 1404.0), 180)]}

# 4. o traço dos tracejados: o cinza do pergolado da Casa B, fino; no fundo escuro, um cinza claro
CINZA = (128, 128, 128)
CINZA_ESCURO = (200, 200, 200)
LARG_PX = 0.8

PASSOS = ("bege", "closets", "bancos", "tracejados")


def bege(Q, out, fora=BEGE_FORA):
    import pedidos_subsolo_casac_1311 as PS
    guarda = Q.chapada
    ch = guarda.copy()
    for x0, y0, x1, y1 in fora:
        reg = ch[y0:y1, x0:x1]
        reg[np.all(reg == 232, axis=2)] = (0, 0, 1)
    Q.chapada = ch
    try:
        return PS.bege(Q, out)
    finally:
        Q.chapada = guarda


def closets(Q, out, q=CLOSETS):
    import um_pav_casaa_1111 as U
    rng = np.random.default_rng(q["semente"])
    nomes = [k for k in q if k != "semente"]
    out = np.ascontiguousarray(out.copy())
    for nome in nomes:
        out = U._closet(Q, out, q[nome], dict(U.CLOSETS_1P), rng)
    print(f"    closets em L numa peça só, sem a lateral entre os trechos: {', '.join(nomes)}")
    return out


def _pingos(out, r, folga=12, acima=18, croma_max=40):
    """Os pingos de cor do banco antigo no tapete em volta do retângulo r (px): os px bem mais coloridos que a mediana
    de 9 px em volta, num fundo pouco colorido (o tapete; a madeira fica de fora), vêm dos vizinhos (inpaint)."""
    X0, Y0 = int(r[0]) - folga, int(r[1]) - folga
    X1, Y1 = int(np.ceil(r[2])) + folga, int(np.ceil(r[3])) + folga
    reg = np.ascontiguousarray(out[Y0:Y1, X0:X1])
    I = reg.astype(np.int16)
    cro = (I.max(-1) - I.min(-1)).astype(np.uint8)
    med = cv2.medianBlur(cro, 9).astype(np.int16)
    banco = np.zeros(cro.shape, bool)
    banco[int(r[1]) - Y0 - 1:int(np.ceil(r[3])) - Y0 + 1, int(r[0]) - X0 - 1:int(np.ceil(r[2])) - X0 + 1] = True
    m = (cro > med + acima) & (med < croma_max) & ~banco
    if m.any():
        m = cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)) & ~banco
        out[Y0:Y1, X0:X1] = cv2.inpaint(reg, m.astype(np.uint8), 3, cv2.INPAINT_TELEA)
    return int(m.sum())


def bancos(out, q=BANCOS):
    import instalacao_terreo_casad_1711 as ID
    P = cv2.imread(str(q["png"]), cv2.IMREAD_UNCHANGED)
    rgb, a = P[..., :3], P[..., 3].astype(np.float32) / 255
    out = out.copy()
    n = 0
    for nome, r, giro in q["bancos"]:
        rr, aa = (cv2.rotate(rgb, cv2.ROTATE_180), cv2.rotate(a, cv2.ROTATE_180)) if giro == 180 else (rgb, a)
        ID._pousar(out, rr, aa, r, q["sombra"], 1.0)
        n += _pingos(out, r)
    print(f"    bancos de pé de cama: o {q['png'].stem} (couro caramelo) em {len(q['bancos'])} suítes "
          f"({', '.join(n for n, _, _ in q['bancos'])}); {n} px de pingos do banco antigo no tapete refeitos")
    return out


VAZIOS = ("vazio da escada", "vazio do hall")


def _faixa_vazios(Q, img, trechos, meia_px=3, sigma=3.0):
    """Nos vazios (o Térreo nublado, liso), a faixa do traço preto antigo (`meia_px` para cada lado das linhas do X) vem
    da média gaussiana do nublado de fora dela (convolução normalizada): a limpeza por deslocamento deixava listras."""
    import final3840_casae as FE
    dentro = cv2.erode(FE._onde_terreo(Q)[1].astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool)
    S = 4
    faixa = np.zeros(img.shape[:2], np.uint8)
    for nome, tr in trechos:
        if nome not in VAZIOS:
            continue
        for x0, y0, x1, y1 in tr:
            (u0, v0), (u1, v1) = Q.p2q(x0, y0), Q.p2q(x1, y1)
            cv2.line(faixa, (int(round(u0 * S)), int(round(v0 * S))), (int(round(u1 * S)), int(round(v1 * S))), 1,
                     thickness=2 * meia_px + 1, lineType=cv2.LINE_8, shift=2)
    faixa = faixa.astype(bool) & dentro
    if not faixa.any():
        return img
    fonte = (dentro & ~faixa).astype(np.float32)
    im = img.astype(np.float32)
    num = cv2.GaussianBlur(im * fonte[..., None], (0, 0), sigma)
    den = cv2.GaussianBlur(fonte, (0, 0), sigma)
    lisa = num / np.maximum(den, 1e-4)[..., None]
    out = img.copy()
    ok = faixa & (den > 0.05)
    out[ok] = np.clip(np.round(lisa[ok]), 0, 255).astype(np.uint8)
    print(f"    vazios: a faixa do traço antigo ({int(ok.sum())} px) pelo nublado de fora dela")
    return out


def tracejados(Q, out):
    import final3840_casae as FE
    guarda, pb = FE.TRACEJADOS_1P, FE.tracejados_pb_te

    def pb_liso(Q_, img, q=None, vaos=True, trechos=None):
        if trechos is not None:
            img = _faixa_vazios(Q_, img, trechos)
        return pb(Q_, img, q=q, vaos=vaos, trechos=trechos)
    FE.TRACEJADOS_1P = dict(guarda, larg_px=LARG_PX, preto=CINZA, branco=CINZA_ESCURO)
    FE.tracejados_pb_te = pb_liso
    try:
        return FE.tracejados_1p_sobre_final(Q, out)
    finally:
        FE.TRACEJADOS_1P, FE.tracejados_pb_te = guarda, pb


def main():
    import final3840_casae as FE
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--passos", default=",".join(PASSOS))
    ap.add_argument("--entrada")
    ap.add_argument("--saida")
    a = ap.parse_args()
    passos = a.passos.split(",")
    Q = FE.QuadroE("1Pavimento")
    out = cv2.imread(a.entrada or str(FINAL))
    for p in PASSOS:
        if p not in passos:
            continue
        print(f"[{p}]")
        out = {"bege": lambda o: bege(Q, o), "closets": lambda o: closets(Q, o), "bancos": bancos,
               "tracejados": lambda o: tracejados(Q, o)}[p](out)
    cv2.imwrite(a.saida or str(FINAL), out)


if __name__ == "__main__":
    main()

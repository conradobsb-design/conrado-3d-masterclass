"""Térreo da Casa C, as correções de 17/11 vendo o Térreo ("VAMOS VER COMO ESTÁ O TERREO DA CASA C"), na final e direto
nos 12K A e B, cada peça desenhada na escala de cada imagem, no afim afinado ali (`Mapa.local` do roteiro da Casa B: a
final ampliada casada com o 12K):

1. `cubas_cozinha` ("CORRIJA AS MANCHAS E O CONTORNO"): na bancada da pia da cozinha, a troca pelo Dekton Danae da foto
   (949e551) deixou a pedra granulada antiga entre as 2 cubas e acima delas, e uns cinzas soltos junto à janela
   ("manchas"); as cubas de inox tinham o contorno marrom grosso, passando do retângulo do PDF. A faixa das cubas
   (`pedra`) recebe o Danae do trecho limpo da mesma bancada à direita, nas mesmas linhas, dobrado em espelho (emenda
   macia à esquerda); as cubas ficam no retângulo do PDF (ARQ_LOUÇAS E METAIS: o inox de dentro, o de antes) com um fio
   cinza fino de contorno; as torneiras do PDF ficam como estão.
2. `armarios_c` ("REMOVA AS LINHAS TÉCNICAS", o aparador da circulação junto ao jantar, com os arcos tracejados das
   portas nas pontas; "APLICAR COR SÓLIDA NOS ARMARIOS", "APLICAR COR SÓLIDA, NÃO NOGUEIRA", os armários dos quartos 3,
   2 e 1, em madeira com veio, o do quarto 1 em nogueira; "TOM DO ARMARIO NA COR SÓLIDA QUE DEFINIMOS NA CASA A"): no
   retângulo do PDF, na cor sólida dos armários (`revisao_terreo_casac_1311.COZINHA`: o miolo liso, a face um tom
   abaixo, a sombra curta), pelo `correcoes_terreo_casab_1611.armarios`.
3. `armario_l_escritorio` ("O L DO ARMÁRIO NÃO TEM DIVISÓRIA ENTRE OS DOIS ARMÁRIOS."): o armário em L do escritório (os
   2 retângulos da DOC_LINHAS E PROJEÇÕES, a perna da direita e a de baixo, cada uma num tom, com a emenda) numa peça
   só, no polígono do L, na mesma cor sólida (a face só no contorno de fora do L).
4. `mesinhas_seixo` ("MESINHAS LATERAIS EM TOM E SOBRETOM, FREIJÓ E NOGUEIRA"): os 2 pares de mesinhas seixo nas pontas
   do sofá do estar (cinza metálico desde 14/11), nos contornos do PDF
   (`renders/POE642_CasaC_PH_Terreo_seixos.json`): a de trás em freijó (o tampo do `aparador-freijo` da biblioteca da
   Casa D) e a da frente, por cima dela, em nogueira (um trecho liso da `mesa-centro-nogueira-adorno-d`), o veio no
   comprido, a borda um pouco mais escura, o contorno fino e a sombra curta (a da frente também sobre a de trás); antes,
   o cinza antigo, o halo claro dele no 12K e os pontinhos em volta saem (inpaint).

5. `armario_tv_master` ("ESSE ARMARIO DA TV PRECISA ESTAR NA COR SÓLIDA"): o rack da TV da suíte master (o retângulo
   da ARQ_LAYOUT HUMANIZAÇÃO, em madeira com veio) na cor sólida dos armários; a TV por cima, no retângulo do PDF, em
   grafite.
6. `mesinhas_redondas` ("AS TRES MESINHAS PEQUENAS REDONDAS TAMBÉM NO NOGUEIRA"): as 3 mesinhas redondas do estar da
   direita (cinza-escuras), nos círculos do PDF, na nogueira da mesa de centro ao lado (um trecho liso da
   `mesa-centro-redonda-nogueira-adorno` da biblioteca da Casa A), como as mesinhas seixo (a borda, o contorno, a
   sombra; o disco e a sombra antigos saem antes).
7. `pisante_mancha` ("CORRIJA A MANCHA NA PEDRA. ESTÁ NO CANTINHO INFERIOR A DIREITA"): o pisante quadrado do jardim
   de baixo, junto à fileira que vai ao hall: o canto de baixo à direita (uma mancha esverdeada, forte no 12K) recebe a
   pedra do mesmo pisante logo acima, com a emenda macia.

  python3 correcoes_terreo_casac_1711.py final [--saida <png>]
  python3 correcoes_terreo_casac_1711.py doze [--opcao AB] [--saida <jpg com {}>]
"""
import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import danae_foto as DF                                     # noqa: E402
import correcoes_terreo_casab_1611 as CB                    # noqa: E402
from correcoes_terreo_casab_1611 import Mapa, _alfa_poli    # noqa: E402
from janela_pia_casaa_1611 import alfa_contorno, alfa_ret, compor   # noqa: E402

FINAL = DF.PLANTAS["C_Terreo"]
DOZE = DF.DOZE_K["C_Terreo"]
RAIZ = AQUI.parents[1]

CUBAS = {"cubas": [(2260.2, 262.7, 2298.4, 288.9), (2308.0, 262.7, 2346.2, 288.9)],
         # as bases das torneiras (o círculo do PDF e a sombra dele na final) ficam
         "torneiras": [(2275.5, 257.5, 2283.5, 262.7), (2323.5, 257.5, 2331.5, 262.7)],
         # a faixa refeita: das cubas à janela (abaixo do caixilho) e à frente da bancada
         "pedra": [(2257.0, 253.2, 2351.0, 290.5), (2271.5, 251.6, 2340.0, 253.2)],
         "fonte_x": (2352.0, 2405.0), "emenda_px": 3.0,
         "contorno": (118, 118, 122), "contorno_px": 0.5, "caixa_local": (2190, 236, 2470, 300)}
ARMARIOS_C = {"aparador da circulação": (2094.2, 820.6, 2213.6, 844.5),
              "quarto 3": (1183.7, 351.9, 1204.6, 465.4),
              "quarto 2": (1673.3, 351.9, 1694.2, 465.4),
              "quarto 1": (1924.1, 351.9, 1942.0, 471.3)}
L_ESCRITORIO = [(2592.8, 1161.0), (2783.9, 1161.0), (2783.9, 981.9), (2801.8, 981.9), (2801.8, 1187.9),
                (2592.8, 1187.9)]
BIB = RAIZ / "POE642_CasaD/biblioteca-objetos/02-terreo"
SEIXOS = {"json": RAIZ / "POE642_CasaC/renders/POE642_CasaC_PH_Terreo_seixos.json",
          "freijo": (BIB / "hall-de-entrada/aparador-freijo.png", (12, 14, 644, 180)),
          "nogueira": (BIB / "living/mesa-centro-nogueira-adorno-d.png", (150, 560, 390, 830)),
          "borda": 0.82, "borda_px": 1.2, "contorno": 0.62, "contorno_px": 0.5,
          "sombra": 0.30, "folga_px": 7.0, "anel_px": 2.2}


TV_MASTER = {"rack": (906.0, 808.7, 1109.0, 826.6), "tv": (967.1, 823.6, 1047.6, 826.6), "grafite": (54, 54, 58),
             "contorno": (36, 36, 40), "contorno_px": 0.4}
REDONDAS = {"circulos": [(2297.46, 1353.98, 10.45), (2323.39, 1460.53, 10.45), (2185.34, 1507.01, 12.51)],
            "madeira": "nogueira_a", "anel_px": 3.0}
SEIXOS_NOG_A = (RAIZ / "POE642_CasaA/biblioteca-objetos/02-terreo/sala-de-estar/mesa-centro-redonda-nogueira-adorno.png",
                (100, 470, 280, 680))
PISANTE = {"canto": (2849.0, 1789.0, 2896.0, 1824.5), "dy": -40.0, "suave_px": 5.0,
           "caixa_local": (2725, 1650, 2915, 1845)}


def _local(out, mp, caixa):
    return mp.local(out, caixa) if mp.ref is not None else mp


# ----------------------------------------------------------------------------------------------------------------------
def cubas_cozinha(out, mp, q=CUBAS):
    m = _local(out, mp, q["caixa_local"])
    fonte = out.copy()
    a0, a1 = q["fonte_x"]
    larg = a1 - a0
    xr = max(r[2] for r in q["pedra"])
    xl = min(r[0] for r in q["pedra"])
    rs = [m.ret(r) for r in q["pedra"]]
    X0, Y0 = int(np.floor(min(r[0] for r in rs))), int(np.floor(min(r[1] for r in rs)))
    X1, Y1 = int(np.ceil(max(r[2] for r in rs))), int(np.ceil(max(r[3] for r in rs)))
    forma = (Y1 - Y0, X1 - X0)

    def loc(r):
        return (r[0] - X0, r[1] - Y0, r[2] - X0, r[3] - Y0)
    a = np.zeros(forma, np.float32)
    for r in rs:
        a = np.maximum(a, alfa_ret(loc(r), forma))
    for r in q["cubas"] + q["torneiras"]:
        a *= 1 - alfa_ret(loc(m.ret(r)), forma)
    # a emenda da esquerda, macia
    e = q["emenda_px"]
    xs = np.array([m.ux(X) for X in range(X0, X1)])
    a *= np.clip((xs - xl) / e, 0, 1)[None, :]
    novo = np.empty((forma[0], forma[1], 3), np.float32)
    for j, X in enumerate(range(X0, X1)):
        t = (xr - xs[j]) % (2 * larg)
        u = a0 + (t if t < larg else 2 * larg - t)
        novo[:, j] = fonte[Y0:Y1, int(np.floor(m.x(u)))]
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    reg = reg * (1 - a[..., None]) + novo * a[..., None]
    for r in q["cubas"]:
        reg = compor(reg, alfa_contorno(loc(m.ret(r)), q["contorno_px"] * m.s, forma), q["contorno"])
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    print("    cozinha: a pedra antiga e os cinzas soltos em volta das cubas viram o Danae da mesma bancada; as 2 cubas "
          "no retângulo do PDF, com o fio cinza fino no lugar do contorno marrom")


def armarios_c(out, mp, q=ARMARIOS_C):
    for nome, r in q.items():
        m = _local(out, mp, (int(r[0]) - 25, int(r[1]) - 25, int(r[2]) + 25, int(r[3]) + 25))
        CB.armarios(out, m, {nome: r}, couro=False)


def armario_poli(out, m, pts):
    import revisao_terreo_casac_1311 as RC
    c = RC.COZINHA
    p = [(m.x(x), m.y(y)) for x, y in pts]
    f = int(np.ceil(6 * m.s))
    X0, Y0 = int(min(v[0] for v in p)) - f, int(min(v[1] for v in p)) - f
    X1, Y1 = int(max(v[0] for v in p)) + f, int(max(v[1] for v in p)) + f
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    forma = reg.shape[:2]
    a, miolo = _alfa_poli([(x - X0, y - Y0) for x, y in p], forma, encolhe=m.s)
    M = np.float32([[1, 0, -1.0 * m.s], [0, 1, 1.3 * m.s]])
    sb = cv2.GaussianBlur(cv2.warpAffine(a, M, (forma[1], forma[0])), (0, 0), 1.1 * m.s) * (1 - a)
    reg = reg * (1 - c["sombra"] * sb)[..., None]
    cor = np.float32(c["cor_armario"])
    reg = compor(reg, a - miolo, cor * c["face"])
    reg = compor(reg, miolo, cor)
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)


def armario_l_escritorio(out, mp, pts=L_ESCRITORIO):
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    m = _local(out, mp, (int(min(xs)) - 30, int(min(ys)) - 30, int(max(xs)) + 5, int(max(ys)) + 5))
    armario_poli(out, m, pts)
    print("    escritório: o armário em L numa peça só, na cor sólida dos armários, sem a emenda entre as pernas")


_MADEIRA = {}


def _madeira(nome, q=SEIXOS):
    if nome not in _MADEIRA:
        p, (x0, y0, x1, y1) = q[nome] if nome in q else SEIXOS_NOG_A
        im = cv2.imread(str(p), cv2.IMREAD_UNCHANGED)[y0:y1, x0:x1]
        if im.shape[2] == 4:
            im = im[..., :3]
        _MADEIRA[nome] = cv2.rotate(im, cv2.ROTATE_90_CLOCKWISE).astype(np.float32)     # o veio em pé
    return _MADEIRA[nome]


def _tampo(reg, X0, Y0, pts, nome, q, sombra_em=None):
    """Um seixo (pts em px da imagem) na madeira `nome`: a sombra curta em volta (e na peça de trás), a madeira no
    comprido do seixo, a borda mais escura e o contorno fino."""
    forma = reg.shape[:2]
    p = np.float64(pts) - (X0, Y0)
    a, miolo = _alfa_poli(p, forma, encolhe=q["borda_px"] * q["_s"])
    s = q["_s"]
    M = np.float32([[1, 0, -1.0 * s], [0, 1, 1.3 * s]])
    sb = cv2.GaussianBlur(cv2.warpAffine(a, M, (forma[1], forma[0])), (0, 0), 1.1 * s) * (1 - a)
    reg *= (1 - q["sombra"] * sb)[..., None]
    # a madeira na caixa do seixo
    bx0, by0 = np.floor(p.min(0)).astype(int)
    bx1, by1 = np.ceil(p.max(0)).astype(int)
    T = _madeira(nome, q)
    w, h = bx1 - bx0, by1 - by0
    k = max(w / T.shape[1], h / T.shape[0])
    Tm = cv2.resize(T, (int(np.ceil(T.shape[1] * k)), int(np.ceil(T.shape[0] * k))), interpolation=cv2.INTER_AREA)
    tx = np.full((forma[0], forma[1], 3), Tm.mean(axis=(0, 1)), np.float32)
    ya, xa = max(by0, 0), max(bx0, 0)
    yb, xb = min(by0 + Tm.shape[0], forma[0]), min(bx0 + Tm.shape[1], forma[1])
    tx[ya:yb, xa:xb] = Tm[ya - by0:yb - by0, xa - bx0:xb - bx0]
    reg[:] = reg * (1 - a[..., None]) + tx * a[..., None] * (q["borda"] + (1 - q["borda"]) * miolo)[..., None]
    reg[:] = compor(reg, np.clip(a - _alfa_poli(p, forma, encolhe=q["contorno_px"] * s)[1], 0, 1) * 0.8,
                    tx.mean(axis=(0, 1)) * q["contorno"])
    return a


def mesinhas_seixo(out, mp, q=SEIXOS):
    pares = json.loads(q["json"].read_text())["pares"]
    for lado, par in pares.items():
        todos = np.float64(par["atras"] + par["frente"])
        x0, y0 = todos.min(0)
        x1, y1 = todos.max(0)
        m = _local(out, mp, (int(x0) - 30, int(y0) - 30, int(x1) + 30, int(y1) + 30))
        qq = dict(q, _s=m.s)
        f = int(np.ceil((q["folga_px"] + 6) * m.s))
        X0, Y0 = int(m.x(x0)) - f, int(m.y(y0)) - f
        X1, Y1 = int(np.ceil(m.x(x1))) + f, int(np.ceil(m.y(y1))) + f
        reg = out[Y0:Y1, X0:X1]
        forma = reg.shape[:2]
        atras = [(m.x(x), m.y(y)) for x, y in par["atras"]]
        frente = [(m.x(x), m.y(y)) for x, y in par["frente"]]
        # o cinza antigo e os pontinhos em volta saem (o piso é rosado: R > B; o cinza não)
        uniao = np.maximum(_alfa_poli(np.float64(atras) - (X0, Y0), forma)[0],
                           _alfa_poli(np.float64(frente) - (X0, Y0), forma)[0])
        I = reg.astype(np.int16)
        cinza = (I[..., 0] - I[..., 2]) > -4
        perto = cv2.dilate((uniao > 0.01).astype(np.uint8),
                           np.ones((2 * int(q["folga_px"] * m.s) + 1,) * 2, np.uint8)) > 0
        anel = cv2.dilate((uniao > 0.01).astype(np.uint8),
                          np.ones((2 * int(np.ceil(q["anel_px"] * m.s)) + 1,) * 2, np.uint8)) > 0
        buraco = ((cinza & perto) | anel).astype(np.uint8)
        buraco = cv2.dilate(buraco, np.ones((3, 3), np.uint8))
        limpo = cv2.inpaint(np.ascontiguousarray(reg), buraco, max(3, int(3 * m.s)), cv2.INPAINT_TELEA)
        R = limpo.astype(np.float32)
        _tampo(R, X0, Y0, atras, "freijo", qq)
        _tampo(R, X0, Y0, frente, "nogueira", qq)
        out[Y0:Y1, X0:X1] = np.clip(np.round(R), 0, 255).astype(np.uint8)
    print("    estar: as 4 mesinhas seixo em tom e sobretom, a de trás em freijó e a da frente em nogueira, nos contornos "
          "do PDF")


def armario_tv_master(out, mp, q=TV_MASTER):
    r = q["rack"]
    m = _local(out, mp, (int(r[0]) - 25, int(r[1]) - 25, int(r[2]) + 25, int(r[3]) + 25))
    CB.armarios(out, m, {"TV da suíte master": r}, couro=False)
    CB.pintar(out, m, [(q["tv"], "ret", q["grafite"], 0), (q["tv"], "contorno", q["contorno"], q["contorno_px"])])
    print("    suíte master: o rack da TV na cor sólida dos armários, a TV em grafite por cima")


def mesinhas_redondas(out, mp, q=REDONDAS, qs=SEIXOS):
    qs = dict(qs, nogueira_a=SEIXOS_NOG_A)
    for cx, cy, r in q["circulos"]:
        m = _local(out, mp, (int(cx - r) - 30, int(cy - r) - 30, int(cx + r) + 30, int(cy + r) + 30))
        qq = dict(qs, _s=m.s)
        f = int(np.ceil((r + q["anel_px"] + 8) * m.s))
        X0, Y0 = int(m.x(cx)) - f, int(m.y(cy)) - f
        X1, Y1 = int(m.x(cx)) + f, int(m.y(cy)) + f
        reg = out[Y0:Y1, X0:X1]
        forma = reg.shape[:2]
        t = np.linspace(0, 2 * np.pi, 96, endpoint=False)
        pts = [(m.x(cx + r * np.cos(a)), m.y(cy + r * np.sin(a))) for a in t]
        anel = [(m.x(cx + (r + q["anel_px"]) * np.cos(a)), m.y(cy + (r + q["anel_px"]) * np.sin(a))) for a in t]
        buraco = (_alfa_poli(np.float64(anel) - (X0, Y0), forma)[0] > 0.01).astype(np.uint8)
        limpo = cv2.inpaint(np.ascontiguousarray(reg), buraco, max(3, int(3 * m.s)), cv2.INPAINT_TELEA)
        R = limpo.astype(np.float32)
        _tampo(R, X0, Y0, pts, q["madeira"], qq)
        out[Y0:Y1, X0:X1] = np.clip(np.round(R), 0, 255).astype(np.uint8)
    print("    estar: as 3 mesinhas redondas na nogueira da mesa de centro, nos círculos do PDF")


def pisante_mancha(out, mp, q=PISANTE):
    m = _local(out, mp, q["caixa_local"])
    fonte = out.copy()
    rm = m.ret(q["canto"])
    X0, Y0, X1, Y1 = int(np.floor(rm[0])), int(np.floor(rm[1])), int(np.ceil(rm[2])), int(np.ceil(rm[3]))
    forma = (Y1 - Y0, X1 - X0)
    loc = (rm[0] - X0, rm[1] - Y0, rm[2] - X0, rm[3] - Y0)
    a = alfa_ret(loc, forma)
    e = q["suave_px"] * m.s
    xs, ys = np.arange(forma[1]) + 0.5, np.arange(forma[0]) + 0.5
    a *= np.clip((xs - loc[0]) / e, 0, 1)[None, :] * np.clip((ys - loc[1]) / e, 0, 1)[:, None]
    dy = int(round(q["dy"] * m.s))
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    src = fonte[Y0 + dy:Y1 + dy, X0:X1].astype(np.float32)
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg * (1 - a[..., None]) + src * a[..., None]), 0, 255).astype(np.uint8)
    print("    jardim: o canto de baixo à direita do pisante quadrado sem a mancha (a pedra de logo acima)")


PASSOS = (cubas_cozinha, armarios_c, armario_l_escritorio, mesinhas_seixo, armario_tv_master, mesinhas_redondas,
          pisante_mancha)
NOVOS_1711B = (armario_tv_master, mesinhas_redondas, pisante_mancha)


def aplicar(img, mp, passos=PASSOS):
    out = img.copy()
    for f in passos:
        f(out, mp)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("acao", choices=("final", "doze"))
    ap.add_argument("--opcao", default="AB")
    ap.add_argument("--saida")
    a = ap.parse_args()
    final = cv2.imread(str(FINAL))
    if a.acao == "final":
        cv2.imwrite(a.saida or str(FINAL), aplicar(final, Mapa()))
        return
    from PIL import Image
    for op in a.opcao:
        f = Path(str(DOZE).format(op))
        doze = cv2.imread(str(f))
        M = DF.afim_12k(final, doze)
        mp = Mapa(float(np.hypot(M[0, 0], M[1, 0])), (float(M[0, 2]), float(M[1, 2])))
        mp.ref = final
        out = aplicar(doze, mp)
        dpi = int(round(out.shape[1] / (420 / 25.4)))
        dest = a.saida.format(op) if a.saida else str(f)
        Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB)).save(dest, quality=95, subsampling=0, dpi=(dpi, dpi))
        print(f"    {Path(dest).name}")


if __name__ == "__main__":
    main()

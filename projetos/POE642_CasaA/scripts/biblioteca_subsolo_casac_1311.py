"""As peças da biblioteca no Subsolo da Casa C (13/11).

Usuário: "Vamos para biblioteca da casa C"; a proposta (`POE642_CasaC/renders/POE642_CasaC_PH_Subsolo_1311_proposta_
biblioteca_1.jpg`) aprovada com "Ok"; os PDFs da Casa C vieram anexados. As recomendadas são as escolhas da Casa A e da
Casa B para o mesmo ambiente (`biblioteca_subsolo_casab_1311`, de onde vêm as funções):
- **Sauna:** o banco reto de travertino da biblioteca no L do PDF (a perna junto à parede da direita, girada, e a de
  baixo, o degrau da frente) e no assento junto à parede de baixo, cada um no tom do de antes (as pontas na escala da
  altura, o meio esticado).
- **BH academia:** a cuba esculpida da biblioteca esculpida no granito da bancada (como no BH sauna da Casa B), no
  retângulo de baixo da bancada do PDF (onde a planta tem a cuba; o de cima, só o contorno, fica), com a faixa até a
  parede da direita; a bacia Carrara branca no retângulo do vaso do PDF (a caixa na parede da direita), o travertino
  logo à esquerda por baixo da marrom de antes; os 2 chuveiros de teto desenhados em planta no quadrado do PDF (os de
  antes, a foto do cromado, viram o travertino do lado).
- **Academia:** as 2 esteiras (`esteira-a`), as 2 bicicletas (`bicicleta-b`) e os 2 supinos (`banco-supino`) da
  biblioteca, no tamanho da Casa A (esteiras 1,76 x 0,77 m, bicicletas 1,23 x 0,51 m, supino 1,60 x 2,04 m), com o meio
  no meio do símbolo do PDF da Casa C e no sentido dele (o console para a esquerda; a barra do supino à esquerda do
  banco, como no PDF: sem espelhar); a sombra curta da Casa A. Os aparelhos de antes (os do render) saem com a sombra:
  o vinílico volta com as mesmas réguas (as do `vinilico_foto.trocar` da final, a mesma conta) vezes a luz do piso em
  volta.
- **Esquadrias:** o contorno fino em preto nos boxes, nas portas de vidro e nos caixilhos
  (`regras_terreo_casab_1311.esquadrias`, "FAÇA APENAS O CONTORNO DA ESQUADRIA EM PRETO").

  python3 biblioteca_subsolo_casac_1311.py [--antes <png>] [--saida <png>]
Sem --antes, parte da final do commit `ANTES_COMMIT`; sem --saida, grava a final e os antes e depois
`POE642_CasaC/renders/POE642_CasaC_PH_Subsolo_1311_<trecho>_antes_depois.jpg`.
"""

import argparse
import contextlib
import io
import subprocess
import sys
import types
from pathlib import Path

import cv2
import numpy as np
from scipy import ndimage

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import final3840_casaa as FA                     # noqa: E402
import final3840_casab as F                      # noqa: E402
import final3840_casac as C                      # noqa: E402
import biblioteca_subsolo_casaa_1211 as BS       # noqa: E402
import biblioteca_subsolo_casab_1311 as BB       # noqa: E402
import biblioteca_1pav_casaa_1211 as B1          # noqa: E402
import biblioteca_terreo_casaa_1211 as BT        # noqa: E402
import regras_terreo_casab_1311 as RT            # noqa: E402

CASA_C = AQUI.parents[1] / "POE642_CasaC"
R = CASA_C / "renders"
FINAL = R / "POE642_CasaC_PH_Subsolo_final_rotulos.png"
RAIZ_GIT = AQUI.parents[2]
ANTES_COMMIT = "4cfe4c5"
PX_M = B1.PX_M

# a sauna (pt): o L do degrau da frente (a perna junto à parede da direita e a de baixo) e o assento junto à parede de
# baixo; o tom de cada um vem do miolo do de antes
SAUNA = [("perna do L", (623.5, 991.4, 651.6, 1082.2), "v"),
         ("degrau do L", (549.7, 1082.2, 651.6, 1110.3), "h"),
         ("assento", (549.7, 1110.3, 651.6, 1138.8), "h")]
# o BH academia: a cuba (pt: o retângulo de baixo da bancada do PDF e a faixa até a parede da direita, com a torneira),
# o miolo da bacia da cuba (pt) e a semente; a bancada de granito em volta (pt), para o tom
BHA = {"cuba_pt": (782.6, 980.0, 809.6, 1015.1), "bacia_pt": (784.6, 982.6, 804.5, 1012.5),
       "bancada_pt": [(780.6, 1015.7, 809.6, 1057.4)], "semente": 1311, "croma_cromo": 20, "lum_cromo": 110}
BACIA = {"nome": "BH academia", "png": "banho-feminino-academia/bacia-carrara.png", "pt": (781.3, 1094.9, 810.4, 1114.9),
         "giro": "cw", "antes_px": (946, 912, 981, 939)}
# os chuveiros de teto (px): a placa do PDF; o de antes (a foto do cromado) vira o travertino do lado (dx, dy)
CH_T = "banho-master/chuveiro-quadrado-planta"
CHUVEIROS = [{"nome": "box de cima", "placa_px": (849.0, 843.0, 861.0, 855.0), "png": CH_T, "parede": None,
              "piso": (1, 0)},
             {"nome": "box de baixo", "placa_px": (849.0, 922.0, 861.0, 934.0), "png": CH_T, "parede": None,
              "piso": (1, 0)}]
# a academia: os símbolos do PDF (px do quadro, a caixa dos traços da ARQ_LAYOUT HUMANIZAÇÃO); o buraco dos aparelhos
# de antes: o que foge do piso esperado (`desvio`) perto do símbolo (`busca_px`), mais `folga_px`
ACADEMIA = {
    "pecas": [
        {"nome": "esteira de cima", "png": "academia/esteira-a.png", "pt": (971.4, 524.3, 1062.2, 564.0)},
        {"nome": "esteira de baixo", "png": "academia/esteira-a.png", "pt": (971.4, 581.0, 1062.2, 620.7)},
        {"nome": "bicicleta de cima", "png": "academia/bicicleta-b.png", "pt": (999.8, 674.8, 1048.0, 694.6)},
        {"nome": "bicicleta de baixo", "png": "academia/bicicleta-b.png", "pt": (999.8, 731.5, 1048.0, 751.3)},
        {"nome": "supino de cima", "png": "academia/banco-supino.png", "pt": (1262.4, 521.7, 1338.9, 619.2)},
        {"nome": "supino de baixo", "png": "academia/banco-supino.png", "pt": (1262.4, 691.8, 1338.9, 789.3)},
    ],
    "busca_px": 14, "folga_px": 3, "desvio": 22, "luz_sigmas": (4.0, 8.0, 16.0, 32.0), "razao_max": 0.005,
}
# os rótulos em fileira (regra: "Alinhados em grade", como no Subsolo da Casa B): a caixa do texto (px, com folga), o
# meio novo (y, o do rótulo da mesma fileira) e de que lado vem o piso que cobre o lugar de antes (dx, dy). VARANDA
# SUBSOLO na linha de ACADEMIA (y 498) e DEPÓSITO na de SAUNA (y 826); o BH ACADEMIA não cabe nessa fileira (entre a
# bancada e a parede há 51 px) e fica no espaço dele
ROTULOS = [{"nome": "VARANDA SUBSOLO", "caixa": (813, 456, 924, 485), "meio_y": 498.0, "piso": (1, 0)},
           {"nome": "DEPÓSITO", "caixa": (1086, 834, 1144, 865), "meio_y": 826.0, "piso": (1, 0)}]
ANTES_DEPOIS = {"sauna": (690, 735, 830, 975), "bh_academia": (820, 735, 1000, 975), "academia": (1130, 290, 1560, 620),
                "rotulos": (640, 420, 1420, 900)}


def quadro():
    if "Q" not in _Q:
        with contextlib.redirect_stdout(io.StringIO()):
            C.contexto_c()
            _Q["Q"] = F.Quadro("Subsolo")
    return _Q["Q"]


_Q = {}


def px(Q, r):
    return BS.caixa_px(Q, r)


# ----------------------------------------------------------------------------------------------------------------------
def sauna(Q, out, antes, par, reg):
    for nome, r, sentido in SAUNA:
        c = px(Q, r)
        e = 3
        x0, y0, x1, y1 = (int(np.ceil(c[0])) + e, int(np.ceil(c[1])) + e, int(np.floor(c[2])) - e,
                          int(np.floor(c[3])) - e)
        tom = np.median(antes[y0:y1, x0:x1].reshape(-1, 3), axis=0)
        if sentido == "h":
            P, _ = BB._banco_12k(c, tom)
        else:                                   # a perna em pé: o banco feito deitado e girado
            cr = (0.0, 0.0, c[3] - c[1], c[2] - c[0])
            P, _ = BB._banco_12k(cr, tom)
            P = BS.girar(P, "cw")
        out = BS.compor(out, P, c, nao=par)
        reg.append({"tipo": "banco", "c": list(c), "tom": [float(t) for t in tom], "sentido": sentido})
        print(f"    sauna: banco reto de travertino da biblioteca ({nome}), no tom do de antes "
              f"(BGR {np.round(tom).astype(int)})")
    return out


def cuba_bha(Q, out, q=BHA):
    """A cuba esculpida no granito, com a parede à direita (`biblioteca_subsolo_casab_1311.cuba_bhs` sem as sobras da
    Casa B): feita na janela girada (a parede embaixo) e girada de volta, no tom do granito da bancada em volta."""
    c = px(Q, q["cuba_pt"])
    b = px(Q, q["bacia_pt"])
    X0, Y0, X1, Y1 = int(np.floor(c[0])) - 8, int(np.floor(c[1])) - 8, int(np.ceil(c[2])) + 8, int(np.ceil(c[3])) + 8
    reg = np.ascontiguousarray(out[Y0:Y1, X0:X1])
    h = Y1 - Y0
    rot = np.ascontiguousarray(cv2.rotate(reg, cv2.ROTATE_90_CLOCKWISE))

    def r2(r):
        return (h - (r[3] - Y0), r[0] - X0, h - (r[1] - Y0), r[2] - X0)
    Qr = types.SimpleNamespace(p2q=lambda x, y: (x, y), px_m=Q.px_m)
    rot = BS.cuba_esculpida(Qr, rot, {"cuba": r2(c), "bacia": r2(b)}, q["semente"])
    novo = cv2.rotate(rot, cv2.ROTATE_90_COUNTERCLOCKWISE).astype(np.float32)
    ref = []
    for r in q["bancada_pt"]:
        a, b_, cc, d = [int(round(t)) for t in px(Q, r)]
        ref.append(out[b_ + 2:d - 2, a + 2:cc - 2].reshape(-1, 3))
    ref = np.median(np.concatenate(ref).astype(np.float32), axis=0)
    xa, ya, xb, yb = [int(round(t)) for t in c]
    jan = novo[ya - Y0:yb - Y0, xa - X0:xb - X0]
    croma = jan.max(axis=2) - jan.min(axis=2)
    cromo = (croma < q["croma_cromo"]) & (jan.mean(axis=2) > q["lum_cromo"])
    gran = ~cromo
    k = ref / np.maximum(np.median(jan[gran], axis=0), 1)
    jan[gran] = np.clip(jan[gran] * k, 0, 255)
    novo[ya - Y0:yb - Y0, xa - X0:xb - X0] = jan
    out[Y0:Y1, X0:X1] = np.clip(np.round(novo), 0, 255).astype(np.uint8)
    print(f"    BH academia: cuba esculpida da biblioteca no granito da bancada (BGR {np.round(ref).astype(int)}), "
          "a torneira cromada dela, girada para a parede da direita")
    return out


def bacia(Q, out, par, reg, v=BACIA):
    out = BB.piso_desloc(out, v["antes_px"], par, -1, 0, folga=0)
    c = px(Q, v["pt"])
    out = BS.compor(out, BB.peca_bacia(v), c, nao=par)
    reg.append({"tipo": "bacia", "png": v["png"], "giro": v["giro"], "c": list(c)})
    print(f"    {v['nome']}: {Path(v['png']).stem} branca no retângulo do vaso do PDF (a de antes vira o travertino)")
    return out


def chuveiros(out, par, reg):
    for ch in CHUVEIROS:
        x0, y0, x1, y1 = ch["placa_px"]
        L = RT.LIMPA_PX
        out = BB.piso_desloc(out, (x0 - L, y0 - L, x1 + L, y1 + L), par, ch["piso"][0], ch["piso"][1], folga=0)
        P, cx, cy, wt, ht, ang = RT.chuveiro_desenho(ch)
        o = BT.pousar(out.astype(np.float32), P, cx, cy, wt, ht, ang, B1.SOMBRAS["chuveiro"], PX_M, nao=par)
        out = np.clip(np.round(o), 0, 255).astype(np.uint8)
        reg.append({"tipo": "chuveiro_teto", "nome": ch["nome"], "placa_px": list(ch["placa_px"])})
    print(f"    BH academia: {len(CHUVEIROS)} chuveiros de teto desenhados em planta, no quadrado do PDF")
    return out


# ----------------------------------------------------------------------------------------------------------------------
def reguas_academia(Q, antes, centro):
    """As réguas do vinílico da academia (BGR float32) e o canto (x, y) delas: as do `vinilico_foto.trocar` da final (a
    mesma conta, só para pegar as réguas; a imagem que ele devolve não é usada)."""
    import um_pav_casaa_1111 as U
    import vinilico_foto as V
    pegas = []
    orig = U._reguas_amostra

    def espiao(h, w, px_m, qv, rng):
        T = orig(h, w, px_m, qv, rng)
        f = sys._getframe(1).f_locals
        pegas.append((T if f["deitado"] else np.ascontiguousarray(T.transpose(1, 0, 2)), f["x"], f["y"]))
        return T
    U._reguas_amostra = espiao
    try:
        BS.quieto(V.trocar, Q, antes, [(124, 162, 200)])
    finally:
        U._reguas_amostra = orig
    cx, cy = centro
    for T, x, y in pegas:
        if x <= cx < x + T.shape[1] and y <= cy < y + T.shape[0]:
            return T, x, y
    raise RuntimeError("as réguas da academia não foram achadas")


def academia(Q, out, antes, par, reg, q=ACADEMIA):
    import vinilico_foto as V
    H, W = out.shape[:2]
    caixas = [px(Q, p["pt"]) for p in q["pecas"]]
    centro = np.mean([[(c[0] + c[2]) / 2, (c[1] + c[3]) / 2] for c in caixas], axis=0)
    T, ox, oy = reguas_academia(Q, antes, centro)
    h, w = T.shape[:2]
    reg_ = out[oy:oy + h, ox:ox + w].astype(np.float32)
    Lr = reg_ / np.maximum(T, 1)
    sala = ndimage.binary_fill_holes(cv2.morphologyEx(V.mascara_vinilico(Q, [(124, 162, 200)]).astype(np.uint8),
                                                      cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8)) > 0)
    s_ = (sala & ~par)[oy:oy + h, ox:ox + w]
    # a. perto dos símbolos: o que foge do piso esperado (as réguas vezes a luz larga de fora deles) é aparelho ou sombra
    perto = np.zeros((H, W), bool)
    for c in caixas:
        b = q["busca_px"]
        perto[int(c[1]) - b:int(c[3]) + b + 1, int(c[0]) - b:int(c[2]) + b + 1] = True
    p_ = perto[oy:oy + h, ox:ox + w]
    num, den = BS.nconv(Lr, s_ & ~p_, 12.0)
    E = T * num / np.maximum(den, 1e-4)
    foge = (np.abs(reg_ - E).max(axis=2) > q["desvio"]) & p_ & s_
    foge = cv2.morphologyEx(foge.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8)) > 0
    k = 2 * q["folga_px"] + 1
    b = (cv2.dilate(foge.astype(np.uint8), np.ones((k, k), np.uint8)) > 0) & p_ & s_
    valido = s_ & ~b & (np.abs(reg_ - E).max(axis=2) <= q["desvio"])
    g = Lr.mean(axis=2)
    alta = float(np.median(np.abs(g - cv2.GaussianBlur(g, (0, 0), 2.0))[valido]))
    if alta > q["razao_max"]:
        raise RuntimeError(f"as réguas pegas não são as do piso (alta frequência da razão {alta:.4f})")
    L = np.zeros_like(Lr)
    falta = b.copy()
    for sig in q["luz_sigmas"]:
        num, den = BS.nconv(Lr, valido, sig)
        ok = falta & (den[..., 0] > 0.05)
        L[ok] = (num / np.maximum(den, 1e-6))[ok]
        falta &= ~ok
        if not falta.any():
            break
    reg_[b] = (T * L)[b]
    out[oy:oy + h, ox:ox + w] = np.clip(np.round(reg_), 0, 255).astype(np.uint8)
    print(f"    academia: os aparelhos de antes saem; o vinílico de volta em {int(b.sum())} px (as réguas da academia, "
          f"alta frequência da razão no piso {alta:.4f}, vezes a luz do piso em volta)")
    for p, cpdf in zip(q["pecas"], caixas):
        P, cc = BB.aparelho({"png": p["png"], "pdf_px": cpdf})
        out = BS.compor(out, P, cc, sombra=BS.ACADEMIA["sombra"], nao=par)
        reg.append({"tipo": "aparelho", "png": p["png"], "pdf_px": list(cpdf), "espelho": False, "c": list(cc)})
        print(f"    academia: {p['nome']} ({Path(p['png']).stem}) em {cc[2] - cc[0]:.1f} x {cc[3] - cc[1]:.1f} px "
              f"({(cc[2] - cc[0]) / PX_M:.2f} x {(cc[3] - cc[1]) / PX_M:.2f} m), o meio em "
              f"({(cc[0] + cc[2]) / 2:.1f}, {(cc[1] + cc[3]) / 2:.1f})")
    return out


# ----------------------------------------------------------------------------------------------------------------------
def aplicar(antes):
    Q = quadro()
    out = antes.copy()
    par = BS.quieto(FA.paredes_pdf, Q) > 0.3
    reg = []
    out = sauna(Q, out, antes, par, reg)
    out = cuba_bha(Q, out)
    out = bacia(Q, out, par, reg)
    out = chuveiros(out, par, reg)
    out = academia(Q, out, antes, par, reg)
    out = esquadrias(Q, out)
    out = rotulos(out, par)
    return out, reg


def rotulos(out, par, q=ROTULOS):
    """Cada rótulo anda na vertical até o meio da fileira: o texto sai pela conta do alfa contra o piso que entra no
    lugar dele (o piso do lado, com a costura) e volta, com o mesmo alfa e a mesma cor, sobre o piso do lugar novo."""
    for r in q:
        x0, y0, x1, y1 = r["caixa"]
        velho = out[y0:y1, x0:x1].astype(np.float32)
        out = BB.piso_desloc(out, (x0, y0, x1, y1), par, r["piso"][0], r["piso"][1], folga=0)
        fundo = out[y0:y1, x0:x1].astype(np.float32)
        lf, lv = fundo.mean(axis=2), velho.mean(axis=2)
        txt = lv < 0.72 * np.median(lf)
        cor = np.median(velho[txt & (lv <= np.percentile(lv[txt], 30))], axis=0)
        a = np.clip((lf - lv) / np.maximum(lf - float(cor.mean()), 1.0), 0, 1)
        a[a < 0.04] = 0
        d = int(round(r["meio_y"] - (y0 + y1) / 2))
        novo = out[y0 + d:y1 + d, x0:x1].astype(np.float32)
        novo = novo * (1 - a[..., None]) + cor * a[..., None]
        out[y0 + d:y1 + d, x0:x1] = np.clip(np.round(novo), 0, 255).astype(np.uint8)
        print(f"    rótulos: {r['nome']} com o meio em y {r['meio_y']:.0f} ({d:+d} px), na fileira")
    return out


def esquadrias(Q, out, min_px=10.0):
    """O contorno preto das esquadrias (`regras_terreo_casab_1311.esquadrias`), sem os batentes: os traços com menos de
    `min_px` no lado maior (as pecinhas do marco nas pontas das paredes) ficam como estão."""
    ch0, tr0 = RT.CHUVEIROS_TB, RT._tracos_esquadrias

    def tracos(Q, q=RT.ESQUADRIAS_TB):
        for cs in tr0(Q, q):
            pts = np.concatenate([np.asarray(c) for c in cs])
            if (pts.max(0) - pts.min(0)).max() >= min_px:
                yield cs
    RT.CHUVEIROS_TB, RT._tracos_esquadrias = CHUVEIROS, tracos
    try:
        return RT.esquadrias(Q, out)
    finally:
        RT.CHUVEIROS_TB, RT._tracos_esquadrias = ch0, tr0


def antes_depois(antes, depois):
    for nome, (x0, y0, x1, y1) in ANTES_DEPOIS.items():
        a, b = antes[y0:y1, x0:x1], depois[y0:y1, x0:x1]
        k = min(6.0, 900 / max(a.shape[:2]))
        a = cv2.resize(a, None, fx=k, fy=k, interpolation=cv2.INTER_LANCZOS4)
        b = cv2.resize(b, None, fx=k, fy=k, interpolation=cv2.INTER_LANCZOS4)
        junto = np.hstack([a, np.full((a.shape[0], 16, 3), 255, np.uint8), b])
        topo = np.full((44, junto.shape[1], 3), 255, np.uint8)
        cv2.putText(topo, "ANTES | DEPOIS", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (40, 40, 40), 2, cv2.LINE_AA)
        arq = R / f"POE642_CasaC_PH_Subsolo_1311_{nome}_antes_depois.jpg"
        cv2.imwrite(str(arq), np.vstack([topo, junto]), [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"    antes e depois: {', '.join(ANTES_DEPOIS)}")


def final_de(commit):
    dado = subprocess.run(["git", "show", f"{commit}:{FINAL.relative_to(RAIZ_GIT).as_posix()}"], cwd=RAIZ_GIT,
                          capture_output=True, check=True).stdout
    return cv2.imdecode(np.frombuffer(dado, np.uint8), cv2.IMREAD_COLOR)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--antes")
    ap.add_argument("--saida")
    a = ap.parse_args()
    antes = cv2.imread(a.antes) if a.antes else final_de(ANTES_COMMIT)
    depois, reg = aplicar(antes)
    if a.saida:
        cv2.imwrite(a.saida, depois)
        print(f"    {a.saida}")
        return
    cv2.imwrite(str(FINAL), depois)
    print(f"    {FINAL.name}: {len(reg)} peças")
    antes_depois(antes, depois)


if __name__ == "__main__":
    main()

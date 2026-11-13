"""Os materiais do Térreo da Casa B no Térreo da Casa C (13/11).

Usuário, vendo o teste das trocas: "ALGUMAS ALTERAÇÕES NA CASA C FORAM BEM VINDAS", "O DECK É UMA DELAS", e, perguntado,
todas: o deck, o granito (cozinha, serviço, quarto e BH externos, garagem), o gramado, o travertino e o vinílico. As duas
casas têm a mesma legenda de materiais, mas a IA de cada uma os desenhou de um jeito (no Térreo da Casa C o granito saiu
escuro e pontilhado, o gramado verde-vivo, o deck claro e rosado). Aqui cada piso do Térreo da Casa C ganha a textura do
mesmo material na final do Térreo da Casa B (`FONTES`: uma amostra limpa de cada), vezes a luz do piso da Casa C (a média
local da luminância só do piso, `sigma_px`, sobre a mediana dele): as sombras dos móveis, a luz das janelas e os cantos
ficam; o desenho e a cor passam a ser os da Casa B.
- **Onde:** as regiões da legenda no PDF (ARQ_CONTRAPISO: o oliva #BAB596 é o travertino, o malva #BFA79F o granito, o
  laranja #CC9966 o vinílico, o polígono do deck); o gramado, no lote, pela cor e pelo pouco contraste local (as árvores
  e os arbustos, de muito contraste, ficam).
- **O que fica:** no travertino e no vinílico, as peças do PDF (com 2 px de folga: os sofás creme têm a cor do
  travertino); em todas, o que foge da cor do piso (a cama, o tapete, o carro), 1 px em volta disso, e os rótulos (o
  texto escuro e o branco pouco colorido, os traços de 10 px ou mais, com 2 px; os pontinhos do granito não contam).

  python3 materiais_terreo_casac_1311.py --antes <png> [--saida <png>]
Sem --saida, grava a final e os antes e depois `POE642_CasaC/renders/POE642_CasaC_PH_Terreo_1311_materiais_<trecho>_antes_depois.jpg`.
"""

import argparse
import contextlib
import io
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import final3840_casab as F                      # noqa: E402
import final3840_casac as C                      # noqa: E402
import paisagismo_terreo_casab_1311 as PJ        # noqa: E402

CASA_C = AQUI.parents[1] / "POE642_CasaC"
R = CASA_C / "renders"
FINAL = R / "POE642_CasaC_PH_Terreo_final_rotulos.png"
FINAL_B = AQUI.parents[1] / "POE642_CasaB" / "renders" / "POE642_CasaB_PH_Terreo_final_rotulos.png"

# as amostras limpas de cada material na final do Térreo da Casa B (px)
FONTES = {"granito": (2090, 1460, 2190, 1560), "travertino": (1100, 1285, 1290, 1470), "vinilico": (1883, 546, 1963, 610),
          "deck": (700, 1420, 840, 1600), "gramado": (926, 112, 1593, 237)}
# as regiões: a cor do preenchimento do PDF (ARQ_CONTRAPISO) ou o desenho do PDF; `obj`: as peças do PDF ficam fora
REGIOES = {"granito": {"fill": (0.749, 0.655, 0.624), "obj": False},
           "travertino": {"fill": (0.729, 0.71, 0.588), "obj": True},
           "vinilico": {"fill": (0.8, 0.6, 0.4), "obj": True},
           "deck": {"desenho": 88937, "obj": False}}
CAMADAS_OBJ = ("ARQ_LAYOUT HUMANIZAÇÃO", "ARQ_BANCADAS", "ARQ_LOUÇAS E METAIS", "ARQ_ELEMENTOS FIXOS", "ARQ_MOBILIÁRIO",
               "ARQ_PAREDE", "ARQ_REVESTIMENTOS", "ARQ_PAISAGISMO", "DOC_TEXTOS", "INS_INSTALAÇÕES",
               "INS_INSTALAÇÕES HIDRÁULICAS")
# `sigma_mat`: no travertino e no vinílico a luz mais larga (com 3 px, os poros e os veios de hoje viravam manchinhas)
Q_ = {"sigma_px": 3.0, "sigma_mat": {"travertino": 8.0, "vinilico": 6.0}, "pontinho_px": 40, "croma_max": 0.10, "lum_min": 0.45, "lum_max": 1.30, "folga_obj_px": 2, "borda_px": 1,
      "texto": {"claro": 1.35, "escuro": 0.65, "croma": 40, "folga_px": 2, "lado_min": 9},
      "gramado": {"std_max": 14.0, "lum_max": 130, "g_r": 8}}
ANTES_DEPOIS = {"cozinha_servico": (2150, 250, 2560, 700), "garagem": (2540, 300, 3330, 830),
                "estar_jantar": (1600, 900, 2400, 1600), "quartos": (1150, 300, 2150, 600),
                "deck_piscina": (600, 950, 1150, 1700), "gramado": (200, 100, 1000, 900)}


def quadro():
    with contextlib.redirect_stdout(io.StringIO()):
        C.contexto_c()
        return F.Quadro("Terreo")


def mascaras(Q, H, W, q=Q_):
    m = {}
    for nome, r in REGIOES.items():
        if "fill" in r:
            alvo = np.float32(r["fill"])
            mm = Q.preencher(lambda d: d.get("layer") == "ARQ_CONTRAPISO" and d.get("fill") is not None and
                             np.abs(np.float32(d["fill"]) - alvo).max() < 0.01, ss=2) > 0.5
        else:
            alvo = Q.desenhos[r["desenho"]]
            mm = Q.preencher(lambda d: d is alvo, ss=2) > 0.5
        m[nome] = mm
    obj = Q.preencher(lambda d: d.get("layer") in CAMADAS_OBJ and d.get("type") in ("f", "fs"), ss=2) > 0.3
    k = 2 * q["folga_obj_px"] + 1
    obj = cv2.dilate(obj.astype(np.uint8), np.ones((k, k), np.uint8)) > 0
    return m, obj


def textos(img, regiao, q=Q_):
    """Os rótulos dentro da região: o que se afasta muito da luz do piso (o branco no piso escuro, o escuro no claro),
    pouco colorido, juntado por 1 px; ficam as manchas com um lado de `lado_min` px ou mais (as letras, as palavras); os
    pontinhos do granito, menores, não contam."""
    I = img.astype(np.int16)
    lum = I.mean(axis=2)
    cr = I.max(axis=2) - I.min(axis=2)
    t = q["texto"]
    med = float(np.median(lum[regiao]))
    cand = (((lum > med * t["claro"]) | (lum < med * t["escuro"])) & (cr < t["croma"]) & regiao).astype(np.uint8)
    cd = cv2.dilate(cand, np.ones((3, 3), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(cd, connectivity=8)
    lado = np.maximum(st[:, cv2.CC_STAT_WIDTH], st[:, cv2.CC_STAT_HEIGHT])
    m = np.isin(lab, np.nonzero(lado >= t["lado_min"])[0][1:]).astype(np.uint8)
    k = 2 * t["folga_px"] + 1
    return cv2.dilate(m, np.ones((k, k), np.uint8)) > 0


def piso_da_regiao(img, regiao, q=Q_):
    """Os px do piso dentro da região: a cromaticidade perto da mediana e a luz dentro da faixa; fora 1 px em volta do que
    não é piso."""
    I = img.astype(np.float32)
    lum = I.mean(axis=2)
    cr = I / np.maximum(lum, 1)[..., None]
    ys, xs = np.nonzero(regiao)
    med_cr = np.median(cr[ys, xs], axis=0)
    med_l = float(np.median(lum[ys, xs]))
    ok = (np.abs(cr - med_cr[None, None]).max(axis=2) < q["croma_max"]) & (lum > q["lum_min"] * med_l) & \
        (lum < q["lum_max"] * med_l)
    fora = (regiao & ~ok).astype(np.uint8)
    # os pontinhos do desenho de hoje (o pontilhado do granito, os poros do travertino) são piso: trocados também, mas
    # fora da conta da luz
    n, lab, st, _ = cv2.connectedComponentsWithStats(fora, connectivity=8)
    pont = np.isin(lab, np.nonzero(st[:, cv2.CC_STAT_AREA] < q["pontinho_px"])[0][1:])
    fora = (fora > 0) & ~pont
    k = 2 * q["borda_px"] + 1
    fora = cv2.dilate(fora.astype(np.uint8), np.ones((k, k), np.uint8)) > 0
    luz = regiao & ok & ~fora
    return luz | (regiao & pont & ~fora), luz


def gramado(img, q=Q_):
    I = img.astype(np.float32)
    lum = I.mean(axis=2)
    g = q["gramado"]
    m1 = cv2.blur(lum, (7, 7))
    m2 = cv2.blur(lum * lum, (7, 7))
    std = np.sqrt(np.maximum(m2 - m1 * m1, 0))
    verde = (I[..., 1] - I[..., 2] > g["g_r"]) & (I[..., 1] > I[..., 0] + 15)
    return verde & (std < g["std_max"]) & (lum < g["lum_max"])


def sem_emenda(P, H, W):
    """A amostra repetida sem emenda (para as texturas sem desenho: o travertino, o granito, o gramado): a amostra no
    meio e ela mesma deslocada de meio lado nas bordas, misturadas por um peso que cai para as bordas; depois repetida por
    translação (o espelho deixava, nas emendas, os poros refletidos em fileira)."""
    h, w = P.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    m = np.minimum(np.minimum(yy, h - 1 - yy) / (h / 2), np.minimum(xx, w - 1 - xx) / (w / 2))
    m = np.clip(m * 2.0, 0, 1)[..., None]
    rol = np.roll(np.roll(P, h // 2, axis=0), w // 2, axis=1)
    t = P * m + rol * (1 - m)
    return np.tile(t, (H // h + 1, W // w + 1, 1))[:H, :W]


def trocar(out, piso, T, sigma, alfa_sig=0.6, luz=None, anel_px=6.0):
    """O piso (`piso`, bool) com a textura `T` (H x W x 3, no tom da Casa B) vezes a luz do piso de hoje (medida em `luz`,
    sem os pontinhos)."""
    luz = piso if luz is None else luz
    ys, xs = np.nonzero(piso)
    if not len(ys):
        return out
    pad = int(4 * sigma) + 4
    Y0, Y1 = max(ys.min() - pad, 0), min(ys.max() + pad + 1, out.shape[0])
    X0, X1 = max(xs.min() - pad, 0), min(xs.max() + pad + 1, out.shape[1])
    sub = out[Y0:Y1, X0:X1].astype(np.float32)
    m = piso[Y0:Y1, X0:X1].astype(np.float32)
    ml = luz[Y0:Y1, X0:X1].astype(np.float32)
    lum = sub.mean(axis=2)
    num = cv2.GaussianBlur(lum * ml, (0, 0), sigma)
    den = cv2.GaussianBlur(ml, (0, 0), sigma)
    L = num / np.maximum(den, 1e-4)
    med = float(np.median(lum[ml > 0]))
    r = np.clip(L / max(med, 1), 0.3, 1.6)
    novo = T[Y0:Y1, X0:X1] * r[..., None]
    a = (np.clip(cv2.GaussianBlur(m, (0, 0), alfa_sig), 0, 1) * m)[..., None]
    res = sub * (1 - a) + novo * a
    # em volta do que ficou (os rótulos, as bordas das peças, o carro), a diferença de tom entre o piso novo e o de antes
    # (a média local), somada aos px que ficaram, caindo até `anel_px`: sem o contorno do piso antigo
    sg = 2.0 * sigma
    den2 = cv2.GaussianBlur(m, (0, 0), sg)[..., None]
    dif = (cv2.GaussianBlur(novo * m[..., None], (0, 0), sg) - cv2.GaussianBlur(sub * m[..., None], (0, 0), sg)) / \
        np.maximum(den2, 1e-4)
    dist = cv2.distanceTransform((m < 0.5).astype(np.uint8), cv2.DIST_L2, 3)
    w = np.clip(1 - dist / anel_px, 0, 1) * (m < 0.5) * np.clip(den2[..., 0] / 0.15, 0, 1)
    res = res + dif * w[..., None]
    out[Y0:Y1, X0:X1] = np.clip(np.round(res), 0, 255).astype(np.uint8)
    return out


def aplicar(antes, q=Q_):
    Q = quadro()
    H, W = antes.shape[:2]
    B = cv2.imread(str(FINAL_B))
    regs, obj = mascaras(Q, H, W)
    out = antes.copy()
    for nome in ("granito", "travertino", "vinilico", "deck"):
        reg = regs[nome] & ~textos(antes, regs[nome])
        if REGIOES[nome]["obj"]:
            reg &= ~obj
        piso, luz = piso_da_regiao(antes, reg)
        x0, y0, x1, y1 = FONTES[nome]
        P = B[y0:y1, x0:x1].astype(np.float32)
        T = PJ.textura(P, H, W) if nome in ("vinilico", "deck") else sem_emenda(P, H, W)
        out = trocar(out, piso, T, q["sigma_mat"].get(nome, q["sigma_px"]), luz=luz)
        print(f"    {nome}: {int(piso.sum())} px com a textura da Casa B (a luz e as sombras do piso de hoje)")
    gr = gramado(antes) & ~obj
    for mm in regs.values():
        gr &= ~mm
    x0, y0, x1, y1 = FONTES["gramado"]
    T = sem_emenda(B[y0:y1, x0:x1].astype(np.float32), H, W)
    out = trocar(out, gr, T, 4.0)
    print(f"    gramado: {int(gr.sum())} px com o gramado da Casa B (as árvores e os arbustos ficam)")
    return out


def antes_depois(antes, depois):
    for nome, (x0, y0, x1, y1) in ANTES_DEPOIS.items():
        a, b = antes[y0:y1, x0:x1], depois[y0:y1, x0:x1]
        k = min(2.0, 1100 / max(a.shape[1], 1), 800 / max(a.shape[0], 1))
        a = cv2.resize(a, None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
        b = cv2.resize(b, None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
        lado = a.shape[1] <= a.shape[0] * 1.3
        junto = np.hstack([a, np.full((a.shape[0], 16, 3), 255, np.uint8), b]) if lado else \
            np.vstack([a, np.full((16, a.shape[1], 3), 255, np.uint8), b])
        topo = np.full((44, junto.shape[1], 3), 255, np.uint8)
        cv2.putText(topo, "ANTES | DEPOIS (materiais da Casa B)" if lado else "ANTES (em cima) | DEPOIS (embaixo)",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (40, 40, 40), 2, cv2.LINE_AA)
        cv2.imwrite(str(R / f"POE642_CasaC_PH_Terreo_1311_materiais_{nome}_antes_depois.jpg"), np.vstack([topo, junto]),
                    [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"    antes e depois: {', '.join(ANTES_DEPOIS)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--antes", required=True)
    ap.add_argument("--saida")
    a = ap.parse_args()
    antes = cv2.imread(a.antes)
    depois = aplicar(antes)
    if a.saida:
        cv2.imwrite(a.saida, depois)
        print(f"    {a.saida}")
        return
    cv2.imwrite(str(FINAL), depois)
    print(f"    {FINAL.name}")
    antes_depois(antes, depois)


if __name__ == "__main__":
    main()

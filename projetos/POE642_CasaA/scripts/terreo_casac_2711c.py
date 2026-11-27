"""Casa C Térreo, 27/11 (3): a revisão completa do 12K e as mantas de volta caindo pelo piso.

- **Mantas** (o usuário: "as mantas devem cobrir a cama e 'cair' pelo piso, de forma 'jogada'"): o corte de
  `terreo_casac_2711` (a manta terminando dentro da cama) sai, e nas três camas (suíte master, quarto 3 e quarto 1) entra
  a manta de tricô grosso nova, gerada no Higgsfield em 4K
  (`../biblioteca-objetos/03-primeiro-pavimento/mantas/manta-trico-jogada.png`, sem fundo): jogada
  sobre os pés da cama, de lado a lado, e caindo pela beirada sobre o tapete, com a dobra na beira do colchão, a parte
  caída mais escura (vertical, fora da luz) e a sombra dela no piso.
- **Sala TV, tapete**: a faixa da direita do tapete (de 1533 a 1551, onde ficava a poltrona) estava num tecido mais
  claro e liso, com um fio claro junto da borda; agora é o mesmo tecido do tapete (quilting do próprio tapete), no tom do
  tapete ao lado. As pintinhas verdes logo acima da borda de cima do tapete saem (o travertino de novo).
- **Sala TV, vaso**: o disco claro do remendo antigo em volta do vaso (e as listras junto do canto do tapete e do braço
  do sofá) sai: o travertino de novo, com a luz do piso de cima, menos o vaso e as folhas, que ganham a sombra curta.

Final, prancha e 12K A e B (pelo registro local).

  python3 terreo_casac_2711c.py [itens]
"""
import json
import os
import subprocess
import sys
from io import BytesIO
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
sys.path.insert(0, str(Path(__file__).resolve().parent))
import esquadrias_pretas_1911 as EP              # noqa: E402
import vetor_2511 as V                           # noqa: E402
import terreo_casaa_2511d as D                   # noqa: E402
import terreo_casaa_2511g as G                   # noqa: E402
import um_pav_casaa_2511d as DD                  # noqa: E402

PLANTA = "C_Terreo"
DZ = json.loads((EP.PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[PLANTA]
ANTES_DO_CORTE = "a93c155"           # o commit de antes de terreo_casac_2711 (as mantas ainda caindo da cama)

# os retângulos do corte das mantas (terreo_casac_2711.MANTAS, com a sombra do corte e 1,5 px de folga)
CORTE = {"suite_master": (937.0, 661.0, 953.8, 711.4), "quarto3": (1313.0, 478.5, 1362.0, 492.5),
         "quarto1": (2028.5, 391.0, 2081.0, 408.5)}

TAPETE_DIR = dict(zona=(1528.0, 710.0, 1551.4, 887.9), fonte=(1502.0, 712.0, 1528.0, 828.0),
                  ref=(1519.0, 711.0, 1527.0, 846.0), sig=6.0, pena=4.0,
                  x_braco=1532.6, y_braco=848.0)
TOPO = ((1316.0, 700.3, 1558.0, 706.6), "lrt")
VASO = dict(zona=[(1245.5, 836.0), (1315.2, 836.0), (1315.2, 891.6), (1321.3, 891.6), (1321.3, 912.4),
                  (1245.5, 912.4)],
            ref=(1246.0, 812.0, 1314.0, 835.0), centro=(1276.8, 874.0), raio=23.9, folhas_raio=33.0,
            pena_topo=4.0, sombra=0.16)


# ----------------------------------------------------------------------------------------------------------------------
def _git_img(rel, commit=ANTES_DO_CORTE):
    dados = subprocess.run(["git", "show", f"{commit}:projetos/{rel}"], cwd=EP.PROJ, capture_output=True,
                           check=True).stdout
    return cv2.cvtColor(np.array(Image.open(BytesIO(dados)).convert("RGB")), cv2.COLOR_RGB2BGR)


def restaurar(img, antigo, s, origem, q=CORTE):
    """As mantas como antes do corte: os pixels do commit de antes nos retângulos do corte (a mesma grade de pixels)."""
    for r in q.values():
        X0, Y0, X1, Y1 = V.janela(img, r, s, origem, folga=0)
        img[Y0:Y1, X0:X1] = antigo[Y0:Y1, X0:X1]
    return img


# ----------------------------------------------------------------------------------------------------------------------
# A manta nova (Higgsfield 4K, sem fundo): por cama, o retângulo da cama (o colchão), a caixa da manta velha, a beira por
# onde a nova cai (eixo, coordenada, sentido para fora), o centro, o comprimento da faixa, o giro (graus, anti-horário na
# tela) e as amostras do edredom e do tapete (para o que sobra da velha fora da nova)
MANTA_PNG = EP.PROJ / "POE642_CasaA/biblioteca-objetos/03-primeiro-pavimento/mantas/manta-trico-jogada.png"
CAMAS = {
    "suite_master": dict(cama=(948.6, 588.0, 1061.5, 709.6), velha=(933.0, 655.0, 1063.0, 714.0),
                         beira=("x", 948.6, -1), centro=(997.0, 682.5), comp=122.0, giro=0.0,
                         edredom=(958.0, 628.0, 1045.0, 656.0), tapete=(905.0, 640.0, 935.0, 740.0)),
    "quarto3": dict(cama=(1315.3, 382.5, 1400.0, 482.7), velha=(1313.0, 383.0, 1361.0, 493.0),
                    beira=("y", 482.7, 1), centro=(1341.0, 441.0), comp=114.0, giro=90.0,
                    edredom=(1365.0, 395.0, 1395.0, 470.0), tapete=(1330.0, 486.0, 1395.0, 500.0)),
    "quarto1": dict(cama=(2030.0, 404.0, 2160.0, 522.0), velha=(2028.0, 395.0, 2082.0, 515.0),
                    beira=("y", 404.0, -1), centro=(2059.0, 453.5), comp=129.0, giro=-90.0,
                    edredom=(2085.0, 415.0, 2120.0, 505.0), tapete=(2040.0, 381.0, 2110.0, 400.0),
                    rb_min=45, l_max=182),
}
CAI = dict(escurece=0.22, cai_px=4.0, crista=0.05, sombra=0.38, sombra_d=(-1.0, 1.3), sombra_sig=1.6,
           contato=0.15, contato_d=(-0.5, 0.6), contato_sig=0.7, tom=1.0, sig_tom=4.0)
_ASSET = {}


def _asset():
    if "P" not in _ASSET:
        P = cv2.imread(str(MANTA_PNG), cv2.IMREAD_UNCHANGED).astype(np.float32)
        ys, xs = np.nonzero(P[..., 3] > 8)
        _ASSET["P"] = P[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return _ASSET["P"]


def _pousar_manta(jan, s, origem, q):
    """A manta na janela: (cor pré-multiplicada, alfa), girada e na escala da planta."""
    X0, Y0, X1, Y1 = jan
    P = _asset()
    h, w = P.shape[:2]
    k = q["comp"] * s / w                                       # px da janela por px do PNG
    tw, th = max(2, int(round(w * k))), max(2, int(round(h * k)))
    r = cv2.resize(P, (tw, th), interpolation=cv2.INTER_AREA)
    r[..., :3] *= r[..., 3:4] / 255
    cx = (q["centro"][0] - origem[0]) * s - X0
    cy = (q["centro"][1] - origem[1]) * s - Y0
    M = cv2.getRotationMatrix2D((tw / 2, th / 2), q["giro"], 1.0)
    M[0, 2] += cx - tw / 2
    M[1, 2] += cy - th / 2
    can = cv2.warpAffine(r, M, (X1 - X0, Y1 - Y0), flags=cv2.INTER_LINEAR, borderValue=0)
    return can[..., :3], np.clip(can[..., 3] / 255, 0, 1)


def _velha(reg, xs, ys, q):
    """A manta velha (o tricô bege, mais saturado e mais escuro que o edredom e o tapete) e a sombra dela no tapete."""
    X, Y = np.meshgrid(xs, ys)
    v = q["velha"]
    caixa = (X >= v[0]) & (X <= v[2]) & (Y >= v[1]) & (Y <= v[3])
    I = reg.astype(np.float32)
    L = I.mean(2)
    rb = I[..., 2] - I[..., 0]
    c = q["cama"]
    na_cama = (X >= c[0]) & (X <= c[2]) & (Y >= c[1]) & (Y <= c[3])
    tricô = (rb > q.get("rb_min", 28)) & (L < q.get("l_max", 232))
    sombra = ~na_cama & (L < q.get("l_tapete", 205) - 9)
    escuro = na_cama & (L < q["l_edredom"] - 30)               # as dobras escuras da manta velha, sobre a cama
    m = (caixa & (tricô | sombra | escuro)).astype(np.uint8)
    return m, na_cama


def _completar(reg, jan, s, origem, m, classe, fonte, img, semente):
    """Os px de m (uma classe: a cama ou o tapete) no tecido da amostra (quilting), no tom local de fora de m."""
    H, W = reg.shape[:2]
    TT = G._quilt(img, s, origem, fonte, H, W, semente=semente)
    sg = CAI["sig_tom"] * s
    TT = TT / np.maximum(cv2.GaussianBlur(TT, (0, 0), sg), 1.0)
    # o tom de referência só nos px do mesmo material (perto da cor da amostra): sem o banco, os criados, as almofadas
    am = V.cob([V.ret(*fonte)], jan, s, origem) > 0.99
    med = np.median(reg[am], axis=0) if am.any() else np.median(reg[classe], axis=0)
    igual = np.abs(reg - med[None, None]).max(2) < 26
    ok = (classe & ~(m > 0) & igual).astype(np.float32)
    w = cv2.GaussianBlur(ok, (0, 0), sg)
    alvo = cv2.GaussianBlur(reg * ok[..., None], (0, 0), sg) / np.maximum(w, 1e-4)[..., None]
    f = np.clip(w / 0.08, 0, 1)[..., None]                       # longe da referência: a cor da amostra
    alvo = alvo * f + med[None, None] * (1 - f)
    a = cv2.GaussianBlur((m > 0).astype(np.float32) * classe, (0, 0), 0.4 * s)
    return reg * (1 - a[..., None]) + TT * alvo * a[..., None]


def manta(img, s, origem, nome):
    q = dict(CAMAS[nome])
    xs_ = [q["velha"][0], q["velha"][2], q["centro"][0] - q["comp"] / 2 - 25, q["centro"][0] + q["comp"] / 2 + 25]
    ys_ = [q["velha"][1], q["velha"][3], q["centro"][1] - q["comp"] / 2 - 25, q["centro"][1] + q["comp"] / 2 + 25]
    jan = V.janela(img, (min(xs_), min(ys_), max(xs_), max(ys_)), s, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    xs, ys = V.coords(jan, s, origem)
    X, Y = np.meshgrid(xs, ys)
    cor, a = _pousar_manta(jan, s, origem, q)
    # a manta velha que a nova não cobre: o edredom (na cama) e o tapete (fora)
    am = V.cob([V.ret(*q["edredom"])], jan, s, origem) > 0.99
    q["l_edredom"] = float(np.median(reg[am].mean(1)))
    m, na_cama = _velha(reg, xs, ys, q)
    m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * int(1.2 * s) + 1,) * 2))
    m = m * (a < 0.98)
    reg = _completar(reg, jan, s, origem, m, na_cama, q["edredom"], img, 31)
    reg = _completar(reg, jan, s, origem, m, ~na_cama, q["tapete"], img, 32)
    # a parte que cai: além da beira (t > 0, para fora), mais escura; a dobra clara na beira
    eixo, e, sen = q["beira"]
    t = ((X if eixo == "x" else Y) - e) * sen
    cai = np.clip(t / CAI["cai_px"], 0, 1)
    cai = cai * cai * (3 - 2 * cai)
    ganho = CAI["tom"] * (1 - CAI["escurece"] * cai + CAI["crista"] * np.exp(-((t + 0.8) / 0.6) ** 2))
    cor = cor * ganho[..., None]
    H, W = a.shape
    # a sombra de contato (sobre a cama e o tapete) e a sombra da parte caída no piso (só fora da cama)
    dx, dy = CAI["contato_d"]
    Mc = np.float32([[1, 0, dx * s], [0, 1, dy * s]])
    sc = cv2.GaussianBlur(cv2.warpAffine(a, Mc, (W, H)), (0, 0), CAI["contato_sig"] * s)
    dx, dy = CAI["sombra_d"]
    Ms = np.float32([[1, 0, dx * s], [0, 1, dy * s]])
    sp = cv2.GaussianBlur(cv2.warpAffine(a * (t > -0.5), Ms, (W, H)), (0, 0), CAI["sombra_sig"] * s) * (t > 0)
    reg = reg * (1 - CAI["contato"] * sc - CAI["sombra"] * sp)[..., None]
    reg = reg * (1 - a[..., None]) + cor
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return img


# ----------------------------------------------------------------------------------------------------------------------
def tapete_tv(img, s, origem, q=TAPETE_DIR):
    """A faixa da direita do tapete no tecido do próprio tapete (quilting), no tom do tapete logo à esquerda, linha a
    linha (abaixo da mesinha e do braço do sofá, o tom da última linha medida); as bordas do tapete ficam."""
    z = q["zona"]
    jan = V.janela(img, (z[0] - 4, z[1] - 4, z[2] + 4, z[3] + 4), s, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    H, W = reg.shape[:2]
    TT = G._quilt(img, s, origem, q["fonte"], H, W, semente=27)
    sg = q["sig"] * s
    TT = TT / np.maximum(cv2.GaussianBlur(TT, (0, 0), sg), 1.0)            # só o desenho do tecido (média 1)
    xs, ys = V.coords(jan, s, origem)
    r0 = q["ref"]
    cols = (xs >= r0[0]) & (xs <= r0[2])
    lin = (ys >= r0[1]) & (ys <= r0[3])
    tom = np.median(reg[:, cols], axis=1)                                   # o tom de cada linha, à esquerda
    k = np.flatnonzero(lin)
    tom[:k[0]] = tom[k[0]]
    tom[k[-1] + 1:] = tom[k[-1]]
    tom = cv2.GaussianBlur(tom[:, None, :].astype(np.float32), (0, 0), sigmaX=0.1, sigmaY=sg)[:, 0, :]
    novo = TT * tom[:, None, :]
    # ao lado do braço do sofá (abaixo de y_braco), a faixa começa depois do braço
    zb = (q["x_braco"], q["y_braco"], z[2], z[3])
    a = np.maximum(G._pena(jan, s, origem, (z[0], z[1], z[2], q["y_braco"]), "l", q["pena"]),
                   G._pena(jan, s, origem, zb, "l", 2.0))
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg * (1 - a[..., None]) + novo * a[..., None]), 0, 255).astype(np.uint8)
    return img


def topo_tv(img, s, origem, q=TOPO):
    return G.refazer(img, s, origem, [q], textura="trav", tol=0.06, luz_sig=10.0, pena=2.0)


def vaso_tv(img, s, origem, q=VASO):
    """O travertino de novo em volta do vaso (sem o disco do remendo), a luz do piso de cima; o vaso (o círculo) e as
    folhas (o verde) ficam, com a sombra curta deles."""
    xs_ = [p[0] for p in q["zona"]]
    ys_ = [p[1] for p in q["zona"]]
    r0 = q["ref"]
    jan = V.janela(img, (min(xs_), min(min(ys_), r0[1]), max(xs_), max(ys_)), s, origem, folga=int(4 * s) + 2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    H, W = reg.shape[:2]
    az = V.cob([q["zona"]], jan, s, origem)
    xs, ys = V.coords(jan, s, origem)
    X, Y = np.meshgrid(xs, ys)
    d = np.hypot(X - q["centro"][0], Y - q["centro"][1])
    I = reg.astype(np.int16)
    b, g, r = I[..., 0], I[..., 1], I[..., 2]
    verde = (g > r + 8) & (g > b + 4) & (d < q["folhas_raio"])
    escuro = (reg.mean(2) < 110) & (d < q["folhas_raio"])
    obj = ((d < q["raio"]) | verde | escuro).astype(np.uint8)
    k = 2 * int(np.ceil(0.5 * s)) + 1
    obj = cv2.morphologyEx(obj, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8))
    obj = cv2.dilate(obj, np.ones((3, 3), np.uint8)).astype(np.float32)
    ao = cv2.GaussianBlur(obj, (0, 0), 0.35 * s)
    TT = D.piso_tt(jan, s)
    ra = reg.mean(2) / np.maximum(TT.mean(2), 1.0)
    livre = V.cob([V.ret(*r0)], jan, s, origem) > 0.99
    h, e = np.histogram(ra[livre], bins=80, range=(0.6, 1.4))
    h = np.convolve(h, np.ones(5) / 5, mode="same")
    luz = float(e[np.argmax(h)] + (e[1] - e[0]) / 2)
    novo = TT * luz
    Ms = np.float32([[1, 0, -0.9 * s], [0, 1, 1.1 * s]])
    sb = cv2.GaussianBlur(cv2.warpAffine(obj, Ms, (W, H)), (0, 0), 1.6 * s) * (1 - ao)
    novo *= (1 - q["sombra"] * sb)[..., None]
    # a emenda suave só em cima (o piso de cima); nas paredes, no tapete e no braço do sofá, o corte é seco
    fy = np.clip((ys - min(ys_)) / q["pena_topo"], 0, 1)
    a = az * fy[:, None] * (1 - ao)
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg * (1 - a[..., None]) + novo * a[..., None]), 0, 255).astype(np.uint8)
    return img


FUNC = {"tapete_tv": tapete_tv, "topo_tv": topo_tv, "vaso_tv": vaso_tv}
FUNC.update({f"manta_{k}": (lambda img, s, o, k=k: manta(img, s, o, k)) for k in CAMAS})
ITENS = {"tapete_tv": (1480.0, 700.0, 1570.0, 900.0), "topo_tv": (1300.0, 690.0, 1570.0, 720.0),
         "vaso_tv": (1235.0, 805.0, 1335.0, 925.0), "manta_suite_master": (880.0, 560.0, 1110.0, 760.0),
         "manta_quarto3": (1280.0, 360.0, 1460.0, 520.0), "manta_quarto1": (1990.0, 360.0, 2180.0, 540.0)}


def item(img, nome, escala=1.0, origem=(0.0, 0.0)):
    return FUNC[nome](img, escala, origem)


def main(so=None):
    c, pav = PLANTA.split("_")
    base = cv2.imread(str(EP.PROJ / EP.PLANTAS[PLANTA][0]))
    nomes = [n for n in ITENS if not so or n in so]
    mantas = not so or "mantas" in so
    for f in EP.PLANTAS[PLANTA]:
        im = cv2.imread(str(EP.PROJ / f))
        if mantas:
            im = restaurar(im, _git_img(f), 1.0, (0.0, 0.0))
        for nome in nomes:
            im = item(im, nome)
        cv2.imwrite(str(EP.PROJ / f), im)
        if f == EP.PLANTAS[PLANTA][0]:
            novo = im
    pf = EP.PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_entrega.png"
    pr = cv2.imread(str(pf))
    pr[:2160] = novo
    cv2.imwrite(str(pf), pr)
    for op in os.environ.get("OPCOES", "AB"):
        rel = f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_12K_opcao_{op}.jpg"
        pil = Image.open(EP.PROJ / rel)
        dpi = pil.info.get("dpi", (743, 743))
        im = cv2.cvtColor(np.array(pil.convert("RGB")), cv2.COLOR_RGB2BGR)
        del pil
        cinza = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        if mantas:
            antigo = _git_img(rel)
            for k, r in CORTE.items():
                sx, org, cc = DD._registro(base, cinza, DZ, (r[0] - 60, r[1] - 60, r[2] + 60, r[3] + 60))
                im = restaurar(im, antigo, sx, org, {k: r})
                print(f"   {op}: corte {k} desfeito (registro {cc:.3f})")
            del antigo
        for nome in nomes:
            sx, org, cc = DD._registro(base, cinza, DZ, ITENS[nome])
            im = item(im, nome, sx, org)
            print(f"   {op}: {nome} (registro {cc:.3f}, escala {sx:.3f})")
        Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).save(EP.PROJ / rel, quality=95, subsampling=0, dpi=dpi)
        del im, cinza


if __name__ == "__main__":
    main(sys.argv[1:] or None)

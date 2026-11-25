"""Casa A Térreo, 6ª leva de 25/11: a escada helicoidal na opção 1 e o lavabo (o rótulo e a bancada).

- **Escada helicoidal** ("vamos com a opção 1, mas os degraus do pavimento superior devem ter o tom dos degraus mas na
  transparência"; as opções em `proposta_caracol_terreo_casaa_2511.py`): os degraus deste nível (o arranque e os
  degraus 1 a 7, de 4,1° a 146,9°, subindo no sentido anti-horário) cheios, com o bocel fino e a sombra curta do degrau
  de cima; a linha de quebra no corte; os de cima (8 a 21) no tom dos degraus em transparência (a pedra a meia
  opacidade sobre o piso da garagem, que aparece por baixo), com os tracejados. A seta ("preciso da seta apontando a
  subida da escada sem a linha indicativa"): o triângulo cheio sobre os primeiros degraus, girado no sentido da subida
  (anti-horário), acima do S, sem a linha de caminhamento. O piso da garagem refeito sob a escada (image quilting do
  trecho à esquerda); o ▶ antigo (apontava para fora) sai; o S de cada imagem (Inter na final e no 12K A, Kalam no
  12K B) fica no mesmo lugar.
- **Lavabo** ("movimente o rótulo para esquerda e corrija a bancada"): a faixa escura à esquerda da bancada voltava
  pela máscara do rótulo (o `letras` a lia como letra); o piso refeito de novo da parede à bancada, sem as letras, a
  peça da cuba redesenhada por cima (`terreo_casaa_2511e.peca_cuba`), e o rótulo (as próprias letras de cada imagem)
  de volta, mais à esquerda: ele ocupava quase todo o vão (55 de 58,6 px da final), então vai a 95%, a 1,6 px da
  parede, com a folga maior do lado da bancada (antes encostava nela); a mancha escura junto à parede, na altura do
  "A:", sai com o piso.

- **Lavabo, batentes** ("remova os batentes"): a soleira bege de parede a parede no lugar dos dois batentes.

Final, prancha e 12K A e B. Cada item roda uma vez sobre a imagem (o rótulo do lavabo não deve ser rodado de novo: ele
reduz o rótulo a 95% de novo):

  python3 terreo_casaa_2511f.py [item ...]
"""
import json
import os
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
sys.path.insert(0, str(Path(__file__).resolve().parent))
import esquadrias_pretas_1911 as EP          # noqa: E402
import vetor_2511 as V                       # noqa: E402
import terreo_casaa_2511d as D               # noqa: E402
import terreo_casaa_2511e as E               # noqa: E402
import proposta_caracol_terreo_casaa_2511 as PC   # noqa: E402

PLANTA = "A_Terreo"

# ----------------------------------------------------------------------------------------------------------------------
HELICOIDAL = dict(janela=(1915.0, 1508.0, 2040.0, 1634.0), fundo_max_y=1628.0, cima_opac=0.58,
                  s_caixa=(1998.0, 1572.6, 2017.5, 1587.0),
                  seta_ang=10.0, seta_ponta=8.0, seta_r=33.0, seta_comp=9.0, seta_larg=8.0, seta_cor=(30.0, 30.0, 30.0))


def _piso_garagem(img, escala, origem, jan):
    """O piso da garagem (image quilting do trecho à esquerda da escada, sem o degradê) do tamanho da janela."""
    sys.path.insert(0, str(EP.PROJ / "_texturas"))
    import texturas
    X0, Y0, X1, Y1 = V.janela(img, PC.PISO_FONTE, escala, origem, folga=0)
    F = img[Y0:Y1, X0:X1]
    lisa = cv2.GaussianBlur(F.astype(np.float32), (0, 0), 6.0 * escala)
    Fd = np.clip(F.astype(np.float32) / np.maximum(lisa, 1) * F.reshape(-1, 3).mean(0), 0, 255).astype(np.uint8)
    p = max(6, int(round(8 * escala)))
    H, W = jan[3] - jan[1], jan[2] - jan[0]
    return texturas.quilting([Fd, np.ascontiguousarray(Fd[:, ::-1]), np.ascontiguousarray(Fd[::-1])], H, W, p=p,
                             sobra=max(3, p // 3), rng=np.random.default_rng(5))[:H, :W].astype(np.float32)


def helicoidal(img, escala, origem, q=HELICOIDAL):
    s = escala
    jan = V.janela(img, q["janela"], s, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    reg0 = img[Y0:Y1, X0:X1].astype(np.float32)
    # o S de hoje (as letras da própria imagem), para voltar por cima
    xs, ys = V.coords(jan, s, origem)
    sx0, sy0, sx1, sy1 = q["s_caixa"]
    zona = ((xs[None, :] >= sx0) & (xs[None, :] <= sx1) & (ys[:, None] >= sy0) & (ys[:, None] <= sy1))
    a_s, cor_s = V.letras(reg0, zona, dif=70.0, escala=s, area_min=2.0)
    n, lab, st, _ = cv2.connectedComponentsWithStats((a_s > 0.3).astype(np.uint8), 8)
    if n > 2:                                       # só o S (os tracinhos do tracejado antigo ficam de fora)
        maior = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
        a_s = a_s * cv2.dilate((lab == maior).astype(np.uint8), np.ones((3, 3), np.uint8))
    T = PC.Tela(reg0.shape[:2], s, origem, X0, Y0)
    T.X0, T.Y0, T.org = X0, Y0, origem
    G = PC.G
    piso = _piso_garagem(img, s, origem, jan)
    TT = D.piso_tt(jan, s, giro=True)
    # o piso sob a escada inteira (sem passar na esquadria de baixo)
    reg = reg0.copy()
    dentro = T.reduz((T.r <= G["R"] + 2.8) & (T.y <= q["fundo_max_y"]))
    reg = reg * (1 - dentro[..., None]) + piso * dentro[..., None]
    k = PC.degraus_vis(T)
    tom = TT / np.maximum(TT.reshape(-1, 3).mean(0), 1.0)
    pedra = np.float32(PC.COR["degrau"]) * (0.55 + 0.45 * tom)
    # os de cima: a pedra dos degraus em transparência (o piso aparece por baixo), os tracejados
    up = T.reduz(PC.cima(T))
    reg = reg * (1 - q["cima_opac"] * up[..., None]) + pedra * (q["cima_opac"] * up)[..., None]
    tr = np.zeros(k.shape, bool)
    for i in PC.de_cima():
        tr |= PC.tracejado(T, PC.limites(i))
    tr |= PC.arco(T, G["R"], PC.limites(G["n_vis"]), G["a0"], t_on=2.2)
    reg = PC.compor(reg, T.reduz(tr) * 0.85, PC.COR["traco"])
    # os deste nível: a pedra, a sombra curta do degrau de cima, um pouco mais clara a cada degrau, o bocel
    som = np.zeros(k.shape, np.float32)
    claro = np.zeros(k.shape, np.float32)
    for i in range(G["n_vis"]):
        d = PC.dist_raio(T, PC.limites(i + 1))
        som = np.maximum(som, np.where(k == i, np.exp(-d / 1.5), 0))
        claro += np.where(k == i, 1.0 + 0.012 * i, 0)
    av = T.reduz(k >= 0)
    luz = T.reduz((1 - 0.26 * som) * (k >= 0)) / np.maximum(av, 1e-3)
    claro = T.reduz(claro) / np.maximum(av, 1e-3)
    reg = reg * (1 - av[..., None]) + pedra * (luz * claro * av)[..., None]
    bocel = np.zeros(k.shape, bool)
    for i in range(1, G["n_vis"]):
        bocel |= (PC.dist_raio(T, PC.limites(i)) < 0.17) & (k >= 0)
    bocel |= ((PC.dist_raio(T, PC.limites(0)) < 0.17) & (np.abs(PC.ang_rel(T.t, PC.limites(0)) - 2) < 30)
              & (T.r <= G["R"]))
    bocel |= PC.arco(T, G["R"] - 0.15, G["a0"], PC.limites(G["n_vis"]), larg=0.36)
    reg = PC.compor(reg, T.reduz(bocel), PC.COR["linha"])
    reg = PC.compor(reg, T.reduz(PC.quebra(T, PC.limites(G["n_vis"]))), PC.COR["linha"])
    reg = PC.pilar(reg, T)
    # a seta da subida (sem a linha de caminhamento): o triângulo cheio sobre os primeiros degraus, girado no sentido
    # em que a escada sobe (anti-horário), acima do S
    tm = G["a0"] + q["seta_ang"]
    st = PC.seta_tri(T, PC.ponto(tm + q["seta_ponta"], q["seta_r"]), PC.tangente(tm), comp=q["seta_comp"],
                     larg=q["seta_larg"])
    reg = PC.compor(reg, T.reduz(st), q["seta_cor"])
    # o S de volta
    reg = V.compor(reg, a_s, cor_s)
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return img


# ----------------------------------------------------------------------------------------------------------------------
LAVABO_ROTULO = dict(piso=(2257.0, 404.0, 2316.6, 470.0), luz=(2258.0, 470.0, 2312.0, 500.0),
                     porta=(2263.4, 459.0, 2268.4, 470.5), rotulo=(2257.0, 424.0, 2315.2, 458.0),
                     parede=2257.0, bancada=2315.6, alt_max=14.0, folga_parede=1.6, escala_rot=0.95)


def lavabo_rotulo(img, escala, origem, q=LAVABO_ROTULO):
    s = escala
    # 1. as letras do rótulo (sem a faixa vertical escura: as peças altas e finas ficam de fora)
    jan = V.janela(img, q["piso"], s, origem, folga=3)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    xs, ys = V.coords(jan, s, origem)
    rx0, ry0, rx1, ry1 = q["rotulo"]
    zona = (xs[None, :] >= rx0) & (xs[None, :] <= rx1) & (ys[:, None] >= ry0) & (ys[:, None] <= ry1)
    L = reg.mean(2)
    ref = float(np.median(L[zona]))
    # o miolo das letras só no quase preto (a mancha junto à parede e a faixa da bancada são cinza); as peças altas
    # (a faixa) e as que saem da parede ficam de fora
    Lt = float(np.percentile(L[zona], 1))
    limiar = Lt + (0.25 if s > 2 else 0.5) * (ref - Lt)     # na final (1x) o traço fino da Inter é cinza
    nucleo = (L < limiar) & zona
    n, lab, st, _ = cv2.connectedComponentsWithStats(nucleo.astype(np.uint8), 8)
    tira = np.zeros(n, bool)
    parede_px = (q["parede"] + 0.8 - origem[0]) * s - X0
    tira[1:] = (st[1:, cv2.CC_STAT_HEIGHT] > q["alt_max"] * s) | (st[1:, cv2.CC_STAT_LEFT] < parede_px)
    zona_l = zona & ~cv2.dilate(tira[lab].astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    a_l, cor_l = V.letras(reg, zona_l, dif=ref - limiar, escala=s, ref=ref, area_min=0.8, piso_dif=30.0)
    ys_, xs_ = np.nonzero(a_l > 0.5)
    xe, xd = xs[xs_.min()], xs[xs_.max()]
    yc = (ys[ys_.min()] + ys[ys_.max()]) / 2
    xc = (xe + xd) / 2
    # para a esquerda: o rótulo a 95% (ele ocupava quase todo o vão), a folga pequena na parede e a maior na bancada
    k = q["escala_rot"]
    dx = (q["parede"] + q["folga_parede"]) - (xc - k * (xc - xe))
    # 2. o piso de novo, da parede à bancada (sem letras), a peça da cuba por cima
    img = D.refazer_piso(img, s, origem, [V.ret(*q["piso"])], objetos=[V.ret(*q["porta"])], sombra=0.0,
                         letras=False, luz_sig=10.0, tol=0.06, ref_luz=[V.ret(*q["piso"]), V.ret(*q["luz"])])
    img = E.peca_cuba(img, s, origem)
    # 3. o rótulo deslocado para o meio
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    cxp, cyp = (xc - origem[0]) * s - X0 - 0.5, (yc - origem[1]) * s - Y0 - 0.5
    M = np.float32([[k, 0, cxp * (1 - k) + dx * s], [0, k, cyp * (1 - k)]])
    a2 = cv2.warpAffine(a_l, M, (a_l.shape[1], a_l.shape[0]), flags=cv2.INTER_AREA if k < 1 else cv2.INTER_LINEAR)
    reg = V.compor(reg, a2, cor_l)
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    print(f"      lavabo: rótulo a {k:.0%}, deslocado {dx:+.2f} px da final; folga na bancada "
          f"{q['bancada'] - (xc + k * (xd - xc) + dx):.2f} px")
    return img


# Lavabo, os batentes ("remova os batentes"): os dois batentes da porta (as peças claras de 2,4 px de cada lado do vão)
# saem; a soleira bege vai de parede a parede (de 2263,0 a 2320,1), como nas outras portas.
LAVABO_BATENTES = dict(soleira=(2263.0, 514.5, 2320.1, 523.5))


def lavabo_batentes(img, escala, origem, q=LAVABO_BATENTES):
    return D.soleira(img, escala, origem, [q["soleira"]])


ITENS = {"helicoidal": (1905.0, 1490.0, 2050.0, 1640.0), "lavabo_rotulo": (2240.0, 395.0, 2350.0, 525.0),
         "lavabo_batentes": (2240.0, 480.0, 2350.0, 545.0)}
FUNC = {"helicoidal": helicoidal, "lavabo_rotulo": lavabo_rotulo, "lavabo_batentes": lavabo_batentes}


def item(img, nome, escala=1.0, origem=(0.0, 0.0)):
    return FUNC[nome](img, escala, origem)


def main(so=None):
    c, pav = PLANTA.split("_")
    base = cv2.imread(str(EP.PROJ / EP.PLANTAS[PLANTA][0]))
    nomes = [n for n in ITENS if not so or n in so]
    for f in EP.PLANTAS[PLANTA]:
        im = cv2.imread(str(EP.PROJ / f))
        for nome in nomes:
            im = item(im, nome)
        cv2.imwrite(str(EP.PROJ / f), im)
        if f == EP.PLANTAS[PLANTA][0]:
            novo = im
    pf = EP.PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_entrega.png"
    pr = cv2.imread(str(pf))
    pr[:2160] = novo
    cv2.imwrite(str(pf), pr)
    dz = json.loads((EP.PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[PLANTA]
    for op in os.environ.get("OPCOES", "AB"):
        rel = EP.PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_12K_opcao_{op}.jpg"
        pil = Image.open(rel)
        dpi = pil.info.get("dpi", (743, 743))
        im = cv2.cvtColor(np.array(pil.convert("RGB")), cv2.COLOR_RGB2BGR)
        del pil
        cinza = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        for nome in nomes:
            x0, y0, x1, y1 = ITENS[nome]
            mapa, cc = EP.registro_12k(base, cinza, dz, (int(x0) - 60, int(y0) - 60, int(x1) + 60, int(y1) + 60))
            A, B = mapa(x0, y0)
            sx = (mapa(x0 + 1000.0, y0)[0] - A) / 1000.0
            im = item(im, nome, sx, (x0 - A / sx, y0 - B / sx))
            print(f"   {op}: {nome} (registro {cc:.3f}, escala {sx:.3f})")
        Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).save(rel, quality=95, subsampling=0, dpi=dpi)
        del im, cinza


if __name__ == "__main__":
    main(sys.argv[1:] or None)

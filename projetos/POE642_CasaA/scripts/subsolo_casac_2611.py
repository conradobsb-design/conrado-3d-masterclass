"""Casa C Subsolo, 26/11: o levantamento no 12K B aplicado ("aplique os 5 itens";
`../../POE642_CasaC/renders/POE642_CasaC_PH_Subsolo_2611_levantamento.jpg`) e a porta da sauna ("a porta da sauna tem
outro formato que as demais").

1. **Vidros sem linha técnica** (a esquadria cromada, os tampões brancos e os traços saem; as folhas no vidro claro dos
   boxes, sem contorno, `um_pav_casaa_2511e.folhas_vidro`, de parede a parede), sobre a soleira do vão no creme das
   soleiras das portas desta planta (a mediana da soleira da porta da sauna, em cada imagem), sem contorno:
   - a sauna, o L junto à jardineira: o vão do PDF (694,0 a 706,0 em pé e 737,1 a 746,0 em cima, até a parede da
     direita, 759,7), o vidro em L (698,8 a 701,8 e 741,8 a 744,8); a ponta de baixo na parede (o toco de 832,6) e o
     traço tracejado da face de dentro (706) vira o piso da sauna de logo ao lado;
   - o box do BH academia: a divisória velha (o fio cromado e o pino) sai, coberta pelo piso de cada lado; as duas
     folhas de correr do PDF (895,6 a 897,1 de 896,5 a 930,2 e 894,1 a 895,6 de 926,1 a 959,8), de parede a parede;
   - a fachada entre a varanda e a academia: o vão do PDF (1063,6 a 1075,6, de 331,0 a 737,1), as quatro folhas de
     correr em escada (1072,6 / 1069,6 / 1066,6 / 1063,6, 3 px cada, com o transpasse do PDF); o fio claro junto à
     madeira vira a madeira de logo ao lado; a parede de baixo até a face (737,1).
2. **BH academia, o vaso**: o vaso quebrado sai (o travertino refeito na pegada, até a parede de trás) e entra a bacia
   Carrara da biblioteca (`biblioteca_1pav_casaa_1211`), na pose do PDF (950,0 a 980,6 x 914,6 a 935,7, de costas para a
   parede da direita), com a sombra rente; a face da parede atrás (o fio preto do vaso velho) no perfil da própria face,
   de logo acima e de logo abaixo.
3. **A janela da parede de baixo do box** (o vão do PDF, 822,6 a 855,1 x 961,0 a 966,9): a borda serrilhada de cima
   vira o piso do box de logo acima, reto até a face (961,0); no vão, o peitoril no creme das soleiras, o vidro claro no
   meio da espessura, o contorno preto fino (0,5 px) e o montante do meio (838,9).
4. **Rótulo SOBE PARA O JARDIM** (só no 12K B, na Kalam): o retângulo cinza atrás de JARDIM sai; o fundo dele vira o
   Bege Bahia de logo à esquerda (o mesmo trecho, 84 px antes), e as letras ficam (a cobertura de cada letra medida
   sobre o fundo cinza, o fundo trocado por baixo). Na final e no 12K A não há o retângulo (nada muda).
5. **Academia, os pontinhos brancos** na face de cima da parede (1604 a 1774,5 x 732,4 a 735,8): cada linha na mediana
   dela (o fio da face fica, os pontinhos saem).
6. **A porta da sauna** (a pedido: "a porta da sauna tem outro formato que as demais"): no PDF é a única porta com a
   folha de vidro (822,4 a 864,2 x 792,9 a 795,3: os dois montantes de 6 px nas pontas e o vidro entre eles); as outras
   são de folha cheia. A folha de madeira inteira sai (o piso do corredor de logo acima) e entram os dois montantes na
   madeira da própria folha de antes e o vidro claro entre eles, sem contorno.

Final, prancha e 12K A e B (cada item pelo registro local).

  python3 subsolo_casac_2611.py [item ...]
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
import esquadrias_pretas_1911 as EP  # noqa: E402
import vetor_2511 as V               # noqa: E402
import terreo_casaa_2511d as D       # noqa: E402
import terreo_casaa_2511g as G       # noqa: E402
import um_pav_casaa_2511 as U        # noqa: E402
import um_pav_casaa_2511c as C       # noqa: E402
import um_pav_casaa_2511d as DD      # noqa: E402
import um_pav_casaa_2511e as E       # noqa: E402

PLANTA = "C_Subsolo"
DZ = json.loads((EP.PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[PLANTA]
D.DZ_S = DZ["s"]                     # o travertino novo: a textura e o px/m da Casa A, o 12K na escala desta planta
PAREDE = (80.0, 80.0, 80.0)
PERFIL = (34.0, 34.0, 36.0)          # o preto das esquadrias (esquadrias_pretas_1911.Q_)
SOLEIRA_REF = (816.6, 756.0, 820.4, 788.0)   # a soleira da porta da sauna: o creme das soleiras desta planta


def copiar(img, s, origem, r, d, lados, pena=1.0):
    return U._copiar(img, s, origem, r, d, lados, pena)


def _mediana(img, s, origem, r):
    jan, reg = C._reg(img, r, s, origem, folga=0)
    xs, ys = V.coords(jan, s, origem)
    m = (xs[None, :] >= r[0]) & (xs[None, :] <= r[2]) & (ys[:, None] >= r[1]) & (ys[:, None] <= r[3])
    return np.median(reg[m], axis=0).astype(np.float32)


def pintar(img, s, origem, rets, cor):
    x0 = min(r[0] for r in rets) - 1
    y0 = min(r[1] for r in rets) - 1
    x1 = max(r[2] for r in rets) + 1
    y1 = max(r[3] for r in rets) + 1
    jan, reg = C._reg(img, (x0, y0, x1, y1), s, origem)
    reg = V.compor(reg, V.cob([V.ret(*r) for r in rets], jan, s, origem), np.float32(cor))
    return C._gravar(img, jan, reg)


def soleira(img, s, origem, rets):
    return pintar(img, s, origem, rets, _mediana(img, s, origem, SOLEIRA_REF))


def vidros(img, s, origem, caixa, folhas):
    jan, reg = C._reg(img, caixa, s, origem, folga=int(2 * s) + 2)
    reg = E.folhas_vidro(reg, jan, s, origem, folhas)
    return C._gravar(img, jan, reg)


def _caixa(rets, m=3.0):
    return (min(r[0] for r in rets) - m, min(r[1] for r in rets) - m, max(r[2] for r in rets) + m,
            max(r[3] for r in rets) + m)


# ----------------------------------------------------------------------------------------------------------------------
# 1. Os vidros
SAUNA = dict(vao=[(695.0, 737.1, 759.7, 746.0), (695.0, 746.0, 707.0, 832.6)],   # a parede de baixo: 695 a 707
             face=((707.0, 746.5, 709.4, 832.4), (3.4, 0.0)),        # o tracejado da face de dentro: o piso ao lado
             parede=[(695.0, 832.6, 707.0, 836.6)], parede_ref=(695.0, 839.0, 707.0, 848.0),
             vidro=[(698.8, 741.8, 701.8, 832.6), (698.8, 741.8, 759.7, 744.8)])


def vidro_sauna(img, s, origem, q=SAUNA):
    r, d = q["face"]
    img = copiar(img, s, origem, r, d, "r", pena=0.8)
    img = soleira(img, s, origem, q["vao"])
    img = pintar(img, s, origem, q["parede"], _mediana(img, s, origem, q["parede_ref"]))
    return vidros(img, s, origem, _caixa(q["vao"]), [q["vidro"]])


BOX_BH = dict(apagar=[((893.0, 896.3, 895.6, 960.0), (-3.4, 0.0), "l"), ((895.6, 896.3, 898.4, 960.0), (3.4, 0.0), "r")],
              folhas=[[(895.6, 896.5, 897.1, 930.2)], [(894.1, 926.1, 895.6, 959.8)]])


def vidro_box_bh(img, s, origem, q=BOX_BH):
    for r, d, lados in q["apagar"]:
        img = copiar(img, s, origem, r, d, lados, pena=0.8)
    return vidros(img, s, origem, _caixa([r for f_ in q["folhas"] for r in f_]), q["folhas"])


FACHADA = dict(vao=(1063.6, 331.0, 1075.6, 737.1), parede=[(1063.6, 737.1, 1075.6, 738.3)],
               parede_ref=(1063.6, 740.0, 1075.6, 743.0), junta=(1075.6, 331.0, 1077.4, 737.1),
               folhas=[(1072.6, 331.0, 1075.6, 437.3), (1069.6, 432.5, 1072.6, 536.4),
                       (1066.6, 531.7, 1069.6, 635.5), (1063.6, 630.8, 1066.6, 737.1)])


def madeira_ao_lado(img, s, origem, r):
    """O trecho `r` coberto pela madeira de logo à direita (o mesmo trecho deslocado: as tábuas correm em x)."""
    x0, y0, x1, y1 = r
    w = x1 - x0
    jan, reg = C._reg(img, (x0 - 1, y0 - 1, x1 + w + 1, y1 + 1), s, origem, folga=int(2 * s) + 2)
    d = int(round(w * s))
    fonte = np.roll(reg, -d, axis=1)
    a = V.cob([V.ret(*r)], jan, s, origem)[..., None]
    return C._gravar(img, jan, reg * (1 - a) + fonte * a)


def fachada_academia(img, s, origem, q=FACHADA):
    img = madeira_ao_lado(img, s, origem, q["junta"])
    img = soleira(img, s, origem, [q["vao"]])
    img = pintar(img, s, origem, q["parede"], _mediana(img, s, origem, q["parede_ref"]))
    return vidros(img, s, origem, _caixa([q["vao"]]), [[r] for r in q["folhas"]])


# ----------------------------------------------------------------------------------------------------------------------
# 2. O vaso do BH academia (a pose do PDF; a mesma bacia e a mesma medida dos banhos da Casa B)
VASO = dict(pdf=(950.0, 914.6, 980.6, 935.7), zona=(947.0, 911.6, 980.6, 938.7), face=(978.8, 909.0, 982.6, 941.0),
            face_ref=[(978.8, 898.0, 982.6, 907.0), (978.8, 943.0, 982.6, 952.0)])


def _face(img, s, origem, r, refs):
    """O retângulo `r` (na face de uma parede em pé) no perfil mediano da própria face, de logo acima e logo abaixo."""
    caixa = _caixa([r] + list(refs), 0.0)
    jan, reg = C._reg(img, caixa, s, origem, folga=0)
    xs, ys = V.coords(jan, s, origem)
    linhas = np.zeros(len(ys), bool)
    for q in refs:
        linhas |= (ys >= q[1]) & (ys <= q[3])
    perfil = np.median(reg[linhas], axis=0)
    a = V.cob([V.ret(*r)], jan, s, origem)[..., None]
    return C._gravar(img, jan, reg * (1 - a) + perfil[None] * a)


def vaso_bh(img, s, origem, q=VASO):
    img = G.refazer(img, s, origem, [(q["zona"], "ltb")])
    img = _face(img, s, origem, q["face"], q["face_ref"])
    x0, y0, x1, y1 = q["pdf"]
    return U._pousar(img, s, origem, "banho-2/bacia-carrara", (x0 + x1) / 2, (y0 + y1) / 2, 21.1, 30.7, -90.0, "baixa")


# ----------------------------------------------------------------------------------------------------------------------
# 3. A janela da parede de baixo do box
JANELA = dict(piso=((822.6, 957.4, 855.1, 961.0), (0.0, -3.8)), vao=(822.6, 961.0, 855.1, 966.9),
              vidro=(822.6, 963.15, 855.1, 964.75), montante=838.9, traco=0.5, montante_l=0.8)


def janela_box(img, s, origem, q=JANELA):
    r, d = q["piso"]
    img = copiar(img, s, origem, r, d, "tr", pena=0.8)
    img = soleira(img, s, origem, [q["vao"]])
    x0, y0, x1, y1 = q["vao"]
    img = vidros(img, s, origem, _caixa([q["vao"]]), [[q["vidro"]]])
    t, m = q["traco"], q["montante_l"] / 2
    linhas = [(x0, y0, x1, y0 + t), (x0, y1 - t, x1, y1), (x0, y0, x0 + t, y1), (x1 - t, y0, x1, y1),
              (q["montante"] - m, y0, q["montante"] + m, y1)]
    return pintar(img, s, origem, linhas, PERFIL)


# ----------------------------------------------------------------------------------------------------------------------
# 4. O rótulo SOBE PARA O JARDIM (o retângulo cinza do 12K B)
ROTULO = dict(janela=(472.0, 713.5, 554.0, 736.6), fonte_dx=-84.0, dif_min=10.0)


def rotulo_jardim(img, s, origem, q=ROTULO):
    jan = V.janela(img, q["janela"], s, origem, folga=0)
    X0, Y0, X1, Y1 = jan
    dx = int(round(q["fonte_dx"] * s))
    F = img[Y0:Y1, X0:X1].astype(np.float32)
    S_ = img[Y0:Y1, X0 + dx:X1 + dx].astype(np.float32)          # o Bege Bahia de logo à esquerda
    L = F.mean(2)
    Lbege = float(np.median(S_.mean(2)))
    letra = (L < 140).astype(np.uint8)
    k = max(int(round(0.45 * s)), 1)
    letra = cv2.dilate(letra, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * k + 1, 2 * k + 1)))
    fundo = cv2.inpaint(np.clip(F, 0, 255).astype(np.uint8), letra, max(3, 2 * k), cv2.INPAINT_TELEA).astype(np.float32)
    Lf = fundo.mean(2)
    Lbox = float(np.median(Lf))
    if Lbege - Lbox < q["dif_min"]:
        return img                                                # sem o retângulo (a final e o 12K A)
    Lfs = cv2.GaussianBlur(Lf, (0, 0), max(0.25 * s, 0.6))
    t = np.clip(((Lbege - Lfs) / (Lbege - Lbox) - 0.3) / 0.4, 0, 1)
    caixa = (t > 0.5).astype(np.uint8)                            # o retângulo, e a beira dele inteira (1 px a mais)
    caixa = cv2.dilate(caixa, np.ones((2 * k + 1, 2 * k + 1), np.uint8)).astype(np.float32)
    t = np.clip(cv2.GaussianBlur(caixa, (0, 0), max(0.2 * s, 0.5)) * 1.6, 0, 1) * (caixa > 0)
    # a luz do Bege Bahia trazido casada com a do entorno (o anel fora do retângulo, sem letras)
    anel = (cv2.dilate(caixa, np.ones((6 * k + 1, 6 * k + 1), np.uint8)) > 0) & (caixa == 0) & (letra == 0)
    if anel.sum() > 50:
        S_ = S_ * (np.median(F[anel], axis=0) / np.maximum(np.median(S_[anel], axis=0), 1.0))[None, None, :]
    Ltxt = float(np.percentile(L, 1))
    a = np.clip((Lf - L) / np.maximum(Lf - Ltxt, 1.0), 0, 1)
    out = F + ((1 - a) * t)[..., None] * (S_ - fundo)
    img[Y0:Y1, X0:X1] = np.clip(np.round(out), 0, 255).astype(np.uint8)
    return img


# ----------------------------------------------------------------------------------------------------------------------
# 5. Os pontinhos da parede da academia
PONTOS = dict(faixa=(1604.0, 732.4, 1774.5, 735.8), ref=(1608.0, 1760.0), dif=14.0)


def pontinhos(img, s, origem, q=PONTOS):
    jan, reg = C._reg(img, q["faixa"], s, origem, folga=0)
    xs, ys = V.coords(jan, s, origem)
    cols = (xs >= q["ref"][0]) & (xs <= q["ref"][1])
    perfil = np.median(reg[:, cols], axis=1)                      # cada linha na mediana dela
    dev = np.abs(reg.mean(2) - perfil.mean(1)[:, None]) > q["dif"]
    dev &= ((xs >= q["faixa"][0]) & (xs <= q["faixa"][2]))[None, :]
    k = max(int(round(0.4 * s)), 1)
    dev = cv2.dilate(dev.astype(np.uint8), np.ones((2 * k + 1, 2 * k + 1), np.uint8)) > 0
    dev &= ((xs >= q["faixa"][0]) & (xs <= q["faixa"][2]))[None, :]
    reg = np.where(dev[..., None], perfil[:, None, :], reg)
    return C._gravar(img, jan, reg)


# ----------------------------------------------------------------------------------------------------------------------
# 6. A porta da sauna: a folha de vidro com os dois montantes do PDF
PORTA = dict(folha=(822.4, 792.9, 864.2, 795.3), montantes=[(822.4, 792.9, 828.4, 795.3), (858.2, 792.9, 864.2, 795.3)],
             madeira=(830.0, 836.0),                               # o trecho da folha velha que dá a madeira
             apagar=((822.4, 791.4, 867.0, 797.0), (0.0, -6.0)), vidro=(828.4, 792.9, 858.2, 795.3))


def porta_sauna(img, s, origem, q=PORTA):
    jan0, reg0 = C._reg(img, _caixa([q["folha"]], 6.0), s, origem, folga=0)
    r, d = q["apagar"]
    img = copiar(img, s, origem, r, d, "trb", pena=0.8)
    jan, reg = C._reg(img, _caixa([q["folha"]], 6.0), s, origem, folga=0)
    assert jan == jan0
    w0, w1 = q["madeira"]
    for m in q["montantes"]:
        dx = int(round((w0 - m[0]) * s))                          # a madeira da folha velha (830 a 836) no montante
        fonte = np.roll(reg0, -dx, axis=1)
        a = V.cob([V.ret(*m)], jan, s, origem)[..., None]
        reg = reg * (1 - a) + fonte * a
    img = C._gravar(img, jan, reg)
    return vidros(img, s, origem, _caixa([q["folha"]]), [[q["vidro"]]])


FUNC = {"vidro_sauna": vidro_sauna, "vidro_box_bh": vidro_box_bh, "fachada_academia": fachada_academia,
        "vaso_bh": vaso_bh, "janela_box": janela_box, "rotulo_jardim": rotulo_jardim, "pontinhos": pontinhos,
        "porta_sauna": porta_sauna}
ITENS = {"vidro_sauna": (680.0, 728.0, 775.0, 845.0), "vidro_box_bh": (860.0, 880.0, 960.0, 975.0),
         "fachada_academia": (1040.0, 320.0, 1090.0, 750.0), "vaso_bh": (935.0, 895.0, 995.0, 955.0),
         "janela_box": (810.0, 945.0, 870.0, 985.0), "rotulo_jardim": (440.0, 690.0, 620.0, 750.0),
         "pontinhos": (1580.0, 710.0, 1780.0, 760.0), "porta_sauna": (805.0, 745.0, 875.0, 805.0)}


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
    for op in os.environ.get("OPCOES", "AB"):
        rel = EP.PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_12K_opcao_{op}.jpg"
        pil = Image.open(rel)
        dpi = pil.info.get("dpi", (743, 743))
        im = cv2.cvtColor(np.array(pil.convert("RGB")), cv2.COLOR_RGB2BGR)
        del pil
        cinza = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        for nome in nomes:
            sx, org, cc = DD._registro(base, cinza, DZ, ITENS[nome])
            im = item(im, nome, sx, org)
            print(f"   {op}: {nome} (registro {cc:.3f}, escala {sx:.3f})")
        Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).save(rel, quality=95, subsampling=0, dpi=dpi)
        del im, cinza


if __name__ == "__main__":
    main(sys.argv[1:] or None)

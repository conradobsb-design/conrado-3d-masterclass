"""Casa C Térreo, 27/11 (2): os carros da garagem e os adornos da mesa redonda da sala TV.

- **Garagem** ("corrigir o contorno dos carros e remover o piso antigo em volta deles"): cada um dos 3 carros tirado
  pela silhueta (o branco e o cinza neutros sobre o piso marrom, os furos fechados) e pousado de novo sobre o piso
  refeito. Numa faixa de 12 px em volta, o piso da garagem é tecido de novo (quilting dos trechos limpos entre os carros,
  no tom do piso em volta), sem o halo e as pintas do piso antigo. A borda do carro fica macia (a silhueta encolhida e
  desfocada) e com a sombra curta de contato, como na garagem da Casa D (`correcoes_terreo_casad_1711.carros`).
- **Sala TV** ("adicione adornos aqui sobre ela"): na mesa redonda de nogueira, a pilha de livros "ART" e o vaso de
  cerâmica com flores secas, da biblioteca (`../biblioteca-objetos/02-terreo/sala-de-estar/adornos/`), com a sombra curta
  para baixo e à esquerda. O tapete em volta da mesa já foi refeito em `terreo_casac_2611g`.

Final, prancha e 12K A e B (pelo registro local).

  python3 terreo_casac_2711b.py [itens]
"""
import json
import os
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
sys.path.insert(0, str(Path(__file__).resolve().parent))
import esquadrias_pretas_1911 as EP              # noqa: E402
import vetor_2511 as V                           # noqa: E402
import um_pav_casaa_2511d as DD                  # noqa: E402
import terreo_casac_2611i as I                   # noqa: E402
from texturizar_base import quilting             # noqa: E402

PLANTA = "C_Terreo"
DZ = json.loads((EP.PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[PLANTA]

CARROS = dict(caixas=[(2730.0, 362.0, 2880.0, 678.0), (2896.0, 362.0, 3044.0, 678.0), (3089.0, 362.0, 3238.0, 678.0)],
              amostras=[(2867.0, 400.0, 2906.0, 640.0), (3226.0, 400.0, 3262.0, 640.0), (2712.0, 400.0, 2742.0, 640.0)],
              rb_carro=30, faixa_px=13.0, p_px=11, sobra_px=4, sombra=0.30, sig_tom=7.0, pena=3.0,
              rotulo=(3018.0, 450.0, 3118.0, 535.0))          # o rótulo GARAGEM: as letras claras ficam
ADORNOS_TV = [("livros-art-d.png", 920.0, 1427.0, 778.0, 10.0),
              ("vaso-flores-secas-a.png", 920.0, 1448.5, 760.0, 0.0)]


# ----------------------------------------------------------------------------------------------------------------------
def _carro(img, s, origem, caixa, fontes, tom, q, rng):
    jan = V.janela(img, caixa, s, origem, folga=0)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1]
    h, w = reg.shape[:2]
    Ii = reg.astype(np.int16)
    carro = ((Ii[..., 2] - Ii[..., 0]) < q["rb_carro"]).astype(np.uint8)
    k = 2 * int(np.ceil(1.5 * s)) + 1
    carro = cv2.morphologyEx(carro, cv2.MORPH_OPEN, np.ones((k, k), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(carro, 8)
    if n < 2:
        return img
    carro = ndimage.binary_fill_holes(lab == (1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))))
    D = int(np.ceil(q["faixa_px"] * s))
    faixa = cv2.dilate(carro.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * D + 1,) * 2))
    p = max(8, int(round(q["p_px"] * s)))
    sobra = max(3, int(round(q["sobra_px"] * s)))
    piso = quilting(fontes, h, w, p=p, sobra=sobra, candidatos=300, rng=rng)[:h, :w]
    # o tom do piso novo segue o do piso de fora, ponto a ponto (a média local, estendida para dentro da faixa), e não
    # um tom só: sem o anel na emenda
    fora = (~(faixa > 0) & (reg.astype(np.float32).mean(2) < 175)).astype(np.float32)   # sem as letras do rótulo
    sg = q["sig_tom"] * s
    peso = cv2.GaussianBlur(fora, (0, 0), sg)
    alvo = cv2.GaussianBlur(reg.astype(np.float32) * fora[..., None], (0, 0), sg) / np.maximum(peso, 1e-4)[..., None]
    base = cv2.GaussianBlur(piso, (0, 0), sg)
    piso = piso * (alvo / np.maximum(base, 1.0))
    a_f = cv2.GaussianBlur(faixa.astype(np.float32), (0, 0), q["pena"] * s)
    a_f = np.maximum(a_f, cv2.erode(faixa, np.ones((3, 3), np.uint8)).astype(np.float32))
    # as letras do rótulo (claras sobre o marrom) não são refeitas
    rot = V.cob([V.ret(*q["rotulo"])], jan, s, origem) > 0.5
    letra = rot & (reg.astype(np.float32).mean(2) > 175) & ~(cv2.dilate(carro.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0)
    if letra.any():
        kk = 2 * int(np.ceil(1.5 * s)) + 1
        letra = cv2.dilate(letra.astype(np.uint8), np.ones((kk, kk), np.uint8)).astype(np.float32)
        a_f *= 1 - cv2.GaussianBlur(letra, (0, 0), 0.6 * s)
    novo = reg.astype(np.float32) * (1 - a_f[..., None]) + piso * a_f[..., None]
    e = max(1, int(round(0.8 * s)))
    core = cv2.erode(carro.astype(np.uint8), np.ones((2 * e + 1, 2 * e + 1), np.uint8)).astype(np.float32)
    ca = np.clip(cv2.GaussianBlur(core, (0, 0), 0.7 * s) * 1.15, 0, 1)
    M = np.float32([[1, 0, -1.2 * s], [0, 1, 1.6 * s]])
    sb = cv2.GaussianBlur(cv2.warpAffine(carro.astype(np.float32), M, (w, h)), (0, 0), 2.2 * s)
    novo *= (1 - q["sombra"] * sb * (1 - ca))[..., None]
    novo = novo * (1 - ca[..., None]) + reg.astype(np.float32) * ca[..., None]
    img[Y0:Y1, X0:X1] = np.clip(np.round(novo), 0, 255).astype(np.uint8)
    return img


def carros(img, s, origem, q=CARROS):
    fontes = []
    for a in q["amostras"]:
        X0, Y0, X1, Y1 = V.janela(img, a, s, origem, folga=0)
        fontes.append(img[Y0:Y1, X0:X1].astype(np.float32))
    tom = np.median(np.concatenate([f.reshape(-1, 3) for f in fontes]), axis=0)
    rng = np.random.default_rng(2711)
    for caixa in q["caixas"]:
        img = _carro(img, s, origem, caixa, fontes, tom, q, rng)
    return img


def adornos_tv(img, s, origem, q=ADORNOS_TV):
    jan = V.janela(img, (1395.0, 730.0, 1480.0, 812.0), s, origem, folga=2)
    X0, Y0, X1, Y1 = jan
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    for png, ppm, cx, cy, giro in q:
        reg = I._colar(reg, jan, s, origem, png, ppm, cx, cy, giro)
    img[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return img


FUNC = {"carros": carros, "adornos_tv": adornos_tv}
ITENS = {"carros": (2700.0, 340.0, 3290.0, 700.0), "adornos_tv": (1380.0, 715.0, 1500.0, 830.0)}


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

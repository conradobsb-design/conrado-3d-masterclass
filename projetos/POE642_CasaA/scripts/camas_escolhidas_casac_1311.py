"""A prancha das camas escolhidas (A) da Casa C (13/11): a manta de tricô grosso jogada e caída nos pés só nas camas de
casal e na king; nas de solteiro, só a peseira leve ("Só use as mantas de tricô nas camas de casal. Nas camas de solteiro
só pezeira"). Todas voltam com a mesma margem `pad` nos 4 lados (o centro não muda), para a prancha sair na mesma escala."""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
import camas_casac_1311 as C, manta_caida_casac_1311 as MC
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont
f_tit = ImageFont.truetype(str(C.FONTES / 'Inter-SemiBold.otf'), 32)
f_cap = ImageFont.truetype(str(C.FONTES / 'Inter-Regular.otf'), 21)
ALT = 400
ims = []
for nome, tipo, roupa, opcoes in C.QUARTOS:
    enf = opcoes[0][0]
    if tipo == "solteiro":
        P = C.cama(tipo, roupa, enf, "peseira")
        pad = int(round(MC.PAD * P.shape[0]))
        Q = np.pad(P, ((pad, pad), (pad, pad), (0, 0)))
        cap = f'roupa {roupa}, peseira {enf}'
    else:
        P = C.cama(tipo, roupa, enf, "nada")
        Q, pad = MC.manta_caida(P, enf, "esq")
        cap = f'roupa {roupa}, manta {enf}'
    cv2.imwrite(str(C.TMP) + f'/escolhida_{tipo}_{roupa}_{enf}_pad{pad}.png'.replace(' ', '-'), Q.astype(np.uint8))
    ims.append((C.foto(Q, ALT, fundo=(236, 232, 226)), nome.split(' · ')[0], cap))
d0 = ImageDraw.Draw(Image.new('RGB', (10, 10)))
larg = [max(im.width, int(d0.textlength(c, font=f_cap))) + 40 for im, _, c in ims]
W = max(sum(larg) + 20, 1500)
folha = Image.new('RGB', (W, 66 + ALT + 150), (247, 245, 242))
d = ImageDraw.Draw(folha)
d.text((14, 14), 'POE 642 · Casa C · camas escolhidas (A): manta de tricô nas de casal, peseira nas de solteiro', font=f_tit, fill=(30, 30, 30))
x = 20
for (im, q, cap), lg in zip(ims, larg):
    folha.paste(im, (x, 66))
    d.text((x, 66 + ALT + 8), q, font=f_cap, fill=(128, 40, 36))
    d.text((x, 66 + ALT + 36), cap, font=f_cap, fill=(30, 30, 30))
    x += lg
for j, l in enumerate(['Casal e king: a manta de tricô grosso amontoada sobre os pés, caindo pela beirada do pé e de um lado (o lado livre '
                       'do quarto), com a sombra no piso.', 'Solteiro: só a peseira em tom leve atravessada nos pés. Em todas, o '
                       'travesseiro extra no tom da manta ou da peseira.']):
    d.text((14, 66 + ALT + 74 + 28 * j), l, font=f_cap, fill=(95, 95, 95))
arq = C.OUT / 'POE642_CasaC_PH_Terreo_1311_camas_escolhidas.jpg'
folha.save(arq, quality=90)
print(arq, folha.size)

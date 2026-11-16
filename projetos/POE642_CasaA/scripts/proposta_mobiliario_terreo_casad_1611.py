"""O mobiliário do Térreo da Casa D pela biblioteca da Casa D (16/11), em duas alternativas, só para a escolha (nada é
aplicado aqui).

Usuário: "Vou precisar de propostas para os mobiliários do térreo, seguindo a biblioteca da casa D. Traga duas
alternativas, para eu decidir." A biblioteca é a do Drive (`POE642-Casa-D-Objetos-e-Pisos-Claude-Code.zip`, 100 objetos
em 38 ambientes), em `POE642_CasaD/biblioteca-objetos`: 42 peças geradas para a Casa D a partir dos renders e das
pranchas dela e as variantes compartilhadas das Casas A e B.

- **Alternativa 1, linha Casa D:** as peças geradas para a Casa D (linho cru, madeira média e escura, a poltrona oliva da
  sala íntima, as cadeiras de fibra da varanda) e as bancadas de quartzito Aura da apresentação de banheiros.
- **Alternativa 2, madeira e fibra:** as variantes compartilhadas onde a biblioteca tem outra peça (poltronas creme com
  aro de madeira, mesas laterais de metal e madeira, cadeiras de madeira e tecido, poltronas externas de corda, criados
  redondos, tapete de lã) e as cubas esculpidas em pedra bege; onde não há outra, a mesma peça da Casa D.

Nas duas: as peças nas posições e nas quantidades do PDF, as mantas das camas nos tons de 15/11 (terracota na master,
bege na suíte 1, areia na suíte 2), a cozinha e o gourmet com as únicas peças da biblioteca para eles.

  python3 proposta_mobiliario_terreo_casad_1611.py [--final <png de hoje>]
Saída: `POE642_CasaD/renders/POE642_CasaD_PH_Terreo_1611_mobiliario_alternativas_<n>.jpg`.
"""
import argparse
from pathlib import Path

import cv2
from PIL import Image, ImageDraw

import proposta_biblioteca_casad_1511 as P15

AQUI = Path(__file__).resolve().parent
CASA_D = AQUI.parents[1] / "POE642_CasaD"
BIB_D = CASA_D / "biblioteca-objetos" / "02-terreo"
R = CASA_D / "renders"
W = P15.W
A1, A2 = (176, 120, 86), (92, 110, 84)          # as cores dos títulos das alternativas (terracota e oliva)

# cada ambiente: título, recortes de hoje (px da final), alternativa 1 (peças, texto), alternativa 2, nas duas (texto)
AMBIENTES = [
 ("Living, jantar e hall de entrada", [(1810, 720, 2620, 1330)],
  ([("living/sofa-living-d", "sofá de linho do living"), ("living/poltrona-concha-d", "poltrona concha de linho"),
    ("living/mesa-centro-circular-d", "mesa de centro redonda (madeira escura)"),
    ("living/mesa-centro-seixo-d", "mesa de centro orgânica"), ("jantar/mesa-jantar-longa-d", "mesa longa de jantar"),
    ("jantar/cadeira-jantar-linho-d", "cadeira de madeira e linho")],
   ["Estar do jantar: as 4 poltronas concha de linho em volta da mesa de centro redonda de madeira escura.",
    "Estar do living: o sofá de linho, as poltronas concha e as mesas orgânicas sobre o tapete de trama clara.",
    "Jantar: a mesa longa de madeira com as cadeiras de madeira e linho, nas 10 do PDF."]),
  ([("living/sofa-living-d", "sofá de linho do living"),
    ("living/poltrona-creme-madeira-render", "poltrona creme com aro de madeira"),
    ("living/mesa-lateral-metal-madeira", "mesa lateral de metal e madeira"),
    ("living/mesa-centro-seixo-d", "mesa de centro orgânica"), ("jantar/mesa-jantar-longa-d", "mesa longa de jantar"),
    ("jantar/cadeira-a", "cadeira de madeira e tecido")],
   ["Estar do jantar: as 4 poltronas creme com aro de madeira em volta da mesa de centro orgânica.",
    "Estar do living: o mesmo sofá de linho, as poltronas creme e as mesas laterais de metal e madeira, no tapete de "
    "trama clara.",
    "Jantar: a mesa longa com as cadeiras de madeira e tecido (o encosto em arco), nas 10 do PDF."]),
  "Hall: o aparador em freijó e o vaso de folhagem (as únicas peças do hall na biblioteca)."),
 ("Varanda gourmet", [(1370, 690, 1830, 1200)],
  ([("varanda-gourmet/sofa-curvo-gourmet-d", "sofá curvo claro"),
    ("varanda-gourmet/mesa-redonda-gourmet-d", "mesa redonda da varanda"),
    ("varanda-gourmet/cadeira-gourmet-fibra-d", "cadeira externa de fibra"),
    ("varanda-gourmet/poltrona-concha-d", "poltrona concha de linho"),
    ("varanda-gourmet/mesa-centro-seixo-d", "mesa de centro orgânica")],
   ["As 2 mesas redondas com as 6 cadeiras de fibra trançada cada (as do PDF).",
    "O estar: o sofá curvo claro, as 2 poltronas concha e as mesas orgânicas no tapete de hoje."]),
  ([("varanda-gourmet/sofa-curvo-gourmet-d", "sofá curvo claro"),
    ("varanda-gourmet/mesa-redonda-gourmet-d", "mesa redonda da varanda"),
    ("varanda-gourmet/cadeira-gourmet-creme-madeira", "cadeira de madeira com assento creme"),
    ("varanda-gourmet/poltrona-externa-b", "poltrona externa de corda"),
    ("varanda-gourmet/mesa-lateral-externa", "mesa lateral externa"),
    ("varanda-gourmet/vaso-folhagem-b", "vaso arredondado com folhagem")],
   ["As 2 mesas redondas com as cadeiras de madeira e assento creme.",
    "O estar: o sofá curvo, as 2 poltronas de corda e as mesas laterais externas de madeira."]),
  ""),
 ("Cozinha e gourmet", [(1370, 330, 2160, 700)],
  ([("gourmet/tampo-gourmet-tabaco-d", "tampo de granito Marrom Tabaco"),
    ("cozinha/ilha-cozinha-clara-d", "ilha clara da cozinha"), ("gourmet/banqueta-gourmet-d", "banqueta alta em madeira"),
    ("gourmet/cooktop-quatro-bocas", "cooktop de 4 bocas"), ("gourmet/grelha-churrasqueira", "grelha da churrasqueira"),
    ("cozinha/cuba-franke-dupla-vista-superior", "cuba dupla de inox")],
   ["A ilha da cozinha clara, a do gourmet com o tampo Marrom Tabaco, as 5 banquetas altas de madeira do PDF."]),
  None,
  "A biblioteca da Casa D tem uma peça só para cada item daqui: a cozinha e o gourmet saem iguais nas duas."),
 ("Sala íntima", [(1400, 1330, 1790, 1720)],
  ([("sala-intima/sofa-intimo-l-d", "sofá em L da sala íntima"), ("sala-intima/poltrona-verde-intima-d", "poltrona oliva"),
    ("sala-intima/mesa-intima-redonda-d", "mesa de centro redonda"), ("sala-intima/tapete-intimo-d", "tapete de trama clara")],
   ["O sofá em L de linho, a poltrona de veludo oliva (o tom de cor da casa), a mesa redonda de madeira clara e o "
    "tapete de trama da sala íntima."]),
  ([("sala-intima/sofa-intimo-l-d", "sofá em L da sala íntima"),
    ("sala-intima/poltrona-creme-madeira-render", "poltrona creme com aro de madeira"),
    ("sala-intima/mesa-lateral-metal-madeira", "mesa lateral de metal e madeira"),
    ("sala-intima/tapete-estar-trama-clara", "tapete de trama clara")],
   ["O mesmo sofá em L, a poltrona creme com aro de madeira, as mesas laterais de metal e madeira e o tapete de trama "
    "clara do living (a sala íntima fica no tom do estar)."]),
  ""),
 ("Suíte master, closet e banho master", [(500, 1321, 1110, 1757)],
  ([("suite-master/cama-master-d", "cama king da Casa D"), ("suite-master/criado-lateral-d", "criado lateral de madeira"),
    ("suite-master/banco-peseira-d", "banco de peseira em linho"), ("living/poltrona-concha-d", "poltrona concha de linho"),
    ("closet-master/armario-cabides-d", "módulo de closet com cabides"),
    ("banho-master/bancada-dupla-quartzito-aura", "bancada dupla de quartzito Aura")],
   ["A cama king da Casa D (manta terracota), os criados laterais de madeira e o banco de peseira em linho.",
    "O estar da suíte com a poltrona concha; o closet com os módulos de cabides.",
    "Banho master: a bancada dupla de quartzito Aura (a apresentação de banheiros)."]),
  ([("suite-master/cama-master-d", "cama king da Casa D"), ("suite-master/criado-redondo", "criado redondo em madeira"),
    ("suite-master/banco-peseira-d", "banco de peseira em linho"),
    ("living/poltrona-creme-madeira-render", "poltrona creme com aro de madeira"), ("suite-master/tapete", "tapete de lã"),
    ("banho-master/cuba-master-dupla-d", "bancada dupla em pedra bege")],
   ["A mesma cama king (manta terracota), os criados redondos de madeira, o banco de peseira e o tapete de lã.",
    "O estar da suíte com a poltrona creme com aro de madeira.",
    "Banho master: a bancada dupla esculpida em pedra bege."]),
  "Nas duas: a cadeira estofada de bancada na escrivaninha; o closet na cor padrão dos armários."),
 ("Suítes 1 e 2 e banhos 1 e 2", [(1079, 1393, 1450, 1757), (1793, 1393, 2193, 1757)],
  ([("suite-1/cama-casal-d", "cama de casal em linho claro"), ("suite-1/criado-lateral-d", "criado lateral de madeira"),
    ("suite-1/banco-peseira-d", "banco de peseira em linho"), ("suite-1/armario-cabides-d", "módulo de closet com cabides"),
    ("banho-1/bancada-simples-quartzito-aura", "bancada de quartzito Aura")],
   ["As camas de casal da Casa D (manta bege na suíte 1, areia na suíte 2), os criados laterais e os bancos de peseira.",
    "Banhos 1 e 2: a bancada de uma cuba em quartzito Aura."]),
  ([("suite-1/cama-casal-d", "cama de casal em linho claro"), ("suite-1/criado-redondo", "criado redondo em madeira"),
    ("suite-1/banco-peseira-d", "banco de peseira em linho"), ("suite-1/tapete", "tapete de lã"),
    ("banho-1/cuba-social-d", "cuba esculpida em pedra bege")],
   ["As mesmas camas (bege e areia), os criados redondos, os bancos de peseira e o tapete de lã sob a cama.",
    "Banhos 1 e 2: a cuba esculpida em pedra bege."]),
  "Nas duas: a cadeira estofada de bancada nas escrivaninhas."),
 ("Suíte 3/escritório e banho 3", [(2150, 1360, 2560, 1757)],
  ([("suite-3-e-escritorio/mesa-escritorio-d", "mesa da suíte escritório"),
    ("suite-3-e-escritorio/cadeira-escritorio", "cadeira de escritório"),
    ("jantar/cadeira-jantar-linho-d", "cadeira de visita em madeira e linho"),
    ("suite-3-e-escritorio/sofa-escritorio-d", "sofá reto da suíte escritório"),
    ("banho-3/bancada-simples-quartzito-aura", "bancada de quartzito Aura")],
   ["A mesa de madeira, a cadeira de escritório e as cadeiras de visita de madeira e linho; o sofá reto no estar.",
    "Banho 3: a bancada de quartzito Aura."]),
  ([("suite-3-e-escritorio/mesa-escritorio-d", "mesa da suíte escritório"),
    ("suite-3-e-escritorio/cadeira-escritorio", "cadeira de escritório"),
    ("jantar/cadeira-a", "cadeira de visita em madeira e tecido"),
    ("suite-3-e-escritorio/sofa-escritorio-d", "sofá reto da suíte escritório"),
    ("banho-3/cuba-social-d", "cuba esculpida em pedra bege")],
   ["A mesma mesa e cadeira de escritório, as cadeiras de visita de madeira e tecido, o sofá reto.",
    "Banho 3: a cuba esculpida em pedra bege."]),
  ""),
 ("Deck da piscina, DCE e banhos de serviço", [(440, 330, 1380, 1180), (2280, 380, 2660, 680)],
  ([("deck-da-piscina/espreguicadeira-deck-d", "espreguiçadeira de linho externo (opcional)"),
    ("deck-da-piscina/vaso-baixo-deck-d", "vaso de cerâmica do deck (opcional)"),
    ("quarto-dce/cama-solteiro-d", "cama de solteiro"), ("banho-dce/cuba-dce-gabriel-d", "cuba DCE com tampo São Gabriel"),
    ("banho-gourmet/cuba-travertino-gourmet", "cuba de travertino do banho gourmet")],
   ["Deck: o PDF não tem espreguiçadeiras; se quiser, as de linho externo da Casa D e os vasos de cerâmica.",
    "DCE: a cama de solteiro; banho DCE: a cuba com tampo São Gabriel."]),
  ([("prainha/espreguicadeira-madeira-render", "espreguiçadeira de madeira (opcional)"),
    ("prainha/espreguicadeira-prainha", "espreguiçadeira da prainha (opcional)"),
    ("quarto-dce/cama-solteiro-d", "cama de solteiro"),
    ("banho-dce/cuba-servico-sao-gabriel", "cuba de serviço São Gabriel"),
    ("banho-gourmet/cuba-travertino-gourmet", "cuba de travertino do banho gourmet")],
   ["Deck: se quiser, as espreguiçadeiras de madeira e, na prainha, as baixas da biblioteca.",
    "DCE: a mesma cama; banho DCE: a cuba de serviço São Gabriel."]),
  "Nas duas: a cuba esculpida em travertino no banho gourmet; o lavabo fica como está (granito Marrom Tabaco)."),
]


def peca_d(rel, lado=150):
    """A peça da biblioteca da Casa D (o `peca` da proposta de 15/11, com a outra pasta)."""
    guarda = P15.BIB
    try:
        P15.BIB = BIB_D
        return P15.peca(rel, lado)
    finally:
        P15.BIB = guarda


def bloco(d, img, x, y, larg, titulo, cor, pecas, textos):
    """O título da alternativa, as peças (6 por linha) e o texto; devolve o y de baixo."""
    d.rectangle([x, y, x + 8, y + 30], fill=cor)
    d.text((x + 18, y), titulo, font=P15.F_S, fill=cor)
    y += 42
    for i, (rel, leg) in enumerate(pecas):
        cx, cy = x + (i % 6) * 222, y + (i // 6) * 196
        img.paste(peca_d(rel), (cx, cy))
        d.rectangle([cx, cy, cx + 150, cy + 150], outline=P15.LINHA, width=1)
        for j, l in enumerate(P15.linhas(leg, P15.F_C, 210)[:2]):
            d.text((cx, cy + 154 + j * 19), l, font=P15.F_C, fill=P15.TINTA)
    y += ((len(pecas) + 5) // 6) * 196 + 4
    for t in textos:
        for l in P15.linhas("• " + t, P15.F_B, larg):
            d.text((x, y), l, font=P15.F_B, fill=P15.TINTA)
            y += 31
        y += 6
    return y + 18


def altura_bloco(larg, pecas, textos):
    return 42 + ((len(pecas) + 5) // 6) * 196 + 4 + sum(len(P15.linhas("• " + t, P15.F_B, larg)) * 31 + 6
                                                         for t in textos) + 18


def secao(final, n, titulo, recortes, alt1, alt2, nas_duas):
    esq = []
    alt_max = 900 if len(recortes) == 1 else 560
    for x0, y0, x1, y1 in recortes:
        c = final[y0:y1, x0:x1]
        k = min(1150 / c.shape[1], alt_max / c.shape[0], 2.4)
        c = cv2.resize(c, None, fx=k, fy=k, interpolation=cv2.INTER_AREA if k < 1 else cv2.INTER_CUBIC)
        esq.append(Image.fromarray(cv2.cvtColor(c, cv2.COLOR_BGR2RGB)))
    h_esq = sum(i.height for i in esq) + 14 * (len(esq) - 1) + 34
    xr, lr = 1230, W - 1230 - 40
    h_dir = 0
    blocos = [("Alternativa 1 · linha Casa D", A1, *alt1)]
    if alt2:
        blocos.append(("Alternativa 2 · madeira e fibra", A2, *alt2))
    else:
        blocos = [("Nas duas alternativas", P15.SUAVE, *alt1)]
    h_dir = sum(altura_bloco(lr, p, t) for _, _, p, t in blocos)
    if nas_duas:
        h_dir += len(P15.linhas(nas_duas, P15.F_P, lr - 28)) * 28 + 40
    H = max(h_esq, h_dir) + 120
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 64], fill=(244, 243, 239))
    d.text((40, 12), f"{n}. {titulo}", font=P15.F_T, fill=P15.TINTA)
    yy = 90
    d.text((40, yy - 4), "Hoje (a revisão de 15/11, em andamento)", font=P15.F_S, fill=P15.SUAVE)
    yy += 30
    for im in esq:
        img.paste(im, (40, yy))
        d.rectangle([40, yy, 40 + im.width, yy + im.height], outline=P15.LINHA, width=2)
        yy += im.height + 14
    y = 90
    for i, (tit, cor, pecas, textos) in enumerate(blocos):
        if i:
            d.line([xr, y - 10, xr + lr, y - 10], fill=P15.LINHA, width=2)
            y += 8
        y = bloco(d, img, xr, y, lr, tit, cor, pecas, textos)
    if nas_duas:
        t = P15.linhas(nas_duas, P15.F_P, lr - 28)
        h = len(t) * 28 + 14
        d.rectangle([xr, y, xr + lr, y + h], fill=(240, 238, 232))
        for j, l in enumerate(t):
            d.text((xr + 14, y + 7 + j * 28), l, font=P15.F_P, fill=P15.TINTA)
    return img


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--final", default=str(R / "POE642_CasaD_PH_Terreo_final_rotulos.png"))
    a = ap.parse_args()
    final = cv2.imread(a.final)
    secs = [secao(final, i + 1, *s) for i, s in enumerate(AMBIENTES)]
    for k, grupo in enumerate((secs[:4], secs[4:])):
        cab = Image.new("RGB", (W, 150), (255, 255, 255))
        dc = ImageDraw.Draw(cab)
        dc.text((40, 22), "Casa D · Térreo · mobiliário pela biblioteca da Casa D · duas alternativas, para a escolha",
                font=P15.F_T, fill=P15.TINTA)
        dc.text((40, 74), "Alternativa 1: as peças geradas para a Casa D (linho, madeira, oliva) e o quartzito Aura nos "
                "banhos. Alternativa 2: as variantes de madeira e fibra da biblioteca e a pedra bege nos banhos.",
                font=P15.F_P, fill=P15.SUAVE)
        dc.text((40, 106), "Nas duas: as peças nas posições e quantidades do PDF; as mantas em terracota, bege e areia "
                "(15/11). Pode também misturar, ambiente por ambiente. Nada aplicado ainda.", font=P15.F_P,
                fill=P15.SUAVE)
        H = cab.height + sum(s.height + 24 for s in grupo)
        out = Image.new("RGB", (W, H), (255, 255, 255))
        out.paste(cab, (0, 0))
        y = cab.height
        for s in grupo:
            out.paste(s, (0, y))
            y += s.height + 24
        f = R / f"POE642_CasaD_PH_Terreo_1611_mobiliario_alternativas_{k + 1}.jpg"
        out.save(f, quality=86)
        print(f.name, out.size)


if __name__ == "__main__":
    main()

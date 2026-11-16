"""A proposta do mobiliário do Térreo da Casa E (16/11), ambiente por ambiente, só para o OK (nada é aplicado aqui).

Usuário: "VAMOS ALTERAR TODO O MOBILIARIO E REVER AMBIENTE POR AMBIENTE". Regra 0 (`POE642_REGRAS_CONSOLIDADAS_CDE.md`):
proposta antes, instalação depois. Para cada ambiente: a planta de hoje (a final de 16/11, com as notas do cliente e os
padrões já aplicados), as peças recomendadas da biblioteca da Casa E (`POE642_CasaE/biblioteca-objetos`, do Drive:
`POE642-Casa-E-Objetos-e-Pisos-Claude-Code.zip`), a referência das vistas 3D da Casa E (sala e gourmet; cozinha) e o
que muda. As peças marcadas "a gerar" não estão na biblioteca: vão ao Higgsfield (4 variantes) só com o OK.

  python3 proposta_mobiliario_terreo_casae_1611.py [--ref3d <pasta das vistas 3D da Casa E>]
Saída: `POE642_CasaE/renders/POE642_CasaE_PH_Terreo_1611_mobiliario_<n>.jpg`.
"""
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

import proposta_biblioteca_casad_1511 as PD

AQUI = Path(__file__).resolve().parent
CASA_E = AQUI.parents[1] / "POE642_CasaE"
BIB_E = CASA_E / "biblioteca-objetos"
BIB_A = AQUI.parent / "biblioteca-objetos"
R = CASA_E / "renders"
VERDE = (62, 128, 86)
FINAL = R / "POE642_CasaE_PH_Terreo_v1_final.png"

# cada ambiente: título, recortes da final de hoje (px), peças [(caminho na biblioteca da E, ou "A:" na da Casa A, ou
# "gerar:" para a que falta; legenda; recomendada)], o que muda
R_ = True
AMBIENTES = [
 ("Living (o estar do sofá e o estar da janela)", [(1580, 1170, 2230, 1590)],
  [("02-terreo/living/sofa-curvo-living-e", "sofá curvo de linho (E)", R_),
   ("02-terreo/living/poltrona-creme-madeira-render", "poltrona creme, aro de madeira (as 7)", R_),
   ("02-terreo/living/mesa-centro-gota-e", "mesa de centro gota", R_),
   ("02-terreo/living/mesa-lateral-metal-madeira", "mesa lateral", R_),
   ("02-terreo/varanda/mesa-redonda-varanda-e", "mesa redonda em nogueira (estar da janela)", R_),
   ("gerar:tapete redondo azul-marinho, como no 3D", "tapete redondo azul (a gerar)", R_),
   ("02-terreo/living/tapete-estar-trama-clara", "tapete claro (alternativa)", False),
   ("02-terreo/living/poltrona-madeira-living-e", "poltrona de madeira (alternativa)", False),
   ("02-terreo/hall-de-entrada/vaso-folhagem-a", "vaso com folhagem", R_)],
  ["Como no 3D da Casa E: o sofá curvo de linho no lugar do branco de hoje, as poltronas creme com o aro de madeira "
   "(as 3 do estar e as 4 da janela), a mesa gota em nogueira e a mesa lateral junto ao sofá.",
   "O tapete redondo azul-marinho do 3D não está na biblioteca: vai ao Higgsfield (4 variantes) com o OK; a "
   "alternativa é o tapete claro da biblioteca, no círculo de hoje.",
   "No estar da janela, a mesa redonda em nogueira no círculo do PDF, as 4 poltronas viradas para ela; os 2 vasos "
   "trocados pela folhagem da E. A cortina C4 fica."]),
 ("Sala de jantar", [(1580, 900, 1880, 1200)],
  [("02-terreo/sala-de-jantar/mesa-jantar-retangular-e", "mesa retangular (E), em nogueira", R_),
   ("02-terreo/sala-de-jantar/cadeira-a", "cadeira estofada, quadro de madeira", R_),
   ("02-terreo/sala-de-jantar/cadeira-jantar-madeira-e", "cadeira de madeira (alternativa)", False)],
  ["A mesa retangular da E no retângulo do PDF, na nogueira das mesas da D (nota 23 do cliente), com o arranjo de "
   "centro de hoje.",
   "As 10 cadeiras do padrão das casas (estofadas, com o quadro de madeira) com o assento azul-marinho do 3D, "
   "alinhadas à mesa e 1/3 sob o tampo."]),
 ("Varanda", [(1150, 880, 1600, 1650)],
  [("02-terreo/varanda/mesa-redonda-varanda-e", "mesa redonda (E)", R_),
   ("02-terreo/varanda/cadeira-redonda-varanda-e", "cadeira redonda creme (E)", R_),
   ("02-terreo/varanda/cadeira-gourmet-creme-madeira", "cadeira creme e madeira (alternativa)", False),
   ("02-terreo/varanda/sofa-varanda-e", "sofá da varanda (E)", R_),
   ("02-terreo/varanda/poltrona-externa-b", "poltrona de corda", R_),
   ("02-terreo/varanda/mesa-lateral-externa", "mesa lateral externa", R_),
   ("02-terreo/varanda/vaso-folhagem-b", "vaso com folhagem", R_)],
  ["As 2 mesas redondas da E com 6 cadeiras redondas creme cada (as cadeiras claras do fundo do 3D), viradas para "
   "o centro, no giro das do PDF.",
   "O estar: o sofá da E no lugar do de hoje, as 2 poltronas de corda e a mesa lateral externa entre elas; a mesa de "
   "centro e o banco ficam nos retângulos do PDF, em madeira.",
   "O vaso de folhagem junto ao vidro do living."]),
 ("Área gourmet, lavabo gourmet e BH gourmet", [(960, 440, 1600, 830)],
  [("02-terreo/area-gourmet/banqueta-varanda-e", "banqueta (E)", R_),
   ("02-terreo/area-gourmet/cooktop-quatro-bocas", "cooktop 4 bocas", R_),
   ("02-terreo/area-gourmet/cuba-franke-misturador-unic", "cuba Franke e misturador", R_),
   ("02-terreo/area-gourmet/grelha-churrasqueira", "grelha da churrasqueira", R_),
   ("02-terreo/banho-gourmet/cuba-travertino-gourmet", "cuba de travertino (BH)", R_),
   ("02-terreo/banho-gourmet/bacia-escura-render", "bacia no marrom (BH e lavabo)", R_),
   ("02-terreo/banho-gourmet/chuveiro-quadrado", "chuveiro quadrado (BH)", R_),
   ("02-terreo/lavabo-gourmet/cuba-social-e", "cuba esculpida (lavabo)", R_),
   ("02-terreo/banho-gourmet/bacia-carrara", "bacia branca (alternativa)", False),
   ("02-terreo/lavabo-gourmet/cuba-quartzo", "cuba de quartzo (alternativa)", False)],
  ["Ilha: as 5 banquetas da E, com 40% sob o tampo e sem tracejado; o cooktop de 4 bocas da biblioteca.",
   "Bancada de trás: a grelha e a cuba Franke com o misturador da E (a geladeira e o armário liso ficam).",
   "BH gourmet: a cuba de travertino na bancada de travertino (nota 8), a bacia no marrom (padrão do BH gourmet e do "
   "lavabo) e o chuveiro quadrado em planta, dentro do box.",
   "Lavabo gourmet: a cuba esculpida da E na bancada e a bacia no marrom."]),
 ("Cozinha", [(1570, 460, 1960, 830)],
  [("02-terreo/cozinha/cooktop-quatro-bocas", "cooktop 4 bocas", R_),
   ("02-terreo/cozinha/cuba-franke-dupla-vista-superior", "cuba Franke dupla", R_),
   ("02-terreo/cozinha/misturador-deca-2280", "misturador Deca 2280", R_),
   ("02-terreo/area-gourmet/banqueta-varanda-e", "banqueta conhaque (E)", R_),
   ("A:02-terreo/cozinha/geladeira-inox", "geladeira inox G2 (fica)", R_),
   ("02-terreo/cozinha/ilha-clara-cozinha-e", "ilha branca do 3D (alternativa)", False)],
  ["Na ilha, o cooktop de 4 bocas e as 4 banquetas conhaque da E (as do 3D), 40% sob o tampo.",
   "Na pia, a cuba Franke dupla com o misturador Deca; as 2 geladeiras inox ficam.",
   "O 3D da E tem a ilha branca e os armários cinza; hoje a ilha está no Dekton Danae (padrão das casas A e D) e os "
   "armários na cor padrão: pergunta 3."]),
 ("Área de serviço, DCE e WC DCE", [(1940, 420, 2500, 715)],
  [("02-terreo/area-de-servico/tanque-duplo-inox", "tanque duplo inox", R_),
   ("02-terreo/area-de-servico/torneira-deca-link-1167", "torneira Deca Link", R_),
   ("02-terreo/area-de-servico/lavadora-tampa-superior", "lavadora e secadora", R_),
   ("02-terreo/quarto-dce-1/cama-solteiro-e", "cama de solteiro (E)", R_),
   ("02-terreo/banho-dce-1/bacia-monte-carlo-sem-valvula", "bacia Monte Carlo", R_),
   ("02-terreo/banho-dce-1/chuveiro-acqua-plus", "chuveiro Acqua Plus", R_),
   ("02-terreo/banho-dce-1/cuba-dce-gabriel-e", "cuba no São Gabriel (E)", R_),
   ("02-terreo/banho-dce-1/cuba-servico-sao-gabriel", "cuba de serviço (alternativa)", False)],
  ["Serviço: o tanque duplo inox com a torneira Deca Link na bancada; a lavadora e a secadora nos 2 vãos do PDF.",
   "DCE: a cama de solteiro de linho da E; o criado e o armário lisos ficam; a cortina C4.",
   "WC DCE: a bacia Monte Carlo (padrão dos banhos de serviço), o chuveiro Acqua Plus em planta no box e a cuba "
   "no São Gabriel da E; o piso cinza dos banhos da D fica, sem as manchas claras de hoje."]),
 ("Escritório, lavabo e hall de entrada", [(2215, 900, 2495, 1600)],
  [("02-terreo/escritorio/mesa-escritorio-e", "mesa do escritório (E)", R_),
   ("02-terreo/escritorio/cadeira-escritorio", "cadeira de escritório", R_),
   ("02-terreo/escritorio/poltrona-intima-e", "poltrona arredondada (E)", R_),
   ("02-terreo/lavabo/cuba-social-e", "cuba esculpida (lavabo)", R_),
   ("02-terreo/lavabo/bacia-escura-render", "bacia no marrom", R_),
   ("02-terreo/hall-de-entrada/aparador-freijo", "aparador em freijó", R_),
   ("02-terreo/hall-de-entrada/vaso-folhagem-a", "vaso com folhagem", R_)],
  ["Escritório: a mesa da E no retângulo do PDF, as 2 cadeiras de couro 1/3 sob o tampo, o encosto para fora; a "
   "chaise de hoje dá lugar à poltrona arredondada da E, com a mesinha lateral.",
   "Lavabo: a cuba esculpida da E na bancada e a bacia no marrom.",
   "Hall: o aparador em freijó no retângulo do PDF e o vaso de folhagem da E (o triângulo da entrada fica)."]),
 ("Adega, despensa, louceiro, elevador e garagem", [(1940, 700, 2490, 830), (2480, 470, 3060, 920)],
  [("02-terreo/adega/armario-adega-e", "adega com garrafas (E)", R_),
   ("02-terreo/despensa/armario-despensa-fechado", "armário liso (despensa e louceiro)", R_),
   ("02-terreo/despensa/modulo-estante-aberta", "estante aberta (alternativa)", False),
   ("02-terreo/elevador/cabine-elevador-e", "cabine do elevador (E)", R_),
   ("02-terreo/garagem/sedan-prata", "sedã prata (os 3)", R_),
   ("02-terreo/garagem/sedan-chumbo", "sedã chumbo (alternativa)", False)],
  ["Adega: o módulo de garrafas da E nas prateleiras do U do PDF, o rótulo fora delas.",
   "Despensa e louceiro: os armários lisos, na cor sólida (nota 16; ficam como hoje, na peça da E).",
   "Elevador: a cabine em aço da E. Garagem: os 3 sedãs prata da E, alinhados e iguais."]),
 ("Deck, piscina e jardim interno", [(640, 900, 1160, 1660), (1870, 1040, 2225, 1130)],
  [("02-terreo/deck-de-pedra/espreguicadeira-madeira-render", "espreguiçadeira de madeira", R_),
   ("02-terreo/jardim-interno/touceira-costela-de-adao", "costela-de-adão", R_),
   ("02-terreo/jardim-interno/palmeira-leque", "palmeira-leque", R_),
   ("02-terreo/jardim-interno/touceira-samambaia", "samambaia (alternativa)", False)],
  ["Deck: 2 espreguiçadeiras de madeira (o padrão das casas A e B) no Bege Bahia, entre o spa e a escada; hoje o deck "
   "está vazio: pergunta 4.",
   "Jardim interno: as 2 plantas de hoje trocadas pela costela-de-adão e pela palmeira-leque do 3D, pequenas, sobre a "
   "grama (o padrão do jardim de 4,79 m² da A)."]),
]

PERGUNTAS = [
 "1. Living: o tapete redondo azul-marinho do 3D (gerado no Higgsfield, 4 variantes) ou o tapete claro da biblioteca?",
 "2. Jantar: as cadeiras com o assento azul-marinho do 3D, ou em creme como na biblioteca?",
 "3. Cozinha: como no 3D (ilha branca e armários cinza) ou como hoje (Dekton Danae e armário na cor padrão)?",
 "4. Deck: entram as 2 espreguiçadeiras de madeira, ou o deck fica vazio?",
]


def peca(rel, lado=150):
    if rel.startswith("gerar:"):
        im = Image.new("RGB", (lado, lado), (246, 236, 230))
        d = ImageDraw.Draw(im)
        for j, l in enumerate(PD.linhas(rel[6:], PD.F_C, lado - 16)[:4]):
            d.text((8, 40 + j * 20), l, font=PD.F_C, fill=(150, 60, 60))
        return im
    base = BIB_A if rel.startswith("A:") else BIB_E
    PD.BIB = base
    return PD.peca(rel[2:] if rel.startswith("A:") else rel, lado)


def secao(final, n, titulo, recortes, pecas, muda):
    esq = []
    alt_max = 760 if len(recortes) == 1 else 470
    for x0, y0, x1, y1 in recortes:
        c = final[y0:y1, x0:x1]
        k = min(1150 / c.shape[1], alt_max / c.shape[0], 2.2)
        esq.append(Image.fromarray(cv2.cvtColor(cv2.resize(c, None, fx=k, fy=k, interpolation=cv2.INTER_AREA if k < 1
                                                           else cv2.INTER_CUBIC), cv2.COLOR_BGR2RGB)))
    h_esq = sum(i.height for i in esq) + 14 * (len(esq) - 1) + 34
    xr, lr = 1230, PD.W - 1230 - 40
    txt = [PD.linhas("• " + m, PD.F_B, lr) for m in muda]
    y = 34 + ((len(pecas) + 5) // 6) * 196 + 40 + sum(len(t) * 31 + 8 for t in txt)
    H = max(h_esq, y) + 110
    img = Image.new("RGB", (PD.W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, PD.W, 64], fill=(244, 243, 239))
    d.text((40, 12), f"{n}. {titulo}", font=PD.F_T, fill=PD.TINTA)
    yy = 90
    d.text((40, yy - 4), "Hoje (a final de 16/11)", font=PD.F_S, fill=PD.SUAVE)
    yy += 30
    for im in esq:
        img.paste(im, (40, yy))
        d.rectangle([40, yy, 40 + im.width, yy + im.height], outline=PD.LINHA, width=2)
        yy += im.height + 14
    y = 90
    d.text((xr, y - 4), "Peças da biblioteca da Casa E (em verde, as recomendadas)", font=PD.F_S, fill=PD.SUAVE)
    y += 30
    for i, (rel, leg, rec) in enumerate(pecas):
        cx, cy = xr + (i % 6) * 222, y + (i // 6) * 196
        img.paste(peca(rel), (cx, cy))
        if rec:
            d.rectangle([cx - 3, cy - 3, cx + 153, cy + 153], outline=VERDE, width=4)
            lt = d.textlength("recomendada", font=PD.F_C)
            d.rectangle([cx + 148 - lt - 10, cy + 2, cx + 148, cy + 23], fill=VERDE)
            d.text((cx + 148 - lt - 5, cy + 3), "recomendada", font=PD.F_C, fill=(255, 255, 255))
        else:
            d.rectangle([cx, cy, cx + 150, cy + 150], outline=PD.LINHA, width=1)
        for j, l in enumerate(PD.linhas(leg, PD.F_C, 210)[:2]):
            d.text((cx, cy + 156 + j * 19), l, font=PD.F_C, fill=PD.TINTA)
    y += ((len(pecas) + 5) // 6) * 196 + 6
    d.text((xr, y), "O que muda", font=PD.F_S, fill=PD.SUAVE)
    y += 36
    for t in txt:
        for l in t:
            d.text((xr, y), l, font=PD.F_B, fill=PD.TINTA)
            y += 31
        y += 8
    return img


def referencias(pasta):
    """A faixa com as duas vistas 3D da Casa E (do Drive, fora do git: `--ref3d <pasta>` com `sala_gourmet.png` e
    `cozinha.png`), a referência do mobiliário."""
    ims = []
    for k in ("sala_gourmet", "cozinha"):
        f = Path(pasta) / f"{k}.png" if pasta else None
        if f is not None and f.exists():
            im = Image.open(f).convert("RGB")
            ims.append(im.resize((round(im.width * 560 / im.height), 560), Image.LANCZOS))
    if not ims:
        return None
    W = PD.W
    out = Image.new("RGB", (W, 660), (255, 255, 255))
    d = ImageDraw.Draw(out)
    d.text((40, 16), "Referência: as vistas 3D da Casa E (sala e gourmet; cozinha)", font=PD.F_S, fill=PD.SUAVE)
    x = 40
    for im in ims:
        k = min(1.0, (W - 80 - 20 * (len(ims) - 1)) / len(ims) / im.width)
        im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
        out.paste(im, (x, 60))
        x += im.width + 20
    return out


def folhas(ref3d=None, por_folha=3):
    final = cv2.imread(str(FINAL))
    secs = [secao(final, i + 1, *s) for i, s in enumerate(AMBIENTES)]
    ref = referencias(ref3d)
    saidas = []
    for k in range(0, len(secs), por_folha):
        grupo = secs[k:k + por_folha]
        cab = Image.new("RGB", (PD.W, 120), (255, 255, 255))
        dc = ImageDraw.Draw(cab)
        dc.text((40, 26), "Casa E · Térreo · proposta do mobiliário (16/11), ambiente por ambiente, para o OK",
                font=PD.F_T, fill=PD.TINTA)
        dc.text((40, 76), "Nada aplicado ainda. As peças são da biblioteca da Casa E; o 3D da Casa E é a referência de "
                          "estilo e de cor.", font=PD.F_P, fill=PD.SUAVE)
        blocos = [cab] + ([ref] if (k == 0 and ref is not None) else []) + grupo
        if k + por_folha >= len(secs):
            perg = Image.new("RGB", (PD.W, 60 + 40 * len(PERGUNTAS)), (255, 255, 255))
            dp = ImageDraw.Draw(perg)
            dp.text((40, 10), "Para decidir", font=PD.F_S, fill=PD.SUAVE)
            for i, p in enumerate(PERGUNTAS):
                dp.text((40, 48 + i * 40), p, font=PD.F_B, fill=PD.TINTA)
            blocos.append(perg)
        H = sum(b.height + 24 for b in blocos)
        out = Image.new("RGB", (PD.W, H), (255, 255, 255))
        y = 0
        for b in blocos:
            out.paste(b, (0, y))
            y += b.height + 24
        f = R / f"POE642_CasaE_PH_Terreo_1611_mobiliario_{k // por_folha + 1}.jpg"
        out.save(f, quality=86)
        saidas.append(f)
        print(f.name, out.size)
    return saidas


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref3d", help="pasta com as vistas 3D da Casa E (sala_gourmet.png, cozinha.png)")
    folhas(ap.parse_args().ref3d)

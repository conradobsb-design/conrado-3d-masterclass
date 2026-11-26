"""Casa B Subsolo, 26/11: o levantamento no 12K B aplicado ("ok, pode aplicar os 5";
`../../POE642_CasaB/renders/POE642_CasaB_PH_Subsolo_2611_levantamento.jpg`).

1. **Vidros sem linha técnica** (a esquadria cromada, o contorno e os tampões brancos saem): as folhas no vidro claro
   dos boxes, sem contorno (`um_pav_casaa_2511e.folhas_vidro`, o padrão aprovado no WC e no box do banho master da
   Casa A), sobre a soleira de pedra do vão (a faixa ARQ_PAREDE do PDF) no travertino mais escuro:
   - a sauna: o L de vidro (o vertical junto à ducha, 961,0 a 964,0, e o de cima, até a parede da direita), a ponta de
     baixo na parede e a ponta da direita na parede (o tampão e a pontinha escura saem);
   - o BH sauna: a porta de vidro da parede de cima (1252,7 a 1315,4);
   - a academia: as duas folhas de correr do PDF para a garagem (1365,2 a 1368,2 de 446,3 a 525,1 e 1362,2 a 1365,2
     de 520,3 a 597,3), de parede a parede; a junta escura da esquadria de antes, do lado da madeira, coberta pela
     madeira de logo ao lado;
   - o box do BH serviço: o vidro de cima (na parede da circulação, sobre a soleira) e a folha da porta (1440,1 a
     1443,1, de 391,3 a 438,5), com o travertino refeito embaixo.
2. **Soleiras** no travertino mais escuro, nítidas, de batente a batente e sem contorno (`terreo_casaa_2511g`, a pedra
   a 84%): a circulação para a sauna (1144,3 a 1153,2), a circulação para o BH sauna (1233,9 a 1245,8), a porta do BH
   serviço (1439,8 a 1448,8) e a passagem do depósito (1511,5 a 1520,5).
3. **BH sauna, o nicho da parede da ducha** (ARQ_PAREDE 1148,5 a 1153,2 x 722,7 a 746,6): o travertino refeito no
   nicho (saem os pontinhos brancos e o retângulo preto); a canopla de metal da ducha fica.
4. **BH serviço, a parede de cima**: o traço preto (o revestimento do PDF, 328,1 a 328,7) vira parede e a faixa clara
   embaixo vira o travertino do banho, até a folha da porta.
5. **Academia, o móvel junto ao elevador** (ARQ_LAYOUT HUMANIZAÇÃO 1687,6 a 1723,5 x 531,7 a 651,1, chapado em salmão):
   o armário baixo no tom sólido dos armários das casas (`revisao_terreo_casac_1311.COZINHA`: a cor, a face um tom
   abaixo na borda, a sombra curta).

Final, prancha e 12K A e B (cada item pelo registro local).

  python3 subsolo_casab_2611.py [item ...]
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
import um_pav_casaa_2511c as C       # noqa: E402
import um_pav_casaa_2511d as DD      # noqa: E402
import um_pav_casaa_2511e as E       # noqa: E402

PLANTA = "B_Subsolo"
DZ = json.loads((EP.PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[PLANTA]
# o travertino novo desta planta: a mesma textura e o mesmo px/m da Casa A (59,7), o 12K na escala desta planta
D.DZ_S = DZ["s"]
PAREDE = (80.0, 80.0, 80.0)
SOLEIRA = dict(escurecer=0.84, contorno=1.0, larg=0.22)      # a pedra mais escura, sem contorno


def soleiras(img, s, origem, rets):
    return G.soleira_trav(img, s, origem, rets, q=SOLEIRA)


def pintar(img, s, origem, rets, cor=PAREDE):
    x0 = min(r[0] for r in rets) - 1
    y0 = min(r[1] for r in rets) - 1
    x1 = max(r[2] for r in rets) + 1
    y1 = max(r[3] for r in rets) + 1
    jan, reg = C._reg(img, (x0, y0, x1, y1), s, origem)
    reg = V.compor(reg, V.cob([V.ret(*r) for r in rets], jan, s, origem), np.float32(cor))
    return C._gravar(img, jan, reg)


def vidros(img, s, origem, caixa, folhas):
    jan, reg = C._reg(img, caixa, s, origem, folga=int(2 * s) + 2)
    reg = E.folhas_vidro(reg, jan, s, origem, folhas)
    return C._gravar(img, jan, reg)


# ----------------------------------------------------------------------------------------------------------------------
SAUNA = dict(soleiras=[(956.2, 606.3, 968.1, 704.8), (956.2, 597.3, 1062.5, 606.3)],
             parede=[(958.5, 704.6, 966.5, 708.0), (1060.4, 597.3, 1064.8, 606.4)],
             piso_ponta=(1056.0, 606.4, 1069.0, 612.5), piso_ponta_luz=[(1066.0, 613.0, 1100.0, 640.0)],
             vidro=[(961.0, 602.1, 964.0, 705.0), (961.0, 602.1, 1062.8, 605.1)])


def sauna(img, s, origem, q=SAUNA):
    img = soleiras(img, s, origem, q["soleiras"])
    img = pintar(img, s, origem, q["parede"])
    img = D.refazer_piso(img, s, origem, [V.ret(*q["piso_ponta"])],
                         ref_luz=[V.ret(*r) for r in q["piso_ponta_luz"]], pena=0.6)
    return vidros(img, s, origem, (950.0, 595.0, 1070.0, 712.0), [q["vidro"]])


BH_SAUNA = dict(soleira=(1252.7, 597.3, 1315.4, 606.3), vidro=(1252.7, 601.3, 1315.4, 604.4))


def porta_bh_sauna(img, s, origem, q=BH_SAUNA):
    img = soleiras(img, s, origem, [q["soleira"]])
    return vidros(img, s, origem, (1248.0, 594.0, 1320.0, 610.0), [[q["vidro"]]])


ACADEMIA = dict(soleira=(1359.2, 446.3, 1368.2, 597.3),
                folhas=[(1365.2, 446.3, 1368.2, 525.1), (1362.2, 520.3, 1365.2, 597.3)],
                junta=(1368.2, 517.5, 1371.9, 528.5))


def madeira_ao_lado(img, s, origem, r):
    """O trecho `r` coberto pela madeira de logo à direita (o mesmo trecho deslocado: as tábuas correm em x)."""
    x0, y0, x1, y1 = r
    w = x1 - x0
    jan, reg = C._reg(img, (x0 - 1, y0 - 1, x1 + w + 1, y1 + 1), s, origem, folga=int(2 * s) + 2)
    d = int(round(w * s))
    fonte = np.roll(reg, -d, axis=1)
    a = V.cob([V.ret(*r)], jan, s, origem)[..., None]
    return C._gravar(img, jan, reg * (1 - a) + fonte * a)


def vidro_academia(img, s, origem, q=ACADEMIA):
    img = madeira_ao_lado(img, s, origem, q["junta"])
    img = soleiras(img, s, origem, [q["soleira"]])
    return vidros(img, s, origem, (1355.0, 442.0, 1372.0, 601.0), [[r] for r in q["folhas"]])


BOX_BHS = dict(soleira=(1448.8, 382.4, 1511.5, 391.3), vidro_cima=(1448.8, 385.3, 1511.5, 388.4),
               piso_folha=(1438.6, 392.0, 1444.6, 438.6),
               piso_luz=[(1420.0, 395.0, 1436.0, 436.0), (1447.0, 395.0, 1478.0, 408.0), (1447.0, 425.0, 1478.0, 436.0)],
               folha=(1440.1, 391.3, 1443.1, 438.5))


def box_bh_servico(img, s, origem, q=BOX_BHS):
    img = soleiras(img, s, origem, [q["soleira"]])
    img = D.refazer_piso(img, s, origem, [V.ret(*q["piso_folha"])], ref_luz=[V.ret(*r) for r in q["piso_luz"]],
                         pena=0.6)
    return vidros(img, s, origem, (1436.0, 380.0, 1514.0, 441.0), [[q["vidro_cima"]], [q["folha"]]])


# ----------------------------------------------------------------------------------------------------------------------
SOLEIRAS = {"soleira_sauna": (1144.3, 613.7, 1153.2, 661.5), "soleira_bh_sauna": (1233.9, 612.2, 1245.8, 664.5),
            "soleira_bh_servico": (1439.8, 333.1, 1448.8, 374.9), "soleira_deposito": (1511.5, 330.1, 1520.5, 377.9)}


def _soleira(nome):
    return lambda img, s, origem: soleiras(img, s, origem, [SOLEIRAS[nome]])


NICHO = dict(zona=(1148.4, 722.6, 1153.4, 746.7), luz=[(1157.0, 742.0, 1200.0, 758.0), (1157.0, 712.0, 1200.0, 727.0)])


def nicho(img, s, origem, q=NICHO):
    return D.refazer_piso(img, s, origem, [V.ret(*q["zona"])], ref_luz=[V.ret(*r) for r in q["luz"]], pena=0.3)


TOPO_BHS = dict(parede=(1392.4, 327.6, 1439.8, 328.8), zona=(1392.6, 328.8, 1439.6, 336.0),
                luz=[(1395.0, 341.0, 1436.0, 362.0)])


def topo_bh_servico(img, s, origem, q=TOPO_BHS):
    img = pintar(img, s, origem, [q["parede"]])
    return D.refazer_piso(img, s, origem, [V.ret(*q["zona"])], ref_luz=[V.ret(*r) for r in q["luz"]], pena=0.4)


ARMARIO = dict(ret=(1687.6, 531.7, 1723.5, 651.1), cor=(129.0, 160.0, 189.0), face=0.86, borda=0.35, sombra=0.22)


def armario(img, s, origem, q=ARMARIO):
    jan, reg = C._reg(img, (1680.0, 524.0, 1730.0, 658.0), s, origem, folga=int(3 * s) + 2)
    H, W = reg.shape[:2]
    x0, y0, x1, y1 = q["ret"]
    a = V.cob([V.ret(*q["ret"])], jan, s, origem)
    e = q["borda"]
    dentro = V.cob([V.ret(x0 + e, y0 + e, x1 - e, y1 - e)], jan, s, origem)
    sb = cv2.GaussianBlur(a, (0, 0), max(0.8 * s, 0.6))
    Ms = np.float32([[1, 0, 0.6 * s], [0, 1, 0.7 * s]])
    sb = cv2.warpAffine(sb, Ms, (W, H)) * (1 - a)
    reg *= (1 - q["sombra"] * sb)[..., None]
    cor = np.float32(q["cor"])[None, None, :] * (1 - (1 - q["face"]) * np.clip(a - dentro, 0, 1))[..., None]
    reg = reg * (1 - a[..., None]) + cor * a[..., None]
    return C._gravar(img, jan, reg)


# ----------------------------------------------------------------------------------------------------------------------
ITENS = {"sauna": (948.0, 592.0, 1072.0, 714.0), "porta_bh_sauna": (1245.0, 592.0, 1322.0, 612.0),
         "vidro_academia": (1352.0, 438.0, 1376.0, 606.0), "box_bh_servico": (1432.0, 378.0, 1516.0, 442.0),
         "soleira_sauna": (1138.0, 606.0, 1160.0, 668.0), "soleira_bh_sauna": (1226.0, 606.0, 1252.0, 670.0),
         "soleira_bh_servico": (1434.0, 326.0, 1454.0, 380.0), "soleira_deposito": (1506.0, 324.0, 1526.0, 384.0),
         "nicho": (1142.0, 715.0, 1162.0, 754.0), "topo_bh_servico": (1388.0, 322.0, 1444.0, 342.0),
         "armario": (1682.0, 526.0, 1728.0, 656.0)}
FUNC = {"sauna": sauna, "porta_bh_sauna": porta_bh_sauna, "vidro_academia": vidro_academia,
        "box_bh_servico": box_bh_servico, "nicho": nicho, "topo_bh_servico": topo_bh_servico, "armario": armario}
FUNC.update({n: _soleira(n) for n in SOLEIRAS})


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

"""Os rótulos do Subsolo da Casa A: a especificação de cada um (texto, corpo, quebra, desvio e cor) e os pedidos sobre ela.

Os rótulos da final vêm gravados na imagem. Para mudá-los (e para as opções de letra e a ampliação) eles são achados na
imagem (`ampliacao_a3_casaa.ajustar_rotulos`, pelo desenho do `retoque_1pav_casae.rotulos_ambientes`), a especificação
recebe os pedidos e é gravada em `renders/POE642_CasaA_PH_Subsolo_rotulos_spec.json`; a partir dela, a final (Inter), a
opção manuscrita (`rotulos_manuscritos_casaa.py`) e a ampliação (`ampliacao_a3_casaa.py`) desenham os mesmos rótulos.

Pedidos do usuário (10/11/26), vendo as duas opções de letra:
- "PARA BANHO USE BH." (`abreviar`): BANHO SERV., BANHO FEM. e BANHO MASC. viram BH. SERV., BH. FEM. e BH. MASC. (como o
  "BH. GOURMET" da Casa D); o nome novo fica centrado onde o antigo estava, e o do banho de serviço, que ia em duas linhas
  ("BANHO" / "SERV."), volta a uma linha só, no mesmo corpo e no mesmo meio do bloco;
- "CENTRALIZE "SAUNA" DENTRO DO AMBIENTE" e, logo depois, "CENTRALIZE TODOS OS RÓTULOS" (`centralizar`): cada rótulo
  no centro do piso livre do seu ambiente (na sauna, entre os vidros, a parede da direita e a frente do banco).
"""

import json
import sys
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import ampliacao_a3_casaa as AM                # noqa: E402
import final3840_casaa as FA                    # noqa: E402
import retoque_1pav_casae as R1                 # noqa: E402

SPEC = FA.CASA / "renders" / "POE642_CasaA_PH_Subsolo_rotulos_spec.json"
PEDIDOS_ROT = {"abreviar": {"BANHO ": "BH. "}}


def texto_novo(nome):
    for a, b in PEDIDOS_ROT["abreviar"].items():
        if nome.startswith(a):
            return b + nome[len(a):]
    return nome


def r_do_ajuste(Q, aj):
    """O rótulo do PDF com o texto da especificação (`texto`): o nome trocado, a origem dele deslocada para o meio
    ficar onde estava (na largura da Inter), sem a quebra em linhas. Devolve (r, opc)."""
    from PIL import ImageFont
    from rodape_entrega import FONTES
    r = AM._r_do_nome(Q, aj["nome"], aj["pdf"])
    opc = dict(aj["opc"])
    texto = aj.get("texto")
    if not texto or texto == r[0]:
        return r, opc
    nome, linhas, centro, caixa = r
    t0, tam0, (ox, oy) = linhas[0]
    f = ImageFont.truetype(str(FONTES / f"Inter-{R1.ROTULOS.get('fonte_nome', R1.ROTULOS['fonte'])}.otf"), 400)

    def larg(s):
        return f.getlength(s) / 400 * tam0
    linhas = [(texto, tam0, (ox + (larg(t0) - larg(texto)) / 2, oy))] + list(linhas[1:])
    opc.pop("quebra", None)
    return (texto, linhas, centro, caixa), opc


def camadas(Q, spec, forma, pdf2img=None, s=1.0):
    """Os rótulos da especificação, como [(alfa, cor)], no quadro `forma` (pdf2img e s: a ampliação)."""
    out = []
    for aj in spec:
        r, opc = r_do_ajuste(Q, aj)
        dx, dy = aj["desvio"]
        out.append((AM._alfa_um(Q, r, opc, dx, dy, forma, pdf2img=pdf2img, esc=Q.W / 2000 * s), tuple(aj["cor"])))
    return out


def _centro(a):
    ys, xs = np.nonzero(a > 0.05)
    return (xs.min() + xs.max() + 1) / 2, (ys.min() + ys.max() + 1) / 2


def aplicar(Q, img):
    """Os pedidos sobre os rótulos da imagem (que ainda tem os rótulos de antes): acha os rótulos, tira os que mudam,
    desenha-os de novo pela especificação nova e grava a especificação."""
    forma = img.shape[:2]
    print("    rótulos da final, achados na imagem:")
    aj0 = AM.ajustar_rotulos(Q, img)
    spec = [dict(a) for a in aj0]
    for b in spec:
        t = texto_novo(b["nome"])
        if t != b["nome"]:
            b["texto"] = t
    spec, notas = centralizar(Q, spec, forma)
    print("    rótulos no centro do piso livre: " + "; ".join(notas))
    mud = [i for i, (a, b) in enumerate(zip(aj0, spec)) if a != b]
    antes = AM.rotulos_camadas(Q, [aj0[i] for i in mud], forma)
    limpa = AM.tirar(img, antes, AM.A3["cheio"], copiar=[k for k, i in enumerate(mud) if aj0[i]["casa"] < AM.A3["casa_px"]])
    out = AM.pintar(limpa, camadas(Q, [spec[i] for i in mud], forma))
    for i in mud:
        spec[i]["casa"] = 1.0                      # desenhados de novo, casam px a px com a imagem
    SPEC.write_text(json.dumps(spec, ensure_ascii=False, indent=1) + "\n")
    print("    rótulos: " + "; ".join(f"{aj0[i]['nome']} -> {spec[i].get('texto', spec[i]['nome'])}"
                                    + (f" (desvio {aj0[i]['desvio']} -> {spec[i]['desvio']})"
                                       if aj0[i]['desvio'] != spec[i]['desvio'] else "") for i in mud))
    return out


def ler_spec():
    return json.loads(SPEC.read_text())


# ----------------------------------------------------------------------------------------------------------------------
# "CENTRALIZE TODOS OS RÓTULOS" (usuário, 10/11/26, logo depois do pedido do SAUNA): a regra do Térreo da Casa A
# (`pedidos_terreo_casaa_2910.rotulos_centro_ta`) sobre a especificação. O recinto de cada rótulo é a repartição do PDF
# que o contém (`final3840_casab.ambientes_rotulos`, fechada também pelos vidros; o box do chuveiro fica de fora); os
# obstáculos são as peças do PDF (louças, aparelhos, bancadas, escadas, pilares), as prateleiras do depósito e o banco da
# sauna, com `obst_px` de folga; o alvo é o centro do piso livre do recinto e o rótulo vai para o ponto mais perto dele
# onde o bloco inteiro cabe com `folga_px` de folga. Onde o recinto vaza (a área passa de `vazou` x a do rótulo, ou fica
# abaixo de `minimo`), o rótulo fica onde está. O ELEVADOR vai ao centro da cabine (`regioes_pt`).
CENTRO = {"obstaculos": ("ARQ_LOUÇAS E METAIS", "ARQ_LAYOUT HUMANIZAÇÃO", "ARQ_BANCADAS", "ARQ_ESCADAS E RAMPAS",
                         "EST - Pilar", "EST_PILAR", "ARQ_ELEMENTOS FIXOS"),
          # o mínimo baixo: nos banhos com box, o piso seco é menos da metade da área do PDF (como no Térreo)
          "obst_px": 2, "folga_px": 3, "vazou": 1.6, "minimo": 0.3,
          "regioes_pt": {"ELEVADOR": FA.ELEVADOR["interno"]}}


def recintos(Q, spec, forma):
    """Os recintos (bool por rótulo), o piso livre e a razão área do recinto / área do rótulo."""
    import re
    import cv2
    import final3840_casab as F
    q = CENTRO
    pontos = [_centro(a) for a, _ in camadas(Q, spec, forma)]
    guardar = (F.vidros_box, F.duchas_box, Q.preencher)
    preencher = Q.preencher

    def preencher_com_divisoria(filtro, ss=4, fs=True):
        m = preencher(filtro, ss=ss, fs=fs)
        sonda = {"layer": "ARQ_PAREDE", "fill": (0.36, 0.36, 0.36), "type": "f"}
        return np.maximum(m, FA.ret_aa(Q, FA.PAREDES_A["divisoria"])) if filtro(sonda) else m
    try:
        F.vidros_box, F.duchas_box = FA.vidros_box_a, FA.duchas_box_a
        Q.preencher = preencher_com_divisoria
        amb = F.ambientes_rotulos(Q, pontos, todas=True)
    finally:
        F.vidros_box, F.duchas_box, Q.preencher = guardar
    obst = Q.preencher(lambda d: d.get("layer") in q["obstaculos"], ss=2, fs=True) > 0.05
    tr = np.zeros(obst.shape, np.uint8)
    for d in Q.desenhos:
        if d.get("layer") in q["obstaculos"] and d["type"] == "s":
            for c in Q.caminhos(d):
                cv2.polylines(tr, [np.int32(np.round(c))], False, 1, 2)
    obst |= tr.astype(bool)
    for r_, _ in FA.DEPOSITO["pecas"]:
        obst |= FA.ret_aa(Q, r_) > 0
    obst |= FA.ret_aa(Q, FA.SAUNA["pt"]) > 0
    k = 2 * q["obst_px"] + 1
    obst = cv2.dilate(obst.astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool)
    regs, razoes = [], []
    for i, b in enumerate(spec):
        r, _ = r_do_ajuste(Q, b)
        area = [float(m_.group(1).replace(",", ".")) for t in r[1] for m_ in [re.search(r"A:\s*([\d,]+)", t[0])] if m_]
        if b["nome"] in q["regioes_pt"]:
            reg = FA.ret_aa(Q, q["regioes_pt"][b["nome"]]) > 0.5
            razoes.append(None)
        else:
            reg = amb == i + 1
            razoes.append(reg.sum() / Q.px_m ** 2 / area[0] if area else None)
        regs.append(reg)
    return regs, obst, razoes


def centralizar(Q, spec, forma):
    import cv2
    q = CENTRO
    regs, obst, razoes = recintos(Q, spec, forma)
    cams = camadas(Q, spec, forma)
    f = q["folga_px"]
    novo, notas = [], []
    for b, reg, z, (a, _) in zip(spec, regs, razoes, cams):
        b = dict(b)
        ys, xs = np.nonzero(a > 0.05)
        x0, y0, x1, y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
        cx0, cy0 = (x0 + x1) / 2, (y0 + y1) / 2
        vazou = z is not None and not (q["minimo"] <= z <= q["vazou"])
        livre = reg & ~obst
        if vazou or not livre.any():
            notas.append(f"{b['nome']}: fica (o recinto {'vazou' if vazou else 'sem piso livre'}"
                         f"{f', {z:.2f} da área' if z else ''})")
            novo.append(b)
            continue
        w, h = x1 - x0, y1 - y0
        cabe = cv2.erode(livre.astype(np.uint8), np.ones((h + 2 * f, w + 2 * f), np.uint8)).astype(bool)
        yl, xl = np.nonzero(livre)
        gx, gy = xl.mean(), yl.mean()
        ys2, xs2 = np.nonzero(cabe)
        if not len(ys2):
            notas.append(f"{b['nome']}: fica (não cabe livre no recinto)")
            novo.append(b)
            continue
        j = int(np.argmin((xs2 - gx) ** 2 + (ys2 - gy) ** 2))
        tx, ty = float(xs2[j]), float(ys2[j])
        b["desvio"] = [round(b["desvio"][0] + tx - cx0), round(b["desvio"][1] + ty - cy0)]
        notas.append(f"{b['nome']}: ({cx0:.0f}, {cy0:.0f}) -> ({tx:.0f}, {ty:.0f}), centro do piso livre "
                     f"({gx:.0f}, {gy:.0f}){f', recinto {z:.2f} da área' if z else ''}")
        novo.append(b)
    return novo, notas

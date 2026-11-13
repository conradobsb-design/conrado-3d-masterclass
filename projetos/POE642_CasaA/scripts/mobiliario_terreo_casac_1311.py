"""O mobiliário do Térreo da Casa C (13/11), a 2ª leva da biblioteca.

Usuário: "E O MOBILIÁRIO DO TERREO DA CASA C?" e "PODE" (a leva dos quartos e das camas); a proposta
(`POE642_CasaC/renders/POE642_CasaC_PH_Terreo_1311_proposta_biblioteca_{1,2,3}.jpg`) aprovada com "Ok", as camas
escolhidas (`camas_escolhidas_casac_1311.py`: a manta de tricô caída nas de casal e na king, a peseira nas de solteiro,
o travesseiro extra) e "SAEM" (os armários altos da cozinha). As peças entram nos desenhos do PDF da Casa C (os índices
dos desenhos, px da final), como no Térreo da Casa B (`regras_terreo_casab_1311`):
- **Camas** (`CAMAS`): a king A na suíte master, a casal A nos quartos 1 e 3, a solteiro A no quarto 2 (2) e no quarto
  externo, com a roupa e o enfeite de cada quarto; os bancos ao pé das camas dos quartos (os do render) de volta por
  cima; na suíte master, o banco de pé de cama da Casa A.
- **Criados** (`CRIADOS`): os da Casa A no tom da madeira das bancadas (o redondo onde o PDF é redondo), com o abajur.
- **Poltronas e pufes** (`POLTRONAS`): a poltrona da suíte master e o pufe dela; a poltrona A e o pufe no quarto 1; a
  frente para o pufe; o vinílico refeito por baixo das de antes.
- **Cadeiras de escritório** (`CADEIRAS`): nas escrivaninhas da suíte master e dos quartos 1 e 3, 1/3 por baixo da
  mesa, a mesa de volta por cima.
- **Sala TV** (`SALA_TV`): o tapete, o sofá em L A (o giro de maior sobreposição com o L do PDF), a poltrona A e as mesas
  laterais; as duas mesas de centro de volta por cima; o vaso de folhagem A no vaso de hoje.
- **Estar** (`ESTAR`): à direita, o tapete no desenho do PDF com a trama do tapete redondo, o sofá curvo da Casa A, a
  mesa de centro seixo, as 2 poltronas oliva de cima, a poltrona creme e as 3 mesas de apoio escuras; à esquerda fica.
- **Jantar** (`JANTAR`): as 10 cadeiras oliva, viradas para a mesa, a mesa de volta por cima.
- **Varanda gourmet e sala de almoço** (`MESAS_REDONDAS`): a mesa redonda e as cadeiras dela da Casa A, viradas para a
  mesa (3 mesas, 18 cadeiras).
- **Escritório** (`ESCRITORIO`): a mesa A, a cadeira de escritório (1/3 sob a mesa) e as 2 cadeiras de visitante.
- **Cozinha** (`COZINHA`): os armários altos saem (o granito do piso por baixo).

  python3 mobiliario_terreo_casac_1311.py [--antes <png>] [--saida <png>]
"""

import argparse
import contextlib
import io
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import final3840_casaa as FA                     # noqa: E402
import final3840_casab as F                      # noqa: E402
import final3840_casac as C                      # noqa: E402
import biblioteca_subsolo_casaa_1211 as BS       # noqa: E402
import biblioteca_1pav_casaa_1211 as B1          # noqa: E402
import biblioteca_terreo_casaa_1211 as BT        # noqa: E402
import regras_terreo_casab_1311 as RT            # noqa: E402
import camas_casac_1311 as CM                    # noqa: E402
import manta_caida_casac_1311 as MC              # noqa: E402
import paisagismo_terreo_casab_1311 as PJ        # noqa: E402  (o `preencher`: a textura de uma amostra no tom do entorno)

CASA_C = AQUI.parents[1] / "POE642_CasaC"
R = CASA_C / "renders"
FINAL = R / "POE642_CasaC_PH_Terreo_final_rotulos.png"
RAIZ_GIT = AQUI.parents[2]
ANTES_COMMIT = "f06d49f"
PX_M = B1.PX_M
T02, P03 = "02-terreo", "03-primeiro-pavimento"

# as camas: (nome, índice do PDF, giro (0: cabeceira em cima; 90: à esquerda; -90: à direita), tipo, roupa, enfeite,
# modo, o lado da manta (o lado do PNG), os bancos do render de volta por cima)
CAMAS = [("suíte master", 80717, 0.0, "king", "off-white", "terracota clara", "manta", "esq", []),
         ("quarto 3", 90159, -90.0, "casal", "branco", "rosé antigo", "manta", "dir", [88634]),
         ("quarto 2, de cima", 90099, 90.0, "solteiro", "areia clara", "palha", "peseira", None, [88609]),
         ("quarto 2, de baixo", 90119, 90.0, "solteiro", "areia clara", "palha", "peseira", None, [88614]),
         ("quarto 1", 80296, -90.0, "casal", "areia", "sálvia", "manta", "esq", [88517]),
         ("quarto externo", 84669, -90.0, "solteiro", "branco", "cinza-claro", "peseira", None, [])]
BANCO_MASTER = {"pdf": 88649, "png": "suite-master/banco-pe-de-cama"}
# os criados: (índice, forma, giro) e o abajur (diâmetro px)
CRIADOS = [(88654, "ret", 0.0, 19.0), (88659, "ret", 0.0, 19.0), (88624, "ret", -90.0, 17.0), (88629, "ret", -90.0, 17.0),
           (88604, "ret", 90.0, 17.0), (88619, "ret", 90.0, 17.0), (88522, "redondo", 0.0, 19.0),
           (88909, "ret", -90.0, 17.0)]
# as poltronas: (nome, PNG da poltrona, índice, PNG do pufe, índice do pufe, a folga do vinílico refeito)
POLTRONAS = [("suíte master", "suite-master/poltrona", 80921, "suite-master/pufe", 88669),
             ("quarto 1", "sala-intima/poltrona-a", 80500, "suite-master/pufe", 88556)]
# as cadeiras de escritório: (nome, índices da cadeira, a borda da mesa (px) e o lado da mesa, a mesa (px, para voltar
# por cima))
CADEIRAS = [("suíte master", (80747, 80748), 1202.5, "dir", (1202, 575, 1231, 745)),
            ("quarto 3", (80543, 80544), 540.0, "baixo", (1314, 540, 1410, 570)),
            ("quarto 1", (80326, 80327), 2133.5, "dir", (2133, 560, 2162, 700))]
CADEIRA_ESC = {"png": "escritorio/cadeira-escritorio", "larg": 34.0, "sob": 1 / 3}
SALA_TV = {"tapete": 85737, "sofa": (85747, 85748, 85749, 85750, 85751, 85752), "poltrona": 90249,
           "mesas_laterais": (88789, 88810), "mesas_centro": (88750, 88717), "vaso_px": (1252, 846, 1310, 908),
           "trav_amostra_px": (1244, 700, 1306, 790)}
ESTAR = {"tapete": 53916, "tapete_amostra_px": (2140, 1420, 2185, 1465), "sofa": 85911, "mesa_centro": 91067, "oliva": (90391, 90320), "creme": 91075,
         "apoio": (91219, 91221, 91238), "vaso": 81802}
JANTAR = {"mesa": 92210, "larg": 30.0, "folga_px": 7,
          "cadeiras": [(84689, 90.0), (79024, 90.0), (78854, 90.0), (78684, 90.0),
                       (84859, -90.0), (79534, -90.0), (79364, -90.0), (79194, -90.0),
                       (79874, 0.0), (79704, 180.0)]}
MESAS_REDONDAS = [(85081, (80170, 80191, 80212, 80233, 80254, 80275)),
                  (85041, (80044, 80065, 80086, 80107, 80128, 80149)),
                  (88856, (82545, 82566, 82587, 82608, 82629, 82650))]
ESCRITORIO = {"mesa": 88841, "cadeira": (82215, 82216), "visitantes": [(82389, 82406, 82431, 82452),
                                                                       (82467, 82484, 82509, 82530)]}
# os armários altos da cozinha (px): a faixa clara junto à parede da esquerda e o bloco junto à parede da direita
COZINHA = {"armarios_px": [(2171, 457, 2206, 630), (2426, 495, 2466, 674)], "folga_px": 2,
           "granito_amostra_px": (2330, 560, 2410, 620)}
ANTES_DEPOIS = {"suite_master": (780, 560, 1240, 840), "quartos": (1170, 330, 1700, 590), "quarto_1": (1960, 330, 2175, 690),
                "quarto_externo": (2990, 690, 3200, 830), "sala_tv": (1240, 690, 1640, 930),
                "estar": (1640, 1290, 2400, 1620), "jantar": (2070, 920, 2240, 1210),
                "varanda_gourmet": (1180, 1250, 1600, 1420), "sala_almoco": (2470, 700, 2680, 900),
                "escritorio": (2600, 1020, 2790, 1180), "cozinha": (2150, 440, 2480, 690)}


def quadro():
    if "Q" not in _Q:
        with contextlib.redirect_stdout(io.StringIO()):
            C.contexto_c()
            _Q["Q"] = F.Quadro("Terreo")
    return _Q["Q"]


_Q = {}


# ----------------------------------------------------------------------------------------------------------------------
def ler(rel):
    leitor = B1 if rel.split("/")[0] in ("suite-master", "suite-1", "suite-2", "suite-3", "sala-intima", "banho-1",
                                          "banho-master", "closet-master") else BT
    return leitor.ler_png(rel)


def pousar(out, P, cx, cy, wt, ht, ang, sombra, par):
    o = BT.pousar(out.astype(np.float32), P, cx, cy, wt, ht, ang, BT.SOMBRAS[sombra] if sombra else [], PX_M, nao=par)
    return np.clip(np.round(o), 0, 255).astype(np.uint8)


def contorno(Q, ids):
    a, m = RT.mascara_pdf(Q, ids)
    return a, m


def encaixar(Q, P, m, giros=range(0, 360, 5), escalas=(0.9, 0.95, 1.0, 1.05)):
    """O giro e o tamanho (wt, ht) de P de maior sobreposição (IoU) com a silhueta `m` do PDF, no centro dela."""
    ys, xs = np.nonzero(m)
    cx, cy = float(xs.mean()), float(ys.mean())
    pts = np.column_stack([xs, ys]).astype(np.float32)
    (_, _), (w, h), _ = cv2.minAreaRect(pts)
    X0, Y0, X1, Y1 = xs.min() - 30, ys.min() - 30, xs.max() + 31, ys.max() + 31
    mm = m[Y0:Y1, X0:X1]
    Pb = P.copy()
    Pb[..., :3] = 255
    melhor = None
    for g in giros:
        for (a_, b_) in ((w, h), (h, w)):
            for e in escalas:
                wt, ht = a_ * e, b_ * e
                al = BT.pousar(np.zeros((Y1 - Y0, X1 - X0, 3), np.float32), Pb, cx - X0, cy - Y0, wt, ht, float(g), [],
                               PX_M)[..., 0] / 255 > 0.5
                iou = (al & mm).sum() / max((al | mm).sum(), 1)
                if melhor is None or iou > melhor[0]:
                    melhor = (iou, float(g), wt, ht)
    return cx, cy, melhor


def piso_vinilico(Q, out, buraco):
    """As réguas do vinílico no buraco (a luz em sigmas até 128: num buraco grande, a de 16 não chegava ao miolo e ele
    ficava preto) e no tom do vinílico em volta (só a madeira, fora os móveis claros)."""
    antes = out.copy()
    out = BS.quieto(RT.piso_reguas, Q, out, buraco, sigmas=(4, 8, 16, 32, 64, 128))
    im = antes.astype(np.int16)
    fonte = ((im.max(axis=2) - im.min(axis=2)) >= 40) & ~buraco
    return RT.tom_do_entorno(antes, out, buraco, fonte)


def piso_travertino(out, buraco, par, alcance=140):
    im = out.astype(np.int16)
    claro = (im.mean(axis=2) > 150) & ((im.max(axis=2) - im.min(axis=2)) < 45)
    fonte = claro & ~buraco & ~RT.dilatar(par, 3)
    feito = RT.piso_saltando(out, buraco, fonte, alcance=alcance, eixo="x", ancorar=True)
    return RT.tom_do_entorno(out, feito, buraco, fonte)


def frente(d):
    """O giro que põe a frente do PNG (embaixo) na direção `d` (dx, dy) da tela."""
    return BT.girar_pt(float(d[0]), float(d[1]))


# ----------------------------------------------------------------------------------------------------------------------
def camas(Q, out, antes, par):
    for nome, i, giro, tipo, roupa, enf, modo, lado, bancos in CAMAS:
        x0, y0, x1, y1 = RT.caixa_pdf(Q, i)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        comp, larg = (y1 - y0, x1 - x0) if giro in (0.0, 180.0) else (x1 - x0, y1 - y0)
        with contextlib.redirect_stdout(io.StringIO()):
            if modo == "manta":
                P0 = CM.cama(tipo, roupa, enf, "nada")
                P, p = MC.manta_caida(P0, enf, lado)
            else:
                P0 = CM.cama(tipo, roupa, enf, "peseira")
                P, p = P0, 0
        H0, W0 = P0.shape[:2]
        wt, ht = larg * (W0 + 2 * p) / W0, comp * (H0 + 2 * p) / H0
        out = pousar(out, P, cx, cy, wt, ht, giro, "movel" if not p else None, par)
        if p == 0:
            pass
        else:                                       # a sombra curta da cama (o colchão), como as outras peças
            pass
        for b in bancos:                            # os bancos do render de volta por cima (a manta caída passa sob eles)
            bx0, by0, bx1, by1 = RT.caixa_pdf(Q, b)
            X0, Y0, X1, Y1 = int(np.floor(bx0)) - 1, int(np.floor(by0)) - 1, int(np.ceil(bx1)) + 1, int(np.ceil(by1)) + 1
            out[Y0:Y1, X0:X1] = antes[Y0:Y1, X0:X1]
        print(f"    {nome}: a cama {tipo} A, roupa {roupa}, {'a manta de tricô caída' if modo == 'manta' else 'a peseira'} "
              f"{enf}, o travesseiro extra")
    # o banco de pé de cama da suíte master (a Casa A)
    x0, y0, x1, y1 = RT.caixa_pdf(Q, BANCO_MASTER["pdf"])
    P = ler(BANCO_MASTER["png"])
    out = pousar(out, P, (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, 0.0, "movel", par)
    print("    suíte master: o banco de pé de cama da Casa A")
    return out


def criados(Q, out, par):
    for i, forma, giro, D in CRIADOS:
        x0, y0, x1, y1 = RT.caixa_pdf(Q, i)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        if forma == "redondo":
            P = ler("suite-3/criado-redondo")
            d = ((x1 - x0) + (y1 - y0)) / 2
            out = pousar(out, P, cx, cy, d, d, 0.0, "movel", par)
        else:
            P, _, _ = B1.preparar("suite-master/criado-retangular-vista-superior", 1, 1, "tom_bancada")
            w, h = (x1 - x0, y1 - y0) if giro in (0.0, 180.0) else (y1 - y0, x1 - x0)
            out = pousar(out, P, cx, cy, w, h, giro, "movel", par)
        out = B1.abajur(out, cx, cy, D)
    print(f"    criados: {len(CRIADOS)} da Casa A no tom da madeira das bancadas (o redondo no quarto 1), com o abajur")
    return out


def poltronas(Q, out, par):
    for nome, png, ip, png_pufe, ipufe in POLTRONAS:
        _, mp = contorno(Q, [ip])
        _, mf = contorno(Q, [ipufe])
        buraco = (RT.dilatar(mp, 8) | RT.dilatar(mf, 8)) & ~par
        out = piso_vinilico(Q, out, buraco)
        ys, xs = np.nonzero(mp)
        pc = np.array([xs.mean(), ys.mean()])
        ys2, xs2 = np.nonzero(mf)
        fc = np.array([xs2.mean(), ys2.mean()])
        g = frente(fc - pc)
        pts = np.column_stack([xs, ys]).astype(np.float32)
        (_, _), (w, h), _ = cv2.minAreaRect(pts)
        lado = 0.92 * min(w, h)
        P = ler(png)
        out = pousar(out, P, pc[0], pc[1], lado * P.shape[1] / P.shape[0], lado, g, "movel", par)
        pts2 = np.column_stack([xs2, ys2]).astype(np.float32)
        (_, _), (w2, h2), _ = cv2.minAreaRect(pts2)
        Pf = ler(png_pufe)
        out = pousar(out, Pf, fc[0], fc[1], max(w2, h2), min(w2, h2), g, "movel", par)
        print(f"    {nome}: {Path(png).stem} e o pufe da Casa A, a frente para o pufe (giro {g:.0f}°); o vinílico refeito")
    return out


def cadeiras_escritorio(Q, out, par, q=CADEIRA_ESC):
    for nome, ids, borda, lado, mesa_px in CADEIRAS:
        _, m = contorno(Q, list(ids))
        ys, xs = np.nonzero(m)
        X0, Y0, X1, Y1 = xs.min() - 3, ys.min() - 3, xs.max() + 4, ys.max() + 4
        buraco = np.zeros(par.shape, bool)
        buraco[Y0:Y1, X0:X1] = True
        mx0, my0, mx1, my1 = mesa_px
        mesa = np.zeros(par.shape, bool)
        mesa[my0:my1, mx0:mx1] = True
        buraco &= ~mesa & ~par
        out = piso_vinilico(Q, out, buraco)
        fonte = out.copy()
        P = ler(q["png"])
        wt = q["larg"]
        ht = wt * P.shape[0] / P.shape[1]
        f = q["sob"]
        if lado == "dir":
            cx, cy, g = borda - ht / 2 + f * ht, (ys.min() + ys.max()) / 2, 90.0
        elif lado == "esq":
            cx, cy, g = borda + ht / 2 - f * ht, (ys.min() + ys.max()) / 2, -90.0
        else:
            cx, cy, g = (xs.min() + xs.max()) / 2, borda - ht / 2 + f * ht, 0.0
        out = pousar(out, P, cx, cy, wt, ht, g, "movel", par)
        ca = RT._alfa_peca(P, cx, cy, wt, ht, g, par.shape)
        a = mesa.astype(np.float32)
        Ya, Yb, Xa, Xb = my0 - 6, my1 + 6, mx0 - 6, mx1 + 6
        out[Ya:Yb, Xa:Xb] = RT.mesa_sobre(out[Ya:Yb, Xa:Xb], fonte[Ya:Yb, Xa:Xb], a[Ya:Yb, Xa:Xb], ca[Ya:Yb, Xa:Xb])
        print(f"    {nome}: a cadeira de escritório, 1/3 por baixo da escrivaninha")
    return out


def sala_tv(Q, out, antes, par, q=SALA_TV):
    _, tap = contorno(Q, [q["tapete"]])
    _, sofa = contorno(Q, list(q["sofa"]))
    _, pol = contorno(Q, [q["poltrona"]])
    _, ml = contorno(Q, list(q["mesas_laterais"]))
    velho = RT.dilatar(sofa | pol | ml | tap, 8) & ~par
    out = piso_travertino(out, velho, par)
    # o tapete, o sofá, a poltrona, as mesas laterais
    x0, y0, x1, y1 = RT.caixa_pdf(Q, q["tapete"])
    P = ler("sala-intima/tapete")
    out = pousar(out, P, (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, 0.0, "tapete", par)
    Ps = ler("sala-intima/sofa-l-a")
    cx, cy, (iou, g, wt, ht) = encaixar(Q, Ps, sofa, giros=(0, 90, 180, 270))
    melhor = (iou, g, wt, ht, False)
    Pm = np.ascontiguousarray(Ps[:, ::-1])
    cx2, cy2, (iou2, g2, wt2, ht2) = encaixar(Q, Pm, sofa, giros=(0, 90, 180, 270))
    if iou2 > iou:
        melhor = (iou2, g2, wt2, ht2, True)
    iou, g, wt, ht, esp = melhor
    # a medida: a caixa do L do PDF (o giro e o espelho do encaixe; o PNG tem outra proporção)
    ys, xs = np.nonzero(sofa)
    bw, bh = float(xs.max() + 1 - xs.min()), float(ys.max() + 1 - ys.min())
    cx, cy = (xs.min() + xs.max() + 1) / 2, (ys.min() + ys.max() + 1) / 2
    wt, ht = (bw, bh) if round(g) % 180 == 0 else (bh, bw)
    out = pousar(out, Pm if esp else Ps, cx, cy, wt, ht, g, "movel", par)
    print(f"    sala TV: o sofá em L A, {'espelhado, ' if esp else ''}giro {g:.0f}° ({iou * 100:.0f}% sobre o L do PDF)")
    out = recorte(Q, out, antes, list(q["mesas_centro"]))
    for i in q["mesas_laterais"]:
        x0, y0, x1, y1 = RT.caixa_pdf(Q, i)
        D = ((x1 - x0) + (y1 - y0)) / 2
        out = pousar(out, ler("sala-intima/mesa-lateral"), (x0 + x1) / 2, (y0 + y1) / 2, D, D, 0.0, "baixa", par)
    Pp = ler("sala-intima/poltrona-a")
    cx, cy, (iou, g, wt, ht) = encaixar(Q, Pp, pol)
    out = pousar(out, Pp, cx, cy, wt, ht, g, "movel", par)
    print(f"    sala TV: a poltrona A (giro {g:.0f}°, {iou * 100:.0f}%), as 2 mesas laterais, o tapete; as mesas de centro "
          "de volta por cima")
    # o vaso de folhagem A no vaso de hoje
    x0, y0, x1, y1 = q["vaso_px"]
    sub = out[y0 - 8:y1 + 8, x0 - 8:x1 + 8].astype(np.int16)
    folha = ((sub[..., 1] - sub[..., 2]) > 4) | (sub.mean(axis=2) < 150)
    folha = cv2.dilate(folha.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
    bur = np.zeros(par.shape, bool)
    bur[y0 - 8:y1 + 8, x0 - 8:x1 + 8] = folha
    bur &= ~RT.dilatar(par, 1)
    fx0, fy0, fx1, fy1 = q["trav_amostra_px"]
    out = PJ.preencher(out, bur, out[fy0:fy1, fx0:fx1].copy(), anel_px=6, nao=RT.dilatar(par, 1))
    D = min(x1 - x0, y1 - y0) - 4
    out = pousar(out, ler("sala-intima/vaso-folhagem-a"), (x0 + x1) / 2, (y0 + y1) / 2, D, D, 0.0, "movel", par)
    print("    sala TV: o vaso de folhagem A no lugar do de hoje")
    return out


def recorte(Q, out, antes, ids):
    """As peças `ids` do PDF de volta de `antes` pelo contorno do PDF, com a sombra curta (como
    `regras_terreo_casab_1311.recorte_de_volta`, sem gravar nada para o 12K)."""
    alvo = {id(Q.desenhos[i]) for i in ids}
    al = np.clip(Q.preencher(lambda d: id(d) in alvo, ss=4, fs=True).astype(np.float32), 0, 1)
    ys, xs = np.nonzero(al > 0.01)
    x0, y0, x1, y1 = xs.min() - 6, ys.min() - 6, xs.max() + 7, ys.max() + 7
    a = al[y0:y1, x0:x1]
    reg = out[y0:y1, x0:x1].astype(np.float32)
    for sb in BT.SOMBRAS["mesa"]:
        sh = cv2.GaussianBlur(a, (0, 0), max(0.3, sb["sig"] * PX_M))
        Ms = np.float32([[1, 0, sb["dx"] * PX_M], [0, 1, sb["dy"] * PX_M]])
        sh = cv2.warpAffine(sh, Ms, (sh.shape[1], sh.shape[0]), flags=cv2.INTER_LINEAR, borderValue=0)
        reg *= (1 - sb["forca"] * sh * (1 - a))[..., None]
    reg = reg * (1 - a[..., None]) + antes[y0:y1, x0:x1].astype(np.float32) * a[..., None]
    out[y0:y1, x0:x1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return out


def estar(Q, out, par, q=ESTAR):
    _, tap = contorno(Q, [q["tapete"]])
    ids = [q["sofa"], q["mesa_centro"], q["creme"], *q["oliva"], *q["apoio"]]
    _, pecas = contorno(Q, ids)
    _, vaso = contorno(Q, [q["vaso"]])
    velho = RT.dilatar(pecas | tap, 8) & ~par & ~RT.dilatar(vaso, 2)
    antes = out.copy()
    out = piso_travertino(out, velho, par, alcance=200)
    # o tapete no desenho do PDF, com a trama do tapete redondo (a amostra do miolo, ampliada para cobrir a caixa)
    ys, xs = np.nonzero(tap)
    X0, Y0, X1, Y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    # (a trama do tapete redondo da biblioteca, repetida, saía em "camuflagem"): a lã lisa do tapete de hoje, a amostra
    # limpa do miolo dele espelhada em vaivém, no tom médio dela
    ax0, ay0, ax1, ay1 = q["tapete_amostra_px"]
    am = antes[ay0:ay1, ax0:ax1].astype(np.float32)
    media = am.reshape(-1, 3).mean(axis=0)
    dp = float((am.mean(axis=2) - cv2.GaussianBlur(am.mean(axis=2), (0, 0), 3)).std())
    # (a amostra repetida em vaivém deixava losangos): a lã no tom médio dela, com o grão fino de ruído (o desvio do
    # grão da amostra), sem repetição
    rng = np.random.default_rng(1311)
    gr = cv2.GaussianBlur(rng.standard_normal((Y1 - Y0, X1 - X0)).astype(np.float32), (0, 0), 0.7)
    gr = gr / max(float(gr.std()), 1e-6) * dp
    rep = media[None, None] * (1 + gr[..., None] / max(float(media.mean()), 1))
    a, _ = contorno(Q, [q["tapete"]])
    al = a[Y0:Y1, X0:X1, None]
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    sh = cv2.GaussianBlur(a[Y0 - 4:Y1 + 4, X0 - 4:X1 + 4] if Y0 >= 4 else a[Y0:Y1, X0:X1], (0, 0), 1.5)
    reg = reg * (1 - al) + rep.astype(np.float32) * al
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    # o sofá curvo
    _, ms = contorno(Q, [q["sofa"]])
    Ps = ler("sala-de-estar/sofa-curvo-render-casa-a")
    cx, cy, (iou, g, wt, ht) = encaixar(Q, Ps, ms)
    out = pousar(out, Ps, cx, cy, wt, ht, g, "movel", par)
    print(f"    estar: o sofá curvo da Casa A (giro {g:.0f}°, {iou * 100:.0f}% sobre o do PDF)")
    # a mesa de centro seixo
    x0, y0, x1, y1 = RT.caixa_pdf(Q, q["mesa_centro"])
    Pm = ler("sala-de-estar/mesa-centro-seixo-render-v2")
    d = (x1 - x0)
    out = pousar(out, Pm, (x0 + x1) / 2, (y0 + y1) / 2, d, d * Pm.shape[0] / Pm.shape[1], 0.0, "baixa", par)
    # as poltronas oliva de cima, viradas para baixo (para a mesa)
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    for i in q["oliva"]:
        a0, b0, a1, b1 = RT.caixa_pdf(Q, i)
        Po = ler("sala-de-estar/poltrona-oliva-render-v2")
        hh = b1 - b0
        out = pousar(out, Po, (a0 + a1) / 2, (b0 + b1) / 2, hh * Po.shape[1] / Po.shape[0], hh, 0.0, "movel", par)
    # a poltrona creme, virada para a mesa
    _, mc = contorno(Q, [q["creme"]])
    ys, xs = np.nonzero(mc)
    pc = np.array([xs.mean(), ys.mean()])
    g = frente(np.array([mx, my]) - pc)
    a0, b0, a1, b1 = RT.caixa_pdf(Q, q["creme"])
    lado = 0.80 * max(a1 - a0, b1 - b0)
    Pc = ler("sala-de-estar/poltrona-creme-madeira-render")
    out = pousar(out, Pc, pc[0], pc[1], lado * Pc.shape[1] / Pc.shape[0], lado, g, "movel", par)
    for i in q["apoio"]:
        a0, b0, a1, b1 = RT.caixa_pdf(Q, i)
        D = ((a1 - a0) + (b1 - b0)) / 2
        out = pousar(out, ler("sala-de-estar/mesa-apoio-escura"), (a0 + a1) / 2, (b0 + b1) / 2, D, D, 0.0, "baixa", par)
    # o vaso de volta por cima
    out = recorte(Q, out, antes, [q["vaso"]])
    print(f"    estar: o tapete no desenho do PDF, a mesa de centro seixo, as 2 poltronas oliva, a poltrona creme (giro "
          f"{g:.0f}°) e as 3 mesas de apoio escuras")
    return out


def jantar(Q, out, par, q=JANTAR):
    a, mesa = RT.mascara_pdf(Q, [q["mesa"]])
    buraco = np.zeros(par.shape, bool)
    for i, _ in q["cadeiras"]:
        x0, y0, x1, y1 = RT.caixa_pdf(Q, i)
        f = q["folga_px"]
        buraco[int(np.floor(y0)) - f:int(np.ceil(y1)) + f, int(np.floor(x0)) - f:int(np.ceil(x1)) + f] = True
    buraco &= ~RT.dilatar(mesa, 1) & ~par
    out = piso_travertino(out, buraco, par, alcance=60)
    fonte_mesa = out.copy()
    ca = np.zeros(par.shape, np.float32)
    P = ler("sala-de-jantar/cadeira-jantar-oliva-render")
    for i, g in q["cadeiras"]:
        x0, y0, x1, y1 = RT.caixa_pdf(Q, i)
        wt = q["larg"]
        ht = wt * P.shape[0] / P.shape[1]
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        out = pousar(out, P, cx, cy, wt, ht, g, "movel", par)
        ca = np.maximum(ca, RT._alfa_peca(P, cx, cy, wt, ht, g, par.shape))
    ys, xs = np.nonzero(a > 0.01)
    X0, Y0, X1, Y1 = xs.min() - 8, ys.min() - 8, xs.max() + 9, ys.max() + 9
    out[Y0:Y1, X0:X1] = RT.mesa_sobre(out[Y0:Y1, X0:X1], fonte_mesa[Y0:Y1, X0:X1], a[Y0:Y1, X0:X1], ca[Y0:Y1, X0:X1])
    print(f"    jantar: as {len(q['cadeiras'])} cadeiras oliva da Casa A, viradas para a mesa (a mesa de volta por cima)")
    return out


def mesas_redondas(Q, out, par, qs=MESAS_REDONDAS):
    Pm = ler("varanda/mesa-redonda")
    Pc = ler("varanda/cadeira-mesa-redonda")
    n = 0
    for im, cads in qs:
        _, mm = contorno(Q, [im])
        _, mc = contorno(Q, list(cads))
        buraco = RT.dilatar(mm | mc, 7) & ~par
        out = piso_travertino(out, buraco, par, alcance=90)
        x0, y0, x1, y1 = RT.caixa_pdf(Q, im)
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        D = ((x1 - x0) + (y1 - y0)) / 2
        for i in cads:
            a0, b0, a1, b1 = RT.caixa_pdf(Q, i)
            cx, cy = (a0 + a1) / 2, (b0 + b1) / 2
            g = frente(np.array([mx - cx, my - cy]))
            ht = 0.95 * max(a1 - a0, b1 - b0)
            out = pousar(out, Pc, cx, cy, ht * Pc.shape[1] / Pc.shape[0], ht, g, "movel", par)
            n += 1
        out = pousar(out, Pm, mx, my, D, D, 0.0, "mesa", par)
    print(f"    varanda gourmet e sala de almoço: {len(qs)} mesas redondas e {n} cadeiras da Casa A, viradas para a mesa")
    return out


def escritorio(Q, out, par, q=ESCRITORIO):
    _, mm = contorno(Q, [q["mesa"]])
    _, mc = contorno(Q, list(q["cadeira"]))
    _, mv = contorno(Q, [i for v in q["visitantes"] for i in v])
    buraco = RT.dilatar(mm | mc | mv, 6) & ~par
    out = piso_vinilico(Q, out, buraco)
    x0, y0, x1, y1 = RT.caixa_pdf(Q, q["mesa"])
    Pm = ler("escritorio/mesa-a")
    fonte = None
    # a cadeira de escritório (a mesa à esquerda dela), 1/3 por baixo da mesa; a mesa por cima
    ys, xs = np.nonzero(mc)
    P = ler("escritorio/cadeira-escritorio")
    wt = 34.0
    ht = wt * P.shape[0] / P.shape[1]
    cx, cy, g = x1 + ht / 2 - ht / 3, (ys.min() + ys.max()) / 2, -90.0
    out = pousar(out, P, cx, cy, wt, ht, g, "movel", par)
    for v in q["visitantes"]:
        _, m = contorno(Q, list(v))
        ys, xs = np.nonzero(m)
        Pv = ler("escritorio/cadeira-visitante")
        hh = 0.95 * (xs.max() - xs.min())
        out = pousar(out, Pv, (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2, hh * Pv.shape[1] / Pv.shape[0], hh,
                     90.0, "movel", par)
    out = pousar(out, Pm, (x0 + x1) / 2, (y0 + y1) / 2, y1 - y0, x1 - x0, 90.0, "mesa", par)
    print("    escritório: a mesa A, a cadeira de escritório (1/3 sob a mesa) e as 2 cadeiras de visitante")
    return out


def cozinha(out, par, q=COZINHA):
    im = out.astype(np.int16)
    lum, croma = im.mean(axis=2), im.max(axis=2) - im.min(axis=2)
    granito = (croma >= 25) & (lum >= 50) & (lum <= 115)
    buraco = np.zeros(par.shape, bool)
    for x0, y0, x1, y1 in q["armarios_px"]:
        buraco[y0:y1, x0:x1] = True
    buraco &= ~RT.dilatar(par, 0)
    fx0, fy0, fx1, fy1 = q["granito_amostra_px"]
    out = PJ.preencher(out, buraco, out[fy0:fy1, fx0:fx1].copy(), anel_px=8, nao=~granito | RT.dilatar(par, 1))
    print(f"    cozinha: os {len(q['armarios_px'])} armários altos saem (o granito do piso por baixo)")
    return out


# (13/11, "CORRIJA O AZUL À ESQUERDA APÓS O VIDRO. NÃO HÁ AZUL DE ÁGUA DEPOIS DO VIDRO") na borda esquerda da piscina,
# entre o gramado e o vidro (a linha escura), o fio claro e a faixa azul viram o gramado (a mesma linha, logo antes)
PISCINA_C = {"x": (636, 652), "y": (1380, 1720), "azul": 30, "vidro_lum": 70}


def piscina(out, q=PISCINA_C):
    x0, x1 = q["x"]
    n = 0
    for y in range(*q["y"]):
        lin = out[y, x0:x1].astype(np.int16)
        lum = lin.mean(axis=1)
        az = np.nonzero((lin[:, 0] - lin[:, 2]) > q["azul"])[0]
        vid = np.nonzero(lum < q["vidro_lum"])[0]
        gr = (lin[:4, 1] > lin[:4, 2] + 5).all()                     # o gramado logo antes
        if not len(az) or not len(vid) or not gr:
            continue
        v = int(vid[vid > az.min()].min()) if (vid > az.min()).any() else None
        if v is None:
            continue
        a_ = 4                                                       # do fim do gramado até o vidro
        while a_ < v and (lin[a_, 1] > lin[a_, 2] + 5) and (lin[a_, 0] - lin[a_, 2]) <= q["azul"] and lum[a_] < 120:
            a_ += 1
        d = v - a_
        out[y, x0 + a_:x0 + v] = out[y, x0 + a_ - d:x0 + v - d]
        n += 1
    print(f"    piscina: a faixa azul entre o gramado e o vidro virou gramado ({n} linhas)")
    return out


# ----------------------------------------------------------------------------------------------------------------------
def aplicar(antes):
    Q = quadro()
    out = antes.copy()
    par = BS.quieto(FA.paredes_pdf, Q) > 0.3
    out = cozinha(out, par)
    out = piscina(out)
    out = camas(Q, out, antes, par)
    out = criados(Q, out, par)
    out = poltronas(Q, out, par)
    out = cadeiras_escritorio(Q, out, par)
    out = sala_tv(Q, out, antes, par)
    out = estar(Q, out, par)
    out = jantar(Q, out, par)
    out = mesas_redondas(Q, out, par)
    out = escritorio(Q, out, par)
    return out


def antes_depois(antes, depois):
    for nome, (x0, y0, x1, y1) in ANTES_DEPOIS.items():
        a, b = antes[y0:y1, x0:x1], depois[y0:y1, x0:x1]
        k = min(3.0, 1000 / max(a.shape[:2]))
        a = cv2.resize(a, None, fx=k, fy=k, interpolation=cv2.INTER_LANCZOS4)
        b = cv2.resize(b, None, fx=k, fy=k, interpolation=cv2.INTER_LANCZOS4)
        lado = a.shape[1] <= a.shape[0] * 1.6
        junto = np.hstack([a, np.full((a.shape[0], 16, 3), 255, np.uint8), b]) if lado else \
            np.vstack([a, np.full((16, a.shape[1], 3), 255, np.uint8), b])
        topo = np.full((44, junto.shape[1], 3), 255, np.uint8)
        cv2.putText(topo, "ANTES | DEPOIS" if lado else "ANTES (em cima) | DEPOIS (embaixo)", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (40, 40, 40), 2, cv2.LINE_AA)
        arq = R / f"POE642_CasaC_PH_Terreo_1311_mob_{nome}_antes_depois.jpg"
        cv2.imwrite(str(arq), np.vstack([topo, junto]), [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"    antes e depois: {', '.join(ANTES_DEPOIS)}")


def final_de(commit):
    dado = subprocess.run(["git", "show", f"{commit}:{FINAL.relative_to(RAIZ_GIT).as_posix()}"], cwd=RAIZ_GIT,
                          capture_output=True, check=True).stdout
    return cv2.imdecode(np.frombuffer(dado, np.uint8), cv2.IMREAD_COLOR)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--antes")
    ap.add_argument("--saida")
    a = ap.parse_args()
    antes = cv2.imread(a.antes) if a.antes else final_de(ANTES_COMMIT)
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

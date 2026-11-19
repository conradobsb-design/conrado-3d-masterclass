"""As esquadrias com o contorno fino preto em todas as plantas; os vidros e os boxes claros (19/11).

Usuário: "faça uma conferência em todas as plantas e garanta que as esquadrias tenham contorno fino preto. já os vidros
e boxes, devem ser claros."

O padrão é o do Térreo da Casa B (`regras_terreo_casab_1311.esquadrias`, "FAÇA APENAS O CONTORNO DA ESQUADRIA EM
PRETO"): o traço de 0,5 px no cinza quase preto (34, 34, 36), só o contorno, com o vidro claro por dentro. Aqui ele vale
para as 12 plantas, pelas peças do PDF de cada uma:
- as esquadrias: as peças brancas finas da ARQ_PAREDE (até `esp_max_pt` de espessura: os vidros, as folhas e os
  caixilhos das janelas e das portas de vidro), agrupadas por vizinhança; o grupo entra se uma das pontas encosta na
  parede do PDF (o vão de uma parede: fica de fora o que não é esquadria, como guarda-corpos soltos e bordas);
- o contorno de cada peça (o retângulo dela) é pintado onde a final mostra o vidro, o alumínio ou o fio cinza claro
  (neutros claros), fora a parede; a madeira das portas, o bronze dos brises e os pisos coloridos não mudam;
- ficam de fora: os vãos das portas dos quartos (o padrão de 14/11, a madeira por fora e o vidro claro com o fio cinza,
  `esquadrias_quartos.vaos_pdf`), as folhas de vidro das varandas da Casa B (`pedidos_terreo_casab_1211.FOLHAS_TB`), a
  água das piscinas e o que já está preto;
- os boxes ficam no vidro claro (estão na camada das louças, não entram) e os vidros não escurecem (só o contorno).
No 12K A e B de cada planta, o mesmo contorno nítido, na escala dele (`doze_k.json` refinado por ECC, como em
`piscinas_sobrias_1911.registro_12k`), onde a final o aceitou.

  python3 esquadrias_pretas_1911.py --auditar           # a conta por planta, sem gravar
  python3 esquadrias_pretas_1911.py --antes_depois A_Terreo
  python3 esquadrias_pretas_1911.py [planta ...]        # grava finais e 12K
"""
import argparse
import contextlib
import io
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
AQUI = Path(__file__).resolve().parent
PROJ = AQUI.parents[1]
sys.path.insert(0, str(AQUI))

ANTES = "247b659"          # o último commit antes desta rodada
R = "renders"
PLANTAS = {
    "A_Subsolo": ["POE642_CasaA/renders/POE642_CasaA_PH_Subsolo_final_rotulos.png",
                  "POE642_CasaA/renders/POE642_CasaA_PH_Subsolo_final_rotulos_manuscrita.png"],
    "A_Terreo": ["POE642_CasaA/renders/POE642_CasaA_PH_Terreo_final_rotulos.png"],
    "A_1Pavimento": ["POE642_CasaA/renders/POE642_CasaA_PH_1Pavimento_v7_final_rotulos.png"],
    "B_Subsolo": ["POE642_CasaB/renders/POE642_CasaB_PH_Subsolo_final_rotulos.png"],
    "B_Terreo": ["POE642_CasaB/renders/POE642_CasaB_PH_Terreo_final_rotulos.png"],
    "C_Subsolo": ["POE642_CasaC/renders/POE642_CasaC_PH_Subsolo_final_rotulos.png"],
    "C_Terreo": ["POE642_CasaC/renders/POE642_CasaC_PH_Terreo_final_rotulos.png"],
    "D_Subsolo": ["POE642_CasaD/renders/POE642_CasaD_PH_Subsolo_final_rotulos.png",
                  "POE642_CasaD/renders/POE642_CasaD_PH_Subsolo_final_rotulos_B.png"],
    "D_Terreo": ["POE642_CasaD/renders/POE642_CasaD_PH_Terreo_final_rotulos.png",
                 "POE642_CasaD/renders/POE642_CasaD_PH_Terreo_final_rotulos_B.png"],
    "E_Subsolo": ["POE642_CasaE/renders/POE642_CasaE_PH_Subsolo_v1_final.png"],
    "E_Terreo": ["POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_final.png"],
    "E_1Pavimento": ["POE642_CasaE/renders/POE642_CasaE_PH_1Pavimento_v1_final.png"],
}
Q_ = {"perfil": (34, 34, 36), "traco_px": 0.5, "ss": 8, "forca": 1.6, "esp_max_pt": 3.4, "comp_min_pt": 8.0,
      "junta_px": 2.0, "ponta_px": 4, "parede_min": 0.25, "croma_max": 20, "lum_min": 100, "agua_px": 8,
      "quarto_folga_px": 4, "grupo_min_px": 12, "caixas_claras": False}
# por planta: as zonas a deixar de fora (px da final) e o bronze aceito (a Casa E, Subsolo: as esquadrias no bronze de
# 18/11, com o contorno bronze escuro; o contorno passa a preto, o bronze fica por dentro)
ELEV_A = (2238, 1112, 2300, 1215)                     # o elevador da Casa A (mesmo lugar nos 3 pavimentos)
EXTRA = {
    "A_Subsolo": {"fora": [ELEV_A]},
    # o elevador, as linhas da bancada da churrasqueira (sem desenho na final) e o box do banho varanda
    "A_Terreo": {"fora": [ELEV_A, (1925, 1265, 2010, 1300), (1598, 1535, 1665, 1560)]},
    # o elevador, o vão com o X junto à escada e as portas das suítes no padrão (bronze por fora, vidro claro por
    # dentro: `revisao_casaa_2910.VAOS_SUITES_TA`, em pt do PDF)
    "A_1Pavimento": {"fora": [ELEV_A, (2240, 370, 2340, 430)],
                     "fora_pt": [(1385, 557, 1410, 788), (1385, 1177, 1410, 1370), (1147, 1395, 1172, 1773),
                                 (2286, 1492, 2312, 1694)]},
    "B_Subsolo": {"fora": [(1785, 630, 1835, 700),                          # o elevador
                           (1225, 605, 1300, 622),                          # a folha de madeira da porta do BH sauna
                           (1445, 380, 1515, 394)]},                        # o box do BH serviço
    # o elevador e os boxes (a ducha em T junto à sauna e o box do vestiário)
    "D_Subsolo": {"fora": [(1420, 1225, 1490, 1340), (1195, 1655, 1265, 1685), (945, 1650, 1030, 1720)]},
    "D_Terreo": {"fora": [(1420, 1225, 1485, 1335), (2046, 1538, 2057, 1602), (2449, 1210, 2518, 1221),
                          (2368, 764, 2444, 775)]},                        # o elevador
    # o bronze das esquadrias (V 139) não é madeira; as portas do elevador ficam (a cabine da biblioteca)
    "E_Subsolo": {"madeira_vmin": 150, "fora": [(1935, 780, 2085, 835)]},
    "E_Terreo": {"fora": [(1940, 790, 2065, 840),                           # o elevador
                          (2386, 832, 2449, 841), (2293, 1210, 2362, 1220), (2390, 619, 2442, 629)]},  # folhas de madeira
    # as portas das suítes nas duas fachadas (o padrão de 14/11: ripado de nogueira por fora, vidro claro por dentro)
    "E_1Pavimento": {"fora": [(1390, 580, 1425, 1480), (2470, 580, 2590, 1160), (1940, 790, 2065, 840)]},
}
# as plantas que já estavam no padrão (o contorno preto fino de `regras_terreo_casab_1311.esquadrias`, com as exceções
# aprovadas pelo usuário): ficam como estão
JA_NO_PADRAO = ("B_Terreo", "C_Subsolo", "C_Terreo")


def quadro(planta):
    import vinilico_foto as VF
    c, pav = planta.split("_")
    with contextlib.redirect_stdout(io.StringIO()):
        return VF.quadro(c, pav)


def elementos(Q, q=Q_):
    """As peças brancas finas da ARQ_PAREDE, em px da final (x0, y0, x1, y1)."""
    els = []
    for d in Q.desenhos:
        if d.get("layer") != "ARQ_PAREDE" or "f" not in d["type"] or not d.get("fill") or min(d["fill"]) < 0.9:
            continue
        r = d["rect"]
        if max(r.width, r.height) < q["comp_min_pt"] or min(r.width, r.height) > q["esp_max_pt"]:
            continue
        a, b = Q.p2q(r.x0, r.y0), Q.p2q(r.x1, r.y1)
        els.append((min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])))
    return els


def grupos(els, j):
    n = len(els)
    pai = list(range(n))

    def raiz(i):
        while pai[i] != i:
            pai[i] = pai[pai[i]]
            i = pai[i]
        return i
    for i in range(n):
        a = els[i]
        for k in range(i + 1, n):
            b = els[k]
            if a[0] - j <= b[2] and b[0] - j <= a[2] and a[1] - j <= b[3] and b[1] - j <= a[3]:
                pai[raiz(i)] = raiz(k)
    g = {}
    for i in range(n):
        g.setdefault(raiz(i), []).append(els[i])
    return list(g.values())


def caixa(g):
    return min(e[0] for e in g), min(e[1] for e in g), max(e[2] for e in g), max(e[3] for e in g)


def paredes_pdf(Q):
    return Q.preencher(lambda d: d.get("layer") in ("ARQ_PAREDE", "EST_PILAR") and d.get("fill")
                       and max(d["fill"]) < 0.6, ss=2) > 0.3


def no_vao(g, par, q=Q_):
    """O grupo encosta na parede numa das pontas (no eixo dele)."""
    x0, y0, x1, y1 = caixa(g)
    H, W = par.shape
    p = q["ponta_px"]
    if x1 - x0 >= y1 - y0:
        ys = slice(max(int(y0) - 1, 0), min(int(np.ceil(y1)) + 1, H))
        a = par[ys, max(int(x0) - p, 0):max(int(x0), 1)]
        b = par[ys, min(int(np.ceil(x1)), W - 1):min(int(np.ceil(x1)) + p, W)]
    else:
        xs = slice(max(int(x0) - 1, 0), min(int(np.ceil(x1)) + 1, W))
        a = par[max(int(y0) - p, 0):max(int(y0), 1), xs]
        b = par[min(int(np.ceil(y1)), H - 1):min(int(np.ceil(y1)) + p, H), xs]
    fa = a.mean() if a.size else 0
    fb = b.mean() if b.size else 0
    return max(fa, fb) >= q["parede_min"]


def fora_zonas(planta, Q, q=Q_):
    """As caixas a deixar de fora: os vãos das portas dos quartos e as folhas das varandas da Casa B."""
    import esquadrias_quartos as EQ
    zs = []
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            for v in EQ.vaos_pdf(Q):
                zs.append(v["faixa"])
        except Exception as e:                                   # noqa: BLE001
            print("vaos_pdf:", e, file=sys.stderr)
    if planta == "B_Terreo":
        import pedidos_terreo_casab_1211 as PB2
        for (wx0, wy0, wx1, wy1), (gx0, gy0, gx1, gy1), _ in PB2.FOLHAS_TB["folhas"]:
            zs.append((min(wx0, gx0), min(wy0, gy0), max(wx1, gx1), max(wy1, gy1)))
    e = q["quarto_folga_px"]
    return [(x0 - e, y0 - e, x1 + e, y1 + e) for x0, y0, x1, y1 in zs]


def agua(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    m = ((hsv[..., 0] >= 70) & (hsv[..., 0] <= 125) & (hsv[..., 1] >= 25) & (hsv[..., 2] >= 60)).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    keep = np.zeros(n, bool)
    keep[1:] = st[1:, cv2.CC_STAT_AREA] >= 4000
    return keep[lab]


def dados(planta, img=None, q=Q_):
    """As esquadrias da planta: os grupos que entram, os de fora e as zonas de fora."""
    Q = quadro(planta)
    if img is None:
        img = cv2.imread(str(PROJ / PLANTAS[planta][0]))
    gs = grupos(elementos(Q, q), q["junta_px"])
    zonas = fora_zonas(planta, Q, q) + EXTRA.get(planta, {}).get("fora", [])
    for x0, y0, x1, y1 in EXTRA.get(planta, {}).get("fora_pt", []):
        a, b = Q.p2q(x0, y0), Q.p2q(x1, y1)
        zonas.append((min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])))
    ag = cv2.dilate(agua(img).astype(np.uint8), np.ones((2 * q["agua_px"] + 1,) * 2, np.uint8)).astype(bool)
    vmin = EXTRA.get(planta, {}).get("madeira_vmin", 50)
    ok, fora = [], []
    for g in gs:
        x0, y0, x1, y1 = caixa(g)
        cx, cy = int((x0 + x1) / 2), int((y0 + y1) / 2)
        if max(x1 - x0, y1 - y0) < q["grupo_min_px"]:
            fora.append(g)                              # os batentes nas pontas das paredes (pecinhas do marco)
        elif any(x0 < c + 0.5 and a - 0.5 < x1 and y0 < d + 0.5 and b - 0.5 < y1 for a, b, c, d in zonas):
            fora.append(g)
        elif ag[min(cy, ag.shape[0] - 1), min(cx, ag.shape[1] - 1)]:
            fora.append(g)
        elif madeira(img, g, vmin):
            fora.append(g)
        elif not visivel(img, g):
            cc = caixa_clara(img, g) if q.get("caixas_claras") else None
            if cc:
                ok.append(cc)                           # a janela pela moldura clara do render
            else:
                fora.append(g)
        elif miolo_parede(img, g):
            fora.append(g)                              # as pecinhas sobre a ponta da parede
        else:
            ok.append(g)
    return Q, ok, fora, zonas


def alfa(gs, forma, origem=(0.0, 0.0), escala=1.0, q=Q_):
    """O contorno de fora de cada esquadria (a união das peças do grupo), uma faixa de `traco_px` logo fora dela, em
    alfa 0..1 na grade `forma` (px da final * escala, a partir de origem): o vidro e os perfis ficam claros por dentro."""
    H, W = forma
    ss = 8 if escala <= 1.5 else 2
    M = np.zeros((H * ss, W * ss), np.uint8)
    B = np.zeros_like(M)
    k = max(1, int(round(q["traco_px"] * escala * ss)))
    ker = cv2.getStructuringElement(cv2.MORPH_RECT, (2 * k + 1, 2 * k + 1))
    for g in gs:
        x0, y0, x1, y1 = caixa(g)
        X0 = max(int(np.floor((x0 - origem[0]) * escala * ss)) - 3 * k, 0)
        Y0 = max(int(np.floor((y0 - origem[1]) * escala * ss)) - 3 * k, 0)
        X1 = min(int(np.ceil((x1 - origem[0]) * escala * ss)) + 3 * k, W * ss)
        Y1 = min(int(np.ceil((y1 - origem[1]) * escala * ss)) + 3 * k, H * ss)
        if X1 <= X0 or Y1 <= Y0:
            continue
        m = np.zeros((Y1 - Y0, X1 - X0), np.uint8)
        for e in g:
            a = (int(round((e[0] - origem[0]) * escala * ss)) - X0, int(round((e[1] - origem[1]) * escala * ss)) - Y0)
            b = (int(round((e[2] - origem[0]) * escala * ss)) - X0 - 1, int(round((e[3] - origem[1]) * escala * ss)) - Y0 - 1)
            cv2.rectangle(m, a, b, 255, -1)
        faixa = cv2.dilate(m, ker) & ~m
        B[Y0:Y1, X0:X1] |= faixa
        M[Y0:Y1, X0:X1] |= m
    B &= ~M
    return cv2.resize(B, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255


def aceita(img, planta, q=Q_):
    """Onde o preto pode entrar: fora da parede, da água e do que já é escuro."""
    im = img.astype(np.int16)
    croma = im.max(2) - im.min(2)
    parede = (np.abs(im - 80).max(2) <= 14) & (croma <= 12)
    if planta == "A_Terreo":
        parede |= (np.abs(im - 53).max(2) <= 12) & (croma <= 12)
    ag = cv2.dilate(agua(img).astype(np.uint8), np.ones((2 * q["agua_px"] + 1,) * 2, np.uint8)).astype(bool)
    return ~parede & ~ag


def visivel(img, g, dif_min=10.0):
    """A esquadria aparece na final: o miolo das peças difere do entorno (2 a 5 px fora); senão é só piso (uma linha do
    PDF sem desenho na imagem) e não ganha contorno."""
    x0, y0, x1, y1 = caixa(g)
    H, W = img.shape[:2]
    X0, Y0, X1, Y1 = max(int(x0) - 6, 0), max(int(y0) - 6, 0), min(int(np.ceil(x1)) + 6, W), min(int(np.ceil(y1)) + 6, H)
    m = np.zeros((Y1 - Y0, X1 - X0), np.uint8)
    for e in g:
        cv2.rectangle(m, (int(round(e[0])) - X0, int(round(e[1])) - Y0), (int(round(e[2])) - X0 - 1, int(round(e[3])) - Y0 - 1), 1, -1)
    fora = cv2.dilate(m, np.ones((11, 11), np.uint8)) & ~cv2.dilate(m, np.ones((5, 5), np.uint8))
    lab = cv2.cvtColor(img[Y0:Y1, X0:X1], cv2.COLOR_BGR2LAB).astype(np.float32)
    if m.sum() == 0 or fora.sum() == 0:
        return True
    d = np.abs(lab[m > 0].mean(0) - lab[fora > 0].mean(0))
    return float(d.max()) >= dif_min


def miolo_parede(img, g, frac=0.75):
    im = img.astype(np.int16)
    vals = []
    for x0, y0, x1, y1 in g:
        a, b = int(np.floor(x0)), int(np.floor(y0))
        c, d = max(int(np.ceil(x1)), a + 1), max(int(np.ceil(y1)), b + 1)
        vals.append(im[b:d, a:c].reshape(-1, 3))
    v = np.concatenate(vals)
    cr = v.max(1) - v.min(1)
    par = ((np.abs(v - 80).max(1) <= 14) | (np.abs(v - 53).max(1) <= 12)) & (cr <= 12)
    return len(v) > 0 and par.mean() >= frac


def caixa_clara(img, g, par_cinzas=(80, 53)):
    """Quando a final desenha a janela maior que a peça do PDF (a moldura clara do render em volta do vidro, e o miolo
    igual ao entorno), a caixa dessa moldura: o componente claro e neutro que contém a peça, entre as paredes, se for
    fino (até 22 px) e não muito mais comprido que a peça. Senão, None."""
    x0, y0, x1, y1 = caixa(g)
    H, W = img.shape[:2]
    m = 30
    X0, Y0, X1, Y1 = max(int(x0) - m, 0), max(int(y0) - m, 0), min(int(np.ceil(x1)) + m, W), min(int(np.ceil(y1)) + m, H)
    reg = img[Y0:Y1, X0:X1].astype(np.int16)
    cr = reg.max(2) - reg.min(2)
    claro = ((reg.mean(2) >= 150) & (cr <= 22)).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(claro, 4)
    cx, cy = int((x0 + x1) / 2) - X0, int((y0 + y1) / 2) - Y0
    ids = set(lab[max(cy - 1, 0):cy + 2, max(cx - 1, 0):cx + 2].ravel()) - {0}
    if not ids:
        return None
    i = max(ids, key=lambda k: st[k, cv2.CC_STAT_AREA])
    bx, by, bw, bh = st[i, :4]
    L = max(x1 - x0, y1 - y0)
    if min(bw, bh) > 22 or max(bw, bh) > 1.25 * L + 8 or max(bw, bh) < 0.8 * L:
        return None
    return [(X0 + bx, Y0 + by, X0 + bx + bw, Y0 + by + bh)]


def madeira(img, g, vmin=50):
    """O miolo das peças do grupo é madeira (as folhas das portas de giro e os brises de madeira): fica."""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    vals = []
    for x0, y0, x1, y1 in g:
        a, b = int(np.floor(x0)), int(np.floor(y0))
        c, d = max(int(np.ceil(x1)), a + 1), max(int(np.ceil(y1)), b + 1)
        vals.append(hsv[b:d, a:c].reshape(-1, 3))
    v = np.concatenate(vals)
    if not len(v):
        return False
    mad = ((v[:, 0] >= 4) & (v[:, 0] <= 28) & (v[:, 1] >= 70) & (v[:, 2] >= vmin)).mean()
    return mad >= 0.5


def pintar(img, a, q=Q_):
    a = np.clip(a * q["forca"], 0, 1)
    novo = img.astype(np.float32) * (1 - a[..., None]) + np.float32(q["perfil"]) * a[..., None]
    return np.clip(np.round(novo), 0, 255).astype(np.uint8)


def final_nova(planta, img, ok_g, q=Q_):
    a = alfa(ok_g, img.shape[:2], q=q)
    ac = aceita(img, planta, q)
    return pintar(img, a * ac, q), ac


def auditar(planta, img, ok_g):
    """A fração do contorno que já está escura (lum < 90) onde o preto pode entrar."""
    a = alfa(ok_g, img.shape[:2]) > 0.3
    ac = aceita(img, planta) | (img.astype(np.int16).mean(2) < 90)
    m = a & ac
    lum = img.astype(np.int16).mean(2)
    return int(m.sum()), float((lum[m] < 90).mean()) if m.sum() else 1.0


def git_img(rel, rev=ANTES):
    dado = subprocess.run(["git", "show", f"{rev}:projetos/{rel}"], cwd=PROJ, capture_output=True, check=True).stdout
    return cv2.imdecode(np.frombuffer(dado, np.uint8), cv2.IMREAD_COLOR)


def registro_12k(pr, cinza12, dz, box):
    import piscinas_sobrias_1911 as PS
    return PS.registro_12k(pr, cinza12, dz, box)


def doze_k(planta, antes, ok_g, ac, q=Q_):
    """O contorno nítido nos 12K A e B da planta (onde a final aceitou o preto)."""
    c, pav = planta.split("_")
    dz = json.loads((PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[planta]
    s = dz["s"]
    ent = PROJ / f"POE642_Casa{c}/entrega"
    xs = [e[0] for g in ok_g for e in g] + [e[2] for g in ok_g for e in g]
    ys = [e[1] for g in ok_g for e in g] + [e[3] for g in ok_g for e in g]
    box = (max(int(min(xs)) - 60, 0), max(int(min(ys)) - 60, 0), min(int(max(xs)) + 60, antes.shape[1]),
           min(int(max(ys)) + 60, antes.shape[0]))
    for op in "AB":
        f = ent / f"POE642_Casa{c}_PH_{pav}_12K_opcao_{op}.jpg"
        if not f.exists():
            print("   (sem)", f.name)
            continue
        pil = Image.open(f)
        dpi = pil.info.get("dpi", (743, 743))
        im = cv2.cvtColor(np.array(pil.convert("RGB")), cv2.COLOR_RGB2BGR)
        del pil
        mapa, cc = registro_12k(antes, cv2.cvtColor(im, cv2.COLOR_BGR2GRAY), dz, box)
        # o mapa é quase uma translação + escala: a origem e a escala dele
        X0, Y0 = mapa(0.0, 0.0)
        X1, _ = mapa(1000.0, 0.0)
        sx = (X1 - X0) / 1000.0
        Hh, Ww = im.shape[:2]
        for y in range(0, Hh, 1024):
            y1 = min(Hh, y + 1024)
            # a faixa do 12K em px da final
            fy0, fy1 = (y - Y0) / sx, (y1 - Y0) / sx
            sel = [g for g in ok_g if caixa(g)[3] >= fy0 - 2 and caixa(g)[1] <= fy1 + 2]
            if not sel:
                continue
            a = alfa(sel, (y1 - y, Ww), origem=(-X0 / sx, fy0), escala=sx, q=q)
            Fq = np.array([[sx, 0, X0], [0, sx, Y0 - y]], np.float64)
            okb = cv2.warpAffine(ac.astype(np.uint8) * 255, Fq, (Ww, y1 - y), flags=cv2.INTER_NEAREST,
                                 borderValue=0) > 127
            im[y:y1] = pintar(im[y:y1], a * okb, q)
        Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).save(f, quality=95, subsampling=0, dpi=dpi)
        print(f"   {f.name} registro {cc:.4f}")
        del im


def folha_12k(cinza, a0, b0, a1, b1, M, limiar=28.0):
    """A folha da janela no próprio 12K (19/11): no 12K a folha sai até 1 px (da final) menor que a peça do PDF, e o
    contorno pela peça ficava solto na parede, fora do vidro. Cada lado vem da borda prevista (a0, b0, a1, b1, px do
    12K): o perfil do lado de fora (M a M + 4 px além da borda) dá o nível de fora; andando para dentro, a borda é o
    primeiro px que se afasta desse nível mais que `limiar`. Sem borda achada em ±M, fica a prevista."""
    g = cv2.GaussianBlur(cinza.astype(np.float32), (0, 0), 0.7)
    lado = {}
    w, h = a1 - a0, b1 - b0
    ca, cb = int(a0 + 0.25 * w), int(a1 - 0.25 * w)
    ra, rb = int(b0 + 0.3 * h), int(b1 - 0.3 * h)
    for nome, e, passo in (("t", b0, -1), ("b", b1, +1), ("l", a0, -1), ("r", a1, +1)):
        if nome in "tb":
            perfil = lambda t: float(g[t, ca:cb].mean())
        else:
            perfil = lambda t: float(g[ra:rb, t].mean())
        fora = [int(round(e + passo * (M + k))) for k in range(4)]
        O = float(np.median([perfil(t) for t in fora]))
        achou = None
        for t in range(int(round(e + passo * M)), int(round(e - passo * M)) - passo, -passo):
            if abs(perfil(t) - O) > limiar:
                # t é o primeiro px da folha vindo de fora; a borda é o lado dele que dá para fora
                achou = float(t) if passo < 0 else float(t + 1)
                break
        lado[nome] = achou if achou is not None else e
    return lado["l"], lado["t"], lado["r"], lado["b"]


def doze_k_local(planta, antes, ok_g, ac, q=Q_, folga=45, na_folha=False):
    """O contorno no 12K A e B com o registro local de cada esquadria (a caixa dela mais `folga` px): o registro da planta
    inteira erra até 2 px da final em alguns trechos (19/11, a janela do banho 1 e a do lavabo)."""
    c, pav = planta.split("_")
    dz = json.loads((PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[planta]
    ent = PROJ / f"POE642_Casa{c}/entrega"
    for op in "AB":
        f = ent / f"POE642_Casa{c}_PH_{pav}_12K_opcao_{op}.jpg"
        pil = Image.open(f)
        dpi = pil.info.get("dpi", (743, 743))
        im = cv2.cvtColor(np.array(pil.convert("RGB")), cv2.COLOR_RGB2BGR)
        del pil
        cinza = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        for g in ok_g:
            x0, y0, x1, y1 = caixa(g)
            box = (max(int(x0) - folga, 0), max(int(y0) - folga, 0), min(int(np.ceil(x1)) + folga, antes.shape[1]),
                   min(int(np.ceil(y1)) + folga, antes.shape[0]))
            mapa, cc = registro_12k(antes, cinza, dz, box)
            X0, Y0 = mapa(0.0, 0.0)
            X1, _ = mapa(1000.0, 0.0)
            sx = (X1 - X0) / 1000.0
            # o encaixe fino pela própria janela: a final em volta dela (6 px), ampliada, procurada no 12K a até 6 px
            # da final do lugar previsto (o 12K às vezes desenha a janela um pouco deslocada)
            e = 6
            fa = cv2.cvtColor(antes[max(int(y0) - e, 0):int(np.ceil(y1)) + e, max(int(x0) - e, 0):int(np.ceil(x1)) + e],
                              cv2.COLOR_BGR2GRAY).astype(np.float32)
            tpl = cv2.resize(fa, None, fx=sx, fy=sx, interpolation=cv2.INTER_CUBIC)
            px0, py0 = mapa(max(int(x0) - e, 0), max(int(y0) - e, 0))
            R = int(round(6 * sx))
            sa0, sb0 = max(int(px0) - R, 0), max(int(py0) - R, 0)
            area = cinza[sb0:sb0 + tpl.shape[0] + 2 * R, sa0:sa0 + tpl.shape[1] + 2 * R].astype(np.float32)
            if area.shape[0] > tpl.shape[0] and area.shape[1] > tpl.shape[1]:
                r = cv2.matchTemplate(area, tpl, cv2.TM_CCOEFF_NORMED)
                _, mx, _, (bx, by) = cv2.minMaxLoc(r)
                ddx, ddy = (sa0 + bx) - px0, (sb0 + by) - py0
                if mx > 0.6:
                    X0, Y0 = X0 + ddx, Y0 + ddy
                    mapa0 = mapa
                    mapa = (lambda m0, dx, dy: (lambda x, y: (m0(x, y)[0] + dx, m0(x, y)[1] + dy)))(mapa0, ddx, ddy)
                    print(f"      encaixe fino: {ddx / sx:+.1f}, {ddy / sx:+.1f} px da final (corr {mx:.2f})")
            # a janela local no 12K
            m = 8
            a0, b0 = mapa(x0 - m, y0 - m)
            a1, b1 = mapa(x1 + m, y1 + m)
            A0, B0, A1, B1 = max(int(a0), 0), max(int(b0), 0), min(int(np.ceil(a1)), im.shape[1]), min(int(np.ceil(b1)), im.shape[0])
            if na_folha:
                # o contorno na folha do 12K, nos 4 lados, encostado no vidro (não na parede, não na soleira)
                pa0, pb0 = mapa(x0, y0)
                pa1, pb1 = mapa(x1, y1)
                L, T, R, B = folha_12k(cinza, pa0, pb0, pa1, pb1, M=int(round(2 * sx)))
                gf = [((L - X0) / sx, (T - Y0) / sx, (R - X0) / sx, (B - Y0) / sx)]
                print("      folha no 12K: " + ", ".join(f"{(v - p_) / sx:+.1f}" for v, p_ in zip((L, T, R, B), (pa0, pb0, pa1, pb1)))
                      + " px da final (esq, cima, dir, baixo)")
                al = alfa([gf], (B1 - B0, A1 - A0), origem=((A0 - X0) / sx, (B0 - Y0) / sx), escala=sx, q=q)
                okb = np.ones_like(al, bool)
            else:
                al = alfa([g], (B1 - B0, A1 - A0), origem=((A0 - X0) / sx, (B0 - Y0) / sx), escala=sx, q=q)
                Fq = np.array([[sx, 0, X0 - A0], [0, sx, Y0 - B0]], np.float64)
                okb = cv2.warpAffine(ac.astype(np.uint8) * 255, Fq, (A1 - A0, B1 - B0), flags=cv2.INTER_NEAREST,
                                     borderValue=0) > 127
            im[B0:B1, A0:A1] = pintar(im[B0:B1, A0:A1], al * okb, q)
            print(f"   {op}: esquadria {int(x0)},{int(y0)} registro local {cc:.3f}")
        Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).save(f, quality=95, subsampling=0, dpi=dpi)
        del im, cinza


def antes_depois(planta, antes, depois, ok_g, n=18):
    """Os grupos que mais mudaram, antes | depois, numa folha."""
    tiles = []
    dif = []
    for g in ok_g:
        x0, y0, x1, y1 = [int(round(v)) for v in caixa(g)]
        m = 10
        X0, Y0, X1, Y1 = max(x0 - m, 0), max(y0 - m, 0), x1 + m, y1 + m
        d = np.abs(antes[Y0:Y1, X0:X1].astype(int) - depois[Y0:Y1, X0:X1].astype(int)).sum()
        dif.append((d, (X0, Y0, X1, Y1)))
    dif.sort(key=lambda t: -t[0])
    for d, (X0, Y0, X1, Y1) in dif[:n]:
        a, b = antes[Y0:Y1, X0:X1], depois[Y0:Y1, X0:X1]
        k = min(6.0, 280 / max(a.shape[:2]))
        a = cv2.resize(a, None, fx=k, fy=k, interpolation=cv2.INTER_CUBIC)
        b = cv2.resize(b, None, fx=k, fy=k, interpolation=cv2.INTER_CUBIC)
        par = np.hstack([a, np.full((a.shape[0], 6, 3), 255, np.uint8), b]) if a.shape[0] < a.shape[1] else \
            np.vstack([a, np.full((6, a.shape[1], 3), 255, np.uint8), b])
        T = np.full((300, 600, 3), 255, np.uint8)
        h, w = min(par.shape[0], 280), min(par.shape[1], 600)
        T[18:18 + h, :w] = par[:h, :w]
        cv2.putText(T, f"{X0},{Y0}", (2, 13), 0, 0.4, (0, 0, 200), 1)
        tiles.append(T)
    while len(tiles) % 3:
        tiles.append(np.full((300, 600, 3), 255, np.uint8))
    return np.vstack([np.hstack(tiles[i:i + 3]) for i in range(0, len(tiles), 3)]) if tiles else None


def visao(planta, img, ok_g, fora_g):
    """A planta inteira com as esquadrias que entram (vermelho, numeradas) e as que ficam (azul)."""
    ov = img.copy()
    for g in fora_g:
        x0, y0, x1, y1 = [int(round(v)) for v in caixa(g)]
        cv2.rectangle(ov, (x0 - 2, y0 - 2), (x1 + 2, y1 + 2), (255, 120, 0), 2)
    for i, g in enumerate(ok_g):
        x0, y0, x1, y1 = [int(round(v)) for v in caixa(g)]
        cv2.rectangle(ov, (x0 - 2, y0 - 2), (x1 + 2, y1 + 2), (0, 0, 255), 2)
        cv2.putText(ov, str(i), (x1 + 3, y0 + 10), 0, 0.55, (0, 0, 200), 2)
    lum = img.astype(np.int16).mean(2)
    ys, xs = np.nonzero(lum < 245)
    X0, X1 = np.percentile(xs, [0.5, 99.5]).astype(int)
    Y0, Y1 = np.percentile(ys, [0.5, 99.5]).astype(int)
    return ov[max(Y0 - 10, 0):Y1 + 10, max(X0 - 10, 0):X1 + 10]


# a conferência planta a planta (19/11): as esquadrias que a final desenha maiores que a peça do PDF (a moldura clara do
# render em volta do vidro) e que por isso ficaram sem o contorno; cada uma pela caixa da moldura (px da final)
EXTRAS = {
    "A_Terreo": [(1885, 359, 1946, 372),           # a janela da sala de estar, na parede de cima
                 (2268, 350, 2333, 356)],          # a janela do lavabo, sob a claraboia
    "A_1Pavimento": [(1539, 1458, 1575, 1466), (1624, 1458, 1643, 1465),   # as 2 janelas do banho master
                     (2533.5, 1126.5, 2545.5, 1174.3)],                    # a janela lateral do banho 1 (a folha, sem a soleira)
}
EXTRAS_FEITAS = {"A_Terreo": 2, "A_1Pavimento": 3}                    # quantas já foram aplicadas (rodar de novo aplica só as novas)


# o contorno que a conferência de 19/11 tirou (falsos positivos da primeira passada): (x0, y0, x1, y1) em px da final;
# a área volta à final de `ANTES` (sem o contorno), na final, nas variantes, na prancha e nos 12K A e B
DESFAZER = {
    "B_Subsolo": [(1228, 607, 1300, 621),       # a folha de madeira da porta do BH sauna (aberta, junto à parede)
                  (1447, 383, 1513, 391)],      # o box do BH serviço (o vidro de correr entre a circulação e o chuveiro)
    "D_Terreo": [(2046, 1538, 2057, 1602),      # as folhas de madeira de 3 portas (a do lavabo e mais duas), como as
                 (2449, 1210, 2518, 1221),      # outras folhas da casa, sem contorno
                 (2368, 764, 2444, 775)],
    "E_Terreo": [(2386, 832, 2449, 841),        # as folhas de madeira de 3 portas, como as outras folhas da casa
                 (2293, 1210, 2362, 1220),
                 (2390, 619, 2442, 629)],
}


def desfazer(planta, caixas, rev=ANTES):
    """Volta as `caixas` (px da final) ao que eram em `rev`: final, variantes, prancha e 12K A e B."""
    c, pav = planta.split("_")
    base = cv2.imread(str(PROJ / PLANTAS[planta][0]))
    for f in PLANTAS[planta]:
        im = cv2.imread(str(PROJ / f))
        old = git_img(f, rev)
        for x0, y0, x1, y1 in caixas:
            im[y0:y1, x0:x1] = old[y0:y1, x0:x1]
        cv2.imwrite(str(PROJ / f), im)
        if f == PLANTAS[planta][0]:
            novo = im
    pf = PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_entrega.png"
    pr = cv2.imread(str(pf))
    pr[:2160] = novo
    cv2.imwrite(str(pf), pr)
    dz = json.loads((PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[planta]
    for op in "AB":
        rel = f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_12K_opcao_{op}.jpg"
        pil = Image.open(PROJ / rel)
        dpi = pil.info.get("dpi", (743, 743))
        im = cv2.cvtColor(np.array(pil.convert("RGB")), cv2.COLOR_RGB2BGR)
        del pil
        dado = subprocess.run(["git", "show", f"{rev}:projetos/{rel}"], cwd=PROJ, capture_output=True, check=True).stdout
        old = cv2.imdecode(np.frombuffer(dado, np.uint8), cv2.IMREAD_COLOR)
        cinza = cv2.cvtColor(old, cv2.COLOR_BGR2GRAY)
        for x0, y0, x1, y1 in caixas:
            mapa, cc = registro_12k(base, cinza, dz, (max(x0 - 100, 0), max(y0 - 100, 0), x1 + 100, y1 + 100))
            A0, B0 = mapa(x0, y0)
            A1, B1 = mapa(x1, y1)
            A0, B0, A1, B1 = int(A0) - 2, int(B0) - 2, int(np.ceil(A1)) + 2, int(np.ceil(B1)) + 2
            im[B0:B1, A0:A1] = old[B0:B1, A0:A1]
            print(f"   {op}: {x0},{y0} desfeito (registro {cc:.3f})")
        Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).save(PROJ / rel, quality=95, subsampling=0, dpi=dpi)
        del im, old, cinza


def aplicar_extras(planta, q=Q_):
    """O contorno das `EXTRAS` da planta na final de hoje (e nas variantes), na prancha e nos 12K A e B."""
    gs = [[r] for r in EXTRAS[planta][EXTRAS_FEITAS.get(planta, 0):]]
    c, pav = planta.split("_")
    base = cv2.imread(str(PROJ / PLANTAS[planta][0]))
    novo, ac = final_nova(planta, base, gs, q)
    cv2.imwrite(str(PROJ / PLANTAS[planta][0]), novo)
    for f in PLANTAS[planta][1:]:
        im2 = cv2.imread(str(PROJ / f))
        cv2.imwrite(str(PROJ / f), final_nova(planta, im2, gs, q)[0])
    pf = PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_entrega.png"
    pr = cv2.imread(str(pf))
    pr[:2160] = novo
    cv2.imwrite(str(pf), pr)
    doze_k_local(planta, base, gs, ac, q, folga=120, na_folha=True)
    return base, novo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plantas", nargs="*")
    ap.add_argument("--auditar", action="store_true")
    ap.add_argument("--antes_depois", action="store_true")
    ap.add_argument("--sem12k", action="store_true")
    ap.add_argument("--extras", action="store_true", help="só as EXTRAS da planta (a conferência de 19/11)")
    ap.add_argument("--desfazer", action="store_true", help="só tira o contorno das caixas de DESFAZER da planta")
    a = ap.parse_args()
    if a.desfazer:
        for planta in a.plantas:
            desfazer(planta, DESFAZER[planta])
        return
    if a.extras:
        for planta in a.plantas:
            base, novo = aplicar_extras(planta)
            print(planta, "extras:", EXTRAS[planta])
        return
    for planta in a.plantas or [p for p in PLANTAS if p not in JA_NO_PADRAO]:
        img = cv2.imread(str(PROJ / PLANTAS[planta][0]))
        if a.antes_depois:
            # (depois de aplicar) a final de antes desta rodada, do git, contra a de hoje
            antes = git_img(PLANTAS[planta][0])
            Q, ok_g, fora_g, zonas = dados(planta, antes)
            fo = antes_depois(planta, antes, img, ok_g, n=24)
            if fo is not None:
                out = PROJ / f"POE642_Casa{planta[0]}/renders/POE642_Casa{planta[0]}_PH_{planta[2:]}_1911_esquadrias_pretas_antes_depois.jpg"
                cv2.imwrite(str(out), fo, [cv2.IMWRITE_JPEG_QUALITY, 88])
                print("  ", out.name)
            continue
        Q, ok_g, fora_g, zonas = dados(planta, img)
        n, frac = auditar(planta, img, ok_g)
        print(f"{planta}: {len(ok_g)} esquadrias (fora {len(fora_g)}); contorno escuro hoje em {frac:.0%} de {n} px")
        if a.auditar:
            v = visao(planta, img, ok_g, fora_g)
            cv2.imwrite(f"/tmp/claude-0/-home-user/610cde13-fae4-5134-867b-524dc247ebb6/scratchpad/esq/visao_{planta}.jpg", v,
                        [cv2.IMWRITE_JPEG_QUALITY, 85])
            continue
        if np.abs(img.astype(np.int16) - git_img(PLANTAS[planta][0]).astype(np.int16)).max() > 0:
            print("   já aplicada (a final difere da de", ANTES + "); nada feito")
            continue
        novo, ac = final_nova(planta, img, ok_g)
        cv2.imwrite(str(PROJ / PLANTAS[planta][0]), novo)
        for f in PLANTAS[planta][1:]:
            im2 = cv2.imread(str(PROJ / f))
            n2, _ = final_nova(planta, im2, ok_g)
            cv2.imwrite(str(PROJ / f), n2)
            print("  ", Path(f).name)
        if not a.sem12k:
            doze_k(planta, img, ok_g, ac)


if __name__ == "__main__":
    main()

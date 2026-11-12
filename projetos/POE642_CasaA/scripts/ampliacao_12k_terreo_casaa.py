"""O JPG em 12K do Térreo da Casa A (usuário, 10/11/26: "GERE A IMAGEM EM 12K JPG. ISSO É REGRA PARA TODAS AS PLANTAS").

Só a imagem (sem rodapé), na proporção da A3 deitada (12288 x 8689 px), como a do Subsolo (`ampliacao_a3_casaa.py`):
  1. `preparar`: da final (`renders/POE642_CasaA_PH_Terreo_final_rotulos.png`) saem os textos e os símbolos, que a IA
     redesenha errado: os rótulos dos ambientes (achados na imagem pela forma, `terreo_casaa_1011.rotulos_na_imagem`,
     com os ajustes de cada um), os triângulos e as descrições das escadas e o triângulo da entrada
     (`terreo_casaa_1011.ESCADAS_TA` e `ENTRADA_TA`). Os tracejados finos dos vazios e do pergolado também saem: a
     entrada da IA parte do passo do shaft (a final antes dos tracejados finos); o alfa deles é a diferença entre a
     final e esse passo. A entrada da IA é o recorte da planta em 16:9 (a proporção da IA mais perto da planta do
     Térreo, mais larga que a A3), com a margem da A3 de cada lado.
  2. A entrada no Nano Banana Pro (4K, 16:9), com o prompt de ampliação fiel (`PROMPT`).
  3. `corrigir`: os trechos que a IA inventou (`CORRIGIR_PX`, conferidos no mapa das diferenças) voltam da entrada.
  4. A saída corrigida no Topaz (High Fidelity V2), a 12288 de largura.
  5. `montar12k`: a saída do Topaz alinhada à entrada (ECC afim), na A3 deitada; os tons da final de volta (a baixa
     frequência); o fundo fora da planta em branco puro; os tracejados finos de volta (o alfa deles ampliado); os
     rótulos, as descrições e os triângulos desenhados direto no corpo de 12K, numa janela em volta de cada um.

  python3 ampliacao_12k_terreo_casaa.py preparar --passos <pasta dos passos de terreo_casaa_1011.py>
  python3 ampliacao_12k_terreo_casaa.py diferencas <saída do Nano Banana Pro>
  python3 ampliacao_12k_terreo_casaa.py corrigir <saída do Nano Banana Pro> <corrigida>
  python3 ampliacao_12k_terreo_casaa.py montar12k <saída do Topaz>
"""

import argparse
import contextlib
import io
import json
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import final3840_casaa as FA                    # noqa: E402
import final3840_casaa_terreo as T              # noqa: E402
import ampliacao_a3_casaa as AM                 # noqa: E402
import terreo_casaa_1011 as TA                  # noqa: E402

R = FA.CASA / "renders"
# o pavimento (o 1º Pavimento usa este mesmo roteiro: `ampliacao_12k_1pav_casaa.py` troca estes nomes e as caixas)
PAV, NOME_PAV = "Terreo", "Térreo"


def quadro():
    return FA.QuadroA(PAV)


FINAL = R / "POE642_CasaA_PH_Terreo_final_rotulos.png"
ENTRADA_IA = R / "POE642_CasaA_PH_Terreo_12K_entrada_ia.png"
TRACOS = R / "POE642_CasaA_PH_Terreo_12K_tracejados.png"       # o alfa (x255) e a cor dos tracejados finos
DADOS = R / "POE642_CasaA_PH_Terreo_12K_dados.json"
# as duas opções de letra (regra de 10/11: "INCLUSIVE TRAZER UMA IMAGEM 12K COM A OUTRA FONTE DE LETRA TAMBÉM É UMA REGRA
# PARA TODAS PLANTAS A PARTIR DE AGORA"): A na Inter das pranchas, B na Kalam (`rotulos_manuscritos_casaa`)
SAIDA = FA.CASA / "entrega" / "POE642_CasaA_PH_Terreo_12K_opcao_{opcao}.jpg"

G12 = {"a3": (4961, 3508), "margem_px": 150, "ia": (16, 9), "branco": 245, "cheio": 0.85, "tom_sigma_px": 2.5,
       "fundo_folga_px": 3, "folga_texto_px": 2, "largura": 12288, "janela_px": 260, "qualidade": 95, "traco_min": 0.04,
       "kalam_estreitos": ["PROJ. CLARABOIA"]}

PROMPT = ("High-fidelity 4K upscale of the reference image, which is a top-down architectural humanized floor plan "
          "(orthographic, viewed straight from above). Reproduce the reference EXACTLY: identical composition, framing, "
          "layout, scale and position of every element; same dark gray walls, black pillars, doors, glass partitions, "
          "stairs and stepping stones, pool, spa and wooden deck, furniture (armchairs, sofas, round tables, dining "
          "table, bar stools, sun loungers), kitchen and gourmet countertops, cooktops, stainless steel appliances, "
          "bathroom fixtures, spiral staircase, elevator, the three cars in the garage, the trees and shrubs, and the "
          "pure white background. Do not add, remove, move, rotate, resize or redesign anything. Do not add any text, "
          "labels, numbers, arrows, triangles, symbols, dashed lines or people. Only increase resolution and detail: "
          "crisp straight wall edges and lines, sharp furniture edges, and fine realistic material textures matching "
          "the existing colors and tones exactly: smooth light beige marble (Bege Bahia) with soft low-contrast veining, "
          "light raw travertine indoors, the uniform medium brown stone floor in the kitchen, gourmet and garage, warm "
          "wood deck boards (same direction and tone), the sober gray-green pool water with the small mosaic tile "
          "pattern, Portuguese stone paving on the driveway, and the dark olive-green lawn with very fine grass grain "
          "at the same small scale. Keep colors, brightness and contrast the same as the reference. Clean, "
          "photographic architectural presentation quality, no artifacts, no noise.")


# ----------------------------------------------------------------------------------------------------------------------
# Os textos e os símbolos da final
def rotulos(Q, img, nomes=None):
    """[(nome, pdf, opc, (dx, dy) px do quadro, cor BGR)] dos rótulos achados na final: o desenho de cada um (corpo,
    quebra, desvio) é o de `pedidos_terreo_casaa_2910._achar_rotulo`, na polaridade de melhor nota; com `nomes`, só os
    desses nomes."""
    import revisao_casaa_2910 as RV
    import pedidos_terreo_casaa_2910 as P
    rot, aj = RV._rotulos_pav(Q)
    if nomes is not None:
        rot = [r for r in rot if r[0] in nomes]
    q = dict(P.ROTULOS_OUTROS_TA, minimo_forma=0.0)
    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
    e = img.shape[1] / 2000
    out = []
    for r in rot:
        melhor = None
        for claro in (False, True):
            src = (255 - img) if claro else img
            with contextlib.redirect_stdout(io.StringIO()):
                al, aj2 = P._achar_rotulo(Q, src, r, aj, q, busca=250)
            if al.max() < 0.3:
                continue
            x0, y0, x1, y1 = RV._caixa(al)
            g = cinza[y0:y1, x0:x1] if claro else 255 - cinza[y0:y1, x0:x1]
            a = al[y0:y1, x0:x1]
            nota = float(np.corrcoef(a.ravel(), g.ravel())[0, 1]) if a.std() > 0 and g.std() > 0 else 0.0
            if melhor is None or nota > melhor[0]:
                ax, ay = Q.p2q(*r[2])
                ent = [a_ for a_ in aj2 if a_[0] == r[0] and np.hypot(a_[1][0] - ax / e, a_[1][1] - ay / e) < 1e-3]
                melhor = (nota, al, claro, ent[0] if ent else None)
        if melhor is None or melhor[0] < 0.6 or melhor[3] is None:
            continue
        nota, al, claro, ent = melhor
        opc = dict(ent[3]) if len(ent) > 3 and isinstance(ent[3], dict) else ({"corpo": ent[3]} if len(ent) > 3 else {})
        opc.pop("cor", None)
        dx, dy = ent[2][0] * Q.W / 2000, ent[2][1] * Q.W / 2000
        cor = TA.ROTULO_CLARO if claro else TA.ROTULO_ESCURO
        out.append({"nome": r[0], "pdf": list(r[2]), "opc": opc, "desvio": [float(dx), float(dy)], "cor": list(cor),
                    "nota": round(nota, 3)})
    return out


def _r(Q, b):
    return AM._r_do_nome(Q, b["nome"], b["pdf"])


def alfa_rotulo(Q, b, forma, s=1.0, x0=0.0, y0=0.0):
    """O alfa do rótulo b no quadro `forma`, levado por u = (x - x0) s, v = (y - y0) s."""
    def loc(x, y):
        u, v = Q.p2q(x, y)
        return (u - x0) * s, (v - y0) * s
    return AM._alfa_um(Q, _r(Q, b), b["opc"], b["desvio"][0], b["desvio"][1], forma, pdf2img=loc, esc=Q.W / 2000 * s)


def anotacoes(Q):
    """Os símbolos e as descrições, em px do quadro: [("tri", pts, cor)] e [("txt", (linhas, x, y, alinhar), cor)]."""
    q = TA.ESCADAS_TA
    out = []
    for nome in ("pisantes", "deck", "jardim"):
        e = q[nome]
        out.append(("tri", [list(map(float, p)) for p in TA.seta_tri(*e["tri_px"], e["dir"])], (30, 30, 30)))
        out.append(("txt", (list(e["texto"]), *e["txt_px"], e["alinhar"]), q["cor_texto"]))
    c = T.CARACOL
    ccx, ccy = Q.p2q(*c["centro"])
    rm = (c["r_pilar"] + c["r_degrau"]) / 2 * FA.PT_PX
    ang = np.radians(c["a0"] + c["passo"] / 2)
    tx, ty = ccx + rm * np.cos(ang), ccy - rm * np.sin(ang)
    pts = TA.seta_tri(tx, ty, (-np.sin(ang), -np.cos(ang)), *q["caracol"]["tri"])
    out.append(("tri", [list(map(float, p)) for p in pts], (30, 30, 30)))
    cc = q["caracol"]
    out.append(("txt", (list(cc["texto"]), *cc["txt_px"], cc["alinhar"]), TA.ROTULO_CLARO))
    e = TA.ENTRADA_TA
    a0, a1 = e["abertura_px"]
    cx = e["x_soleira_px"] + e["recuo_px"] + e["comp"] / 2
    pts = TA.seta_tri(cx, (a0 + a1) / 2, (-1, 0), e["comp"], e["larg"])
    out.append(("tri", [list(map(float, p)) for p in pts], (30, 30, 30)))
    return out


def alfa_anotacao(tipo, dados, forma, s=1.0, x0=0.0, y0=0.0, ss=8):
    H, W = forma
    if tipo == "tri":
        p = (np.float32(dados) - [x0, y0]) * s
        bx0, by0 = np.floor(p.min(axis=0)).astype(int) - 2
        bx1, by1 = np.ceil(p.max(axis=0)).astype(int) + 3
        m = np.zeros(((by1 - by0) * ss, (bx1 - bx0) * ss), np.uint8)
        cv2.fillPoly(m, [np.int32(np.round((p - [bx0, by0]) * ss))], 255, cv2.LINE_AA)
        a = np.zeros((H, W), np.float32)
        sub = cv2.resize(m.astype(np.float32) / 255, (bx1 - bx0, by1 - by0), interpolation=cv2.INTER_AREA)
        ya, yb, xa, xb = max(0, by0), min(H, by1), max(0, bx0), min(W, bx1)
        a[ya:yb, xa:xb] = sub[ya - by0:yb - by0, xa - bx0:xb - bx0]
        return a
    linhas, x, y, alinhar = dados
    corpo = TA.ESCADAS_TA.get("corpo_desc_px") or FA.ESCADA_A["corpo_px"]
    return TA.alfa_texto(linhas, (x - x0) * s, (y - y0) * s, alinhar, corpo=int(round(corpo * s)),
                         entrelinha=round(corpo * 1.18) * s, forma=forma)


# ----------------------------------------------------------------------------------------------------------------------
def recortes(img):
    q = G12
    Wa, _ = q["a3"]
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ys, xs = np.nonzero(g < q["branco"])
    x0, y0, x1, y1 = int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1
    Wc = int(round((x1 - x0) * Wa / (Wa - 2 * q["margem_px"])))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    X0 = int(round(cx - Wc / 2))
    Hia = int(round(Wc * q["ia"][1] / q["ia"][0]))
    Yia = int(round(cy - Hia / 2))
    if Yia < 0 or Yia + Hia > img.shape[0] or X0 < 0 or X0 + Wc > img.shape[1] or y1 - y0 > Hia:
        raise SystemExit(f"o recorte sai do quadro ou corta a planta: {X0},{Yia} {Wc}x{Hia}, planta {x0},{y0}-{x1},{y1}")
    return {"planta": (x0, y0, x1, y1), "X0": X0, "Wc": Wc, "Yia": Yia, "Hia": Hia}


def preparar(passos):
    Q = FA.QuadroA("Terreo")
    img = cv2.imread(str(FINAL))
    # o passo antes dos tracejados finos (os contornos de 10/11, depois do shaft)
    base_arq = Path(passos) / "passo_contornos.png"
    base = cv2.imread(str(base_arq if base_arq.exists() else Path(passos) / "passo_shaft.png"))
    # os tracejados finos: o alfa (a final entre o passo do shaft e a cor do traço) e a cor (cinza escuro ou claro)
    f, b = img.astype(np.float32), base.astype(np.float32)
    esc, cla = np.float32(TA.FINOS_TA["escuro"]), np.float32(TA.FINOS_TA["claro"])
    a_esc = np.clip(((b - f) / np.maximum(b - esc, 1)).mean(axis=2), 0, 1)
    a_cla = np.clip(((f - b) / np.maximum(cla - b, 1)).mean(axis=2), 0, 1)
    escuro = a_esc >= a_cla
    alfa = np.where(escuro, a_esc, a_cla)
    alfa[alfa < G12["traco_min"]] = 0
    tr = np.zeros(img.shape, np.uint8)
    tr[..., 0] = np.round(alfa * 255).astype(np.uint8)
    tr[..., 1] = np.where(escuro, 0, 255).astype(np.uint8)
    cv2.imwrite(str(TRACOS), tr)
    # os textos e os símbolos saem do passo do shaft (o fundo pela conta do alfa, o miolo pelo entorno)
    rots = rotulos(Q, img)
    # os do lavabo (LAVABO e PROJ. CLARABOIA, centralizados em 10/11) no desenho gravado pela etapa dos contornos
    # e os recentralizados de 11/11 (`terreo_casaa_1011.rotulos_1111`), no desenho gravado (o corpo do B. MOTORISTA)
    for arq in (TA.ROTULOS_LAVABO, TA.ROTULOS_1111_JSON):
        if arq.exists():
            lav = json.loads(arq.read_text())
            nomes = {b_["nome"] for b_ in lav}
            rots = [b_ for b_ in rots if b_["nome"] not in nomes] + lav
    camadas = [(alfa_rotulo(Q, b_, img.shape[:2]), tuple(b_["cor"])) for b_ in rots]
    anot = anotacoes(Q)
    camadas += [(alfa_anotacao(t, d, img.shape[:2]), tuple(c)) for t, d, c in anot]
    limpa = AM.tirar(base, camadas, G12["cheio"])
    # onde o desenho achado não casa px a px com o da final, sobra a sombra do texto: a área de cada texto (com folga)
    # vem toda do entorno (a IA refaz a textura; no 12K o texto volta por cima)
    txt = np.zeros(img.shape[:2], np.uint8)
    for (a, _), t in zip(camadas, ["rot"] * len(rots) + [t_ for t_, _, _ in anot]):
        if t != "tri":
            txt |= (a > 0.02).astype(np.uint8)
    k = 2 * G12["folga_texto_px"] + 1
    limpa = cv2.inpaint(limpa, cv2.dilate(txt, np.ones((k, k), np.uint8)) * 255, 4, cv2.INPAINT_TELEA)
    # a água (piscina, prainha e spa) sem os rótulos: o desenho do passo da piscina de novo (a semente é fixa), em vez
    # do texto tirado de cima das pastilhas, que borrava a grade (10/11, o Barlavento visível)
    limpa = TA.piscina_ta(Q, limpa, com_rotulos=False)
    rc = recortes(img)
    X0, Wc, Yia, Hia = rc["X0"], rc["Wc"], rc["Yia"], rc["Hia"]
    cv2.imwrite(str(ENTRADA_IA), limpa[Yia:Yia + Hia, X0:X0 + Wc])
    DADOS.write_text(json.dumps({"rotulos": rots, "anotacoes": anot, "recortes": rc}, ensure_ascii=False, indent=1)
                     + "\n")
    # conferência: o desenho de volta sobre a limpa, contra a final (o quanto o redesenho bate)
    volta = AM.pintar(limpa, camadas)
    dif = np.abs(volta.astype(np.int16) - base.astype(np.int16)).max(axis=2)
    print(f"[Térreo] {len(rots)} rótulos ({', '.join(b_['nome'] for b_ in rots)}), {len(anot)} símbolos e descrições;"
          f" o redesenho contra a final: {int((dif > 24).sum())} px com mais de 24 de diferença")
    x0, y0, x1, y1 = rc["planta"]
    cv2.imwrite(str(R / "POE642_CasaA_PH_Terreo_12K_sem_textos.jpg"),
                np.hstack([img[y0:y1, x0:x1], limpa[y0:y1, x0:x1]]), [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"    a planta {x0},{y0} - {x1},{y1}; o recorte da IA {X0},{Yia} {Wc}x{Hia} (16:9)")
    print(f"    {ENTRADA_IA}")


# ----------------------------------------------------------------------------------------------------------------------
def _alinhar(ia, entrada):
    Hc, Wc = entrada.shape[:2]
    peq = cv2.resize(ia, (Wc, Hc), interpolation=cv2.INTER_AREA)
    g0 = cv2.GaussianBlur(cv2.cvtColor(entrada, cv2.COLOR_BGR2GRAY).astype(np.float32), (0, 0), 1.2)
    g1 = cv2.GaussianBlur(cv2.cvtColor(peq, cv2.COLOR_BGR2GRAY).astype(np.float32), (0, 0), 1.2)
    M = np.eye(2, 3, dtype=np.float32)
    _, M = cv2.findTransformECC(g0, g1, M, cv2.MOTION_AFFINE,
                                (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 300, 1e-7), None, 5)
    return M


def diferencas(saida_ia):
    """O mapa das diferenças de estrutura (passa-banda) entre a saída da IA e a entrada, na escala da entrada: onde ela
    inventou ou tirou peças. Grava o mapa e lista as manchas maiores (px da final)."""
    entrada = cv2.imread(str(ENTRADA_IA))
    rc = json.loads(DADOS.read_text())["recortes"]
    ia = cv2.imread(str(saida_ia))
    M = _alinhar(ia, entrada)
    Hc, Wc = entrada.shape[:2]
    Hi, Wi = ia.shape[:2]
    Tm = (np.diag([Wi / Wc, Hi / Hc, 1.0]) @ np.vstack([M.astype(np.float64), [0, 0, 1]]))[:2]
    peq = cv2.warpAffine(ia, Tm, (Wc, Hc), flags=cv2.INTER_AREA | cv2.WARP_INVERSE_MAP, borderValue=(255, 255, 255))

    def banda(x):
        g = cv2.cvtColor(x, cv2.COLOR_BGR2LAB).astype(np.float32)
        return cv2.GaussianBlur(g, (0, 0), 1.0) - cv2.GaussianBlur(g, (0, 0), 6.0)
    d = np.abs(banda(peq) - banda(entrada)).max(axis=2)
    d += np.abs(cv2.GaussianBlur(cv2.cvtColor(peq, cv2.COLOR_BGR2LAB).astype(np.float32), (0, 0), 3)
                - cv2.GaussianBlur(cv2.cvtColor(entrada, cv2.COLOR_BGR2LAB).astype(np.float32), (0, 0), 3)).max(axis=2)
    m = cv2.GaussianBlur(d, (0, 0), 4) > 14
    n, lab, st, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8))
    manchas = sorted([(int(st[i, 4]), int(st[i, 0]) + rc["X0"], int(st[i, 1]) + rc["Yia"],
                       int(st[i, 0] + st[i, 2]) + rc["X0"], int(st[i, 1] + st[i, 3]) + rc["Yia"])
                      for i in range(1, n) if st[i, 4] > 150], reverse=True)
    viz = np.hstack([entrada, peq, cv2.applyColorMap(np.clip(d * 6, 0, 255).astype(np.uint8), cv2.COLORMAP_JET)])
    cv2.imwrite(str(R / f"POE642_CasaA_PH_{PAV}_12K_diferencas.jpg"), viz, [cv2.IMWRITE_JPEG_QUALITY, 85])
    for a, *b in manchas[:40]:
        print(f"    {a:6d} px  {b}")
    return manchas


# Os trechos que a IA inventou ou trocou (px da final), conferidos no mapa das diferenças e nos recortes (10/11/26):
# voltam da entrada ampliada (Lanczos, com nitidez), com a borda esfumada; o resto (as árvores, as plantas, os móveis,
# mais nítidos e fiéis) fica o da IA. A IA tinha: posto todos os degraus da caracol em linha cheia (sem o tracejado dos
# de cima); trocado os dois cooktops (bocas quadradas) e a cuba do lavabo; alisado o marrom tabaco da bancada gourmet;
# feito a prainha com uma grade forte de pastilhas e a piscina sem o desenho; e trocado o leque da pedra portuguesa
# por um cascalho claro. A água e a pedra portuguesa vão pelas máscaras (`CORRIGIR_MASCARAS`), não por caixas.
# Na leva de 10/11 à noite (a entrada nova, com a piscina, as paredes, os guarda-corpos e o escritório refeitos), a IA
# também: tirou o X e os puxadores do elevador e trocou a roupa de cama e a cuba do motorista; juntou as duas mesas
# laterais do escritório numa só e listrou o aparador; trocou a cuba esculpida do lavabo por uma de granito e a do
# lavatório por um ralo linear; tirou os ralos e trocou as torneiras das pias da cozinha; fez das prateleiras da garagem
# um armário rosado; pôs um puxador de porta no vidro da sala de estar e mudou a janela nova; e apagou parte do vidro do
# jardim junto ao elevador. Esses trechos voltam da entrada; o resto da IA (a vegetação, as janelas, o deck, a escada do
# jardim mais limpa, os resíduos que ela tirou) fica.
CORRIGIR_PX = {"caracol": (1918, 1512, 2036, 1632), "cooktop_cozinha": (1964, 1280, 2022, 1318),
               "gourmet": (1476, 1266, 1804, 1444), "lavabo": (2296, 350, 2362, 522),
               "elevador_motorista": (2244, 1096, 2456, 1298), "escritorio_mesas": (2500, 548, 2546, 594),
               "escritorio_aparador": (2420, 562, 2504, 601), "lavatorio": (1468, 1440, 1625, 1508),
               "pias_cozinha": (2122, 1326, 2168, 1410), "prateleiras_garagem": (2494, 1114, 2537, 1230),
               "janela_estar": (1880, 354, 1952, 378), "vidro_estar": (1864, 372, 1882, 440),
               "vidro_jardim": (2250, 980, 2400, 1018),
               # os retoques de 11/11 (`terreo_casaa_1011.RETOQUES_1111` e as bordas da pista em `_acesso`): a saída da
               # IA é a mesma; esses trechos, refeitos na final, voltam da entrada nova
               "curva_acesso_cima": (3326, 1316, 3440, 1366), "curva_acesso_baixo": (3326, 1552, 3440, 1684),
               "tracejado_jardim": (1236, 1634, 1708, 1650), "armario_lavabo": (2188, 364, 2262, 616),
               "porta_lavabo": (2256, 455, 2278, 524), "grama_motorista": (2544, 1150, 2702, 1322),
               "parede_hall": (2244, 866, 2548, 892), "pedras_acesso": (2606, 598, 3436, 878),
               "porta_correr_cozinha": (2140, 1145, 2186, 1300), "porta_1_3": (1585, 1535, 1682, 1630),
               "porta_6": (1975, 1445, 2062, 1475), "porta_7": (2044, 1510, 2072, 1582),
               "porta_9": (2225, 1240, 2252, 1326), "porta_13": (2330, 1284, 2405, 1310),
               "garagem_ponta": (2455, 1294, 2480, 1324), "porta_18": (2512, 1240, 2539, 1326),
               # os pedidos de 11/11, 2ª leva: o deck em madeira nova; os guarda-corpos da escada do jardim na borda;
               # a faixa de baixo (o traço da área descoberta, o portão de vidro torto e as pedras inventadas da IA no
               # acesso à garagem, com a mancha escura junto à grama); os pontos azulados nas pontas dos X da varanda e
               # da sala de estar ("limpe residuos e alinhe os rotulos"; "corrija as imperfeições desse portão em vidro";
               # "limpe residuos e corrija o piso de acesso a garagem")
               "deck_1111": (720, 500, 1090, 1135), "guarda_corpo_1111": (2245, 905, 2495, 1090),
               "faixa_baixo_1111": (1690, 1636, 3440, 1960), "varanda_sala_1111": (1500, 595, 2165, 775),
               # 11/11, 3ª leva: a sala nos tons da vista 3D (os dois tapetes, o sofá, as poltronas, as mesas)
               "sala_1111": (1590, 375, 2165, 845)}
# o gramado inteiro (11/11: a grama realista e o paisagismo B, com a palmeira) volta da entrada nova pela máscara do
# gramado (`terreo_casaa_1011.gramado_mascara` sobre a final). As manchas da grama realista são mais oliva (o verde um
# pouco abaixo do vermelho) que o limite da máscara (`verde` -4): nelas a máscara furava e dois arbustos antigos da IA
# ficavam no gramado do fundo; aqui o limite desce para `gramado_verde` (a máscara do passo do gramado, quase igual)
CORRIGIR_MASCARAS = {"agua": "agua", "pedra_portuguesa": (85, 138, 185), "gramado": "gramado"}
CORRECAO = {"nitidez": (0.6, 1.2), "borda_px": 2.0, "folga_mascara_px": 2, "gramado_verde": -10}


def _mascara(Q, chave):
    if chave == "agua":
        return TA.agua_mascara(Q) > 0.5
    if chave == "gramado":
        img = cv2.imread(str(FA.CASA / "renders" / "POE642_CasaA_PH_Terreo_final_rotulos.png"))
        return (TA.gramado_mascara(Q, img)
                | TA.gramado_mascara(Q, img, dict(TA.GRAMADO_TA, verde=CORRECAO["gramado_verde"])))
    return np.all(Q.chapada == np.uint8(chave), axis=2)


def corrigir_ia(saida_ia, destino):
    q = CORRECAO
    ia = cv2.imread(str(saida_ia))
    entrada = cv2.imread(str(ENTRADA_IA))
    rc = json.loads(DADOS.read_text())["recortes"]
    X0, Yia = rc["X0"], rc["Yia"]
    Hi, Wi = ia.shape[:2]
    Hc, Wc = entrada.shape[:2]
    M = _alinhar(ia, entrada)
    Tm = (np.diag([Wi / Wc, Hi / Hc, 1.0]) @ np.vstack([M.astype(np.float64), [0, 0, 1]]))[:2]
    ref = cv2.warpAffine(entrada, Tm, (Wi, Hi), flags=cv2.INTER_LANCZOS4, borderValue=(255, 255, 255)).astype(np.float32)
    f_, r_ = q["nitidez"]
    ref = np.clip(ref + f_ * (ref - cv2.GaussianBlur(ref, (0, 0), r_)), 0, 255)
    m = np.zeros((Hi, Wi), np.float32)
    for nome, (x0, y0, x1, y1) in CORRIGIR_PX.items():
        pts = np.float32([[x0 - X0, y0 - Yia], [x1 - X0, y0 - Yia], [x1 - X0, y1 - Yia], [x0 - X0, y1 - Yia]])
        pq = cv2.transform(pts[None], Tm)[0]
        cv2.fillConvexPoly(m, np.int32(np.round(pq)), 1.0)
    Q = quadro()
    k = 2 * q["folga_mascara_px"] + 1
    for nome, chave in CORRIGIR_MASCARAS.items():
        mq = cv2.dilate(_mascara(Q, chave).astype(np.uint8), np.ones((k, k), np.uint8))[Yia:Yia + Hc, X0:X0 + Wc]
        m = np.maximum(m, cv2.warpAffine(mq.astype(np.float32), Tm, (Wi, Hi), flags=cv2.INTER_LINEAR))
    m = cv2.GaussianBlur(m, (0, 0), q["borda_px"] * Wi / Wc / 2.7)[..., None]
    out = np.clip(np.round(ia * (1 - m) + ref * m), 0, 255).astype(np.uint8)
    cv2.imwrite(str(destino), out)
    print(f"    a saída da IA corrigida em {len(CORRIGIR_PX)} trechos ({', '.join(CORRIGIR_PX) or 'nenhum'}) e nas "
          f"máscaras ({', '.join(CORRIGIR_MASCARAS)}): {destino}")


# ----------------------------------------------------------------------------------------------------------------------
def _itens_manuscrita(Q, b, s, X0, Ya3, fator=None):
    """As linhas do rótulo b na Kalam, em px do 12K: [(texto, corpo, x, y, âncora)]; com `fator`, todas as linhas no
    mesmo fator do corpo (o mesmo tamanho em todos os rótulos, 11/11), sem ele cada linha no teto dela."""
    import rotulos_manuscritos_casaa as RM
    import retoque_1pav_casae as R1
    from rodape_entrega import FONTES

    def loc(x, y):
        u, v = Q.p2q(x, y)
        return (u - X0) * s, (v - Ya3) * s
    from PIL import ImageFont
    k = (RM._altura_maiuscula(FONTES / f"Inter-{R1.ROTULOS['fonte']}.otf") / RM._altura_maiuscula(RM.FONTE)
         * RM.MANUSCRITA["altura"])
    q = R1.ROTULOS

    def largura(fonte, texto, corpo):
        return ImageFont.truetype(str(fonte), max(4, int(round(corpo * 4)))).getlength(texto) / 4

    # a linha na Kalam não passa da largura que ocupava na Inter (a opção A): a Kalam é mais larga na mesma altura das
    # maiúsculas, e num vão estreito (o PROJ. CLARABOIA do lavabo, 10/11) passaria por cima da parede
    itens = []
    for t, c, x, y in RM.linhas_rotulo(Q, b, pdf2img=loc, escala_desvio=Q.W / 2000 * s):
        peso = q["fonte"] if t.startswith("A:") else q.get("fonte_nome", q["fonte"])
        teto = largura(FONTES / f"Inter-{peso}.otf", t, c) / max(largura(RM.FONTE, t, c * k), 1e-6)
        f_ = min(1.0, teto) if fator is None else (1.0 if fator == "tetos" else fator)
        itens.append((t, c * k * f_, x, y, "ms", teto))
    if fator == "tetos":
        return [it[5] for it in itens]
    return [it[:5] for it in itens]


def fator_manuscrita(Q, rots, s, X0, Ya3):
    """O fator único do corpo na Kalam (usuário, 11/11: "centralize e alinhe os rótulos. mantenha os mesmos tamanho de
    fonte, sempre que possível"): o menor teto (a largura da linha na Inter sobre a da Kalam) entre os rótulos comuns,
    para todos; os de `kalam_estreitos` (num vão estreito, como a PROJ. CLARABOIA) podem ficar abaixo dele."""
    tetos = {b["nome"]: min(_itens_manuscrita(Q, b, s, X0, Ya3, fator="tetos")) for b in rots}
    est = set(G12.get("kalam_estreitos", ()))
    f = min(1.0, min(v for n, v in tetos.items() if n not in est))
    return f, {n: min(f, v) for n, v in tetos.items() if n in est}


def _itens_anotacao_manuscrita(dados, s, X0, Ya3):
    """As descrições das escadas na Kalam (o mesmo meio de linha e o mesmo alinhamento), em px do 12K."""
    import rotulos_manuscritos_casaa as RM
    from rodape_entrega import FONTES
    e = FA.ESCADA_A
    linhas, x, y, alinhar = dados
    k = RM._altura_maiuscula(FONTES / e["fonte"]) / RM._altura_maiuscula(RM.FONTE) * RM.MANUSCRITA["altura"]
    corpo = TA.ESCADAS_TA.get("corpo_desc_px") or e["corpo_px"]       # o corpo das descrições na final (11/11)
    entre = round(corpo * 1.18)
    anc = {"esquerda": "lm", "direita": "rm", "centro": "mm"}[alinhar]
    n = len(linhas)
    return [(ln, corpo * k * s, (x - X0) * s, (y + (i - (n - 1) / 2) * entre - Ya3) * s, anc)
            for i, ln in enumerate(linhas)]


def _desenhar_janela(out, itens, cor, reforco):
    import rotulos_manuscritos_casaa as RM
    xs = [x for _, _, x, _, _ in itens]
    ys = [y for _, _, _, y, _ in itens]
    c = max(it[1] for it in itens)
    larg = max(len(t) for t, _, _, _, _ in itens) * c * 0.9
    bx, by = max(0, int(min(xs) - larg - 4 * c)), max(0, int(min(ys) - 3 * c))
    bx1, by1 = min(out.shape[1], int(max(xs) + larg + 4 * c)), min(out.shape[0], int(max(ys) + 3 * c))
    janela = out[by:by1, bx:bx1]
    loc = [(t, cc, x - bx, y - by, a) for t, cc, x, y, a in itens]
    out[by:by1, bx:bx1] = RM.desenhar(janela, loc, cor, reforco_px=reforco)


def montar12k(saida_topaz, largura=None, opcao="A"):
    from PIL import Image
    q = G12
    L = largura or q["largura"]
    Wa0, Ha0 = q["a3"]
    Hh = int(round(L * Ha0 / Wa0))
    Q = quadro()
    img = cv2.imread(str(FINAL))
    entrada = cv2.imread(str(ENTRADA_IA))
    d = json.loads(DADOS.read_text())
    rc, rots, anot = d["recortes"], d["rotulos"], d["anotacoes"]
    X0, Wc, Yia, Hia = rc["X0"], rc["Wc"], rc["Yia"], rc["Hia"]
    Ya3 = Yia + (Hia - Wc * Ha0 / Wa0) / 2            # o topo da A3 (px da final): a A3 é mais alta que o 16:9
    s = L / Wc
    ia = cv2.imread(str(saida_topaz))
    Hi, Wi = ia.shape[:2]
    print(f"[{NOME_PAV}] a saída ampliada: {Wi}x{Hi}; o JPG: {L}x{Hh} ({s:.3f}x a final)")
    M = _alinhar(ia, entrada)
    print(f"    alinhamento (entrada -> saída): [[{M[0, 0]:.4f} {M[0, 1]:.4f} {M[0, 2]:.2f}] "
          f"[{M[1, 0]:.4f} {M[1, 1]:.4f} {M[1, 2]:.2f}]]")
    Au = np.array([[1 / s, 0, 0], [0, 1 / s, Ya3 - Yia], [0, 0, 1]], np.float64)
    Tm = (np.diag([Wi / Wc, Hi / Hia, 1.0]) @ np.vstack([M.astype(np.float64), [0, 0, 1]]) @ Au)[:2]
    out = cv2.warpAffine(ia, Tm, (L, Hh), flags=cv2.INTER_LANCZOS4 | cv2.WARP_INVERSE_MAP,
                         borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))
    del ia
    # os tons da final: a baixa frequência na escala da entrada, ampliada (em faixas)
    hb = int(round(Hh / s))
    ref0 = cv2.warpAffine(entrada, np.array([[1, 0, 0], [0, 1, -(Ya3 - Yia)]], np.float64), (Wc, hb),
                          flags=cv2.INTER_LINEAR, borderValue=(255, 255, 255)).astype(np.float32)
    peq = cv2.resize(out, (Wc, hb), interpolation=cv2.INTER_AREA).astype(np.float32)
    sg = q["tom_sigma_px"]
    corr = cv2.resize(cv2.GaussianBlur(ref0, (0, 0), sg) - cv2.GaussianBlur(peq, (0, 0), sg), (L, Hh),
                      interpolation=cv2.INTER_CUBIC)
    for y in range(0, Hh, 1024):
        out[y:y + 1024] = np.clip(np.round(out[y:y + 1024].astype(np.float32) + corr[y:y + 1024]), 0, 255
                                  ).astype(np.uint8)
    del corr
    # os vasos que a IA borrou (12/11): refeitos com a entrada ampliada, antes dos tracejados e dos textos
    import regras_1211_casaa as RG
    out, sem_tracos = RG.vasos_12k(PAV, img, entrada, out, s, X0, Yia, Ya3)
    if PAV == "Terreo":
        # as peças da biblioteca (12/11): a zona refeita da final e as peças nítidas, na escala do 12K
        import biblioteca_terreo_casaa_1211 as BT
        out = BT.pecas_12k(img, entrada, out, s, X0, Yia, Ya3)
        # os pedidos de 12/11 à noite: o Bege do pergolado, os riscos dos brises, a porta do banho varanda, a borda do
        # deck e da escada (o rótulo do JARDIM vai pelos dados)
        import pedidos_terreo_casaa_1211c as P3
        out = P3.doze(out, s, X0, Ya3)
    Fq = np.array([[s, 0, -s * X0], [0, s, -s * Ya3]], np.float64)
    # o fundo: branco puro fora da planta
    gq = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    fundo = (gq >= 254).astype(np.uint8)
    _, lab = cv2.connectedComponents(fundo)
    fundo = (lab == lab[0, 0]).astype(np.uint8)
    kk = 2 * q["fundo_folga_px"] + 1
    fundo = cv2.erode(fundo, np.ones((kk, kk), np.uint8)).astype(np.float32)
    tr = cv2.imread(str(TRACOS))
    alfa_tr = tr[..., 0].astype(np.float32) / 255
    alfa_tr[sem_tracos] = 0
    sai_cl = RG.claraboia_sai(PAV)          # a claraboia sem o X, só o tracejado horizontal (12/11)
    if sai_cl is not None:
        alfa_tr[sai_cl] = 0
    cor_tr = np.where(tr[..., 1] > 127, np.float32(TA.FINOS_TA["claro"][0]), np.float32(TA.FINOS_TA["escuro"][0]))
    sf = 2.0 * L / Wa0
    for y in range(0, Hh, 1024):
        y1 = min(Hh, y + 1024)
        pad = int(4 * sf) + 2
        ya, yb = max(0, y - pad), min(Hh, y1 + pad)
        Ft = Fq.copy()
        Ft[1, 2] -= ya
        fa = cv2.warpAffine(fundo, Ft, (L, yb - ya), flags=cv2.INTER_LINEAR, borderValue=1.0)
        fa = cv2.GaussianBlur(fa, (0, 0), sf)[y - ya:y1 - ya, :, None]
        reg = out[y:y1].astype(np.float32) * (1 - fa) + 255 * fa
        # os tracejados finos: o alfa ampliado (cúbico), na cor deles
        Ft = Fq.copy()
        Ft[1, 2] -= y
        at = np.clip(cv2.warpAffine(alfa_tr, Ft, (L, y1 - y), flags=cv2.INTER_CUBIC, borderValue=0.0), 0, 1)[..., None]
        ct = cv2.warpAffine(cor_tr, Ft, (L, y1 - y), flags=cv2.INTER_NEAREST, borderValue=0.0)[..., None]
        reg = reg * (1 - at) + ct * at
        out[y:y1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)

    # os shafts (12/11): o vão claro e o X cinza fino, desenhados na escala do 12K (`regras_1211_casaa.shafts_12k`)
    out = RG.shafts_12k(PAV, img, out, s, X0, Ya3)

    # os textos e os símbolos, numa janela em volta de cada um
    def janela(cx, cy, meia):
        return (max(0, int(cx - meia)), max(0, int(cy - meia / 2)), min(L, int(cx + meia)), min(Hh, int(cy + meia / 2)))

    def com_alfa(a, cor, bx, by):
        h, w = a.shape[:2]
        reg = out[by:by + h, bx:bx + w].astype(np.float32)
        out[by:by + h, bx:bx + w] = np.clip(np.round(reg * (1 - a[..., None]) + np.float32(cor) * a[..., None]), 0,
                                            255).astype(np.uint8)
    meia = q["janela_px"] * s
    import rotulos_manuscritos_casaa as RM
    reforco = RM.MANUSCRITA["reforco_px"] * s
    if opcao == "B":
        fk, fk_est = fator_manuscrita(Q, rots, s, X0, Ya3)
        print(f"    Kalam: o mesmo fator {fk:.3f} em todos os rótulos"
              + (f" (menos {', '.join(f'{n} {v:.3f}' for n, v in fk_est.items())})" if fk_est else ""))
    for b in rots:
        if opcao == "B":
            _desenhar_janela(out, _itens_manuscrita(Q, b, s, X0, Ya3, fator=fk_est.get(b["nome"], fk)),
                             tuple(b["cor"]), reforco)
            continue
        u, v = Q.p2q(*b["pdf"])
        cx, cy = (u + b["desvio"][0] - X0) * s, (v + b["desvio"][1] - Ya3) * s
        bx, by, bx1, by1 = janela(cx, cy, meia)
        a = alfa_rotulo(Q, b, (by1 - by, bx1 - bx), s, X0 + bx / s, Ya3 + by / s)
        com_alfa(a, b["cor"], bx, by)
    for tipo, dados, cor in anot:
        if opcao == "B" and tipo == "txt":
            _desenhar_janela(out, _itens_anotacao_manuscrita(dados, s, X0, Ya3), tuple(cor), reforco)
            continue
        if tipo == "tri":
            cx, cy = np.mean(np.float32(dados), axis=0)
        else:
            _, x, y, alinhar = dados
            cx, cy = x + {"esquerda": 60, "direita": -60, "centro": 0}[alinhar], y
        cx, cy = (cx - X0) * s, (cy - Ya3) * s
        bx, by, bx1, by1 = janela(cx, cy, meia)
        a = alfa_anotacao(tipo, dados, (by1 - by, bx1 - bx), s, X0 + bx / s, Ya3 + by / s)
        com_alfa(a, cor, bx, by)
    saida = Path(str(SAIDA).format(opcao=opcao))
    saida.parent.mkdir(parents=True, exist_ok=True)
    dpi = int(round(L / (420 / 25.4)))
    Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB)).save(saida, quality=q["qualidade"], subsampling=0,
                                                               dpi=(dpi, dpi), optimize=True)
    cv2.imwrite(str(R / f"POE642_CasaA_PH_{PAV}_12K_opcao_{opcao}_previa.jpg"),
                cv2.resize(out, (2000, round(2000 * Hh / L)), interpolation=cv2.INTER_AREA), [cv2.IMWRITE_JPEG_QUALITY, 90])
    for nome, (x0, y0, x1, y1) in CONFERENCIA.items():
        u0, v0, u1, v1 = [int(round(t_)) for t_ in ((x0 - X0) * s, (y0 - Ya3) * s, (x1 - X0) * s, (y1 - Ya3) * s)]
        cr = out[v0:v1, u0:u1]
        ref = cv2.resize(img[y0:y1, x0:x1], (cr.shape[1], cr.shape[0]), interpolation=cv2.INTER_LANCZOS4)
        par = np.hstack([ref, np.full((cr.shape[0], 24, 3), 255, np.uint8), cr])
        cv2.imwrite(str(R / f"POE642_CasaA_PH_{PAV}_12K_opcao_{opcao}_conferencia_{nome}.jpg"),
                    cv2.resize(par, (par.shape[1] // 2, par.shape[0] // 2), interpolation=cv2.INTER_AREA),
                    [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"    {saida} {L}x{Hh} ({dpi} dpi na A3), {saida.stat().st_size / 1e6:.1f} MB")


# Os recortes da conferência (px da final): a final ampliada sem IA ao lado do 12K
CONFERENCIA = {"piscina_deck": (700, 320, 1360, 1150), "varanda_estar": (1480, 330, 2180, 910),
               "gourmet_cozinha": (1180, 1100, 2200, 1680), "hall_lavabo_escritorio": (2200, 330, 2640, 900),
               "garagem": (2180, 1100, 2720, 1660)}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="etapa", required=True)
    p = sub.add_parser("preparar")
    p.add_argument("--passos", required=True, help="a pasta dos passos de terreo_casaa_1011.py (passo_shaft.png)")
    d_ = sub.add_parser("diferencas")
    d_.add_argument("saida_ia", type=Path)
    c_ = sub.add_parser("corrigir")
    c_.add_argument("saida_ia", type=Path)
    c_.add_argument("destino", type=Path)
    m_ = sub.add_parser("montar12k")
    m_.add_argument("saida_topaz", type=Path)
    m_.add_argument("--largura", type=int, default=None)
    m_.add_argument("--opcao", choices=("A", "B", "AB"), default="AB")
    a = ap.parse_args()
    if a.etapa == "preparar":
        preparar(a.passos)
    elif a.etapa == "diferencas":
        diferencas(a.saida_ia)
    elif a.etapa == "corrigir":
        corrigir_ia(a.saida_ia, a.destino)
    else:
        for op in a.opcao:
            montar12k(a.saida_topaz, a.largura, op)

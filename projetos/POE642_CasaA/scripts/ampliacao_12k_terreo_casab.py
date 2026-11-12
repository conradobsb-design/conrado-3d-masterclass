"""O JPG em 12K do Térreo da Casa B (usuário, 12/11/26: "pode fazer o 12K do Térreo da Casa B"; regras de 10/11: "GERE A
IMAGEM EM 12K JPG. ISSO É REGRA PARA TODAS AS PLANTAS" e as duas letras, A na Inter e B na Kalam).

O roteiro do 12K do Subsolo da Casa B (`ampliacao_12k_subsolo_casab.py`: da IA só os pisos, o resto da casa da entrada
ampliada) com os textos e os símbolos do Térreo (`ampliacao_12k_terreo_casaa.py`: rótulos, triângulos e descrições
desenhados direto em 12K):
  1. A planta sem os textos: os passos de `pedidos_terreo_casab_1211.py` de `escadas` ao fim, de novo, sem as
     anotações (`terreo_casaa_1011.ANOTAR`: os triângulos e as descrições das 3 escadas e o triângulo da entrada) e sem
     desenhar os rótulos (`ROTULOS_TB["desenhar"] = False`: os rótulos antigos saem como na final, pelo piso ao lado, e os
     novos não entram); conferida igual à final fora dos textos. Roteiro: `sem_anotacoes_casab.py`.
  2. `preparar <a planta sem os textos>`: os rótulos que a final traz de antes (`ROTULOS_TB["manter"]`: SPA, PISCINA,
     PRAINHA, JARDIM DE INVERNO, JARDIM, ELEVADOR) achados na final pela forma e tirados pela conta do alfa
     (`ampliacao_a3_casaa.tirar`), com a área de cada texto refeita do entorno; os 32 rótulos desenhados pelo passo
     `rotulos` (`POE642_CasaB_PH_Terreo_rotulos_1211.json`), os manter, os 4 triângulos e as 3 descrições vão para os
     dados. A entrada da IA é o recorte da planta em 16:9 com a margem da A3.
  3. A entrada no Nano Banana Pro (4K, 16:9), com o prompt de ampliação fiel (`PROMPT`).
  4. `corrigir`: da IA ficam só os pisos (travertino, Bege Bahia, vinílico, o marrom, o deck, a pedra portuguesa e o
     gramado, no que é piso: a cor da base, fora das peças do PDF e no tom do piso do lugar; ambiente por ambiente, o que
     foge da entrada na cor ou na estrutura volta dela); todo o resto (paredes, portas, móveis, camas, louças, bancadas,
     a água, os carros, as árvores, os tracejados) volta da entrada ampliada.
  5. A saída corrigida no Topaz (High Fidelity V2), a 12288 de largura.
  6. `montar12k --opcao AB`: a saída alinhada à entrada, na A3 deitada (12288 x 8689); os tons da final; o fundo fora da
     planta em branco puro; os rótulos, os triângulos e as descrições desenhados em 12K (A na Inter, B na Kalam).

  python3 sem_anotacoes_casab.py <passo_bege_escadas.png> <saída sem textos> <pasta dos passos>
  python3 ampliacao_12k_terreo_casab.py preparar <saída sem textos>
  python3 ampliacao_12k_terreo_casab.py diferencas <saída do Nano Banana Pro>
  python3 ampliacao_12k_terreo_casab.py corrigir <saída do Nano Banana Pro> <corrigida>
  python3 ampliacao_12k_terreo_casab.py montar12k <saída do Topaz> [--opcao AB]
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
import final3840_casab as F                     # noqa: E402
import ampliacao_a3_casaa as AM                 # noqa: E402
import ampliacao_12k_terreo_casaa as Z          # noqa: E402
import pedidos_terreo_casab_1211 as P           # noqa: E402
import terreo_casaa_1011 as TC                  # noqa: E402

CASA_B = AQUI.parents[1] / "POE642_CasaB"
R = CASA_B / "renders"
FINAL = P.FINAL
ENTRADA_IA = R / "POE642_CasaB_PH_Terreo_12K_entrada_ia.png"
DADOS = R / "POE642_CasaB_PH_Terreo_12K_dados.json"
SAIDA = CASA_B / "entrega" / "POE642_CasaB_PH_Terreo_12K_opcao_{opcao}.jpg"

PROMPT = ("High-fidelity 4K upscale of the reference image, which is a top-down architectural humanized floor plan of a "
          "house ground floor (orthographic, viewed straight from above). Reproduce the reference EXACTLY: identical "
          "composition, framing, layout, scale and position of every element; same dark gray walls, doors, thresholds "
          "and glass partitions, the pool, spa and beach area with their water, the wooden decks and steps, the stone "
          "stepping slabs, all the furniture (sofas, armchairs, beds with their bedding, tables, chairs, stools, rugs), "
          "the kitchen and gourmet countertops, cooktops and appliances, bathroom fixtures, the elevator, the three cars "
          "in the garage, the trees and plants, the thin dashed lines and the pure white background. Do not add, "
          "remove, move, rotate, resize or redesign anything. Do not add any text, labels, numbers, arrows, triangles, "
          "symbols or people. Only increase resolution and detail: crisp straight wall edges and lines, sharp object "
          "edges, and fine realistic material textures matching the existing colors and tones exactly: light raw "
          "travertine with fine horizontal veining in the living, porch and halls, smooth light beige marble (Bege "
          "Bahia) with soft low-contrast veining on the pool surround and steps, warm wood vinyl planks (thin crisp "
          "joints, fine wood grain) in the bedrooms, closets and corridor, the uniform medium brown stone floor in the "
          "kitchen and service areas, warm wood deck boards (same direction and tone), the Portuguese stone paving in "
          "a fan pattern in the garage and driveway, and the dark olive-green lawn with very fine grass grain at the "
          "same small scale. Keep colors, brightness and contrast the same as the reference. Clean, photographic "
          "architectural presentation quality, no artifacts, no noise.")

# o recorte: a planta pelas linhas e colunas com mais de `linha_min` px não brancos (na final há uns pontos claros
# soltos acima e abaixo do lote, que esticariam a caixa além do 16:9)
RECORTE = {"branco": 245, "linha_min": 50}
# os pisos (a cor na base chapada) onde a IA fica; o resto da casa volta da entrada (`corrigir`): travertino, Bege
# Bahia, vinílico, o marrom, o deck e o gramado (a pedra portuguesa volta da entrada: a IA rachou o leque e mudou a
# escala das pedras)
PISOS_12K = {"pisos": ((202, 217, 220), (202, 218, 221), (124, 162, 200), (50, 66, 90), (99, 136, 174),
                       (80, 145, 110)),
             "desvio": 30, "croma": 0.035, "r": (0.55, 1.2), "pdf_folga_px": 2, "borda_px": 2}
# como no Subsolo: os tons da IA casados com os da entrada; ambiente por ambiente, o piso que foge na cor (ΔE mediano
# acima de `sala_max`) volta inteiro da entrada; nos que ficam, o que foge na estrutura (a IA inventou) também
CORRECAO = {"nitidez": (0.6, 1.2), "borda_px": 2.0, "tom_sigma_px": 2.5, "cor_sigma_px": 2.0, "sala_max": 15.0,
            "sala_min_px": 300, "estrutura": 8.0, "folga_px": 3, "da_entrada_px": {}}
CONFERENCIA = {"varanda_piscina": (590, 560, 1560, 1400), "suites": (950, 300, 2700, 920),
               "living_hall": (1480, 700, 2760, 1300), "cozinha_servico": (1550, 1250, 2310, 1880),
               "garagem_motorista": (2300, 1250, 3000, 1660)}


def quadro():
    with contextlib.redirect_stdout(io.StringIO()):
        return F.Quadro("Terreo")


def rotulos_b(Q):
    """Os rótulos do PDF do Térreo da Casa B (os do passo `rotulos`), no lugar dos da Casa A em
    `ampliacao_a3_casaa._rotulos` (o desenho em 12K da Casa A procura o rótulo por ali)."""
    return F.textos_rotulos(F.B.rotulos_casab(Q.pg, Q.p2q2000))


def _usar_rotulos_b(Q):
    rot = rotulos_b(Q)
    AM._rotulos = lambda Q_: rot
    return rot


def anotacoes():
    """Os triângulos e as descrições das 3 escadas (`ESCADAS_TB`) e o triângulo da entrada (`ENTRADA_TB`), como os passos
    `escadas` e `entrada` os desenham: [("tri", pts, cor)] e [("txt", (linhas, x, y, alinhar), cor)], px do quadro."""
    q = P.ESCADAS_TB
    out = []
    for nome in ("seis", "nove", "blocos"):
        e = q[nome]
        out.append(("tri", [list(map(float, p)) for p in TC.seta_tri(*e["tri_px"], e["dir"])], [30, 30, 30]))
        out.append(("txt", [list(e["texto"]), *e["txt_px"], e["alinhar"]], list(q["cor"])))
    e = P.ENTRADA_TB
    a0, a1 = e["abertura_px"]
    cx = e["soleira_px"][2] + e["recuo_px"] + e["comp"] / 2
    pts = TC.seta_tri(cx, (a0 + a1) / 2, (-1, 0), e["comp"], e["larg"])
    out.append(("tri", [list(map(float, p)) for p in pts], [30, 30, 30]))
    return out


def recortes(img):
    q, g12 = RECORTE, Z.G12
    Wa, _ = g12["a3"]
    m = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) < q["branco"]
    cols = np.nonzero(m.sum(axis=0) > q["linha_min"])[0]
    rows = np.nonzero(m.sum(axis=1) > q["linha_min"])[0]
    x0, y0, x1, y1 = int(cols.min()), int(rows.min()), int(cols.max()) + 1, int(rows.max()) + 1
    Wc = int(round((x1 - x0) * Wa / (Wa - 2 * g12["margem_px"])))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    X0 = int(round(cx - Wc / 2))
    Hia = int(round(Wc * g12["ia"][1] / g12["ia"][0]))
    Yia = int(round(cy - Hia / 2))
    if Yia < 0 or Yia + Hia > img.shape[0] or X0 < 0 or X0 + Wc > img.shape[1] or y1 - y0 > Hia:
        raise SystemExit(f"o recorte sai do quadro ou corta a planta: {X0},{Yia} {Wc}x{Hia}, planta {x0},{y0}-{x1},{y1}")
    return {"planta": (x0, y0, x1, y1), "X0": X0, "Wc": Wc, "Yia": Yia, "Hia": Hia}


# ----------------------------------------------------------------------------------------------------------------------
def preparar(sem_textos):
    Q = quadro()
    rot = _usar_rotulos_b(Q)
    final = cv2.imread(str(FINAL))
    limpa = cv2.imread(str(sem_textos))
    forma = final.shape[:2]
    # os 32 rótulos do passo `rotulos` (o desenho gravado) e os que a final traz de antes, achados nela
    rots = json.loads(P.ROTULOS_JSON.read_text())
    mant = [r for r in rot if r[0] in P.ROTULOS_TB["manter"]]
    with contextlib.redirect_stdout(io.StringIO()):
        achados = P._achar_rotulos(Q, final, mant, P.ROTULOS_TB)
    manter = []
    for a in achados:
        r1 = a["r1"]
        if a["nota"] < 0.6:
            print(f"    {r1[0]} em {tuple(round(v) for v in r1[2])}: não está na final (nota {a['nota']:.2f})")
            continue
        cheio = a["alfa"] > 0.9
        cor = [int(v) for v in np.median(final[cheio], axis=0)] if cheio.sum() > 5 else \
            ([20, 20, 20] if a["tom"] == "escuro" else [255, 255, 255])
        b = {"nome": r1[0], "pdf": [float(v) for v in r1[2]],
             "opc": {k: (list(v) if isinstance(v, tuple) else v) for k, v in a["opc"].items()},
             "desvio": [float(a["desvio"][0]), float(a["desvio"][1])], "cor": cor, "nota": round(float(a["nota"]), 3)}
        manter.append(b)
    cam_m = [(Z.alfa_rotulo(Q, b, forma), tuple(b["cor"])) for b in manter]
    limpa = AM.tirar(limpa, cam_m, Z.G12["cheio"])
    # a área de cada texto tirado (com folga) refeita do entorno: onde o desenho achado não casa px a px, sobraria a
    # sombra do texto
    txt = np.zeros(forma, np.uint8)
    for a_, _ in cam_m:
        txt |= (a_ > 0.02).astype(np.uint8)
    k = 2 * Z.G12["folga_texto_px"] + 1
    limpa = cv2.inpaint(limpa, cv2.dilate(txt, np.ones((k, k), np.uint8)) * 255, 4, cv2.INPAINT_TELEA)
    rots = rots + manter
    anot = anotacoes()
    rc = recortes(final)
    X0, Wc, Yia, Hia = rc["X0"], rc["Wc"], rc["Yia"], rc["Hia"]
    cv2.imwrite(str(ENTRADA_IA), limpa[Yia:Yia + Hia, X0:X0 + Wc])
    DADOS.write_text(json.dumps({"rotulos": rots, "anotacoes": anot, "recortes": rc}, ensure_ascii=False, indent=1)
                     + "\n")
    # conferência: os textos e os símbolos desenhados de volta sobre a limpa, contra a final
    camadas = [(Z.alfa_rotulo(Q, b, forma), tuple(b["cor"])) for b in rots]
    camadas += [(Z.alfa_anotacao(t, d, forma), tuple(c)) for t, d, c in anot]
    volta = AM.pintar(limpa, camadas)
    caixa = np.zeros(forma, bool)
    for a_, _ in camadas:
        caixa |= cv2.dilate((a_ > 0.02).astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
    dif = np.abs(volta.astype(np.int16) - final.astype(np.int16)).max(axis=2)
    print(f"[Térreo da Casa B] {len(rots)} rótulos ({len(rots) - len(manter)} do passo e {len(manter)} de antes: "
          f"{', '.join(b['nome'] for b in manter)}), {len(anot)} símbolos e descrições")
    print(f"    o redesenho contra a final: nas caixas dos textos {int(((dif > 24) & caixa).sum())} px com mais de 24 de "
          f"diferença; fora delas {int(((dif > 24) & ~caixa).sum())} px")
    x0, y0, x1, y1 = rc["planta"]
    cv2.imwrite(str(R / "POE642_CasaB_PH_Terreo_12K_sem_textos.jpg"),
                np.vstack([final[y0:y1, x0:x1], limpa[y0:y1, x0:x1]]), [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"    a planta {x0},{y0} - {x1},{y1}; o recorte da IA {X0},{Yia} {Wc}x{Hia} (16:9)")
    print(f"    {ENTRADA_IA}")


# ----------------------------------------------------------------------------------------------------------------------
def diferencas(saida_ia):
    Z.ENTRADA_IA, Z.DADOS, Z.R, Z.PAV = ENTRADA_IA, DADOS, R, "Terreo"
    m = Z.diferencas(saida_ia)
    viz = Z.R / "POE642_CasaA_PH_Terreo_12K_diferencas.jpg"
    if viz.exists():
        viz.rename(R / "POE642_CasaB_PH_Terreo_12K_diferencas.jpg")
    return m


def mascara_pecas(Q):
    """Dentro da casa e do lote, o que não é piso (a conta do Subsolo, `ampliacao_12k_subsolo_casab.mascara_pecas`)."""
    import um_pav_casaa_1111 as U
    q = PISOS_12K
    img = cv2.imread(str(FINAL))
    piso = np.zeros(img.shape[:2], bool)
    pdf = U._objetos_pdf(Q, U.PISOS_1111E["camadas_pdf"], q["pdf_folga_px"])
    par = U.dilatar(FA.paredes_pdf(Q) > 0.3, 1)
    I = img.astype(np.float32)
    n = I / np.maximum(I.sum(axis=2, keepdims=True), 1)
    for cor in q["pisos"]:
        mat = (Q.chapada == cor).all(axis=2) & ~par
        L = F.luz_robusta(img, mat & ~pdf, 0.5 * Q.px_m, desvio=q["desvio"])
        nL = L / np.maximum(L.sum(axis=2, keepdims=True), 1)
        r = I.mean(axis=2) / np.maximum(L.mean(axis=2), 1)
        piso |= mat & ~pdf & (np.abs(n - nL).max(axis=2) < q["croma"]) & (r > q["r"][0]) & (r < q["r"][1])
    piso = cv2.morphologyEx(piso.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    piso = cv2.erode(piso, np.ones((2 * q["borda_px"] + 1,) * 2, np.uint8)) > 0
    casa = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) < 254
    casa = cv2.dilate(casa.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
    return casa & ~piso


def corrigir_ia(saida_ia, destino):
    import ampliacao_12k_subsolo_casab as ZS
    ZS.ENTRADA_IA, ZS.DADOS, ZS.CORRECAO, ZS.quadro, ZS.mascara_pecas = ENTRADA_IA, DADOS, CORRECAO, quadro, mascara_pecas
    ZS.corrigir_ia(saida_ia, destino)
    # onde saíram os rótulos de antes (a água, os jardins, o elevador), a entrada tem o miolo refeito do entorno (borrado):
    # ali fica a textura da IA, nos tons da corrigida (o rótulo volta por cima em 12K)
    Q = quadro()
    _usar_rotulos_b(Q)
    d = json.loads(DADOS.read_text())
    rc = d["recortes"]
    X0, Yia, Wc, Hia = rc["X0"], rc["Yia"], rc["Wc"], rc["Hia"]
    final = cv2.imread(str(FINAL))
    zona = np.zeros(final.shape[:2], np.uint8)
    for b in d["rotulos"]:
        if "nota" in b:
            zona |= (Z.alfa_rotulo(Q, b, final.shape[:2]) > 0.02).astype(np.uint8)
    k = 2 * (Z.G12["folga_texto_px"] + 3) + 1
    zona = cv2.dilate(zona, np.ones((k, k), np.uint8))[Yia:Yia + Hia, X0:X0 + Wc].astype(np.float32)
    ia = cv2.imread(str(saida_ia))
    out = cv2.imread(str(destino)).astype(np.float32)
    entrada = cv2.imread(str(ENTRADA_IA))
    Hi, Wi = ia.shape[:2]
    M = Z._alinhar(ia, entrada)
    Tm = (np.diag([Wi / Wc, Hi / Hia, 1.0]) @ np.vstack([M.astype(np.float64), [0, 0, 1]]))[:2]
    m = cv2.GaussianBlur(cv2.warpAffine(zona, Tm, (Wi, Hi), flags=cv2.INTER_LINEAR), (0, 0), 2.0 * Wi / Wc)[..., None]
    sg = CORRECAO["tom_sigma_px"] * Wi / Wc
    iaf = ia.astype(np.float32)
    iaf = iaf + cv2.GaussianBlur(out, (0, 0), sg) - cv2.GaussianBlur(iaf, (0, 0), sg)
    out = out * (1 - m) + iaf * m
    cv2.imwrite(str(destino), np.clip(np.round(out), 0, 255).astype(np.uint8))
    print(f"    sob os {sum('nota' in b for b in d['rotulos'])} rótulos de antes: a textura da IA ({float(zona.mean()):.2%} "
          f"do recorte)")


# ----------------------------------------------------------------------------------------------------------------------
def montar12k(saida_topaz, largura=None, opcao="A"):
    """O 12K (`ampliacao_12k_terreo_casaa.montar12k`, sem os tracejados finos: aqui eles vêm da entrada)."""
    Q = quadro()
    _usar_rotulos_b(Q)
    rc = json.loads(DADOS.read_text())["recortes"]
    tracos = R / "POE642_CasaB_PH_Terreo_12K_tracejados_vazio.png"
    img = cv2.imread(str(FINAL))
    cv2.imwrite(str(tracos), np.zeros(img.shape, np.uint8))
    Z.FINAL, Z.ENTRADA_IA, Z.DADOS, Z.TRACOS, Z.SAIDA = FINAL, ENTRADA_IA, DADOS, tracos, SAIDA
    Z.R, Z.PAV, Z.NOME_PAV, Z.CONFERENCIA, Z.quadro = R, "Terreo_CasaB", "Térreo da Casa B", CONFERENCIA, quadro
    Z.G12 = dict(Z.G12, kalam_estreitos=["BH SERVIÇO", "BH MOTORISTA", "LAVABO", "BH. GOURMET", "BANHO GOURMET"])
    Z.montar12k(saida_topaz, largura, opcao)
    tracos.unlink()
    for arq in R.glob("POE642_CasaA_PH_Terreo_CasaB_12K_*"):
        arq.rename(R / arq.name.replace("POE642_CasaA_PH_Terreo_CasaB_12K_", "POE642_CasaB_PH_Terreo_12K_"))
    del rc


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="etapa", required=True)
    p = sub.add_parser("preparar")
    p.add_argument("sem_textos", type=Path, help="a planta sem os textos (sem_anotacoes_casab.py)")
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
        preparar(a.sem_textos)
    elif a.etapa == "diferencas":
        diferencas(a.saida_ia)
    elif a.etapa == "corrigir":
        corrigir_ia(a.saida_ia, a.destino)
    else:
        for op in a.opcao:
            montar12k(a.saida_topaz, a.largura, op)

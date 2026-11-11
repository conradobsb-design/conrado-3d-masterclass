"""O JPG em 12K do 1º Pavimento da Casa A (regra de 10/11: "GERE A IMAGEM EM 12K JPG. ISSO É REGRA PARA TODAS AS
PLANTAS", nas duas letras: A na Inter das pranchas e B na Kalam; usuário, 11/11: "termine os ajustes e gere o 12K em
seguida").

O mesmo roteiro do Térreo (`ampliacao_12k_terreo_casaa.py`, que este módulo usa com os nomes e as caixas do 1º
Pavimento), com duas diferenças na preparação:
  - os triângulos e as descrições das escadas (a em U e a caracol, `um_pav_casaa_1111.ESCADAS_1P`) saem refazendo os
    passos `escadas` e `floreira` (a partir do passo `portas`) sem as anotações (`terreo_casaa_1011.ANOTAR`): o que
    muda contra o passo `floreira` com as anotações entra na final (os passos de depois, pisos e retoques, não tocam
    nas escadas): a escada fica com o D apagado e os guarda-corpos, sem o desenho por cima;
  - os tracejados finos ficam na entrada da IA (no 1º Pavimento eles vêm no começo da final, com o Térreo nublado),
    então o alfa dos tracejados é vazio (o 12K não redesenha nenhum).
Os rótulos saem da final pela conta do alfa (`ampliacao_a3_casaa.tirar`) e voltam desenhados direto no 12K.

  python3 ampliacao_12k_1pav_casaa.py preparar --passos <pasta dos passos de um_pav_casaa_1111.py>
  python3 ampliacao_12k_1pav_casaa.py diferencas <saída do Nano Banana Pro>
  python3 ampliacao_12k_1pav_casaa.py corrigir <saída do Nano Banana Pro> <corrigida>
  python3 ampliacao_12k_1pav_casaa.py montar12k <saída do Topaz> [--opcao A|B|AB]
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
import final3840_casaa_1pav as P1               # noqa: E402
import ampliacao_a3_casaa as AM                 # noqa: E402
import ampliacao_12k_terreo_casaa as Z          # noqa: E402
import terreo_casaa_1011 as TA                  # noqa: E402
import um_pav_casaa_1111 as U                   # noqa: E402

R = Z.R
Z.PAV, Z.NOME_PAV = "1Pavimento", "1º Pavimento"
Z.FINAL = U.FINAL
Z.ENTRADA_IA = R / "POE642_CasaA_PH_1Pavimento_12K_entrada_ia.png"
Z.TRACOS = R / "POE642_CasaA_PH_1Pavimento_12K_tracejados.png"
Z.DADOS = R / "POE642_CasaA_PH_1Pavimento_12K_dados.json"
Z.SAIDA = FA.CASA / "entrega" / "POE642_CasaA_PH_1Pavimento_12K_opcao_{opcao}.jpg"
Z.G12 = dict(Z.G12, kalam_estreitos=[])


def _quadro():
    with contextlib.redirect_stdout(io.StringIO()):
        return U.quadro()


Z.quadro = _quadro

PROMPT = ("High-fidelity 4K upscale of the reference image, which is a top-down architectural humanized floor plan "
          "(orthographic, viewed straight from above) of the upper floor of a house, drawn over the faded, misty ground "
          "floor plan below it. Reproduce the reference EXACTLY: identical composition, framing, layout, scale and "
          "position of every element; same dark gray walls, sliding doors with walnut wood leaves and thin glass "
          "leaves, thin glass balustrades, the U-shaped staircase and the spiral staircase, the elevator, the shafts "
          "with their dashed X, the beds with white duvets and burgundy throws, the upholstered bench at the foot of "
          "each bed, nightstands, armchairs, the cream L-shaped boucle sofa with terracotta cushions, the walnut coffee "
          "table and the dark round side tables, the rugs, the desk with the open laptop and the wood-and-linen chair, "
          "the wardrobes with hangers, the bathroom fixtures, the carved "
          "raw travertine washbasins, bathtub, toilets and showers, the faded wooden pergola and the faded ground floor "
          "around the house, and the pure white background. Keep every thin dashed line exactly where it is. Do not "
          "add, remove, move, rotate, resize or redesign anything. Do not add any text, labels, numbers, arrows, "
          "triangles, symbols or people. Only increase resolution and detail: crisp straight wall edges and lines, "
          "sharp furniture edges, and fine realistic material textures matching the existing colors and tones exactly: "
          "warm wood vinyl planks (20 cm wide, thin crisp joints, fine wood grain) in the bedrooms and closets, clean "
          "light raw travertine with fine horizontal veining in the corridor, the family room and the bathrooms, "
          "smooth light beige marble (Bege Bahia) on the balconies with soft low-contrast veining, soft fabric on the "
          "beds and upholstery. Keep colors, brightness and contrast the same as the reference. Clean, photographic "
          "architectural presentation quality, no artifacts, no noise.")

# o que a IA trocou (11/11, saída do job 09c2bb19, conferida no mapa das diferenças e nos recortes): as cortinas
# franzidas viraram fileiras de contas, as folhas amadeiradas das portas mudaram de ripado, as camas (travesseiros, a
# manta, a do quarto de serviço), as cubas (a da bancada Danae e a do banho de serviço), os ralos e o canteiro do banho
# master, a cadeira e o laptop da escrivaninha da suíte 1, a janela de vidro da circulação e trechos de parede. Em vez
# de caixas, todas as peças da casa voltam da entrada (`pecas`: dentro da pegada, tudo o que não é piso: os móveis, as
# louças, as bancadas, as portas, os vidros, as paredes, as escadas); da IA ficam os pisos (vinílico, travertino bruto e
# Bege Bahia, no que é piso, com a mesma conta do passo `pisos_1111e`) e o entorno (o Térreo nublado e o pergolado)
Z.CORRIGIR_PX = {}
Z.CORRIGIR_MASCARAS = {"pecas": "pecas"}
PECAS_12K = {"pisos": ((79, 120, 168), (202, 217, 220), (232, 232, 232)), "desvio": 30, "croma": 0.035,
             "r": (0.55, 1.2), "pdf_folga_px": 2, "borda_px": 2}
_mascara_terreo = Z._mascara


def _mascara_1p(Q, chave):
    """As máscaras do 1º Pavimento para a correção da saída da IA (`pecas`); as outras como no Térreo."""
    if chave != "pecas":
        return _mascara_terreo(Q, chave)
    import final3840_casab as F
    q = PECAS_12K
    img = cv2.imread(str(Z.FINAL))
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
    # as juntas e os veios do piso (finos) contam como piso; o que sobra são as peças
    piso = cv2.morphologyEx(piso.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    piso = cv2.erode(piso, np.ones((2 * q["borda_px"] + 1,) * 2, np.uint8)) > 0
    casa = cv2.dilate((Q.pegada > 0).astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
    return casa & ~piso


# (11/11, a 6ª leva e o vinílico da foto sobre a mesma saída do Nano Banana Pro, job 09c2bb19) o que mudou na entrada
# contra a que a IA viu (`MUDOU_12K["antes"]`: os degraus, a caracol, as folhas das portas, a saleta, a cadeira e o
# vinílico) vem da entrada nova; e os arcos das portas (o setor de cada arco do PDF, que a IA desenhava no piso, R3)
MUDOU_12K = {"antes": None, "limiar": 10, "folga_px": 3}
ARCOS_12K = {"camada": "ARQ_PAREDE", "lado_pt": (15.0, 90.0), "folga_px": 4}


def _mascara_mudou(Q):
    rc = json.loads(Z.DADOS.read_text())["recortes"]
    X0, Yia = rc["X0"], rc["Yia"]
    a0, a1 = cv2.imread(str(MUDOU_12K["antes"])), cv2.imread(str(Z.ENTRADA_IA))
    d = (np.abs(a0.astype(np.int16) - a1.astype(np.int16)).max(axis=2) > MUDOU_12K["limiar"]).astype(np.uint8)
    k = 2 * MUDOU_12K["folga_px"] + 1
    d = cv2.dilate(d, np.ones((k, k), np.uint8))
    m = np.zeros((Q.H, Q.W), bool)
    m[Yia:Yia + d.shape[0], X0:X0 + d.shape[1]] = d > 0
    return m


def _mascara_arcos(Q):
    q = ARCOS_12K
    m = np.zeros((Q.H, Q.W), np.uint8)
    for d in Q.desenhos:
        r = d["rect"]
        if d.get("layer") == q["camada"] and d["type"] == "s" and d["items"] and all(it[0] == "c" for it in d["items"]) \
                and abs(r.width - r.height) < 4 and q["lado_pt"][0] < max(r.width, r.height) < q["lado_pt"][1]:
            for c in Q.caminhos(d):
                c = np.float64(c)
                x0, y0 = c.min(axis=0)
                x1, y1 = c.max(axis=0)
                meio = c[len(c) // 2]
                cantos = np.array([[x0, y0], [x1, y0], [x1, y1], [x0, y1]])
                centro = cantos[np.argmax(np.hypot(*(cantos - meio).T))]      # o centro: o canto mais longe do meio
                cv2.fillPoly(m, [np.int32(np.round(np.vstack([centro[None], c])))], 1)
                cv2.polylines(m, [np.int32(np.round(c))], False, 1, 3)
    k = 2 * q["folga_px"] + 1
    return cv2.dilate(m, np.ones((k, k), np.uint8)) > 0


def _mascara_1p_todas(Q, chave):
    if chave == "mudou":
        return _mascara_mudou(Q)
    if chave == "arcos":
        return _mascara_arcos(Q)
    return _mascara_1p(Q, chave)


Z._mascara = _mascara_1p_todas
Z.CONFERENCIA = {"suites_3_2": (1490, 320, 2100, 1220), "sala_intima_escada": (1980, 880, 2580, 1280),
                 "master_banho": (1200, 1190, 1960, 1660), "suite_1_varanda": (2150, 1100, 2790, 1660)}


def anotacoes_1p(Q):
    """Os triângulos e as descrições das duas escadas, em px do quadro, como os desenha `um_pav_casaa_1111.escadas_1p`."""
    q = U.ESCADAS_1P
    u, c = q["u"], q["caracol"]
    out = [("tri", [list(map(float, p)) for p in TA.seta_tri(*u["tri_px"], u["dir"])], (30, 30, 30)),
           ("txt", (list(u["texto"]), *u["txt_px"], u["alinhar"]), q["cor_texto"])]
    cx, cy = Q.p2q(*P1.CARACOL_1P["centro"])
    ang = np.radians(c["ang"])
    rm = c["raio_pt"] * FA.PT_PX
    tx, ty = cx + rm * np.cos(ang), cy - rm * np.sin(ang)
    sg = c.get("sentido", 1)
    pts = TA.seta_tri(tx, ty, (sg * np.sin(ang), sg * np.cos(ang)), *c["tri"])
    out += [("tri", [list(map(float, p)) for p in pts], (30, 30, 30)),
            ("txt", (list(c["texto"]), *c["txt_px"], c["alinhar"]), q["cor_texto"])]
    return out


def preparar(passos):
    Q = _quadro()
    img = cv2.imread(str(Z.FINAL))
    # a final sem os triângulos e as descrições: os passos `escadas` e `floreira` de novo, a partir do passo `portas`,
    # sem as anotações; o que eles mudam (contra o passo `floreira` com as anotações) entra na final, que tem os passos
    # seguintes (`pisos_1111e`, `retoques_1111e`), que não tocam nas escadas
    sem = cv2.imread(str(Path(passos) / "passo_portas.png"))
    TA.ANOTAR["sim"] = False
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            sem = U.floreira_1p(Q, U.escadas_1p(Q, sem))
            # (11/11) os passos de depois (pisos, retoques, degraus) também mexem nas escadas (os degraus da escada em
            # U, a caracol): eles rodam sobre a versão sem as anotações, e o trecho delas vem dali
            sem_fim = U.correcoes(sem, "pisos_1111e")
    finally:
        TA.ANOTAR["sim"] = True
    com = cv2.imread(str(Path(passos) / "passo_floreira.png"))
    anot = cv2.dilate((np.abs(sem.astype(np.int16) - com.astype(np.int16)).max(axis=2) > 0).astype(np.uint8),
                      np.ones((5, 5), np.uint8)) > 0
    base = img.copy()
    base[anot] = sem_fim[anot]
    fora = int((np.abs(sem_fim.astype(np.int16) - img.astype(np.int16)).max(axis=2)[~anot] > 6).sum())
    print(f"    a versão sem anotações contra a final, fora delas: {fora} px com mais de 6 de diferença")
    dif = np.abs(base.astype(np.int16) - img.astype(np.int16)).max(axis=2)
    # sem tracejados a redesenhar: o alfa vazio
    cv2.imwrite(str(Z.TRACOS), np.zeros(img.shape, np.uint8))
    rots = Z.rotulos(Q, img)
    camadas = [(Z.alfa_rotulo(Q, b_, img.shape[:2]), tuple(b_["cor"])) for b_ in rots]
    limpa = AM.tirar(base, camadas, Z.G12["cheio"])
    txt = np.zeros(img.shape[:2], np.uint8)
    for a, _ in camadas:
        txt |= (a > 0.02).astype(np.uint8)
    k = 2 * Z.G12["folga_texto_px"] + 1
    limpa = cv2.inpaint(limpa, cv2.dilate(txt, np.ones((k, k), np.uint8)) * 255, 4, cv2.INPAINT_TELEA)
    anot = anotacoes_1p(Q)
    rc = Z.recortes(img)
    X0, Wc, Yia, Hia = rc["X0"], rc["Wc"], rc["Yia"], rc["Hia"]
    cv2.imwrite(str(Z.ENTRADA_IA), limpa[Yia:Yia + Hia, X0:X0 + Wc])
    Z.DADOS.write_text(json.dumps({"rotulos": rots, "anotacoes": anot, "recortes": rc}, ensure_ascii=False, indent=1)
                       + "\n")
    volta = AM.pintar(limpa, camadas)
    d2 = np.abs(volta.astype(np.int16) - base.astype(np.int16)).max(axis=2)
    print(f"[1º Pavimento] {len(rots)} rótulos ({', '.join(b_['nome'] for b_ in rots)}), {len(anot)} símbolos e "
          f"descrições (fora da entrada: {int((dif > 24).sum())} px); o redesenho dos rótulos contra a base: "
          f"{int((d2 > 24).sum())} px com mais de 24 de diferença")
    x0, y0, x1, y1 = rc["planta"]
    cv2.imwrite(str(R / "POE642_CasaA_PH_1Pavimento_12K_sem_textos.jpg"),
                np.hstack([img[y0:y1, x0:x1], limpa[y0:y1, x0:x1]]), [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"    a planta {x0},{y0} - {x1},{y1}; o recorte da IA {X0},{Yia} {Wc}x{Hia} (16:9)")
    print(f"    {Z.ENTRADA_IA}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="etapa", required=True)
    p = sub.add_parser("preparar")
    p.add_argument("--passos", required=True, help="a pasta dos passos de um_pav_casaa_1111.py (passo_portas.png)")
    d_ = sub.add_parser("diferencas")
    d_.add_argument("saida_ia", type=Path)
    c_ = sub.add_parser("corrigir")
    c_.add_argument("saida_ia", type=Path)
    c_.add_argument("destino", type=Path)
    c_.add_argument("--entrada_antes", type=Path, default=None,
                    help="a entrada que a IA viu: o que mudou na entrada nova vem dela (`MUDOU_12K`), e os arcos")
    m_ = sub.add_parser("montar12k")
    m_.add_argument("saida_topaz", type=Path)
    m_.add_argument("--largura", type=int, default=None)
    m_.add_argument("--opcao", choices=("A", "B", "AB"), default="AB")
    a = ap.parse_args()
    if a.etapa == "preparar":
        preparar(a.passos)
    elif a.etapa == "diferencas":
        Z.diferencas(a.saida_ia)
    elif a.etapa == "corrigir":
        if a.entrada_antes:
            MUDOU_12K["antes"] = a.entrada_antes
            Z.CORRIGIR_MASCARAS = dict(Z.CORRIGIR_MASCARAS, mudou="mudou", arcos="arcos")
        Z.corrigir_ia(a.saida_ia, a.destino)
    else:
        for op in a.opcao:
            Z.montar12k(a.saida_topaz, a.largura, op)

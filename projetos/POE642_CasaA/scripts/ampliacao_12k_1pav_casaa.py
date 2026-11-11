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
          "table and the dark round side tables, the rugs, the wardrobes with hangers, the bathroom fixtures, the carved "
          "raw travertine washbasins, bathtub, toilets and showers, the faded wooden pergola and the faded ground floor "
          "around the house, and the pure white background. Keep every thin dashed line exactly where it is. Do not "
          "add, remove, move, rotate, resize or redesign anything. Do not add any text, labels, numbers, arrows, "
          "triangles, symbols or people. Only increase resolution and detail: crisp straight wall edges and lines, "
          "sharp furniture edges, and fine realistic material textures matching the existing colors and tones exactly: "
          "warm wood vinyl planks in the bedrooms, closets and living area, light raw travertine in the bathrooms, "
          "smooth light beige marble (Bege Bahia) on the balconies with soft low-contrast veining, soft fabric on the "
          "beds and upholstery. Keep colors, brightness and contrast the same as the reference. Clean, photographic "
          "architectural presentation quality, no artifacts, no noise.")

# os trechos que a IA trocar (px da final), conferidos no mapa das diferenças: voltam da entrada (preenchido depois de
# ver a saída da IA)
Z.CORRIGIR_PX = {}
Z.CORRIGIR_MASCARAS = {}
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
    pts = TA.seta_tri(tx, ty, (np.sin(ang), np.cos(ang)), *c["tri"])
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
    finally:
        TA.ANOTAR["sim"] = True
    com = cv2.imread(str(Path(passos) / "passo_floreira.png"))
    anot = cv2.dilate((np.abs(sem.astype(np.int16) - com.astype(np.int16)).max(axis=2) > 0).astype(np.uint8),
                      np.ones((5, 5), np.uint8)) > 0
    base = img.copy()
    base[anot] = sem[anot]
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
        Z.corrigir_ia(a.saida_ia, a.destino)
    else:
        for op in a.opcao:
            Z.montar12k(a.saida_topaz, a.largura, op)

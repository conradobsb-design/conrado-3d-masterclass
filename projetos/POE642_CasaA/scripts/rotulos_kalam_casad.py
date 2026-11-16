"""A opção B da Casa D: os rótulos na letra Kalam (16/11, usuário: "precisamos ter a versão B com rótulos na outra fonte"),
como a opção B da Casa C (`rotulos_kalam_casac`, de onde vêm a busca, o apagar e o desenho).

- No **Térreo**, desde 16/11 todos os rótulos são escritos no padrão das casas (`rotulos_padrao_casad_1611`) e vêm das
  próprias linhas (texto, fonte, corpo, meio, base), com as descrições das escadas; antes, os do motor eram achados na
  final pela forma (`rotulos_kalam_casac.achar`) e só os da revisão de 15/11 vinham das linhas (`escritos_1511`).
- No **Subsolo**, todos os rótulos foram reescritos (`biblioteca_subsolo_casad_1511.ROTULOS`) e vêm das linhas, com a
  descrição da escada.

Cada linha sai inteira (`rotulos_kalam_casac.apagar`, o piso deslocado mais parecido) e volta na Kalam no mesmo meio e na
mesma linha de base, um corpo só em todos os rótulos, a mesma cor (`rotulos_kalam_casac.desenhar`); as setas, os D e os
S ficam. A final sem os rótulos é a entrada do Topaz da opção B do 12K; os dados das linhas vão para
`POE642_CasaD/renders/POE642_CasaD_PH_<pav>_rotulos_kalam.json`.

  python3 rotulos_kalam_casad.py <Terreo|Subsolo> [--entrada <png>] [--saida <png da opção B>] [--limpa <png sem rótulos>]
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
import rotulos_kalam_casac as KC                 # noqa: E402

R = AQUI.parents[1] / "POE642_CasaD" / "renders"
# os rótulos do PDF que a revisão de 15/11 reescreveu (saem da busca: vêm das linhas)
REESCRITOS_T = ("GARAGEM", "DCE TÉRREO", "DCE TERREO", "LOUCEIRO", "DESPENSA")


def final(pav):
    return R / f"POE642_CasaD_PH_{pav}_final_rotulos.png"


def dados(pav):
    return R / f"POE642_CasaD_PH_{pav}_rotulos_kalam.json"


def quadro(pav):
    if pav == "Terreo":
        import biblioteca_terreo_casad_1511 as TD
        return TD.quadro()
    import biblioteca_subsolo_casad_1511 as SD
    return SD.quadro()


def _escadas(escadas):
    """As linhas das descrições das escadas (`pedidos_terreo_casac_1311._escada`)."""
    import final3840_casaa as FA
    import pedidos_subsolo_casac_1311 as PS
    from rodape_entrega import FONTES
    e = FA.ESCADA_A
    fonte = str(FONTES / e["fonte"])
    out = []
    for q in escadas:
        ll = [(t, fonte, e["corpo_px"], q["centro_x"], q["base_y"] + i * PS.ENTRELINHA) for i, t in enumerate(q["texto"])]
        out.append((f"escada: {q['nome']}", ll, list(e["cor_texto"])))
    return out


def escritos(pav):
    """Os rótulos escritos pelos scripts: [(nome, linhas (texto, fonte, corpo, meio, base), cor)]. No Térreo, desde 16/11,
    todos (`rotulos_padrao_casad_1611`, o padrão das casas) e as descrições das escadas."""
    if pav == "Terreo":
        import biblioteca_terreo_casad_1511 as TD
        import rotulos_padrao_casad_1611 as RP
        return RP.linhas() + _escadas(TD.ESCADAS)
    return escritos_1511(pav)


def escritos_1511(pav):
    """Os rótulos que os scripts de 15/11 escreveram (no Térreo, os outros vinham do motor)."""
    from PIL import ImageFont
    from rodape_entrega import FONTES
    reg = str(FONTES / "Inter-Regular.otf")
    out = []
    if pav == "Terreo":
        import biblioteca_terreo_casad_1511 as TD
        q = TD.CLOSETS
        for nome, (x0, y0, x1, y1), (cx, base) in q["rotulos"]:
            area = (x1 - x0) * (y1 - y0) / TD.PX_M ** 2
            txt = f"A: {area:.2f} m²".replace(".", ",")
            out.append((nome, [(nome, reg, q["corpo"][0], cx, base), (txt, reg, q["corpo"][1], cx, base + q["entrelinha"])],
                        list(q["cor"])))
        g = TD.ROTULOS_NOVOS["garagem"]
        corpo = 400 * g["largura"] / ImageFont.truetype(reg, 400).getlength(g["linhas"][0][0])
        out.append(("GARAGEM", [(t, reg, corpo, cx, b) for t, cx, b in g["linhas"]], list(g["cor"])))
        d = TD.ROTULOS_NOVOS["dce"]
        out.append(("DCE TÉRREO", [(t, reg, d["corpo"], cx, b) for t, cx, b in d["linhas"]], list(d["cor"])))
        a = TD.ROTULOS_NOVOS["armarios"]
        f400 = ImageFont.truetype(reg, 400)
        corpo_a = min(400 * a["largura"] / (f400.getbbox(t[0])[2] - f400.getbbox(t[0])[0]) for t, _, _ in a["itens"])
        for linhas_, (cx, cy), _ in a["itens"]:
            e = a["entrelinha"] * corpo_a
            b0 = cy - ((len(linhas_) - 1) * e - a["altura"] * corpo_a) / 2
            out.append((linhas_[0], [(t, reg, corpo_a, cx, b0 + i * e) for i, t in enumerate(linhas_)], list(a["cor"])))
        out += _escadas(TD.ESCADAS)
    else:
        import biblioteca_subsolo_casad_1511 as SD
        q = SD.ROTULOS
        f400 = ImageFont.truetype(reg, 400)
        for it in q["itens"]:
            if "corpo" in it:
                corpo = it["corpo"]
            else:
                l_, _, r_, _ = f400.getbbox(it["linhas"][0])
                corpo = 400 * it["largura"] / (r_ - l_)
            n, e = len(it["linhas"]), q["entrelinha"] * corpo
            cx, cy = it["centro"]
            b0 = cy - ((n - 1) * e - q["altura"] * corpo) / 2
            out.append((it["linhas"][0], [(t, reg, corpo, cx, b0 + i * e) for i, t in enumerate(it["linhas"])],
                        list(q[it["cor"]])))
        out += _escadas(SD.SETA)
    return out


def preparar(pav, img):
    """(a final sem os rótulos, os dados das linhas)."""
    forma = img.shape[:2]
    camadas, linhas, caixas = [], [], []
    for nome, ll, cor in escritos(pav):
        a = KC._alfa_texto_linhas(ll, forma, None)
        camadas.append((a, tuple(cor)))
        linhas.append({"nome": nome, "cor": cor, "linhas": KC._geometria(a, [x[0] for x in ll])})
        ys, xs = np.nonzero(a > 0.02)
        caixas.append((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    if pav == "Terreo_motor":                      # (até 16/11; desde então o Térreo tem todos os rótulos escritos)
        import biblioteca_terreo_casad_1511 as TD
        # o ² do SPA (desenhado à parte): sai com o rótulo; a linha da Kalam leva o ²
        q = TD.SPA_M2
        from rodape_entrega import FONTES
        a2 = KC._alfa_texto_linhas([("²", str(FONTES / "Inter-Regular.otf"), q["corpo"], q["cx"], q["base"])], forma,
                                   None)
        camadas.append((a2, tuple(q["cor"])))
        KC.quadro = quadro
        with contextlib.redirect_stdout(io.StringIO()) as log:
            _, rots = KC.achar(pav, img)
        for b in rots:
            if b["nome"] in REESCRITOS_T:
                continue
            ys, xs = np.nonzero(b["_alfa"] > 0.02)
            cx_ = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
            if any(min(cx_[2], c[2]) > max(cx_[0], c[0]) and min(cx_[3], c[3]) > max(cx_[1], c[1]) for c in caixas):
                continue                                # cai sobre um rótulo escrito: é ele
            ll = b["linhas"]
            if b["nome"] == "SPA" and ll and ll[-1][0].endswith(" m"):
                ll[-1] = (ll[-1][0] + "²",) + tuple(ll[-1][1:])
            camadas.append((b["_alfa"], tuple(b["cor"])))
            linhas.append({"nome": b["nome"], "cor": b["cor"], "linhas": ll})
        fora = [l_ for l_ in log.getvalue().splitlines() if "não achado" in l_]
        if fora:
            print("\n".join(fora))
    limpa = KC.apagar(img, camadas)
    sem = [b["nome"] for b in linhas if not b["linhas"]]
    if sem:
        print(f"    sem as linhas (fica sem Kalam): {', '.join(sem)}")
    print(f"    {pav}: {len(linhas)} rótulos na Kalam")
    return limpa, linhas


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pav", choices=("Terreo", "Subsolo"))
    ap.add_argument("--entrada")
    ap.add_argument("--saida")
    ap.add_argument("--limpa")
    ap.add_argument("--dados")
    a = ap.parse_args()
    img = cv2.imread(a.entrada or str(final(a.pav)))
    limpa, linhas = preparar(a.pav, img)
    arq = Path(a.dados) if a.dados else dados(a.pav)
    arq.write_text(json.dumps(linhas, ensure_ascii=False, indent=1) + "\n")
    if a.limpa:
        cv2.imwrite(a.limpa, limpa)
    KC.dados = lambda pav: arq
    out = KC.desenhar(limpa.copy(), a.pav, 1.0, 0.0, 0.0)
    saida = a.saida or str(R / f"POE642_CasaD_PH_{a.pav}_final_rotulos_B.png")
    cv2.imwrite(saida, out)
    print(f"    {saida}")


if __name__ == "__main__":
    main()

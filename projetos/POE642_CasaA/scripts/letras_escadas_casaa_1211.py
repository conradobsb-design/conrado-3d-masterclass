"""O S ou o D logo abaixo da seta das escadas do Subsolo e do 1º Pavimento da Casa A (12/11).

Usuário, depois do Térreo ("ADICIONE AS ESCADAS O "S" OU "D" DE SUBIR OU DESCER, LOGO ABAIXO DA SETA",
`pedidos_terreo_casaa_1211c.letras`): "APLIQUE O S E D NO SUBSOLO E 1º PAVIMENTO".
  - Subsolo: o S sob a seta do SOBE PARA O DECK, na fonte, no corpo e na cor da descrição: é a última camada de
    `ampliacao_a3_casaa.escada_camadas` (`cliente_subsolo_casaa_0511.ESCADA_CS["letra"]`), a mesma que a A3 4K, o 12K
    (A na Inter, B na Kalam, `letra_kalam`) e a letra manuscrita (`rotulos_manuscritos_casaa`) desenham.
  - 1º Pavimento: o D sob a seta da escada em U (DESCE PARA O HALL INTERNO) e da caracol (DESCE PARA A ÁREA DE
    SERVIÇO), no corpo e na cor das descrições, como as do Térreo: uma anotação "txt" a mais nos dados do 12K do
    1º Pavimento (`ampliacao_12k_1pav_casaa`), que o `montar12k` desenha (A na Inter, B na Kalam).

  python3 letras_escadas_casaa_1211.py Subsolo|1Pavimento [--antes <png>]
Sem --antes, parte da final do commit `ANTES_COMMIT` (sem as letras) e grava a final do pavimento e o antes e depois
`renders/POE642_CasaA_PH_<pavimento>_1211_letras_escadas_antes_depois.jpg`.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

R = AQUI.parent / "renders"
RAIZ_GIT = AQUI.parent.parent.parent
ANTES_COMMIT = "f37669e"
FINAIS = {"Subsolo": R / "POE642_CasaA_PH_Subsolo_final_rotulos.png",
          "1Pavimento": R / "POE642_CasaA_PH_1Pavimento_v7_final_rotulos.png"}
LETRAS_1P = {"escadas": [((2261.5, 1046.0), "D"), ((2006.4, 1568.5), "D")], "folga_px": 2.5}
CAIXAS = {"Subsolo": [(1030, 1060, 1180, 1130)], "1Pavimento": [(2235, 1020, 2400, 1080), (1960, 1530, 2160, 1625)]}


def subsolo(img):
    import ampliacao_a3_casaa as AM
    a, cor = AM.escada_camadas(img.shape[:2])[-1]
    ys, xs = np.nonzero(a > 0.3)
    print(f"    Subsolo: S em x {xs.min()}-{xs.max()}, y {ys.min()}-{ys.max()}")
    return AM.pintar(img, [(a, cor)])


def um_pav(img, q=LETRAS_1P, gravar=True):
    import ampliacao_12k_1pav_casaa as Z1
    import terreo_casaa_1011 as TA
    Z = Z1.Z
    forma = img.shape[:2]
    d = json.loads(Z.DADOS.read_text())
    d["anotacoes"] = [a for a in d["anotacoes"] if not (a[0] == "txt" and a[1][0] in (["S"], ["D"]))]
    tris = [np.float32(a[1]) for a in d["anotacoes"] if a[0] == "tri"]
    txts = [a for a in d["anotacoes"] if a[0] == "txt"]
    out = img.astype(np.float32)
    feitos = []
    for (cx, cy), L in q["escadas"]:
        t = min(tris, key=lambda p: float(np.hypot(*(p.mean(axis=0) - (cx, cy)))))
        cor = min(txts, key=lambda a: float(np.hypot(a[1][1] - cx, a[1][2] - cy)))[2]
        x = float(t[:, 0].min() + t[:, 0].max()) / 2
        topo = float(t[:, 1].max()) + q["folga_px"]
        dados = [[L], x, topo + 6.0, "centro"]
        a = Z.alfa_anotacao("txt", dados, forma)
        ys, xs = np.nonzero(a > 0.3)
        dados[2] += topo - ys.min()
        dados[1] += x - (xs.min() + xs.max()) / 2
        a = Z.alfa_anotacao("txt", dados, forma)
        out = TA.compor(out, a, tuple(cor))
        ys, xs = np.nonzero(a > 0.3)
        feitos.append(f"{L} em x {xs.min()}-{xs.max()}, y {ys.min()}-{ys.max()}")
        d["anotacoes"].append(["txt", dados, list(cor)])
    print(f"    1º Pavimento: {'; '.join(feitos)}")
    if gravar:
        Z.DADOS.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def antes_depois(pav, antes, depois):
    blocos = []
    for x0, y0, x1, y1 in CAIXAS[pav]:
        a = cv2.resize(antes[y0:y1, x0:x1], None, fx=4, fy=4, interpolation=cv2.INTER_LANCZOS4)
        b = cv2.resize(depois[y0:y1, x0:x1], None, fx=4, fy=4, interpolation=cv2.INTER_LANCZOS4)
        blocos.append(np.hstack([a, np.full((a.shape[0], 16, 3), 255, np.uint8), b]))
    W = max(b.shape[1] for b in blocos)
    blocos = [np.hstack([b, np.full((b.shape[0], W - b.shape[1], 3), 255, np.uint8)]) for b in blocos]
    sep = np.full((16, W, 3), 255, np.uint8)
    corpo = blocos[0]
    for b in blocos[1:]:
        corpo = np.vstack([corpo, sep, b])
    topo = np.full((40, W, 3), 255, np.uint8)
    cv2.putText(topo, "ANTES | DEPOIS", (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (40, 40, 40), 2, cv2.LINE_AA)
    arq = R / f"POE642_CasaA_PH_{pav}_1211_letras_escadas_antes_depois.jpg"
    cv2.imwrite(str(arq), np.vstack([topo, corpo]), [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"    {arq}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pavimento", choices=list(FINAIS))
    ap.add_argument("--antes")
    a = ap.parse_args()
    if a.antes:
        antes = cv2.imread(a.antes)
    else:
        rel = FINAIS[a.pavimento].relative_to(RAIZ_GIT)
        dado = subprocess.run(["git", "-C", str(RAIZ_GIT), "show", f"{ANTES_COMMIT}:{rel}"], capture_output=True,
                              check=True).stdout
        antes = cv2.imdecode(np.frombuffer(dado, np.uint8), cv2.IMREAD_COLOR)
    depois = subsolo(antes) if a.pavimento == "Subsolo" else um_pav(antes)
    cv2.imwrite(str(FINAIS[a.pavimento]), depois)
    print(f"    {FINAIS[a.pavimento]}")
    antes_depois(a.pavimento, antes, depois)


if __name__ == "__main__":
    main()

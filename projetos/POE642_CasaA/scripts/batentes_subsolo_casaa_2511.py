"""Casa A Subsolo: sem as linhas dos batentes nas portas do BH. FEM. e do BH. MASC. (25/11).

Usuário (com o recorte da parede de baixo da academia): "remova essas linhas de batentes das portas do subsolo da casa".

Os batentes (as pecinhas brancas do marco, na espessura da parede, nas pontas do vão) ganharam o contorno preto na rodada
das esquadrias de 19/11 (`esquadrias_pretas_1911`, commit c946cc5): duas na ponta da parede do meio (entre os dois vãos)
e duas nos tocos de parede, onde o contorno da folha subia pela espessura da parede. As outras portas do Subsolo não têm
batente contornado (conferidas no 12K: depósito, hall, sauna, circulação, BH serv., elevador).

Cada batente volta ao que era antes de c946cc5 (a parede termina limpa, sem o retângulo): final (e a manuscrita),
prancha e 12K A e B. Nos tocos, só a espessura da parede volta: a folha, abaixo da face da parede, fica com o seu
contorno fino.

No 12K saem também os resíduos antigos do render em volta desses vãos (`LIMPAR`).

  python3 batentes_subsolo_casaa_2511.py
  python3 batentes_subsolo_casaa_2511.py --so-limpar   # só a limpeza do 12K (os batentes já feitos)
"""
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import esquadrias_pretas_1911 as EP  # noqa: E402

PLANTA = "A_Subsolo"
REV = "c946cc5~1"            # antes da rodada das esquadrias de 19/11
FACE = 1514.7                # a face de baixo da parede (px da final), onde começa a folha
# (x0, y0, x1, y1) em px da final; `ate_face`: o limite de baixo é a face da parede (a folha fica)
BATENTES = [
    ((1548.0, 1497.0, 1556.0, 1518.0), False),   # ponta esquerda da parede do meio (vão do BH. FEM.)
    ((1804.0, 1497.0, 1812.0, 1518.0), False),   # ponta direita da parede do meio (vão do BH. MASC.)
    ((1493.0, 1497.0, 1502.0, FACE), True),      # toco da esquerda (a folha do BH. FEM.)
    ((1858.0, 1497.0, 1867.0, FACE), True),      # toco da direita (a folha do BH. MASC.)
]


def final_e_prancha():
    c, pav = PLANTA.split("_")
    for f in EP.PLANTAS[PLANTA]:
        im = cv2.imread(str(EP.PROJ / f))
        old = EP.git_img(f, REV)
        for (x0, y0, x1, y1), _ in BATENTES:
            X0, Y0, X1, Y1 = int(x0), int(y0), int(np.ceil(x1)), int(round(y1))
            im[Y0:Y1, X0:X1] = old[Y0:Y1, X0:X1]
        cv2.imwrite(str(EP.PROJ / f), im)
        if f == EP.PLANTAS[PLANTA][0]:
            novo = im
    pf = EP.PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_entrega.png"
    pr = cv2.imread(str(pf))
    pr[:2160] = novo
    cv2.imwrite(str(pf), pr)
    return novo


def doze_k(base):
    c, pav = PLANTA.split("_")
    dz = json.loads((EP.PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[PLANTA]
    for op in "AB":
        rel = f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_12K_opcao_{op}.jpg"
        pil = Image.open(EP.PROJ / rel)
        dpi = pil.info.get("dpi", (743, 743))
        im = cv2.cvtColor(np.array(pil.convert("RGB")), cv2.COLOR_RGB2BGR)
        del pil
        dado = subprocess.run(["git", "show", f"{REV}:projetos/{rel}"], cwd=EP.PROJ, capture_output=True,
                              check=True).stdout
        old = cv2.imdecode(np.frombuffer(dado, np.uint8), cv2.IMREAD_COLOR)
        cinza = cv2.cvtColor(old, cv2.COLOR_BGR2GRAY)
        for (x0, y0, x1, y1), ate_face in BATENTES:
            mapa, cc = EP.registro_12k(base, cinza, dz, (int(x0) - 100, int(y0) - 100, int(x1) + 100, int(y1) + 100))
            A0, B0 = mapa(x0, y0)
            A1, B1 = mapa(x1, y1)
            A0, B0, A1 = int(A0) - 2, int(B0) - 2, int(np.ceil(A1)) + 2
            B1 = int(round(B1)) if ate_face else int(np.ceil(B1)) + 2
            im[B0:B1, A0:A1] = old[B0:B1, A0:A1]
            print(f"   {op}: batente {x0:.0f},{y0:.0f} -> 12K {A0},{B0}-{A1},{B1} (registro {cc:.3f})")
        Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).save(EP.PROJ / rel, quality=95, subsampling=0, dpi=dpi)
        del im, old, cinza


# os resíduos antigos do render em volta dos vãos (já estavam antes de 19/11), no 12K: o tom claro na madeira nas pontas da
# parede do meio e os pontinhos brancos/laranja no piso do vão do BH. MASC. Cada caixa (px do 12K A) recebe a textura do
# mesmo piso deslocada `dx` px na mesma linha (as tábuas correm na horizontal), sem tocar a parede nem a folha.
LIMPAR = [((6080, 6005, 6168, 6066), -110),     # madeira na ponta esquerda da parede do meio
          ((6085, 6060, 6116, 6080), -110),     # o pontinho branco na divisa madeira/pedra, na mesma ponta
          ((7875, 6015, 7925, 6055), 80),       # madeira na ponta direita
          ((8195, 6066, 8238, 6128), -60),      # piso do vão do BH. MASC., junto ao toco
          ((8195, 6128, 8223, 6155), -60)]


def limpar_12k():
    c, pav = PLANTA.split("_")
    for op in "AB":
        rel = f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_12K_opcao_{op}.jpg"
        pil = Image.open(EP.PROJ / rel)
        dpi = pil.info.get("dpi", (743, 743))
        im = cv2.cvtColor(np.array(pil.convert("RGB")), cv2.COLOR_RGB2BGR)
        del pil
        for (x0, y0, x1, y1), dx in LIMPAR:
            m = 6
            reg = im[y0 - m:y1 + m, x0 - m:x1 + m].astype(np.float32)
            src = im[y0 - m:y1 + m, x0 - m + dx:x1 + m + dx].astype(np.float32)
            cinza = lambda r: (r.mean(2) < 110) & (r.max(2) - r.min(2) < 25)     # a parede é cinza (os pontinhos não)
            parede = cinza(reg) | cinza(src)
            parede = cv2.dilate(parede.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
            a = np.zeros(reg.shape[:2], np.float32)
            a[m:-m, m:-m] = 1
            a[parede] = 0
            a = cv2.GaussianBlur(a, (0, 0), 1.5)
            a[parede] = 0
            im[y0 - m:y1 + m, x0 - m:x1 + m] = np.clip(reg * (1 - a[..., None]) + src * a[..., None], 0, 255).astype(np.uint8)
        Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).save(EP.PROJ / rel, quality=95, subsampling=0, dpi=dpi)
        del im
        print(f"   {op}: resíduos em volta dos vãos limpos")


def main(so_limpar=False):
    if not so_limpar:
        novo = final_e_prancha()
        doze_k(novo)
    limpar_12k()


if __name__ == "__main__":
    main(so_limpar="--so-limpar" in sys.argv)

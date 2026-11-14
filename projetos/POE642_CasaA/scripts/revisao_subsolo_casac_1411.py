"""A revisão do 12K do Subsolo da Casa C de 14/11 (os 5 recortes do usuário).

Sobre a final de `ANTES_COMMIT` (a de 48a23e8: a biblioteca, os post-its e a revisão do 12K de 13/11), em px da final:
1. **"CORRIJA A PAREDE DA IMAGEM 01"** (`parede_bh`): a parede entre a ducha e o BH academia tinha a face da direita
   serrilhada (um entalhe claro logo abaixo da soleira, pontos pretos do traço do PDF): a coluna da face no cinza da
   parede e a seguinte na meia-tinta entre a parede e o piso, de cima a baixo.
2. **"CORRIJA PAREDE DA SAUNA ... E PONTOS PRETO NA SOLEIRA DO VIDRO"** (`sauna`): os pontos pretos (o tracejado do PDF)
   na coluna da direita da soleira do vidro da sauna saem (a cor dela); a face da parede logo abaixo, que falhava (clara
   num trecho, preta no outro), reta no cinza da parede, e o piso ao lado sem os restos.
3. **"REMOVA DEMARCAÇÃO DE ARMÁRIO SUPERIOR NA BANCADA"** (`bancada_bh`): o retângulo de cima do PDF na bancada de
   granito do BH academia (só o contorno, sobra do armário superior) sai: o fio de cada lado vira o granito de 3 px para
   dentro.
4. **"CORRIJA FALHA NA PAREDE AO LADO DA PORTA"** (`deposito`): o canto de dentro entre a parede da esquerda e a de cima,
   junto à porta do depósito, tinha um ponto preto e a meia-tinta escura: no cinza da parede e na meia-tinta da face.
5. **"ESQUADRIA EM TOM DE VIDRO, NÃO PRETO"** (`vidros_academia`): as 4 folhas de vidro de correr entre a varanda e a
   academia (o contorno preto das esquadrias de 13/11 e o miolo cinza) no vidro claro dos boxes da Casa C
   (`final3840_casab.BOXES_VIDRO`: o vidro azul-acinzentado claro e as faces finas num cinza claro), pela luminância de
   cada px (o fio escuro vira a face, o miolo vira o vidro); os encontros brancos das folhas ficam.

  python3 revisao_subsolo_casac_1411.py [--antes <png>] [--saida <png>]
"""

import argparse
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

R = AQUI.parents[1] / "POE642_CasaC" / "renders"
FINAL = R / "POE642_CasaC_PH_Subsolo_final_rotulos.png"
RAIZ_GIT = AQUI.parents[2]
ANTES_COMMIT = "48a23e8"
PAREDE = 80

PAREDE_BH = {"x_face": 897, "y": (804, 895)}
SAUNA = {"soleira_x": 706, "soleira_y": (750, 832), "escuro": 150, "parede": (695, 706), "y0": 835, "face_x": 706,
         "face_cor": 84, "piso_min": 195}
BANCADA_BH = {"ret": (948, 755, 980, 795), "fios": {"cima": (757, 761), "baixo": (790, 790), "esq": (949, 955),
                                                     "dir": (972, 979), "ate_y": 792}, "dentro": 4, "dif": -1}
DEPOSITO = {"canto": [(992, 746)], "face_x": 993, "face_y": (746, 748), "amostra_y": (752, 790)}
VIDROS_ACADEMIA = {"caixa": (1060, 334, 1082, 738), "croma_max": 18, "claro_max": 200,
                   "face": (162, 164, 166), "vidro": (218, 214, 204), "l0": 34, "l1": 150}
ANTES_DEPOIS = {"bh_academia": (860, 730, 1000, 910), "sauna": (680, 725, 760, 910), "deposito": (975, 725, 1090, 800),
                "vidros_academia": (1030, 320, 1110, 750)}


def parede_bh(img, q=PAREDE_BH):
    out = img.copy()
    x = q["x_face"]
    y0, y1 = q["y"]
    out[y0:y1, x] = PAREDE
    piso = img[y0:y1, x + 2].astype(np.float32)
    out[y0:y1, x + 1] = np.round(0.45 * PAREDE + 0.55 * piso).astype(np.uint8)
    print(f"    BH academia: a face da direita da parede reta (x {x}), de y {y0} a {y1}")
    return out


def sauna(img, q=SAUNA):
    out = img.copy()
    # os pontos pretos na coluna da direita da soleira do vidro
    x = q["soleira_x"]
    y0, y1 = q["soleira_y"]
    col = img[y0:y1, x].astype(np.float32)
    esc = col.mean(axis=1) < q["escuro"]
    cor = np.median(col[~esc], axis=0)
    out[y0:y1, x][esc] = np.round(cor).astype(np.uint8)
    # a parede de baixo: a face reta e o piso ao lado sem restos
    p0, p1 = q["parede"]
    y = q["y0"]
    n = 0
    while y < img.shape[0] and (np.abs(img[y, p0:p1].astype(np.int16) - PAREDE).max() <= 2):
        out[y, q["face_x"]] = q["face_cor"]
        if img[y, q["face_x"] + 1].astype(np.float32).mean() < q["piso_min"]:
            out[y, q["face_x"] + 1] = img[y, q["face_x"] + 2]
        y += 1
        n += 1
    print(f"    sauna: {int(esc.sum())} pontos pretos na soleira do vidro fora; a face da parede reta em {n} linhas")
    return out


def bancada_bh(img, q=BANCADA_BH):
    out = img.copy()
    X0, Y0, X1, Y1 = q["ret"]
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    lum = reg.mean(axis=2)
    fundo = cv2.medianBlur(img[Y0 - 4:Y1 + 4, X0 - 4:X1 + 4], 7)[4:-4, 4:-4].astype(np.float32).mean(axis=2)
    fio = np.abs(lum - fundo) > q["dif"]
    m = np.zeros_like(fio)
    d = q["dentro"]
    f = q["fios"]
    a, b = f["cima"]
    m[a - Y0:b - Y0, :] = True
    a, b = f["baixo"]
    m[a - Y0:b - Y0, :] = True
    # os lados só até o fio escuro de cima da cuba (`ate_y`), que fica
    v0, v1 = f["cima"][0] - Y0, f["ate_y"] - Y0
    a, b = f["esq"]
    m[v0:v1, a - X0:b - X0] = True
    a, b = f["dir"]
    m[v0:v1, a - X0:b - X0] = True
    m &= fio
    # o granito de `dentro` px para o miolo do retângulo
    cy, cx = (f["cima"][1] + f["baixo"][0]) / 2 - Y0, (f["esq"][1] + f["dir"][0]) / 2 - X0
    ys, xs = np.nonzero(m)
    for v, u in zip(ys, xs):
        dv = int(np.sign(cy - v)) * d if (v + Y0 < f["cima"][1] or v + Y0 >= f["baixo"][0]) else 0
        du = int(np.sign(cx - u)) * d if (u + X0 < f["esq"][1] or u + X0 >= f["dir"][0]) else 0
        out[Y0 + v, X0 + u] = img[Y0 + v + dv, X0 + u + du]
    print(f"    BH academia: o contorno do armário superior na bancada fora ({int(m.sum())} px)")
    return out


def deposito(img, q=DEPOSITO):
    out = img.copy()
    for x, y in q["canto"]:
        out[y, x] = PAREDE
    x = q["face_x"]
    a, b = q["amostra_y"]
    cor = np.median(img[a:b, x].astype(np.float32), axis=0)
    y0, y1 = q["face_y"]
    out[y0:y1, x] = np.round(cor).astype(np.uint8)
    print("    depósito: o canto de dentro da parede junto à porta sem o ponto preto")
    return out


def vidros_academia(img, q=VIDROS_ACADEMIA):
    out = img.copy()
    X0, Y0, X1, Y1 = q["caixa"]
    reg = img[Y0:Y1, X0:X1].astype(np.float32)
    I = reg.astype(np.int16)
    croma = I.max(axis=2) - I.min(axis=2)
    lum = reg.mean(axis=2)
    folha = (croma <= q["croma_max"]) & (lum <= q["claro_max"])
    t = np.clip((lum - q["l0"]) / (q["l1"] - q["l0"]), 0, 1)[..., None]
    novo = np.float32(q["face"]) * (1 - t) + np.float32(q["vidro"]) * t
    reg[folha] = novo[folha]
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    print(f"    academia: as 4 folhas de vidro de correr no vidro claro ({int(folha.sum())} px), sem o preto")
    return out


def aplicar(antes):
    out = parede_bh(antes)
    out = sauna(out)
    out = bancada_bh(out)
    out = deposito(out)
    out = vidros_academia(out)
    return out


def final_de(commit):
    dado = subprocess.run(["git", "show", f"{commit}:{FINAL.relative_to(RAIZ_GIT).as_posix()}"], cwd=RAIZ_GIT,
                          capture_output=True, check=True).stdout
    return cv2.imdecode(np.frombuffer(dado, np.uint8), cv2.IMREAD_COLOR)


def antes_depois(antes, depois):
    for nome, (x0, y0, x1, y1) in ANTES_DEPOIS.items():
        a, b = antes[y0:y1, x0:x1], depois[y0:y1, x0:x1]
        k = min(5.0, 1400 / max(a.shape[:2]))
        a = cv2.resize(a, None, fx=k, fy=k, interpolation=cv2.INTER_CUBIC)
        b = cv2.resize(b, None, fx=k, fy=k, interpolation=cv2.INTER_CUBIC)
        j = np.hstack([a, np.full((a.shape[0], 16, 3), 255, np.uint8), b])
        t = np.full((44, j.shape[1], 3), 255, np.uint8)
        cv2.putText(t, "ANTES | DEPOIS", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (40, 40, 40), 2, cv2.LINE_AA)
        cv2.imwrite(str(R / f"POE642_CasaC_PH_Subsolo_1411_{nome}_antes_depois.jpg"), np.vstack([t, j]),
                    [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"    antes e depois: {', '.join(ANTES_DEPOIS)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--antes")
    ap.add_argument("--saida")
    a = ap.parse_args()
    antes = cv2.imread(a.antes) if a.antes else final_de(ANTES_COMMIT)
    depois = aplicar(antes)
    cv2.imwrite(a.saida or str(FINAL), depois)
    print(f"    {a.saida or FINAL.name}")
    if not a.saida:
        antes_depois(antes, depois)


if __name__ == "__main__":
    main()

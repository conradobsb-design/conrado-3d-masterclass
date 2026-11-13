"""As peças da biblioteca no Térreo da Casa C (13/11), 1ª leva: banhos, lavabos, cozinha, gourmet e serviço.

Usuário: "Vamos para biblioteca da casa C"; a proposta (`POE642_CasaC/renders/POE642_CasaC_PH_Terreo_1311_proposta_
biblioteca_{1,2,3}.jpg`) aprovada com "Ok"; os PDFs da Casa C anexados. As peças e as convenções são as da Casa A e do
Térreo da Casa B (`regras_terreo_casab_1311`, de onde vêm as funções), nos retângulos do PDF da Casa C (px da final):
- **BH master 1:** a bancada dupla esculpida no comprimento da bancada do PDF, as 2 cubas nas do PDF (as pontas lisas e
  o meio entre as cubas esticados, as cubas sem deformar), a bacia Carrara branca.
- **BH master 2 e BH 1 a 3:** a cuba esculpida de travertino na bancada inteira, a cuba no lugar da do PDF; a bacia
  Carrara branca.
- **Lavabos (masculino, feminino e o social, junto à adega):** a cuba esculpida de poros e a bacia Carrara no marrom
  dos vasos do Térreo.
- **BH serviço e BH externo:** só a louça da cuba (a bancada fica) e a bacia Monte Carlo.
- **Chuveiros:** os desenhos em planta: de teto no quadrado do PDF (BH master 1 e 2, BH 1 a 3, a ducha entre os
  lavabos: o PDF não tem o braço), os redondos de parede no BH serviço e no BH externo (o braço até a parede); os de antes
  (a foto do cromado) viram o piso do lado.
- **Cozinha:** o cooktop de 4 bocas no meio do de 5 da ilha (o resto vira bancada, `balcao`), as 2 cubas Franke da pia,
  a geladeira inox (G2) nos 2 retângulos do PDF com a frente para a ilha, as 4 banquetas da ilha da Casa A nos círculos
  do PDF, com a ilha de volta por cima (a parte do assento sob o tampo não aparece).
- **Gourmet:** o cooktop de 4 bocas e a cuba Franke com misturador.
- **Área de serviço:** os 2 tanques Franke (a torneira na parede da direita).
- **Bege Bahia:** as manchas a 45% (a regra de 10/11), nos banhos, nos caminhos e nos pisantes.
- **Esquadrias:** o contorno fino em preto (`regras_terreo_casab_1311.esquadrias`), sem os batentes.

  python3 biblioteca_terreo_casac_1311.py [--antes <png>] [--saida <png>]
Sem --antes, parte da final do commit `ANTES_COMMIT`; sem --saida, grava a final e os antes e depois
`POE642_CasaC/renders/POE642_CasaC_PH_Terreo_1311_<trecho>_antes_depois.jpg`.
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
import biblioteca_subsolo_casab_1311 as BB       # noqa: E402
import biblioteca_1pav_casaa_1211 as B1          # noqa: E402
import biblioteca_terreo_casaa_1211 as BT        # noqa: E402
import regras_terreo_casab_1311 as RT            # noqa: E402
import biblioteca_subsolo_casac_1311 as SC       # noqa: E402

CASA_C = AQUI.parents[1] / "POE642_CasaC"
R = CASA_C / "renders"
FINAL = R / "POE642_CasaC_PH_Terreo_final_rotulos.png"
RAIZ_GIT = AQUI.parents[2]
ANTES_COMMIT = "1b15917"
PX_M = B1.PX_M

# as peças (`regras_terreo_casab_1311.item_bib`: leitor, png, cx, cy, larg, alt, giro, sombra, extra); o giro pela
# parede: 0 em cima, 180 embaixo, 90 à esquerda, -90 à direita; ("cuba", c): o miolo da cuba a c px da ponta direita
# do PNG (aqui sempre no meio da bancada)
PECAS = {
    "bh_master_2": [("B1", "banho-2/cuba-esculpida-travertino", 662.7, 901.25, 131.3, 32.8, 90.0, "baixa",
                     ("cuba", 65.65)),
                    ("B1", "banho-master/bacia-carrara", 729.85, 951.6, 21.1, 30.7, 180.0, "baixa", None)],
    "bh_master_1": [("B1", "banho-master/bacia-carrara", 864.25, 343.35, 21.1, 30.7, 0.0, "baixa", None)],
    "bhs": [("B1", "banho-3/cuba-esculpida-travertino", 1089.6, 371.35, 110.5, 32.8, 90.0, "baixa", ("cuba", 55.25)),
            ("B1", "banho-3/bacia-carrara", 1088.55, 286.25, 21.1, 30.7, 90.0, "baixa", None),
            ("B1", "banho-2/cuba-esculpida-travertino", 1782.25, 371.35, 110.5, 32.8, -90.0, "baixa", ("cuba", 55.25)),
            ("B1", "banho-2/bacia-carrara", 1783.35, 286.25, 21.1, 30.7, -90.0, "baixa", None),
            ("B1", "banho-1/cuba-esculpida-travertino", 1836.0, 371.35, 110.5, 32.8, 90.0, "baixa", ("cuba", 55.25)),
            ("B1", "banho-1/bacia-carrara", 1834.9, 286.25, 21.1, 30.7, 90.0, "baixa", None)],
    "lavabos": [("BT", "lavabo/cuba-esculpida-poros-render", 1214.1, 1553.85, 54.9, 31.0, 90.0, "baixa", "lavabo"),
                ("BT", "lavabo/bacia-carrara", 1302.65, 1608.8, 21.1, 30.7, -90.0, "baixa", "marrom"),
                ("BT", "lavabo/cuba-esculpida-poros-render", 1526.4, 1553.85, 54.9, 31.0, -90.0, "baixa", "lavabo"),
                ("BT", "lavabo/bacia-carrara", 1467.25, 1626.3, 21.1, 30.7, 180.0, "baixa", "marrom"),
                ("BT", "lavabo/cuba-esculpida-poros-render", 2382.3, 1108.75, 71.7, 32.8, 90.0, "baixa", "lavabo"),
                ("BT", "lavabo/bacia-carrara", 2381.25, 996.75, 21.1, 30.7, 90.0, "baixa", "marrom")],
    "servico": [("B1", "banho-de-servico/cuba-servico-granito", 2681.2, 526.6, 23.8, None, -90.0, None, "louca"),
                ("BT", "banho-do-motorista/bacia-monte-carlo-sem-valvula", 2683.85, 578.85, 22.5, 32.7, -90.0, "baixa",
                 None),
                ("BT", "area-de-servico/cuba-franke-inox-link", 2676.35, 372.85, 37.9, 31.9, -90.0, None, None),
                ("BT", "area-de-servico/cuba-franke-inox-link", 2676.35, 414.65, 37.9, 31.9, -90.0, None, None)],
    "externo": [("BT", "banho-do-motorista/cuba-compacta", 2829.9, 722.1, 23.8, None, 90.0, None, "louca"),
                ("BT", "banho-do-motorista/bacia-monte-carlo-sem-valvula", 2827.15, 784.85, 22.5, 32.7, 90.0, "baixa",
                 None)],
    "cozinha": [("BT", "cozinha/cooktop-quatro-bocas", 2309.15, 435.55, 31.0, 29.0, 90.0, None, None),
                ("BT", "area-de-servico/cuba-franke-inox-link", 2279.3, 275.8, 38.2, 26.3, 0.0, None, None),
                ("BT", "area-de-servico/cuba-franke-inox-link", 2327.1, 275.8, 38.2, 26.3, 0.0, None, None)],
    "gourmet": [("BT", "cozinha/cooktop-quatro-bocas", 1404.95, 1107.95, 31.0, 29.0, 0.0, None, None),
                ("BT", "area-gourmet/cuba-franke-misturador-unic", 1312.0, 954.05, 38.2, 26.3, 0.0, None, None)],
}
# a bancada dupla do BH master 1 (px: a bancada do PDF, a parede à esquerda) e o miolo das 2 cubas do PDF ao longo dela;
# no PNG (782 x 332 depois do corte), as colunas das pontas (o canto e o liso), das cubas e do meio
DUPLA = {"png": "banho-master/bancada-dupla-esculpida-render-v2", "c": (750.8, 411.6, 783.6, 569.9), "giro": 90.0,
         "cubas": (456.5, 524.8), "colunas": {"canto": 30, "cuba1": (60, 335), "cuba2": (452, 725)}}
# a pedra das bancadas dos lavabos (px, os trechos fora da cuba nova) e a borda da cuba nova de onde vem o tom
LAVABOS_PEDRA = [("lavabo masculino", [(1199, 1499, 1222, 1526), (1199, 1582, 1222, 1641)],
                  [(1201, 1528, 1221, 1531), (1201, 1577, 1221, 1580)]),
                 ("lavabo feminino", [(1519, 1499, 1542, 1526), (1519, 1582, 1542, 1641)],
                  [(1520, 1528, 1540, 1531), (1520, 1577, 1540, 1580)]),
                 ("lavabo da adega", [(2366, 1029, 2396, 1072), (2366, 1145, 2396, 1188)],
                  [(2368, 1075, 2396, 1078), (2368, 1139, 2396, 1142)])]
# os cooktops de 5 bocas que saem (`regras_terreo_casab_1311.balcao`: c, eixo, folga, rampa)
BALCAO = [((2294.2, 409.3, 2324.1, 461.8), "y", 2, 3), ((1378.7, 1093.0, 1431.2, 1122.9), "x", 2, 3)]
# os chuveiros: a placa do PDF (px), o desenho, a parede (face px e lado; None: de teto) e de onde vem o piso
CH_T, CH_R = "banho-master/chuveiro-quadrado-planta", "banho-de-servico/chuveiro-redondo-parede-planta"
CHUVEIROS = [
    {"nome": "BH master 1", "placa_px": (783.7, 361.0, 795.5, 372.8), "png": CH_T, "parede": None, "piso": (1, 0)},
    {"nome": "BH master 2", "placa_px": (843.4, 931.2, 855.2, 943.0), "png": CH_T, "parede": None, "piso": (-1, 0)},
    {"nome": "BH 3", "placa_px": (1204.6, 287.8, 1216.4, 299.6), "png": CH_T, "parede": None, "piso": (0, 1)},
    {"nome": "BH 2", "placa_px": (1661.4, 287.8, 1673.2, 299.6), "png": CH_T, "parede": None, "piso": (0, 1)},
    {"nome": "BH 1", "placa_px": (1945.0, 287.8, 1956.8, 299.6), "png": CH_T, "parede": None, "piso": (0, 1)},
    {"nome": "ducha dos lavabos", "placa_px": (1368.8, 1602.9, 1380.6, 1614.7), "png": CH_T, "parede": None,
     "piso": (-1, 0)},
    {"nome": "BH serviço", "placa_px": (2671.4, 629.6, 2683.2, 641.4), "png": CH_R, "parede": (2700, "dir"),
     "piso": (0, -1)},
    {"nome": "BH externo", "placa_px": (2928.1, 777.4, 2939.9, 789.2), "png": CH_R, "parede": (2956, "dir"),
     "piso": (0, -1)},
]
# a geladeira inox (G2) nos 2 retângulos do PDF (os índices dos desenhos), a frente para a ilha (à esquerda)
GELADEIRAS = {"png": "02-terreo/cozinha/geladeira-inox.png", "pdf": [81377, 81383]}
# as banquetas da ilha (a da Casa A) nos círculos do PDF (centro e diâmetro, px); a ilha (px) volta por cima
BANQUETAS = {"png": "cozinha/banqueta-ilha", "d": 23.7, "x": 2252.45, "ys": (399.7, 439.5, 479.35, 519.15),
             "ilha": (2258.4, 363.9, 2330.1, 554.9)}
ANTES_DEPOIS = {"bh_master_1": (735, 300, 900, 590), "bh_master_2": (630, 820, 900, 985),
                "bh_1_2_3": (1060, 250, 1990, 440), "lavabos": (1180, 1480, 1560, 1660),
                "lavabo_adega": (2250, 960, 2480, 1210), "cozinha_servico": (2160, 240, 2720, 690),
                "gourmet": (1220, 910, 1580, 1170), "externo": (2790, 670, 2980, 830),
                "bege_bahia": (560, 1180, 3300, 1860)}


def quadro():
    if "Q" not in _Q:
        with contextlib.redirect_stdout(io.StringIO()):
            C.contexto_c()
            _Q["Q"] = F.Quadro("Terreo")
    return _Q["Q"]


_Q = {}


# ----------------------------------------------------------------------------------------------------------------------
def dupla_png(q=DUPLA):
    """A bancada dupla no comprimento e com as cubas do PDF: as colunas das pontas lisas (fora o canto) e do meio entre
    as cubas esticadas, as cubas na escala da profundidade (sem deformar). (P, larg, alt)."""
    P = B1.ler_png(q["png"])
    x0, y0, x1, y1 = q["c"]
    L, D = y1 - y0, x1 - x0                         # na parede da esquerda: o comprimento em y
    s = D / P.shape[0]
    k = q["colunas"]["canto"]
    a1, b1 = q["colunas"]["cuba1"]
    a2, b2 = q["colunas"]["cuba2"]
    c1, c2 = q["cubas"][0] - y0, q["cubas"][1] - y0
    w = P.shape[1]
    esq = (c1 - (b1 - a1) * s / 2) / s - k                # as colunas de PNG de cada trecho esticado
    meio = (c2 - c1 - ((b1 - a1) + (b2 - a2)) * s / 2) / s
    dir_ = (L - c2 - (b2 - a2) * s / 2) / s - k
    P = BS.esticar(P, 1, [(0, k, None), (k, a1, esq), (a1, b1, None), (b1, a2, meio), (a2, b2, None),
                          (b2, w - k, dir_), (w - k, w, None)])
    return P, float(L), float(D)


def bancada_dupla(out, par, reg, q=DUPLA):
    P, L, D = dupla_png(q)
    x0, y0, x1, y1 = q["c"]
    o = BT.pousar(out.astype(np.float32), P, (x0 + x1) / 2, (y0 + y1) / 2, L, D, q["giro"], BT.SOMBRAS["baixa"], PX_M,
                  nao=par)
    reg.append({"tipo": "dupla"})
    print(f"    BH master 1: a bancada dupla esculpida em {L:.1f} x {D:.1f} px, as cubas nas do PDF")
    return np.clip(np.round(o), 0, 255).astype(np.uint8)


def pecas(out, par, reg, q=PECAS):
    n = 0
    for amb, ps in q.items():
        for p in ps:
            it = RT.item_bib(*p)
            out = RT.pousar_bib(out, it, par)
            reg.append(it)
            n += 1
    print(f"    peças: {n} da biblioteca ({', '.join(q)})")
    return out


def chuveiros(out, par, reg, q=CHUVEIROS):
    for ch in q:
        x0, y0, x1, y1 = ch["placa_px"]
        L = RT.LIMPA_PX
        a = [x0 - L, y0 - L, x1 + L, y1 + L]
        if ch["parede"] is not None:
            face, lado = ch["parede"]
            if lado == "esq":
                a[0] = face
            elif lado == "dir":
                a[2] = face
            elif lado == "cima":
                a[1] = face
            else:
                a[3] = face
        out = BB.piso_desloc(out, tuple(a), par, ch["piso"][0], ch["piso"][1], folga=0)
        P, cx, cy, wt, ht, ang = RT.chuveiro_desenho(ch)
        o = BT.pousar(out.astype(np.float32), P, cx, cy, wt, ht, ang, B1.SOMBRAS["chuveiro"], PX_M, nao=par)
        out = np.clip(np.round(o), 0, 255).astype(np.uint8)
        reg.append({"tipo": "chuveiro", "nome": ch["nome"]})
    print(f"    chuveiros: {len(q)} desenhados em planta")
    return out


def geladeiras(Q, out, par, reg, q=GELADEIRAS):
    for i in q["pdf"]:
        it = {"tipo": "png", "png": q["png"], "rot": -1, "c": list(RT.caixa_pdf(Q, i)), "sombra": "movel"}
        out = RT.pousar_peca(out, it, BT.SOMBRAS["movel"], par)
        reg.append(it)
    print(f"    cozinha: a geladeira inox nos {len(q['pdf'])} retângulos do PDF, a frente para a ilha")
    return out


def banquetas(out, par, reg, q=BANQUETAS):
    antes = out.copy()
    d = q["d"]
    for y in q["ys"]:
        it = RT.item_bib("BT", q["png"], q["x"], y, d, d, 90.0, "movel", None)
        out = RT.pousar_bib(out, it, par)
        reg.append(it)
    x0, y0, x1, y1 = q["ilha"]
    X0 = int(np.floor(x0))
    al = np.clip(np.arange(X0, X0 + 3) + 0.5 - x0, 0, 1)[None, :, None]      # a borda da ilha antisserrilhada
    Y0, Y1 = int(np.floor(y0)), int(np.ceil(y1))
    reg_ = out[Y0:Y1, X0:X0 + 3].astype(np.float32)
    out[Y0:Y1, X0:X0 + 3] = np.clip(np.round(reg_ * (1 - al) + antes[Y0:Y1, X0:X0 + 3] * al), 0, 255).astype(np.uint8)
    out[Y0:Y1, X0 + 3:int(np.ceil(x1))] = antes[Y0:Y1, X0 + 3:int(np.ceil(x1))]
    print(f"    cozinha: as {len(q['ys'])} banquetas da ilha da Casa A nos círculos do PDF, a ilha por cima")
    return out


def bancadas_lavabos(out, q=LAVABOS_PEDRA):
    """A pedra das bancadas dos lavabos no tom da cuba esculpida (regra da Casa A, "A BANCADA É NO MESMO TOM DA CUBA
    ESCULPIDA. CORRIJA", `pedidos_terreo_casaa_1211c.bancada`): a mediana da borda da cuba sobre a da pedra, px a px (o
    desenho, a luz e o contorno da pedra ficam)."""
    f = out.astype(np.float32)
    for nome, pedras, bordas in q:
        alvo = np.median(np.concatenate([f[b:d, a:c].reshape(-1, 3) for a, b, c, d in bordas]), axis=0)
        atual = np.median(np.concatenate([f[b + 2:d - 2, a + 2:c - 2].reshape(-1, 3) for a, b, c, d in pedras]),
                          axis=0)
        for a, b, c, d in pedras:
            reg = f[b:d, a:c] * (alvo / np.maximum(atual, 1))[None, None]
            base = cv2.GaussianBlur(reg, (0, 0), 2.0)
            f[b:d, a:c] = base + 0.35 * (reg - base)          # os pontos do granito, suaves como o veio da cuba
        print(f"    {nome}: a bancada de BGR {np.round(atual).astype(int)} para {np.round(alvo).astype(int)} "
              "(a borda da cuba)")
    return np.clip(np.round(f), 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
def aplicar(antes):
    Q = quadro()
    out = antes.copy()
    par = BS.quieto(FA.paredes_pdf, Q) > 0.3
    reg = []
    # (13/11, "Já removeu manchas do bege Bahia como fizemos nas outras plantas?"; a regra de 10/11) o Bege Bahia (a
    # chapada 232: os banhos, os caminhos e os pisantes) com as manchas a 45% (`pedidos_subsolo_casac_1311.bege`)
    import pedidos_subsolo_casac_1311 as PS
    out = PS.bege(Q, out)
    out = RT.balcao(out, par, BALCAO)
    out = chuveiros(out, par, reg)
    out = bancada_dupla(out, par, reg)
    out = pecas(out, par, reg)
    out = bancadas_lavabos(out)
    out = geladeiras(Q, out, par, reg)
    out = banquetas(out, par, reg)
    ch0 = SC.CHUVEIROS
    SC.CHUVEIROS = CHUVEIROS
    try:
        out = SC.esquadrias(Q, out)
    finally:
        SC.CHUVEIROS = ch0
    return out, reg


def antes_depois(antes, depois):
    for nome, (x0, y0, x1, y1) in ANTES_DEPOIS.items():
        a, b = antes[y0:y1, x0:x1], depois[y0:y1, x0:x1]
        k = min(6.0, 900 / max(a.shape[:2]))
        a = cv2.resize(a, None, fx=k, fy=k, interpolation=cv2.INTER_LANCZOS4)
        b = cv2.resize(b, None, fx=k, fy=k, interpolation=cv2.INTER_LANCZOS4)
        lado = a.shape[1] <= a.shape[0] * 1.6
        junto = np.hstack([a, np.full((a.shape[0], 16, 3), 255, np.uint8), b]) if lado else \
            np.vstack([a, np.full((16, a.shape[1], 3), 255, np.uint8), b])
        topo = np.full((44, junto.shape[1], 3), 255, np.uint8)
        cv2.putText(topo, "ANTES | DEPOIS" if lado else "ANTES (em cima) | DEPOIS (embaixo)", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (40, 40, 40), 2, cv2.LINE_AA)
        arq = R / f"POE642_CasaC_PH_Terreo_1311_{nome}_antes_depois.jpg"
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
    depois, reg = aplicar(antes)
    if a.saida:
        cv2.imwrite(a.saida, depois)
        print(f"    {a.saida}")
        return
    cv2.imwrite(str(FINAL), depois)
    print(f"    {FINAL.name}: {len(reg)} peças")
    antes_depois(antes, depois)


if __name__ == "__main__":
    main()

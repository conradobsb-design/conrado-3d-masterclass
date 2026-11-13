"""As alterações da Casa A no Térreo da Casa B (13/11).

Usuário, vendo o Térreo da Casa B ao lado da lista do que a Casa A recebeu depois de 12/11: "VAMOS REVISAR OS
MOBILIÁRIOS DO TÉRREO DA CASA B E REALIZAR AS ALTERAÇÕES FEITAS NA CASA A LISTADAS ACIMA". Sobre a final de 4574dc9 (o
Térreo de 12/11), as regras aprovadas na Casa A (o mobiliário vai pela proposta, à parte):
- **Letras (`LETRAS_TB`, `letras`):** o D logo abaixo da seta das 3 escadas (DESCE PARA O SUBSOLO, PARA O DECK e PARA O
  JARDIM), como no Térreo da Casa A (`pedidos_terreo_casaa_1211c.letras`, `letras_escadas_casaa_1211.um_pav`): no corpo
  e na cor das descrições, centrado sob o triângulo, a `folga_px` dele; uma anotação "txt" a mais nos dados do 12K
  (`POE642_CasaB_PH_Terreo_12K_dados.json`), que o `montar12k` desenha (A na Inter, B na Kalam).
- **Shafts (`SHAFTS_TB`, `shafts`):** os 2 vãos (junto à sala íntima e junto à cozinha) no claro e o X de canto a canto
  em cinza fino, tracejado (`regras_1211_casaa.desenhar_x`, a regra de 12/11), com a borda de parede em volta limpa
  (`limpar_aro`); no 12K, desenhados na escala dele (`regras_1211_casaa.shafts_12k`).
- **Chuveiros (`CHUVEIROS_TB`, `chuveiros`):** os desenhos em planta (`chuveiros_planta_casaa_1211`, como no 1º
  Pavimento da Casa A e no Subsolo da Casa B): os 2 de teto do banho master no quadrado do PDF; os de parede (banhos 1,
  2 e 3, os 2 BH gourmet e a ducha do deck) com a placa quadrada e o braço até a face da parede; os do BH serviço e do
  BH motorista, redondos de parede (o banho de serviço da Casa A). Os de antes (a placa, o braço, a canopla e a sombra)
  viram o piso do lado (`biblioteca_subsolo_casab_1311.piso_desloc`, com a costura); a sombra `chuveiro`.
- **Paredes retas (`PAREDES_TB`, `paredes`):** `biblioteca_subsolo_casaa_1211.paredes_retas` no cinza 80 das paredes da
  Casa B, com as proteções do Térreo da Casa A (`regras_1211_casaa`: os objetos do PDF, as folhas e esquadrias da
  ARQ_PAREDE fora do cinza das paredes, só o branco ligado à borda é o lado de fora) e o elevador.
- **Esquadrias pretas (`ESQUADRIAS_TB`, `esquadrias`):** os perfis dos boxes, das portas de vidro e os caixilhos das
  janelas em preto, o vidro claro (a regra de 12/11 da Casa A, "As esquadrias dos box, portas de vidro e janelas são
  pretas"): nas esquadrias do PDF, o traço neutro (o alumínio e a face cinza dos boxes) vai ao preto do perfil na
  proporção do escuro dele (o vidro claro fica); a madeira das portas de giro, o bronze dos brises e as soleiras
  (coloridas) não mudam.
No 12K (`ampliacao_12k_terreo_casaa.montar12k` com `PAV` "Terreo_CasaB", chamado pelo `ampliacao_12k_terreo_casab`):
`pecas_12k` traz o que mudou na final (`REG_MASC`) da final ampliada sobre a saída do Topaz e, por cima, os chuveiros
nítidos na escala do 12K; os shafts e as letras vão pelo `montar12k`.

  python3 regras_terreo_casab_1311.py [--antes <png>] [--saida <png>]
Sem --antes, parte da final do commit `ANTES_COMMIT`; sem --saida, grava a final, os dados do 12K, o registro e os
antes e depois `POE642_CasaB/renders/POE642_CasaB_PH_Terreo_1311_<trecho>_antes_depois.jpg`.
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
from scipy import ndimage

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import final3840_casaa as FA                     # noqa: E402
import final3840_casab as F                      # noqa: E402
import biblioteca_subsolo_casaa_1211 as BS       # noqa: E402
import biblioteca_1pav_casaa_1211 as B1          # noqa: E402
import biblioteca_terreo_casaa_1211 as BT        # noqa: E402
import biblioteca_subsolo_casab_1311 as BB       # noqa: E402
import regras_1211_casaa as RG                   # noqa: E402

CASA_B = AQUI.parents[1] / "POE642_CasaB"
R = CASA_B / "renders"
FINAL = R / "POE642_CasaB_PH_Terreo_final_rotulos.png"
DADOS = R / "POE642_CasaB_PH_Terreo_12K_dados.json"
REG_JSON = R / "POE642_CasaB_PH_Terreo_12K_regras.json"
REG_MASC = R / "POE642_CasaB_PH_Terreo_12K_regras_zona.png"
RAIZ_GIT = AQUI.parents[2]
ANTES_COMMIT = "7ecb326"
PX_M = B1.PX_M

# as letras: a escada (o meio do triângulo dela nos dados do 12K, px) e a letra
LETRAS_TB = {"escadas": [((680.6, 643.6), "D"), ((1080.3, 833.0), "D"), ((608.0, 917.6), "D")], "folga_px": 2.5}
# os vãos dos shafts na final (px, x1/y1 exclusivos): o branco dentro das paredes
SHAFTS_TB = [(1564, 742, 1592, 771), (1563, 1252, 1591, 1278)]
# os chuveiros: a placa (o quadrado do PDF, px), o desenho, a face da parede (px) e o lado do braço (None: de teto), e o
# lado de onde vem o piso que cobre o de antes (dx, dy)
CH_Q, CH_R = "banho-1/chuveiro-quadrado-parede-planta", "banho-de-servico/chuveiro-redondo-parede-planta"
CH_T = "banho-master/chuveiro-quadrado-planta"
CHUVEIROS_TB = [
    {"nome": "banho master (esquerda)", "placa_px": (1278.7, 391.4, 1290.5, 403.2), "png": CH_T, "parede": None,
     "piso": (-1, 0)},
    {"nome": "banho master (direita)", "placa_px": (1505.6, 391.4, 1517.4, 403.2), "png": CH_T, "parede": None,
     "piso": (1, 0)},
    {"nome": "banho 1", "placa_px": (1903.6, 373.5, 1915.4, 385.3), "png": CH_Q, "parede": (1932, "dir"), "piso": (0, 1)},
    {"nome": "banho 2", "placa_px": (2675.0, 373.5, 2686.8, 385.3), "png": CH_Q, "parede": (2658, "esq"), "piso": (0, 1)},
    {"nome": "banho 3", "placa_px": (2768.4, 859.2, 2780.2, 871.0), "png": CH_Q, "parede": (842, "cima"), "piso": (-1, 0)},
    {"nome": "BH gourmet (esquerda)", "placa_px": (1125.6, 1630.4, 1137.4, 1642.2), "png": CH_Q, "parede": (1109, "esq"),
     "piso": (0, -1)},
    {"nome": "BH gourmet (direita)", "placa_px": (1509.5, 1630.4, 1521.3, 1642.2), "png": CH_Q, "parede": (1538, "dir"),
     "piso": (0, -1)},
    # no deck, o piso de cada linha (as tábuas são deitadas) vem das duas laterais da mesma linha, em degradê (copiado
    # de um lado só, o trecho aparecia como uma faixa de outro tom)
    {"nome": "ducha do deck", "placa_px": (854.6, 741.4, 866.4, 753.2), "png": CH_Q, "parede": (776, "baixo"),
     "piso": "linhas"},
    {"nome": "BH serviço", "placa_px": (1848.0, 1633.3, 1859.8, 1645.1), "png": CH_R, "parede": (1831, "esq"),
     "piso": (0, 1)},
    {"nome": "BH motorista", "placa_px": (2822.2, 1547.7, 2834.0, 1559.5), "png": CH_R, "parede": (1576, "baixo"),
     "piso": (-1, 0)},
]
LIMPA_PX = 3                 # em volta da placa e do braço de antes (a sombra deles)
PAREDES_TB = dict(BS.PAREDES_RETAS, fora_fundo=True)
ELEVADOR_TB = (1720, 515, 1825, 665)          # a caixa do elevador (px), fora das paredes retas
ESQUADRIAS_TB = {"perfil": (34, 34, 36), "croma_max": 14, "escuro": 170.0, "vidro": 226.0, "cresce_px": 1,
                 "fora_px": []}
ANTES_DEPOIS = {"letras_escadas": (590, 600, 1180, 960), "shafts": (1540, 720, 1615, 1300),
                "chuveiros_banhos": (1250, 340, 2810, 900), "chuveiros_servico": (1095, 1520, 2880, 1680)}


def quadro():
    if "Q" not in _Q:
        with contextlib.redirect_stdout(io.StringIO()):
            _Q["Q"] = F.Quadro("Terreo")
    return _Q["Q"]


_Q = {}


# ----------------------------------------------------------------------------------------------------------------------
def letras(img, q=LETRAS_TB, gravar=True):
    """O D sob a seta de cada escada (como `letras_escadas_casaa_1211.um_pav`), na final e nos dados do 12K."""
    import ampliacao_12k_terreo_casaa as Z
    import terreo_casaa_1011 as TA
    forma = img.shape[:2]
    d = json.loads(DADOS.read_text())
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
    print(f"    letras: {'; '.join(feitos)}")
    if gravar:
        DADOS.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def shafts(img, vaos=SHAFTS_TB):
    for v in vaos:
        img = RG.desenhar_x(img, v)
        img, n = RG.limpar_aro(img, v)
    print(f"    shafts: {len(vaos)} vãos no claro e o X em cinza fino")
    return img


def shafts_12k(final, out, s, ox, oy):
    for v in SHAFTS_TB:
        out = RG.desenhar_x(out, v, s, ox, oy)
        out, _ = RG.limpar_aro(out, v, s, ox, oy)
    return out


def chuveiro_desenho(ch):
    """(P, cx, cy, larg, alt, giro) do chuveiro na final (px)."""
    x0, y0, x1, y1 = ch["placa_px"]
    pc = ((x0 + x1) / 2, (y0 + y1) / 2)
    placa = ((x1 - x0) + (y1 - y0)) / 2
    if ch["parede"] is None:
        P = B1.ler_png(ch["png"])
        return P, pc[0], pc[1], placa, placa, 0.0
    return BB.chuveiro_pos(ch["png"], pc, ch["parede"], placa)


def piso_linhas(out, r):
    """O retângulo r (px) com o piso de cada linha das duas laterais dela (a mesma largura logo à esquerda e logo à
    direita), em degradê da esquerda para a direita."""
    x0, y0, x1, y1 = int(np.floor(r[0])), int(np.floor(r[1])), int(np.ceil(r[2])), int(np.ceil(r[3]))
    w = x1 - x0
    esq = out[y0:y1, x0 - w - 1:x0 - 1].astype(np.float32)
    dir_ = out[y0:y1, x1 + 1:x1 + w + 1].astype(np.float32)
    t = np.linspace(0, 1, w, dtype=np.float32)[None, :, None]
    out[y0:y1, x0:x1] = np.clip(np.round(esq * (1 - t) + dir_ * t), 0, 255).astype(np.uint8)
    return out


def chuveiros(out, par, reg):
    for ch in CHUVEIROS_TB:
        x0, y0, x1, y1 = ch["placa_px"]
        a = [x0 - LIMPA_PX, y0 - LIMPA_PX, x1 + LIMPA_PX, y1 + LIMPA_PX]
        if ch["parede"] is not None:                    # o trecho de antes vai da placa até a face da parede
            face, lado = ch["parede"]
            if lado == "esq":
                a[0] = face
            elif lado == "dir":
                a[2] = face
            elif lado == "cima":
                a[1] = face
            else:
                a[3] = face
        if ch["piso"] == "linhas":
            out = piso_linhas(out, a)
        else:
            out = BB.piso_desloc(out, tuple(a), par, ch["piso"][0], ch["piso"][1], folga=0)
        P, cx, cy, wt, ht, ang = chuveiro_desenho(ch)
        o = BT.pousar(out.astype(np.float32), P, cx, cy, wt, ht, ang, B1.SOMBRAS["chuveiro"], PX_M, nao=par)
        out = np.clip(np.round(o), 0, 255).astype(np.uint8)
        reg["pecas"].append({"tipo": "chuveiro_tb", "nome": ch["nome"]})
    print(f"    chuveiros: {len(CHUVEIROS_TB)} desenhados em planta (2 de teto, 6 quadrados e 2 redondos de parede)")
    return out


def paredes(Q, out, antes):
    q = PAREDES_TB
    protegido = ndimage.binary_dilation((out != antes).any(axis=2), iterations=2)
    im = out.astype(np.int16)
    cinza = (np.abs(im - q["cor"]).max(axis=2) <= q["tol"]) & ((im.max(axis=2) - im.min(axis=2)) <= q["croma"])
    folhas = (BS.quieto(FA.paredes_pdf, Q) > 0.3) & ~cinza
    protegido |= ndimage.binary_dilation(folhas, iterations=1) | RG.objetos_pdf(Q)
    x0, y0, x1, y1 = ELEVADOR_TB
    protegido[y0:y1, x0:x1] = True
    return BS.paredes_retas(Q, out, protegido, FA, q)


def esquadrias_mascara(Q, out, q=ESQUADRIAS_TB):
    """As esquadrias do PDF na final: o que a ARQ_PAREDE preenche e não é o cinza das paredes, com `cresce_px`."""
    im = out.astype(np.int16)
    croma = im.max(axis=2) - im.min(axis=2)
    parede = (np.abs(im - 80).max(axis=2) <= 22) & (croma <= 12)
    pdf = BS.quieto(FA.paredes_pdf, Q) > 0.15
    # fora a parede e a borda dela (o degradê de 1 px da parede para o piso fica como está)
    m = ndimage.binary_dilation(pdf, iterations=q["cresce_px"]) & ~ndimage.binary_dilation(parede, iterations=1)
    for x0, y0, x1, y1 in q["fora_px"]:
        m[y0:y1, x0:x1] = False
    return m


def esquadrias(Q, out, q=ESQUADRIAS_TB):
    m = esquadrias_mascara(Q, out, q)
    im = out.astype(np.float32)
    croma = im.max(axis=2) - im.min(axis=2)
    lum = im.mean(axis=2)
    neutro = m & (croma <= q["croma_max"]) & (lum < q["vidro"])
    a = np.clip((q["vidro"] - lum) / (q["vidro"] - q["escuro"]), 0, 1) * neutro
    novo = im * (1 - a[..., None]) + np.float32(q["perfil"]) * a[..., None]
    print(f"    esquadrias: {int((a > 0.05).sum())} px do perfil neutro no preto (o vidro claro fica)")
    return np.clip(np.round(novo), 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
def aplicar(antes, gravar_dados=True):
    Q = quadro()
    out = antes.copy()
    par = BS.quieto(FA.paredes_pdf, Q) > 0.3
    reg = {"pecas": []}
    out = letras(out, gravar=gravar_dados)
    out = shafts(out)
    out = chuveiros(out, par, reg)
    out = paredes(Q, out, antes)
    # as esquadrias pretas (`esquadrias`) só depois da prévia aprovada (a cor sozinha não basta: os boxes não pegam e
    # as portas das suítes têm os brises de bronze de 29/10)
    return out, reg, par


def peca_12k(it):
    if it["tipo"] != "chuveiro_tb":
        return None
    ch = next(c for c in CHUVEIROS_TB if c["nome"] == it["nome"])
    P, cx, cy, wt, ht, ang = chuveiro_desenho(ch)
    return P, cx, cy, wt, ht, ang, []


def pecas_12k(final, out, s, X0, Ya3):
    """No 12K do Térreo da Casa B (`ampliacao_12k_terreo_casaa.montar12k`, antes dos tracejados e dos textos)."""
    return BB.pecas_12k(final, out, s, X0, Ya3, reg_json=REG_JSON, reg_masc=REG_MASC, peca=peca_12k)


def salvar_registro(antes, depois, reg, par):
    zona = cv2.dilate((np.abs(antes.astype(np.int16) - depois.astype(np.int16)).max(axis=2) > 2).astype(np.uint8),
                      np.ones((5, 5), np.uint8)).astype(bool)
    m = np.zeros(antes.shape, np.uint8)
    m[..., 0] = zona * 255
    m[..., 1] = par * 255
    cv2.imwrite(str(REG_MASC), m)
    REG_JSON.write_text(json.dumps(reg, ensure_ascii=False, indent=1) + "\n")
    print(f"    {REG_JSON.name}: {len(reg['pecas'])} peças; zona {int(zona.sum())} px")


def antes_depois(antes, depois):
    for nome, (x0, y0, x1, y1) in ANTES_DEPOIS.items():
        a, b = antes[y0:y1, x0:x1], depois[y0:y1, x0:x1]
        k = min(4.0, 1600 / max(a.shape[1], 1), 900 / max(a.shape[0], 1))
        a = cv2.resize(a, None, fx=k, fy=k, interpolation=cv2.INTER_LANCZOS4)
        b = cv2.resize(b, None, fx=k, fy=k, interpolation=cv2.INTER_LANCZOS4)
        junto = np.vstack([a, np.full((16, a.shape[1], 3), 255, np.uint8), b]) if a.shape[1] > a.shape[0] * 1.6 \
            else np.hstack([a, np.full((a.shape[0], 16, 3), 255, np.uint8), b])
        topo = np.full((44, junto.shape[1], 3), 255, np.uint8)
        cv2.putText(topo, "ANTES | DEPOIS" if junto.shape[1] > 2 * a.shape[1] else "ANTES (em cima) | DEPOIS (embaixo)",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (40, 40, 40), 2, cv2.LINE_AA)
        arq = R / f"POE642_CasaB_PH_Terreo_1311_{nome}_antes_depois.jpg"
        cv2.imwrite(str(arq), np.vstack([topo, junto]), [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"    antes e depois: {', '.join(ANTES_DEPOIS)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--antes", type=Path)
    ap.add_argument("--saida", type=Path)
    a = ap.parse_args()
    if a.antes:
        antes = cv2.imread(str(a.antes))
    else:
        rel = FINAL.relative_to(RAIZ_GIT)
        dado = subprocess.run(["git", "-C", str(RAIZ_GIT), "show", f"{ANTES_COMMIT}:{rel}"], capture_output=True,
                              check=True).stdout
        antes = cv2.imdecode(np.frombuffer(dado, np.uint8), cv2.IMREAD_COLOR)
    depois, reg, par = aplicar(antes, gravar_dados=not a.saida)
    cv2.imwrite(str(a.saida or FINAL), depois)
    print(f"    {a.saida or FINAL}")
    if not a.saida:
        salvar_registro(antes, depois, reg, par)
        antes_depois(antes, depois)


if __name__ == "__main__":
    main()

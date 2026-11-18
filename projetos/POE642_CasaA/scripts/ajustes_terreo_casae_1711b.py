"""Térreo da Casa E, 17/11, ajustes do usuário, na final e direto nos 12K A e B:

1. `tracejado` ("REMOVER ESSE TRACEJADO"): a linha tracejada vertical do living, junto à cortina da fachada da
   esquerda (x ~1599,5), sai: cada px que destoa da mediana da linha na faixa recebe o travertino de logo à direita;
2. `bacia` ("CORRIGIR O ENTORNO DO VASO", o lavabo): em volta da bacia, o retângulo do remendo de antes (mais claro,
   com as emendas verticais) e os dois tracinhos brancos acima saem: o canto volta ao travertino limpo (o de logo
   abaixo do jardim do living), com a sombra curta rente às paredes, e a bacia da biblioteca volta no retângulo do PDF;
3. `bancada` ("REMOVER AS LINHAS TÉCNICAS DE CONTORNO DA BANCADA NO GRANITO MARROM", a bancada acima da adega): o fio
   claro em volta da pedra sai (o granito de logo para dentro), e a frente (a borda de cima, a que dá para a
   circulação) fica um tom abaixo, como nas outras bancadas;
4. `adega` ("CORRIGIR A ESCALA DAS GARRAFAS"): o módulo de cima tinha o desenho inteiro do armário esticado no
   comprido (12 garrafas de ~11 px); agora as células de garrafa se repetem 3 vezes entre as duas cabeceiras, com as
   garrafas na escala das dos módulos dos lados (~3,7 px).

  python3 ajustes_terreo_casae_1711b.py doze [--opcao AB] [--passos ...]   (antes da final: a final de antes é a ref.)
  python3 ajustes_terreo_casae_1711b.py final [--passos ...]
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import biblioteca_terreo_casaa_1211 as BT                   # noqa: E402
import danae_foto as DF                                     # noqa: E402
import instalacao_terreo_casad_1711 as ID                   # noqa: E402
from correcoes_terreo_casab_1611 import Mapa                # noqa: E402
from janela_pia_casaa_1611 import alfa_ret                  # noqa: E402

RAIZ = AQUI.parents[1]
FINAL = RAIZ / "POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_final.png"
DOZE = RAIZ / "POE642_CasaE/entrega/POE642_CasaE_PH_Terreo_12K_opcao_{}.jpg"
BIB = RAIZ / "POE642_CasaE/biblioteca-objetos/02-terreo"

# px da final
TRACEJADO = {"ret": (1596.5, 815.0, 1603.0, 1562.0), "caixa": (1570, 1180, 1650, 1320), "limiar": 5.0,
             "fontes": [(6, 0), (8, 0), (0, -9), (0, 9)]}
BACIA = {"caixa": (2385, 1230, 2485, 1330), "ret": (2410.0, 1270.0, 2472.0, 1318.7), "fonte": (1900.0, 1135.0),
         "suave": 4.0, "paredes": {"direita": 2475.8, "baixo": 1318.7}, "sombra_parede": (0.10, 2.0),
         "png": BIB / "lavabo/bacia-escura-render.png", "peca": (2433.3, 1288.3, 2454.4, 1319.0),
         "sombra": [{"dx": 0.01, "dy": -0.015, "sig": 0.02, "forca": 0.25}]}
BANCADA = {"caixa": (2070, 690, 2235, 760), "ret": (2128.0, 706.8, 2216.7, 742.6), "miolo": (2134, 711, 2212, 739),
           "frente": 0.88, "frente_px": 0.8}
ADEGA = {"caixa": (2070, 740, 2230, 830), "png": BIB / "adega/armario-adega-e.png", "topo": (2082, 752, 2217, 775),
         "cabeceira": (13, 12), "vezes": 3}


def _png(caminho):
    P = cv2.imread(str(caminho), cv2.IMREAD_UNCHANGED).astype(np.float32)
    ys, xs = np.nonzero(P[..., 3] > 0)
    return np.ascontiguousarray(P[ys.min():ys.max() + 1, xs.min():xs.max() + 1])


# ----------------------------------------------------------------------------------------------------------------------
def tracejado(out, m, q=TRACEJADO):
    def destoa(reg):
        L = reg.mean(axis=2)
        med = np.median(L, axis=1, keepdims=True)
        return np.abs(L - med) > q["limiar"]
    ID._remenda(out, m, q["ret"], q["fontes"], destoa, 10)
    print("    living: o tracejado vertical junto à cortina saiu")


def _piso_canto(out, m, q):
    """O retângulo q["ret"] no travertino de q["fonte"], com a borda suave nos lados livres e a sombra rente às
    paredes (q["paredes"]: as faces)."""
    s = m.s
    rm = m.ret(q["ret"])
    X0, Y0 = int(np.floor(rm[0])), int(np.floor(rm[1]))
    X1, Y1 = int(np.ceil(rm[2])), int(np.ceil(rm[3]))
    forma = (Y1 - Y0, X1 - X0)
    yy = np.arange(forma[0], dtype=np.float32)[:, None]
    xx = np.arange(forma[1], dtype=np.float32)[None, :]
    k = q["suave"] * s
    a = alfa_ret((rm[0] - X0, rm[1] - Y0, rm[2] - X0, rm[3] - Y0), forma)
    a = a * np.clip((yy + 0.5 - (rm[1] - Y0)) / k, 0, 1) * np.clip((xx + 0.5 - (rm[0] - X0)) / k, 0, 1)
    dx = int(round(m.x(q["fonte"][0]) - rm[0]))
    dy = int(round(m.y(q["fonte"][1]) - rm[1]))
    novo = out[Y0 + dy:Y1 + dy, X0 + dx:X1 + dx].astype(np.float32)
    f, d0 = q["sombra_parede"]
    sb = np.zeros(forma, np.float32)
    if "direita" in q["paredes"]:
        sb += np.exp(-np.maximum((m.x(q["paredes"]["direita"]) - X0) - (xx + 0.5), 0) / (d0 * s))
    if "baixo" in q["paredes"]:
        sb += np.exp(-np.maximum((m.y(q["paredes"]["baixo"]) - Y0) - (yy + 0.5), 0) / (d0 * s))
    novo *= (1 - np.clip(f * sb, 0, 0.3))[..., None]
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg * (1 - a[..., None]) + novo * a[..., None]), 0, 255).astype(np.uint8)


def bacia(out, m, q=BACIA):
    s = m.s
    _piso_canto(out, m, q)
    P = _png(q["png"])
    x0, y0, x1, y1 = q["peca"]
    o = out.astype(np.float32)
    BT.pousar(o, P, m.x((x0 + x1) / 2) - 0.5, m.y((y0 + y1) / 2) - 0.5, (x1 - x0) * s, (y1 - y0) * s, 180.0,
              q["sombra"], DF.PX_M * s)
    out[...] = np.clip(np.round(o), 0, 255).astype(np.uint8)
    print("    lavabo: o canto da bacia no travertino limpo, a bacia de volta")


def bancada(out, m, q=BANCADA):
    """A pedra refeita do granito de dentro dela (espelhado até as bordas), no retângulo do PDF levado até a cabeceira
    clara da esquerda (o fio cinza entre as duas sai), sem o fio claro; a frente (a borda de cima) um tom abaixo."""
    s = m.s
    rm = m.ret(q["ret"])
    g = int(np.ceil(3 * s))
    X0, Y0 = int(np.floor(rm[0])) - g, int(np.floor(rm[1])) - g
    X1, Y1 = int(np.ceil(rm[2])) + g, int(np.ceil(rm[3])) + g
    forma = (Y1 - Y0, X1 - X0)
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    ix0, iy0, ix1, iy1 = m.reti(q["miolo"])
    miolo = out[iy0:iy1, ix0:ix1]
    pad = (iy0 - Y0, Y1 - iy1, ix0 - X0, X1 - ix1)
    tex = cv2.copyMakeBorder(miolo, *pad, cv2.BORDER_REFLECT_101).astype(np.float32)
    a = alfa_ret((rm[0] - X0, rm[1] - Y0, rm[2] - X0, rm[3] - Y0), forma)[..., None]
    reg = reg * (1 - a) + tex * a
    x0, y0, x1, y1 = q["ret"]
    rf = m.ret((x0, y0, x1, y0 + q["frente_px"]))
    af = alfa_ret((rf[0] - X0, rf[1] - Y0, rf[2] - X0, rf[3] - Y0), forma)[..., None]
    reg = reg * (1 - af) + reg * q["frente"] * af
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    print("    bancada de granito acima da adega: sem o fio claro de contorno, a frente um tom abaixo")


def _adega_topo(q=ADEGA):
    P = _png(q["png"])
    ce, cd = q["cabeceira"]
    esq, meio, dir_ = P[:, :ce], P[:, ce:P.shape[1] - cd], P[:, P.shape[1] - cd:]
    return np.ascontiguousarray(np.concatenate([esq] + [meio] * q["vezes"] + [dir_], axis=1))


def adega(out, m, q=ADEGA):
    s = m.s
    P = _adega_topo(q)
    x0, y0, x1, y1 = q["topo"]
    o = out.astype(np.float32)
    # como em `mobiliario_terreo_casae_1611.hall_e_outros` (o mesmo retângulo, sem sombra)
    BT.pousar(o, P, m.x((x0 + x1) / 2) - 0.5, m.y((y0 + y1) / 2) - 0.5, (x1 - x0) * s, (y1 - y0) * s, 0.0, [],
              DF.PX_M * s)
    out[...] = np.clip(np.round(o), 0, 255).astype(np.uint8)
    print(f"    adega: o módulo de cima com as células repetidas {q['vezes']} vezes (garrafas na escala dos lados)")


PASSOS = {"tracejado": (tracejado, TRACEJADO), "bacia": (bacia, BACIA), "bancada": (bancada, BANCADA),
          "adega": (adega, ADEGA)}


def aplicar(img, mp, passos=tuple(PASSOS)):
    out = img.copy()
    for p in passos:
        f, q = PASSOS[p]
        m = mp.local(out, q["caixa"]) if mp.ref is not None else mp
        f(out, m)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("acao", choices=("final", "doze"))
    ap.add_argument("--opcao", default="AB")
    ap.add_argument("--entrada")
    ap.add_argument("--saida")
    ap.add_argument("--passos", default=",".join(PASSOS))
    a = ap.parse_args()
    passos = a.passos.split(",")
    fin = cv2.imread(a.entrada or str(FINAL))
    if a.acao == "final":
        cv2.imwrite(a.saida or str(FINAL), aplicar(fin, Mapa(), passos))
        return
    from PIL import Image
    for op in a.opcao:
        f = Path(str(DOZE).format(op))
        img = cv2.imread(str(f))
        M = DF.afim_12k(fin, img)
        mp = Mapa(float(np.hypot(M[0, 0], M[1, 0])), (float(M[0, 2]), float(M[1, 2])))
        mp.ref = fin
        out = aplicar(img, mp, passos)
        dpi = int(round(out.shape[1] / (420 / 25.4)))
        dest = a.saida.format(op) if a.saida else str(f)
        Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB)).save(dest, quality=95, subsampling=0, dpi=(dpi, dpi))
        print(f"    {Path(dest).name}")


if __name__ == "__main__":
    main()

"""O Bege Bahia sob o pergolado do Térreo da Casa A (12/11).

Usuário, com o recorte do pergolado junto à prainha: "PRECISAMOS MELHORAR O ASPECTO DO MARMORE BEGE BAHIA NESSA REGIÃO".
Ali o Bege Bahia tinha saído acinzentado e rosado, com manchas brancas (o refazimento do pergolado de 10/11 emendava o
tecido ao piso de fora pela membrana, e a borda de baixo e a da direita, no travertino da varanda e do lounge, puxavam o
tom para o do travertino; a IA do 12K seguiu o mesmo tom). O deck em volta da piscina e a faixa à esquerda do lounge
estão no tom certo (bege quente, nuvens suaves).

Refeito: o Bege Bahia (o cinza 232 da base chapada) de dentro do pergolado (do traço de fora da esquerda até a borda do
travertino) e a faixa entre a prainha e a linha do guarda-corpo, tecido do próprio deck bom (`fontes_px`) e emendado só
ao Bege bom de fora (a membrana vale só nos px do cinza 232 fora da zona, no tom do deck; a água, a linha do
guarda-corpo e o travertino ficam livres); os tracejados finos do pergolado de volta por cima (a camada do 12K).
O mesmo no 12K (`pergolado_12k`, chamado pelo `ampliacao_12k_terreo_casaa.montar12k` antes dos tracejados): o tecido do
deck da própria saída da IA, com a correção de tom calculada na escala da final e ampliada.

  python3 bege_pergolado_casaa_1211.py [--antes <png>] [--saida <png>]
Sem --antes, parte da final instalada; sem --saida, grava a final e o antes e depois
`renders/POE642_CasaA_PH_Terreo_1211c_bege_pergolado_antes_depois.jpg`.
"""

import argparse
import contextlib
import io
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

R = AQUI.parent / "renders"
FINAL = R / "POE642_CasaA_PH_Terreo_final_rotulos.png"
TRACOS = R / "POE642_CasaA_PH_Terreo_12K_tracejados.png"

PERGOLADO = {
    # a zona (px da final): o pergolado, do traço de fora da esquerda (x 1218) até o travertino, da linha de cima do
    # tracejado até o lounge; e a faixa entre a prainha (y 1046) e a linha do guarda-corpo (y 1061), à esquerda dele
    "caixas_px": [(1217, 875, 1520, 1214), (1090, 1046, 1217, 1061)],
    "bege": (232, 232, 232),
    "agua_folga_px": 2, "linha_folga_px": 1, "travertino_folga_px": 1,
    # as fontes: o deck à direita da piscina (abaixo das espreguiçadeiras), a faixa à esquerda do lounge e o deck de
    # cima (sem o rótulo)
    "fontes_px": [(1345, 725, 1505, 862), (1105, 1080, 1205, 1340), (1290, 345, 1450, 470)],
    "p_px": 24, "semente": 1212, "suave_px": 2.0, "salto": 14, "tom_tol": 22, "anel_px": 10,
    # no 12K: o retalho maior (o grão da IA) e a correção de tom na escala da final
    "p_12k": 72,
}


def _quadro():
    import final3840_casaa as FA
    with contextlib.redirect_stdout(io.StringIO()):
        return FA.QuadroA("Terreo")


def zona(Q, q=PERGOLADO):
    """(zona, bom): a zona refeita e o Bege bom de fora (bool, no quadro)."""
    C = Q.chapada.astype(np.int16)
    H, W = C.shape[:2]
    bege = (C == q["bege"]).all(axis=2)
    agua = (C == (255, 247, 223)).all(axis=2)
    linha = (np.abs(C - 146) <= 2).all(axis=2)
    trav = (np.abs(C - np.array((202, 217, 220))) <= 2).all(axis=2)

    def dil(m, r):
        return cv2.dilate(m.astype(np.uint8), np.ones((2 * r + 1, 2 * r + 1), np.uint8)) > 0
    caixa = np.zeros((H, W), bool)
    for x0, y0, x1, y1 in q["caixas_px"]:
        caixa[y0:y1, x0:x1] = True
    livre = ~dil(agua, q["agua_folga_px"]) & ~dil(linha, q["linha_folga_px"]) & ~dil(trav, q["travertino_folga_px"])
    # o tracejado da chapada (o cinza dos traços) entra na zona: o fechamento do Bege cobre os traços
    bege_f = cv2.morphologyEx(bege.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)) > 0
    Z = caixa & bege_f & livre
    bom = bege & ~Z & ~caixa & livre
    return Z, bom


def _tecido(img, fontes, h, w, p, semente):
    sys.path.insert(0, str(AQUI.parent.parent / "_texturas"))
    import texturas
    fs = []
    for a, b, c, d in fontes:
        f_ = img[b:d, a:c]
        fs += [f_, np.ascontiguousarray(f_[:, ::-1]), np.ascontiguousarray(f_[::-1])]
    tec = texturas.quilting(fs, h, w, p=p, sobra=max(3, p // 3), rng=np.random.default_rng(semente))[:h, :w]
    med = np.median(np.concatenate([f_.reshape(-1, 3) for f_ in fs]).astype(np.float32), axis=0)
    return tec.astype(np.float32), med


def _correcao(I, tec, Z, bom, med, q):
    """A membrana: a diferença entre o piso bom de fora e o tecido, levada para dentro da zona (só onde a borda é o
    Bege bom; na água, na linha e no travertino, a borda é livre)."""
    import pedidos_terreo_casaa_2910 as PT
    fixo = bom & ~PT._salientes(np.clip(I, 0, 255).astype(np.uint8), k=21, lim=q["salto"]) & \
        (np.abs(I - med).max(axis=2) < q["tom_tol"])
    V = fixo.astype(np.float32)
    s = q["suave_px"]
    c = cv2.GaussianBlur((I - tec) * V[..., None], (0, 0), s) / np.maximum(cv2.GaussianBlur(V, (0, 0), s),
                                                                         1e-3)[..., None]
    return PT._membrana(c, Z, fixo)


def tracos():
    import terreo_casaa_1011 as TA
    tr = cv2.imread(str(TRACOS))
    alfa = tr[..., 0].astype(np.float32) / 255
    cor = np.where(tr[..., 1] > 127, np.float32(TA.FINOS_TA["claro"][0]), np.float32(TA.FINOS_TA["escuro"][0]))
    return alfa, cor


def aplicar(antes, q=PERGOLADO):
    Q = _quadro()
    Z, bom = zona(Q, q)
    ys, xs = np.nonzero(Z)
    m = q["anel_px"] + 4
    y0, y1, x0, x1 = ys.min() - m, ys.max() + m + 1, xs.min() - m, xs.max() + m + 1
    h, w = y1 - y0, x1 - x0
    tec, med = _tecido(antes, q["fontes_px"], h, w, q["p_px"], q["semente"])
    I = antes[y0:y1, x0:x1].astype(np.float32)
    z, b = Z[y0:y1, x0:x1], bom[y0:y1, x0:x1]
    cor = _correcao(I, tec, z, b, med, q)
    novo = tec + cor
    out = antes.copy()
    reg = out[y0:y1, x0:x1]
    reg[z] = np.clip(np.round(novo[z]), 0, 255).astype(np.uint8)
    # os tracejados finos de volta, só na zona
    alfa, cr = tracos()
    a = (alfa * Z)[..., None]
    out = np.clip(np.round(out.astype(np.float32) * (1 - a) + cr[..., None] * a), 0, 255).astype(np.uint8)
    print(f"    Bege Bahia do pergolado: {int(Z.sum())} px refeitos (tom do deck BGR {np.round(med).astype(int)})")
    return out


def pergolado_12k(out, s, X0, Ya3, q=PERGOLADO):
    """No 12K (antes dos tracejados): o tecido do deck da saída da IA na zona ampliada, com a correção de tom calculada
    na escala da final (a saída reduzida) e ampliada."""
    Q = _quadro()
    Z, bom = zona(Q, q)
    ys, xs = np.nonzero(Z)
    m = q["anel_px"] + 4
    fy0, fy1, fx0, fx1 = ys.min() - m, ys.max() + m + 1, xs.min() - m, xs.max() + m + 1
    H, W = out.shape[:2]
    U0, V0 = int(np.floor((fx0 - X0) * s)), int(np.floor((fy0 - Ya3) * s))
    U1, V1 = min(int(np.ceil((fx1 - X0) * s)), W), min(int(np.ceil((fy1 - Ya3) * s)), H)
    # a final -> 12K (o mesmo da `biblioteca_terreo_casaa_1211.pecas_12k`)
    Mw = np.array([[1 / s, 0, U0 / s + X0 - fx0], [0, 1 / s, V0 / s + Ya3 - fy0]], np.float64)
    zf = cv2.warpAffine(Z[fy0:fy1, fx0:fx1].astype(np.float32), Mw, (U1 - U0, V1 - V0),
                        flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP)
    z12 = zf > 0.5
    fontes = [(int(round((a - X0) * s)), int(round((b - Ya3) * s)), int(round((c - X0) * s)), int(round((d - Ya3) * s)))
              for a, b, c, d in q["fontes_px"]]
    tec, med = _tecido(out, fontes, V1 - V0, U1 - U0, q["p_12k"], q["semente"] + 1)
    # a correção de tom na escala da final: a saída e o tecido reduzidos (área) à grade da final
    red = (fx1 - fx0, fy1 - fy0)
    Ir = cv2.resize(cv2.resize(out[V0:V1, U0:U1].astype(np.float32), None, fx=1 / s, fy=1 / s,
                               interpolation=cv2.INTER_AREA), red, interpolation=cv2.INTER_LINEAR)
    Tr = cv2.resize(cv2.resize(tec, None, fx=1 / s, fy=1 / s, interpolation=cv2.INTER_AREA), red,
                    interpolation=cv2.INTER_LINEAR)
    cor = _correcao(Ir, Tr, Z[fy0:fy1, fx0:fx1], bom[fy0:fy1, fx0:fx1], med, dict(q, salto=q["salto"] + 4))
    cor12 = cv2.warpAffine(cor.astype(np.float32), Mw, (U1 - U0, V1 - V0),
                           flags=cv2.INTER_CUBIC | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REPLICATE)
    novo = np.clip(np.round(tec + cor12), 0, 255).astype(np.uint8)
    reg = out[V0:V1, U0:U1]
    reg[z12] = novo[z12]
    print(f"    Bege Bahia do pergolado no 12K: {int(z12.sum())} px")
    return out


def antes_depois(antes, depois, destino, caixa=(1080, 840, 1540, 1230), escala=2):
    x0, y0, x1, y1 = caixa
    a = cv2.resize(antes[y0:y1, x0:x1], None, fx=escala, fy=escala, interpolation=cv2.INTER_LANCZOS4)
    d = cv2.resize(depois[y0:y1, x0:x1], None, fx=escala, fy=escala, interpolation=cv2.INTER_LANCZOS4)
    sep = np.full((a.shape[0], 16, 3), 255, np.uint8)
    topo = np.full((44, a.shape[1] * 2 + 16, 3), 255, np.uint8)
    cv2.putText(topo, "ANTES", (12, 32), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (40, 40, 40), 2, cv2.LINE_AA)
    cv2.putText(topo, "DEPOIS", (a.shape[1] + 28, 32), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (40, 40, 40), 2, cv2.LINE_AA)
    cv2.imwrite(str(destino), np.vstack([topo, np.hstack([a, sep, d])]), [cv2.IMWRITE_JPEG_QUALITY, 90])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--antes")
    ap.add_argument("--saida")
    a = ap.parse_args()
    antes = cv2.imread(a.antes or str(FINAL))
    depois = aplicar(antes)
    destino = Path(a.saida) if a.saida else FINAL
    cv2.imwrite(str(destino), depois)
    print(f"    {destino}")
    if not a.saida:
        ad = R / "POE642_CasaA_PH_Terreo_1211c_bege_pergolado_antes_depois.jpg"
        antes_depois(antes, depois, ad)
        print(f"    {ad}")


if __name__ == "__main__":
    main()

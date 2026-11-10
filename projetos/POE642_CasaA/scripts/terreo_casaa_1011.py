r"""Casa A, Térreo: as correções de 10/11/26 (lista do cliente, com os recortes da planta, e as respostas do usuário).

Um passo por pedido, sobre a final do Térreo de antes (a do commit 58ea098, a mesma de 0a17741), na ordem de
`correcoes_ta`:

1. Os tracejados (cliente: "Remover as linhas tracejadas. Fica uma representação mais técnica e pode confundir quem
   olha a planta. Deixar apenas as que representam 'vazios'"; o usuário aprovou a lista): saem os afastamentos, os dois
   contornos da laje da cobertura, a grade do pergolado e as linhas da garagem; ficam os X dos vazios (`tracejados_ta`).
2. O piso marrom (cliente: "Trocar o marrom do piso por essa opção. Para deixar o marrom mais uniforme com o restante da
   casa e mais sóbrio." e "As bancadas que são em marrom tabaco podem permanecer no tom mais escuro"): o granito do
   piso no marrom da amostra (`piso_marrom_ta`); as bancadas ficam.
3. A piscina (cliente: "Deixar o tom de azul para a piscina mais sóbrio. Ver exemplo."; usuário: "USAR COMO REFERENCIA O
   TOM DA PISCINA E PRAINHA DA IMAGEM 3. E O REVESTIMENTO BARLAVENTO PORTOBELO DA PISCINA"): `piscina_ta`.
4. As árvores (cliente: "No terreno não precisa representar muitas árvores ... Representar arbustos que são menores";
   usuário: "Arbustos e 4 árvores"): `vegetacao_ta`.
5. As escadas (cliente: "Colocar a seta na escada e a descrição Desce para o subsolo"; usuário: "NA ESCADA DE PLACAS
   ESCALONADAS - DESCE PARA O DECK; NA ESCADA ABAIXO DO SPA - DESCE PARA O SUBSOLO"): `escadas_ta`.
6. As banquetas da área gourmet (cliente: "Colocar só 5 banquetas. E com um tom um pouco mais destacado em relação ao
   piso"): `banquetas_ta`.
7. O pilar (cliente: "Falha na representação do pilar."): `pilar_ta`.

Uso (de POE642_CasaA/scripts/):
  python3 terreo_casaa_1011.py --antes <a final do Térreo do commit 58ea098> [--ate <passo>] [--saida <png>]
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
from scipy import ndimage

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import final3840_casaa as FA                                    # noqa: E402
import final3840_casaa_terreo as T                              # noqa: E402

FINAL = FA.CASA / "renders" / "POE642_CasaA_PH_Terreo_final_rotulos.png"


# ----------------------------------------------------------------------------------------------------------------------
# Ferramentas
def materiais(Q):
    """O material de cada px pela base chapada (as cores frequentes do PDF; o antialias, o material mais perto)."""
    if getattr(Q, "_materiais", None) is None:
        c = Q.chapada.astype(np.int32)
        k = (c[..., 0] << 16) | (c[..., 1] << 8) | c[..., 2]
        cores, inv, n = np.unique(k, return_inverse=True, return_counts=True)
        lab = inv.reshape(k.shape)
        raro = n[lab] < 5000
        _, (iy, ix) = ndimage.distance_transform_edt(raro, return_indices=True)
        Q._materiais = lab[iy, ix]
    return Q._materiais


def dilatar(m, px):
    if px <= 0:
        return m.astype(bool)
    return cv2.dilate(m.astype(np.uint8), np.ones((2 * px + 1, 2 * px + 1), np.uint8)).astype(bool)


def alfa_segs(Q, segs, larg_px, ss=4):
    """O alfa dos segmentos (pt) no quadro, com a largura dada (px)."""
    m = np.zeros((Q.H * ss, Q.W * ss), np.uint8)
    for x0, y0, x1, y1 in segs:
        (u0, v0), (u1, v1) = Q.p2q(x0, y0), Q.p2q(x1, y1)
        cv2.line(m, (int(round(u0 * ss)), int(round(v0 * ss))), (int(round(u1 * ss)), int(round(v1 * ss))), 255,
                 max(1, int(round(larg_px * ss))), cv2.LINE_AA)
    return cv2.resize(m.astype(np.float32) / 255, (Q.W, Q.H), interpolation=cv2.INTER_AREA)


def rotulos_alfa(Q, img):
    """O alfa de todos os rótulos dos ambientes (os do PDF, onde a final os desenhou), para protegê-los."""
    import revisao_casaa_2910 as R
    import pedidos_terreo_casaa_2910 as P
    rot, aj = R._rotulos_pav(Q)
    q = dict(P.ROTULOS_OUTROS_TA)
    a = np.zeros(img.shape[:2], np.float32)
    achados = []
    for r in rot:
        al, _ = P._achar_rotulo(Q, img, r, aj, q)
        if al.max() > 0.3:
            a = np.maximum(a, al)
            achados.append((r, al))
    return a, achados


def espelhar_bandas(img, banda, horizontal, fonte_ok, mat):
    """Os px da `banda` recebem o material de fora dela, refletido na borda dela, coluna a coluna (bandas horizontais)
    ou linha a linha (verticais), do mesmo material (`mat`) e só de px de `fonte_ok`; primeiro do próprio lado, senão do
    outro. Devolve a imagem e os px que ficaram sem fonte."""
    out = img.copy()
    if not horizontal:
        o, f = espelhar_bandas(img.transpose(1, 0, 2), banda.T, True, fonte_ok.T, mat.T)
        return o.transpose(1, 0, 2).copy(), f.T.copy()
    H = banda.shape[0]
    falta = np.zeros(banda.shape, bool)
    for x in np.nonzero(banda.any(axis=0))[0]:
        col = banda[:, x]
        d = np.diff(np.r_[0, col.astype(np.int8), 0])
        for r0, r1 in zip(np.nonzero(d == 1)[0], np.nonzero(d == -1)[0] - 1):
            meio = (r0 + r1) / 2
            for r in range(r0, r1 + 1):
                lados = ((2 * r0 - 1 - r), (2 * r1 + 1 - r))
                if r > meio:
                    lados = lados[::-1]
                feito = False
                for s in lados:
                    for extra in (0, 1, 2, 3):
                        ss = s - extra if s < r0 else s + extra
                        if 0 <= ss < H and fonte_ok[ss, x] and mat[ss, x] == mat[r, x]:
                            out[r, x] = img[ss, x]
                            feito = True
                            break
                    if feito:
                        break
                if not feito:
                    falta[r, x] = True
    return out, falta


# ----------------------------------------------------------------------------------------------------------------------
# 1. Os tracejados. Saem (pelo PDF, a reta inteira de cada um, do primeiro ao último traço):
# - os afastamentos (DOC_LINHAS E PROJEÇÕES, as 4 retas de `pedidos_terreo_casaa_2910.TRACEJADOS_TA["afastamento"]`);
# - os dois contornos da laje da cobertura (ARQ_CONTRAPISO, retas horizontais e verticais em `laje_px`), com os lados da
#   esquerda do terraço gourmet que o render desenhou em cinza (`laje_extra_px`);
# - a grade do pergolado sobre a prainha (ARQ_PERGOLADO).
# Na faixa de `banda_px` de cada lado da reta, o material de fora, refletido na borda da faixa, só do mesmo material da
# base chapada; ficam as paredes, os pilares, os rótulos e os tracejados dos vazios. Ficam os X dos vazios (DOC_LINHAS
# E PROJEÇÕES dentro de `vazios_px`): a varanda e a sala de estar (sob o vazio do 1º Pavimento), a escada caracol, a
# área de serviço descoberta, a claraboia do lavabo e o shaft. O lado esquerdo do vazio da varanda era a linha da laje
# (9 px fora dos vértices do X): entra no alinhamento do X, no traço da moldura (`vazio_esquerda_pt`).
TRACEJADOS_TA = {"laje_px": {"h": (299, 335, 1177, 1213, 1637, 1672), "v": (2635, 2599, 1521, 1485)}, "tol_px": 3,
                 "laje_extra_px": [((1219, 1177), (1219, 1675)), ((1255, 1213), (1255, 1640))],
                 "banda_px": 3, "vazios_px": [(1505, 600, 2160, 888), (1905, 1490, 2048, 1640),
                                             (1700, 1638, 1918, 1935), (2248, 345, 2352, 392), (2348, 1110, 2392, 1214)],
                 "vazio_esquerda_pt": 1315.4}


def _segs_vazios(Q, q):
    segs = []
    for _, _, ss in T.cadeias_tracejadas(Q, ["DOC_LINHAS E PROJEÇÕES"], min_n=2, min_ext=20):
        for s in ss:
            u, v = Q.p2q((s[0] + s[2]) / 2, (s[1] + s[3]) / 2)
            if any(a <= u <= c and b <= v <= d for a, b, c, d in q["vazios_px"]):
                segs.append(s)
    return segs


def _linhas_remover(Q, q):
    """As retas a tirar, em px: (p0, p1, horizontal)."""
    import pedidos_terreo_casaa_2910 as P
    linhas = []
    for a, o in P.TRACEJADOS_TA["afastamento"]:
        g = P._segs_doc(Q, a, o, "DOC_LINHAS E PROJEÇÕES")
        if g:
            x0, y0, x1, y1 = P._linha_inteira(g)
            linhas.append((Q.p2q(x0, y0), Q.p2q(x1, y1), a == 0.0))
    for (cam, a, off), ext, segs in T.cadeias_tracejadas(Q, ["ARQ_CONTRAPISO"], min_ext=40):
        if a not in (0.0, 90.0):
            continue
        p = [Q.p2q(x, y) for s in segs for x, y in ((s[0], s[1]), (s[2], s[3]))]
        pos = p[0][1] if a == 0.0 else p[0][0]
        alvo = q["laje_px"]["h" if a == 0.0 else "v"]
        if any(abs(pos - t) <= q["tol_px"] for t in alvo):
            x0, y0, x1, y1 = P._linha_inteira(segs)
            linhas.append((Q.p2q(x0, y0), Q.p2q(x1, y1), a == 0.0))
    for _, _, segs in T.cadeias_tracejadas(Q, ["ARQ_PERGOLADO"]):
        x0, y0, x1, y1 = P._linha_inteira(segs)
        (u0, v0), (u1, v1) = Q.p2q(x0, y0), Q.p2q(x1, y1)
        linhas.append(((u0, v0), (u1, v1), abs(v1 - v0) < abs(u1 - u0)))
    for p0, p1 in q["laje_extra_px"]:
        linhas.append((p0, p1, p0[1] == p1[1]))
    return linhas


def tracejados_ta(Q, img, q=None):
    q = q or TRACEJADOS_TA
    h = q["banda_px"]
    linhas = _linhas_remover(Q, q)
    bh, bv = np.zeros((Q.H, Q.W), np.uint8), np.zeros((Q.H, Q.W), np.uint8)
    for p0, p1, horiz in linhas:
        cv2.line(bh if horiz else bv, tuple(int(round(c)) for c in p0), tuple(int(round(c)) for c in p1), 1, 2 * h + 1)
    vazios = alfa_segs(Q, _segs_vazios(Q, q), 3.0) > 0.02
    par = FA.paredes_pdf(Q) > 0.05
    pil = Q.preencher(lambda d: d.get("layer") == "EST_PILAR", ss=2) > 0.05
    rot, _ = rotulos_alfa(Q, img)
    fixo = dilatar(par | pil, 1) | dilatar(rot > 0.02, 1) | vazios
    mat = materiais(Q)
    bh, bv = bh.astype(bool) & ~fixo, bv.astype(bool) & ~fixo
    out, f1 = espelhar_bandas(img, bh, True, ~bh & ~fixo, mat)
    out, f2 = espelhar_bandas(out, bv, False, ~bv & ~fixo, mat)
    falta = f1 | f2
    if falta.any():
        out = cv2.inpaint(out, (falta * 255).astype(np.uint8), 3, cv2.INPAINT_TELEA)
    # o lado esquerdo do vazio da varanda, no alinhamento do X e no traço da moldura (o da direita, espelhado)
    x = q["vazio_esquerda_pt"]
    lado = [(x, s[1], x, s[3]) for k, _, ss in T.cadeias_tracejadas(Q, ["DOC_LINHAS E PROJEÇÕES"])
            if k[1] == 90.0 and round(k[2]) == -1922 for s in ss]
    out, _ = T.preto_branco(Q, out, lado)
    print(f"    tracejados: {len(linhas)} retas tiradas (afastamentos, laje da cobertura, pergolado), "
          f"{int((bh | bv).sum())} px; ficam os X dos vazios; o lado esquerdo do vazio da varanda ({len(lado)} traços); "
          f"{int(falta.sum())} px sem fonte (inpaint)")
    return out


# ----------------------------------------------------------------------------------------------------------------------
PASSOS = [("tracejados", tracejados_ta)]


def correcoes_ta(img, ate=None, salvar_passos=None):
    Q = FA.QuadroA("Terreo")
    out = img.copy()
    for nome, f in PASSOS:
        print(f"  {nome}")
        out = f(Q, out)
        if salvar_passos:
            cv2.imwrite(str(Path(salvar_passos) / f"passo_{nome}.png"), out)
        if nome == ate:
            break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--antes", required=True)
    ap.add_argument("--ate")
    ap.add_argument("--saida")
    ap.add_argument("--passos")
    a = ap.parse_args()
    img = cv2.imread(a.antes)
    out = correcoes_ta(img, a.ate, a.passos)
    cv2.imwrite(a.saida or str(FINAL), out)


if __name__ == "__main__":
    main()

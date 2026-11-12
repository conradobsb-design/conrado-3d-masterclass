"""As regras de 12/11 do Subsolo levadas ao Térreo e ao 1º Pavimento da Casa A.

Usuário (12/11), depois dos defeitos do Subsolo ("OS X PRECISAM SER EM CINZA COM TRAÇOS MAIS FINOS E DELICADOS";
"DEIXAR O CONTORNO EM VOLTA DOS VASOS PERFEITOS."; "DEIXAR AS PAREDES RETAS"): "PODE APLICAR NO TÉRREO E 1º PAVIMENTO
DA CASA A". Sobre a final de cada pavimento (como está no commit `ANTES_COMMIT`):

- **Shafts (`SHAFTS`, `shafts`):** o vão de cada shaft limpo (o fundo claro, sem o rosado nem os restos do render) e o X
  de canto a canto redesenhado em cinza médio (128), com 0,8 px, tracejado e simétrico (um traço cruza o centro, o mesmo
  passo para os dois lados). No 1º Pavimento, os 4 shafts de `um_pav_casaa_1111.SHAFTS_1P` (o X ia em cinza 60); no
  Térreo, o shaft junto ao elevador (o vão achado na final dentro da caixa do PDF de
  `revisao_casaa_2910.ELEVADOR_TA["shafts_pt"]["Terreo"]`; o X ia escuro, sobre um fundo rosado). `desenhar_x` serve
  também ao 12K (`ampliacao_12k_terreo_casaa.montar12k`), que desenha o mesmo X na escala dele (`shafts_12k`).
- **Paredes retas (`PAREDES`, `biblioteca_subsolo_casaa_1211.paredes_retas`):** a mesma rotina do Subsolo, com o cinza
  das paredes de cada pavimento (53 no Térreo, mais escuras desde 11/11; 80 no 1º Pavimento) e o preto das esquadrias
  abaixo dele (no Térreo, abaixo de 35). Ficam o elevador, as esquadrias pretas e o que não é parede.
- **Vasos (`VASOS`, `vasos`):** o contorno em volta de cada vaso sem pontos soltos: no anel de `anel_px` em volta do
  retângulo do vaso do PDF, o px claro que foge do piso em volta (o ponto branco do vaso do lavabo junto à parede) é
  refeito pelo piso de perto (inpaint). Os vasos dos dois pavimentos não têm o retângulo chapado do Subsolo.

  python3 regras_1211_casaa.py Terreo [--saida <png>]
  python3 regras_1211_casaa.py 1Pavimento [--saida <png>]

Sem `--saida`, grava a final do pavimento e os antes/depois em `renders/POE642_CasaA_PH_{pav}_1211_*_antes_depois.jpg`.
"""
import argparse
import contextlib
import io
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
from scipy import ndimage

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import final3840_casaa as FA                    # noqa: E402
import biblioteca_subsolo_casaa_1211 as BS      # noqa: E402

CASA = FA.CASA
RAIZ_GIT = CASA.parent.parent
ANTES_COMMIT = "1415b75"
FINAIS = {"Terreo": CASA / "renders" / "POE642_CasaA_PH_Terreo_final_rotulos.png",
          "1Pavimento": CASA / "renders" / "POE642_CasaA_PH_1Pavimento_v7_final_rotulos.png"}

# o X dos shafts (o mesmo traço do Subsolo: cinza 128, 0,8 px; o passo e o recuo do X do 1º Pavimento)
SHAFTS = {"fundo": (246, 246, 245), "x": (128, 128, 128), "x_px": 0.8, "traco_px": 3.4, "vao_px": 2.2,
          "recuo_px": 1.8, "ss": 8, "aro_px": 1.5, "aro_desvio": 12,
          # Térreo: a caixa do PDF (pt) e o cinza das paredes, para achar o vão na final
          "Terreo": {"caixas_pt": None, "parede": 53, "tol": 18},
          # 1º Pavimento: os vãos da final (`um_pav_casaa_1111.SHAFTS_1P["shafts_px"]`)
          "1Pavimento": {"vaos_px": None}}

PAREDES = {"Terreo": dict(BS.PAREDES_RETAS, cor=53, tol=14, preto_max=35, fora_fundo=True),
           "1Pavimento": dict(BS.PAREDES_RETAS, fora_fundo=True)}

VASOS = {"anel_px": 3, "desvio": 45, "claro": 25, "escuro": 110, "claro_louca": 20, "miolo_max_px": 40}


def quadro(pav):
    with contextlib.redirect_stdout(io.StringIO()):
        return FA.QuadroA(pav)


def vaos_shafts(pav, Q, img):
    """Os vãos dos shafts do pavimento na final, (x0, y0, x1, y1) em px inteiros (x1, y1 exclusivos)."""
    if pav == "1Pavimento":
        import um_pav_casaa_1111 as U
        return [tuple(r) for r in (SHAFTS["1Pavimento"]["vaos_px"] or U.SHAFTS_1P["shafts_px"])]
    import revisao_casaa_2910 as RA
    q = SHAFTS["Terreo"]
    vaos = []
    for caixa in q["caixas_pt"] or RA.ELEVADOR_TA["shafts_pt"]["Terreo"]:
        x0, y0, x1, y1 = BS.caixa_px(Q, caixa)
        X0, Y0, X1, Y1 = int(np.floor(x0)) - 3, int(np.floor(y0)) - 3, int(np.ceil(x1)) + 3, int(np.ceil(y1)) + 3
        reg = img[Y0:Y1, X0:X1].astype(np.int16)
        parede = (np.abs(reg - q["parede"]).max(axis=2) <= q["tol"]) & ((reg.max(axis=2) - reg.min(axis=2)) <= 12)
        n, lab, st, _ = cv2.connectedComponentsWithStats((~parede).astype(np.uint8), 4)
        cand = [i for i in range(1, n) if st[i, 0] > 0 and st[i, 1] > 0 and st[i, 0] + st[i, 2] < reg.shape[1]
                and st[i, 1] + st[i, 3] < reg.shape[0]]
        i = max(cand, key=lambda i: st[i, 4])
        vaos.append((X0 + st[i, 0], Y0 + st[i, 1], X0 + st[i, 0] + st[i, 2], Y0 + st[i, 1] + st[i, 3]))
    return vaos


def desenhar_x(img, vao, s=1.0, ox=0.0, oy=0.0, q=None):
    """O vão (px da final, x1/y1 exclusivos) no fundo claro e o X tracejado de canto a canto em cinza fino, na escala
    `s` (px da final -> px de img: (x - ox) * s)."""
    q = q or SHAFTS
    x0, y0, x1, y1 = [float(v) for v in vao]
    a0, b0, a1, b1 = (x0 - ox) * s, (y0 - oy) * s, (x1 - ox) * s, (y1 - oy) * s
    A0, B0, A1, B1 = int(np.round(a0)), int(np.round(b0)), int(np.round(a1)), int(np.round(b1))
    img[B0:B1, A0:A1] = q["fundo"]
    ss = q["ss"]
    w, h = A1 - A0, B1 - B0
    M = np.zeros((h * ss, w * ss), np.uint8)
    r = q["recuo_px"] * s
    traco, passo = q["traco_px"] * s, (q["traco_px"] + q["vao_px"]) * s
    for (ax, ay), (bx, by) in (((a0 + r, b0 + r), (a1 - r, b1 - r)), ((a1 - r, b0 + r), (a0 + r, b1 - r))):
        cx, cy = (ax + bx) / 2, (ay + by) / 2
        L = np.hypot(bx - ax, by - ay) / 2
        ux, uy = (bx - ax) / (2 * L), (by - ay) / (2 * L)
        kmax = int(np.ceil(L / passo)) + 1
        for kk in range(-kmax, kmax + 1):
            t0, t1 = max(kk * passo - traco / 2, -L), min(kk * passo + traco / 2, L)
            if t1 - t0 < 0.4 * s:
                continue
            p0 = ((cx + ux * t0 - A0) * ss, (cy + uy * t0 - B0) * ss)
            p1 = ((cx + ux * t1 - A0) * ss, (cy + uy * t1 - B0) * ss)
            cv2.line(M, tuple(int(round(v)) for v in p0), tuple(int(round(v)) for v in p1), 255,
                     max(1, int(round(q["x_px"] * s * ss))), cv2.LINE_AA)
    al = cv2.resize(M.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)[..., None]
    reg = img[B0:B1, A0:A1].astype(np.float32)
    img[B0:B1, A0:A1] = np.clip(np.round(reg * (1 - al) + np.float32(q["x"]) * al), 0, 255).astype(np.uint8)
    return img


def limpar_aro(img, vao, s=1.0, ox=0.0, oy=0.0, q=None):
    """A parede em volta do vão (uma faixa de `aro_px` px da final): em cada lado e a cada distância da beira, o px cinza
    que foge mais de `aro_desvio` da mediana da faixa volta a ela (os pontinhos claros nos cantos do vão; o fio escuro
    da beira, quando uniforme, fica)."""
    q = q or SHAFTS
    x0, y0, x1, y1 = [float(v) for v in vao]
    A0, B0 = int(np.round((x0 - ox) * s)), int(np.round((y0 - oy) * s))
    A1, B1 = int(np.round((x1 - ox) * s)), int(np.round((y1 - oy) * s))
    k = max(1, int(np.ceil(q["aro_px"] * s)))
    H, W = img.shape[:2]
    faixas = []                                         # (linhas ou colunas, fatia ao longo, eixo)
    for d in range(k):
        faixas += [(B0 - 1 - d, slice(A0 - k, A1 + k), 0), (B1 + d, slice(A0 - k, A1 + k), 0),
                   (A0 - 1 - d, slice(B0, B1), 1), (A1 + d, slice(B0, B1), 1)]
    n = 0
    for i, fat, eixo in faixas:
        if eixo == 0:
            if not 0 <= i < H:
                continue
            reg = img[i, max(fat.start, 0):min(fat.stop, W)]
        else:
            if not 0 <= i < W:
                continue
            reg = img[max(fat.start, 0):min(fat.stop, H), i]
        r = reg.astype(np.int16)
        cinza = (r.max(axis=1) - r.min(axis=1)) <= 12
        if cinza.mean() < 0.9:
            continue                                    # não é parede: fica como está
        med = np.median(r[cinza], axis=0)
        fora = cinza & (np.abs(r - med).max(axis=1) > q["aro_desvio"])
        reg[fora] = np.round(med).astype(np.uint8)
        n += int(fora.sum())
    return img, n


def shafts(pav, Q, img):
    vaos = vaos_shafts(pav, Q, img)
    for v in vaos:
        img = desenhar_x(img, v)
        img, n = limpar_aro(img, v)
        if n:
            print(f"    aro do vão {tuple(map(int, v))}: {n} px fora do tom da parede")
    print(f"    shafts: {len(vaos)} vãos no fundo claro e o X em cinza fino ({', '.join(str(tuple(map(int, v))) for v in vaos)})")
    return img


def vasos_12k(pav, final, entrada, out, s, X0, Yia, Ya3, q=None):
    """Os vasos de `DOZE["vasos_entrada"]` no 12K: o vaso (o que foge do piso na caixa do PDF, com folga), o trecho
    entre ele e a parede e uma faixa junto à face da parede, do alto do ambiente até um pouco abaixo do vaso, com a
    entrada da IA (a final sem textos) ampliada em Lanczos e um pouco de nitidez, com a beira em pluma. Devolve também
    a máscara (px da final) onde os tracejados finos não entram."""
    q = q or DOZE
    nomes = q["vasos_entrada"].get(pav, ())
    sem_tracos = np.zeros(final.shape[:2], bool)
    if not nomes:
        return out, sem_tracos
    Q = quadro(pav)
    parede, tol = (SHAFTS["Terreo"]["parede"], SHAFTS["Terreo"]["tol"]) if pav == "Terreo" else (80, 18)
    H, W = final.shape[:2]
    f16 = final.astype(np.int16)
    e_parede = (np.abs(f16 - parede).max(axis=2) <= tol) & ((f16.max(axis=2) - f16.min(axis=2)) <= 12)
    for nome, c in vasos_pav(pav, Q):
        if nome not in nomes:
            continue
        x0, y0, x1, y1 = BS.caixa_px(Q, c)
        X0b, Y0b, X1b, Y1b = int(np.floor(x0)), int(np.floor(y0)), int(np.ceil(x1)), int(np.ceil(y1))
        m = np.zeros((H, W), bool)
        da_final = np.zeros((H, W), bool)          # a caixa do vaso e a faixa da parede: sem textos, vêm da final
        da_final[Y0b:Y1b, X0b:X1b] = True
        # o vaso: o que foge do tom do piso em volta, na caixa com folga
        f = q["vaso_folga_px"]
        anel = np.zeros((H, W), bool)
        anel[Y0b - 2 * f - 4:Y1b + 2 * f + 4, X0b - 2 * f - 4:X1b + 2 * f + 4] = True
        anel[Y0b - f:Y1b + f, X0b - f:X1b + f] = False
        piso = anel & ~e_parede & (final.min(axis=2) >= 150)
        med = np.median(final[piso].astype(np.float32), axis=0)
        cx = np.zeros((H, W), bool)
        cx[Y0b - f:Y1b + f, X0b - f:X1b + f] = True
        objeto = cx & ~e_parede & (np.abs(final.astype(np.float32) - med).max(axis=2) > q["vaso_desvio"])
        m |= cv2.dilate(objeto.astype(np.uint8), np.ones((2 * f + 1, 2 * f + 1), np.uint8)).astype(bool) & ~e_parede
        # a face da parede no lado em que o vaso encosta (o primeiro px de parede a partir da caixa)
        # (procurada numa linha logo acima do vaso: a parte escura do vaso se confunde com a parede)
        yc = Y0b - f - 2
        lados = {"direita": (yc, range(X1b - 6, X1b + 8)), "esquerda": (yc, range(X0b + 5, X0b - 9, -1))}
        for lado, (yy, xs) in lados.items():
            xw = next((x for x in xs if e_parede[yy, x]), None)
            if xw is None:
                continue
            k = q["parede_faixa_px"]
            xa, xb = (xw - k, xw) if lado == "direita" else (xw + 1, xw + 1 + k)
            xi = xa if lado == "direita" else xb - 1
            yt = next(y for y in range(yc, 0, -1) if e_parede[y, xi])      # o alto do ambiente nessa coluna
            yb = Y1b + q["parede_abaixo_px"]
            m[yt + 1:yb, xa:xb] = True
            da_final[yt + 1:yb, xa:xb] = True
            # os tracejados finos não passam por essa faixa (a camada tinha resíduos na sombra da face da parede,
            # que viravam quadradinhos claros); fica só o fim da diagonal da claraboia nas 2 linhas do canto
            sem_tracos[yt + 3:yb, xa:xb] = True
            if lado == "direita":
                m[Y0b - f:Y1b + f, X1b - 1:xw] = True
            else:
                m[Y0b - f:Y1b + f, xw + 1:X0b + 1] = True
            m &= ~e_parede
        ys, xs = np.nonzero(m)
        pad = 4
        fx0, fy0, fx1, fy1 = xs.min() - pad, ys.min() - pad, xs.max() + 1 + pad, ys.max() + 1 + pad
        U0, V0 = int(np.floor((fx0 - X0) * s)), int(np.floor((fy0 - Ya3) * s))
        U1, V1 = int(np.ceil((fx1 - X0) * s)), int(np.ceil((fy1 - Ya3) * s))
        w, h = U1 - U0, V1 - V0
        # 12K -> final pela mesma conta de índices de `montar12k`, sem meio px (o que a IA ampliada já segue)
        Mf = np.array([[1 / s, 0, U0 / s + X0], [0, 1 / s, V0 / s + Ya3]], np.float64)
        # o contorno do vaso liso no 12K: a cobertura do vaso sobre o piso (a projeção de cada px no eixo piso -> vaso,
        # que guarda o antisserrilhado da final) ampliada e só então recortada; a cor do vaso e a do piso em camadas
        # separadas (cada uma completada por inpaint), ampliadas e compostas por essa cobertura
        ex0, ey0 = fx0 - X0, fy0 - Yia
        E = entrada[ey0:ey0 + (fy1 - fy0), ex0:ex0 + (fx1 - fx0)].copy()
        # (a entrada não recebe as correções da final junto aos tracejados, e a face dessa parede tinha resíduos na
        # camada deles: na caixa do vaso e na faixa da parede, onde não há texto, vale a final)
        zf = da_final[fy0:fy1, fx0:fx1]
        E[zf] = final[fy0:fy1, fx0:fx1][zf]
        ob = objeto[fy0:fy1, fx0:fx1]
        dentro = cv2.erode(ob.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        cor_v = np.median(E[dentro].astype(np.float32), axis=0)
        eixo = cor_v - med
        cov = np.clip(((E.astype(np.float32) - med) @ eixo) / float(eixo @ eixo), 0, 1)
        perto = cv2.dilate(ob.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
        cov[~perto] = 0
        cheio = (cov > 0.9).astype(np.uint8)
        camada_v = cv2.inpaint(E, (1 - cheio) * 255, 3, cv2.INPAINT_TELEA) if cheio.any() else E
        vazio = cv2.dilate((cov > 0.08).astype(np.uint8), np.ones((3, 3), np.uint8))
        camada_p = cv2.inpaint(E, vazio * 255, 3, cv2.INPAINT_TELEA)
        Mw = np.array([[1 / s, 0, U0 / s + X0 - fx0], [0, 1 / s, V0 / s + Ya3 - fy0]], np.float64)
        def amplia(a, flag=cv2.INTER_LANCZOS4):
            return cv2.warpAffine(a, Mw, (w, h), flags=flag | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REPLICATE)
        up_v, up_p = amplia(camada_v).astype(np.float32), amplia(camada_p).astype(np.float32)
        c = amplia(cov.astype(np.float32), cv2.INTER_CUBIC)
        c = cv2.GaussianBlur(c, (0, 0), q["vaso_liso_px"] * s)
        t = np.clip((c - 0.5) / q["vaso_corte"] + 0.5, 0, 1)
        a_v = (t * t * (3 - 2 * t))[..., None]
        src = up_p * (1 - a_v) + up_v * a_v
        src = src + q["vaso_nitidez"] * (src - cv2.GaussianBlur(src, (0, 0), 0.6 * s))
        al = cv2.warpAffine(m.astype(np.float32), Mf, (w, h), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP)
        al = np.clip(cv2.GaussianBlur(al, (0, 0), q["vaso_pluma_px"] * s), 0, 1)[..., None]
        reg = out[V0:V1, U0:U1].astype(np.float32)
        out[V0:V1, U0:U1] = np.clip(np.round(reg * (1 - al) + src * al), 0, 255).astype(np.uint8)
        print(f"    vaso {nome}: refeito no 12K com a entrada ampliada ({int(m.sum())} px da final)")
    return out, sem_tracos


def shafts_12k(pav, final, out, s, ox, oy):
    """O mesmo X na escala do 12K (`ampliacao_12k_terreo_casaa.montar12k`), sobre o miolo dos shafts."""
    for v in vaos_shafts(pav, quadro(pav), final):
        out = desenhar_x(out, v, s, ox, oy)
        out, _ = limpar_aro(out, v, s, ox, oy)
    return out


def vasos_pav(pav, Q):
    """Os retângulos (pt) dos vasos do pavimento."""
    if pav == "Terreo":
        import final3840_casaa_terreo as T
        return [(n, c) for n, c, _ in T.LOUCAS["vasos"]]
    import final3840_casaa_1pav as P1
    return [(nome, b["vaso"][0]) for nome, b in P1.BANHOS_1P.items() if isinstance(b, dict) and "vaso" in b]


def vasos(pav, Q, img):
    q = VASOS
    out = img.copy()
    total = 0
    for nome, caixa in vasos_pav(pav, Q):
        x0, y0, x1, y1 = BS.caixa_px(Q, caixa)
        a = q["anel_px"]
        X0, Y0, X1, Y1 = int(np.floor(x0)) - a - 6, int(np.floor(y0)) - a - 6, int(np.ceil(x1)) + a + 6, \
            int(np.ceil(y1)) + a + 6
        jan = np.ascontiguousarray(out[Y0:Y1, X0:X1])
        caixa_m = np.zeros(jan.shape[:2], np.uint8)
        caixa_m[int(np.floor(y0)) - Y0:int(np.ceil(y1)) - Y0, int(np.floor(x0)) - X0:int(np.ceil(x1)) - X0] = 1
        anel = cv2.dilate(caixa_m, np.ones((2 * a + 1,) * 2, np.uint8)) - caixa_m
        fora = cv2.dilate(caixa_m, np.ones((2 * a + 13,) * 2, np.uint8)) - cv2.dilate(caixa_m, np.ones((2 * a + 1,) * 2,
                                                                                                    np.uint8))
        j16 = jan.astype(np.int16)
        lum = j16.mean(axis=2)
        piso = fora.astype(bool) & (lum > np.percentile(lum[fora.astype(bool)], 25))
        med = np.median(j16[piso], axis=0)
        # o ponto claro solto: bem mais claro que o piso em volta e fora do tom dele
        m = anel.astype(bool) & (np.abs(j16 - med).max(axis=2) > q["desvio"]) & (lum > med.mean() + q["claro"])
        if m.any():
            mm = ndimage.binary_dilation(m, iterations=1).astype(np.uint8)
            out[Y0:Y1, X0:X1] = cv2.inpaint(jan, mm, 2, cv2.INPAINT_TELEA)
            total += int(m.sum())
            print(f"    vaso {nome}: {int(m.sum())} px claros soltos em volta refeitos pelo piso")
        # nos vasos escuros (louça marrom), o ponto claro na beira do vaso junto à parede vira a louça
        corpo = cv2.erode(caixa_m, np.ones((7, 7), np.uint8)).astype(bool)
        if corpo.any():
            jan = out[Y0:Y1, X0:X1]
            j16 = jan.astype(np.int16)
            lum = j16.mean(axis=2)
            louca = np.median(j16[corpo], axis=0)
            if louca.mean() < q["escuro"]:
                par = ndimage.binary_dilation(BS.quieto(FA.paredes_pdf, Q)[Y0:Y1, X0:X1] > 0.5, iterations=3)
                beira = caixa_m.astype(bool) & ~corpo & par & (lum > louca.mean() + q["claro_louca"])
                if beira.any():
                    # refeito pelo que está em volta (a beira escura da louça e a parede), sem o miolo claro da louça
                    out[Y0:Y1, X0:X1] = cv2.inpaint(np.ascontiguousarray(jan), beira.astype(np.uint8), 2,
                                                    cv2.INPAINT_TELEA)
                    total += int(beira.sum())
                    print(f"    vaso {nome}: {int(beira.sum())} px claros na beira junto à parede no tom da louça")
                # e a mancha clara pequena no miolo da louça (o ponto cinza junto à parede do vaso do lavabo): o que
                # é mais claro que a louça, não encosta na caixa (o piso em volta da bacia) e é pequeno
                jan = np.ascontiguousarray(out[Y0:Y1, X0:X1])
                lum = jan.astype(np.int16).mean(axis=2)
                claro = (caixa_m.astype(bool) & (lum > louca.mean() + q["claro_louca"])).astype(np.uint8)
                n, lab, st, _ = cv2.connectedComponentsWithStats(claro, 8)
                cx0, cy0 = int(np.floor(x0)) - X0, int(np.floor(y0)) - Y0
                cx1, cy1 = int(np.ceil(x1)) - X0, int(np.ceil(y1)) - Y0
                miolo = np.zeros_like(claro)
                for i in range(1, n):
                    bx, by, bw, bh, area = st[i]
                    if area <= q["miolo_max_px"] and bx > cx0 and by > cy0 and bx + bw < cx1 and by + bh < cy1:
                        miolo[lab == i] = 1
                if miolo.any():
                    mm = cv2.dilate(miolo, np.ones((3, 3), np.uint8)) & caixa_m
                    out[Y0:Y1, X0:X1] = cv2.inpaint(jan, mm, 2, cv2.INPAINT_TELEA)
                    total += int(miolo.sum())
                    print(f"    vaso {nome}: {int(miolo.sum())} px de mancha clara no miolo da louça")
    print(f"    vasos: {total} px no total")
    return out


# o que o PDF desenha e não é parede (louças, mobiliário, equipamentos, bancadas, marcenaria, carros, escadas, pilares):
# fica fora da limpeza das paredes, com a folga de `folga_px` (a grelha da churrasqueira, as geladeiras e as folhas das
# portas encostam nas paredes e têm o cinza claro das linhas soltas)
OBJETOS = {"camadas": ("ARQ_LOUÇAS E METAIS", "ARQ_MOBILIÁRIO", "ARQ_ELEMENTOS FIXOS", "ARQ_BANCADAS",
                       "ARQ_MARCENARIA", "ARQ_LAYOUT HUMANIZAÇÃO", "ARQ_ESCADAS E RAMPAS", "EST - Pilar"),
           "folga_px": 2, "ss": 2}


def objetos_pdf(Q):
    q = OBJETOS
    ss = q["ss"]
    cam = set(q["camadas"])
    m = (Q.preencher(lambda d: d.get("layer") in cam, ss=ss) * 255).astype(np.uint8)
    tr = np.zeros((Q.H * ss, Q.W * ss), np.uint8)
    for d in Q.desenhos:
        if d.get("layer") in cam and d["type"] == "s":
            for c in Q.caminhos(d):
                cv2.polylines(tr, [np.int32(np.round(c * ss))], False, 255, max(1, round(0.8 * ss)))
    tr = cv2.resize(tr, (Q.W, Q.H), interpolation=cv2.INTER_AREA)
    if m.shape != tr.shape:
        m = cv2.resize(m, (Q.W, Q.H), interpolation=cv2.INTER_AREA)
    obj = (np.maximum(m, tr) > 40)
    return ndimage.binary_dilation(obj, iterations=q["folga_px"])


# Térreo, a claraboia do lavabo (usuário, 12/11: "Na claraboia não precisa do X, apenas os traços na horizontal"; "Falei
# para remover o x tracejado da claraboia mantendo apenas o tracejado horizontal"): saem as diagonais e o X do meio;
# fica a linha tracejada horizontal. Na camada dos tracejados finos do 12K (`..._12K_tracejados.png`), na caixa da
# claraboia, fica só a linha horizontal (as linhas com traço em ao menos `linha_min` da largura da caixa); o resto sai, com os resíduos junto às faces das paredes. Na final, o piso
# por baixo do que sai vem da entrada da IA do 12K (a final antes dos tracejados finos: fora dos traços, idêntica à
# final), só no piso (fora das faces das paredes, abaixo de `face_y`).
CLARABOIA = {"Terreo": {"caixa_px": (2252, 349, 2348, 401), "piso_x": (2257, 2341), "face_y": 357,
                        "linha_min": 0.25, "limiar": 20}}


def claraboia_sai(pav, q=None):
    """A máscara (px da final) do que sai da claraboia na camada dos tracejados finos, ou None se o pavimento não tem."""
    q = q or CLARABOIA
    if pav not in q:
        return None
    c = q[pav]
    tr = cv2.imread(str(FINAIS[pav].parent / f"POE642_CasaA_PH_{pav}_12K_tracejados.png"))[..., 0].astype(np.int16)
    x0, y0, x1, y1 = c["caixa_px"]
    a = tr[y0:y1, x0:x1]
    linha = (a > c["limiar"]).sum(axis=1) >= c["linha_min"] * (x1 - x0)
    # (a linha horizontal é de 2 px sem franja: o que encosta nela por cima ou por baixo é a ponta das diagonais)
    fica = np.zeros(a.shape, bool)
    fica[linha] = a[linha] > 0
    sai = np.zeros(tr.shape, bool)
    sai[y0:y1, x0:x1] = (a > 0) & ~fica
    return sai


def claraboia(pav, img, q=None):
    q = q or CLARABOIA
    sai = claraboia_sai(pav, q)
    if sai is None:
        return img
    c = q[pav]
    import ampliacao_12k_terreo_casaa as Z
    dados = __import__("json").loads(Z.DADOS.read_text())["recortes"]
    ent = cv2.imread(str(Z.ENTRADA_IA))
    X0, Yia = dados["X0"], dados["Yia"]
    x0, y0, x1, y1 = c["caixa_px"]
    piso = np.zeros(sai.shape, bool)
    piso[y0:y1, x0:x1] = True
    face = np.zeros(sai.shape, bool)
    face[c["face_y"]:y1, x0:c["piso_x"][0]] = True
    face[c["face_y"]:y1, c["piso_x"][1]:x1] = True
    zona = ndimage.binary_dilation(sai, iterations=1) & piso & ~face
    E = np.zeros_like(img)
    E[Yia:Yia + ent.shape[0], X0:X0 + ent.shape[1]] = ent
    zona &= (img != E).any(axis=2)
    out = img.copy()
    out[zona] = E[zona]
    print(f"    claraboia: sem o X (diagonais e o X do meio), só o tracejado horizontal; {int(zona.sum())} px do piso "
          f"de volta; {int(sai.sum())} px fora da camada dos tracejados do 12K")
    return out


def aplicar(pav, antes):
    Q = quadro(pav)
    out = np.ascontiguousarray(antes.copy())
    out = shafts(pav, Q, out)
    protegido = ndimage.binary_dilation((out != antes).any(axis=2), iterations=2)
    # as folhas das portas e as esquadrias do PDF (o que a ARQ_PAREDE preenche e não tem o cinza das paredes) e os
    # objetos do PDF ficam
    q = PAREDES[pav]
    im = out.astype(np.int16)
    cinza = (np.abs(im - q["cor"]).max(axis=2) <= q["tol"]) & ((im.max(axis=2) - im.min(axis=2)) <= q["croma"])
    folhas = (BS.quieto(FA.paredes_pdf, Q) > 0.3) & ~cinza
    protegido |= ndimage.binary_dilation(folhas, iterations=1) | objetos_pdf(Q)
    out = BS.paredes_retas(Q, out, protegido, FA, q)
    out = vasos(pav, Q, out)
    out = claraboia(pav, out)
    return out


# ----------------------------------------------------------------------------------------------------------------------
# O 12K (A e B) de cada pavimento, sem gerar a IA de novo: a entrada da IA recebe só o que mudou na final (fora dos textos
# e dos tracejados que a entrada não tem); no Térreo, a saída corrigida da IA (no git) é remendada onde a entrada mudou;
# no 1º Pavimento, a saída da IA (job 09c2bb19) é corrigida de novo (`ampliacao_12k_1pav_casaa.py corrigir --entrada_antes
# <a entrada que a IA viu>`), já com a entrada nova. Os shafts são desenhados direto no 12K (`shafts_12k`, chamado pelo
# `montar12k`).
DOZE = {"Terreo": "POE642_CasaA_PH_Terreo_12K", "1Pavimento": "POE642_CasaA_PH_1Pavimento_12K",
        "limiar": 6, "folga_px": 2, "texto_folga_px": 2,
        # os vasos que a IA borrou no 12K (o do lavabo do Térreo: a borda esquerda em pinceladas e pontinhos claros
        # na face da parede): refeitos com a entrada (a final sem textos) ampliada, antes dos tracejados e dos textos
        "vasos_entrada": {"Terreo": ("lavabo",), "1Pavimento": ()},
        "vaso_folga_px": 3, "vaso_desvio": 40, "parede_faixa_px": 5, "parede_abaixo_px": 15,
        "vaso_pluma_px": 0.8, "vaso_nitidez": 0.5, "vaso_liso_px": 0.45, "vaso_corte": 0.35}


def entrada_nova(pav, antes_final, guardar_antes):
    """A entrada da IA do pavimento com o que mudou na final (antes_final -> final nova); guarda a de antes."""
    import json
    q = DOZE
    R = CASA / "renders"
    arq = R / f"{q[pav]}_entrada_ia.png"
    rc = json.loads((R / f"{q[pav]}_dados.json").read_text())["recortes"]
    X0, Wc, Yia, Hia = rc["X0"], rc["Wc"], rc["Yia"], rc["Hia"]
    ent = cv2.imread(str(arq))
    cv2.imwrite(str(guardar_antes), ent)
    a = antes_final[Yia:Yia + Hia, X0:X0 + Wc]
    b = cv2.imread(str(FINAIS[pav]))[Yia:Yia + Hia, X0:X0 + Wc]
    mudou = (a != b).any(axis=2)
    texto = ndimage.binary_dilation((np.abs(ent.astype(np.int16) - a.astype(np.int16)).max(axis=2) > 3),
                                    iterations=q["texto_folga_px"])
    sel = mudou & ~texto
    ent[sel] = b[sel]
    cv2.imwrite(str(arq), ent)
    print(f"    [{pav}] entrada da IA: {int(sel.sum())} px da final nova ({int((mudou & texto).sum())} junto aos textos "
          f"e tracejados ficam)")
    return arq


def remendar_ia(pav, saida_ia, destino, entrada_antes):
    """A saída corrigida da IA com o que mudou na entrada (contra `entrada_antes`) vindo da entrada nova, ampliada."""
    import ampliacao_12k_terreo_casaa as Z
    q = DOZE
    R = CASA / "renders"
    ent = cv2.imread(str(R / f"{q[pav]}_entrada_ia.png"))
    ent0 = cv2.imread(str(entrada_antes))
    ia = cv2.imread(str(saida_ia))
    Hi, Wi = ia.shape[:2]
    Hc, Wc = ent.shape[:2]
    M = Z._alinhar(ia, ent)
    Tm = (np.diag([Wi / Wc, Hi / Hc, 1.0]) @ np.vstack([M.astype(np.float64), [0, 0, 1]]))[:2]
    ref = cv2.warpAffine(ent, Tm, (Wi, Hi), flags=cv2.INTER_LANCZOS4, borderValue=(255, 255, 255)).astype(np.float32)
    f_, r_ = Z.CORRECAO["nitidez"]
    ref = np.clip(ref + f_ * (ref - cv2.GaussianBlur(ref, (0, 0), r_)), 0, 255)
    d = (np.abs(ent.astype(np.int16) - ent0.astype(np.int16)).max(axis=2) > q["limiar"]).astype(np.uint8)
    k = 2 * q["folga_px"] + 1
    d = cv2.dilate(d, np.ones((k, k), np.uint8)).astype(np.float32)
    m = cv2.warpAffine(d, Tm, (Wi, Hi), flags=cv2.INTER_LINEAR)
    m = cv2.GaussianBlur(m, (0, 0), Z.CORRECAO["borda_px"] * Wi / Wc / 2.7)[..., None]
    out = np.clip(np.round(ia * (1 - m) + ref * m), 0, 255).astype(np.uint8)
    cv2.imwrite(str(destino), out)
    print(f"    [{pav}] a saída da IA remendada em {int(d.sum())} px da entrada: {destino}")


ANTES_DEPOIS = {"Terreo": {"shaft_elevador": (2200, 1080, 2420, 1300), "lavabo": (2240, 300, 2420, 500)},
                "1Pavimento": {"shaft_cima": (2230, 330, 2380, 430), "shaft_elevador": (2300, 1090, 2420, 1230),
                               "shafts_master": (1630, 1410, 1770, 1480)}}


def antes_depois(pav, antes, depois, extra=None):
    feitos = []
    zonas = dict(ANTES_DEPOIS[pav], **(extra or {}))
    for nome, (x0, y0, x1, y1) in zonas.items():
        a, b = antes[y0:y1, x0:x1], depois[y0:y1, x0:x1]
        k = max(1, int(round(700 / max(x1 - x0, y1 - y0))))
        a = cv2.resize(a, None, fx=k, fy=k, interpolation=cv2.INTER_CUBIC)
        b = cv2.resize(b, None, fx=k, fy=k, interpolation=cv2.INTER_CUBIC)
        junto = np.hstack([a, np.full((a.shape[0], 16, 3), 255, np.uint8), b])
        arq = CASA / "renders" / f"POE642_CasaA_PH_{pav}_1211_{nome}_antes_depois.jpg"
        cv2.imwrite(str(arq), junto, [cv2.IMWRITE_JPEG_QUALITY, 92])
        feitos.append(arq)
        print(f"    {arq.name}")
    return feitos


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pav", choices=("Terreo", "1Pavimento"))
    ap.add_argument("--antes", type=Path)
    ap.add_argument("--saida", type=Path)
    ap.add_argument("--entrada12k", type=Path, default=None,
                    help="depois da final: a entrada da IA do 12K com o que mudou; a de antes vai para este arquivo")
    ap.add_argument("--remendar", nargs=3, type=Path, default=None, metavar=("SAIDA_IA", "DESTINO", "ENTRADA_ANTES"),
                    help="a saída corrigida da IA remendada onde a entrada mudou (Térreo)")
    a = ap.parse_args()
    if a.remendar:
        remendar_ia(a.pav, *a.remendar)
        return
    final = FINAIS[a.pav]
    if a.antes:
        antes = cv2.imread(str(a.antes))
    else:
        dado = subprocess.run(["git", "show", f"{ANTES_COMMIT}:{final.relative_to(RAIZ_GIT).as_posix()}"],
                              cwd=RAIZ_GIT, capture_output=True, check=True).stdout
        antes = cv2.imdecode(np.frombuffer(dado, np.uint8), cv2.IMREAD_COLOR)
    print(f"[{a.pav}]")
    out = aplicar(a.pav, antes)
    saida = a.saida or final
    cv2.imwrite(str(saida), out)
    print(f"    {saida}; {int((out != antes).any(axis=2).sum())} px mudaram")
    if not a.saida:
        antes_depois(a.pav, antes, out)
    if a.entrada12k:
        entrada_nova(a.pav, antes, a.entrada12k)


if __name__ == "__main__":
    main()

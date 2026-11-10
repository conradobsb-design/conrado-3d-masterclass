r"""Casa A, Térreo: as correções de 10/11/26 (a lista do cliente, com os recortes da planta, e as respostas do usuário).

Um passo por pedido, sobre a final do Térreo de antes (a do commit 58ea098, a mesma de 0a17741), na ordem de `PASSOS`:

1. `tracejados_ta`: saem todos os tracejados (cliente: "Remover as linhas tracejadas. Fica uma representação mais técnica
   e pode confundir quem olha a planta. Deixar apenas as que representam 'vazios'"; "Não representar as linhas
   tracejadas do telhado"): os afastamentos, os dois contornos da laje da cobertura, a grade do pergolado e os X; os dos
   vazios e o pergolado voltam no fim, finos e claros (`tracejados_finos_ta`).
2. `gramado_ta`: o gramado do lote na grama do Subsolo (usuário: "USE O MESMO TOM DE GRAMA DO SUBSOLO"), sem as árvores
   (cliente: "No terreno não precisa representar muitas árvores ... Representar arbustos que são menores"; usuário:
   "Arbustos e 4 árvores"): 4 árvores pequenas nos cantos e arbustos baixos junto aos muros; o jardim de 4,79 m² com as
   plantas em tamanhos diferentes (cliente: "Deixar melhor representada as plantas, pode diferenciar os tamanhos").
3. `piscina_ta`: a piscina, a prainha e o spa no tom da foto do cliente (cliente: "Deixar o tom de azul para a piscina
   mais sóbrio"; usuário: "USAR COMO REFERENCIA O TOM DA PISCINA E PRAINHA DA IMAGEM 3. E O REVESTIMENTO BARLAVENTO
   PORTOBELO"), com o desenho do Barlavento.
4. `bege_ta`: o Bege Bahia menos manchado, como no Subsolo (usuário: "Isso vai se repetir para todas as plantas da
   casa, de todas as casas daqui para frente"): as manchas a 45% do contraste; a luz, as sombras e o tom iguais.
5. `piso_marrom_ta`: o granito do piso no marrom da amostra do cliente ("mais uniforme ... e mais sóbrio"; "deixar a
   tonalidade do piso mais claro").
6. `bancadas_ta`: a ilha e a bancada da pia da cozinha e a bancada dos tanques em Dekton Danae; o lavatório (bancada e
   cuba) em marrom tabaco, a cuba mais escura; a churrasqueira na bancada da área gourmet; no lavabo, a pedra lateral
   na cor da cuba.
7. `banquetas_ta`: 5 banquetas na ilha da área gourmet, num tom mais destacado do piso.
8. `pilar_ta`: o pilar do canto do terraço gourmet no desenho do PDF.
9. `soleiras_ta`: a soleira na entrada (como a da Casa C); sem a soleira entre a sala e o escritório.
10. `entrada_ta`: a seta antiga sai; o triângulo no centro da abertura da porta.
11. `escadas_ta`: o triângulo e a descrição em todas as escadas; a caracol com os degraus em linhas, o tracejado só nos
    degraus de cima, sem a linha de corte; o guarda-corpo da escada do jardim.
12. `shaft_ta`: sem o nome SHAFT.
13. `tracejados_finos_ta`: os X dos vazios (varanda e sala de estar, área de serviço descoberta, claraboia, shaft) e o
    pergolado, finos e claros.

Uso (de POE642_CasaA/scripts/):
  python3 terreo_casaa_1011.py --antes <a final do Térreo do commit 58ea098> [--ate <passo>] [--saida <png>]
"""
import argparse
import contextlib
import io
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
RAIZ = FA.A.RAIZ


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


def nconv(a, m, sig):
    m = m.astype(np.float32)
    num = cv2.GaussianBlur(a * (m[..., None] if a.ndim == 3 else m), (0, 0), sig)
    den = cv2.GaussianBlur(m, (0, 0), sig)
    if a.ndim == 3:
        den = den[..., None]
    return num / np.maximum(den, 1e-4)


def variantes(a):
    return [a, a[:, ::-1].copy(), a[::-1].copy(), a[::-1, ::-1].copy(), np.ascontiguousarray(a.transpose(1, 0, 2)),
            np.ascontiguousarray(a.transpose(1, 0, 2)[::-1])]


def tecido(fontes_, h, w, p, sobra, semente):
    sys.path.insert(0, str(RAIZ / "_texturas"))
    import texturas
    return texturas.quilting(fontes_, h, w, p=p, sobra=sobra, rng=np.random.default_rng(semente))[:h, :w]


def ret_q(Q, r):
    """O retângulo r (pt) em px do quadro: (x0, y0, x1, y1)."""
    (a, b), (c, d) = Q.p2q(r[0], r[1]), Q.p2q(r[2], r[3])
    return min(a, c), min(b, d), max(a, c), max(b, d)


def preencher_pdf(Q, filtro, ss=2):
    return Q.preencher(filtro, ss=ss) > 0.05


def rotulos_na_imagem(Q, img, dentro=None, nota_min=0.6, busca=250):
    """[(r, alfa, claro, nota)] dos rótulos do PDF achados na imagem pela forma (`pedidos_terreo_casaa_2910.
    _achar_rotulo`, nas duas polaridades: o texto escuro e o claro), cada um na de melhor nota (a correlação do alfa
    com o texto da imagem no lugar achado); com `dentro` (bool), só os de centro dentro dela."""
    import revisao_casaa_2910 as R
    import pedidos_terreo_casaa_2910 as P
    rot, aj = R._rotulos_pav(Q)
    q = dict(P.ROTULOS_OUTROS_TA, minimo_forma=0.0)
    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
    achados = []
    for r in rot:
        melhor = None
        for claro in (False, True):
            src = (255 - img) if claro else img
            with contextlib.redirect_stdout(io.StringIO()):
                al, _ = P._achar_rotulo(Q, src, r, aj, q, busca=busca)
            if al.max() < 0.3:
                continue
            x0, y0, x1, y1 = R._caixa(al)
            g = cinza[y0:y1, x0:x1] if claro else 255 - cinza[y0:y1, x0:x1]
            a = al[y0:y1, x0:x1]
            nota = float(np.corrcoef(a.ravel(), g.ravel())[0, 1]) if a.std() > 0 and g.std() > 0 else 0.0
            if melhor is None or nota > melhor[3]:
                melhor = (r, al, claro, nota)
        if melhor is None or melhor[3] < nota_min:
            continue
        if dentro is not None:
            ys, xs = np.nonzero(melhor[1] > 0.3)
            if not dentro[int(ys.mean()), int(xs.mean())]:
                continue
        achados.append(melhor)
    return achados


def compor(out, al, cor):
    return out * (1 - al[..., None]) + np.float32(cor) * al[..., None]


ROTULO_ESCURO, ROTULO_CLARO = (20, 20, 20), (250, 250, 250)


def cor_rotulo(img, al, lum=125):
    """A cor do rótulo pelo fundo (a regra dos rótulos: branco no fundo escuro)."""
    x0, y0, x1, y1 = np.nonzero(al.any(axis=0))[0].min(), np.nonzero(al.any(axis=1))[0].min(), \
        np.nonzero(al.any(axis=0))[0].max(), np.nonzero(al.any(axis=1))[0].max()
    reg = img[y0:y1 + 1, x0:x1 + 1].astype(np.float32).mean(axis=2)
    fundo = np.median(reg[al[y0:y1 + 1, x0:x1 + 1] < 0.03])
    return ROTULO_CLARO if fundo < lum else ROTULO_ESCURO


def alfa_texto(linhas, x, y_meio, alinhar="esquerda", corpo=None, entrelinha=None, forma=(2160, 3840)):
    """O alfa de um texto de uma ou mais linhas na fonte das letras das escadas (`final3840_casaa.ESCADA_A`), com o meio
    do bloco em y_meio; x é a borda de `alinhar` ("esquerda", "direita" ou "centro")."""
    from PIL import Image, ImageDraw, ImageFont
    from rodape_entrega import FONTES
    e = FA.ESCADA_A
    corpo = corpo or e["corpo_px"]
    entrelinha = entrelinha or round(corpo * 1.18)
    S = 4
    fonte = ImageFont.truetype(str(FONTES / e["fonte"]), corpo * S)
    H, W = forma
    t = Image.new("L", (W * S, H * S), 0)
    d = ImageDraw.Draw(t)
    n = len(linhas)
    for i, ln in enumerate(linhas):
        yb = y_meio + (i - (n - 1) / 2) * entrelinha
        anc = {"esquerda": "lm", "direita": "rm", "centro": "mm"}[alinhar]
        d.text((x * S, yb * S), ln, font=fonte, fill=255, anchor=anc)
    return np.asarray(t.resize((W, H), Image.LANCZOS), np.float32) / 255


def triangulo(out, pts, cor=(30, 30, 30), ss=8):
    """O triângulo cheio (a seta das escadas), antisserrilhado."""
    pts = np.float32(pts)
    bx0, by0 = np.floor(pts.min(axis=0)).astype(int) - 2
    bx1, by1 = np.ceil(pts.max(axis=0)).astype(int) + 3
    m = np.zeros(((by1 - by0) * ss, (bx1 - bx0) * ss), np.uint8)
    cv2.fillPoly(m, [np.int32(np.round((pts - [bx0, by0]) * ss))], 255, cv2.LINE_AA)
    a = cv2.resize(m.astype(np.float32) / 255, (bx1 - bx0, by1 - by0), interpolation=cv2.INTER_AREA)[..., None]
    reg = out[by0:by1, bx0:bx1].astype(np.float32)
    out[by0:by1, bx0:bx1] = reg * (1 - a) + np.float32(cor) * a
    return out


def seta_tri(cx, cy, direcao, comp=15.0, larg=17.0):
    """Os 3 vértices do triângulo com a ponta para `direcao` (dx, dy), centrado em (cx, cy)."""
    d = np.float32(direcao) / np.hypot(*direcao)
    n = np.float32([-d[1], d[0]])
    c = np.float32([cx, cy])
    return [c + d * comp / 2, c - d * comp / 2 + n * larg / 2, c - d * comp / 2 - n * larg / 2]


def tirar_letra(Q, out, texto, centro_q, desloc):
    """A letra antiga (`final3840_casaa_terreo.letra`, centrada em centro_q) sai: os px dela e 2 em volta recebem os do
    mesmo lugar deslocados de `desloc` (dx, dy), no mesmo degrau."""
    vazio = np.zeros(out.shape, np.uint8)
    a = T.letra(Q, vazio.copy() + 0, texto, centro_q=centro_q).astype(np.float32)
    # a letra foi escrita em cinza 45 sobre o preto: o alfa é o que subiu
    al = a.max(axis=2) > 0
    m = dilatar(al, 2)
    ys, xs = np.nonzero(m)
    dx, dy = desloc
    out[ys, xs] = out[ys + dy, xs + dx]
    return out


def danae(h, w, semente, q=None):
    """O Dekton Danae: bege-areia claro e fosco, de grão fino e manchas suaves (a cor da descrição do fabricante; a
    foto não pôde ser baixada)."""
    q = q or DANAE
    rng = np.random.default_rng(semente)
    f = np.ones((h, w), np.float32)
    for amp, sig in q["camadas"]:
        n = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), sig)
        f += amp * n / max(float(n.std()), 1e-6)
    return np.float32(q["tom"]) * f[..., None]


DANAE = {"tom": (172, 189, 200), "camadas": [(0.030, 0.6), (0.022, 6.0)], "molhada": 0.93, "borda": 0.86}


# ----------------------------------------------------------------------------------------------------------------------
# 1. Os tracejados saem todos (pelo PDF, a reta inteira de cada um): os afastamentos, os dois contornos da laje da
# cobertura (o telhado), os lados da esquerda do terraço gourmet que o render desenhou em cinza (`laje_extra_px`), a
# grade do pergolado e os X e as molduras da DOC_LINHAS E PROJEÇÕES (menos os de dentro das paredes e os de `fora_px`:
# o X do elevador, coberto pela cabine, e o da faixa branca, que já saiu). Em cada reta, só os px do traço (neutros,
# escuros ou claros, que fogem do material de fora), com 1 px de antialias em volta, recebem o material a `banda_px` x
# 2 + 2 px dali, na direção normal à reta, do mesmo material da base chapada e fora de todas as faixas; ficam as
# paredes, os pilares, os rótulos e os móveis do PDF. Na grama e na água, nada: o gramado e a água são refeitos nos
# passos deles.
TRACEJADOS_TA = {"laje_px": {"h": (299, 335, 1177, 1213, 1637, 1672), "v": (2635, 2599, 1521, 1485)}, "tol_px": 3,
                 "laje_extra_px": [((1219, 1177), (1219, 1675))], "banda_px": 3, "pergolado_px": 8,
                 "pergolado_fontes_px": [(1290, 345, 1450, 470), (1100, 1180, 1185, 1560)], "pergolado_bege_px": (1400, 1100),
                 "pergolado_semente": 3105, "croma_obj": 10, "lum_obj": 140, "ponta_px": 5, "canto_px": 18, "canto_dif": 22, "claro_montante": 120, "preto_traco": 100,
                 "fora_px": [(2250, 1112, 2350, 1212), (2540, 880, 2770, 910)],
                 "neutro": 34, "escuro": 125, "claro": 205, "salto_lum": 14, "moveis_m2": 3.0}


def _retas_tracejadas(Q, q):
    """As retas dos tracejados, em px: [(p0, p1, h, cheia)]: h, a meia largura da faixa; `cheia`, a faixa inteira sai
    (as vigas do pergolado do render: a faixa clara entre os dois traços de cada viga)."""
    import pedidos_terreo_casaa_2910 as P
    par = FA.paredes_pdf(Q)
    h, hp = q["banda_px"], q["pergolado_px"]
    retas = []
    for a, o in P.TRACEJADOS_TA["afastamento"]:
        g = P._segs_doc(Q, a, o, "DOC_LINHAS E PROJEÇÕES")
        if g:
            x0, y0, x1, y1 = P._linha_inteira(g)
            retas.append((Q.p2q(x0, y0), Q.p2q(x1, y1), h, False))
    for (cam, a, off), ext, segs in T.cadeias_tracejadas(Q, ["ARQ_CONTRAPISO"], min_ext=40):
        if a not in (0.0, 90.0):
            continue
        p = [Q.p2q(x, y) for s in segs for x, y in ((s[0], s[1]), (s[2], s[3]))]
        pos = p[0][1] if a == 0.0 else p[0][0]
        if any(abs(pos - t) <= q["tol_px"] for t in q["laje_px"]["h" if a == 0.0 else "v"]):
            x0, y0, x1, y1 = P._linha_inteira(segs)
            retas.append((Q.p2q(x0, y0), Q.p2q(x1, y1), h, False))
    for _, _, segs in T.cadeias_tracejadas(Q, ["ARQ_PERGOLADO"]):
        x0, y0, x1, y1 = P._linha_inteira(segs)
        retas.append((Q.p2q(x0, y0), Q.p2q(x1, y1), hp, True))
    for _, _, segs in T.cadeias_tracejadas(Q, ["DOC_LINHAS E PROJEÇÕES"], min_n=2, min_ext=20):
        x0, y0, x1, y1 = P._linha_inteira(segs)
        (u0, v0), (u1, v1) = Q.p2q(x0, y0), Q.p2q(x1, y1)
        um, vm = (u0 + u1) / 2, (v0 + v1) / 2
        if not (0 <= um < Q.W and 0 <= vm < Q.H) or par[int(vm), int(um)] > 0.5:
            continue
        if any(a <= um <= c and b <= vm <= d for a, b, c, d in q["fora_px"]):
            continue
        retas.append(((u0, v0), (u1, v1), h, False))
    retas += [(tuple(map(float, a)), tuple(map(float, b)), h, False) for a, b in q["laje_extra_px"]]
    return retas


def agua_mascara(Q):
    """A água da piscina, da prainha e do spa: os retângulos do PDF (cobertura de 0 a 1)."""
    import piscinas_turquesa as PT
    a = np.zeros((Q.H, Q.W), np.float32)
    for r in PT.BORDAS["A-Terreo"]["agua"]:
        a = np.maximum(a, FA.ret_aa(Q, r))
    return a


def moveis_pdf(Q, q=None):
    """Os móveis e as peças do PDF (menos as peças grandes, os tapetes e os carros), com 1 px em volta."""
    import pedidos_terreo_casaa_2910 as P
    q = q or TRACEJADOS_TA
    grande = q["moveis_m2"] * 56.69 ** 2
    m = Q.preencher(lambda d: (d.get("layer") in P.ROTULOS_CENTRO_TA["obstaculos"] or str(d.get("layer", "")).startswith("EST"))
                    and d["rect"].width * d["rect"].height < grande, ss=2, fs=True) > 0.05
    return dilatar(m, 1)


def _orientacao(p0, p1):
    a = np.degrees(np.arctan2(p1[1] - p0[1], p1[0] - p0[0])) % 180
    return "h" if min(a, 180 - a) < 10 else ("v" if abs(a - 90) < 10 else f"d{round(a)}")


def apagar_retas(img, retas, fixo, moveis, mat, pular, q):
    """Os tracejados saem, por grupos de mesma direção (as horizontais, as verticais e cada diagonal), um grupo depois
    do outro (no cruzamento, o grupo seguinte já acha o material limpo). No piso, a faixa inteira de cada reta recebe o
    piso de logo ao lado, transladado na normal da reta (2h + 2 px, depois mais longe), do mesmo material e fora das
    faixas, do que fica (`fixo`: paredes e rótulos) e dos móveis; sobre os móveis e os carros (`moveis` e o claro sem
    cor), só os px do traço (neutros, escuros ou claros, que fogem da mediana em volta, com 1 px de antialias), por
    inpaint, sem trazer piso para dentro deles. Devolve a imagem e o número de px trocados."""
    out = img.copy()
    H, W = img.shape[:2]
    grupos = {}
    for r in retas:
        grupos.setdefault(_orientacao(r[0], r[1]), []).append(r)
    n_troca = 0
    for _, grupo in sorted(grupos.items()):
        # as retas um pouco mais longas nas pontas (o traço do canto passa do último ponto do PDF)
        ext = q["ponta_px"]
        grupo = [((p0[0] - (p1[0] - p0[0]) / max(np.hypot(p1[0] - p0[0], p1[1] - p0[1]), 1e-6) * ext,
                   p0[1] - (p1[1] - p0[1]) / max(np.hypot(p1[0] - p0[0], p1[1] - p0[1]), 1e-6) * ext),
                  (p1[0] + (p1[0] - p0[0]) / max(np.hypot(p1[0] - p0[0], p1[1] - p0[1]), 1e-6) * ext,
                   p1[1] + (p1[1] - p0[1]) / max(np.hypot(p1[0] - p0[0], p1[1] - p0[1]), 1e-6) * ext), h, c)
                 for p0, p1, h, c in grupo]
        o = out.astype(np.float32)
        lum = o.mean(axis=2)
        croma = o.max(axis=2) - o.min(axis=2)
        mo = cv2.medianBlur(out, 11).astype(np.float32)
        med, croma_med = mo.mean(axis=2), mo.max(axis=2) - mo.min(axis=2)
        obj = moveis | ((croma_med < q["croma_obj"]) & (med > q["lum_obj"]))
        Tg = np.zeros((H, W), bool)
        Ti = np.zeros((H, W), bool)
        faixas = []
        for p0, p1, h, _ in grupo:
            mb = np.zeros((H, W), np.uint8)
            cv2.line(mb, tuple(int(round(c)) for c in p0), tuple(int(round(c)) for c in p1), 1, 2 * h + 1)
            mb = mb.astype(bool) & ~fixo & ~pular
            traco = dilatar((croma < q["neutro"]) & ((lum < q["escuro"]) | (lum > q["claro"])) &
                            (np.abs(lum - med) > q["salto_lum"]), 1) & mb
            Ti |= traco & obj
            t = mb & ~obj
            Tg |= t
            faixas.append((p0, p1, h, t))
        Tall = Tg | Ti
        feito = np.zeros((H, W), bool)
        for p0, p1, h, t in faixas:
            ys, xs = np.nonzero(t & ~feito)
            if not len(ys):
                continue
            dx, dy = p1[0] - p0[0], p1[1] - p0[1]
            L = max(np.hypot(dx, dy), 1e-6)
            nx, ny = -dy / L, dx / L
            sg = np.where((xs - p0[0]) * nx + (ys - p0[1]) * ny >= 0, 1.0, -1.0)
            sy, sx = np.full(len(ys), -1), np.full(len(ys), -1)
            pend = np.ones(len(ys), bool)
            for k in (2 * h + 2, 2 * h + 4, 3 * h + 4, 4 * h + 5, 5 * h + 8):
                for lado in (1.0, -1.0):
                    cy = np.round(ys + ny * sg * lado * k).astype(int)
                    cx = np.round(xs + nx * sg * lado * k).astype(int)
                    dentro = (cy >= 0) & (cy < H) & (cx >= 0) & (cx < W)
                    cy_, cx_ = np.clip(cy, 0, H - 1), np.clip(cx, 0, W - 1)
                    ok = pend & dentro & ~Tall[cy_, cx_] & ~fixo[cy_, cx_] & ~pular[cy_, cx_] & ~obj[cy_, cx_] & \
                        (mat[cy_, cx_] == mat[ys, xs])
                    sy[ok], sx[ok] = cy[ok], cx[ok]
                    pend &= ~ok
                if not pend.any():
                    break
            v = ~pend
            out[ys[v], xs[v]] = out[sy[v], sx[v]]
            feito[ys[v], xs[v]] = True
            n_troca += int(v.sum())
        resto = (Tg & ~feito) | Ti
        if resto.any():
            out = cv2.inpaint(out, (resto * 255).astype(np.uint8), 3, cv2.INPAINT_TELEA)
            n_troca += int(resto.sum())
    return out, n_troca


def pergolado_ta(Q, img, fixo, pular, q):
    """A grade do pergolado do render (as vigas: a faixa clara entre os dois traços de cada uma) sai com o piso refeito
    (`pedidos_terreo_casaa_2910.piso_refeito`: o Bege Bahia tecido das `fontes_px`, emendado ao piso de fora pela
    membrana), no retângulo da grade, só no Bege Bahia (fora da água, das paredes e dos rótulos)."""
    import pedidos_terreo_casaa_2910 as P
    pts = np.array([Q.p2q(x, y) for _, _, segs in T.cadeias_tracejadas(Q, ["ARQ_PERGOLADO"])
                    for s in segs for x, y in ((s[0], s[1]), (s[2], s[3]))])
    x0, y0 = np.floor(pts.min(axis=0)).astype(int) - q["pergolado_px"]
    x1, y1 = np.ceil(pts.max(axis=0)).astype(int) + q["pergolado_px"]
    mat = materiais(Q)
    zona = np.zeros(img.shape[:2], bool)
    zona[y0:y1, x0:x1] = True
    rotulo_bege = mat[q["pergolado_bege_px"][1], q["pergolado_bege_px"][0]]
    zona &= (mat == rotulo_bege) & ~fixo & ~pular
    out = P.piso_refeito(img, zona, q["pergolado_semente"], dict(P.PISO_TA, fontes_px=q["pergolado_fontes_px"],
                                                                  tom_tol=40))
    return out, int(zona.sum())


def tracejados_ta(Q, img, q=None):
    q = q or TRACEJADOS_TA
    # as do pergolado também passam pela limpeza fina, depois do piso refeito (o traço que sobra fora do Bege Bahia)
    retas = [(r[0], r[1], q["banda_px"], False) for r in _retas_tracejadas(Q, q)]
    par = FA.paredes_pdf(Q) > 0.05
    rots = rotulos_na_imagem(Q, img)
    rot = np.zeros(img.shape[:2], np.float32)
    for _, al, _, _ in rots:
        rot = np.maximum(rot, al)
    fixo = dilatar(par, 1) | dilatar(rot > 0.02, 1)
    pular = gramado_mascara(Q, img) | (agua_mascara(Q) > 0)
    out, n_p = pergolado_ta(Q, img, fixo, pular, q)
    moveis = moveis_pdf(Q, q)
    out, n = apagar_retas(out, retas, fixo, moveis, materiais(Q), pular, q)
    # as pontas dos X (o traço do render engrossava no canto, em ponta de seta): no disco de `canto_px` em volta de
    # cada ponta das diagonais, o que é bem mais escuro que o piso em volta sai por inpaint
    o = out.astype(np.float32)
    lum = o.mean(axis=2)
    med = cv2.medianBlur(out, 15).astype(np.float32).mean(axis=2)
    cantos = np.zeros(lum.shape, np.uint8)
    for p0, p1, _, _ in retas:
        if _orientacao(p0, p1).startswith("d"):
            for c in (p0, p1):
                cv2.circle(cantos, (int(round(c[0])), int(round(c[1]))), q["canto_px"], 1, -1)
    livre = cantos.astype(bool) & ~fixo & ~pular & ~moveis
    sujo = livre & (lum < med - q["canto_dif"])
    sujo = dilatar(sujo, 1) & livre
    # e o pedaço do traço sobre os montantes cinza do PDF (claros: não é parede preta), fora dos rótulos
    sobre = (cantos.astype(bool) & dilatar(par, 1) & ~dilatar(rot > 0.02, 2) & (med > q["claro_montante"])
             & (lum < q["preto_traco"]))
    sujo |= sobre
    if sujo.any():
        out = cv2.inpaint(out, (sujo * 255).astype(np.uint8), 3, cv2.INPAINT_TELEA)
    print(f"    tracejados: {len(retas)} retas (afastamentos, laje da cobertura, X e molduras), {n} px trocados pelo "
          f"piso de perto (sobre os móveis e os carros, só o traço); a grade do pergolado com o piso refeito "
          f"({n_p} px); na grama e na água, nos passos deles")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 2. O gramado: a grama do Subsolo (`texturas.textura("grama_padrao")`, na escala real, na cor dela) no gramado inteiro
# do lote (o branco da base chapada dentro dos muros que a final mostra verde: grama, árvores e sombras; os furos
# pequenos, flores e touceiras, também), sem as árvores e as touceiras do render. Por cima: as 4 árvores pequenas nos
# cantos do lote (`arvores`: a planta da biblioteca, o diâmetro da copa em m) e os arbustos baixos (`arbusto_m`) junto
# aos muros, espaçados (`passo_m`, a `recuo_m` do muro), cada um só onde a copa cabe inteira no gramado; a sombra da
# biblioteca (para baixo e à esquerda). No jardim de 4,79 m², as 3 plantas em tamanhos diferentes (`jardim_479`). O
# jardim interno da escada (17,46 m², o verde da base) recebe o tom da grama nova, só nos px de grama. Os rótulos sobre o
# gramado (o JARDIM de 4,79 m²) saem e voltam em branco.
GRAMADO_TA = {"lote_px": (300, 186, 3398, 1912), "verde": -4, "verde_azul": 10, "faixa_px": 4, "fechar": 7, "buraco_max": 9000, "area_min": 3000,
              "semente": 7, "semente_plantas": 11, "suave": 0.7,
              "arvores": [("arvore_3", (420, 310), 2.6), ("arvore_1", (3280, 310), 2.8), ("arvore_2", (420, 1795), 2.6),
                          ("arvore_3", (3260, 1190), 2.4)],
              "arbustos": ("arbusto_1", "arbusto_2", "arbusto_3"), "arbusto_m": (0.85, 1.25), "passo_m": (4.8, 7.0),
              "recuo_m": 0.85, "longe_arvore_m": 3.6, "par": 0.35,
              "jardim_479": [("palmeira_1", (1510, 1684), 1.1), ("palmeira_3", (1662, 1686), 0.85),
                             ("arbusto_3", (1563, 1709), 0.5)],
              "jardim_interno": (80, 145, 110), "jardim_479_px": (1440, 1620, 1720, 1760)}


def gramado_mascara(Q, img, q=None):
    q = q or GRAMADO_TA
    x0, y0, x1, y1 = q["lote_px"]
    lote = np.zeros(img.shape[:2], bool)
    lote[y0:y1, x0:x1] = True
    # o branco da base com as linhas finas dela fechadas (os tracejados e os contornos que cruzam o gramado)
    branco = cv2.morphologyEx(np.all(Q.chapada == 255, axis=2).astype(np.uint8), cv2.MORPH_CLOSE,
                              np.ones((5, 5), np.uint8)).astype(bool) & lote
    I = img.astype(np.int16)
    verde = (I[..., 1] >= I[..., 2] + q["verde"]) & (I[..., 1] >= I[..., 0] + q["verde_azul"]) & branco
    k = q["fechar"]
    m = cv2.morphologyEx(verde.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((k, k), np.uint8)).astype(bool) & branco
    furo = ndimage.binary_fill_holes(m) & ~m & branco
    n, lab, st, _ = cv2.connectedComponentsWithStats(furo.astype(np.uint8), 8)
    m |= np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] <= q["buraco_max"]])
    n, lab, st, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8), 8)
    m = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= q["area_min"]])
    # as faixas dos tracejados tirados que caem no branco da base junto ao gramado (o traço na divisa com a pedra)
    fx = np.zeros(m.shape, np.uint8)
    for p0, p1, _, _ in _retas_tracejadas(Q, TRACEJADOS_TA):
        cv2.line(fx, tuple(int(round(c)) for c in p0), tuple(int(round(c)) for c in p1), 1, 2 * q["faixa_px"] + 1)
    return m | (fx.astype(bool) & branco & dilatar(m, 2 * q["faixa_px"]))


def _pousar(fundo, nome, cx, cy, d_m, px_m):
    """A planta da biblioteca com a copa de d_m metros."""
    import json
    sys.path.insert(0, str(RAIZ / "_texturas"))
    import texturas
    cfg = json.loads((RAIZ / "_texturas" / "texturas.json").read_text())
    d0 = 2 * cfg["vegetacao"]["plantas"][nome]["raio"] / cfg["referencia_planta"]["px_por_m"]
    texturas.pousar(fundo, nome, cx, cy, px_m * d_m / d0)


def _cabe(m_ok, cx, cy, r):
    H, W = m_ok.shape
    yy, xx = np.ogrid[max(0, int(cy - r)):min(H, int(cy + r) + 1), max(0, int(cx - r)):min(W, int(cx + r) + 1)]
    disco = (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r
    sub = m_ok[max(0, int(cy - r)):min(H, int(cy + r) + 1), max(0, int(cx - r)):min(W, int(cx + r) + 1)]
    return disco.sum() > 0 and bool(sub[disco].all()) and int(cy - r) >= 0 and int(cx - r) >= 0


def gramado_ta(Q, img, q=None):
    sys.path.insert(0, str(RAIZ / "_texturas"))
    from texturas import textura
    q = q or GRAMADO_TA
    m = gramado_mascara(Q, img, q)
    rots = rotulos_na_imagem(Q, img, dentro=dilatar(m, 2))
    ys, xs = np.nonzero(m)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    G = textura("grama_padrao", Q.px_m, y1 - y0, x1 - x0, semente=q["semente"]).astype(np.float32)
    novo = img.astype(np.float32).copy()
    novo[y0:y1, x0:x1] = G
    out = T.F.pousar(img.astype(np.float32), novo, m, suave=q["suave"])
    # o jardim interno da escada: o tom da grama nova, só na grama (o verde)
    # (o trecho esmaecido da escada é um véu claro sobre a grama: o px sobe para a grama nova na fração de grama dele)
    tom_novo = np.median(G.reshape(-1, 3), axis=0)
    ji = T.F.fechar(np.all(Q.chapada == np.uint8(q["jardim_interno"]), axis=2), 5)
    I = img.astype(np.float32)
    pedra = I[..., 2] > I[..., 1] + 2
    verde_ji = ji & ~pedra & (I[..., 1] - I[..., 2] > 9)
    g_velho = np.median(I[verde_ji], axis=0)
    claro = ji & ~pedra & (I.mean(axis=2) > np.percentile(I[ji & ~pedra].mean(axis=1), 90))
    veu = np.median(I[claro], axis=0)
    d = veu - g_velho
    t = np.clip(((I - g_velho) * d).sum(axis=2) / max(float((d * d).sum()), 1e-3), 0, 1)
    w = (ji & ~pedra).astype(np.float32) * (1 - t)
    out = np.where((ji & ~pedra)[..., None], out + (tom_novo - g_velho) * w[..., None], out)
    # as plantas: as 4 árvores dos cantos e os arbustos junto aos muros
    ok = cv2.erode(m.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    rng = np.random.default_rng(q["semente_plantas"])
    px = Q.px_m
    arvores = []
    for nome, (cx, cy), d in q["arvores"]:
        r = d / 2 * px * 0.8
        for passo in range(0, 120, 10):                      # se não couber, anda para dentro do lote
            ux = cx + (passo if cx < Q.W / 2 else -passo)
            uy = cy + (passo if cy < Q.H / 2 else -passo)
            if _cabe(ok, ux, uy, r):
                _pousar(out, nome, ux, uy, d, px)
                arvores.append((ux, uy))
                break
    lx0, ly0, lx1, ly1 = q["lote_px"]
    rec = q["recuo_m"] * px
    muros = [((lx0, ly0 + rec), (lx1, ly0 + rec)), ((lx0, ly1 - rec), (lx1, ly1 - rec)),
             ((lx0 + rec, ly0), (lx0 + rec, ly1)), ((lx1 - rec, ly0), (lx1 - rec, ly1))]
    n_arb = 0
    for (ax, ay), (bx, by) in muros:
        L = np.hypot(bx - ax, by - ay)
        t = rng.uniform(1.5, 3.0) * px
        while t < L:
            cx, cy = ax + (bx - ax) * t / L, ay + (by - ay) * t / L
            d = rng.uniform(*q["arbusto_m"])
            if all(np.hypot(cx - u, cy - v) > q["longe_arvore_m"] * px for u, v in arvores) and \
                    _cabe(ok, cx, cy, d / 2 * px):
                _pousar(out, q["arbustos"][rng.integers(len(q["arbustos"]))], cx, cy, d, px)
                n_arb += 1
                if rng.random() < q["par"]:                  # às vezes, um segundo, menor, ao lado
                    e = d * 0.85 * px
                    cx2, cy2 = cx + (bx - ax) / L * e, cy + (by - ay) / L * e
                    d2 = d * rng.uniform(0.7, 0.85)
                    if _cabe(ok, cx2, cy2, d2 / 2 * px):
                        _pousar(out, q["arbustos"][rng.integers(len(q["arbustos"]))], cx2, cy2, d2, px)
                        n_arb += 1
            t += rng.uniform(*q["passo_m"]) * px
    # no jardim de 4,79 m², as plantas só dentro dele (sem passar sobre as paredes)
    dentro = cv2.erode((m | ji).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(np.float32)
    tmp = out.copy()
    for nome, (cx, cy), d in q["jardim_479"]:
        _pousar(tmp, nome, cx, cy, d, px)
    a = cv2.GaussianBlur(dentro, (0, 0), 0.6)[..., None]
    x0j, y0j, x1j, y1j = q["jardim_479_px"]
    out[y0j:y1j, x0j:x1j] = (tmp * a + out * (1 - a))[y0j:y1j, x0j:x1j]
    for _, al, _, _ in rots:
        out = compor(out, al, ROTULO_CLARO)
    print(f"    gramado: a grama do Subsolo em {m.sum() / px ** 2:.0f} m² do lote, sem as árvores do render; "
          f"{len(arvores)} árvores pequenas nos cantos e {n_arb} arbustos junto aos muros; o jardim de 4,79 m² com "
          f"{len(q['jardim_479'])} plantas de tamanhos diferentes; o jardim da escada no tom da grama nova; rótulos de "
          f"volta: {', '.join(r[0] for r, _, _, _ in rots)}")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
# 3. A água: a piscina e o spa no tom da água da foto do cliente (BGR ~118, 117, 106: o cinza-esverdeado escuro, sem os
# brilhos) e a prainha (abaixo do degrau do PDF, `prainha_y_pt`) no cinza claro da parte rasa da foto (~141, 145, 146).
# O desenho do Barlavento fica: a luz relativa de cada px da água antiga (as pastilhas, o rejunte, os degraus, a sombra
# das bordas e a rede das cáusticas) passa ao tom novo com o contraste de `ganho`; os traços escuros sobre a água (o
# pergolado; ele volta no fim, fino e claro) e os rótulos saem (a luz deles é a da água de perto); os rótulos voltam no
# mesmo desenho, em branco na água escura e em preto na prainha. A água fica nos retângulos do PDF, com a cobertura
# exata da borda.
PISCINA_TA = {"tom": (118, 117, 106), "tom_prainha": (141, 145, 146), "prainha_y_pt": 1049.5, "ganho": 0.85,
              "base": (0.55, 1.55), "traco_rel": -0.22, "ref_sig": 25.0}


def piscina_ta(Q, img, q=None):
    import piscinas_turquesa as PT
    q = q or PISCINA_TA
    cob = agua_mascara(Q)
    agua = cob > 0
    rots = rotulos_na_imagem(Q, img, dentro=agua)
    texto = np.zeros(agua.shape, np.float32)
    for _, al, _, _ in rots:
        texto = np.maximum(texto, al)
    im = img.astype(np.float32)
    Y = im.mean(axis=2)
    ok = agua & (cob > 0.99) & (texto < 0.02)
    ref = nconv(Y, ok, q["ref_sig"])
    rel = Y / np.maximum(ref, 1) - 1
    traco = dilatar((rel < q["traco_rel"]) & agua, 1) | dilatar(texto > 0.02, 1)
    # nos traços, a luz relativa da água de perto
    limpo = ok & ~traco
    rel_l = nconv(rel, limpo, 2.0)
    rel = np.where(traco, rel_l, rel)
    base = np.clip(1 + q["ganho"] * rel, *q["base"])
    yp = Q.p2q(0, q["prainha_y_pt"])[1]
    xs0, _, xs1, _ = ret_q(Q, PT.BORDAS["A-Terreo"]["agua"][0])
    prainha = np.zeros(agua.shape, bool)
    prainha[int(round(yp)):, int(xs0):int(np.ceil(xs1))] = True
    prainha &= agua
    tom = np.where(prainha[..., None], np.float32(q["tom_prainha"]), np.float32(q["tom"]))
    novo = tom * base[..., None]
    out = im * (1 - cob[..., None]) + novo * cob[..., None]
    nomes = []
    for r, al, _, _ in rots:
        out = compor(out, al, cor_rotulo(out, al))
        nomes.append(r[0])
    print(f"    água: a piscina e o spa no tom da foto (BGR {q['tom']}) e a prainha no cinza claro ({q['tom_prainha']}), "
          f"com o desenho do Barlavento; os traços sobre a água saem; rótulos de volta: {', '.join(nomes)}")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
# 3b. O Bege Bahia menos manchado (a regra do Subsolo da Casa A, 05/11: cliente, "Deixar a representação do Bege Bahia
# menos manchado (para melhor representação)"; usuário, 10/11: "Isso vai se repetir para todas as plantas ... tem que
# ser como regra"): nos pisos de Bege Bahia (o cinza 232 da base chapada: o hall externo, o deck da piscina e a pedra
# em volta dela, o pergolado, os pisantes, o lance do deck, a pedra junto ao terraço gourmet; e o banho do motorista),
# as manchas a `forca` do contraste, como no Subsolo (45%); a luz, as sombras, o tom e o degrau de cada pedra ficam.
# O tom do lugar é a mediana de `mediana_px` (com as peças tapadas antes: as espreguiçadeiras, os pilares, as plantas,
# os rótulos); o desenho é a imagem sobre esse tom, e é ele que cai para `forca`. Junto às arestas do tom (as bordas dos
# degraus e das sombras, `aresta`), fica o px de antes. Os rótulos voltam no mesmo desenho.
BEGE_TA = {"chapada": (232, 232, 232), "forca": 0.45, "mediana_px": 25, "croma_obj": 22, "lum_obj": 120,
           "area_obj": 30, "aresta": 10.0, "aresta_px": 2}


def bege_ta(Q, img, q=None):
    q = q or BEGE_TA
    im = img.astype(np.float32)
    B = T.F.fechar(np.all(Q.chapada == np.uint8(q["chapada"]), axis=2), 5) | (FA.ret_aa(Q, T.GRANITO_T["bege"]) > 0.5)
    B &= ~(FA.paredes_pdf(Q) > 0.3)
    rots = rotulos_na_imagem(Q, img, dentro=B)
    texto = np.zeros(B.shape, np.float32)
    for _, al, _, _ in rots:
        texto = np.maximum(texto, al)
    f = cv2.GaussianBlur(im, (0, 0), 0.7)
    lum, croma = f.mean(axis=2), f.max(axis=2) - f.min(axis=2)
    verde = f[..., 1] > f[..., 2] + 4
    obj = T.manchas(B & ((croma < q["croma_obj"]) | (lum < q["lum_obj"]) | verde), q["area_obj"], 4000)
    obj |= dilatar(texto > 0.02, 2) | (moveis_pdf(Q) & B)
    obj = dilatar(obj, 1)
    piso = B & ~obj
    # o tom do lugar: as peças tapadas (inpaint) e a mediana
    ys, xs = np.nonzero(B)
    y0, y1 = max(ys.min() - 30, 0), min(ys.max() + 31, Q.H)
    x0, x1 = max(xs.min() - 30, 0), min(xs.max() + 31, Q.W)
    sub = img[y0:y1, x0:x1].copy()
    fora = ~piso[y0:y1, x0:x1]
    sub = cv2.inpaint(sub, (fora * 255).astype(np.uint8), 5, cv2.INPAINT_TELEA)
    tom = cv2.medianBlur(sub, q["mediana_px"]).astype(np.float32)
    tom = cv2.GaussianBlur(tom, (0, 0), 1.5)
    # as arestas do tom (as bordas dos degraus e das sombras) ficam como estão
    tl = tom.mean(axis=2)
    gx, gy = cv2.Sobel(tl, cv2.CV_32F, 1, 0, ksize=3), cv2.Sobel(tl, cv2.CV_32F, 0, 1, ksize=3)
    aresta = dilatar(np.hypot(gx, gy) / 8 > q["aresta"], q["aresta_px"])
    D = im[y0:y1, x0:x1] / np.maximum(tom, 1)
    novo = tom * (1 + q["forca"] * (D - 1))
    m = (piso[y0:y1, x0:x1] & ~aresta).astype(np.float32)
    m = cv2.GaussianBlur(m, (0, 0), 0.8) * piso[y0:y1, x0:x1]
    out = im.copy()
    out[y0:y1, x0:x1] = im[y0:y1, x0:x1] * (1 - m[..., None]) + novo * m[..., None]
    for _, al, claro, _ in rots:
        out = compor(out, al, cor_rotulo(out, al))
    print(f"    Bege Bahia: as manchas a {q['forca']:.0%} do contraste em {piso.sum() / Q.px_m ** 2:.0f} m² (a regra do "
          f"Subsolo); rótulos de volta: {', '.join(r[0] for r, _, _, _ in rots) or 'nenhum'}")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
# 4. O piso marrom (a amostra do cliente: o marrom médio e uniforme, RGB ~135, 108, 87, de manchas suaves e sem as pintas
# do granito): no granito do piso (a cor malva da base chapada: cozinha, área gourmet, serviço, despensa, gás, quarto do
# motorista e garagem; o banho do motorista é Bege Bahia), a amostra tecida por image quilting, no tom dela. A luz da
# final passa ao piso novo (as sombras dos carros, das bancadas e das paredes; as nuvens e as pintas do granito, não: a
# luz é medida na mediana de `mediana` px e só vale o que escurece além de `limiar`). As peças ficam (as bancadas e os
# armários do PDF; o que a final mostra claro, sem cor ou fora do marrom: inox, carros e o contorno deles, banquetas,
# cubas, a cama), e o px da borda delas é refeito pela fração da peça (o px antigo entre a cor da peça e a do granito
# de perto) sobre o piso novo. Os rótulos saem e voltam em branco, no mesmo desenho. A escada caracol é redesenhada
# depois, sobre o piso novo.
PISO_MARROM_TA = {"amostra": "_texturas/originais/amostra_piso_marrom_cliente_1011.png", "p_px": 40, "sobra": 12,
                  "mediana": 5, "sig_luz": 1.4, "sig_base_m": 0.8, "limiar": 0.07, "lum_obj": 150, "croma_obj": 16,
                  "rb_obj": 20, "area_obj": 60, "buraco_max": 600, "anel_px": 2, "semente": 3101}


def amostra_piso(q=None):
    q = q or PISO_MARROM_TA
    return cv2.imread(str(RAIZ / q["amostra"])).astype(np.float32)


def caracol_disco(Q, folga_px=3):
    cx, cy = Q.p2q(*T.CARACOL["centro"])
    r = T.CARACOL["r_corrimao"] * FA.PT_PX + folga_px
    yy, xx = np.ogrid[:Q.H, :Q.W]
    return (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r


def piso_marrom_mascara(Q):
    g = T.GRANITO_T
    ch = T.F.fechar(np.all(Q.chapada == np.uint8(g["chapada"]), axis=2), g["fechar"])
    return ch & ~(FA.ret_aa(Q, g["bege"]) > 0.5)


def piso_marrom_ta(Q, img, q=None):
    q = q or PISO_MARROM_TA
    im = img.astype(np.float32)
    ch = piso_marrom_mascara(Q)
    regiao = dilatar(ch, 3)
    rots = [a for a in rotulos_na_imagem(Q, img, dentro=ch) if a[2]]
    texto = np.zeros(ch.shape, np.float32)
    for _, al, _, _ in rots:
        texto = np.maximum(texto, al)
    caixa_txt = dilatar(texto > 0.02, 3)
    # as peças: claras, sem cor ou fora do marrom (o vermelho pouco acima do azul)
    f = cv2.GaussianBlur(im, (0, 0), 0.6)
    lum, croma = f.mean(axis=2), f.max(axis=2) - f.min(axis=2)
    rb = f[..., 2] - f[..., 0]
    cand = regiao & ((lum > q["lum_obj"]) | (croma < q["croma_obj"]) | (rb < q["rb_obj"])) & ~caixa_txt
    obj = T.manchas(cand, q["area_obj"], q["buraco_max"])
    obj |= dilatar(T.pecas_cheias(Q), 1) & regiao
    obj |= (FA.paredes_pdf(Q) > 0.5) & regiao
    disco = caracol_disco(Q)
    obj &= ~disco
    nucleo = cv2.erode(obj.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    piso = (ch & ~dilatar(obj, q["anel_px"] - 1)) | (ch & disco)
    anel = ch & ~piso & ~nucleo
    # a luz do piso antigo, sem as pintas
    L = cv2.medianBlur(np.clip(im.mean(axis=2), 0, 255).astype(np.uint8), q["mediana"]).astype(np.float32)
    mf = (piso & ~caixa_txt & ~disco).astype(np.float32)
    perto = T.nconv2(L, mf, q["sig_luz"], onde=piso | anel)
    base = T.nconv2(L, mf, q["sig_base_m"] * Q.px_m, onde=piso | anel)
    sh = np.clip(perto / np.maximum(base, 1) + q["limiar"], 0, 1)
    sh[disco] = 1.0
    # o tecido da amostra, no tom dela
    A = amostra_piso(q)
    tom = A.reshape(-1, 3).mean(axis=0)
    ys, xs = np.nonzero(piso | anel)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    Tq = tecido(variantes(A), y1 - y0, x1 - x0, q["p_px"], q["sobra"], q["semente"])
    Tq = Tq / Tq.reshape(-1, 3).mean(axis=0) * tom
    N = im.copy()
    N[y0:y1, x0:x1] = Tq * sh[y0:y1, x0:x1, None]
    out = im.copy()
    out[piso] = N[piso]
    # o px da borda das peças: a fração da peça sobre o piso novo
    G = nconv(cv2.medianBlur(img, q["mediana"]).astype(np.float32), mf, 2.0)
    _, (iy, ix) = ndimage.distance_transform_edt(~nucleo, return_indices=True)
    C = im[iy, ix]
    d = C - G
    den = (d * d).sum(axis=2)
    a = np.clip(((im - G) * d).sum(axis=2) / np.maximum(den, 1e-3), 0, 1)
    a = np.where(den < 400, (np.abs(im - C).sum(axis=2) < np.abs(im - G).sum(axis=2)).astype(np.float32), a)
    novo_anel = a[..., None] * C + (1 - a[..., None]) * N
    out[anel] = novo_anel[anel]
    for _, al, _, _ in rots:
        out = compor(out, al, ROTULO_CLARO)
    print(f"    piso marrom: a amostra do cliente (tom BGR {tuple(int(round(v)) for v in tom)}) em "
          f"{piso.sum() / Q.px_m ** 2:.1f} m², com a luz da final; {int(anel.sum())} px de borda refeitos pela fração da "
          f"peça; rótulos em branco de volta: {', '.join(r[0] for r, _, _, _ in rots)}")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
# 5. As bancadas:
# - cozinha (cliente: "Cor da ilha é no Dekton Danae"; "Cor da bancada é no Dekton Danae"): a ilha e a bancada da pia
#   (`final3840_casaa_terreo.COZINHA`) no Danae, com a borda e a sombra; as laterais em cascata, o cooktop, a área
#   molhada um tom abaixo e as duas cubas de inox de novo por cima;
# - área de serviço (cliente: "Cor da bancada é no Dekton Danae"): a bancada dos tanques e o braço dela (`ajustes_casaa.
#   TANQUES` e `ARMARIOS_A["bancada"]`) no Danae, menos os tanques, que ficam;
# - lavatório (cliente: "Toda a bancada e a cuba é no marrom tabaco ... deixar a cuba ou com um tom mais claro ou mais
#   escuro que a bancada"): a bancada no marrom tabaco da ilha da área gourmet e a cuba esculpida nele, mais escura
#   (`cuba_esc`); a torneira de novo;
# - churrasqueira (cliente: "Faltou a representação da churrasqueira"): no retângulo do PDF (ARQ_LAYOUT HUMANIZAÇÃO) na
#   bancada de trás da área gourmet: o aro de inox, a grelha escura com as barras e a sombra curta;
# - lavabo (cliente: "A cuba e a pedra lateral são da mesma cor"): a pedra lateral (ARQ_BANCADAS, abaixo da bancada) no
#   tom e no desenho da bancada da cuba.
BANCADAS_TA = {"semente": 3120, "cuba_esc": 0.78,
               "churrasqueira_pt": (1315.4, 1557.1, 1391.9, 1596.6), "inox": (190, 193, 196), "grelha": (40, 40, 42),
               "barra": (96, 98, 100), "barra_px": (1.0, 4.0), "aro_px": 3.0,
               "lavabo_cuba_pt": (2077.9, 615.8, 2106.3, 670.2), "lavabo_lateral_pt": (2089.3, 670.2, 2106.3, 715.0),
               "lavabo_camadas": [(0.010, 0.6), (0.022, 5.0)]}


def _danae_fn(semente, mult=1.0):
    return lambda tl: danae(tl.h, tl.w, semente) * mult


def bancadas_ta(Q, img, q=None):
    import ajustes_casaa as AJ
    q = q or BANCADAS_TA
    out = np.ascontiguousarray(img.copy())
    i, c = T.ILHA, T.COZINHA
    s = q["semente"]
    # cozinha
    out = FA.bancada_pedra(Q, out, c["ilha"], _danae_fn(s), DANAE["borda"], i["larg"], i["sombra"])
    out = T.linhas_pedra(Q, out, c["laterais"], i["linha_px"], i["linha"])
    out = T.cooktop(Q, out, c["cooktop"])
    out = FA.bancada_pedra(Q, out, c["pia"], _danae_fn(s + 1), DANAE["borda"], i["larg"], i["sombra"])
    out = FA.bancada_pedra(Q, out, c["molhada"], _danae_fn(s + 2, DANAE["molhada"]), DANAE["borda"], i["larg"], 0.0)
    for cb in c["cubas"]:
        out = T.cuba_inox(Q, out, cb)
    # área de serviço: a bancada dos tanques e o braço dela, menos os tanques
    rets = list(AJ.TANQUES["bancada"]) + [AJ.ARMARIOS_A["bancada"]]
    caixa = (min(r[0] for r in rets), min(r[1] for r in rets), max(r[2] for r in rets), max(r[3] for r in rets))
    tl = FA.tela(out, Q, caixa, folga=6)
    m = tl.vazia()
    for r in rets:
        m |= tl.ret(r)
    for t in AJ.TANQUES["tanques"]:
        m &= ~cv2.dilate(tl.ret(t["caixa"], 3.0), np.ones((5, 5), np.uint8))
    tl.pintar_img(m, danae(tl.h, tl.w, s + 3))
    tl.contorno(m, 0.35, (140, 146, 150))
    out = tl.gravar()
    # lavatório: a bancada no marrom tabaco e a cuba esculpida, mais escura
    lv = T.LOUCAS["lavatorio"]
    tab = lambda k, sem: (lambda tl_: FA._granito(Q, tl_, sem) * i["escurecer"] * k)
    out = FA.bancada_pedra(Q, out, lv["bancada"], tab(1.0, lv["semente"]), i["borda"], i["larg"], i["sombra"])
    out = FA.cuba_pedra(Q, out, lv, tab(q["cuba_esc"], lv["semente"] + 1), FA.GRANITO_CUBA)
    out = FA.torneira(Q, out, lv["torneira"], lv["base"])
    # a churrasqueira
    r = q["churrasqueira_pt"]
    tl = FA.tela(out, Q, r, folga=6)
    m = tl.ret(r, 0.6)
    FA.sombra_q(tl, m, forca=0.30)
    tl.pintar(m, q["inox"])
    aro = q["aro_px"] / FA.PT_PX
    g = tl.ret((r[0] + aro, r[1] + aro, r[2] - aro, r[3] - aro), 0.4)
    tl.pintar(g, q["grelha"])
    larg, passo = q["barra_px"]
    X, Y = tl.grade()
    barras = (np.mod((X - r[0]) * FA.PT_PX, passo) < larg) & (tl.reduzir(g) > 0.5)
    tl.reg = np.where(barras[..., None], np.float32(q["barra"]), tl.reg)
    tl.contorno(m, 0.4, (110, 112, 114))
    out = tl.gravar()
    # lavabo: a pedra lateral na cor e no desenho da bancada da cuba
    x0, y0, x1, y1 = (int(round(v)) for v in ret_q(Q, q["lavabo_cuba_pt"]))
    cuba = img[y0 + 3:y1 - 3, x0 + 3:x1 - 3].astype(np.float32)
    tom = np.median(cuba.reshape(-1, 3), axis=0)
    lx0, ly0, lx1, ly1 = ret_q(Q, q["lavabo_lateral_pt"])
    tl = FA.tela(out, Q, q["lavabo_lateral_pt"], folga=4)
    m = tl.ret(q["lavabo_lateral_pt"])
    FA.sombra_q(tl, m, forca=T.LAVABO["sombra"], dist=1.3, sigma=1.3)
    tl.pintar_img(m, danae(tl.h, tl.w, q["semente"] + 7, dict(DANAE, tom=tuple(float(v) for v in tom),
                                                                camadas=q["lavabo_camadas"])))
    k = max(1, int(round(T.LAVABO["larg_px"] * 8)))
    borda = m & ~cv2.erode(m, np.ones((k, k), np.uint8))
    tl.pintar_img(borda, tl.reg * T.LAVABO["borda"])
    out = tl.gravar()
    print("    bancadas: a ilha e a bancada da pia da cozinha e a bancada dos tanques no Dekton Danae; o lavatório em "
          "marrom tabaco, a cuba mais escura; a churrasqueira no PDF; a pedra lateral do lavabo na cor da cuba "
          f"(BGR {tuple(int(v) for v in tom)})")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 6. As banquetas da área gourmet (cliente: "Colocar só 5 banquetas. E com um tom um pouco mais destacado em relação ao
# piso"): as 6 do render (as caixas acima do tampo, `zona_px`) saem com o travertino refeito
# (`pedidos_terreo_casaa_2910.piso_refeito`); entram 5, espaçadas por igual no trecho das 6 (`x_px`), a banqueta de linho
# da biblioteca virada para a ilha, parcialmente sob o tampo, no tom `tom` (mais escuro que o travertino), com a sombra
# curta.
BANQUETAS_TA = {"zona_px": (1488, 1240, 1740, 1272), "x_px": (1512.0, 1712.0), "n": 5, "y_px": 1262.0, "d_m": 0.42,
                "tom": (140, 158, 178), "sombra": (0.22, 0.05, 0.06), "semente": 3130}


def banquetas_ta(Q, img, q=None):
    import pedidos_terreo_casaa_2910 as P
    sys.path.insert(0, str(RAIZ / "_blocos"))
    import blocos
    q = q or BANQUETAS_TA
    tampo = Q.preencher(lambda d: d.get("layer") == "ARQ_BANCADAS" and d.get("fill"), fs=False)
    x0, y0, x1, y1 = q["zona_px"]
    zona = np.zeros(img.shape[:2], bool)
    zona[y0:y1, x0:x1] = True
    zona &= tampo < 0.5
    out = P.piso_refeito(img, zona, q["semente"])
    cor, al = blocos.bloco("banqueta_linho", q["d_m"] * Q.px_m / 0.45)
    cor, al = cv2.rotate(cor, cv2.ROTATE_180), cv2.rotate(al, cv2.ROTATE_180)
    al = np.clip(al, 0, 1).astype(np.float32)
    cor = cor.astype(np.float32)
    med = np.median(cor[al > 0.8], axis=0)
    cor = cor / med * np.float32(q["tom"])
    h, w = al.shape
    fs, dm, sm = q["sombra"]
    d_, sig = dm * Q.px_m, sm * Q.px_m
    of = out.astype(np.float32)
    for cx in np.linspace(*q["x_px"], q["n"]):
        cy = q["y_px"]
        f = int(np.ceil(d_ + 4 * sig)) + 2
        X0, Y0 = int(cx - w / 2) - f, int(cy - h / 2) - f
        Wr, Hr = w + 2 * f, h + 2 * f
        Mt = np.float32([[1, 0, cx - w / 2 - X0], [0, 1, cy - h / 2 - Y0]])
        livre = 1 - tampo[Y0:Y0 + Hr, X0:X0 + Wr]
        a = cv2.warpAffine(al, Mt, (Wr, Hr), flags=cv2.INTER_LINEAR)
        c = cv2.warpAffine(cor, Mt, (Wr, Hr), flags=cv2.INTER_LINEAR)
        sb = cv2.GaussianBlur(cv2.warpAffine(a, np.float32([[1, 0, -d_], [0, 1, d_]]), (Wr, Hr)), (0, 0), sig) * fs
        a = a * livre
        reg = of[Y0:Y0 + Hr, X0:X0 + Wr]
        reg *= (1 - sb * livre * (1 - a))[..., None]
        of[Y0:Y0 + Hr, X0:X0 + Wr] = reg * (1 - a[..., None]) + c * a[..., None]
    print(f"    área gourmet: as 6 banquetas do render saem; {q['n']} banquetas de linho no tom BGR {q['tom']}, "
          "parcialmente sob o tampo, com a sombra curta")
    return np.clip(np.round(of), 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
# 7. O pilar do canto do terraço gourmet (cliente: "Falha na representação do pilar."): o quadrado do PDF (EST - Pilar)
# em preto, nítido, com a cobertura exata da borda; a mancha cinza que o render deixou no canto de cima, à esquerda
# (fora do quadrado), sai com o travertino de logo ao lado.
PILAR_TA = {"pt": (1037.6, 1758.2, 1065.9, 1786.5), "cor": (24, 24, 24), "mancha_px": 6}


def pilar_ta(Q, img, q=None):
    q = q or PILAR_TA
    out = img.astype(np.float32)
    a = FA.ret_aa(Q, q["pt"])
    x0, y0, x1, y1 = (int(round(v)) for v in ret_q(Q, q["pt"]))
    k = q["mancha_px"]
    # a mancha cinza fora do quadrado, acima e à esquerda: o travertino de logo acima (2x mais longe)
    for yy in range(y0 - k, y0):
        for xx in range(x0 - k, x1):
            if a[yy, xx] < 0.02:
                L = out[yy, xx].mean()
                if L < 185:
                    out[yy, xx] = out[yy - 2 * k, xx]
    out = out * (1 - a[..., None]) + np.float32(q["cor"]) * a[..., None]
    print("    pilar do terraço gourmet: o quadrado do PDF em preto, sem a mancha cinza do canto")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
# 8. As soleiras:
# - a da entrada (cliente: "Representar uma soleira na entrada igual a casa C"): no vão da porta pivotante, entre os
#   batentes do PDF (`entrada_pt`), a faixa de pedra clara da Casa C (`tom`), com as faces em cinza fino;
# - a da sala para o escritório (cliente: "Não tem soleira entre a sala e o escritório"): a faixa clara no vão
#   (`escritorio_px`) sai; o travertino atravessa o vão.
SOLEIRAS_TA = {"entrada_px": (2444.0, 686.0, 2456.5, 843.0), "tom": (196, 210, 222), "face": (150, 150, 150),
               "face_px": 0.6, "escritorio_px": (2343, 529, 2359, 589), "semente": 3140}


def soleiras_ta(Q, img, q=None):
    import pedidos_terreo_casaa_2910 as P
    q = q or SOLEIRAS_TA
    out = np.ascontiguousarray(img.copy())
    # a da sala para o escritório sai: a faixa do vão (o branco da ARQ_PAREDE entre as pontas das paredes), menos o
    # escuro das paredes, com o travertino refeito
    x0, y0, x1, y1 = q["escritorio_px"]
    reg = img[y0:y1, x0:x1].astype(np.float32)
    zona = np.zeros(img.shape[:2], bool)
    zona[y0:y1, x0:x1] = reg.mean(axis=2) > 140
    out = P.piso_refeito(out, zona, q["semente"])
    # a da entrada
    (ax, ay), (bx, by) = Q.q2p(*q["entrada_px"][:2]), Q.q2p(*q["entrada_px"][2:])
    r = (min(ax, bx), min(ay, by), max(ax, bx), max(ay, by))
    tl = FA.tela(out, Q, r, folga=4)
    m = tl.ret(r)
    sys.path.insert(0, str(RAIZ / "_texturas"))
    from texturas import textura
    Tb = textura("bege_bahia", Q.px_m, tl.h, tl.w, semente=q["semente"]).astype(np.float32)
    Tb = Tb / Tb.reshape(-1, 3).mean(axis=0) * np.float32(q["tom"])
    tl.pintar_img(m, Tb)
    tl.contorno(m, q["face_px"], q["face"])
    out = tl.gravar()
    print(f"    soleiras: sem a da sala para o escritório ({int(zona.sum())} px de travertino refeito); a da entrada no vão "
          "da porta pivotante, como a da Casa C")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 9. A entrada (cliente: "Centralizar a seta com a abertura da porta, usando este modelo de seta"; usuário: "USAR O
# TRIANGULO COMO SETA E REMOVER A SETA QUE HAVIA."): a seta de 1,5 m do hall externo (`final3840_casaa_terreo.SETA`)
# sai com o Bege Bahia refeito; entra o triângulo cheio das escadas, com a ponta para dentro da casa, no centro da
# abertura da porta (`abertura_px`: de y0 a y1), a `recuo_px` da soleira.
ENTRADA_TA = {"abertura_px": (686.0, 843.0), "x_soleira_px": 2457.0, "recuo_px": 16.0, "comp": 18.0, "larg": 21.0,
              "semente": 3150, "fontes_px": [(2480, 700, 2600, 760), (2480, 820, 2600, 860)]}


def entrada_ta(Q, img, q=None):
    import pedidos_terreo_casaa_2910 as P
    q = q or ENTRADA_TA
    s = T.SETA
    px, py = s["ponta"]
    k = Q.px_m
    x0, x1 = int(px - 4), int(px + s["comp_m"] * k + 6)
    hl = s["cabeca_m"][1] * k
    y0, y1 = int(py - hl / 2 - 5), int(py + hl / 2 + 6)
    reg = img[y0:y1, x0:x1].astype(np.float32)
    zona = np.zeros(img.shape[:2], bool)
    zona[y0:y1, x0:x1] = dilatar(reg.mean(axis=2) < 120, 3)
    out = P.piso_refeito(img, zona, q["semente"], dict(P.PISO_TA, fontes_px=q["fontes_px"]))
    a0, a1 = q["abertura_px"]
    cy = (a0 + a1) / 2
    cx = q["x_soleira_px"] + q["recuo_px"] + q["comp"] / 2
    out = triangulo(out.astype(np.float32), seta_tri(cx, cy, (-1, 0), q["comp"], q["larg"]))
    print(f"    entrada: sem a seta antiga; o triângulo no centro da abertura da porta (y = {cy:.0f} px)")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
# 10. As escadas (cliente: "Colocar a seta em todas as escadas e a descrição"; o modelo é o do Subsolo aprovado: o
# triângulo cheio, com a ponta para onde se vai, e a descrição em caixa alta, em duas linhas, no lugar da letra):
# - os degraus escalonados junto à piscina: "DESCE PARA O DECK" (usuário); o D sai;
# - o lance abaixo do spa: "DESCE PARA O SUBSOLO" (usuário); o D sai;
# - a escada do jardim: "SOBE PARA O 1º PAVIMENTO"; o S sai; e o guarda-corpo de vidro fino ao longo do vão entre os
#   lances (cliente: "Representar o guarda-corpo");
# - a caracol (cliente: "Melhorar a representação da escada helicoidal. Ver exemplo."; "Deixar a linha tracejada apenas
#   nos degraus da escada como está no exemplo"; "Não esquecer o S e a descrição sobe 'para tal espaço'"; "A linha de
#   corte não precisa ser feita"): redesenhada sobre o piso novo, os degraus em leque no tom claro, com as linhas dos
#   degraus (cheias até o corte e tracejadas nos de cima, sem a linha de corte) e o corrimão em volta (cheio, depois
#   tracejado), o pilar preto no centro; o triângulo no 1º degrau, para onde ela sobe, e "SOBE PARA O 1º PAVIMENTO".
ESCADAS_TA = {
    "pisantes": {"texto": ("DESCE PARA O", "DECK"), "dir": (-1, 0), "tri_px": (1052.0, 418.0), "txt_px": (1094.0, 418.0),
                 "alinhar": "esquerda", "letra": ("D", (0, 26))},
    "deck": {"texto": ("DESCE PARA O", "SUBSOLO"), "dir": (1, 0), "tri_px": (914.0, 1094.0), "txt_px": (896.0, 1094.0),
             "alinhar": "direita", "letra": ("D", (0, -22))},
    "jardim": {"texto": ("SOBE PARA O", "1º PAVIMENTO"), "dir": (1, 0), "tri_px": (2266.0, 948.0),
               "txt_px": (2282.0, 948.0), "alinhar": "esquerda", "letra": ("S", (0, 24)),
               "guarda_corpo_pt": [((2021.2, 1162.9), (2174.3, 1162.9)), ((2019.5, 1185.6), (2174.3, 1185.6)),
                                   ((2174.3, 1162.9), (2174.3, 1185.6))],
               "vidro": (214, 220, 224), "vidro_face": (120, 126, 130), "vidro_px": 2.0},
    "caracol": {"texto": ("SOBE PARA O", "1º PAVIMENTO"), "txt_px": (1916.0, 1604.0), "alinhar": "direita", "tom": (166, 186, 208),
                "tons": (0.90, 1.0), "linha": (96, 96, 98), "linha_px": 0.8, "traco_pt": (4.0, 3.0), "tri": (13.0, 15.0)},
    "cor_texto": (45, 45, 45)}


def _texto_escada(out, linhas, x, y, alinhar, cor):
    a = alfa_texto(linhas, x, y, alinhar, forma=out.shape[:2])
    return compor(out.astype(np.float32), a, cor)


def caracol_novo(Q, img, q):
    """A caracol redesenhada (ver `ESCADAS_TA["caracol"]`)."""
    c = T.CARACOL
    cx, cy = c["centro"]
    R = c["r_corrimao"] + 1.5
    tl = FA.tela(np.ascontiguousarray(img.copy()), Q, (cx - R, cy - R, cx + R, cy + R), folga=3)
    S = 8
    ys, xs = np.mgrid[0:tl.h * S, 0:tl.w * S].astype(np.float32)
    (ax, ay), (bx, by) = Q.q2p(tl.x0, tl.y0), Q.q2p(tl.x0 + 1, tl.y0 + 1)
    X, Y = ax + (xs + 0.5) / S * (bx - ax), ay + (ys + 0.5) / S * (by - ay)
    r = np.hypot(X - cx, Y - cy)
    th = (np.degrees(np.arctan2(-(Y - cy), X - cx)) - c["a0"]) % 360
    n = int(np.ceil(360 / c["passo"]))
    k = np.clip((th // c["passo"]).astype(int), 0, n - 1)
    t0, t1 = q["tons"]
    f = t0 + (t1 - t0) * k / (n - 1)

    def red(m):
        return cv2.resize(m.astype(np.float32), (tl.w, tl.h), interpolation=cv2.INTER_AREA)
    degrau = (r >= c["r_pilar"]) & (r <= c["r_degrau"])
    corte = c["corte"] - c["a0"]
    a_deg = red(degrau)[..., None]
    fr = (red(f * degrau) / np.maximum(red(degrau), 1e-4))[..., None]
    tl.reg = tl.reg * (1 - a_deg) + np.float32(q["tom"]) * fr * a_deg
    # as linhas dos degraus (os espelhos, radiais): cheias até o corte, tracejadas depois
    lpx = q["linha_px"] / FA.PT_PX
    dist_esp = np.abs(((th + c["passo"] / 2) % c["passo"]) - c["passo"] / 2) * np.pi / 180 * r
    esp = (dist_esp <= lpx / 2 * 1.0) & degrau
    tr, va = q["traco_pt"]
    tracejado_r = np.mod(r, tr + va) < tr
    esp = esp & ((th <= corte) | tracejado_r)
    # o contorno dos degraus (o corrimão), cheio até o corte e tracejado depois
    arco = np.abs(r - c["r_degrau"]) <= lpx / 2
    s_arco = th * np.pi / 180 * c["r_degrau"]
    arco &= (th <= corte) | (np.mod(s_arco, tr + va) < tr)
    a_lin = red(esp | arco)[..., None]
    tl.reg = tl.reg * (1 - a_lin) + np.float32(q["linha"]) * a_lin
    a_pil = red(r < c["r_pilar"])[..., None]
    tl.reg = tl.reg * (1 - a_pil) + np.float32(c["pilar"]) * a_pil
    return tl.gravar()


def escadas_ta(Q, img, q=None):
    q = q or ESCADAS_TA
    out = np.ascontiguousarray(img.copy())
    cor = q["cor_texto"]
    # as letras antigas saem
    centros = {"pisantes": None, "deck": Q.p2q(*T.DECK_T["centro"]), "jardim": Q.p2q(*T.ESCADA_U["centro"])}
    x0, y0, x1, y1 = T.PISANTES["blocos"][-1]
    centros["pisantes"] = Q.p2q((x0 + x1) / 2, (y0 + y1) / 2)
    for nome in ("pisantes", "deck", "jardim"):
        e = q[nome]
        out = tirar_letra(Q, out, e["letra"][0], centros[nome], e["letra"][1])
    # a caracol, sobre o piso novo
    out = caracol_novo(Q, out, q["caracol"])
    out = out.astype(np.float32)
    for nome in ("pisantes", "deck", "jardim"):
        e = q[nome]
        tx, ty = e["tri_px"]
        out = triangulo(out, seta_tri(tx, ty, e["dir"]))
        out = _texto_escada(out, e["texto"], *e["txt_px"], e["alinhar"], cor)
    # o guarda-corpo da escada do jardim: o vidro fino com as faces
    j = q["jardim"]
    for p0, p1 in j["guarda_corpo_pt"]:
        a, b = Q.p2q(*p0), Q.p2q(*p1)
        m = np.zeros(out.shape[:2], np.uint8)
        S = 4
        mm = np.zeros((out.shape[0] * S, out.shape[1] * S), np.uint8)
        cv2.line(mm, (int(a[0] * S), int(a[1] * S)), (int(b[0] * S), int(b[1] * S)), 255,
                 int(round(j["vidro_px"] * S)), cv2.LINE_AA)
        al = cv2.resize(mm.astype(np.float32) / 255, (out.shape[1], out.shape[0]), interpolation=cv2.INTER_AREA)
        borda = np.clip(al - cv2.erode(al, np.ones((3, 3), np.float32)), 0, 1)
        out = compor(out, al, j["vidro"])
        out = compor(out, borda * 0.8, j["vidro_face"])
        _ = m
    # a caracol: o triângulo no 1º degrau, para onde ela sobe (anti-horário), e a descrição
    c = T.CARACOL
    ccx, ccy = Q.p2q(*c["centro"])
    rm = (c["r_pilar"] + c["r_degrau"]) / 2 * FA.PT_PX
    ang = np.radians(c["a0"] + c["passo"] / 2)
    tx, ty = ccx + rm * np.cos(ang), ccy - rm * np.sin(ang)
    out = triangulo(out, seta_tri(tx, ty, (-np.sin(ang), -np.cos(ang)), *q["caracol"]["tri"]))
    cc = q["caracol"]
    if cc["txt_px"] is not None:
        out = _texto_escada(out, cc["texto"], *cc["txt_px"], cc["alinhar"], ROTULO_CLARO)
    print("    escadas: o triângulo e a descrição nas 4 escadas (DESCE PARA O DECK, DESCE PARA O SUBSOLO, SOBE PARA O 1º "
          "PAVIMENTO na do jardim e na caracol); a caracol com as linhas dos degraus, tracejadas nos de cima, sem a "
          "linha de corte; o guarda-corpo de vidro da escada do jardim")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
# 11. O shaft (cliente: "Tirar o nome shaft"): o rótulo SHAFT sai (o fundo claro de dentro do shaft, do entorno).
def shaft_ta(Q, img):
    out = img.copy()
    rots = [a for a in rotulos_na_imagem(Q, img) if a[0][0] == "SHAFT"]
    for _, al, _, _ in rots:
        m = (dilatar(al > 0.02, 1) * 255).astype(np.uint8)
        out = cv2.inpaint(out, m, 3, cv2.INPAINT_TELEA)
    print(f"    shaft: {'sem o nome SHAFT' if rots else 'o rótulo SHAFT não foi achado'}")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 12. Os tracejados que ficam, finos e claros (cliente, no pergolado: "Deixar as linhas do pergolado tracejadas mais
# finas e mais claras"; na área de serviço descoberta e nos X da varanda e da sala de estar: "Deixar as linhas
# tracejadas mais finas e mais claras"): os traços do PDF de novo, a `larg_px`, em cinza (`escuro` nos fundos claros,
# `claro` nos escuros, pela luz em volta de cada traço): o pergolado, os X e as molduras dos vazios (varanda e sala de
# estar, com o lado esquerdo no alinhamento do X; a área de serviço descoberta, aberta em volta do rótulo; a claraboia
# do lavabo; o shaft). Não passam sobre os rótulos nem sobre os móveis do PDF.
FINOS_TA = {"larg_px": 0.9, "escuro": (112, 112, 112), "claro": (205, 205, 205), "limiar": 125,
            "vazios_px": [(1505, 600, 2160, 888), (1700, 1638, 1918, 1935), (2248, 345, 2352, 392),
                          (2348, 1110, 2392, 1214)], "vazio_esquerda_pt": 1315.4, "folga_rotulo": 6}


def tracejados_finos_ta(Q, img, q=None):
    q = q or FINOS_TA
    segs = []
    for _, _, ss in T.cadeias_tracejadas(Q, ["DOC_LINHAS E PROJEÇÕES"], min_n=2, min_ext=20):
        for s in ss:
            u, v = Q.p2q((s[0] + s[2]) / 2, (s[1] + s[3]) / 2)
            if any(a <= u <= c and b <= v <= d for a, b, c, d in q["vazios_px"]):
                segs.append(s)
    x = q["vazio_esquerda_pt"]
    segs += [(x, s[1], x, s[3]) for k, _, ss in T.cadeias_tracejadas(Q, ["DOC_LINHAS E PROJEÇÕES"])
             if k[1] == 90.0 and round(k[2]) == -1922 for s in ss]
    segs += [s for _, _, ss in T.cadeias_tracejadas(Q, ["ARQ_PERGOLADO"]) for s in ss]
    # fora dos rótulos (com folga) e dos móveis
    rots = rotulos_na_imagem(Q, img)
    tapa = np.zeros(img.shape[:2], bool)
    for _, al, _, _ in rots:
        tapa |= dilatar(al > 0.02, q["folga_rotulo"])
    tapa |= moveis_pdf(Q)
    pq = dict(T.PROJ, larg_px=q["larg_px"], preto=q["escuro"], branco=q["claro"], limiar=q["limiar"])
    novo, _ = T.preto_branco(Q, img, segs, pq)
    out = np.where(tapa[..., None], img, novo)
    print(f"    tracejados finos e claros: {len(segs)} traços (o pergolado e os X dos vazios), fora dos rótulos e dos "
          "móveis")
    return out


# ----------------------------------------------------------------------------------------------------------------------
PASSOS = [("tracejados", tracejados_ta), ("gramado", gramado_ta), ("piscina", piscina_ta),
          ("bege", bege_ta), ("piso_marrom", piso_marrom_ta), ("bancadas", bancadas_ta), ("banquetas", banquetas_ta), ("pilar", pilar_ta),
          ("soleiras", soleiras_ta), ("entrada", entrada_ta), ("escadas", escadas_ta), ("shaft", shaft_ta),
          ("tracejados_finos", tracejados_finos_ta)]


def correcoes_ta(img, de=None, ate=None, salvar_passos=None):
    Q = FA.QuadroA("Terreo")
    out = img.copy()
    ativo = de is None
    for nome, f in PASSOS:
        if nome == de:
            ativo = True
        if not ativo:
            continue
        print(f"  {nome}")
        out = f(Q, out)
        if salvar_passos:
            cv2.imwrite(str(Path(salvar_passos) / f"passo_{nome}.png"), out)
        if nome == ate:
            break
    return out


# os antes e depois (contra a final do commit 58ea098), em renders/POE642_CasaA_PH_Terreo_1011_<trecho>_antes_depois.jpg
ANTES_DEPOIS_1011 = {"Terreo": {"planta": (270, 140, 3440, 1960), "vazios_varanda_estar": (1480, 580, 2180, 910),
                                "pergolado": (1180, 840, 1560, 1240), "pisantes_deck": (700, 320, 1240, 470),
                                "piscina_prainha": (700, 480, 1360, 1060), "escada_subsolo": (740, 1020, 1130, 1150),
                                "gourmet": (1180, 1180, 1800, 1680), "cozinha_servico": (1700, 1100, 2200, 1660),
                                "caracol": (1760, 1480, 2060, 1660), "entrada_escritorio": (2240, 460, 2640, 880),
                                "lavabo_shaft": (2220, 330, 2420, 560), "escada_jardim": (2240, 860, 2560, 1110),
                                "jardim_479": (1430, 1600, 1730, 1780)}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--antes", required=True)
    ap.add_argument("--de")
    ap.add_argument("--ate")
    ap.add_argument("--saida")
    ap.add_argument("--passos")
    ap.add_argument("--antes_depois", action="store_true", help="grava os recortes de ANTES_DEPOIS_1011 em renders/")
    a = ap.parse_args()
    img = cv2.imread(a.antes)
    out = correcoes_ta(img, a.de, a.ate, a.passos)
    cv2.imwrite(a.saida or str(FINAL), out)
    if a.antes_depois:
        import pedidos_terreo_casaa_2910 as P
        P.antes_depois_pedidos_ta("Terreo", img, out, caixas=ANTES_DEPOIS_1011, sufixo="1011")


if __name__ == "__main__":
    main()

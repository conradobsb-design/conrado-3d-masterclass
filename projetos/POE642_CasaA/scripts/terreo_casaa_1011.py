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
ROTULOS_LAVABO = FA.CASA / "renders" / "POE642_CasaA_PH_Terreo_rotulos_lavabo.json"
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


ANOTAR = {"sim": True}     # False: sem os triângulos e as descrições (o Térreo para o nublado do 1º Pavimento)


def triangulo(out, pts, cor=(30, 30, 30), ss=8):
    """O triângulo cheio (a seta das escadas), antisserrilhado."""
    if not ANOTAR["sim"]:
        return out
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
GRAMADO_TA = {"lote_px": (300, 186, 3398, 1912), "mascara_px": (262, 140, 3450, 1960), "muro_px": 8, "verde": -4, "verde_azul": 10, "faixa_px": 4, "fechar": 7, "buraco_max": 9000, "area_min": 3000,
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
    # a caixa passa dos muros (usuário: "VAMOS CORRIGIR O GRAMADO ATÉ O MURO"): o limite é o verde do render, que vai
    # até a face de dentro dos muros e até a linha do lote; `lote_px` fica só para pôr os arbustos junto aos muros
    x0, y0, x1, y1 = q["mascara_px"]
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
    # junto aos muros, o render vai uns px além da base (a grama até a face do muro que ele desenha): o verde do render
    # colado ao gramado entra, fora do branco da base; o muro (cinza neutro) segue sendo o limite
    vr = (I[..., 1] >= I[..., 2] + q["verde"]) & (I[..., 1] >= I[..., 0] + q["verde_azul"]) & lote
    for _ in range(q["muro_px"]):
        m |= dilatar(m, 1) & vr
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
# Depois (usuário, 10/11, com 3 fotos de uma piscina vista de cima: "CONSEGUIMOS DEIXAR O TOM DA PISCINA E DA PRAINHA/SPA
# MAIS PARECIDO COM ESTES"): a água funda no azul-ardósia escuro das fotos (`tom`), com o grão fino do revestimento
# (`grao_*`), manchas largas de luz (`manchas_*`), as cáusticas finas e curtas em grupos (as linhas onde um ruído de banda
# estreita passa por zero, `caus_*`, quebradas e com densidade variável) e a sombra das bordas (mais forte na esquerda e
# em cima, como nas fotos); a parte rasa no cinza neutro das fotos (`tom_rasa`), com mais grão e cáusticas fracas: a
# prainha e o banco do spa (o anel do PDF em volta do quadrado do fundo); o degrau entre a prainha e a piscina com a
# sombra fina do lado fundo. Os traços sobre a água saem (o pergolado volta no fim, fino e claro); os rótulos voltam no
# mesmo desenho, em branco na água escura e em preto na rasa. A água fica nos retângulos do PDF, com a cobertura exata.
# Depois (usuário, 10/11, no prompt v34: "Preciso que o revestimento das piscinas apareça na planta humanizada"; e, na
# pergunta do tom: "Turquesa #7CC8D4 do item novo"): a água turquesa clara, límpida e luminosa #7CC8D4 sobre o
# revestimento Barlavento, que aparece através dela: pastilhas cinza-esverdeadas claras #B7CFC9 de `peca_cm`, cada uma
# num tom um pouco diferente (`peca_var`), com as juntas finas e regulares (`junta`, a fração da peça de cada lado,
# escurecidas a `junta_f`) e a grade alinhada à borda de cada tanque; nas partes fundas a água um pouco mais intensa
# (`tom`) e as pastilhas menos marcadas (`contraste`), na prainha e no banco do spa a água mais rasa e mais clara
# (`tom_rasa`, o turquesa misturado ao tom da pastilha) e as pastilhas mais visíveis; as ondulações sutis (a grade
# levemente deslocada pela refração, `onda`, e as cáusticas fracas), sem reflexo forte, brilho de sol nem sombra (só um
# esfumado mínimo junto às bordas e o fio do degrau da prainha). O azul e as pastilhas ficam só nos retângulos da água.
PISCINA_TA = {"tom": (204, 192, 114), "tom_rasa": (207, 203, 150), "pastilha": (201, 207, 183), "peca_cm": 14.5,
              "junta": 0.075, "junta_f": 0.84, "peca_var": 0.025, "grao_a": 0.015, "onda": (7.0, 0.35),
              "contraste": {"funda": 0.55, "rasa": 1.0},
              "prainha_y_pt": 1049.5,
              "spa_pt": (748.5, 1049.5, 907.2, 1219.6), "spa_fundo_bgr": (255, 247, 223), "semente": 4210,
              "funda": {"grao_sig": 0.5, "grao_a": 0.0, "manchas_sig": 30.0, "manchas_a": 0.03, "caus_sig": 3.0,
                        "caus_larg": 0.15, "quebra_sig": 4.0, "quebra_b": 0.4, "dens_sig": 24.0, "dens_k": 0.7,
                        "dens_b": 0.5, "caus_a": 0.12, "caus_cor": (240, 242, 226)},
              "rasa": {"grao_sig": 0.5, "grao_a": 0.0, "manchas_sig": 30.0, "manchas_a": 0.02, "caus_sig": 3.0,
                       "caus_larg": 0.13, "quebra_sig": 4.0, "quebra_b": 0.3, "dens_sig": 24.0, "dens_k": 0.8,
                       "dens_b": 0.3, "caus_a": 0.07, "caus_cor": (242, 244, 234)},
              # o esfumado das bordas: (força, alcance em px) na esquerda, em cima, na direita e embaixo
              "sombra": {"funda": ((0.06, 3), (0.05, 3), (0.04, 3), (0.04, 3)),
                         "rasa": ((0.04, 3), (0.03, 3), (0.03, 3), (0.03, 3))},
              "degrau": (0.16, 1.6)}


def pastilhas_rel(h, w, lado_px, q, rng, ss=4):
    """O Barlavento visto através da água, relativo (média 1), em (h, w) px com a grade a partir de (0, 0): cada peça
    num tom, o grão fino, as juntas escurecidas e a grade levemente ondulada pela refração."""
    H, W = h * ss, w * ss
    lado = lado_px * ss
    sig, amp = q["onda"]
    desl = []
    for _ in range(2):
        n = cv2.GaussianBlur(rng.standard_normal((h, w)).astype(np.float32), (0, 0), sig)
        desl.append(cv2.resize(n / (n.std() + 1e-6) * amp * ss, (W, H), interpolation=cv2.INTER_LINEAR))
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    yy, xx = yy + desl[0], xx + desl[1]
    i, j = np.floor(yy / lado).astype(np.int32) + 1, np.floor(xx / lado).astype(np.int32) + 1
    tom = np.clip(1 + q["peca_var"] * rng.standard_normal((int(i.max()) + 2, int(j.max()) + 2)), 0.9, 1.1)
    img = tom[np.clip(i, 0, None), np.clip(j, 0, None)].astype(np.float32)
    fy, fx = (yy / lado) % 1, (xx / lado) % 1
    junta = np.minimum(np.minimum(fy, 1 - fy), np.minimum(fx, 1 - fx)) < q["junta"]
    img = np.where(junta, img * q["junta_f"], img)
    g = cv2.GaussianBlur(rng.standard_normal((H, W)).astype(np.float32), (0, 0), 0.6 * ss)
    img = img * (1 + q["grao_a"] * g / (g.std() + 1e-6))
    img = cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)
    return img / img.mean()


def _ruido(rng, h, w, sig):
    n = cv2.GaussianBlur(rng.standard_normal((h, w)).astype(np.float32), (0, 0), sig)
    return n / (n.std() + 1e-6)


def agua_textura(h, w, tom, q, rng):
    """A água das fotos do cliente: o tom com o grão, as manchas largas e as cáusticas finas (BGR float)."""
    grao = _ruido(rng, h, w, q["grao_sig"])
    manchas = _ruido(rng, h, w, q["manchas_sig"])
    linhas = np.exp(-(_ruido(rng, h, w, q["caus_sig"]) / q["caus_larg"]) ** 2)
    quebra = np.clip(_ruido(rng, h, w, q["quebra_sig"]) * 0.9 + q["quebra_b"], 0, 1)
    dens = np.clip(_ruido(rng, h, w, q["dens_sig"]) * q["dens_k"] + q["dens_b"], 0, 1)
    a = (linhas * quebra * dens * q["caus_a"])[..., None]
    base = np.float32(tom)[None, None] * (1 + q["grao_a"] * grao + q["manchas_a"] * manchas)[..., None]
    return base * (1 - a) + np.float32(q["caus_cor"]) * a


def _sombra_bordas(h, w, ret, forcas):
    """1 menos a sombra das 4 bordas do retângulo `ret` (x0, y0, x1, y1 em px), em (h, w)."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    x0, y0, x1, y1 = ret
    d = (xx - x0, yy - y0, x1 - xx, y1 - yy)
    s = np.zeros((h, w), np.float32)
    for (f, alc), di in zip(forcas, d):
        s += f * np.exp(-np.clip(di, 0, None) / alc)
    return np.clip(1 - s, 0.3, 1)


def piscina_ta(Q, img, q=None, com_rotulos=True):
    """A água nova sobre `img`; com `com_rotulos=False`, sem os rótulos de volta (a entrada da IA do 12K: o mesmo
    desenho, porque a semente é fixa, sem o borrão de tirar o texto de cima das pastilhas)."""
    import piscinas_turquesa as PT
    q = q or PISCINA_TA
    cob = agua_mascara(Q)
    agua = cob > 0
    rots = rotulos_na_imagem(Q, img, dentro=agua) if com_rotulos else []
    H, W = agua.shape
    rng = np.random.default_rng(q["semente"])
    funda_t = agua_textura(H, W, q["tom"], q["funda"], rng)
    rasa_t = agua_textura(H, W, q["tom_rasa"], q["rasa"], rng)
    # as partes: a piscina funda, a prainha (abaixo do degrau) e o spa (o banco no anel, o fundo no quadrado do PDF)
    xs0, ys0, xs1, ys1 = [float(v) for v in ret_q(Q, PT.BORDAS["A-Terreo"]["agua"][0])]
    yp = Q.p2q(0, q["prainha_y_pt"])[1]
    sx0, sy0, sx1, sy1 = [float(v) for v in ret_q(Q, q["spa_pt"])]
    yy, xx = np.mgrid[0:H, 0:W]
    na_piscina = (xx >= xs0 - 1) & (xx <= xs1 + 1) & (yy >= ys0 - 1) & (yy <= ys1 + 1)
    no_spa = (xx >= sx0 - 1) & (xx <= sx1 + 1) & (yy >= sy0 - 1) & (yy <= sy1 + 1)
    prainha = na_piscina & (yy >= yp)
    fundo_spa = no_spa & T.F.fechar(np.all(Q.chapada == np.uint8(q["spa_fundo_bgr"]), axis=2), 3)
    ys_, xs_ = np.where(fundo_spa)
    fs = (float(xs_.min()), float(ys_.min()), float(xs_.max() + 1), float(ys_.max() + 1))
    rasa = prainha | (no_spa & ~fundo_spa)
    sombra = np.ones((H, W), np.float32)
    sombra = np.where(na_piscina & ~prainha, _sombra_bordas(H, W, (xs0, ys0, xs1, yp), q["sombra"]["funda"]), sombra)
    sombra = np.where(prainha, _sombra_bordas(H, W, (xs0, yp, xs1, ys1), q["sombra"]["rasa"]), sombra)
    sombra = np.where(no_spa & ~fundo_spa, _sombra_bordas(H, W, (sx0, sy0, sx1, sy1), q["sombra"]["rasa"]), sombra)
    sombra = np.where(fundo_spa, _sombra_bordas(H, W, fs, q["sombra"]["funda"]), sombra)
    # o degrau da prainha: a sombra fina do lado fundo
    f, alc = q["degrau"]
    sombra = np.where(na_piscina & (yy < yp), sombra * (1 - f * np.exp(-np.clip(yp - yy, 0, None) / alc)), sombra)
    # o Barlavento: a grade de cada tanque a partir do canto de cima à esquerda (a piscina e a prainha numa grade só)
    lado = q["peca_cm"] / 100 * Q.px_m
    rel = np.ones((H, W), np.float32)
    for x0, y0, x1, y1 in ((xs0, ys0, xs1, ys1), (sx0, sy0, sx1, sy1)):
        a0, b0 = int(np.floor(x0)) - 1, int(np.floor(y0)) - 1
        a1, b1 = int(np.ceil(x1)) + 2, int(np.ceil(y1)) + 2
        rel[b0:b1, a0:a1] = pastilhas_rel(b1 - b0, a1 - a0, lado, q, rng)
    cf, cr = q["contraste"]["funda"], q["contraste"]["rasa"]
    funda_t = funda_t * (1 + cf * (rel - 1))[..., None]
    rasa_t = rasa_t * (1 + cr * (rel - 1))[..., None]
    novo = np.where(rasa[..., None], rasa_t, funda_t) * sombra[..., None]
    im = img.astype(np.float32)
    out = im * (1 - cob[..., None]) + novo * cob[..., None]
    nomes = []
    for r, al, _, _ in rots:
        out = compor(out, al, cor_rotulo(out, al))
        nomes.append(r[0])
    print(f"    água: turquesa sobre o Barlavento (pastilhas de {q['peca_cm']} cm, {lado:.1f} px, juntas finas): a funda "
          f"(BGR {q['tom']}) e a rasa, prainha e banco do spa (BGR {q['tom_rasa']}), com as pastilhas mais visíveis; "
          f"ondulação e cáusticas sutis; rótulos de volta: {', '.join(nomes)}")
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
    # sob os rótulos (e 2 px em volta), o piso vem da imagem tapada: o rótulo volta inteiro por cima, no alfa dele
    # (compor sobre o rótulo antigo engrossava a borda das letras)
    tt = dilatar(texto > 0.02, 2) & B
    t = tt[y0:y1, x0:x1]
    D = np.where(t[..., None], sub.astype(np.float32), im[y0:y1, x0:x1]) / np.maximum(tom, 1)
    novo = tom * (1 + q["forca"] * (D - 1))
    m = (piso[y0:y1, x0:x1] & ~aresta).astype(np.float32)
    m = cv2.GaussianBlur(m, (0, 0), 0.8) * piso[y0:y1, x0:x1]
    m = np.maximum(m, t.astype(np.float32))
    out = im.copy()
    out[y0:y1, x0:x1] = im[y0:y1, x0:x1] * (1 - m[..., None]) + novo * m[..., None]
    for _, al, claro, _ in rots:
        al = al * tt                                   # só onde o piso foi refeito (fora dele, o rótulo está inteiro)
        if al.max() > 0.02:
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
               "lavabo_camadas": [(0.010, 0.6), (0.022, 5.0)],
               # depois (usuário: "MELHORAR A BANCADA. ELA NÃO TEM ESSA LINHA NA HORIZONTAL ANTES DA CUBA. E ELA DEVERIA
               # IR E FAZER UM CONTORNO EM VOLTA DA CUBA ESCULPIDA"): a bancada é uma peça só, em L (a parte larga da
               # cuba e a estreita de baixo), sem a linha entre elas; a cuba esculpida fica dentro da parte larga, com a
               # borda da bancada em volta (`cuba_folga_pt`: esquerda, cima, direita/parede, baixo), mais escura e com o
               # fundo côncavo (`cuba_tons`), o ralo e a torneira na parede
               "cuba_folga_pt": (2.6, 2.6, 2.0, 2.6), "cuba_raio_pt": 3.2, "cuba_tons": (0.80, 0.93), "ralo_pt": 0.9}


def _danae_fn(semente, mult=1.0):
    return lambda tl: danae(tl.h, tl.w, semente) * mult



def cuba_esculpida(Q, out, c, textura, escurecer, raio_pt=3.0):
    """A cuba esculpida na pedra da bancada: a bacia (`c["bacia"]`, cantos de `raio_pt`) lisa e `escurecer` x o tom da
    pedra, com o fundo côncavo (mais escuro junto às bordas, sobretudo a de cima e a da esquerda), a borda fina, o lábio
    claro embaixo e à direita e o ralo cromado no meio."""
    tl = FA.tela(out, Q, c["cuba"], folga=4)
    G = textura(tl)
    liso = cv2.GaussianBlur(G.astype(np.float32), (0, 0), 1.6)
    b = tl.ret(c["bacia"], raio_pt)
    d = cv2.resize(cv2.distanceTransform(b, cv2.DIST_L2, 5).astype(np.float32) / 8, (tl.w, tl.h),
                   interpolation=cv2.INTER_AREA)
    X, Y = tl.grade()
    x0, y0, x1, y1 = c["bacia"]
    lado = np.clip(((x1 - X) / (x1 - x0) + (y1 - Y) / (y1 - y0)) / 2, 0, 1)        # 1 no alto à esquerda
    prof = (0.84 + 0.16 * (1 - np.exp(-d / 2.4))) * (1 - 0.10 * lado * np.exp(-d / 3.0))
    tl.pintar_img(b, liso * escurecer * prof[..., None])
    labio = b & ~cv2.erode(b, np.ones((5, 5), np.uint8))
    lab = tl.vazia()
    lab[labio > 0] = 255
    ys, xs = np.nonzero(lab)
    if len(ys):
        cxs, cys = tl.pt((x0 + x1) / 2, (y0 + y1) / 2)
        fora = (ys < cys) | (xs < cxs - (xs.max() - xs.min()) * 0.1)
        lab[ys[fora], xs[fora]] = 0
    tl.pintar(lab, tuple(float(v) for v in np.median(G.reshape(-1, 3), axis=0) * 1.18), 0.55)
    tl.contorno(b, 0.35, (34, 44, 58))
    v = tl.vazia()
    cx, cy = tl.pt((x0 + x1) / 2, (y0 + y1) / 2)
    cv2.circle(v, (int(cx), int(cy)), int(1.05 * FA.PT_PX * 8), 255, -1, cv2.LINE_AA)
    tl.pintar(v, FA.CROMO["meio"])
    miolo = tl.vazia()
    cv2.circle(miolo, (int(cx), int(cy)), int(0.45 * FA.PT_PX * 8), 255, -1, cv2.LINE_AA)
    tl.pintar(miolo, FA.CROMO["escuro"])
    tl.contorno(v, 0.3, FA.CROMO["contorno"])
    return tl.gravar()

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
    # (usuário, 10/11: "MELHORAR A REPRESENTAÇÃO DESSA CUBA"): a cuba esculpida na própria bancada, sem o aro de outro
    # tom: a bacia de cantos redondos, lisa (a pedra sem os pontos claros), um tom abaixo, com o fundo côncavo, a borda
    # fina, o lábio claro embaixo e o ralo cromado
    out = cuba_esculpida(Q, out, lv, tab(1.0, lv["semente"] + 1), q["cuba_esc"])
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
    # lavabo: a bancada inteira em L, na cor da cuba antiga, com a cuba esculpida dentro (sem a linha entre as partes)
    x0, y0, x1, y1 = (int(round(v)) for v in ret_q(Q, q["lavabo_cuba_pt"]))
    cuba = img[y0 + 3:y1 - 3, x0 + 3:x1 - 3].astype(np.float32)
    tom = np.median(cuba.reshape(-1, 3), axis=0)
    c, l_ = q["lavabo_cuba_pt"], q["lavabo_lateral_pt"]
    caixa = (min(c[0], l_[0]), c[1], max(c[2], l_[2]), l_[3])
    tl = FA.tela(out, Q, caixa, folga=4)
    m = np.maximum(tl.ret(c), tl.ret(l_))
    FA.sombra_q(tl, m, forca=T.LAVABO["sombra"], dist=1.3, sigma=1.3)
    pedra = danae(tl.h, tl.w, q["semente"] + 7, dict(DANAE, tom=tuple(float(v) for v in tom), camadas=q["lavabo_camadas"]))
    tl.pintar_img(m, pedra)
    k = max(1, int(round(T.LAVABO["larg_px"] * 8)))
    borda = m & ~cv2.erode(m, np.ones((k, k), np.uint8))
    tl.pintar_img(borda, tl.reg * T.LAVABO["borda"])
    fe, fc, fd, fb = q["cuba_folga_pt"]
    bac = (c[0] + fe, c[1] + fc, c[2] - fd, c[3] - fb)
    mb = tl.ret(bac, q["cuba_raio_pt"])
    dist = cv2.distanceTransform((mb > 0).astype(np.uint8), cv2.DIST_L2, 5).astype(np.float32)
    dist = cv2.resize(dist, (tl.w, tl.h), interpolation=cv2.INTER_AREA) / 8.0       # em px do quadro
    t0, t1 = q["cuba_tons"]
    fundo = t0 + (t1 - t0) * (1 - np.exp(-dist / 2.5))                             # côncavo: escuro na borda
    tl.pintar_img(mb, pedra * fundo[..., None])
    tl.contorno(mb, 0.35, tuple(float(v) * 0.62 for v in tom))
    cx, cy = (bac[0] + bac[2]) / 2, (bac[1] + bac[3]) / 2
    ralo = tl.vazia()
    px_, py_ = tl.pt(cx - 0.5, cy)
    cv2.circle(ralo, (int(px_), int(py_)), int(q["ralo_pt"] * FA.PT_PX * 8), 255, -1, cv2.LINE_AA)
    tl.pintar(ralo, (150, 152, 156))
    tl.contorno(ralo, 0.25, (95, 97, 100))
    out = tl.gravar()
    out = FA.torneira(Q, out, (c[2] - fd - 3.2, cy - 0.45, c[2] - 0.4, cy + 0.45), (c[2] - 1.0, cy, 1.1))
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
# - a da entrada (cliente: "Representar uma soleira na entrada igual a casa C"): no vão da porta pivotante, de batente
#   a batente (`entrada_px`; usuário: "A SOLEIRA VAI DE FORA A FORA"), a própria faixa da soleira da entrada da Casa C
#   (`casa_c`, da final dela): a pedra clara e lisa, com a face fina de cada lado; a folha da porta fica por cima;
# - a da sala para o escritório (cliente: "Não tem soleira entre a sala e o escritório"): a faixa clara no vão
#   (`escritorio_px`) sai; o travertino atravessa o vão.
# Depois (usuário: "CORRIGIR BATENTE E A PEDRA DO HALL EXTERNO. ELA É RENTE A PAREDE", com o recorte do PDF): os dois
# batentes da porta pivotante no desenho do PDF (de 2440 a 2457 px; o de cima da parede até 647, o de baixo de 843 até a
# parede), na cor das paredes, como os da entrada da Casa C (`batentes_px`); a soleira de batente a batente na largura
# deles; e a pedra (o Bege Bahia) do hall externo até a parede de baixo (`hall_px`: a faixa de grama entre a pedra e a
# parede sai; a pedra continua, espelhada da faixa de cima).
SOLEIRAS_TA = {"entrada_px": (2441, 647, 2457, 843), "folha_y": (681, 686),
               "casa_c": "_texturas/originais/soleira_entrada_casac.png",
               "batentes_px": [(2441, 609, 2457, 647), (2441, 843, 2457, 879)], "parede": (79, 79, 79),
               "hall_px": (2458, 850, 2605, 890),
               "escritorio_px": (2343, 529, 2359, 589), "semente": 3140}


def _pedra_ate_parede(out, ret, parede):
    """Em cada coluna de `ret`, a pedra clara desce até a parede cinza: os px entre o fim da pedra e o topo da parede
    recebem a pedra espelhada de cima."""
    x0, y0, x1, y1 = ret
    n = 0
    for x in range(x0, x1):
        col = out[y0:y1, x].astype(np.float32)
        lum = col.mean(axis=1)
        cin = (np.abs(col - np.float32(parede)).max(axis=1) < 14).astype(np.uint8)
        corrida = np.convolve(cin, np.ones(5, np.uint8), mode="valid") == 5      # a parede: 5 px cinza seguidos
        iw = np.where(corrida)[0]
        if not len(iw):
            continue
        yw = y0 + int(iw[0])
        ip = np.where(lum[:iw[0]] > 170)[0]
        if not len(ip):
            continue
        yf = y0 + int(ip[-1]) - 2                     # sem a luz da beirada antiga
        for i, y in enumerate(range(yf + 1, yw)):
            out[y, x] = out[max(yf - i, 0), x]
            n += 1
    return n


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
    # a da entrada (cliente: "Representar uma soleira na entrada igual a casa C"): a faixa da soleira da entrada da
    # Casa C (`casa_c`, 13 px de face a face: a face de 1 px do lado de dentro, a pedra lisa clara, a face de 2 px do
    # lado de fora), na mesma largura, esticada no comprimento do vão
    # (usuário: "A SOLEIRA VAI DE FORA A FORA. NÃO PARA NA PORTA"): de batente a batente, passando sob a folha da porta
    # pivotante, que fica por cima (`folha_y`, as linhas da barra cinza dela)
    x0, y0, x1, y1 = q["entrada_px"]
    c = cv2.imread(str(RAIZ / q["casa_c"]))
    out[y0:y1, x0:x1] = cv2.resize(c, (x1 - x0, y1 - y0), interpolation=cv2.INTER_LINEAR)
    f0, f1 = q["folha_y"]
    out[f0:f1, x0:x1] = img[f0:f1, x0:x1]
    # os batentes na cor das paredes, como na entrada da Casa C; a pedra do hall externo rente à parede de baixo
    for b0, c0, b1, c1 in q["batentes_px"]:
        out[c0:c1, b0:b1] = np.uint8(q["parede"])
    n = _pedra_ate_parede(out, q["hall_px"], q["parede"])
    print(f"    soleiras: sem a da sala para o escritório ({int(zona.sum())} px de travertino refeito); a da entrada no vão "
          f"da porta pivotante, como a da Casa C, entre os batentes na cor da parede; o hall externo rente à parede "
          f"({n} px de pedra)")
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
               # o guarda-corpo de vidro (usuário: "FALTOU A BOA REPRESENTAÇÃO DO GUARDA CORPO NO CONTORNO"): as lâminas
               # brancas de 1,1 pt da ARQ_ELEMENTOS FIXOS do PDF, em todo o contorno da escada (em cima, na direita e
               # embaixo) e em volta da floreira do meio, emendadas onde a linha de corte as interrompe; no desenho da
               # regra [22/10] (o da Casa B): o vidro claro, as duas faces em linha fina, o brilho no meio e a sombra
               # curta, com 2,4 px no mínimo e as pontas passando `ponta_px` para as quinas fecharem.
               "guarda_corpo_ret_pt": [(2021.2, 1097.1, 2240.1, 1098.3), (2238.9, 1097.1, 2240.1, 1251.3),
                                       (2019.5, 1250.2, 2240.1, 1251.3), (2021.2, 1159.5, 2177.7, 1160.6),
                                       (2176.6, 1159.5, 2177.7, 1189.0), (2019.5, 1187.8, 2177.7, 1189.0)],
               "vidro": {"vidro": (226, 219, 206), "alfa": 0.95, "contorno": (96, 100, 104), "larg_min_px": 2.4,
                         "linha_px": 0.6, "brilho": 0.5, "sombra": 0.18, "ponta_px": 0.6}},
    "caracol": {"texto": ("SOBE PARA O", "1º PAVIMENTO"), "txt_px": (1916.0, 1604.0), "alinhar": "direita", "tom": (166, 186, 208),
                "tons": (0.90, 1.0), "linha": (96, 96, 98), "linha_px": 0.8, "traco_pt": (4.0, 3.0), "tri": (13.0, 15.0),
                # (11/11, "TOM MAIS CLARO PARA PARTE DA ESCADA QUE PERTENCE AO 1º PAVIMENTO"): os degraus inteiros acima
                # do corte (do `degrau_1pav` em diante, os de linhas tracejadas) clareados para o véu claro
                "degrau_1pav": 9, "claro_1pav": ((236, 236, 234), 0.45)},
    "cor_texto": (45, 45, 45)}



def vidro_laminas(Q, img, rets_pt, q):
    """As lâminas de vidro do guarda-corpo (regra [22/10], o desenho da Casa B, `final3840_casab.guarda_corpo`): cada
    retângulo do PDF (pt) como o vidro claro, as duas faces em linha fina, o brilho no meio e a sombra curta."""
    ss = 8
    out = img.astype(np.float32)
    for r in rets_pt:
        (x0, y0), (x1, y1) = Q.p2q(r[0], r[1]), Q.p2q(r[2], r[3])
        deitado = x1 - x0 > y1 - y0
        if deitado and y1 - y0 < q["larg_min_px"]:
            c_ = (y0 + y1) / 2
            y0, y1 = c_ - q["larg_min_px"] / 2, c_ + q["larg_min_px"] / 2
        if not deitado and x1 - x0 < q["larg_min_px"]:
            c_ = (x0 + x1) / 2
            x0, x1 = c_ - q["larg_min_px"] / 2, c_ + q["larg_min_px"] / 2
        if deitado:
            x0, x1 = x0 - q["ponta_px"], x1 + q["ponta_px"]
        else:
            y0, y1 = y0 - q["ponta_px"], y1 + q["ponta_px"]
        X0, Y0, X1, Y1 = int(x0) - 3, int(y0) - 3, int(np.ceil(x1)) + 4, int(np.ceil(y1)) + 4
        w, h = X1 - X0, Y1 - Y0
        m = np.zeros((h * ss, w * ss), np.uint8)
        a0, b0, a1, b1 = [int(round(v * ss)) for v in (x0 - X0, y0 - Y0, x1 - X0, y1 - Y0)]
        cv2.rectangle(m, (a0, b0), (a1 - 1, b1 - 1), 255, -1)
        lt = max(1, int(round(q["linha_px"] * ss)))
        bordas = np.zeros_like(m)
        meio = np.zeros_like(m)
        if deitado:
            bordas[b0:b0 + lt, a0:a1] = 255
            bordas[b1 - lt:b1, a0:a1] = 255
            c_ = (b0 + b1) // 2
            meio[c_ - lt // 2:c_ + lt // 2 + 1, a0 + lt:a1 - lt] = 255
        else:
            bordas[b0:b1, a0:a0 + lt] = 255
            bordas[b0:b1, a1 - lt:a1] = 255
            c_ = (a0 + a1) // 2
            meio[b0 + lt:b1 - lt, c_ - lt // 2:c_ + lt // 2 + 1] = 255

        def reduzir(x):
            return cv2.resize(x.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)
        av, ab, am = reduzir(m), reduzir(bordas), reduzir(meio)
        reg = out[Y0:Y1, X0:X1]
        sb = cv2.GaussianBlur(cv2.warpAffine(av, np.float32([[1, 0, -0.7], [0, 1, 0.7]]), (w, h)), (0, 0), 0.5)
        reg *= (1 - q["sombra"] * sb * (1 - av))[..., None]
        al = av[..., None] * q["alfa"]
        reg[:] = reg * (1 - al) + np.float32(q["vidro"]) * al
        reg[:] = reg * (1 - ab[..., None]) + np.float32(q["contorno"]) * ab[..., None]
        am = am[..., None] * q["brilho"]
        reg[:] = reg * (1 - am) + 250 * am
    return out

def _texto_escada(out, linhas, x, y, alinhar, cor):
    if not ANOTAR["sim"]:
        return out.astype(np.float32)
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
    if q.get("degrau_1pav") is not None:
        veu, a_v = q["claro_1pav"]
        a_1p = red(degrau & (k >= q["degrau_1pav"]))[..., None] * a_v
        tl.reg = tl.reg * (1 - a_1p) + np.float32(veu) * a_1p
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
    # o guarda-corpo da escada do jardim: as lâminas de vidro do PDF no contorno
    j = q["jardim"]
    out = vidro_laminas(Q, out, j["guarda_corpo_ret_pt"], j["vidro"])
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
# Nos dois vazios pequenos (a claraboia do lavabo e o shaft), o X antigo, curto e inclinado, não sai inteiro no passo 1
# (a faixa vizinha cai no outro braço do X ou na moldura; no shaft, o rótulo protegia os traços junto dele): sem o
# rótulo, o que sobra dentro da caixa (`caixas_px`, fora das paredes do PDF), neutro e bem mais escuro ou mais claro
# que o piso de perto (a mediana de `mediana_px`), sai por inpaint. O X fino volta no passo 12.
SHAFT_TA = {"caixas_px": [(2252, 355, 2350, 391), (2350, 1112, 2390, 1212)], "escuro": 18, "claro": 16, "croma": 22,
            "mediana_px": 15, "margem_px": 8}


def _restos_caixa(Q, img, caixa, q):
    x0, y0, x1, y1 = caixa
    m = q["margem_px"]
    X0, Y0, X1, Y1 = x0 - m, y0 - m, x1 + m, y1 + m
    sub = img[Y0:Y1, X0:X1]
    f = sub.astype(np.float32)
    lum, croma = f.mean(axis=2), f.max(axis=2) - f.min(axis=2)
    med = cv2.medianBlur(sub, q["mediana_px"]).astype(np.float32).mean(axis=2)
    par = dilatar(FA.paredes_pdf(Q) > 0.05, 2)[Y0:Y1, X0:X1]
    dentro = np.zeros(lum.shape, bool)
    dentro[m:m + y1 - y0, m:m + x1 - x0] = True
    livre = dentro & ~par
    sujo = livre & (croma < q["croma"]) & ((lum < med - q["escuro"]) | (lum > med + q["claro"]))
    sujo = dilatar(sujo, 1) & livre
    out = img.copy()
    if sujo.any():
        out[Y0:Y1, X0:X1] = cv2.inpaint(sub, (sujo * 255).astype(np.uint8), 3, cv2.INPAINT_TELEA)
    return out, int(sujo.sum())


def shaft_ta(Q, img, q=None):
    q = q or SHAFT_TA
    out = img.copy()
    rots = [a for a in rotulos_na_imagem(Q, img) if a[0][0] == "SHAFT"]
    for _, al, _, _ in rots:
        m = (dilatar(al > 0.02, 1) * 255).astype(np.uint8)
        out = cv2.inpaint(out, m, 3, cv2.INPAINT_TELEA)
    n = 0
    for caixa in q["caixas_px"]:
        out, k = _restos_caixa(Q, out, caixa, q)
        n += k
    print(f"    shaft: {'sem o nome SHAFT' if rots else 'o rótulo SHAFT não foi achado'}; os restos do X antigo na "
          f"claraboia e no shaft ({n} px)")
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
                          (2348, 1110, 2392, 1214), (2540, 884, 2770, 908)], "vazio_esquerda_pt": 1315.4, "folga_rotulo": 6,
            "pontos_px": 18, "pontos_dif": 12, "pontos_area": 10}


def _pontos_cantos(Q, img, q):
    lum = img.astype(np.float32).mean(axis=2)
    med = cv2.medianBlur(img, 9).astype(np.float32).mean(axis=2)
    cantos = np.zeros(lum.shape, np.uint8)
    for p0, p1, _, _ in _retas_tracejadas(Q, TRACEJADOS_TA):
        if _orientacao(p0, p1).startswith("d"):
            for c in (p0, p1):
                cv2.circle(cantos, (int(round(c[0])), int(round(c[1]))), q["pontos_px"], 1, -1)
    escuro = cantos.astype(bool) & (lum < med - q["pontos_dif"]) & ~(FA.paredes_pdf(Q) > 0.05) & ~moveis_pdf(Q)
    n, lab, st, _ = cv2.connectedComponentsWithStats(escuro.astype(np.uint8), connectivity=8)
    pts = np.isin(lab, [i for i in range(1, n) if st[i, 4] <= q["pontos_area"]])
    if not pts.any():
        return img
    return cv2.inpaint(img, (dilatar(pts, 1) * 255).astype(np.uint8), 3, cv2.INPAINT_TELEA)


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
    # os pontinhos escuros que sobraram nas pontas dos X (manchas de até `pontos_area` px, bem mais escuras que o piso)
    img = _pontos_cantos(Q, img, q)
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
# 14. Os contornos e os acertos pedidos depois da rodada de 10/11 (usuário, com recortes da planta):
# - carro: "CORRIGIR CONTORNO DO CARRO E O ERRO NA GARAGEM, NA PARTE DE BAIXO TEM UM DENTE QUE NÃO EXISTE": o 3º carro
#   ficou com a borda direita serrilhada e um anel do granito antigo em volta, que descia até a pedra portuguesa (o
#   dente); os carros são iguais, então o 3º é o 2º com o piso em volta (`carro`: o bloco do 2º, deslocado `dx`, com as
#   bordas fundidas em `funde_px`; a faixa de cima, sem o rótulo GARAGEM, vem do 1º);
# - pedras: "CORRIGIR OS ERROS NAS PEDRAS": a 5ª pedra do acesso subia 5 px e tinha a direita serrilhada (ela é a 1ª,
#   que tem a mesma largura, com a grama em volta); a 4ª tinha um filete branco na direita, onde passava o tracejado
#   (a pedra espelhada da coluna ao lado);
# - acesso: "CORRIGIR CONTORNO DO ACESSO À GARAGEM DESDE O INÍCIO E O MURO (NA PARTE DE BAIXO)": no início (a direita
#   do lote) a pedra portuguesa parava 3 px antes da grama e a borda de cima tinha um dente; a pedra vai até a borda do
#   lote, com as bordas de cima e de baixo continuando as curvas; no muro de baixo, a cunha cinza entre a curva da pista
#   e o muro vira grama, o muro fica inteiro (sem os pontos brancos e sem a pista entrando nele) e a ponta direita
#   fecha reta na borda do lote;
# - faixa de baixo: "REMOVER OS TRACEJADOS E CORRIGIR CONTORNOS": o tracejado branco na borda do gramado entre a área de
#   serviço descoberta e a garagem sai; os pontinhos escuros nas pontas dos X e dos portões saem;
# - deck e escada: "CORRIGIR CONTORNO DA ESCADA E DECK (SE HOUVER)": o deck descia 4 px abaixo da escada (no PDF as
#   duas acabam juntas): a borda de baixo do deck sobe até a da escada; a faixa rosada entre a escada e o guarda-corpo
#   do terraço (branca no PDF) vira grama;
# - guarda-corpos: "AQUI TEM UM GUARDA CORPO" (a borda de cima do terraço, com o recorte do PDF): pela regra [22/10]
#   (todo guarda-corpo do PDF em vidro), todas as lâminas da ARQ_ELEMENTOS FIXOS do terraço: a de cima, a da esquerda
#   (junto à escada do Subsolo e ao gramado), e as de baixo;
# - janela: "FALTOU REPRESENTAR A JANELA AQUI": a janela da parede de cima da sala de estar (o vão do PDF): o peitoril
#   claro com o vidro no meio, no desenho dos vidros;
# - lavabo: "MELHORE O RÓTULO E CENTRALIZE-O TAMBÉM. O RÓTULO DA CLARABOIA NÃO DÁ PARA LER DIREITO": LAVABO no corpo
#   dos outros rótulos, no centro do piso livre (entre a parede e a bancada, abaixo da claraboia); PROJ. CLARABOIA no
#   mesmo corpo, logo abaixo da projeção, no centro do lavabo; depois (usuário, 10/11: "APENAS 'CLARABOIA'", porque
#   numa linha o PROJ. CLARABOIA encostava nas duas paredes do lavabo): só CLARABOIA (`quebra` de uma linha só);
# - paredes: "O TOM DAS PAREDES PRECISA FICAR UM CINZA MAIS ESCURO": as paredes do PDF, os batentes e os muros do lote,
#   do cinza 79 para `parede_nova` (as bordas antisserrilhadas na mesma proporção).
CONTORNOS_TA = {
    "carro": {"fonte_px": (2354, 1341, 2516, 1649), "dx": 169, "topo_px": (2354, 1324, 2516, 1341), "dx_topo": 335,
              "funde_px": 6},
    "pedras": {"fonte_px": (2612, 596, 2777, 871), "destino_x": 3269, "pedra4_px": (3247, 600, 3264, 871),
               "pedra4_fonte_x": 3079},
    # (11/11, "CORRIGIR ESSA FALHA" nas duas bordas da curva) as bordas de cima e de baixo da pista são ajustadas pela
    # parábola das bordas reais de `x_fit_topo`/`x_fit_base` (fora do dente da ponta) e refeitas de `x_ini` até a borda
    # do lote; a pedra nova vem da mesma coluna, mais para dentro da pista (antes vinha de 18 px à esquerda, e a grama
    # da coluna de lá entrava na borda de cima: o degrau em x 3377), e a grama nova, de mais para fora
    "acesso": {"x_borda": 3434, "x_fit_topo": (3300, 3413), "x_fit_base": (3300, 3429), "x_ini": 3340,
               "y_px": (1250, 1760), "busca": 40},
    "muro": {"cunha_px": (3020, 1890, 3130, 1945), "linha_topo": 1924, "modelo_x": 3000, "grama_dx": 110,
             "ponta_px": (3416, 1890, 3435, 1950), "modelo_ponta_x": 3400},
    "faixa": {"tracejado_px": (1912, 1636, 2172, 1649), "pontos_px": (1690, 1636, 1930, 1700), "pontos_dif": 28,
              "pontos_area": 30},
    "deck": {"x_px": (722, 904), "y_px": (1118, 1150), "base_escada": 1131, "faixa_px": (1084, 1056, 1097, 1132)},
    "guarda_corpo_pt": [(907.2, 547.2, 1389.1, 548.6), (920.8, 1233.2, 1156.7, 1234.3),
                        (920.8, 1233.2, 921.9, 1784.2), (920.8, 1783.1, 1037.6, 1784.2)],
    "janela": {"vao_px": (1884, 359, 1947, 372), "peitoril": (214, 214, 212), "vidro_pt": (1668.9, 572.1, 1727.2, 575.0),
               "batentes_px": [(1882, 359, 1885, 372), (1946, 359, 1949, 372)]},
    "lavabo": {"caixa_px": (2252, 350, 2352, 520), "lavabo_centro": (2285.5, 440.0), "claraboia_centro": (2301.5, 401.0),
               "lavabo": {"nome": "LAVABO", "pdf": [2053.0685, 635.3293]},
               "claraboia": {"nome": "PROJ. CLARABOIA", "pdf": [2053.5996, 600.1947], "texto": ["CLARABOIA"]},
               "padrao": {"nome": "ESCRITÓRIO", "pdf": [2225.7157, 708.6874]}, "semente": 3170},
    # "LIMPA ESSE ERRO AO LADO DA PLANTA": o resto do desenho branco da planta do PDF entre o vidro e a planta
    "residuos_px": [(1876, 1073, 1888, 1093)],
    # os dois resíduos que sobraram (achados na conferência do 12K; usuário, 10/11: "PODE LIMPAR OS DOIS RESÍDUOS
    # TAMBÉM"): o traço escuro de 2 px na ponta direita da pedra do hall externo, colado à parede de baixo (refeito pela
    # pedra das colunas dos lados, linha a linha), e a mancha clara no granito logo abaixo da ponta da parede atrás da
    # porta da área de serviço, à direita da folha (refeita pelo granito de `fonte_dy` px abaixo)
    "residuos_finos": [{"px": (2598, 867, 2600, 879), "modo": "lados"},
                       {"px": (2043, 1459, 2050, 1462), "modo": "abaixo", "fonte_dy": 6}],
    # "MELHORAR A REPRESENTAÇÃO DO MARMORE BEGE BAHIA ENTRE OS QUADRADOS": nas faixas das vigas do pergolado (entre as
    # duas linhas tracejadas de cada viga), o Bege Bahia de dentro dos quadrados, trecho a trecho (`copiar_textura`)
    "pergolado": {"caixa_px": (1205, 865, 1530, 1222), "faixa_max_px": 18, "trecho": 14, "busca": 140},
    # "MELHORAR A REPRESENTAÇÃO DA PAREDE ATRÁS DA PORTA DA ÁREA DE SERVIÇO" (a porta para a cozinha, aberta junto à
    # parede): entre a parede e a folha, o granito limpo (sem a linha clara e sem a sombra pontilhada embaixo da folha,
    # o granito de `fonte_dy` px abaixo); a folha nítida no retângulo do PDF (o cinza claro com a face fina) e a sombra
    # curta e lisa
    "porta_servico": {"x_px": (1984, 2043), "limpar_y": [(1453, 1460), (1464, 1470)], "fonte_dy": 14,
                      "folha_px": (1987.0, 1460.5, 2042.0, 1464.5), "folha": (222, 224, 226), "face": (92, 94, 97)},
    # "NESSAS PIAS: ÁREA GOURMET, COZINHA PRECISAMOS REPRESENTAR O RALO DE CADA UMA DELAS": os ralos do PDF (ARQ_LOUÇAS E
    # METAIS, os círculos pequenos no fundo das cubas), em cromado com o anel fino e o miolo escuro (pt: centro e raio)
    # (11/11, "ADICIONAR RALO EM CADA UMA DAS PIAS DA COZINHA" / "ADICIONAR RALO NA PIA DO GOURMET"): os ralos do PDF,
    # de 1 pt, ficavam embaixo da base da torneira e não apareciam; cada ralo tem 5 px (~9 cm) e fica no eixo da bica,
    # logo depois da ponta dela, no fundo da cuba (px: centro e raio)
    "ralos_px": [(1722.3, 1417.5, 2.6), (2126.5, 1344.2, 2.6), (2127.0, 1392.3, 2.6)],
    # escritório (usuário: "MELHORE A REPRESENTAÇÃO DESSAS MESAS REDONDAS LATERAIS, PONHA UM TOM O SOBRETOM NELAS. E ALTERE
    # O TOM DO ARMARIO PARA O TOM JÁ DEFINIDO. E MELHORE A REPRESENTAÇÃO DA PORTA DO ESCRITÓRIO"): o aparador no tom
    # padrão dos armários (regra de 10/11: RGB 208, 178, 156, quase liso, o do armário junto ao lavabo); as duas mesinhas
    # redondas do PDF, a de baixo no sobretom claro e a de cima no tom de nogueira, com a sombra de uma sobre a outra; a
    # folha da porta (aberta junto à parede de baixo, como no PDF) nítida e presa ao batente
    "escritorio": {"aparador_pt": (2182.8, 766.0, 2250.8, 793.3), "armario": (156, 178, 208),
                   "mesas_pt": [((2270.6, 771.8, 8.5), (130, 160, 194)), ((2278.7, 761.5, 8.5), (74, 100, 132))],
                   "porta_limpar_px": (2356, 582, 2412, 587), "porta_fonte_dy": -9,
                   "folha_px": (2355.0, 586.4, 2408.0, 589.4), "folha": (222, 224, 226), "face": (92, 94, 97)},
    # o rasgo branco na viga entre o hall externo e o jardim (no PDF, um vazio com X tracejado; usuário: "Vazio com X
    # fino"): o branco no tom do piso do hall (o Bege Bahia), e o X fino e claro dos vazios (`FINOS_TA`)
    "vazio_viga": {"caixa_px": (2540, 884, 2770, 908), "fonte_px": (2470, 815, 2590, 830)},
    "parede": 79, "parede_nova": 52, "parede_tol": 12,
    "muros_px": [(262, 130, 3450, 175), (262, 1915, 3450, 1952), (262, 130, 292, 1952)],
}


def _fundir_bloco(out, src, x0, y0, funde):
    """Cola `src` em (x0, y0) com as bordas fundidas em `funde` px."""
    h, w = src.shape[:2]
    a = np.ones((h, w), np.float32)
    if funde > 0:
        r = np.minimum.reduce([np.arange(w)[None, :].repeat(h, 0), np.arange(w)[::-1][None, :].repeat(h, 0)])
        a = np.clip((r + 1) / (funde + 1), 0, 1).astype(np.float32)
    reg = out[y0:y0 + h, x0:x0 + w].astype(np.float32)
    out[y0:y0 + h, x0:x0 + w] = np.round(reg * (1 - a[..., None]) + src.astype(np.float32) * a[..., None])
    return out


def _carro(out, q):
    a, b, c, d = q["fonte_px"]
    bloco = out[b:d, a:c].copy()
    t0, t1, t2, t3 = q["topo_px"]
    topo = out[t1:t3, t0 - q["dx_topo"] + q["dx"]:t2 - q["dx_topo"] + q["dx"]].copy()
    out = _fundir_bloco(out, bloco, a + q["dx"], b, q["funde_px"])
    out = _fundir_bloco(out, topo, t0 + q["dx"], t1, q["funde_px"])
    return out


def _pedras(out, q):
    a, b, c, d = q["fonte_px"]
    out[b:d, q["destino_x"]:q["destino_x"] + (c - a)] = out[b:d, a:c].copy()
    # a ponta direita da 4ª pedra (onde passava o tracejado) é a ponta direita da 3ª, com a borda dela
    x0, y0, x1, y1 = q["pedra4_px"]
    fx = q["pedra4_fonte_x"]
    out[y0:y1, x0:x1] = out[y0:y1, fx:fx + (x1 - x0)].copy()
    return out


def _bordas_pista(out, x0, x1, y0, y1):
    """As bordas de cima e de baixo da pista (o 1º e o último px claros de cada coluna)."""
    cols, tops, bots = [], [], []
    for x in range(x0, x1):
        col = out[y0:y1, x].astype(np.float32)
        p = np.where(col.mean(axis=1) > 150)[0]
        if len(p) > 20:
            cols.append(x)
            tops.append(y0 + p[0])
            bots.append(y0 + p[-1])
    return np.array(cols, np.float32), np.array(tops, np.float32), np.array(bots, np.float32)


def _acesso(out, q):
    a = q["acesso"]
    y0, y1 = a["y_px"]
    img = out.copy()
    xs, tops, _ = _bordas_pista(img, *a["x_fit_topo"], y0, y1)
    pt = np.polyfit(xs, tops, 2)
    xs, _, bots = _bordas_pista(img, *a["x_fit_base"], y0, y1)
    pb = np.polyfit(xs, bots, 2)
    lum = img.astype(np.float32).mean(axis=2)
    viz = lambda m: m & np.roll(m, 1, 0) & np.roll(m, -1, 0) & np.roll(m, 1, 1) & np.roll(m, -1, 1)
    pista_n, grama_n = viz(lum > 150), viz(lum < 120)   # sem a franja antisserrilhada
    H = out.shape[0]

    def fonte(m, x, y, passo):
        for dx in (0, 4, 8, 12, 16, 20):
            for k in range(0, a["busca"]):
                yy = int(np.clip(y + passo * k, 0, H - 1))
                if m[yy, x - dx]:
                    return img[yy, x - dx].astype(np.float32)
        return None

    for x in range(a["x_ini"], a["x_borda"] + 1):
        yt, yb = np.polyval(pt, x), np.polyval(pb, x)
        meio = (yt + yb) / 2
        for y in range(int(yt) - 10, int(yb) + 11):
            al = float(np.clip(min(y - yt, yb - y) + 0.5, 0, 1))   # 1 dentro da pista, meia transição de 1 px
            if al >= 1 and pista_n[y, x] or al <= 0 and grama_n[y, x]:
                continue
            pe = fonte(pista_n, x, y, 1 if y < meio else -1) if al > 0 else None
            gr = fonte(grama_n, x, y, -1 if y < meio else 1) if al < 1 else None
            if al > 0 and pe is None or al < 1 and gr is None:
                continue
            v = (pe * al if al > 0 else 0) + (gr * (1 - al) if al < 1 else 0)
            out[y, x] = np.round(v)
    # o muro de baixo: a cunha cinza vira grama, o muro inteiro e a ponta reta
    m = q["muro"]
    x0, ya, x1, yb2 = m["cunha_px"]
    mod = img[m["linha_topo"]:yb2, m["modelo_x"]].copy()
    for x in range(x0, x1):
        col = out[ya:m["linha_topo"], x].astype(np.float32)
        cinza = (col.max(axis=1) - col.min(axis=1) < 14) & (col.mean(axis=1) < 130)
        gx = min(x + m["grama_dx"], out.shape[1] - 1)
        for i in np.where(cinza)[0]:
            out[ya + i, x] = img[ya + i, gx]
        out[m["linha_topo"]:yb2, x] = mod
    x0, ya, x1, yb2 = m["ponta_px"]
    modp = img[ya:yb2, m["modelo_ponta_x"]].copy()
    for x in range(x0, x1):
        topo_muro = m["linha_topo"] - 1
        out[topo_muro:yb2, x] = modp[topo_muro - ya:]
    return out


def _faixa(Q, out, q):
    x0, y0, x1, y1 = q["tracejado_px"]
    reg = out[y0:y1, x0:x1].astype(np.float32)
    branco = (reg.mean(axis=2) > 185) & (reg.max(axis=2) - reg.min(axis=2) < 30)
    m = np.zeros(out.shape[:2], np.uint8)
    m[y0:y1, x0:x1] = dilatar(branco, 1)
    out = cv2.inpaint(out, m * 255, 2, cv2.INPAINT_TELEA)
    x0, y0, x1, y1 = q["pontos_px"]
    reg = out[y0:y1, x0:x1]
    lum = reg.astype(np.float32).mean(axis=2)
    med = cv2.medianBlur(reg, 9).astype(np.float32).mean(axis=2)
    escuro = (lum < med - q["pontos_dif"]).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(escuro, connectivity=8)
    pts = np.isin(lab, [i for i in range(1, n) if st[i, 4] <= q["pontos_area"]])
    pts &= ~(FA.paredes_pdf(Q)[y0:y1, x0:x1] > 0.05)
    m = np.zeros(out.shape[:2], np.uint8)
    m[y0:y1, x0:x1] = dilatar(pts, 1)
    return cv2.inpaint(out, m * 255, 3, cv2.INPAINT_TELEA)


def _deck(out, q):
    x0, x1 = q["x_px"]
    y0, y1 = q["y_px"]
    img = out.copy()
    alvo = q["base_escada"]
    for x in range(x0, x1):
        col = img[y0:y1, x].astype(np.float32)
        verde = (col[:, 1] > col[:, 0] + 8) & (col.mean(axis=1) < 130)
        g = np.where(verde)[0]
        if not len(g):
            continue
        base = y0 + int(g[0]) - 1                      # o último px do deck
        dy = base - alvo
        if dy <= 0:
            continue
        for y in range(alvo - 6, alvo + 1):            # a borda (com a sombra) sobe dy px
            out[y, x] = img[y + dy, x]
        for y in range(alvo + 1, base + 1):            # a grama de baixo sobe junto
            out[y, x] = img[min(y + dy + 6, out.shape[0] - 1), x]
    fx0, fy0, fx1, fy1 = q["faixa_px"]
    for x in range(fx0, fx1):
        for y in range(fy0, fy1):
            out[y, x] = img[min(y + (fy1 - fy0) + 4, out.shape[0] - 1), x]
    return out


def _janela(Q, out, q, vidro):
    x0, y0, x1, y1 = q["vao_px"]
    out[y0:y1, x0:x1] = np.uint8(q["peitoril"])
    for a, b, c, d in q["batentes_px"]:
        out[b:d, a:c] = np.uint8((79, 79, 79))
    return np.clip(np.round(vidro_laminas(Q, out, [q["vidro_pt"]], vidro)), 0, 255).astype(np.uint8)


def _alfa_rot(Q, b, opc, dx, dy, forma):
    import ampliacao_12k_terreo_casaa as Z
    return Z.alfa_rotulo(Q, dict(b, opc=opc, desvio=[dx, dy]), forma)


def _altura_maiuscula(al):
    ys = np.nonzero(al.max(axis=1) > 0.4)[0]
    return ys.max() - ys.min() + 1 if len(ys) else 0


def _lavabo_rotulos(Q, out, q):
    import pedidos_terreo_casaa_2910 as P
    forma = out.shape[:2]
    x0, y0, x1, y1 = q["caixa_px"]
    dentro = np.zeros(forma, bool)
    dentro[y0:y1, x0:x1] = True
    rots = [r for r in rotulos_na_imagem(Q, out, dentro=dentro) if r[0][0] in ("LAVABO", "PROJ. CLARABOIA")]
    zona = np.zeros(forma, bool)
    for _, al, _, _ in rots:
        zona |= dilatar(al > 0.02, 2)
    if zona.any():
        out = P.piso_refeito(out, zona, q["semente"])
    # o corpo padrão dos rótulos (seção 12, [29/10]: 1,3×); a PROJ. CLARABOIA, de texto menor no PDF, no corpo em que a
    # altura das letras dela fica igual à do nome LAVABO
    def h_nome(a):
        ys = np.nonzero(a.max(axis=1) > 0.4)[0]
        if not len(ys):
            return 0
        quebras = np.nonzero(np.diff(ys) > 2)[0]
        fim = ys[quebras[0]] if len(quebras) else ys[-1]
        return fim - ys[0] + 1
    h_ref = h_nome(_alfa_rot(Q, q["lavabo"], {"corpo": 1.3}, 0, 0, forma))
    res = out.astype(np.float32)
    feitos = []
    for chave, centro in (("lavabo", q["lavabo_centro"]), ("claraboia", q["claraboia_centro"])):
        b = {k: v for k, v in q[chave].items() if k != "texto"}
        opc = {"corpo": 1.3}
        if "texto" in q[chave]:
            opc["quebra"] = list(q[chave]["texto"])        # o texto trocado, centrado no nome do PDF
        a0 = _alfa_rot(Q, b, opc, 0, 0, forma)
        if chave == "claraboia":
            h1 = h_nome(a0)
            if h1 > 0 and h_ref > 0:
                opc["corpo"] = round(float(np.clip(h_ref / h1 * 1.3, 0.8, 2.4)), 2)
                a0 = _alfa_rot(Q, b, opc, 0, 0, forma)
        ys, xs = np.nonzero(a0 > 0.3)
        cx, cy = (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2
        al = _alfa_rot(Q, b, opc, centro[0] - cx, centro[1] - cy, forma)
        res = compor(res, al, ROTULO_ESCURO)
        feitos.append({"nome": b["nome"], "pdf": b["pdf"], "opc": opc, "desvio": [float(centro[0] - cx),
                       float(centro[1] - cy)], "cor": list(ROTULO_ESCURO), "nota": 1.0})
        print(f"      {b['nome']}: corpo {opc['corpo']}, centro {centro}")
    # o desenho deles fica gravado para o 12K (a busca pela forma não testa esses corpos)
    import json
    ROTULOS_LAVABO.write_text(json.dumps(feitos, ensure_ascii=False, indent=1))
    return np.clip(np.round(res), 0, 255).astype(np.uint8)


def _residuos(out, caixas):
    for x0, y0, x1, y1 in caixas:
        reg = out[y0:y1, x0:x1].astype(np.float32)
        verde = (reg[..., 1] > reg[..., 0] + 15) & (reg.mean(axis=2) < 150)
        m = np.zeros(out.shape[:2], np.uint8)
        m[y0:y1, x0:x1] = (~verde & (reg.mean(axis=2) < 200)).astype(np.uint8)
        out = cv2.inpaint(out, m * 255, 3, cv2.INPAINT_TELEA)
    return out


def _pergolado_bege(Q, out, q):
    import pedidos_terreo_casaa_2910 as P
    x0, y0, x1, y1 = q["caixa_px"]
    H, W = out.shape[:2]
    linhas = np.zeros((H, W), np.uint8)
    tracos = np.zeros((H, W), np.uint8)
    for _, _, segs in T.cadeias_tracejadas(Q, ["ARQ_PERGOLADO"]):
        a0, b0, a1, b1 = P._linha_inteira(segs)
        (u0, v0), (u1, v1) = Q.p2q(a0, b0), Q.p2q(a1, b1)
        cv2.line(linhas, (int(round(u0)), int(round(v0))), (int(round(u1)), int(round(v1))), 1, 1)
        for sg in segs:
            (c0, d0), (c1, d1) = Q.p2q(sg[0], sg[1]), Q.p2q(sg[2], sg[3])
            cv2.line(tracos, (int(round(c0)), int(round(d0))), (int(round(c1)), int(round(d1))), 1, 2)
    livre = np.zeros((H, W), np.uint8)
    livre[y0:y1, x0:x1] = 1 - linhas[y0:y1, x0:x1]
    n, lab, st, _ = cv2.connectedComponentsWithStats(livre, connectivity=4)
    faixas = np.zeros((H, W), bool)
    celulas = np.zeros((H, W), bool)
    for i in range(1, n):
        bx, by, bw, bh, ar = st[i]
        if bx <= x0 or by <= y0 or bx + bw >= x1 or by + bh >= y1:
            continue
        if min(bw, bh) <= q["faixa_max_px"]:
            faixas |= lab == i
        else:
            celulas |= lab == i
    fixo = (agua_mascara(Q) > 0) | moveis_pdf(Q) | dilatar(tracos > 0, 1)
    rots = rotulos_na_imagem(Q, out, dentro=np.pad(np.ones((y1 - y0, x1 - x0), bool), ((y0, H - y1), (x0, W - x1))))
    for _, al, _, _ in rots:
        fixo |= dilatar(al > 0.02, 3)
    buraco = faixas & ~fixo
    valido = cv2.erode(celulas.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool) & ~fixo
    falhou = P.copiar_textura(out, buraco, valido, busca=q["busca"], trecho=q["trecho"])
    if falhou.any():
        out = cv2.inpaint(out, (falhou * 255).astype(np.uint8), 3, cv2.INPAINT_TELEA)
    print(f"      pergolado: {int(buraco.sum())} px das faixas das vigas no Bege dos quadrados")
    return out


def _porta_servico(Q, out, q):
    x0, x1 = q["x_px"]
    img = out.copy()
    for a, b in q["limpar_y"]:
        out[a:b, x0:x1] = img[a + q["fonte_dy"]:b + q["fonte_dy"], x0:x1]
    fx0, fy0, fx1, fy1 = q["folha_px"]
    (p0, p1), (p2, p3) = Q.q2p(fx0, fy0), Q.q2p(fx1, fy1)
    r = (min(p0, p2), min(p1, p3), max(p0, p2), max(p1, p3))
    tl = FA.tela(out, Q, r, folga=4)
    m = tl.ret(r, 0.3)
    FA.sombra_q(tl, m, forca=0.25, dist=0.9, sigma=0.9)
    tl.pintar(m, q["folha"])
    tl.contorno(m, 0.35, q["face"])
    return tl.gravar()


def _ralos(Q, out, ralos):
    for cx, cy, r in ralos:
        tl = FA.tela(out, Q, (cx - r - 1, cy - r - 1, cx + r + 1, cy + r + 1), folga=4)
        m = tl.vazia()
        px_, py_ = tl.pt(cx, cy)
        rr = r * FA.PT_PX * 8
        cv2.circle(m, (int(px_), int(py_)), int(rr), 255, -1, cv2.LINE_AA)
        FA.sombra_q(tl, m, forca=0.18, dist=0.5, sigma=0.5)
        tl.pintar(m, FA.CROMO["meio"])
        miolo = tl.vazia()
        cv2.circle(miolo, (int(px_), int(py_)), int(rr * 0.55), 255, -1, cv2.LINE_AA)
        tl.pintar(miolo, (78, 82, 86))
        tl.contorno(m, 0.45, (70, 74, 78))
        out = tl.gravar()
    return out


def _escritorio(Q, out, q):
    rng = np.random.default_rng(3190)
    # o aparador no tom padrão dos armários, quase liso (um veio leve no comprido)
    r = q["aparador_pt"]
    tl = FA.tela(out, Q, r, folga=4)
    m = tl.ret(r, 0.3)
    FA.sombra_q(tl, m, forca=0.22, dist=1.0, sigma=1.0)
    veio = cv2.GaussianBlur(rng.standard_normal((tl.h, 1)).astype(np.float32), (0, 0), 1.2)
    veio = np.repeat(veio / (veio.std() + 1e-6), tl.w, axis=1)
    tl.pintar_img(m, np.float32(q["armario"])[None, None] * (1 + 0.018 * veio)[..., None])
    tl.contorno(m, 0.35, tuple(v * 0.8 for v in q["armario"]))
    out = tl.gravar()
    # as mesinhas: a de baixo e a de cima, cada uma com o tampo de borda mais escura e o miolo mais claro
    for (cx, cy, rr), cor in q["mesas_pt"]:
        tl = FA.tela(out, Q, (cx - rr - 1, cy - rr - 1, cx + rr + 1, cy + rr + 1), folga=4)
        m = tl.vazia()
        px_, py_ = tl.pt(cx, cy)
        R = rr * FA.PT_PX * 8
        cv2.circle(m, (int(px_), int(py_)), int(R), 255, -1, cv2.LINE_AA)
        FA.sombra_q(tl, m, forca=0.30, dist=1.1, sigma=1.1)
        X, Y = tl.grade()
        d = np.hypot(X - cx, Y - cy) / rr
        tom = np.float32(cor)[None, None] * (1.05 - 0.10 * np.clip(d, 0, 1) ** 2)[..., None] \
            * (1 + 0.012 * np.cos(d * 26))[..., None]
        tl.pintar_img(m, tom)
        tl.contorno(m, 0.35, tuple(v * 0.7 for v in cor))
        out = tl.gravar()
    # a porta: o traço fraco antigo sai (o travertino de cima) e a folha entra nítida, do batente ao fim do vão
    x0, y0, x1, y1 = q["porta_limpar_px"]
    out[y0:y1, x0:x1] = out[y0 + q["porta_fonte_dy"]:y1 + q["porta_fonte_dy"], x0:x1]
    fx0, fy0, fx1, fy1 = q["folha_px"]
    (p0, p1), (p2, p3) = Q.q2p(fx0, fy0), Q.q2p(fx1, fy1)
    r = (min(p0, p2), min(p1, p3), max(p0, p2), max(p1, p3))
    tl = FA.tela(out, Q, r, folga=4)
    m = tl.ret(r, 0.3)
    FA.sombra_q(tl, m, forca=0.25, dist=0.9, sigma=0.9)
    tl.pintar(m, q["folha"])
    tl.contorno(m, 0.35, q["face"])
    return tl.gravar()


def _vazio_viga(out, q):
    x0, y0, x1, y1 = q["caixa_px"]
    reg = out[y0:y1, x0:x1].astype(np.float32)
    branco = (reg.mean(axis=2) > 232) & (reg.max(axis=2) - reg.min(axis=2) < 16)
    a, b, c, d = q["fonte_px"]
    fonte = out[b:d, a:c]
    reps = (int(np.ceil((y1 - y0) / fonte.shape[0])), int(np.ceil((x1 - x0) / fonte.shape[1])))
    tecido = np.tile(np.concatenate([fonte, fonte[:, ::-1]], axis=1), (reps[0], reps[1], 1))[: y1 - y0, : x1 - x0]
    sub = out[y0:y1, x0:x1]
    sub[branco] = tecido[branco]
    return out


def _residuos_finos(out, itens):
    out = out.copy()
    for it in itens:
        x0, y0, x1, y1 = it["px"]
        if it["modo"] == "lados":
            esq = out[y0:y1, x0 - 1].astype(np.float32)
            dir_ = out[y0:y1, x1].astype(np.float32)
            n = x1 - x0
            for k in range(n):
                t = (k + 1) / (n + 1)
                out[y0:y1, x0 + k] = np.round(esq * (1 - t) + dir_ * t).astype(np.uint8)
        else:
            dy = it["fonte_dy"]
            out[y0:y1, x0:x1] = out[y0 + dy:y1 + dy, x0:x1]
    return out


def _paredes_escuras(Q, out, q):
    v0, v1, tol = q["parede"], q["parede_nova"], q["parede_tol"]
    zona = dilatar(FA.paredes_pdf(Q) > 0.05, 3)
    for a, b, c, d in q["muros_px"] + SOLEIRAS_TA["batentes_px"] + CONTORNOS_TA["janela"]["batentes_px"]:
        zona[b:d, a:c] = True
    im = out.astype(np.float32)
    lum = im.mean(axis=2)
    cin = (im.max(axis=2) - im.min(axis=2) < tol)
    cheio = zona & cin & (np.abs(lum - v0) < 22)
    borda = zona & dilatar(cheio, 2) & ~cheio & (lum < 215)
    s = np.zeros(lum.shape, np.float32)
    s[cheio] = 1.0
    s[borda] = np.clip((215 - lum[borda]) / (215 - v0), 0, 1)
    novo = im - (v0 - v1) * s[..., None]
    print(f"      paredes: {int(cheio.sum())} px do cinza {v0} para {v1} ({int(borda.sum())} px de borda)")
    return np.clip(np.round(novo), 0, 255).astype(np.uint8)



# ----------------------------------------------------------------------------------------------------------------------
# Os retoques de 11/11 (pedidos do usuário com os recortes da planta e do 12K), no fim do passo `contornos`:
# - tracejado: "REMOVER ESSE TRACEJADO JUNTO AO CONTORNO / TRACEJADO NA HORIZONTAL": na borda de baixo do travertino
#   junto ao gramado (à esquerda do jardim de 4,79 m²), a última linha alternava travertino e grama (o tracejado); ela
#   fica toda no travertino. No jardim e na ponta da parede do gás, o filete branco entre a parede e a grama vira grama
#   (e parede, na ponta);
# - armário: "CORRIGIR ACABAMENTO DO ARMARIO E RETOQUE NA PAREDE" (o armário alto à esquerda do lavabo): o topo
#   esbranquiçado, a borda da esquerda com degrau e a faixa dupla junto à parede saem; o armário fica um retângulo limpo
#   na madeira dele (o miolo, espelhado nas bordas), com o contorno fino mais escuro, encostado na parede (a 1ª coluna da
#   parede na cobertura do PDF); a parede do lavabo no cinza das paredes, sem as pontas claras;
# - parede do hall: "RETOCAR PAREDE" (a parede embaixo do aparador do hall interno, sobre o jardim da escada): o topo
#   dela variava entre 875 e 878 px, com uma faixa cinza; fica reto na linha do PDF (meia cobertura em 878, cheia de 879
#   para baixo), o piso acima limpo (o travertino 6 px acima; embaixo do aparador, o travertino ao lado dele) e uma
#   sombra de contato leve sob o aparador;
# - grama: "CORRIGIR BORRÃO E RETOCAR O PISO DA GARAGEM, REMOVENDO RESIDUOS DO PISO ANTERIOR": os dois borrões cinza na
#   grama junto à parede do quarto do motorista viram a grama 50 px à direita (com a borda esfumada); a faixa roxa do
#   piso antigo entre a grama e a garagem sai: a grama até 1313 px e o piso da garagem a partir de 1314, sem os pontos
#   claros;
# - pedras: "RETOCAR AS PEDRAS E SUAS BORDAS" (as 5 pedras do acesso ao hall externo, no 12K): cada pedra vira um
#   retângulo limpo (y 608-866, as bordas da esquerda da 2ª e da 3ª sem os dentes), na textura do miolo dela espelhada
#   nas bordas, com o contorno fino; a 4ª, que tinha a emenda da faixa copiada da 3ª, é a 2ª espelhada; e a grama em
#   volta sem os restos claros (cada px claro a até 3 px da pedra vira a grama mais perto, para fora);
# - portas: "NÃO PODEMOS TER NENHUMA PORTA 'FLUTUANTE'. REVISE TODAS E GARANTA QUINA A QUINA ENTRE A PORTA E A PAREDE"
#   (regra de 10/11, a mesma do Subsolo): nas portas de abrir em que a folha parava a ~3 px da ponta da parede (1, 3,
#   6, 7, 9, 13 e 18 da lista das folhas do PDF), a ponta da parede avança, na espessura dela, até a face de dentro da
#   folha (`cliente_subsolo_casaa_0511.portais_cs`, as pontes da ARQ_PAREDE), e a ponta da parede da garagem perde o
#   marco claro; a porta de correr entre a cozinha e o hall (a folha aberta pela metade, solta no vão) fica fechada, de
#   batente a batente: a folha no vão, com as quinas nas dos dois batentes, e a parte que corria junto à parede sai.
RETOQUES_1111 = {
    "tracejado": {"y": 1643, "trav_x": (1240, 1482), "jardim_x": (1482, 1705), "grama_dy": 3},
    "armario": {"ret": (2194, 372, 2242, 609), "miolo": (2199, 378, 2228, 603), "contorno": (0.80, 0.93),
                "parede_caixa": (2236, 340, 2262, 615), "parede_col_25": 2243},
    "parede_hall": {"x": (2248, 2546), "y_meia": 878, "faixa": (875, 877), "fonte_dy": -6,
                    "aparador_x": (2272, 2397), "aparador_fonte_x": (2400, 2423), "sombra": 0.9},
    "grama": {"borroes_px": [(2547, 1160, 2577, 1198), (2547, 1255, 2588, 1308)], "fonte_dx": 50, "funde_px": 4,
              "borda": {"x": (2547, 2700), "y_grama": 1313, "faixa": (1306, 1319), "grama_dy": -9, "piso_dy": 8}},
    "pedras": {"rets": [(2615, 608, 2772, 866), (2781, 608, 2932, 866), (2945, 608, 3095, 866), (3108, 608, 3263, 866),
                        (3272, 608, 3429, 866)], "inset": 4, "contorno": (0.86, 0.95), "refazer": {3: 1},
               "anel_px": 3, "busca_px": 10},
    "portas": {"caixas": {"porta_1": (1590, 1541, 1624, 1627), "porta_3": (1593, 1539, 1678, 1573),
                          "porta_6": (1981, 1451, 2057, 1471), "porta_7": (2048, 1514, 2067, 1579),
                          "porta_9": (2229, 1245, 2248, 1322), "porta_13": (2336, 1288, 2401, 1307),
                          "porta_18": (2516, 1245, 2535, 1322), "garagem_ponta": (2460, 1298, 2476, 1320)},
               "garagem_fio": {"x": (2468, 2473), "y": (1303, 1318), "fonte_dx": 7},
               "correr": {"folha_x": (2164, 2168), "vao_y": (1160, 1228), "perfil_y": (1245, 1270),
                          "batentes": [(1158, 1159), (1229, 1232)], "batente_x": (2152, 2168),
                          "limpar": [(2153, 1196, 2164, 1229), (2164, 1233, 2170, 1296), (2164, 1155, 2171, 1158),
                                     (2153, 1160, 2164, 1164)], "piso_dx": 16, "quina": (2163, 1154, 1158)},
               # a porta do lavabo (aberta junto à parede da esquerda): a folha estava apagada pela metade (um degradê
               # largo, com um vão no meio) e, com o rótulo subindo, ficava solta; ela volta nítida no retângulo do PDF,
               # e a ponta da parede de baixo chega à quina dela
               "lavabo": {"limpar": (2262, 459, 2273, 513), "piso_dx": 14, "folha_px": (2264.7, 460.8, 2267.0, 514.5),
                          "folha": (222, 224, 226), "face": (92, 94, 97), "ponta": (2258, 513, 2264, 523),
                          "ponta_col": (2264, 514, 523, 0.7)},
               "claros": {"mediana": 5, "acima": 25, "subiu": 20}},
}


def _grama_px(px):
    px = np.asarray(px, np.int32)
    return (px[..., 1] - px[..., 0] > 20) & (px.mean(axis=-1) < 115)


def _r_tracejado(out, q):
    y = q["y"]
    im = out.astype(np.int32)
    lum = im.mean(axis=2)
    sat = im.max(axis=2) - im.min(axis=2)
    for x in range(*q["trav_x"]):
        if lum[y, x] < 150 and lum[y - 1, x] > 180:
            out[y, x] = out[y - 2, x]
    for x in range(*q["jardim_x"]):
        if lum[y, x] > 170 and sat[y, x] < 25:
            out[y, x] = out[y + q["grama_dy"], x]
        if lum[y - 1, x] > 120 and sat[y - 1, x] < 25 and lum[y - 2, x] < 70:
            out[y - 1, x] = out[y + q["grama_dy"], x]
    return out


def _r_armario(Q, out, q, P, parede):
    x0, y0, x1, y1 = q["ret"]
    a, b, c, d = q["miolo"]
    miolo = out[b:d + 1, a:c + 1].astype(np.float32)
    lado = np.pad(miolo, ((b - y0, y1 - d), (a - x0, x1 - c), (0, 0)), mode="reflect")
    f0, f1 = q["contorno"]
    lado[[0, -1], :] *= f0
    lado[:, [0, -1]] *= f0
    lado[[1, -2], 1:-1] *= f1
    lado[1:-1, [1, -2]] *= f1
    out[y0:y1 + 1, x0:x1 + 1] = np.clip(np.round(lado), 0, 255).astype(np.uint8)
    # a parede do lavabo: o cinza das paredes onde o PDF tem parede cheia; a 1ª coluna, na cobertura dela
    X0, Y0, X1, Y1 = q["parede_caixa"]
    cheia = P[Y0:Y1, X0:X1] >= 0.99
    reg = out[Y0:Y1, X0:X1]
    reg[cheia] = parede
    xc = q["parede_col_25"]
    for y in range(y0, y1 + 1):
        al = float(P[y, xc])
        out[y, xc] = np.round(out[y, xc - 1].astype(np.float32) * (1 - al) + parede.astype(np.float32) * al)
    return out


def _r_parede_hall(out, q, P, parede):
    ym = q["y_meia"]
    f0, f1 = q["faixa"]
    a0, a1 = q["aparador_x"]
    s0, s1 = q["aparador_fonte_x"]
    for x in range(*q["x"]):
        if not (P[ym - 1, x] < 0.1 and P[ym + 1, x] > 0.9):
            continue
        for y in range(f0, f1 + 1):
            if a0 <= x < a1:
                out[y, x] = out[y - 6, s0 + (x - a0) % (s1 - s0)]
            else:
                out[y, x] = out[y + q["fonte_dy"], x]
        if a0 <= x < a1:
            out[f0, x] = np.round(out[f0, x].astype(np.float32) * q["sombra"])
        al = float(P[ym, x])
        out[ym, x] = np.round(out[ym - 1, x].astype(np.float32) * (1 - al) + parede.astype(np.float32) * al)
        out[ym + 1:ym + 12, x] = parede
    return out


def _r_grama(out, q):
    dx, fu = q["fonte_dx"], q["funde_px"]
    for x0, y0, x1, y1 in q["borroes_px"]:
        src = out[y0:y1, x0 + dx:x1 + dx].astype(np.float32)
        h, w = src.shape[:2]
        yy, xx = np.mgrid[0:h, 0:w]
        dist = np.minimum.reduce([yy, h - 1 - yy, w - 1 - xx]).astype(np.float32)   # a esquerda encosta na parede
        al = np.clip((dist + 1) / (fu + 1), 0, 1)[..., None]
        reg = out[y0:y1, x0:x1].astype(np.float32)
        out[y0:y1, x0:x1] = np.round(reg * (1 - al) + src * al).astype(np.uint8)
    b = q["borda"]
    yg = b["y_grama"]
    f0, f1 = b["faixa"]
    for x in range(*b["x"]):
        for y in range(f0, f1 + 1):
            out[y, x] = out[y + b["grama_dy"], x] if y <= yg else out[y + b["piso_dy"], x]
    return out


def _r_pedras(out, q):
    ins, (c0, c1) = q["inset"], q["contorno"]
    img = out.copy()
    miolos = []
    for x0, y0, x1, y1 in q["rets"]:
        miolos.append(img[y0 + ins:y1 - ins + 1, x0 + ins:x1 - ins + 1].astype(np.float32))
    for i, (x0, y0, x1, y1) in enumerate(q["rets"]):
        m = miolos[i]
        if i in q["refazer"]:
            j = q["refazer"][i]
            m = cv2.resize(miolos[j][:, ::-1], (m.shape[1], m.shape[0]), interpolation=cv2.INTER_LINEAR)
        lado = np.pad(m, ((ins, ins), (ins, ins), (0, 0)), mode="reflect")
        lado[[0, -1], :] *= c0
        lado[:, [0, -1]] *= c0
        lado[[1, -2], 1:-1] *= c1
        lado[1:-1, [1, -2]] *= c1
        out[y0:y1 + 1, x0:x1 + 1] = np.clip(np.round(lado), 0, 255).astype(np.uint8)
    # a grama em volta: os px claros a até `anel_px` da pedra viram a grama mais perto, para fora
    H, W = out.shape[:2]
    pedra = np.zeros((H, W), bool)
    for x0, y0, x1, y1 in q["rets"]:
        pedra[y0:y1 + 1, x0:x1 + 1] = True
    an = q["anel_px"]
    for x0, y0, x1, y1 in q["rets"]:
        for y in range(y0 - an, y1 + an + 1):
            for x in range(x0 - an, x1 + an + 1):
                if pedra[y, x] or _grama_px(out[y, x]):
                    continue
                dx = -1 if x < x0 else (1 if x > x1 else 0)
                dy = -1 if y < y0 else (1 if y > y1 else 0)
                for k in range(1, q["busca_px"] + 1):
                    yy, xx = y + dy * k, x + dx * k
                    if 0 <= yy < H and 0 <= xx < W and not pedra[yy, xx] and _grama_px(out[yy, xx]):
                        out[y, x] = out[yy, xx]
                        break
    return out


def _r_portas(Q, out, q, parede):
    import cliente_subsolo_casaa_0511 as CS
    antes = CS.PORTAIS_CS
    CS.PORTAIS_CS = dict(antes, portais=q["caixas"], faixas={}, cor_parede=int(parede[0]),
                         contorno=(0.0, int(parede[0])), piso_min=70)
    velho = out.copy()
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            out = CS.portais_cs(Q, out)
    finally:
        CS.PORTAIS_CS = antes
    # os px claros que a cópia do piso deixou nas quinas (mais claros que a mediana em volta e que antes) saem
    cl = q["claros"]
    for x0, y0, x1, y1 in q["caixas"].values():
        reg = out[y0:y1, x0:x1]
        med = cv2.medianBlur(np.ascontiguousarray(reg), cl["mediana"])
        lr, lm = reg.astype(np.float32).mean(axis=2), med.astype(np.float32).mean(axis=2)
        lv = velho[y0:y1, x0:x1].astype(np.float32).mean(axis=2)
        m = (lr > lm + cl["acima"]) & (lr > lv + cl["subiu"])
        reg[m] = med[m]
    g = q["garagem_fio"]
    for x in range(*g["x"]):
        for y in range(*g["y"]):
            if out[y, x].astype(np.int32).mean() > 70:
                out[y, x] = out[y, x + g["fonte_dx"]]
    # a porta de correr da cozinha, fechada de batente a batente
    c = q["correr"]
    img = out.copy()
    for x0, y0, x1, y1 in c["limpar"]:
        for y in range(y0, y1):
            for x in range(x0, x1):
                out[y, x] = img[y, x + c["piso_dx"]]
    p0, p1 = c["perfil_y"]
    perfil = img[p0:p1, c["folha_x"][0]:c["folha_x"][1] + 1]
    v0, v1 = c["vao_y"]
    for i, y in enumerate(range(v0, v1 + 1)):
        out[y, c["folha_x"][0]:c["folha_x"][1] + 1] = perfil[i % (p1 - p0)]
    for b0, b1 in c["batentes"]:
        out[b0:b1 + 1, c["batente_x"][0]:c["batente_x"][1] + 1] = parede
    qx, qy0, qy1 = c["quina"]
    out[qy0 + 1:qy1, qx] = out[qy0, qx]
    # a porta do lavabo
    lv = q["lavabo"]
    x0, y0, x1, y1 = lv["limpar"]
    out[y0:y1, x0:x1] = out[y0:y1, x0 + lv["piso_dx"]:x1 + lv["piso_dx"]]
    with contextlib.redirect_stdout(io.StringIO()):
        P = FA.paredes_pdf(Q)
    a, b, c_, d = lv["ponta"]
    ponta = P[b:d, a:c_] >= 0.6
    out[b:d, a:c_][ponta] = parede
    xc, yc0, yc1, al = lv["ponta_col"]
    out[yc0:yc1, xc] = np.round(out[yc0:yc1, xc].astype(np.float32) * (1 - al) + parede.astype(np.float32) * al)
    fx0, fy0, fx1, fy1 = lv["folha_px"]
    (p0, p1), (p2, p3) = Q.q2p(fx0, fy0), Q.q2p(fx1, fy1)
    r = (min(p0, p2), min(p1, p3), max(p0, p2), max(p1, p3))
    tl = FA.tela(out, Q, r, folga=4)
    m = tl.ret(r, 0.3)
    FA.sombra_q(tl, m, forca=0.25, dist=0.9, sigma=0.9)
    tl.pintar(m, lv["folha"])
    tl.contorno(m, 0.35, lv["face"])
    out = np.clip(np.round(tl.gravar()), 0, 255).astype(np.uint8)
    return out


def retoques_1111(Q, out, q=None):
    q = q or RETOQUES_1111
    with contextlib.redirect_stdout(io.StringIO()):
        P = FA.paredes_pdf(Q)
    parede = out[885, 2300].copy()
    out = _r_tracejado(out, q["tracejado"])
    out = _r_armario(Q, out, q["armario"], P, parede)
    out = _r_parede_hall(out, q["parede_hall"], P, parede)
    out = _r_grama(out, q["grama"])
    out = _r_pedras(out, q["pedras"])
    out = _r_portas(Q, out, q["portas"], parede)
    print("      retoques de 11/11: o tracejado junto ao jardim, o armário do lavabo, a parede do hall, a grama do "
          "motorista e a borda da garagem, as 5 pedras do acesso e as portas quina a quina (e a de correr fechada)")
    return out


def contornos_ta(Q, img, q=None):
    q = q or CONTORNOS_TA
    out = np.ascontiguousarray(img.copy())
    out = _carro(out, q["carro"])
    out = _pedras(out, q["pedras"])
    out = _acesso(out, q)
    out = _faixa(Q, out, q["faixa"])
    out = _deck(out, q["deck"])
    vidro = ESCADAS_TA["jardim"]["vidro"]
    out = np.clip(np.round(vidro_laminas(Q, out, q["guarda_corpo_pt"], vidro)), 0, 255).astype(np.uint8)
    out = _janela(Q, out, q["janela"], vidro)
    out = _lavabo_rotulos(Q, out, q["lavabo"])
    out = _residuos(out, q["residuos_px"])
    out = _vazio_viga(out, q["vazio_viga"])
    out = np.clip(np.round(_escritorio(Q, out, q["escritorio"])), 0, 255).astype(np.uint8)
    ralos_pt = [(*Q.q2p(x, y), r / FA.PT_PX) for x, y, r in q["ralos_px"]]
    out = np.clip(np.round(_ralos(Q, out, ralos_pt)), 0, 255).astype(np.uint8)
    out = np.clip(np.round(_porta_servico(Q, out, q["porta_servico"])), 0, 255).astype(np.uint8)
    out = _pergolado_bege(Q, out, q["pergolado"])
    out = _paredes_escuras(Q, out, q)
    out = _residuos_finos(out, q["residuos_finos"])
    out = retoques_1111(Q, out)
    print("    contornos: o 3º carro e o piso em volta; as pedras do acesso; o início da pista e o muro de baixo; a faixa "
          "de baixo sem o tracejado; o deck rente à escada; os guarda-corpos do terraço; a janela da sala de estar; "
          "os rótulos do lavabo; as paredes no cinza mais escuro; os dois resíduos (hall externo e porta de serviço)")
    return out


# ----------------------------------------------------------------------------------------------------------------------
PASSOS = [("tracejados", tracejados_ta), ("gramado", gramado_ta), ("piscina", piscina_ta),
          ("bege", bege_ta), ("piso_marrom", piso_marrom_ta), ("bancadas", bancadas_ta), ("banquetas", banquetas_ta), ("pilar", pilar_ta),
          ("soleiras", soleiras_ta), ("entrada", entrada_ta), ("escadas", escadas_ta), ("shaft", shaft_ta),
          ("contornos", contornos_ta), ("tracejados_finos", tracejados_finos_ta)]


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


# ----------------------------------------------------------------------------------------------------------------------
# O 1º Pavimento mostra o Térreo nublado fora da pegada e nos vazios, sem os rótulos, as letras e setas das escadas e as
# projeções do Térreo (`POE642_REGRAS.md`, seção 11). Ele é refeito onde o Térreo mudou, pela conta de
# `pedidos_terreo_casaa_2910.nublado_1pav_ta` (a diferença entre o Térreo novo e o antigo, nublados), com os dois Térreos
# sem o que o nublado não leva: o antigo é o passo dos tracejados (a final de antes sem nenhum tracejado), sem as letras
# S e D, sem a seta da entrada e sem o nome SHAFT; o novo é o passo do shaft refeito sem os triângulos e as descrições
# (`ANOTAR`), antes dos tracejados finos. Os rótulos, iguais nos dois, se cancelam. A caracol e o shaft são do desenho
# do 1º Pavimento (`fora_px`, com a pista de antes).
NUBLADO_1011 = {"fora_px": [(1860, 1560, 3460, 1960), (1770, 1490, 1990, 1680), (2240, 335, 2360, 400)]}


def terreos_sem_anotacoes(passo_tracejados, passo_soleiras):
    Q = FA.QuadroA("Terreo")
    ANOTAR["sim"] = False
    try:
        velho = passo_tracejados.copy()
        q = ESCADAS_TA
        x0, y0, x1, y1 = T.PISANTES["blocos"][-1]
        centros = {"pisantes": Q.p2q((x0 + x1) / 2, (y0 + y1) / 2), "deck": Q.p2q(*T.DECK_T["centro"]),
                   "jardim": Q.p2q(*T.ESCADA_U["centro"])}
        for nome in ("pisantes", "deck", "jardim"):
            velho = tirar_letra(Q, velho, q[nome]["letra"][0], centros[nome], q[nome]["letra"][1])
        with contextlib.redirect_stdout(io.StringIO()):
            velho = shaft_ta(Q, entrada_ta(Q, velho))
            novo = shaft_ta(Q, escadas_ta(Q, entrada_ta(Q, passo_soleiras)))
    finally:
        ANOTAR["sim"] = True
    return velho, novo


def nublado_1pav_1011(img_1pav, velho, novo):
    import pedidos_terreo_casaa_2910 as P
    return P.nublado_1pav_ta(img_1pav, velho, novo, dict(P.NUBLADO_1PAV_TA, fora_px=NUBLADO_1011["fora_px"]))


# os antes e depois (contra a final do commit 58ea098), em renders/POE642_CasaA_PH_Terreo_1011_<trecho>_antes_depois.jpg
ANTES_DEPOIS_1011 = {"Terreo": {"planta": (270, 140, 3440, 1960), "vazios_varanda_estar": (1480, 580, 2180, 910),
                                "pergolado": (1180, 840, 1560, 1240), "pisantes_deck": (700, 320, 1240, 470),
                                "piscina_prainha": (700, 480, 1360, 1060), "escada_subsolo": (740, 1020, 1130, 1150),
                                "gourmet": (1180, 1180, 1800, 1680), "cozinha_servico": (1700, 1100, 2200, 1660),
                                "caracol": (1760, 1480, 2060, 1660), "entrada_escritorio": (2240, 460, 2640, 880),
                                "lavabo_shaft": (2220, 330, 2420, 560), "escada_jardim": (2240, 860, 2560, 1110),
                                "jardim_479": (1430, 1600, 1730, 1780),
                                # a leva de 10/11 à noite
                                "garagem": (2180, 1310, 2720, 1665), "pedras_hall": (2400, 560, 3440, 910),
                                "acesso_muro": (2880, 1260, 3440, 1960), "faixa_baixo": (1440, 1540, 2900, 1960),
                                "escritorio": (2330, 330, 2610, 620), "terraco_guarda_corpo": (1040, 320, 1620, 420),
                                "janela_estar": (1740, 320, 2000, 430), "lavatorio": (1440, 1420, 1660, 1500)}}
# os antes e depois dos retoques de 11/11 (contra a final de 41f6731), em renders/..._1111_<trecho>_antes_depois.jpg
ANTES_DEPOIS_1111 = {"Terreo": {"curva_acesso": (3280, 1300, 3440, 1700), "tracejado_jardim": (1230, 1600, 1720, 1680),
                                "lavabo_armario": (2180, 330, 2370, 625), "ralos_cozinha": (2100, 1315, 2180, 1420),
                                "ralo_gourmet": (1680, 1390, 1770, 1450), "caracol": (1900, 1500, 2050, 1645),
                                "grama_garagem": (2500, 1120, 2720, 1340), "parede_hall": (2230, 830, 2560, 910),
                                "pedras": (2590, 590, 3440, 890), "porta_correr_cozinha": (2130, 1140, 2200, 1305),
                                "portas_servico": (1580, 1440, 2075, 1630), "portas_motorista": (2220, 1240, 2545, 1330)}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--antes", required=True)
    ap.add_argument("--de")
    ap.add_argument("--ate")
    ap.add_argument("--saida")
    ap.add_argument("--passos")
    ap.add_argument("--antes_depois", action="store_true", help="grava os recortes de ANTES_DEPOIS_1011 em renders/")
    ap.add_argument("--um_pav", help="a final do 1º Pavimento de antes: o Térreo nublado é refeito (pede --passos)")
    a = ap.parse_args()
    img = cv2.imread(a.antes)
    out = correcoes_ta(img, a.de, a.ate, a.passos)
    cv2.imwrite(a.saida or str(FINAL), out)
    if a.antes_depois:
        import pedidos_terreo_casaa_2910 as P
        P.antes_depois_pedidos_ta("Terreo", img, out, caixas=ANTES_DEPOIS_1011, sufixo="1011")
    if a.um_pav:
        pasta = Path(a.passos)
        velho, novo = terreos_sem_anotacoes(cv2.imread(str(pasta / "passo_tracejados.png")),
                                            cv2.imread(str(pasta / "passo_soleiras.png")))
        um = nublado_1pav_1011(cv2.imread(a.um_pav), velho, novo)
        cv2.imwrite(str(FA.CASA / "renders" / "POE642_CasaA_PH_1Pavimento_v7_final_rotulos.png"), um)


if __name__ == "__main__":
    main()

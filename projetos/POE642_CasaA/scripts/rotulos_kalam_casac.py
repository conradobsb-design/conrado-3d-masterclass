"""A opção B do 12K da Casa C: os rótulos na letra Kalam (14/11, "QUERO OS RÓTULOS NO SUBSOLO - VERSÃO B TAMBÉM" e
"TAMBÉM QUERO O RÓTULO VERSÃO B PARA O TERREO"), como as opções B das Casas A e B (`rotulos_manuscritos_casaa`).

1. `achar(pav)`: cada rótulo do PDF (`final3840_casab.textos_rotulos(B.rotulos_casab)`) achado na final de 3840 pela
   forma: o desenho da Inter do motor (`retoque_1pav_casae.rotulos_ambientes`, nos corpos de `CORPOS`, numa linha ou com
   o nome quebrado, o nome em SemiBold ou Regular) casado com o texto escuro (ou claro) da final (correlação
   normalizada, até `BUSCA_PX` do ponto do PDF; os rótulos levados de lugar nas revisões também). O do louceiro 1 vem de
   `revisao_terreo_casac_1411.louceiro1_rotulo` (desenhado lá) e as descrições das escadas do desenho delas
   (`pedidos_*_casac_1311.ESCADAS`). Para cada um: o alfa na final, a cor (a mediana dos px cheios) e as linhas
   (o texto, o meio, a linha de base e a altura das maiúsculas).
2. `limpa(pav)`: a final sem esses textos (`ampliacao_a3_casaa.tirar`: o fundo pela conta do alfa e o miolo do traço
   pelo entorno), a entrada do Topaz da opção B.
3. `desenhar(out, pav, s, X0, Y0)`: no 12K, cada linha na Kalam, no mesmo meio e na mesma linha de base, a altura das
   maiúsculas `ALTURA` x a da Inter (a manuscrita lê menor no mesmo corpo), um corpo só em todos os rótulos (o menor
   teto, a largura da Inter sobre a da Kalam), a mesma cor; as setas, os D e os S ficam como estão.
"""

import contextlib
import io
import json
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
R = AQUI.parents[1] / "POE642_CasaC" / "renders"

CORPOS = [0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0, 1.05, 1.1, 1.15]   # x a escala do motor
BUSCA_PX = 260
JANELA_PX = 260
NOTA_MIN = 0.55
ALTURA = 1.12
TETO_MIN = 0.72


def quadro(pav):
    if pav == "Terreo":
        import revisao_terreo_casac_1311 as RT
        return RT.quadro()
    import pedidos_subsolo_casac_1311 as PS
    return PS.quadro()


def final(pav):
    return R / f"POE642_CasaC_PH_{pav}_final_rotulos.png"


def dados(pav):
    return R / f"POE642_CasaC_PH_{pav}_rotulos_kalam.json"


def _alfa_local(Q, r, opc, centro, forma, fonte_nome):
    """O alfa do rótulo r (opções `opc`) numa janela `forma` com o ponto do PDF em `centro` da janela."""
    import retoque_1pav_casae as R1
    cx, cy = Q.p2q(*r[2])
    ox, oy = cx - centro[0], cy - centro[1]

    def loc(x, y):
        u, v = Q.p2q(x, y)
        return u - ox, v - oy
    h, w = forma
    aj = [(r[0], (centro[0] * 2000 / w, centro[1] * 2000 / w), (0.0, 0.0), dict(opc, cor=(255, 255, 255)))]
    antes = R1.ROTULOS.get("fonte_nome")
    R1.ROTULOS["fonte_nome"] = fonte_nome
    try:
        o = R1.rotulos_ambientes(np.zeros((h, w, 3), np.uint8), [r], loc, escala_desvio=Q.W / 2000, granito=None,
                                 ajustes=aj)
    finally:
        if antes is None:
            R1.ROTULOS.pop("fonte_nome", None)
        else:
            R1.ROTULOS["fonte_nome"] = antes
    return o[..., 1].astype(np.float32) / 255


def _linhas_texto(r, opc):
    """Os textos das linhas como o motor as desenha: o nome (ou a quebra dele), as outras linhas do nome do PDF e a área
    num texto só ("A: 11,7 m²")."""
    resto = [t for t, _, _ in r[1][1:] if not t.startswith("A:") and t != "2"]
    area = "".join(t for t, _, _ in r[1] if t.startswith("A:"))
    if area and any(t == "2" for t, _, _ in r[1]):
        area += "²"
    nomes = list(opc["quebra"]) if "quebra" in opc else [r[1][0][0]]
    return nomes + resto + ([area] if area else [])


def _geometria(alfa, textos):
    """As linhas do alfa (grupos de linhas com tinta): [(texto, meio x, base, altura das maiúsculas, largura)]."""
    tinta = (alfa > 0.35).sum(axis=1)
    ys = np.nonzero(tinta > 0)[0]
    grupos = np.split(ys, np.nonzero(np.diff(ys) > 1)[0] + 1)
    grupos = [g for g in grupos if len(g) >= 3]
    if len(grupos) != len(textos):
        return None
    out = []
    for t, g in zip(textos, grupos):
        prof = tinta[g[0]:g[-1] + 1]
        forte = np.nonzero(prof >= 0.25 * prof.max())[0]
        top, base = g[0] + forte[0], g[0] + forte[-1] + 1
        cols = np.nonzero((alfa[g[0]:g[-1] + 1] > 0.35).any(axis=0))[0]
        out.append((t, float((cols[0] + cols[-1] + 1) / 2), float(base), float(base - top), float(cols[-1] - cols[0] + 1)))
    return out


def _picos(res, n=3, raio=8):
    """Os `n` maiores picos do mapa (supressão de não máximos num raio)."""
    r = res.copy()
    out = []
    for _ in range(n):
        _, mx, _, (lx, ly) = cv2.minMaxLoc(r)
        if mx < NOTA_MIN:
            break
        out.append((float(mx), lx, ly))
        r[max(0, ly - raio):ly + raio + 1, max(0, lx - raio):lx + raio + 1] = -1
    return out


def achar(pav, img=None):
    """Os candidatos de cada rótulo (os melhores picos de todas as variantes) e a atribuição gulosa sem repetição: os
    rótulos de nota maior primeiro, cada um no melhor candidato que não cai sobre um texto já tomado (o QUARTO 3 e o
    QUARTO 2 têm a mesma área e casavam no mesmo lugar)."""
    import final3840_casab as F
    import final3840_casac as C
    import retoque_1pav_casae as R1
    Q = quadro(pav)
    img = cv2.imread(str(final(pav))) if img is None else img
    H, W = img.shape[:2]
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
    rot = F.textos_rotulos(C.B.rotulos_casab(Q.pg, Q.p2q2000))
    quebras = dict(C.ROTULOS_TC["quebras"]) if pav == "Terreo" else {}
    esc = R1.ROTULOS["escala"]
    J = JANELA_PX
    cands = []
    for i, r in enumerate(rot):
        if pav == "Terreo" and r[0] == "LOUCEIRO 1":
            continue                                    # o de `revisao_terreo_casac_1411`, em `extras`
        cx, cy = Q.p2q(*r[2])
        pal = r[1][0][0].split()
        opcs = []
        for c in CORPOS:
            opcs.append({"corpo": esc * c})
            if len(pal) >= 2:
                m = (len(pal) + 1) // 2
                opcs.append({"corpo": esc * c, "quebra": [" ".join(pal[:m]), " ".join(pal[m:])]})
            if r[0] in quebras:
                opcs.append({"corpo": esc * c, "quebra": list(quebras[r[0]])})
        lista = []
        for fonte_nome in ("SemiBold", "Regular"):
            for opc in opcs:
                a = _alfa_local(Q, r, opc, (J, J), (2 * J, 2 * J), fonte_nome)
                ys, xs = np.nonzero(a > 0.02)
                if not len(xs):
                    continue
                x0, y0, x1, y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
                tpl = a[y0:y1, x0:x1]
                if tpl.std() < 1e-3:
                    continue
                wx0 = max(0, int(cx - J + x0 - BUSCA_PX))
                wy0 = max(0, int(cy - J + y0 - BUSCA_PX))
                wx1 = min(W, int(cx - J + x1 + BUSCA_PX))
                wy1 = min(H, int(cy - J + y1 + BUSCA_PX))
                jan = g[wy0:wy1, wx0:wx1]
                if jan.shape[0] < tpl.shape[0] or jan.shape[1] < tpl.shape[1]:
                    continue
                for claro in (False, True):
                    res = cv2.matchTemplate(jan if claro else 255 - jan, tpl, cv2.TM_CCOEFF_NORMED)
                    for nota, lx, ly in _picos(res):
                        # a caixa do texto na final
                        bx, by = wx0 + lx, wy0 + ly
                        lista.append((nota, opc, fonte_nome, claro, bx - x0 - (cx - J), by - y0 - (cy - J), a,
                                      (bx, by, bx + (x1 - x0), by + (y1 - y0))))
        lista.sort(key=lambda t: -t[0])
        cands.append((i, r, lista[:12]))
    # a atribuição: os de nota maior primeiro, sem cair sobre um texto já tomado
    tomadas = []

    def sobre(c1, c2):
        ix = max(0, min(c1[2], c2[2]) - max(c1[0], c2[0]))
        iy = max(0, min(c1[3], c2[3]) - max(c1[1], c2[1]))
        a1 = (c1[2] - c1[0]) * (c1[3] - c1[1])
        return ix * iy / max(1, a1)
    escolha = {}
    for i, r, lista in sorted(cands, key=lambda t: -(t[2][0][0] if t[2] else 0)):
        for cand in lista:
            if all(sobre(cand[7], t) < 0.3 for t in tomadas):
                escolha[i] = (r, cand)
                tomadas.append(cand[7])
                break
    out = []
    for i, r, lista in cands:
        if i not in escolha:
            print(f"    {pav} {r[0]:24s} não achado, fica fora")
            continue
        r, (nota, opc, fonte_nome, claro, dx, dy, a, caixa) = escolha[i]
        cx, cy = Q.p2q(*r[2])
        X0, Y0 = int(round(cx - J + dx)), int(round(cy - J + dy))
        al = np.zeros((H, W), np.float32)
        ya, yb, xa, xb = max(0, Y0), min(H, Y0 + 2 * J), max(0, X0), min(W, X0 + 2 * J)
        al[ya:yb, xa:xb] = a[ya - Y0:yb - Y0, xa - X0:xb - X0]
        cheio = al > 0.9
        cor = np.median(img[cheio], axis=0) if cheio.sum() > 5 else (np.array([250, 250, 250]) if claro else
                                                                      np.array([20, 20, 20]))
        cor = [int(v) for v in cor]
        linhas = _geometria(al, _linhas_texto(r, opc))
        print(f"    {pav} {r[0]:24s} {nota:.3f}  corpo {opc['corpo'] / esc:.2f}  {fonte_nome}"
              f"{'  quebra' if 'quebra' in opc else ''}  ({dx:+.0f}, {dy:+.0f}) px  {'claro' if claro else 'escuro'}"
              f"{'' if linhas else '  (linhas: não casou)'}")
        out.append({"nome": r[0], "pdf": list(r[2]), "opc": opc, "fonte_nome": fonte_nome, "cor": cor, "nota": nota,
                    "linhas": linhas, "_alfa": al})
    return Q, out


def _alfa_texto_linhas(linhas, forma, cor_fonte):
    """O alfa (quadro `forma`) de linhas (texto, fonte, corpo px, meio x, base) na Inter."""
    from PIL import Image, ImageDraw, ImageFont
    H, W = forma
    ss = 4
    al = np.zeros((H, W), np.float32)
    for t, fonte, corpo, cx, base in linhas:
        f = ImageFont.truetype(str(fonte), int(round(corpo * ss)))
        lw = f.getlength(t) / ss
        X0, Y0 = int(cx - lw / 2) - 8, int(base - corpo * 1.5) - 4
        w_, h_ = int(lw) + 16, int(corpo * 2.2) + 8
        tela = Image.new("L", (w_ * ss, h_ * ss), 0)
        ImageDraw.Draw(tela).text(((cx - X0) * ss, (base - Y0) * ss), t, font=f, fill=255, anchor="ms")
        a = np.asarray(tela.resize((w_, h_), Image.LANCZOS), np.float32) / 255
        ya, yb, xa, xb = max(0, Y0), min(H, Y0 + h_), max(0, X0), min(W, X0 + w_)
        al[ya:yb, xa:xb] = np.maximum(al[ya:yb, xa:xb], a[ya - Y0:yb - Y0, xa - X0:xb - X0])
    return al


def extras(pav, forma):
    """As descrições das escadas e, no Térreo, o rótulo do louceiro 1: [(nome, alfa, cor, linhas)]."""
    import final3840_casaa as FA
    from rodape_entrega import FONTES
    from PIL import ImageFont
    e = FA.ESCADA_A
    out = []
    if pav == "Terreo":
        import pedidos_terreo_casac_1311 as PT
        import revisao_terreo_casac_1411 as R14
        escadas, entre = [dict(x) for x in PT.ESCADAS], PT.PS.ENTRELINHA
        q = R14.DESC_DECK
        t = list(escadas[q["escada"]]["texto"])
        t[q["linha"]] = q["novo"]
        escadas[q["escada"]]["texto"] = tuple(t)
        ll = R14.louceiro1_rotulo()
        a = _alfa_texto_linhas(ll, forma, None)
        out.append(("LOUCEIRO 1", a, list(R14.LOUCEIRO1["cor"]),
                    _geometria(a, [x[0] for x in ll])))
    else:
        import pedidos_subsolo_casac_1311 as PS
        escadas, entre = PS.ESCADAS, PS.ENTRELINHA
    fonte = FONTES / e["fonte"]
    for q in escadas:
        ll = [(t, fonte, e["corpo_px"], q["centro_x"], q["base_y"] + i * entre) for i, t in enumerate(q["texto"])]
        a = _alfa_texto_linhas(ll, forma, None)
        out.append((f"escada: {q['nome']}", a, list(e["cor_texto"]), _geometria(a, list(q["texto"]))))
    return out


def apagar(img, camadas):
    """Cada linha de cada texto sai inteira: o piso deslocado (para cima, para baixo ou para os lados) que mais se parece
    com o piso em volta da linha (a mediana da volta, sem textos) e sem outro texto entra no lugar, esfumado (a cópia só
    na vertical trazia a bancada e o vaso para o lugar do BH ACADEMIA)."""
    out = img.copy()
    H, W = img.shape[:2]
    texto = np.zeros((H, W), np.uint8)
    for a, _ in camadas:
        texto |= (a > 0.02).astype(np.uint8)
    texto_d = cv2.dilate(texto, np.ones((7, 7), np.uint8))
    for a, _ in camadas:
        linhas = (a > 0.02).any(axis=1)
        idx = np.nonzero(linhas)[0]
        if not len(idx):
            continue
        for grupo in np.split(idx, np.nonzero(np.diff(idx) > 1)[0] + 1):
            al = np.zeros_like(a)
            al[grupo[0]:grupo[-1] + 1] = a[grupo[0]:grupo[-1] + 1]
            m = cv2.dilate((al > 0.02).astype(np.uint8), np.ones((7, 7), np.uint8))
            ys, xs = np.nonzero(m)
            y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
            h, w = y1 - y0, x1 - x0
            anel = (cv2.dilate(m, np.ones((15, 15), np.uint8)) > 0) & (texto_d == 0)
            ref = np.median(out[anel].astype(np.float32), axis=0)
            mm = m[y0:y1, x0:x1] > 0
            melhor = None
            for dx, dy in ([(0, -(h + k)) for k in (2, 6, 10)] + [(0, h + k) for k in (2, 6, 10)]
                           + [(-(w + k), 0) for k in (4, 12)] + [(w + k, 0) for k in (4, 12)]
                           + [(-(w // 2 + 4), 0), (w // 2 + 4, 0)]):
                sy0, sx0 = y0 + dy, x0 + dx
                if sy0 < 0 or sx0 < 0 or sy0 + h > H or sx0 + w > W:
                    continue
                src = out[sy0:sy0 + h, sx0:sx0 + w].astype(np.float32)
                dif = np.abs(src - ref).max(axis=2)
                ruim = (float(np.mean(dif[mm])) + 400.0 * float((dif[mm] > 22).mean())
                        + 1000.0 * float((texto[sy0:sy0 + h, sx0:sx0 + w] > 0)[mm].mean()))
                if melhor is None or ruim < melhor[0]:
                    melhor = (ruim, dx, dy)
            _, dx, dy = melhor
            mf = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.2)[y0:y1, x0:x1, None]
            src = out[y0 + dy:y1 + dy, x0 + dx:x1 + dx].astype(np.float32)
            out[y0:y1, x0:x1] = np.clip(np.round(out[y0:y1, x0:x1] * (1 - mf) + src * mf), 0, 255).astype(np.uint8)
            # o que destoa do piso da volta (uma ponta de peça que veio na cópia) sai por inpaint
            dev = np.abs(out[y0:y1, x0:x1].astype(np.float32) - ref).max(axis=2)
            ruins = cv2.dilate(((dev > 26) & mm).astype(np.uint8), np.ones((3, 3), np.uint8))
            if ruins.any():
                p0, q0 = max(0, y0 - 6), max(0, x0 - 6)
                sub = np.ascontiguousarray(out[p0:y1 + 6, q0:x1 + 6])
                mk = np.zeros(sub.shape[:2], np.uint8)
                mk[y0 - p0:y1 - p0, x0 - q0:x1 - q0] = ruins * 255
                out[p0:y1 + 6, q0:x1 + 6] = cv2.inpaint(sub, mk, 3, cv2.INPAINT_TELEA)
            texto[y0:y1, x0:x1][mm] = 0
    return out


def preparar(pav):
    """A final sem os rótulos (a entrada do Topaz da opção B) e os dados das linhas para a Kalam."""
    import ampliacao_a3_casaa as AM
    img = cv2.imread(str(final(pav)))
    with contextlib.redirect_stdout(io.StringIO()):
        pass
    Q, rots = achar(pav, img)
    camadas = [(b["_alfa"], tuple(b["cor"])) for b in rots]
    linhas = [{"nome": b["nome"], "cor": b["cor"], "linhas": b["linhas"]} for b in rots]
    for nome, a, cor, ll in extras(pav, img.shape[:2]):
        if nome == "LOUCEIRO 1":
            # o louceiro é estreito (o armário logo abaixo): sai como na opção A, pelo piso de cima
            import revisao_terreo_casac_1411 as R14
            img = R14.louceiro1_apaga(img)
        else:
            camadas.append((a, tuple(cor)))
        linhas.append({"nome": nome, "cor": cor, "linhas": ll})
    # cada linha sai inteira, pelo piso deslocado mais parecido com o da volta (`apagar`; a conta do alfa deixava o
    # fantasma das letras: o desenho achado cai a px inteiros, o da final em fração de px)
    limpa = apagar(img, camadas)
    sem = [b["nome"] for b in linhas if not b["linhas"]]
    if sem:
        print(f"    sem as linhas (fica sem Kalam): {', '.join(sem)}")
    dados(pav).write_text(json.dumps(linhas, ensure_ascii=False, indent=1) + "\n")
    return limpa


def desenhar(out, pav, s, X0, Y0, altura=ALTURA, teto_min=TETO_MIN):
    """As linhas de `dados(pav)` na Kalam no 12K (u = (x - X0) s, v = (y - Y0) s)."""
    import rotulos_manuscritos_casaa as RM
    from rodape_entrega import FONTES
    from PIL import Image, ImageDraw, ImageFont
    rots = json.loads(dados(pav).read_text())
    k_altura = RM._altura_maiuscula(RM.FONTE)            # px de maiúscula por px de corpo, x 200 (em=200)
    ref = ImageFont.truetype(str(RM.FONTE), 200)

    def corpo_para(cap):
        return cap * altura / (k_altura / 200)

    # o teto de cada linha: a largura da Inter sobre a da Kalam no corpo da altura
    tetos = []
    for b in rots:
        for t, mx, base, cap, larg in b["linhas"] or []:
            c = corpo_para(cap)
            tetos.append(larg / max(ref.getlength(t) * c / 200, 1e-6))
    f_glob = min(1.0, max(teto_min, min(tetos) if tetos else 1.0))
    ss = 4
    n = 0
    for b in rots:
        if not b["linhas"]:
            continue
        cor = tuple(int(v) for v in b["cor"])
        for t, mx, base, cap, larg in b["linhas"]:
            c = corpo_para(cap)
            teto = larg / max(ref.getlength(t) * c / 200, 1e-6)
            c *= min(f_glob, teto)
            cs = c * s
            f = ImageFont.truetype(str(RM.FONTE), max(4, int(round(cs * ss))))
            u, v = (mx - X0) * s, (base - Y0) * s
            lw = f.getlength(t) / ss
            bx, by = int(u - lw / 2) - 12, int(v - cs * 1.4) - 8
            w_, h_ = int(lw) + 24, int(cs * 2.2) + 16
            tela = Image.new("L", (w_ * ss, h_ * ss), 0)
            ImageDraw.Draw(tela).text(((u - bx) * ss, (v - by) * ss), t, font=f, fill=255, anchor="ms")
            a = np.asarray(tela.resize((w_, h_), Image.LANCZOS), np.float32)[..., None] / 255
            ya, yb, xa, xb = max(0, by), min(out.shape[0], by + h_), max(0, bx), min(out.shape[1], bx + w_)
            reg = out[ya:yb, xa:xb].astype(np.float32)
            aa = a[ya - by:yb - by, xa - bx:xb - bx]
            out[ya:yb, xa:xb] = np.clip(np.round(reg * (1 - aa) + np.float32(cor) * aa), 0, 255).astype(np.uint8)
            n += 1
    print(f"    {n} linhas na Kalam (o fator único do corpo {f_glob:.3f})")
    return out

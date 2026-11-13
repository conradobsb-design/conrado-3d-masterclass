"""Camas da Casa A com variações de tom da roupa de cama, travesseiro extra e peseira leve ou colcha decorativa
(13/11, Casa C: "Vamos de camas da casa A com variações de tom de roupa de cama e pezeiras"; "Acrescenta travesseiro
extra"; "Mantém tom leve na peneira ou colcha decorativa")."""
import cv2, numpy as np, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, '/home/user/conrado-3d-masterclass/projetos/POE642_CasaA/scripts')
from rodape_entrega import FONTES
B = Path('/home/user/conrado-3d-masterclass/projetos/POE642_CasaA/biblioteca-objetos/03-primeiro-pavimento')
OUT = Path('/home/user/conrado-3d-masterclass/projetos/POE642_CasaC/renders')
TMP = Path('/tmp/poe642_camas'); TMP.mkdir(exist_ok=True)

# frações do PNG: onde começa a roupa de cama, os travesseiros (x0, y0, x1, y1), as almofadas (só a king) e quanto o
# travesseiro extra desce em relação ao original (fração da altura dele)
CAMAS = {"king": {"png": "suite-master/cama-king-a", "roupa_y0": 0.335,
                  "travesseiros": [(0.104, 0.079, 0.48, 0.25), (0.495, 0.079, 0.874, 0.25)],
                  "almofadas": (0.165, 0.335, 28), "desce": 0.40},
         "casal": {"png": "suite-2/cama-casal-a", "roupa_y0": 0.225,
                   "travesseiros": [(0.085, 0.06, 0.469, 0.245), (0.483, 0.06, 0.872, 0.245)],
                   "almofadas": None, "desce": 0.50},
         "solteiro": {"png": "suite-1/cama-solteiro-a", "roupa_y0": 0.222,
                      "travesseiros": [(0.136, 0.052, 0.833, 0.231)], "almofadas": None, "desce": 0.50}}
FONTE_TRAV = ("casal", 0)               # o travesseiro limpo (sem almofada na frente) que vira o extra
PESEIRA_Y = (0.735, 0.865)
COLCHA_Y0 = 0.585
MANTA_V = (0.82, 0.70, 0.11)
MANTA_TRI = (0.60, 0.985, 0.075)        # a dobra (topo do triângulo), a ponta (frações da altura) e o ponto (fração da largura)            # o meio do V (topo da faixa), o topo nos lados e a largura (frações da altura)
RGB = lambda r, g, b: (b, g, r)
TONS = {"off-white": RGB(236, 230, 220), "areia": RGB(214, 197, 176), "branco": RGB(242, 241, 238),
        "areia clara": RGB(226, 214, 198), "greige": RGB(196, 190, 182),
        "terracota clara": RGB(214, 192, 178), "sálvia": RGB(202, 202, 188), "rosé antigo": RGB(210, 190, 188),
        "palha": RGB(224, 214, 190), "cinza-claro": RGB(206, 206, 204), "azul acinzentado": RGB(198, 204, 207),
        "areia média": RGB(214, 200, 180)}


def ler(rel):
    P = cv2.imread(str(B / f'{rel}.png'), cv2.IMREAD_UNCHANGED).astype(np.float32)
    ys, xs = np.nonzero(P[..., 3] > 0)
    return np.ascontiguousarray(P[ys.min():ys.max() + 1, xs.min():xs.max() + 1])


def tingir(P, m, alvo, contraste=1.0):
    med = np.median(P[..., :3][m & (P[..., 3] > 200)], axis=0)
    c = P[..., :3] * (np.float32(alvo) / np.maximum(med, 1))[None, None]
    if contraste != 1.0:
        base = cv2.GaussianBlur(c, (0, 0), 2.0)
        c = base + (c - base) * contraste
    P[..., :3][m] = np.clip(c[m], 0, 255)
    return P


def travesseiro(alvo, w, h):
    """O travesseiro limpo da cama de casal A, no tom `alvo`, w x h px, com o alfa de cantos arredondados."""
    q = CAMAS[FONTE_TRAV[0]]
    P = ler(q["png"])
    H, W = P.shape[:2]
    x0, y0, x1, y1 = q["travesseiros"][FONTE_TRAV[1]]
    T = np.ascontiguousarray(P[int(y0 * H):int(y1 * H), int(x0 * W):int(x1 * W)])
    T = cv2.resize(T, (int(round(w)), int(round(h))), interpolation=cv2.INTER_AREA)
    hh, ww = T.shape[:2]
    m = np.zeros((hh * 4, ww * 4), np.uint8)
    r = int(0.22 * hh * 4)
    ins = int(0.03 * min(hh, ww) * 4)
    cv2.rectangle(m, (ins + r, ins), (ww * 4 - ins - r, hh * 4 - ins), 255, -1)
    cv2.rectangle(m, (ins, ins + r), (ww * 4 - ins, hh * 4 - ins - r), 255, -1)
    for cx, cy in ((ins + r, ins + r), (ww * 4 - ins - r, ins + r), (ins + r, hh * 4 - ins - r), (ww * 4 - ins - r, hh * 4 - ins - r)):
        cv2.circle(m, (cx, cy), r, 255, -1)
    a = cv2.resize(m, (ww, hh), interpolation=cv2.INTER_AREA).astype(np.float32)
    T[..., 3] = cv2.GaussianBlur(a, (0, 0), 0.8)
    T = tingir(T, T[..., 3] > 200, alvo)
    return T


def colar(P, T, x0, y0, sombra=0.30):
    """T (BGRA) sobre P em (x0, y0), com a sombra curta para baixo; só onde P é cama."""
    H, W = P.shape[:2]
    h, w = T.shape[:2]
    x0, y0 = int(round(x0)), int(round(y0))
    a = T[..., 3] / 255
    sh = cv2.GaussianBlur(np.pad(a, 6), (0, 0), 2.2)
    sh = np.roll(sh, 3, axis=0)
    ya, xa = y0 - 6, x0 - 6
    ys, xs = slice(max(ya, 0), min(ya + h + 12, H)), slice(max(xa, 0), min(xa + w + 12, W))
    shc = sh[ys.start - ya:ys.stop - ya, xs.start - xa:xs.stop - xa]
    P[ys, xs, :3] *= (1 - sombra * shc)[..., None]
    ys, xs = slice(max(y0, 0), min(y0 + h, H)), slice(max(x0, 0), min(x0 + w, W))
    ac = a[ys.start - y0:ys.stop - y0, xs.start - x0:xs.stop - x0, None] * (P[ys, xs, 3:4] > 0)
    P[ys, xs, :3] = P[ys, xs, :3] * (1 - ac) + T[ys.start - y0:ys.stop - y0, xs.start - x0:xs.stop - x0, :3] * ac
    return P


def tricô(h, w, s, ss=4):
    """O relevo (0 a 1) do tricô grosso: colunas de pontos em V (cada ponto, duas laçadas inclinadas), visto de cima."""
    H4, W4 = h * ss, w * ss
    sw, sh = s * ss, s * 0.80 * ss
    camadas = []
    for lado in (-1, 1):
        m = np.zeros((H4, W4), np.float32)
        for jj in range(-1, int(H4 / sh) + 2):
            for ii in range(-1, int(W4 / sw) + 2):
                cx, cy = (ii + 0.5) * sw, jj * sh
                cv2.ellipse(m, (int(cx + lado * 0.25 * sw), int(cy)), (int(0.27 * sw), int(0.60 * sh)), lado * 30, 0, 360,
                            1.0, -1, cv2.LINE_AA)
        d = cv2.distanceTransform((m > 0.5).astype(np.uint8), cv2.DIST_L2, 5)
        camadas.append(np.clip(d / (0.22 * sw), 0, 1) ** 0.6)            # cada laçada arredondada (mais alta no meio)
    alt = np.maximum(*camadas)
    alt = cv2.resize(alt, (w, h), interpolation=cv2.INTER_AREA)
    return np.clip(alt, 0, 1)


def cama(tipo, roupa, enfeite, modo):
    """modo "peseira" (a faixa leve nos pés) ou "colcha" (a colcha matelassê leve da metade para os pés)."""
    q = CAMAS[tipo]
    P0 = ler(q["png"])
    P = P0.copy()
    H, W = P.shape[:2]
    yy = np.arange(H)[:, None] * np.ones((1, W))
    xx = np.ones((H, 1)) * np.arange(W)[None, :]
    a = P[..., 3] > 0
    P = tingir(P, a & (yy >= q["roupa_y0"] * H), TONS[roupa])
    # o travesseiro extra, na frente de cada um, no tom do enfeite
    for x0, y0, x1, y1 in q["travesseiros"]:
        w, h = (x1 - x0) * W * 0.96, (y1 - y0) * H * 0.92
        T = travesseiro(TONS[enfeite], w, h)
        P = colar(P, T, (x0 + x1) / 2 * W - w / 2, y0 * H + q["desce"] * (y1 - y0) * H)
    # as almofadas de enfeite (king) de volta por cima, um tom abaixo do enfeite
    if q["almofadas"]:
        ya, yb, croma = q["almofadas"]
        c = P0[..., :3].max(axis=2) - P0[..., :3].min(axis=2)
        m = a & (yy >= ya * H) & (yy < yb * H) & (c > croma)
        m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
        n, lab, st, _ = cv2.connectedComponentsWithStats(m)
        m = np.isin(lab, sorted(range(1, n), key=lambda i: -st[i, cv2.CC_STAT_AREA])[:2])
        A = P0.copy()
        A = tingir(A, m, tuple(0.86 * np.float32(TONS[enfeite])), 1.2)
        ys, xs = np.nonzero(m)
        T = A[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
        T[..., 3] = cv2.GaussianBlur((m[ys.min():ys.max() + 1, xs.min():xs.max() + 1] * 255).astype(np.float32), (0, 0), 0.7)
        P = colar(P, T, xs.min(), ys.min(), sombra=0.25)
    if modo == "manta_tricô":
        # (referência do usuário, "Assim": a manta de tricô grosso dobrada em triângulo e caída nos pés, em V) o
        # triângulo com a dobra atravessando a cama e a ponta para os pés, os pontos do tricô grosso, o rolo da dobra
        # em cima e a sombra curta em volta, no tom do enfeite
        yt, yp, s_rel = MANTA_TRI
        y_t, y_p = yt * H, yp * H
        meia = (W / 2) * np.clip(1 - (yy - y_t) / (y_p - y_t), 0, 1) * 0.97
        tri = a & (yy >= y_t) & (yy <= y_p) & (np.abs(xx - W / 2) <= meia)
        # a sombra da manta no edredom
        sh = cv2.GaussianBlur(tri.astype(np.float32), (0, 0), 0.012 * H)
        sh = np.roll(np.roll(sh, int(0.008 * H), axis=0), -int(0.004 * W), axis=1)
        P[..., :3] *= (1 - 0.30 * sh * (~tri & a))[..., None]
        relevo = tricô(H, W, s_rel * W)
        luz = 0.84 + 0.22 * relevo
        gy, gx = np.gradient(cv2.GaussianBlur(relevo, (0, 0), 0.8))
        luz += 0.35 * (gx - gy) * s_rel * W * 0.08                         # a luz do alto à direita nas laçadas
        rolo = np.clip(1 - (yy - y_t) / (0.035 * H), 0, 1)                    # a dobra de cima, mais alta
        luz = luz * (1 + 0.10 * rolo)
        luz[(yy >= y_t + 0.035 * H) & (yy < y_t + 0.035 * H + 1.5)] *= 0.85
        cor = np.float32(TONS[enfeite])[None, None] * luz[..., None]
        borda = cv2.GaussianBlur(tri.astype(np.float32), (0, 0), 0.8)
        al = np.where(tri, 1.0, 0.0)
        al = np.minimum(al, np.clip(borda * 1.6, 0, 1))[..., None]
        P[..., :3] = P[..., :3] * (1 - al) + np.clip(cor, 0, 255) * al
    elif modo == "manta_v":
        # ("A manta seria posta em v") a manta atravessada nos pés em V: a faixa desce dos lados para o meio, a ponta do
        # V para os pés; as duas barras acompanham o V e a sombra curta fica logo abaixo dela
        yc, ylado, esp = MANTA_V
        y_topo = yc * H - (yc - ylado) * H * np.abs(xx - W / 2) / (W / 2)
        dy = yy - y_topo
        faixa = a & (dy >= 0) & (dy < esp * H)
        P = tingir(P, faixa, TONS[enfeite], 2.2)
        tt = np.clip(dy / (esp * H), 0, 1)
        P[..., :3] *= np.where(faixa, 1.0 - 0.08 * (2 * tt - 1) ** 2, 1.0)[..., None]
        barra = faixa & ((dy < 1.0) | (dy >= esp * H - 1.0))
        P[..., :3] *= np.where(barra, 0.80, 1.0)[..., None]
        luz = faixa & (dy >= 2.0) & (dy < 3.0)
        P[..., :3] *= np.where(luz, 1.05, 1.0)[..., None]
        k = 0.02 * H
        sob = a & ~faixa & (dy >= esp * H) & (dy < esp * H + k)
        P[..., :3] *= np.where(sob, 1 - 0.12 * (1 - (dy - esp * H) / k), 1.0)[..., None]
    elif modo == "peseira":
        p0, p1 = int(PESEIRA_Y[0] * H), int(PESEIRA_Y[1] * H)
        faixa = a & (yy >= p0) & (yy < p1)
        P = tingir(P, faixa, TONS[enfeite], 2.2)
        t = (np.arange(H, dtype=np.float32) - p0) / max(p1 - p0, 1)
        P[..., :3] *= np.where(faixa, (1.0 - 0.08 * (2 * np.clip(t, 0, 1) - 1) ** 2)[:, None], 1.0)[..., None]
        for yb in (p0, p1 - 1):
            P[yb, :, :3][a[yb]] *= 0.80
        P[p0 + 2, :, :3][a[p0 + 2]] *= 1.05
        sombra = np.zeros(H, np.float32)
        k = max(2, int(0.02 * H))
        sombra[p1:p1 + k] = np.linspace(0.12, 0.0, len(sombra[p1:p1 + k]))
        P[..., :3] *= (1 - np.where(a & ~faixa, sombra[:, None], 0.0))[..., None]
    elif modo == "colcha":
        c0 = int(COLCHA_Y0 * H)
        colcha = a & (yy >= c0)
        P = tingir(P, colcha, TONS[enfeite], 1.4)
        s = 0.085 * W                                                    # o matelassê em losangos
        u, v = (xx + yy) / s, (xx - yy) / s
        fu, fv = u - np.floor(u), v - np.floor(v)
        larg = 1.3 / s
        linha = (fu < larg) | (fv < larg)
        luz = ((fu >= larg) & (fu < 2.6 / s)) | ((fv >= larg) & (fv < 2.6 / s))
        fator = np.where(linha, 0.90, np.where(luz, 1.04, 1.0))
        P[..., :3] *= np.where(colcha, fator, 1.0)[..., None]
        for yb, f in ((c0, 0.78), (c0 + 1, 0.86), (c0 + 3, 1.05)):     # a barra de cima, com a luz da dobra
            P[yb, :, :3][a[yb]] *= f
    return np.clip(P, 0, 255)


def foto(P, alt=330, fundo=(233, 228, 220)):
    a = P[..., 3:4] / 255
    rgb = P[..., :3] * a + np.float32(fundo[::-1]) * (1 - a)
    k = alt / P.shape[0]
    rgb = cv2.resize(rgb.astype(np.uint8), None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
    return Image.fromarray(cv2.cvtColor(rgb, cv2.COLOR_BGR2RGB))


# (nome, cama, roupa, [(enfeite, modo)]): A com a peseira leve, B com a colcha decorativa; o travesseiro extra no tom dela
QUARTOS = [("Suíte master · cama king A", "king", "off-white", [("terracota clara", "peseira"), ("areia média", "colcha")]),
           ("Quarto 1 · cama de casal A", "casal", "areia", [("sálvia", "peseira"), ("off-white", "colcha")]),
           ("Quarto 3 · cama de casal A", "casal", "branco", [("rosé antigo", "peseira"), ("cinza-claro", "colcha")]),
           ("Quarto 2 · 2 camas de solteiro A", "solteiro", "areia clara", [("palha", "peseira"), ("azul acinzentado", "colcha")]),
           ("Quarto externo · cama de solteiro A", "solteiro", "branco", [("cinza-claro", "peseira"), ("areia média", "colcha")])]

if __name__ == "__main__":
    f_tit = ImageFont.truetype(str(FONTES / 'Inter-SemiBold.otf'), 34)
    f_sec = ImageFont.truetype(str(FONTES / 'Inter-SemiBold.otf'), 28)
    f_cap = ImageFont.truetype(str(FONTES / 'Inter-Regular.otf'), 21)
    W = 1560
    blocos = []
    for nome, tipo, roupa, opcoes in QUARTOS:
        ims = []
        for i, (enf, modo) in enumerate(opcoes):
            P = cama(tipo, roupa, enf, modo)
            cv2.imwrite(str(TMP / f'{tipo}_{roupa}_{enf}_{modo}.png'.replace(' ', '-')), P.astype(np.uint8))
            ims.append((foto(P), f'{"A" if i == 0 else "B"}: roupa {roupa}, {modo} {enf}'
                                 f'{" · recomendada" if i == 0 else ""}', 'travesseiro extra no mesmo tom'))
        alt = max(im.height for im, _, _ in ims) + 120
        bl = Image.new('RGB', (W, alt), (244, 241, 236))
        d = ImageDraw.Draw(bl)
        d.text((14, 10), nome, font=f_sec, fill=(128, 40, 36))
        x = 14
        for im, cap, cap2 in ims:
            bl.paste(im, (x, 54))
            d.text((x, 54 + im.height + 8), cap, font=f_cap, fill=(30, 30, 30))
            d.text((x, 54 + im.height + 36), cap2, font=f_cap, fill=(95, 95, 95))
            x += max(im.width, int(d.textlength(cap, font=f_cap))) + 70
        blocos.append(bl)
    alto = 66 + sum(b.height + 12 for b in blocos) + 70
    folha = Image.new('RGB', (W, alto), (247, 245, 242))
    d = ImageDraw.Draw(folha)
    d.text((14, 14), 'POE 642 · Casa C · Térreo · camas da Casa A: travesseiro extra, peseira ou colcha',
           font=f_tit, fill=(30, 30, 30))
    y = 66
    for b in blocos:
        folha.paste(b, (0, y))
        y += b.height + 12
    for i, l in enumerate(['As camas da biblioteca da Casa A, no retângulo do PDF; os travesseiros brancos ficam e o extra '
                           'vai na frente, no tom do enfeite;', 'A: a peseira em tom leve, atravessada nos pés; B: a '
                           'colcha decorativa matelassê, da metade para os pés. Na suíte master, as almofadas um tom abaixo.']):
        d.text((14, y + 6 + i * 28), l, font=f_cap, fill=(95, 95, 95))
    arq = OUT / 'POE642_CasaC_PH_Terreo_1311_proposta_camas.jpg'
    folha.save(arq, quality=90)
    print(arq, folha.size)

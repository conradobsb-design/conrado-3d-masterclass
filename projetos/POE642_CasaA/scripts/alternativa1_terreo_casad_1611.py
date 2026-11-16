"""O mobiliário do Térreo da Casa D pela biblioteca da Casa D, a Alternativa 1 (16/11, usuário: "Alternativa 1", sobre
`POE642_CasaD/renders/POE642_CasaD_PH_Terreo_1611_mobiliario_alternativas_{1,2}.jpg`).

As peças geradas para a Casa D (`POE642_CasaD/biblioteca-objetos/02-terreo`), nos desenhos do PDF (os índices de
`F.Quadro("Terreo")` depois de `final3840_casad.contexto_d()`; px da final de 3840). As etapas entram no lugar das da
revisão de 15/11 em `biblioteca_terreo_casad_1511.aplicar` (as mesmas caixas e regras; muda a peça):
- **Suítes:** a cama king da Casa D na master e a de casal nas suítes 1 e 2 (a manta e as almofadas no tom do quarto de
  15/11: terracota, bege, areia; o pé esticado até o comprimento do PDF, a cabeceira e os travesseiros no tamanho do
  PNG); os criados laterais de madeira com o abajur; o banco de peseira em linho; a poltrona concha de linho (o pufe da
  Casa A fica); a cadeira estofada de bancada nas escrivaninhas, 1/3 sob o tampo.
- **Banhos:** a bancada dupla de quartzito Aura no banho master (as cubas nas do PDF) e a de uma cuba nos banhos 1, 2 e 3.
- **Sala íntima:** o sofá em L, a poltrona oliva, as mesas redondas (a de centro e a lateral) e o tapete de trama.
- **Suíte 3/escritório:** a mesa de madeira, o sofá reto; a cadeira de escritório e as de visita de madeira e linho.
- **Jantar:** a mesa longa de madeira e as 10 cadeiras de madeira e linho, o linho em terracota (usuário, 15/11:
  "cadeiras terracota").
- **Living:** no estar do jantar, as 4 poltronas concha em volta da mesa de centro redonda de madeira escura; no estar do
  living, o sofá de linho, 4 poltronas concha (as 2 de cima e as 2 da esquerda) e as 2 mesas orgânicas.
- **Varanda gourmet:** as 2 mesas redondas com as 6 cadeiras de fibra cada; no estar, o sofá curvo, as 3 poltronas concha
  e as mesas orgânicas.
- **Gourmet:** as 4 banquetas altas de madeira; **DCE:** a cama de solteiro da Casa D (a manta em areia).
Os tapetes de hoje, a cozinha (Dekton Danae), o tampo Marrom Tabaco do gourmet, o lavabo e os closets (a cor sólida dos
armários, nota do cliente) ficam.
"""
import contextlib
import io
from pathlib import Path

import cv2
import numpy as np

import biblioteca_1pav_casaa_1211 as B1
import biblioteca_subsolo_casaa_1211 as BS
import biblioteca_terreo_casaa_1211 as BT
import mobiliario_terreo_casac_1311 as MB
import regras_terreo_casab_1311 as RT

AQUI = Path(__file__).resolve().parent
BIB_D = AQUI.parents[1] / "POE642_CasaD" / "biblioteca-objetos" / "02-terreo"
PX_M = B1.PX_M

# as camas: o PNG, as linhas (fração da altura) da manta e das almofadas, a fração de cima que não estica
CAMAS_D = {"king": {"png": "suite-master/cama-master-d", "manta": (0.60, 0.93), "almofadas": (0.20, 0.40), "fixo": 0.42},
           "casal": {"png": "suite-1/cama-casal-d", "manta": (0.56, 0.82), "almofadas": None, "fixo": 0.40},
           "solteiro": {"png": "quarto-dce/cama-solteiro-d", "manta": (0.58, 0.92), "almofadas": None, "fixo": 0.40,
                        "vermelho": True}}
# a cadeira estofada nas escrivaninhas (como `mobiliario_terreo_casac_1311.CADEIRA_ESC`)
CADEIRA_BANCADA = {"png": "D:suite-master/cadeira-bancada-suite", "larg": 30.0, "sob": 1 / 3}
# a bancada dupla de quartzito Aura: as colunas do PNG (o canto, as 2 cubas) que não esticam
DUPLA_D = {"png": "banho-master/bancada-dupla-quartzito-aura", "canto": 30, "cuba1": (60, 260), "cuba2": (387, 589)}
SIMPLES_D = {"png": "banho-1/bancada-simples-quartzito-aura", "canto": 30, "cuba": (130, 366)}
# o jantar: a mesa, as 10 cadeiras e a zona refeita (px); a largura da cadeira (px); o linho em terracota (BGR)
JANTAR_D = {"mesa": 97706, "cadeiras": (65896, 65927, 65959, 65990, 66021, 66052, 66082, 66113, 66144, 66175),
            "zona": (1886, 740, 2015, 977), "larg": 28.0, "terracota": (66, 98, 164)}
# o living: o estar do jantar (as 4 poltronas e a mesa redonda) e o do living (o sofá, as poltronas, as 2 mesas)
ESTAR_D = {"jantar": {"poltronas": (93392, 93435, 93478, 93521), "mesa": 125158, "ficam": (100540, 100542, 97760)},
           "living": {"sofa": 125853, "poltronas": (125012, 125083, 100594, 100810), "mesas": ((125154, 18.0),
                                                                                              (126185, -24.0)),
                      "ficam": (101028, 126168, 101026, 125827, 98058),
                      # (16/11, usuário: "vamos começar por essas duas poltronas do living, no tom terracota") as 2
                      # junto ao vidro da varanda (as de couro do 3D da sala), no terracota das cadeiras do jantar
                      "terracota": (125012, 125083),
                      # (16/11, usuário: "duas poltronas do living, mesmo tom encosto e assento") as 4 num tom só
                      # (encosto e assento): as 2 da janela em terracota, as outras 2 no bege médio da peça
                      "gama_tom_unico": 0.35,
                      # (16/11, usuário, com o 3D: "trocar os tampos das mesas para nogueira ou freijós, pedra em
                      # verde rajada, espelho"; "não precisa trazer o reflexo do ripado na mesa redonda"; "Colocar
                      # adorno") a grande no espelho liso, a menor na pedra verde rajada, as duas com adorno (geradas
                      # no Higgsfield pelo 3D da sala, recortadas no círculo)
                      "mesas_png": ("living/mesa-centro-espelho-adorno-d", "living/mesa-centro-pedra-verde-adorno-d"),
                      # (16/11, usuário: "o tapete não está aparecendo aqui. corrija") o de trama clara da biblioteca da
                      # Casa D (um tom acima do travertino), no retângulo do de antes; as peças que ficam voltam por cima
                      "tapete_png": "living/tapete-estar-trama-clara"}}
# (16/11, usuário: "as quatro poltronas do estar, com mesa redonda ao centro") o estar do jantar: as 4 poltronas creme
# com o aro de madeira (as do 3D) e a mesa redonda de tampo de nogueira com adorno
ESTAR_JANTAR_D = {"poltrona_png": "living/poltrona-creme-madeira-render", "mesa_png": "living/mesa-centro-nogueira-adorno-d",
                  # (16/11, usuário: "melhore a representação desse tapete. e traga o tom de mesa nogueira para as
                  # mesinhas redondas laterais") o tapete redondo de lã greige com a beira debruada (gerado no Higgsfield
                  # em 2K) no círculo do de antes, 1,5 px maior (a beira de antes por baixo); as 2 mesinhas de apoio no
                  # tom da mesa de centro (`pedidos_terreo_casad_1611b.mesinha`)
                  "tapete_png": "living/tapete-redondo-trama-greige-d", "tapete_folga_px": 1.5,
                  "mesinhas": (100540, 100542)}
# a varanda gourmet: as 2 mesas e as 6 cadeiras de cada; o estar (o sofá curvo, as poltronas, as mesas de centro de
# antes e as 2 orgânicas novas: centro, tamanho e giro, px)
VARANDA_D = {"mesas": ((97771, (93266, 93287, 93308, 93329, 93350, 93371)),
                       (101156, (101030, 101051, 101072, 101093, 101114, 101135))),
             "sofa": 125596, "poltronas": (125338, 125467, 125639), "mesas_velhas": (97966, 97991, 98008, 98033),
             "organicas": (((1566.0, 1057.0), (52.0, 40.0), 8.0), ((1601.0, 1075.0), (32.0, 27.0), -18.0)),
             # (16/11, usuário: "proposta de poltrona da varanda", a de fibra trançada do 3D; "use esse sofá com
             # almofadas em tom terracota na varanda, no lugar daquele") as poltronas de fibra com a almofada creme
             # e o sofá curvo da sala de estar da Casa A com as 4 almofadas em terracota
             "poltrona_png": "varanda-gourmet/poltrona-externa-b",
             "sofa_png": "varanda-gourmet/sofa-curvo-almofadas-terracota-d"}
# o piso refeito onde as peças de antes saem: em cada região (o tapete do PDF ou o resto), o desenho de uma amostra limpa
# dela (px, ladrilhada em espelho) na luz do entorno (o inpaint só da própria região, desfocado em `sigma`): o tapete
# redondo do estar do jantar (CONTRAPISO 53503), o do living (66510), o do estar da varanda (66205); o travertino do
# living e o Bege Bahia da varanda
PISOS_D = {"sigma": 4.0, "travertino": (1815, 985, 1875, 1045), "bege": (1562, 712, 1608, 758),
           "tapetes": {"jantar": (53503, (2186, 878, 2224, 908)), "living": (66510, (2140, 1212, 2195, 1236)),
                       "varanda": (66205, (1610, 1100, 1660, 1140))}}
# a suíte 3/escritório: a mesa (px, a do PDF) e o sofá (os 4 retângulos da INS_INSTALAÇÕES, px)
ESCRITORIO_D = {"mesa": (2362.5, 1553.8, 2410.3, 1673.2), "sofa": (2339.8, 1341.5, 2459.2, 1401.2)}


def ler(rel):
    P = cv2.imread(str(BIB_D / f"{rel}.png"), cv2.IMREAD_UNCHANGED).astype(np.float32)
    ys, xs = np.nonzero(P[..., 3] > 8)
    return np.ascontiguousarray(P[ys.min():ys.max() + 1, xs.min():xs.max() + 1])


@contextlib.contextmanager
def com_d(apelidos=None):
    """Os leitores das bibliotecas das Casas A a C (`MB.ler`, `B1.ler_png`, `BT.ler_png`) também leem "D:<rel>" da
    biblioteca da Casa D; `apelidos` troca um PNG de antes por um da Casa D."""
    apelidos = apelidos or {}
    orig = MB.ler, B1.ler_png, BT.ler_png

    def envolver(f):
        def g(rel, *a, **k):
            rel = apelidos.get(rel, rel)
            if isinstance(rel, str) and rel.startswith("D:"):
                return ler(rel[2:])
            return f(rel, *a, **k)
        return g
    MB.ler, B1.ler_png, BT.ler_png = (envolver(f) for f in orig)
    try:
        yield
    finally:
        MB.ler, B1.ler_png, BT.ler_png = orig


def tingir(P, m, cor, gama=0.9, suave=0.7):
    """Os px `m` de P no tom `cor` (BGR), com a luz de cada px (a razão à mediana deles, ** gama), a borda macia."""
    Y = P[..., :3] @ np.float32([0.114, 0.587, 0.299])
    r = (Y / max(float(np.median(Y[m])), 1.0)) ** gama
    novo = np.float32(cor)[None, None] * r[..., None]
    a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), suave)[..., None] * (P[..., 3:4] > 0)
    P = P.copy()
    P[..., :3] = np.clip(P[..., :3] * (1 - a) + novo * a, 0, 255)
    return P


def _sat(P):
    return cv2.cvtColor(np.clip(P[..., :3], 0, 255).astype(np.uint8), cv2.COLOR_BGR2HSV)[..., 1].astype(np.int16)


def cama_png(tipo, cor_bgr, comp, larg):
    """A cama da Casa D com a manta (e as almofadas) no tom do quarto, esticada até comp/larg só da parte de baixo."""
    q = CAMAS_D[tipo]
    P = ler(q["png"])
    h, w = P.shape[:2]
    s = _sat(P)
    lin, col = np.arange(h)[:, None], np.arange(w)[None, :]
    dentro = (col > 0.05 * w) & (col < 0.95 * w) & (P[..., 3] > 200)
    a, b = q["manta"]
    m = (s >= 45) & (lin >= a * h) & (lin <= b * h) & dentro
    if q["almofadas"]:
        c, d = q["almofadas"]
        m |= (s >= 32) & (lin >= c * h) & (lin <= d * h) & dentro
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)) > 0
    if q.get("vermelho"):
        # a manta vinho da cama de solteiro: toda ela, a borda inclusive (o vermelho, onde estiver)
        hue = cv2.cvtColor(np.clip(P[..., :3], 0, 255).astype(np.uint8), cv2.COLOR_BGR2HSV)[..., 0]
        m = ((hue <= 10) | (hue >= 165)) & (s >= 60) & (P[..., 3] > 0)
        m = cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
        m &= (s >= 25) & (P[..., 3] > 0)
    P = tingir(P, m, cor_bgr)
    k = int(q["fixo"] * h)
    alvo = w * comp / larg
    return BS.esticar(P, 0, [(0, k, None), (k, h, max(alvo - k, 0.3 * (h - k)))])


def _cor_quarto(tom):
    import biblioteca_terreo_casad_1511 as TD
    r, g, b = TD.QUARTOS[tom]["manta"]
    return (b, g, r)


def camas(out, par):
    import biblioteca_terreo_casad_1511 as TD
    for nome, (x0, y0, x1, y1), giro, tipo, _, tom, _ in TD.CAMAS:
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        comp, larg = (y1 - y0, x1 - x0) if giro in (0.0, 180.0) else (x1 - x0, y1 - y0)
        P = cama_png(tipo, _cor_quarto(tom), comp, larg)
        out = MB.pousar(out, P, cx, cy, larg, comp, giro, "movel", par)
        out = TD._resto_fora(out, (x0, y0, x1, y1), RT._alfa_peca(P, cx, cy, larg, comp, giro, par.shape), par)
        print(f"    {nome}: a cama {tipo} da Casa D, a manta em {tom}")
    return out


def cama_dce(out, par):
    import biblioteca_terreo_casad_1511 as TD
    q = TD.DCE
    x0, y0, x1, y1 = q["caixa"]
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    P = cama_png("solteiro", _cor_quarto(q["tom"]), y1 - y0, x1 - x0)
    out = MB.pousar(out, P, cx, cy, x1 - x0, y1 - y0, q["giro"], "movel", par)
    out = TD._resto_fora(out, (x0, y0, x1, y1), RT._alfa_peca(P, cx, cy, x1 - x0, y1 - y0, q["giro"], par.shape), par)
    print(f"    DCE do Térreo: a cama de solteiro da Casa D, a manta em {q['tom']}")
    return out


# (16/11, usuário: "temos os recamiers em frente as camas de casal a serem representados com a biblioteca de móveis,
# mais realismo aqui também") o recamier de linho creme com os braços enrolados e a moldura de madeira da biblioteca
# da Casa A (`banco-k3`), os braços inteiros nas pontas e o miolo esticado até o retângulo do PDF
RECAMIER_D = AQUI.parents[1] / "POE642_CasaA" / "biblioteca-objetos" / "03-primeiro-pavimento" / \
    "bancos-pe-de-cama-propostas" / "banco-k3.png"


def ler_abs(caminho):
    P = cv2.imread(str(caminho), cv2.IMREAD_UNCHANGED).astype(np.float32)
    ys, xs = np.nonzero(P[..., 3] > 8)
    return np.ascontiguousarray(P[ys.min():ys.max() + 1, xs.min():xs.max() + 1])


def bancos(Q, out, par):
    import biblioteca_terreo_casad_1511 as TD
    P0 = ler_abs(RECAMIER_D)
    hh, ww = P0.shape[:2]
    e = int(0.14 * ww)
    for i, _ in TD.BANCOS:
        x0, y0, x1, y1 = RT.caixa_pdf(Q, i)
        w, h = x1 - x0, y1 - y0
        L, Dp, g = (w, h, 0.0) if w >= h else (h, w, 90.0)
        P = BS.esticar(P0, 1, [(0, e, None), (e, ww - e, max(hh * L / Dp - 2 * e, 10)), (ww - e, ww, None)])
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        out = MB.pousar(out, P, cx, cy, L, Dp, g, "movel", par)
        out = TD._resto_fora(out, (x0, y0, x1, y1), RT._alfa_peca(P, cx, cy, L, Dp, g, par.shape), par)
    print(f"    recamiers ao pé das camas de casal: o de linho creme com braços e moldura de madeira da biblioteca "
          f"(banco-k3) nos {len(TD.BANCOS)} retângulos do PDF")
    return out


# (16/11, usuário: "na suite master da casa D, temos luminárias de parede") os criados da master sem o abajur: as
# arandelas da parede (`pedidos_terreo_casad_1611.arandelas`) iluminam
SEM_ABAJUR = (97046, 97058)


def criados(Q, out, par):
    import biblioteca_terreo_casad_1511 as TD
    P = ler("suite-master/criado-lateral-d")
    for i, forma, giro, D in TD.CRIADOS:
        x0, y0, x1, y1 = RT.caixa_pdf(Q, i)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        if forma == "redondo":
            w = h = ((x1 - x0) + (y1 - y0)) / 2
            g = 0.0
        else:
            w, h = (x1 - x0, y1 - y0) if giro in (0.0, 180.0) else (y1 - y0, x1 - x0)
            g = giro
        out = MB.pousar(out, P, cx, cy, w, h, g, "movel", par)
        out = TD._resto_fora(out, (x0, y0, x1, y1), RT._alfa_peca(P, cx, cy, w, h, g, par.shape), par)
        if i not in SEM_ABAJUR:
            out = B1.abajur(out, cx, cy, D)
    print(f"    criados: os {len(TD.CRIADOS)} criados laterais de madeira da Casa D, com o abajur")
    return out


# (16/11, usuário, com o recorte da suíte master: "Corrija essa mesinha redonda lateral ao lado da poltrona para um tom
# nogueira e aí corrige já o formato dela") a mesinha de apoio redonda do PDF ao lado da poltrona: a de antes sai junto
# com a poltrona e o pufe (o vinílico refeito de uma vez, sem a borda escura e a cunha clara que sobravam) e entra o
# disco de nogueira da Casa C (`revisao_terreo_casac_1511._png_mesinha`, no painel liso da nogueira), no círculo do PDF,
# com a aresta e a sombra curta
MESINHAS = {"suíte master": 97704}


def _mesinha_nogueira(Q, out, par, i):
    import revisao_terreo_casac_1511 as R15
    x0, y0, x1, y1 = RT.caixa_pdf(Q, i)
    D = ((x1 - x0) + (y1 - y0)) / 2
    P = R15._png_mesinha(dict(R15.MESINHA, patch=ESCRIVANINHAS["painel"]))
    return MB.pousar(out, P, (x0 + x1) / 2, (y0 + y1) / 2, D, D, 0.0, "baixa", par), D


def poltronas(Q, out, par):
    """Como `mobiliario_terreo_casac_1311.poltronas`, com a poltrona concha de linho (o pufe da Casa A fica) e a mesinha
    de apoio em nogueira (`MESINHAS`)."""
    import biblioteca_terreo_casad_1511 as TD
    for nome, _, ip, png_pufe, ipufe in TD.POLTRONAS:
        _, mp = MB.contorno(Q, [ip])
        _, mf = MB.contorno(Q, [ipufe])
        # na suíte master, 12 px em volta (a sombra larga da poltrona de antes, maior, também sai, sem a cunha mais
        # escura junto à mesinha); na suíte 2, 8 (mais largo, o vinílico refeito vira remendo)
        d = 12 if nome in MESINHAS else 8
        buraco = RT.dilatar(mp, d) | RT.dilatar(mf, d)
        if nome in MESINHAS:
            buraco |= RT.dilatar(MB.contorno(Q, [MESINHAS[nome]])[1], d)
        out = MB.piso_vinilico(Q, out, buraco & ~par)
        if nome in MESINHAS:
            out, D = _mesinha_nogueira(Q, out, par, MESINHAS[nome])
            print(f"    {nome}: a mesinha de apoio redonda em nogueira ({D:.1f} px, o círculo do PDF)")
        ys, xs = np.nonzero(mp)
        pc = np.array([xs.mean(), ys.mean()])
        ys2, xs2 = np.nonzero(mf)
        fc = np.array([xs2.mean(), ys2.mean()])
        g = MB.frente(fc - pc)
        (_, _), (w, h), _ = cv2.minAreaRect(np.column_stack([xs, ys]).astype(np.float32))
        lado = 0.95 * min(w, h)
        P = ler("living/poltrona-concha-d")
        out = MB.pousar(out, P, pc[0], pc[1], lado * P.shape[1] / P.shape[0], lado, g, "movel", par)
        (_, _), (w2, h2), _ = cv2.minAreaRect(np.column_stack([xs2, ys2]).astype(np.float32))
        Pf = MB.ler(png_pufe)
        out = MB.pousar(out, Pf, fc[0], fc[1], max(w2, h2), min(w2, h2), g, "movel", par)
        print(f"    {nome}: a poltrona concha de linho da Casa D e o pufe, a frente para o pufe (giro {g:.0f}°)")
    return out


def cadeiras(Q, out, par):
    import biblioteca_terreo_casad_1511 as TD
    with com_d(), contextlib.redirect_stdout(io.StringIO()):
        out = TD.cadeiras(Q, out, par, qc=CADEIRA_BANCADA)
    print("    escrivaninhas (suíte master e suíte 1): a cadeira estofada de bancada da Casa D, 1/3 sob o tampo")
    return out


def _bancada(P, L, Dp, colunas):
    """P esticado no comprimento L (px) com a profundidade Dp: as colunas fixas (o canto e as cubas) iguais."""
    s = Dp / P.shape[0]
    w = P.shape[1]
    fixos = sorted(colunas)
    livre = L / s - sum(b - a for a, b in fixos)
    vaos = [(0, fixos[0][0])] + [(fixos[i][1], fixos[i + 1][0]) for i in range(len(fixos) - 1)] + [(fixos[-1][1], w)]
    tot = sum(b - a for a, b in vaos)
    trechos = []
    for i, (a, b) in enumerate(vaos):
        trechos.append((a, b, (b - a) * livre / tot))
        if i < len(fixos):
            trechos.append((fixos[i][0], fixos[i][1], None))
    return BS.esticar(P, 1, [t for t in trechos if t[1] > t[0]])


def bancada_dupla(out, par):
    import biblioteca_terreo_casad_1511 as TD
    q, d = TD.DUPLA, DUPLA_D
    x0, y0, x1, y1 = q["c"]
    L, Dp = x1 - x0, y1 - y0
    P = ler(d["png"])
    s = Dp / P.shape[0]
    # as cubas nas do PDF: o espaço entre os fixos repartido para os centros caírem em `cubas`
    (a1, b1), (a2, b2) = d["cuba1"], d["cuba2"]
    c1, c2 = q["cubas"][0] - x0, q["cubas"][1] - x0
    w = P.shape[1]
    esq = c1 / s - (b1 - a1) / 2
    meio = (c2 - c1) / s - (b1 - a1) / 2 - (b2 - a2) / 2
    dir_ = (L - c2) / s - (b2 - a2) / 2
    P = BS.esticar(P, 1, [(0, a1, esq), (a1, b1, None), (b1, a2, meio), (a2, b2, None), (b2, w, dir_)])
    o = BT.pousar(out.astype(np.float32), P, (x0 + x1) / 2, (y0 + y1) / 2, L, Dp, q["giro"], BT.SOMBRAS["baixa"], PX_M,
                  nao=par)
    print(f"    banho master: a bancada dupla de quartzito Aura da Casa D em {L:.1f} x {Dp:.1f} px, as cubas nas do PDF")
    return np.clip(np.round(o), 0, 255).astype(np.uint8)


def pecas(out, par):
    """As peças dos banhos de 15/11 (`biblioteca_terreo_casad_1511.PECAS`), a cuba esculpida trocada pela bancada de
    uma cuba de quartzito Aura (o mesmo retângulo; a cuba no meio)."""
    import biblioteca_terreo_casad_1511 as TD
    n = 0
    for amb, ps in TD.PECAS.items():
        for p in ps:
            if "cuba-esculpida" in p[1]:
                _, _, cx, cy, wt, ht, g, sombra, _ = p
                q = SIMPLES_D
                P0 = ler(q["png"])
                w0 = P0.shape[1]
                P = _bancada(P0, wt, ht, [(0, q["canto"]), q["cuba"], (w0 - q["canto"], w0)])
                o = BT.pousar(out.astype(np.float32), P, cx, cy, wt, ht, g, BT.SOMBRAS[sombra], PX_M, nao=par)
                out = np.clip(np.round(o), 0, 255).astype(np.uint8)
            else:
                out = RT.pousar_bib(out, RT.item_bib(*p), par)
            n += 1
    print(f"    banhos 1, 2 e 3: a bancada de uma cuba de quartzito Aura da Casa D; as bacias Carrara ({n} peças)")
    return out


def sala_intima(Q, out, antes, par):
    """Como `biblioteca_terreo_casad_1511.sala_intima`, com as peças da Casa D (a mesa de centro de antes sai)."""
    import biblioteca_terreo_casad_1511 as TD
    q = TD.SALA_INTIMA
    _, tap = MB.contorno(Q, [q["tapete"]])
    _, sofa = MB.contorno(Q, list(q["sofa"]))
    _, pol = MB.contorno(Q, [q["poltrona"]])
    _, ml = MB.contorno(Q, list(q["mesas_laterais"]) + list(q["mesas_centro"]))
    out = MB.piso_vinilico(Q, out, RT.dilatar(sofa | pol | ml | tap, 8) & ~par)
    x0, y0, x1, y1 = RT.caixa_pdf(Q, q["tapete"])
    out = MB.pousar(out, ler("sala-intima/tapete-intimo-d"), (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, 0.0,
                    "tapete", par)
    Ps = ler("sala-intima/sofa-intimo-l-d")
    melhor = None
    for esp, P in ((False, Ps), (True, np.ascontiguousarray(Ps[:, ::-1]))):
        _, _, (iou, g, _, _) = MB.encaixar(Q, P, sofa, giros=(0, 90, 180, 270))
        if melhor is None or iou > melhor[0]:
            melhor = (iou, g, esp, P)
    iou, g, esp, P = melhor
    ys, xs = np.nonzero(sofa)
    bw, bh = float(xs.max() + 1 - xs.min()), float(ys.max() + 1 - ys.min())
    cx, cy = (xs.min() + xs.max() + 1) / 2, (ys.min() + ys.max() + 1) / 2
    wt, ht = (bw, bh) if round(g) % 180 == 0 else (bh, bw)
    out = MB.pousar(out, P, cx, cy, wt, ht, g, "movel", par)
    Pm = ler("sala-intima/mesa-intima-redonda-d")
    for i in list(q["mesas_centro"]) + list(q["mesas_laterais"]):
        a0, b0, a1, b1 = RT.caixa_pdf(Q, i)
        D_ = ((a1 - a0) + (b1 - b0)) / 2
        out = MB.pousar(out, Pm, (a0 + a1) / 2, (b0 + b1) / 2, D_, D_, 0.0, "mesa", par)
    Pp = ler("sala-intima/poltrona-verde-intima-d")
    cx, cy, (iou2, _, wt2, ht2) = MB.encaixar(Q, Pp, pol)
    # (16/11, usuário: "rotação das poltronas [...] para a direção do 3D") como no 3D da sala íntima: de costas para a
    # entrada, de frente para a mesa de centro e a janela (a frente do PNG para baixo); o encaixe na silhueta redonda do
    # PDF não diz a frente
    g2 = 0.0
    lado = min(wt2, ht2)
    out = MB.pousar(out, Pp, cx, cy, lado * Pp.shape[1] / Pp.shape[0], lado, g2, "movel", par)
    print(f"    sala íntima: o tapete de trama, o sofá em L da Casa D ({'espelhado, ' if esp else ''}giro {g:.0f}°, "
          f"{iou * 100:.0f}% sobre o L do PDF), a poltrona oliva (giro {g2:.0f}°) e as mesas redondas")
    return out


def escritorio(out, par, q=ESCRITORIO_D):
    import biblioteca_terreo_casad_1511 as TD
    x0, y0, x1, y1 = q["mesa"]
    P = ler("suite-3-e-escritorio/mesa-escritorio-d")
    out = MB.pousar(out, P, (x0 + x1) / 2, (y0 + y1) / 2, y1 - y0, x1 - x0, 90.0, "mesa", par)
    x0, y0, x1, y1 = q["sofa"]
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    P = ler("suite-3-e-escritorio/sofa-escritorio-d")
    out = MB.pousar(out, P, cx, cy, x1 - x0, y1 - y0, 0.0, "movel", par)
    out = TD._resto_fora(out, (x0, y0, x1, y1), RT._alfa_peca(P, cx, cy, x1 - x0, y1 - y0, 0.0, par.shape), par)
    print("    suíte 3/escritório: a mesa de madeira e o sofá reto da Casa D")
    return out


def cadeiras_s3(Q, out, par):
    import biblioteca_terreo_casad_1511 as TD
    q = [(n, "D:suite-3-e-escritorio/cadeira-escritorio" if n == "escritório" else "D:jantar/cadeira-jantar-linho-d",
          c, lado, borda, wt) for n, _, c, lado, borda, wt in TD.CADEIRAS_S3]
    with com_d(), contextlib.redirect_stdout(io.StringIO()):
        out = TD.cadeiras_s3(Q, out, par, q=q)
    print("    suíte 3: a cadeira de escritório e as 2 de visita de madeira e linho, 1/3 sob o tampo")
    return out


def cadeira_terracota(cor):
    """A cadeira de madeira e linho da Casa D com o linho (o que não é a madeira) no tom `cor` (BGR)."""
    P = ler("jantar/cadeira-jantar-linho-d")
    m = (_sat(P) < 75) & (P[..., 3] > 200)
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)) > 0
    return tingir(P, m, cor)


def _ladrilho(img, amostra, h, w):
    x0, y0, x1, y1 = amostra
    A = img[y0:y1, x0:x1].astype(np.float32)
    A = np.concatenate([A, A[:, ::-1]], axis=1)
    A = np.concatenate([A, A[::-1]], axis=0)
    return np.tile(A, (h // A.shape[0] + 1, w // A.shape[1] + 1, 1))[:h, :w]


def refazer(out, buraco, regioes, sigma=PISOS_D["sigma"], ficam=None, todo=False):
    """O piso no `buraco`, região por região ((máscara ou None: o resto, amostra px)): o desenho da amostra (o detalhe
    sobre a média desfocada dela) na luz da região em volta (o inpaint que só lê a região fora do buraco)."""
    ys, xs = np.nonzero(buraco)
    if not len(xs):
        return out
    H, W = buraco.shape
    X0, Y0 = max(xs.min() - 16, 0), max(ys.min() - 16, 0)
    X1, Y1 = min(xs.max() + 17, W), min(ys.max() + 17, H)
    sub = out[Y0:Y1, X0:X1]
    excl = np.zeros(buraco.shape, bool) if ficam is None else ficam
    b = buraco[Y0:Y1, X0:X1] & ~excl[Y0:Y1, X0:X1]
    e = excl[Y0:Y1, X0:X1]
    h, w = b.shape
    novo = sub.astype(np.float32)
    resto = np.ones((h, w), bool)
    for reg, amostra in regioes:
        r = resto if reg is None else (reg[Y0:Y1, X0:X1] & resto)
        resto = resto & ~r
        m = b if todo else (b & r)                   # `todo`: o buraco inteiro com o piso desta região
        if not m.any():
            continue
        fora = (b | ~r | e).astype(np.uint8) * 255           # as peças que ficam não dão a luz
        if (fora == 0).sum() < 20:
            continue
        luz = cv2.GaussianBlur(cv2.inpaint(sub, fora, 5, cv2.INPAINT_TELEA).astype(np.float32), (0, 0), sigma)
        T = _ladrilho(out, amostra, h, w)
        det = T / np.maximum(cv2.GaussianBlur(T, (0, 0), sigma), 1)
        novo[m] = (luz * det)[m]
    out = out.copy()
    out[Y0:Y1, X0:X1] = np.clip(np.round(novo), 0, 255).astype(np.uint8)
    return out


def _borda(out, tap, buraco, par, larg=2):
    """A borda do tapete (a faixa de `larg` px dos dois lados do contorno) que caiu no buraco volta copiada da própria
    borda fora dele, ao longo dela (em pé nos lados em pé, deitada nos deitados): a franja e o fio seguem."""
    t = tap.astype(np.uint8)
    contorno_ = (cv2.dilate(t, np.ones((3, 3), np.uint8)) - cv2.erode(t, np.ones((3, 3), np.uint8))) > 0
    gx = cv2.Sobel(tap.astype(np.float32), cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(tap.astype(np.float32), cv2.CV_32F, 0, 1, ksize=3)
    k = np.ones((2 * larg + 1, 2 * larg + 1), np.uint8)
    for eixo, lado in (("y", np.abs(gx) > np.abs(gy)), ("x", np.abs(gy) >= np.abs(gx))):
        faixa = cv2.dilate((contorno_ & lado).astype(np.uint8), k) > 0
        b = faixa & buraco & ~par
        if b.any():
            out = RT.piso_saltando(out, b, faixa & ~buraco & ~par, larg=12, alcance=80, eixo=eixo)
    return out


def _limpa(Q, out, par, ids, regioes, d=5, ficam=()):
    """As peças `ids` do PDF (a silhueta, `d` px a mais) saem: o piso refeito por `refazer`; nos tapetes, a borda. As
    peças `ficam` (mesinhas, o banco) não entram no buraco nem dão a luz do piso (sem o halo em volta delas)."""
    _, m = MB.contorno(Q, list(ids))
    excl = RT.dilatar(MB.contorno(Q, list(ficam))[1], 2) if ficam else None
    buraco = RT.dilatar(m, d) & ~par
    if excl is not None:
        buraco &= ~excl
    out = refazer(out, buraco, regioes, ficam=excl)
    for reg, _ in regioes:
        if reg is not None:
            out = _borda(out, reg, buraco, par)
    return out


def _circulo(img, ref, amostras, buraco):
    """O círculo (cx, cy, R) do tapete redondo da imagem: a beira de onde o tom é mais o do tapete que o do piso (as
    amostras), fora do buraco, ajustada por mínimos quadrados."""
    ys, xs = np.nonzero(ref)
    X0, Y0, X1, Y1 = xs.min() - 14, ys.min() - 14, xs.max() + 15, ys.max() + 15
    sub = cv2.GaussianBlur(img[Y0:Y1, X0:X1].astype(np.float32), (0, 0), 1.5)
    cor = [img[b0:b1, a0:a1].reshape(-1, 3).astype(np.float32).mean(axis=0) for a0, b0, a1, b1 in amostras]
    e = (np.linalg.norm(sub - cor[0], axis=2) < np.linalg.norm(sub - cor[1], axis=2)).astype(np.uint8)
    e = cv2.morphologyEx(e, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    cs, _ = cv2.findContours(e, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cs, key=cv2.contourArea)[:, 0].astype(np.float64)
    longe = ~cv2.dilate(buraco[Y0:Y1, X0:X1].astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool)
    c = c[longe[c[:, 1].astype(int), c[:, 0].astype(int)]]
    A = np.column_stack([2 * c[:, 0], 2 * c[:, 1], np.ones(len(c))])
    a, b, k = np.linalg.lstsq(A, (c ** 2).sum(axis=1), rcond=None)[0]
    return X0 + a, Y0 + b, float(np.sqrt(k + a * a + b * b))


def _limpa_redondo(Q, out, par, ids, nome, piso, d=7, ficam=(), circulo=False):
    """Como `_limpa`, num tapete redondo: o círculo do tapete da imagem (`_circulo`), o tapete e o piso refeitos no
    buraco inteiro e no anel da beira, juntados pela distância ao círculo, com a beira macia de 2 px (sem os degraus da
    máscara nem os da beira do render)."""
    _, m = MB.contorno(Q, list(ids))
    excl = RT.dilatar(MB.contorno(Q, list(ficam))[1], 2) if ficam else None
    buraco = RT.dilatar(m, d) & ~par
    if excl is not None:
        buraco &= ~excl
    i, amostra = PISOS_D["tapetes"][nome]
    ref = MB.contorno(Q, [i])[1]
    cx, cy, R = _circulo(out, ref, (amostra, piso), buraco)
    H, W = par.shape
    yy, xx = np.mgrid[0:H, 0:W]
    dist = np.hypot(xx - cx, yy - cy)
    dentro = dist < R
    # a beira inteira do tapete (o anel de 5 px dos dois lados) também: o círculo igual em toda a volta
    buraco = (buraco | (np.abs(dist - R) < 5)) & ~par
    if excl is not None:
        buraco &= ~excl
    o_t = refazer(out, buraco, [(dentro, amostra)], ficam=excl, todo=True)
    o_p = refazer(out, buraco, [(~dentro, piso)], ficam=excl, todo=True)
    a = np.clip((R - dist) / 2.0 + 0.5, 0, 1)[..., None]
    novo = o_t.astype(np.float32) * a + o_p.astype(np.float32) * (1 - a)
    out = out.copy()
    out[buraco] = np.clip(np.round(novo[buraco]), 0, 255).astype(np.uint8)
    print(f"      o tapete redondo: o círculo da imagem (centro {cx:.1f}, {cy:.1f}; raio {R:.1f} px)")
    return (out, (cx, cy, R)) if circulo else out


def _tapete(Q, nome, img=None):
    """A máscara do tapete: a do PDF (o redondo) ou, com `img`, o retângulo do tapete da própria imagem (a borda do
    render, que fica uns px fora da do PDF): por linha e por coluna, onde o tom é mais o da amostra do tapete que o do
    piso em volta (o travertino ou o Bege Bahia)."""
    i, amostra = PISOS_D["tapetes"][nome]
    m = MB.contorno(Q, [i])[1]
    if img is None:
        return m, amostra
    piso = PISOS_D["bege"] if nome == "varanda" else PISOS_D["travertino"]
    ys, xs = np.nonzero(m)
    X0, Y0, X1, Y1 = xs.min() - 12, ys.min() - 12, xs.max() + 13, ys.max() + 13
    sub = cv2.GaussianBlur(img[Y0:Y1, X0:X1].astype(np.float32), (0, 0), 1.5)
    cor = [img[b0:b1, a0:a1].reshape(-1, 3).astype(np.float32).mean(axis=0) for a0, b0, a1, b1 in (amostra, piso)]
    e_tap = np.linalg.norm(sub - cor[0], axis=2) < np.linalg.norm(sub - cor[1], axis=2)
    my0, my1 = ys.min() - Y0, ys.max() - Y0
    mx0, mx1 = xs.min() - X0, xs.max() - X0
    col = e_tap[my0 + 8:my1 - 8].mean(axis=0)
    lin = e_tap[:, mx0 + 8:mx1 - 8].mean(axis=1)
    c = np.nonzero(col > 0.5)[0]
    r = np.nonzero(lin > 0.5)[0]
    ret = np.zeros(m.shape, bool)
    ret[Y0 + r.min():Y0 + r.max() + 1, X0 + c.min():X0 + c.max() + 1] = True
    return ret, amostra


def _centro(Q, i):
    x0, y0, x1, y1 = RT.caixa_pdf(Q, i)
    return (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0


def _cadeiras_mesa(Q, out, par, mesa_c, ids, P, larg, mesa_r=None):
    """As cadeiras de frente para a mesa: na redonda, para o centro; na retangular (`mesa_r`, px), (16/11, usuário: "deixe
    as cadeiras alinhadas, sem ficarem tortas ou bagunçadas") de frente para o lado da mesa em que estão, alinhadas a ele
    (as dos lados em pé, as das cabeceiras deitadas), no centro do PDF."""
    for i in ids:
        cx, cy, _, _ = _centro(Q, i)
        d = np.array(mesa_c) - np.array([cx, cy])
        if mesa_r is not None:
            x0, y0, x1, y1 = mesa_r
            d = np.array([np.sign(d[0]), 0.0]) if (cx < x0 or cx > x1) else np.array([0.0, np.sign(d[1])])
        g = MB.frente(d)
        out = MB.pousar(out, P, cx, cy, larg, larg * P.shape[0] / P.shape[1], g, "movel", par)
    return out


def jantar(Q, out, par, q=JANTAR_D):
    x0, y0, x1, y1 = q["zona"]
    zona = np.zeros(par.shape, bool)
    zona[y0:y1, x0:x1] = True
    out = MB.piso_travertino(out, zona & ~par, par, alcance=200)
    mx, my, mw, mh = _centro(Q, q["mesa"])
    out = _cadeiras_mesa(Q, out, par, (mx, my), q["cadeiras"], cadeira_terracota(q["terracota"]), q["larg"],
                         mesa_r=RT.caixa_pdf(Q, q["mesa"]))
    P = ler("jantar/mesa-jantar-longa-d")
    out = MB.pousar(out, P, mx, my, mh, mw, 90.0, "mesa", par)
    print(f"    jantar: a mesa longa de madeira da Casa D e as {len(q['cadeiras'])} cadeiras de madeira e linho, o linho "
          "em terracota")
    return out


def estar(Q, out, par, q=ESTAR_D, qj=ESTAR_JANTAR_D):
    Pp = ler("living/poltrona-concha-d")
    Pj = ler(qj["poltrona_png"])
    # o estar do jantar: as 4 poltronas viradas para a mesa redonda de madeira escura
    e = q["jantar"]
    trav = (None, PISOS_D["travertino"])
    import pedidos_terreo_casad_1611b as PD2
    mesinhas = tuple(qj.get("mesinhas", ()))
    out, (tcx, tcy, tR) = _limpa_redondo(Q, out, par, list(e["poltronas"]) + [e["mesa"], *mesinhas], "jantar",
                                         PISOS_D["travertino"], ficam=[i for i in e["ficam"] if i not in mesinhas],
                                         circulo=True)
    if qj.get("tapete_png"):
        Rn = tR + qj["tapete_folga_px"]
        out = MB.pousar(out, ler(qj["tapete_png"]), tcx, tcy, 2 * Rn, 2 * Rn, 0.0, "tapete", par)
    mx, my, mw, mh = _centro(Q, e["mesa"])
    for i in e["poltronas"]:
        cx, cy, w, h = _centro(Q, i)
        lado = 0.95 * min(w, h)
        g = MB.frente(np.array([mx - cx, my - cy]))
        out = MB.pousar(out, Pj, cx, cy, lado * Pj.shape[1] / Pj.shape[0], lado, g, "movel", par)
    D_ = (mw + mh) / 2
    out = MB.pousar(out, ler(qj["mesa_png"]), mx, my, D_, D_, 0.0, "mesa", par)
    for i in mesinhas:
        out = PD2.mesinha(Q, out, par, i)
    # o estar do living: o sofá de linho (de costas para baixo), as poltronas para o meio, as mesas orgânicas
    e = q["living"]
    tap_l = _tapete(Q, "living", out)
    out = _limpa(Q, out, par, [e["sofa"], *e["poltronas"], *[i for i, _ in e["mesas"]]],
                 [tap_l, trav], ficam=e["ficam"])
    if e.get("tapete_png"):
        cx_ = PD2.caixa_uniao(tap_l[0], RT.caixa_pdf(Q, PISOS_D["tapetes"]["living"][0]))
        out = PD2.tapete_novo(Q, out, par, ler(e["tapete_png"]), cx_, ficam=e["ficam"])
    cxs, cys, ws, hs = _centro(Q, e["sofa"])
    out = MB.pousar(out, ler("living/sofa-living-d"), cxs, cys, ws, hs, 180.0, "movel", par)
    pts = np.array([_centro(Q, i)[:2] for i, _ in e["mesas"]])
    meio = pts.mean(axis=0)
    a_ = Pp[..., 3] > 200
    Pt = tingir(Pp, a_, JANTAR_D["terracota"], gama=e["gama_tom_unico"])
    Pb = tingir(Pp, a_, tuple(float(v) for v in np.median(Pp[..., :3][a_], axis=0)), gama=e["gama_tom_unico"])
    for i in e["poltronas"]:
        cx, cy, w, h = _centro(Q, i)
        lado = 0.95 * min(w, h)
        g = MB.frente(meio - np.array([cx, cy]))
        g = round(g / 90.0) * 90.0                     # de frente para o estar, alinhadas às paredes
        P_ = Pt if i in e.get("terracota", ()) else Pb
        out = MB.pousar(out, P_, cx, cy, lado * P_.shape[1] / P_.shape[0], lado, g, "movel", par)
    for (i, g), png in zip(e["mesas"], e["mesas_png"]):
        Pm = ler(png)
        cx, cy, w, h = _centro(Q, i)
        D_ = 0.96 * (w + h) / 2
        out = MB.pousar(out, Pm, cx, cy, D_, D_ * Pm.shape[0] / Pm.shape[1], g, "mesa", par)
    print("    living: o estar do jantar com as 4 poltronas creme com aro de madeira e a mesa redonda de nogueira com "
          "adorno; o do living com o sofá de linho, 4 poltronas concha num tom só (as 2 junto ao vidro da varanda em "
          "terracota) e as mesas de espelho e de pedra verde rajada com adorno")
    return out


def varanda(Q, out, par, q=VARANDA_D):
    Pc = ler("varanda-gourmet/cadeira-gourmet-fibra-d")
    Pm = ler("varanda-gourmet/mesa-redonda-gourmet-d")
    bege = (None, PISOS_D["bege"])
    for mesa, cads in q["mesas"]:
        out = _limpa(Q, out, par, [mesa, *cads], [bege])
        mx, my, mw, mh = _centro(Q, mesa)
        larg = 0.95 * float(np.mean([min(_centro(Q, i)[2:]) for i in cads]))
        out = _cadeiras_mesa(Q, out, par, (mx, my), cads, Pc, larg)
        D_ = (mw + mh) / 2
        out = MB.pousar(out, Pm, mx, my, D_, D_, 0.0, "mesa", par)
    # o estar: o sofá curvo no desenho do PDF, as poltronas para o meio, as mesas orgânicas
    # (16/11, usuário: "corrija essas falhas nas bordas laterais do tapete") o tapete no próprio tecido (a amostra limpa,
    # sem emenda) com a beira nítida, cobrindo o de antes e as franjas tracejadas das laterais
    import pedidos_terreo_casad_1611b as PD2
    tap_v = _tapete(Q, "varanda", out)
    _, amostra_v = tap_v
    cx_ = PD2.caixa_uniao(tap_v[0], RT.caixa_pdf(Q, PISOS_D["tapetes"]["varanda"][0]), folga=1.0)
    Pv = PD2.tapete_amostra(out, amostra_v, cx_[2] - cx_[0], cx_[3] - cx_[1])
    out = _limpa(Q, out, par, [q["sofa"], *q["poltronas"], *q["mesas_velhas"]], [tap_v, bege])
    out = PD2.tapete_novo(Q, out, par, Pv, cx_)
    out = PD2.franjas(out, par, cx_)
    _, ms = MB.contorno(Q, [q["sofa"]])
    Ps = ler(q["sofa_png"])
    cx, cy, (iou, g, wt, ht) = MB.encaixar(Q, Ps, ms, giros=(0, 180), escalas=(0.95, 1.0, 1.05))
    out = MB.pousar(out, Ps, cx, cy, wt, ht, g, "movel", par)
    meio = np.mean([c for c, _, _ in q["organicas"]], axis=0)
    Pp = ler(q["poltrona_png"])
    for i in q["poltronas"]:
        pcx, pcy, w, h = _centro(Q, i)
        lado = 0.92 * min(w, h)
        gp = round(MB.frente(meio - np.array([pcx, pcy])) / 90.0) * 90.0
        out = MB.pousar(out, Pp, pcx, pcy, lado * Pp.shape[1] / Pp.shape[0], lado, gp, "movel", par)
    Po = ler("varanda-gourmet/mesa-centro-seixo-d")
    for (ox, oy), (w, h), go in q["organicas"]:
        out = MB.pousar(out, Po, ox, oy, w, h, go, "mesa", par)
    print(f"    varanda gourmet: as 2 mesas redondas com as 12 cadeiras de fibra; o sofá curvo (giro {g:.0f}°, "
          f"{iou * 100:.0f}% sobre o do PDF; o curvo da Casa A, as almofadas em terracota), as 3 poltronas de fibra e 2 "
          "mesas orgânicas")
    return out


def gourmet(Q, out, par):
    import biblioteca_terreo_casad_1511 as TD
    with com_d({"area-gourmet/banqueta-b": "D:gourmet/banqueta-gourmet-d"}), contextlib.redirect_stdout(io.StringIO()):
        out = TD.gourmet(Q, out, par)
    print("    gourmet: como em 15/11, com as 4 banquetas altas de madeira da Casa D")
    return out


# ----------------------------------------------------------------------------------------------------------------------
# 16/11, a revisão do usuário sobre a Alternativa 1:
# - "Para as escrivaninhas dos quartos, use o tom de madeira nogueira": os tampos das escrivaninhas com cadeira (suíte
#   master, suíte 1, suíte 3/escritório; os retângulos da DOC_LINHAS E PROJEÇÕES e da mesa do escritório, px) na
#   nogueira da biblioteca da Casa A (o painel liso da mesa de centro redonda de nogueira, o veio no comprido do tampo),
#   a aresta um tom abaixo e a sombra curta; a bancada da suíte 2 (sem cadeira) fica armário.
# - "Verifica a rotação das poltronas [...] para a direção do 3D": no 3D da sala íntima ("POE 642 - CASA D - SALA
#   ÍNTIMA"), a poltrona verde fica de costas para a entrada, de frente para a mesa de centro e a janela; aqui ela vai
#   a 0° (a frente para baixo), no lugar do giro do encaixe na silhueta redonda do PDF (235°). As outras conferem com o
#   3D da sala e do quarto (as do estar do living para o meio, as do estar do jantar para a mesa redonda, as dos
#   quartos para o pufe).
# - "Esse último WC-DCE do térreo tá bem desconfigurado [...] Piso" (`wc_dce`): o banho refeito pelo PDF. O piso inteiro
#   (o miolo das paredes, fora a bancada) no Mármore Bege Bahia fosco da biblioteca da Casa D (60 x 60, na escala da
#   final), no tom e no contraste do Bege Bahia do vestiário do Subsolo (Lab casado com a amostra); por cima, a bacia Carrara dos outros
#   banhos, o chuveiro em planta na parede da direita, a folha de madeira da porta aberta e o vidro do box no desenho do
#   banho 2. A bancada de granito marrom tabaco e a cuba ficam.
ESCRIVANINHAS = {"png": "02-terreo/sala-de-estar/mesa-centro-redonda-nogueira-adorno.png",
                 "painel": (0.165, 0.55, 0.30, 0.80), "aresta": 0.78,
                 "mesas": [("suíte master", (1046.0, 1434.4, 1081.8, 1552.6)),
                           ("suíte 1", (1290.8, 1422.4, 1440.1, 1452.3)),
                           ("suíte 3/escritório", (2362.5, 1553.8, 2410.3, 1673.2))]}
WC_DCE_D = {"miolo": (2386.5, 526.8, 2476.0, 676.0), "bancada": (2386.5, 526.8, 2410.8, 621.4),
            # (16/11, usuário: "mantém o mármore bege Bahia no banheiro") o Mármore Bege Bahia fosco da biblioteca da
            # Casa D (60 x 60, a indicação dela para o banho DCE do térreo), no tom e no contraste do Bege Bahia do
            # vestiário do Subsolo aprovado (as manchas reduzidas, como nas Casas A, B e C)
            "piso_png": "04-materiais/pisos-internos/bege-bahia-fosco.png", "piso_m": 3.6,
            # (16/11, usuário: "de acordo com a recomendação no Miro, esse banho segue o mesmo piso dos outros banhos")
            # o mármore claro dos banhos 1 a 3 (a amostra limpa do banho 1 na final do Térreo, sem emenda), no lugar do
            # Bege Bahia
            "piso_amostra": ("POE642_CasaD_PH_Terreo_final_rotulos.png", (1128, 1553, 1190, 1620)),
            "amostra": ("POE642_CasaD_PH_Subsolo_final_rotulos.png", (1140, 1688, 1192, 1734)), "contraste": 1.0,
            "bacia": ("B1", "banho-1/bacia-carrara", 2449.4, 542.1, 21.0, 30.6, 0.0, "baixa", None),
            "chuveiro": (2447.2, 642.7, 2459.0, 654.5, 2476.0),
            "folha": ((2434.3, 612.5, 2476.0, 614.8), (124, 154, 188)),
            "vidro": {"x": (2386.5, 2476.0), "linhas": [(622, (189, 187, 182)), (623, (201, 199, 195)),
                                                       (624, (189, 193, 198))]}}


def _painel_nogueira(L, D, q=ESCRIVANINHAS, ss=4):
    """O tampo L x D px (o comprimento na horizontal), em ss: o painel liso da nogueira, o veio no comprido, repetido em
    espelho ao longo dele; a aresta um tom abaixo."""
    P = cv2.imread(str(AQUI.parent / "biblioteca-objetos" / q["png"]), cv2.IMREAD_UNCHANGED)
    h, w = P.shape[:2]
    a0, b0, a1, b1 = q["painel"]
    pn = np.ascontiguousarray(np.rot90(P[int(b0 * h):int(b1 * h), int(a0 * w):int(a1 * w), :3]))   # o veio deitado
    W, H = int(round(L * ss)), int(round(D * ss))
    k = H / pn.shape[0]
    pn = cv2.resize(pn, (max(1, int(round(pn.shape[1] * k))), H), interpolation=cv2.INTER_AREA)
    tiras = []
    while sum(t.shape[1] for t in tiras) < W:
        tiras.append(pn if len(tiras) % 2 == 0 else pn[:, ::-1])
    T = np.concatenate(tiras, axis=1)[:, :W].astype(np.float32)
    e = max(1, int(round(0.7 * ss)))
    T[:e] *= q["aresta"]
    T[-e:] *= q["aresta"]
    T[:, :e] *= q["aresta"]
    T[:, -e:] *= q["aresta"]
    return np.dstack([T, np.full(T.shape[:2], 255, np.float32)])


def escrivaninhas(out, par, q=ESCRIVANINHAS):
    for nome, (x0, y0, x1, y1) in q["mesas"]:
        w, h = x1 - x0, y1 - y0
        L, D, g = (w, h, 0.0) if w >= h else (h, w, 90.0)
        P = _painel_nogueira(L, D, q)
        out = MB.pousar(out, P, (x0 + x1) / 2, (y0 + y1) / 2, L, D, g, "mesa", par)
    print(f"    escrivaninhas: os tampos em nogueira ({', '.join(n for n, _ in q['mesas'])})")
    return out


def _lab_casado(T, ref, contraste):
    """T (BGR float) com a média de L, a, b de `ref` e o desvio de L dela vezes `contraste`."""
    Tl = cv2.cvtColor(np.clip(T, 0, 255).astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32)
    Rl = cv2.cvtColor(ref, cv2.COLOR_BGR2LAB).reshape(-1, 3).astype(np.float32)
    for c in range(3):
        sd_t, sd_r = float(Tl[..., c].std()) or 1.0, float(Rl[:, c].std())
        f = sd_r / sd_t * (contraste if c == 0 else 1.0)
        Tl[..., c] = (Tl[..., c] - Tl[..., c].mean()) * f + Rl[:, c].mean()
    return cv2.cvtColor(np.clip(Tl, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR).astype(np.float32)


def wc_dce(out, par, q=WC_DCE_D):
    import biblioteca_terreo_casac_1311 as BC
    import biblioteca_terreo_casad_1511 as TD
    X0, Y0, X1, Y1 = q["miolo"]
    A0, B0, A1, B1 = int(np.floor(X0)) - 1, int(np.floor(Y0)) - 1, int(np.ceil(X1)) + 1, int(np.ceil(Y1)) + 1
    h, w = B1 - B0, A1 - A0
    # o piso: o Bege Bahia fosco da biblioteca, na escala da final, casado com o do vestiário do Subsolo
    if q.get("piso_amostra"):
        import materiais_terreo_casac_1311 as MT
        arq, (ax0, ay0, ax1, ay1) = q["piso_amostra"]
        ref = cv2.imread(str(AQUI.parents[1] / "POE642_CasaD" / "renders" / arq))
        T = MT.sem_emenda(ref[ay0:ay1, ax0:ax1].astype(np.float32), h, w)
    else:
        T = cv2.imread(str(BIB_D.parent / q["piso_png"]))
        lado = int(round(q["piso_m"] * PX_M))
        T = cv2.resize(T, (lado, lado), interpolation=cv2.INTER_AREA).astype(np.float32)
        T = np.tile(T, (h // lado + 1, w // lado + 1, 1))[:h, :w]
        arq, (ax0, ay0, ax1, ay1) = q["amostra"]
        ref = cv2.imread(str(AQUI.parents[1] / "POE642_CasaD" / "renders" / arq))
        T = _lab_casado(T, ref[ay0:ay1, ax0:ax1], q["contraste"])
    # a cobertura: o miolo menos a bancada, menos as paredes do PDF (exata, em ss)
    ss = 8
    M = np.zeros((h * ss, w * ss), np.uint8)
    cv2.rectangle(M, (int(round((X0 - A0) * ss)), int(round((Y0 - B0) * ss))),
                  (int(round((X1 - A0) * ss)) - 1, int(round((Y1 - B0) * ss)) - 1), 255, -1)
    bx0, by0, bx1, by1 = q["bancada"]
    cv2.rectangle(M, (int(round((bx0 - A0) * ss)), int(round((by0 - B0) * ss))),
                  (int(round((bx1 - A0) * ss)) - 1, int(round((by1 - B0) * ss)) - 1), 0, -1)
    a = cv2.resize(M.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)
    a *= ~par[B0:B1, A0:A1]
    reg = out[B0:B1, A0:A1].astype(np.float32)
    out = out.copy()
    out[B0:B1, A0:A1] = np.clip(np.round(reg * (1 - a[..., None]) + T * a[..., None]), 0, 255).astype(np.uint8)
    # a bacia Carrara (a parede em cima), o chuveiro em planta na parede da direita
    out = RT.pousar_bib(out, RT.item_bib(*q["bacia"]), par)
    cx0, cy0, cx1, cy1, parede = q["chuveiro"]
    with contextlib.redirect_stdout(io.StringIO()):
        out = BC.chuveiros(out, par, [], [{"nome": "WC DCE", "placa_px": (cx0, cy0, cx1, cy1), "png": TD.CH_Q,
                                           "parede": (parede, "dir"), "piso": (0, -1)}])
    # a folha da porta aberta (madeira) e o vidro do box (o desenho do banho 2)
    (fx0, fy0, fx1, fy1), cor = q["folha"]
    out = TD._poligono(out, [(fx0, fy0), (fx1, fy0), (fx1, fy1), (fx0, fy1)], cor)
    vx0, vx1 = q["vidro"]["x"]
    for y, c in q["vidro"]["linhas"]:
        out[y, int(np.ceil(vx0)):int(np.floor(vx1))] = c
    out = cuba_dce(out, par)
    print("    WC DCE: refeito pelo PDF (o piso inteiro no mármore claro dos outros banhos; a bacia "
          "Carrara, o chuveiro, a folha da porta e o vidro do box; a bancada e a cuba em `cuba_dce`)")
    return out


# (16/11, usuário, sobre o WC DCE do Térreo: "Corrija essa cuba e o contorno dela na bancada [...] Tá muito feio. Preciso
# de um toque aí mais refinado") a bancada inteira no granito marrom tabaco do Subsolo (`biblioteca_subsolo_casad_1511
# .tabaco`, sem a moldura bege e as pintas grandes de antes) com a aresta da frente um tom abaixo; a cuba desenhada em
# 8x no retângulo do PDF (a borda da ARQ_REVESTIMENTOS e o bojo da ARQ_BANCADAS, px): a louça branca de sobrepor com os
# cantos arredondados, o fio cinza fino em volta, o bojo com a sombra suave nas paredes do lado da luz (que vem do alto
# à direita), o ralo, e a sombra curta da borda no granito; o misturador do PDF (o corpo junto à parede e a bica sobre o
# bojo) em cromado, com o brilho no meio e a sombra curta
CUBA_DCE = {"bancada": (2386.5, 526.8, 2410.8, 621.4), "face": 0.80, "semente": 1611,
            "borda": (2392.4, 561.2, 2409.6, 587.0), "raio_borda": 2.6,
            "bojo": (2393.7, 562.5, 2408.3, 585.7), "raio_bojo": 2.1,
            "loucas": {"borda": (243, 244, 245), "bojo": (236, 237, 239), "fio": (150, 152, 156), "aresta": (206, 208, 211),
                       "ralo": (150, 154, 158)},
            "ralo": (2401.0, 574.1, 1.1),
            "corpo": (2389.1, 572.8, 2394.4, 575.2), "bica": (2394.4, 573.35, 2399.2, 574.65),
            "cromo": ((132, 134, 138), (232, 234, 237)), "sombra": (-0.6, 0.6, 0.6, 0.30), "ss": 8,
            "janela": (2384, 553, 2413, 595)}


def _sd_ret(X, Y, r, raio):
    """A distância com sinal (px) ao retângulo de cantos arredondados `r` (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = r
    cx, cy, hx, hy = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2 - raio, (y1 - y0) / 2 - raio
    qx, qy = np.abs(X - cx) - hx, np.abs(Y - cy) - hy
    return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - raio


def cuba_dce(out, par, q=CUBA_DCE):
    import biblioteca_subsolo_casad_1511 as SD
    import biblioteca_terreo_casad_1511 as TD
    # a bancada no granito marrom tabaco, a aresta da frente um tom abaixo
    x0, y0, x1, y1 = q["bancada"]
    X0, Y0, X1, Y1 = int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))
    m = np.zeros(par.shape, bool)
    m[Y0:Y1, X0:X1] = True
    m &= ~par
    out = TD._pinta_textura(out, m, SD.tabaco(Y1 - Y0, X1 - X0, q["semente"]), None)
    out = TD._poligono(out, [(x1 - 0.8, y0), (x1, y0), (x1, y1), (x1 - 0.8, y1)],
                       tuple(float(v) for v in np.median(out[Y0:Y1, X0:X1].reshape(-1, 3), axis=0) * q["face"]))
    out = TD._poligono(out, [(x0, y1 - 0.8), (x1, y1 - 0.8), (x1, y1), (x0, y1)],
                       tuple(float(v) for v in np.median(out[Y0:Y1, X0:X1].reshape(-1, 3), axis=0) * q["face"]))
    # a cuba e o misturador em 8x
    s = q["ss"]
    A0, B0, A1, B1 = q["janela"]
    w, h = (A1 - A0) * s, (B1 - B0) * s
    X, Y = np.meshgrid(A0 + (np.arange(w) + 0.5) / s, B0 + (np.arange(h) + 0.5) / s)
    base = cv2.resize(out[B0:B1, A0:A1].astype(np.float32), (w, h), interpolation=cv2.INTER_LINEAR)
    lc = {k: np.float32(v) for k, v in q["loucas"].items()}

    def mistura(img, a, cor):
        a = np.clip(a, 0, 1)[..., None]
        return img * (1 - a) + (cor if np.ndim(cor) == 3 else np.float32(cor)) * a

    def sombra(img, d_fn, forca):
        dx, dy, sig, _ = q["sombra"]
        m_ = (d_fn(X - dx, Y - dy) < 0).astype(np.float32)
        sh = cv2.GaussianBlur(m_, (0, 0), sig * s)
        return img * (1 - forca * sh)[..., None]

    def d_borda(Xs, Ys):
        return _sd_ret(Xs, Ys, q["borda"], q["raio_borda"])
    db = d_borda(X, Y)
    base = sombra(base, d_borda, q["sombra"][3]) * 1.0
    base = mistura(base, (db < 0).astype(np.float32), lc["borda"])
    base = mistura(base, (np.abs(db) < 0.28).astype(np.float32) * 0.85, lc["fio"])
    # o bojo: a sombra suave nas paredes de cima e da direita (as que dão as costas para a luz do alto à direita)
    dj = _sd_ret(X, Y, q["bojo"], q["raio_bojo"])
    bx0, by0, bx1, by1 = q["bojo"]
    perto_cima = np.clip(1 - (Y - by0) / 4.0, 0, 1)
    perto_dir = np.clip(1 - (bx1 - X) / 4.0, 0, 1)
    perto = np.clip(1 - (-dj) / 2.5, 0, 1)
    tom = 1 - 0.09 * perto - 0.12 * np.maximum(perto_cima, perto_dir) ** 1.5
    bojo = lc["bojo"][None, None] * tom[..., None]
    base = mistura(base, (dj < 0).astype(np.float32), bojo)
    base = mistura(base, (np.abs(dj) < 0.22).astype(np.float32) * 0.7, lc["aresta"])
    rx, ry, rr = q["ralo"]
    dr = np.hypot(X - rx, Y - ry)
    base = mistura(base, (dr < rr).astype(np.float32), lc["ralo"])
    base = mistura(base, (np.abs(dr - rr) < 0.2).astype(np.float32) * 0.8, lc["ralo"] * 0.75)
    # o misturador: o corpo e a bica, o cromado com o brilho no meio, a sombra curta
    c0, c1 = np.float32(q["cromo"][0]), np.float32(q["cromo"][1])
    for r_, raio in ((q["corpo"], 0.9), (q["bica"], 0.6)):
        def d_m(Xs, Ys, r_=r_, raio=raio):
            return _sd_ret(Xs, Ys, r_, raio)
        base = sombra(base, d_m, 0.35)
    for r_, raio in ((q["corpo"], 0.9), (q["bica"], 0.6)):
        d = _sd_ret(X, Y, r_, raio)
        meio = (r_[1] + r_[3]) / 2
        t = np.clip(1 - np.abs(Y - meio) / ((r_[3] - r_[1]) / 2), 0, 1) ** 0.8
        cromo = c0[None, None] + (c1 - c0)[None, None] * t[..., None]
        base = mistura(base, (d < 0).astype(np.float32), cromo)
    # a ponta da bica, um tom abaixo
    bx = q["bica"][2]
    base = mistura(base, ((np.abs(X - (bx - 0.35)) < 0.35) & (np.abs(Y - (q["bica"][1] + q["bica"][3]) / 2) < 0.6))
                   .astype(np.float32) * 0.8, c0 * 0.9)
    novo = cv2.resize(base, (A1 - A0, B1 - B0), interpolation=cv2.INTER_AREA)
    out = out.copy()
    reg = out[B0:B1, A0:A1].astype(np.float32)
    fora = par[B0:B1, A0:A1][..., None]
    out[B0:B1, A0:A1] = np.clip(np.round(np.where(fora, reg, novo)), 0, 255).astype(np.uint8)
    print("    WC DCE: a bancada no granito marrom tabaco com a aresta; a cuba branca de sobrepor redesenhada no PDF "
          "(a borda arredondada com o fio, o bojo com a sombra suave, o ralo) e o misturador cromado")
    return out

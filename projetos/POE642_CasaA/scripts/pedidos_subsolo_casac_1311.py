"""Os post-its do cliente no Subsolo da Casa C (13/11, quadro "POE 642 - Revisão de Imagens").

Sobre a final com a biblioteca (`biblioteca_subsolo_casac_1311`, commit `ANTES_COMMIT`), como os mesmos pedidos no
Subsolo da Casa B (`pedidos_subsolo_casab_1211`, de onde vêm as portas e o desenho das setas):
- **"Colocar um piso com menos manchas cinzas."** (`travertino`, a varanda do Subsolo): as manchas largas do travertino
  saem (a luz e a cor de baixa frequência levadas à mediana do piso, `forca`); o veio fino fica.
- **"Representar um filete entre os dois pisos"** (`filete`, entre o Bege Bahia do pátio e o travertino da varanda): uma
  tira de pedra de 4 cm no encontro dos dois, com os fios das bordas.
- **"Tem um pilar aqui"** (`pilar`, no alto do encontro; o PDF não o desenha): redondo, de 0,30 m, no cinza das paredes,
  como o pilar do Subsolo da Casa B.
- **"Trocar essa representação para uma escala de plantinhas menores"** (`floreira`, a floreira junto à sauna): o
  canteiro refeito com a terra, a forração miúda e plantinhas de ~0,18 m (antes, arbustos de ~0,40 m numa faixa de
  0,27 m).
- **"Colocar a seta em todas as escadas e a descrição."** (`escadas`): o triângulo cheio no 1º degrau, com a ponta para
  onde a escada sobe, o S logo abaixo dele e a descrição em duas linhas, como no Subsolo das Casas A e B: nos degraus
  largos, "SOBE PARA O / JARDIM" no pátio, acima da escada; na escada estreita (degraus 11 a 21), "SOBE PARA O / DECK"
  logo abaixo dela, sobre a hachura limpa em volta do texto.
- **"Melhorar representação das portas de giro. Encostar nas paredes."** (`portas`, `pedidos_subsolo_casab_1211.
  portas_sb`): as 3 portas de giro (sauna, BH academia e depósito) com a folha de madeira clara, o veio no comprido, o
  contorno e a sombra curta, quina com quina na ponta da parede; os marcos saem (a parede vai até a folha) e o vão fica
  com a soleira de travertino; a do depósito, numa parede deitada, feita na imagem transposta.
- **"Fazer as mesmas mudanças que foram apontadas no subsolo da casa A e que cabem para essa casa"**: as que cabem já
  estão (os chuveiros desenhados, as louças sem caixa, os aparelhos da academia no tamanho da Casa A, BH nos rótulos) ou
  entram aqui (a seta com o S e a descrição, as portas quina com quina e as pontas de parede retas nos portais).

  python3 pedidos_subsolo_casac_1311.py [--antes <png>] [--saida <png>]
"""

import argparse
import contextlib
import io
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import final3840_casaa as FA                     # noqa: E402
import final3840_casab as F                      # noqa: E402
import final3840_casac as C                      # noqa: E402
import biblioteca_subsolo_casaa_1211 as BS       # noqa: E402

CASA_C = AQUI.parents[1] / "POE642_CasaC"
R = CASA_C / "renders"
FINAL = R / "POE642_CasaC_PH_Subsolo_final_rotulos.png"
RAIZ_GIT = AQUI.parents[2]
ANTES_COMMIT = "6ea1bc3"

# a varanda do Subsolo (px): o retângulo do travertino, a força e o sigma da baixa frequência que sai
TRAVERTINO = {"px": (637, 321, 1064, 737), "sigma": (28.0, 2.5), "forca": 0.75, "texto": 0.80}
# o encontro do Bege Bahia com o travertino (px): x, de y0 a y1; a largura (m), a cor da pedra e a dos fios (BGR)
FILETE = {"x": 636.4, "y0": 320.0, "y1": 737.0, "larg_m": 0.04, "cor": (118, 128, 138), "fio": (88, 96, 104),
          "ss": 8}
PILAR = {"centro_px": (636.4, 329.5), "diam_m": 0.30, "cor": (80, 80, 80), "ss": 8}
# a floreira junto à sauna (`final3840_casac.FLOREIRA_S`): plantinhas de `d_m`, a cada `passo` (fração da altura)
FLOREIRA = {"d_m": (0.16, 0.20), "passo": 0.056, "forracao_m": (0.09, 0.14), "forracao_passo_m": 0.07, "semente": 1311}
# as escadas: o triângulo (px, a ponta para onde sobe), a letra (centro x, topo y) e a descrição (linhas, centro x, base
# da 1ª linha, a entrelinha e o fundo branco em volta para a hachura)
ESCADAS = [
    {"nome": "degraus largos", "triangulo": [(509.0, 740.5), (519.0, 740.5), (514.0, 749.5)],
     "s_px": (505, 744, 525, 765), "s_fonte": (25, 0), "letra_topo": 751.5,
     "texto": ("SOBE PARA O", "JARDIM"), "centro_x": 514.0, "base_y": 711.0, "fundo": None},
    {"nome": "escada estreita", "triangulo": [(697.0, 1001.0), (697.0, 1012.0), (707.5, 1006.5)],
     "s_px": None, "texto": ("SOBE PARA O", "DECK"), "centro_x": 762.0, "base_y": 1090.0, "fundo": (255, 255, 255)},
]
COR_SETA = (30, 30, 30)
ENTRELINHA = 20
# as portas de giro (`pedidos_subsolo_casab_1211.PORTAS_SB`, px): a parede (as faces), as pontas do PDF, a folha aberta,
# a dobradiça (topo ou base) e o lado para onde abre; a do depósito na imagem transposta (x e y trocados)
PORTAS = {
    "portas": [
        {"nome": "sauna", "parede": (813.5, 822.4), "topo": 750.5, "base": 798.3,
         "folha": (822.4, 792.9, 864.2, 795.3), "dobra": "base", "lado": +1, "soleira": True},
        {"nome": "BH academia", "parede": (888.1, 897.1), "topo": 750.5, "base": 804.2,
         "folha": (897.1, 753.5, 944.8, 755.9), "dobra": "topo", "lado": +1, "soleira": True},
    ],
    "soleira_px": (815, 762, 821, 788),
    "transpostas": [
        {"nome": "depósito", "parede": (737.1, 746.0), "topo": 998.6, "base": 1052.3,
         "folha": (746.0, 1001.5, 793.8, 1003.9), "dobra": "topo", "lado": +1, "soleira": True},
    ],
}
ANTES_DEPOIS = {"varanda_filete_pilar": (600, 300, 1080, 760), "floreira_escadas": (355, 690, 900, 1120),
                "portas": (780, 725, 1080, 830)}


def quadro():
    if "Q" not in _Q:
        with contextlib.redirect_stdout(io.StringIO()):
            C.contexto_c()
            _Q["Q"] = F.Quadro("Subsolo")
    return _Q["Q"]


_Q = {}


def _alfa_poligono(pts, X0, Y0, w, h, ss=8):
    m = np.zeros((h * ss, w * ss), np.uint8)
    cv2.fillPoly(m, [np.int32(np.round((np.float32(pts) - [X0, Y0]) * ss))], 255, cv2.LINE_AA)
    return cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)


def _pintar(out, a, X0, Y0, cor):
    h, w = a.shape
    reg = out[Y0:Y0 + h, X0:X0 + w].astype(np.float32)
    out[Y0:Y0 + h, X0:X0 + w] = np.clip(np.round(reg * (1 - a[..., None]) + np.float32(cor) * a[..., None]), 0,
                                        255).astype(np.uint8)
    return out


# ----------------------------------------------------------------------------------------------------------------------
def travertino(out, q=TRAVERTINO):
    """As manchas largas do travertino da varanda saem: a baixa frequência (média normalizada no piso, sem o texto) vai
    à mediana do piso, com `forca`; o veio fino e o texto ficam."""
    x0, y0, x1, y1 = q["px"]
    reg = out[y0:y1, x0:x1].astype(np.float32)
    lum = reg.mean(axis=2)
    med = float(np.median(lum))
    piso = lum > q["texto"] * med
    piso = cv2.erode(piso.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    # as manchas são faixas deitadas (o veio do travertino): a média normalizada esticada na horizontal
    sx, sy = q["sigma"]
    m = piso.astype(np.float32)
    num = cv2.GaussianBlur(reg * m[..., None], (0, 0), sigmaX=sx, sigmaY=sy)
    den = cv2.GaussianBlur(m, (0, 0), sigmaX=sx, sigmaY=sy)[..., None]
    L = num / np.maximum(den, 1e-4)
    alvo = np.median(reg[piso], axis=0)
    reg += q["forca"] * (alvo[None, None] - L)
    out[y0:y1, x0:x1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    print(f"    varanda: as manchas largas do travertino saem (BGR mediano {np.round(alvo).astype(int)}, força "
          f"{q['forca']})")
    return out


def filete(Q, out, q=FILETE):
    w = q["larg_m"] * Q.px_m
    x, y0, y1 = q["x"], q["y0"], q["y1"]
    X0, Y0 = int(np.floor(x - w)) - 2, int(np.floor(y0))
    W, H = int(np.ceil(2 * w)) + 4, int(np.ceil(y1 - y0))
    a = _alfa_poligono([(x - w / 2, y0), (x + w / 2, y0), (x + w / 2, y1), (x - w / 2, y1)], X0, Y0, W, H, q["ss"])
    out = _pintar(out, a, X0, Y0, q["cor"])
    for xf in (x - w / 2, x + w / 2):                     # os fios das bordas
        a = _alfa_poligono([(xf - 0.3, y0), (xf + 0.3, y0), (xf + 0.3, y1), (xf - 0.3, y1)], X0, Y0, W, H, q["ss"])
        out = _pintar(out, a * 0.8, X0, Y0, q["fio"])
    print(f"    o filete de pedra entre o Bege Bahia e o travertino ({w:.1f} px), de y {y0:.0f} a {y1:.0f}")
    return out


def pilar(Q, out, q=PILAR):
    ss = q["ss"]
    cx, cy = q["centro_px"]
    r = q["diam_m"] * Q.px_m / 2
    x0, y0 = int(cx - r) - 2, int(cy - r) - 2
    w = h = int(2 * r) + 5
    m = np.zeros((h * ss, w * ss), np.uint8)
    cv2.circle(m, (int(round((cx - x0) * ss)), int(round((cy - y0) * ss))), int(round(r * ss)), 255, -1, cv2.LINE_AA)
    a = cv2.resize(m.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)
    out = _pintar(out, a, x0, y0, q["cor"])
    print(f"    o pilar redondo de {q['diam_m']:.2f} m no alto do encontro dos pisos, em ({cx:.0f}, {cy:.0f})")
    return out


def floreira(Q, img, q=FLOREIRA):
    """O canteiro da floreira (`final3840_casac.floreira_s`) com a forração miúda e as plantinhas menores."""
    qs = C.FLOREIRA_S
    fl = Q.cor([C.FLOREIRA_COR], tol=6).astype(np.uint8)
    x0, y0, x1, y1 = qs["caixa"]
    m = np.zeros_like(fl)
    m[y0 - 2:y1 + 2, x0 - 2:x1 + 2] = fl[y0 - 2:y1 + 2, x0 - 2:x1 + 2]
    a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.5) * m
    rng = np.random.default_rng(q["semente"])
    plantas = []
    tipos = ("arbusto_1", "arbusto_2", "arbusto_3")
    n = int(round(1 / q["passo"]))
    for i in range(n):
        v = (i + 0.5) / n + rng.uniform(-0.15, 0.15) * q["passo"]
        u = 0.5 + (0.12 if i % 2 else -0.12) + rng.uniform(-0.05, 0.05)
        plantas.append((tipos[i % 3], float(rng.uniform(*q["d_m"])), (float(u), float(v)), int(rng.integers(0, 4)) * 90))
    cfg = {"terra": C.JARDINS_C["terra"], "terra_ruido": C.JARDINS_C["terra_ruido"],
           "forracao": dict(C.JARDINS_C["forracao"], d_m=q["forracao_m"], passo_m=q["forracao_passo_m"]),
           "plantas": plantas, "transbordo_m": 0.0, "semente": q["semente"]}
    B, AJ = F.B, F.AJ
    with F.em_quadro(Q):
        AJ.base_terreo, base = (lambda forma, c="Terreo": cv2.resize(Q.chapada, (forma[1], forma[0]),
                                                                      interpolation=cv2.INTER_NEAREST)), AJ.base_terreo
        try:
            r = B.mascara_pdf
            B.mascara_pdf = lambda chave, forma, **kw: r("Subsolo", forma, **kw)
            with contextlib.redirect_stdout(io.StringIO()):
                out = B.canteiro(np.ascontiguousarray(img.copy()), a, (x0, y0, x1, y1), cfg, Q.px_m,
                                 "floreira da sauna")
        finally:
            B.mascara_pdf = r
            AJ.base_terreo = base
    # o canteiro só dentro da floreira (ele refazia também o entorno: os degraus, o rótulo da sauna, o S da escada)
    dentro = cv2.dilate((a > 0.01).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    fim = img.copy()
    fim[dentro] = out[dentro]
    print(f"    floreira: {len(plantas)} plantinhas de {q['d_m'][0]:.2f} a {q['d_m'][1]:.2f} m e a forração miúda")
    return fim


def escadas(out, qs=ESCADAS):
    from PIL import ImageFont
    from rodape_entrega import FONTES
    from cliente_subsolo_casaa_0511 import _alfa_texto
    e = FA.ESCADA_A
    fonte = ImageFont.truetype(str(FONTES / e["fonte"]), e["corpo_px"] * 4)
    for q in qs:
        # o S de antes sai (o degrau logo ao lado, na mesma linha) e volta logo abaixo da seta
        if q["s_px"] is not None:
            x0, y0, x1, y1 = q["s_px"]
            dx, dy = q["s_fonte"]
            reg = out[y0:y1, x0:x1].astype(np.float32).mean(axis=2)
            s_ = cv2.dilate((reg < 150).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
            ys, xs = np.nonzero(s_)
            out[ys + y0, xs + x0] = out[ys + y0 + dy, xs + x0 + dx]
            pts = np.float32(q["triangulo"])
            cx = float(pts[:, 0].min() + pts[:, 0].max()) / 2
            l_, t_, r_, b_ = fonte.getbbox("S", anchor="ls")
            ox, oy = cx - (l_ + r_) / 8, q["letra_topo"] - t_ / 4
            W, H = int((r_ - l_) / 4) + 12, e["corpo_px"] * 3
            X0, Y0 = int(ox) - 4, int(oy) - e["corpo_px"] * 2
            a = _alfa_texto("S", fonte, e["corpo_px"], ox, oy, (X0, Y0, W, H))
            out = _pintar(out, a, X0, Y0, e["cor_texto"])
        # a seta
        pts = np.float32(q["triangulo"])
        bx0, by0 = np.floor(pts.min(axis=0)).astype(int) - 2
        bx1, by1 = np.ceil(pts.max(axis=0)).astype(int) + 3
        out = _pintar(out, _alfa_poligono(pts, bx0, by0, bx1 - bx0, by1 - by0), bx0, by0, COR_SETA)
        # a descrição
        larg = [fonte.getlength(t) / 4 for t in q["texto"]]
        for i, (linha, lw) in enumerate(zip(q["texto"], larg)):
            tx, ly = q["centro_x"] - lw / 2, q["base_y"] + i * ENTRELINHA
            W, H = int(lw) + 12, e["corpo_px"] * 3
            X0, Y0 = int(tx) - 4, int(ly) - e["corpo_px"] * 2
            a = _alfa_texto(linha, fonte, e["corpo_px"], tx, ly, (X0, Y0, W, H))
            if q["fundo"] is not None:                    # a hachura limpa em volta do texto
                f = cv2.dilate((a > 0.02).astype(np.uint8), np.ones((7, 7), np.uint8)).astype(np.float32)
                f = cv2.GaussianBlur(f, (0, 0), 1.0)
                out = _pintar(out, np.clip(f, 0, 1), X0, Y0, q["fundo"])
            out = _pintar(out, a, X0, Y0, e["cor_texto"])
        print(f"    {q['nome']}: a seta no 1º degrau{', o S logo abaixo dela' if q['s_px'] else ''} e "
              f"\"{' / '.join(q['texto'])}\"")
    return out


def portas(Q, out, q=PORTAS):
    import pedidos_subsolo_casab_1211 as PB
    # a soleira no bege das soleiras de antes da Casa C (a mediana do vão da porta da sauna), não no cinza da Casa B
    x0, y0, x1, y1 = q["soleira_px"]
    sol = tuple(float(v) for v in np.median(out[y0:y1, x0:x1].reshape(-1, 3), axis=0))
    base = dict(PB.PORTAS_SB, tique_px=(0, 0, 0, 0), soleira=sol)
    with contextlib.redirect_stdout(io.StringIO()):
        out = PB.portas_sb(Q, out, q=dict(base, portas=q["portas"]))
        T = np.ascontiguousarray(out.transpose(1, 0, 2))
        T = PB.portas_sb(Q, T, q=dict(base, portas=q["transpostas"]))
    out = np.ascontiguousarray(T.transpose(1, 0, 2))
    nomes = [p["nome"] for p in q["portas"] + q["transpostas"]]
    print(f"    portas: {', '.join(nomes)} com a folha de madeira clara quina com quina na ponta da parede, sem os "
          "marcos, a soleira no vão")
    return out


# ----------------------------------------------------------------------------------------------------------------------
def aplicar(antes):
    Q = quadro()
    out = antes.copy()
    out = travertino(out)
    out = filete(Q, out)
    out = pilar(Q, out)
    out = floreira(Q, out)
    out = portas(Q, out)
    out = escadas(out)
    return out


def antes_depois(antes, depois):
    for nome, (x0, y0, x1, y1) in ANTES_DEPOIS.items():
        a, b = antes[y0:y1, x0:x1], depois[y0:y1, x0:x1]
        k = min(4.0, 1000 / max(a.shape[:2]))
        a = cv2.resize(a, None, fx=k, fy=k, interpolation=cv2.INTER_LANCZOS4)
        b = cv2.resize(b, None, fx=k, fy=k, interpolation=cv2.INTER_LANCZOS4)
        junto = np.hstack([a, np.full((a.shape[0], 16, 3), 255, np.uint8), b])
        topo = np.full((44, junto.shape[1], 3), 255, np.uint8)
        cv2.putText(topo, "ANTES | DEPOIS", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (40, 40, 40), 2, cv2.LINE_AA)
        arq = R / f"POE642_CasaC_PH_Subsolo_1311_postits_{nome}_antes_depois.jpg"
        cv2.imwrite(str(arq), np.vstack([topo, junto]), [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"    antes e depois: {', '.join(ANTES_DEPOIS)}")


def final_de(commit):
    dado = subprocess.run(["git", "show", f"{commit}:{FINAL.relative_to(RAIZ_GIT).as_posix()}"], cwd=RAIZ_GIT,
                          capture_output=True, check=True).stdout
    return cv2.imdecode(np.frombuffer(dado, np.uint8), cv2.IMREAD_COLOR)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--antes")
    ap.add_argument("--saida")
    a = ap.parse_args()
    antes = cv2.imread(a.antes) if a.antes else final_de(ANTES_COMMIT)
    depois = aplicar(antes)
    if a.saida:
        cv2.imwrite(a.saida, depois)
        print(f"    {a.saida}")
        return
    cv2.imwrite(str(FINAL), depois)
    print(f"    {FINAL.name}")
    antes_depois(antes, depois)


if __name__ == "__main__":
    main()

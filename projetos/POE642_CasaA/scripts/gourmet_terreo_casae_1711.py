"""Térreo da Casa E, 17/11: o bloco gourmet (o BH e o lavabo gourmet, o chuveiro de fora e os brises do lado da
gourmet), na final e direto nos 12K A e B.

1. `soleira_bh` (usuário: "tirar a soleira da porta", o BH GOURMET): a soleira clara no vão da porta (ARQ_PAREDE, o vão
   branco de 1446,4 a 1455,4) sai: o granito marrom de logo ao lado, contínuo do BH à circulação.
2. `chuveiro` (usuário: "adicionar chuveiro realista aqui, no lugar desse aí"): o círculo e o cano desenhados saem (o
   Bege Bahia de logo abaixo) e entra o chuveiro redondo da biblioteca da Casa E (`chuveiro-acqua-plus`, o do banho DCE
   1) no círculo do PDF (ARQ_LOUÇAS E METAIS, 11,8 px), com o braço cromado do PDF até a parede, a canopla e a sombra
   curta.
3. `cuba_lavabo` (usuário: "melhorar a representação da cuba e torneira lateral, ela fica de cima para baixo"): a cuba e a
   torneira desenhadas saem da bancada do LAVABO GOURMET (a pedra de logo abaixo) e entra a cuba da biblioteca do lavabo
   gourmet (`cuba-quartzo`, só a louça e o metal: `biblioteca_terreo_casaa_1211.so_louca`) em pé, no comprido da
   bancada, com a torneira do lado da parede (a lateral), no lugar da de antes.
4. `brises` (usuário: "revise os brises e os represente com primor"): as 4 lâminas do lado da gourmet (a última quase
   apagada, as outras borradas, com o brilho branco) saem (o Bege Bahia de 30 px à esquerda) e cada uma vem de novo na
   posição e no ângulo do PDF (ARQ_ELEMENTOS FIXOS: as lâminas a 45°), no desenho das lâminas da varanda (a 2ª, na
   própria imagem: o cinza com o contorno escuro), na escala do comprimento (49,5 contra 53,6 px).

  python3 gourmet_terreo_casae_1711.py doze [--opcao AB]     (antes da final: a final de antes é a referência)
  python3 gourmet_terreo_casae_1711.py final
  (--passos soleira_bh,chuveiro,cuba_lavabo,brises)
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import danae_foto as DF                                     # noqa: E402
import correcoes_terreo_casab_1611 as CB                    # noqa: E402
import instalacao_terreo_casad_1711 as ID                   # noqa: E402
from biblioteca_terreo_casaa_1211 import pousar, so_louca   # noqa: E402
from correcoes_terreo_casab_1611 import Mapa                # noqa: E402

RAIZ = AQUI.parents[1]
FINAL = RAIZ / "POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_final.png"
DOZE = RAIZ / "POE642_CasaE/entrega/POE642_CasaE_PH_Terreo_12K_opcao_{}.jpg"
BIB = RAIZ / "POE642_CasaE/biblioteca-objetos/02-terreo"

SOLEIRA_BH = {"ret": (1446.4, 496.3, 1455.4, 550.0), "folga": 1.2, "d": (14, 0), "caixa": (1420, 480, 1480, 570)}
CHUVEIRO = {"limpa": (944.5, 554.0, 977.5, 575.5), "limpa_d": (0, 22), "caixa": (930, 530, 1000, 600),
            "cabeca": (954.7, 564.6), "diam": 11.8, "png": BIB / "banho-dce-1/chuveiro-acqua-plus.png",
            "braco": (957.0, 563.9, 977.1, 565.3), "canopla": (976.0, 562.3, 977.7, 566.9),
            "cromo": (206, 208, 211), "cromo_brilho": (238, 239, 241), "cromo_borda": (118, 121, 126),
            "sombra": [{"dx": 0.02, "dy": 0.03, "sig": 0.02, "forca": 0.28}]}
CUBA = {"limpa": (988.6, 511.5, 1014.4, 549.5), "limpa_d": (0, 45), "caixa": (975, 495, 1025, 600),
        "png": BIB / "lavabo-gourmet/cuba-quartzo.png", "centro": (1001.6, 530.5), "fundo": 21.0,
        "sombra": [{"dx": 0.01, "dy": 0.015, "sig": 0.012, "forca": 0.22}]}
# as lâminas (centro, comprimento) do PDF; o modelo: a 2ª lâmina da varanda
BRISES = {"laminas": [((999.69, 671.94), 49.32), ((1000.0, 723.0), 49.5), ((999.73, 774.5), 49.53),
                      ((999.8, 825.84), 49.69)],
          "modelo": ((1224.25, 1334.38), 53.56), "raio": 30, "meia_larg": 6.0,
          "limpa_d": (-30, 0), "caixa": (960, 630, 1045, 860), "caixa_modelo": (1185, 1290, 1265, 1380)}


def _local(out, mp, caixa):
    return mp.local(out, caixa) if mp.ref is not None else mp


def soleira_bh(out, mp, q=SOLEIRA_BH):
    """O vão no granito sem emenda (usuário, depois do 1º remendo: "não pode ficar linha aqui"): a luz baixa vem do
    piso em volta (o inpaint dos dois lados, borrado), o grão do granito de logo ao lado, e a borda some aos poucos
    nos dois lados (as faces da soleira de antes também)."""
    m = _local(out, mp, q["caixa"])
    s = m.s
    x0, y0, x1, y1 = q["ret"]
    e = q["folga"]
    rm = m.ret((x0 - e, y0, x1 + e, y1))
    X0, Y0 = int(np.floor(rm[0])) - int(np.ceil(3 * s)), int(np.floor(rm[1]))
    X1, Y1 = int(np.ceil(rm[2])) + int(np.ceil(3 * s)), int(np.ceil(rm[3]))
    reg = np.ascontiguousarray(out[Y0:Y1, X0:X1])
    from janela_pia_casaa_1611 import alfa_ret
    a = alfa_ret((rm[0] - X0, 0, rm[2] - X0, Y1 - Y0), reg.shape[:2])
    mask = (a > 0.01).astype(np.uint8) * 255
    sig = 2.0 * s
    # a luz baixa só do piso (a parede e a folha da porta, escuras ou cinza, não entram na média)
    inp = cv2.inpaint(reg, mask, max(3, int(round(4 * s))), cv2.INPAINT_TELEA).astype(np.float32)
    Lr = inp.mean(axis=2)
    crr = inp.max(axis=2) - inp.min(axis=2)
    w = ((Lr > 90) & (crr > 18)).astype(np.float32)
    baixa = cv2.GaussianBlur(inp * w[..., None], (0, 0), sig) / np.maximum(cv2.GaussianBlur(w, (0, 0), sig),
                                                                             1e-3)[..., None]
    dx = int(round(q["d"][0] * s))
    fonte = out[Y0:Y1, X0 + dx:X1 + dx].astype(np.float32)
    grao = fonte - cv2.GaussianBlur(fonte, (0, 0), sig)
    af = cv2.GaussianBlur(a, (0, 0), 0.8 * s, sigmaY=0.01)[..., None]
    af = np.maximum(af, a[..., None] * (a[..., None] > 0.99))
    novo = reg.astype(np.float32) * (1 - af) + (baixa + grao) * af
    out[Y0:Y1, X0:X1] = np.clip(np.round(novo), 0, 255).astype(np.uint8)
    print("    BH gourmet: a soleira da porta saiu (o granito marrom contínuo, sem emenda)")


def _destoa(lim=8, croma_min=25):
    def f(reg):
        L = reg.mean(axis=2)
        cr = reg.max(axis=2) - reg.min(axis=2)
        return (np.abs(L - float(np.median(L))) > lim) | (cr < croma_min)
    return f


def _png(caminho):
    P = cv2.imread(str(caminho), cv2.IMREAD_UNCHANGED).astype(np.float32)
    ys, xs = np.nonzero(P[..., 3] > 0)
    return np.ascontiguousarray(P[ys.min():ys.max() + 1, xs.min():xs.max() + 1])


def chuveiro(out, mp, q=CHUVEIRO):
    m = _local(out, mp, q["caixa"])
    s = m.s
    ID._remenda(out, m, q["limpa"], [q["limpa_d"]], _destoa(), 30)
    # o braço e a canopla, cromados (o fio escuro, o corpo e o brilho em cima)
    x0, y0, x1, y1 = q["braco"]
    e = 0.35
    CB.pintar(out, m, [((x0 - e, y0 - e, x1, y1 + e), "ret", q["cromo_borda"], 0),
                       ((x0, y0, x1, y1), "ret", q["cromo"], 0),
                       ((x0, y0 + 0.15, x1, y0 + 0.6), "ret", q["cromo_brilho"], 0)])
    cx0, cy0, cx1, cy1 = q["canopla"]
    CB.pintar(out, m, [((cx0 - e, cy0 - e, cx1, cy1 + e), "ret", q["cromo_borda"], 0),
                       ((cx0, cy0, cx1, cy1), "ret", q["cromo"], 0)])
    # a cabeça, da biblioteca, no círculo do PDF
    P = _png(q["png"])
    cx, cy = q["cabeca"]
    d = q["diam"] * s
    o = out.astype(np.float32)
    pousar(o, P, m.x(cx) - 0.5, m.y(cy) - 0.5, d, d * P.shape[0] / P.shape[1], 0.0, q["sombra"], DF.PX_M * s)
    out[...] = np.clip(np.round(o), 0, 255).astype(np.uint8)
    print("    chuveiro de fora: o redondo da biblioteca no círculo do PDF, com o braço cromado até a parede")


def cuba_lavabo(out, mp, q=CUBA):
    m = _local(out, mp, q["caixa"])
    s = m.s
    ID._remenda(out, m, q["limpa"], [q["limpa_d"]], _destoa(6, 0), 30)
    P = so_louca(_png(q["png"]), croma=12)          # só o branco da louça e o metal (sem o creme da pedra)
    h, w = P.shape[:2]
    # a imagem com a torneira em cima: girada 90° (anti-horário), a torneira vai para a esquerda, a parede
    fundo = q["fundo"] * s                       # a profundidade da peça (da torneira à frente), na bancada
    cx, cy = q["centro"]
    o = out.astype(np.float32)
    pousar(o, P, m.x(cx) - 0.5, m.y(cy) - 0.5, fundo * w / h, fundo, 90.0, q["sombra"], DF.PX_M * s)
    out[...] = np.clip(np.round(o), 0, 255).astype(np.uint8)
    print("    lavabo gourmet: a cuba da biblioteca em pé, a torneira na lateral (do lado da parede)")


def brises(out, mp, q=BRISES):
    m = _local(out, mp, q["caixa"])
    mm = _local(out, mp, q["caixa_modelo"])
    s = m.s
    # o modelo: a lâmina da varanda, com o alfa pelo croma (o cinza da lâmina contra o Bege)
    (tx, ty), tl = q["modelo"]
    R = int(np.ceil(q["raio"] * s))
    TX, TY = mm.x(tx) - 0.5, mm.y(ty) - 0.5
    X0, Y0 = int(round(TX)) - R, int(round(TY)) - R
    pat = out[Y0:Y0 + 2 * R + 1, X0:X0 + 2 * R + 1].astype(np.float32)
    cr = pat.max(axis=2) - pat.min(axis=2)
    yy, xx = np.mgrid[0:2 * R + 1, 0:2 * R + 1].astype(np.float32)
    u, v = xx + X0 - TX, yy + Y0 - TY
    perp = np.abs(u - v) / np.sqrt(2)              # a lâmina vai de cima-esquerda a baixo-direita (45°)
    longo = np.abs(u + v) / np.sqrt(2)
    zona = (perp < q["meia_larg"] * s) & (longo < (tl / 2 + 3) * s)
    a = np.clip((32.0 - cr) / 18.0, 0, 1) * zona
    piso = np.median(pat[(cr > 34) & ~zona], axis=0)
    cor = np.where(a[..., None] > 0.05, (pat - (1 - a[..., None]) * piso) / np.maximum(a[..., None], 0.05), piso)
    modelo = np.dstack([np.clip(cor, 0, 255) * a[..., None], a])      # pré-multiplicado
    for (cx, cy), ln in q["laminas"]:
        # a de antes sai (o Bege de 30 px à esquerda: longe dela e das vizinhas)
        h = ln / (2 * np.sqrt(2)) + 4              # a meia caixa da lâmina a 45° (o piso marrom ao lado fica)
        r = (cx - h, cy - h, cx + h, cy + h)
        ID._remenda(out, m, r, [q["limpa_d"]], _destoa(8, 25), 30)
        k = ln / tl
        PX, PY = m.x(cx) - 0.5, m.y(cy) - 0.5
        M = np.float32([[k, 0, PX - k * (TX - X0)], [0, k, PY - k * (TY - Y0)]])
        L = int(np.ceil((R * 2 + 1) * k)) + 4
        bx, by = int(np.floor(PX)) - L // 2, int(np.floor(PY)) - L // 2
        M[0, 2] -= bx
        M[1, 2] -= by
        w = cv2.warpAffine(modelo, M, (L, L), flags=cv2.INTER_LINEAR, borderValue=0)
        reg = out[by:by + L, bx:bx + L].astype(np.float32)
        al = w[..., 3:4]
        out[by:by + L, bx:bx + L] = np.clip(np.round(reg * (1 - al) + w[..., :3]), 0, 255).astype(np.uint8)
    print(f"    brises da gourmet: as {len(q['laminas'])} lâminas do PDF no desenho das da varanda")


PASSOS = ("soleira_bh", "chuveiro", "cuba_lavabo", "brises")


def aplicar(img, mp, passos=PASSOS):
    out = img.copy()
    for p in PASSOS:
        if p in passos:
            globals()[p](out, mp)
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

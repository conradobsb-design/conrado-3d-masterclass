"""Térreo da Casa E, 18/11, na final e direto nos 12K A (Inter) e B (Kalam): a escada do Subsolo invertida (usuário:
"Pode inverter a escada no térreo, para ficar coerente, sim"). Pelo PDF do Térreo, a escada começa a descer no degrau
17, à direita (o "D" do PDF ali, a seta para a esquerda), e é desenhada inteira, sem corte; no Subsolo, o mesmo lance
sobe do degrau 1, à esquerda. O Térreo aprovado tinha o ▶ D no degrau 1, apontando para a direita, o alto à esquerda e,
depois da diagonal, o resto sob o véu.

1. `degraus`: os 17 degraus inteiros, no travertino da escada, sem a diagonal e sem o véu; o sombreamento das escadas
   aprovadas (`final3840_casab.ESCADA_SOMBRA`) no sentido novo: o degrau 1 (à esquerda) o mais escuro (0,84) e o 17 (à
   direita, no nível do Térreo) o mais claro (1,0), cada um com o tom dele (semente 2812, a da escada), e a sombra curta
   de cada espelho no degrau de baixo, agora junto à borda DIREITA de cada degrau (o de cima fica à direita); o 17, o
   de cima, sem sombra. O travertino vem dos degraus 2 a 5 da final (os inteiros, sem marca e longe da diagonal): a
   sombra do espelho de antes (na borda esquerda) sai pelo mesmo modelo (e o fio dela, os 3 px junto à borda, fica de
   fora: o degrau novo é tirado do resto da fonte, um pouco esticado), e o degrau é levado ao tom novo.
2. `seta`: o ◀ no degrau 17 (o triângulo das escadas, 13 x 15 px, cinza 30) e o D embaixo dele (Inter SemiBold 17 px,
   cinza 45, `final3840_casaa_terreo.letra`), no meio do degrau 17 do PDF (pt 1244 a 1262,9).
3. `descricao`: o "DESCE PARA O / SUBSOLO" sai da esquerda da escada (o Bege Bahia de volta, como em
   `descricao_subsolo_terreo_casae_1711`) e vai para a direita do triângulo, fora da escada, na circulação gourmet: a
   ~8 px da borda da escada, no meio da altura do triângulo e do D, em branco (236), como os rótulos no granito marrom;
   no 12K B na Kalam, e o JSON da Kalam atualizado (o centro e a cor).

4. `veu` (depois, usuário: "Lembrar que tem a parte que a gente deixa transparente em virtude de já estar na altura do
   pavimento inferior"): a diagonal de corte do PDF do Subsolo, o mesmo lance, e os degraus de baixo dela (1 a 7, já na
   altura do Subsolo) sob o véu claro do Subsolo (38%, cinza 236, rampa de 1,5 px), o espelho de lá; os de cima (8 a
   17, junto ao Térreo, com o ◀ D) inteiros.

  python3 escada_subsolo_terreo_casae_1811.py doze [--opcao AB]     (antes da final: a final de antes é a referência)
  python3 escada_subsolo_terreo_casae_1811.py final
  (o véu sozinho, nas imagens que já tinham a escada invertida: `doze --so-veu` e depois `final --so-veu`)
"""
import argparse
import contextlib
import io
import json
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import danae_foto as DF                                     # noqa: E402
import descricao_subsolo_terreo_casae_1711 as D17           # noqa: E402
import escada_painel_casae_1711 as EP                       # noqa: E402
from correcoes_terreo_casab_1611 import Mapa                # noqa: E402

RAIZ = AQUI.parents[1]
FINAL = RAIZ / "POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_final.png"
DOZE = RAIZ / "POE642_CasaE/entrega/POE642_CasaE_PH_Terreo_12K_opcao_{}.jpg"
KALAM = EP.KALAM

# px da final (o PDF do Térreo, ARQ_ESCADAS: a caixa pt 972 a 1262,9 x 617 a 685, os bocéis a cada 17 pt; o último
# degrau tem 18,9 pt)
ESCADA = {"x0": 1150.84, "p": 17.905, "x_fim": 1457.21, "y": (411.30, 482.92), "n": 17,
          # os degraus da final de onde vem o travertino (0 = o da esquerda; o 0 tem o ▶ D, do 6 em diante a diagonal)
          "fontes": (1, 2, 3, 4),
          # qual fonte vai em cada degrau novo (da esquerda para a direita; nunca a mesma em dois vizinhos)
          "ordem": (2, 4, 1, 3, 2, 1, 4, 3, 1, 2, 4, 3, 2, 4, 1, 3, 2),
          # o tom 1,0: o degrau 0 da final (o alto de antes, sem sombra de espelho), nas linhas abaixo do D
          "base_linhas": (456.0, 481.0),
          # da fonte, só o que fica depois do fio do espelho de antes (px da final a partir da borda esquerda dela)
          "pula": 3.0,
          "tom": (0.84, 1.0), "tom_degrau": 0.02, "espelho": (0.34, 2.4), "semente": 2812,
          # (depois, usuário: "Lembrar que tem a parte que a gente deixa transparente em virtude de já estar na altura do
          # pavimento inferior") a diagonal de corte do PDF do Subsolo (o mesmo lance) e, do lado de baixo dela (os degraus
          # 1 a 7, já na altura do Subsolo), o véu do Subsolo (38%, no claro 236, rampa de 1,5 px), o espelho de lá: no
          # Subsolo o véu fica depois da diagonal (os degraus de cima), aqui antes dela
          "corte": ((1258.1, 411.3), (1294.2, 482.9)), "veu": 0.38, "veu_cor": (236, 236, 236), "rampa_px": 1.5,
          "tri": (1447.0, 430.0), "tri_tam": (13.0, 15.0), "tri_cor": (30, 30, 30),
          "letra": ("D", (1447.26, 447.11)),
          "caixa": (1040, 340, 1600, 500)}
DESCE = dict(D17.DESCE, centro=(1504.5, 437.5), cor=(236, 236, 236), velho=(1058, 420, 1149, 456))


def _sombra(d, s, q):
    """O fator da sombra curta de um espelho a `d` px (da imagem) dele."""
    fs, alc = q["espelho"]
    return 1 - fs * np.exp(-np.maximum(d, 0) / (alc * s))


def degraus(out, m, q=ESCADA):
    s = m.s
    orig = out.copy()
    bord = [q["x0"] + i * q["p"] for i in range(q["n"])] + [q["x_fim"]]
    B = np.array([m.x(b) for b in bord])
    r0, r1 = int(np.floor(m.y(q["y"][0]))), int(np.ceil(m.y(q["y"][1])))
    c0, c1 = int(np.ceil(B[0])), int(np.floor(B[-1]))
    ri0, ri1 = int(np.ceil(m.y(q["y"][0] + 2))), int(np.floor(m.y(q["y"][1] - 2)))    # as linhas de dentro

    def borda_fonte(j):
        return m.x(q["x0"] + j * q["p"]), m.x(q["x0"] + (j + 1) * q["p"])

    # o tom de cada fonte, sem a sombra do espelho de antes (na borda esquerda), e o tom 1,0
    meds = {}
    for j in q["fontes"]:
        L, R = borda_fonte(j)
        cs = np.arange(int(np.ceil(L + 0.3 * (R - L))), int(np.floor(L + 0.95 * (R - L))))
        reg = orig[ri0:ri1, cs].astype(np.float32) / _sombra(cs + 0.5 - L, s, q)[None, :, None]
        meds[j] = np.median(reg.reshape(-1, 3), axis=0)
    L0, R0 = borda_fonte(0)
    cs = np.arange(int(np.ceil(L0 + 0.15 * (R0 - L0))), int(np.floor(L0 + 0.85 * (R0 - L0))))
    rb0, rb1 = int(round(m.y(q["base_linhas"][0]))), int(round(m.y(q["base_linhas"][1])))
    base = np.median(orig[rb0:rb1, cs].astype(np.float32).reshape(-1, 3), axis=0)

    rng = np.random.default_rng(q["semente"])
    tons = 1 + rng.uniform(-q["tom_degrau"], q["tom_degrau"], q["n"])
    t0, t1 = q["tom"]
    f = (t0 + (t1 - t0) * np.arange(q["n"]) / (q["n"] - 1)) * tons

    cols = np.arange(c0, c1)
    xc = cols + 0.5
    k = np.clip(np.searchsorted(B, xc) - 1, 0, q["n"] - 1)
    o = (xc - B[k]) / (B[k + 1] - B[k])
    j = np.array(q["ordem"])[k]
    LR = np.array([borda_fonte(int(jj)) for jj in j])
    xs = LR[:, 0] + q["pula"] * s + o * (LR[:, 1] - LR[:, 0] - (q["pula"] + 1.2) * s)
    des = _sombra(xs - LR[:, 0], s, q)                                       # a sombra de antes, que sai
    nova = np.where(k < q["n"] - 1, _sombra(B[k + 1] - xc, s, q), 1.0)      # a do espelho de cima, à direita
    ganho = (base[None, :] * f[k][:, None]) / np.array([meds[int(jj)] for jj in j])     # (colunas, 3)
    fator = (nova / des)[:, None] * ganho

    linhas = np.arange(r0, r1)
    mx = np.repeat((xs - 0.5)[None, :].astype(np.float32), len(linhas), axis=0)
    my = np.repeat(linhas[:, None].astype(np.float32), len(cols), axis=1)
    amostra = cv2.remap(orig, mx, my, cv2.INTER_LINEAR).astype(np.float32)
    out[r0:r1, c0:c1] = np.clip(np.round(amostra * fator[None]), 0, 255).astype(np.uint8)
    print(f"    escada do Subsolo: os 17 degraus inteiros (sem a diagonal e sem o véu), do degrau 1 a {f[0]:.2f} ao 17 "
          f"a {f[-1]:.2f}, a sombra de cada espelho junto à borda direita do degrau")


def veu(out, m, q=ESCADA, ss=4):
    """Os degraus de baixo (à esquerda da diagonal de corte, já na altura do Subsolo) sob o véu claro: transparentes no
    tom da escada, como os de cima no Subsolo."""
    (cx0, cy0), (cx1, cy1) = q["corte"]
    X0, X1 = int(np.floor(m.x(q["x0"]))) - 1, int(np.ceil(m.x(q["x_fim"]))) + 1
    Y0, Y1 = int(np.floor(m.y(q["y"][0]))) - 1, int(np.ceil(m.y(q["y"][1]))) + 1
    h, w = Y1 - Y0, X1 - X0
    yy, xx = np.mgrid[0:h * ss, 0:w * ss].astype(np.float32)
    X = m.ux(X0 + (xx + 0.5) / ss - 0.5)                     # px da final (o inverso de `m`)
    Y = (Y0 + (yy + 0.5) / ss - m.t[1]) / m.s + 0.5
    dentro = (X >= q["x0"]) & (X < q["x_fim"]) & (Y >= q["y"][0]) & (Y < q["y"][1])
    Xc = cx0 + (Y - cy0) * (cx1 - cx0) / (cy1 - cy0)
    v = np.clip((Xc - X) / q["rampa_px"] + 0.5, 0, 1) * dentro
    v = cv2.resize(v.astype(np.float32), (w, h), interpolation=cv2.INTER_AREA)[..., None] * q["veu"]
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    out[Y0:Y1, X0:X1] = np.clip(np.round(reg * (1 - v) + np.float32(q["veu_cor"]) * v), 0, 255).astype(np.uint8)
    print(f"    escada do Subsolo: os degraus de baixo (antes da diagonal de corte) sob o véu de {q['veu']:.0%}")


def seta(out, m, q=ESCADA):
    import terreo_casaa_1011 as TA
    import final3840_casaa_terreo as T
    from PIL import Image, ImageDraw, ImageFont
    from rodape_entrega import FONTES
    s = m.s
    # o triângulo: os vértices no px de centro (o `fillPoly`), como na final
    tx, ty = q["tri"]
    u, v = m.x(tx + 0.5) - 0.5, m.y(ty + 0.5) - 0.5
    comp, larg = q["tri_tam"]
    f = out.astype(np.float32)
    f = TA.triangulo(f, TA.seta_tri(u, v, (-1, 0), comp * s, larg * s), q["tri_cor"])
    out[:] = np.clip(np.round(f), 0, 255).astype(np.uint8)
    # a letra, como `final3840_casaa_terreo.letra`, no corpo da imagem
    texto, (cx, cy) = q["letra"]
    lq = T.LETRA
    corpo = lq["corpo_px"] * s
    fonte = ImageFont.truetype(str(FONTES / lq["fonte"]), int(round(corpo * 4)))
    ox, oy = m.x(cx), m.y(cy)
    W = H = int(round(corpo * 3))
    X0, Y0 = int(ox) - W // 2, int(oy) - H // 2
    t = Image.new("L", (W * 4, H * 4), 0)
    ImageDraw.Draw(t).text(((ox - X0) * 4, (oy - Y0) * 4), texto, font=fonte, fill=255, anchor="mm")
    a = np.asarray(t.resize((W, H), Image.LANCZOS), np.float32)[..., None] / 255
    reg = out[Y0:Y0 + H, X0:X0 + W].astype(np.float32)
    out[Y0:Y0 + H, X0:X0 + W] = np.clip(np.round(reg * (1 - a) + np.float32(lq["cor"]) * a), 0, 255).astype(np.uint8)
    print("    escada do Subsolo: o ◀ e o D no degrau 17, de onde se desce")


def aplicar(img, mp, kalam=None, so_veu=False):
    m = mp.local(img, ESCADA["caixa"]) if mp.ref is not None else mp
    m = Mapa(m.s, m.t)                                     # sem `ref`: o afim desta caixa vale para os passos
    out = img.copy()
    if so_veu:                                             # nas imagens que já têm a escada invertida (18/11)
        veu(out, m)
        return out
    degraus(out, m)
    veu(out, m)
    seta(out, m)
    with contextlib.redirect_stdout(io.StringIO()):         # as mensagens de lá falam da posição de 17/11
        D17.descricao(out, m, kalam, DESCE)
    print("    escada do Subsolo: a descrição à direita do triângulo, em branco no granito")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("acao", choices=("final", "doze"))
    ap.add_argument("--opcao", default="AB")
    ap.add_argument("--entrada")
    ap.add_argument("--saida")
    ap.add_argument("--so-veu", action="store_true", help="só o véu dos degraus de baixo (imagens já invertidas)")
    a = ap.parse_args()
    fin = cv2.imread(a.entrada or str(FINAL))
    if a.acao == "final":
        cv2.imwrite(a.saida or str(FINAL), aplicar(fin, Mapa(), so_veu=a.so_veu))
        if not a.saida and not a.so_veu:
            rots = json.loads(KALAM.read_text())
            for b in rots:
                if b["nome"] == DESCE["nome_kalam"]:
                    b["linhas"] = EP._linhas_kalam(DESCE)
                    b["cor"] = list(DESCE["cor"])
            KALAM.write_text(json.dumps(rots, ensure_ascii=False, indent=1) + "\n")
        return
    from PIL import Image
    for op in a.opcao:
        f = Path(str(DOZE).format(op))
        img = cv2.imread(str(f))
        M = DF.afim_12k(fin, img)
        mp = Mapa(float(np.hypot(M[0, 0], M[1, 0])), (float(M[0, 2]), float(M[1, 2])))
        mp.ref = fin
        out = aplicar(img, mp, EP._kalam_global() if op == "B" else None, so_veu=a.so_veu)
        dpi = int(round(out.shape[1] / (420 / 25.4)))
        dest = a.saida.format(op) if a.saida else str(f)
        Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB)).save(dest, quality=95, subsampling=0, dpi=(dpi, dpi))
        print(f"    {Path(dest).name}")


if __name__ == "__main__":
    main()

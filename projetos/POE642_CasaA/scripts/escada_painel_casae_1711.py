"""Térreo da Casa E, 17/11, na final e direto nos 12K A (Inter) e B (Kalam), no afim afinado em cada caixa:

1. `descricao_sobe` ("A descrição de sobe para o primeiro pavimento tem que ficar ali próximo ao S e o triângulo, de
   preferência do lado direito ... o ideal é que fique na área de circulação. Você pode até reduzir um pouco a fonte ...
   Que não fique em cima de parede nem nada"): o "SOBE PARA O / 1º PAVIMENTO" sai de junto da mesa de jantar (o piso de
   logo acima no lugar das letras) e vai para a circulação à direita do triângulo e do S (entre o fim da escada, x 2218,
   e o batente do escritório, x 2283), centrado na faixa e na altura do triângulo e do S, em duas linhas, no corpo das
   descrições x `k` (0,7: a faixa tem 62 px e a descrição inteira, 78). No 12K B, na Kalam, como as outras.
2. `painel_escritorio` ("Aqui é um painel de madeira com as ripas ... bem da forma como a gente fez o painel de madeira
   na casa D"; depois: "Não preenche com material de madeira, não. Tem a soleira da janela ... Na verdade, deixa só o
   ripado no tom amadeirado e preserva o que estava antes, com a soleira e a janela"): só as 7 ripas que saem para o
   gramado, de creme para a nogueira da Casa D (`correcoes_terreo_casad_1711._ripado`, `FOLHAS_1P`, maciça: o veio ao
   longo, a luz, o contorno e a sombra curta no gramado); a soleira e as folhas de vidro da janela ficam como estavam.

  python3 escada_painel_casae_1711.py doze [--opcao AB]     (antes da final: a final de antes é a referência)
  python3 escada_painel_casae_1711.py final
"""
import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import danae_foto as DF                                     # noqa: E402
import correcoes_terreo_casad_1711 as CD                     # noqa: E402
from correcoes_terreo_casab_1611 import Mapa                # noqa: E402

RAIZ = AQUI.parents[1]
FINAL = RAIZ / "POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_final.png"
DOZE = RAIZ / "POE642_CasaE/entrega/POE642_CasaE_PH_Terreo_12K_opcao_{}.jpg"
KALAM = RAIZ / "POE642_CasaE/renders/POE642_CasaE_PH_Terreo_rotulos_kalam.json"

# px da final
SOBE = {"texto": ("SOBE PARA O", "1º PAVIMENTO"), "corpo": 11, "k": 0.70, "centro": (2250.5, 995.0),
        "cor": (20, 20, 20), "velho": (1784, 990, 1874, 1026), "desloc_y": -30, "escuro": 40, "escuro_12k": 14,
        "caixa": (1760, 940, 2300, 1060), "nome_kalam": "escada: SOBE PARA O 1º PAVIMENTO",
        "kalam_linhas": ((9.0, 73.0), (9.0, 77.0))}
PAINEL = {"ripas": [(2488.6, y0, 2501.8, y1) for y0, y1 in ((987.6, 995.4), (1008.8, 1015.4), (1029.6, 1036.3),
                                                           (1051.6, 1057.6), (1070.8, 1078.3), (1091.8, 1099.3),
                                                           (1112.7, 1120.4))],
          "caixa": (2440, 960, 2540, 1150)}


def _fonte():
    import terreo_casaa_1011 as TA
    from rodape_entrega import FONTES
    return FONTES / TA.FA.ESCADA_A["fonte"]


def _alfa_inter(linhas, cx, ym, corpo, forma, X0, Y0, ss=4):
    """O alfa local (forma h, w com a origem em X0, Y0, px da imagem) das linhas na fonte das descrições, centradas em cx
    e com o meio do bloco em ym (px da imagem); a entrelinha de `terreo_casaa_1011.alfa_texto`."""
    from PIL import Image, ImageDraw, ImageFont
    h, w = forma
    f = ImageFont.truetype(str(_fonte()), max(4, int(round(corpo * ss))))
    entre = corpo * 1.18
    t = Image.new("L", (w * ss, h * ss), 0)
    d = ImageDraw.Draw(t)
    n = len(linhas)
    for i, ln in enumerate(linhas):
        yb = ym + (i - (n - 1) / 2) * entre
        d.text(((cx - X0) * ss, (yb - Y0) * ss), ln, font=f, fill=255, anchor="mm")
    return np.asarray(t.resize((w, h), Image.LANCZOS), np.float32) / 255


def _apagar(out, m, q):
    """As letras de antes saem: os px escuros da caixa (com 1 px a mais) recebem o piso de logo acima."""
    x0, y0, x1, y1 = m.reti(q["velho"])
    reg = out[y0:y1, x0:x1].astype(np.float32)
    L = reg.mean(-1)
    fundo = float(np.median(L))
    marca = (L < fundo - (q["escuro"] if m.s < 1.5 else q["escuro_12k"])).astype(np.uint8)
    k = max(1, int(round((0.8 if m.s < 1.5 else 1.4) * m.s)))
    marca = cv2.dilate(marca, np.ones((2 * k + 1, 2 * k + 1), np.uint8)) > 0
    dy = int(round(q["desloc_y"] * m.s))
    fonte = out[y0 + dy:y1 + dy, x0:x1]
    reg = out[y0:y1, x0:x1]
    reg[marca] = fonte[marca]
    out[y0:y1, x0:x1] = reg


def _kalam_global():
    """O fator único do corpo da Kalam do 12K B (o de `rotulos_kalam_casac.desenhar`, com os dados de antes)."""
    import rotulos_manuscritos_casaa as RM
    from PIL import ImageFont
    import rotulos_kalam_casac as K
    rots = json.loads(KALAM.read_text())
    k_alt = RM._altura_maiuscula(RM.FONTE)
    ref = ImageFont.truetype(str(RM.FONTE), 200)
    tetos = [larg / max(ref.getlength(t) * (cap * K.ALTURA / (k_alt / 200)) / 200, 1e-6)
             for b in rots for t, mx, base, cap, larg in (b["linhas"] or [])]
    return min(1.0, max(K.TETO_MIN, min(tetos) if tetos else 1.0)), k_alt, ref


def _linhas_kalam(q):
    """As linhas da descrição nova no formato da Kalam (texto, meio x, base, altura das maiúsculas, largura), px da
    final."""
    cx, ym = q["centro"]
    corpo = q["corpo"] * q["k"]
    entre = corpo * 1.18
    n = len(q["texto"])
    out = []
    for i, (t, (cap, larg)) in enumerate(zip(q["texto"], q["kalam_linhas"])):
        mid = ym + (i - (n - 1) / 2) * entre
        c = cap * q["k"]
        out.append([t, cx, round(mid + c / 2, 2), round(c, 2), round(larg * q["k"], 2)])
    return out


def _desenha_kalam(out, m, linhas, cor, glob):
    import rotulos_kalam_casac as K
    import rotulos_manuscritos_casaa as RM
    from PIL import Image, ImageDraw, ImageFont
    f_glob, k_alt, ref = glob
    ss = 4
    for t, mx, base, cap, larg in linhas:
        c = cap * K.ALTURA / (k_alt / 200)
        teto = larg / max(ref.getlength(t) * c / 200, 1e-6)
        cs = c * min(f_glob, teto) * m.s
        f = ImageFont.truetype(str(RM.FONTE), max(4, int(round(cs * ss))))
        u, v = m.x(mx), m.y(base)
        lw = f.getlength(t) / ss
        bx, by = int(u - lw / 2) - 12, int(v - cs * 1.4) - 8
        w_, h_ = int(lw) + 24, int(cs * 2.2) + 16
        tela = Image.new("L", (w_ * ss, h_ * ss), 0)
        ImageDraw.Draw(tela).text(((u - bx) * ss, (v - by) * ss), t, font=f, fill=255, anchor="ms")
        a = np.asarray(tela.resize((w_, h_), Image.LANCZOS), np.float32)[..., None] / 255
        reg = out[by:by + h_, bx:bx + w_].astype(np.float32)
        out[by:by + h_, bx:bx + w_] = np.clip(np.round(reg * (1 - a) + np.float32(cor) * a), 0, 255).astype(np.uint8)


def descricao_sobe(out, mp, kalam=None, q=SOBE):
    m = mp.local(out, q["caixa"]) if mp.ref is not None else mp
    _apagar(out, m, q)
    if kalam is not None:
        _desenha_kalam(out, m, _linhas_kalam(q), q["cor"], kalam)
    else:
        cx, ym = q["centro"]
        u, v = m.x(cx), m.y(ym)
        corpo = q["corpo"] * q["k"] * m.s
        X0, Y0 = int(u - 60 * m.s), int(v - 20 * m.s)
        w, h = int(120 * m.s), int(40 * m.s)
        a = _alfa_inter(q["texto"], u, v, corpo, (h, w), X0, Y0)[..., None]
        reg = out[Y0:Y0 + h, X0:X0 + w].astype(np.float32)
        out[Y0:Y0 + h, X0:X0 + w] = np.clip(np.round(reg * (1 - a) + np.float32(q["cor"]) * a), 0,
                                            255).astype(np.uint8)
    print("    escada: o SOBE PARA O 1º PAVIMENTO na circulação, à direita do triângulo e do S"
          + (" (Kalam)" if kalam is not None else ""))


def painel_escritorio(out, mp, q=PAINEL):
    import um_pav_casaa_1111 as U
    m = mp.local(out, q["caixa"]) if mp.ref is not None else mp
    macica = dict(U.FOLHAS_1P, junta_forca=0.0)
    for i, r in enumerate(q["ripas"]):
        CD._ripado(out, m, r, "y+", macica, np.random.default_rng(1760 + i))
    print("    escritório: as 7 ripas de fora em nogueira (a da Casa D); a soleira e a janela como estavam")


def aplicar(img, mp, kalam=None):
    out = img.copy()
    descricao_sobe(out, mp, kalam)
    painel_escritorio(out, mp)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("acao", choices=("final", "doze"))
    ap.add_argument("--opcao", default="AB")
    ap.add_argument("--saida")
    a = ap.parse_args()
    fin = cv2.imread(str(FINAL))
    if a.acao == "final":
        cv2.imwrite(a.saida or str(FINAL), aplicar(fin, Mapa()))
        if not a.saida:
            rots = json.loads(KALAM.read_text())
            for b in rots:
                if b["nome"] == SOBE["nome_kalam"]:
                    b["linhas"] = _linhas_kalam(SOBE)
            KALAM.write_text(json.dumps(rots, ensure_ascii=False, indent=1) + "\n")
        return
    from PIL import Image
    for op in a.opcao:
        f = Path(str(DOZE).format(op))
        img = cv2.imread(str(f))
        M = DF.afim_12k(fin, img)
        mp = Mapa(float(np.hypot(M[0, 0], M[1, 0])), (float(M[0, 2]), float(M[1, 2])))
        mp.ref = fin
        out = aplicar(img, mp, _kalam_global() if op == "B" else None)
        dpi = int(round(out.shape[1] / (420 / 25.4)))
        dest = a.saida.format(op) if a.saida else str(f)
        Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB)).save(dest, quality=95, subsampling=0, dpi=(dpi, dpi))
        print(f"    {Path(dest).name}")


if __name__ == "__main__":
    main()

"""Casa A Subsolo: o contorno na folha das portas do BH. FEM. e do BH. MASC. (25/11).

Usuário (com o recorte das duas folhas no 12K): "corrija o contorno para ficar na porta." No 12K a folha do render
(a barra clara, com a sombra à esquerda e embaixo) estava até 1,5 px da final à direita do lugar do PDF, e o contorno
fino (da rodada de 19/11) ficou entre as duas: metade na folha, metade no piso.

A folha do render, a sombra e o contorno saem (a pedra do próprio banho ao lado, deslocada, sem tocar a parede) e
cada folha é desenhada no padrão das esquadrias (`vidros_claros_1911`: perfil cinza claro, vidro claro e a linha fina
por fora), com o tamanho do PDF e "quina a quina" (o usuário: "quina da parede com a quina da porta"): a quina de cima
da folha, do lado da dobradiça, na quina do toco de parede — a face do toco e o pé dele medidos em cada imagem (final e
12K), porque o render desenha a parede até ~1 px da final fora do PDF. Final (e a manuscrita), prancha e 12K A e B.

  python3 folhas_bh_subsolo_casaa_2511.py
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import esquadrias_pretas_1911 as EP  # noqa: E402
import vidros_claros_1911 as VC  # noqa: E402
from subsolo_casaa_juncao_portas_2511 import copiar  # noqa: E402

PLANTA = "A_Subsolo"
COMPR, ESP = 53.7, 2.4                  # a folha do PDF (px da final)
# lado da dobradiça (+1: a folha à direita da face da parede; -1: à esquerda), semente dentro do toco de parede,
# faixa das linhas dentro da espessura da parede, caixa do que sai (folha antiga, sombra e contorno) e o deslocamento
# da pedra que entra no lugar — px da final
FOLHAS = {
    "fem": dict(lado=+1, semente=(1491.0, 1508.0), busca=(1490.0, 1504.0), caixa=(1490.3, 1503.0),
                desloc=(14.0, 0.0)),
    "masc": dict(lado=-1, semente=(1867.0, 1508.0), busca=(1856.0, 1869.0), caixa=(1856.5, 1869.2),
                 desloc=(-14.0, 0.0)),
}
LINHAS_PAREDE = (1507.5, 1513.0)        # dentro da espessura da parede (acima do pé)
TOPO_LIMPA = 1513.8                     # o que sai começa logo abaixo da faixa da junção (a parede fica protegida)
TOPO_BUSCA, FUNDO = 1509.0, 1572.0


def quina(img, f, escala, origem):
    """A quina da parede (o toco) junto à dobradiça, medida na própria imagem: a face do toco do lado do vão e o pé.
    A parede = o cinza escuro aberto (as linhas finas, como o contorno antigo, saem na abertura) ligado à semente."""
    P = lambda x, y: (int(round((x - origem[0]) * escala)), int(round((y - origem[1]) * escala)))
    A0, B0 = P(f["busca"][0] - 12, TOPO_BUSCA - 6)
    A1, B1 = P(f["busca"][1] + 12, FUNDO)
    reg = img[B0:B1, A0:A1].astype(np.float32)
    esc = ((reg.mean(2) < 110) & (reg.max(2) - reg.min(2) < 25)).astype(np.uint8)
    k = max(3, int(round(0.7 * escala)) | 1)
    esc = cv2.morphologyEx(esc, cv2.MORPH_OPEN, np.ones((k, k), np.uint8))
    n, lab = cv2.connectedComponents(esc)
    sx, sy = P(*f["semente"])
    par = lab == lab[sy - B0, sx - A0]
    ya, yb = P(0, LINHAS_PAREDE[0])[1] - B0, P(0, LINHAS_PAREDE[1])[1] - B0
    xs = np.where(par[ya:yb].any(0))[0]
    face = (xs.max() + 1) if f["lado"] > 0 else xs.min()          # px da região (borda da parede)
    # o pé: nas colunas da parede junto à face (1 a 3 px da final para dentro), a última linha de parede
    d0, d1 = int(round(1.0 * escala)), int(round(3.0 * escala))
    cols = range(face - d1, face - d0) if f["lado"] > 0 else range(face + d0, face + d1)
    pes = [np.where(par[:, c])[0].max() + 1 for c in cols if par[:, c].any()]
    pe = int(np.median(pes))
    fx = origem[0] + (A0 + face) / escala
    fy = origem[1] + (B0 + pe) / escala
    return fx, fy, par, (A0, B0)


def folha(img, nome, escala=1.0, origem=(0.0, 0.0)):
    f = FOLHAS[nome]
    fx, fy, par, (A0, B0) = quina(img, f, escala, origem)
    # o que sai: tudo abaixo do pé, entre o revestimento e a caixa, que não seja a parede (nem o pé dela)
    x0, x1 = f["caixa"]
    P = lambda x, y: (int(round((x - origem[0]) * escala)), int(round((y - origem[1]) * escala)))
    # os tracinhos do contorno antigo no pé da parede (mais escuros que a parede), junto à quina: saem
    T0, U0 = P(fx - 4.0, TOPO_LIMPA)
    T1, U1 = P(fx + 4.0, fy + 0.8)
    rt = img[U0:U1, T0:T1]
    risco = (rt.astype(np.float32).mean(2) < 55).astype(np.uint8)
    if risco.any():
        risco = cv2.dilate(risco, np.ones((3, 3), np.uint8))
        img[U0:U1, T0:T1] = cv2.inpaint(rt.copy(), risco, max(2, int(round(0.6 * escala))), cv2.INPAINT_TELEA)
    C0, D0 = P(x0, TOPO_LIMPA)
    C1, D1 = P(x1, FUNDO - 0.5)
    dx = int(round(f["desloc"][0] * escala))
    reg = img[D0:D1, C0:C1].astype(np.float32)
    src = img[D0:D1, C0 + dx:C1 + dx].astype(np.float32)
    a = np.ones(reg.shape[:2], np.float32)
    pw = np.zeros(reg.shape[:2], bool)
    ys, xs = D0 - B0, C0 - A0
    sub = par[max(ys, 0):ys + reg.shape[0], max(xs, 0):xs + reg.shape[1]]
    pw[:sub.shape[0], :sub.shape[1]] = sub
    pw = cv2.dilate(pw.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    a[pw] = 0
    m = max(1, int(round(0.4 * escala)))
    a[:, :m] *= np.linspace(0, 1, m, dtype=np.float32)[None, :]
    a[:, -m:] *= np.linspace(1, 0, m, dtype=np.float32)[None, :]
    a[-m:] *= np.linspace(1, 0, m, dtype=np.float32)[:, None]
    img[D0:D1, C0:C1] = np.clip(reg * (1 - a[..., None]) + src * a[..., None], 0, 255).astype(np.uint8)
    g = [(fx, fy, fx + ESP, fy + COMPR)] if f["lado"] > 0 else [(fx - ESP, fy, fx, fy + COMPR)]
    traco = 0.5 if escala <= 1.5 else min(0.5, EP.TRACO_12K / escala)
    print(f"      {nome}: quina da parede em ({fx:.1f}, {fy:.1f}); folha {tuple(round(v, 1) for v in g[0])}")
    return VC.redesenhar(img, g, escala=escala, origem=origem, traco=traco, inpaint=False)


def main():
    c, pav = PLANTA.split("_")
    base = cv2.imread(str(EP.PROJ / EP.PLANTAS[PLANTA][0]))
    for f in EP.PLANTAS[PLANTA]:
        im = cv2.imread(str(EP.PROJ / f))
        for nome in FOLHAS:
            im = folha(im, nome)
        cv2.imwrite(str(EP.PROJ / f), im)
        if f == EP.PLANTAS[PLANTA][0]:
            novo = im
    pf = EP.PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_entrega.png"
    pr = cv2.imread(str(pf))
    pr[:2160] = novo
    cv2.imwrite(str(pf), pr)
    dz = json.loads((EP.PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[PLANTA]
    for op in "AB":
        rel = EP.PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_12K_opcao_{op}.jpg"
        pil = Image.open(rel)
        dpi = pil.info.get("dpi", (743, 743))
        im = cv2.cvtColor(np.array(pil.convert("RGB")), cv2.COLOR_RGB2BGR)
        del pil
        cinza = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        for nome, f in FOLHAS.items():
            x0, x1 = f["caixa"]
            y0, y1 = TOPO_BUSCA, FUNDO
            mapa, cc = EP.registro_12k(base, cinza, dz, (int(x0) - 100, int(y0) - 100, int(x1) + 100, int(y1) + 100))
            A, B = mapa(x0, y0)
            sx = (mapa(x0 + 1000.0, y0)[0] - A) / 1000.0
            im = folha(im, nome, sx, (x0 - A / sx, y0 - B / sx))
            print(f"   {op}: folha {nome} (registro {cc:.3f}, escala {sx:.3f})")
        Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).save(rel, quality=95, subsampling=0, dpi=dpi)
        del im, cinza


if __name__ == "__main__":
    main()

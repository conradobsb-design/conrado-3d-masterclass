"""O JPG em 12K do Térreo da Casa E (16/11, usuário: "Gere", depois do Térreo pronto), pelo roteiro das Casas C e D
(`ampliacao_12k_casad`: o recorte A3, o Topaz High Fidelity V2 a 12288 x 8689, os tons da final, o fundo branco).

  1. `preparar Terreo`: o recorte A3 deitado (4961 x 3508) da planta na final de 3840 px: a caixa do que não é branco, a
     margem da A3 (`MARGEM`), completado no branco até a proporção da A3; grava a entrada do Topaz e os dados do recorte.
  2. A entrada no Topaz (High Fidelity V2), a 12288 x 8689.
  3. `montar Terreo <saída do Topaz>`: a saída no tamanho certo, os tons da final (a baixa frequência da entrada,
     ampliada), o fundo fora da planta em branco puro; o JPG (qualidade 95, 743 dpi na A3) e as conferências.

A opção B (os rótulos e as descrições das escadas na Kalam): a entrada do Topaz é a final sem textos, que o roteiro do
Térreo gera direto (`pedidos_terreo_casae_1611.py --sem_textos --saida <png>`: nada a apagar, o piso de baixo é o de
verdade), no mesmo recorte da A (`preparar` da A antes); as linhas dos textos (texto, meio, base, altura das maiúsculas,
largura) vêm das tabelas do Térreo (`ROTULOS`, `ESCADAS`) e vão para `renders/POE642_CasaE_PH_Terreo_rotulos_kalam.json`;
no 12K, `rotulos_kalam_casac.desenhar` as escreve na Kalam no mesmo meio e na mesma base, um corpo só, a mesma cor.

  python3 ampliacao_12k_casae.py preparar Terreo [--opcao B --sem_textos <png>]
  python3 ampliacao_12k_casae.py montar Terreo <saída do Topaz> [--opcao B]

O Subsolo (18/11, usuário: "Ok do subsolo para gerar o 12k"): o mesmo roteiro, com a cascata fora da entrada do Topaz
(usuário: "traga a cascata em 4K [...] senão vai sair muito distorcido na hora que for gerar o 12K"): as entradas vêm de
`pedidos_subsolo_casae_1811.py --sem_cascata` (A, `--base`) e `--sem_cascata --sem_textos` (B); o recorte é o da final;
no `montar`, depois dos tons, a peça 4K da biblioteca entra direto no 12K (`pedidos_subsolo_casae_1811.
cascata_biblioteca`, no afim da final ao 12K afinado na piscina). Na B, as linhas da Kalam vêm de `ROTULOS` e
`DESCRICAO` do Subsolo.

  python3 ampliacao_12k_casae.py preparar Subsolo --base <png sem a cascata>
  python3 ampliacao_12k_casae.py preparar Subsolo --opcao B --sem_textos <png sem a cascata e sem textos>
  python3 ampliacao_12k_casae.py montar Subsolo <saída do Topaz> [--opcao B]
"""

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
CASA_E = AQUI.parents[1] / "POE642_CasaE"
R = CASA_E / "renders"
E = CASA_E / "entrega"
A3 = (4961, 3508)
L, H = 12288, 8689
MARGEM = 150 / 4961                      # a margem da A3 (fração da largura), como nas outras casas
TOM_SIGMA_PX = 2.5
FUNDO_FOLGA_PX = 3
# os trechos de conferência (px da final): a final ampliada ao lado do 12K
CONFERENCIA = {"Terreo": {"gourmet": (930, 380, 1480, 800), "cozinha_servico": (1580, 420, 2500, 830),
                          "living_jantar": (1580, 820, 2480, 1560), "piscina_deck": (600, 880, 1180, 1680),
                          "hall_escritorio": (2200, 900, 2660, 1600)},
               "Subsolo": {"piscina_cascata": (840, 460, 1080, 960), "escada_circulacao": (1040, 320, 1500, 520),
                           "academia": (1180, 480, 1960, 900), "sauna_vestiario": (1040, 750, 1500, 1010),
                           "dce_wc_maquinas": (1630, 470, 2060, 830)}}
# o afinamento do afim da final ao 12K para a cascata (px da final): a piscina acima dela, sem a cascata
CAIXA_CASCATA = (845, 700, 1075, 850)
# a cuba do WC DCE 2 (usuário: "SOBRE A PIA, TRAGA UMA DA BIBLIOTECA EM ALTA DEFINIÇÃO, EM VEZ DE DESENHAR AQUI"): a peça
# da biblioteca (313 x 339 px) direto no 12K, por cima da ampliada (o afim afinado no DCE, no WC DCE 2 e na casa de
# máquinas de 5,83 m²)
CAIXA_CUBA = (1840, 480, 1960, 640)


def final(pav):
    return R / f"POE642_CasaE_PH_{pav}_v1_final.png"


def entrada(pav, opcao="A"):
    return R / f"POE642_CasaE_PH_{pav}_12K_entrada_topaz{'' if opcao == 'A' else '_opcao_B'}.png"


def dados(pav):
    return R / f"POE642_CasaE_PH_{pav}_12K_dados.json"


def kalam(pav):
    return R / f"POE642_CasaE_PH_{pav}_rotulos_kalam.json"


def linhas_kalam_subsolo(sem_textos):
    """As linhas da Kalam do Subsolo: os rótulos (`ROTULOS`, a cor pelo piso de baixo) e a descrição da escada."""
    import pedidos_subsolo_casae_1811 as PS
    import pedidos_terreo_casae_1611 as PE
    import rotulos_kalam_casac as KC
    forma = sem_textos.shape[:2]
    lum = cv2.GaussianBlur(sem_textos.astype(np.float32).mean(axis=2), (0, 0), 3)
    out = []
    guarda = PE.ROTULOS
    PE.ROTULOS = PS.ROTULOS
    try:
        for r in PS.ROTULOS:
            out.append({"nome": r[0], "cor": list(PE.cor_rotulo(r, sem_textos, lum)),
                        "linhas": KC._geometria(PE.alfa_rotulo(r, forma), list(r[1]))})
        d = PS.DESCRICAO
        out.append({"nome": "escada: " + " ".join(d["texto"]), "cor": list(d["cor"]),
                    "linhas": KC._geometria(PE.alfa_escada(d["texto"], d["x"], d["y"], d["alinhar"], forma),
                                            list(d["texto"]))})
    finally:
        PE.ROTULOS = guarda
    sem = [b["nome"] for b in out if not b["linhas"]]
    if sem:
        raise SystemExit(f"sem as linhas medidas: {', '.join(sem)}")
    return out


def cascata_12k(out, fin):
    """A peça 4K da cascata direto no 12K: o afim da final ao 12K, afinado na piscina acima da cascata."""
    import danae_foto as DF
    import pedidos_subsolo_casae_1811 as PS
    from correcoes_terreo_casab_1611 import Mapa
    M = DF.afim_12k(fin, out)
    mp = Mapa(float(np.hypot(M[0, 0], M[1, 0])), (float(M[0, 2]), float(M[1, 2])))
    mp.ref = fin
    m = mp.local(out, CAIXA_CASCATA)
    res = PS.cascata_biblioteca(out, PS.CASCATA_BIB, m=Mapa(m.s, m.t))
    out[:] = res
    print(f"    a cascata da biblioteca (4K) direto no 12K, a {m.s:.4f}x")


def cuba_12k(out, fin):
    """A cuba de travertino da biblioteca direto no 12K, no retângulo do PDF (`pedidos_subsolo_casae_1811.WC2`)."""
    import biblioteca_terreo_casaa_1211 as BT
    import danae_foto as DF
    import pedidos_subsolo_casae_1811 as PS
    from correcoes_terreo_casab_1611 import Mapa
    M = DF.afim_12k(fin, out)
    mp = Mapa(float(np.hypot(M[0, 0], M[1, 0])), (float(M[0, 2]), float(M[1, 2])))
    mp.ref = fin
    m = mp.local(out, CAIXA_CUBA)
    x0, y0, x1, y1 = PS.WC2["cuba"]
    cx, cy = m.x((x0 + x1) / 2) - 0.5, m.y((y0 + y1) / 2) - 0.5
    # só a região em volta (o 12K inteiro em float não cabe à toa)
    folga = int(12 * m.s)
    X0, Y0 = int(m.x(x0)) - folga, int(m.y(y0)) - folga
    X1, Y1 = int(m.x(x1)) + folga, int(m.y(y1)) + folga
    reg = out[Y0:Y1, X0:X1].astype(np.float32)
    o = BT.pousar(reg, PS.png(PS.WC2["cuba_png"]), cx - X0, cy - Y0, (y1 - y0) * m.s, (x1 - x0) * m.s, -90.0,
                  BT.SOMBRAS["baixa"], 59.70590031258779 * m.s)
    out[Y0:Y1, X0:X1] = np.clip(np.round(o), 0, 255).astype(np.uint8)
    print(f"    a cuba de travertino da biblioteca direto no 12K, a {m.s:.4f}x")


def linhas_kalam(sem_textos):
    """[{nome, cor, linhas: [(texto, meio x, base, altura das maiúsculas, largura)]}]: os rótulos (`ROTULOS`, a cor pelo
    piso de baixo, como na A) e as descrições das escadas (`ESCADAS["setas"]`), medidos no próprio desenho da Inter."""
    import pedidos_terreo_casae_1611 as PE
    import rotulos_kalam_casac as KC
    forma = sem_textos.shape[:2]
    lum = cv2.GaussianBlur(sem_textos.astype(np.float32).mean(axis=2), (0, 0), 3)
    out = []
    for r in PE.ROTULOS:
        out.append({"nome": r[0], "cor": list(PE.cor_rotulo(r, sem_textos, lum)),
                    "linhas": KC._geometria(PE.alfa_rotulo(r, forma), list(r[1]))})
    for _, _, txt, (x, y), al, cor in PE.ESCADAS["setas"]:
        out.append({"nome": "escada: " + " ".join(txt), "cor": list(cor),
                    "linhas": KC._geometria(PE.alfa_escada(txt, x, y, al, forma), list(txt))})
    sem = [b["nome"] for b in out if not b["linhas"]]
    if sem:
        raise SystemExit(f"sem as linhas medidas: {', '.join(sem)}")
    return out


def preparar(pav, opcao="A", sem_textos=None, base=None):
    if opcao == "B":
        img = cv2.imread(str(sem_textos))
        lk = linhas_kalam_subsolo(img) if pav == "Subsolo" else linhas_kalam(img)
        kalam(pav).write_text(json.dumps(lk, ensure_ascii=False, indent=1) + "\n")
        d = json.loads(dados(pav).read_text())           # o recorte da A
        X0, Y0, Wi, Hi = d["X0"], d["Y0"], *d["entrada"]
    else:
        img = cv2.imread(str(final(pav)))
        nb = (img.astype(np.int16).min(axis=2) < 245)
        ys, xs = np.nonzero(nb)
        x0, y0, x1, y1 = int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1
        w, h = x1 - x0, y1 - y0
        # a largura do recorte com a margem; a altura pela proporção da A3 (ou o contrário, se a planta for alta)
        Wc = w / (1 - 2 * MARGEM)
        Hc = Wc * A3[1] / A3[0]
        if Hc < h / (1 - 2 * MARGEM * A3[0] / A3[1]):
            Hc = h / (1 - 2 * MARGEM * A3[0] / A3[1])
            Wc = Hc * A3[0] / A3[1]
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        X0, Y0 = cx - Wc / 2, cy - Hc / 2
        Wi, Hi = int(round(Wc)), int(round(Hc))
        if base:                                          # a entrada do Topaz de outra imagem, no recorte da final
            img = cv2.imread(str(base))
    M = np.float64([[1, 0, -X0], [0, 1, -Y0]])
    ent = cv2.warpAffine(img, M, (Wi, Hi), flags=cv2.INTER_NEAREST, borderMode=cv2.BORDER_CONSTANT,
                         borderValue=(255, 255, 255))
    cv2.imwrite(str(entrada(pav, opcao)), ent)
    if opcao == "B":
        print(f"[{pav}] a entrada da opção B (sem textos) -> {entrada(pav, opcao).name}; as linhas -> {kalam(pav).name}")
        return
    dados(pav).write_text(json.dumps({"planta": [x0, y0, x1, y1], "X0": X0, "Y0": Y0, "Wc": Wc, "Hc": Hc,
                                      "entrada": [Wi, Hi]}, indent=1) + "\n")
    print(f"[{pav}] a planta {x0},{y0} a {x1},{y1}; o recorte A3 {Wi}x{Hi} a partir de ({X0:.1f}, {Y0:.1f}) "
          f"({L / Wc:.3f}x no 12K) -> {entrada(pav).name}")


def montar(pav, saida_topaz, opcao="A"):
    from PIL import Image
    d = json.loads(dados(pav).read_text())
    img = cv2.imread(str(final(pav)))
    ent = cv2.imread(str(entrada(pav, opcao)))
    Wi, Hi = ent.shape[1], ent.shape[0]
    ia = cv2.imread(str(saida_topaz))
    print(f"[{pav}] a saída do Topaz: {ia.shape[1]}x{ia.shape[0]}; o JPG: {L}x{H} ({L / d['Wc']:.3f}x a final)")
    out = ia if ia.shape[:2] == (H, L) else cv2.resize(ia, (L, H), interpolation=cv2.INTER_LANCZOS4)
    del ia
    # os tons da final: a baixa frequência da entrada, ampliada
    peq = cv2.resize(out, (Wi, Hi), interpolation=cv2.INTER_AREA).astype(np.float32)
    corr = cv2.GaussianBlur(ent.astype(np.float32), (0, 0), TOM_SIGMA_PX) - cv2.GaussianBlur(peq, (0, 0), TOM_SIGMA_PX)
    corr = cv2.resize(corr, (L, H), interpolation=cv2.INTER_CUBIC)
    # o fundo: o branco ligado à borda da entrada, branco puro
    g = cv2.cvtColor(ent, cv2.COLOR_BGR2GRAY)
    fundo = (g >= 250).astype(np.uint8)
    n, lab = cv2.connectedComponents(fundo)
    bordas = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    fundo = np.isin(lab, bordas[bordas > 0]).astype(np.uint8)
    kk = 2 * FUNDO_FOLGA_PX + 1
    fundo = cv2.erode(fundo, np.ones((kk, kk), np.uint8)).astype(np.float32)
    fa = cv2.GaussianBlur(cv2.resize(fundo, (L, H), interpolation=cv2.INTER_LINEAR), (0, 0), 2.0)
    for y in range(0, H, 1024):
        reg = out[y:y + 1024].astype(np.float32) + corr[y:y + 1024]
        f_ = fa[y:y + 1024, :, None]
        reg = reg * (1 - f_) + 255 * f_
        out[y:y + 1024] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    del corr, fa
    if pav == "Subsolo":
        cascata_12k(out, img)
        cuba_12k(out, img)
    if opcao == "B":
        import rotulos_kalam_casac as K
        K.dados = kalam
        K.desenhar(out, pav, L / d["Wc"], d["X0"], d["Y0"])
    saida = E / f"POE642_CasaE_PH_{pav}_12K_opcao_{opcao}.jpg"
    dpi = int(round(L / (420 / 25.4)))
    Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB)).save(saida, quality=95, subsampling=0, dpi=(dpi, dpi),
                                                               optimize=True)
    cv2.imwrite(str(R / f"POE642_CasaE_PH_{pav}_12K_opcao_{opcao}_previa.jpg"),
                cv2.resize(out, (2000, round(2000 * H / L)), interpolation=cv2.INTER_AREA), [cv2.IMWRITE_JPEG_QUALITY, 90])
    s = L / d["Wc"]
    for nome, (x0, y0, x1, y1) in CONFERENCIA[pav].items():
        u0, v0 = int(round((x0 - d["X0"]) * s)), int(round((y0 - d["Y0"]) * s))
        u1, v1 = int(round((x1 - d["X0"]) * s)), int(round((y1 - d["Y0"]) * s))
        cr = out[max(v0, 0):v1, max(u0, 0):u1]
        ref = cv2.resize(img[y0:y1, x0:x1], (cr.shape[1], cr.shape[0]), interpolation=cv2.INTER_LANCZOS4)
        par = np.hstack([ref, np.full((cr.shape[0], 24, 3), 255, np.uint8), cr])
        cv2.imwrite(str(R / f"POE642_CasaE_PH_{pav}_12K_opcao_{opcao}_conferencia_{nome}.jpg"),
                    cv2.resize(par, (par.shape[1] // 3, par.shape[0] // 3), interpolation=cv2.INTER_AREA),
                    [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"    {saida} {L}x{H} ({dpi} dpi na A3), {saida.stat().st_size / 1e6:.1f} MB")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("acao", choices=["preparar", "montar"])
    ap.add_argument("pav", choices=["Terreo", "Subsolo"])
    ap.add_argument("saida_topaz", nargs="?")
    ap.add_argument("--opcao", choices=("A", "B"), default="A")
    ap.add_argument("--sem_textos", help="opção B: a final sem textos (`pedidos_terreo_casae_1611.py --sem_textos`)")
    ap.add_argument("--base", help="opção A: a entrada do Topaz de outra imagem (no Subsolo, a final sem a cascata)")
    a = ap.parse_args()
    if a.acao == "preparar":
        if a.opcao == "B" and not a.sem_textos:
            ap.error("a opção B precisa de --sem_textos <png>")
        preparar(a.pav, a.opcao, a.sem_textos, a.base)
    else:
        montar(a.pav, a.saida_topaz, a.opcao)


if __name__ == "__main__":
    sys.exit(main())

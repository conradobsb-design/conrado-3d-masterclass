"""Térreo da Casa E, 17/11: a cozinha e a área de serviço, na final e direto nos 12K A e B (com a imagem do 3D que o
usuário mandou como referência).

1. `bancadas` (usuário: "corrigir imperfeições na bancada. melhorar o aspecto do dekton" (a da cuba dupla); "deixar
   retinho a bancada. tem uma curva acima do cooktop que precisa ser corrigida" (a ilha); "corrija as imperfeições na
   bancada" (a das duas cubas do serviço)): cada bancada refeita no retângulo reto (o do PDF, ARQ_BANCADAS; onde o render
   encosta numa parede ou numa face, a borda do render), na chapa do Dekton Danae da foto oficial
   (`danae_foto.textura`, os veios no comprido, sem os pontinhos claros: `danae_bancadas_1611.sem_pontinhos`), numa luz
   só. As peças por cima ficam (`pecas`: a cuba dupla e a torneira, as duas cubas do serviço e as torneiras, o cooktop),
   só os px delas (o inox e o cromado neutros, o cooktop escuro), dentro da caixa de cada uma; o resto do desenho sai: os
   pontinhos claros, a faixa de granito escuro atrás das cubas do serviço, o degrau e a quina redonda da ilha acima do
   cooktop, a borda serrilhada de baixo. Fora da bancada, junto à borda de baixo, os px claros soltos voltam ao piso.
2. `janelas` (usuário: "melhorar representação da soleira e folhas da janela na cozinha"; "melhore o aspecto da
   janela" (a do serviço)): as duas janelas de correr redesenhadas pela geometria do PDF (ARQ_PAREDE) no padrão das
   janelas da Casa A (`janela_pia_casaa_1611.desenhar`, `pedidos_terreo_casaa_2910.JANELAS_TA`): o vão no cinza do
   peitoril com as faces num fio escuro, cada folha em vidro claro com o contorno fino, desencontradas como no PDF (a da
   cozinha com três folhas, a do serviço com duas), com a sombra curta.

  python3 cozinha_servico_terreo_casae_1711.py doze [--opcao AB]     (antes da final: a final de antes é a referência)
  python3 cozinha_servico_terreo_casae_1711.py final
  (--passos bancadas,janelas)
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import danae_foto as DF                                     # noqa: E402
import danae_bancadas_1611 as DB                            # noqa: E402
import janela_pia_casaa_1611 as JP                          # noqa: E402
from correcoes_terreo_casab_1611 import Mapa                # noqa: E402
from janela_pia_casaa_1611 import alfa_ret                  # noqa: E402
from pedidos_terreo_casaa_2910 import JANELAS_TA            # noqa: E402

RAIZ = AQUI.parents[1]
FINAL = RAIZ / "POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_final.png"
DOZE = RAIZ / "POE642_CasaE/entrega/POE642_CasaE_PH_Terreo_12K_opcao_{}.jpg"

# px da final. `ret`: a pedra; `pecas`: (caixa, "neutro" | "cromo" | "tudo") o que fica por cima (o inox e o cooktop;
# o cromado das torneiras do serviço, sem o granito em volta: o maior pedaço; a caixa inteira das cubas do serviço); `fora`: a faixa de fora junto à
# borda de baixo (os px claros soltos voltam ao piso de `fora_d` px adiante)
BANCADAS = {
    "bancada da cuba dupla (cozinha)": {
        "ret": (1597.0, 495.6, 1944.6, 536.9), "caixa": (1580, 470, 1960, 560), "semente": 51,
        "pecas": [((1735.5, 500.0, 1803.0, 534.0), "neutro"), ((1763.5, 496.0, 1775.5, 512.0), "neutro")],
        "fora": (1597.0, 536.9, 1944.6, 540.0), "fora_d": (0, 5)},
    "ilha (cozinha)": {
        "ret": (1680.3, 609.3, 1859.4, 687.1), "caixa": (1665, 595, 1875, 712), "semente": 52,
        "pecas": [((1781.5, 609.8, 1819.5, 642.5), "neutro")]},
    "bancada das duas cubas (serviço)": {
        "ret": (1954.6, 564.0, 2067.6, 607.0), "caixa": (1940, 545, 2080, 620), "semente": 53,
        "pecas": [((1975.0, 574.8, 2050.8, 605.5), "tudo"), ((1990.5, 566.0, 1998.5, 576.0), "cromo"),
                  ((2029.5, 566.0, 2037.5, 576.0), "cromo")],
        "fora": (1954.6, 607.0, 2067.6, 610.0), "fora_d": (0, 4)},
}
# as janelas: o vão (ARQ_PAREDE, de face a face) e as folhas de correr (com os perfis), px da final
JANELAS = {
    "cozinha": {"vao": (1676.3, 482.9, 1861.4, 494.9), "caixa": (1650, 460, 1890, 520),
                "folhas": [(1678.7, 482.9, 1742.0, 485.9), (1737.2, 485.9, 1800.5, 488.9),
                           (1795.7, 488.9, 1859.0, 491.9)]},
    "serviço": {"vao": (1992.8, 554.6, 2124.1, 563.5), "caixa": (1970, 535, 2150, 585),
                "folhas": [(1995.2, 554.6, 2060.8, 557.5), (2056.1, 557.5, 2121.7, 560.5)]},
}


def _loc(m, r, X0, Y0):
    rm = m.ret(r)
    return (rm[0] - X0, rm[1] - Y0, rm[2] - X0, rm[3] - Y0)


def bancada(out, mp, nome, q):
    m = mp.local(out, q["caixa"]) if mp.ref is not None else mp
    s = m.s
    rm = m.ret(q["ret"])
    X0, Y0 = int(np.floor(rm[0])) - 1, int(np.floor(rm[1])) - 1
    X1, Y1 = int(np.ceil(rm[2])) + 1, int(np.ceil(rm[3])) + 1
    forma = (Y1 - Y0, X1 - X0)
    sub = out[Y0:Y1, X0:X1].astype(np.float32)
    a = alfa_ret(_loc(m, q["ret"], X0, Y0), forma)
    # as peças por cima: só os px delas, na caixa de cada uma
    sb = cv2.GaussianBlur(sub, (0, 0), 0.4 * s)
    lum = sb.mean(axis=2)
    neutro = ((sb[..., 2] - sb[..., 0]) < DB.NEUTRO) | (lum < 95)
    fica = np.zeros(forma, np.float32)
    for caixa, tipo in q["pecas"]:
        c = alfa_ret(_loc(m, caixa, X0, Y0), forma)
        k = max(1, int(round(0.6 * s)))
        if tipo == "tudo":
            crit = np.ones(forma, np.uint8)
        elif tipo == "neutro":
            crit = cv2.morphologyEx(neutro.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((2 * k + 1, 2 * k + 1), np.uint8))
        else:
            cr = (((sb[..., 2] - sb[..., 0]) <= 7) & (lum > 125) & (c > 0.5)).astype(np.uint8)
            cr = cv2.morphologyEx(cr, cv2.MORPH_CLOSE, np.ones((2 * k + 1, 2 * k + 1), np.uint8))
            n, lab, st, _ = cv2.connectedComponentsWithStats(cr, 8)
            crit = (lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))).astype(np.uint8) if n > 1 else cr
        fica = np.maximum(fica, c * crit)
    fica = np.clip(cv2.GaussianBlur(fica, (0, 0), 0.35 * s) * 1.4, 0, 1) if s > 1.5 else fica
    a = a * (1 - fica)
    hh, ww = forma
    T = DB.sem_pontinhos(DF.textura(hh, ww, DF.PX_M * s, deitada=ww >= hh, semente=q["semente"]), s)
    out[Y0:Y1, X0:X1] = np.clip(np.round(sub * (1 - a[..., None]) + T * a[..., None]), 0, 255).astype(np.uint8)
    if "fora" in q:
        import instalacao_terreo_casad_1711 as ID

        def claro(reg):
            L = reg.mean(axis=2)
            return L > float(np.median(L)) + 25
        ID._remenda(out, m, q["fora"], [q["fora_d"]], claro, 30)
    print(f"    {nome}: o Dekton Danae no retângulo reto, as peças por cima ficam")


def janela(out, mp, nome, q, p=JANELAS_TA):
    m = mp.local(out, q["caixa"]) if mp.ref is not None else mp
    v = q["vao"]
    jq = {"vao": v, "folhas": q["folhas"], "fora": (v[0], v[1], v[0], v[1]), "fora_dx": 0.0}
    novo = JP.desenhar(out, m.s, m.t, jq, p)
    out[...] = novo
    print(f"    janela da {nome}: o vão no cinza do peitoril e as {len(q['folhas'])} folhas de correr do PDF")


PASSOS = ("bancadas", "janelas")


def aplicar(img, mp, passos=PASSOS):
    out = img.copy()
    if "bancadas" in passos:
        for nome, q in BANCADAS.items():
            bancada(out, mp, nome, q)
    if "janelas" in passos:
        for nome, q in JANELAS.items():
            janela(out, mp, nome, q)
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

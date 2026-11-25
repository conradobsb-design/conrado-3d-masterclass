"""Casa A Subsolo, revisão do usuário de 25/11: a junção dos pisos, a porta de correr da circulação e a porta do BH. SERV.

Usuário (com o recorte da parede de baixo da academia e o da porta da circulação): "corrija a junção dos pisos,
deixando-os alinhados. Corrija essas portas e seus desenhos. remova da porta do lavabo essa linha dentro dela."

1. **Junção dos pisos** (vinílico da academia / pedra): nos três vãos da parede de baixo da academia (a passagem junto à
   sauna, o vão do BH. FEM. e o do BH. MASC.) a divisa era ondulada e cada vão num nível. No PDF do escritório, os pisos
   de baixo (ARQ_CONTRAPISO) começam todos em y = 1505,7, a mesma linha da face de cima da parede da sauna: a junção
   passa a uma reta só nessa linha, nos três vãos: o vinílico de cima é esticado até a divisa e a pedra de baixo, da
   divisa para baixo (as tábuas e a pedra seguem contínuas, sem emenda), sem tocar as paredes.
2. **Porta de correr da circulação** (entre a circulação e o patamar da escada do deck): a rodada de 19/11 desenhou um
   retângulo preto em volta das duas folhas juntas, e as folhas eram as barras cinza do render. O desenho antigo sai (o
   piso de baixo, deslocado) e cada folha é desenhada pelo PDF no padrão das esquadrias (`vidros_claros_1911`): perfil
   cinza claro, vidro claro e a sua linha preta fina — a da direita no trilho de cima, a da esquerda no de baixo.
3. **Porta do BH. SERV.** ("a porta do lavabo"): a linha preta estava no vidro de dentro da folha. A folha antiga (e a
   pontinha que descia junto ao bloco da parede) sai e a folha é desenhada inteira no mesmo padrão: a linha fina só por
   fora, nenhuma linha dentro.

Final (e a manuscrita), prancha e 12K A e B (cada item no 12K pelo registro local, como em `esquadrias_pretas_1911`).

  python3 subsolo_casaa_juncao_portas_2511.py
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

PLANTA = "A_Subsolo"

# 1. a junção dos pisos (px da final)
JUNCAO_Y = 1505.7                       # o começo dos pisos de baixo no PDF (= face de cima da parede da sauna)
FAIXA = (1496.0, 1514.2)                # a faixa refeita em cada vão: o vinílico de cima e a pedra de baixo esticados
VAOS = [(1387.5, 1476.3),               # a passagem junto à sauna
        (1494.9, 1550.5),               # o vão do BH. FEM.
        (1808.9, 1864.4)]               # o vão do BH. MASC.
# a pontinha clara da folha do BH. FEM. que o render subiu pela espessura da parede: a pedra ao lado (px da final)
PONTA_FEM = ((1498.6, 1505.0, 1501.4, 1514.5), (4.5, 0.0))

# 2. a porta de correr da circulação
FOLHAS_C = [[(1263.8, 1041.2, 1333.4, 1044.2)],      # a da direita (trilho de cima)
            [(1199.0, 1044.2, 1268.6, 1047.1)]]      # a da esquerda (trilho de baixo)
APAGA_C = [((1199.3, 1039.6, 1333.1, 1048.6), (0.0, 12.0), False),   # o desenho antigo sai pelo piso de baixo
           ((1198.6, 1037.0, 1199.6, 1047.6), (3.0, 0.0), True)]      # o resto claro do batente junto ao bloco

# 3. a porta do BH. SERV.
FOLHA_B = [[(1148.3, 1034.6, 1190.1, 1037.0)]]
APAGA_B = [((1146.5, 1032.4, 1190.0, 1039.4), (0.0, -9.0), False),    # a barra antiga, pelo piso de cima
           ((1185.6, 1039.4, 1190.0, 1045.4), (-8.0, 0.0), False)]    # a pontinha junto ao bloco, pelo piso ao lado

ITENS = {                                # caixa de cada item (px da final), para o registro local no 12K
    "juncao": (1385.0, 1495.0, 1862.0, 1516.0),
    "porta_c": (1196.0, 1036.0, 1336.0, 1050.0),
    "porta_b": (1144.0, 1030.0, 1192.0, 1047.0),
}


def caixa_px(c, escala, origem):
    x0, y0, x1, y1 = c
    return (int(round((x0 - origem[0]) * escala)), int(round((y0 - origem[1]) * escala)),
            int(round((x1 - origem[0]) * escala)), int(round((y1 - origem[1]) * escala)))


def parede(reg):
    r = reg.astype(np.float32)
    return (r.mean(2) < 110) & (r.max(2) - r.min(2) < 25)


def copiar(img, c, desloc, escala, origem, protege=False):
    """`img` na caixa `c` recebe o próprio piso deslocado `desloc` (px da final), com a borda suavizada."""
    A0, B0, A1, B1 = caixa_px(c, escala, origem)
    dx, dy = int(round(desloc[0] * escala)), int(round(desloc[1] * escala))
    m = max(2, int(round(1.0 * escala)))
    reg = img[B0 - m:B1 + m, A0 - m:A1 + m].astype(np.float32)
    src = img[B0 - m + dy:B1 + m + dy, A0 - m + dx:A1 + m + dx].astype(np.float32)
    a = np.zeros(reg.shape[:2], np.float32)
    a[m:-m, m:-m] = 1
    a = cv2.GaussianBlur(a, (0, 0), max(0.6, 0.25 * escala))
    a[m:-m, m:-m] = np.maximum(a[m:-m, m:-m], 0.0)
    if protege:
        p = cv2.dilate((parede(reg) | parede(src)).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        a[p] = 0
    img[B0 - m:B1 + m, A0 - m:A1 + m] = np.clip(reg * (1 - a[..., None]) + src * a[..., None], 0, 255).astype(np.uint8)
    return img


def juncao(img, escala=1.0, origem=(0.0, 0.0)):
    """Cada vão: a divisa reta em JUNCAO_Y. Na faixa, o vinílico de cima (até onde a pedra começava) é esticado até a
    divisa e a pedra de baixo (de onde o vinílico acabava) é esticada da divisa para baixo: as tábuas e a pedra seguem
    contínuas, sem emenda. As colunas com parede ficam como estão."""
    img = copiar(img, *PONTA_FEM, escala, origem, protege=True)
    for x0, x1 in VAOS:
        A0, B0, A1, B1 = caixa_px((x0, FAIXA[0], x1, FAIXA[1]), escala, origem)
        reg = img[B0:B1, A0:A1].copy()
        f = reg.astype(np.float32)
        H, W = reg.shape[:2]
        vin = ((f[..., 2] - f[..., 0]) > 48) & (f.mean(2) < 190)       # o vinílico (R - B ~70, escuro); a pedra ~27, clara
        par = parede(reg)
        ok = ~cv2.dilate(par.astype(np.uint8), np.ones((1, 5), np.uint8)).astype(bool).any(0)
        if not ok.any():
            continue
        cols = np.where(ok)[0]
        pedra_ini = [int(np.argmax(~vin[:, k])) for k in cols]          # a 1ª linha de pedra de cada coluna
        vin_fim = [H - 1 - int(np.argmax(vin[::-1, k])) if vin[:, k].any() else 0 for k in cols]   # a última de vinílico
        yj = int(round((JUNCAO_Y - origem[1]) * escala)) - B0
        y_min = max(2, min(int(np.percentile(pedra_ini, 2)), yj) - 2)
        y_max = min(H - 2, max(int(np.percentile(vin_fim, 98)), yj) + 3)
        y_min = max(y_min, int(0.5 * yj))                               # nada esticado mais que 2x (sem riscas)
        y_max = min(y_max, H - int(0.5 * (H - yj)))
        cima = cv2.resize(reg[:y_min], (W, yj), interpolation=cv2.INTER_LINEAR)
        baixo = cv2.resize(reg[y_max:], (W, H - yj), interpolation=cv2.INTER_LINEAR)
        novo = np.vstack([cima, baixo])
        reg[:, ok] = novo[:, ok]
        img[B0:B1, A0:A1] = reg
    return img


def portas(img, escala=1.0, origem=(0.0, 0.0), so=None):
    traco = 0.5 if escala <= 1.5 else min(0.5, EP.TRACO_12K / escala)
    if so in (None, "porta_c"):
        for c, d, p in APAGA_C:
            img = copiar(img, c, d, escala, origem, protege=p)
        for f in FOLHAS_C:
            img = VC.redesenhar(img, f, escala=escala, origem=origem, traco=traco, inpaint=False)
    if so in (None, "porta_b"):
        for c, d, p in APAGA_B:
            img = copiar(img, c, d, escala, origem, protege=p)
        for f in FOLHA_B:
            img = VC.redesenhar(img, f, escala=escala, origem=origem, traco=traco, inpaint=False)
    return img


def tudo(img, escala=1.0, origem=(0.0, 0.0), so=None):
    if so in (None, "juncao"):
        img = juncao(img, escala, origem)
    if so != "juncao":
        img = portas(img, escala, origem, so)
    return img


def main():
    c, pav = PLANTA.split("_")
    base = cv2.imread(str(EP.PROJ / EP.PLANTAS[PLANTA][0]))
    for f in EP.PLANTAS[PLANTA]:
        im = cv2.imread(str(EP.PROJ / f))
        im = tudo(im)
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
        for nome, (x0, y0, x1, y1) in ITENS.items():
            mapa, cc = EP.registro_12k(base, cinza, dz, (int(x0) - 100, int(y0) - 100, int(x1) + 100, int(y1) + 100))
            A, B = mapa(x0, y0)
            sx = (mapa(x0 + 1000.0, y0)[0] - A) / 1000.0
            origem = (x0 - A / sx, y0 - B / sx)
            im = tudo(im, sx, origem, so=nome)
            print(f"   {op}: {nome} (registro {cc:.3f}, escala {sx:.3f})")
        Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).save(rel, quality=95, subsampling=0, dpi=dpi)
        del im, cinza


if __name__ == "__main__":
    main()

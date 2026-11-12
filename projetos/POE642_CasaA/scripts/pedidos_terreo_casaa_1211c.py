"""Os pedidos de 12/11 à noite no Térreo da Casa A, depois das peças da biblioteca (na final e no 12K).

Usuário, com um recorte cada:
  - "PRECISAMOS MELHORAR O ASPECTO DO MARMORE BEGE BAHIA NESSA REGIÃO" (o pergolado junto à prainha):
    `bege_pergolado_casaa_1211` (o Bege Bahia de dentro do pergolado tecido do deck bom, no tom dele);
  - "REMOVA ESSES RISCOS PRETOS ENTE OS BRISES" (`brises`): as seis marquinhas na linha entre os brises do lounge (na
    final, cinza-claras; no 12K, a IA as fez traços pretos) saem: cada coluna da caixa vem da linha de cima e da de
    baixo dela (a linha vertical do guarda-corpo continua);
  - "CORRIJA ESSA PORTA." (`porta`, o banho varanda): a folha borrada (uma barra rosada larga, com a sombra em cima)
    sai, o piso de baixo é tecido do piso logo abaixo dela, e a folha entra nítida no retângulo do PDF (a ARQ_PAREDE, aberta
    junto à parede da esquerda), no desenho das outras portas do Térreo (o cinza claro com a face fina e a sombra curta,
    `terreo_casaa_1011`: a do lavabo e a da área de serviço);
  - "CORRIJA ESSE CONTORNO DO DECK E ESCADAS" (`deck`, a borda de baixo do deck de madeira e da escada para o Subsolo,
    junto ao gramado): no PDF as duas terminam na mesma reta (y 1130); na final, a última régua tinha uma faixa clara com
    tracinhos e a borda ondulava (o gramado entrava ou ficava 1 a 4 px abaixo). O deck vai até a reta com a régua de
    cima (a do mesmo desenho, uma régua acima), a escada com os degraus de logo acima, e o gramado começa logo abaixo
    (o próprio gramado, refletido na borda dele, com a sombra de contato);
  - "DIMINUA A FONTE PARA CABER NO VÃO, SEM ENCOSTAR NAS BORDAS." (`jardim`, o rótulo JARDIM A: 17,46 m² entre as
    duas linhas cinza da floreira): o rótulo sai (o fundo é a mesma floreira 70 px à esquerda: a faixa e as linhas
    continuam) e volta no corpo `corpo` (0,9; antes 1,3, o padrão), no mesmo centro na horizontal e no meio da faixa na
    vertical, com "17,46" (a vírgula dos outros rótulos); o desenho vai ao 12K (`ampliacao_12k_terreo_casaa.DADOS`).
  - "ESCREVA O RÓTULO DA CLARABOIA DENTRO DO ESPAÇO DESTINADO PARA CLARABOIA, COM UMA FONTE MAIS REDUZIDA. ELA FICA
    DENTRO DO TRACEJADO E PAREDE DA JANELA" (`claraboia`, o lavabo): o CLARABOIA, que ficava abaixo do tracejado, sai (o
    piso do lavabo ao lado) e volta no corpo 0,9 no meio do trecho livre da claraboia, entre a face da janela e o
    tracejado, à esquerda da bacia; o desenho vai aos dados do 12K e ao `ROTULOS_LAVABO`.
  - "A BANCADA É NO MESMO TOM DA CUBA ESCULPIDA. CORRIJA" (`bancada`, a pedra abaixo da cuba do lavabo): o tom mediano
    da borda da cuba sobre o da pedra, px a px (o desenho, a luz e o contorno da pedra ficam); no 12K, o mesmo com os
    tons do 12K. (O vaso do lavabo, "MELHORE A REPRESENTAÇÃO DESSE VASO", é peça da biblioteca:
    `biblioteca_terreo_casaa_1211`, a bacia Carrara no marrom dos vasos.)
  - "COLOCA ESSE RÓTULO MAIS PARA DIREITA OU DIMINUA O TAMANHO DA FONTE" (`garagem`): o GARAGEM, espremido entre a parede
    e o carro do meio, vai à direita, no mesmo corpo, sobre o vão entre o carro do meio e o da direita (os carros não
    mudam); "COLOCA ESSE RÓTULO ACIMA DA ESCADA" (`caracol`): o SOBE PARA O 1º PAVIMENTO da caracol da área de serviço,
    que ficava à esquerda dela, centrado acima dela; os dois desenhos vão aos dados do 12K.
  - "CORRIJA ESSE GUARDA CORPO" (`guarda_corpo`, o da borda de cima do deck): a faixa da barra cinza com os pontinhos
    volta ao piso de 10 px abaixo e a lâmina de vidro do PDF entra no desenho das guardas do Térreo;
  - "FALTOU A SOLEIRA DE UM DOS LADOS DA JANELA" (`soleira`, a janela de canto do escritório): no vão da direita, que
    mostrava o gramado, a soleira da janela de cima, girada (na final e no 12K, cada um com a sua de cima).
  - "DEIXE RETO A FOLHA DO BOX. ESTÁ MUITO TORTO" (`box`, o B. MOTORISTA): a faixa da folha volta ao piso do box e a folha
    entra reta, de parede a parede, no eixo das folhas do PDF, no desenho do vidro do box do banho varanda.
  - "ADICIONE AS ESCADAS O "S" OU "D" DE SUBIR OU DESCER, LOGO ABAIXO DA SETA" (`letras`): o D (deck, Subsolo) e o S
    (jardim, caracol) centrados sob o triângulo, 2,5 px abaixo da ponta de baixo, no corpo e na cor das descrições;
    vão aos dados do 12K como anotações.

  python3 pedidos_terreo_casaa_1211c.py [--antes <png>] [--saida <png>]
Roda depois do `biblioteca_terreo_casaa_1211.py` (parte da final que ele grava). Sem --saida, grava a final e os antes e
depois `renders/POE642_CasaA_PH_Terreo_1211c_<pedido>_antes_depois.jpg`. No 12K: `doze`, chamado pelo `montar12k`.
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
import bege_pergolado_casaa_1211 as BP          # noqa: E402

R = AQUI.parent / "renders"
FINAL = R / "POE642_CasaA_PH_Terreo_final_rotulos.png"

PEDIDOS_1211C = {
    # as marquinhas (px da final), entre os brises, na linha do guarda-corpo
    "brises": {"caixas_px": [(1219, 1260, 1233, 1270), (1219, 1319, 1233, 1327), (1219, 1377, 1233, 1386),
                             (1219, 1435, 1233, 1442), (1219, 1493, 1233, 1500), (1219, 1551, 1233, 1559)],
               "media_px": 2},
    # a folha do PDF (ARQ_PAREDE, o retângulo branco aberto junto à parede da esquerda) e o desenho das portas do Térreo
    "porta": {"folha_px": (1617.0, 1545.1, 1670.7, 1547.5), "limpar_px": (1618, 1536, 1678, 1553),
              "fontes_px": [(1620, 1552, 1696, 1563)], "folha": (222, 224, 226), "face": (92, 94, 97),
              "semente": 1213},
    # a borda de baixo do deck e da escada (o fim do material na linha y_borda - 1, no PDF)
    "deck": {"y_borda": 1131, "deck_x": (726, 903), "escada_x": (903, 1083), "regua_px": 12, "deck_de": 1125,
             "escada_de": 1126, "escada_dy": 6, "grama_ate": 1142, "grama_lum": 85, "beira": 0.93},
    "jardim": {"nome": "JARDIM", "pdf": (2120.7135009765625, 1174.2780151367188), "corpo": 0.9,
               "faixa_y": (985.5, 1010.5), "folga_px": 2, "fonte_dx": 70,
               # no 12K: a mancha que a IA fez sob o rótulo antigo (a entrada tinha ali o texto tirado pelo entorno), com
               # as linhas da floreira quebradas, que o rótulo menor deixa à mostra; sai com a floreira de 72 px à
               # esquerda (4 vezes o passo das listras da grama e dos degraus, 18 px)
               "doze_px": (2332, 983, 2400, 1016), "doze_dx": 72},
    # o rótulo da claraboia do lavabo dentro dela: entre a face da janela (y 356) e o tracejado (y 383), à esquerda da
    # bacia (de x 2316), da face da parede (x 2257): o centro do trecho livre, no corpo 0,9 (antes 1,3, abaixo do traço)
    # a bancada do lavabo (a pedra abaixo da cuba, ARQ_BANCADAS) no tom da cuba esculpida: o fator do tom mediano da
    # borda da cuba sobre o da pedra, px a px (o desenho, a luz e o contorno da pedra ficam)
    "bancada": {"pedra_px": (2328, 468, 2345, 514), "borda_cuba_px": [(2318, 412, 2344, 416), (2318, 461, 2344, 465),
                                                                      (2317, 417, 2320, 460)]},
    # (12/11, depois) "COLOCA ESSE RÓTULO MAIS PARA DIREITA OU DIMINUA O TAMANHO DA FONTE" (a GARAGEM, espremida entre a
    # parede e o carro do meio): no mesmo corpo, à direita, sobre o vão entre o carro do meio (até x 2468 nesta altura)
    # e o da direita (de x 2564), 13 px abaixo da ponta da parede da direita (y 1314)
    "garagem": {"nome": "GARAGEM", "centro": (2516.0, 1340.0), "fundo_dx": 95},
    # "CORRIJA ESSE GUARDA CORPO" (o da borda de cima do deck, junto ao gramado): no PDF, a lâmina de vidro da
    # ARQ_ELEMENTOS FIXOS (1082,6–1590,1 x 337,8–339,3); na final, uma barra cinza com pontinhos escuros embaixo. A faixa
    # (da borda do gramado até 6 px abaixo do vidro) volta ao piso de `fonte_dy` px abaixo e o vidro entra no desenho das
    # guardas do Térreo (`terreo_casaa_1011.vidro_laminas`, os números da escada do jardim)
    "guarda_corpo": {"vidro_px": (1082.6, 337.8, 1590.1, 339.3), "faixa_y": (336, 346), "x": (1083, 1591),
                     "fonte_dy": 10},
    # "FALTOU A SOLEIRA DE UM DOS LADOS DA JANELA" (a janela de canto do escritório): o vão da direita do PDF (ARQ_PAREDE,
    # 2593,2–2605,2 x 355,2–429,1) mostrava o gramado; entra a soleira da janela de cima (o vão dela, 341,4–349,7, da
    # face de fora à de dentro), girada: a face de fora junto ao gramado, o comprido da de cima ao longo
    "soleira": {"vao_px": (2593.2, 355.2, 2605.2, 429.1), "topo_y": (341.4, 349.7), "topo_x": (2500.0, 2588.0)},
    # "COLOCA ESSE RÓTULO ACIMA DA ESCADA" (o SOBE PARA O 1º PAVIMENTO da caracol da área de serviço, à esquerda dela):
    # centrado sobre a caracol (o centro dela, x 1977), no piso livre entre as máquinas e o topo da escada (y 1518)
    "caracol": {"linhas": ["SOBE PARA O", "1º PAVIMENTO"], "perto": (1916.0, 1604.0), "novo": (1977.0, 1501.0, "centro")},
    # "DEIXE RETO A FOLHA DO BOX. ESTÁ MUITO TORTO" (o box do B. MOTORISTA): a linha de vidro tinha um degrau no meio (na
    # final) e saía inclinada e quebrada no 12K. A faixa volta ao piso do box (o de `fonte_dx` px à esquerda) e a folha
    # entra reta, de parede a parede, no eixo das duas folhas de correr do PDF (ARQ_LOUÇAS E METAIS, x 2296,9–2298,4), no
    # desenho do vidro do box do banho varanda (as duas faces cinza e o vidro claro no meio, 1 px cada)
    "box": {"x": 2297.65, "y": (1216.0, 1305.6), "limpar_x": (2293, 2301), "fonte_dx": 9,
            "faces": (177, 183, 188), "vidro": (229, 225, 215), "halo": 0.05},
    # "ADICIONE AS ESCADAS O "S" OU "D" DE SUBIR OU DESCER, LOGO ABAIXO DA SETA": a letra centrada sob o triângulo de cada
    # escada (o centro de cada triângulo, para achá-lo nos dados do 12K), `folga_px` abaixo da ponta de baixo dele, no
    # corpo e na cor das descrições (o mesmo desenho das anotações, também no 12K)
    "letras": {"escadas": [((1052.0, 418.0), "D"), ((914.0, 1094.0), "D"), ((2266.0, 948.0), "S"),
                           ((2005.5, 1567.3), "S")], "folga_px": 2.5, "cor": (45, 45, 45)},
    "claraboia": {"nome": "PROJ. CLARABOIA", "corpo": 0.9, "centro": (2286.0, 369.0), "livre_px": (2257, 356, 2316, 383)},
}


def _quadro():
    import final3840_casaa as FA
    with contextlib.redirect_stdout(io.StringIO()):
        return FA.QuadroA("Terreo")


# ----------------------------------------------------------------------------------------------------------------------
def _colunas(reg, y0, y1, m):
    """A caixa [y0, y1) de `reg` (float32), coluna a coluna, entre a média de `m` linhas acima e a de `m` abaixo."""
    cima = reg[y0 - m:y0].mean(axis=0)
    baixo = reg[y1:y1 + m].mean(axis=0)
    t = ((np.arange(y1 - y0) + 0.5) / (y1 - y0))[:, None, None]
    reg[y0:y1] = cima[None] * (1 - t) + baixo[None] * t
    return reg


def brises(img, q=None):
    q = q or PEDIDOS_1211C["brises"]
    out = img.astype(np.float32)
    for x0, y0, x1, y1 in q["caixas_px"]:
        sub = out[:, x0:x1]
        _colunas(sub, y0, y1, q["media_px"])
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def brises_12k(out, s, X0, Ya3, q=None):
    q = q or PEDIDOS_1211C["brises"]
    f = out.astype(np.float32)
    for x0, y0, x1, y1 in q["caixas_px"]:
        u0, u1 = int(np.floor((x0 - X0) * s)), int(np.ceil((x1 - X0) * s))
        v0, v1 = int(np.floor((y0 - Ya3) * s)), int(np.ceil((y1 - Ya3) * s))
        sub = f[:, u0:u1]
        _colunas(sub, v0, v1, int(round(q["media_px"] * s)))
        # o grão do piso de volta (o alto da linha de cima, repetida), para a caixa não ficar lisa
        g = f[v0 - (v1 - v0):v0, u0:u1] - cv2.GaussianBlur(f[v0 - (v1 - v0):v0, u0:u1], (0, 0), 3)
        f[v0:v1, u0:u1] += 0.8 * g[:v1 - v0]
    return np.clip(np.round(f), 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
def _folha(Q, out, q):
    import final3840_casaa as FA
    fx0, fy0, fx1, fy1 = q["folha_px"]
    (p0, p1), (p2, p3) = Q.q2p(fx0, fy0), Q.q2p(fx1, fy1)
    r = (min(p0, p2), min(p1, p3), max(p0, p2), max(p1, p3))
    tl = FA.tela(out, Q, r, folga=4)
    m = tl.ret(r, 0.3)
    FA.sombra_q(tl, m, forca=0.25, dist=0.9, sigma=0.9)
    tl.pintar(m, q["folha"])
    tl.contorno(m, 0.35, q["face"])
    return np.clip(np.round(tl.gravar()), 0, 255).astype(np.uint8)


def porta(Q, img, q=None):
    import pedidos_terreo_casaa_2910 as PT
    import biblioteca_terreo_casaa_1211 as BT
    q = q or PEDIDOS_1211C["porta"]
    H, W = img.shape[:2]
    par = PT._paredes_fixas(Q, (H, W))
    rot = BT.rotulos(img)
    x0, y0, x1, y1 = q["limpar_px"]
    z = np.zeros((H, W), bool)
    z[y0:y1, x0:x1] = True
    z &= ~par & ~rot
    out = PT.piso_refeito(img, z, q["semente"], q=dict(PT.PISO_TA, fontes_px=q["fontes_px"], p_px=8))
    return _folha(Q, out, q)


def porta_12k(out, s, X0, Ya3, q=None):
    import biblioteca_terreo_casaa_1211 as BT
    q = q or PEDIDOS_1211C["porta"]
    out = BT.bancadas_12k(out, s, X0, Ya3, q=[(q["limpar_px"], q["fontes_px"])])
    # a folha nítida na escala do 12K: o retângulo do PDF em 8x, a sombra curta, o cinza claro e a face fina
    fx0, fy0, fx1, fy1 = q["folha_px"]
    m_ = 4
    u0, v0 = int(np.floor((fx0 - m_ - X0) * s)), int(np.floor((fy0 - m_ - Ya3) * s))
    u1, v1 = int(np.ceil((fx1 + m_ - X0) * s)), int(np.ceil((fy1 + m_ - Ya3) * s))
    ss = 8
    w, h = u1 - u0, v1 - v0
    M = np.zeros((h * ss, w * ss), np.uint8)
    a = ((fx0 - X0) * s - u0) * ss, ((fy0 - Ya3) * s - v0) * ss
    b = ((fx1 - X0) * s - u0) * ss, ((fy1 - Ya3) * s - v0) * ss
    cv2.rectangle(M, (int(round(a[0])), int(round(a[1]))), (int(round(b[0])) - 1, int(round(b[1])) - 1), 255, -1)
    m = cv2.resize(M.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)
    sh = cv2.warpAffine(m, np.float32([[1, 0, 0.9 * s], [0, 1, 0.9 * s]]), (w, h))
    sh = cv2.GaussianBlur(sh, (0, 0), 0.9 * s)
    reg = out[v0:v1, u0:u1].astype(np.float32)
    reg *= (1 - 0.25 * sh * (1 - m))[..., None]
    reg = reg * (1 - m[..., None]) + np.float32(q["folha"])[None, None] * m[..., None]
    e = int(round(0.6 * s * ss))
    borda = M.astype(np.float32) / 255 - cv2.erode(M, np.ones((2 * e + 1, 2 * e + 1), np.uint8)).astype(np.float32) / 255
    borda = cv2.resize(np.clip(borda, 0, 1), (w, h), interpolation=cv2.INTER_AREA)[..., None]
    reg = reg * (1 - borda) + np.float32(q["face"])[None, None] * borda
    out[v0:v1, u0:u1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return out


# ----------------------------------------------------------------------------------------------------------------------
def _grama_espelho(f, cols, v_e, v_max, lum):
    """Coluna a coluna: o gramado começa na linha v_e (o primeiro px escuro a partir dela, refletido para cima)."""
    for u in cols:
        c = f[v_e - 2:v_max, u].mean(axis=1)
        esc = np.nonzero(c < lum)[0]
        if len(esc) == 0:
            continue
        g = v_e - 2 + int(esc[0])
        if g <= v_e:
            continue
        n = g - v_e
        f[v_e:g, u] = f[g:g + n, u][::-1]
    return f


def deck(img, q=None):
    q = q or PEDIDOS_1211C["deck"]
    f = img.astype(np.float32)
    yb = q["y_borda"]
    a0, a1 = q["deck_x"]
    e0, e1 = q["escada_x"]
    r = q["regua_px"]
    # o gramado: logo abaixo da reta (antes, porque o material pode ter avançado nele)
    _grama_espelho(f, range(a0, e1), yb, q["grama_ate"], q["grama_lum"])
    # o deck: a última régua, a de cima (o mesmo desenho, uma régua acima), até a reta
    y0 = q["deck_de"]
    f[y0:yb, a0:a1] = f[y0 - r:yb - r, a0:a1]
    # a escada: os degraus de logo acima, até a reta, com a beira um tom abaixo
    y0 = q["escada_de"]
    d = q["escada_dy"]
    f[y0:yb, e0:e1] = f[y0 - d:yb - d, e0:e1]
    f[yb - 1, e0:e1] *= q["beira"]
    return np.clip(np.round(f), 0, 255).astype(np.uint8)


def deck_12k(out, s, X0, Ya3, q=None):
    q = q or PEDIDOS_1211C["deck"]
    f = out.astype(np.float32)

    def U(x):
        return int(round((x - X0) * s))

    def V(y):
        return int(round((y - Ya3) * s))
    v_e = V(q["y_borda"])
    a0, a1, e0, e1 = U(q["deck_x"][0]), U(q["deck_x"][1]), U(q["escada_x"][0]), U(q["escada_x"][1])
    _grama_espelho(f, range(a0, e1), v_e, V(q["grama_ate"]), q["grama_lum"])
    # o passo das réguas do deck na saída da IA (a autocorrelação das linhas, perto de `regua_px` na escala)
    perfil = f[V(1030):V(1120), a0:a1].mean(axis=(1, 2))
    perfil = perfil - perfil.mean()
    p0 = q["regua_px"] * s
    cand = range(int(p0 * 0.8), int(p0 * 1.2) + 1)
    passo = max(cand, key=lambda k: float(np.dot(perfil[:-k], perfil[k:]) / (len(perfil) - k)))
    y0 = V(q["deck_de"])
    f[y0:v_e, a0:a1] = f[y0 - passo:v_e - passo, a0:a1]
    y0, d = V(q["escada_de"]), int(round(q["escada_dy"] * s))
    f[y0:v_e, e0:e1] = f[y0 - d:v_e - d, e0:e1]
    b = max(1, int(round(0.8 * s)))
    f[v_e - b:v_e, e0:e1] *= q["beira"]
    print(f"    deck no 12K: o passo das réguas {passo} px")
    return np.clip(np.round(f), 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------------------------------------------------
def _registro_jardim(Q, forma, q):
    import ampliacao_12k_terreo_casaa as Z
    d = json.loads(Z.DADOS.read_text())
    for i, b in enumerate(d["rotulos"]):
        if b["nome"] == q["nome"] and np.allclose(b["pdf"], q["pdf"]):
            return d, i
    raise SystemExit("o rótulo do JARDIM não está nos dados do 12K")


def jardim(Q, img, q=None, gravar=True):
    import ampliacao_12k_terreo_casaa as Z
    import terreo_casaa_1011 as TA
    q = q or PEDIDOS_1211C["jardim"]
    forma = img.shape[:2]
    d, i = _registro_jardim(Q, forma, q)
    b = d["rotulos"][i]
    if "_antes" in b:                             # o desenho de antes (o que está na final de antes)
        b0 = dict(b, opc=b["_antes"]["opc"], desvio=b["_antes"]["desvio"])
    else:
        b0 = dict(b)
    a0 = Z.alfa_rotulo(Q, b0, forma)
    ys, xs = np.nonzero(a0 > 0.3)
    cx = (xs.min() + xs.max()) / 2
    # o fundo: a mesma floreira, `fonte_dx` px à esquerda (a faixa e as duas linhas cinza são horizontais: o trecho ao
    # lado as continua), com a emenda esfumada
    zona = TA.dilatar(a0 > 0.02, q["folga_px"])
    dx = q["fonte_dx"]
    fonte = np.roll(img, dx, axis=1).astype(np.float32)
    al = np.clip(cv2.GaussianBlur(zona.astype(np.float32), (0, 0), 0.8) * 1.6, 0, 1)
    al[~TA.dilatar(zona, 2)] = 0
    out = np.clip(np.round(img.astype(np.float32) * (1 - al[..., None]) + fonte * al[..., None]), 0, 255
                  ).astype(np.uint8)
    desl = f"{dx} px à esquerda"
    nb = {k: v for k, v in b0.items() if not k.startswith("_")}
    nb["opc"] = dict(nb["opc"], corpo=q["corpo"])
    a1 = Z.alfa_rotulo(Q, nb, forma)
    ys, xs = np.nonzero(a1 > 0.3)
    cy = sum(q["faixa_y"]) / 2
    nb["desvio"] = [nb["desvio"][0] + cx - (xs.min() + xs.max()) / 2, nb["desvio"][1] + cy - (ys.min() + ys.max()) / 2]
    a = Z.alfa_rotulo(Q, nb, forma)
    out = np.clip(np.round(TA.compor(out.astype(np.float32), a, tuple(nb["cor"]))), 0, 255).astype(np.uint8)
    ys, xs = np.nonzero(a > 0.3)
    print(f"    JARDIM: corpo {q['corpo']}, {xs.max() - xs.min() + 1} x {ys.max() - ys.min() + 1} px, de y {ys.min()} a "
          f"{ys.max()} (faixa {q['faixa_y'][0]:.1f} a {q['faixa_y'][1]:.1f}); fundo de {desl}")
    if gravar:
        nb["_antes"] = {"opc": b0["opc"], "desvio": b0["desvio"]}
        d["rotulos"][i] = nb
        Z.DADOS.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
    return out


def claraboia(Q, img, q=None, gravar=True):
    import ampliacao_12k_terreo_casaa as Z
    import terreo_casaa_1011 as TA
    q = q or PEDIDOS_1211C["claraboia"]
    forma = img.shape[:2]
    d = json.loads(Z.DADOS.read_text())
    i = next(k for k, b in enumerate(d["rotulos"]) if b["nome"] == q["nome"])
    b = d["rotulos"][i]
    b0 = dict(b, opc=b["_antes"]["opc"], desvio=b["_antes"]["desvio"]) if "_antes" in b else dict(b)
    a0 = Z.alfa_rotulo(Q, b0, forma)
    # o rótulo antigo sai (o piso do lavabo de logo ao lado, `terreo_casaa_1011._tapar_rotulo`, como os de 11/11)
    with contextlib.redirect_stdout(io.StringIO()):
        import final3840_casaa as FA
        par = FA.paredes_pdf(Q) > 0.05
    lum = img.astype(np.float32).mean(axis=2)
    texto = np.abs(lum - cv2.medianBlur(img, 7).astype(np.float32).mean(axis=2)) > TA.ROTULOS_1111["texto_dif"]
    proibido = TA.dilatar((a0 > 0.02) | texto, 2) | TA.moveis_pdf(Q) | par
    zona = TA.dilatar(a0 > 0.02, TA.ROTULOS_1111["folga_px"])
    out, desl = TA._tapar_rotulo(img, zona, proibido, Q.chapada, TA.ROTULOS_1111)
    nb = {k: v for k, v in b0.items() if not k.startswith("_")}
    nb["opc"] = dict(nb["opc"], corpo=q["corpo"])
    a1 = Z.alfa_rotulo(Q, nb, forma)
    ys, xs = np.nonzero(a1 > 0.3)
    tx, ty = q["centro"]
    nb["desvio"] = [nb["desvio"][0] + tx - (xs.min() + xs.max()) / 2, nb["desvio"][1] + ty - (ys.min() + ys.max()) / 2]
    a = Z.alfa_rotulo(Q, nb, forma)
    out = np.clip(np.round(TA.compor(out.astype(np.float32), a, tuple(nb["cor"]))), 0, 255).astype(np.uint8)
    ys, xs = np.nonzero(a > 0.3)
    x0, y0, x1, y1 = q["livre_px"]
    print(f"    CLARABOIA: corpo {q['corpo']}, x {xs.min()}-{xs.max()}, y {ys.min()}-{ys.max()} (o livre: x {x0}-{x1}, "
          f"y {y0}-{y1}); fundo de {desl}")
    if gravar:
        nb["_antes"] = {"opc": b0["opc"], "desvio": b0["desvio"]}
        d["rotulos"][i] = nb
        Z.DADOS.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
        # o desenho gravado do lavabo (de onde o `preparar` do 12K o tira da final) acompanha
        lav = json.loads(TA.ROTULOS_LAVABO.read_text())
        lav = [({k: v for k, v in nb.items() if not k.startswith("_")} if r["nome"] == q["nome"] else r) for r in lav]
        TA.ROTULOS_LAVABO.write_text(json.dumps(lav, ensure_ascii=False, indent=1))
    return out


def _tom_pedra(f, pedra, bordas):
    x0, y0, x1, y1 = pedra
    reg = f[y0:y1, x0:x1]
    alvo = np.median(np.concatenate([f[b:d, a:c].reshape(-1, 3) for a, b, c, d in bordas]), axis=0)
    # a mediana da pedra pelo miolo (sem o contorno)
    m = max(1, (x1 - x0) // 6)
    atual = np.median(reg[m:-m, m:-m].reshape(-1, 3), axis=0)
    f[y0:y1, x0:x1] = reg * (alvo / np.maximum(atual, 1))[None, None]
    return alvo, atual


def bancada(img, q=None):
    q = q or PEDIDOS_1211C["bancada"]
    f = img.astype(np.float32)
    alvo, atual = _tom_pedra(f, q["pedra_px"], q["borda_cuba_px"])
    print(f"    bancada do lavabo: BGR {np.round(atual).astype(int)} -> {np.round(alvo).astype(int)} (a borda da cuba)")
    return np.clip(np.round(f), 0, 255).astype(np.uint8)


def bancada_12k(out, s, X0, Ya3, q=None):
    q = q or PEDIDOS_1211C["bancada"]

    def m(r):
        return (int(np.floor((r[0] - X0) * s)), int(np.floor((r[1] - Ya3) * s)), int(np.ceil((r[2] - X0) * s)),
                int(np.ceil((r[3] - Ya3) * s)))
    f = out.astype(np.float32)
    _tom_pedra(f, m(q["pedra_px"]), [m(r) for r in q["borda_cuba_px"]])
    return np.clip(np.round(f), 0, 255).astype(np.uint8)


def _tapar(Q, img, a0):
    import terreo_casaa_1011 as TA
    with contextlib.redirect_stdout(io.StringIO()):
        import final3840_casaa as FA
        par = FA.paredes_pdf(Q) > 0.05
    lum = img.astype(np.float32).mean(axis=2)
    texto = np.abs(lum - cv2.medianBlur(img, 7).astype(np.float32).mean(axis=2)) > TA.ROTULOS_1111["texto_dif"]
    proibido = TA.dilatar((a0 > 0.02) | texto, 2) | TA.moveis_pdf(Q) | par
    zona = TA.dilatar(a0 > 0.02, TA.ROTULOS_1111["folga_px"])
    return TA._tapar_rotulo(img, zona, proibido, Q.chapada, TA.ROTULOS_1111)


def garagem(Q, img, q=None, gravar=True):
    """O rótulo da GARAGEM no mesmo desenho, com o centro em `centro`."""
    import ampliacao_12k_terreo_casaa as Z
    import terreo_casaa_1011 as TA
    q = q or PEDIDOS_1211C["garagem"]
    forma = img.shape[:2]
    d = json.loads(Z.DADOS.read_text())
    i = next(k for k, b in enumerate(d["rotulos"]) if b["nome"] == q["nome"])
    b = d["rotulos"][i]
    b0 = dict(b, opc=b["_antes"]["opc"], desvio=b["_antes"]["desvio"]) if "_antes" in b else dict(b)
    a0 = Z.alfa_rotulo(Q, b0, forma)
    # o fundo: o mesmo trecho `fundo_dx` px à esquerda (a parede de cima é reta; o carro da esquerda começa mais abaixo)
    zona = TA.dilatar(a0 > 0.02, 2)
    al = np.clip(cv2.GaussianBlur(zona.astype(np.float32), (0, 0), 0.8) * 1.6, 0, 1)
    al[~TA.dilatar(zona, 2)] = 0
    fonte = np.roll(img, q["fundo_dx"], axis=1).astype(np.float32)
    out = np.clip(np.round(img.astype(np.float32) * (1 - al[..., None]) + fonte * al[..., None]), 0, 255
                  ).astype(np.uint8)
    desl = f"{q['fundo_dx']} px à esquerda"
    nb = {k: v for k, v in b0.items() if not k.startswith("_")}
    ys, xs = np.nonzero(a0 > 0.3)
    tx, ty = q["centro"]
    nb["desvio"] = [nb["desvio"][0] + tx - (xs.min() + xs.max()) / 2, nb["desvio"][1] + ty - (ys.min() + ys.max()) / 2]
    a = Z.alfa_rotulo(Q, nb, forma)
    out = np.clip(np.round(TA.compor(out.astype(np.float32), a, tuple(nb["cor"]))), 0, 255).astype(np.uint8)
    ys, xs = np.nonzero(a > 0.3)
    print(f"    GARAGEM: x {xs.min()}-{xs.max()}, y {ys.min()}-{ys.max()}; fundo de {desl}")
    if gravar:
        nb["_antes"] = {"opc": b0["opc"], "desvio": b0["desvio"]}
        d["rotulos"][i] = nb
        Z.DADOS.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
    return out


def caracol(Q, img, q=None, gravar=True):
    """O SOBE PARA O 1º PAVIMENTO da caracol (uma anotação: os dados do 12K) no lugar novo, no mesmo desenho."""
    import ampliacao_12k_terreo_casaa as Z
    import terreo_casaa_1011 as TA
    q = q or PEDIDOS_1211C["caracol"]
    forma = img.shape[:2]
    d = json.loads(Z.DADOS.read_text())
    i = next(k for k, (t, dd, c) in enumerate(d["anotacoes"])
             if t == "txt" and dd[0] == q["linhas"] and (np.allclose(dd[1:3], q["perto"])
                                                          or np.allclose(dd[1:3], q["novo"][:2])))
    t, dd, cor = d["anotacoes"][i]
    d0 = [dd[0], q["perto"][0], q["perto"][1], "direita"]          # o desenho de antes (o que está na final de antes)
    a0 = Z.alfa_anotacao(t, d0, forma)
    out, desl = _tapar(Q, img, a0)
    d1 = [dd[0], *q["novo"]]
    a = Z.alfa_anotacao(t, d1, forma)
    out = np.clip(np.round(TA.compor(out.astype(np.float32), a, tuple(cor))), 0, 255).astype(np.uint8)
    ys, xs = np.nonzero(a > 0.3)
    print(f"    SOBE PARA O 1º PAVIMENTO (caracol): x {xs.min()}-{xs.max()}, y {ys.min()}-{ys.max()}; fundo de {desl}")
    if gravar:
        d["anotacoes"][i] = [t, d1, cor]
        Z.DADOS.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
    return out


def vidro_ret(out, ret, q, s=1.0, X0=0.0, Y0=0.0, ss=8):
    """Uma lâmina de vidro deitada (px da final: x0, y0, x1, y1), no desenho de `terreo_casaa_1011.vidro_laminas`
    (o vidro claro, as duas faces em linha fina, o brilho no meio e a sombra curta), na escala s (u = (x - X0) s)."""
    x0, y0, x1, y1 = ret
    if y1 - y0 < q["larg_min_px"]:
        c_ = (y0 + y1) / 2
        y0, y1 = c_ - q["larg_min_px"] / 2, c_ + q["larg_min_px"] / 2
    x0, x1 = x0 - q["ponta_px"], x1 + q["ponta_px"]
    u0, v0, u1, v1 = (x0 - X0) * s, (y0 - Y0) * s, (x1 - X0) * s, (y1 - Y0) * s
    A0, B0, A1, B1 = int(u0) - 3 * int(np.ceil(s)), int(v0) - 3 * int(np.ceil(s)), int(np.ceil(u1)) + 4 * int(np.ceil(s)), \
        int(np.ceil(v1)) + 4 * int(np.ceil(s))
    w, h = A1 - A0, B1 - B0
    m = np.zeros((h * ss, w * ss), np.uint8)
    a0, b0, a1, b1 = [int(round(v * ss)) for v in (u0 - A0, v0 - B0, u1 - A0, v1 - B0)]
    cv2.rectangle(m, (a0, b0), (a1 - 1, b1 - 1), 255, -1)
    lt = max(1, int(round(q["linha_px"] * s * ss)))
    bordas, meio = np.zeros_like(m), np.zeros_like(m)
    bordas[b0:b0 + lt, a0:a1] = 255
    bordas[b1 - lt:b1, a0:a1] = 255
    c_ = (b0 + b1) // 2
    meio[c_ - lt // 2:c_ + lt // 2 + 1, a0 + lt:a1 - lt] = 255

    def reduzir(x):
        return cv2.resize(x.astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)
    av, ab, am = reduzir(m), reduzir(bordas), reduzir(meio)
    reg = out[B0:B1, A0:A1].astype(np.float32)
    sb = cv2.GaussianBlur(cv2.warpAffine(av, np.float32([[1, 0, -0.7 * s], [0, 1, 0.7 * s]]), (w, h)), (0, 0), 0.5 * s)
    reg *= (1 - q["sombra"] * sb * (1 - av))[..., None]
    al = av[..., None] * q["alfa"]
    reg = reg * (1 - al) + np.float32(q["vidro"]) * al
    reg = reg * (1 - ab[..., None]) + np.float32(q["contorno"]) * ab[..., None]
    am = am[..., None] * q["brilho"]
    reg = reg * (1 - am) + 250 * am
    out[B0:B1, A0:A1] = np.clip(np.round(reg), 0, 255).astype(np.uint8)
    return out


def guarda_corpo(img, q=None, s=1.0, X0=0.0, Y0=0.0):
    import terreo_casaa_1011 as TA
    q = q or PEDIDOS_1211C["guarda_corpo"]
    out = img.copy()
    y0, y1 = [int(round((v - Y0) * s)) for v in q["faixa_y"]]
    x0, x1 = [int(round((v - X0) * s)) for v in q["x"]]
    d = int(round(q["fonte_dy"] * s))
    out[y0:y1, x0:x1] = img[y0 + d:y1 + d, x0:x1]
    return vidro_ret(out, q["vidro_px"], TA.ESCADAS_TA["jardim"]["vidro"], s, X0, Y0)


def soleira(img, q=None, s=1.0, X0=0.0, Y0=0.0):
    """A soleira do vão da direita, tirada da de cima (a mesma imagem), girada; px da final -> u = (x - X0) s."""
    q = q or PEDIDOS_1211C["soleira"]
    vx0, vy0, vx1, vy1 = q["vao_px"]
    ty0, ty1 = q["topo_y"]
    tx0, tx1 = q["topo_x"]
    u0, v0 = int(np.floor((vx0 - X0) * s)), int(np.floor((vy0 - Y0) * s))
    u1, v1 = int(np.ceil((vx1 - X0) * s)), int(np.ceil((vy1 - Y0) * s))
    uu, vv = np.meshgrid(np.arange(u0, u1) + 0.5, np.arange(v0, v1) + 0.5)
    x, y = uu / s + X0, vv / s + Y0                       # px da final de cada px do destino
    # a face de fora (x = vx1, junto ao gramado) <-> a de fora de cima (y = ty0); o comprido <-> x de cima
    yt = ty0 + (vx1 - x) * (ty1 - ty0) / (vx1 - vx0)
    xt = tx0 + (y - vy0) * (tx1 - tx0) / (vy1 - vy0)
    mx = ((xt - X0) * s - 0.5).astype(np.float32)
    my = ((yt - Y0) * s - 0.5).astype(np.float32)
    amostra = cv2.remap(img, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE).astype(np.float32)
    # a cobertura do vão em cada px (as bordas fracionárias)
    cx = np.clip(np.minimum(uu + 0.5, (vx1 - X0) * s) - np.maximum(uu - 0.5, (vx0 - X0) * s), 0, 1)
    cy = np.clip(np.minimum(vv + 0.5, (vy1 - Y0) * s) - np.maximum(vv - 0.5, (vy0 - Y0) * s), 0, 1)
    al = (cx * cy)[..., None]
    out = img.copy()
    reg = out[v0:v1, u0:u1].astype(np.float32)
    out[v0:v1, u0:u1] = np.clip(np.round(reg * (1 - al) + amostra * al), 0, 255).astype(np.uint8)
    return out


def box(img, q=None, s=1.0, X0=0.0, Y0=0.0, ss=8):
    """A folha do box reta: a faixa limpa com o piso de `fonte_dx` px à esquerda e o vidro (face, vidro, face) no eixo,
    de parede a parede; px da final -> u = (x - X0) s."""
    q = q or PEDIDOS_1211C["box"]
    out = img.astype(np.float32)
    y0, y1 = q["y"]
    v0, v1 = int(np.floor((y0 - Y0) * s)), int(np.ceil((y1 - Y0) * s))
    a0, a1 = int(np.floor((q["limpar_x"][0] - X0) * s)), int(np.ceil((q["limpar_x"][1] - X0) * s))
    d = int(round(q["fonte_dx"] * s))
    out[v0:v1, a0:a1] = img[v0:v1, a0 - d:a1 - d].astype(np.float32)
    # as emendas dos dois lados esfumadas (1 px da final; no 12K, a da esquerda aparecia como um fio)
    e = max(1, int(round(s)))
    t = np.linspace(1, 0, e + 2)[1:-1][None, :, None]
    out[v0:v1, a1 - e:a1] = out[v0:v1, a1 - e:a1] * t + img[v0:v1, a1 - e:a1].astype(np.float32) * (1 - t)
    t = t[:, ::-1]
    out[v0:v1, a0:a0 + e] = out[v0:v1, a0:a0 + e] * t + img[v0:v1, a0:a0 + e].astype(np.float32) * (1 - t)
    # o vidro: três faixas de 1 px (da final), em 8x
    xc = (q["x"] - X0) * s
    U0, U1 = int(np.floor(xc - 3 * s)), int(np.ceil(xc + 3 * s))
    w = U1 - U0
    xs = (np.arange(w * ss) + 0.5) / ss + U0
    k = (xs - xc) / s                                         # em px da final, a partir do eixo
    face = ((np.abs(k) >= 0.5) & (np.abs(k) < 1.5)).astype(np.float32)
    meio = (np.abs(k) < 0.5).astype(np.float32)
    halo = ((np.abs(k) >= 1.5) & (np.abs(k) < 2.5)).astype(np.float32)

    def red(x):
        return x.reshape(w, ss).mean(axis=1)[None, :, None]
    fa, me, ha = red(face), red(meio), red(halo)
    reg = out[v0:v1, U0:U1]
    reg *= 1 - q["halo"] * ha
    reg[:] = reg * (1 - fa) + np.float32(q["faces"]) * fa
    reg[:] = reg * (1 - me) + np.float32(q["vidro"]) * me
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def letras(Q, img, q=None, gravar=True):
    """O S ou o D logo abaixo da seta de cada escada (uma anotação "txt" a mais nos dados do 12K)."""
    import ampliacao_12k_terreo_casaa as Z
    import terreo_casaa_1011 as TA
    q = q or PEDIDOS_1211C["letras"]
    forma = img.shape[:2]
    d = json.loads(Z.DADOS.read_text())
    # as letras de uma rodada anterior saem dos dados (a final de antes não as tem)
    d["anotacoes"] = [a for a in d["anotacoes"] if not (a[0] == "txt" and a[1][0] in (["S"], ["D"]))]
    tris = [np.float32(a[1]) for a in d["anotacoes"] if a[0] == "tri"]
    out = img.astype(np.float32)
    feitos = []
    for (cx, cy), L in q["escadas"]:
        t = min(tris, key=lambda p: float(np.hypot(*(p.mean(axis=0) - (cx, cy)))))
        x = float(t[:, 0].min() + t[:, 0].max()) / 2
        topo = float(t[:, 1].max()) + q["folga_px"]
        dados = [[L], x, topo + 6.0, "centro"]
        a = Z.alfa_anotacao("txt", dados, forma)
        ys, xs = np.nonzero(a > 0.3)
        dados[2] += topo - ys.min()                             # o alto da letra na folga sob a ponta do triângulo
        dados[1] += x - (xs.min() + xs.max()) / 2
        a = Z.alfa_anotacao("txt", dados, forma)
        out = TA.compor(out, a, q["cor"])
        ys, xs = np.nonzero(a > 0.3)
        feitos.append(f"{L} em x {xs.min()}-{xs.max()}, y {ys.min()}-{ys.max()}")
        d["anotacoes"].append(["txt", dados, list(q["cor"])])
    print(f"    letras das escadas: {'; '.join(feitos)}")
    if gravar:
        Z.DADOS.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def jardim_12k(out, s, X0, Ya3, q=None):
    q = q or PEDIDOS_1211C["jardim"]
    x0, y0, x1, y1 = q["doze_px"]
    u0, u1 = int(np.floor((x0 - X0) * s)), int(np.ceil((x1 - X0) * s))
    v0, v1 = int(np.floor((y0 - Ya3) * s)), int(np.ceil((y1 - Ya3) * s))
    d = int(round(q["doze_dx"] * s))
    fonte = out[v0:v1, u0 - d:u1 - d].astype(np.float32)
    al = np.ones((v1 - v0, u1 - u0), np.float32)
    e = int(round(4.0 * s))
    rampa = np.linspace(0, 1, e + 2)[1:-1]
    al[:, :e] *= rampa[None]
    al[:, -e:] *= rampa[::-1][None]
    reg = out[v0:v1, u0:u1].astype(np.float32)
    out[v0:v1, u0:u1] = np.clip(np.round(reg * (1 - al[..., None]) + fonte * al[..., None]), 0, 255).astype(np.uint8)
    return out


# ----------------------------------------------------------------------------------------------------------------------
ANTES_DEPOIS = {"bege_pergolado": (1080, 840, 1540, 1230), "brises": (1180, 1240, 1260, 1580),
                "porta": (1590, 1480, 1710, 1620), "deck_escadas": (700, 1060, 1110, 1160),
                "jardim": (2250, 950, 2440, 1040), "sofa": (1860, 340, 2200, 640),
                "claraboia": (2240, 335, 2360, 425), "lavabo_vaso_bancada": (2250, 340, 2365, 525),
                "garagem": (2280, 1280, 2700, 1460), "caracol": (1780, 1440, 2060, 1630),
                "guarda_corpo": (1060, 322, 1600, 362), "soleira": (2460, 320, 2625, 470),
                "box_motorista": (2240, 1200, 2330, 1315), "letra_deck": (1020, 395, 1110, 455),
                "letra_subsolo": (850, 1070, 960, 1135), "letra_jardim": (2240, 925, 2370, 985),
                "letra_caracol": (1930, 1520, 2040, 1620)}


def antes_depois(antes, depois):
    for nome, (x0, y0, x1, y1) in ANTES_DEPOIS.items():
        e = max(2, int(round(900 / max(x1 - x0, 1) / 2)))
        e = min(e, 4)
        a = cv2.resize(antes[y0:y1, x0:x1], None, fx=e, fy=e, interpolation=cv2.INTER_LANCZOS4)
        d = cv2.resize(depois[y0:y1, x0:x1], None, fx=e, fy=e, interpolation=cv2.INTER_LANCZOS4)
        vert = (x1 - x0) * 2 < (y1 - y0)
        if vert:
            sep = np.full((a.shape[0], 16, 3), 255, np.uint8)
            corpo = np.hstack([a, sep, d])
        else:
            sep = np.full((16, a.shape[1], 3), 255, np.uint8)
            corpo = np.vstack([a, sep, d])
        topo = np.full((40, corpo.shape[1], 3), 255, np.uint8)
        rot = "ANTES | DEPOIS" if vert else "ANTES (em cima) | DEPOIS (embaixo)"
        cv2.putText(topo, rot, (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (40, 40, 40), 2, cv2.LINE_AA)
        cv2.imwrite(str(R / f"POE642_CasaA_PH_Terreo_1211c_{nome}_antes_depois.jpg"), np.vstack([topo, corpo]),
                    [cv2.IMWRITE_JPEG_QUALITY, 90])


def aplicar(antes):
    Q = _quadro()
    out = BP.aplicar(antes)
    out = brises(out)
    out = porta(Q, out)
    out = deck(out)
    out = jardim(Q, out)
    out = claraboia(Q, out)
    out = bancada(out)
    out = garagem(Q, out)
    out = caracol(Q, out)
    out = guarda_corpo(out)
    out = soleira(out)
    out = box(out)
    out = letras(Q, out)
    return out


def doze(out, s, X0, Ya3):
    """No 12K (`ampliacao_12k_terreo_casaa.montar12k`, antes dos tracejados e dos textos)."""
    out = BP.pergolado_12k(out, s, X0, Ya3)
    out = brises_12k(out, s, X0, Ya3)
    out = porta_12k(out, s, X0, Ya3)
    out = deck_12k(out, s, X0, Ya3)
    out = jardim_12k(out, s, X0, Ya3)
    out = bancada_12k(out, s, X0, Ya3)
    out = guarda_corpo(out, s=s, X0=X0, Y0=Ya3)
    out = soleira(out, s=s, X0=X0, Y0=Ya3)
    out = box(out, s=s, X0=X0, Y0=Ya3)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--antes", help="a final de antes (sem os pedidos de 12/11 à noite); padrão: a final instalada")
    ap.add_argument("--saida")
    ap.add_argument("--antes_depois", help="a final de referência dos antes e depois (padrão: a de --antes)")
    a = ap.parse_args()
    antes = cv2.imread(a.antes or str(FINAL))
    depois = aplicar(antes)
    destino = Path(a.saida) if a.saida else FINAL
    cv2.imwrite(str(destino), depois)
    print(f"    {destino}")
    if not a.saida:
        ref = cv2.imread(a.antes_depois) if a.antes_depois else antes
        antes_depois(ref, depois)


if __name__ == "__main__":
    main()

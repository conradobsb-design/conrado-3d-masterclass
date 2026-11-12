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
                "claraboia": (2240, 335, 2360, 425), "lavabo_vaso_bancada": (2250, 340, 2365, 525)}


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
    return out


def doze(out, s, X0, Ya3):
    """No 12K (`ampliacao_12k_terreo_casaa.montar12k`, antes dos tracejados e dos textos)."""
    out = BP.pergolado_12k(out, s, X0, Ya3)
    out = brises_12k(out, s, X0, Ya3)
    out = porta_12k(out, s, X0, Ya3)
    out = deck_12k(out, s, X0, Ya3)
    out = jardim_12k(out, s, X0, Ya3)
    out = bancada_12k(out, s, X0, Ya3)
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

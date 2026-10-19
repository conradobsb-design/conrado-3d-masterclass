#!/usr/bin/env python3
"""Texturas de referência das plantas humanizadas (POE 642), as mesmas para todas as casas.

Pedido do usuário (19/10/26): "vamos inserir as referências de imagem das texturas (que devem simular pedra, não
porcelanato) a serem utilizadas em todas as casas. lembrando da importância de aplicar a devida escala aos renders.
1- Bege bahia. 2- Travertino 3- Quartzito Aura 4- Pedra Portuguesa 5- Marrom granito (deixar mais liso e menos
escuro)".

- As fotos que o usuário mandou ficam em `originais/`, como vieram.
- `python3 texturas.py` prepara as versões de uso, em `texturas.json` (uma por material, com a largura real que a imagem
  cobre). Duas são tratadas:
  - pedra portuguesa: a foto é de uma calçada em perspectiva; vira vista de cima (homografia pelas duas bordas da
    calçada, que se encontram no ponto de fuga), só a faixa do meio, sem a grama e o meio-fio;
  - granito marrom: mais liso (o ruído fino e as manchas atenuados) e menos escuro (tons x 1,25), como pedido.
- Madeira, vinílico, grama e vegetação externa vêm da planta humanizada de referência que o usuário mandou
  (`originais/referencia_planta.webp`; pedido de 19/10/26: "para o madeira e o vinílico, use a imagem de referência.
  use também a vegetação externa como referencia dessa imagem também. Importante preservar a escala. Use a grama
  como referência também"). A escala foi medida nela (camas, carros e portas: 26 px/m); as texturas saem de recortes
  limpos (o deck, o piso dos quartos e o gramado fora da sombra), na escala dela.
- `vegetacao()` recorta da referência as árvores, os arbustos e as palmeiras, com fundo transparente, em
  `vegetacao/`; `pousar(fundo, nome, cx, cy, px_por_m)` põe uma delas num render, no tamanho real e com a sombra.
- `textura(nome, px_por_m, alto, largo)` devolve a textura na escala do render: a imagem é reduzida para que a
  largura real dela caia em px_por_m e tecida por image quilting (sem repetição visível, como pedra natural), no
  tamanho pedido. A escala de cada render vem do PDF (1:50: 1 pt = 17,64 mm) e do afim do pavimento.

Uso:
  python3 texturas.py              # prepara as texturas de uso, as plantas e a cartela (cartela_texturas.jpg)
"""
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

AQUI = Path(__file__).resolve().parent
CONFIG = AQUI / "texturas.json"
M_POR_PT = 0.0254 / 72 * 50              # 1:50: um ponto do PDF são 17,64 mm


def ler(caminho):
    return np.asarray(Image.open(caminho).convert("RGB"))[..., ::-1].astype(np.float32)


def pedra_portuguesa_de_cima(img, q):
    """A faixa do meio da calçada, vista de cima: as duas bordas da calçada (grama e meio-fio) se encontram no ponto
    de fuga; as linhas entre elas, pelas frações t da largura, são paralelas no chão."""
    (ax, ay), (bx, by) = q["borda_esq"]
    (cx, cy), (dx, dy) = q["borda_dir"]
    # ponto de fuga: o encontro das duas bordas
    A = np.array([[bx - ax, -(dx - cx)], [by - ay, -(dy - cy)]], float)
    s, _ = np.linalg.solve(A, np.array([cx - ax, cy - ay], float))
    vp = np.array([ax + s * (bx - ax), ay + s * (by - ay)])
    yb = q["base_y"]
    xe = ax + (bx - ax) * (yb - ay) / (by - ay)
    xd = cx + (dx - cx) * (yb - cy) / (dy - cy)

    def ponto(t, y):
        alvo = np.array([xe + t * (xd - xe), yb])
        return vp + (alvo - vp) * (y - vp[1]) / (yb - vp[1])
    t1, t2 = q["faixa_t"]
    src = np.float32([ponto(t1, q["topo_y"]), ponto(t2, q["topo_y"]), ponto(t2, yb - 1), ponto(t1, yb - 1)])
    larg = int(round((t2 - t1) * (xd - xe)))
    alto = int(round(larg * q["alto_por_largura"]))
    H = cv2.getPerspectiveTransform(src, np.float32([(0, 0), (larg, 0), (larg, alto), (0, alto)]))
    return cv2.warpPerspective(img, H, (larg, alto), flags=cv2.INTER_CUBIC)


def granito_liso(img, q):
    """Mais liso e menos escuro: o fundo largo fica; as manchas médias e o grão fino, atenuados; os tons sobem."""
    base = cv2.GaussianBlur(img, (0, 0), 12)
    meio = cv2.GaussianBlur(cv2.bilateralFilter(img, 9, 30, 5), (0, 0), 1.2) - base
    fino = img - cv2.GaussianBlur(img, (0, 0), 1.2)
    return np.clip((base + q["manchas"] * meio + (1 - q["liso"]) * fino) * q["clarear"], 0, 255)


def variantes(img, direcional):
    """Os espelhos (e, nas pedras sem direção, os giros de 90°): mais retalhos diferentes para o quilting."""
    vs = [img, img[:, ::-1], img[::-1, :], img[::-1, ::-1]]
    if not direcional:
        vs += [np.rot90(v) for v in vs]
    return [np.ascontiguousarray(v) for v in vs]


def preparar():
    """As texturas de uso (o tratamento de cada foto) e, de cada uma, a amostra grande: 3 x 3 m tecidos na resolução
    de trabalho (retalhos pequenos perto da foto, para a pedra variar de verdade), que é de onde sai a textura em
    qualquer escala. Sem ela, numa escala pequena a foto de 60 cm vira poucos px e o quilting só a repete em espelho,
    com cara de porcelanato."""
    cfg = json.loads(CONFIG.read_text())
    (AQUI / "amostras").mkdir(exist_ok=True)
    for nome, m in cfg["materiais"].items():
        a = {**cfg["amostra"], **m.get("amostra", {})}
        if m.get("fonte") == "referencia":
            ref = cfg["referencia_planta"]
            planta = ler(AQUI / ref["original"])
            fontes = [planta[y0:y1, x0:x1] for x0, y0, x1, y1 in m["recortes"]]
            img, px_m = max(fontes, key=lambda f: f.size), ref["px_por_m"]
            print(f"{nome}: {len(fontes)} recorte(s) da referência ({px_m} px/m), o maior "
                  f"{img.shape[1] / px_m:.2f} x {img.shape[0] / px_m:.2f} m")
        else:
            img = ler(AQUI / m["original"])
            t = m.get("tratamento")
            if t and t["tipo"] == "vista_de_cima":
                img = pedra_portuguesa_de_cima(img, t)
            elif t and t["tipo"] == "liso_e_claro":
                img = granito_liso(img, t)
            if img.shape[1] > a["largura_max_uso"]:
                img = cv2.resize(img, (a["largura_max_uso"], round(img.shape[0] * a["largura_max_uso"] / img.shape[1])),
                                 interpolation=cv2.INTER_AREA)
            fontes, px_m = [img], img.shape[1] / m["largura_m"]
            alto_m = m["largura_m"] * img.shape[0] / img.shape[1]
            print(f"{nome}: {img.shape[1]} x {img.shape[0]} px = {m['largura_m']:.2f} x {alto_m:.2f} m "
                  f"({px_m:.0f} px/m)")
        cv2.imwrite(str(AQUI / m["arquivo"]), np.clip(img, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 95])
        f = a["px_por_m"] / px_m
        if abs(f - 1) > 1e-3:
            fontes = [cv2.resize(fo, (round(fo.shape[1] * f), round(fo.shape[0] * f)), interpolation=cv2.INTER_AREA)
                      for fo in fontes]
        lado = round(a["lado_m"] * a["px_por_m"])
        am = quilting([v for fo in fontes for v in variantes(fo, m.get("direcional", False))], lado, lado,
                      p=a["retalho"], sobra=max(3, a["retalho"] // 4), candidatos=300,
                      rng=np.random.default_rng(642))[:lado, :lado]
        cv2.imwrite(str(AQUI / "amostras" / f"{nome}.jpg"), np.clip(am, 0, 255).astype(np.uint8),
                    [cv2.IMWRITE_JPEG_QUALITY, 95])
        print(f"    amostra {a['lado_m']} x {a['lado_m']} m ({lado} px, {a['px_por_m']} px/m)")


def recorte_planta(img, cx, cy, r, F=4):
    """Uma planta da referência com fundo transparente (BGR e alfa, ampliados F x). O contorno sai da textura das
    folhas: a copa tem detalhe fino; a grama em volta, lisa (mesmo na sombra). Pelo raio, de dentro para fora, o
    contorno é onde o detalhe some; suavizado em volta, sem pegar as plantas vizinhas, e com as bordas das folhas
    (sem a grama na sombra, mais escura que a copa, nem o piso, que não é verde)."""
    from scipy.ndimage import median_filter, uniform_filter1d
    m = int(r * 1.25) + 3
    x0, y0 = cx - m, cy - m
    c = img[max(0, y0):cy + m + 1, max(0, x0):cx + m + 1]
    c = cv2.copyMakeBorder(c, max(0, -y0), 0, max(0, -x0), 0, cv2.BORDER_REPLICATE)
    cu = np.clip(cv2.resize(c, None, fx=F, fy=F, interpolation=cv2.INTER_CUBIC), 0, 255)
    L = cu.mean(2)
    h, w = L.shape
    C, R = (w / 2, h / 2), r * F
    yy, xx = np.mgrid[0:h, 0:w]
    rad = np.hypot(xx - C[0], yy - C[1])
    E = cv2.GaussianBlur(np.abs(L - cv2.GaussianBlur(L, (0, 0), 1.2 * F)), (0, 0), 1.5 * F)
    rmax = int(1.2 * R)
    pol = cv2.warpPolar(E, (rmax, 360), C, rmax, cv2.WARP_POLAR_LINEAR)
    thr = 0.5 * (np.median(pol[:, int(0.3 * R):int(0.8 * R)]) + np.median(E[rad > 1.15 * R]))
    r0, seguidos = int(0.6 * R), max(2, int(0.08 * R))
    raios = np.empty(360, np.float32)
    for a in range(360):
        abaixo = pol[a, r0:rmax] < thr
        fim = next((i for i in range(len(abaixo) - seguidos) if abaixo[i:i + seguidos].all()), len(abaixo))
        raios[a] = r0 + fim
    raios = uniform_filter1d(median_filter(np.clip(raios, 0.85 * R, 1.05 * R), 41, mode="wrap"), 15, mode="wrap")
    ang = np.degrees(np.arctan2(yy - C[1], xx - C[0])) % 360
    lim = np.interp(ang, np.arange(361), np.append(raios, raios[0]))
    limite = np.clip((lim - rad) / (1.2 * F) + 0.5, 0, 1)
    Ef = cv2.GaussianBlur(np.abs(L - cv2.GaussianBlur(L, (0, 0), F)), (0, 0), 0.9 * F)
    nucleo, grama = np.median(Ef[rad < 0.5 * R]), np.median(Ef[rad > 1.15 * R])
    folha = np.clip((Ef - grama) / max(1e-3, 0.7 * (nucleo - grama)), 0, 1)
    folha = cv2.morphologyEx(folha, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3 * F + 1,) * 2))
    # fora do miolo, nem a grama na sombra (mais escura que a copa) nem o piso (cinza, sem verde) entram
    escuro = np.percentile(L[rad < 0.6 * R], 8)
    verde = cu[..., 1] - (cu[..., 0] + cu[..., 2]) / 2
    planta = np.clip((L - 0.85 * escuro) / (0.15 * escuro + 1e-3), 0, 1) * np.clip((verde - 2) / 8, 0, 1)
    alfa = np.maximum(np.clip((0.82 * lim - rad) / (2 * F) + 0.5, 0, 1), folha * planta) * limite
    return cu, cv2.GaussianBlur(alfa, (0, 0), 0.6 * F)


def vegetacao():
    """As plantas da referência em `vegetacao/<nome>.png` (RGBA, na escala px_por_m_sprite)."""
    cfg = json.loads(CONFIG.read_text())
    v, ref = cfg["vegetacao"], cfg["referencia_planta"]
    img = ler(AQUI / ref["original"])
    (AQUI / "vegetacao").mkdir(exist_ok=True)
    F = 4
    f = v["px_por_m_sprite"] / (ref["px_por_m"] * F)
    for nome, p in v["plantas"].items():
        cu, alfa = recorte_planta(img, *p["centro"], p["raio"], F)
        tam = (round(cu.shape[1] * f), round(cu.shape[0] * f))
        rgba = np.dstack([cv2.resize(cu, tam, interpolation=cv2.INTER_AREA),
                          cv2.resize(alfa, tam, interpolation=cv2.INTER_AREA) * 255])
        cv2.imwrite(str(AQUI / "vegetacao" / f"{nome}.png"), np.clip(rgba, 0, 255).astype(np.uint8))
        print(f"{nome}: copa de {2 * p['raio'] / ref['px_por_m']:.2f} m ({p['tipo']})")


def planta(nome, px_por_m):
    """A planta na escala do render: BGR e alfa (0 a 1), float32, com a copa no centro."""
    cfg = json.loads(CONFIG.read_text())
    s = cv2.imread(str(AQUI / "vegetacao" / f"{nome}.png"), cv2.IMREAD_UNCHANGED).astype(np.float32)
    f = px_por_m / cfg["vegetacao"]["px_por_m_sprite"]
    s = cv2.resize(s, (max(1, round(s.shape[1] * f)), max(1, round(s.shape[0] * f))),
                   interpolation=cv2.INTER_AREA if f < 1 else cv2.INTER_CUBIC)
    return np.clip(s[..., :3], 0, 255), np.clip(s[..., 3] / 255, 0, 1)


def pousar(fundo, nome, cx, cy, px_por_m, sombra=True):
    """Põe a planta `nome` com o centro em (cx, cy) no render `fundo` (BGR float32, alterado no lugar), no tamanho
    real pela escala do render, com a sombra da referência (para baixo e à esquerda)."""
    cfg = json.loads(CONFIG.read_text())
    cor, alfa = planta(nome, px_por_m)
    d = 2 * cfg["vegetacao"]["plantas"][nome]["raio"] / cfg["referencia_planta"]["px_por_m"] * px_por_m
    camadas = []
    if sombra:
        s = cfg["vegetacao"]["sombra"]
        a = cv2.GaussianBlur(alfa, (0, 0), max(0.5, s["desfoque"] * d)) * s["opacidade"]
        camadas.append((None, a, cx + s["dx"] * d, cy + s["dy"] * d))
    camadas.append((cor, alfa, cx, cy))
    for c, a, x, y in camadas:
        h, w = a.shape
        x0, y0 = int(round(x - w / 2)), int(round(y - h / 2))
        fx0, fy0, fx1, fy1 = max(0, x0), max(0, y0), min(fundo.shape[1], x0 + w), min(fundo.shape[0], y0 + h)
        if fx1 <= fx0 or fy1 <= fy0:
            continue
        aa = a[fy0 - y0:fy1 - y0, fx0 - x0:fx1 - x0, None]
        reg = fundo[fy0:fy1, fx0:fx1]
        alvo = reg * 0.35 if c is None else c[fy0 - y0:fy1 - y0, fx0 - x0:fx1 - x0]
        fundo[fy0:fy1, fx0:fx1] = reg * (1 - aa) + alvo * aa


def quilting(fontes, alto, largo, p=36, sobra=10, candidatos=400, rng=None):
    """Image quilting (Efros e Freeman): blocos das fontes, escolhidos pela sobreposição, com a costura mínima."""
    import sys
    sys.path.insert(0, str(AQUI.parent / "POE642_CasaA" / "scripts"))
    from texturizar_base import quilting as q_
    return q_(fontes, alto, largo, p=p, sobra=sobra, candidatos=candidatos, rng=rng)


def textura(nome, px_por_m, alto, largo, semente=642):
    """A textura do material na escala do render (px_por_m), tecida no tamanho pedido (BGR, float32): a amostra do
    material (3 x 3 m nas pedras, 10 a 12 m nas da referência) levada à escala e tecida por image quilting (retalhos
    dela, com os espelhos e, nas sem direção, os giros)."""
    cfg = json.loads(CONFIG.read_text())
    m = cfg["materiais"][nome]
    a = {**cfg["amostra"], **m.get("amostra", {})}
    am = ler(AQUI / "amostras" / f"{nome}.jpg")
    lado = max(16, round(a["lado_m"] * px_por_m))
    peq = cv2.resize(am, (lado, lado), interpolation=cv2.INTER_AREA)
    if alto <= lado and largo <= lado:
        rng = np.random.default_rng(semente)
        y, x = int(rng.integers(0, lado - alto + 1)), int(rng.integers(0, lado - largo + 1))
        return peq[y:y + alto, x:x + largo].copy()
    p = int(min(40, lado // 4))
    return quilting(variantes(peq, m.get("direcional", False)), alto, largo, p=p, sobra=max(3, p // 4),
                    rng=np.random.default_rng(semente))[:alto, :largo]


def cartela():
    """As texturas: a foto de referência, a versão de uso e um trecho de 3 x 2 m na escala da prancha (a planta da
    Casa A em 3840 px: 1 m = 60 px), ampliado 3 x ao lado para ver o desenho. Por último, as plantas da referência
    sobre a grama, no tamanho real, na mesma escala."""
    import sys
    sys.path.insert(0, str(AQUI.parent / "POE642_CasaA" / "scripts"))
    from PIL import ImageDraw, ImageFont
    from rodape_entrega import FONTES
    cfg = json.loads(CONFIG.read_text())
    px_m = cfg["escala_prancha_px_por_m"]
    ref = cfg["referencia_planta"]
    planta_ref = ler(AQUI / ref["original"])
    H = 300

    def caber(a, h=H, wmax=640):
        f = min(h / a.shape[0], wmax / a.shape[1])
        return cv2.resize(a, (round(a.shape[1] * f), round(a.shape[0] * f)),
                          interpolation=cv2.INTER_AREA if f < 1 else cv2.INTER_CUBIC)

    def com_recortes(caixas, cor=(40, 40, 230)):
        im = planta_ref.copy()
        for x0, y0, x1, y1 in caixas:
            cv2.rectangle(im, (x0, y0), (x1 - 1, y1 - 1), cor, 2)
        return im

    def montar(pecas):
        linha = np.full((H + 70, 40 + sum(p.shape[1] + 30 for p in pecas), 3), 255, np.float32)
        x = 40
        for p in pecas:
            linha[60:60 + p.shape[0], x:x + p.shape[1]] = p
            x += p.shape[1] + 30
        return linha

    linhas = []
    for nome, m in cfg["materiais"].items():
        uso = ler(AQUI / m["arquivo"])
        if m.get("fonte") == "referencia":
            ref_img, larg = com_recortes(m["recortes"]), uso.shape[1] / ref["px_por_m"]
            sub = f"recortes da planta de referência ({ref['px_por_m']} px/m)"
        else:
            ref_img, larg = ler(AQUI / m["original"]), m["largura_m"]
            sub = f"a imagem cobre {larg:.2f} m de largura"
        tr = textura(nome, px_m, round(2 * px_m), round(3 * px_m))
        amp = cv2.resize(tr, None, fx=3, fy=3, interpolation=cv2.INTER_NEAREST)
        pecas = [caber(ref_img), caber(uso),
                 np.vstack([tr, np.full((H - tr.shape[0], tr.shape[1], 3), 255, np.float32)]), amp[:H]]
        linhas.append((f"{m['titulo']}  ·  {sub}  ·  foto  |  textura de uso  |  3 x 2 m na escala da prancha  |  "
                       "o mesmo, ampliado 3 x", montar(pecas), []))

    # as plantas, no tamanho real, sobre a grama
    v = cfg["vegetacao"]
    diam = {n: 2 * p["raio"] / ref["px_por_m"] for n, p in v["plantas"].items()}
    folga = 0.6
    larg_m = sum(diam.values()) + folga * (len(diam) + 1)
    jardim = textura("grama", px_m, H, round(larg_m * px_m), semente=7)
    x_m, marcas = folga, []
    for n, d in diam.items():
        cx = (x_m + d / 2) * px_m
        cy = H / 2 if d > 2.5 else H * 0.42
        pousar(jardim, n, cx, cy, px_m)
        marcas.append((cx, f"{n.replace('_', ' ')}", f"{d:.1f} m"))
        x_m += d + folga
    ref_v = com_recortes([[p["centro"][0] - p["raio"], p["centro"][1] - p["raio"],
                           p["centro"][0] + p["raio"], p["centro"][1] + p["raio"]] for p in v["plantas"].values()])
    pv = caber(ref_v)
    linha = montar([pv, jardim])
    linha = np.vstack([linha, np.full((50, linha.shape[1], 3), 255, np.float32)])
    x_j = 40 + pv.shape[1] + 30
    linhas.append(("9. Vegetação externa  ·  recortada da planta de referência, com a sombra dela  ·  "
                   f"sobre a grama, no tamanho real, na escala da prancha (1 m = {px_m} px)", linha,
                   [(x_j + cx, t1, t2) for cx, t1, t2 in marcas]))

    larg = max(li.shape[1] for _, li, _ in linhas)
    tela = np.full((80 + sum(li.shape[0] for _, li, _ in linhas), larg, 3), 255, np.float32)
    y, pos = 80, []
    for titulo, li, marc in linhas:
        tela[y:y + li.shape[0], :li.shape[1]] = li
        pos.append((y, titulo, marc))
        y += li.shape[0]
    im = Image.fromarray(np.clip(tela, 0, 255).astype(np.uint8)[..., ::-1])
    d = ImageDraw.Draw(im)
    f1 = ImageFont.truetype(str(FONTES / "Inter-Medium.otf"), 30)
    f2 = ImageFont.truetype(str(FONTES / "Inter-Regular.otf"), 20)
    f3 = ImageFont.truetype(str(FONTES / "Inter-Regular.otf"), 17)
    d.text((40, 24), "Texturas de referência · POE 642 · todas as casas", font=f1, fill=(40, 40, 40))
    for y, titulo, marc in pos:
        d.text((40, y + 14), titulo, font=f2, fill=(60, 60, 60))
        for cx, t1, t2 in marc:
            for k, t in enumerate((t1, t2)):
                w = d.textlength(t, font=f3)
                d.text((cx - w / 2, y + 60 + H + 8 + 20 * k), t, font=f3, fill=(70, 70, 70))
    im.save(AQUI / "cartela_texturas.jpg", quality=92)
    print(AQUI / "cartela_texturas.jpg", im.size)


if __name__ == "__main__":
    preparar()
    vegetacao()
    cartela()

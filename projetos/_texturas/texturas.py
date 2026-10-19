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
- `textura(nome, px_por_m, alto, largo)` devolve a textura na escala do render: a imagem é reduzida para que a
  largura real dela caia em px_por_m e tecida por image quilting (sem repetição visível, como pedra natural), no
  tamanho pedido. A escala de cada render vem do PDF (1:50: 1 pt = 17,64 mm) e do afim do pavimento.

Uso:
  python3 texturas.py              # prepara as texturas de uso e a cartela (cartela_texturas.jpg)
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
    a = cfg["amostra"]
    (AQUI / "amostras").mkdir(exist_ok=True)
    for nome, m in cfg["materiais"].items():
        img = ler(AQUI / m["original"])
        t = m.get("tratamento")
        if t and t["tipo"] == "vista_de_cima":
            img = pedra_portuguesa_de_cima(img, t)
        elif t and t["tipo"] == "liso_e_claro":
            img = granito_liso(img, t)
        if img.shape[1] > a["largura_max_uso"]:
            img = cv2.resize(img, (a["largura_max_uso"], round(img.shape[0] * a["largura_max_uso"] / img.shape[1])),
                             interpolation=cv2.INTER_AREA)
        cv2.imwrite(str(AQUI / m["arquivo"]), np.clip(img, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 95])
        alto_m = m["largura_m"] * img.shape[0] / img.shape[1]
        print(f"{nome}: {img.shape[1]} x {img.shape[0]} px = {m['largura_m']:.2f} x {alto_m:.2f} m "
              f"({img.shape[1] / m['largura_m']:.0f} px/m)")
        f = a["px_por_m"] * m["largura_m"] / img.shape[1]
        fonte = cv2.resize(img, (round(img.shape[1] * f), round(img.shape[0] * f)), interpolation=cv2.INTER_AREA)
        lado = round(a["lado_m"] * a["px_por_m"])
        am = quilting(variantes(fonte, m.get("direcional", False)), lado, lado, p=a["retalho"],
                      sobra=a["retalho"] // 4, candidatos=300, rng=np.random.default_rng(642))[:lado, :lado]
        cv2.imwrite(str(AQUI / "amostras" / f"{nome}.jpg"), np.clip(am, 0, 255).astype(np.uint8),
                    [cv2.IMWRITE_JPEG_QUALITY, 95])
        print(f"    amostra {a['lado_m']} x {a['lado_m']} m ({lado} px, {a['px_por_m']} px/m)")


def quilting(fontes, alto, largo, p=36, sobra=10, candidatos=400, rng=None):
    """Image quilting (Efros e Freeman): blocos das fontes, escolhidos pela sobreposição, com a costura mínima."""
    import sys
    sys.path.insert(0, str(AQUI.parent / "POE642_CasaA" / "scripts"))
    from texturizar_base import quilting as q_
    return q_(fontes, alto, largo, p=p, sobra=sobra, candidatos=candidatos, rng=rng)


def textura(nome, px_por_m, alto, largo, semente=642):
    """A textura do material na escala do render (px_por_m), tecida no tamanho pedido (BGR, float32): a amostra de
    3 x 3 m reduzida à escala e tecida por image quilting (retalhos dela, com os espelhos e giros)."""
    cfg = json.loads(CONFIG.read_text())
    m, a = cfg["materiais"][nome], cfg["amostra"]
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
    """As cinco texturas: a foto de referência, a versão de uso e um trecho de 3 x 2 m na escala da prancha (a planta
    da Casa A em 3840 px: 1 m = 60 px), ampliado 3 x ao lado para ver o desenho."""
    import sys
    sys.path.insert(0, str(AQUI.parent / "POE642_CasaA" / "scripts"))
    from PIL import ImageDraw, ImageFont
    from rodape_entrega import FONTES
    cfg = json.loads(CONFIG.read_text())
    px_m = cfg["escala_prancha_px_por_m"]
    linhas = []
    for nome, m in cfg["materiais"].items():
        ref = ler(AQUI / m["original"])
        uso = ler(AQUI / m["arquivo"])

        def caber(a, h=300):
            return cv2.resize(a, (round(a.shape[1] * h / a.shape[0]), h), interpolation=cv2.INTER_AREA)
        tr = textura(nome, px_m, round(2 * px_m), round(3 * px_m))
        amp = cv2.resize(tr, None, fx=3, fy=3, interpolation=cv2.INTER_NEAREST)
        h = 300
        peca = [caber(ref), caber(uso), np.vstack([tr, np.full((h - tr.shape[0], tr.shape[1], 3), 255, np.float32)]),
                amp[:h]]
        linha = np.full((h + 70, 40 + sum(p.shape[1] + 30 for p in peca), 3), 255, np.float32)
        x = 40
        for p in peca:
            linha[60:60 + p.shape[0], x:x + p.shape[1]] = p
            x += p.shape[1] + 30
        linhas.append((nome, m, linha))
    larg = max(li.shape[1] for _, _, li in linhas)
    tela = np.full((80 + sum(li.shape[0] for _, _, li in linhas), larg, 3), 255, np.float32)
    y = 80
    marcas = []
    for nome, m, li in linhas:
        tela[y:y + li.shape[0], :li.shape[1]] = li
        marcas.append((y, nome, m))
        y += li.shape[0]
    im = Image.fromarray(np.clip(tela, 0, 255).astype(np.uint8)[..., ::-1])
    d = ImageDraw.Draw(im)
    f1 = ImageFont.truetype(str(FONTES / "Inter-Medium.otf"), 30)
    f2 = ImageFont.truetype(str(FONTES / "Inter-Regular.otf"), 20)
    d.text((40, 24), "Texturas de referência · POE 642 · todas as casas", font=f1, fill=(40, 40, 40))
    for y, nome, m in marcas:
        d.text((40, y + 14), f"{m['titulo']}  ·  a imagem cobre {m['largura_m']:.2f} m de largura  ·  "
               "foto  |  textura de uso  |  3 x 2 m na escala da prancha  |  o mesmo, ampliado 3 x",
               font=f2, fill=(60, 60, 60))
    im.save(AQUI / "cartela_texturas.jpg", quality=92)
    print(AQUI / "cartela_texturas.jpg", im.size)


if __name__ == "__main__":
    preparar()
    cartela()

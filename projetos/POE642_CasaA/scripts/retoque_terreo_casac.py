#!/usr/bin/env python3
"""Retoque sem IA do render do Térreo da Casa C (prompt v3). A imagem final é o render.

Os erros são corrigidos um a um, na ordem combinada com o usuário.

1. Chuveiros de teto: o motor deixou os boxes vazios. Cada um recebe a placa quadrada aprovada
   na Casa A (banho 3 do 1º Pavimento, 11 x 11 px, a mesma escala), no centro do símbolo do PDF
   (quadrado de 20 cm da layer ARQ_LOUÇAS E METAIS, levado ao render pela base alinhada).
2. Plantas fora do lote: o motor deixou palmeiras passando da linha tracejada em todo o lado
   esquerdo e do muro nos cantos de cima e de baixo à esquerda. Fora do lote volta a ser o que a
   base tem (fundo branco e linha tracejada); os dois trechos de muro cobertos pelas folhas são
   refeitos com o próprio muro do render, um pouco à direita. A vegetação termina no lote.
3. Jardins de inverno: as plantas passavam dos vidros, sobre o piso, a caixa do elevador e os
   próprios vidros. Ficam só dentro das floreiras (geometria medida no render). Os vidros e a
   parede de baixo do elevador são refeitos com o perfil de um trecho limpo do mesmo elemento; as
   faixas de piso com folha ou sombra são trocadas pelo piso limpo logo ao lado, com emenda suave.
   As portas de correr de vidro (folhas em dois planos dos lados, embaixo e em cima do jardim 2)
   vêm da base alinhada, que coincide com o render nos montantes; entre as folhas, piso do lado de
   fora e floreira do lado de dentro.
4. Cozinha: o motor fez as bancadas e a ilha no granito do piso, com uma cuba só. Bancadas e ilha
   ficam no quartzo claro da bancada gourmet do próprio render (image quilting), com o cooktop e as
   banquetas como estão; os dois armários altos (retângulo com diagonal no PDF: o de baixo à
   esquerda e o junto à geladeira) viram o tampo do armário em marcenaria areia, tecida do painel
   do quarto, com contorno nas faces livres e sem a diagonal, como os armários das Casas A e B;
   entre a geladeira e o armário volta o vão de piso do PDF; as duas
   cubas do PDF são desenhadas como as do lavatório gourmet da Casa B, com a torneira do lado da
   parede.
5. Quarto externo: o motor trocou a cama de solteiro do PDF por dois eletrodomésticos e o
   criado-mudo por uma caixa branca. A cama vem de uma das camas de solteiro do próprio render
   (quarto 2), virada para a cabeceira ficar na parede da direita como no PDF, encurtada no
   cobertor e ajustada à largura do PDF; o criado-mudo vem do criado-mudo da suíte. O piso que
   ficou à mostra (a sombra do eletrodoméstico) vem do piso limpo ao lado, e cada peça ganha a
   sombra curta que as camas do render têm.

As coordenadas estão em px do render (2000 x 1116).

Uso:
  python retoque_terreo_casac.py RENDER.webp --saida PASTA --nome NOME
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent          # projetos/
sys.path.insert(0, str(AQUI))
from retoque_terreo_casab import cuba  # noqa: E402
from texturizar_base import quilting  # noqa: E402

BASE = RAIZ / "POE642_CasaC/bases/POE642_CasaC_BASE_Terreo_v3_texturas_16x9.png"
BASE_CHAPADA = RAIZ / "POE642_CasaC/bases/POE642_CasaC_BASE_Terreo_v2_16x9.png"   # cores exatas da legenda
VIDRO = (211, 214, 214)                                  # BGR de #D6D6D3
# lote no render: linha tracejada da esquerda e muros de cima e de baixo
LOTE = {"x_esq": 155, "muro_cima": (24, 32), "muro_baixo": (952, 958)}
# trecho com folhas por cima dos muros (x) e coluna limpa de onde o muro é copiado
MURO_COBERTO = {"x": (150, 262), "coluna_limpa": 300}
# jardins de inverno no render: interiores (onde as plantas ficam), vidros e parede do elevador.
# Cada vidro/parede: faixa [x0, x1) x [y0, y1) e o perfil limpo (linha ou coluna) que a refaz.
JARDINS = {
    "interiores": [(924, 482, 1055, 615), (984, 424, 1057, 475)],      # onde as plantas ficam
    "faixas": [
        {"nome": "vidro esquerdo", "ret": (918, 482, 924, 615), "perfil": ("linha", 560)},
        {"nome": "vidro direito", "ret": (1055, 482, 1061, 615), "perfil": ("linha", 600)},
        {"nome": "vidro de baixo", "ret": (924, 616, 1055, 621), "perfil": ("coluna", 1040)},
        {"nome": "vidro de cima do jardim 2", "ret": (984, 419, 1057, 424), "perfil": ("coluna", 1040, 616)},
        {"nome": "parede de baixo do elevador", "ret": (918, 475, 984, 482), "perfil": ("coluna", 930)},
    ],
    # faixas de piso com folha ou sombra de folha: trocadas inteiras pelo piso limpo ao lado
    # (veios verticais: de lado à esquerda, de baixo para a faixa de baixo), com emenda suave
    "pisos": [
        ("à esquerda do jardim", (895, 478, 918, 626), (-22, 0)),
        ("abaixo do jardim", (916, 621, 1063, 635), (0, 14)),
        ("interior do elevador, embaixo", (936, 455, 978, 475), (0, -20)),
    ],
    "emenda": 3,
    # portas de vidro: faixa, deslocamento para dentro (floreira), eixo e limite da floreira
    # (do lado de dentro do limite é floreira; do lado de fora, piso)
    "portas": [
        ("esquerda", (914, 482, 927, 618), (13, 0), "x", 924),
        ("direita", (1048, 482, 1063, 618), (-15, 0), "x", 1054),
        ("embaixo", (919, 609, 1060, 624), (0, -15), "y", 614),
        ("em cima do jardim 2", (984, 416, 1057, 428), (0, 12), "y", 424),
    ],
}
# cozinha (geometria medida no render, conferida com o PDF levado ao render)
COZINHA = {
    # bancada de cima (das cubas), bancada da esquerda, ilha e bancada de baixo à direita
    "quartzo": [(1131, 131, 1283, 150), (1131, 150, 1147, 238), (1176, 188, 1213, 286),
                (1265, 281, 1283, 340)],
    "cooktop": (1192, 207, 1212, 239),          # fica, com o contorno escuro em volta
    # armários altos (o de baixo à esquerda e o junto à geladeira) e as faces livres (as que não
    # encostam em parede), onde vai o contorno
    "armarios": [((1131, 238, 1147, 323), ("cima", "direita")),
                 ((1265, 257, 1283, 281), ("cima", "esquerda", "baixo"))],
    # vão de piso entre a geladeira e o armário (no render era bancada): piso de 22 px à esquerda,
    # com a sombra junto ao armário igual à da bancada (fator por linha, até o armário), só da
    # coluna da sombra lateral da bancada para a direita
    "vao": ((1258, 251, 1283, 257), -22, (0.70, 0.59, 0.51), 1262),
    "cubas": [(1177, 135, 1197, 149), (1202, 135, 1222, 149)],
    # quartzo limpo da bancada gourmet (os dois lados do cooktop e o braço da esquerda)
    "fonte_quartzo": [(646, 566, 714, 596), (752, 566, 812, 596), (647, 507, 666, 560)],
    "fonte_areia": (690, 281, 744, 290),         # painel laqueado do quarto (liso)
    "contorno": 0.75,                            # face livre do armário (1 px)
}
# quarto externo (geometria da base chapada alinhada; paredes conferidas no render)
QUARTO_EXTERNO = {
    "cama": (1589, 389, 1650, 419),              # até a parede da direita e a de baixo
    "fonte_cama": (753, 189, 825, 222),          # cama de solteiro de cima do quarto 2 (cabeceira à esquerda)
    "cortar_cobertor": (796, 807),               # colunas do cobertor liso tiradas da fonte
    "criado": (1636, 369, 1650, 386),
    "fonte_criado": (733, 178, 747, 195),        # criado-mudo da suíte
    # piso: a sombra do eletrodoméstico à esquerda da cama e a borda de cima da caixa branca
    "pisos": [((1584, 386, 1590, 419), (-12, 0)), ((1636, 368, 1650, 369), (0, -3))],
    "sombra_cima": 0.91,                         # como em cima das camas do quarto 2
    "sombra_pe": 0.93,                           # no pé da cama (a ponta das camas do quarto 2)
}
CHUVEIRO_TETO = (RAIZ / "POE642_CasaA/renders/POE642_CasaA_PH_1Pavimento_v7_final2.png", (1160, 214, 1171, 225))
CHUVEIROS = {
    "BH master 1": (411.2, 187.9),
    "BH 3": (630.5, 149.8),
    "BH 2": (868.4, 149.8),
    "BH 1": (1016.1, 149.8),
    "BH master 2": (442.3, 484.6),
}


def chuveiros_teto(out):
    img = cv2.imread(str(CHUVEIRO_TETO[0]))
    hx0, hy0, hx1, hy1 = CHUVEIRO_TETO[1]
    cab = img[hy0:hy1, hx0:hx1]
    for nome, (cx, cy) in CHUVEIROS.items():
        px, py = round(cx - (hx1 - hx0 - 1) / 2), round(cy - (hy1 - hy0 - 1) / 2)
        out[py:py + cab.shape[0], px:px + cab.shape[1]] = cab
        print(f"    {nome}: chuveiro de teto em ({cx}, {cy})")
    return out


def alinhar_base(render):
    """Base 16:9 reduzida e levada ao render por SIFT + afim; também a base chapada (v2)."""
    base = cv2.resize(cv2.imread(str(BASE)), render.shape[1::-1], interpolation=cv2.INTER_AREA)
    sift = cv2.SIFT_create(10000)
    k1, d1 = sift.detectAndCompute(cv2.cvtColor(base, cv2.COLOR_BGR2GRAY), None)
    k2, d2 = sift.detectAndCompute(cv2.cvtColor(render, cv2.COLOR_BGR2GRAY), None)
    pares = [a for a, b in cv2.BFMatcher().knnMatch(d1, d2, k=2) if a.distance < 0.7 * b.distance]
    A, inl = cv2.estimateAffine2D(np.float32([k1[a.queryIdx].pt for a in pares]),
                                  np.float32([k2[a.trainIdx].pt for a in pares]), ransacReprojThreshold=2.0)
    print(f"    base alinhada: {int(inl.sum())} pontos, escala {A[0, 0]:.4f} x {A[1, 1]:.4f}")
    chapada = cv2.resize(cv2.imread(str(BASE_CHAPADA)), render.shape[1::-1], interpolation=cv2.INTER_NEAREST)
    return (cv2.warpAffine(base, A, render.shape[1::-1], flags=cv2.INTER_LINEAR, borderValue=(255, 255, 255)),
            cv2.warpAffine(chapada, A, render.shape[1::-1], flags=cv2.INTER_NEAREST, borderValue=(255, 255, 255)))


def fora_do_lote(out, base):
    H, W = out.shape[:2]
    x0 = LOTE["x_esq"]
    (c0, c1), (b0, b1) = LOTE["muro_cima"], LOTE["muro_baixo"]
    fora = np.zeros((H, W), bool)
    fora[:, :x0] = True                                   # à esquerda da linha tracejada
    fora[:c0, :MURO_COBERTO["x"][1]] = True               # acima do muro de cima, no canto
    fora[b1:, :MURO_COBERTO["x"][1]] = True               # abaixo do muro de baixo, no canto
    mudou = fora & (np.abs(out.astype(int) - base.astype(int)).max(axis=2) > 40)
    out[fora] = base[fora]
    # muros: as folhas passavam por cima; o muro volta, copiado da coluna limpa do próprio render
    mx0, mx1 = MURO_COBERTO["x"]
    xl = MURO_COBERTO["coluna_limpa"]
    for y0, y1 in ((c0, c1), (b0, b1)):
        out[y0:y1, max(mx0, x0):mx1] = out[y0:y1, xl:xl + 1]
    print(f"    {int(mudou.sum())} px de folhas fora do lote; muros refeitos em x {max(mx0, x0)}-{mx1}")
    return out


def jardins_de_inverno(out):
    j = JARDINS
    a = out.astype(np.int32)
    n_faixas = 0
    for f in j["faixas"]:                                   # vidros e parede: perfil limpo repetido
        x0, y0, x1, y1 = f["ret"]
        tipo, pos = f["perfil"][0], f["perfil"][1]
        if tipo == "linha":
            out[y0:y1, x0:x1] = a[pos, x0:x1][None].astype(np.uint8)
        else:
            ini = f["perfil"][2] if len(f["perfil"]) > 2 else y0
            out[y0:y1, x0:x1] = a[ini:ini + (y1 - y0), pos][:, None].astype(np.uint8)
        n_faixas += (y1 - y0) * (x1 - x0)
    e = j["emenda"]
    n = 0
    for nome, (x0, y0, x1, y1), (dx, dy) in j["pisos"]:
        fonte = out[y0 + dy:y1 + dy, x0 + dx:x1 + dx].astype(np.float32)
        alvo = out[y0:y1, x0:x1].astype(np.float32)
        h, w = y1 - y0, x1 - x0
        # emenda suave só no lado que encosta no piso que fica (longe dos jardins)
        al = np.ones((h, w), np.float32)
        if dx < 0:
            al[:, :e] = (np.arange(e) + 1)[None] / (e + 1)
        elif dx > 0:
            al[:, -e:] = (np.arange(e)[::-1] + 1)[None] / (e + 1)
        elif dy > 0:
            al[-e:, :] = (np.arange(e)[::-1] + 1)[:, None] / (e + 1)
        out[y0:y1, x0:x1] = np.clip(alvo * (1 - al[..., None]) + fonte * al[..., None], 0, 255).astype(np.uint8)
        n += h * w
    print(f"    {n_faixas} px de vidro e parede refeitos; {n} px de piso refeitos (folhas e sombras)")
    return out


def portas_de_vidro(out, base, chapada):
    """Folhas de vidro da base sobre as faixas dos jardins; o resto da faixa é piso ou floreira."""
    a = out.copy()
    c = chapada.astype(np.int32)
    # vidro e montantes: a cor exata do vidro da legenda e o preto (contorno e montantes) da base chapada
    cinza = np.abs(c - np.array(VIDRO)).max(axis=2) <= 8
    preto = c.max(axis=2) < 60
    vidro = cinza | preto
    n = 0
    for nome, (x0, y0, x1, y1), (dx, dy), eixo, lim in JARDINS["portas"]:
        for y in range(y0, y1):
            for x in range(x0, x1):
                if vidro[y, x]:
                    out[y, x] = base[y, x]
                    n += 1
                    continue
                pos = x if eixo == "x" else y
                passo = dx if eixo == "x" else dy
                dentro = (pos >= lim) if passo > 0 else (pos <= lim)
                out[y, x] = a[y + dy, x + dx] if dentro else a[y - dy, x - dx]
    print(f"    portas de vidro da base: {n} px")
    return out


def cozinha(out):
    c = COZINHA
    fontes = []
    for x0, y0, x1, y1 in c["fonte_quartzo"]:
        t = out[y0:y1, x0:x1].astype(np.float32)
        fontes += [np.ascontiguousarray(v) for v in (t, t[:, ::-1], t[::-1, :], t[::-1, ::-1])]
    bx0, by0 = min(r[0] for r in c["quartzo"]), min(r[1] for r in c["quartzo"])
    bx1, by1 = max(r[2] for r in c["quartzo"]), max(r[3] for r in c["quartzo"])
    tex = quilting(fontes, by1 - by0, bx1 - bx0, p=16, sobra=4, candidatos=600)
    m = np.zeros((by1 - by0, bx1 - bx0), bool)
    for x0, y0, x1, y1 in c["quartzo"]:
        m[y0 - by0:y1 - by0, x0 - bx0:x1 - bx0] = True
    cx0, cy0, cx1, cy1 = c["cooktop"]
    m[cy0 - by0:cy1 - by0, cx0 - bx0:cx1 - bx0] = False
    reg = out[by0:by1, bx0:bx1]
    reg[m] = np.clip(tex[m], 0, 255).astype(np.uint8)
    print(f"    quartzo: {int(m.sum())} px de bancada e ilha")

    (x0, y0, x1, y1), dx, sombra, xs = c["vao"]
    out[y0:y1, x0:x1] = out[y0:y1, x0 + dx:x1 + dx]
    for i, f in enumerate(sombra):
        y = y1 - len(sombra) + i
        out[y, xs:x1] = np.clip(out[y, xs:x1].astype(np.float32) * f, 0, 255).astype(np.uint8)
    print(f"    vão de piso entre a geladeira e o armário: {(x1 - x0) * (y1 - y0)} px")

    fx0, fy0, fx1, fy1 = c["fonte_areia"]
    t = out[fy0:fy1, fx0:fx1]
    lado = {"esquerda": (slice(None), 0), "direita": (slice(None), -1), "cima": (0, slice(None)),
            "baixo": (-1, slice(None))}
    for (x0, y0, x1, y1), faces in c["armarios"]:
        h, w = y1 - y0, x1 - x0
        lin = np.concatenate([t, t[::-1]] * (h // (2 * t.shape[0]) + 1), axis=0)[:h]
        reg = np.concatenate([lin, lin[:, ::-1]] * (w // (2 * t.shape[1]) + 1), axis=1)[:, :w].astype(np.float32)
        borda = np.zeros((h, w), bool)
        for face in faces:
            borda[lado[face]] = True
        reg[borda] *= c["contorno"]
        out[y0:y1, x0:x1] = np.clip(reg, 0, 255).astype(np.uint8)
        print(f"    armário alto {w}x{h} px, contorno em {', '.join(faces)}")

    for x0, y0, x1, y1 in c["cubas"]:                      # torneira do lado da parede (em cima)
        reg = np.ascontiguousarray(out[y0:y1, x0:x1][::-1])
        reg = cuba(reg, (0, 0, x1 - x0, y1 - y0))
        out[y0:y1, x0:x1] = reg[::-1]
    print(f"    {len(c['cubas'])} cubas")
    return out


def quarto_externo(out):
    q = QUARTO_EXTERNO
    a = out.copy()
    for (x0, y0, x1, y1), (dx, dy) in q["pisos"]:
        out[y0:y1, x0:x1] = a[y0 + dy:y1 + dy, x0 + dx:x1 + dx]
    fx0, fy0, fx1, fy1 = q["fonte_cama"]
    c0, c1 = q["cortar_cobertor"]
    cama = np.concatenate([a[fy0:fy1, fx0:c0], a[fy0:fy1, c1:fx1]], axis=1)[:, ::-1]   # cabeceira à direita
    x0, y0, x1, y1 = q["cama"]
    out[y0:y1, x0:x1] = cv2.resize(cama, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)
    out[y0 - 1, x0:x1] = np.clip(out[y0 - 1, x0:x1] * q["sombra_cima"], 0, 255).astype(np.uint8)
    out[y0:y1, x0 - 1] = np.clip(out[y0:y1, x0 - 1] * q["sombra_pe"], 0, 255).astype(np.uint8)
    print(f"    cama de solteiro: {fx1 - fx0 - (c1 - c0)}x{fy1 - fy0} px da fonte em {x1 - x0}x{y1 - y0} px")
    fx0, fy0, fx1, fy1 = q["fonte_criado"]
    x0, y0, x1, y1 = q["criado"]
    out[y0:y1, x0:x1] = cv2.resize(a[fy0:fy1, fx0:fx1], (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)
    print(f"    criado-mudo: {x1 - x0}x{y1 - y0} px")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("render", type=Path)
    ap.add_argument("--saida", type=Path, default=Path("."))
    ap.add_argument("--nome", required=True)
    args = ap.parse_args()

    orig = cv2.imread(str(args.render))
    out = orig.copy()
    print("[1] chuveiros de teto")
    out = chuveiros_teto(out)
    print("[2] plantas fora do lote")
    base, chapada = alinhar_base(orig)
    out = fora_do_lote(out, base)
    print("[3] jardins de inverno")
    out = jardins_de_inverno(out)
    out = portas_de_vidro(out, base, chapada)
    print("[4] cozinha")
    out = cozinha(out)
    print("[5] quarto externo")
    out = quarto_externo(out)

    args.saida.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(args.saida / f"{args.nome}.png"), out)
    alfa = np.where(np.abs(out.astype(int) - orig.astype(int)).max(axis=2) > 0, 255, 0).astype(np.uint8)
    cv2.imwrite(str(args.saida / f"{args.nome}_camada.png"), np.dstack([out, alfa]))
    print(f"[6] {args.saida / (args.nome + '.png')}; {int((alfa > 0).sum())} px alterados")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Retoque sem IA do render final do 1º Pavimento a partir da base v3, alinhada por SIFT.

1. Escada em U: o motor errou a linha de descida (as pontas viraram arcos de porta) e o
   número de degraus. As linhas do render saem por inpaint, e entram as linhas da base:
   degraus, linha de descida, círculo de partida e seta. A textura de travertino fica.
2. Saleta da caracol: a abertura em L em volta da escada é vão e fica branca, com o desenho
   do PDF: degraus que descem (contínuos e tracejados), arco central, marcas e as linhas duplas
   que dividem o vão do piso. O quarto creme e o piso em volta ficam do render.
   Na bancada da entrada da suíte master entra a cuba redonda com torneira da base.
   Os vãos de pé-direito duplo deixam o cinza-escuro e ficam brancos, com o X tracejado do PDF.
3. Entorno: tudo fora do 1º pavimento (fora dos retângulos 'manter_bbox_vis' do
   esmaecer) passa a ser a base, esmaecida. Isso inclui as pedras de acesso ao hall
   externo, o pergolado tracejado, a piscina, o deck e os contornos.

Uso:
  python retoque_base_1pav.py RENDER BASE_V3_16x9 --saida PASTA [--config config_bases.json]
"""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
LARGURA_VIS = 1800
BASE_LARGURA_SEM_MARGEM = 6001


def afim(origem, destino, n=10000, razao=0.75, tol=2.5):
    sift = cv2.SIFT_create(n)
    k1, d1 = sift.detectAndCompute(cv2.cvtColor(origem, cv2.COLOR_BGR2GRAY), None)
    k2, d2 = sift.detectAndCompute(cv2.cvtColor(destino, cv2.COLOR_BGR2GRAY), None)
    bons = [a for a, b in cv2.BFMatcher().knnMatch(d1, d2, k=2) if a.distance < razao * b.distance]
    src = np.float32([k1[m.queryIdx].pt for m in bons])
    dst = np.float32([k2[m.trainIdx].pt for m in bons])
    A, inl = cv2.estimateAffine2D(src, dst, ransacReprojThreshold=tol)
    res = np.linalg.norm(src @ A[:, :2].T + A[:, 2] - dst, axis=1)[inl.ravel() == 1]
    print(f"    {int(inl.sum())} pontos, erro mediano {np.median(res):.2f} px")
    return np.vstack([A, [0, 0, 1]])


def lum(img):
    return img.astype(np.float32).mean(axis=2)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("render", type=Path)
    ap.add_argument("base", type=Path)
    ap.add_argument("--saida", type=Path, default=Path("."))
    ap.add_argument("--config", type=Path, default=AQUI / "config_bases.json")
    ap.add_argument("--base-sem-texto", type=Path, default=AQUI.parent / "bases" / "POE642_CasaA_BASE_1Pavimento_semtexto.png",
                    help="base sem texto do gerar_bases.py (desenho do PDF sem legenda nem esmaecimento)")
    args = ap.parse_args()

    r = cv2.imread(str(args.render))
    base = cv2.imread(str(args.base))
    H, W = r.shape[:2]
    pav = json.loads(args.config.read_text())["pavimentos"]["1Pavimento"]

    print("[1] alinhando a base ao render")
    s = W / base.shape[1]
    base_red = cv2.resize(base, (W, round(base.shape[0] * s)), interpolation=cv2.INTER_AREA)
    A_b = afim(base_red, r)                              # base reduzida -> render
    T = A_b @ np.diag([s, s, 1])                         # base em px reais -> render
    # reduz primeiro com média (INTER_AREA) e só depois aplica a afim, quase identidade:
    # o warpAffine não faz média, e as linhas finas da base sumiriam aos pedaços
    bw = cv2.warpAffine(base_red, A_b[:2], (W, H), flags=cv2.INTER_LINEAR, borderValue=(255, 255, 255))
    k = BASE_LARGURA_SEM_MARGEM / LARGURA_VIS
    margem = (base.shape[1] - BASE_LARGURA_SEM_MARGEM) / 2

    def vis_px(x, y):
        return (T @ np.array([x * k + margem, y * k, 1]))[:2]

    out = r.copy()
    alterado = np.zeros((H, W), bool)

    # 2. escada em U -------------------------------------------------------------------
    print("[2] escada em U: linhas da base sobre o travertino do render")
    x0, y0 = vis_px(1080, 481)
    x1, y1 = vis_px(1231, 597)
    x0, y0, x1, y1 = int(x0), int(y0), int(np.ceil(x1)), int(np.ceil(y1))
    trav_base = np.array([202, 217, 220], np.float32)  # #DCD9CA em BGR
    sub_b = bw[y0:y1, x0:x1].astype(np.float32)
    perto = np.abs(sub_b - trav_base).max(axis=2) < 14
    linha_b = (lum(bw[y0:y1, x0:x1]) < 200) & ((sub_b.max(axis=2) - sub_b.min(axis=2)) < 30)
    # área do degrau: travertino da base com as linhas entre um degrau e outro
    area = cv2.morphologyEx((perto | linha_b).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    vazio = lum(bw[y0:y1, x0:x1]) < 95                # cinza-escuro dos vazios e paredes
    area = area.astype(bool) & ~cv2.dilate(vazio.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    sub_r = out[y0:y1, x0:x1]
    # as linhas do render também são apagadas numa faixa em volta da área (as pontas dos degraus
    # encostam na borda clara da escada), sem tocar no cinza-escuro dos vazios
    limpar = cv2.dilate(area.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool) & (lum(sub_r) > 150)
    mediana = cv2.medianBlur(sub_r, 7).astype(np.float32)
    linhas_r = ((lum(mediana) - lum(sub_r)) > 10) & limpar
    linhas_r = cv2.dilate(linhas_r.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & limpar
    cor_linha = np.array([98, 104, 112], np.float32)   # cinza-taupe escuro, o mesmo tom das linhas do render (BGR)
    limpo = cv2.inpaint(sub_r, linhas_r.astype(np.uint8) * 255, 3, cv2.INPAINT_TELEA)
    # linhas da base medidas na resolução cheia: o traço de 2 px vira cobertura parcial no render,
    # que é reforçada para a linha ficar com o peso das linhas do render
    lb = lum(base)
    neutro_b = (base.max(axis=2).astype(int) - base.min(axis=2)) < 30
    linha_full = ((lb > 90) & (lb < 200) & neutro_b).astype(np.float32)
    linha_red = cv2.resize(linha_full, (base_red.shape[1], base_red.shape[0]), interpolation=cv2.INTER_AREA)
    cobertura = cv2.warpAffine(linha_red, A_b[:2], (W, H), flags=cv2.INTER_LINEAR)[y0:y1, x0:x1]
    alfa = np.clip(cobertura * 1.7, 0, 0.85)[..., None] * area[..., None]
    novo = limpo.astype(np.float32) * (1 - alfa) + cor_linha.astype(np.float32) * alfa
    out[y0:y1, x0:x1] = np.where(area[..., None], novo, limpo).astype(np.uint8)
    alterado[y0:y1, x0:x1] |= area | linhas_r
    print(f"    {int(linhas_r.sum())} px de linha do render apagados")

    # 3. escada caracol --------------------------------------------------------------
    # a saleta segue o desenho do PDF: a abertura em L em volta da caracol é vão e fica branca,
    # com os degraus que descem (contínuos no quarto de cima à esquerda, tracejados embaixo),
    # o arco central, as marcas e as linhas duplas que dividem o vão do piso. O desenho vem da
    # base sem texto (sem legenda nem esmaecimento); o quarto creme e o piso em volta ficam do render.
    print("[3] saleta: vão em L branco com os degraus e as bordas do PDF")
    st = cv2.imread(str(args.base_sem_texto))
    pad = (base.shape[1] - st.shape[1]) // 2
    st = cv2.copyMakeBorder(st, 0, base.shape[0] - st.shape[0], pad, base.shape[1] - st.shape[1] - pad,
                            cv2.BORDER_CONSTANT, value=(255, 255, 255))
    ls = lum(st)
    linha_st = ((ls < 200) & ((st.max(axis=2).astype(int) - st.min(axis=2)) < 30)).astype(np.float32)
    linha_st = cv2.resize(linha_st, (base_red.shape[1], base_red.shape[0]), interpolation=cv2.INTER_AREA)
    cob = cv2.warpAffine(linha_st, A_b[:2], (W, H), flags=cv2.INTER_LINEAR)
    vao = np.zeros((H, W), np.uint8)
    # medidas na prévia de 1800 px: lado esquerdo do L e o braço de baixo, até as linhas duplas
    for vx0, vy0, vx1, vy1 in [(896.7, 808.2, 932.0, 877.6), (930.6, 846.0, 967.5, 877.6)]:
        q = np.array([vis_px(vx0, vy0), vis_px(vx1, vy0), vis_px(vx1, vy1), vis_px(vx0, vy1)])
        cv2.fillConvexPoly(vao, np.round(q).astype(np.int32), 1)
    # teto baixo de opacidade: o contorno duplo do círculo não engrossa e todas as linhas ficam
    # com o mesmo peso, como no PDF
    alfa = (np.clip(cob * 1.6, 0, 0.65) * vao)[..., None]
    branco = np.array([250, 250, 250], np.float32)
    cor = np.array([92, 92, 92], np.float32)
    desenho = branco * (1 - alfa) + cor * alfa
    out = np.where(vao[..., None].astype(bool), desenho, out).astype(np.uint8)
    alterado |= vao.astype(bool)

    # 3b. cuba da bancada na entrada da suíte master -----------------------------------
    # o motor desenhou a bancada lisa; na base ela tem uma cuba redonda com a torneira saindo
    # da parede de baixo. Medidas na base sem texto (px reais): centro, raio e base da torneira.
    print("[3b] cuba redonda na bancada da entrada da suíte master")
    def st_px(x, y):
        return (T @ np.array([x + pad, y, 1]))[:2]
    ccx, ccy = st_px(3022.0, 2348.4)
    tx, ty = st_px(3021.0, 2373.0)
    rr = 18.5 * np.sqrt(abs(np.linalg.det(T[:2, :2])))
    ss = 8
    n = int(np.ceil(rr * 2 + 12))
    ox, oy = int(np.floor(ccx - n / 2)), int(np.floor(ccy - n / 2))
    big = np.zeros((n * ss, n * ss, 4), np.float32)
    c = (int(round((ccx - ox) * ss)), int(round((ccy - oy) * ss)))
    R = int(round(rr * ss))
    cv2.circle(big, c, R, (238, 239, 240, 1.0), -1, cv2.LINE_AA)                        # borda da louça
    cv2.circle(big, c, int(R * 0.80), (250, 250, 250, 1.0), -1, cv2.LINE_AA)            # bacia
    cv2.circle(big, c, R, (168, 170, 172, 1.0), max(1, int(round(0.5 * ss))), cv2.LINE_AA)  # contorno fino
    cv2.circle(big, c, int(R * 0.80), (205, 207, 209, 1.0), max(1, int(round(0.35 * ss))), cv2.LINE_AA)
    cv2.circle(big, c, max(2, int(round(0.7 * ss))), (150, 152, 155, 1.0), -1, cv2.LINE_AA)  # ralo
    t0 = (int(round((tx - ox) * ss)), int(round((ty - oy) * ss)))
    t1 = (c[0], int(round(c[1] + R * 0.15)))
    cv2.line(big, t0, t1, (140, 143, 147, 1.0), max(2, int(round(0.9 * ss))), cv2.LINE_AA)     # bica cromada
    cv2.line(big, t0, t1, (205, 208, 212, 1.0), max(1, int(round(0.3 * ss))), cv2.LINE_AA)     # brilho da bica
    cv2.rectangle(big, (t0[0] - int(1.2 * ss), t0[1] - int(0.6 * ss)), (t0[0] + int(1.2 * ss), t0[1] + int(0.8 * ss)),
                  (125, 128, 132, 1.0), -1)                                                       # corpo da torneira
    peq = cv2.resize(big, (n, n), interpolation=cv2.INTER_AREA)
    a = peq[..., 3:4]
    reg = out[oy:oy + n, ox:ox + n].astype(np.float32)
    out[oy:oy + n, ox:ox + n] = (reg * (1 - a) + peq[..., :3] * a).astype(np.uint8)
    alterado[oy:oy + n, ox:ox + n] |= a[..., 0] > 0.02
    print(f"    centro ({ccx:.1f}, {ccy:.1f}), diâmetro {2 * rr:.1f} px")

    # 3c. vãos de pé-direito duplo em branco ------------------------------------------
    # o cinza-escuro dos vãos (os dois quadrados grandes, as faixas em volta da escada em U e o
    # vão entre os lances) vira branco, com o X tracejado e as linhas do PDF por cima
    print("[3c] vãos em branco, com o X tracejado do PDF")
    lr = lum(out)
    croma = out.max(axis=2).astype(int) - out.min(axis=2)
    vaos = np.zeros((H, W), np.uint8)
    for regra in pav["legenda"]["retangulos"]:
        if regra.get("para", "").upper() != "#4A4A4A":
            continue
        bx0, by0, bx1, by1 = regra["bbox_vis"]
        q = np.round(np.array([vis_px(bx0, by0), vis_px(bx1, by0), vis_px(bx1, by1), vis_px(bx0, by1)])).astype(np.int32)
        dentro = np.zeros((H, W), np.uint8)
        cv2.fillConvexPoly(dentro, q, 1)
        escuro = ((lr >= 58) & (lr <= 110) & (croma <= 14) & dentro.astype(bool)).astype(np.uint8)
        # o X claro e as emendas finas ficam dentro do vão
        escuro = cv2.morphologyEx(escuro, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
        # a borda serrilhada entre o cinza-escuro e o vizinho (travertino, parede) entra no vão:
        # o contorno limpo volta pelas linhas do PDF
        borda = cv2.dilate(escuro, np.ones((3, 3), np.uint8)).astype(bool) & (lr >= 45) & (lr < 175) & (croma < 20)
        vaos |= (escuro.astype(bool) | borda).astype(np.uint8) & dentro
    alfa_v = (np.clip(cob * 1.6, 0, 0.65) * vaos)[..., None]
    desenho = np.array([250, 250, 250], np.float32) * (1 - alfa_v) + np.array([92, 92, 92], np.float32) * alfa_v
    out = np.where(vaos[..., None].astype(bool), desenho, out).astype(np.uint8)
    alterado |= vaos.astype(bool)
    print(f"    {int(vaos.sum())} px de vão")

    # 4. entorno = base --------------------------------------------------------------
    print("[4] entorno: base esmaecida fora do 1º pavimento")
    manter = np.zeros((H, W), np.uint8)
    for bx0, by0, bx1, by1 in pav["esmaecer"]["manter_bbox_vis"]:
        p = np.array([vis_px(bx0, by0), vis_px(bx1, by0), vis_px(bx1, by1), vis_px(bx0, by1)], np.int32)
        cv2.fillConvexPoly(manter, p, 1)
    fora = cv2.GaussianBlur((1 - manter).astype(np.float32), (0, 0), 0.6)[..., None]
    out = (out.astype(np.float32) * (1 - fora) + bw.astype(np.float32) * fora).astype(np.uint8)
    alterado |= fora[..., 0] > 0.02

    args.saida.mkdir(parents=True, exist_ok=True)
    nome = args.render.stem.replace("_final", "") + "_final2"
    cv2.imwrite(str(args.saida / f"{nome}.png"), out)
    cv2.imwrite(str(args.saida / f"{nome}_camada.png"),
                np.dstack([out, (alterado * 255).astype(np.uint8)]))
    print(f"[5] {args.saida / (nome + '.png')} ({W}x{H})")


if __name__ == "__main__":
    main()

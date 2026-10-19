#!/usr/bin/env python3
"""Portas sem os arcos, em qualquer casa (POE 642).

Regra do usuário (19/10/26, para todas as casas: "remover os arcos, escadas com linhas"; e na consolidação: "Não
mostrar arco da porta"). Feito primeiro no Térreo da Casa A (`ajustes_casaa.sem_arcos`) e trazido para cá para servir
às outras casas e pavimentos.

`remover_arcos(out, pg, p2r, ...)` tira da imagem (o render retocado, no quadro em que `p2r` leva os pontos do PDF)
os arcos de porta do PDF: as curvas das camadas dadas (um quarto de círculo por arco). Ficam as folhas e os batentes.
- Portas de giro (o arco é um quarto de círculo): o círculo pelas pontas e pelo meio do arco, levado à imagem. Na
  faixa de ±`tol` px em volta dele, onde o traço passa (o que difere do piso de dentro e de fora da faixa, na mesma
  direção), a faixa inteira vira a textura do mesmo piso logo depois dela, na mesma direção (de quatro afastamentos,
  o mais parecido com o piso em volta), com a borda suave. Onde nenhum afastamento serve, inpaint. Ficam a folha e o
  batente (as retas do centro às pontas do arco) e o que é preto.
- Porta camarão (os arcos rasos): o setor entre cada folha e o arco, menos as folhas pretas, vira o piso tecido de
  trechos limpos (`camarao_fontes`, em px), normalizado, vezes o campo de luz do piso em volta.
"""
import cv2
import numpy as np


def remover_arcos(out, pg, p2r, camadas=("ARQ_PAREDE",), tol=3.0, limiar=7, inpaint=18, raso=1.6,
                  camarao_fontes=(), tam_min_pt=12.0, so_folha=False):
    """so_folha: a reta do centro a uma ponta só é protegida se lá houver mesmo uma folha (o traço difere do piso
    dos dois lados dela); sem isso, as duas retas são protegidas (na porta dupla, a ponta do arco fechado ficava)."""
    from retoque_bege_bahia_terreo import quilting
    q = {"tol": tol, "limiar": limiar, "inpaint": inpaint, "raso": raso, "camarao_fontes": camarao_fontes}
    im = out.copy()
    res = out.astype(np.float32)
    H, W = out.shape[:2]
    T = q["tol"]

    def bez(p, t):
        return sum(((1 - t) ** (3 - i)) * (t ** i) * [1, 3, 3, 1][i] * np.array([p[i].x, p[i].y]) for i in range(4))

    def circulo(a, b, c):
        (x1, y1), (x2, y2), (x3, y3) = a, b, c
        A = np.array([[x2 - x1, y2 - y1], [x3 - x1, y3 - y1]]) * 2
        cx, cy = np.linalg.solve(A, [x2 ** 2 - x1 ** 2 + y2 ** 2 - y1 ** 2, x3 ** 2 - x1 ** 2 + y3 ** 2 - y1 ** 2])
        return cx, cy, np.hypot(x1 - cx, y1 - cy)

    camarao = np.zeros((H, W), bool)
    n_giro = n_px = 0
    for d in pg.get_drawings():
        if d.get("layer") not in camadas or max(d["rect"].width, d["rect"].height) < tam_min_pt:
            continue
        for it in d["items"]:
            if it[0] != "c":
                continue
            P0, Pm, P3 = (np.array(p2r(*bez(it[1:], t))) for t in (0, 0.5, 1))
            cx, cy, R = circulo(P0, Pm, P3)
            am = np.arctan2(Pm[1] - cy, Pm[0] - cx)

            def rel(a):
                return (a - am + np.pi) % (2 * np.pi) - np.pi
            lim0, lim3 = sorted((rel(np.arctan2(P0[1] - cy, P0[0] - cx)), rel(np.arctan2(P3[1] - cy, P3[0] - cx))))
            x0, x1 = int(max(0, cx - R - T - 2)), int(min(W, cx + R + T + 3))
            y0, y1 = int(max(0, cy - R - T - 2)), int(min(H, cy + R + T + 3))
            yy, xx = np.mgrid[y0:y1, x0:x1]
            r = np.hypot(xx - cx, yy - cy)
            ang = rel(np.arctan2(yy - cy, xx - cx))
            faixa = (np.abs(r - R) <= T) & (ang > lim0) & (ang < lim3)
            # a folha e o batente (as retas do centro às pontas) e o que é preto ficam
            prot = np.zeros(faixa.shape, bool)
            for E in (P0, P3):
                u = (E - (cx, cy)) / R
                if so_folha:
                    # há folha se, ao longo da reta, o traço difere do piso a 4 px dos dois lados
                    nrm = np.array([-u[1], u[0]])
                    ts = np.linspace(0.25, 0.85, 12) * R
                    pts = np.array([(cx, cy)]) + ts[:, None] * u
                    def amost(P):
                        return np.array([cv2.getRectSubPix(im.astype(np.float32), (1, 1), (float(a), float(b)))[0, 0]
                                         for a, b in P])
                    dif = np.abs(amost(pts) - (amost(pts + 4 * nrm) + amost(pts - 4 * nrm)) / 2).max(axis=1)
                    if np.median(dif) < 12:
                        continue
                prot |= (np.abs((xx - cx) * u[1] - (yy - cy) * u[0]) < 1.8) & ((xx - cx) * u[0] + (yy - cy) * u[1] > 0)
            reg = res[y0:y1, x0:x1]
            prot |= reg.mean(axis=2) < 55
            bb = d["rect"]
            if max(bb.width, bb.height) / max(1e-3, min(bb.width, bb.height)) >= q["raso"]:
                camarao[y0:y1, x0:x1] |= (((r <= R + T) & (ang > lim0 - 0.05) & (ang < lim3 + 0.05)) | faixa) & ~prot
                continue

            def amostra(rr):
                k = rr / np.maximum(r, 1e-3)
                return cv2.remap(im.astype(np.float32), (cx + (xx - cx) * k).astype(np.float32),
                                 (cy + (yy - cy) * k).astype(np.float32), cv2.INTER_CUBIC)
            bg = (amostra(R + T + 2) + amostra(R - T - 2)) / 2
            achado = faixa & (np.abs(reg - bg).max(axis=2) > q["limiar"]) & ~prot
            if not achado.any():
                continue
            perto = cv2.dilate(achado.astype(np.uint8), np.ones((2 * int(T) + 3,) * 2, np.uint8)).astype(bool)
            peso = np.clip((T + 1.0 - np.abs(r - R)) / 2.0, 0, 1) * (perto & ~prot & (ang > lim0) & (ang < lim3))
            cands = [amostra(r + k) for k in (2 * T + 2, -(2 * T + 2), 3 * T + 3, -(3 * T + 3))]
            dists = np.stack([np.abs(c - bg).max(axis=2) for c in cands])
            src = np.take_along_axis(np.stack(cands), dists.argmin(axis=0)[None, ..., None], axis=0)[0]
            ruim = (dists.min(axis=0) > q["inpaint"]) & (peso > 0)
            if ruim.any():
                pint = cv2.inpaint(np.clip(reg, 0, 255).astype(np.uint8), ruim.astype(np.uint8), 2, cv2.INPAINT_TELEA)
                src = np.where(ruim[..., None], pint.astype(np.float32), src)
            reg[:] = reg * (1 - peso[..., None]) + src * peso[..., None]
            n_giro += 1
            n_px += int((peso > 0).sum())
    print(f"    portas de giro: {n_giro} arcos fora ({n_px} px)")
    # porta camarão: o setor de cada arco raso vira travertino tecido, na luz do lugar
    escuro = cv2.dilate((im.astype(np.float32).mean(axis=2) < 70).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    cam = camarao & ~escuro
    if cam.any():
        ys, xs = np.nonzero(cam)
        bx0, by0, bx1, by1 = xs.min() - 8, ys.min() - 8, xs.max() + 9, ys.max() + 9
        fontes = [im[b:d, a:c].astype(np.float32) for a, b, c, d in q["camarao_fontes"]]
        tex = quilting(fontes, by1 - by0, bx1 - bx0, p=14, sobra=5, candidatos=300,
                       rng=np.random.default_rng(652))[:by1 - by0, :bx1 - bx0]
        tex = tex / cv2.GaussianBlur(tex, (0, 0), 8)
        med = cv2.medianBlur(im, 5).astype(np.float32)[by0:by1, bx0:bx1]
        piso = (~cam[by0:by1, bx0:bx1] & ~escuro[by0:by1, bx0:bx1]).astype(np.float32)
        campo = cv2.GaussianBlur(med * piso[..., None], (0, 0), 4) / \
            np.maximum(cv2.GaussianBlur(piso, (0, 0), 4), 1e-4)[..., None]
        a = np.maximum(cv2.GaussianBlur(cam[by0:by1, bx0:bx1].astype(np.float32), (0, 0), 0.6), cam[by0:by1, bx0:bx1])
        a = (a * ~escuro[by0:by1, bx0:bx1])[..., None]
        res[by0:by1, bx0:bx1] = res[by0:by1, bx0:bx1] * (1 - a) + tex * campo * a
        print(f"    porta camarão: o setor dos arcos rasos de volta ao travertino ({int(cam.sum())} px)")
    return np.clip(res, 0, 255).astype(np.uint8)

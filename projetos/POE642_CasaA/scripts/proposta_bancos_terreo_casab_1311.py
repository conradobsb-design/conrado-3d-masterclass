"""A proposta dos bancos de pé de cama do Térreo da Casa B, na escala do 12K (a opção A de hoje como fundo)."""
import sys
import cv2
import numpy as np
sys.path.insert(0, '/home/user/conrado-3d-masterclass/projetos/POE642_CasaA/scripts')
import biblioteca_terreo_casaa_1211 as BT          # noqa: E402
import biblioteca_1pav_casaa_1211 as B1            # noqa: E402
import paisagismo_terreo_casab_1311 as PJ          # noqa: E402

D = '/tmp/claude-0/-home-user/610cde13-fae4-5134-867b-524dc247ebb6/scratchpad/bancos/'
K12 = '/home/user/conrado-3d-masterclass/projetos/POE642_CasaB/entrega/POE642_CasaB_PH_Terreo_12K_opcao_A.jpg'
SAIDA = '/home/user/conrado-3d-masterclass/projetos/POE642_CasaB/renders/POE642_CasaB_PH_Terreo_1311_proposta_bancos.jpg'
S, X0, Y0 = 3.587, 190, -220
PX_M = B1.PX_M
OPCOES = [("B1", "Veludo bordô capitonê, moldura de freijó", "k1", "s1"),
          ("B2", "Linho cinza, 2 almofadas, moldura de latão escovado", "k2", "s2"),
          ("B3", "Bouclé off-white com rolos, base de nogueira", "k3", "s3"),
          ("B4", "Couro caramelo costurado, moldura de carvalho escuro", "k4", "s4")]
# (retângulo do PDF, giro, o lado da cama: o banco encosta nele; amostra do tapete)
SUITE_MASTER = {"crop": (1030, 580, 1215, 705), "bancos": [((1051.3, 595.5, 1158.9, 639.7), 0.0, "baixo")],
                "tapete": (1166, 597, 1188, 638)}
SUITE_2 = {"crop": (2370, 345, 2470, 535), "bancos": [((2386.4, 354.9, 2410.3, 411.6), 90.0, "dir"),
                                                      ((2386.4, 470.9, 2410.3, 527.6), 90.0, "dir")],
           "tapete": (2388, 418, 2408, 464)}


def u(x):
    return (x - X0) * S


def v(y):
    return (y - Y0) * S


def ler(nome):
    P = cv2.imread(D + f'cut_{nome}.png', cv2.IMREAD_UNCHANGED).astype(np.float32)
    ys, xs = np.nonzero(P[..., 3] > 8)
    return np.ascontiguousarray(P[ys.min():ys.max() + 1, xs.min():xs.max() + 1])


def montar(img, q, nome):
    out = img.copy()
    tx0, ty0, tx1, ty1 = q["tapete"]
    tapete = img[int(v(ty0)):int(v(ty1)), int(u(tx0)):int(u(tx1))].copy()
    P = ler(nome) if nome else None
    for (x0, y0, x1, y1), giro, lado in q["bancos"]:
        if P is None:
            continue
        m = np.zeros(out.shape[:2], bool)
        m[int(v(y0) - 8):int(v(y1) + 8), int(u(x0) - 8):int(u(x1) + 8)] = True
        out = PJ.preencher(out, m, tapete, anel_px=int(8 * S), sig=10 * S)
        h, w = P.shape[:2]
        asp = w / h
        if giro == 0.0:
            L = (x1 - x0)
            prof = min(y1 - y0, L / asp * 1.15)
            cx, cy = (x0 + x1) / 2, (y1 - prof / 2) if lado == "baixo" else (y0 + prof / 2)
        else:
            L = (y1 - y0) * 0.97
            prof = min(x1 - x0, L / asp * 1.15)
            cx, cy = (x1 - prof / 2) if lado == "dir" else (x0 + prof / 2), (y0 + y1) / 2
        o = BT.pousar(out.astype(np.float32), P, u(cx), v(cy), L * S, prof * S, giro, BT.SOMBRAS["movel"], PX_M * S)
        out = np.clip(np.round(o), 0, 255).astype(np.uint8)
    cx0, cy0, cx1, cy1 = q["crop"]
    return out[int(v(cy0)):int(v(cy1)), int(u(cx0)):int(u(cx1))]


def titulo(im, txt, h=46, esc=0.85):
    t = np.full((h, im.shape[1], 3), 255, np.uint8)
    cv2.putText(t, txt, (8, 32), cv2.FONT_HERSHEY_SIMPLEX, esc, (40, 40, 40), 2, cv2.LINE_AA)
    return np.vstack([t, im])


def main():
    big = cv2.imread(K12)
    # só a região das duas suítes (o 12K inteiro não cabe à vontade na memória com as cópias)
    linhas = []
    for rot, txt, k, s_ in [("HOJE", "o 12K de hoje (os bancos do render)", None, None)] + OPCOES:
        a = montar(big, SUITE_MASTER, k)
        b = montar(big, SUITE_2, s_)
        f = 0.75
        a = cv2.resize(a, None, fx=f, fy=f, interpolation=cv2.INTER_AREA)
        b = cv2.resize(b, None, fx=f, fy=f, interpolation=cv2.INTER_AREA)
        h = max(a.shape[0], b.shape[0])
        a = np.pad(a, ((0, h - a.shape[0]), (0, 0), (0, 0)), constant_values=255)
        b = np.pad(b, ((0, h - b.shape[0]), (0, 0), (0, 0)), constant_values=255)
        linha = np.hstack([a, np.full((h, 16, 3), 255, np.uint8), b])
        linhas.append(titulo(linha, f"{rot}: {txt}"))
    W = max(l.shape[1] for l in linhas)
    linhas = [np.pad(l, ((0, 14), (0, W - l.shape[1]), (0, 0)), constant_values=255) for l in linhas]
    folha = titulo(np.vstack(linhas), "POE 642 - Casa B - Terreo - bancos de pe de cama (escala do 12K)",
                   h=56, esc=0.78)
    cv2.imwrite(SAIDA, folha, [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(SAIDA, folha.shape)


if __name__ == "__main__":
    main()

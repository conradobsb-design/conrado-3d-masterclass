"""As esquadrias das Casas B e C Térreo no padrão das outras casas (19/11, conferência planta a planta).

Usuário: "garanta que as esquadrias tenham contorno fino preto. já os vidros e boxes, devem ser claros" e, sobre o
contorno: "é só para contornar a folha de vidro ... é só uma linha fina, não é para criar uma borda grossa". Na B Térreo
(o contorno preto marcado de 13/11) o vidro era um fio claro entre dois traços pretos e no 12K virou barra preta; na C
Térreo o caixilho era claro e o vidro preto. O usuário aprovou passar as duas para o padrão ("Sim").

Cada esquadria (as peças brancas finas do PDF, `esquadrias_pretas_1911.dados`, agrupadas) é redesenhada: a forma é a
união das peças com as frestas de até 3 px fechadas; dentro, o perfil cinza claro (1 px; 0,5 px nas peças finas) e o
vidro claro; o preto antigo em volta (lum < 60, até 3 px da forma) sai (inpaint pelo entorno); por fora, a linha preta
fina (0,5 px na final; no máximo `TRACO_12K` px no 12K). Nos 12K A e B o mesmo, pelo registro local de cada esquadria.
As folhas de madeira (tom de madeira dentro das peças) ficam como estão.

  python3 vidros_claros_1911.py B_Terreo [--sem12k] [--so i,j,...]
"""
import argparse
import contextlib
import io
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import esquadrias_pretas_1911 as EP  # noqa: E402

PROJ = EP.PROJ
PERFIL = (186, 184, 180)          # BGR: o perfil cinza claro do caixilho
VIDRO = (225, 221, 214)           # BGR: o vidro claro (o mesmo tom das janelas das Casas A e D)
LINHA = EP.Q_["perfil"]           # (34, 34, 36): a linha fina de fora
FRESTA_PX = 3.0                   # frestas entre peças do mesmo grupo fechadas até isto (px da final)
LIMPA_PX = 3.0                    # o preto antigo sai até esta distância da forma (px da final)
FORA = {                          # o que não é janela e fica como está (px da final)
    "B_Terreo": [(1725, 630, 1830, 700)],          # os batentes da porta do elevador
    "C_Terreo": [(1740, 815, 1800, 905)],           # os batentes da porta do elevador
}


def madeira(img, g):
    """A folha de madeira (o tom de madeira dentro das peças) fica de fora."""
    px = []
    for e in g:
        x0, y0, x1, y1 = [int(round(v)) for v in e[:4]]
        if x1 > x0 and y1 > y0:
            px.append(img[y0:y1, x0:x1].reshape(-1, 3))
    if not px:
        return False
    c = np.median(np.concatenate(px).astype(np.float32), 0)     # BGR
    return c[2] - c[0] > 30 and c.mean() > 110


def redesenhar(img, g, escala=1.0, origem=(0.0, 0.0), traco=0.5, inpaint=True):
    """A esquadria `g` (peças em px da final) redesenhada em `img` (BGR, grade = (px da final - origem) * escala)."""
    x0, y0, x1, y1 = EP.caixa(g)
    m = int(np.ceil((LIMPA_PX + 2) * escala)) + 2
    P = lambda v, o: (v - o) * escala
    X0, Y0 = max(int(P(x0, origem[0])) - m, 0), max(int(P(y0, origem[1])) - m, 0)
    X1, Y1 = min(int(np.ceil(P(x1, origem[0]))) + m, img.shape[1]), min(int(np.ceil(P(y1, origem[1]))) + m, img.shape[0])
    if X1 <= X0 or Y1 <= Y0:
        return img
    ss = 4 if escala <= 1.5 else 2
    H, W = (Y1 - Y0) * ss, (X1 - X0) * ss
    S = np.zeros((H, W), np.uint8)
    for e in g:
        a = (int(round((P(e[0], origem[0]) - X0) * ss)), int(round((P(e[1], origem[1]) - Y0) * ss)))
        b = (int(round((P(e[2], origem[0]) - X0) * ss)) - 1, int(round((P(e[3], origem[1]) - Y0) * ss)) - 1)
        cv2.rectangle(S, a, b, 255, -1)
    k = max(1, int(round(FRESTA_PX * escala * ss)))
    S = cv2.morphologyEx(S, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (k | 1, k | 1)))
    esp = min(x1 - x0, y1 - y0)
    fw = max(1, int(round((1.0 if esp >= 4 else 0.5) * escala * ss)))
    dentro = cv2.erode(S, cv2.getStructuringElement(cv2.MORPH_RECT, (2 * fw + 1, 2 * fw + 1)))
    tb = max(1, int(round(traco * escala * ss)))
    banda = cv2.dilate(S, cv2.getStructuringElement(cv2.MORPH_RECT, (2 * tb + 1, 2 * tb + 1))) & ~S
    kl = max(1, int(round(LIMPA_PX * escala * ss)))
    perto = cv2.dilate(S, cv2.getStructuringElement(cv2.MORPH_RECT, (2 * kl + 1, 2 * kl + 1)))

    def red(x):
        return cv2.resize(x.astype(np.float32) / 255, (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA)
    cS, cIn, cB, cP = red(S), red(dentro), red(banda), red(perto)
    reg = img[Y0:Y1, X0:X1].copy()
    if inpaint:
        lum = reg.astype(np.float32).mean(2)
        preto = ((lum < 60) & (cP > 0.3) & (cS < 0.5)).astype(np.uint8)
        if preto.any():
            preto = cv2.dilate(preto, np.ones((3, 3), np.uint8))
            reg = cv2.inpaint(reg, preto, max(2, int(round(1.5 * escala))), cv2.INPAINT_TELEA)
    out = reg.astype(np.float32)
    cF = np.clip(cS - cIn, 0, 1)
    out = out * (1 - cS[..., None]) + np.float32(PERFIL) * cF[..., None] + np.float32(VIDRO) * cIn[..., None]
    a = np.clip(cB * EP.Q_["forca"], 0, 1)[..., None]
    out = out * (1 - a) + np.float32(LINHA) * a
    img[Y0:Y1, X0:X1] = np.clip(np.round(out), 0, 255).astype(np.uint8)
    return img


def grupos(planta, img):
    with contextlib.redirect_stdout(io.StringIO()):
        Q, ok, fora, zonas = EP.dados(planta, img)
    def fora(g):
        x0, y0, x1, y1 = EP.caixa(g)
        return any(x0 < b and x1 > a and y0 < d and y1 > c for a, c, b, d in FORA.get(planta, []))
    return [g for g in ok if not madeira(img, g) and not fora(g)]


def forma(g, escala, origem, forma_hw, dil=1.0):
    """A forma da esquadria (peças, frestas fechadas) dilatada `dil` px da final, na grade dada (máscara bool)."""
    H, W = forma_hw
    S = np.zeros((H, W), np.uint8)
    for e in g:
        a = (int(round((e[0] - origem[0]) * escala)), int(round((e[1] - origem[1]) * escala)))
        b = (int(round((e[2] - origem[0]) * escala)) - 1, int(round((e[3] - origem[1]) * escala)) - 1)
        cv2.rectangle(S, a, b, 255, -1)
    k = max(1, int(round(FRESTA_PX * escala)))
    S = cv2.morphologyEx(S, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (k | 1, k | 1)))
    d = max(1, int(round(dil * escala)))
    return cv2.dilate(S, cv2.getStructuringElement(cv2.MORPH_RECT, (2 * d + 1, 2 * d + 1))) > 0


def doze_k(planta, antes, gs, folga=100, busca=15):
    """No 12K, cada esquadria é achada pela própria janela: a final (de antes, com o preto antigo) em volta dela,
    ampliada pela escala do `doze_k.json`, procurada a até `busca` px da final do lugar previsto (o registro da planta
    inteira erra até 8 px da final na fachada de baixo da Casa B). Dos candidatos (registro local + encaixe fino e a
    busca direta), fica o que põe mais do preto antigo do 12K dentro da forma."""
    c, pav = planta.split("_")
    dz = json.loads((PROJ / "POE642_Book/checklist/dados/doze_k.json").read_text())[planta]
    s = dz["s"]
    for op in "AB":
        f = PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_12K_opcao_{op}.jpg"
        pil = Image.open(f)
        dpi = pil.info.get("dpi", (743, 743))
        im = cv2.cvtColor(np.array(pil.convert("RGB")), cv2.COLOR_RGB2BGR)
        del pil
        cinza = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        ruins = []
        for gi, g in enumerate(gs):
            x0, y0, x1, y1 = EP.caixa(g)
            cand = []
            # 1) o registro local (ECC) + o encaixe fino
            try:
                box = (max(int(x0) - folga, 0), max(int(y0) - folga, 0), min(int(np.ceil(x1)) + folga, antes.shape[1]),
                       min(int(np.ceil(y1)) + folga, antes.shape[0]))
                mapa, cc = EP.registro_12k(antes, cinza, dz, box)
                X0, Y0 = mapa(0.0, 0.0)
                cand.append((X0, Y0, (mapa(1000.0, 0.0)[0] - X0) / 1000.0))
            except cv2.error:
                pass
            # 2) a busca direta da janela (a final em volta, 10 px), a até `busca` px da final
            e = 10
            ax0, ay0 = max(int(x0) - e, 0), max(int(y0) - e, 0)
            fa = cv2.cvtColor(antes[ay0:int(np.ceil(y1)) + e, ax0:int(np.ceil(x1)) + e], cv2.COLOR_BGR2GRAY).astype(np.float32)
            tpl = cv2.resize(fa, None, fx=s, fy=s, interpolation=cv2.INTER_CUBIC)
            px0, py0 = (ax0 - dz["x0"]) * s, (ay0 - dz["y0"]) * s
            R = int(round(busca * s))
            sa0, sb0 = max(int(px0) - R, 0), max(int(py0) - R, 0)
            area = cinza[sb0:sb0 + tpl.shape[0] + 2 * R, sa0:sa0 + tpl.shape[1] + 2 * R].astype(np.float32)
            if area.shape[0] > tpl.shape[0] and area.shape[1] > tpl.shape[1]:
                r = cv2.matchTemplate(area, tpl, cv2.TM_CCOEFF_NORMED)
                _, mx, _, (bx, by) = cv2.minMaxLoc(r)
                if mx > 0.5:
                    cand.append((sa0 + bx - ax0 * s, sb0 + by - ay0 * s, s))
            if not cand:
                continue
            # o candidato que põe mais do preto antigo dentro da forma (dilatada 1,5 px)
            melhor, nota = None, -1.0
            for X0, Y0, sx in cand:
                m = int(np.ceil((LIMPA_PX + 2) * sx))
                A0, B0 = max(int((x0 * sx + X0)) - m, 0), max(int((y0 * sx + Y0)) - m, 0)
                A1, B1 = min(int(np.ceil(x1 * sx + X0)) + m, im.shape[1]), min(int(np.ceil(y1 * sx + Y0)) + m, im.shape[0])
                if A1 <= A0 or B1 <= B0:
                    continue
                preto = cinza[B0:B1, A0:A1] < 70
                fm = forma(g, sx, ((A0 - X0) / sx, (B0 - Y0) / sx), preto.shape, dil=1.5)
                n = preto.sum()
                v = (preto & fm).sum() / n if n else 0.0
                if v > nota:
                    melhor, nota = (X0, Y0, sx), v
            X0, Y0, sx = melhor
            if nota < 0.5:
                ruins.append((gi, round(nota, 2)))
            im = redesenhar(im, g, escala=sx, origem=(-X0 / sx, -Y0 / sx), traco=min(0.5, EP.TRACO_12K / sx))
        Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).save(f, quality=95, subsampling=0, dpi=dpi)
        print(f"   {f.name}: {len(gs)} esquadrias; encaixe fraco: {ruins}")
        del im, cinza


def aplicar(planta, sem12k=False, so=None):
    c, pav = planta.split("_")
    fin = PROJ / EP.PLANTAS[planta][0]
    antes = cv2.imread(str(fin))
    gs = grupos(planta, antes)
    if so is not None:
        gs = [g for i, g in enumerate(gs) if i in so]
    novo = antes.copy()
    for g in gs:
        novo = redesenhar(novo, g)
    cv2.imwrite(str(fin), novo)
    pf = PROJ / f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{pav}_entrega.png"
    pr = cv2.imread(str(pf))
    pr[:2160] = novo
    cv2.imwrite(str(pf), pr)
    print(planta, len(gs), "esquadrias na final")
    if not sem12k:
        doze_k(planta, antes, gs)
    return antes, novo, gs


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("planta")
    ap.add_argument("--sem12k", action="store_true")
    ap.add_argument("--so", default=None)
    a = ap.parse_args()
    aplicar(a.planta, a.sem12k, None if a.so is None else {int(v) for v in a.so.split(",")})

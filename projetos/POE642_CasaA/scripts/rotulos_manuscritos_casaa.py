"""Os rótulos da Casa A em letra manuscrita (opção B, ao lado da fonte atual).

Pedido do usuário (10/11/26), com o recorte do título "Katherine Backyard" da planta de referência do quintal: "E ME
MANDE UMA VERSÃO TAMBÉM COM TIPO DE FONTE. QUERO TER DUAS OPÇÕES. COM A FONTE ATUAL E A FONTE DA LETRA IGUAL A ESSA A DA
IMAGEM".

A letra da referência é de marcador, levemente inclinada, com o "a" de um bojo e o "y" de perna reta. Entre as
manuscritas livres (OFL) comparadas na mesma largura (Architects Daughter, Caveat, Coming Soon, Delius, Gloria
Hallelujah, Handlee, Indie Flower, Kalam, Patrick Hand, Sue Ellen Francisco), a mais parecida é a Kalam Regular
(`entrega/assets/fontes/Kalam-Regular.woff`, com a licença): o mesmo traço, a inclinação e as proporções. A Caveat é mais
estreita e mais inclinada.

A opção A é a final como está (Inter). A opção B parte dela:
  1. os rótulos (pela especificação de `rotulos_subsolo_casaa`, a mesma da final) e o "SOBE PARA O / DECK" da escada
     saem (`ampliacao_a3_casaa.tirar`: o fundo pela conta do alfa e o miolo do traço pelo entorno);
  2. cada linha volta na Kalam, no mesmo lugar: o centro da linha em Inter (as linhas presas pela esquerda, como o nome
     e a área, viram centradas no mesmo meio) e a mesma linha de base, a altura das maiúsculas `altura` x a da Inter (a
     manuscrita lê menor no mesmo corpo); a área num texto só ("A: 6,83 m²", com o ² da própria Kalam); a mesma cor;
  3. o texto da escada, preso pela esquerda junto à seta, como estava.

  python3 rotulos_manuscritos_casaa.py                 # Subsolo: a final e a prancha da opção B (sufixo _manuscrita)

Saída: `renders/POE642_CasaA_PH_<pavimento>_final_rotulos_manuscrita.png`, a comparação das duas opções em
`renders/POE642_CasaA_PH_<pavimento>_rotulos_opcoes_A_B.jpg` e a prancha `entrega/POE642_CasaA_PH_<pavimento>_entrega_manuscrita.png`.
"""

import argparse
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import ampliacao_a3_casaa as AM                # noqa: E402
import final3840_casaa as FA                    # noqa: E402
import retoque_1pav_casae as R1                 # noqa: E402
import rotulos_subsolo_casaa as RS              # noqa: E402

FONTE = FA.CASA / "entrega" / "assets" / "fontes" / "Kalam-Regular.woff"
MANUSCRITA = {"altura": 1.12, "ss": 4,
              # o traço engrossado (px de cada lado), para o peso de marcador da referência
              "reforco_px": 0.25,
              # o corpo da escada (px) e a cor ficam os da final; a letra da escada na mesma proporção dos rótulos
              "escada": True}


def _altura_maiuscula(caminho, em=200):
    from PIL import ImageFont
    f = ImageFont.truetype(str(caminho), em)
    x0, y0, x1, y1 = f.getbbox("H", anchor="ls")
    return (y1 - y0) / em


def linhas_rotulo(Q, aj, pdf2img=None, escala_desvio=None):
    """As linhas do rótulo ajustado, como o `retoque_1pav_casae.rotulos_ambientes` as põe: [(texto, corpo em px,
    centro x, linha de base y)], com a área e o "2" num texto só ("A: 6,83 m²"), centrada no meio do que a Inter
    ocupava."""
    from PIL import ImageFont
    from rodape_entrega import FONTES
    q = R1.ROTULOS
    pdf2img = pdf2img or Q.p2q
    esc = escala_desvio or Q.W / 2000
    r, opc = RS.r_do_ajuste(Q, aj)                 # o texto da especificação (BH., 10/11)
    nome, linhas, (pcx, pcy), caixa = r
    e = opc.get("corpo", q["escala"])
    dx, dy = aj["desvio"][0] / (Q.W / 2000) * esc, aj["desvio"][1] / (Q.W / 2000) * esc
    (ax_, ay_), (bx_, by_) = pdf2img(0, 0), pdf2img(100, 0)
    px_pt = np.hypot(bx_ - ax_, by_ - ay_) / 100
    cx, cy = pdf2img(pcx, pcy)
    linhas = [(t, tam, o, "ls") for t, tam, o in linhas]
    if "quebra" in opc:
        _, tam0, (_, oy0), _ = linhas[0]
        passo = linhas[1][2][1] - oy0 if len(linhas) > 1 else 1.33 * tam0
        extra_n = len(opc["quebra"]) - 1
        sobe, xm = extra_n * passo / 2, (caixa.x0 + caixa.x1) / 2
        linhas = ([(p, tam0, (xm, oy0 - sobe + k * passo), "ms") for k, p in enumerate(opc["quebra"])]
                  + [(t, tam, (ox, oy - sobe + extra_n * passo), a) for t, tam, (ox, oy), a in linhas[1:]])
    out = []
    i = 0
    while i < len(linhas):
        texto, tam, (ox, oy), ancora = linhas[i]
        corpo = tam * px_pt * e
        gx, gy = pdf2img(ox, oy)
        gx, gy = cx + (gx - cx) * e + dx, cy + (gy - cy) * e + dy
        peso = q["fonte"] if texto.startswith("A:") else q.get("fonte_nome", q["fonte"])
        f = ImageFont.truetype(str(FONTES / f"Inter-{peso}.otf"), max(4, int(round(corpo * 4))))
        larg = f.getlength(texto) / 4
        if texto.startswith("A:") and i + 1 < len(linhas) and linhas[i + 1][0] == "2":
            t2, tam2 = linhas[i + 1][0], linhas[i + 1][1]
            c2 = tam2 * px_pt * e
            f2 = ImageFont.truetype(str(FONTES / f"Inter-{q['fonte']}.otf"), max(4, int(round(c2 * 4))))
            larg += q["folga_m2"] * corpo + f2.getlength(t2) / 4
            texto = texto + "²"
            i += 1
        meio = gx + larg / 2 if ancora == "ls" else gx
        out.append((texto, corpo, meio, gy))
        i += 1
    return out


def desenhar(img, itens, cor, fonte=FONTE, ss=4, reforco_px=0.0):
    """Os textos [(texto, corpo em px, x, y, âncora)] na fonte, em `cor`, com antisserrilhado e o traço engrossado
    `reforco_px` de cada lado."""
    rf = int(round(reforco_px * ss))
    from PIL import Image, ImageDraw, ImageFont
    f = img.astype(np.float32)
    for texto, corpo, x, y, ancora in itens:
        ft = ImageFont.truetype(str(fonte), max(4, int(round(corpo * ss))))
        x0, y0, x1, y1 = ft.getbbox(texto, anchor=ancora)
        bx0, by0 = int(np.floor(x + x0 / ss)) - 3, int(np.floor(y + y0 / ss)) - 3
        bx1, by1 = int(np.ceil(x + x1 / ss)) + 3, int(np.ceil(y + y1 / ss)) + 3
        tela = Image.new("L", ((bx1 - bx0) * ss, (by1 - by0) * ss), 0)
        ImageDraw.Draw(tela).text(((x - bx0) * ss, (y - by0) * ss), texto, font=ft, fill=255, anchor=ancora,
                                  stroke_width=rf, stroke_fill=255)
        a = np.asarray(tela.resize((bx1 - bx0, by1 - by0), Image.LANCZOS), np.float32)[..., None] / 255
        f[by0:by1, bx0:bx1] = f[by0:by1, bx0:bx1] * (1 - a) + np.float32(cor) * a
    return np.clip(np.round(f), 0, 255).astype(np.uint8)


def manuscrita(chave, img):
    q = MANUSCRITA
    Q = FA.QuadroA(chave)
    from rodape_entrega import FONTES
    k_rot = _altura_maiuscula(FONTES / f"Inter-{R1.ROTULOS['fonte']}.otf") / _altura_maiuscula(FONTE) * q["altura"]
    # os rótulos da final: a especificação gravada (`rotulos_subsolo_casaa`, com os pedidos de 10/11)
    aj = RS.ler_spec()
    print(f"[{chave}] {len(aj)} rótulos da especificação ({RS.SPEC.name})")
    camadas = RS.camadas(Q, aj, img.shape[:2])
    escada = q["escada"] and chave == "Subsolo"
    if escada:
        camadas += AM.escada_camadas(img.shape[:2])
    copiar = [i for i, r in enumerate(aj) if r["casa"] < AM.A3["casa_px"]]
    limpa = AM.tirar(img, camadas, AM.A3["cheio"], copiar=copiar)
    out = limpa
    for a in aj:
        itens = [(t, c * k_rot, x, y, "ms") for t, c, x, y in linhas_rotulo(Q, a)]
        out = desenhar(out, itens, tuple(a["cor"]), reforco_px=q["reforco_px"])
    if escada:
        # a seta (a primeira camada da escada) volta como estava; o texto, na Kalam, preso pela esquerda
        seta_a, seta_cor = camadas[len(aj)]
        out = AM.pintar(out, [(seta_a, seta_cor)])
        import cliente_subsolo_casaa_0511 as CS
        e, qe = FA.ESCADA_A, CS.ESCADA_CS
        k_esc = _altura_maiuscula(FONTES / e["fonte"]) / _altura_maiuscula(FONTE) * q["altura"]
        tx, ty = qe["origem_px"]
        itens = [(linha, e["corpo_px"] * k_esc, tx, ty + i * qe["entrelinha_px"], "ls") for i, linha in enumerate(qe["texto"])]
        out = desenhar(out, itens, e["cor_texto"], reforco_px=q["reforco_px"])
    print(f"    {len(aj)} rótulos{' e o texto da escada' if escada else ''} na Kalam (maiúsculas {q['altura']:.2f} x "
          "a altura da Inter)")
    return out


def comparar(chave, a, b):
    """As duas opções, uma sobre a outra, no recorte da planta."""
    from PIL import Image, ImageDraw, ImageFont
    from rodape_entrega import FONTES
    g = cv2.cvtColor(a, cv2.COLOR_BGR2GRAY)
    ys, xs = np.nonzero(g < 245)
    x0, y0, x1, y1 = xs.min() - 20, ys.min() - 60, xs.max() + 20, ys.max() + 20
    blocos = []
    for rot, im in (("A · fonte atual (Inter)", a), ("B · letra manuscrita (Kalam)", b)):
        c = Image.fromarray(cv2.cvtColor(im[y0:y1, x0:x1], cv2.COLOR_BGR2RGB))
        ImageDraw.Draw(c).text((24, 14), rot, font=ImageFont.truetype(str(FONTES / "Inter-Medium.otf"), 30),
                               fill=(40, 40, 40))
        blocos.append(cv2.cvtColor(np.asarray(c), cv2.COLOR_RGB2BGR))
    junto = np.vstack([blocos[0], np.full((16, blocos[0].shape[1], 3), 255, np.uint8), blocos[1]])
    arq = FA.CASA / "renders" / f"POE642_CasaA_PH_{chave}_rotulos_opcoes_A_B.jpg"
    cv2.imwrite(str(arq), junto, [cv2.IMWRITE_JPEG_QUALITY, 92])
    print(f"    {arq.name}")


FINAIS = {"Subsolo": FA.CASA / "renders" / "POE642_CasaA_PH_Subsolo_final_rotulos.png"}

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pavimento", nargs="?", default="Subsolo", choices=list(FINAIS))
    ap.add_argument("--sem-prancha", action="store_true")
    a = ap.parse_args()
    img = cv2.imread(str(FINAIS[a.pavimento]))
    out = manuscrita(a.pavimento, img)
    saida = FINAIS[a.pavimento].with_name(FINAIS[a.pavimento].stem + "_manuscrita.png")
    cv2.imwrite(str(saida), out)
    print(f"    {saida}")
    comparar(a.pavimento, img, out)
    if not a.sem_prancha:
        subprocess.run([sys.executable, str(AQUI / "rodape_entrega.py"), "--no-quadro", "--sufixo", "_manuscrita",
                        "--render", f"{a.pavimento}={saida}"], check=True, cwd=AQUI)

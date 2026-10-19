#!/usr/bin/env python3
"""Nomes e áreas dos ambientes nas plantas da Casa A (POE 642), pela regra da Casa E.

Pedido do usuário (18/10/26): "vamos fazer os ajustes nas plantas da casa A", os mesmos que a Casa E recebeu:
os nomes e as áreas dos ambientes, como no 1º Pavimento, no Subsolo e no Térreo da Casa E
(`retoque_1pav_casae.rotulos_ambientes`). Cada linha do rótulo do PDF entra igual (o nome e "A: 15,25 m²"), na
posição do PDF, no corpo do PDF 30% maior, em Inter Regular preta; no granito marrom, cinza (150); os que caem
sobre móvel ou peça vão ao piso livre mais próximo. Os PDFs são os do Drive que geraram as bases da Casa A,
em `_pdfs_cliente/642 - <PAVIMENTO> - CASA A.pdf`. Ficam fora as notas que não são ambientes (projeções,
shafts, afastamentos, divisa, muros, acessos) e o título da folha.

As imagens aprovadas da Casa A têm 2000 px (os renders chegaram comprimidos pelo chat), e em 2000 px o rótulo
do PDF fica com ~6 px de corpo e não se lê. Por isso a imagem vai ao quadro comum em 3840 px (ampliada com
Lanczos pelo `rodape_entrega.no_quadro_comum`, como nas pranchas) e os rótulos são escritos nessa resolução.
O granito é achado na própria imagem (escuro e quente), porque a base da Casa A não tem a cor da legenda.

Uso (da pasta POE642_CasaA/scripts/):
  python3 rotulos_casaa.py Subsolo     # -> renders/POE642_CasaA_PH_Subsolo_final_rotulos.png (+ _preview.jpg)
"""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np
import pymupdf
from PIL import Image

import retoque_1pav_casae as R1
from opcoes_1pav_casae import quadro_pdf
from rodape_entrega import no_quadro_comum

AQUI = Path(__file__).resolve().parent
CASA = AQUI.parent
RAIZ = CASA.parent
CONFIG = AQUI / "config_bases.json"
LARGURA = 3840
# notas do PDF que não são ambientes, e o título da folha
FORA = ("PROJ.", "SHAFT", "FLOREIRA", "AFASTAMENTO", "DIVISA", "MURO", "LIMITE", "ACESSO", "PEDESTRES",
        "VEÍCULOS", "SUBSOLO", "TÉRREO")
# granito marrom na imagem: luminância (desfocada) baixa e tom quente (o deck de madeira e a grama não entram)
GRANITO = {"lum_max": 95, "quente_min": 12, "sigma": 3}

PAVIMENTOS = {
    "Subsolo": {"render": "renders/POE642_CasaA_PH_Subsolo_final_ajustes.png",   # com os ajustes da conferência
                # o alinhamento ao quadro comum vem sempre da imagem aprovada: os ajustes não mexem no resto
                "aprovada": "renders/POE642_CasaA_PH_Subsolo_final.png",
                "pdf": "642 - SUBSOLO - CASA A.pdf",
                "sem_tela": "bases/POE642_CasaA_BASE_Subsolo_v4.png",
                # (nome, centro do rótulo do PDF no quadro final em px de 2000, desvio em px de 2000[, opções])
                "ajustes": [
                    # o piso de cima do banho é o box (o chuveiro e o vidro entraram nos ajustes): no corpo do PDF,
                    # à direita da ducha, dentro do box (o resto do banho é vaso, bancada e o arco da porta)
                    ("BANHO SERV.", (605.5, 513.0), (-4.5, -39), 1.0),
                    ("BANHO MASC.", (926.4, 809.0), (-2, 0))]},          # encostado no arco da porta
    "Terreo": {"render": "renders/POE642_CasaA_PH_Terreo_final_bege_barlavento_ajustes.png",   # com os ajustes
               "aprovada": "renders/POE642_CasaA_PH_Terreo_final_bege_barlavento.png",
               "pdf": "642 - TÉRREO - CASA A.pdf",
               "sem_tela": "bases/POE642_CasaA_BASE_Terreo_v6.png",
               # notas do PDF que entram mesmo estando em FORA (pedidos do usuário, 19/10/26: "representar e gerar o
               # rótulo da claraboia"; "trazer o rótulo do shaft")
               "incluir": ("PROJ. CLARABOIA", "SHAFT"),
               "ajustes": [
                   # a garagem é toda carro: no corpo do PDF, no vão entre o primeiro e o segundo carro
                   ("GARAGEM", (1265.1, 771.7), (-40.6, 0), 1.0),
                   ("SALA DE ESTAR", (1074.6, 270.8), (-8.6, 12.2)),      # na mesa de centro: abaixo dela, no tapete
                   # o quarto do motorista (pedido do usuário, 19/10/26: "o rótulo do quarto do motorista está no local
                   # errado"): ao lado da cama, como no PDF, no piso livre entre a cama e o armário (~26 px), um pouco
                   # menor que o PDF (a Inter é mais larga); no granito (a caixa do texto pega a cama, então a cor vai dada)
                   ("Q. MOTORISTA", (1281.4, 632.7), (6.2, -0.2), {"cor": (150, 150, 150), "corpo": 0.8}),
                   # banhos e despensa estreitos: no corpo do PDF, no piso livre entre as peças
                   # o banho do motorista ganhou o arco da porta em cinza (ajustes, portas no granito): o rótulo sobe
                   # e vai à esquerda, entre o vaso e o arco, um pouco menor, para o arco não cortar o texto
                   ("B. MOTORISTA", (1211.8, 661.1), (0, -7), 0.9),
                   ("WC", (803.7, 833.6), (0, 0), 1.0),
                   ("BANHO VARANDA", (862.0, 793.0), (1, 0), 1.0),
                   # a despensa ganhou o arco da porta (ajustes, portas no granito): o rótulo desce para baixo do
                   # arco, como no PDF, um pouco menor
                   ("DESPENSA", (1092.0, 825.2), (-1, -3.2), 0.9),
                   ("VARANDA", (879.1, 345.6), (0, -8)),                  # na poltrona: um pouco acima
                   ("LAVABO", (1192.4, 224.3), (-2, 0)),                  # encostado na bancada
                   ("SALA DE JANTAR", (1142.7, 506.4), (-2.5, 0)),       # encostado no vidro
                   # o jardim de 4,79 m² ficou verde, com as três touceiras (ajustes): em branco, que se lê sobre a
                   # grama e as palmeiras
                   ("JARDIM", (826.1, 870.7), (0, 0), {"cor": (255, 255, 255)}),
                   # a claraboia do lavabo: no corpo do PDF, em duas linhas (numa só, encostava na parede e no vaso),
                   # logo abaixo do tracejado
                   ("PROJ. CLARABOIA", (1192.2, 204.2), (0, 4), {"corpo": 1.0, "quebra": ["PROJ.", "CLARABOIA"]}),
                   # o shaft ao lado do elevador tem ~15 px de largura: no corpo do PDF um pouco menor, para caber
                   ("SHAFT", (1233.4, 606.7), (0, 0), 0.85)]},
    "1Pavimento": {"render": "renders/POE642_CasaA_PH_1Pavimento_v7_final2.png",
                   "pdf": "642 - 1º PAVIMENTO - CASA A.pdf",
                   "sem_tela": "bases/POE642_CasaA_BASE_1Pavimento_v3.png",
                   "ajustes": [
                       ("SUÍTE 3", (904.1, 237.3), (1, 28.7)),             # na cama: no tapete, abaixo dela
                       ("SUÍTE 2", (932.9, 575.9), (-12.9, -20.9)),        # na cama: no tapete, acima dela
                       ("SUÍTE MASTER", (837.0, 695.9), (25, -13.9)),      # no pufe: no piso acima dele, fora do tapete
                       ("SALA ÍNTIMA", (1083.4, 552.2), (0, -20.7)),       # na mesa de centro: entre ela e o sofá
                       ("B. SERVIÇO", (1142.1, 779.6), (5.3, -10.6)),      # o "m²" caía no vaso: no piso livre de cima
                       ("BANHO 1", (1287.3, 636.5), (-3.3, 0)),            # encostado no vaso
                       ("CLOSET MASTER", (947.8, 757.1), (-3, 0))]},       # encostado no armário
}


def granito(img):
    q = GRANITO
    f = cv2.GaussianBlur(img.astype(np.float32), (0, 0), q["sigma"])
    lum = f.mean(axis=2)
    return (lum < q["lum_max"]) & (f[..., 2] - f[..., 0] > q["quente_min"]) & (f[..., 2] >= f[..., 1])


def no_quadro_fixo(render, aprovada, base_png, chave):
    """Como `rodape_entrega.no_quadro_comum`, mas o afim vem da imagem aprovada e é aplicado à ajustada: o SIFT
    na imagem ajustada achava um afim um pouco diferente e a prancha inteira mudava por reamostragem."""
    base = cv2.imread(str(base_png))
    W = LARGURA
    H = round(base.shape[0] * W / base.shape[1])
    base_red = cv2.resize(base, (W, H), interpolation=cv2.INTER_AREA)

    def ampliar(im):
        r = cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2BGR)
        interp = cv2.INTER_AREA if r.shape[1] > W else cv2.INTER_LANCZOS4
        return cv2.resize(r, (W, round(r.shape[0] * W / r.shape[1])), interpolation=interp)
    ap, aj = ampliar(aprovada), ampliar(render)
    sift = cv2.SIFT_create(12000)
    k1, d1 = sift.detectAndCompute(cv2.cvtColor(base_red, cv2.COLOR_BGR2GRAY), None)
    k2, d2 = sift.detectAndCompute(cv2.cvtColor(ap, cv2.COLOR_BGR2GRAY), None)
    bons = [a for a, b in cv2.BFMatcher().knnMatch(d1, d2, k=2) if a.distance < 0.75 * b.distance]
    src = np.float32([k1[m.queryIdx].pt for m in bons])
    dst = np.float32([k2[m.trainIdx].pt for m in bons])
    A, inl = cv2.estimateAffine2D(src, dst, ransacReprojThreshold=2.5)
    print(f"    {chave}: afim da imagem aprovada ({int(inl.sum())} pontos), aplicado à imagem com ajustes")
    return cv2.warpAffine(aj, cv2.invertAffineTransform(A), (W, H), flags=cv2.INTER_CUBIC,
                          borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))


def final_rotulos(chave):
    q = PAVIMENTOS[chave]
    cfg = json.loads(CONFIG.read_text())
    base = (CONFIG.parent / cfg["entrega"]["pasta_bases"] / cfg["entrega"]["pavimentos"][chave]["base"]).resolve()
    render = Image.open(CASA / q["render"]).convert("RGB")
    if "aprovada" in q:
        final = no_quadro_fixo(render, Image.open(CASA / q["aprovada"]).convert("RGB"), base, chave)
    else:
        final = cv2.cvtColor(np.asarray(no_quadro_comum(render, base, chave, LARGURA)), cv2.COLOR_RGB2BGR)
    pg = pymupdf.open(RAIZ / "_pdfs_cliente" / q["pdf"])[cfg["pavimentos"][chave]["pagina"]]
    at, lt = cv2.imread(str(base), cv2.IMREAD_GRAYSCALE).shape
    hb, wb = cv2.imread(str(CASA / q["sem_tela"]), cv2.IMREAD_GRAYSCALE).shape
    p2q = quadro_pdf(pg, cfg, lt, at, wb, hb, LARGURA)
    rot = [r for r in R1.rotulos_pdf(pg) if r[0] in q.get("incluir", ()) or not any(f in r[0] for f in FORA)]
    print(f"    {len(rot)} rótulos: " + ", ".join(r[0] for r in rot))
    return R1.rotulos_ambientes(final, rot, p2q, escala_desvio=LARGURA / 2000, granito=granito(final),
                                ajustes=q["ajustes"])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pavimento", choices=list(PAVIMENTOS))
    ap.add_argument("--saida", type=Path, default=CASA / "renders")
    args = ap.parse_args()
    print(f"[{args.pavimento}] nomes e áreas dos ambientes, pela regra da Casa E")
    final = final_rotulos(args.pavimento)
    nome = Path(PAVIMENTOS[args.pavimento]["render"]).stem.split("_final")[0] + "_final_rotulos"
    args.saida.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(args.saida / f"{nome}.png"), final)
    cv2.imwrite(str(args.saida / f"{nome}_preview.jpg"),
                cv2.resize(final, (2000, round(2000 * final.shape[0] / final.shape[1])), interpolation=cv2.INTER_AREA),
                [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"    {args.saida / (nome + '.png')} {final.shape[1]}x{final.shape[0]}")


if __name__ == "__main__":
    main()

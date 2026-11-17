"""Térreo da Casa E, 17/11, na final e direto nos 12K A (Inter) e B (Kalam) (usuário, com a imagem da escada do
Subsolo: "a descrição fica ao lado esquerdo do triângulo/seta"): o "DESCE PARA O / SUBSOLO" sai da circulação gourmet
(o piso marrom de volta: a baixa frequência pelo inpaint do entorno e o grão do piso de logo acima; a máscara pega as
letras claras e o antisserrilhado) e vai para a esquerda do triângulo e do D da escada (x 1153 a 1164, y 423 a 452),
a ~7 px deles, no meio da altura dos dois, no corpo das descrições (`escada_painel_casae_1711.descricao_sobe`). O fundo
ali é o Bege Bahia: as letras no escuro das descrições (20), como o "DESCE PARA O JARDIM"; no 12K B na Kalam, e o JSON
da Kalam atualizado (as linhas e a cor).

  python3 descricao_subsolo_terreo_casae_1711.py doze [--opcao AB]     (antes da final)
  python3 descricao_subsolo_terreo_casae_1711.py final
"""
import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import danae_foto as DF                                     # noqa: E402
import escada_painel_casae_1711 as EP                       # noqa: E402
from correcoes_terreo_casab_1611 import Mapa                # noqa: E402

RAIZ = AQUI.parents[1]
FINAL = RAIZ / "POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_final.png"
DOZE = RAIZ / "POE642_CasaE/entrega/POE642_CasaE_PH_Terreo_12K_opcao_{}.jpg"
KALAM = EP.KALAM

DESCE = {"texto": ("DESCE PARA O", "SUBSOLO"), "corpo": 11, "k": 1.0, "centro": (1106.5, 437.5),
         "cor": (20, 20, 20), "velho": (1258, 376, 1352, 411), "desloc_y": -30, "destoa": 14, "destoa_12k": 12,
         "caixa": (1040, 340, 1370, 480), "nome_kalam": "escada: DESCE PARA O SUBSOLO",
         "kalam_linhas": ((9.0, 79.0), (9.0, 52.0))}


def _apagar(out, m, q):
    """As letras de antes (claras no piso marrom) saem: a baixa frequência pelo inpaint do entorno e o grão do piso de
    logo acima; a máscara, o que destoa da mediana da caixa (claro ou escuro), com folga."""
    x0, y0, x1, y1 = m.reti(q["velho"])
    reg = np.ascontiguousarray(out[y0:y1, x0:x1])
    L = reg.astype(np.float32).mean(-1)
    marca = (np.abs(L - float(np.median(L))) > (q["destoa"] if m.s < 1.5 else q["destoa_12k"])).astype(np.uint8)
    k = max(1, int(round(1.5 * m.s)))
    marca = cv2.dilate(marca, np.ones((2 * k + 1, 2 * k + 1), np.uint8))
    sig = 1.5 * m.s
    baixa = cv2.GaussianBlur(cv2.inpaint(reg, marca * 255, max(3, int(round(5 * m.s))), cv2.INPAINT_TELEA)
                             .astype(np.float32), (0, 0), sig)
    dy = int(round(q["desloc_y"] * m.s))
    fonte = out[y0 + dy:y1 + dy, x0:x1].astype(np.float32)
    grao = fonte - cv2.GaussianBlur(fonte, (0, 0), sig)
    a = np.clip(cv2.GaussianBlur(marca.astype(np.float32), (0, 0), 0.6 * m.s) * 1.5, 0, 1)[..., None]
    novo = reg.astype(np.float32) * (1 - a) + (baixa + grao) * a
    out[y0:y1, x0:x1] = np.clip(np.round(novo), 0, 255).astype(np.uint8)


def descricao(out, mp, kalam=None, q=DESCE):
    guarda = EP._apagar
    EP._apagar = _apagar
    try:
        EP.descricao_sobe(out, mp, kalam, q)
    finally:
        EP._apagar = guarda
    print("    escada do Subsolo: a descrição à esquerda do triângulo e do D")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("acao", choices=("final", "doze"))
    ap.add_argument("--opcao", default="AB")
    ap.add_argument("--entrada")
    ap.add_argument("--saida")
    a = ap.parse_args()
    fin = cv2.imread(a.entrada or str(FINAL))
    if a.acao == "final":
        out = fin.copy()
        descricao(out, Mapa())
        cv2.imwrite(a.saida or str(FINAL), out)
        if not a.saida:
            rots = json.loads(KALAM.read_text())
            for b in rots:
                if b["nome"] == DESCE["nome_kalam"]:
                    b["linhas"] = EP._linhas_kalam(DESCE)
                    b["cor"] = list(DESCE["cor"])
            KALAM.write_text(json.dumps(rots, ensure_ascii=False, indent=1) + "\n")
        return
    from PIL import Image
    for op in a.opcao:
        f = Path(str(DOZE).format(op))
        img = cv2.imread(str(f))
        M = DF.afim_12k(fin, img)
        mp = Mapa(float(np.hypot(M[0, 0], M[1, 0])), (float(M[0, 2]), float(M[1, 2])))
        mp.ref = fin
        out = img.copy()
        descricao(out, mp, EP._kalam_global() if op == "B" else None)
        dpi = int(round(out.shape[1] / (420 / 25.4)))
        dest = a.saida.format(op) if a.saida else str(f)
        Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB)).save(dest, quality=95, subsampling=0, dpi=(dpi, dpi))
        print(f"    {Path(dest).name}")


if __name__ == "__main__":
    main()

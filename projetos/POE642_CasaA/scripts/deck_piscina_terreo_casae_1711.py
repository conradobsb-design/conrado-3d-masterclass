"""Térreo da Casa E, 17/11, na final e direto nos 12K A (Inter) e B (Kalam), no afim afinado em cada caixa:

1. `descricao_desce` (usuário: "a descrição 'desce para o jardim' fica ao lado direito da seta, próxima a ela"): o
   "DESCE PARA O / JARDIM" sai do deck (o piso de logo acima no lugar das letras) e vai para a direita do triângulo e do
   D da escada do deck, a ~10 px da base do triângulo, no meio da altura do triângulo e do D, no corpo das descrições
   (a rotina de `escada_painel_casae_1711.descricao_sobe`). No 12K B, na Kalam; o JSON da Kalam é atualizado.
2. `vidros_piscina` (usuário: "coloque bordas de vidros finos. são dois, um mais extremo e outro mais recuado à
   esquerda. esses que estão são muito grossos."): as duas barras cinza grossas da borda esquerda da piscina (as duas
   paredes de vidro do PDF, ARQ_PAREDE, de 9 px cada) saem; a água de logo ao lado no lugar (`_remenda`, a borda de
   fora com a água de dentro do canal, a de dentro com a do canal e a da piscina, metade a metade) e o vidro fino da
   piscina da Casa C (`mobiliario_terreo_casac_1311.VIDRO_PISC_C`: o perfil escuro de 1,8 px): o de fora na face
   externa (o extremo). Depois (usuário, com a imagem: "mantenha o vidro na extremidade e represente a parede com o
   tom de parede onde está indicado"): `parede_piscina`, a de dentro é parede, o retângulo do PDF no cinza das
   paredes (80).

  python3 deck_piscina_terreo_casae_1711.py doze [--opcao AB]     (antes da final: a final de antes é a referência)
  python3 deck_piscina_terreo_casae_1711.py final
  (--passos descricao,vidros,parede; na rodada da parede, só `--passos parede` sobre a final já com os outros dois)
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
import correcoes_terreo_casab_1611 as CB                    # noqa: E402
import escada_painel_casae_1711 as EP                       # noqa: E402
from correcoes_terreo_casab_1611 import Mapa                # noqa: E402

RAIZ = AQUI.parents[1]
FINAL = RAIZ / "POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_final.png"
DOZE = RAIZ / "POE642_CasaE/entrega/POE642_CasaE_PH_Terreo_12K_opcao_{}.jpg"
KALAM = EP.KALAM

# 1. px da final: o meio do bloco à direita do triângulo (base em x ~781) e do D (y 1352 e 1371)
DESCE = {"texto": ("DESCE PARA O", "JARDIM"), "corpo": 11, "k": 1.0, "centro": (832.0, 1361.5),
         "cor": (20, 20, 20), "velho": (574, 1446, 671, 1481), "desloc_y": -32, "escuro": 10, "escuro_12k": 10,
         "caixa": (560, 1290, 900, 1500), "nome_kalam": "escada: DESCE PARA O JARDIM",
         "kalam_linhas": ((9.0, 79.0), (9.0, 42.0))}

# 2. px da final: as duas paredes de vidro (o PDF), o trecho em y entre as bordas de pedra, a água de cada metade e o
# vidro fino
VIDROS = {"y": (928.5, 1106.9),
          "paredes": [{"x": (655.2, 664.2), "agua": [((656.0, 664.4), (9, 0))], "vidro": (655.2, 657.0)}],
          "cor": (24, 30, 30), "caixa": (630, 900, 730, 1135),
          # (17/11, usuário, com a imagem: "mantenha o vidro na extremidade e represente a parede com o tom de parede
          # onde está indicado") a de dentro é parede: o retângulo do PDF no cinza das paredes da planta
          "parede": (688.0, 696.9), "cor_parede": (80, 80, 80)}


def _local(out, mp, caixa):
    return mp.local(out, caixa) if mp.ref is not None else mp


def _apagar(out, m, q):
    """As letras de antes saem pelo piso de volta: a baixa frequência pelo inpaint do entorno (o Bege liso) e o grão
    do piso de logo acima (`desloc_y`); a máscara pega o antisserrilhado (`escuro`) com folga."""
    x0, y0, x1, y1 = m.reti(q["velho"])
    reg = np.ascontiguousarray(out[y0:y1, x0:x1])
    L = reg.astype(np.float32).mean(-1)
    marca = (L < float(np.median(L)) - (q["escuro"] if m.s < 1.5 else q["escuro_12k"])).astype(np.uint8)
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


def descricao_desce(out, mp, kalam=None, q=DESCE):
    guarda = EP._apagar
    EP._apagar = _apagar
    try:
        EP.descricao_sobe(out, mp, kalam, q)
    finally:
        EP._apagar = guarda


def vidros_piscina(out, mp, q=VIDROS):
    import instalacao_terreo_casad_1711 as ID
    m = _local(out, mp, q["caixa"])
    y0, y1 = q["y"]
    for p in q["paredes"]:
        for (xa, xb), d in p["agua"]:
            ID._remenda(out, m, (xa, y0, xb, y1), [d], None, 0)
    for p in q["paredes"]:
        va, vb = p["vidro"]
        CB.pintar(out, m, [((va, y0 - 0.6, vb, y1 + 0.6), "ret", q["cor"], 0)])
    print("    piscina: a barra grossa do extremo virou água, com o vidro fino (o da Casa C) na face de fora")


def parede_piscina(out, mp, q=VIDROS):
    m = _local(out, mp, q["caixa"])
    xa, xb = q["parede"]
    y0, y1 = q["y"]
    CB.pintar(out, m, [((xa, y0, xb, y1), "ret", q["cor_parede"], 0)])
    # as pontas do vidro fino de antes, que passavam 0,6 px para dentro das pedras de cima e de baixo: a pedra ao lado
    import instalacao_terreo_casad_1711 as ID
    ID._remenda(out, m, (xa, y0 - 1.2, xb, y0), [(0, -3)], None, 0)
    ID._remenda(out, m, (xa, y1, xb, y1 + 1.2), [(0, 3)], None, 0)
    print("    piscina: a de dentro é parede, no cinza das paredes")


PASSOS = ("descricao", "vidros", "parede")


def aplicar(img, mp, kalam=None, passos=PASSOS):
    out = img.copy()
    if "descricao" in passos:
        descricao_desce(out, mp, kalam)
    if "vidros" in passos:
        vidros_piscina(out, mp)
    if "parede" in passos:
        parede_piscina(out, mp)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("acao", choices=("final", "doze"))
    ap.add_argument("--opcao", default="AB")
    ap.add_argument("--entrada")
    ap.add_argument("--saida")
    ap.add_argument("--passos", default=",".join(PASSOS))
    a = ap.parse_args()
    passos = a.passos.split(",")
    fin = cv2.imread(a.entrada or str(FINAL))
    if a.acao == "final":
        cv2.imwrite(a.saida or str(FINAL), aplicar(fin, Mapa(), passos=passos))
        if not a.saida and "descricao" in passos:
            rots = json.loads(KALAM.read_text())
            for b in rots:
                if b["nome"] == DESCE["nome_kalam"]:
                    b["linhas"] = EP._linhas_kalam(DESCE)
            KALAM.write_text(json.dumps(rots, ensure_ascii=False, indent=1) + "\n")
        return
    from PIL import Image
    for op in a.opcao:
        f = Path(str(DOZE).format(op))
        img = cv2.imread(str(f))
        M = DF.afim_12k(fin, img)
        mp = Mapa(float(np.hypot(M[0, 0], M[1, 0])), (float(M[0, 2]), float(M[1, 2])))
        mp.ref = fin
        out = aplicar(img, mp, EP._kalam_global() if op == "B" else None, passos)
        dpi = int(round(out.shape[1] / (420 / 25.4)))
        dest = a.saida.format(op) if a.saida else str(f)
        Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB)).save(dest, quality=95, subsampling=0, dpi=(dpi, dpi))
        print(f"    {Path(dest).name}")


if __name__ == "__main__":
    main()

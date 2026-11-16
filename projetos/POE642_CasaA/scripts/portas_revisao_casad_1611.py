"""A revisão das portas do Térreo da Casa D (16/11, usuário: "Confira o contorno das portas também, para evitar que tenha
alguma mancha ao redor da porta. Confira também se a parede atrás da porta ela não está com algum dente, algum recorte
inapropriado. Não pode ter nenhuma mancha de arco da porta [...] Revise também as soleiras, onde tiver soleira tem que
colocar").

A conferência foi porta a porta contra o PDF (os 22 arcos da ARQ_PAREDE, os vãos brancos) e contra a imagem de entrada
(a parede que existia e sumiu perto de cada porta). O que entra aqui, no fim de `biblioteca_terreo_casad_1511.aplicar`
(depois dos rótulos, que também apagam e escrevem perto das portas):

- `PAREDES`: a face da parede atrás da folha, reta. A limpeza em volta da folha nova (`pedidos_terreo_casac_1311.portas`)
  comia 1 px da face ao longo da folha (a circulação da suíte 2, o banho 1, o pé da parede do banho gourmet) e deixava
  três dentes claros na parede de cima do lavabo: a coluna (ou a linha) volta ao cinza das paredes, na linha da face de
  antes e depois da folha.
- `MANCHAS`: o tracinho branco que a limpeza da porta do WC DCE deixava no piso do DCE, junto ao "DCE TÉRREO", e a fileira
  de pontinhos escuros no granito da despensa, acima do rótulo: saem (o piso em volta, por inpaint), só os px claros ou
  escuros demais para o piso (as letras ficam).
- `SOLEIRAS_CORRER`: as portas de correr do living para as duas circulações e as duas do banho master tinham a soleira do
  render borrada (um brilho branco no meio, uma faixa escura e a ponta da parede esfumada, em degradê): a soleira entra
  nítida no vão do PDF (ARQ_PAREDE, branco), no claro das soleiras das portas de giro, com as faces finas; a parede vai
  até a ponta dela no PDF (o marco cinza é parede). As folhas de correr ficam.
"""
import cv2
import numpy as np

PAREDE = (80, 80, 80)
# (caixa px [x0, y0, x1, y1), o que é): a parede volta ao cinza dela
PAREDES = [((2037, 1422, 2038, 1480), "circulação da suíte 2: a face da parede atrás da folha"),
           ((1198, 1552, 1199, 1604), "banho 1: a face da parede atrás da folha da porta do closet"),
           ((1553, 428, 1554, 439), "banho gourmet: o pé da parede abaixo da soleira"),
           ((2514, 899, 2515, 901), "adega: a ponta do tracejado do telhado na face da parede, junto à porta da entrada")]
# (caixa px, dy): o piso de `dy` px acima (a face da parede, fora dela, volta ao piso do hall)
PISOS = [((2515, 899, 2516, 901), -3)]
# a parede de cima do lavabo: na linha `y`, de x0 a x1, onde a linha de cima é parede, a de baixo também
LINHAS_PAREDE = [{"y": 1210, "x": (2453, 2516), "nome": "lavabo: os dentes claros na parede de cima da folha"}]
# (caixa px, "claro", "escuro" ou "ambos", limiar em relação à mediana do piso da caixa)
MANCHAS = [((2485, 575, 2490, 595), "claro", 45, "DCE: o tracinho branco junto ao rótulo"),
           ((2110, 594, 2152, 602), "ambos", 12, "despensa: os pontinhos acima do rótulo")]
# os vãos do PDF (px) das portas de correr com a soleira do render borrada; `parede`: as faixas (px) que voltam ao cinza
# das paredes até a ponta do PDF
SOLEIRAS_CORRER = [
    {"nome": "do living para a circulação da suíte 1", "vao": (1841.5, 1329.9, 1909.6, 1338.8),
     "parede": [(1839, 1330, 1842, 1339), (1909, 1330, 1912, 1339)]},
    {"nome": "do living para a circulação das suítes 2 e 3", "vao": (2242.1, 1329.9, 2310.2, 1338.8),
     "parede": [(2240, 1330, 2243, 1339), (2309, 1330, 2312, 1339)]},
    {"nome": "do closet para o banho master", "vao": (759.4, 1605.7, 774.3, 1655.8),
     "parede": [(760, 1603, 774, 1606)]},
    {"nome": "do banho master para o closet 2", "vao": (947.5, 1605.2, 956.5, 1655.3),
     "parede": [(948, 1603, 956, 1605)]},
]
# o claro das soleiras das portas de giro (`pedidos_terreo_casac_1311.portas`): a mediana do miolo da soleira da porta da
# circulação para a suíte 1 (px), as faces em `fio` dele
SOLEIRA = {"amostra": (1442, 1360, 1447, 1396), "fio": 0.74, "ss": 8}


def _soleira(out, r, cor, fio, ss):
    import biblioteca_terreo_casad_1511 as TD
    x0, y0, x1, y1 = r
    out = TD._poligono(out, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], tuple(v * fio for v in cor), ss)
    return TD._poligono(out, [(x0 + 0.8, y0 + 0.8), (x1 - 0.8, y0 + 0.8), (x1 - 0.8, y1 - 0.8), (x0 + 0.8, y1 - 0.8)],
                        cor, ss)


def _mancha(out, caixa, tipo, limiar):
    x0, y0, x1, y1 = caixa
    reg = np.ascontiguousarray(out[y0:y1, x0:x1])
    L = reg.astype(np.float32).mean(axis=2)
    med = float(np.median(L))
    m = {"claro": L > med + limiar, "escuro": L < med - limiar,
         "ambos": np.abs(L - med) > limiar}[tipo]
    m = cv2.dilate(m.astype(np.uint8) * 255, np.ones((2, 2), np.uint8))
    if m.any():
        out[y0:y1, x0:x1] = cv2.inpaint(reg, m, 2, cv2.INPAINT_TELEA)
    return int((m > 0).sum())


def aplicar(out):
    out = out.copy()
    feitos = []
    for (x0, y0, x1, y1), nome in PAREDES:
        out[y0:y1, x0:x1] = PAREDE
        feitos.append(nome)
    for (x0, y0, x1, y1), dy in PISOS:
        out[y0:y1, x0:x1] = out[y0 + dy:y1 + dy, x0:x1]
    for q in LINHAS_PAREDE:
        y, (a, b) = q["y"], q["x"]
        cima = np.abs(out[y - 1, a:b].astype(np.int16) - 80).max(axis=1) <= 4
        linha = out[y, a:b]
        linha[cima] = PAREDE
        feitos.append(q["nome"])
    for caixa, tipo, limiar, nome in MANCHAS:
        n = _mancha(out, caixa, tipo, limiar)
        feitos.append(f"{nome} ({n} px)")
    x0, y0, x1, y1 = SOLEIRA["amostra"]
    cor = tuple(float(v) for v in np.median(out[y0:y1, x0:x1].reshape(-1, 3), axis=0))
    for p in SOLEIRAS_CORRER:
        for a0, b0, a1, b1 in p["parede"]:
            out[b0:b1, a0:a1] = PAREDE
        out = _soleira(out, p["vao"], cor, SOLEIRA["fio"], SOLEIRA["ss"])
    feitos.append(f"{len(SOLEIRAS_CORRER)} soleiras de correr nítidas no vão do PDF ("
                  f"{', '.join(p['nome'] for p in SOLEIRAS_CORRER)})")
    print("    portas (revisão): " + "; ".join(feitos))
    return out

# A revisão da Casa D de 28/10 (os 7 itens) aplicada sobre as finais aprovadas. Uso: python3 aplica7_d.py <pasta de saída>
import sys, cv2, numpy as np
sys.path.insert(0, ".")
import final3840_casad as D, final3840_casab as F
D.contexto_d()
R = "../../POE642_CasaD/renders/"
S = sys.argv[1]
# Térreo
Q = F.Quadro("Terreo")
im = cv2.imread(R + "POE642_CasaD_PH_Terreo_final_rotulos.png")
antes = cv2.imread("/tmp/poe642_casad_etapas/final3840/Terreo_soleiras.png")
out = D.projecoes_terreo_d(Q, im, so_pisos=True)
out = D.restos_folha_td(Q, out, antes)
out = D.hall_porta_td(Q, out)
d = np.abs(out.astype(int) - im.astype(int)).max(axis=2) > 0
print("Térreo: px mudados", int(d.sum()))
cv2.imwrite(S + "/d_terreo_7.png", out)
# Subsolo
Q = F.Quadro("Subsolo")
im = cv2.imread(R + "POE642_CasaD_PH_Subsolo_final_rotulos.png")
out = D.vao_sem_soleira_td(Q, im)
out = D.parede_patio_sd(Q, out, D.pegada_subsolo(Q))
d = np.abs(out.astype(int) - im.astype(int)).max(axis=2) > 0
print("Subsolo: px mudados", int(d.sum()))
cv2.imwrite(S + "/d_subsolo_7.png", out)

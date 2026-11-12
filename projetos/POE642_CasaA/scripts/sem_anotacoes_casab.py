"""A planta do Térreo da Casa B sem os textos, para o 12K (`ampliacao_12k_terreo_casab.py`): os passos de
`pedidos_terreo_casab_1211.py` de `escadas` ao fim, sem as anotações (os triângulos e as descrições das escadas e da
entrada, `terreo_casaa_1011.ANOTAR`) e sem desenhar os rótulos (`ROTULOS_TB["desenhar"]`; os antigos saem como na final).

  python3 sem_anotacoes_casab.py <passo_bege_escadas.png> <saída> <pasta dos passos>
"""
import sys
from pathlib import Path
import cv2
sys.path.insert(0, str(Path(__file__).resolve().parent))
import terreo_casaa_1011 as TC
import pedidos_terreo_casab_1211 as P
TC.ANOTAR["sim"] = False
P.ROTULOS_TB["desenhar"] = False
antes, saida, passos = sys.argv[1:4]
out = P.correcoes(cv2.imread(antes), de="escadas", salvar_passos=passos)
cv2.imwrite(saida, out)
print(saida)

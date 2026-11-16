"""As cortinas do Térreo da Casa D no padrão das Casas A, B e C (16/11, usuário: "Precisamos adotar o padrão das
cortinas que eu tenho feito nas casas A, B e C, tá? Altera e deixe num formato bem visível as cortinas").

O padrão é o da Casa C (`pedidos_terreo_casac_1311.cortinas`, a C4 que veio da Casa B): o linho em ondas
(`regras_terreo_casab_1311.cortina_desenho`, o PNG da biblioteca com o trilho grafite do lado do vidro) em cada janela
dos trechos do PDF, os da mesma janela unidos, até a ponta da parede de cada lado do vão e 0,15 m além dela do lado de
dentro onde a parede segue na linha ("Pode deixar a cortina ultrapassar um pouco as laterais da janela"); o pano e o
trilho de antes saem (o piso logo de dentro, em espelho). Aqui a mesma função, no quadro da Casa D, para ficar bem visível:
o pano mais fundo (`prof_px`, 13 px, 0,22 m, contra 9), o linho um tom abaixo (`tom`) e a sombra inteira (a curta e a
macia, como as cortinas do estar da Casa C de 15/11); e a da suíte 3 (nota do cliente "Colocar cortina"; fora dos
trechos do PDF), no mesmo desenho.
"""
import contextlib
import io

import numpy as np

CORTINAS_D = {"tom": 0.82, "prof_px": 13.0,
              # a cortina da suíte 3 (`biblioteca_terreo_casad_1511.CORTINA_S3`: o vidro à direita, x da face, o trecho)
              "extra": [("v", "direita", 2504.0, 1352.0, 1493.0)]}


@contextlib.contextmanager
def _visivel(q=CORTINAS_D):
    """O desenho da C4 com o linho `tom` e a sombra inteira (`pedidos_terreo_casac_1311.cortinas` pousa com
    `SOMBRAS["movel"][1:]`, só a curta)."""
    import biblioteca_terreo_casaa_1211 as BT
    import regras_terreo_casab_1311 as RT
    orig, somb, tb = RT.cortina_desenho, BT.SOMBRAS["movel"], RT.CORTINAS_TB
    RT.CORTINAS_TB = dict(tb, prof_px=q["prof_px"])        # o pano mais fundo (0,22 m), para as ondas lerem

    def desenho(it, qc=None):
        P, cx, cy, wt, ht = orig(it, qc or RT.CORTINAS_TB)
        P = P.copy()
        P[..., :3] *= q["tom"]
        return P, cx, cy, wt, ht
    RT.cortina_desenho = desenho
    BT.SOMBRAS["movel"] = [somb[0]] + list(somb)
    try:
        yield desenho
    finally:
        RT.cortina_desenho = orig
        BT.SOMBRAS["movel"] = somb
        RT.CORTINAS_TB = tb


def aplicar(Q, out, par=None, q=CORTINAS_D):
    import biblioteca_1pav_casaa_1211 as B1
    import biblioteca_terreo_casaa_1211 as BT
    import pedidos_terreo_casac_1311 as PT
    log = io.StringIO()
    with _visivel(q) as desenho:
        with contextlib.redirect_stdout(log):
            out = PT.cortinas(Q, out)
        o_ = out.astype(np.float32)
        for o, v, ex, t0, t1 in q["extra"]:
            P, cx, cy, wt, ht = desenho({"o": o, "v": v, "ex": ex, "t0": t0, "t1": t1})
            o_ = BT.pousar(o_, P, cx, cy, wt, ht, 0.0, BT.SOMBRAS["movel"], B1.PX_M)
        out = np.clip(np.round(o_), 0, 255).astype(np.uint8)
    linha = [l_.strip() for l_ in log.getvalue().splitlines() if "cortinas:" in l_]
    print(f"    {linha[0] if linha else 'cortinas: (sem trechos)'}; o padrão da Casa C, o linho {q['tom']:.2f} e a sombra "
          f"inteira; mais a da suíte 3")
    return out

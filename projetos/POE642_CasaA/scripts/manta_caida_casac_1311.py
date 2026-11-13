"""A manta de tricô grosso jogada e caída nos pés da cama (13/11, referência do usuário: "Não ficou bom a manta assim
não. Ela fica caída"): amontoada solta sobre os pés, com as dobras grandes e a borda de cima enrolada e ondulada,
caindo pela beirada do pé e de um lado (em planta, a faixa estreita além do colchão, com as ondas das pregas que descem)
e a sombra curta no piso. A cama volta num PNG com margem `pad` igual nos 4 lados (o centro não muda)."""
import cv2, numpy as np, sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
import camas_casac_1311 as C

PAD = 0.06                 # margem (fração da altura da cama) para a parte caída e a sombra no piso
CAI = 0.026                # quanto a manta caída aparece além do colchão, em planta (fração da altura)
ONDA = 0.10                # o passo das pregas que descem pela beirada (fração da largura)
PONTO = 0.044              # o ponto do tricô (fração da altura: o mesmo tamanho na king, na casal e na solteiro)
LUZ = np.float32([0.45, -0.55, 0.70])                                 # do alto à direita (x para a direita, y para baixo)


def borda_de_cima(u, rng):
    """A borda de cima da manta (v em função de u, lado esquerdo): atravessa os pés subindo para o lado onde cai, com
    ondas largas (a manta amontoada) e um tremido."""
    f1, f2 = rng.uniform(0, 2 * np.pi, 2)
    return 0.665 + 0.135 * np.clip(u, 0, 1) ** 1.3 + 0.024 * np.sin(2 * np.pi * 1.3 * u + f1) + 0.007 * np.sin(2 * np.pi * 3.1 * u + f2)


def _over(dst, rgb, a):
    ad = dst[..., 3] / 255
    ao = a + ad * (1 - a)
    c = (rgb * a[..., None] + dst[..., :3] * (ad * (1 - a))[..., None]) / np.maximum(ao, 1e-6)[..., None]
    dst[..., :3] = np.where(ao[..., None] > 0, c, dst[..., :3])
    dst[..., 3] = ao * 255
    return dst


def manta_caida(P, enfeite, lado="esq", semente=7):
    H, W = P.shape[:2]
    p = int(round(PAD * H))
    Q = np.zeros((H + 2 * p, W + 2 * p, 4), np.float32)
    Q[p:p + H, p:p + W] = P
    Hc, Wc = Q.shape[:2]
    rng = np.random.default_rng(semente)
    yy, xx = np.mgrid[0:Hc, 0:Wc].astype(np.float32)
    v = (yy - p) / H
    xe = (xx - p) if lado == "esq" else (W - 1 - (xx - p))             # x espelhado: a forma, não a luz
    u = xe / W
    cama = Q[..., 3] > 127
    d_fora = cv2.distanceTransform((~cama).astype(np.uint8), cv2.DIST_L2, 5)
    d_dentro = cv2.distanceTransform(cama.astype(np.uint8), cv2.DIST_L2, 5)
    # a forma sobre a cama: abaixo da borda de cima, até a ponta solta (arredondada) no lado oposto
    vt = borda_de_cima(u, rng)
    u_fim = 0.91 - 0.20 * np.clip((v - 0.84) / 0.24, 0, 1) ** 1.6 - 0.05 * np.clip(1 - (v - vt) / 0.05, 0, 1)
    M = (v >= vt) & (u <= u_fim)
    M = cv2.GaussianBlur(M.astype(np.float32), (0, 0), 0.012 * H) > 0.5
    # a parte caída: além do colchão (no pé e no lado), com as ondas das pregas
    t = np.where(v > 0.97, np.clip(u, 0, None) * W, 0) + np.where(u < 0.03, np.clip(1 - v, 0, None) * H, 0)
    crista = np.cos(2 * np.pi * t / (ONDA * H) + 0.8 + 0.7 * np.sin(2 * np.pi * t / (3.7 * ONDA * H)))
    cai = CAI * H * (0.72 + 0.28 * crista)
    caida = M & ~cama & (d_fora < cai)
    caida = (cv2.GaussianBlur(caida.astype(np.float32), (0, 0), 0.006 * H) > 0.5) & ~cama & M   # as ondas arredondadas
    sobre = M & cama
    manta = sobre | caida
    # o relevo (px): as dobras irradiando do canto onde cai, a borda de cima enrolada e a queda na beirada
    phi = np.arctan2(v - 1.08, u + 0.08)
    r = np.hypot(v - 1.08, u + 0.08)
    dobra = (0.55 * np.sin(8 * phi + 0.4) + 0.30 * np.sin(15 * phi + 1.3) + 0.20 * np.sin(23 * phi + 2.2)) * np.clip(r / 0.2, 0, 1)
    rolo = np.exp(-((v - vt - 0.030) / 0.024) ** 2)
    beira = np.clip(d_dentro / (0.03 * H), 0, 1) ** 0.5                # a manta desce na beirada do colchão
    bolo = sum(a * np.exp(-((u - uc) ** 2 + ((v - vc) * 1.6) ** 2) / (2 * rr ** 2))
               for uc, vc, rr, a in ((0.22, 0.82, 0.11, 1.0), (0.58, 0.90, 0.10, 0.8), (0.06, 0.95, 0.07, 0.6)))
    alt = (0.016 * dobra * (0.6 + 0.4 * bolo) + 0.026 * rolo + 0.022 * bolo + 0.016 * beira) * H
    alt = cv2.GaussianBlur(alt.astype(np.float32), (0, 0), 0.012 * H)
    # o tricô: colunas de pontos em V, levemente giradas e entortadas pelas dobras
    s = PONTO * H
    G = 1.5
    T = C.tricô(int(Hc * G), int(Wc * G), s)
    R = cv2.getRotationMatrix2D((Wc * G / 2, Hc * G / 2), -8 if lado == "esq" else 8, 1.0)
    T = cv2.warpAffine(T, R, (int(Wc * G), int(Hc * G)), borderMode=cv2.BORDER_REFLECT)
    gy, gx = np.gradient(alt)
    o = (G - 1) / 2
    rel = cv2.remap(T, (xx + Wc * o + 0.6 * gx * s / 2).astype(np.float32), (yy + Hc * o + 0.6 * gy * s / 2).astype(np.float32),
                    cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    z = alt + 0.075 * s * rel
    zy, zx = np.gradient(cv2.GaussianBlur(z, (0, 0), 0.7))
    n = np.dstack([-zx, -zy, np.ones_like(z)])
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    L = LUZ / np.linalg.norm(LUZ)
    lamb = np.clip(n @ L, 0, 1) / L[2]
    luz = np.clip(0.40 + 0.60 * lamb, 0, 1.12)
    luz *= 0.90 + 0.10 * rel                                           # o fundo entre as laçadas, mais escuro
    # a parte caída: quase vertical, na sombra; as cristas das pregas mais claras, escurecendo para baixo
    luz_c = (0.70 + 0.09 * crista) * (0.93 + 0.07 * rel) * (1 - 0.22 * np.clip(d_fora / cai, 0, 1))
    luz = np.where(caida, luz_c, luz)
    cor = np.clip(np.float32(C.TONS[enfeite])[None, None] * luz[..., None], 0, 255)
    # as sombras: da manta no edredom e no piso (a luz do alto à direita: a sombra cai para baixo e para a esquerda)
    sm = cv2.GaussianBlur(manta.astype(np.float32), (0, 0), 0.010 * H)
    sm = np.roll(np.roll(sm, int(0.010 * H), axis=0), -int(0.008 * H), axis=1)
    Q[..., :3] *= (1 - 0.30 * sm * (cama & ~manta))[..., None]
    sp = cv2.GaussianBlur(manta.astype(np.float32), (0, 0), 0.014 * H)
    sp = np.roll(np.roll(sp, int(0.012 * H), axis=0), -int(0.010 * H), axis=1)
    piso = np.zeros((Hc, Wc, 4), np.float32)
    piso[..., 3] = 255 * 0.36 * sp * (~manta)
    Q = _over(piso, Q[..., :3], Q[..., 3] / 255)
    ab = cv2.GaussianBlur(manta.astype(np.float32), (0, 0), 0.7)
    Q = _over(Q, cor, np.clip(ab * 1.4, 0, 1) * (ab > 0.02))
    return np.clip(Q, 0, 255), p

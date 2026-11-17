"""Teste das texturas dos materiais do projeto no Meshy (17/11, usuário: "eu quero testar as texturas dos materiais com
esse aplicativo"): a Retexture API (`POST /openapi/v1/retexture`, docs.meshy.ai/en/api/retexture) numa placa de piso
de 1 x 1 m x 2 cm (GLB com as UVs de 0 a 1 no tampo), cada material com a foto de referência do projeto
(`projetos/_texturas/originais`, `image_style_url` em data URI) e a descrição em inglês (`text_style_prompt`; com a
imagem, o Meshy segue a imagem), o PBR ligado (base color, roughness, metallic, normal). O modelo e as imagens vão no
próprio pedido (data URI), sem hospedar nada.

A chave: um segredo de rede do ambiente para api.meshy.ai (Authorization: Bearer); o proxy da sessão o põe no pedido,
o script manda um valor qualquer no lugar.

  python3 teste_texturas_meshy.py kit                         # a placa e as referências, sem chamar o Meshy
  python3 teste_texturas_meshy.py saldo                       # os créditos da conta
  python3 teste_texturas_meshy.py rodar [--materiais a,b]     # ~10 créditos por material
  python3 teste_texturas_meshy.py folha                       # a comparação (referência x Meshy) dos já baixados
"""
import argparse
import base64
import json
import struct
import sys
import time
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
ORIG = RAIZ / "_texturas/originais"
SAIDA = RAIZ / "_texturas/meshy"
API = "https://api.meshy.ai/openapi/v1"
CABECALHO = {"Authorization": "Bearer chave-no-proxy", "Content-Type": "application/json"}

MATERIAIS = {
    "bege_bahia": ("bege_bahia.png", "Bege Bahia limestone floor tile, warm cream beige with soft fossil spots, honed"),
    "travertino": ("travertino.webp", "Roman travertine floor tile, light ivory with horizontal veins and small pores"),
    "dekton_danae": ("dekton_danae_cosentino_KAC.jpg", "Dekton Danae by Cosentino, warm greige sintered stone, "
                                                       "subtle cloudy texture, matte"),
    "granito_marrom": ("granito_marrom.png", "Brown granite floor tile, tobacco brown with dark grains, polished"),
    "quartzito_aura": ("quartzito_aura.jpg", "Aura quartzite slab, light warm white with soft beige veining"),
    "pedra_portuguesa": ("pedra_portuguesa.webp", "Portuguese stone mosaic pavement, small irregular beige stones"),
    "vinilico_carvalho": ("amostra_vinilico_carvalho_1111.png", "Oak vinyl plank floor, natural light oak, matte"),
}


# ----------------------------------------------------------------------------------------------------------------------
def placa_glb(lado=1.0, esp=0.02):
    """Uma caixa (lado x lado x esp, m; Y para cima) em GLB: o tampo com as UVs de 0 a 1, as faces dos lados em tiras
    finas da mesma imagem."""
    h, e = lado / 2, esp
    faces = [  # (4 vértices em sentido anti-horário visto de fora, normal, uvs)
        ([(-h, e, h), (h, e, h), (h, e, -h), (-h, e, -h)], (0, 1, 0), [(0, 1), (1, 1), (1, 0), (0, 0)]),
        ([(-h, 0, -h), (h, 0, -h), (h, 0, h), (-h, 0, h)], (0, -1, 0), [(0, 0), (1, 0), (1, 1), (0, 1)]),
        ([(-h, 0, h), (h, 0, h), (h, e, h), (-h, e, h)], (0, 0, 1), [(0, 1), (1, 1), (1, 0.98), (0, 0.98)]),
        ([(h, 0, -h), (-h, 0, -h), (-h, e, -h), (h, e, -h)], (0, 0, -1), [(1, 0.02), (0, 0.02), (0, 0), (1, 0)]),
        ([(h, 0, h), (h, 0, -h), (h, e, -h), (h, e, h)], (1, 0, 0), [(1, 1), (1, 0), (0.98, 0), (0.98, 1)]),
        ([(-h, 0, -h), (-h, 0, h), (-h, e, h), (-h, e, -h)], (-1, 0, 0), [(0, 0), (0, 1), (0.02, 1), (0.02, 0)]),
    ]
    pos, nor, uv, idx = [], [], [], []
    for vs, n, us in faces:
        b = len(pos)
        pos += vs
        nor += [n] * 4
        uv += us
        idx += [b, b + 1, b + 2, b, b + 2, b + 3]
    P = np.float32(pos)
    N = np.float32(nor)
    T = np.float32(uv)
    I = np.uint16(idx)
    blob = b""
    vistas = []
    for arr, alvo in ((P, 34962), (N, 34962), (T, 34962), (I, 34963)):
        while len(blob) % 4:
            blob += b"\0"
        vistas.append({"buffer": 0, "byteOffset": len(blob), "byteLength": arr.nbytes, "target": alvo})
        blob += arr.tobytes()
    while len(blob) % 4:
        blob += b"\0"
    gltf = {
        "asset": {"version": "2.0", "generator": "teste_texturas_meshy"},
        "scene": 0, "scenes": [{"nodes": [0]}], "nodes": [{"mesh": 0, "name": "placa"}],
        "meshes": [{"name": "placa", "primitives": [{"attributes": {"POSITION": 0, "NORMAL": 1, "TEXCOORD_0": 2},
                                                     "indices": 3, "material": 0}]}],
        "materials": [{"name": "piso", "pbrMetallicRoughness": {"baseColorFactor": [0.8, 0.8, 0.8, 1.0],
                                                                 "metallicFactor": 0.0, "roughnessFactor": 0.8}}],
        "buffers": [{"byteLength": len(blob)}],
        "bufferViews": vistas,
        "accessors": [
            {"bufferView": 0, "componentType": 5126, "count": len(P), "type": "VEC3",
             "min": P.min(0).tolist(), "max": P.max(0).tolist()},
            {"bufferView": 1, "componentType": 5126, "count": len(N), "type": "VEC3"},
            {"bufferView": 2, "componentType": 5126, "count": len(T), "type": "VEC2"},
            {"bufferView": 3, "componentType": 5123, "count": len(I), "type": "SCALAR"}],
    }
    js = json.dumps(gltf, separators=(",", ":")).encode()
    while len(js) % 4:
        js += b" "
    corpo = struct.pack("<II", len(js), 0x4E4F534A) + js + struct.pack("<II", len(blob), 0x004E4942) + blob
    return struct.pack("<III", 0x46546C67, 2, 12 + len(corpo)) + corpo


def referencia(nome, lado=1024):
    """A foto do material, recortada ao quadrado do meio e reduzida a `lado` px, em JPG."""
    arq, _ = MATERIAIS[nome]
    img = cv2.imread(str(ORIG / arq), cv2.IMREAD_COLOR)
    if img is None:                                       # webp sem suporte no OpenCV: pelo PIL
        from PIL import Image
        img = cv2.cvtColor(np.asarray(Image.open(ORIG / arq).convert("RGB")), cv2.COLOR_RGB2BGR)
    h, w = img.shape[:2]
    m = min(h, w)
    img = img[(h - m) // 2:(h - m) // 2 + m, (w - m) // 2:(w - m) // 2 + m]
    if m > lado:
        img = cv2.resize(img, (lado, lado), interpolation=cv2.INTER_AREA)
    return img


def _uri(dados, mime):
    return f"data:{mime};base64," + base64.b64encode(dados).decode()


def kit():
    SAIDA.mkdir(parents=True, exist_ok=True)
    (SAIDA / "placa.glb").write_bytes(placa_glb())
    for nome in MATERIAIS:
        cv2.imwrite(str(SAIDA / f"ref_{nome}.jpg"), referencia(nome), [cv2.IMWRITE_JPEG_QUALITY, 92])
    print(f"    {SAIDA}: placa.glb e {len(MATERIAIS)} referências ({', '.join(MATERIAIS)}); ~{10 * len(MATERIAIS)} "
          "créditos para rodar todos")


# ----------------------------------------------------------------------------------------------------------------------
def _req(metodo, rota, corpo=None):
    import requests
    r = requests.request(metodo, f"{API}{rota}", headers=CABECALHO, json=corpo, timeout=120)
    if r.status_code >= 400:
        raise SystemExit(f"Meshy {metodo} {rota}: {r.status_code} {r.text[:400]}")
    return r.json()


def saldo():
    print(f"    créditos: {_req('GET', '/balance')}")


def rodar(nomes):
    import requests
    SAIDA.mkdir(parents=True, exist_ok=True)
    modelo = _uri(placa_glb(), "application/octet-stream")
    tarefas = {}
    for nome in nomes:
        ok, buf = cv2.imencode(".jpg", referencia(nome), [cv2.IMWRITE_JPEG_QUALITY, 92])
        corpo = {"model_url": modelo, "image_style_url": _uri(buf.tobytes(), "image/jpeg"),
                 "text_style_prompt": MATERIAIS[nome][1], "enable_pbr": True, "enable_original_uv": True,
                 "target_formats": ["glb"]}
        tarefas[nome] = _req("POST", "/retexture", corpo)["result"]
        print(f"    {nome}: tarefa {tarefas[nome]}")
    feitas = {}
    while len(feitas) < len(tarefas):
        time.sleep(10)
        for nome, tid in tarefas.items():
            if nome in feitas:
                continue
            t = _req("GET", f"/retexture/{tid}")
            if t["status"] in ("SUCCEEDED", "FAILED", "CANCELED"):
                feitas[nome] = t
                print(f"    {nome}: {t['status']} ({t.get('consumed_credits', '?')} créditos)"
                      + (f" {t.get('task_error')}" if t["status"] != "SUCCEEDED" else ""))
    for nome, t in feitas.items():
        if t["status"] != "SUCCEEDED":
            continue
        pasta = SAIDA / nome
        pasta.mkdir(exist_ok=True)
        (pasta / "tarefa.json").write_text(json.dumps(t, indent=1))
        for mapa, url in (t.get("texture_urls") or [{}])[0].items():
            (pasta / f"{mapa}.png").write_bytes(requests.get(url, timeout=120).content)
        if (t.get("model_urls") or {}).get("glb"):
            (pasta / "placa.glb").write_bytes(requests.get(t["model_urls"]["glb"], timeout=120).content)
    folha()


def folha(lado=360):
    """Uma linha por material: a referência do projeto, o base color do Meshy, a rugosidade e a normal."""
    linhas = []
    for nome in MATERIAIS:
        pasta = SAIDA / nome
        if not (pasta / "base_color.png").exists():
            continue
        quadros = [referencia(nome)]
        for mapa in ("base_color", "roughness", "normal"):
            im = cv2.imread(str(pasta / f"{mapa}.png"))
            quadros.append(im if im is not None else np.full((lado, lado, 3), 255, np.uint8))
        quadros = [cv2.resize(q, (lado, lado), interpolation=cv2.INTER_AREA) for q in quadros]
        faixa = np.full((34, 4 * lado + 30, 3), 255, np.uint8)
        cv2.putText(faixa, f"{nome}: referencia | Meshy base color | roughness | normal", (6, 24),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (30, 30, 30), 1, cv2.LINE_AA)
        corpo = np.hstack(sum([[q, np.full((lado, 10, 3), 255, np.uint8)] for q in quadros], [])[:-1])
        linhas += [faixa, cv2.copyMakeBorder(corpo, 0, 16, 0, faixa.shape[1] - corpo.shape[1],
                                             cv2.BORDER_CONSTANT, value=(255, 255, 255))]
    if not linhas:
        print("    nada baixado ainda")
        return
    cv2.imwrite(str(SAIDA / "comparacao.jpg"), np.vstack(linhas), [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"    {SAIDA / 'comparacao.jpg'}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("acao", choices=("kit", "saldo", "rodar", "folha"))
    ap.add_argument("--materiais", default=",".join(MATERIAIS))
    a = ap.parse_args()
    if a.acao == "kit":
        kit()
    elif a.acao == "saldo":
        saldo()
    elif a.acao == "rodar":
        rodar([m for m in a.materiais.split(",") if m])
    else:
        folha()


if __name__ == "__main__":
    sys.exit(main())

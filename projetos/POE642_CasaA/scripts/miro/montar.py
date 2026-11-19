import json,re,difflib,unicodedata,sys
IT="/tmp/claude-0/-home-user/610cde13-fae4-5134-867b-524dc247ebb6/scratchpad/miro/orig/"
q=json.load(open("alvos.json"))
G=[("G1","Colocar a seta em todas as escadas e a descrição",["seta em todas as escadas","seta e descricao em todas","seta e a descricao em todas"]),
   ("G2","Fazer as mesmas mudanças que foram apontadas no subsolo da casa A e que cabem para essa casa",["mesmas mudancas que foram apontadas"]),
   ("G3","Tirar o contorno dos mobiliários",["contorno dos mobiliarios"]),
   ("G4","Geral: Não precisa representar os armários inferiores ou superiores.",["armarios inferiores ou superiores"]),
   ("G5","Representar as claraboias apenas com as linhas de fora, sem o X no meio para ficar mais discreto. Usar um tom cinza e as linhas mais fininhas. Padronizar para as outras plantas que tiverem claraboia.",["claraboias apenas com as linhas","outras plantas que tiverem claraboia"]),
   ("G6","OBS GERAL: No terreno não precisa representar muitas árvores, pra não ficar muito poluído e acabar afetando um futuro projeto de paisagismo. Representar arbustos que são menores.",["muitas arvores"]),
   ("G7","Melhorar representação das portas de giro. Encostar nas paredes.",["portas de giro"])]
def norm(s):
    s=unicodedata.normalize("NFKD",s.lower()); s="".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+"," ",re.sub(r"[^a-z0-9 ]+"," ",s)).strip()
def sim(a,b):
    a,b=norm(a),norm(b)
    if not a or not b: return 0
    if len(a)>12 and len(b)>12 and (a in b or b in a): return 0.95
    return difflib.SequenceMatcher(None,a,b).ratio()
def geral(t):
    n=norm(t)
    for gid,_,ch in G:
        if any(c in n for c in ch): return gid
MANUAL=json.load(open("manual.json")) if len(sys.argv)<2 or sys.argv[1]!="rel" else {}
saida={}
rel=[]
for k,notas in q.items():
    its=json.load(open(IT+k+".json"))["itens"]
    grupos={}
    FORCA={3458764689998091936:"bancada da área de serviço",3458764689998092101:"bancada da área de serviço",
           3458764689998092912:"bancada de trás da área gourmet"}
    def perto(n):
        if n["id"] in FORCA:
            j=[j for j,it in enumerate(its) if FORCA[n["id"]] in it["fala"]]
            if j: return j[0]
        """o item da frente que trata deste post-it: entre os de texto parecido, o mais perto dele na planta"""
        alvo=(n["alvos"] or [n["no_post_it"]])[0]
        cands=[]
        for j,it in enumerate(its):
            s_=max(sim(n["text"],f) for f in it["fala"].replace("[sem o texto literal]","").split(" / "))
            if s_>=0.5 and it.get("pontos"):
                d=min(((a-alvo[0])**2+(b-alvo[1])**2)**.5 for a,b in it["pontos"])
                cands.append((d,-s_,j))
        if not cands: return None
        smax=max(-c[1] for c in cands)
        cands=sorted(c for c in cands if -c[1]>=smax-0.25)
        return cands[0][2] if cands[0][0]<350 else None
    for n in notas:
        g=geral(n["text"])
        jp=None if g else perto(n)
        chave=g or (norm(n["text"]),jp)
        grupos.setdefault(chave,{"g":g,"textos":[],"pontos":[],"ids":[],"jp":jp})
        gr=grupos[chave]
        if n["text"] not in gr["textos"]: gr["textos"].append(n["text"])
        gr["pontos"]+= n["alvos"] or [n["no_post_it"]]
        gr["ids"].append(n["id"])
    lst=[]
    usados=set()
    for chave,gr in grupos.items():
        fala=gr["textos"][0] if not gr["g"] else gr["textos"][0]
        best=(0,None)
        for j,it in enumerate(its):
            for f in it["fala"].replace("[sem o texto literal]","").split(" / "):
                s=sim(fala,f)
                if s>best[0]: best=(s,j)
        if gr.get("jp") is not None:
            best=(max(best[0],0.9),gr["jp"])
        man=MANUAL.get(f"{k}|{norm(fala)[:60]}")
        item={"fala":fala,"pontos":[[round(x),round(y)] for x,y in gr["pontos"]],"miro_ids":[str(i) for i in gr["ids"]],"geral":bool(gr["g"]),"status":"feito"}
        if gr["g"]: item["g"]=gr["g"]
        if man is not None and isinstance(man,dict) and "usar" in man:
            j=[j for j,it in enumerate(its) if man["usar"].lower() in it["fala"].lower()]
            best=(1.0,j[0]) if j else best; man=None
        if man is not None and isinstance(man,dict):
            item.update(man)
        elif man is not None and isinstance(man,int):
            best=(1.0,man)
        if "como" not in item:
            if best[0]>=0.6 or (man is not None and isinstance(man,int)):
                it=its[best[1]]; usados.add(best[1])
                for c in ("como","conferir","status","obs"):
                    if it.get(c): item[c]=it[c]
                item["casou"]=round(best[0],2)
            elif gr["g"]:
                continue                              # o geral sem texto da planta: vale o padrão de planos.json
            else:
                rel.append((k,fala,best[0],its[best[1]]["fala"] if best[1] is not None else ""))
                item["como"]="(A ESCREVER)"
        lst.append(item)
    # ordem: de cima para baixo, esquerda para direita (pelo 1º ponto), gerais no fim
    lst.sort(key=lambda z:(z["geral"],round(z["pontos"][0][1]/120),z["pontos"][0][0]))
    textos=[n["text"] for n in notas]+[g[1] for g in G]
    fora=[dict(it,status="fora_do_miro") for j,it in enumerate(its) if j not in usados and not it.get("geral")
          and max(sim(it["fala"].replace("[sem o texto literal]",""),t) for t in textos)<0.85]
    saida[k]={"itens":lst,"fora_do_miro":fora}
if len(sys.argv)>1 and sys.argv[1]=="rel":
    for k,f,s,c in rel: print(f"{k}|{norm(f)[:60]}  ({s:.2f})\n   M: {f[:140]}\n   I: {c[:140]}")
    print(len(rel))
else:
    json.dump(saida,open("itens_miro.json","w"),ensure_ascii=False,indent=1)
    for k,v in saida.items(): print(k,len(v["itens"]),"itens;",sum(1 for i in v["itens"] if i["como"]=="(A ESCREVER)"),"a escrever;",len(v["fora_do_miro"]),"fora do Miro")

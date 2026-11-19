import json,re
w=json.load(open("widgets.json"))
F=3458764689445751310
ch=[o for o in w if o["parent"]==F]
IM={"A_Subsolo":3458764689445933983,"A_Terreo":3458764689445934471,"A_1Pavimento":3458764689445934839,
    "B_Subsolo":3458764689452528595,"B_Terreo":3458764689452680078,"C_Subsolo":3458764689459593757,"C_Terreo":3458764689459593923,
    "D_Subsolo":3458764689459781599,"D_Terreo":3458764689459942971,"E_Subsolo":3458764689459943452,"E_Terreo":3458764689460100160,"E_1Pavimento":3458764689538273764}
W={o["id"]:o for o in w}
bands=[("A",-14000,14000),("B",14000,44000),("C",44000,78000),("D",78000,109000),("E",109000,190000)]
def casa(y):
    for c,a,b in bands:
        if a<=y<b: return c
st=[o for o in ch if o["type"] in("sticker","shape") and o["text"]]
res={k:[] for k in IM}; sobra=[]
for o in st:
    c=casa(o["y"]); best=None
    for k,i in IM.items():
        if k[0]!=c: continue
        im=W[i]; dx=max(abs(o["x"]-im["x"])-im["w"]/2,0); dy=max(abs(o["y"]-im["y"])-im["h"]/2,0); dd=(dx*dx+dy*dy)**.5
        if best is None or dd<best[0]: best=(dd,k)
    if best: res[best[1]].append((o,best[0]))
    else: sobra.append(o)
cor=lambda o:"ROSA" if "16620263" in (o.get("style") or "") else ""
out={}
for k,l in res.items():
    im=W[IM[k]]
    l.sort(key=lambda z:(z[0]["y"],z[0]["x"]))
    out[k]=[{"id":o["id"],"text":o["text"],"x":o["x"],"y":o["y"],"w":o["w"],"h":o["h"],"cor":cor(o),"fora":round(dd)} for o,dd in l]
    print("==",k,len(l),"img",round(im["x"]),round(im["y"]),round(im["w"]),round(im["h"]))
json.dump({"planos":out,"imagens":{k:W[i] for k,i in IM.items()}},open("notas_por_planta.json","w"),ensure_ascii=False,indent=1)
print("sobra",len(sobra),[o["text"][:60] for o in sobra])

import json,numpy as np,cv2
P="/home/user/conrado-3d-masterclass/projetos/"
w=json.load(open("widgets.json")); W={o["id"]:o for o in w}
q=json.load(open("notas_por_planta.json")); R=json.load(open("registro.json"))
F=3458764689445751310
lines=[o for o in w if o["type"]=="line" and o["parent"]==F]
def ponta(e):
    """(x,y) absoluto da ponta de uma linha."""
    if e.get("widget"):
        t=W.get(int(e["widget"]["id"]))
        if not t: return None,None
        u,v=e.get("point",{}).get("x",.5),e.get("point",{}).get("y",.5)
        return (t["x"]-t["w"]/2+u*t["w"], t["y"]-t["h"]/2+v*t["h"]), int(e["widget"]["id"])
    p=e.get("point"); return ((p["x"],p["y"]) if p else None), None
alvos={}
for k,notas in q["planos"].items():
    im=q["imagens"][k]; M=np.array(R[k]["M"]); Wm,Hm=R[k]["W"],R[k]["H"]
    def para_prancha(x,y):
        u=(x-(im["x"]-im["w"]/2))/im["w"]; v=(y-(im["y"]-im["h"]/2))/im["h"]
        X,Y=M@np.array([u*Wm,v*Hm,1.0]); return [round(float(X),1),round(float(Y),1)]
    for n in notas:
        pts=[]
        for o in lines:
            p,s=o["raw"].get("primary",{}),o["raw"].get("secondary",{})
            for a,b in ((p,s),(s,p)):
                if a.get("widget") and int(a["widget"]["id"])==n["id"]:
                    xy,wid=ponta(b)
                    if xy and wid!=n["id"]: pts.append(para_prancha(*xy))
        n["alvos"]=pts
        n["no_post_it"]=para_prancha(n["x"],n["y"])
    alvos[k]=notas
json.dump(alvos,open("alvos.json","w"),ensure_ascii=False,indent=1)
for k,l in alvos.items(): print(k,len(l),"com seta",sum(1 for n in l if n["alvos"]))
# conferência visual
for k in ["B_Subsolo","C_Subsolo","D_Subsolo","A_Terreo"]:
    c,p=k.split("_"); pr=cv2.imread(P+f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{p}_entrega.png")[:2160].copy()
    for i,n in enumerate(alvos[k],1):
        x,y=n["no_post_it"]; cv2.circle(pr,(int(x),int(y)),14,(0,160,255),-1); cv2.putText(pr,str(i),(int(x)+12,int(y)),0,1.2,(0,0,200),3)
        for a in n["alvos"]:
            cv2.line(pr,(int(x),int(y)),(int(a[0]),int(a[1])),(0,0,255),3); cv2.circle(pr,(int(a[0]),int(a[1])),10,(0,0,255),-1)
    cv2.imwrite(f"alvos_{k}.jpg",cv2.resize(pr,(1920,1080)))

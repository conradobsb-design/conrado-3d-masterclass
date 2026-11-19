import json,re,struct,html
d=open("ws_dec.bin","rb").read()
dec=json.JSONDecoder()
recs={}
for m in re.finditer(rb'\{"', d):
    s=m.start()
    pre=d[max(0,s-60):s]
    tm=re.search(rb'[\x03-\x10]([a-z_]{3,16})[\x00-\xff]{1,6}$', pre)
    if not tm: continue
    typ=tm.group(1).decode()
    try: obj,end=dec.raw_decode(d[s:s+300000].decode("utf-8","ignore"))
    except Exception: continue
    idm=None
    for im in re.finditer(rb'\x08(0\x00\x00[\x00-\xff]{5})', d[max(0,s-140):s]): idm=im.group(1)
    if idm is None or not isinstance(obj,dict): continue
    wid=struct.unpack(">Q",idm)[0]
    recs.setdefault(wid,{"id":wid,"type":typ}); recs[wid].update(obj)
def txt(r):
    t=r.get("text") or r.get("title") or ""
    if not isinstance(t,str): t=json.dumps(t,ensure_ascii=False)
    return re.sub(r"\s+"," ",html.unescape(re.sub(r"<[^>]+>"," ",t))).strip()
def pid(r):
    p=r.get("_parent"); return int(p["id"]) if isinstance(p,dict) and p.get("id") else None
memo={}
def absxy(wid,depth=0):
    if wid in memo: return memo[wid]
    r=recs.get(wid)
    if not r or depth>20: return (0,0)
    o=((r.get("_position") or {}).get("offsetPx") or {})
    x,y=o.get("x",0),o.get("y",0)
    p=pid(r)
    if p:
        px,py=absxy(p,depth+1)
        pr=recs.get(p,{})
        # parent offset relative to parent's top-left
        sz=pr.get("size") or {}; sc=(pr.get("scale") or {}).get("scale",1)
        x+=px-(sz.get("width",0)*sc)/2; y+=py-(sz.get("height",0)*sc)/2
    memo[wid]=(x,y); return (x,y)
out=[]
for wid,r in recs.items():
    x,y=absxy(wid)
    sz=r.get("size") or {}; sc=(r.get("scale") or {}).get("scale",1)
    res=r.get("resource") or {}
    out.append({"id":wid,"type":r["type"],"text":txt(r),"x":x,"y":y,"w":sz.get("width",res.get("width",0))*sc,"h":sz.get("height",res.get("height",0))*sc,
                "parent":pid(r),"res":res.get("name"),"resid":res.get("id"),"style":r.get("style"),"raw":{k:r[k] for k in r if k in ("primary","secondary","points")}})
json.dump(out,open("widgets.json","w"),ensure_ascii=False)
for o in out:
    if o["type"]=="frame": print(o["id"],round(o["x"]),round(o["y"]),round(o["w"]),round(o["h"]),"|",o["text"][:80], sum(1 for z in out if z["parent"]==o["id"]))

import cv2,numpy as np,json
P="/home/user/conrado-3d-masterclass/projetos/"
q=json.load(open("notas_por_planta.json"))
out={}
for k,im in q["imagens"].items():
    c,p=k.split("_")
    m=68; kk=min((1920-2*m)/im["w"],(1200-2*m)/im["h"])
    hw,hh=im["w"]*kk,im["h"]*kk
    x0,y0=(960-hw/2)*2,(600-hh/2)*2
    a=cv2.imread(f"miro_{k}.png")
    mir=a[int(y0):int(y0+hh*2),int(x0):int(x0+hw*2)]
    cv2.imwrite(f"img_{k}.png",mir)
    pr=cv2.imread(P+f"POE642_Casa{c}/entrega/POE642_Casa{c}_PH_{p}_entrega.png")[:2160]
    g1=cv2.cvtColor(mir,cv2.COLOR_BGR2GRAY); g2=cv2.cvtColor(pr,cv2.COLOR_BGR2GRAY)
    sift=cv2.SIFT_create(8000)
    k1,d1=sift.detectAndCompute(g1,None); k2,d2=sift.detectAndCompute(g2,None)
    mt=cv2.BFMatcher().knnMatch(d1,d2,k=2)
    good=[a for a,b in mt if a.distance<0.75*b.distance]
    src=np.float32([k1[g.queryIdx].pt for g in good]); dst=np.float32([k2[g.trainIdx].pt for g in good])
    M,inl=cv2.estimateAffinePartial2D(src,dst,method=cv2.RANSAC,ransacReprojThreshold=4)
    ni=int(inl.sum()) if inl is not None else 0
    # normalized (u,v) of miro image -> prancha: px = M @ [u*W, v*H, 1]
    out[k]={"M":M.tolist(),"W":mir.shape[1],"H":mir.shape[0],"inliers":ni,"good":len(good)}
    sc=np.sqrt(abs(np.linalg.det(M[:,:2])))
    print(k,"good",len(good),"inl",ni,"escala %.3f"%sc, "t",M[:,2].round(1))
json.dump(out,open("registro.json","w"))

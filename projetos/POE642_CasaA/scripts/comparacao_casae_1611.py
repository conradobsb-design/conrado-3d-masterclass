"""Folha 'Casa E x referência': cada linha, o recorte atual da E ao lado do exemplo citado (A, C ou D)."""
import sys, json
from PIL import Image, ImageDraw, ImageFont
P='/home/user/conrado-3d-masterclass/projetos/'
F={'E_T':'POE642_CasaE/renders/POE642_CasaE_PH_Terreo_v1_final.png','E_S':'POE642_CasaE/renders/POE642_CasaE_PH_Subsolo_v1_final.png',
   'E_1':'POE642_CasaE/renders/POE642_CasaE_PH_1Pavimento_v1_final.png','A_T':'POE642_CasaA/renders/POE642_CasaA_PH_Terreo_final_rotulos.png',
   'C_T':'POE642_CasaC/renders/POE642_CasaC_PH_Terreo_final_rotulos.png','C_S':'POE642_CasaC/renders/POE642_CasaC_PH_Subsolo_final_rotulos.png',
   'D_T':'POE642_CasaD/renders/POE642_CasaD_PH_Terreo_final_rotulos.png','D_S':'POE642_CasaD/renders/POE642_CasaD_PH_Subsolo_final_rotulos.png'}
cache={}
def img(k):
    if k not in cache: cache[k]=Image.open(P+F[k]).convert('RGB')
    return cache[k]
try: fnt=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',26); fb=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',30)
except: fnt=fb=ImageFont.load_default()
linhas=json.load(open(sys.argv[1])); saida=sys.argv[2]; H=int(sys.argv[3]) if len(sys.argv)>3 else 420
blocos=[]
for ln in linhas:
    pares=[]
    for k,box,leg in ln['itens']:
        c=img(k).crop(tuple(box)); w=round(c.width*H/c.height); pares.append((c.resize((w,H),Image.LANCZOS),leg))
    W=sum(p.width for p,_ in pares)+20*(len(pares)-1)
    b=Image.new('RGB',(W,H+90),'white'); d=ImageDraw.Draw(b); d.text((0,4),ln['titulo'],fill=(20,20,20),font=fb)
    x=0
    for p,leg in pares:
        b.paste(p,(x,80)); d.text((x+6,48),leg,fill=(90,90,90),font=fnt); x+=p.width+20
    blocos.append(b)
W=max(b.width for b in blocos); Ht=sum(b.height for b in blocos)+30*len(blocos)
out=Image.new('RGB',(W+40,Ht+20),'white'); y=20
for b in blocos: out.paste(b,(20,y)); y+=b.height+30
out.save(saida,quality=88); print(saida,out.size)

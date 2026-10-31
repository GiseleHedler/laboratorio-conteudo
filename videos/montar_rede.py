# reel "a rede": um gesto pequeno corre pela rede e, anos depois, a ajuda volta de alguém que ela nunca conheceu
# uso: python3 rede.py [saida.mp4] [quadros_em_segundos]
import sys, math, random, subprocess
from collections import deque
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S='/tmp/claude-0/-home-user/f19a087c-4085-5aef-b35a-89b81156bb55/scratchpad'; M='/home/user/laboratorio-conteudo/marca/fontes'; O=S+'/rede'
W,H,FPS,DUR=1080,1920,30,72.0
CX,CY=540,930
random.seed(3)
FT=ImageFont.truetype(M+'/Poppins-Medium.ttf',52); FB=ImageFont.truetype(M+'/Poppins-Black.ttf',96)
FN=ImageFont.truetype(M+'/Poppins-Medium.ttf',30); FW=ImageFont.truetype(S+'/fonts/Merriweather-400-italic.ttf',50)
ROSE=(242,180,159)
def suave(u): u=max(0,min(1,u)); return u*u*(3-2*u)
def fade(t,a,b,fi=0.8,fo=0.8): return max(0,min(1,(t-a)/fi,(b-t)/fo))
def lerp(a,b,u): return a+(b-a)*u

# a rede: ela no centro, seis pessoas próximas em volta, centenas mais longe
N=700; pts=[(0.0,0.0)]
for k in range(6):
    a=k*6.283/6+0.4; pts.append((0.75*math.cos(a),0.9*math.sin(a)))
while len(pts)<N:
    r=0.45+abs(random.gauss(0,1.1)); a=random.random()*6.283
    pts.append((r*math.cos(a),r*math.sin(a)*1.3))
P=np.array(pts)
ARES=set()
for i in range(N):
    d=np.hypot(*(P-P[i]).T); d[i]=9
    for j in np.argsort(d)[:3]: ARES.add((min(i,int(j)),max(i,int(j))))
NOMES={i+1:n for i,n in enumerate(['mãe','filha','vizinha','cliente','moça do caixa','amiga'])}
for i in NOMES: ARES.add((0,i))
ADJ={i:set() for i in range(N)}
for i,j in ARES: ADJ[i].add(j); ADJ[j].add(i)
ARES=list(ARES)
def dist_de(a):
    d={a:0}; q=deque([a])
    while q:
        u=q.popleft()
        for w in ADJ[u]:
            if w not in d: d[w]=d[u]+1; q.append(w)
    return d
def caminho(a,b):
    pai={a:None}; q=deque([a])
    while q:
        u=q.popleft()
        if u==b: break
        for w in ADJ[u]:
            if w not in pai: pai[w]=u; q.append(w)
    c=[b]
    while pai[c[-1]] is not None: c.append(pai[c[-1]])
    return c[::-1]
CAIXA=5; DC=dist_de(CAIXA); DE=dist_de(0)
LONGE=max([i for i in range(N) if abs(P[i][0]*150)<440 and -700<P[i][1]*150<-200],key=lambda i:np.hypot(*P[i]))   # longe, mas dentro da tela
VOLTA=caminho(LONGE,0); VSET={v:k for k,v in enumerate(VOLTA)}
def longe_de(cands,outros): return max(cands,key=lambda w:min([np.hypot(*(P[w]-P[o])) for o in outros]+[9]) if abs(P[w][0])<1.6 else -1)
R1=longe_de([w for w in DC if DC[w]==1 and w and w not in NOMES],[0])
R3=longe_de([w for w in DC if DC[w]==3],[0,R1,CAIXA]); R5=longe_de([w for w in DC if DC[w]==5],[0,R1,R3,CAIXA])
# pulsos que correm pela rede no fim
AMB=[]
for _ in range(60):
    a=random.randrange(N); c=[a]
    for _ in range(random.randint(4,9)): c.append(random.choice(list(ADJ[c[-1]])))
    AMB.append((c,random.uniform(53,69),random.uniform(1.6,3.2)))

def zoom(t):
    kf=[(0,330),(8,330),(14,300),(22,250),(30,230),(40,150),(52,150),(58,112),(72,104)]
    for (a0,z0),(a1,z1) in zip(kf,kf[1:]):
        if t<=a1: return lerp(z0,z1,suave((t-a0)/(a1-a0)))
    return kf[-1][1]
def brilho_ela(t):
    if t<31: return 1.0
    if t<38: return lerp(1.0,0.14,suave((t-31)/7))
    if t<52.2: return 0.14+0.04*math.sin(t*2)
    return lerp(0.14,1.35,suave((t-52.2)/1.6))
def aceso(i,t):
    k=0.0
    if i in DC and 16.4<t<34:   # onda do bom dia
        t0=16.4+0.85*DC[i]
        if t>t0: k=max(k,math.exp(-(t-t0)*0.35)*(1 if t<30 else max(0,(34-t)/4)))
    if i in VSET:   # o caminho da ajuda que volta
        t0=42+10*VSET[i]/(len(VOLTA)-1)
        if t>t0: k=max(k,0.8*math.exp(-(t-t0)*0.25) if t<53 else 0.5)
    if t>53:   # a rede inteira acende a partir dela
        t0=53+0.45*DE.get(i,20)
        if t>t0: k=max(k,0.8*suave((t-t0)/1.2))
    return min(1,k)
def global_alfa(t):   # a rede aparece depois de ela estar sozinha; escurece na noite difícil
    a=suave((t-6)/3.5)
    if 31<t<53: a*=lerp(1,0.4,suave((t-31)/6)) if t<45 else lerp(0.4,0.6,suave((t-45)/8))
    return a

def ceu():
    y=np.linspace(0,1,H)[:,None]; b=np.zeros((H,W,3),np.float32)
    for k,(t0,t1) in enumerate([(10,26),(6,16),(28,52)]): b[:,:,k]=t0+(t1-t0)*(1-abs(y-0.48)*2)
    im=Image.fromarray(np.clip(b,0,255).astype(np.uint8)); d=ImageDraw.Draw(im)
    for _ in range(300):
        x,yy=random.randint(0,W),random.randint(0,H); c=random.randint(50,140); d.point((x,yy),fill=(c,c,c+30))
    neb=Image.new('RGB',(W,H)); dn=ImageDraw.Draw(neb)
    for _ in range(10):
        x,yy,r=random.randint(0,W),random.randint(300,1500),random.randint(200,400); dn.ellipse((x-r,yy-r,x+r,yy+r),fill=random.choice([(60,25,90),(40,20,80),(70,30,80)]))
    return Image.fromarray(np.clip(np.asarray(im,np.float32)+np.asarray(neb.filter(ImageFilter.GaussianBlur(140)),np.float32)*0.5,0,255).astype(np.uint8))
CEU=ceu()

def texto(d,txt,y,fo,al):
    if al<=0: return
    w=d.textlength(txt,font=fo); d.text(((W-w)/2,y),txt,font=fo,fill=(242,236,246,int(255*al)))
def pulso(d,dl_luz,cam,u,sc,cor=(255,232,196)):
    segs=len(cam)-1; pos=max(0,min(segs,u*segs)); k=min(int(pos),segs-1); f=pos-k
    for z in range(int(pos)):
        (a0,a1),(b0,b1)=sc(cam[z]),sc(cam[z+1]); d.line((a0,a1,b0,b1),fill=cor+(200,),width=4)
    (xa,ya),(xb,yb)=sc(cam[k]),sc(cam[k+1]); px,py=xa+(xb-xa)*f,ya+(yb-ya)*f
    d.line((xa,ya,px,py),fill=cor+(220,),width=4)
    dl_luz.ellipse((px-40,py-40,px+40,py+40),fill=cor+(160,)); d.ellipse((px-9,py-9,px+9,py+9),fill=(255,255,255,255))

def quadro(t):
    z=zoom(t); ga=global_alfa(t)
    sc=lambda i:(CX+P[i][0]*z,CY+P[i][1]*z)
    im=CEU.copy().convert('RGBA'); L=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(L)
    LZ=Image.new('RGBA',(W,H),(0,0,0,0)); dz=ImageDraw.Draw(LZ); LG=Image.new('RGBA',(W,H),(0,0,0,0)); dg=ImageDraw.Draw(LG); T=Image.new('RGBA',(W,H),(0,0,0,0)); dt=ImageDraw.Draw(T)
    AC=[aceso(i,t) for i in range(N)]
    for i,j in ARES:
        x0,y0=sc(i); x1,y1=sc(j)
        if (x0<-60 and x1<-60) or (x0>W+60 and x1>W+60) or (y0<-60 and y1<-60) or (y0>H+60 and y1>H+60): continue
        k=max(AC[i],AC[j]); nome=(i==0 and j in NOMES)
        a=(70+170*k)*ga*(1 if not nome else max(1,fade(t,8,99)*2.2))
        if a>3: d.line((x0,y0,x1,y1),fill=(int(110+140*k),int(90+130*k),int(170+75*k),int(min(255,a))),width=1+int(2*k)+(1 if nome and t>8 else 0))
    for i in range(1,N):
        x,y=sc(i)
        if not(-20<x<W+20 and -20<y<H+20): continue
        k=AC[i]; r=3+5*k; a=(170+85*k)*ga
        if a>3: d.ellipse((x-r,y-r,x+r,y+r),fill=(int(170+85*k),int(160+85*k),int(220+35*k),int(a)))
        if k>0.35: dz.ellipse((x-r*4,y-r*4,x+r*4,y+r*4),fill=(255,226,200,int(90*k*ga)))
    # ela
    b=brilho_ela(t); x,y=sc(0); pul=1+0.08*math.sin(t*2.2); r=(10*min(b,1.2)+3)*pul
    dz.ellipse((x-r*5,y-r*5,x+r*5,y+r*5),fill=ROSE+(int(120*min(1,b)),))
    d.ellipse((x-r*2.2,y-r*2.2,x+r*2.2,y+r*2.2),fill=ROSE+(int(110*min(1,b)),)); d.ellipse((x-r,y-r,x+r,y+r),fill=(255,240,232,int(255*max(0.3,min(1,b)))))
    if 52.2<t<55:   # a luz dela volta com força
        e=t-52.2; R=60+500*suave(e/2.5); dg.ellipse((x-R,y-R,x+R,y+R),fill=(255,236,220,int(120*(1-e/2.8))))
        d.ellipse((x-R*0.5,y-R*0.5,x+R*0.5,y+R*0.5),outline=ROSE+(int(200*(1-e/2.8)),),width=3)
    w=dt.textlength('você',font=FN); dt.text((x-w/2,y+r*2.3+8),'você',font=FN,fill=ROSE+(int(230*max(0.4,min(1,b))),))
    # nomes de quem está perto
    na=fade(t,9,17,1.2,1.2)
    for i,n in NOMES.items():
        if n=='moça do caixa' and 14<t<29: continue
        xi,yi=sc(i); w=dt.textlength(n,font=FN); dt.text((xi-w/2,yi-48),n,font=FN,fill=(235,225,245,int(230*na)))
    # o bom dia
    if 14.4<t<16.6: pulso(d,dz,[0,CAIXA],(t-14.4)/2.2,sc)
    for i,txt,a0,a1 in [(CAIXA,'um bom dia',15.6,21),(R1,'um sorriso pro filho',18.2,23.5),(R3,'uma aula mais paciente',20.6,26),(R5,'um pedido de desculpa',23,28.5)]:
        al=fade(t,a0,a1); xi,yi=sc(i); w=dt.textlength(txt,font=FN)
        if al>0: dt.text((min(max(xi-w/2,30),W-30-w),yi-50),txt,font=FN,fill=(255,236,214,int(240*al)))
    # a ajuda que volta de longe
    if 42<t<52.3: pulso(d,dz,VOLTA,(t-42)/10.3,sc)
    xl,yl=sc(LONGE); al=fade(t,41.5,47)
    if al>0:
        dz.ellipse((xl-34,yl-34,xl+34,yl+34),fill=(255,232,196,int(150*al))); w=dt.textlength('alguém',font=FN)
        dt.text((min(max(xl-w/2,30),W-30-w),yl-52),'alguém',font=FN,fill=(255,236,214,int(240*al)))
    for c,t0,du in AMB:
        if t0<t<t0+du: pulso(d,dz,c,(t-t0)/du,sc,(255,214,232))
    # textos
    texto(dt,'você acha que',400,FT,fade(t,0.6,5.6)); texto(dt,'está sozinha.',470,FT,fade(t,0.6,5.6))
    texto(dt,'nunca esteve.',400,FB,fade(t,8,13.8))
    texto(dt,'anos depois.',400,FT,fade(t,32,36.5))
    texto(dt,'alguém que você',1520,FT,fade(t,45,52)); texto(dt,'nunca conheceu.',1590,FT,fade(t,45,52))
    texto(dt,'ninguém muda sozinha.',360,FT,fade(t,57,DUR+5,1.0))
    texto(dt,'e ninguém muda',1520,FT,fade(t,61,DUR+5,1.0)); texto(dt,'só pra si.',1590,FB,fade(t,61.5,DUR+5,1.0))
    w=dt.textlength('@giselehedler',font=FW); dt.text(((W-w)/2,1380),'@giselehedler',font=FW,fill=(234,232,236,95))
    if LG.getbbox(): im.alpha_composite(LG.filter(ImageFilter.GaussianBlur(110)))
    im.alpha_composite(LZ.filter(ImageFilter.GaussianBlur(28)))
    im.alpha_composite(L.filter(ImageFilter.GaussianBlur(6))); im.alpha_composite(L); im.alpha_composite(T)
    if t<0.8: im=Image.blend(Image.new('RGBA',(W,H),(0,0,0,255)),im,t/0.8)
    return im.convert('RGB')

if __name__=='__main__':
    out=sys.argv[1] if len(sys.argv)>1 else O+'/rede_sem_som.mp4'
    if len(sys.argv)>2:
        for s in sys.argv[2].split(','): quadro(float(s)).save(f'{O}/r_{s}.jpg',quality=90)
        sys.exit()
    p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
        '-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p',out],stdin=subprocess.PIPE)
    for i in range(int(DUR*FPS)): p.stdin.write(quadro(i/FPS).tobytes())
    p.stdin.close(); p.wait(); print('ok',out)

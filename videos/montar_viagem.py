# reel "a vida é uma viagem": linhas de luz numa régua de anos, ascendentes antes, descendentes depois
# uso: python3 viagem.py [saida.mp4] [quadro_unico_em_segundos]
import sys, math, random, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S='/tmp/claude-0/-home-user/f19a087c-4085-5aef-b35a-89b81156bb55/scratchpad'; M='/home/user/laboratorio-conteudo/marca/fontes'
W,H,FPS=1080,1920,30
Y0=880          # linha do "agora": cabeças das linhas
V=150           # px por segundo que o passado desce
DUR=72.0
random.seed(7)

# tempo do vídeo (s) -> idade dela (anos)
def T(t):
    if t<6:  return -6+t*1.0          # antes de ela nascer, devagar
    if t<62: return (t-6)*85/56       # vida dela: 0 a 85
    return 85+(t-62)*1.2              # o filho segue
def tdeT(a):  # inversa
    if a<0: return a+6
    if a<85: return 6+a*56/85
    return 62+(a-85)/1.2

def hexrgb(h): h=h.lstrip('#'); return tuple(int(h[i:i+2],16) for i in (0,2,4))
def mix(a,b,k): return tuple(int(a[i]+(b[i]-a[i])*k) for i in range(3))
def suave(u): u=max(0,min(1,u)); return u*u*(3-2*u)
def interp(kf,a):
    if a<=kf[0][0]: return kf[0][1]
    for (a0,x0),(a1,x1) in zip(kf,kf[1:]):
        if a<=a1: return x0+(x1-x0)*suave((a-a0)/(a1-a0))
    return kf[-1][1]
def cor_eu(a):   # a cor dela muda com a vida; quem chega, chega da cor dela naquele momento
    return tuple(int(c) for c in (interp([(0,255),(30,226),(60,255),(85,255)],a),interp([(0,214),(30,159),(60,196),(85,226)],a),interp([(0,206),(30,142),(60,122),(85,170)],a)))

# pessoas: nome, cor, nasce (idade dela), parte (None = segue), trajetória x
P=[
 dict(n='avó',  c=hexrgb('#b9a6ff'), ini=-99, fim=22, kf=[(-99,130),(22,150)]),
 dict(n='mãe',  c=hexrgb('#ff7eb3'), ini=-99, fim=60, kf=[(-99,320),(10,300),(40,290),(60,300)]),
 dict(n='pai',  c=hexrgb('#6aa8ff'), ini=-99, fim=52, kf=[(-99,760),(30,860),(52,860)]),
 dict(n='avô',  c=hexrgb('#8fe3ff'), ini=-99, fim=12, kf=[(-99,960),(12,980)]),
 dict(n='eu',   c=hexrgb('#f2b49f'), ini=0,   fim=85, kf=[(0,540),(25,540),(32,520),(60,530),(85,540)]),
 dict(n='irmã', c=hexrgb('#c77dff'), ini=3,   fim=79, kf=[(3,300),(6,420),(40,420),(65,380),(79,380)]),
 dict(n='amiga de infância', c=hexrgb('#ffd166'), ini=6, fim=None, sai=17, kf=[(5.5,1180),(8,670),(14,670),(17,-80)]),
 dict(n='primeiro amor',     c=hexrgb('#ff5d73'), ini=15, fim=None, sai=19, kf=[(14.5,1180),(16.5,600),(17.5,598),(19,1180)]),
 dict(n='mentora', c=hexrgb('#4ee3c1'), ini=22, fim=None, sai=33, kf=[(21.5,1180),(24,770),(30,770),(33,1180)]),
 dict(n='marido',  c=hexrgb('#9be37a'), ini=27, fim=74, kf=[(26.5,1180),(29.5,690),(60,690),(74,680)]),
 dict(n='filho',   c=hexrgb('#5ad1ff'), ini=31, fim=None, kf=[(31,600),(34,615),(70,615),(86,615),(95,540)]),
]
def cor(p,a): return p['c']
def vivo(p,a):
    fim=p['fim'] if p['fim'] is not None else p.get('sai',999)
    return p['ini']<=a<=fim
# estrela de quem parte: posição no céu
ESTRELA={'avô':(900,250),'avó':(190,300),'pai':(800,430),'mãe':(300,470),'marido':(660,320),'eu':(470,200),'irmã':(150,580)}

F=lambda f,s: ImageFont.truetype(f,s)
FN=F(M+'/Poppins-Medium.ttf',27); FT=F(M+'/Poppins-Medium.ttf',48); FB=F(M+'/Poppins-Black.ttf',84)
FR=F(S+'/fonts/Merriweather-400-italic.ttf',30); FA=F(M+'/Poppins-Medium.ttf',26)

# céu de fundo: roxo profundo, nebulosa ameixa, estrelinhas
def ceu():
    y=np.linspace(0,1,H)[:,None]; base=np.zeros((H,W,3),np.float32)
    top=np.array([10,6,28]); mid=np.array([26,14,52]); bot=np.array([6,4,16])
    for i in range(3): base[:,:,i]=np.where(y<0.5,top[i]+(mid[i]-top[i])*y*2,mid[i]+(bot[i]-mid[i])*(y-0.5)*2)
    im=Image.fromarray(base.astype(np.uint8)).convert('RGB')
    neb=Image.new('RGB',(W,H),(0,0,0)); d=ImageDraw.Draw(neb)
    for _ in range(14):
        x,yv,r=random.randint(-100,W+100),random.randint(0,1300),random.randint(180,420)
        d.ellipse((x-r,yv-r*0.6,x+r,yv+r*0.6),fill=random.choice([(70,30,100),(50,25,90),(90,40,90),(30,30,80)]))
    neb=neb.filter(ImageFilter.GaussianBlur(120))
    im=Image.fromarray(np.clip(np.asarray(im,np.float32)+np.asarray(neb,np.float32)*0.55,0,255).astype(np.uint8))
    d=ImageDraw.Draw(im)
    for _ in range(520):
        x,yv=random.randint(0,W),int(random.random()**1.6*H); b=random.randint(60,190); r=random.choice([0.6,0.8,1,1.2])
        d.ellipse((x-r,yv-r,x+r,yv+r),fill=(b,b,min(255,b+30)))
    return im
CEU=ceu()
PISCA=[(random.randint(0,W),int(random.random()**1.5*1300),random.random()*6.28,random.uniform(0.6,1.6)) for _ in range(70)]

def texto(d,txt,y,fo,alfa,cor=(240,234,244)):
    if alfa<=0: return
    w=d.textlength(txt,font=fo); d.text(((W-w)/2,y),txt,font=fo,fill=cor+(int(255*alfa),))
def fade(t,a,b,fi=0.6,fo=0.6): return max(0,min(1,(t-a)/fi,(b-t)/fo))

def quadro(t):
    im=CEU.copy().convert('RGBA'); a_now=T(t)
    lin=Image.new('RGBA',(W,H),(0,0,0,0)); dl=ImageDraw.Draw(lin)
    txt=Image.new('RGBA',(W,H),(0,0,0,0)); dt=ImageDraw.Draw(txt)
    for x,y,ph,sp in PISCA:
        b=int(110+100*(0.5+0.5*math.sin(t*sp+ph))); dl.ellipse((x-1.6,y-1.6,x+1.6,y+1.6),fill=(b,b,255,b))
    # régua de anos (idade dela), à esquerda
    dt.text((36,40),'anos',font=FA,fill=(200,190,220,150))
    for ida in range(0,100,5):
        yv=Y0+V*(t-tdeT(ida))
        if 60<yv<H-40:
            al=int(150*min(1,max(0,(yv-60)/120)))
            dl.line((28,yv,44,yv),fill=(200,190,220,al),width=2); dt.text((54,yv-16),str(ida),font=FA,fill=(200,190,220,al))
    dl.line((36,90,36,H-40),fill=(200,190,220,40),width=1)
    # linhas: rastro do passado descendo
    vivos=sorted([(interp(p['kf'],a_now),p['n']) for p in P if vivo(p,a_now)])
    ALT={}; borda=[-999,-999,-999]   # borda direita do último nome em cada altura
    for x,n in vivos:
        w=dt.textlength(n,font=FN); nv=next((k for k in range(3) if x-w/2>borda[k]+14),2)
        ALT[n]=58+34*nv; borda[nv]=x+w/2
    for p in P:
        pts=[]; tau=0.0
        while Y0+V*tau<H+20:
            a=T(t-tau)
            if vivo(p,a):
                x=interp(p['kf'],a); pts.append((x,Y0+V*tau,cor(p,a)))
            else:
                if pts: break
            tau+=1/30
        ph=(sum(map(ord,p['n']))%100)/16
        def balanco(x,y):
            d=min(1,max(0,(y-Y0)/(H-Y0))); amp=26*d**1.4
            return x+amp*math.sin(t*0.9+ph+d*5.5)+0.5*amp*math.sin(t*0.55+ph*2+d*9)
        n=len(pts)
        for k,((x0,y0,c0),(x1,y1,c1)) in enumerate(zip(pts,pts[1:])):
            d=min(1,max(0,(y0-Y0)/(H-Y0))); al=int(240*(1-d)**1.3); wd=max(2,int(5-3*d))
            if al>4: dl.line((balanco(x0,y0),y0,balanco(x1,y1),y1),fill=c0+(al,),width=wd)
        # cabeça e nome
        if vivo(p,a_now):
            x=interp(p['kf'],a_now); c=cor(p,a_now)
            if -40<x<W+40:
                dl.line((x,Y0-ALT[p['n']]+30,x,Y0-14),fill=c+(90,),width=1) if ALT[p['n']]>58 else None
                dl.ellipse((x-9,Y0-9,x+9,Y0+9),fill=(255,255,255,255)); dl.ellipse((x-16,Y0-16,x+16,Y0+16),outline=c+(200,),width=3)
                nm=p['n']; w=dt.textlength(nm,font=FN)
                if 40<x-w/2 and x+w/2<W-20: dt.text((x-w/2,Y0-ALT[nm]),nm,font=FN,fill=c+(240,))
    # quem parte: explode em luz e sobe até virar estrela
    for p in P:
        if p['fim'] is None or p['n'] not in ESTRELA: continue
        tf=tdeT(p['fim']); sx,sy=ESTRELA[p['n']]; c=cor(p,p['fim']); x0=interp(p['kf'],p['fim'])
        if t<tf: continue
        e=t-tf
        lenta=1.8 if p['n']=='eu' else 1.0
        e=e/lenta
        if e<1.6:   # explosão: clarão, anel e faíscas
            fl=max(0,1-e/0.5); r=40+260*suave(e/1.6)
            dl.ellipse((x0-90*fl-10,Y0-90*fl-10,x0+90*fl+10,Y0+90*fl+10),fill=(255,255,255,int(200*fl)))
            dl.ellipse((x0-r,Y0-r,x0+r,Y0+r),outline=c+(int(200*(1-e/1.6)),),width=4)
            rnd=random.Random(sum(map(ord,p['n'])))
            for k in range(90 if p['n']=='eu' else 46):
                ang=rnd.random()*6.283; sp=rnd.uniform(120,420); vida=rnd.uniform(0.8,1.6)
                if e<vida:
                    d=sp*e*(1-e/(2*vida)); xx=x0+math.cos(ang)*d; yy=Y0+math.sin(ang)*d+40*e*e
                    rr=2.6*(1-e/vida)+0.6; dl.ellipse((xx-rr,yy-rr,xx+rr,yy+rr),fill=c+(int(255*(1-e/vida)),))
        u=suave((e-0.5)/2.6)
        if e>0.5:   # sobe em curva, com cauda de luz
            for k in range(18):
                uk=max(0,u-k*0.012); xk=x0+(sx-x0)*uk+60*math.sin(uk*3.14)*(1 if sx>x0 else -1); yk=Y0+(sy-Y0)*uk
                if u<1 and k>0: dl.ellipse((xk-3,yk-3,xk+3,yk+3),fill=c+(int(180*(1-k/18)),))
            x=x0+(sx-x0)*u+60*math.sin(u*3.14)*(1 if sx>x0 else -1); y=Y0+(sy-Y0)*u
            r=6+4*u+1.6*math.sin(t*2+sx)
            dl.ellipse((x-r*3,y-r*3,x+r*3,y+r*3),fill=c+(60,)); dl.ellipse((x-r*1.6,y-r*1.6,x+r*1.6,y+r*1.6),fill=c+(140,))
            dl.ellipse((x-r,y-r,x+r,y+r),fill=(255,255,255,255))
            if u>0.85: dt.text((x+22,y-18),p['n'],font=FN,fill=c+(int(230*(u-0.85)/0.15),))
    # ela vem do céu: luz descendo antes de nascer
    if 4.0<=t<6.2:
        u=suave((t-4.0)/2.0); x=540; y=150+(Y0-150)*u
        for k in range(14):
            yy=y-k*14; al=int(200*(1-k/14))
            dl.ellipse((x-5,yy-5,x+5,yy+5),fill=(255,214,206,al))
        dl.ellipse((x-10,y-10,x+10,y+10),fill=(255,255,255,255))
    # brilho
    glow=lin.filter(ImageFilter.GaussianBlur(10)); glow2=lin.filter(ImageFilter.GaussianBlur(3))
    im.alpha_composite(glow); im.alpha_composite(glow); im.alpha_composite(glow2); im.alpha_composite(lin)
    # textos
    texto(dt,'a viagem não começa',300,FT,fade(t,0.4,4.2)); texto(dt,'quando você nasce.',366,FT,fade(t,0.4,4.2))
    texto(dt,'a família certa',1500,FT,fade(t,7.5,12.5)); texto(dt,'pro que você veio aprender.',1566,FT,fade(t,7.5,12.5))
    texto(dt,'ninguém chegou na sua vida',1500,FT,fade(t,tdeT(27),tdeT(36),0.8,0.8)); texto(dt,'por acaso.',1566,FT,fade(t,tdeT(27),tdeT(36),0.8,0.8))
    texto(dt,'nem você.',1660,FB,fade(t,tdeT(29.5),tdeT(36),0.8,0.8))
    texto(dt,'a viagem da vida termina.',1360,FT,fade(t,63.6,DUR+5,1.0))
    fa=fade(t,67.8,DUR+5,0.9)
    texto(dt,'você continua.',1450,FB,fade(t,66.2,DUR+5,1.2))
    w=dt.textlength('@giselehedler',font=FR); dt.text(((W-w)/2,H-90),'@giselehedler',font=FR,fill=(234,232,236,190))
    im.alpha_composite(txt)
    if t<0.8: im=Image.blend(Image.new('RGBA',(W,H),(0,0,0,255)),im,t/0.8)
    return im.convert('RGB')

if __name__=='__main__':
    out=sys.argv[1] if len(sys.argv)>1 else S+'/viagem/viagem_sem_som.mp4'
    if len(sys.argv)>2:
        for s in sys.argv[2].split(','): quadro(float(s)).save(f'{S}/viagem/q_{s}.jpg',quality=90)
        sys.exit()
    p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
        '-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p',out],stdin=subprocess.PIPE)
    for i in range(int(DUR*FPS)):
        p.stdin.write(quadro(i/FPS).tobytes())
    p.stdin.close(); p.wait(); print('ok',out)

# reel "a rede" v2: um fio de luz só, pessoas com nome e cor, câmera parada; a ajuda volta de um estranho
# uso: python3 rede2.py [saida.mp4] [quadros_em_segundos]
import sys, math, random, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S='/tmp/claude-0/-home-user/f19a087c-4085-5aef-b35a-89b81156bb55/scratchpad'; M='/home/user/laboratorio-conteudo/marca/fontes'; O=S+'/rede'
W,H,FPS,DUR=1080,1920,30,76.0
random.seed(11)
FT=ImageFont.truetype(M+'/Poppins-Medium.ttf',54); FB=ImageFont.truetype(M+'/Poppins-Black.ttf',100)
FN=ImageFont.truetype(M+'/Poppins-Medium.ttf',38); FG=ImageFont.truetype(M+'/Poppins-Medium.ttf',36)
FW=ImageFont.truetype(S+'/fonts/Merriweather-400-italic.ttf',46)
def hexrgb(h): h=h.lstrip('#'); return tuple(int(h[i:i+2],16) for i in (0,2,4))
ROSE=hexrgb('#f2b49f'); OURO=(255,214,140); AMEIXA=hexrgb('#c393dc'); CINZA=(150,140,175)
def suave(u): u=max(0,min(1,u)); return u*u*(3-2*u)
def fade(t,a,b,fi=0.7,fo=0.7): return max(0,min(1,(t-a)/fi,(b-t)/fo))
def lerp(a,b,u): return a+(b-a)*u
def mix(c1,c2,u): return tuple(int(lerp(a,b,u)) for a,b in zip(c1,c2))

EU=(540,1350)
PERTO=[('mãe',(290,1420),'#ff7eb3'),('filha',(310,1185),'#5ad1ff'),('amiga',(450,1075),'#c77dff'),
       ('cliente',(640,1075),'#4ee3c1'),('moça do caixa',(795,1185),'#ffa94d'),('vizinha',(800,1425),'#ffd166')]
PERTO=[(n,p,hexrgb(c)) for n,p,c in PERTO]
CAIXA=PERTO[4][1]
# o fio do bom dia: sobe pela tela, passando por estranhos
FIO=[EU,CAIXA,(870,960),(590,770),(300,580),(560,380),(720,-80)]
GESTO=[None,('moça do caixa','um bom dia'),('o filho dela','um sorriso pro filho'),('a professora','uma aula mais paciente'),
       ('uma aluna','uma aluna que não desistiu'),('o pai da aluna','um pedido de desculpa'),None]
T_FIO=[11.0,13.0,15.6,18.2,20.8,23.4,26.2]   # quando a luz chega em cada ponto
# a ajuda que volta: um estranho entra por cima e a luz dourada desce devagar até ela
ESTR0=(780,-60); ESTR=(780,250)
VOLTA=[ESTR,(920,470),(640,650),(400,840),PERTO[1][1],EU]
VGESTO=[('alguém','um eu te amo'),('um vizinho dele','uma mão estendida'),('uma enfermeira','um plantão a mais'),
        ('a amiga da sua filha','uma mensagem às 3 da manhã'),(None,'mãe, eu tô aqui'),None]
T_VOLTA=[44.5,46.3,48.1,49.9,51.7,53.3]
# raios: cada pessoa próxima também passa adiante a sua própria história, rapidinho
RAIOS=[(1,['um abraço apertado','um conselho','uma ligação']),(2,['uma risada','um convite','uma segunda chance']),
       (3,['um elogio','uma indicação','um emprego']),(0,['uma oração','um prato de comida','um colo']),
       (5,['uma carona','um recado','um pode contar comigo'])]
def raio_pts(k):
    (x,y)=PERTO[k][1]; dx,dy=x-EU[0],y-EU[1]; n=math.hypot(dx,dy); dx,dy=dx/n,dy/n; px,py=-dy,dx
    pts=[(x,y)]
    for h in range(1,4):
        z=(1 if h%2 else -1)*45
        pts.append((min(max(x+dx*165*h+px*z,70),W-70),min(max(y+dy*165*h+py*z-60*h,180),1640)))
    return pts
RAIO_T0=[26.6+0.85*i for i in range(5)]

# a rede: ~120 pessoas sem nome, espalhadas acima dela
NOS=[]
fixos=[p for _,p,_ in PERTO]+FIO[2:6]+VOLTA[1:4]+[EU]+[q for k,_ in RAIOS for q in raio_pts(k)[1:]]
while len(NOS)<120:
    x,y=random.uniform(110,970),random.uniform(200,1560)
    if all(math.hypot(x-a,y-b)>78 for a,b in NOS+fixos): NOS.append((x,y))
TODOS=NOS+FIO[2:6]+VOLTA[1:4]
ARES=set()
for i,(x,y) in enumerate(TODOS):
    d=sorted(range(len(TODOS)),key=lambda j:math.hypot(TODOS[j][0]-x,TODOS[j][1]-y))
    for j in d[1:3]: ARES.add((min(i,j),max(i,j)))
ARES=list(ARES)
DIST_EU=[math.hypot(x-EU[0],y-EU[1]) for x,y in TODOS]
DIST_ES=[math.hypot(x-ESTR[0],y-ESTR[1]) for x,y in TODOS]

def cam(t):   # aproxima nela no renascer e depois abre
    kf=[(0,1.0),(52.5,1.0),(56,1.28),(60,1.0),(68,0.9),(76,0.88)]
    for (a0,z0),(a1,z1) in zip(kf,kf[1:]):
        if t<=a1: return lerp(z0,z1,suave((t-a0)/(a1-a0)))
    return kf[-1][1]
def brilho_ela(t):
    if t<34: return 1.0
    if t<40: return lerp(1.0,0.12,suave((t-34)/6))
    if t<53.3: return 0.12+0.03*math.sin(t*2.4)
    return lerp(0.12,1.4,suave((t-53.3)/1.4))
def lig_perto(k,t):   # as ligações com quem está perto: aparecem, apagam na noite, voltam no renascer
    a=fade(t,6.2+k*0.45,99,0.5,1)
    if t>34: a*=1-suave((t-(34.5+k*0.8))/1.2)
    if t>54: a=max(a,suave((t-(54+k*0.5))/0.8))
    return a
def rede_alfa(t):
    a=suave((t-5)/2.5)
    if t>34: a*=lerp(1,0.35,suave((t-34)/5))
    if t>54: a=max(a,lerp(0.35,1,suave((t-54)/3)))
    return a
def cor_no(i,t):   # no fim, a rede ganha a cor dela (de baixo) e a do estranho (de cima)
    if t<57: return CINZA,0.0
    u_eu=suave((t-57-DIST_EU[i]/160)/1.5); u_es=suave((t-57-DIST_ES[i]/160)/1.5)
    if u_eu>=u_es: return mix(CINZA,ROSE,u_eu),u_eu
    return mix(CINZA,AMEIXA,u_es),u_es

def ceu():
    y=np.linspace(0,1,H)[:,None]; b=np.zeros((H,W,3),np.float32)
    for k,(t0,t1) in enumerate([(12,28),(7,17),(30,54)]): b[:,:,k]=t0+(t1-t0)*(1-abs(y-0.5)*2)
    im=Image.fromarray(np.clip(b,0,255).astype(np.uint8)); d=ImageDraw.Draw(im)
    for _ in range(260):
        x,yy=random.randint(0,W),random.randint(0,H); c=random.randint(50,130); d.point((x,yy),fill=(c,c,c+30))
    neb=Image.new('RGB',(W,H)); dn=ImageDraw.Draw(neb)
    for _ in range(9):
        x,yy,r=random.randint(0,W),random.randint(200,1600),random.randint(220,420); dn.ellipse((x-r,yy-r,x+r,yy+r),fill=random.choice([(60,25,90),(45,20,80),(75,30,85)]))
    return Image.fromarray(np.clip(np.asarray(im,np.float32)+np.asarray(neb.filter(ImageFilter.GaussianBlur(150)),np.float32)*0.5,0,255).astype(np.uint8))
CEU=ceu()

def rotulo(dt,txt,x,y,fo,cor,al):
    if al<=0: return
    w=dt.textlength(txt,font=fo); x=min(max(x-w/2,24),W-24-w)
    dt.text((x+2,y+3),txt,font=fo,fill=(10,5,20,int(180*al))); dt.text((x,y),txt,font=fo,fill=cor+(int(255*al),))
def texto(dt,txt,y,fo,al):
    if al<=0: return
    w=dt.textlength(txt,font=fo); dt.text(((W-w)/2+2,y+3),txt,font=fo,fill=(10,5,20,int(170*al))); dt.text(((W-w)/2,y),txt,font=fo,fill=(244,238,248,int(255*al)))
def fio(d,dz,pts,tempos,t,cor,larg):   # luz que corre de ponto em ponto e deixa o rastro aceso
    for k in range(len(pts)-1):
        a,b=tempos[k],tempos[k+1]
        if t<a: break
        u=suave(min(1,(t-a)/(b-a))); (x0,y0),(x1,y1)=pts[k],pts[k+1]; xe,ye=lerp(x0,x1,u),lerp(y0,y1,u)
        d.line((x0,y0,xe,ye),fill=cor+(230,),width=larg)
        if u<1: dz.ellipse((xe-46,ye-46,xe+46,ye+46),fill=cor+(170,)); d.ellipse((xe-10,ye-10,xe+10,ye+10),fill=(255,255,255,255))

def quadro(t):
    z=cam(t); P=lambda p:(EU[0]+(p[0]-EU[0])*z,EU[1]+(p[1]-EU[1])*z)
    im=CEU.copy().convert('RGBA')
    L=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(L)
    LZ=Image.new('RGBA',(W,H),(0,0,0,0)); dz=ImageDraw.Draw(LZ)
    LG=Image.new('RGBA',(W,H),(0,0,0,0)); dg=ImageDraw.Draw(LG)
    T=Image.new('RGBA',(W,H),(0,0,0,0)); dt=ImageDraw.Draw(T)
    ra=rede_alfa(t)
    # rede de fundo
    for i,j in ARES:
        (x0,y0),(x1,y1)=P(TODOS[i]),P(TODOS[j]); ci,ki=cor_no(i,t); cj,kj=cor_no(j,t)
        k=max(ki,kj); c=mix(ci,cj,0.5)
        d.line((x0,y0,x1,y1),fill=c+(int((55+120*k)*ra),),width=1+int(2*k))
    for i,p in enumerate(TODOS):
        x,y=P(p); c,k=cor_no(i,t); r=4+3*k
        d.ellipse((x-r,y-r,x+r,y+r),fill=c+(int((150+100*k)*ra),))
        if k>0.5: dz.ellipse((x-16,y-16,x+16,y+16),fill=c+(int(70*k),))
    # o fio do bom dia (rose) e as pessoas que ele toca
    fade_fio=1.0 if t<34 else max(0.3,1-(t-34)/6)
    Lf=Image.new('RGBA',(W,H),(0,0,0,0)); df=ImageDraw.Draw(Lf)
    fio(df,dz,[P(p) for p in FIO],T_FIO,t,ROSE,7)
    L.alpha_composite(Image.fromarray((np.asarray(Lf).astype(np.float32)*[1,1,1,fade_fio]).astype(np.uint8)))
    for k in range(2,6):
        if t>T_FIO[k]:
            x,y=P(FIO[k]); u=suave((t-T_FIO[k])/0.6)*fade_fio
            d.ellipse((x-11,y-11,x+11,y+11),fill=ROSE+(int(255*u),)); dz.ellipse((x-40,y-40,x+40,y+40),fill=ROSE+(int(120*u),))
            nome,gesto=GESTO[k]
            rotulo(dt,nome,x,y+20,FG,(235,226,245),u*0.85)
            rotulo(dt,gesto,x,y-64,FN,(255,226,206),fade(t,T_FIO[k]-0.1,T_FIO[k]+2.9))
    rotulo(dt,'um bom dia',P(CAIXA)[0],P(CAIXA)[1]-110,FN,(255,226,206),fade(t,T_FIO[1]-0.2,T_FIO[1]+2.8))
    # raios: as histórias de cada um, rápidas
    for (k,gestos),t0 in zip(RAIOS,RAIO_T0):
        if t<t0: continue
        cor=PERTO[k][2]; pts=raio_pts(k); tempos=[t0+0.5*h for h in range(4)]
        Lr=Image.new('RGBA',(W,H),(0,0,0,0)); dr=ImageDraw.Draw(Lr); fio(dr,dz,[P(q) for q in pts],tempos,t,cor,4)
        fr=1.0 if t<34 else max(0.2,1-(t-34)/5)
        L.alpha_composite(Image.fromarray((np.asarray(Lr).astype(np.float32)*[1,1,1,fr]).astype(np.uint8)))
        for h in range(1,4):
            if t>tempos[h]:
                x,y=P(pts[h]); d.ellipse((x-8,y-8,x+8,y+8),fill=cor+(int(240*fr),))
                rotulo(dt,gestos[h-1],x,y-50,FG,(255,236,220),fade(t,tempos[h]-0.05,tempos[h]+1.4,0.15,0.4))
    # quem está perto dela
    for k,(n,p,c) in enumerate(PERTO):
        x,y=P(p); la=lig_perto(k,t); vis=fade(t,6.2+k*0.45,99,0.5,1)
        volta_k=T_VOLTA[4] if n=='filha' else 54+k*0.5
        cz=c if t<34 else mix(c,CINZA,suave((t-(34.5+k*0.8))/1.2))
        if t>volta_k: cz=mix(CINZA,c,suave((t-volta_k)/0.8))
        ex,ey=P(EU)
        if la>0.02: d.line((ex,ey,x,y),fill=cz+(int(200*la),),width=3)
        if vis>0:
            d.ellipse((x-14,y-14,x+14,y+14),fill=cz+(int(255*vis),)); dz.ellipse((x-38,y-38,x+38,y+38),fill=cz+(int(90*vis),))
            rotulo(dt,n,x,y+22 if y>EU[1]-60 else y-60,FN,cz,vis)
    # o estranho entra por cima e a luz dourada desce até ela
    if t>42:
        u=suave((t-42)/2.5); ex,ey=P((lerp(ESTR0[0],ESTR[0],u),lerp(ESTR0[1],ESTR[1],u)))
        d.ellipse((ex-14,ey-14,ex+14,ey+14),fill=AMEIXA+(255,)); dz.ellipse((ex-44,ey-44,ex+44,ey+44),fill=AMEIXA+(130,))
        rotulo(dt,'alguém',ex,ey-62,FN,AMEIXA,fade(t,42.5,58,1,1))
        fio(d,dz,[P(p) for p in VOLTA],T_VOLTA,t,OURO,6)
        for k in range(5):
            if t>T_VOLTA[k]-(1.2 if k==0 else 0):
                x,y=P(VOLTA[k]); nome,gesto=VGESTO[k]
                if 0<k<4:
                    d.ellipse((x-11,y-11,x+11,y+11),fill=OURO+(255,)); dz.ellipse((x-38,y-38,x+38,y+38),fill=OURO+(120,))
                    rotulo(dt,nome,x,y+20,FG,(240,232,214),0.9)
                rotulo(dt,gesto,x,(y+34 if k==0 else y-(110 if k==4 else 64)),FN,(255,232,190),fade(t,T_VOLTA[k]-(1.2 if k==0 else 0.1),T_VOLTA[k]+2.6))
    # ela
    b=brilho_ela(t); x,y=P(EU); pul=1+0.07*math.sin(t*2.2); r=(13*min(b,1.25)+4)*pul
    dz.ellipse((x-r*5,y-r*5,x+r*5,y+r*5),fill=ROSE+(int(130*min(1,b)),))
    d.ellipse((x-r*2.1,y-r*2.1,x+r*2.1,y+r*2.1),fill=ROSE+(int(120*min(1,b)),)); d.ellipse((x-r,y-r,x+r,y+r),fill=(255,242,234,int(255*max(0.3,min(1,b)))))
    rotulo(dt,'você',x,y+r*2.2+6,FN,ROSE,max(0.45,min(1,b)))
    if 53.3<t<57.4:   # renascer: clarão grande, anéis e faíscas
        e=t-53.3; k=max(0,1-e/4)
        dg.ellipse((x-650*suave(e/0.8),y-650*suave(e/0.8),x+650*suave(e/0.8),y+650*suave(e/0.8)),fill=(255,232,214,int(110*k)))
        dg.ellipse((x-220,y-220,x+220,y+220),fill=(255,248,240,int(200*max(0,1-e/1.5))))
        for q in (0.0,0.5):
            rr=40+420*suave((e-q)/2.6)
            if e>q: d.ellipse((x-rr,y-rr,x+rr,y+rr),outline=ROSE+(int(210*max(0,1-(e-q)/2.6)),),width=5)
        rnd=random.Random(5)
        for _ in range(200):
            ang=rnd.random()*6.283; sp=rnd.uniform(200,700); vida=rnd.uniform(1.0,2.4)
            if e<vida:
                dd=sp*e*(1-e/(2*vida)); xx=x+math.cos(ang)*dd; yy=y+math.sin(ang)*dd
                rp=3*(1-e/vida)+0.6; d.ellipse((xx-rp,yy-rp,xx+rp,yy+rp),fill=mix(ROSE,OURO,rnd.random())+(int(255*(1-e/vida)),))
    # textos (sempre fora da rede: no alto ou embaixo)
    texto(dt,'você acha que',300,FT,fade(t,0.6,5.4)); texto(dt,'está sozinha.',372,FT,fade(t,0.6,5.4))
    texto(dt,'nunca esteve.',150,FB,fade(t,7,11))
    texto(dt,'anos depois.',150,FT,fade(t,34,37.6)); texto(dt,'em uma das noites',150,FT,fade(t,37.8,42)); texto(dt,'mais desafiadoras...',222,FT,fade(t,37.8,42))
    texto(dt,'alguém que você',1640,FT,fade(t,55,63)); texto(dt,'nunca conheceu.',1712,FT,fade(t,55,63))
    texto(dt,'ninguém muda sozinha.',140,FT,fade(t,63.5,DUR+5,1))
    texto(dt,'e ninguém muda',1640,FT,fade(t,67,DUR+5,1)); texto(dt,'só pra si.',1712,FB,fade(t,67.5,DUR+5,1))
    w=dt.textlength('@giselehedler',font=FW); dt.text(((W-w)/2,1525),'@giselehedler',font=FW,fill=(234,232,236,90))
    if LG.getbbox(): im.alpha_composite(LG.filter(ImageFilter.GaussianBlur(100)))
    im.alpha_composite(LZ.filter(ImageFilter.GaussianBlur(26)))
    im.alpha_composite(L.filter(ImageFilter.GaussianBlur(5))); im.alpha_composite(L); im.alpha_composite(T)
    if t<0.8: im=Image.blend(Image.new('RGBA',(W,H),(0,0,0,255)),im,t/0.8)
    return im.convert('RGB')

if __name__=='__main__':
    out=sys.argv[1] if len(sys.argv)>1 else O+'/rede3_sem_som.mp4'
    if len(sys.argv)>2:
        for s in sys.argv[2].split(','): quadro(float(s)).save(f'{O}/s_{s}.jpg',quality=90)
        sys.exit()
    p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
        '-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p',out],stdin=subprocess.PIPE)
    for i in range(int(DUR*FPS)): p.stdin.write(quadro(i/FPS).tobytes())
    p.stdin.close(); p.wait(); print('ok',out)

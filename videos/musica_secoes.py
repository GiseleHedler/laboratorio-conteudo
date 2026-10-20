# Trilha por partes: um clima diferente em cada trecho do vídeo, com impacto grave nas viradas
# uso: python3 musica_secoes.py <saida.wav> <duração> <inicio:fim:clima> [<inicio:fim:clima> ...]
# climas: suspense, misterio, aceleracao, susto, sombrio, resolucao
import sys, numpy as np, wave
SR=44100
rng=np.random.default_rng(7)
def hz(m): return 440*2**((m-69)/12)
def tt(d): return np.arange(int(SR*d))/SR
def env_ar(n,a=0.005,r=0.2):
    t=np.arange(n)/SR; return np.minimum(1,t/a)*np.exp(-t/r)
def add(buf,sig,st):
    i=int(st*SR)
    if i>=len(buf) or i<0: return
    j=min(len(buf),i+len(sig)); buf[i:j]+=sig[:j-i]
def kick(v=0.9):
    t=tt(0.35); f=50+90*np.exp(-t*30); return v*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*9)
def hat(v=0.15):
    n=int(SR*0.05); return v*rng.standard_normal(n)*np.exp(-np.arange(n)/SR*90)*np.sign(np.sin(np.arange(n)*1.7))
def click(v=0.25):
    n=int(SR*0.015); t=np.arange(n)/SR; return v*np.sin(2*np.pi*3200*t)*np.exp(-t*400)
def pluck(f,d=0.9,v=0.3):
    # Karplus-Strong: corda pinçada
    n=int(SR*d); p=max(2,int(SR/f)); b=rng.uniform(-1,1,p); out=np.zeros(n)
    for i in range(n):
        out[i]=b[i%p]; b[i%p]=0.5*(b[i%p]+b[(i+1)%p])*0.996
    return v*out
def drone(freqs,d,v=0.12,trem=0.0):
    t=tt(d); s=sum(np.sin(2*np.pi*f*t)+0.3*np.sin(2*np.pi*2*f*t+0.5) for f in freqs)/len(freqs)
    if trem: s*=1-0.35*(0.5+0.5*np.sin(2*np.pi*trem*t))
    return v*s
def sino(f,v=0.12):
    t=tt(2.5); return v*(np.sin(2*np.pi*f*t)+0.5*np.sin(2*np.pi*f*2.76*t)*np.exp(-t*3))*np.exp(-t*1.4)
def impacto(v=1.0):
    t=tt(2.2); f=70*np.exp(-t*1.5)+28
    boom=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*2.2)
    ruido=rng.standard_normal(len(t))*np.exp(-t*12)*0.35
    return v*(boom+ruido)

def suspense(d):
    b=np.zeros(int(SR*d)); t=tt(d)
    add(b,drone([hz(33),hz(40)],d,0.16,trem=0.25)*np.minimum(1,0.4+0.6*t/d),0)
    beat=60/72; k=0.0
    while k<d:
        add(b,kick(0.75),k); add(b,kick(0.5),k+0.22); k+=beat
    c=0.0
    while c<d: add(b,click(0.18),c); c+=0.5
    # zumbido que sobe no fim
    r=tt(min(3,d)); sweep=np.sin(2*np.pi*np.cumsum(200+900*(r/r[-1])**2)/SR)*0.06*(r/r[-1])**2
    add(b,sweep,d-len(r)/SR)
    return b
def misterio(d):
    b=np.zeros(int(SR*d)); beat=60/96
    acordes=[(57,60,64),(53,57,60),(50,53,57),(52,56,59)]   # Am F Dm E
    add(b,drone([hz(45)],d,0.07),0)
    t=0.0; k=0
    while t<d:
        a=acordes[(k//8)%4]; nota=[a[0],a[1],a[2],a[1]+12,a[2],a[1],a[0]+12,a[2]][k%8]
        add(b,pluck(hz(nota),0.8,0.22),t)
        if k%8==0: add(b,pluck(hz(a[0]-24),1.6,0.35),t)
        t+=beat/2; k+=1
    return b
def aceleracao(d):
    b=np.zeros(int(SR*d)); beat=60/128; t=0.0; k=0
    while t<d:
        add(b,kick(0.8),t)
        for h in range(4): add(b,hat(0.12 if h%2 else 0.08),t+h*beat/4)
        for s16 in range(4):
            nota=[45,57,45,52][s16]
            add(b,pluck(hz(nota),0.22,0.28),t+s16*beat/4)
        if k%4==3: add(b,drone([hz(69),hz(72),hz(76)],beat*0.5,0.10)*env_ar(int(SR*beat*0.5),0.005,0.12),t+beat/2)
        t+=beat; k+=1
    r=tt(min(4,d)); add(b,rng.standard_normal(len(r))*0.05*(r/r[-1])**2,d-len(r)/SR)   # subida de ruído
    return b
def susto(d):
    b=np.zeros(int(SR*d)); t=tt(d)
    cluster=sum(np.sin(2*np.pi*hz(m)*t) for m in (69,70,71,72,75))/5
    agudo=np.sin(2*np.pi*hz(93)*t)*0.4
    curva=(t/d)**2
    add(b,(cluster+agudo)*0.22*curva,0)
    add(b,impacto(1.0),d*0.92)
    return b
def sombrio(d):
    b=np.zeros(int(SR*d)); t=tt(d)
    add(b,drone([hz(33),hz(39)],d,0.14,trem=0.12),0)   # trítono grave
    add(b,drone([hz(57)*1.003,hz(57)*0.997],d,0.05),0)  # batimento desconfortável
    s=0.0; k=0
    while s<d:
        add(b,sino(hz([81,80,76,75][k%4])*(1+0.012*rng.standard_normal()),0.10),s)
        s+=2.6; k+=1
    w=0.0
    while w<d-3:
        r=tt(3); add(b,rng.standard_normal(len(r))*0.04*(r/r[-1])**3,w); w+=8   # inspirações ao contrário
    return b
def resolucao(d):
    b=np.zeros(int(SR*d)); beat=60/72; bar=4*beat
    acordes=[(57,61,64),(54,57,61),(50,54,57),(52,56,59)]   # A F#m D E
    t=0.0; k=0
    while t<d:
        a=acordes[k%4]
        add(b,drone([hz(m) for m in a],bar+1,0.07)*np.minimum(1,tt(bar+1)/0.8),t)
        for i,m in enumerate([a[0]+12,a[2]+12,a[1]+24,a[2]+12]):
            add(b,sino(hz(m),0.08),t+i*beat)
        t+=bar; k+=1
    return b

CLIMAS={'suspense':suspense,'misterio':misterio,'aceleracao':aceleracao,'susto':susto,'sombrio':sombrio,'resolucao':resolucao}
saida=sys.argv[1]; DUR=float(sys.argv[2])
out=np.zeros(int(SR*(DUR+1)))
for arg in sys.argv[3:]:
    a,b_,clima=arg.split(':'); a=float(a); b_=float(b_)
    sec=CLIMAS[clima](b_-a+0.6)
    sec=sec/(np.sqrt(np.mean(sec**2))+1e-9)*0.12            # mesmo volume percebido entre as partes
    n=len(sec); f=int(0.6*SR)
    sec[:f]*=np.linspace(0,1,f); sec[-f:]*=np.linspace(1,0,f)
    add(out,sec,a)
    if clima not in ('susto',) and a>0.5: add(out,impacto(0.5),a)   # batida grave na virada
rev=out.copy()
for dly,g in [(0.031,0.4),(0.053,0.32),(0.079,0.25),(0.13,0.18),(0.21,0.12),(0.34,0.07)]:
    d=int(dly*SR); rev[d:]+=g*out[:-d]
rev=rev[:int(SR*DUR)]
rev=rev/np.max(np.abs(rev))*0.85
st=np.stack([rev,np.roll(rev,int(0.012*SR))],1)
with wave.open(saida,'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st*32767).astype(np.int16).tobytes())

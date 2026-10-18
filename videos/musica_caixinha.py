# Caixinha de música em valsa (3/4), lá menor, que cresce até o clímax, para no silêncio e volta em lá maior
# uso: python3 musica_caixinha.py <duração> <para_em> <volta_em> <saida.wav>
import sys, numpy as np, wave
DUR,PARA,VOLTA=map(float,sys.argv[1:4]); SAIDA=sys.argv[4]
SR=44100; N=int(SR*(DUR+1)); out=np.zeros(N)
def hz(m): return 440*2**((m-69)/12)
def caixinha(f,vel):
    # lâmina de metal: parciais inarmônicos com queda rápida
    d=2.2; n=int(SR*d); t=np.arange(n)/SR
    s=(np.sin(2*np.pi*f*t)*np.exp(-t*2.0)+0.35*np.sin(2*np.pi*f*2.76*t)*np.exp(-t*5)
       +0.12*np.sin(2*np.pi*f*5.40*t)*np.exp(-t*9))
    return vel*s*(1-np.exp(-t*400))
def add(sig,start):
    i=int(start*SR)
    if i>=N or start<0: return
    j=min(N,i+len(sig)); out[i:j]+=sig[:j-i]
beat=60/80; bar=3*beat
# Am Dm G C F Dm E E (fundamental, terça, quinta em MIDI)
acordes=[(57,60,64),(50,53,57),(55,59,62),(48,52,55),(53,57,60),(50,53,57),(52,56,59),(52,56,59)]
t=0.0; k=0
while t<PARA-0.05:
    r,ter,qui=acordes[k%8]
    cresc=0.55+0.45*min(1,t/max(PARA,1))           # vai crescendo até o clímax
    seq=[r+12,qui+12,ter+24,qui+24,ter+24,qui+12]   # arpejo em colcheias
    for i,mn in enumerate(seq):
        st=t+i*beat/2
        if st<PARA-0.05: add(caixinha(hz(mn+12),0.10*cresc*(1.3 if i==0 else 1)),st)
    if t<PARA-0.05: add(caixinha(hz(r),0.12*cresc),t)
    t+=bar; k+=1
# volta em lá maior, lenta, e deixa soar
seq=[45,57,61,64,69,73,76]
for i,mn in enumerate(seq): add(caixinha(hz(mn+12),0.11),VOLTA+i*beat*0.75)
for mn in (57,61,64,69): add(caixinha(hz(mn+12),0.07),VOLTA+len(seq)*beat*0.75+0.3)
# corta seco no clímax (com 60 ms de fade para não estalar)
i0=int(PARA*SR); fl=int(0.06*SR); out[i0:i0+fl]*=np.linspace(1,0,fl); out[i0+fl:int(VOLTA*SR)]=0
rev=out.copy()
for dly,g in [(0.029,0.45),(0.043,0.38),(0.067,0.30),(0.101,0.24),(0.157,0.17),(0.241,0.11),(0.37,0.07)]:
    d=int(dly*SR); rev[d:]+=g*out[:-d]
rev=rev[:int(SR*DUR)]
rev=rev/np.max(np.abs(rev))*0.6
st=np.stack([rev,np.roll(rev,int(0.011*SR))],1)
with wave.open(SAIDA,'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st*32767).astype(np.int16).tobytes())

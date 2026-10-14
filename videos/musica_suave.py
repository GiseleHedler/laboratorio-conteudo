# Trilha suave sintetizada (piano elétrico + pad), 66 s, Am F C G, ~68 bpm
import numpy as np, wave
SR=44100; DUR=66.0; N=int(SR*DUR); out=np.zeros(N)
def hz(m): return 440*2**((m-69)/12)
def piano(f,dur,vel=0.3):
    n=int(SR*dur); t=np.arange(n)/SR
    env=np.exp(-t*2.2)*(1-np.exp(-t*80))
    s=(np.sin(2*np.pi*f*t)+0.35*np.sin(2*np.pi*2*f*t)*np.exp(-t*4)+0.12*np.sin(2*np.pi*3*f*t)*np.exp(-t*6))
    return vel*env*s
def pad(freqs,dur,vel=0.05):
    n=int(SR*dur); t=np.arange(n)/SR; s=np.zeros(n)
    for f in freqs:
        for d in (-0.15,0.15): s+=np.sin(2*np.pi*(f+d)*t)
    a=np.minimum(1,t/1.5)*np.minimum(1,(dur-t)/1.5)
    return vel*s*a/len(freqs)
def add(sig,start):
    i=int(start*SR)
    if i>=N: return
    j=min(N,i+len(sig)); out[i:j]+=sig[:j-i]
beat=60/68; bar=4*beat
acordes=[[57,60,64],[53,57,60],[48,52,55],[55,59,62]]  # Am F C G
baixos=[45,41,36,43]
t=0.0; k=0
while t<DUR:
    a=acordes[k%4]; b=baixos[k%4]
    add(pad([hz(m) for m in a],bar+1.5),t)
    add(piano(hz(b),bar,0.18),t)
    # arpejo leve
    seq=[a[0],a[1],a[2],a[1]+12 if k%2 else a[2]+12]
    for i,m in enumerate(seq*2):
        add(piano(hz(m+12),beat*2,0.10 if i%4 else 0.14),t+i*beat/2)
    t+=bar; k+=1
# reverb simples (vários ecos amortecidos)
rev=out.copy()
for dly,g in [(0.031,0.5),(0.047,0.42),(0.071,0.35),(0.113,0.28),(0.173,0.2),(0.257,0.14)]:
    d=int(dly*SR); rev[d:]+=g*out[:-d]
rev*= np.minimum(1,np.arange(N)/(SR*2))  # fade in
fo=int(SR*3); rev[-fo:]*=np.linspace(1,0,fo)
rev=rev/np.max(np.abs(rev))*0.6
st=np.stack([rev,np.roll(rev,int(0.012*SR))],1)
with wave.open('/tmp/claude-0/-home-user/f19a087c-4085-5aef-b35a-89b81156bb55/scratchpad/reel/v3/musica.wav','wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st*32767).astype(np.int16).tobytes())

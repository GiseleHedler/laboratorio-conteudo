# Acha as pausas internas de uma frase (envelope de energia em janelas de 20 ms)
import numpy as np, wave
_cache={}
def env(wav):
    if wav not in _cache:
        w=wave.open(wav); n=w.getnframes(); sr=w.getframerate()
        x=np.frombuffer(w.readframes(n),np.int16).astype(float)/32768
        k=int(sr*0.02); m=len(x)//k
        db=20*np.log10(np.sqrt((x[:m*k].reshape(m,k)**2).mean(1))+1e-9)
        _cache[wav]=db
    return _cache[wav]
def pedacos(wav,a,b,min_gap=0.14,keep=0.07):
    db=env(wav); i0,i1=int(a/0.02),int(b/0.02); seg=db[i0:i1]
    if len(seg)<5: return [(a,b)]
    thr=np.percentile(seg,90)-14
    on=seg>thr
    falas=[];ini=None
    for i,v in enumerate(on):
        if v and ini is None: ini=i
        if not v and ini is not None: falas.append([ini,i]); ini=None
    if ini is not None: falas.append([ini,len(on)])
    falas=[f for f in falas if f[1]-f[0]>=2]
    if not falas: return [(a,b)]
    out=[];cur=a
    for f,g in zip(falas,falas[1:]):
        s=a+f[1]*0.02; e=a+g[0]*0.02
        if e-s>=min_gap:
            out.append((cur,s+keep/2)); cur=e-keep/2
    out.append((cur,b))
    return [(x,y) for x,y in out if y-x>0.12]

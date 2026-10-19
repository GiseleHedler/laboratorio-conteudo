# Mede as pausas de fala de cada tomada (envelope de energia em janelas de 20 ms)
import subprocess, numpy as np, json, sys
V='../videos/'
def env(f):
    raw=subprocess.run(['ffmpeg','-v','error','-i',V+f+'.mp4','-vn','-ac','1','-ar','16000','-f','s16le','-'],capture_output=True).stdout
    x=np.frombuffer(raw,np.int16).astype(float)/32768
    n=len(x)//320; x=x[:n*320].reshape(n,320)
    return 20*np.log10(np.sqrt((x**2).mean(1))+1e-9)
def falas(f,min_gap=0.18):
    db=env(f); thr=np.percentile(db,95)-24
    on=db>thr
    t=np.arange(len(db))*0.02
    seg=[];ini=None
    for i,v in enumerate(on):
        if v and ini is None: ini=t[i]
        if not v and ini is not None: seg.append([ini,t[i]]); ini=None
    if ini is not None: seg.append([ini,t[-1]])
    # junta trechos separados por menos de min_gap
    out=[]
    for s in seg:
        if s[1]-s[0]<0.04: continue
        if out and s[0]-out[-1][1]<min_gap: out[-1][1]=s[1]
        else: out.append(s)
    return out
if __name__=='__main__':
    for f in sys.argv[1:]:
        s=falas(f)
        gaps=[(round(a[1],2),round(b[0],2),round(b[0]-a[1],2)) for a,b in zip(s,s[1:])]
        print(f,'fala',round(s[0][0],2),'-',round(s[-1][1],2),'pausas',gaps)

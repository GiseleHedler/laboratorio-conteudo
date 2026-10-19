# Vlog final v4: encurta pausas longas (dissolve curto), audio travado por cena, cartoes, legenda, sons
import subprocess, numpy as np, os
import pausas
V='../videos/'; D=0.08; KEEP=0.20; MINGAP=0.34
SEG=[ # arquivo, ini, fim, zoom, branco_entra, branco_sai, legendas (tempo do clipe original)
 ('tomada1-wan',0.10,8.30,None,True,False,[(0.25,4.0,"Gente, eu voltei 2.400 anos no tempo."),(4.0,8.1,"Tô na Grécia, e vim conhecer quem começou tudo isso.")]),
 ('tomada2a-wan',0.10,3.55,None,False,False,[(0.26,3.4,"Hipócrates, o senhor pergunta o que o paciente come?")]),
 ('tomada2b-wan',0.10,4.15,(0.33,0.45,1.35),False,False,[(0.25,1.2,"Sempre."),(1.2,4.0,"O que come, como vive, onde mora.")]),
 ('tomada3-wan',0.10,8.00,None,False,True,[(0.25,5.0,"2.400 anos atrás ele já olhava o prato do paciente."),(5.0,7.8,"Hoje, muita gente só olha o laudo.")]),
 ('tomada4-chegada-wan',0.10,2.05,None,True,False,[(0.25,1.95,"Pulei 600 anos.")]),
 ('tomada4a2-wan',0.22,4.95,None,False,False,[(0.37,1.85,"Galeno, olha esse exame:"),(1.85,4.8,"tudo normal, mas a paciente continua mal.")]),
 ('tomada4b-wan',0.10,5.60,(0.38,0.40,1.25),False,False,[(0.25,2.5,"Na época de vocês pode ter isso."),(2.5,5.45,"Aqui, a gente olha a paciente inteira.")]),
 ('tomada5-wan',0.10,4.60,(0.55,0.50,1.12),False,False,[(0.25,2.2,"O exame e a pessoa."),(2.2,4.45,"Normal para quem, né?")]),
 ('tomada6-wan',0.10,11.90,None,False,False,[(0.26,2.9,"Eles já olhavam o ser humano inteiro."),(2.9,4.95,"É isso que eu ensino há 27 anos."),(4.95,9.1,"E pela primeira vez, as formações da FSA têm acesso vitalício."),(9.1,11.9,"O vitalício fecha dia 31/10.")]),
]
CARTOES=[('card-hip.png',6.0,100,985),('card-gal.png',6.8,100,1209),('card-oli.png',7.6,100,1433),('card-sel.png',9.15,159,900)]
W0,H0=716,1284

def gaps(f,rel=12,mg=0.14):
    db=pausas.env(f); thr=np.percentile(db,95)-rel; on=db>thr; t=np.arange(len(db))*0.02
    seg=[];ini=None
    for i,v in enumerate(on):
        if v and ini is None: ini=t[i]
        if not v and ini is not None: seg.append([ini,t[i]]); ini=None
    if ini is not None: seg.append([ini,t[-1]])
    out=[]
    for s in seg:
        if out and s[0]-out[-1][1]<mg: out[-1][1]=s[1]
        else: out.append(s)
    return [(a[1],b[0]) for a,b in zip(out,out[1:]) if b[0]-a[1]>=MINGAP]

def pedacos(s):
    f,ss,to=s[0],s[1],s[2]
    cortes=[(a+KEEP/2+D/2, b-KEEP/2+D/2) for a,b in gaps(f) if a>ss and b<to]
    p=[];cur=ss
    for a,b in cortes: p.append((cur,a)); cur=b
    p.append((cur,to)); return p

def mapa(p,t):
    acc=0
    for k,(a,b) in enumerate(p):
        if t<b or k==len(p)-1:
            return acc+max(0,t-a)
        acc+=(b-a)-D
    return acc

os.makedirs('cenas',exist_ok=True)
info=[]
for i,s in enumerate(SEG):
    p=pedacos(s); L=sum(b-a for a,b in p)-D*(len(p)-1)
    cx,cy,z=s[3] if s[3] else (0.5,0.5,1.0)
    w=int(W0/z)//2*2;h=int(1272/z)//2*2
    x=int(min(max(cx*W0-w/2,0),W0-w));y=int(min(max(cy*H0-h/2,0),H0-h))
    fc=[f"[0:v]crop={w}:{h}:{x}:{y},scale=1080:1920:flags=lanczos,setsar=1,fps=30,eq=contrast=1.04:saturation=1.06,format=yuv420p,split={len(p)}"+''.join(f'[vs{k}]' for k in range(len(p))),
        f"[0:a]aresample=44100,asplit={len(p)}"+''.join(f'[as{k}]' for k in range(len(p)))]
    for k,(a,b) in enumerate(p):
        fc.append(f"[vs{k}]trim={a:.3f}:{b:.3f},setpts=PTS-STARTPTS[vp{k}]")
        fc.append(f"[as{k}]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS[ap{k}]")
    v,a_='vp0','ap0'; R=p[0][1]-p[0][0]
    for k in range(1,len(p)):
        fc.append(f"[{v}][vp{k}]xfade=transition=fade:duration={D}:offset={R-D:.3f}[vx{k}]")
        fc.append(f"[{a_}][ap{k}]acrossfade=d={D}[ax{k}]")
        v,a_=f'vx{k}',f'ax{k}'; R+=p[k][1]-p[k][0]-D
    vf=f"[{v}]null"
    if s[4]: vf+=",fade=t=in:st=0:d=0.35:color=white"
    if s[5]: vf+=f",fade=t=out:st={L-0.15:.3f}:d=0.15:color=white"
    fc.append(vf+f",trim=0:{L:.3f}[vo]")
    fc.append(f"[{a_}]afade=t=in:d=0.02,afade=t=out:st={L-0.05:.3f}:d=0.05,apad,atrim=0:{L:.3f}[ao]")
    out=f'cenas/c{i}.mp4'
    subprocess.run(['ffmpeg','-v','error','-y','-i',V+s[0]+'.mp4','-filter_complex',';'.join(fc),'-map','[vo]','-map','[ao]','-c:v','libx264','-crf','15','-preset','fast','-c:a','pcm_s16le','-ar','44100',out.replace('.mp4','.mov')],check=True)
    info.append((p,L))
    print(i,s[0],'cortes',len(p)-1,'antes',round(s[2]-s[1],2),'depois',round(L,2))

inicio=[];t=0
for p,L in info: inicio.append(t); t+=L
TOTAL=t
def ts(x): return f"{int(x//3600)}:{int(x%3600//60):02d}:{x%60:05.2f}"
ass=["[Script Info]","ScriptType: v4.00+","PlayResX: 1080","PlayResY: 1920","WrapStyle: 0","","[V4+ Styles]",
"Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
"Style: Baixo,Archivo Black,60,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,5,2,2,90,90,520,1",
"Style: Topo,Archivo Black,56,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,5,2,8,90,90,300,1","","[Events]",
"Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
for i,s in enumerate(SEG):
    p,L=info[i]
    for a,b,txt in s[6]:
        A=inicio[i]+mapa(p,a);B=min(inicio[i]+mapa(p,b),inicio[i]+L)
        est='Topo' if i==len(SEG)-1 and a>=4.9 else 'Baixo'
        ass.append(f"Dialogue: 0,{ts(A)},{ts(B)},{est},,0,0,0,,{{\\fad(60,60)}}{txt}")
open('legendas.ass','w').write('\n'.join(ass)+'\n')

n=len(SEG); cmd=['ffmpeg','-v','error','-y']
for i in range(n): cmd+=['-i',f'cenas/c{i}.mov']
for c in CARTOES: cmd+=['-loop','1','-framerate','30','-t',f'{TOTAL:.2f}','-i',c[0]]
cmd+=['-i','pop.wav','-i','whoosh.wav']
fc=[''.join(f"[{i}:v][{i}:a]" for i in range(n))+f"concat=n={n}:v=1:a=1[vc][ac]"]
prev='vc'; pops=[]
for k,(img,tt,x,y) in enumerate(CARTOES):
    T=inicio[-1]+mapa(info[-1][0],tt); pops.append(T)
    fc.append(f"[{n+k}:v]format=rgba,fade=t=in:st={T:.2f}:d=0.18:alpha=1[c{k}]")
    fc.append(f"[{prev}][c{k}]overlay=x={x}:y='{y}+50*max(0\\,1-(t-{T:.2f})/0.18)':enable='gte(t\\,{T:.2f})'[o{k}]")
    prev=f'o{k}'
fc.append(f"[{prev}]ass=legendas.ass:fontsdir=/root/.fonts[vout]")
pi=n+len(CARTOES);wi=pi+1
fc.append("[ac]loudnorm=I=-15:TP=-2,aresample=44100[voz]")
fc.append(f"[{pi}:a]asplit={len(pops)}"+''.join(f"[p{j}]" for j in range(len(pops))))
for j,T in enumerate(pops): fc.append(f"[p{j}]adelay={int(T*1000)}:all=1,volume=0.45[pp{j}]")
corte=inicio[4]
fc.append(f"[{wi}:a]asplit=2[w0][w1]")
fc.append("[w0]atrim=start=0.45,asetpts=PTS-STARTPTS,volume=0.5[ww0]")
fc.append(f"[w1]adelay={int((corte-0.55)*1000)}:all=1,volume=0.6[ww1]")
fc.append("[voz]"+''.join(f"[pp{j}]" for j in range(len(pops)))+f"[ww0][ww1]amix=inputs={len(pops)+3}:normalize=0:duration=first,alimiter=limit=0.89,apad,atrim=0:{TOTAL:.3f}[aout]")
cmd+=['-filter_complex',';'.join(fc),'-map','[vout]','-map','[aout]','-c:v','libx264','-crf','20','-preset','medium','-profile:v','high','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart','-t',f'{TOTAL:.2f}','../videos/vlog-gabriel-final-v4.mp4']
subprocess.run(cmd,check=True)
print('total',round(TOTAL,2),'cartoes',[round(x,2) for x in pops])

# Monta o vlog final: tomadas + zoom + transicoes + cartoes dos pacotes + legenda + sons
import subprocess
V='../videos/'
SEG=[ # arquivo, ini, fim, zoom(cx,cy,z) ou None, branco_entra, branco_sai, legendas (tempo do clipe)
 ('tomada1-wan',0.10,8.30,None,True,False,[(0.25,3.9,"Gente, eu voltei 2.400 anos no tempo."),(3.9,8.1,"Tô na Grécia, e vim conhecer quem começou tudo isso.")]),
 ('tomada2a-wan',0.10,3.55,None,False,False,[(0.26,3.4,"Hipócrates, o senhor pergunta o que o paciente come?")]),
 ('tomada2b-wan',0.10,4.15,(0.33,0.45,1.35),False,False,[(0.25,1.15,"Sempre."),(1.15,4.0,"O que come, como vive, onde mora.")]),
 ('tomada3-wan',0.10,8.00,None,False,True,[(0.25,5.0,"2.400 anos atrás ele já olhava o prato do paciente."),(5.0,7.8,"Hoje, muita gente só olha o laudo.")]),
 ('tomada4-chegada-wan',0.10,2.05,None,True,False,[(0.25,1.95,"Pulei 600 anos.")]),
 ('tomada4a2-wan',0.22,4.95,None,False,False,[(0.37,1.6,"Galeno, olha esse exame:"),(1.6,4.8,"tudo normal, mas a paciente continua mal.")]),
 ('tomada4b-wan',0.10,5.60,(0.38,0.40,1.25),False,False,[(0.25,2.5,"Na época de vocês pode ter isso."),(2.5,5.45,"Aqui, a gente olha a paciente inteira.")]),
 ('tomada5-wan',0.10,4.60,(0.55,0.50,1.12),False,False,[(0.25,2.45,"O exame e a pessoa."),(2.45,4.45,"Normal para quem, né?")]),
 ('tomada6-wan',0.10,11.60,None,False,False,[(0.26,2.75,"Eles já olhavam o ser humano inteiro."),(2.75,4.9,"É isso que eu ensino há 27 anos."),(4.9,9.1,"E pela primeira vez, as formações da FSA têm acesso vitalício."),(9.1,11.45,"O vitalício fecha dia 31/10.")]),
]
CARTOES=[('card-hip.png',6.0,100,985),('card-gal.png',6.8,100,1209),('card-oli.png',7.6,100,1433),('card-sel.png',9.15,159,900)]
W0,H0=716,1284
inicio=[];t=0
for s in SEG: inicio.append(t); t+=s[2]-s[1]
TOTAL=t
ultimo=inicio[-1]-SEG[-1][1]

def ts(x):
    h=int(x//3600);m=int(x%3600//60);s=x%60
    return f"{h}:{m:02d}:{s:05.2f}"
ass=["[Script Info]","ScriptType: v4.00+","PlayResX: 1080","PlayResY: 1920","WrapStyle: 0","",
"[V4+ Styles]","Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
"Style: Baixo,Archivo Black,60,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,5,2,2,90,90,520,1",
"Style: Topo,Archivo Black,56,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,5,2,8,90,90,300,1",
"","[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
for i,s in enumerate(SEG):
    for a,b,txt in s[6]:
        A=inicio[i]+a-s[1];B=inicio[i]+b-s[1]
        estilo='Topo' if i==len(SEG)-1 and a>=4.9 else 'Baixo'
        ass.append(f"Dialogue: 0,{ts(A)},{ts(B)},{estilo},,0,0,0,,{{\\fad(60,60)}}{txt}")
open('legendas.ass','w').write('\n'.join(ass)+'\n')

cmd=['ffmpeg','-v','error','-y']
for s in SEG: cmd+=['-ss',str(s[1]),'-to',str(s[2]),'-i',V+s[0]+'.mp4']
for c in CARTOES: cmd+=['-loop','1','-framerate','30','-t',f'{TOTAL:.2f}','-i',c[0]]
cmd+=['-i','pop.wav','-i','whoosh.wav']
n=len(SEG);fc=[]
for i,s in enumerate(SEG):
    L=s[2]-s[1]
    if s[3]:
        cx,cy,z=s[3]
    else:
        cx,cy,z=0.5,0.5,1.0
    w=int(W0/z)//2*2;h=int(1272/z)//2*2
    x=int(min(max(cx*W0-w/2,0),W0-w));y=int(min(max(cy*H0-h/2,0),H0-h))
    f=f"[{i}:v]crop={w}:{h}:{x}:{y},scale=1080:1920:flags=lanczos,setsar=1,fps=30,eq=contrast=1.04:saturation=1.06,format=yuv420p"
    if s[4]: f+=",fade=t=in:st=0:d=0.35:color=white"
    if s[5]: f+=f",fade=t=out:st={L-0.15:.2f}:d=0.15:color=white"
    fc.append(f+f",setpts=PTS-STARTPTS[v{i}]")
    fc.append(f"[{i}:a]aresample=44100,afade=t=in:d=0.02,afade=t=out:st={L-0.05:.2f}:d=0.05,asetpts=PTS-STARTPTS[a{i}]")
fc.append(''.join(f"[v{i}][a{i}]" for i in range(n))+f"concat=n={n}:v=1:a=1[vc][ac]")
prev='vc'
for k,(img,tt,x,y) in enumerate(CARTOES):
    T=inicio[-1]+tt-SEG[-1][1]
    fc.append(f"[{n+k}:v]format=rgba,fade=t=in:st={T:.2f}:d=0.18:alpha=1[c{k}]")
    fc.append(f"[{prev}][c{k}]overlay=x={x}:y='{y}+50*max(0\\,1-(t-{T:.2f})/0.18)':enable='gte(t\\,{T:.2f})'[o{k}]")
    prev=f'o{k}'
fc.append(f"[{prev}]ass=legendas.ass:fontsdir=/root/.fonts[vout]")
pi=n+len(CARTOES);wi=pi+1
pops=[inicio[-1]+c[1]-SEG[-1][1] for c in CARTOES]
fc.append(f"[ac]loudnorm=I=-15:TP=-2[voz]")
fc.append(f"[{pi}:a]asplit={len(pops)}"+''.join(f"[p{j}]" for j in range(len(pops))))
for j,T in enumerate(pops): fc.append(f"[p{j}]adelay={int(T*1000)}:all=1,volume=0.45[pp{j}]")
corte=inicio[4]
fc.append(f"[{wi}:a]asplit=2[w0][w1]")
fc.append(f"[w0]atrim=start=0.45,asetpts=PTS-STARTPTS,volume=0.5[ww0]")
fc.append(f"[w1]adelay={int((corte-0.55)*1000)}:all=1,volume=0.6[ww1]")
fc.append("[voz]"+''.join(f"[pp{j}]" for j in range(len(pops)))+f"[ww0][ww1]amix=inputs={len(pops)+3}:normalize=0:duration=first,alimiter=limit=0.89[aout]")
cmd+=['-filter_complex',';'.join(fc),'-map','[vout]','-map','[aout]','-c:v','libx264','-crf','18','-preset','medium','-profile:v','high','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart','-t',f'{TOTAL:.2f}','../videos/vlog-gabriel-final-v3.mp4']
subprocess.run(cmd,check=True)
print('total',round(TOTAL,2),'cartoes em',[round(p,2) for p in pops],'corte roma',round(corte,2))

# Reel "boleto da culpa" (domingo): câmera principal com zoom lento, 2 cortes da lateral, legenda sem borda e trilha
import subprocess
from PIL import Image, ImageDraw
S='/tmp/claude-0/-home-user/f19a087c-4085-5aef-b35a-89b81156bb55/scratchpad'
V=S+'/boleto'; F=S+'/fonts'
P=V+'/v1.mov'; L=V+'/v2.mov'
W,H=1080,1920
LAT_OFF=86.48   # v2 começa no segundo 86.48 da principal (sincronizado pelo áudio)
def run(c): subprocess.run(c,check=True)

# trechos da principal (tempo de origem); some só a tentativa interrompida ("essa sim, essa... peraí")
SEG=[(1.70,5.50),(7.95,57.60),(62.20,73.40),(86.65,99.95),(104.35,111.00)]
OUT=[]; o=0.0
for a,b in SEG: OUT.append((a,b,o)); o+=b-a
TOT=round(o,2)
def m(t):
    for a,b,o0 in OUT:
        if a-0.05<=t<=b+0.05: return o0+min(max(t,a),b)-a
    return None

# lateral por cima da principal (tempo de origem)
LAT=[(93.95,95.65),(104.35,106.05)]   # takes curtos

# zoom (tempo de saída): aproximação lenta, afastamento rápido, recomeço em cada corte
K=[(0,1.0),(3.8,1.12),(3.81,1.0),(15.5,1.15),(15.9,1.0),(30.0,1.18),(30.4,1.02),(50.8,1.20),(53.44,1.28),
   (53.45,1.0),(64.64,1.15),(64.65,1.05),(77.94,1.22),(77.95,1.12),(TOT,1.30)]
expr=str(K[-1][1])
for (t0,z0),(t1,z1) in reversed(list(zip(K,K[1:]))):
    u=f"((it-{t0})/({t1}-{t0}))"
    expr=f"if(lt(it,{t1}),{z0}+({z1}-{z0})*(3*{u}*{u}-2*{u}*{u}*{u}),{expr})"

# degradê atrás das legendas e do título
g=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(g)
for y in range(H):
    a=0
    if 1080<=y<1700: a=int(150*min(1,(y-1080)/220)*min(1,(1700-y)/200))
    if y<620: a=max(a,int(130*(1-y/620)))
    d.line([(0,y),(W,y)],fill=(0,0,0,a))
g.save(V+'/degrade.png')

def ts(s):
    h,mi,r=s.split(':'); sec,ms=r.split(','); return int(h)*3600+int(mi)*60+int(sec)+int(ms)/1000
def fmt(t): return f'{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}'
HOOK_FIM=5.6
ev=[]
for blk in open(V+'/principal.srt',encoding='utf-8').read().strip().split('\n\n'):
    l=blk.split('\n'); a,b=[ts(x.strip()) for x in l[1].split('-->')]; txt=' '.join(l[2:])
    a,b=m(a),m(b)
    if a is None or b<=HOOK_FIM: continue   # o gancho já está escrito no topo
    pal=txt.split(); n=len(pal); ch=[]; i=0
    while i<n:
        k=min(4,n-i)
        if n-i-k==1: k+=1
        ch.append(' '.join(pal[i:i+k])); i+=k
    tot=sum(len(c) for c in ch); t=a
    for c in ch:
        dt=(b-a)*len(c)/tot; ev.append((t,t+dt,c)); t+=dt
lin=[f'Dialogue: 0,{fmt(a)},{fmt(b)},Leg,,0,0,0,,{c.upper()}' for a,b,c in ev]
ass=f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Leg,Merriweather Black,78,&H00ECE8EA,&H00ECE8EA,&H00000000,&H8C000000,0,0,0,0,100,100,1,0,1,0,3,2,80,80,520,1
Style: Topo,Merriweather Black,84,&H00ECE8EA,&H00ECE8EA,&H00000000,&H8C000000,0,0,0,0,100,100,1,0,1,0,3,8,70,70,200,1
Style: Cursiva,Satisfy,140,&H008E9FE2,&H008E9FE2,&H00000000,&H8C000000,0,0,0,0,100,100,0,0,1,0,3,8,70,70,318,1
Style: Arroba,Merriweather,40,&H30ECE8EA,&H30ECE8EA,&H00000000,&H8C000000,0,1,0,0,100,100,1,0,1,0,2,2,70,70,440,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 1,{fmt(0)},{fmt(HOOK_FIM)},Topo,,0,0,0,,{{\\fad(150,200)}}A MULHER QUE PAGA TUDO EM DIA É A MAIS ENDIVIDADA DA FAMÍLIA.
Dialogue: 1,{fmt(m(8.40))},{fmt(HOOK_FIM)},Cursiva,,0,0,0,,{{\\fad(120,200)}}em culpa.
Dialogue: 1,{fmt(HOOK_FIM)},{fmt(TOT)},Arroba,,0,0,0,,@giselehedler
"""+'\n'.join(lin)+'\n'
open(V+'/leg.ass','w',encoding='utf-8').write(ass)

# cortes da lateral: gira (automático), recorta 9:16 e aproxima devagar
for i,(a,b) in enumerate(LAT):
    dd=b-a+0.1
    vf=(f"crop=iw:'iw*16/9':0:'(ih-iw*16/9)/2',scale={2*W}:{2*H}:flags=lanczos,"
        f"zoompan=z='1.50+0.06*on/({dd}*30)':x='iw*0.64-iw/zoom/2':y='ih*0.49-ih/zoom/2':d=1:s={W}x{H}:fps=30,setsar=1")
    run(['ffmpeg','-loglevel','error','-y','-ss',f'{a-LAT_OFF:.3f}','-t',f'{dd:.3f}','-i',L,'-an','-vf',vf,
         '-c:v','libx264','-preset','veryfast','-crf','18',V+f'/lat{i}.mp4'])

# base: junta os trechos da principal (vídeo + áudio)
fc=''.join(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS,fps=30[v{i}];[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS[a{i}];" for i,(a,b) in enumerate(SEG))
fc+=''.join(f"[v{i}][a{i}]" for i in range(len(SEG)))+f"concat=n={len(SEG)}:v=1:a=1[v][a]"
run(['ffmpeg','-loglevel','error','-y','-i',P,'-filter_complex',fc,'-map','[v]','-map','[a]',
     '-c:v','libx264','-preset','veryfast','-crf','14','-c:a','pcm_s16le',V+'/base.mov'])

# áudio: voz normalizada + trilha baixa que abaixa quando ela fala
run(['ffmpeg','-loglevel','error','-y','-i',V+'/base.mov','-map','0:a','-af','aresample=48000,loudnorm=I=-14:TP=-1.5:LRA=11','-c:a','pcm_s16le',V+'/ln.wav'])
run(['ffmpeg','-loglevel','error','-y','-i',V+'/ln.wav','-i',V+'/musica.wav','-filter_complex',
     f"[0:a]asplit=2[voz][sc];[1:a]aresample=48000,atrim=0:{TOT},volume=0.20,afade=t=out:st={TOT-2.5}:d=2.5[mus];"
     f"[mus][sc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=400[musd];"
     f"[voz][musd]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.89",'-c:a','pcm_s16le',V+'/audio_final.wav'])

fc=(f"[0:v]scale={2*W}:{2*H}:flags=lanczos,zoompan=z='{expr}':x='iw/2-iw/zoom/2':y='(ih-ih/zoom)*0.28':d=1:s={W}x{H}:fps=30,setsar=1[w0];"
    +"".join(f"[{1+i}:v]setpts=PTS-STARTPTS+{m(a)}/TB[l{i}];[w{i}][l{i}]overlay=enable='between(t,{m(a)},{m(b)})':eof_action=pass[w{i+1}];" for i,(a,b) in enumerate(LAT))
    +f"[w{len(LAT)}][{1+len(LAT)}:v]overlay[v4];[v4]ass={V}/leg.ass:fontsdir={F}[v]")
run(['ffmpeg','-loglevel','error','-y','-i',V+'/base.mov',*sum([['-i',V+f'/lat{i}.mp4'] for i in range(len(LAT))],[]),
     '-loop','1','-t',str(TOT),'-i',V+'/degrade.png','-i',V+'/audio_final.wav',
     '-filter_complex',fc,'-map','[v]','-map',f'{2+len(LAT)}:a','-t',str(TOT),
     '-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',
     V+'/reel-boleto-v1.mp4'])
print('ok',TOT)

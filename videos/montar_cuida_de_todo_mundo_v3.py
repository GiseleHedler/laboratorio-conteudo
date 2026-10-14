# Reel "cuida de todo mundo" v3: edição do CapCut + zoom suave, B-rolls, legenda sem borda e trilha
import subprocess
from PIL import Image, ImageDraw
S='/tmp/claude-0/-home-user/f19a087c-4085-5aef-b35a-89b81156bb55/scratchpad'
V=S+'/reel/v3'; B=S+'/reel/build'; F=S+'/fonts'
SRC=V+'/novo'; CUP='/root/.claude/uploads/f19a087c-4085-5aef-b35a-89b81156bb55/073f74a6-Close-up-of-a-mature-woman-s-hands-arou.mp4'
W,H=1080,1920; TOT=63.2
CARD=(52.0,56.0)
def run(c): subprocess.run(c,check=True)

# zoom: (tempo, fator) com interpolação linear; trechos curtos = afastamento rápido
K=[(0,1.0),(2.2,1.07),(2.21,1.0),(9.2,1.10),(9.21,1.0),(19.95,1.04),(23.1,1.14),(23.45,1.0),
   (25.1,1.0),(33.3,1.12),(33.6,1.22),(37.8,1.26),(38.15,1.0),(43.7,1.10),(46.6,1.30),(46.95,1.0),
   (52.0,1.06),(52.01,1.0),(56.0,1.0),(63.2,1.08)]
expr=str(K[-1][1])
for (t0,z0),(t1,z1) in reversed(list(zip(K,K[1:]))):
    expr=f"if(lt(t,{t1}),{z0}+({z1}-{z0})*(t-{t0})/({t1}-{t0}),{expr})"

# degradê atrás das legendas (no lugar da borda nas letras)
g=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(g)
for y in range(H):
    a=0
    if 1080<=y<1700: a=int(150*min(1,(y-1080)/220)*min(1,(1700-y)/200))
    if y<520: a=max(a,int(120*(1-y/520)))
    d.line([(0,y),(W,y)],fill=(0,0,0,a))
g.save(V+'/degrade.png')

# legendas a partir do SRT da edição
def ts(s):
    h,m,r=s.split(':'); sec,ms=r.split(','); return int(h)*3600+int(m)*60+int(sec)+int(ms)/1000
def fmt(t): return f'{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}'
ev=[]
for blk in open(V+'/capcut.srt',encoding='utf-8').read().strip().split('\n\n'):
    l=blk.split('\n'); a,b=[ts(x.strip()) for x in l[1].split('-->')]; txt=' '.join(l[2:])
    pal=txt.split(); n=len(pal); ch=[]; i=0
    while i<n:
        k=min(4,n-i)
        if n-i-k==1: k+=1
        ch.append(' '.join(pal[i:i+k])); i+=k
    tot=sum(len(c) for c in ch); t=a
    for c in ch:
        dt=(b-a)*len(c)/tot; ev.append((t,t+dt,c)); t+=dt
lin=[]
for a,b,c in ev:
    if b>CARD[0] and a<CARD[1]: continue   # o card da Quinta já traz o texto
    lin.append(f'Dialogue: 0,{fmt(a)},{fmt(b)},Leg,,0,0,0,,{c.upper()}')
ass=f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Leg,Merriweather Black,78,&H00ECE8EA,&H00ECE8EA,&H00000000,&H8C000000,0,0,0,0,100,100,1,0,1,0,3,2,80,80,520,1
Style: Topo,Merriweather Black,72,&H00ECE8EA,&H00ECE8EA,&H00000000,&H8C000000,0,0,0,0,100,100,1,0,1,0,3,8,70,70,210,1
Style: Cursiva,Satisfy,104,&H008E9FE2,&H008E9FE2,&H00000000,&H8C000000,0,0,0,0,100,100,0,0,1,0,3,8,70,70,250,1
Style: Cta,Merriweather Black,76,&H00ECE8EA,&H00ECE8EA,&H00703BB5,&H00703BB5,0,0,0,0,100,100,1,0,3,22,0,2,70,70,700,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 1,{fmt(0)},{fmt(2.9)},Topo,,0,0,0,,ELA CUIDA DE TODO MUNDO.
Dialogue: 1,{fmt(0)},{fmt(2.9)},Cursiva,,0,0,0,,e quando é a vez dela?
Dialogue: 1,{fmt(59.9)},{fmt(TOT)},Cta,,0,0,0,,COMENTA 5524
"""+'\n'.join(lin)+'\n'
open(V+'/leg.ass','w',encoding='utf-8').write(ass)

c0,c1=2.2,4.1; p0,p1=9.2,14.5; g0,g1=14.75,19.95
fc=(f"[0:v]scale=w='trunc({W}*({expr})/2)*2':h='trunc({H}*({expr})/2)*2':eval=frame:flags=bicubic,"
    f"crop={W}:{H}:(iw-{W})/2:(ih-{H})*0.28,setsar=1,fps=30[base];"
    f"[1:v]trim=0:{c1-c0+0.05},setpts=PTS-STARTPTS+{c0}/TB,scale={W}:{H},fps=30[cup];"
    f"[base][cup]overlay=enable='between(t,{c0},{c1})':eof_action=pass[v1];"
    f"[3:v]trim=0:{p1-p0+0.05},setpts=PTS-STARTPTS+{p0}/TB[pan];"
    f"[v1][pan]overlay=enable='between(t,{p0},{p1})':eof_action=pass[v2];"
    f"[2:v]format=rgba,fade=t=in:st={g0}:d=0.25:alpha=1[ch];"
    f"[v2][ch]overlay=enable='between(t,{g0},{g1})'[v3];"
    f"[v3][4:v]overlay=enable='not(between(t,{CARD[0]},{CARD[1]}))'[v4];"
    f"[v4]ass={V}/leg.ass:fontsdir={F}[v];"
    # trilha: baixa, abaixa mais quando ela fala (sidechain), some no card não
    f"[0:a]aresample=48000,loudnorm=I=-14:TP=-1.5:LRA=11,asplit=2[voz][sc];"
    f"[5:a]aresample=48000,volume=0.22,atrim=0:{TOT},afade=t=out:st={TOT-2.5}:d=2.5[mus];"
    f"[mus][sc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=400[musd];"
    f"[voz][musd]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.89[a]")
run(['ffmpeg','-loglevel','error','-y','-i',SRC,'-i',CUP,'-loop','1','-t',str(TOT),'-i',B+'/chat.png',
     '-i',B+'/panela.mp4','-loop','1','-t',str(TOT),'-i',V+'/degrade.png','-i',V+'/musica.wav',
     '-filter_complex',fc,'-map','[v]','-map','[a]','-t',str(TOT),
     '-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',
     V+'/reel-cuida-de-todo-mundo-v3.mp4'])
print('ok')

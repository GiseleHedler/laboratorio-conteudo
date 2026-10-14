import subprocess, os, re
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S='/tmp/claude-0/-home-user/f19a087c-4085-5aef-b35a-89b81156bb55/scratchpad'
R=S+'/reel'; B=R+'/build'; F=S+'/fonts'
SRC=R+'/v.mov'
CUP='/root/.claude/uploads/f19a087c-4085-5aef-b35a-89b81156bb55/073f74a6-Close-up-of-a-mature-woman-s-hands-arou.mp4'
W,H=1080,1920
def run(c): subprocess.run(c,check=True)

# (ini, fim, zoom) no tempo do arquivo original
SEG=[(0.25,4.40,1.0),(5.00,10.25,1.12),(12.80,18.30,1.0),(21.05,26.60,1.0),
     (29.45,35.00,1.12),(35.00,44.40,1.0),(44.40,48.90,1.16),(48.90,54.80,1.0),
     (54.80,58.00,1.22),(58.00,74.60,1.0)]
def mapt(t):
    acc=0
    for a,b,z in SEG:
        if a<=t<=b: return acc+(t-a)
        acc+=b-a
    return None

parts=[]
for i,(a,b,z) in enumerate(SEG):
    w=int(720/z)//2*2; h=int(1280/z)//2*2; x=(720-w)//2; y=int((1280-h)*0.3)
    d=b-a; o=f'{B}/s{i}.mp4'
    run(['ffmpeg','-loglevel','error','-y','-ss',str(a),'-t',str(d),'-i',SRC,
         '-vf',f'crop={w}:{h}:{x}:{y},scale={W}:{H}:flags=lanczos,setsar=1,fps=30',
         '-af',f'afade=t=in:d=0.03,afade=t=out:st={d-0.04}:d=0.04,aresample=48000',
         '-c:v','libx264','-preset','veryfast','-crf','18','-c:a','aac','-b:a','192k',o])
    parts.append(o)
open(B+'/lista.txt','w').write(''.join(f"file '{p}'\n" for p in parts))
run(['ffmpeg','-loglevel','error','-y','-f','concat','-safe','0','-i',B+'/lista.txt','-c','copy',B+'/corte.mp4'])
TOT=sum(b-a for a,b,z in SEG)

# tela do grupo da família
def chat():
    im=Image.new('RGBA',(W,H),(10,8,25,150)); d=ImageDraw.Draw(im)
    px,py,pw,ph=150,330,780,1120
    d.rounded_rectangle((px,py,px+pw,py+ph),60,fill=(236,229,221,255))
    d.rounded_rectangle((px,py,px+pw,py+170),60,fill=(36,23,81,255)); d.rectangle((px,py+110,px+pw,py+170),fill=(36,23,81,255))
    f1=ImageFont.truetype(F+'/Figtree-Medium.ttf',46); f2=ImageFont.truetype(F+'/Figtree-Medium.ttf',34); f3=ImageFont.truetype(F+'/Figtree-Medium.ttf',38)
    d.ellipse((px+40,py+45,px+120,py+125),fill=(226,159,142,255))
    d.text((px+145,py+50),'Família',font=f1,fill=(255,255,255)); d.text((px+145,py+105),'14 participantes',font=f2,fill=(210,205,225))
    def bolha(y,quem,txt,hora,direita=False):
        tw=max(d.textlength(txt,font=f3),d.textlength(quem,font=f2) if quem else 0)+60
        bx=px+pw-40-tw if direita else px+40
        hh=150 if quem else 115
        d.rounded_rectangle((bx,y,bx+tw,y+hh),24,fill=(217,246,204,255) if direita else (255,255,255,255))
        yy=y+14
        if quem: d.text((bx+30,yy),quem,font=f2,fill=(181,59,112)); yy+=42
        d.text((bx+30,yy),txt,font=f3,fill=(30,30,30))
        d.text((bx+tw-90,y+hh-38),hora,font=ImageFont.truetype(F+'/Figtree-Medium.ttf',26),fill=(120,120,120))
        return y+hh+28
    y=py+220
    y=bolha(y,'Mãe','Alguém viu meus óculos?','19:02')
    y=bolha(y,'Cunhada','Quem leva a sobremesa domingo?','20:15')
    y=bolha(y,'Irmão','Mana, me empresta o carro amanhã?','20:41')
    y+=30
    y2=bolha(y,None,'Gente, hoje é meu aniversário.','21:47',True)
    d.text((px+pw-330,y2-14),'Visualizada por 13',font=f2,fill=(110,110,110))
    im.save(B+'/chat.png')
chat()

# legendas (ASS) a partir do SRT exportado do Descript, com o atraso de 0,7 s corrigido
srt=open(R+'/legenda.srt',encoding='utf-8').read()
def ts(s):
    h,m,r=s.split(':'); sec,ms=r.split(','); return int(h)*3600+int(m)*60+int(sec)+int(ms)/1000
blocos=[]
for blk in srt.strip().split('\n\n'):
    l=blk.split('\n'); a,b=[ts(x.strip()) for x in l[1].split('-->')]
    txt=' '.join(l[2:]).replace('Speaker: ','').strip()
    blocos.append((a-0.7,b-0.7,txt))
# junta blocos quebrados no meio da frase
ev=[]
for a,b,txt in blocos:
    pal=txt.split(); n=len(pal); chunks=[]; i=0
    while i<n:
        k=min(4,n-i)
        if n-i-k==1: k+=1
        chunks.append(pal[i:i+k]); i+=k
    tot=sum(len(' '.join(c)) for c in chunks); t=a
    for c in chunks:
        dt=(b-a)*len(' '.join(c))/tot
        ev.append((t,t+dt,' '.join(c))); t+=dt
def fmt(t):
    h=int(t//3600); m=int(t%3600//60); s=t%60; return f'{h}:{m:02d}:{s:05.2f}'
lin=[]
for a,b,txt in ev:
    ma,mb=mapt(min(max(a,0.26),74.5)),mapt(min(b,74.59))
    if ma is None or mb is None or mb<=ma: 
        # ajusta para o segmento mais próximo
        for x,y,z in SEG:
            if x-0.6<=a<=y: ma=mapt(max(a,x)); mb=mapt(min(b,y)); break
    if ma is None or mb is None or mb<=ma: continue
    txt=txt.upper().replace('"','')
    lin.append(f'Dialogue: 0,{fmt(ma)},{fmt(mb)},Leg,,0,0,0,,{txt}')
CTA=mapt(58.30); CTA2=mapt(71.45)
ass=f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Leg,Merriweather,74,&H00ECE8EA,&H00ECE8EA,&H00511724,&H80000000,1,0,0,0,100,100,0,0,1,8,2,2,70,70,560,1
Style: Topo,Merriweather,70,&H00ECE8EA,&H00ECE8EA,&H00511724,&H80000000,1,0,0,0,100,100,0,0,1,7,2,8,70,70,230,1
Style: Cursiva,Satisfy,100,&H008E9FE2,&H008E9FE2,&H00511724,&H80000000,0,0,0,0,100,100,0,0,1,5,2,8,70,70,292,1
Style: Cta,Merriweather,78,&H00ECE8EA,&H00ECE8EA,&H00703BB5,&H00703BB5,1,0,0,0,100,100,0,0,3,22,0,2,70,70,720,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 1,{fmt(0)},{fmt(3.0)},Topo,,0,0,0,,ELA CUIDA DE TODO MUNDO.
Dialogue: 1,{fmt(0)},{fmt(3.0)},Cursiva,,0,0,0,,e quando é a vez dela?
Dialogue: 1,{fmt(CTA)},{fmt(TOT)},Topo,,0,0,0,,QUINTA · 18:59
Dialogue: 1,{fmt(CTA)},{fmt(TOT)},Cursiva,,0,0,0,,ao vivo e de graça
Dialogue: 1,{fmt(CTA2)},{fmt(TOT)},Cta,,0,0,0,,COMENTA 5524
"""+'\n'.join(lin)+'\n'
open(B+'/leg.ass','w',encoding='utf-8').write(ass)

# composição final: cupcake sobre "a dela, ela mesma comprou o bolo", tela do grupo sobre a mensagem
c0=mapt(2.70); c1=c0+2.6
g0=mapt(21.20); g1=mapt(26.55)
fc=(f"[1:v]trim=0:3.9,setpts=PTS-STARTPTS+{c0}/TB,scale={W}:{H},fps=30[cup];"
    f"[0:v][cup]overlay=enable='between(t,{c0},{c1})':eof_action=pass[v1];"
    f"[2:v]format=rgba,fade=t=in:st={g0}:d=0.25:alpha=1[ch];"
    f"[v1][ch]overlay=enable='between(t,{g0},{g1})'[v2];"
    f"[v2]ass={B}/leg.ass:fontsdir={F}[v]")
run(['ffmpeg','-loglevel','error','-y','-i',B+'/corte.mp4','-i',CUP,'-loop','1','-t',str(TOT),'-i',B+'/chat.png',
     '-filter_complex',fc,'-map','[v]','-map','0:a','-af','loudnorm=I=-14:TP=-1.5:LRA=11',
     '-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',
     R+'/reel-cuida-de-todo-mundo-v1.mp4'])
print('total',round(TOT,2),'cup',round(c0,2),'chat',round(g0,2),round(g1,2),'cta',round(CTA,2))

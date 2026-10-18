# Reel "O alfaiate da Mentira" (fábula): mesmo estilo do boleto, com uma câmera só
import subprocess, re
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S='/tmp/claude-0/-home-user/f19a087c-4085-5aef-b35a-89b81156bb55/scratchpad'
V=S+'/alfaiataria'; F=S+'/fonts'
P=V+'/v1.mov'
W,H=1080,1920
def run(c): subprocess.run(c,check=True)

# começa no "Era uma vez" certo (o primeiro saiu errado) e vai até o fim da fala
BLOCOS=[(1.74,64.95)]
# corta todas as pausas; nas que contam a história, fica um respiro (início do silêncio, duração)
PRE,POS=0.10,0.12
RESPIRO={59.62:0.75}   # antes de "E a Verdade passou"
r=subprocess.run(['ffmpeg','-i',P,'-af','silencedetect=n=-40dB:d=0.25','-f','null','-'],capture_output=True,text=True).stderr
sil=list(zip([float(x) for x in re.findall(r'silence_start: ([0-9.]+)',r)],[float(x) for x in re.findall(r'silence_end: ([0-9.]+)',r)]))
SEG=[]
for a,b in BLOCOS:
    cur=a
    for s0,s1 in sil:
        c0,c1=s0+POS,s1-PRE
        k=next((v for t,v in RESPIRO.items() if abs(t-s0)<0.3),None)
        if k is not None: c0,c1=s0+k/2,s1-k/2
        if c1-c0<0.05 or c1<=cur or c0>=b: continue
        if c0>cur: SEG.append((round(cur,3),round(c0,3)))
        cur=max(cur,c1)
    if b>cur: SEG.append((round(cur,3),round(b,3)))
# fora pedacinhos sem fala (respiração, barulho): curtos e fora de qualquer frase da transcrição
FALAS=[tuple(sum(int(x)*k for x,k in zip(re.split('[:,]',t.strip()),(3600,60,1,0.001))) for t in l.split('-->'))
       for l in open(V+'/alfaiataria.srt',encoding='utf-8') if '-->' in l]
SEG=[(a,b) for a,b in SEG if b-a>0.12 and (b-a>=0.45 or any(f0<b and f1>a for f0,f1 in FALAS))]
SEG[-1]=(SEG[-1][0],SEG[-1][1]+1.0)   # ela em silêncio um segundo no fim
OUT=[]; o=0.0
for a,b in SEG: OUT.append((a,b,o)); o+=b-a
TOT=round(o,2)
def m(t):
    """tempo de origem -> tempo no vídeo final (o mais próximo, se cair num corte)"""
    best=None
    for a,b,o0 in OUT:
        if a<=t<=b: return o0+t-a
        x,y=(o0,a) if t<a else (o0+b-a,b)
        if best is None or abs(t-y)<best[0]: best=(abs(t-y),x)
    return best[1]

# zoom (tempo de origem): ela gravou de longe, então parte já aproximado e vai chegando devagar;
# afastamento rápido em dois respiros da história
KS=[(1.74,1.30),(20.6,1.46),(21.0,1.32),(46.5,1.52),(49.43,1.38),(59.62,1.60),(60.6,1.42),(TOT+50,1.58)]
K=[]
for t,z in KS:
    ot=m(t) if t<100 else TOT
    if K and ot<=K[-1][0]+0.005: ot=K[-1][0]+0.01
    K.append((round(ot,3),z))
K[0]=(0,K[0][1])
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
HOOK_FIM=round(m(8.3),2)
PRETA=[('E bastou um fio.',m(49.43),m(51.18))]
ev=[]
for blk in open(V+'/alfaiataria.srt',encoding='utf-8').read().strip().split('\n\n'):
    l=blk.split('\n'); a,b=[ts(x.strip()) for x in l[1].split('-->')]; txt=' '.join(l[2:])
    a,b=m(a),m(b)
    pal=txt.split(); n=len(pal); ch=[]; i=0
    while i<n:
        k=min(4,n-i)
        if n-i-k==1: k+=1
        ch.append(' '.join(pal[i:i+k])); i+=k
    tot=sum(len(c) for c in ch); t=a
    for c in ch:
        dt=(b-a)*len(c)/tot
        if t+dt>HOOK_FIM: ev.append((max(t,HOOK_FIM),t+dt,c))   # o gancho já está escrito no topo
        t+=dt
lin=[f'Dialogue: 0,{fmt(a)},{fmt(b)},Leg,,0,0,0,,{c}' for a,b,c in ev if b-a>0.1 and not any(a<p1-0.05 and b>p0+0.05 for _,p0,p1 in PRETA)]
arroba=''.join(f'Dialogue: 1,{fmt(x)},{fmt(y)},Arroba,,0,0,0,,@giselehedler\n' for x,y in zip([HOOK_FIM]+[p1 for _,p0,p1 in PRETA],[p0 for _,p0,p1 in PRETA]+[TOT]))
ass=f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Leg,Merriweather Black,78,&H00ECE8EA,&H00ECE8EA,&H00000000,&H8C000000,0,0,0,0,100,100,1,0,1,0,3,2,80,80,520,1
Style: Topo,Merriweather Black,84,&H00ECE8EA,&H00ECE8EA,&H00000000,&H8C000000,0,0,0,0,100,100,1,0,1,0,3,8,70,70,100,1
Style: Arroba,Merriweather,40,&H30ECE8EA,&H30ECE8EA,&H00000000,&H8C000000,0,1,0,0,100,100,1,0,1,0,2,2,70,70,440,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 1,{fmt(0)},{fmt(HOOK_FIM)},Topo,,0,0,0,,{{\\fad(150,200)}}Era uma vez um alfaiate que só tinha uma cliente:
"""+arroba+'\n'.join(lin)+'\n'
open(V+'/leg.ass','w',encoding='utf-8').write(ass)

# áudio: corta igual ao vídeo, voz normalizada, eco na tela preta e trilha baixa que abaixa quando ela fala
fc=''.join(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS,fps=30[v{i}];[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS[a{i}];" for i,(a,b) in enumerate(SEG))
fc+=''.join(f"[v{i}][a{i}]" for i in range(len(SEG)))+f"concat=n={len(SEG)}:v=1:a=1[v][a]"
run(['ffmpeg','-loglevel','error','-y','-i',P,'-filter_complex',fc,'-map','[v]','-map','[a]',
     '-c:v','libx264','-preset','veryfast','-crf','14','-c:a','pcm_s16le',V+'/base.mov'])
PG='+'.join(f'between(t,{p0:.3f},{p1:.3f})' for _,p0,p1 in PRETA)
run(['ffmpeg','-loglevel','error','-y','-i',V+'/base.mov','-map','0:a','-af','aresample=48000,loudnorm=I=-14:TP=-1.5:LRA=11','-c:a','pcm_s16le',V+'/ln.wav'])
run(['ffmpeg','-loglevel','error','-y','-i',V+'/ln.wav','-i',S+'/boleto/musica.wav','-filter_complex',
     f"[0:a]asplit=3[v0][w0][sc];"
     f"[v0]volume='1-({PG})':eval=frame[seco];[w0]volume='{PG}':eval=frame,aecho=0.8:0.85:90|180|270:0.45|0.30|0.18,highpass=f=180,volume=1.3[eco];"
     f"[seco][eco]amix=inputs=2:normalize=0:duration=first[voz];"
     f"[1:a]aresample=48000,atrim=0:{TOT},volume=0.20,afade=t=out:st={TOT-1.5}:d=1.5[mus];"
     f"[mus][sc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=400[musd];"
     f"[voz][musd]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.89",'-c:a','pcm_s16le',V+'/audio_final.wav'])

# palavras em cursiva grande pegando o topo da cabeça (recorte da pessoa quadro a quadro)
ATRAS=[('a Mentira.',m(5.30),HOOK_FIM,250),('remendo',m(18.60),m(20.9),330),
       ('Verdade',m(31.14),m(34.5),330),('nua.',m(57.40),m(59.62)+0.3,560)]
fc=f"[0:v]scale={2*W}:{2*H}:flags=lanczos,zoompan=z='{expr}':x='iw/2-iw/zoom/2':y='(ih-ih/zoom)*0.57':d=1:s={W}x{H}:fps=30,setsar=1[v]"
p1=subprocess.Popen(['ffmpeg','-loglevel','error','-i',V+'/base.mov','-filter_complex',fc,'-map','[v]','-t',str(TOT),
     '-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
p2=subprocess.Popen(['ffmpeg','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','30','-i','-',
     '-loop','1','-t',str(TOT),'-i',V+'/degrade.png','-i',V+'/audio_final.wav',
     '-filter_complex',f"[0:v][1:v]overlay[v4];[v4]ass={V}/leg.ass:fontsdir={F}[v]",'-map','[v]','-map','2:a','-t',str(TOT),
     '-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',
     V+'/reel-alfaiataria.mp4'],stdin=subprocess.PIPE)
import numpy as np, mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
seg=vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=BaseOptions(model_asset_path=S+'/seg.tflite'),output_confidence_masks=True))
def camada(txt,tam,topo_cabeca):
    f=ImageFont.truetype(F+'/Satisfy-400-normal.ttf',tam)
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    bb=d.textbbox((0,0),txt,font=f); tw,th=bb[2]-bb[0],bb[3]-bb[1]
    cy=max(topo_cabeca+0.16*th,th/2+40)   # letras pegando o topo da cabeça
    pos=((W-tw)/2-bb[0],cy-th/2-bb[1])
    # sombra escura larga: a estante atrás é colorida e a cursiva sumia
    sh=Image.new('RGBA',(W,H),(0,0,0,0)); ImageDraw.Draw(sh).text((pos[0]+3,pos[1]+5),txt,font=f,fill=(20,8,30,215),stroke_width=9,stroke_fill=(20,8,30,215))
    lay=Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)),lay)
    ImageDraw.Draw(lay).text(pos,txt,font=f,fill=(0xe2,0x9f,0x8e,255))
    return np.array(lay).astype(np.float32)/255
FB=W*H*3; n=0; ativo=None; prev=None
while True:
    buf=p1.stdout.read(FB)
    if len(buf)<FB: break
    t=n/30; n+=1
    pr=next((x for x in PRETA if x[1]<=t<x[2]),None)
    if pr:
        k=min(1,(t-pr[1])/0.35); tam=int(120*(1.10-0.10*(3*k*k-2*k**3)))
        fr=Image.new('RGB',(W,H),(0,0,0)); d=ImageDraw.Draw(fr); fo=ImageFont.truetype(F+'/ArchivoBlack.ttf',tam)
        bb=d.textbbox((0,0),pr[0],font=fo); d.text(((W-bb[2]-bb[0])/2,(H-bb[3]-bb[1])/2-60),pr[0],font=fo,fill=(0xea,0xe8,0xec))
        p2.stdin.write(fr.tobytes()); continue
    w=next((x for x in ATRAS if x[1]<=t<x[2]),None)
    if w is None:
        ativo=prev=None; p2.stdin.write(buf); continue
    im=np.frombuffer(buf,np.uint8).reshape(H,W,3)
    cm=[c.numpy_view()[...,0] for c in seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB,data=np.ascontiguousarray(im))).confidence_masks]
    pessoa=1-cm[0]
    if ativo is not w:
        ys=np.where(((cm[1]+cm[3])>0.5).any(1))[0]
        lay=camada(w[0],w[3],ys.min() if len(ys) else 400); ativo=w; prev=pessoa
    pessoa=0.6*pessoa+0.4*prev; prev=pessoa
    mk=np.clip((pessoa-0.35)/0.3,0,1)
    mk=np.array(Image.fromarray((mk*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5))).astype(np.float32)/255
    fade=min(1,(t-w[1])/0.25)*(1 if w[2]>=TOT-0.01 else min(1,(w[2]-t)/0.15))
    a=lay[...,3]*(1-mk)*fade
    out=im*(1-a[...,None])+lay[...,:3]*255*a[...,None]
    p2.stdin.write(out.astype(np.uint8).tobytes())
p2.stdin.close(); p2.wait(); p1.wait()
print('ok',TOT)

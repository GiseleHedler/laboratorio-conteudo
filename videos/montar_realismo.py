# Reel "direita x esquerda" (realismo ingênuo e crença): mesmo estilo do alfaiate, uma câmera só
import subprocess, re
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S='/tmp/claude-0/-home-user/f19a087c-4085-5aef-b35a-89b81156bb55/scratchpad'
V=S+'/realismo'; F=S+'/fonts'
P=V+'/proxy.mov'   # o original (1440x2560, 60 quadros) convertido para 1080x1920, 30 quadros: a montagem direto do original estourava a memória
W,H=1080,1920
def run(c): subprocess.run(c,check=True)

# some só o final errado e recomeçado ("pera aí... volta... espera")
BLOCOS=[(0.70,133.93),(154.05,163.95)]
# corta todas as pausas; nas que contam a história, fica um respiro (início do silêncio, duração)
PRE,POS=0.10,0.12
RESPIRO={}
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
       for l in open(V+'/realismo.srt',encoding='utf-8') if '-->' in l]
SEG=[(a,b) for a,b in SEG if b-a>0.12 and (b-a>=0.45 or any(f0<b and f1>a for f0,f1 in FALAS))]
SEG[-1]=(SEG[-1][0],SEG[-1][1]+1.0)
SEG=[(round(a*30)/30,round(b*30)/30) for a,b in SEG]   # cortes no quadro exato: a junção não escorrega o áudio   # ela em silêncio um segundo no fim
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
# aproximação lenta e afastamento rápido em cada virada do texto
KS=[(0.70,1.30),(11.3,1.45),(12.6,1.30),(16.6,1.42),(17.3,1.30),(46.1,1.50),(46.5,1.32),(71.2,1.48),(74.0,1.30),
    (100.2,1.50),(101.5,1.32),(133.9,1.55),(154.05,1.38),(TOT+500,1.56)]
K=[]
for t,z in KS:
    ot=m(t) if t<400 else TOT
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
BIPE=[(4.98,5.24),(10.94,11.36)]
HOOK_FIM=round(m(11.9),2)   # título no topo durante o gancho; a legenda corre junto
PRETA=[]   # tela preta testada e tirada: no clímax quem faz o peso é o silêncio da música
ev=[]
for blk in open(V+'/realismo.srt',encoding='utf-8').read().strip().split('\n\n'):
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
        ev.append((t,t+dt,c))
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
Dialogue: 1,{fmt(0)},{fmt(HOOK_FIM)},Topo,,0,0,0,,{{\\fad(150,200)}}O que a direita pensa da esquerda. E o contrário.
"""+arroba+'\n'.join(lin)+'\n'
open(V+'/leg.ass','w',encoding='utf-8').write(ass)

# áudio: corta igual ao vídeo, voz normalizada, eco na tela preta e trilha baixa que abaixa quando ela fala
# corta cada trecho num arquivo e junta (um filtro só com dezenas de trims estourava a memória)
lista=[]
for i,(a,b) in enumerate(SEG):
    f=V+f'/seg{i:02d}.mov'
    run(['ffmpeg','-loglevel','error','-y','-ss',f'{a:.3f}','-t',f'{b-a:.3f}','-i',P,'-vf','fps=30','-frames:v',str(round((b-a)*30)),
         '-c:v','libx264','-preset','veryfast','-crf','14','-c:a','pcm_s16le','-ar','48000',f])
    lista.append(f"file '{f}'")
open(V+'/segs.txt','w').write('\n'.join(lista)+'\n')
run(['ffmpeg','-loglevel','error','-y','-f','concat','-safe','0','-i',V+'/segs.txt','-c','copy',V+'/base.mov'])
run(['ffmpeg','-loglevel','error','-y','-i',V+'/base.mov','-map','0:a','-af','aresample=48000,loudnorm=I=-14:TP=-1.5:LRA=11','-c:a','pcm_s16le',V+'/ln.wav'])
# bipe: some a voz na janela e entra um tom de 1 kHz no lugar
import numpy as np, wave
w=wave.open(V+'/ln.wav'); sr=w.getframerate(); ch=w.getnchannels(); x=np.frombuffer(w.readframes(w.getnframes()),np.int16).reshape(-1,ch).astype(np.float32); w.close()
for b0,b1 in BIPE:
    i0,i1=int(m(b0)*sr),int(m(b1)*sr); n=i1-i0; t=np.arange(n)/sr
    env=np.minimum(1,np.minimum(t,(n/sr)-t)/0.01)
    x[i0:i1]=(0.35*32767*np.sin(2*np.pi*1000*t)*env)[:,None]
w=wave.open(V+'/ln.wav','wb'); w.setnchannels(ch); w.setsampwidth(2); w.setframerate(sr); w.writeframes(np.clip(x,-32768,32767).astype(np.int16).tobytes()); w.close()
# trilha de piano suave (mesma do boleto, gerada no comprimento do vídeo)
run(['python3',S+'/tools/musica_realismo.py'])
run(['ffmpeg','-loglevel','error','-y','-i',V+'/ln.wav','-i',V+'/musica.wav','-filter_complex',
     f"[0:a]asplit=2[voz][sc];"
     f"[1:a]aresample=48000,atrim=0:{TOT},volume=0.16,afade=t=out:st={TOT-1.0}:d=1.0[mus];"
     f"[mus][sc]sidechaincompress=threshold=0.03:ratio=5:attack=20:release=400[musd];"
     f"[voz][musd]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.89",'-c:a','pcm_s16le',V+'/audio_final.wav'])

# palavras em cursiva grande pegando o topo da cabeça (recorte da pessoa quadro a quadro)
ATRAS=[('cego.',m(15.2),m(18.2),360),('crença',m(75.6),m(79.0),340),
       ('bolha',m(83.0),m(86.0),360),('certeza',m(131.0),m(134.0),330)]
# cenas de apoio: tela dividida com o debate (sem áudio) e o jogo de futebol na explicação do experimento
B=S+'/broll'
DEB=(m(67.78),m(71.22)); FUT=(m(49.40),m(63.30))
run(['ffmpeg','-loglevel','error','-y','-ss','4','-t',f'{DEB[1]-DEB[0]+0.2:.3f}','-i',B+'/debate.mov','-an','-vf',
     f"crop='ih*1.125':ih:'(iw-ih*1.125)/2':0,scale={W}:{H//2}:flags=lanczos,fps=30,setsar=1",'-c:v','libx264','-crf','16',V+'/deb.mp4'])
dd=FUT[1]-FUT[0]+0.2
# jogo real de 1951 (o do estudo): sem as faixas pretas, inteiro no meio da tela, com ele mesmo desfocado no fundo
run(['ffmpeg','-loglevel','error','-y','-ss','0.3','-t',f'{dd:.3f}','-i',B+'/jogo1951.mov','-an','-filter_complex',
     f"[0:v]crop=1062:654:72:4,fps=30,split=2[a][b];"
     f"[a]scale=-2:{H}:flags=lanczos,crop={W}:{H},gblur=sigma=28,eq=brightness=-0.18[fundo];"
     f"[b]scale={W}:-2:flags=lanczos,scale={int(W*2.2)}:-2,zoompan=z='1.0+0.05*on/({dd}*30)':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s={W}x{int(W*654/1062)//2*2}:fps=30[jogo];"
     f"[fundo][jogo]overlay=0:(H-h)/2-120,setsar=1",
     '-c:v','libx264','-crf','16',V+'/fut.mp4'])
fc=(f"[0:v]scale={2*W}:{2*H}:flags=lanczos,zoompan=z='{expr}':x='iw/2-iw/zoom/2':y='(ih-ih/zoom)*0.57':d=1:s={W}x{H}:fps=30,setsar=1,split=2[z0][z1];"
    f"[z1]crop={W}:{H//2}:0:{int(H*0.27)}[ela];"
    f"[1:v]setpts=PTS-STARTPTS+{DEB[0]}/TB[deb];[2:v]setpts=PTS-STARTPTS+{FUT[0]}/TB[fut];"
    f"[z0][deb]overlay=0:0:enable='between(t,{DEB[0]},{DEB[1]})':eof_action=pass[a1];"
    f"[ela]setpts=PTS[ela2];[a1][ela2]overlay=0:{H//2}:enable='between(t,{DEB[0]},{DEB[1]})'[a2];"
    f"[a2][fut]overlay=0:0:enable='between(t,{FUT[0]},{FUT[1]})':eof_action=pass[v]")
p1=subprocess.Popen(['ffmpeg','-loglevel','error','-i',V+'/base.mov','-i',V+'/deb.mp4','-i',V+'/fut.mp4','-filter_complex',fc,'-map','[v]','-t',str(TOT),
     '-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
p2=subprocess.Popen(['ffmpeg','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','30','-i','-',
     '-loop','1','-t',str(TOT),'-i',V+'/degrade.png','-i',V+'/audio_final.wav',
     '-filter_complex',f"[0:v][1:v]overlay[v4];[v4]ass={V}/leg.ass:fontsdir={F}[v]",'-map','[v]','-map','2:a','-t',str(TOT),
     '-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',
     V+'/reel-realismo.mp4'],stdin=subprocess.PIPE)
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
import os
FUNDO=None
if os.path.exists(S+'/fotos/lula.jpg') and os.path.exists(S+'/fotos/bolsonaro.jpg'):
    def metade(f):
        im=Image.open(f).convert('RGB'); w0,h0=im.size; alvo=(W//2)/H
        if w0/h0>alvo: nw=int(h0*alvo); im=im.crop(((w0-nw)//2,0,(w0-nw)//2+nw,h0))
        else: nh=int(w0/alvo); y0=int((h0-nh)*0.25); im=im.crop((0,y0,w0,y0+nh))
        return im.resize((W//2,H),Image.LANCZOS)
    fu=Image.new('RGB',(W,H)); fu.paste(metade(S+'/fotos/lula.jpg'),(0,0)); fu.paste(metade(S+'/fotos/bolsonaro.jpg'),(W//2,0))
    FUNDO=np.array(fu).astype(np.float32)*0.85
FUNDO_FIM=m(11.40)
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
    if FUNDO is not None and t<FUNDO_FIM:
        im=np.frombuffer(buf,np.uint8).reshape(H,W,3).astype(np.float32)
        pm=1-seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB,data=np.ascontiguousarray(im.astype(np.uint8)))).confidence_masks[0].numpy_view()[...,0]
        pm=np.clip((pm-0.35)/0.3,0,1); pm=np.array(Image.fromarray((pm*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5))).astype(np.float32)/255
        fade=min(1,(FUNDO_FIM-t)/0.3)
        out=im*pm[...,None]+(FUNDO*fade+im*(1-fade))*(1-pm[...,None])
        p2.stdin.write(out.astype(np.uint8).tobytes()); continue
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

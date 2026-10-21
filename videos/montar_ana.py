# Reel "Ana Hickmann" (Quinta da Mente): falas da Gisele intercaladas com trechos da entrevista da Ana
# gancho com a Ana em tela cheia; nos outros trechos, Ana em cima e a Gisele ouvindo embaixo
import subprocess, re, numpy as np, wave
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S='/tmp/claude-0/-home-user/f19a087c-4085-5aef-b35a-89b81156bb55/scratchpad'
A=S+'/ana'; G=A+'/gravacao'; F=S+'/fonts'; T=G+'/tmp'
P=G+'/proxy.mov'   # gravação dela (1440x2560, 60 quadros) convertida para 1080x1920, 30 quadros
ANA=A+'/ana.mp4'; R4=A+'/trechos/00_rechonchuda_caveira.mp4'
W,H=1080,1920; HM=H//2
subprocess.run(['mkdir','-p',T])
def run(c): subprocess.run(c,check=True)
def dur(f): return float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f],capture_output=True,text=True).stdout)
ENC=['-r','30','-c:v','libx264','-preset','veryfast','-crf','15','-pix_fmt','yuv420p','-c:a','pcm_s16le','-ar','48000','-ac','2']

# trechos da Ana: (arquivo de origem, [(início, fim)], legenda [(início, fim, texto)] no tempo do trecho)
# o tempo entre pergunta e resposta do gancho foi encurtado
TRECHOS={
 'gancho':(ANA,[(672.66,674.62),(675.62,677.40)],[(0,1.9,'Por que que você atura tanta truculência?'),(2.0,3.74,'Eu me acostumei a dizer: é o jeito dele.')],None),
 'caveira':(R4,[(0,12.08)],[],None),   # já vem com legenda gravada no vídeo
 'velha':(ANA,[(732.95,736.35)],[(0,1.6,'Tá, mas ninguém quer uma Ana Hickmann velha.'),(2.2,3.4,'Ninguém quer uma gorda.')],560),
 'marca':(ANA,[(1320.70,1329.20)],[(0,2.3,'Essa marca que eu tenho na minha mão foi meu pai que me deu.'),(3.1,8.5,'Por isso que eu jurei que nenhum homem me tocaria pra fazer isso.')],640),
 'ninguem':(ANA,[(777.45,783.85)],[(0,3.0,'Eu achei que as pessoas fossem perceber isso, mas acho que as pessoas'),(3.0,6.4,'tavam tão acostumadas com aquela situação toda, que ninguém percebeu.')],560),
 'chega':(ANA,[(763.97,764.40),(765.73,767.58)],[(0,0.5,'Chega.'),(0.6,2.28,'Eu não sou um objeto.')],560),
}
# roteiro na ordem: falas dela (tempo da gravação), trechos da Ana com ela ouvindo (pausa da gravação usada embaixo)
ROTEIRO=[('cheia','gancho'),('ela',10.12,16.46),('dividida','caveira',(85.6,97.1)),('ela',26.50,44.67),
         ('dividida','velha',(47.3,55.9)),('ela',56.25,71.39),('dividida','marca',(16.8,26.2)),('ela',78.05,85.53),
         ('preta',97.15,101.83,'O que a menina aprendeu em casa, a mulher, quando cresce, reconhece como|casa.'),
         ('dividida','ninguem',(102.1,111.5)),('ela',111.75,116.97),('dividida','chega',(117.3,124.2)),('ela',124.42,164.34),
         ('final',3.8,'Se você está com medo agora, liga|180.|É gratuito, funciona 24 horas e é sigiloso.')]
CORTA=[(65.24,68.25)]   # "umas de cada vez, devagar o ba--": ela repetiu a frase
PRE,POS=0.10,0.12
r=subprocess.run(['ffmpeg','-i',P,'-af','silencedetect=n=-40dB:d=0.25','-f','null','-'],capture_output=True,text=True).stderr
sil=list(zip([float(x) for x in re.findall(r'silence_start: ([0-9.]+)',r)],[float(x) for x in re.findall(r'silence_end: ([0-9.]+)',r)]))
sil=sorted(sil+[(a-POS,b+PRE) for a,b in CORTA])
def ts(s):
    h,mi,rr=s.split(':'); sec,ms=rr.split(','); return int(h)*3600+int(mi)*60+int(sec)+int(ms)/1000
LEG=[]
for blk in open(G+'/voz.srt',encoding='utf-8').read().strip().split('\n\n'):
    l=blk.split('\n'); a,b=[ts(x.strip()) for x in l[1].split('-->')]; LEG.append((a,b,' '.join(l[2:])))
def falas(a,b):
    """trechos com fala entre a e b, sem as pausas"""
    seg=[]; cur=a-PRE
    for s0,s1 in sil:
        c0,c1=s0+POS,s1-PRE
        if c1-c0<0.05 or c1<=cur or c0>=b+POS: continue
        if c0>cur: seg.append((cur,c0))
        cur=max(cur,c1)
    if b+POS>cur: seg.append((cur,b+POS))
    seg=[(x,y) for x,y in seg if y-x>0.12 and (y-x>=0.45 or any(f0<y and f1>x for f0,f1,_ in LEG))]
    return [(round(x*30)/30,round(y*30)/30) for x,y in seg]

# zoom nela: chega devagar ao longo de cada bloco de fala (ela gravou de longe)
def zoom_ela(d,z0,z1):
    u=f"(min(it/{d:.3f},1))"
    return f"scale={2*W}:{2*H}:flags=lanczos,zoompan=z='{z0}+({z1}-{z0})*(3*{u}*{u}-2*{u}*{u}*{u})':x='iw/2-iw/zoom/2':y='(ih-ih/zoom)*0.57':d=1:s={W}x{H}:fps=30,setsar=1"
def corta(src,trechos,saida,vf=None,af=None):
    partes=[]
    for i,(a,b) in enumerate(trechos):
        f=f'{saida}_{i}.mov'
        run(['ffmpeg','-loglevel','error','-y','-ss',f'{a:.3f}','-t',f'{b-a:.3f}','-i',src,'-vf','fps=30','-frames:v',str(round((b-a)*30)),
             '-c:v','libx264','-preset','veryfast','-crf','14','-c:a','pcm_s16le','-ar','48000','-ac','2',f])
        partes.append(f"file '{f}'")
    open(saida+'.txt','w').write('\n'.join(partes)+'\n')
    run(['ffmpeg','-loglevel','error','-y','-f','concat','-safe','0','-i',saida+'.txt']+(['-vf',vf] if vf else [])+(['-af',af] if af else [])+ENC+[saida+'.mov'])
VOZ='loudnorm=I=-14:TP=-1.5:LRA=11'
def preta(txt,tam=112):
    """tela preta: trechos entre | alternam letra branca e cursiva rose gold"""
    fr=Image.new('RGB',(W,H),(0,0,0)); d=ImageDraw.Draw(fr); fo=ImageFont.truetype(F+'/ArchivoBlack.ttf',tam)
    fc=ImageFont.truetype(F+'/Satisfy-400-normal.ttf',int(tam*1.75)); blocos=[]
    for n_,trecho in enumerate(txt.split('|')):
        if n_%2: blocos.append(('c',trecho.strip())); continue
        atual=''
        for pal in trecho.split():
            teste=(atual+' '+pal).strip()
            if d.textlength(teste,font=fo)>W-120 and atual: blocos.append(('b',atual)); atual=pal
            else: atual=teste
        if atual: blocos.append(('b',atual))
    altura={'b':int(tam*1.18),'c':int(tam*1.9)}
    y=(H-sum(altura[k] for k,_ in blocos))//2-80
    for k,ln in blocos:
        if k=='b': d.text(((W-d.textlength(ln,font=fo))/2,y),ln,font=fo,fill=(0xea,0xe8,0xec))
        else: d.text(((W-d.textlength(ln,font=fc))/2,y-int(tam*0.25)),ln,font=fc,fill=(0xe2,0x9f,0x8e))
        y+=altura[k]
    return fr

PECAS=[]; MAPA=[]; EV=[]; PRETAS=[]; DIVIDIDAS=[]; o=0.0; zi=0
for i,p in enumerate(ROTEIRO):
    s=f'{T}/p{i:02d}'
    if p[0]=='ela':
        seg=falas(p[1],p[2]); d=sum(b-a for a,b in seg)
        z0,z1=(1.30,1.44) if zi%2==0 else (1.36,1.50); zi+=1
        corta(P,seg,s,vf=zoom_ela(d,z0,z1),af=VOZ)
        oo=o
        for a,b in seg: MAPA.append((a,b,oo)); oo+=b-a
    elif p[0]=='preta':
        seg=falas(p[1],p[2]); d=sum(b-a for a,b in seg)
        preta(p[3]).save(s+'.png')
        corta(P,seg,s+'_voz',af=VOZ)
        run(['ffmpeg','-loglevel','error','-y','-loop','1','-i',s+'.png','-i',s+'_voz.mov','-map','0:v','-map','1:a','-t',f'{d:.3f}','-vf','fps=30,format=yuv420p']+ENC+[s+'.mov'])
        PRETAS.append((o,o+d))
    elif p[0]=='final':
        preta(p[2],96).save(s+'.png')
        run(['ffmpeg','-loglevel','error','-y','-loop','1','-i',s+'.png','-f','lavfi','-i','anullsrc=r=48000:cl=stereo','-t',str(p[1]),
             '-vf','fps=30,format=yuv420p,fade=t=in:d=0.4']+ENC+[s+'.mov'])
        PRETAS.append((o,o+p[1]))
    else:
        src,tr,leg,x0=TRECHOS[p[1]]
        corta(src,tr,s+'_ana',af=VOZ); d=dur(s+'_ana.mov')
        if p[0]=='cheia':
            # Ana grande no centro (recorte nela) com ela mesma desfocada no fundo
            fc=(f"[0:v]split=2[a][b];[a]crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale={W}:{H},gblur=sigma=30,eq=brightness=-0.2[fundo];"
                f"[b]scale=-2:1100:flags=lanczos,crop={W}:1100:315:0[ana];[fundo][ana]overlay=0:180,setsar=1[v]")
            run(['ffmpeg','-loglevel','error','-y','-i',s+'_ana.mov','-filter_complex',fc,'-map','[v]','-map','0:a']+ENC+[s+'.mov'])
        else:
            l0,l1=p[2]; f=d/(l1-l0)   # a pausa dela é esticada ou encurtada para durar o mesmo que o trecho da Ana
            if x0 is None:   # vídeo vertical do Instagram: inteiro na largura, ele mesmo desfocado atrás
                topo=(f"[0:v]split=2[a][b];[a]scale=-2:{HM},crop={W}:{HM},gblur=sigma=28,eq=brightness=-0.2[fu];"
                      f"[b]scale={W}:-2:flags=lanczos[t];[fu][t]overlay=0:(H-h)/2[topo];")
            else:
                topo=f"[0:v]crop=810:720:{x0-405}:0,scale={W}:{HM}:flags=lanczos[topo];"
            fc=(topo+f"[1:v]trim={l0}:{l1},setpts=(PTS-STARTPTS)*{f:.4f},fps=30,scale={int(W*1.4)}:{int(H*1.4)}:flags=lanczos,"
                f"crop={W}:{HM}:{int((W*1.4-W)/2)}:420[ela];[topo][ela]vstack,setsar=1[v]")
            run(['ffmpeg','-loglevel','error','-y','-i',s+'_ana.mov','-i',P,'-filter_complex',fc,'-map','[v]','-map','0:a','-t',f'{d:.3f}']+ENC+[s+'.mov'])
            DIVIDIDAS.append((o,o+d))
        for a,b,txt in leg: EV.append((o+a,o+min(b,d),txt))
        PECAS.append((p[1],o,o+d))
    d=dur(s+'.mov'); o+=d
    if p[0]=='ela': PECAS.append(('ela',o-d,o))
    open(T+'/lista.txt','a' if i else 'w').write(f"file '{s}.mov'\n")
TOT=round(o,2)
run(['ffmpeg','-loglevel','error','-y','-f','concat','-safe','0','-i',T+'/lista.txt','-c','copy',T+'/base.mov'])
def m(t):
    """tempo da gravação -> tempo no vídeo final"""
    best=None
    for a,b,o0 in MAPA:
        if a<=t<=b: return o0+t-a
        x,y=(o0,a) if t<a else (o0+b-a,b)
        if best is None or abs(t-y)<best[0]: best=(abs(t-y),x)
    return best[1]
ini={k:(a,b) for k,a,b in PECAS if k!='ela'}

# legendas: blocos de até 4 palavras
for a,b,txt in LEG:
    if any(p[0]=='preta' and p[1]-0.3<=a<=p[2] for p in ROTEIRO): continue
    EV.append((m(a),m(b),txt))
def fmt(t): return f'{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}'
lin=[]
for a,b,txt in sorted(EV):
    pal=txt.split(); n=len(pal); ch=[]; i=0
    while i<n:
        k=min(4,n-i)
        if n-i-k==1: k+=1
        ch.append(' '.join(pal[i:i+k])); i+=k
    tot=sum(len(c) for c in ch); t=a
    for c in ch:
        dt=(b-a)*len(c)/tot
        if dt>0.1: lin.append(f'Dialogue: 0,{fmt(t)},{fmt(t+dt)},Leg,,0,0,0,,{c}')
        t+=dt
LIVRE=sorted(PRETAS+DIVIDIDAS); arroba=''; c0=ini['gancho'][1]
for a,b in LIVRE:
    if a>c0: arroba+=f'Dialogue: 1,{fmt(c0)},{fmt(a)},Arroba,,0,0,0,,@giselehedler\n'
    c0=b
CAV=m(26.6),m(30.1); CTA=m(153.95),m(164.34)
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
Dialogue: 1,{fmt(CAV[0])},{fmt(CAV[1])},Topo,,0,0,0,,{{\\fad(150,200)}}Gorda e caveira. Em segundos.
Dialogue: 1,{fmt(CTA[0])},{fmt(CTA[1])},Topo,,0,0,0,,{{\\fad(150,200)}}Escreve 5524
"""+arroba+'\n'.join(lin)+'\n'
open(T+'/leg.ass','w',encoding='utf-8').write(ass)

# degradê atrás das legendas e do título
g=Image.new('RGBA',(W,H),(0,0,0,0)); dr=ImageDraw.Draw(g)
for y in range(H):
    a=0
    if 1080<=y<1700: a=int(150*min(1,(y-1080)/220)*min(1,(1700-y)/200))
    if y<620: a=max(a,int(110*(1-y/620)))
    dr.line([(0,y),(W,y)],fill=(0,0,0,a))
g.save(T+'/degrade.png')

# áudio: trilha por partes (gancho sem música), abaixa quando alguém fala
run(['ffmpeg','-loglevel','error','-y','-i',T+'/base.mov','-map','0:a','-c:a','pcm_s16le',T+'/voz.wav'])
CORTES=[ini['gancho'][1],m(56.3),ini['ninguem'][0],m(124.5),TOT]
CLIMAS=['misterio','sombrio','susto','resolucao']
run(['python3','/home/user/laboratorio-conteudo/videos/musica_secoes.py',T+'/musica.wav',str(TOT)]+
    [f'{a:.3f}:{b:.3f}:{c}' for a,b,c in zip(CORTES,CORTES[1:],CLIMAS)])
run(['ffmpeg','-loglevel','error','-y','-i',T+'/voz.wav','-i',T+'/musica.wav','-filter_complex',
     f"[0:a]asplit=2[voz][sc];"
     f"[1:a]aresample=48000,atrim=0:{TOT},volume=0.32,afade=t=out:st={TOT-1.5}:d=1.5[mus];"
     f"[mus][sc]sidechaincompress=threshold=0.03:ratio=5:attack=20:release=400[musd];"
     f"[voz][musd]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.89",'-c:a','pcm_s16le',T+'/audio_final.wav'])

# palavras em cursiva grande pegando o topo da cabeça (recorte da pessoa quadro a quadro)
ATRAS=[('o corpo',m(32.6),m(34.0),330),('normal',m(70.1),m(71.39),360),('acordada',m(146.6),m(148.38),320),('gaveta',m(150.6),m(153.4),360)]
p1=subprocess.Popen(['ffmpeg','-loglevel','error','-i',T+'/base.mov','-map','0:v','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
p2=subprocess.Popen(['ffmpeg','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','30','-i','-',
     '-loop','1','-t',str(TOT),'-i',T+'/degrade.png','-i',T+'/audio_final.wav',
     '-filter_complex',f"[0:v][1:v]overlay[v4];[v4]ass={T}/leg.ass:fontsdir={F}[v]",'-map','[v]','-map','2:a','-t',str(TOT),
     '-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',
     G+'/reel-ana.mp4'],stdin=subprocess.PIPE)
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
segm=vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=BaseOptions(model_asset_path=S+'/seg.tflite'),output_confidence_masks=True))
def camada(txt,tam,topo_cabeca):
    f=ImageFont.truetype(F+'/Satisfy-400-normal.ttf',tam)
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    bb=d.textbbox((0,0),txt,font=f); tw,th=bb[2]-bb[0],bb[3]-bb[1]
    if tw>W-60: return camada(txt,int(tam*(W-60)/tw),topo_cabeca)
    cy=max(topo_cabeca+0.16*th,th/2+40)
    pos=((W-tw)/2-bb[0],cy-th/2-bb[1])
    sh=Image.new('RGBA',(W,H),(0,0,0,0)); ImageDraw.Draw(sh).text((pos[0]+3,pos[1]+5),txt,font=f,fill=(20,8,30,215),stroke_width=9,stroke_fill=(20,8,30,215))
    lay=Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)),lay)
    ImageDraw.Draw(lay).text(pos,txt,font=f,fill=(0xe2,0x9f,0x8e,255))
    return np.array(lay).astype(np.float32)/255
FB=W*H*3; n=0; ativo=None; prev=None
while True:
    buf=p1.stdout.read(FB)
    if len(buf)<FB: break
    t=n/30; n+=1
    w=next((x for x in ATRAS if x[1]<=t<x[2]),None)
    if w is None:
        ativo=prev=None; p2.stdin.write(buf); continue
    im=np.frombuffer(buf,np.uint8).reshape(H,W,3)
    cm=[c.numpy_view()[...,0] for c in segm.segment(mp.Image(image_format=mp.ImageFormat.SRGB,data=np.ascontiguousarray(im))).confidence_masks]
    pessoa=1-cm[0]
    if ativo is not w:
        ys=np.where(((cm[1]+cm[3])>0.5).any(1))[0]
        lay=camada(w[0],w[3],ys.min() if len(ys) else 400); ativo=w; prev=pessoa
    pessoa=0.6*pessoa+0.4*prev; prev=pessoa
    mk=np.clip((pessoa-0.35)/0.3,0,1)
    mk=np.array(Image.fromarray((mk*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5))).astype(np.float32)/255
    fade=min(1,(t-w[1])/0.25)*min(1,(w[2]-t)/0.15)
    a=lay[...,3]*(1-mk)*fade
    out=im*(1-a[...,None])+lay[...,:3]*255*a[...,None]
    p2.stdin.write(out.astype(np.uint8).tobytes())
p2.stdin.close(); p2.wait(); p1.wait()
print('ok',TOT,PECAS)

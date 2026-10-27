# Reel pós-eleição gravado no carro: "nenhum presidente me colocou naquele carro"
# falas sem pausas nem repetições, legenda acima da cabeça (às vezes no peito), trilha emocional na história
# e esperança a partir do "Então, madame"; FOTOS entra quando ela mandar (enchente e hospital)
import subprocess, re, os
from PIL import Image, ImageDraw
S='/tmp/claude-0/-home-user/f19a087c-4085-5aef-b35a-89b81156bb55/scratchpad'
E=S+'/soberania'; F=S+'/fonts'; T=E+'/tmp'
P=E+'/proxy.mov'   # gravação dela (2160x3840, 60 quadros) convertida para 1080x1920, 30 quadros
W,H=1080,1920
os.makedirs(T,exist_ok=True)
def run(c): subprocess.run(c,check=True)
def dur(f): return float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f],capture_output=True,text=True).stdout)
ENC=['-r','30','-c:v','libx264','-preset','veryfast','-crf','15','-pix_fmt','yuv420p','-c:a','pcm_s16le','-ar','48000','-ac','2']
VOZ='highpass=f=80,loudnorm=I=-14:TP=-1.5:LRA=11'

# melhores tomadas: lista de (início, fim) da gravação e a legenda corrigida
FALAS=[
 ([(4.60,10.38)],'Eu fui dormir muito mal no domingo, e na segunda-feira eu precisei inclusive de um remédio para dor de cabeça.'),
 ([(18.98,24.28),(24.44,24.96)],'A maioria de vocês sabe as minhas preferências políticas, então eu entendo muito bem quem está com raiva.'),
 ([(44.08,47.44)],'Eu não vou dizer pra ti não se sentir injustiçado.'),
 ([(52.66,56.58)],'Mas eu vou te dizer uma coisa que eu precisei dizer pra mim na segunda-feira de manhã.'),
 ([(64.10,73.64)],'Em 2024, Porto Alegre, a cidade onde eu morava, onde eu estou agora, ficou embaixo d\'água. E eu estava, naquela época, em fase terminal de uma doença grave.'),
 ([(78.76,83.64)],'Ninguém veio no meu ouvido dizer assim: fica tranquila, isso vai ser resolvido.'),
 ([(88.84,92.24)],'Eu peguei o meu carro. Eu mesma precisei sair dali.'),
 ([(107.34,111.24),(114.40,120.70)],'Fui pra São Paulo e conheci uma médica que eu paguei do meu bolso. Ela me deu exames pra fazer pra eu poder entrar numa lista do SUS, pra ter esperança de ter um transplante.'),
 ([(129.52,142.88)],'Eu consegui, e eu sou muito grata por isso. Mas o SUS não pertence a nenhum presidente. O SUS pertence a mim, pertence a ti, pertence à gente. É um direito nosso.'),
 ([(147.44,149.66),(167.30,168.80)],'Nenhum presidente me colocou naquele carro. De nenhum partido.'),
 ([(172.32,176.46),(184.18,185.18)],'Quem foi atrás, quem enfrentou, quem fez os exames, quem fez o tratamento, fui eu.'),
 ([(191.98,195.66)],'O que tiver que ser apurado vai ser apurado.'),
 ([(200.08,205.76)],'Mas a nossa raiva no grupo do WhatsApp, infelizmente, não muda o presidente eleito.'),
 ([(214.56,217.32)],'Não muda nada. Isso só muda a gente.'),
 ([(226.42,235.28)],'Então, se por acaso tu percebeu que tu tá em ruminação de pensamentos, que tu tá se sentindo inflamada, experimenta sair desses grupos do WhatsApp.'),
 ([(253.68,258.24)],'Já é tão difícil a gente desinflamar o nosso corpo, pra que ficar inflamando a nossa mente?'),
 ([(264.76,271.20)],'E a Bíblia manda a gente orar por aqueles que governam, quer a gente goste ou não deles.'),
 ([(277.60,280.30)],'O nosso coração precisa de paz.'),
 ([(284.68,287.92)],'E tudo bem, tu tem o teu favorito. Eu tenho o meu.'),
 ([(295.38,299.38)],'Mas a tua vida, a minha, não acaba por causa de um ou por causa de outro.'),
 ([(309.14,310.10)],'Ela continua.'),
 ([(326.84,337.02)],'Então, madame, vamos trabalhar, vamos cuidar do nosso dinheiro, do nosso relacionamento, do nosso marido, dos nossos filhos, da nossa casa, da gente, do nosso corpo.'),
 ([(356.72,362.20)],'E se tu quer a minha ajuda nisso, toda quinta-feira eu faço uma aula ao vivo, a Quinta da Mente,'),
 ([(369.96,374.78)],'pra você aprender a iluminar a sua mente, fazendo pequenas mudanças e tendo resultados impressionantes.'),
 ([(376.44,380.22)],'Se tu escrever 5524 aqui nos comentários, eu vou te mandar o link.'),
 ([(386.10,398.56)],'E não deixa nada nem ninguém abalar a tua confiança. A tua confiança é a coisa mais importante que tu tem.'),
]
MEIO={4,8,13,17,21,25}   # falas com a legenda na altura do peito; o resto vai acima da cabeça
# imagens dela por cima da fala, em tela cheia: (índice da fala, arquivo, fração inicial e final da fala, início no vídeo)
# enchente: gravação de tela do drone (sem crédito, a pedido dela); depois a selfie no hospital
FOTOS=[x for x in [(4,E+'/fotos/enchente_rec.mp4',0.0,0.52,1.5),(4,E+'/fotos/doente.jpg',0.52,1.0,0),
                   (7,E+'/fotos/hospital.jpg',0.0,1.0,0)] if os.path.exists(x[1])]

PRE,POS=0.10,0.22   # folga depois da última palavra antes de cada pausa, pra não engolir o fim
r=subprocess.run(['ffmpeg','-i',P,'-vn','-af','silencedetect=n=-37dB:d=0.25','-f','null','-'],capture_output=True,text=True).stderr
sil=list(zip([float(x) for x in re.findall(r'silence_start: ([0-9.]+)',r)],[float(x) for x in re.findall(r'silence_end: ([0-9.]+)',r)]))
# trechos com o rosto virado (lendo o texto): cabeça girada mais de 22 graus ou fora do quadro; olhar de lado sem virar o rosto fica
import numpy as np
OL=np.loadtxt(E+'/olhar.txt')
LADO=[]
for t,yaw,pitch in OL:
    if abs(yaw)>22:
        if LADO and t-LADO[-1][1]<0.35: LADO[-1][1]=t+0.1
        else: LADO.append([t-0.15,t+0.1])
LADO=[(x,y) for x,y in LADO if y-x>0.8]   # viradas curtas no meio da fala ficam (cortar comeria palavra)
# nunca corta em cima de palavra: tira das viradas os trechos em que ela está falando
PAL=[(float(x),float(y)) for l in open(E+'/transc.txt') for x,y in re.findall(r'\[([\d.]+)-([\d.]+)\]',l)]
def menos_fala(x,y):
    res=[(x,y)]
    for p0,p1 in PAL:
        nv=[]
        for u,v in res:
            if p1<=u or p0>=v: nv.append((u,v)); continue
            if p0>u: nv.append((u,p0-0.05))
            if p1<v: nv.append((p1+0.05,v))
        res=nv
    return [(u,v) for u,v in res if v-u>0.2]
LADO=[z for x,y in LADO for z in menos_fala(x,y)]
def tira_olhar(seg):
    out=[]
    for a,b in seg:
        cur=a
        for x,y in LADO:
            if y<=cur or x>=b: continue
            if x>cur: out.append((cur,x))
            cur=max(cur,y)
        if b>cur: out.append((cur,b))
    return out
def sem_pausas(a,b):
    seg=[]; cur=a
    for s0,s1 in sil:
        c0,c1=s0+POS,s1-PRE
        if c1-c0<0.05 or c1<=cur or c0>=b: continue
        if c0>cur: seg.append((cur,c0))
        cur=max(cur,c1)
    if b>cur: seg.append((cur,b))
    seg=tira_olhar(seg)
    return [(round(x*30)/30,round(y*30)/30) for x,y in seg if y-x>0.15]
def zoom(d,z0,z1):
    u=f"(min(it/{d:.3f},1))"
    return f"scale={2*W}:{2*H}:flags=lanczos,zoompan=z='{z0}+({z1}-{z0})*(3*{u}*{u}-2*{u}*{u}*{u})':x='iw/2-iw/zoom/2':y='(ih-ih/zoom)*0.35':d=1:s={W}x{H}:fps=30,setsar=1"
def corta(trechos,saida,vf,af):
    partes=[]
    for i,(a,b) in enumerate(trechos):
        f=f'{saida}_{i}.mov'
        run(['ffmpeg','-loglevel','error','-y','-ss',f'{a:.3f}','-t',f'{b-a:.3f}','-i',P,'-vf','fps=30','-frames:v',str(round((b-a)*30)),
             '-c:v','libx264','-preset','veryfast','-crf','14','-c:a','pcm_s16le','-ar','48000','-ac','2',f])
        partes.append(f"file '{f}'")
    open(saida+'.txt','w').write('\n'.join(partes)+'\n')
    run(['ffmpeg','-loglevel','error','-y','-f','concat','-safe','0','-i',saida+'.txt','-vf',vf,'-af',af]+ENC+[saida+'.mov'])

def folga(a,b):
    """estica o começo e o fim da tomada até perto da palavra vizinha (o tempo do whisper corta o fim da última palavra)"""
    ant=max([y for x,y in PAL if y<=a+0.05]+[a-0.3]); prox=min([x for x,y in PAL if x>=b-0.05]+[b+0.6])
    return max(a-0.12,ant+0.05),min(b+0.35,prox-0.08)
EV=[]; o=0.0; LISTA=[]
for i,(trs,txt) in enumerate(FALAS):
    s=f'{T}/p{i:02d}'
    a0,b0=folga(trs[0][0],trs[-1][1]); trs=[(a0 if k==0 else a,b0 if k==len(trs)-1 else b) for k,(a,b) in enumerate(trs)]   # folga só nas pontas da fala; cortes internos (palavra repetida) ficam exatos
    seg=[x for a,b in trs for x in sem_pausas(a,b)]; d=sum(y-x for x,y in seg)
    z0,z1=(1.00,1.08) if i%2==0 else (1.06,1.14)
    corta(seg,s,zoom(d,z0,z1),VOZ)
    d=dur(s+'.mov'); EV.append((o,o+d,txt,i)); LISTA.append(f"file '{s}.mov'"); o+=d
TOT=round(o,2); print('duração',TOT)
open(T+'/lista.txt','w').write('\n'.join(LISTA)+'\n')
run(['ffmpeg','-loglevel','error','-y','-f','concat','-safe','0','-i',T+'/lista.txt','-c','copy',T+'/base.mov'])

# legendas: blocos de até 4 palavras, Poppins Medium; acima da cabeça (teto escuro do carro) ou no peito
def fmt(t): return f'{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}'
lin=[]
for a,b,txt,i in EV:
    pal=txt.split(); n=len(pal); ch=[]; k0=0
    while k0<n:
        k=min(4,n-k0)
        if n-k0-k==1: k+=1
        ch.append(' '.join(pal[k0:k0+k])); k0+=k
    tot=sum(len(c) for c in ch); t=a
    for c in ch:
        dt=(b-a)*len(c)/tot
        if dt>0.1: lin.append(f"Dialogue: 0,{fmt(t)},{fmt(t+dt)},{'Meio' if i in MEIO else 'Topo'},,0,0,0,,{c}")
        t+=dt
ass=f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Topo,Poppins Medium,74,&H00FFFFFF,&H00FFFFFF,&H00000000,&H8C000000,0,0,0,0,100,100,0,0,1,0,4,8,80,80,330,1
Style: Meio,Poppins Medium,74,&H00FFFFFF,&H00FFFFFF,&H00000000,&H8C000000,0,0,0,0,100,100,0,0,1,0,4,2,80,80,620,1
Style: Arroba,Merriweather,38,&H30ECE8EA,&H30ECE8EA,&H00000000,&H8C000000,0,1,0,0,100,100,1,0,1,0,2,2,70,70,50,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 1,{fmt(0)},{fmt(TOT)},Arroba,,0,0,0,,@giselehedler
"""+'\n'.join(lin)+'\n'
JAN=[]   # janela de cada imagem no tempo do reel
for idx,arq,f0,f1,ss in FOTOS:
    a,b=EV[idx][0],EV[idx][1]; JAN.append((a+(b-a)*f0,a+(b-a)*f1))
open(T+'/leg.ass','w',encoding='utf-8').write(ass)

# sombra suave atrás das legendas (topo e peito)
g=Image.new('RGBA',(W,H),(0,0,0,0)); dr=ImageDraw.Draw(g)
for y in range(H):
    a=int(110*max(0,1-y/700))
    if 1050<=y<1500: a=max(a,int(90*min(1,(y-1050)/150)*min(1,(1500-y)/150)))
    dr.line([(0,y),(W,y)],fill=(0,0,0,a))
g.save(T+'/degrade.png')

# trilhas do Envato dela: emocional na história, esperança a partir do "Então, madame"
import numpy as np, wave
M=S+'/trilhas'
t_madame=next(x[0] for x in EV if x[2].startswith('Então, madame'))
TRILHAS=[(0,t_madame,M+'/sad/Top Flow - Emotional.wav',0),
         (t_madame,TOT,M+'/hope/Hope for Humanity/Hope for Humanity.wav',24)]
run(['ffmpeg','-loglevel','error','-y','-i',T+'/base.mov','-map','0:a','-c:a','pcm_s16le',T+'/voz.wav'])
SR=48000; mus=np.zeros((int(SR*(TOT+1)),2),np.float32); XF=1.2
for a0,b0,f,off in TRILHAS:
    raw=subprocess.run(['ffmpeg','-loglevel','error','-ss',str(off),'-t',f'{b0-a0+XF:.3f}','-i',f,'-ac','2','-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout
    x=np.frombuffer(raw,np.float32).reshape(-1,2).copy(); x*=0.12/(np.sqrt(np.mean(x**2))+1e-9)
    nf=int(XF*SR); x[:nf]*=np.linspace(0,1,nf)[:,None]; x[-nf:]*=np.linspace(1,0,nf)[:,None]
    i=int(max(0,a0-XF/2)*SR); j=min(len(mus),i+len(x)); mus[i:j]+=x[:j-i]
with wave.open(T+'/musica.wav','wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(mus,-1,1)*32767).astype(np.int16).tobytes())
run(['ffmpeg','-loglevel','error','-y','-i',T+'/voz.wav','-i',T+'/musica.wav','-filter_complex',
     f"[0:a]asplit=2[voz][sc];[1:a]atrim=0:{TOT},volume=0.55,afade=t=out:st={TOT-2.0}:d=2.0[mus];"
     f"[mus][sc]sidechaincompress=threshold=0.04:ratio=4:attack=20:release=450[musd];"
     f"[voz][musd]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.89",'-c:a','pcm_s16le',T+'/audio_final.wav'])

# fotos (quando houver): tela cheia com leve zoom, por cima da fala correspondente, legenda continua por cima
ins=['-i',T+'/base.mov','-loop','1','-t',str(TOT),'-i',T+'/degrade.png','-i',T+'/audio_final.wav']
fc="[0:v][1:v]overlay[v0];"; ult='v0'
for n,((idx,arq,f0,f1,ss),(a,b)) in enumerate(zip(FOTOS,JAN)):
    d=b-a
    if arq.endswith('.mp4'):   # gravação de tela: tira as faixas pretas e ocupa a tela
        ins+=['-ss',str(ss),'-t',f'{d:.2f}','-i',arq]
        base=f"[{3+n}:v]fps=30,crop=886:1560:0:180,scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1"
    else:
        ins+=['-loop','1','-t',f'{d:.2f}','-i',arq]
        base=(f"[{3+n}:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
              f"zoompan=z='1+0.06*on/({d:.2f}*30)':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s={W}x{H}:fps=30")
    fc+=(base+f",format=rgba,fade=t=in:st=0:d=0.3:alpha=1,fade=t=out:st={d-0.3:.2f}:d=0.3:alpha=1,format=rgba,setpts=PTS+{a:.3f}/TB[f{n}];"
         f"[{ult}][f{n}]overlay=eof_action=pass:enable='between(t,{a:.3f},{b:.3f})'[v{n+1}];")
    ult=f'v{n+1}'
fc+=f"[{ult}]ass={T}/leg.ass:fontsdir={F}[v]"
run(['ffmpeg','-loglevel','error','-y']+ins+['-filter_complex',fc,'-map','[v]','-map','2:a','-t',str(TOT),
     '-c:v','libx264','-preset','medium','-crf','22','-maxrate','8M','-bufsize','16M','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',E+'/reel-soberania.mp4'])
print('ok',TOT,'fotos:',len(FOTOS))

# Reel do posicionamento na eleição (Lula x Flávio): falas dela sem pausas nem tomadas repetidas,
# trecho verificado da reportagem sobre a anulação dos processos e a oração do Flávio no fim, com som
# trilhas do Envato dela: tensão nos argumentos, esperança a partir do voto no Flávio (gancho sem música)
import subprocess, re, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S='/tmp/claude-0/-home-user/f19a087c-4085-5aef-b35a-89b81156bb55/scratchpad'
E=S+'/eleicao'; F=S+'/fonts'; T=E+'/tmp'
P=E+'/proxy.mov'   # gravação dela (2160x3840, 60 quadros) convertida para 1080x1920, 30 quadros
W,H=1080,1920
subprocess.run(['mkdir','-p',T])
def run(c): subprocess.run(c,check=True)
def dur(f): return float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f],capture_output=True,text=True).stdout)
ENC=['-r','30','-c:v','libx264','-preset','veryfast','-crf','15','-pix_fmt','yuv420p','-c:a','pcm_s16le','-ar','48000','-ac','2']
VOZ='loudnorm=I=-14:TP=-1.5:LRA=11'

# melhores tomadas (tempo da gravação) e a legenda de cada uma
FALAS=[
 (2.87,13.58,'Na minha bio está escrito: vida morna não combina com soberania. Seria muito incoerente eu ser morna justamente agora, numa eleição como essa.'),
 (21.42,26.32,'E quem se diz neutro numa eleição como essa escolheu justamente não olhar.'),
 (37.79,41.08,'Eu não voto no Lula. Foram duas condenações:'),
 (53.01,57.55,'Lava Jato, triplex e sítio de Atibaia, todas confirmadas, tá?'),
 (66.23,70.34,'Em segunda instância, e 580 dias de prisão.'),
 (76.96,81.53,'E o STF anulou os processos. Por quê? Porque corriam no tribunal errado.'),
 (88.46,90.93,'E o que aconteceu depois? Eles prescreveram.'),
 (101.36,105.05,'Veja: ninguém julgou o Lula inocente.'),
 (108.47,114.23,'Processo anulado e inocentado são palavras e coisas completamente diferentes.'),
 ('LULA',),
 (127.66,129.21,'Isso não é pessoal, tá?'),
 (156.45,163.70,'O mesmo partido já governou o Brasil por 18 anos. Mais quatro anos, seriam 22.'),
 (171.07,177.65,'Eu não sei você, mas eu desconfio de qualquer grupo, de qualquer lado, que queira ficar tanto tempo assim no poder.'),
 (202.32,207.84,'Porque alternância é o que impede um país de virar propriedade de alguém.'),
 (232.59,239.49,'Eu não sei se tu sabe, mas dois anos atrás ele fez uma cirurgia intracraniana de emergência.'),
 (247.32,253.09,'Pensa no final do mandato dele: ele teria 85 anos.'),
 (260.01,278.95,'E no último debate a gente conseguiu ver que talvez esse problema não deixe ele mais firme. Ele está muito lúcido, está muito bem, sim, é verdade. Mas será o suficiente para governar um país? Do meu ponto de vista, e ele é só meu.'),
 (286.06,287.18,'Eu voto no Flávio.'),
 (322.48,332.88,'Veja, a dívida do país saiu de 71% nesses quatro anos para 83% do PIB, e sem pandemia alguma para justificar isso.'),
 (344.00,348.64,'E o Flávio colocou essa conta, esse problema, no centro do jogo dele.'),
 (383.30,389.99,'A ideia dele é implementar algumas regras, inclusive diminuir o número de ministérios e esses supersalários.'),
 (395.25,401.61,'Olha, vou ser sincera: eu não espero um salvador nem um santo. Até porque política não é lugar de santo.'),
 (420.78,424.78,'Quem procura santo na política aceita qualquer pecado do seu lado.'),
 (458.48,468.84,'Acho que vale uma pergunta pra mim e pra ti antes de votar: eu sei em quem eu estou votando, ou só estou escolhendo votar nesse porque sou contra aquele?'),
 (490.36,505.64,'Pode discordar de mim, óbvio. Mas se a tua forma de discordar de mim é em forma de xingamento, tu não discordas de mim: tu só mostrou que faltou argumento.'),
 (517.38,519.75,'E se você vai votar no Lula, tá tudo certo.'),
 (525.55,530.78,'Eu não sou tua inimiga por conta disso. Tu tem todo o direito de votar em quem tu quiser.'),
 (532.31,535.81,'Assim como eu tenho o direito de expressar aqui na minha rede social aquilo que eu penso.'),
 (539.81,548.85,'E se tu tá em cima do muro: em cima do muro ninguém é neutro. Só fica mais fácil de alguém te empurrar.'),
 ('FLAVIO',),
]
# trecho verificado da reportagem: Lula dizendo que foi inocentado e juristas explicando a anulação
LULA=[(S+'/reelpol/lula.mp4',36.2,47.62,'"Eu fui julgado, fui considerado inocente." Não, não foi. A pior e maior mentira dessa eleição é dizer que Lula foi inocentado.'),
      (S+'/reelpol/lula.mp4',59.78,75.75,'O Supremo não inocentou. O Supremo assentou a nulidade dos processos, o que implica o retorno à fase inicial.')]
# oração do Flávio na igreja, com som, e o "amém" da multidão no fim
FLAVIO=[(S+'/reelflavio2/f.mp4',62.9,75.3,'Que o Senhor me dê muita sabedoria, coragem, saúde, discernimento, para causar um avivamento nessa nação.'),
        (S+'/painosso/f.mp4',18.4,23.0,'Amém!')]

PRE,POS=0.10,0.12
r=subprocess.run(['ffmpeg','-i',P,'-af','silencedetect=n=-38dB:d=0.3','-f','null','-'],capture_output=True,text=True).stderr
sil=list(zip([float(x) for x in re.findall(r'silence_start: ([0-9.]+)',r)],[float(x) for x in re.findall(r'silence_end: ([0-9.]+)',r)]))
def sem_pausas(a,b):
    seg=[]; cur=a
    for s0,s1 in sil:
        c0,c1=s0+POS,s1-PRE
        if c1-c0<0.05 or c1<=cur or c0>=b: continue
        if c0>cur: seg.append((cur,c0))
        cur=max(cur,c1)
    if b>cur: seg.append((cur,b))
    return [(round(x*30)/30,round(y*30)/30) for x,y in seg if y-x>0.15]
def zoom(d,z0,z1):
    u=f"(min(it/{d:.3f},1))"
    return f"scale={2*W}:{2*H}:flags=lanczos,zoompan=z='{z0}+({z1}-{z0})*(3*{u}*{u}-2*{u}*{u}*{u})':x='iw/2-iw/zoom/2':y='(ih-ih/zoom)*0.45':d=1:s={W}x{H}:fps=30,setsar=1"
def corta(src,trechos,saida,vf=None,af=None):
    partes=[]
    for i,(a,b) in enumerate(trechos):
        f=f'{saida}_{i}.mov'
        run(['ffmpeg','-loglevel','error','-y','-ss',f'{a:.3f}','-t',f'{b-a:.3f}','-i',src,'-vf','fps=30','-frames:v',str(round((b-a)*30)),
             '-c:v','libx264','-preset','veryfast','-crf','14','-c:a','pcm_s16le','-ar','48000','-ac','2',f])
        partes.append(f"file '{f}'")
    open(saida+'.txt','w').write('\n'.join(partes)+'\n')
    run(['ffmpeg','-loglevel','error','-y','-f','concat','-safe','0','-i',saida+'.txt']+(['-vf',vf] if vf else [])+(['-af',af] if af else [])+ENC+[saida+'.mov'])
def cena_de_fora(src,a,b,saida,horizontal):
    """vídeo de outra fonte: horizontal entra inteiro na largura com ele mesmo desfocado atrás; vertical ocupa a tela"""
    if horizontal:
        fc=(f"[0:v]crop=720:404:0:462,split=2[x][y];[x]scale=-2:{H},crop={W}:{H},gblur=sigma=30,eq=brightness=-0.25[fu];"
            f"[y]scale={W}:-2:flags=lanczos[fr];[fu][fr]overlay=0:(H-h)/2-120,setsar=1,fps=30[v]")
    elif 'reelflavio2' in src:   # tira a legenda de outro perfil escrita por cima
        fc=f"[0:v]crop=472:840:124:0,scale={W}:{H}:flags=lanczos,setsar=1,fps=30[v]"
    else:                         # Pai Nosso em Manaus: tira o letreiro do topo
        fc=f"[0:v]crop=574:1020:73:260,scale={W}:{H}:flags=lanczos,setsar=1,fps=30[v]"
    run(['ffmpeg','-loglevel','error','-y','-ss',f'{a:.3f}','-t',f'{b-a:.3f}','-i',src,'-filter_complex',fc,'-map','[v]','-map','0:a','-af',VOZ]+ENC+[saida])

EV=[]; o=0.0; zi=0; LISTA=[]; DE_FORA=[]
for i,f in enumerate(FALAS):
    s=f'{T}/p{i:02d}'
    if len(f)==3:
        a,b,txt=f; seg=sem_pausas(a,b); d=sum(y-x for x,y in seg)
        z0,z1=(1.00,1.10) if zi%2==0 else (1.08,1.16); zi+=1
        corta(P,seg,s,vf=zoom(d,z0,z1),af=VOZ)
        blocos=[(s+'.mov',txt,'ela')]
    else:
        blocos=[]
        for j,(src,a,b,txt) in enumerate(LULA if f[0]=='LULA' else FLAVIO):
            cena_de_fora(src,a,b,f'{s}_{j}.mov',f[0]=='LULA')
            blocos.append((f'{s}_{j}.mov',txt,'fora'))
    for arq,txt,quem in blocos:
        d=dur(arq); EV.append((o,o+d,txt,quem)); LISTA.append(f"file '{arq}'")
        if quem=='fora': DE_FORA.append((o,o+d))
        o+=d
TOT=round(o,2); print('duração',TOT)
open(T+'/lista.txt','w').write('\n'.join(LISTA)+'\n')
run(['ffmpeg','-loglevel','error','-y','-f','concat','-safe','0','-i',T+'/lista.txt','-c','copy',T+'/base.mov'])

# legendas: blocos de até 4 palavras, Poppins Medium (a da marca para legenda); nas cenas de fora, numa caixa escura acima do meio
def fmt(t): return f'{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}'
lin=[]
for a,b,txt,quem in EV:
    pal=txt.split(); n=len(pal); ch=[]; i=0
    while i<n:
        k=min(4,n-i)
        if n-i-k==1: k+=1
        ch.append(' '.join(pal[i:i+k])); i+=k
    tot=sum(len(c) for c in ch); t=a
    for c in ch:
        dt=(b-a)*len(c)/tot
        if dt>0.1: lin.append(f"Dialogue: 0,{fmt(t)},{fmt(t+dt)},{'Leg' if quem=='ela' else 'Fora'},,0,0,0,,{c}")
        t+=dt
GANCHO=min(EV[0][1],6.0)
ass=f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Leg,Poppins Medium,74,&H00FFFFFF,&H00FFFFFF,&H00000000,&H8C000000,0,0,0,0,100,100,0,0,1,0,4,2,80,80,470,1
Style: Fora,Poppins Medium,64,&H00FFFFFF,&H00FFFFFF,&H00000000,&H66140A1E,0,0,0,0,100,100,0,0,3,14,0,2,90,90,1260,1
Style: Gancho,Poppins Black,100,&H00FFFFFF,&H00FFFFFF,&H00000000,&H99000000,0,0,0,0,100,100,-1,0,1,0,5,8,70,70,190,1
Style: Arroba,Merriweather,38,&H30ECE8EA,&H30ECE8EA,&H00000000,&H8C000000,0,1,0,0,100,100,1,0,1,0,2,2,70,70,50,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 1,{fmt(0)},{fmt(GANCHO)},Gancho,,0,0,0,,{{\\fad(0,200)\\q2}}em quem eu voto\\Namanhã,\\N{{\\fnPinyon Script\\fs230\\c&H8E9FE2&\\shad6\\frz6}}e por quê.
Dialogue: 1,{fmt(0)},{fmt(TOT)},Arroba,,0,0,0,,@giselehedler
"""+'\n'.join(lin)+'\n'
open(T+'/leg.ass','w',encoding='utf-8').write(ass)

# degradê atrás da legenda e do título, só nas falas dela
g=Image.new('RGBA',(W,H),(0,0,0,0)); dr=ImageDraw.Draw(g)
for y in range(H):
    a=0
    if 1080<=y<1750: a=int(140*min(1,(y-1080)/220)*min(1,(1750-y)/200))
    if y<640: a=max(a,int(120*(1-y/640)))
    dr.line([(0,y),(W,y)],fill=(0,0,0,a))
g.save(T+'/degrade.png')
import numpy as np, wave
M=S+'/trilhas'
t_flavio=next(x[0] for x in EV if x[2]=='Eu voto no Flávio.')
TRILHAS=[(EV[0][1],t_flavio,M+'/cold/gentlejammers_cold-revenge_main-03_underscore.wav',4),
         (t_flavio,TOT,M+'/hope/Hope for Humanity/Hope for Humanity.wav',24)]
run(['ffmpeg','-loglevel','error','-y','-i',T+'/base.mov','-map','0:a','-c:a','pcm_s16le',T+'/voz.wav'])
SR=48000; mus=np.zeros((int(SR*(TOT+1)),2),np.float32); XF=0.8
for a0,b0,f,off in TRILHAS:
    raw=subprocess.run(['ffmpeg','-loglevel','error','-ss',str(off),'-t',f'{b0-a0+XF:.3f}','-i',f,'-ac','2','-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout
    x=np.frombuffer(raw,np.float32).reshape(-1,2).copy(); x*=0.12/(np.sqrt(np.mean(x**2))+1e-9)
    nf=int(XF*SR); x[:nf]*=np.linspace(0,1,nf)[:,None]; x[-nf:]*=np.linspace(1,0,nf)[:,None]
    i=int(max(0,a0-XF/2)*SR); j=min(len(mus),i+len(x)); mus[i:j]+=x[:j-i]
with wave.open(T+'/musica.wav','wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(mus,-1,1)*32767).astype(np.int16).tobytes())
run(['ffmpeg','-loglevel','error','-y','-i',T+'/voz.wav','-i',T+'/musica.wav','-filter_complex',
     f"[0:a]asplit=2[voz][sc];[1:a]atrim=0:{TOT},volume=0.6,afade=t=out:st={TOT-2.0}:d=2.0[mus];"
     f"[mus][sc]sidechaincompress=threshold=0.04:ratio=4:attack=20:release=450[musd];"
     f"[voz][musd]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.89",'-c:a','pcm_s16le',T+'/audio_final.wav'])
SEM='+'.join(f'between(t,{x:.3f},{y:.3f})' for x,y in DE_FORA)
run(['ffmpeg','-loglevel','error','-y','-i',T+'/base.mov','-loop','1','-t',str(TOT),'-i',T+'/degrade.png','-i',T+'/audio_final.wav','-filter_complex',
     f"[0:v][1:v]overlay=enable='not({SEM})'[v1];[v1]ass={T}/leg.ass:fontsdir={F}[v]",'-map','[v]','-map','2:a','-t',str(TOT),
     '-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',E+'/reel-eleicao.mp4'])
print('ok',TOT)

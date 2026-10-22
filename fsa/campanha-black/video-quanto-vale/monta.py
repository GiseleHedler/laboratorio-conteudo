# Edita o "Resolvido" (C0059): takes escolhidos, giro para vertical, balões, selo RESOLVIDO, cartões, legenda
import subprocess, os, sys
import pausas_fala
SRC='/tmp/claude-0/-home-user/f6d0531c-9b3a-5a68-94b3-f4878f32a73b/scratchpad/drive-gabriel/C0061.MP4'
WAV='/tmp/claude-0/-home-user/f6d0531c-9b3a-5a68-94b3-f4878f32a73b/scratchpad/drive-gabriel/C0061.wav'
TMP='/tmp/claude-0/-home-user/f6d0531c-9b3a-5a68-94b3-f4878f32a73b/scratchpad/quantovale'; os.makedirs(TMP,exist_ok=True)
VERSAO=sys.argv[1] if len(sys.argv)>1 else 'organico'
B='baloes/'; P='pecas/'
# blocos: (zoom, balao, [subs (ini,fim,legenda,selo?)] ) ; sub especial ('CARD',arquivo,duracao,frame_t)
BL=[
 (1.00,None,[(14.90,18.75,'Quanto vale saber o que fazer com cada paciente',0),(18.85,20.45,'que entra no teu consultório?',0)]),
 (1.12,None,[(21.85,25.15,'A paciente cansada, com tudo normal no laudo.',0),(26.30,30.00,'Formação em Nutrição Funcional e Exames Laboratoriais.',0,P+'arte-nf.png')]),
 (1.00,None,[(34.25,39.00,'As dúvidas de qual suplemento, quanto, qual forma, com o quê?',0),(40.00,42.40,'Formação em Suplementação Individualizada.',0,P+'arte-sup.png')]),
 (1.12,None,[(47.55,51.35,'A tireoide, o hormônio fora do lugar, o ciclo desregulado.',0),(52.05,53.70,'Formação em Saúde Hormonal.',0,P+'arte-hor.png')]),
 (1.00,None,[(65.60,70.90,'A mulher tentando engravidar, o homem infértil, a gestante complicando.',0),(71.45,74.10,'Formação em Fertilidade e Gestação.',0,P+'arte-fer.png')]),
 (1.12,None,[(86.40,93.25,'O paciente que quer emagrecer ou fazer jejum e não sabe se deve, ou qual a melhor forma.',0),(93.75,95.05,'Formação em Jejum.',0,P+'arte-jej.png')]),
 (1.00,None,[(103.10,110.60,'O hemograma que tu olha e parece todo normal, mas tu sabe que tem alguma coisa errada.',0),(112.15,113.45,'Formação em Exames.',0,P+'arte-hem.png')]),
 (1.12,None,[(130.75,136.40,'A criança que reage a tudo que come, ou aquele adulto que tá sempre passando mal depois das refeições.',0),(137.05,138.60,'Alergias Alimentares.',0,P+'arte-ale.png')]),
 (1.00,None,[(146.00,149.20,'E o caso que junta tudo isso ao mesmo tempo:',0),(149.20,153.00,'Formação Avançada em Nutrição Funcional.',0,P+'arte-ava.png')]),
 (1.12,None,[(170.35,175.55,'Não é um curso, são formações completas pra enxergar o ser humano inteiro.',0)]),
 (1.00,None,[(192.70,195.35,'E agora com uma diferença: é vitalício.',0,P+'pill-vit.png'),(195.70,201.25,'Cada um desses casos pode chegar amanhã, na semana que vem ou daqui a cinco anos.',0),(205.45,207.95,'Quando chegar, a aula vai tá lá.',0)]),
 (1.12,None,[(241.15,246.20,'Comprando as formações separadas, seria R$ 19.970.',0,P+'pill-preco.png'),(247.05,250.75,'Na Black Vitalícia, menos da metade.',0,P+'pill-preco.png'),(251.20,256.10,'Todas as formações tuas pra sempre, pro resto da tua vida.',0)]),
 (1.00,None,[(300.65,305.00,'Se tu já estudou na FSA, o teu valor é ainda mais especial.',0),(305.80,308.40,'15 dias de garantia incondicional.',0),(326.95,330.20,'O vitalício termina dia 31/10.',0)]+([(330.75,333.75,'Comenta BLACK26 que eu te mando o link.',0)] if VERSAO=='organico' else [('HOLD',2.2,330.20)])),
]
def vf(z):
    w=int(2160/z)//2*2;h=int(3840/z)//2*2;x=(2160-w)//2;y=int(min(max(0.40*3840-h/2,0),3840-h))
    return f"transpose=1,crop={w}:{h}:{x}:{y},scale=1080:1920:flags=lanczos,setsar=1,fps=30,format=yuv420p"
pecas=[];linha=[];t=0;n=0
for bi,(z,balao,subs) in enumerate(BL):
    ini_bloco=t
    for s in subs:
        out=f'{TMP}/s{n:02d}.mov'
        if s[0]=='CARD':
            _,card,dur,ft=s
            cmd=['ffmpeg','-v','error','-y','-ss',str(ft),'-i',SRC,'-loop','1','-i',card,'-f','lavfi','-i','anullsrc=r=48000:cl=stereo',
                 '-filter_complex',f"[0:v]trim=end_frame=1,{vf(z)},tpad=stop_mode=clone:stop_duration={dur},trim=0:{dur}[b];[1:v]format=rgba,fade=t=in:d=0.15:alpha=1[c];[b][c]overlay=0:0:shortest=1,trim=0:{dur},setpts=PTS-STARTPTS[v]",
                 '-map','[v]','-map','2:a','-t',str(dur),'-ar','48000','-c:v','libx264','-crf','16','-preset','fast','-c:a','pcm_s16le',out]
            linha.append(('pop',t)); d=dur
        elif s[0]=='HOLD':
            _,dur,ft=s
            cmd=['ffmpeg','-v','error','-y','-ss',str(ft),'-i',SRC,'-f','lavfi','-i','anullsrc=r=48000:cl=stereo','-filter_complex',f"[0:v]trim=end_frame=1,{vf(z)},tpad=stop_mode=clone:stop_duration={dur},trim=0:{dur},setpts=PTS-STARTPTS[v]",'-map','[v]','-map','1:a','-t',str(dur),'-ar','48000','-c:v','libx264','-crf','16','-preset','fast','-c:a','pcm_s16le',out]
            d=dur
        else:
            a,b,txt,selo=s[:4]
            pcs=pausas_fala.pedacos(WAV,a,b)
            X=0.06; V=1.08
            fcs=[];vs=[];as_=[]
            for q,(pa,pb) in enumerate(pcs):
                fcs.append(f"[0:v]trim={pa-a:.3f}:{pb-a:.3f},setpts=PTS-STARTPTS,{vf(z)}[pv{q}]")
                fcs.append(f"[0:a]aresample=48000,atrim={pa-a:.3f}:{pb-a:.3f},asetpts=PTS-STARTPTS[pa{q}]")
            R=pcs[0][1]-pcs[0][0]; v='pv0'; au='pa0'
            for q in range(1,len(pcs)):
                fcs.append(f"[{v}][pv{q}]xfade=transition=fade:duration={X}:offset={R-X:.3f}[xv{q}]")
                fcs.append(f"[{au}][pa{q}]acrossfade=d={X}[xa{q}]")
                v,au=f'xv{q}',f'xa{q}'; R+=pcs[q][1]-pcs[q][0]-X
            d=round(round(R/V*30)/30,4)
            fcs.append(f"[{v}]setpts=PTS/{V},fps=30,trim=0:{d},tpad=stop_mode=clone:stop_duration=0.2,trim=0:{d},setpts=PTS-STARTPTS[v]")
            fcs.append(f"[{au}]atempo={V},atrim=0:{d},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={d-0.03:.3f}:d=0.03,apad,atrim=0:{d}[a]")
            if len(s)>4: linha.append(('arte',t,t+d,s[4]))
            cmd=['ffmpeg','-v','error','-y','-ss',str(a),'-t',str(b-a+0.3),'-i',SRC,'-filter_complex',';'.join(fcs),'-map','[v]','-map','[a]','-c:v','libx264','-crf','16','-preset','fast','-c:a','pcm_s16le','-ar','48000',out]
            linha.append(('leg',t,t+d,txt))
            if txt.startswith('O vitalício termina'): FIM_T=t
            if selo: linha.append(('selo',t))
        subprocess.run(cmd,check=True); pecas.append(out); t+=d; n+=1
    if balao: linha.append(('balao',ini_bloco,balao))
    if bi==len(BL)-1: linha.append(('fim',FIM_T))
TOTAL=t
print('total',round(TOTAL,2),'pecas',n)
open(f'{TMP}/lista.txt','w').write(''.join(f"file '{p}'\n" for p in pecas))
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',f'{TMP}/lista.txt','-c','copy',f'{TMP}/base.mov'],check=True)
# legenda ASS
def ts(x): return f"{int(x//3600)}:{int(x%3600//60):02d}:{x%60:05.2f}"
ass=["[Script Info]","ScriptType: v4.00+","PlayResX: 1080","PlayResY: 1920","WrapStyle: 0","","[V4+ Styles]",
"Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
"Style: L,Archivo Black,58,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,5,2,2,80,80,430,1","","[Events]",
"Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
fim_t=[e[1] for e in linha if e[0]=='fim'][0]
for e in linha:
    if e[0]=='leg' and e[1]<fim_t-0.05: ass.append(f"Dialogue: 0,{ts(e[1])},{ts(min(e[2],fim_t))},L,,0,0,0,,{{\\fad(60,60)}}{e[3]}")
open(f'{TMP}/leg.ass','w').write('\n'.join(ass)+'\n')
# overlays
ins=['-i',f'{TMP}/base.mov']; fc=[]; prev='0:v'; k=1; pops=[]
def add(img,T0,T1,x,y,anim=True):
    global prev,k
    ins.extend(['-loop','1','-framerate','30','-t',f'{TOTAL:.2f}','-i',img])
    fc.append(f"[{k}:v]format=rgba,fade=t=in:st={T0:.2f}:d=0.15:alpha=1,fade=t=out:st={T1-0.15:.2f}:d=0.15:alpha=1[o{k}]")
    yy=f"'{y}+40*max(0\\,1-(t-{T0:.2f})/0.15)'" if anim else str(y)
    fc.append(f"[{prev}][o{k}]overlay=x={x}:y={yy}:enable='between(t\\,{T0:.2f}\\,{T1:.2f})'[v{k}]")
    prev=f'v{k}'; k+=1
from PIL import Image
for e in linha:
    if e[0]=='balao':
        im=Image.open(e[2]); w=im.width
        if w>940:
            nw=f'{TMP}/'+os.path.basename(e[2]); im.resize((940,int(im.height*940/w))).save(nw); src=nw; w=940
        else: src=e[2]
        hh=Image.open(src).height; add(src,e[1]+0.05,e[1]+2.3,60,min(930,1360-hh)); pops.append(e[1]+0.05)
    elif e[0]=='selo':
        add(P+'selo.png',e[1]+0.05,e[1]+1.5,'(W-w)/2',1000); pops.append(e[1]+0.05)
    elif e[0]=='fim':
        add(P+('fim.png' if VERSAO=='organico' else 'fim2.png'),e[1],TOTAL,0,740); pops.append(e[1])
        for j,c in enumerate(['card-hip-p.png','card-gal-p.png','card-oli-p.png']):
            add(P+c,e[1]+0.3+0.35*j,TOTAL,'(W-w)/2',950+190*j); pops.append(e[1]+0.3+0.35*j)
    elif e[0]=='arte':
        add(e[3],e[1]+0.2,e[2],'(W-w)/2',960); pops.append(e[1]+0.2)
    elif e[0]=='pop': pops.append(e[1])
fc.append(f"[{prev}]ass={TMP}/leg.ass:fontsdir=/root/.fonts[vout]")
ins+=['-i',P+'pop.wav','-i','trilha/sweet-piano.mp3']; pi=k; mi=k+1
fc.append("[0:a]highpass=f=80,loudnorm=I=-14:TP=-1.5,aresample=48000,asplit=2[voz][sc]")
fc.append(f"[{mi}:a]aresample=48000,atrim=0:{TOTAL:.3f},volume=0.22,afade=t=in:d=0.8,afade=t=out:st={TOTAL-1.5:.3f}:d=1.5[mus0]")
fc.append("[mus0][sc]sidechaincompress=threshold=0.04:ratio=6:attack=20:release=400[mus]")
fc.append(f"[{pi}:a]asplit={len(pops)}"+''.join(f'[p{j}]' for j in range(len(pops))))
for j,T in enumerate(pops): fc.append(f"[p{j}]adelay={int(T*1000)}:all=1,volume=0.4[q{j}]")
fc.append('[voz][mus]'+''.join(f'[q{j}]' for j in range(len(pops)))+f"amix=inputs={len(pops)+2}:normalize=0:duration=first,alimiter=limit=0.9,apad,atrim=0:{TOTAL:.3f}[aout]")
out=f'video-quanto-vale-{VERSAO}.mp4'
subprocess.run(['ffmpeg','-v','error','-y',*ins,'-filter_complex',';'.join(fc),'-map','[vout]','-map','[aout]','-c:v','libx264','-crf','20','-preset','medium','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart','-t',f'{TOTAL:.2f}',out],check=True)
print('ok',out)

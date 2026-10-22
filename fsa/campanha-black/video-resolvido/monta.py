# Edita o "Resolvido" (C0059): takes escolhidos, giro para vertical, balões, selo RESOLVIDO, cartões, legenda
import subprocess, os, sys
import pausas_fala
SRC='/tmp/claude-0/-home-user/f6d0531c-9b3a-5a68-94b3-f4878f32a73b/scratchpad/drive-gabriel/C0059.MP4'
WAV='/tmp/claude-0/-home-user/f6d0531c-9b3a-5a68-94b3-f4878f32a73b/scratchpad/drive-gabriel/C0059.wav'
TMP='/tmp/claude-0/-home-user/f6d0531c-9b3a-5a68-94b3-f4878f32a73b/scratchpad/resolvido'; os.makedirs(TMP,exist_ok=True)
VERSAO=sys.argv[1] if len(sys.argv)>1 else 'organico'
B='baloes/'; P='pecas/'
# blocos: (zoom, balao, [subs (ini,fim,legenda,selo?)] ) ; sub especial ('CARD',arquivo,duracao,frame_t)
BL=[
 (1.00,B+'balao-0a-dois-anos-e-pouco.png',[(132.60,135.25,'Acesso de 2 anos é pouco?',0),(136.25,137.10,'Resolvido.',1),(137.60,139.60,'Não vão ser dois, nem cinco.',0),(140.20,142.90,'Acesso vitalício, teu pra sempre.',0)]),
 (1.12,B+'balao-0b-nao-tenho-tempo.png',[(148.20,150.95,'Mas eu não tenho tempo agora.',0),(151.80,153.80,'Resolvido também, é teu pra sempre.',1),(154.25,160.35,'Começa quando quiser, estuda no teu ritmo e vai ter os cursos quando aquele caso difícil aparecer.',0)]),
 (1.00,B+'balao-1-so-queria-exames.png',[(172.95,175.70,'Mas eu só queria o de exames.',0),(176.00,178.25,'Resolvido, tem o Galeno.',1),(178.75,185.05,'Exames Laboratoriais, Fertilidade e Gestação, Saúde Hormonal e Alergias.',0,P+'card-gal.png')]),
 (1.12,B+'balao-2-e-se-eu-quiser-tudo.png',[(216.30,217.95,'E se eu quiser tudo?',0),(218.65,219.70,'Olimpo.',1),('CARD',P+'olimpo.png',2.8,219.70),(227.00,229.45,'São mais de 300 horas aula.',0)]),
 (1.00,B+'balao-3-deve-ser-carissima.png',[(238.50,240.75,'Deve ser caríssimo.',0),('CARD',P+'cinquenta.png',2.4,240.75),(248.55,253.15,'E se tu é ou já foi aluno da FSA, tem um valor ainda mais especial.',0)]),
 (1.12,B+'balao-4-e-se-eu-nao-gostar.png',[(279.60,280.85,'E se eu não gostar?',0),(281.90,283.95,'15 dias de garantia incondicional.',1)]),
 (1.00,None,[(306.85,307.95,'É pouco ou quer mais?',0),(308.00,311.75,'Então corre, porque dia 31 termina o vitalício.',0)]+([(317.90,320.45,'Comenta BLACK26 que eu te mando o link.',0)] if VERSAO=='organico' else [('HOLD',2.2,311.75)])),
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
            if selo: linha.append(('selo',t))
        subprocess.run(cmd,check=True); pecas.append(out); t+=d; n+=1
    if balao: linha.append(('balao',ini_bloco,balao))
    if bi==len(BL)-1: linha.append(('fim',ini_bloco+1.1))
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
ins+=['-i',P+'pop.wav','-i','trilha/Uplifting.mp3']; pi=k; mi=k+1
fc.append("[0:a]highpass=f=80,loudnorm=I=-14:TP=-1.5,aresample=48000,asplit=2[voz][sc]")
fc.append(f"[{mi}:a]aresample=48000,atrim=0:{TOTAL:.3f},volume=0.22,afade=t=in:d=0.8,afade=t=out:st={TOTAL-1.5:.3f}:d=1.5[mus0]")
fc.append("[mus0][sc]sidechaincompress=threshold=0.04:ratio=6:attack=20:release=400[mus]")
fc.append(f"[{pi}:a]asplit={len(pops)}"+''.join(f'[p{j}]' for j in range(len(pops))))
for j,T in enumerate(pops): fc.append(f"[p{j}]adelay={int(T*1000)}:all=1,volume=0.4[q{j}]")
fc.append('[voz][mus]'+''.join(f'[q{j}]' for j in range(len(pops)))+f"amix=inputs={len(pops)+2}:normalize=0:duration=first,alimiter=limit=0.9,apad,atrim=0:{TOTAL:.3f}[aout]")
out=f'video-resolvido-{VERSAO}.mp4'
subprocess.run(['ffmpeg','-v','error','-y',*ins,'-filter_complex',';'.join(fc),'-map','[vout]','-map','[aout]','-c:v','libx264','-crf','20','-preset','medium','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart','-t',f'{TOTAL:.2f}',out],check=True)
print('ok',out)

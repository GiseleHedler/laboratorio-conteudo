#!/bin/bash
# Uso: editar_planta.sh entrada.mp4 saida.mp4
# Reels da planta: acelera a passagem e o replantio, desacelera a entrega para a menina,
# congela o quadro final e escreve as frases e o @ (centro, abaixo da frase).
set -e
IN="$1"; OUT="$2"
F=/tmp/claude-0/-home-user/f19a087c-4085-5aef-b35a-89b81156bb55/scratchpad/fonts
# corte para o plano aberto da entrega (detectado no próprio vídeo)
CORTE=$(ffmpeg -hide_banner -i "$IN" -vf "select='gt(scene,0.2)',showinfo" -f null - 2>&1 | grep -o "pts_time:[0-9.]*" | tail -1 | cut -d: -f2)
CORTE=${CORTE:-13.79}; echo "corte em $CORTE s"

# Saída (15 s): passagem 0-3.0 | replantio 3.0-4.6 | crescimento 4.6-6.5 | flores 6.5-8.5 | entrega lenta 8.5-12.3 | congelado até 15
T1_IN=0.2; T1_OUT=3.0
T2_IN=8.7; T2_OUT=15.1

W=$(ffprobe -v error -select_streams v:0 -show_entries stream=width -of csv=p=0 "$IN")
FS=$(( W * 78 / 1080 ))      # tamanho da frase
FW=$(( W * 30 / 1080 ))      # tamanho do @
LH=$(( FS * 112 / 100 ))     # altura da linha
Y0=$(( W * 150 / 1080 ))     # topo do bloco de texto
SH=$(( W * 3 / 1080 + 1 ))   # sombra

linha() { # texto fonte n_linha entrada saida
  echo "drawtext=fontfile=$2:text='$1':fontsize=$FS:fontcolor=0x3B2A22:x=(w-text_w)/2:y=$Y0+$3*$LH:shadowcolor=0xF5EDE4@0.5:shadowx=$SH:shadowy=$SH:alpha='if(lt(t,$4),0,if(lt(t,$4+0.5),(t-$4)/0.5,if(lt(t,$5-0.4),1,if(lt(t,$5),($5-t)/0.4,0))))'"
}

TXT="$(linha 'Por gerações,' $F/CG-Medium.ttf 0 $T1_IN $T1_OUT),\
$(linha 'a gente entregou' $F/CG-Medium.ttf 1 $T1_IN $T1_OUT),\
$(linha 'o que recebeu.' $F/CG-Medium.ttf 2 $T1_IN $T1_OUT),\
$(linha 'Até que um dia,' $F/CG-Medium.ttf 0 $T2_IN $T2_OUT),\
$(linha 'a madame' $F/CG-Italic.ttf 1 $T2_IN $T2_OUT),\
$(linha 'decidiu replantar.' $F/CG-Medium.ttf 2 $T2_IN $T2_OUT),\
drawtext=fontfile=$F/Figtree-Medium.ttf:text='@giselehedler':fontsize=$FW:fontcolor=0x3B2A22@0.55:x=(w-text_w)/2:y=$Y0+3*$LH+$LH/3:shadowcolor=0xF5EDE4@0.4:shadowx=1:shadowy=1"

ffmpeg -loglevel error -y -i "$IN" -filter_complex "\
[0:v]split=5[a][b][c][e][d];\
[a]trim=0:6,setpts=(PTS-STARTPTS)/2[va];\
[b]trim=6:10,setpts=(PTS-STARTPTS)/2.5[vb];\
[c]trim=10:12.3,setpts=(PTS-STARTPTS)/1.2[vc];\
[e]trim=12.3:$CORTE,setpts=(PTS-STARTPTS)*1.33,minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:vsbmc=1[ve];\
[d]trim=$CORTE,setpts=(PTS-STARTPTS)*3,minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:vsbmc=1,tpad=stop_mode=clone:stop_duration=4[vd];\
[va][vb][vc][ve][vd]concat=n=5:v=1:a=0,fps=24,trim=0:15,$TXT,format=yuv420p[v]" \
-map "[v]" -c:v libx264 -preset slow -crf 18 -movflags +faststart "$OUT"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT"

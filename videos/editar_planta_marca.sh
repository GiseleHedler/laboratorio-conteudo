#!/bin/bash
# Uso: editar_planta_marca.sh entrada.mp4 <claro|foto> saida.mp4
# Mesmo ritmo do editar_planta.sh, com o texto na identidade da Gisele
# (camadas PNG geradas por texto_marca.py: Merriweather + Satisfy).
set -e
IN="$1"; MODO="$2"; OUT="$3"
D=/tmp/claude-0/-home-user/f19a087c-4085-5aef-b35a-89b81156bb55/scratchpad
for q in frase1 frase2 marca; do python3 -I $D/texto_marca.py $MODO $q $D/camadas/${MODO}_$q.png; done
CORTE=$(ffmpeg -hide_banner -i "$IN" -vf "select='gt(scene,0.2)',showinfo" -f null - 2>&1 | grep -o "pts_time:[0-9.]*" | tail -1 | cut -d: -f2)
CORTE=${CORTE:-13.79}; echo "corte em $CORTE s"
# frase 1: 0.2 a 3.0 s | frase 2: 8.7 s até o fim | @ o tempo todo
ffmpeg -loglevel error -y -i "$IN" \
 -loop 1 -t 15 -i $D/camadas/${MODO}_frase1.png \
 -loop 1 -t 15 -i $D/camadas/${MODO}_frase2.png \
 -loop 1 -t 15 -i $D/camadas/${MODO}_marca.png -filter_complex "\
[0:v]split=5[a][b][c][e][d];\
[a]trim=0:6,setpts=(PTS-STARTPTS)/2[va];\
[b]trim=6:10,setpts=(PTS-STARTPTS)/2.5[vb];\
[c]trim=10:12.3,setpts=(PTS-STARTPTS)/1.2[vc];\
[e]trim=12.3:$CORTE,setpts=(PTS-STARTPTS)*1.33,minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:vsbmc=1[ve];\
[d]trim=$CORTE,setpts=(PTS-STARTPTS)*3,minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:vsbmc=1,tpad=stop_mode=clone:stop_duration=4[vd];\
[va][vb][vc][ve][vd]concat=n=5:v=1:a=0,fps=24,trim=0:15,setpts=PTS-STARTPTS[base];\
[1:v]format=rgba,fade=in:st=0.2:d=0.5:alpha=1,fade=out:st=2.6:d=0.4:alpha=1,setpts=PTS-STARTPTS[t1];\
[2:v]format=rgba,fade=in:st=8.7:d=0.6:alpha=1,setpts=PTS-STARTPTS[t2];\
[3:v]format=rgba,setpts=PTS-STARTPTS[m];\
[base][t1]overlay=shortest=1[x1];[x1][t2]overlay=shortest=1[x2];[x2][m]overlay=shortest=1,format=yuv420p[v]" \
-map "[v]" -c:v libx264 -preset slow -crf 18 -movflags +faststart "$OUT"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT"

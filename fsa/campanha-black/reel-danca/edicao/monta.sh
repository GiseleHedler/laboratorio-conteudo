#!/bin/bash
# Reel dança: 8s de dança + 5s com as informações da Black, música do exemplo por baixo
set -e
T=13.0
EL=("tit.png 8.10 0 380" "card-hip.png 8.70 100 570" "card-gal.png 9.20 100 800" "card-oli.png 9.70 100 1030" "prova.png 10.50 0 1290" "fecha.png 11.40 0 1440")
IN=(-i ../danca-bruta.mp4 -loop 1 -framerate 30 -t $T -i topo.png)
FC="color=c=0x14020D:s=1080x1920:r=30:d=$T[bg];[0:v]scale=1080:1440,fps=30,tpad=stop_mode=clone:stop_duration=5,trim=0:$T,setpts=PTS-STARTPTS,split[v1][v2];[v2]gblur=sigma=22,eq=brightness=-0.45:saturation=0.6,format=rgba,fade=t=in:st=8.0:d=0.35:alpha=1[vd];[v1][vd]overlay=0:0:enable='gte(t,8.0)'[vv];[bg][vv]overlay=0:300[c0];[c0][1:v]overlay=0:0[k0]"
prev=k0; i=2; pops=""
for e in "${EL[@]}"; do set -- $e
  IN+=(-loop 1 -framerate 30 -t $T -i $1)
  FC+=";[$i:v]format=rgba,fade=t=in:st=$2:d=0.2:alpha=1[e$i];[$prev][e$i]overlay=x=$3:y='$4+40*max(0\,1-(t-$2)/0.2)':enable='gte(t,$2)'[k$i]"
  prev=k$i; pops+="$2 "; i=$((i+1))
done
IN+=(-i musica-completa.wav -i pop.wav)
mi=$i; pi=$((i+1))
n=0; mix="[mus]"
FC+=";[$mi:a]atrim=0:$T,afade=t=out:st=12.4:d=0.6[mus];[$pi:a]asplit=6[p0][p1][p2][p3][p4][p5]"
for t in $pops; do FC+=";[p$n]adelay=$(python3 -c "print(int($t*1000))"):all=1,volume=0.35[q$n]"; mix+="[q$n]"; n=$((n+1)); done
FC+=";${mix}amix=inputs=$((n+1)):normalize=0:duration=first,alimiter=limit=0.9[a]"
ffmpeg -v error -y "${IN[@]}" -filter_complex "$FC" -map "[$prev]" -map "[a]" -t $T -c:v libx264 -crf 19 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart ../reel-danca-black-com-musica.mp4
ffmpeg -v error -y -i ../reel-danca-black-com-musica.mp4 -an -c:v copy ../reel-danca-black-sem-musica.mp4

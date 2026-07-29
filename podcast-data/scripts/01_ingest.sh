#!/bin/bash
# Ingesta: metadatos + descripciones + subtitulos automaticos ES de la playlist
export PATH=$PATH:/sessions/serene-gallant-gates/.local/bin
BASE=/sessions/serene-gallant-gates/mnt/outputs/punzadas
PL="https://www.youtube.com/playlist?list=PLLbN7SMQhMVbsBcHlP9RnBXFjZyPgam6y"
cd "$BASE/raw"
yt-dlp --skip-download --write-info-json --write-auto-subs --sub-langs "es" --sub-format json3 \
  --ignore-errors --no-abort-on-error --sleep-requests 1 \
  -o "%(id)s.%(ext)s" "$PL"
mv "$BASE"/raw/*.es.json3 "$BASE"/transcripts/ 2>/dev/null

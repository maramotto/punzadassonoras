#!/bin/bash
# Descarga por lotes: solo los IDs que aun no tienen info.json (reanudable)
export PATH=$PATH:/sessions/serene-gallant-gates/.local/bin
BASE=/sessions/serene-gallant-gates/mnt/outputs/punzadas
cd "$BASE/raw"
N=${1:-12}
cut -d'|' -f2 "$BASE/data/playlist.txt" | while read -r id; do
  [ -f "$BASE/raw/$id.info.json" ] && continue
  echo "$id"
done | head -n "$N" | while read -r id; do
  timeout 25 yt-dlp --skip-download --write-info-json --write-auto-subs --sub-langs es --sub-format json3 \
    --ignore-errors --no-abort-on-error -o "%(id)s.%(ext)s" "https://www.youtube.com/watch?v=$id" >/dev/null 2>&1
done
echo "info: $(ls $BASE/raw/*.info.json 2>/dev/null|wc -l)/66  subs: $(ls $BASE/raw/*.json3 2>/dev/null|wc -l)"

import json,glob,os,re,html,unicodedata
import xml.etree.ElementTree as ET
BASE='/sessions/serene-gallant-gates/mnt/outputs/punzadas'

def norm(s):
    s=unicodedata.normalize('NFKD',s.lower())
    s=''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+',' ',s).strip()

# --- RSS de Megaphone (117 eps, todas las temporadas) ---
rss={}
root=ET.parse(f'{BASE}/data/feed.xml').getroot()
for it in root.findall('.//item'):
    g=lambda t: (it.findtext(t) or '').strip()
    title=g('title')
    rss[norm(title)]={'rss_title':title,'rss_desc':g('description'),
                      'rss_date':g('pubDate'),'duration_s':g('{http://www.itunes.com/dtds/podcast-1.0.dtd}duration')}

SEA=re.compile(r'(\d{1,2})\s*[xX]\s*(\d{1,2})')
eps=[]
order={}
for line in open(f'{BASE}/data/playlist.txt'):
    idx,vid,t=line.rstrip('\n').split('|',2); order[vid]=int(idx)

for p in sorted(glob.glob(f'{BASE}/raw/*.info.json')):
    d=json.load(open(p))
    vid=d.get('id')
    if vid not in order: continue
    yt_title=d.get('title','')
    m=SEA.search(yt_title)
    season,epnum=(int(m.group(1)),int(m.group(2))) if m else (None,None)
    serie='Las Glosas' if ('GLOSSES' in yt_title.upper() or 'GLOSAS' in yt_title.upper()) else 'Punzadas Sonoras'
    if serie=='Las Glosas': season=None
    # titulo limpio: quita marca de serie/numero y hashtags
    clean=re.sub(r'#\w+','',yt_title)
    clean=re.sub(r'(?i)(punzadas\s+sonoras|sound\s+punches|sound\s+punctures|sounding\s+punches|the\s+glosses|las\s+glosas)','',clean)
    clean=SEA.sub('',clean)
    clean=clean.strip(' -|–—\t').strip()
    ep={'video_id':vid,'orden_playlist':order[vid],'serie':serie,'temporada':season,
        'episodio':epnum,'codigo':f"{season}x{epnum:02d}" if season and epnum else (f"Glosas 1x{epnum:02d}" if epnum else ''),
        'titulo':clean,'titulo_youtube':yt_title,
        'url_youtube':f'https://www.youtube.com/watch?v={vid}',
        'fecha':d.get('upload_date'),'duracion_s':d.get('duration'),
        'descripcion':(d.get('description') or '').split('Escolta tots els episodis')[0].strip(),
        'tiene_transcripcion':os.path.exists(f'{BASE}/transcripts/{vid}.es.json3')}
    r=rss.get(norm(clean))
    if r: ep.update({'rss_title':r['rss_title'],'rss_date':r['rss_date']})
    eps.append(ep)

eps.sort(key=lambda e:e['orden_playlist'])
json.dump(eps,open(f'{BASE}/data/episodios.json','w'),ensure_ascii=False,indent=1)
print('episodios:',len(eps))
print('con transcripcion:',sum(e['tiene_transcripcion'] for e in eps))
print('sin codigo:',[e['titulo_youtube'] for e in eps if not e['codigo']])
print('match RSS:',sum('rss_title' in e for e in eps))
from collections import Counter
print(Counter((e['serie'],e['temporada']) for e in eps))

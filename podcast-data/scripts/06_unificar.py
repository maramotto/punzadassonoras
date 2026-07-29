#!/usr/bin/env python3
"""Unifica las dos fuentes (YouTube T3-T5 y feed RSS T1-T2) en un solo dataset."""
import json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOW_SPOTIFY = 'https://open.spotify.com/show/444xAKuV4A4WUlSXqyl51P'

eps_yt = {e['video_id']: e for e in json.load(open(f'{BASE}/data/episodios.json'))}
refs_yt = json.load(open(f'{BASE}/data/refs_desc.json'))
eps_t12 = {e['codigo']: e for e in json.load(open(f'{BASE}/data/episodios_t1t2.json'))}
refs_t12 = json.load(open(f'{BASE}/data/refs_t1t2.json'))

unificado = []

# --- T1 y T2 (feed RSS / Spotify) ---
for ep in refs_t12:
    e = eps_t12[ep['codigo']]
    unificado.append({
        'clave': ep['codigo'],
        'serie': 'Punzadas Sonoras',
        'temporada': e['temporada'],
        'codigo': e['codigo'],
        'titulo': e['title'],
        'fecha': e['fecha'],
        'duracion_s': int(e['dur']) if e.get('dur') else None,
        'descripcion': e['desc'],
        'url_youtube': '',
        'url_spotify': SHOW_SPOTIFY,
        'url_audio': e.get('audio') or '',
        'tiene_transcripcion': False,
        'fuente_datos': 'feed RSS + newsletter' if ep['codigo'] >= '2x09' else 'feed RSS',
        'orden': (e['temporada'], int(e['codigo'].split('x')[1])),
        'tags': ep.get('tags', []),
        'refs': ep['refs'],
        'notas_episodio': ep.get('notas_episodio', ''),
    })

# --- T3, T4, T5 y especiales (YouTube) ---
for ep in refs_yt:
    e = eps_yt[ep['video_id']]
    temp = e['temporada']
    num = e['episodio'] or 99
    unificado.append({
        'clave': e['video_id'],
        'serie': e['serie'],
        'temporada': temp,
        'codigo': e['codigo'] or 'Especial',
        'titulo': e['titulo'],
        'fecha': f"{e['fecha'][:4]}-{e['fecha'][4:6]}-{e['fecha'][6:]}" if e.get('fecha') else '',
        'duracion_s': e.get('duracion_s'),
        'descripcion': e['descripcion'],
        'url_youtube': e['url_youtube'],
        'url_spotify': SHOW_SPOTIFY,
        'url_audio': '',
        'tiene_transcripcion': e['tiene_transcripcion'],
        'fuente_datos': 'descripción de YouTube',
        'orden': (temp or 9, num),
        'tags': ep.get('tags', []),
        'refs': ep['refs'],
        'notas_episodio': ep.get('notas_episodio', ''),
    })

unificado.sort(key=lambda x: (x['orden'][0], x['orden'][1]))
json.dump(unificado, open(f'{BASE}/data/refs_all.json', 'w'), ensure_ascii=False, indent=1)

from collections import Counter
print('episodios:', len(unificado))
print('referencias:', sum(len(e['refs']) for e in unificado))
print(Counter(e['temporada'] for e in unificado))

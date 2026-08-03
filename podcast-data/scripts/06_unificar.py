#!/usr/bin/env python3
"""Unifica las tres fuentes en un solo dataset:

  1. YouTube (T3-T5 y especiales)  -> episodios.json + refs_desc.json
  2. feed RSS (T1-T2)              -> episodios_t1t2.json + refs_t1t2.json
  3. feed RSS (los 15 que no estan en la playlist de YouTube)
                                   -> meta_faltantes.json + refs_faltantes.json

La fuente 3 son episodios que si tienen transcripcion propia pero nunca se
subieron a la playlist: 3x03, 3x17, 3x21, 4x03, 4x08, 4x16, 4x19, 5x13, 5x14,
5x18 y cinco Glosas. Su numeracion es una reconstruccion por fecha.
"""
import json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOW_SPOTIFY = 'https://open.spotify.com/show/444xAKuV4A4WUlSXqyl51P'

eps_yt = {e['video_id']: e for e in json.load(open(f'{BASE}/data/episodios.json'))}
refs_yt = json.load(open(f'{BASE}/data/refs_desc.json'))
eps_t12 = {e['codigo']: e for e in json.load(open(f'{BASE}/data/episodios_t1t2.json'))}
refs_t12 = json.load(open(f'{BASE}/data/refs_t1t2.json'))
meta_falt = json.load(open(f'{BASE}/data/meta_faltantes.json'))
refs_falt = json.load(open(f'{BASE}/data/refs_faltantes.json'))

# El podcast titula dos Glosas distintas como «1x05». Se renumeran por orden
# cronologico para que la serie sea consecutiva; el titulo original se conserva.
GLOSAS_RENUM = {
    '2026-04-16': ('Glosas 1x06', 6),   # «Rodoreda, un bosque»       (original: 1x05)
    '2026-04-30': ('Glosas 1x07', 7),   # «Sobre la salud sexual»     (original: 1x05)
}

# Correcciones de fecha detectadas al cruzar con las transcripciones del feed.
FECHA_FIX = {'3x05': '2023-11-09'}

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
    fecha = f"{e['fecha'][:4]}-{e['fecha'][4:6]}-{e['fecha'][6:]}" if e.get('fecha') else ''
    codigo = e['codigo'] or 'Especial'
    notas = ep.get('notas_episodio', '')
    fecha = FECHA_FIX.get(codigo, fecha)
    if fecha in GLOSAS_RENUM:
        codigo_nuevo, num = GLOSAS_RENUM[fecha]
        notas = (notas + ' ' if notas else '') + \
            f'Renumerado a {codigo_nuevo} por orden cronologico; el podcast lo titula «{codigo}».'
        codigo = codigo_nuevo
    unificado.append({
        'clave': e['video_id'],
        'serie': e['serie'],
        'temporada': temp,
        'codigo': codigo,
        'titulo': e['titulo'],
        'fecha': fecha,
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
        'notas_episodio': notas,
    })

# --- Los 15 que no estan en la playlist de YouTube (feed RSS) ---
def dur_a_segundos(d):
    if not d:
        return None
    if ':' not in d:
        return int(d)
    partes = [int(x) for x in d.split(':')]
    s = 0
    for p in partes:
        s = s * 60 + p
    return s

for ep in refs_falt:
    m = meta_falt[ep['fecha']]
    es_glosa = ep['serie'] == 'Las Glosas'
    unificado.append({
        'clave': ep['codigo'],
        'serie': ep['serie'],
        # Las Glosas van sin temporada, igual que las que vienen de YouTube.
        'temporada': None if es_glosa else ep['temporada'],
        'codigo': ep['codigo'],
        'titulo': m['titulo'],
        'fecha': ep['fecha'],
        'duracion_s': dur_a_segundos(m.get('duracion')),
        'descripcion': m.get('descripcion', ''),
        'url_youtube': '',
        'url_spotify': SHOW_SPOTIFY,
        'url_audio': m.get('url_audio', ''),
        'tiene_transcripcion': True,
        'fuente_datos': 'feed RSS (fuera de la playlist)',
        'orden': (9 if es_glosa else ep['temporada'], ep['orden']),
        'tags': ep.get('tags', []),
        'refs': ep['refs'],
        'notas_episodio': ep.get('notas_episodio', ''),
    })

unificado.sort(key=lambda x: (x['orden'][0], x['orden'][1], x['fecha']))
json.dump(unificado, open(f'{BASE}/data/refs_all.json', 'w'), ensure_ascii=False, indent=1)

from collections import Counter
print('episodios:', len(unificado))
print('referencias:', sum(len(e['refs']) for e in unificado))
print(Counter(e['temporada'] for e in unificado))

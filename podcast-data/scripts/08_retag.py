#!/usr/bin/env python3
"""Sustituye los tags libres de refs_all.json por la taxonomia controlada de
data/tag_mapping.json (295 tags originales -> 37 tags tematicos).

Conserva los tags libres en 'tags_originales' junto a los nuevos 'tags',
para poder revertir sin reprocesar nada.

Debe ejecutarse DESPUES de 06_unificar.py: ese script reconstruye 'tags' a
partir de las fuentes originales (refs_part1-4.json, refs_t1t2.json), asi
que si se vuelve a correr, hay que relanzar este paso despues.
"""
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

mapeo = json.load(open(f'{BASE}/data/tag_mapping.json'))
episodios = json.load(open(f'{BASE}/data/refs_all.json'))

sin_mapear = set()
for ep in episodios:
    nuevo_ep = {}
    for clave, valor in ep.items():
        if clave != 'tags':
            nuevo_ep[clave] = valor
            continue
        nuevos = []
        for tag in valor:
            if tag not in mapeo:
                sin_mapear.add(tag)
                continue
            tag_nuevo = mapeo[tag]
            if tag_nuevo not in nuevos:
                nuevos.append(tag_nuevo)
        nuevo_ep['tags'] = nuevos
        nuevo_ep['tags_originales'] = valor
    ep.clear()
    ep.update(nuevo_ep)

if sin_mapear:
    print('AVISO: tags sin mapeo, sin tocar (revisa data/tag_mapping.json):', sorted(sin_mapear))

json.dump(episodios, open(f'{BASE}/data/refs_all.json', 'w'), ensure_ascii=False, indent=1)
print('episodios actualizados:', len(episodios))

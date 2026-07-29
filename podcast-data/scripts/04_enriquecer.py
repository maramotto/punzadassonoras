#!/usr/bin/env python3
"""Enriquece las referencias con datos de Open Library y construye enlaces de compra.

Reanudable: guarda una cache en data/cache_openlibrary.json y solo consulta lo que falta.
Uso:  python3 04_enriquecer.py [n_consultas_max]
"""
import json, os, re, sys, time, unicodedata
from urllib.parse import quote_plus
from urllib.request import urlopen, Request

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = f'{BASE}/data/cache_openlibrary.json'
UA = {'User-Agent': 'PunzadasRefs/1.0 (proyecto de fans; contacto via github)'}

# Tipos que tiene sentido buscar en un catalogo de libros
TIPOS_LIBRO = {'libro', 'ensayo', 'poema', 'cuento', 'relato', 'obra de teatro', 'texto medieval', 'texto mitológico'}


def norm(s):
    s = unicodedata.normalize('NFKD', (s or '').lower())
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()


def clave(autor, obra):
    return f'{norm(autor)}||{norm(obra)}'


def consulta_openlibrary(autor, obra):
    """Devuelve dict con editorial/anio/idiomas o None."""
    q = quote_plus(f'{obra} {autor}'.strip())
    url = (f'https://openlibrary.org/search.json?q={q}&limit=3'
           '&fields=title,author_name,first_publish_year,publisher,language,key,edition_count')
    try:
        with urlopen(Request(url, headers=UA), timeout=20) as r:
            d = json.load(r)
    except Exception as e:
        return {'error': str(e)}
    docs = d.get('docs') or []
    if not docs:
        return {'sin_resultados': True}
    # preferimos el doc cuyo titulo se parezca mas al buscado
    obj = norm(obra)
    docs.sort(key=lambda x: 0 if norm(x.get('title', '')) == obj else (1 if obj in norm(x.get('title', '')) else 2))
    d0 = docs[0]
    exacto = norm(d0.get('title', '')) == obj
    autor_ok = any(norm(autor).split(' ')[-1] in norm(a) for a in (d0.get('author_name') or [])) if autor else False
    return {
        'ol_titulo': d0.get('title'),
        'ol_autor': (d0.get('author_name') or [None])[0],
        'anio_primera_edicion': d0.get('first_publish_year'),
        'editoriales': (d0.get('publisher') or [])[:6],
        'idiomas': d0.get('language') or [],
        'ol_key': d0.get('key'),
        'coincidencia_titulo': exacto,
        'coincidencia_autor': autor_ok,
    }


def confianza(info):
    if not info or info.get('sin_resultados') or info.get('error'):
        return 'sin datos'
    if info.get('coincidencia_titulo') and info.get('coincidencia_autor'):
        return 'verificado'
    return 'inferido'


def enlace_compra(autor, obra):
    return 'https://www.todostuslibros.com/busquedas?keyword=' + quote_plus(f'{obra} {autor}'.strip())


def main():
    limite = int(sys.argv[1]) if len(sys.argv) > 1 else 10**6
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    refs = json.load(open(f'{BASE}/data/refs_all.json'))

    pendientes = []
    for ep in refs:
        for r in ep['refs']:
            if not r.get('obra') or r.get('tipo') not in TIPOS_LIBRO:
                continue
            k = clave(r.get('autor', ''), r['obra'])
            if k not in cache:
                pendientes.append((k, r.get('autor', ''), r['obra']))

    # deduplicar manteniendo orden
    vistos, cola = set(), []
    for k, a, o in pendientes:
        if k not in vistos:
            vistos.add(k); cola.append((k, a, o))

    print(f'pendientes: {len(cola)}')
    for i, (k, a, o) in enumerate(cola[:limite]):
        cache[k] = consulta_openlibrary(a, o)
        time.sleep(0.6)
        if i % 10 == 9:
            json.dump(cache, open(CACHE, 'w'), ensure_ascii=False)
    json.dump(cache, open(CACHE, 'w'), ensure_ascii=False)
    print(f'cache: {len(cache)} entradas | quedan {max(0, len(cola) - limite)}')


if __name__ == '__main__':
    main()

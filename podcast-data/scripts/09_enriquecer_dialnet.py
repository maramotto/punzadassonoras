#!/usr/bin/env python3
"""Enriquece articulos academicos y tesis con datos de Dialnet (revista o
institucion, anio, paginas). Cubre el hueco que deja Open Library, que solo
indexa libros.

Reanudable: guarda una cache en data/cache_dialnet.json y solo consulta lo
que falta. Uso:  python3 09_enriquecer_dialnet.py [n_consultas_max]

Dialnet no tiene API publica: se scrapea el HTML de su buscador de
documentos. A diferencia de MCU, aqui SI funciona pegar "autor obra" en una
sola consulta de texto libre.
"""
import json, os, re, sys, time, unicodedata
from urllib.parse import quote_plus, urlencode
from urllib.request import urlopen, Request

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = f'{BASE}/data/cache_dialnet.json'
UA = {'User-Agent': 'PunzadasRefs/1.0 (proyecto de fans; contacto via github)'}

TIPOS_DIALNET = {'artículo', 'tesis doctoral', 'tesis/tfm'}


def norm(s):
    s = unicodedata.normalize('NFKD', (s or '').lower())
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()


def clave(autor, obra):
    return f'{norm(autor)}||{norm(obra)}'


def _limpiar(html_fragmento):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', html_fragmento)).strip()


def consulta_dialnet(autor, obra, reintentos=4):
    """Devuelve dict con autor/localizacion/anio del primer resultado, o None."""
    # (ver anio_de_localizacion mas abajo para el parseo del anio)
    q = f'{autor} {obra}'.strip()
    url = 'https://dialnet.unirioja.es/buscar/documentos?' + urlencode({'querysDismax.DOCUMENTAL_TODO': q})
    html = None
    for intento in range(reintentos):
        try:
            with urlopen(Request(url, headers=UA), timeout=20) as r:
                html = r.read().decode('utf-8', 'replace')
            break
        except Exception as e:
            if intento == reintentos - 1:
                return {'error': str(e)}
            time.sleep(5 * (intento + 1))  # 503 = bloqueo temporal, hay que espaciar mas

    bloques = re.findall(r'<li id="(?:articulo|tesis)\d+"[^>]*>(.*?)</li>', html, re.S)
    if not bloques:
        return {'sin_resultados': True}

    obj = norm(obra)
    mejores = []
    for b in bloques[:5]:
        t = re.search(r'class="titulo"><a[^>]*>([^<]+)</a>', b)
        a = re.search(r'class="autores"><a[^>]*>([^<]+)</a>', b)
        loc = re.search(r'class="localizacion">(.*?)</p>', b, re.S)
        titulo = t.group(1) if t else None
        mejores.append({
            'titulo': titulo,
            'autor': a.group(1) if a else None,
            'localizacion': _limpiar(loc.group(1)) if loc else None,
            'exacto': norm(titulo or '') == obj,
        })
    mejores.sort(key=lambda x: 0 if x['exacto'] else 1)
    d0 = mejores[0]
    autor_ok = any(norm(autor).split(' ')[-1] in norm(d0['autor'] or '') for _ in [0]) if autor else False
    return {
        'dialnet_titulo': d0['titulo'],
        'dialnet_autor': d0['autor'],
        'localizacion': d0['localizacion'],
        'anio': anio_de_localizacion(d0['localizacion']),
        'coincidencia_titulo': d0['exacto'],
        'coincidencia_autor': autor_ok,
    }


def anio_de_localizacion(loc):
    """Saca el anio de publicacion de la cadena de localizacion de Dialnet.

    El ISSN empieza por cuatro digitos que parecen un anio, y la version
    electronica del ISSN suele empezar por 19xx o 20xx. Un \\d{4} a secas
    cogia el ISSN en 11 de 42 fichas:

        "Eidos: Revista de Filosofia, ISSN 1692-8857, ISSN-e 2011-7477,
         N. 33, 2020, pags. 242-262"      -> guardaba 2011, es 2020
        "Minerva, ISSN 1886-340X, N. 40, 2023, pags. 60-65"
                                          -> guardaba 1886, es 2023

    Se quitan primero los ISSN y se coge el ultimo anio plausible que
    quede, que es el de la revista o el del ejemplar."""
    if not loc:
        return None
    limpio = re.sub(r'ISSN(?:-e)?\s*[\dX-]+', ' ', loc, flags=re.I)
    candidatos = re.findall(r'\b(1[89]\d{2}|20[0-2]\d)\b', limpio)
    return candidatos[-1] if candidatos else None


def confianza(info):
    if not info or info.get('sin_resultados') or info.get('error'):
        return 'sin datos'
    if info.get('coincidencia_titulo') and info.get('coincidencia_autor'):
        return 'verificado'
    return 'inferido'


def main():
    limite = int(sys.argv[1]) if len(sys.argv) > 1 else 10**6
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    ol_cache = json.load(open(f'{BASE}/data/cache_openlibrary.json'))
    refs = json.load(open(f'{BASE}/data/refs_all.json'))

    def clave_ol(autor, obra):
        return f'{norm(autor)}||{norm(obra)}'

    pendientes, vistos = [], set()
    for ep in refs:
        for r in ep['refs']:
            if not r.get('obra') or norm(r.get('tipo', '')) not in {norm(t) for t in TIPOS_DIALNET}:
                continue
            if (ol_cache.get(clave_ol(r.get('autor', ''), r['obra']), {}) or {}).get('editoriales'):
                continue  # Open Library ya lo resolvio
            k = clave(r.get('autor', ''), r['obra'])
            if k not in cache and k not in vistos:
                vistos.add(k)
                pendientes.append((k, r.get('autor', ''), r['obra']))

    print(f'pendientes: {len(pendientes)}')
    for i, (k, a, o) in enumerate(pendientes[:limite]):
        cache[k] = consulta_dialnet(a, o)
        time.sleep(3.5)
        if i % 10 == 9:
            json.dump(cache, open(CACHE, 'w'), ensure_ascii=False, indent=1)
    json.dump(cache, open(CACHE, 'w'), ensure_ascii=False, indent=1)
    print(f'cache: {len(cache)} entradas | quedan {max(0, len(pendientes) - limite)}')


if __name__ == '__main__':
    main()

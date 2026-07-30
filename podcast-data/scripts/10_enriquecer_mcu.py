#!/usr/bin/env python3
"""Enriquece libros/ensayos con editorial y anio de la base de datos ISBN
del Ministerio de Cultura, para el ensayo espanol de editorial pequena que
Open Library no cubre.

Reanudable: guarda una cache en data/cache_mcu.json y solo consulta lo que
falta. Uso:  python3 10_enriquecer_mcu.py [n_consultas_max]

La base del ISBN no tiene API publica: es una app con sesion (cookie
JSESSIONID) que hay que scrapear. Se usa curl via subprocess -- via urllib
falla con CERTIFICATE_VERIFY_FAILED en este entorno porque su cadena de
certificados no esta en el bundle por defecto de Python, aunque curl (que
usa el llavero del sistema) la resuelve sin problema.

A diferencia de Open Library/Dialnet, aqui pegar "autor completo + titulo
completo" en una sola consulta reduce mucho el acierto (el buscador hace
un AND estricto de cada palabra). Se prueba primero solo el titulo; si no
hay resultados, apellido del autor + primeras palabras del titulo.
"""
import json, os, re, subprocess, sys, tempfile, time, unicodedata

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = f'{BASE}/data/cache_mcu.json'
INIT_URL = ('https://www.cultura.gob.es/webISBN/tituloSimpleFilter.do'
            '?cache=init&prev_layout=busquedaisbn&layout=busquedaisbn&language=es')
BUSCA_URL = 'https://www.cultura.gob.es/webISBN/tituloSimpleDispatch.do'

TIPOS_MCU = {'libro', 'ensayo', 'cuento', 'poema', 'relato', 'obra de teatro',
             'texto medieval', 'texto mitológico'}


def norm(s):
    s = unicodedata.normalize('NFKD', (s or '').lower())
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()


def clave(autor, obra):
    return f'{norm(autor)}||{norm(obra)}'


def _curl_get(url, jar):
    subprocess.run(['curl', '-s', '-L', '--max-time', '20', '-c', jar, '-b', jar, url],
                   capture_output=True)


def _curl_post(url, campos, jar):
    args = ['curl', '-s', '-L', '--max-time', '20', '-c', jar, '-b', jar, '-X', 'POST', url]
    for k, v in campos.items():
        args += ['--data-urlencode', f'{k}={v}']
    r = subprocess.run(args, capture_output=True)
    return r.stdout.decode('cp1252', 'replace')


def _busca_mcu(texto, jar):
    html = _curl_post(BUSCA_URL, {
        'params.forzaQuery': 'N', 'params.cdispo': 'A', 'params.cisbnExt': '',
        'params.liConceptosExt[0].texto': texto, 'params.orderByFormId': '3',
        'language': 'es', 'prev_layout': 'busquedaisbn', 'layout': 'busquedaisbn',
        'action': 'Buscar',
    }, jar)
    bloques = re.findall(r'<div class="isbnResDescripcion">(.*?)</div>\s*</div>', html, re.S)
    resultados = []
    for b in bloques[:5]:
        m_tit = re.search(r'<a[^>]*>([^<]+)</a>', b)
        anio = re.search(r'\((\d{4})\)', b)
        autor_m = re.search(r'Autor/es:&nbsp;\s*<strong>([^<]+)</strong>', b)
        ed_m = re.search(r'Editorial/es:&nbsp;\s*<a[^>]*>([^<]+)</a>', b)
        resultados.append({
            'titulo': m_tit.group(1) if m_tit else None,
            'anio': anio.group(1) if anio else None,
            'autor': autor_m.group(1).strip() if autor_m else None,
            'editorial': ed_m.group(1) if ed_m else None,
        })
    return resultados


def consulta_mcu(autor, obra, jar):
    """Devuelve dict con editorial/anio o None. Reintenta con una consulta
    mas simple si la busqueda por titulo completo no encuentra nada."""
    candidatos = _busca_mcu(obra, jar)
    if not candidatos:
        apellido = (autor or '').split(' ')[-1]
        candidatos = _busca_mcu(f'{apellido} {" ".join(obra.split()[:4])}', jar)
    if not candidatos:
        return {'sin_resultados': True}

    obj = norm(obra)
    apellido_buscado = norm(autor).split(' ')[-1] if autor else ''

    def coincide_titulo(c):
        # El titulo principal puede llevar subtitulo en cualquiera de las
        # dos fuentes y no en la otra (p. ej. nosotros "Decir el mal" vs
        # MCU "Decir el mal : la destruccion del nosotros"; o al reves,
        # nosotros "Los laberintos del aire. Vientos, miasmas..." vs MCU
        # solo "Los laberintos del aire"), asi que cualquiera de los dos
        # siendo prefijo del otro cuenta como coincidencia.
        t = norm(c['titulo'] or '')
        if not t or not obj:
            return False
        return t == obj or t.startswith(obj + ' ') or obj.startswith(t + ' ')

    def autor_coincide(c):
        return bool(apellido_buscado) and apellido_buscado in norm(c['autor'] or '')

    def rango_titulo(c):
        return 0 if norm(c['titulo'] or '') == obj else (0 if coincide_titulo(c) else 2)

    # Ante un empate de titulo (frecuente con titulos comunes: "La baba del
    # caracol" tiene una edicion de 1985/2019 de otro autor ademas de la de
    # Maillard de 2014), el autor decide el desempate en vez del orden en
    # que MCU devuelve los resultados (alfabetico por apellido).
    candidatos.sort(key=lambda c: (rango_titulo(c), 0 if autor_coincide(c) else 1))
    d0 = candidatos[0]
    exacto = coincide_titulo(d0)
    autor_ok = bool(autor) and norm(autor).split(' ')[-1] in norm(d0['autor'] or '')
    return {
        'mcu_titulo': d0['titulo'],
        'mcu_autor': d0['autor'],
        'editorial': d0['editorial'],
        'anio': d0['anio'],
        'coincidencia_titulo': exacto,
        'coincidencia_autor': autor_ok,
    }


def confianza(info):
    if not info or info.get('sin_resultados') or info.get('error') or not info.get('editorial'):
        return 'sin datos'
    if info.get('coincidencia_titulo') and info.get('coincidencia_autor'):
        return 'verificado'
    return 'inferido'


def main():
    limite = int(sys.argv[1]) if len(sys.argv) > 1 else 10**6
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    ol_cache = json.load(open(f'{BASE}/data/cache_openlibrary.json'))
    refs = json.load(open(f'{BASE}/data/refs_all.json'))

    pendientes, vistos = [], set()
    for ep in refs:
        for r in ep['refs']:
            if not r.get('obra') or norm(r.get('tipo', '')) not in {norm(t) for t in TIPOS_MCU}:
                continue
            if (ol_cache.get(clave(r.get('autor', ''), r['obra']), {}) or {}).get('editoriales'):
                continue  # Open Library ya lo resolvio
            k = clave(r.get('autor', ''), r['obra'])
            if k not in cache and k not in vistos:
                vistos.add(k)
                pendientes.append((k, r.get('autor', ''), r['obra']))

    print(f'pendientes: {len(pendientes)}')
    with tempfile.TemporaryDirectory() as td:
        jar = os.path.join(td, 'cookies.txt')
        _curl_get(INIT_URL, jar)
        for i, (k, a, o) in enumerate(pendientes[:limite]):
            cache[k] = consulta_mcu(a, o, jar)
            time.sleep(0.5)
            if i % 10 == 9:
                json.dump(cache, open(CACHE, 'w'), ensure_ascii=False, indent=1)
                _curl_get(INIT_URL, jar)  # refresca la sesion por si caduco
    json.dump(cache, open(CACHE, 'w'), ensure_ascii=False, indent=1)
    print(f'cache: {len(cache)} entradas | quedan {max(0, len(pendientes) - limite)}')


if __name__ == '__main__':
    main()

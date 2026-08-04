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
import difflib, json, os, re, subprocess, sys, tempfile, time, unicodedata

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


# --- Reconocer autores -----------------------------------------------------
#
# Nosotros escribimos "Nombre Apellido" y el MCU escribe "Apellido, Nombre".
# Ademas nuestras referencias traen a veces varios autores, coordinadores o
# la marca de anonimato. Comparar solo la ultima palabra de nuestro campo
# contra la cadena del MCU fallaba en cinco casos reales:
#
#   "Laura C. Vela y Carlota Visier"     -> ultima palabra "visier"
#                                           MCU "Carrascosa Vela, Laura"
#   "Rosana Trivino y Txetxu Ausin (eds.)" -> ultima palabra "eds"
#   "Anonimo" / "VV.AA."                 -> el MCU no trae autor: no es un
#                                           fallo, es que no aplica
#   "Mohamed Chukri"                     -> MCU "Sukri, Muhammad" (otra
#                                           transliteracion del mismo nombre)

ANONIMOS = {'anonimo', 'anonima', 'vv aa', 'vvaa', 'varios autores', 'aa vv'}
PARTICULAS = {'de', 'del', 'la', 'las', 'los', 'el', 'van', 'von', 'da', 'di', 'y'}
ROLES = re.compile(r'\(?\b(eds?|coords?|comps?|dirs?)\b\.?\)?', re.I)


def personas(autor):
    """Parte un campo de autor en nombres sueltos."""
    s = ROLES.sub(' ', autor or '')
    return [p.strip() for p in re.split(r'\s+y\s+|&|;|,', s) if p.strip()]


def tokens_nombre(nombre):
    """Palabras utiles de un nombre: fuera particulas e iniciales sueltas."""
    return [t for t in norm(nombre).split() if len(t) > 2 and t not in PARTICULAS]


def autor_coincide(autor_nuestro, autor_mcu):
    """True si los dos campos designan a la misma persona. Tolera el orden
    invertido, varios autores y pequenas variaciones de transliteracion.

    Cuando ambos lados dan nombre y apellido se exigen DOS coincidencias,
    no una: compartir solo el apellido no basta. "Juan Evaristo Boix" y
    "Boix, Frederic" son dos personas distintas, y con una sola
    coincidencia el MCU nos colaba un estudio sobre prostitucion de 1969
    como si fuera "El derecho a las cosas bellas"."""
    if norm(autor_nuestro) in ANONIMOS or not (autor_nuestro or '').strip():
        # Obra anonima o colectiva: coincide si el MCU tampoco da autor.
        return not (autor_mcu or '').strip()
    mcu = tokens_nombre(autor_mcu)
    if not mcu:
        return False
    for p in personas(autor_nuestro):
        nuestros = tokens_nombre(p)
        if not nuestros:
            continue
        aciertos = 0
        for t in nuestros:
            if t in mcu or any(difflib.SequenceMatcher(None, t, m).ratio() >= 0.85
                               for m in mcu):
                aciertos += 1
        # Si alguno de los dos lados solo trae una palabra util (autores de
        # un solo nombre, o fichas del MCU sin nombre de pila), basta una.
        necesarias = 2 if len(nuestros) >= 2 and len(mcu) >= 2 else 1
        if aciertos >= necesarias:
            return True
    return False


# --- Reconocer editoriales que en realidad son personas --------------------
#
# El MCU rellena el campo de editorial con el nombre del autor cuando el
# libro es autoeditado o de deposito. Eso colaba cosas como
# "Aguado Rubira, Pedro Francisco" o "Badenes Bou, Maria Elena" en la
# columna Editorial de la hoja.

CORPORATIVO = re.compile(
    r'\b(s\s*l\s*u?|s\s*a\s*u?|sociedad|editorial|editoriales|ediciones|edicions'
    r'|editora|editores|libros|publicaciones|publishing|grupo|universidad|universitat'
    r'|instituto|institut|fundacion|fundacio|gobierno|generalitat|ayuntamiento|diputacion'
    r'|consejo|consorcio|servicio|prensa|press|books|verlag|editions|impresa|imprenta)\b')


def editorial_es_persona(ed):
    """True si el campo editorial tiene forma «Apellido(s), Nombre»."""
    if not ed or ',' not in ed:
        return False
    if CORPORATIVO.search(norm(ed)):
        return False
    izq, der = ed.split(',', 1)
    nombre = r'^[A-ZÁÉÍÓÚÑ][\wáéíóúñü\'-]*(\s+[\wáéíóúñü\'-]+)*\.?$'
    return bool(re.match(nombre, izq.strip())) and bool(re.match(nombre, der.strip()))


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


def titulo_coincide(obra, titulo_mcu):
    # El titulo principal puede llevar subtitulo en cualquiera de las dos
    # fuentes y no en la otra (p. ej. nosotros "Decir el mal" vs MCU
    # "Decir el mal : la destruccion del nosotros"; o al reves, nosotros
    # "Los laberintos del aire. Vientos, miasmas..." vs MCU solo "Los
    # laberintos del aire"), asi que cualquiera de los dos siendo prefijo
    # del otro cuenta como coincidencia.
    obj, t = norm(obra), norm(titulo_mcu or '')
    if not t or not obj:
        return False
    return t == obj or t.startswith(obj + ' ') or obj.startswith(t + ' ')


def evaluar(autor, obra, cand):
    """Convierte un candidato del MCU en entrada de cache, o lo descarta.

    Un candidato solo vale si coincide el titulo o el autor. Si no coincide
    ninguno de los dos es que el buscador devolvio otra cosa: "El hombre
    joven" de Ernaux emparejaba con "La atraccion sexual del hombre joven"
    de Juan Julio de Abajo, y se publicaba como dato bueno."""
    tit_ok = titulo_coincide(obra, cand.get('titulo'))
    aut_ok = autor_coincide(autor, cand.get('autor'))
    if not tit_ok and not aut_ok:
        return {'sin_resultados': True, 'descartado': 'ni titulo ni autor',
                'mcu_titulo': cand.get('titulo'), 'mcu_autor': cand.get('autor')}
    editorial = cand.get('editorial')
    descartada = None
    if editorial_es_persona(editorial):
        descartada, editorial = editorial, None
    info = {
        'mcu_titulo': cand.get('titulo'),
        'mcu_autor': cand.get('autor'),
        'editorial': editorial,
        'anio': cand.get('anio'),
        'coincidencia_titulo': tit_ok,
        'coincidencia_autor': aut_ok,
    }
    if descartada:
        info['editorial_descartada'] = descartada
    return info


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

    def rango_titulo(c):
        return 0 if titulo_coincide(obra, c['titulo']) else 2

    # Ante un empate de titulo (frecuente con titulos comunes: "La baba del
    # caracol" tiene una edicion de 1985/2019 de otro autor ademas de la de
    # Maillard de 2014), el autor decide el desempate en vez del orden en
    # que MCU devuelve los resultados (alfabetico por apellido).
    candidatos.sort(key=lambda c: (rango_titulo(c),
                                   0 if autor_coincide(autor, c['autor']) else 1))
    return evaluar(autor, obra, candidatos[0])


def confianza(info):
    if not info or info.get('sin_resultados') or info.get('error') or not info.get('editorial'):
        return 'sin datos'
    if info.get('coincidencia_titulo') and info.get('coincidencia_autor'):
        return 'verificado'
    return 'inferido'


def reevaluar():
    """Vuelve a aplicar las reglas de aceptacion sobre el cache ya
    descargado, sin tocar la red. El cache no guarda el autor y el titulo
    originales (la clave va normalizada), asi que se recuperan de
    refs_all.json."""
    cache = json.load(open(CACHE))
    refs = json.load(open(f'{BASE}/data/refs_all.json'))
    originales = {}
    for ep in refs:
        for r in ep['refs']:
            if r.get('obra'):
                originales.setdefault(clave(r.get('autor', ''), r['obra']),
                                      (r.get('autor', ''), r['obra']))
    cambios = {'descartados': [], 'editorial_quitada': [], 'ascendidos': [], 'sin_cambio': 0}
    for k, v in cache.items():
        if not isinstance(v, dict) or v.get('error') or 'mcu_titulo' not in v:
            continue
        if k not in originales:
            continue  # referencia que ya no esta en el catalogo
        autor, obra = originales[k]
        antes = confianza(v)
        nuevo = evaluar(autor, obra, {'titulo': v.get('mcu_titulo'), 'autor': v.get('mcu_autor'),
                                      'editorial': v.get('editorial') or v.get('editorial_descartada'),
                                      'anio': v.get('anio')})
        cache[k] = nuevo
        despues = confianza(nuevo)
        etiqueta = f'{autor} — {obra}'
        if nuevo.get('descartado'):
            cambios['descartados'].append(etiqueta)
        elif nuevo.get('editorial_descartada'):
            cambios['editorial_quitada'].append(f"{etiqueta}  [{nuevo['editorial_descartada']}]")
        elif antes != despues and despues == 'verificado':
            cambios['ascendidos'].append(etiqueta)
        else:
            cambios['sin_cambio'] += 1
    json.dump(cache, open(CACHE, 'w'), ensure_ascii=False, indent=1)
    for titulo, clave_c in [('DESCARTADOS (ni titulo ni autor)', 'descartados'),
                            ('EDITORIAL QUITADA (era una persona)', 'editorial_quitada'),
                            ('ASCENDIDOS a verificado', 'ascendidos')]:
        print(f'\n--- {titulo}: {len(cambios[clave_c])} ---')
        for x in cambios[clave_c]:
            print('   ', x)
    print(f'\nsin cambio: {cambios["sin_cambio"]}')


def main():
    if '--reevaluar' in sys.argv:
        return reevaluar()
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

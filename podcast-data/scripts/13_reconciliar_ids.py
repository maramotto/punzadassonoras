#!/usr/bin/env python3
"""Reconcilia identificadores entre extraccion/, manifiesto_audio.json y refs_all.json.

Problema de partida: 13 episodios ya extraidos no tenian su "codigo" enlazado en el
manifiesto (constaban con codigo vacio pese a existir su extraccion), y 27 entradas del
manifiesto -los especiales y Las Glosas- no tienen codigo de temporada. Ademas, el
"titulo" no es fiable como clave: en 9 episodios difiere entre extraccion/ (titulo de
trabajo, a veces en mayusculas o con "(LIVE)") y el manifiesto (titulo publicado). El
caso mas claro es el 5x11: "MARGENES SILENTES..." en extraccion frente a "Pensar el
silencio..." en el manifiesto. Por eso el identificador se calcula UNA SOLA VEZ, desde
el titulo del manifiesto (fuente autorizada), y se propaga por "fecha" -clave fiable,
compartida por los tres ficheros- en vez de recalcularse en cada fichero por separado.

Asigna a cada episodio "id" = "{fecha}_{slug-del-titulo-del-manifiesto}". No toca el
campo "slug" existente del manifiesto (los ficheros de transcripcion ya validados usan
ese nombre) ni renombra ninguna transcripcion. "codigo" queda como campo aparte y
opcional: se enlaza cuando se conoce (el codigo de temporada real, o "Glosas 1xNN" segun
refs_all.json) y se deja vacio para los especiales sin numeracion propia.

De paso enlaza "video_id" cuando el manifiesto lo tiene vacio pero el campo "clave" de
refs_all.json resulta ser un id de YouTube real (11 caracteres) en vez del texto
placeholder "Glosas 1xNN": son 5 casos (Punziber y las Glosas 1x02, 1x03, 1x06 y 1x07)
que si tienen video en YouTube y el manifiesto no lo sabia.

Uso:
    python3 13_reconciliar_ids.py             aplica los cambios
    python3 13_reconciliar_ids.py --dry-run    solo muestra lo que haria

Idempotente: una segunda pasada no cambia nada si la primera ya se aplico. Guarda una
copia .bak de cada fichero antes de escribir en el, salvo en --dry-run.
"""
import glob
import json
import os
import re
import shutil
import sys
import unicodedata
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
EXTRACCION = os.path.join(BASE, "extraccion")
RUTA_MANIFIESTO = os.path.join(DATA, "manifiesto_audio.json")
RUTA_REFS = os.path.join(DATA, "refs_all.json")


def slugify(texto):
    texto = texto.lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"[^a-z0-9]+", "-", texto)
    return texto.strip("-")


def cargar_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def insertar_id_extraccion(path, nuevo_id, dry_run):
    """Anade "id" al final del objeto de un fichero extraccion/<codigo>.json tocando
    solo el texto, sin volver a serializar el JSON entero. Estos ficheros usan arrays
    cortos en una sola linea ("en_dialogo_con": ["Marcelino"]) que json.dump no
    reproduce -expande siempre cada lista-, y reescribirlos enteros ensuciaria el diff
    de los 104 ficheros con solo anadir un campo a cada uno."""
    with open(path, encoding="utf-8") as f:
        texto = f.read()
    cuerpo = texto.rstrip()
    if not cuerpo.endswith("}"):
        raise ValueError(f"{path}: no termina en '}}', no se puede insertar de forma segura")
    cuerpo = cuerpo[:-1].rstrip()
    nuevo_texto = f'{cuerpo},\n  "id": "{nuevo_id}"\n}}\n'
    # comprobacion de seguridad: el resultado debe seguir siendo JSON valido y con
    # el mismo contenido salvo el campo nuevo
    reparseado = json.loads(nuevo_texto)
    if reparseado.get("id") != nuevo_id:
        raise ValueError(f"{path}: el id insertado no se leyo de vuelta correctamente")
    if dry_run:
        return
    shutil.copy2(path, path + ".bak")
    with open(path, "w", encoding="utf-8") as f:
        f.write(nuevo_texto)


def guardar_json(path, data, dry_run, indent=2):
    # indent=1 para los ficheros que son una lista de episodios (manifiesto, refs_all):
    # es el formato con el que ya estan en el repo, y usar 2 aqui reformatearia el
    # fichero entero y taparia el diff real bajo miles de lineas de indentacion.
    if dry_run:
        return
    if os.path.exists(path):
        shutil.copy2(path, path + ".bak")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)
        f.write("\n")


def main():
    dry_run = "--dry-run" in sys.argv
    prefijo = "[DRY-RUN] " if dry_run else ""

    manifiesto = cargar_json(RUTA_MANIFIESTO)
    refs_all = cargar_json(RUTA_REFS)

    rutas_extraccion = sorted(glob.glob(os.path.join(EXTRACCION, "*.json")))
    extraccion = {os.path.basename(p)[:-5]: cargar_json(p) for p in rutas_extraccion}
    extraccion_por_fecha = {}
    for codigo, d in extraccion.items():
        extraccion_por_fecha.setdefault(d["fecha"], []).append(codigo)

    refs_codigo_por_fecha = {e["fecha"]: e.get("codigo", "") for e in refs_all}
    refs_clave_por_fecha = {e["fecha"]: e.get("clave", "") for e in refs_all}
    patron_youtube_id = re.compile(r"^[A-Za-z0-9_-]{11}$")

    # --- id canonico, calculado una sola vez desde el titulo del manifiesto ---
    ids_por_fecha = {}
    contador_slug = Counter()
    for e in manifiesto:
        nuevo_id = f"{e['fecha']}_{slugify(e['titulo'])}"
        ids_por_fecha[e["fecha"]] = nuevo_id
        contador_slug[nuevo_id] += 1

    colisiones = {slug: n for slug, n in contador_slug.items() if n > 1}
    if colisiones:
        print("ERROR: dos episodios de fechas distintas generan el mismo id. Aborto sin escribir nada:")
        for slug, n in colisiones.items():
            print(f"  {slug!r} ({n} veces)")
        sys.exit(1)

    # --- manifiesto: id + enlace de "codigo" donde falte ---
    cambios_manifiesto = 0
    codigos_enlazados = []
    video_ids_enlazados = []
    for e in manifiesto:
        nuevo_id = ids_por_fecha[e["fecha"]]
        if e.get("id") != nuevo_id:
            e["id"] = nuevo_id
            cambios_manifiesto += 1

        if not e.get("codigo"):
            fecha = e["fecha"]
            candidatos = extraccion_por_fecha.get(fecha, [])
            if len(candidatos) == 1:
                e["codigo"] = candidatos[0]
                codigos_enlazados.append((nuevo_id, candidatos[0]))
                cambios_manifiesto += 1
            elif not candidatos:
                codigo_refs = refs_codigo_por_fecha.get(fecha, "")
                if codigo_refs.startswith("Glosas"):
                    e["codigo"] = codigo_refs
                    cambios_manifiesto += 1
                # especiales puros (Punziber, los cuatro elementos): "codigo" queda
                # vacio a proposito, es opcional y no tienen numeracion de temporada.

        if not e.get("video_id"):
            clave = refs_clave_por_fecha.get(e["fecha"], "")
            if patron_youtube_id.match(clave):
                e["video_id"] = clave
                video_ids_enlazados.append((nuevo_id, clave))
                cambios_manifiesto += 1

    # --- extraccion/*.json: id propagado por fecha, nunca recalculado del propio titulo ---
    cambios_extraccion = 0
    fechas_extraccion_sin_manifiesto = []
    for codigo, d in extraccion.items():
        fecha = d["fecha"]
        if fecha not in ids_por_fecha:
            fechas_extraccion_sin_manifiesto.append(codigo)
            continue
        nuevo_id = ids_por_fecha[fecha]
        if d.get("id") != nuevo_id:
            path = os.path.join(EXTRACCION, f"{codigo}.json")
            insertar_id_extraccion(path, nuevo_id, dry_run)
            cambios_extraccion += 1

    # --- refs_all.json: mismo id, por fecha ---
    cambios_refs = 0
    fechas_refs_sin_manifiesto = []
    for e in refs_all:
        fecha = e["fecha"]
        if fecha not in ids_por_fecha:
            fechas_refs_sin_manifiesto.append(e.get("clave"))
            continue
        nuevo_id = ids_por_fecha[fecha]
        if e.get("id") != nuevo_id:
            e["id"] = nuevo_id
            cambios_refs += 1

    if cambios_manifiesto:
        guardar_json(RUTA_MANIFIESTO, manifiesto, dry_run, indent=1)
    if cambios_refs:
        guardar_json(RUTA_REFS, refs_all, dry_run, indent=1)

    print(f"{prefijo}manifiesto: {cambios_manifiesto} campo(s) actualizados sobre {len(manifiesto)} entradas")
    print(f"  codigo enlazado desde extraccion o refs_all: {len(codigos_enlazados)}")
    for nuevo_id, c in codigos_enlazados:
        print(f"    {nuevo_id} -> {c}")
    print(f"  video_id enlazado desde refs_all.clave: {len(video_ids_enlazados)}")
    for nuevo_id, v in video_ids_enlazados:
        print(f"    {nuevo_id} -> {v}")
    print(f"{prefijo}extraccion: {cambios_extraccion} fichero(s) actualizados sobre {len(extraccion)}")
    print(f"{prefijo}refs_all: {cambios_refs} entrada(s) actualizadas sobre {len(refs_all)}")
    if fechas_extraccion_sin_manifiesto:
        print(f"AVISO: extracciones sin fecha en el manifiesto: {fechas_extraccion_sin_manifiesto}")
    if fechas_refs_sin_manifiesto:
        print(f"AVISO: entradas de refs_all sin fecha en el manifiesto: {fechas_refs_sin_manifiesto}")

    print()
    verificar(dry_run)


def verificar(dry_run):
    """Comprueba que la reconciliacion quedo bien. Si --dry-run, verifica el estado
    ANTERIOR a los cambios (informativo); si no, verifica lo que se acaba de escribir."""
    manifiesto = cargar_json(RUTA_MANIFIESTO)
    rutas_extraccion = sorted(glob.glob(os.path.join(EXTRACCION, "*.json")))
    extraccion = {os.path.basename(p)[:-5]: cargar_json(p) for p in rutas_extraccion}

    fallos = []

    ids_manifiesto = [e.get("id") for e in manifiesto]
    if any(not i for i in ids_manifiesto):
        fallos.append("hay entradas del manifiesto sin 'id'")
    duplicados = [i for i, n in Counter(ids_manifiesto).items() if n > 1]
    if duplicados:
        fallos.append(f"ids duplicados en el manifiesto: {duplicados}")

    ids_manifiesto_set = set(ids_manifiesto)
    for codigo, d in extraccion.items():
        eid = d.get("id")
        if not eid:
            fallos.append(f"extraccion {codigo} sin 'id'")
        elif eid not in ids_manifiesto_set:
            fallos.append(f"extraccion {codigo} (id={eid!r}) no casa con ninguna entrada del manifiesto")

    if dry_run:
        print("VERIFICACION (estado previo, informativa en --dry-run):")
    if fallos:
        print(f"VERIFICACION: FALLA ({len(fallos)})")
        for f in fallos:
            print(" -", f)
        if not dry_run:
            sys.exit(1)
    else:
        print("VERIFICACION: OK — todo episodio del manifiesto tiene id unico y toda extraccion casa con exactamente una entrada")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Valida un archivo de extraccion/<codigo>.json contra la transcripcion citada.

Uso: python3 11_validar_extraccion.py 5x21

Sale con codigo != 0 si alguna comprobacion falla.
"""
import json
import os
import re
import sys
import unicodedata
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TIPOS = {"libro", "artículo", "película", "serie", "obra de teatro", "poema",
         "obra de arte", "música", "podcast", "persona", "concepto", "otro"}
FUNCIONES = {"eje del episodio", "apoyo teórico", "ejemplo", "contrapunto",
             "mención de pasada", "recomendación"}
ALCANCES = {"obra completa", "un capítulo o figura", "un pasaje o cita", "solo el autor"}
SOPORTES = {"leído", "visto", "escuchado", "citado de oídas", "sin determinar"}
TONOS = {"entusiasta", "crítico", "ambivalente", "neutro"}
GRADOS = {"primera mano", "dentro de otra fuente"}
FUENTES = {"audio", "descripción", "ambas"}
CONFIANZAS = {"alta", "media", "baja"}

OBLIGATORIOS = ["id", "autor", "tipo", "funcion", "fuente", "confianza"]

WINDOW_BEFORE = 30
WINDOW_AFTER = 90


def normalizar(texto):
    texto = texto.lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def cargar_transcripcion(nombre):
    path = os.path.join(BASE, "transcribir", "transcripciones", nombre)
    with open(path, encoding="utf-8") as f:
        return json.load(f)["segmentos"]


def construir_corpus(segs):
    """Concatena los textos de los segmentos con un solo espacio, normalizados,
    y guarda el offset normalizado de inicio de cada segmento."""
    piezas = []
    offsets = []  # offset normalizado -> indice de segmento
    pos = 0
    for i, s in enumerate(segs):
        norm = normalizar(s["texto"])
        offsets.append((pos, pos + len(norm), i))
        piezas.append(norm)
        pos += len(norm) + 1  # +1 por el espacio separador
    corpus = " ".join(piezas)
    return corpus, offsets


def segmento_en_offset(offsets, pos):
    for start, end, idx in offsets:
        if start <= pos <= end:
            return idx
    # cae en un espacio separador: usa el segmento anterior
    for start, end, idx in offsets:
        if pos < start:
            return max(idx - 1, 0)
    return offsets[-1][2]


def main():
    if len(sys.argv) != 2:
        print("Uso: 11_validar_extraccion.py <codigo_episodio>", file=sys.stderr)
        sys.exit(2)

    codigo = sys.argv[1]
    ruta_extraccion = os.path.join(BASE, "extraccion", f"{codigo}.json")
    if not os.path.exists(ruta_extraccion):
        print(f"No existe {ruta_extraccion}", file=sys.stderr)
        sys.exit(2)

    with open(ruta_extraccion, encoding="utf-8") as f:
        data = json.load(f)

    duracion_s = data["duracion_s"]
    segs = cargar_transcripcion(data["transcripcion"])
    corpus, offsets = construir_corpus(segs)

    menciones = data["menciones"]
    ids_vistos = Counter(m["id"] for m in menciones)
    ids_existentes = set(ids_vistos)

    errores = []

    for m in menciones:
        mid = m.get("id", "???")

        # 6. ids no repetidos
        if ids_vistos[mid] > 1:
            errores.append(f"[{mid}] id duplicado")

        # 5. obligatorios
        for campo in OBLIGATORIOS:
            if not m.get(campo):
                errores.append(f"[{mid}] falta campo obligatorio '{campo}'")

        es_descripcion = m.get("fuente") == "descripción"
        if not es_descripcion:
            if not m.get("cita"):
                errores.append(f"[{mid}] falta 'cita' (fuente != descripción)")
            if m.get("inicio_s") is None:
                errores.append(f"[{mid}] falta 'inicio_s' (fuente != descripción)")

        # 4. vocabularios cerrados
        def check_vocab(campo, valores):
            v = m.get(campo)
            if v and v not in valores:
                errores.append(f"[{mid}] valor no admitido en '{campo}': {v!r}")

        check_vocab("tipo", TIPOS)
        check_vocab("funcion", FUNCIONES)
        check_vocab("alcance", ALCANCES)
        check_vocab("soporte", SOPORTES)
        check_vocab("tono", TONOS)
        check_vocab("grado", GRADOS)
        check_vocab("fuente", FUENTES)
        check_vocab("confianza", CONFIANZAS)

        # 6. via apunta a un id existente
        via = m.get("via")
        if via and via not in ids_existentes:
            errores.append(f"[{mid}] 'via' apunta a un id inexistente: {via!r}")
        if via and m.get("grado") != "dentro de otra fuente":
            errores.append(f"[{mid}] tiene 'via' pero grado no es 'dentro de otra fuente'")

        # 7. rango
        inicio_s = m.get("inicio_s")
        if inicio_s is not None:
            if not (0 <= inicio_s <= duracion_s):
                errores.append(f"[{mid}] inicio_s {inicio_s} fuera de rango [0, {duracion_s}]")

        if es_descripcion or not m.get("cita"):
            continue

        cita_norm = normalizar(m["cita"])

        # 1. cita literal (comprobacion global, la importante)
        posiciones = [mm.start() for mm in re.finditer(re.escape(cita_norm), corpus)]
        if not posiciones:
            errores.append(f"[{mid}] CITA NO LITERAL, no aparece en la transcripcion: {m['cita']!r}")
            continue

        # 2. coherencia temporal: alguna aparicion debe caer en la ventana
        ventana_ok = False
        idx_en_ventana = None
        for pos in posiciones:
            idx = segmento_en_offset(offsets, pos)
            t = segs[idx]["inicio"]
            if inicio_s - WINDOW_BEFORE <= t <= inicio_s + WINDOW_AFTER:
                ventana_ok = True
                idx_en_ventana = idx
                break
        if not ventana_ok:
            errores.append(
                f"[{mid}] incoherencia temporal: la cita no aparece en la ventana "
                f"[{inicio_s - WINDOW_BEFORE}, {inicio_s + WINDOW_AFTER}]s"
            )
            idx_en_ventana = segmento_en_offset(offsets, posiciones[0])

        # 3. hablante: el hablante declarado coincide con el del segmento de inicio_s
        hablante_declarado = m.get("hablante")
        if idx_en_ventana is not None:
            hablante_real = segs[idx_en_ventana]["hablante"]
            if hablante_declarado != hablante_real:
                errores.append(
                    f"[{mid}] hablante no coincide: declarado {hablante_declarado!r}, "
                    f"segmento real {hablante_real!r} (idx {idx_en_ventana})"
                )

    print(f"Episodio {codigo}: {len(menciones)} menciones")
    print(f"Reparto por fuente: {dict(Counter(m['fuente'] for m in menciones))}")
    print(f"Reparto por tipo: {dict(Counter(m['tipo'] for m in menciones))}")
    print(f"Reparto por funcion: {dict(Counter(m['funcion'] for m in menciones))}")
    no_alta = [m["id"] for m in menciones if m.get("confianza") != "alta"]
    print(f"Confianza distinta de alta: {len(no_alta)} -> {no_alta}")
    print()

    if errores:
        print(f"FALLA: {len(errores)} error(es)")
        for e in errores:
            print(" -", e)
        sys.exit(1)

    print("OK: validacion limpia")
    sys.exit(0)


if __name__ == "__main__":
    main()

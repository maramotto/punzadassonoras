#!/usr/bin/env python3
"""Control de calidad del archivo completo de extraccion/*.json.

Recorre TODAS las extracciones (118 episodios) y genera un informe en Markdown con:
1. Titulos de obra que normalizados coinciden pero se escriben distinto.
2. Obras atribuidas a mas de una autoria (posibles atribuciones cruzadas).
3. Menciones con autor "sin determinar", agrupadas por obra.
4. Menciones con confianza "baja", con su cita y su episodio.
5. Nombres de autoria muy parecidos entre si (probable misma persona transcrita de
   dos formas), agrupados por letra inicial para que la comparacion sea manejable.

Solo genera el informe. No corrige nada automaticamente: las decisiones (que variante
de titulo se queda, que atribucion es un error, que mencion "sin determinar" se puede
completar) las toma Mara a mano sobre este documento.

Uso: python3 15_qa_archivo.py
Escribe podcast-data/INFORME_qa_archivo.md
"""
import glob
import json
import os
import re
import unicodedata
from collections import defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXTRACCION = os.path.join(BASE, "extraccion")
SALIDA = os.path.join(BASE, "INFORME_qa_archivo.md")

# Decision 2026-08-19: "desconocido", "sin determinar" y "Autor sin determinar" son
# el mismo hueco de dato y se unificaron a "sin determinar". "anonimo"/"Anonimo"/
# "Anonimo hipocratico" NO entran aqui: son autoria real de obras genuinamente
# anonimas (mitos, textos antiguos), no un hueco de la extraccion.
AUTOR_NO_DETERMINADO = "sin determinar"


def normalizar(texto):
    texto = texto.lower().strip()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"[^a-z0-9]+", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


def levenshtein(a, b):
    if a == b:
        return 0
    if len(a) < len(b):
        a, b = b, a
    fila = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        nueva = [i] + [0] * len(b)
        for j, cb in enumerate(b, 1):
            costo = 0 if ca == cb else 1
            nueva[j] = min(fila[j] + 1, nueva[j - 1] + 1, fila[j - 1] + costo)
        fila = nueva
    return fila[-1]


def cargar_menciones():
    """Devuelve una lista de (mencion, episodio_id, episodio_codigo, episodio_titulo)."""
    filas = []
    for path in sorted(glob.glob(os.path.join(EXTRACCION, "*.json"))):
        d = json.load(open(path, encoding="utf-8"))
        eid = d.get("id") or os.path.basename(path)[:-5]
        for m in d.get("menciones", []):
            filas.append((m, eid, d.get("codigo", ""), d.get("titulo", "")))
    return filas


def seccion_titulos_duplicados(filas):
    por_norm = defaultdict(lambda: defaultdict(int))
    for m, eid, codigo, etitulo in filas:
        obra = (m.get("obra") or "").strip()
        if not obra:
            continue
        por_norm[normalizar(obra)][obra] += 1

    lineas = [
        "## 1. Titulos de obra que normalizados coinciden pero se escriben distinto\n",
        "Mismo titulo (sin mayusculas/tildes/puntuacion) escrito de mas de una forma. "
        "Decide cual variante se queda; el resto hay que fundirlas.\n",
    ]
    grupos = [(norm, variantes) for norm, variantes in por_norm.items() if len(variantes) > 1]
    grupos.sort(key=lambda x: -sum(x[1].values()))
    if not grupos:
        lineas.append("\nNinguno encontrado.\n")
    for norm, variantes in grupos:
        lineas.append(f"\n**{norm}**\n")
        for variante, n in sorted(variantes.items(), key=lambda x: -x[1]):
            lineas.append(f"- {n} mencion(es) — {variante!r}\n")
    lineas.append(f"\nTotal de grupos con variantes: {len(grupos)}\n")
    return "".join(lineas)


def seccion_atribuciones_cruzadas(filas):
    por_obra = defaultdict(lambda: defaultdict(int))
    for m, eid, codigo, etitulo in filas:
        obra = (m.get("obra") or "").strip()
        autor = (m.get("autor") or "").strip()
        if not obra or not autor or autor.lower() == AUTOR_NO_DETERMINADO:
            continue
        por_obra[normalizar(obra)][autor] += 1

    lineas = [
        "\n## 2. Obras atribuidas a mas de una autoria\n",
        "Mismo titulo normalizado con mas de un autor distinto. Puede ser una "
        "atribucion cruzada real (error) o dos obras homonimas de autoras distintas: "
        "hay que mirar caso a caso. Ordenado por numero total de menciones.\n",
    ]
    grupos = [(norm, autores) for norm, autores in por_obra.items() if len(autores) > 1]
    grupos.sort(key=lambda x: -sum(x[1].values()))
    if not grupos:
        lineas.append("\nNinguna encontrada.\n")
    for norm, autores in grupos:
        total = sum(autores.values())
        lineas.append(f"\n**{norm}** ({total} menciones)\n")
        for autor, n in sorted(autores.items(), key=lambda x: -x[1]):
            lineas.append(f"- {n} mencion(es) — {autor}\n")
    lineas.append(f"\nTotal de obras con autoria en conflicto: {len(grupos)}\n")
    return "".join(lineas)


def seccion_desconocidos(filas):
    por_obra = defaultdict(list)
    total = 0
    for m, eid, codigo, etitulo in filas:
        if (m.get("autor") or "").strip().lower() != AUTOR_NO_DETERMINADO:
            continue
        total += 1
        obra = (m.get("obra") or "").strip() or "(sin obra)"
        por_obra[obra].append((eid, codigo, m.get("cita") or ""))

    lineas = [
        "\n## 3. Menciones con autor \"sin determinar\"\n",
        f"Total: {total}. Agrupadas por obra para ver cuales se pueden completar a mano "
        "y cuales quedan fuera de rankings de autoria.\n",
    ]
    grupos = sorted(por_obra.items(), key=lambda x: -len(x[1]))
    for obra, apariciones in grupos:
        lineas.append(f"\n**{obra}** ({len(apariciones)})\n")
        for eid, codigo, cita in apariciones:
            ref = codigo or eid
            cita_corta = (cita[:120] + "…") if len(cita) > 120 else cita
            lineas.append(f"- {ref}: {cita_corta!r}\n")
    return "".join(lineas)


def minuto(segundos):
    if segundos is None:
        return "?"
    m, s = divmod(int(segundos), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def seccion_confianza_baja(filas):
    bajas = [(m, eid, codigo) for m, eid, codigo, etitulo in filas if m.get("confianza") == "baja"]
    lineas = [
        "\n## 4. Menciones con confianza \"baja\"\n",
        f"Total: {len(bajas)}.\n",
    ]
    bajas.sort(key=lambda x: (x[2] or x[1]))
    for m, eid, codigo in bajas:
        ref = codigo or eid
        t = minuto(m.get("inicio_s"))
        autor = m.get("autor") or "(sin autor)"
        obra = m.get("obra") or "(sin obra)"
        cita = m.get("cita") or ""
        lineas.append(f"- **{ref}** [{t}] {autor} — *{obra}* — {cita!r}\n")
    return "".join(lineas)


def seccion_nombres_parecidos(filas):
    autores = set()
    for m, eid, codigo, etitulo in filas:
        a = (m.get("autor") or "").strip()
        if a and a.lower() != AUTOR_NO_DETERMINADO:
            autores.add(a)

    por_inicial = defaultdict(list)
    for a in autores:
        norm = normalizar(a)
        if norm:
            por_inicial[norm[0]].append(a)

    parejas = []
    for inicial, nombres in por_inicial.items():
        nombres = sorted(set(nombres))
        for i in range(len(nombres)):
            for j in range(i + 1, len(nombres)):
                a, b = nombres[i], nombres[j]
                na, nb = normalizar(a), normalizar(b)
                if na == nb:
                    continue
                dist = levenshtein(na, nb)
                largo = max(len(na), len(nb))
                if largo and dist <= max(2, largo // 8) and dist > 0:
                    parejas.append((dist, a, b))

    parejas = sorted(set(parejas), key=lambda x: x[0])
    lineas = [
        "\n## 5. Nombres de autoria muy parecidos entre si\n",
        "Comparados solo dentro del mismo grupo de letra inicial (normalizada), asi que "
        "no detecta deformaciones que cambien la primera letra. Distancia de edicion "
        "pequena entre nombres normalizados; suele ser la misma persona transcrita de "
        "dos formas.\n",
    ]
    if not parejas:
        lineas.append("\nNinguna encontrada.\n")
    for dist, a, b in parejas:
        lineas.append(f"- (distancia {dist}) {a!r} / {b!r}\n")
    lineas.append(f"\nTotal de parejas sospechosas: {len(parejas)}\n")
    return "".join(lineas)


def main():
    filas = cargar_menciones()
    n_episodios = len(glob.glob(os.path.join(EXTRACCION, "*.json")))
    n_menciones = len(filas)

    partes = [
        "# Informe de QA del archivo\n\n",
        f"Generado por `15_qa_archivo.py` sobre {n_episodios} episodios y {n_menciones} "
        "menciones. Solo diagnostico: no se ha corregido nada automaticamente.\n",
        seccion_titulos_duplicados(filas),
        seccion_atribuciones_cruzadas(filas),
        seccion_desconocidos(filas),
        seccion_confianza_baja(filas),
        seccion_nombres_parecidos(filas),
    ]

    with open(SALIDA, "w", encoding="utf-8") as f:
        f.write("".join(partes))

    print(f"Informe escrito en {SALIDA}")
    print(f"Episodios: {n_episodios}, menciones: {n_menciones}")


if __name__ == "__main__":
    main()

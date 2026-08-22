#!/usr/bin/env python3
"""Aplica las correcciones decididas tras el informe de QA (INFORME_qa_archivo.md).

Bloque A: 15 menciones concretas con autor mal atribuido, verificadas una a una
contra su "cita" y "contexto" reales (no solo por el nombre de la obra) antes de
decidir la correccion. Dos de ellas ademas pasan a "grado: dentro de otra fuente"
con su "via" correspondiente, porque en realidad citan una idea/frase ajena dentro
de otra fuente ya catalogada, y no una obra propia de esa persona.

Bloque B: fusiones de nombre de autoria y de titulo de obra que son la misma
persona/obra escrita de mas de una forma (typos, acentos, mayusculas, un espacio
de diferencia). Se aplican por sustitucion exacta del valor del campo en TODO el
archivo, nunca tocando "cita" (que es intocable) ni "contexto".

Vocabulario de autoria no determinada: unifica "desconocido", "sin determinar" y
"Autor sin determinar" en "sin determinar" (autor Manuel del podcast: aviso, decision
explicita de Mara 2026-08-19). Deja "anonimo" / "Anonimo" / "Anonimo hipocratico"
SIN TOCAR: comprobado contra sus obras (Enuma Elish, Genesis, Orfeo y Euridice,
Glosas Emilianenses, Sobre la naturaleza del hombre...) que no es un hueco de dato,
es autoria real de obras genuinamente anonimas. Convertirlas tambien habria borrado
informacion correcta.

Edita por reemplazo de texto anclado al campo exacto, nunca reserializando el JSON
entero (evita reformatear listas compactas y ensuciar el diff). Guarda un .bak por
fichero tocado. Reejecuta el validador sobre cada fichero de Bloque A al terminar.

Uso: python3 16_aplicar_correcciones_qa.py [--dry-run]
Idempotente: una segunda pasada no encuentra ya los valores viejos y no cambia nada.
"""
import glob
import json
import os
import re
import shutil
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXTRACCION = os.path.join(BASE, "extraccion")

# --- Bloque A: correcciones puntuales por id de mencion ------------------------
# (fichero, id_mencion, {campo: valor_nuevo})
BLOQUE_A = [
    ("2x10.json", "2x10-022", {"autor": "Pierre Bourdieu"}),
    ("1x10.json", "1x10-023", {"autor": "Sara Mesa"}),
    ("3x06.json", "3x06-039", {"autor": "Sara Mesa"}),
    ("3x08.json", "3x08-042", {"autor": "Isabel Coixet"}),
    ("2x05.json", "2x05-042", {"autor": "Vladimir Nabokov"}),
    ("1x06.json", "1x06-030", {
        "autor": "Joan Didion", "grado": "dentro de otra fuente", "via": "1x06-029",
    }),
    ("4x08.json", "4x08-029", {
        "autor": "Pau Luque", "grado": "dentro de otra fuente", "via": "4x08-030",
    }),
    ("4x13.json", "4x13-092", {"autor": "C. J. Hauser"}),
    ("4x21.json", "4x21-025", {"autor": "Eudald Espluga"}),
    ("4x01.json", "4x01-027", {"autor": "Peter Morgan"}),
    ("5x20.json", "5x20-033", {"autor": "Gillian Flynn"}),
    ("5x04.json", "5x04-036", {"autor": "Blanca Lacasa"}),
    ("5x04.json", "5x04-037", {"autor": "Blanca Lacasa"}),
    (
        "2026-02-19_las-glosas-el-cuento-de-una-noche-de-verano-de-maria-herrera.json",
        "glosas1x05-013", {"autor": "Elena Martín Gimeno"},
    ),
    ("5x15.json", "5x15-014", {"autor": "Noemí Sabugal"}),
]

# --- Bloque B: fusiones globales de "autor" -------------------------------------
FUSIONES_AUTOR = [
    ("CJ Hauser", "C. J. Hauser"),
    ("James Miley", "Jane Smiley"),
    ("Estela Sánchez", "Estela Sanchis"),
    ("Viviana Collado", "Bibiana Collado"),
    ("Goudal", "Eudald Espluga"),
    ("Lola López Mondéjar", "Lola López-Mondéjar"),
    ("Jorge Diony López", "Jorge Dioni López"),
    ("Lain Vilar Madruga", "Elaine Vilar Madruga"),
    ("León Siminiani", "Elías León Siminiani"),
    ("Rachel Kask", "Rachel Cusk"),
    ("Tenconi", "Mariano Tenconi"),
    ("Leo Tolstoy", "León Tolstói"),
    ("Liev Tolstói", "León Tolstói"),
    ("Sigrid Núñez", "Sigrid Nunez"),
    ("Paul Lucke", "Pau Luque"),
]

# --- Bloque B: fusiones globales de "obra" (mismo titulo, distinta grafia) -----
FUSIONES_OBRA = [
    ("Contra el Patrimonio", "Contra el patrimonio"),
    ("Ojos y Capital", "Ojos y capital"),
    ("Personajes Desesperados", "Personajes desesperados"),
    ("Call Me By Your Name", "Call Me by Your Name"),
    ("Los Herederos", "Los herederos"),
    ("Tecnologías de representación de las ruralidades queer en el cine: un conflicto hermenéutico",
     "Tecnologías de representación de las ruralidades queer en el cine. Un conflicto hermenéutico"),
    ("La caída de la Casa Usher", "La caída de la casa Usher"),
    ("Arquitectura Emocional 1959", "Arquitectura emocional 1959"),
    ("Laberinto Mar", "Laberinto mar"),
    ("Hipocondría Moral", "Hipocondría moral"),
    ("Los Juegos del Hambre", "Los juegos del hambre"),
    ("La Isla de las Tentaciones", "La isla de las tentaciones"),
    ("Primero Sueño", "Primero sueño"),
    ("Historia Natural", "Historia natural"),
    ("La Casa del Dragón", "La casa del dragón"),
    ("La Virgen de Agosto", "La virgen de agosto"),
    ("Anna Karénina", "Anna Karenina"),
    ("Amiga date cuenta", "Amiga, date cuenta"),
    ("Maternidad y Creación", "Maternidad y creación"),
    ("Divina comedia", "Divina Comedia"),
    ("Los rescoldos de la Culebra", "Los rescoldos de la culebra"),
    ("Demasiadas Mujeres", "Demasiadas mujeres"),
    ("Homo Sovieticus", "Homo sovieticus"),
    ("La Quimera", "La quimera"),
    ("4′33′′", "4'33\""),
    ("4\\'33\"", "4'33\""),
    ("Sino el invierno", "Si no, el invierno"),
]

# --- Vocabulario de autoria no determinada --------------------------------------
FUSIONES_DESCONOCIDO = [
    ("desconocido", "sin determinar"),
    ("Autor sin determinar", "sin determinar"),
]
# Deliberadamente NO se incluyen aqui: "anónimo", "Anónimo", "Anónimo hipocrático".
# Verificado contra sus obras (mitos, textos antiguos, autoria real desconocida por
# la historia, no por la extraccion): son informacion correcta, no un hueco de dato.


def cargar_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def escribir(path, texto, dry_run):
    if dry_run:
        return
    shutil.copy2(path, path + ".bak")
    with open(path, "w", encoding="utf-8") as f:
        f.write(texto)


PATRON_INICIO_MENCION = re.compile(r"^    \{$", re.MULTILINE)
PATRON_FIN_MENCION = re.compile(r"^    \}", re.MULTILINE)


def localizar_bloque_mencion(texto, mencion_id):
    """Encuentra los limites [inicio, fin) del objeto de una mencion, buscando el
    "id" en cualquier posicion del objeto (el orden de campos no es el mismo en
    todos los ficheros: en las extracciones mas antiguas "id" va al final, no al
    principio). Los limites del objeto son las lineas "    {" / "    }" propias de
    cada mencion (con 4 espacios exactos); los sub-objetos de "datos_nuevos" van
    mas indentados, asi que no se confunden con estos limites."""
    anchor_pos = texto.find(f'"id": "{mencion_id}"')
    if anchor_pos == -1:
        return None
    inicios = [m.start() for m in PATRON_INICIO_MENCION.finditer(texto) if m.start() <= anchor_pos]
    if not inicios:
        return None
    pos_ini = inicios[-1]
    m_fin = PATRON_FIN_MENCION.search(texto, anchor_pos)
    if not m_fin:
        return None
    pos_fin = m_fin.end()
    return pos_ini, pos_fin


def aplicar_bloque_a(dry_run):
    print("=== Bloque A: correcciones puntuales ===")
    ficheros_tocados = set()
    for nombre_fichero, mencion_id, cambios in BLOQUE_A:
        path = os.path.join(EXTRACCION, nombre_fichero)
        with open(path, encoding="utf-8") as f:
            texto = f.read()

        limites = localizar_bloque_mencion(texto, mencion_id)
        if limites is None:
            print(f"  AVISO: no se encontro {mencion_id} en {nombre_fichero}")
            continue
        pos_ini, pos_fin = limites
        bloque = texto[pos_ini:pos_fin]
        bloque_original = bloque

        for campo, valor_nuevo in cambios.items():
            if campo == "via":
                patron = re.compile(r'("via":\s*)(null|"[^"]*")')
                valor_json = json.dumps(valor_nuevo, ensure_ascii=False)
                bloque, n = patron.subn(rf'\g<1>{valor_json}', bloque, count=1)
            else:
                patron = re.compile(rf'("{campo}":\s*)"[^"]*"')
                valor_json = json.dumps(valor_nuevo, ensure_ascii=False)
                bloque, n = patron.subn(rf'\g<1>{valor_json}', bloque, count=1)
            if n != 1:
                print(f"  AVISO: campo '{campo}' no sustituido de forma unica en {mencion_id} ({nombre_fichero})")

        if bloque != bloque_original:
            texto = texto[:pos_ini] + bloque + texto[pos_fin:]
            print(f"  {nombre_fichero} / {mencion_id}: {cambios}")
            escribir(path, texto, dry_run)
            ficheros_tocados.add(nombre_fichero)
    return ficheros_tocados


def aplicar_fusiones_globales(campo, fusiones, dry_run):
    total = 0
    for path in sorted(glob.glob(os.path.join(EXTRACCION, "*.json"))):
        with open(path, encoding="utf-8") as f:
            texto = f.read()
        original = texto
        for viejo, nuevo in fusiones:
            patron_str = rf'"{campo}":\s*"{re.escape(viejo)}"'
            nuevo_str = f'"{campo}": {json.dumps(nuevo, ensure_ascii=False)}'
            texto, n = re.subn(patron_str, nuevo_str, texto)
            if n:
                total += n
        if texto != original:
            nombre = os.path.basename(path)
            print(f"  {nombre}: fusiones aplicadas en '{campo}'")
            escribir(path, texto, dry_run)
    return total


def main():
    dry_run = "--dry-run" in sys.argv
    if dry_run:
        print("[DRY-RUN] no se escribira nada\n")

    ficheros_a = aplicar_bloque_a(dry_run)

    print("\n=== Bloque B: fusiones de autor ===")
    n_autor = aplicar_fusiones_globales("autor", FUSIONES_AUTOR, dry_run)
    print(f"Total sustituciones de autor: {n_autor}")

    print("\n=== Bloque B: fusiones de obra ===")
    n_obra = aplicar_fusiones_globales("obra", FUSIONES_OBRA, dry_run)
    print(f"Total sustituciones de obra: {n_obra}")

    print("\n=== Vocabulario de autoria no determinada ===")
    n_desc = aplicar_fusiones_globales("autor", FUSIONES_DESCONOCIDO, dry_run)
    print(f"Total sustituciones: {n_desc}")
    print("(\"anónimo\"/\"Anónimo\"/\"Anónimo hipocrático\" NO se tocan: son autoria real, no un hueco.)")

    if not dry_run and ficheros_a:
        print("\n=== Revalidando ficheros del Bloque A ===")
        for nombre in sorted(ficheros_a):
            codigo = nombre[:-5]
            r = subprocess.run(
                [sys.executable, os.path.join(BASE, "scripts", "11_validar_extraccion.py"), codigo],
                capture_output=True, text=True,
            )
            estado = "OK" if r.returncode == 0 else "FALLA"
            print(f"  {codigo}: {estado}")
            if r.returncode != 0:
                print(r.stdout)
                print(r.stderr)


if __name__ == "__main__":
    main()

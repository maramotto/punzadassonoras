#!/usr/bin/env python3
"""Rutina para incorporar episodios nuevos según van saliendo (ritmo previsto:
un par al mes desde septiembre). Cubre lo mecánico; la transcripción (Mac de
Mara, mlx-whisper) y la extracción (lectura de la transcripción entera con el
criterio de podcast-data/CRITERIO_extraccion.md, hoy hecha vía Claude Code)
siguen siendo pasos aparte, a propósito: no son automatizables sin perder
calidad, esta sesión lo ha demostrado varias veces.

Tres subcomandos, en el orden en que se usan:

  comprobar   Descarga el feed RSS y compara con el manifiesto. No toca nada,
              solo dice qué episodios son nuevos.

  alta CODIGO --fecha ... --titulo ...
              Da de alta UN episodio nuevo en el manifiesto (equivale al
              bloque A0 de PROMPTS_claude_code.md). No transcribe ni extrae.
              --codigo es opcional a propósito: si el número de temporada es
              ambiguo, el bloque A0 manda preguntar antes de decidirlo, así
              que aquí se deja vacío en vez de adivinarlo.

  regenerar   Una vez transcrito y EXTRAÍDO el episodio (por separado), corre
              la cadena mecánica completa: reconciliar ids, validar la
              extracción nueva, regenerar el informe de QA, reconstruir los
              datos de la web y compilar Astro. No despliega: el Paso 7
              (publicación) todavía no está decidido.

Uso:
  python3 17_nuevo_episodio.py comprobar
  python3 17_nuevo_episodio.py alta --fecha 2026-09-10 --titulo "..." [--codigo 6x01]
  python3 17_nuevo_episodio.py regenerar [--codigo-nuevo 6x01 ...]
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
SCRIPTS = os.path.join(BASE, "scripts")
WEB = os.path.join(os.path.dirname(BASE), "web")

FEED_URL = "https://feeds.megaphone.fm/PMSL3601016455"
NS_ITUNES = {"itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd"}
RUTA_MANIFIESTO = os.path.join(DATA, "manifiesto_audio.json")


def slugify(texto):
    texto = texto.lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"[^a-z0-9]+", "-", texto)
    return texto.strip("-")


def cargar_manifiesto():
    with open(RUTA_MANIFIESTO, encoding="utf-8") as f:
        return json.load(f)


def guardar_manifiesto(manifiesto):
    shutil.copy2(RUTA_MANIFIESTO, RUTA_MANIFIESTO + ".bak")
    with open(RUTA_MANIFIESTO, "w", encoding="utf-8") as f:
        json.dump(manifiesto, f, ensure_ascii=False, indent=1)
        f.write("\n")


def descargar_feed():
    ruta_feed = os.path.join(DATA, "feed.xml")
    ruta_anterior = os.path.join(DATA, "feed_anterior.xml")
    if os.path.exists(ruta_feed):
        shutil.copy2(ruta_feed, ruta_anterior)
    with urllib.request.urlopen(FEED_URL, timeout=30) as r:
        contenido = r.read()
    with open(ruta_feed, "wb") as f:
        f.write(contenido)
    return contenido


def parsear_items(contenido_xml):
    root = ET.fromstring(contenido_xml)
    items = []
    for item in root.findall(".//item"):
        pub = item.findtext("pubDate")
        fecha = parsedate_to_datetime(pub).date().isoformat() if pub else None
        duracion = item.findtext("itunes:duration", namespaces=NS_ITUNES)
        enclosure = item.find("enclosure")
        items.append({
            "titulo": (item.findtext("title") or "").strip(),
            "fecha": fecha,
            "duracion_s": int(duracion) if duracion and duracion.isdigit() else None,
            "url_audio": enclosure.get("url") if enclosure is not None else "",
        })
    return items


def comando_comprobar(args):
    print(f"Descargando {FEED_URL} …")
    contenido = descargar_feed()
    items = parsear_items(contenido)
    manifiesto = cargar_manifiesto()
    fechas_conocidas = {e["fecha"] for e in manifiesto}

    nuevos = [it for it in items if it["fecha"] not in fechas_conocidas]

    print(f"\nFeed: {len(items)} episodios. Manifiesto: {len(manifiesto)} episodios.")
    if not nuevos:
        print("Nada nuevo que dar de alta.")
        return

    print(f"\n{len(nuevos)} episodio(s) en el feed sin entrada en el manifiesto:\n")
    for it in nuevos:
        print(f"  {it['fecha']}  {it['titulo']!r}  ({it['duracion_s']}s)")
    print(
        "\nPara cada uno, decide el 'codigo' (número de temporada) y da de alta con:\n"
        "  python3 17_nuevo_episodio.py alta --fecha AAAA-MM-DD --titulo \"...\" [--codigo 6x01]\n"
        "El 'codigo' es opcional: si dudas del número de temporada, no lo pongas y decídelo\n"
        "a mano en el manifiesto, tal como manda el bloque A0."
    )


def comando_alta(args):
    contenido = None
    ruta_feed = os.path.join(DATA, "feed.xml")
    if os.path.exists(ruta_feed) and not args.forzar_descarga:
        with open(ruta_feed, "rb") as f:
            contenido = f.read()
    else:
        contenido = descargar_feed()

    items = {it["fecha"]: it for it in parsear_items(contenido)}
    item = items.get(args.fecha)
    if item is None:
        print(f"AVISO: no encuentro un episodio con fecha {args.fecha} en el feed guardado.")
        print("Vuelve a correr con --forzar-descarga o revisa la fecha.")
        sys.exit(1)

    titulo = args.titulo or item["titulo"]
    if not titulo:
        print("ERROR: falta --titulo (el feed no trae uno utilizable).")
        sys.exit(1)

    manifiesto = cargar_manifiesto()
    if any(e["fecha"] == args.fecha for e in manifiesto):
        print(f"ERROR: ya hay una entrada del manifiesto con fecha {args.fecha}. No hago nada.")
        sys.exit(1)

    slug = f"{args.fecha}_{args.codigo}" if args.codigo else f"{args.fecha}_sincodigo"
    entrada = {
        "codigo": args.codigo or "",
        "titulo": titulo,
        "fecha": args.fecha,
        "video_id": args.video_id or "",
        "url_audio": item["url_audio"],
        "duracion_s": item["duracion_s"],
        "slug": slug,
        "id": f"{args.fecha}_{slugify(titulo)}",
    }

    manifiesto.append(entrada)
    manifiesto.sort(key=lambda e: e["fecha"])
    guardar_manifiesto(manifiesto)

    print("Dado de alta en el manifiesto:")
    print(json.dumps(entrada, ensure_ascii=False, indent=2))
    print(
        "\nSiguientes pasos, en orden (no los hace este script):\n"
        "  1. Transcribir en el Mac (bloque A1 de PROMPTS_claude_code.md).\n"
        "  2. Extraer las referencias leyendo la transcripción entera (bloque B1),\n"
        "     validar con 11_validar_extraccion.py.\n"
        "  3. Añadir su fila a data/refs_all.json (tema, descripción) si procede.\n"
        "  4. Cuando todo eso esté hecho: python3 17_nuevo_episodio.py regenerar"
    )


def correr(cmd, cwd=None):
    print(f"\n$ {' '.join(cmd)}")
    r = subprocess.run(cmd, cwd=cwd)
    if r.returncode != 0:
        print(f"FALLA: {' '.join(cmd)} (código {r.returncode})")
        sys.exit(r.returncode)


def comando_regenerar(args):
    correr([sys.executable, os.path.join(SCRIPTS, "13_reconciliar_ids.py")])

    for codigo in args.codigo_nuevo or []:
        correr([sys.executable, os.path.join(SCRIPTS, "11_validar_extraccion.py"), codigo])

    correr([sys.executable, os.path.join(SCRIPTS, "15_qa_archivo.py")])
    correr([sys.executable, os.path.join(SCRIPTS, "14_build_web_data.py")])

    if os.path.exists(os.path.join(WEB, "package.json")):
        correr(["npm", "run", "build"], cwd=WEB)
    else:
        print("\nAVISO: web/package.json no existe todavía, salto 'npm run build'.")

    print(
        "\nRegenerado. Revisa podcast-data/INFORME_qa_archivo.md por si el episodio nuevo\n"
        "trae algún duplicado o atribución dudosa antes de publicar.\n"
        "El despliegue (Paso 7) sigue siendo manual: no está decidido todavía."
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="comando", required=True)

    p_comprobar = sub.add_parser("comprobar", help="descarga el feed y lista episodios nuevos")
    p_comprobar.set_defaults(func=comando_comprobar)

    p_alta = sub.add_parser("alta", help="da de alta un episodio nuevo en el manifiesto")
    p_alta.add_argument("--fecha", required=True, help="AAAA-MM-DD, tal como sale en el feed")
    p_alta.add_argument("--titulo", help="si se omite, se usa el título del feed")
    p_alta.add_argument("--codigo", help="p. ej. 6x01; se deja vacío si dudas del número de temporada")
    p_alta.add_argument("--video-id", help="id de YouTube si ya se sabe; si no, se enlaza solo más tarde")
    p_alta.add_argument("--forzar-descarga", action="store_true", help="descarga el feed de nuevo en vez de reusar data/feed.xml")
    p_alta.set_defaults(func=comando_alta)

    p_regenerar = sub.add_parser("regenerar", help="reconcilia, valida, reconstruye datos y compila la web")
    p_regenerar.add_argument("--codigo-nuevo", nargs="*", help="codigo(s) de episodio a validar explícitamente, p. ej. 6x01")
    p_regenerar.set_defaults(func=comando_regenerar)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

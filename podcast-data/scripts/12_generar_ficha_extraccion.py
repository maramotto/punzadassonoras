#!/usr/bin/env python3
"""Genera la ficha legible extraccion/<codigo>.md a partir de extraccion/<codigo>.json.

Uso: python3 12_generar_ficha_extraccion.py 5x21

No se edita el .md a mano: se regenera siempre desde el JSON.
"""
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def minuto(segundos):
    m, s = divmod(int(segundos), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def fila(campo, valor):
    if valor in (None, "", [], {}):
        return ""
    return f"| **{campo}** | {valor} |\n"


def render_mencion(m, video_id):
    titulo = m["obra"] if m["obra"] else f"({m['autor']}, sin obra concreta)"
    lineas = [f"### {m['id']} — {m['autor']} — *{titulo}*\n"]
    if m.get("subtipo"):
        lineas.append(f"*{m['subtipo']}*\n")
    lineas.append("| campo | valor |\n|---|---|\n")
    lineas.append(fila("tipo", m["tipo"]))
    lineas.append(fila("función", m["funcion"]))
    lineas.append(fila("alcance", m["alcance"]))
    lineas.append(fila("soporte", m["soporte"]))
    lineas.append(fila("tono", m["tono"]))
    lineas.append(fila("grado", m["grado"] + (f" (via {m['via']})" if m.get("via") else "")))
    lineas.append(fila("fuente", m["fuente"]))
    lineas.append(fila("confianza", m["confianza"]))
    if m.get("hablante"):
        lineas.append(fila("hablante", m["hablante"]))
    if m.get("inicio_s") is not None:
        t = m["inicio_s"]
        enlace = f"[{minuto(t)}](https://www.youtube.com/watch?v={video_id}&t={t}s)"
        lineas.append(fila("minuto", enlace))
    if m.get("en_dialogo_con"):
        lineas.append(fila("en diálogo con", ", ".join(m["en_dialogo_con"])))
    if m.get("datos_nuevos"):
        dn = "; ".join(f"{k}: {v}" for k, v in m["datos_nuevos"].items())
        lineas.append(fila("datos nuevos", dn))
    lineas.append("\n")
    if m.get("contexto"):
        lineas.append(f"**Contexto:** {m['contexto']}\n\n")
    if m.get("cita"):
        lineas.append(f"> {m['cita']}\n\n")
    return "".join(lineas)


def main():
    if len(sys.argv) != 2:
        print("Uso: 12_generar_ficha_extraccion.py <codigo_episodio>", file=sys.stderr)
        sys.exit(2)

    codigo = sys.argv[1]
    ruta_json = os.path.join(BASE, "extraccion", f"{codigo}.json")
    with open(ruta_json, encoding="utf-8") as f:
        data = json.load(f)

    menciones = sorted(data["menciones"], key=lambda m: m.get("inicio_s") or 0)
    video_id = data["video_id"]

    out = [f"# {data['codigo']} — {data['titulo']}\n\n"]
    out.append(f"Fecha: {data['fecha']} · Duración: {data['duracion_s']}s · "
                f"[YouTube](https://www.youtube.com/watch?v={video_id}) · "
                f"Transcripción: `{data['transcripcion']}`\n\n")
    out.append(f"**{len(menciones)} menciones.** Generado automáticamente desde "
                f"`{codigo}.json` por `12_generar_ficha_extraccion.py`. No editar a mano.\n\n")
    out.append("---\n\n")

    for m in menciones:
        out.append(render_mencion(m, video_id))

    ruta_md = os.path.join(BASE, "extraccion", f"{codigo}.md")
    with open(ruta_md, "w", encoding="utf-8") as f:
        f.write("".join(out))
    print(f"Escrito {ruta_md} ({len(menciones)} menciones)")


if __name__ == "__main__":
    main()

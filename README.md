# UniversoPunzadas

**Proyecto aficionado (no oficial)**, creado por [maramotto](https://github.com/maramotto)
(Mara Crespo), para catalogar todas las obras, autoras y autores que se citan en
**Punzadas Sonoras**, el podcast de **Paula Ducay** e **Inés García** producido por
**Radio Primavera Sound**. El objetivo final es una web pública navegable por autor,
obra, tema y temporada — un mapa de todo lo que se ha citado, leído, visto y discutido a
lo largo del podcast.

> Este es un proyecto aficionado, sin relación oficial con Punzadas Sonoras, Paula Ducay,
> Inés García ni Radio Primavera Sound. Todo el contenido citado (títulos, citas,
> transcripciones) pertenece a sus autoras y autores originales; este repositorio solo
> cataloga referencias con fines de documentación y consulta.

---

## Estado actual

| | |
|---|---|
| Episodios en el catálogo | **118 de 118** — extracción completa |
| Transcripciones propias | **118 de 118**, con hablante identificado (mlx-whisper large-v3 + pyannote 3.1) |
| Menciones extraídas desde el audio | **5.874** |
| Autoras y autores distintos citados | **1.160** |
| Web pública | esqueleto en `web/` (Astro + React), en construcción |

El dato central del proyecto: las descripciones escritas de los episodios solo dan una
fracción de lo que realmente se cita. Comparando ambas fuentes, la transcripción aporta
en torno al **85-90% de las referencias** que no aparecen en ningún otro sitio — nombres
propios, ediciones, citas exactas y matices (leído/visto/escuchado, entusiasta/crítico,
qué figura concreta de un libro, con qué otra obra se pone en diálogo) que solo se oyen
en el propio episodio.

---

## De dónde salen los datos

- **Descripciones oficiales** de la playlist de YouTube y del feed RSS público del
  podcast, usadas para contrastar nombres y fechas — nunca para inventar contenido.
- **Transcripción propia** de los 118 episodios, hecha con `mlx-whisper` (modelo
  large-v3) y diarización con `pyannote` 3.1, corriendo en local.
- **Extracción de referencias** hecha leyendo la transcripción entera de cada episodio,
  con un criterio explícito y verificable: cada dato tiene que poder señalarse con una
  cita literal en el audio. Lo que no se dice, no entra — el enriquecimiento contra
  catálogos externos (editoriales, años, traductores) es una fase aparte, posterior.

El criterio completo de extracción, con ejemplos y su historial de versiones, está en
[`podcast-data/CRITERIO_extraccion.md`](podcast-data/CRITERIO_extraccion.md).

---

## Estructura del repositorio

```
punzadassonoras/
├── web/                      sitio Astro + React (esqueleto ya montado)
│   └── public/data/          JSON que consume el sitio, generados por 14_build_web_data.py
└── podcast-data/
    ├── data/                 índices, feeds y caches de enriquecimiento
    ├── extraccion/           una ficha .json + .md por episodio, con cada mención
    ├── transcribir/          transcripciones propias (una por episodio)
    ├── scripts/              extracción, validación, datos de la web y entregable
    └── Punzadas_Sonoras_referencias.xlsx   entregable .xlsx (autor, obra, tipo, tag...)
```

---

## Añadir un episodio nuevo

El podcast saca episodios nuevos a partir de septiembre a ritmo de un par al mes.
`podcast-data/scripts/17_nuevo_episodio.py` cubre la parte mecánica del proceso; la
transcripción y la extracción siguen siendo pasos aparte a propósito, porque no son
automatizables sin perder calidad — la extracción en concreto exige leer la transcripción
entera con el criterio de `podcast-data/CRITERIO_extraccion.md`, hoy vía Claude Code.

```bash
# 1. ¿Hay episodios nuevos en el feed que no estén en el manifiesto?
python3 podcast-data/scripts/17_nuevo_episodio.py comprobar

# 2. Dar de alta uno (equivale al bloque A0 de podcast-data/PROMPTS_claude_code.md)
python3 podcast-data/scripts/17_nuevo_episodio.py alta --fecha AAAA-MM-DD --titulo "..." [--codigo 6x01]

# 3. Aparte: transcribir (bloque A1) y extraer (bloque B1) el episodio dado de alta.

# 4. Cuando la extracción esté validada, reconstruir todo lo demás:
python3 podcast-data/scripts/17_nuevo_episodio.py regenerar --codigo-nuevo 6x01
```

El paso 4 encadena la reconciliación de identificadores, el informe de QA, la
regeneración de los datos de la web y `npm run build` en `web/`. No despliega: eso sigue
sin decidirse.

Los bloques de transcripción y extracción, con sus prompts exactos, están documentados
en detalle en [`podcast-data/PROMPTS_claude_code.md`](podcast-data/PROMPTS_claude_code.md);
no se duplican aquí para no desincronizarse.

---

## Próximos pasos

1. Buscador con Orama (tolerancia a erratas, cuatro pestañas: autoras, obras, menciones,
   episodios).
2. Los siete gráficos: matriz temas × episodios de portada, pulso fecha × minuto, grafo
   de obras en diálogo, matriz de autoría, área por tipo.
3. Publicación: dominio, cabeceras de caché, sitemap y comprobación de accesibilidad.

---

## Licencia y atribución

El código y los datos catalográficos de este repositorio están bajo licencia MIT (ver
[`LICENSE`](LICENSE)). Las transcripciones son un volcado automático del audio original
del podcast, con su propio aviso de atribución en
[`podcast-data/transcribir/README.md`](podcast-data/transcribir/README.md); son
automáticas y pueden contener errores. El contenido original —el podcast en sí— es
propiedad de sus autoras y de Radio Primavera Sound.

---

## Enlaces

- Punzadas Sonoras en Radio Primavera Sound: <https://www.primaverasound.com/es/radio/shows/punzadas-sonoras>
- Playlist de YouTube: <https://www.youtube.com/playlist?list=PLLbN7SMQhMVbsBcHlP9RnBXFjZyPgam6y>
- Spotify: <https://open.spotify.com/show/444xAKuV4A4WUlSXqyl51P>
- Web de las autoras: <https://punzadas.com/punzadas-sonoras/>
- Newsletter: <https://punzadas.substack.com>

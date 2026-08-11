# punzadassonoras

Proyecto de fans (no oficial) para catalogar todas las obras, autoras y autores que se
citan en **Punzadas Sonoras**, el podcast de **Paula Ducay** e **Inés García** producido
por **Radio Primavera Sound**. El objetivo final es una web pública navegable por autor,
obra, tema y temporada — un mapa de todo lo que se ha citado, leído, visto y discutido a
lo largo de la serie.

> Este es un proyecto de aficionadas, sin relación oficial con Punzadas Sonoras, Paula
> Ducay, Inés García ni Radio Primavera Sound. Todo el contenido citado (títulos, citas,
> transcripciones) pertenece a sus autoras y autores originales; este repositorio solo
> cataloga referencias con fines de documentación y consulta.

---

## Estado actual

| | |
|---|---|
| Episodios en el catálogo | **118** (117 originales + el cierre de temporada 5x22) |
| Transcripciones propias | **118 de 118**, con hablante identificado (mlx-whisper large-v3 + pyannote 3.1) |
| Episodios con extracción de referencias desde el audio | **103 de 118** (temporadas 1 a 5 completas; quedan Las Glosas, los especiales y el 5x22) |
| Menciones extraídas (solo temporadas 1-5, desde audio) | **5.524** |
| Autoras y autores distintos citados | **1.100** |

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
├── web/                      sitio estático público (pendiente)
└── podcast-data/
    ├── data/                 índices, feeds y caches de enriquecimiento
    ├── extraccion/           una ficha .json + .md por episodio, con cada mención
    ├── transcribir/          transcripciones propias (una por episodio)
    ├── scripts/              extracción, validación y generación del entregable
    └── Punzadas_Sonoras_referencias.xlsx   entregable actual (autor, obra, tipo, tag...)
```

---

## Próximos pasos

1. Completar la extracción de las referencias que faltan (Las Glosas, los especiales y
   el episodio de cierre de temporada).
2. Construir la web pública: sitio estático que lee el dataset, con filtros por autor,
   obra, temporada, tipo y tema, y un grafo de obras puestas en diálogo entre sí.

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

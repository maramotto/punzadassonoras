# Punzadas Sonoras — base de datos de referencias culturales

Proyecto de fans (Mara) para catalogar todas las obras que se citan en el podcast
**Punzadas Sonoras**, de Paula Ducay e Inés García, producido por Radio Primavera Sound.
El objetivo final es una **web pública** navegable por autor, obra, tema y temporada.

Habla en español con la usuaria. El proyecto será público, así que las autoras del podcast
deben quedar acreditadas y las fuentes citadas con claridad.

---

## Estado actual

| | |
|---|---|
| Episodios catalogados | **102** de 117 |
| Referencias extraídas | **583** |
| Autores distintos | **412** |
| Enriquecimiento bibliográfico | **258 de 583 filas (44%)** con editorial/año, vía Open Library + Dialnet + MCU |
| Fuente de las referencias | Solo texto (descripciones + newsletter). **Ninguna del audio todavía.** |
| Entregable actual | `Punzadas_Sonoras_referencias.xlsx` (4 pestañas: Referencias, Episodios, Autores, Leyenda) |

Barthes es el eje del podcast: 55 menciones, presente en las cinco temporadas. Ernaux, 20.

## De dónde sale cada cosa

- **T3, T4, T5, especiales y Las Glosas (66 eps)** — descripciones de la playlist de YouTube
  `PLLbN7SMQhMVbsBcHlP9RnBXFjZyPgam6y`. Son descripciones largas, con bibliografía detallada.
- **T1 y T2 (36 eps)** — no están en YouTube. Reconstruidos desde el feed RSS público
  `https://feeds.megaphone.fm/PMSL3601016455` (117 episodios, el mismo que alimenta Spotify).
- **T2 desde 2x09 (16 eps)** — además, la newsletter `https://punzadas.substack.com/feed`,
  que da títulos exactos y editoriales que la descripción omite. Solo sirve los 20 posts más
  recientes, así que las cartas de T1 ya no son accesibles por esa vía.

## Mapa de archivos

Este `CLAUDE.md` vive en la raíz del repo; **los datos cuelgan de `podcast-data/`**. Los
scripts calculan sus rutas a partir de su propia ubicación, así que funcionan desde cualquier
directorio.

```
punzadassonoras/                  repo: github.com/maramotto/punzadassonoras
├── CLAUDE.md                     este archivo
├── README.md · LICENSE · .gitignore
├── web/                          vacía, para el sitio estático
└── podcast-data/
    ├── PILOTO_esquema_blando.md  esquema pendiente con ejemplos — LÉELO PRIMERO
    ├── Punzadas_Sonoras_referencias.xlsx    entregable actual
    ├── data/
    │   ├── refs_all.json         ← DATASET PRINCIPAL. 102 episodios con sus referencias.
    │   ├── episodios.json        índice de los 66 vídeos de YouTube
    │   ├── episodios_t1t2.json   índice de los 36 episodios de T1-T2 desde el RSS
    │   ├── cache_openlibrary.json  cache del enriquecimiento (225 entradas)
    │   ├── feed.xml              feed RSS completo (117 episodios)
    │   ├── substack.xml          feed de la newsletter
    │   ├── refs_part1-4.json     extracción por lotes de T3-T5 (fuente de refs_all)
    │   ├── refs_t1t2.json        extracción de T1-T2 (fuente de refs_all)
    │   ├── tag_mapping.json      taxonomía controlada: mapea cada tag libre a uno de 37 tags temáticos
    │   ├── cache_dialnet.json    cache del enriquecimiento vía Dialnet (artículos y tesis)
    │   └── cache_mcu.json        cache del enriquecimiento vía la base ISBN del Ministerio de Cultura
    ├── raw/                      .info.json de yt-dlp, uno por vídeo (34 MB)
    ├── transcripts/              65 subtítulos automáticos de YouTube (87 MB)
    ├── scripts/                  ver abajo
    └── transcribir/              paquete para el Mac de la usuaria
```

Los scripts, por orden de uso: `02_batch.sh` (descarga desde YouTube, reanudable) ·
`03_index.py` (construye episodios.json) · `06_unificar.py` (funde las dos fuentes en
refs_all.json) · `08_retag.py` (sustituye los tags libres de cada episodio por la taxonomía
controlada de `data/tag_mapping.json`, conservando los originales en `tags_originales`) ·
`04_enriquecer.py` (Open Library → cache, reanudable, acepta límite) · `09_enriquecer_dialnet.py`
(Dialnet → cache, para artículos y tesis que Open Library no cubre) · `10_enriquecer_mcu.py`
(base ISBN del Ministerio de Cultura → cache, para libros/ensayo que Open Library no cubre) ·
`05_hoja.py` (genera el xlsx) · `07_ventanas.py` (ventanas de transcripción alrededor de un
término: `python3 scripts/07_ventanas.py VIDEO_ID "término" 500`).

**Cadena de regeneración:** `06_unificar.py` → `08_retag.py` → `04_enriquecer.py` →
`09_enriquecer_dialnet.py` → `10_enriquecer_mcu.py` → `05_hoja.py`. Si se corre `06_unificar.py`
de nuevo, vuelve a traer los tags libres desde las fuentes originales y pisa la taxonomía
controlada — hay que relanzar `08_retag.py` después.

## Esquema de datos

`refs_all.json` es una lista de episodios:

```json
{
  "clave": "KMPT0YIutUk",          // video_id de YouTube, o código si es T1/T2
  "serie": "Punzadas Sonoras",      // o "Las Glosas"
  "temporada": 5, "codigo": "5x21",
  "titulo": "...", "fecha": "2026-07-16", "duracion_s": 3927,
  "descripcion": "...",
  "url_youtube": "...", "url_spotify": "...", "url_audio": "...",
  "tiene_transcripcion": true,
  "fuente_datos": "descripción de YouTube",
  "tags": ["Amor y vínculos afectivos"],          // taxonomía controlada, 37 valores posibles
  "tags_originales": ["amor", "ruptura amorosa"],  // tags libres previos, por si hay que revertir
  "refs": [
    {"autor": "Roland Barthes", "obra": "Fragmentos de un discurso amoroso",
     "tipo": "libro", "notas": "figura «Exilio»", "editorial_mencionada": "Katz"}
  ]
}
```

---

## LA TAREA PENDIENTE: extracción desde el audio

Es lo único que queda de la fase de datos. **Lee `podcast-data/PILOTO_esquema_blando.md` antes de
tocar nada**: contiene el esquema acordado con ejemplos reales y tres preguntas de criterio
que la usuaria puede haber contestado ya.

### Por qué merece la pena

En una sola prueba sobre el 5x21, el audio aportó: tres obras que no aparecen en la
descripción (*Persuasión*, *Jane Eyre*, *Por el camino de Swann*), una editorial que las
bases de datos no daban (Katz), el alcance real (de Cavarero leyeron solo unos capítulos),
el soporte (de *Sentido y sensibilidad* vieron la película, no leyeron el libro) y una misma
obra usada con dos funciones distintas en el mismo episodio.

### Campos nuevos por referencia

- **función** — eje del episodio · apoyo teórico · ejemplo · contrapunto · mencionada dentro
  de otra fuente · mención de pasada · recomendación
- **alcance** — obra completa · un capítulo o figura · un pasaje o cita · solo el autor
- **soporte** — leído · visto · escuchado · citado de oídas
- **tono** — entusiasta · crítico · ambivalente · neutro
- **contexto** — una o dos frases: qué idea concreta ilustra
- **cita** — literal de la transcripción
- **inicio_s** — segundos, para construir `youtube.com/watch?v=ID&t=Ns`
- **hablante** — cuando haya diarización
- **en_dialogo_con** — otras obras con las que se contrapone o compara

### Método recomendado

No leas las transcripciones enteras: son ~90.000 caracteres por episodio, 116 horas en total.

1. Para cada episodio ya tienes en `podcast-data/data/refs_all.json` la **lista canónica** de obras y autores,
   sacada del texto. Búscalos en la transcripción con **coincidencia difusa**
   (`difflib.SequenceMatcher`, umbral ~0.72), porque Whisper y los subtítulos destrozan los
   nombres propios: Cavarero → «cabarero», Proust → «prust», Cianfrance → «derexian france».
   Está comprobado que se recuperan.
2. Extrae ventanas de ±400-700 caracteres alrededor de cada acierto. `podcast-data/scripts/07_ventanas.py`
   ya hace esto; úsalo o adáptalo. Uso: `python3 scripts/07_ventanas.py VIDEO_ID "término" 500`.
3. Sobre esas ventanas, rellena los campos blandos.
4. Segunda pasada para **descubrir obras nuevas**: busca marcadores («el libro», «la novela»,
   «la peli», «el ensayo», «que se llama», «escribe», «de la mano de») y revisa esas ventanas.
   Ahí es donde aparecieron *Persuasión* y *Jane Eyre*.
5. Guarda en un archivo nuevo (`podcast-data/data/refs_audio.json`), **sin sobrescribir**
   `refs_all.json`. Fúndelo después.

Ve por lotes y guarda el progreso entre lotes; son 117 episodios.

## Trabajo posterior, por orden

1. **Completar el catálogo** — faltan 15 episodios que están en el RSS pero no en la playlist
   de YouTube (3x03, 3x17, 3x21, 4x03, 4x08, 4x16, 4x19, 5x13, 5x14, 5x18 y algunas Glosas).
   Se extraen igual que T1-T2, desde `podcast-data/data/feed.xml`.
2. **Mejorar el enriquecimiento** — ya en marcha. Open Library dejaba 412 de 583 filas sin datos
   (cubre mal el ensayo español de editorial pequeña, los artículos académicos y las tesis). Se
   probaron tres fuentes alternativas sobre 10 casos reales antes de lanzar la pasada completa, y
   luego se lanzó con las dos que funcionaron:
   - **Dialnet** (artículos y tesis, vía `09_enriquecer_dialnet.py`): 100% de acierto en la
     prueba de 10 casos; **31 de 59 filas (53%)** en la pasada completa sobre las 59 que Open
     Library no cubría. Sin API pública, se scrapea el HTML de su buscador. Es muy sensible al
     ritmo de peticiones — empieza a devolver 503 incluso a menos de una petición por segundo;
     el script reintenta con espera creciente y aun así hubo que relanzarlo dos veces subiendo el
     intervalo hasta 3.5 s entre consultas.
   - **Base de datos ISBN del Ministerio de Cultura** (libros/ensayo, vía
     `10_enriquecer_mcu.py`): 67% de acierto en la prueba de 10 casos; **56 de 100 filas (56%)**
     en la pasada completa, de las cuales 30 «verificado» (título y autor coinciden) y 26
     «inferido» (revísalas antes de publicar). Sin API pública tampoco: es una app con sesión
     (`JSESSIONID`) que hay que scrapear con `curl` (vía `urllib` falla por un
     `CERTIFICATE_VERIFY_FAILED` — su cadena de certificados no está en el bundle por defecto de
     Python). A diferencia de Open Library, aquí buscar por «autor completo + título completo»
     pegado falla casi siempre: hay que buscar solo por título (o apellido + primeras palabras),
     lo que sube el riesgo de coincidir con un libro de otro autor con el mismo título exacto
     (pasó con «La baba del caracol», que además de la edición de Chantal Maillard de 2014 tiene
     una homónima de 1985/2019 de otro autor completamente distinto) — el script desempata
     prefiriendo el candidato cuyo autor también coincide, pero **las filas marcadas
     «MCU — inferido» en la hoja siguen mereciendo una revisión manual**, es el punto más frágil
     de esta pasada.
   - **Wikidata**: descartada, no se llegó a lanzar. 0 aciertos sobre los 10 casos, y ni siquiera
     en el mejor caso posible (los originales de Barthes y Bourdieu, que sí están en Wikidata)
     tiene editorial ni traductor de la edición *española* — solo autor, idioma y año de la obra
     *original*.
   - **Resultado combinado**: de 412 filas sin datos se pasó a **325** (171 ya las resolvía Open
     Library, 87 más entre Dialnet y MCU; 175 nunca se van a poder resolver porque no tienen una
     obra concreta — son autoras mencionadas, colaboradoras, etc.). Cobertura total: del 29% al
     44% de las 583 referencias.
   - **La columna Traductor sigue vacía**: ninguna de las tres fuentes la resuelve, tampoco en
     libros claramente traducidos (comprobado con la biografía de Barthes de Samoyault, que ni
     MCU ni Wikidata traen). Sigue pendiente — requeriría otra fuente específica de traducciones.
   - Google Books devuelve 429 por cuota. `todostuslibros.com` no responde a peticiones
     automáticas: los enlaces de compra son búsquedas construidas, no fichas verificadas.
3. **La web** — va en `web/` (vacía), que está vacía a propósito. Decisión ya tomada: sitio estático
   que lee un JSON, desplegable en GitHub Pages o Netlify, con filtros por autor, obra,
   temporada, tipo y tag. Los campos blandos permiten además un grafo de obras en diálogo, que
   es lo que la haría distinta de una lista.

## Transcripción (corre en el Mac de la usuaria, no aquí)

`podcast-data/transcribir/` contiene `transcribir.py`, `README.md` y `manifiesto_audio.json` (117 episodios
con su URL de audio del feed). Transcribe con mlx-whisper large-v3 en Apple Silicon y separa
voces con pyannote 3.1. Es reanudable. Probado end-to-end salvo el paso de Whisper.

Cuando termine, los `.json` de `podcast-data/transcribir/transcripciones/` sustituyen a
`podcast-data/transcripts/*.es.json3` como fuente: tienen puntuación, nombres propios correctos y
hablante.

**Sobre los hablantes:** salen como `SPEAKER_00` / `SPEAKER_01`, y la asignación **puede
cambiar de un episodio a otro**. Hay que emparejarlos episodio a episodio. En los directos con
invitada (Elena López Riera 4x05, Marta Jiménez Serrano 4x10, Pau Luque, Blanca Lacasa) el
script asume dos voces y saldrá mal: hay que relanzarlos con `N_HABLANTES = 3`.

## Cosas que ya se han aprendido a la mala

- **Las descripciones de YouTube son la mejor fuente de nombres**, y las transcripciones la
  mejor fuente de contexto. No compiten: se complementan. Un nombre propio se fía siempre al
  texto, nunca al audio.
- **Numeración de T1 y T2: es una reconstrucción, no oficial.** El feed no trae número de
  temporada ni de episodio. Se ordenó por fecha y se puso el corte en el parón de verano de
  2022 (T1: feb–ago 2022, 12 eps; T2: sep 2022–jul 2023, 24 eps). **Decisión (2026-07-31): se
  queda así, no se va a contrastar con las autoras.**
- **Enlaces de Spotify**: solo se tiene el del programa. Los enlaces por episodio requieren la
  API de Spotify con credenciales. `punzadas.com/punzadas-sonoras` tiene algunos sueltos de
  episodios en vivo.
- **Numeración duplicada**: las Glosas «Sobre la salud sexual» y «Rodoreda, un bosque»
  aparecen ambas como 1x05 en los títulos originales del podcast.
- **Huecos de contenido**: 3x06, 3x07 y el especial «Fuego» no tienen bibliografía en la
  descripción. 5x02 no tiene subtítulos en YouTube. Todos se resuelven con la transcripción.
- **Verificación automática ya montada**: la columna «Título citado literalmente» del xlsx
  comprueba que cada título aparezca tal cual en la descripción. 345 sí, 63 no (títulos
  normalizados o inferidos). Mantén esa comprobación al añadir datos nuevos.
- **El repo es público**: <https://github.com/maramotto/punzadassonoras>. Antes de hacer
  commit de `podcast-data/`, lee la sección siguiente.

## Qué publicar y qué no

`podcast-data/` pesa 123 MB, de los cuales 121 MB son `transcripts/` (87 MB de subtítulos
automáticos de YouTube) y `raw/` (34 MB de metadatos de yt-dlp). No revientan ningún límite de
GitHub —el archivo mayor son 1,8 MB— pero son **material de terceros**: transcripciones
íntegras del podcast, no un índice derivado. Publicar el catálogo de referencias es una cosa;
republicar las transcripciones completas es otra distinta, y conviene consultarlo con las
autoras antes.

Recomendación por defecto: versionar `podcast-data/data/`, `scripts/`, `transcribir/`, el xlsx
y el piloto; dejar `transcripts/` y `raw/` fuera con `.gitignore` (son regenerables con
`02_batch.sh`). Si la usuaria decide publicarlo todo, que sea una decisión suya y explícita.

Falta además añadir al `.gitignore`: `.DS_Store`, `.idea/`, `podcast-data/transcribir/audio/`
y `podcast-data/transcribir/transcripciones/`.

## Enlaces

- Playlist YouTube: <https://www.youtube.com/playlist?list=PLLbN7SMQhMVbsBcHlP9RnBXFjZyPgam6y>
- Feed RSS: <https://feeds.megaphone.fm/PMSL3601016455>
- Spotify: <https://open.spotify.com/show/444xAKuV4A4WUlSXqyl51P>
- Web de las autoras: <https://punzadas.com/punzadas-sonoras/>
- Newsletter: <https://punzadas.substack.com>
- Radio Primavera Sound: <https://www.primaverasound.com/es/radio/shows/punzadas-sonoras>

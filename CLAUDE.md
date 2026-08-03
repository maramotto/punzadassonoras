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
| Episodios catalogados | **117 de 117** ✅ |
| Transcripciones | **117 de 117** ✅ (mlx-whisper large-v3 + pyannote 3.1, con hablante) |
| Referencias extraídas | **671** |
| Autores distintos | **469** |
| Enriquecimiento bibliográfico | **286 de 671 filas (43%)** con editorial/año, vía Open Library + Dialnet + MCU. Sobre las 465 filas que sí tienen obra concreta: **62%** |
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
- **Los 15 fuera de la playlist (2026-08-03)** — 3x03, 3x17, 3x21, 4x03, 4x08, 4x16, 4x19,
  5x13, 5x14, 5x18 y las Glosas 1x01, 1x04, 1x05, 1x08, 1x09. Tienen transcripción propia pero
  nunca se subieron a YouTube, así que sus referencias salen de la descripción del feed RSS
  (`data/desc_faltantes.md` → `data/refs_faltantes.json`). Su numeración es **reconstruida por
  fecha**, igual que la de T1-T2.

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
    │   ├── refs_faltantes.json   extracción de los 15 fuera de la playlist (fuente de refs_all)
    │   ├── meta_faltantes.json   metadatos de esos 15 sacados del feed (título, audio, duración)
    │   ├── desc_faltantes.md     sus descripciones en limpio, para releerlas sin tocar el XML
    │   ├── tag_mapping.json      taxonomía controlada: mapea cada tag libre a uno de 37 tags temáticos
    │   ├── cache_dialnet.json    cache del enriquecimiento vía Dialnet (artículos y tesis)
    │   └── cache_mcu.json        cache del enriquecimiento vía la base ISBN del Ministerio de Cultura
    ├── raw/                      .info.json de yt-dlp, uno por vídeo (34 MB)
    ├── transcripts/              65 subtítulos automáticos de YouTube (87 MB)
    ├── scripts/                  ver abajo
    └── transcribir/              paquete para el Mac de la usuaria
```

Los scripts, por orden de uso: `02_batch.sh` (descarga desde YouTube, reanudable) ·
`03_index.py` (construye episodios.json) · `06_unificar.py` (funde las **tres** fuentes en
refs_all.json; también renumera las Glosas duplicadas y corrige la fecha del 3x05) · `08_retag.py` (sustituye los tags libres de cada episodio por la taxonomía
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
tocar nada**: contiene el esquema acordado con ejemplos reales.

### Criterio ya decidido por la usuaria (2026-08-03)

Las tres dudas del piloto están contestadas. No hay que volver a preguntarlas:

1. **Una fila por mención**, no por obra y episodio. Si una obra aparece dos veces en el mismo
   episodio con dos funciones distintas, son dos filas.
2. **`cita` y `contexto` en campos separados**: `cita` es literal de la transcripción y no se
   toca; `contexto` es interpretación nuestra y va marcado como tal, para poder ocultarlo o
   filtrarlo en la web.
3. **Las obras anidadas sí entran**, con `función = mencionada dentro de otra fuente` y un
   campo que apunta a la fuente que las cita (p. ej. *Persuasión* y *Jane Eyre* dentro del
   artículo de Pahl). Se pueden filtrar después.

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

1. ~~**Completar el catálogo**~~ — **hecho el 2026-08-03.** Los 15 que faltaban ya están, vía
   `data/refs_faltantes.json`. 102 → 117 episodios, 583 → 671 referencias, 412 → 469 autores.
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

## Transcripción — TERMINADA (2026-08-03)

**117 de 117 episodios transcritos.** Corrió en el Mac de la usuaria con mlx-whisper large-v3
(Apple Silicon) + pyannote 3.1. `podcast-data/transcribir/` contiene `transcribir.py`,
`README.md`, `manifiesto_audio.json` y el log `progreso.log`.

Los `.json` de `podcast-data/transcribir/transcripciones/` **ya sustituyen** a
`podcast-data/transcripts/*.es.json3` como fuente: tienen puntuación, nombres propios correctos y
hablante. Formato: `{slug, codigo, titulo, fecha, video_id, url_audio, segmentos:[{inicio, fin,
texto, hablante}]}`. Los `.txt` hermanos son un volcado legible del mismo contenido.

Los cuatro directos con invitada (Blanca Lacasa 3x17, Elena López Riera 4x05, Pau Luque 4x08,
Marta Jiménez Serrano 4x10) se relanzaron con `N_HABLANTES = 3` y están verificados con tres
voces.

**Sobre los hablantes:** salen como `SPEAKER_00` / `SPEAKER_01` / `SPEAKER_02`, y la asignación
**cambia de un episodio a otro**. Hay que emparejar quién es quién episodio a episodio, a mano,
cuando toque explotar las transcripciones. No está hecho.

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
- **Numeración duplicada de las Glosas**: «Rodoreda, un bosque» y «Sobre la salud sexual»
  aparecen ambas como 1x05 en los títulos originales del podcast. **Decisión (2026-08-03):**
  `06_unificar.py` las renumera por orden cronológico a **1x06** y **1x07** (constante
  `GLOSAS_RENUM`), y deja constancia del título original en `notas_episodio`. Con eso la serie
  queda consecutiva de 1x01 a 1x09. La numeración de las Glosas la confirman las propias
  descripciones: Nefando dice «primer episodio» y La cronología del agua dice «cuarto episodio»,
  y ambas cuadran con el orden por fecha.
- **Fecha del 3x05**: YouTube dice 2023-11-08 y el feed 2023-11-09. Se usa la del feed, que es
  la que llevan las transcripciones (constante `FECHA_FIX` en `06_unificar.py`).
- **Huecos de contenido**: 3x06, 3x07 y el especial «Fuego» no tienen bibliografía en la
  descripción. 5x02 no tiene subtítulos en YouTube. Todos se resuelven con la transcripción.
- **Verificación automática ya montada**: la columna «Título citado literalmente» del xlsx
  comprueba que cada título aparezca tal cual en la descripción. 345 sí, 63 no (títulos
  normalizados o inferidos). Mantén esa comprobación al añadir datos nuevos.
- **El repo es público**: <https://github.com/maramotto/punzadassonoras>. Antes de hacer
  commit de `podcast-data/`, lee la sección siguiente.

## Qué publicar y qué no

El criterio no es el tamaño, es **qué es caro o imposible de regenerar**. `podcast-data/` pesa
1,8 GB, pero casi todo es reproducible:

| Carpeta | Peso | ¿Regenerable? | ¿Al repo? |
|---|---|---|---|
| `data/` | 2,3 MB | Las caches, **no sin volver a scrapear** | **Sí** |
| `scripts/` | 76 KB | No | **Sí** |
| `transcribir/` (código y logs) | ~80 KB | No | **Sí** |
| `Punzadas_Sonoras_referencias.xlsx` | 192 KB | Sí, con `05_hoja.py` | **Sí**, es el entregable |
| `transcribir/transcripciones/` | 30 MB | **No en la práctica** | **Sí** (decisión de Mara, 2026-08-03) |
| `transcripts/` (subtítulos YouTube) | 87 MB | Sí, `02_batch.sh` | No |
| `raw/` (yt-dlp `.info.json`) | 34 MB | Sí, `02_batch.sh` | No |
| `transcribir/audio/` | 150 MB | Sí, desde `manifiesto_audio.json` | No, nunca |

Tres cosas que conviene tener claras:

1. **Las caches de enriquecimiento (`cache_*.json`) hay que versionarlas.** Son 85 KB y son lo
   único que evita repetir el scrapeo de Dialnet y del MCU, que no tienen API, van por sesión
   y devuelven 503 en cuanto se les aprieta. Perderlas cuesta horas, no minutos.
2. **`transcribir/transcripciones/` es el activo irrepetible del proyecto.** Son 117 JSON con
   texto puntuado, marcas de tiempo y hablante: 111 horas de audio pasadas por la GPU del Mac.
   Ningún script del repo las reconstruye. **Decisión de Mara (2026-08-03): van al repo.**
   Git normal, no LFS (el archivo mayor son 304 KB, y en texto plano GitHub las deja buscar y
   diferenciar). Versionarlas es a la vez la copia de seguridad.
3. Al ser transcripción íntegra de material de terceros, la carpeta lleva su propio
   `README.md` con la atribución a Paula Ducay e Inés García y a Radio Primavera Sound, el
   aviso de que son automáticas y contienen errores, y la advertencia de que las etiquetas de
   hablante no están emparejadas con personas. **Si se toca esa carpeta, se mantiene el
   README.** Si las autoras piden retirarla, se retira.

Ya están en `.gitignore`: `.DS_Store`, `.idea/`, `transcripts/`, `raw/`, `transcribir/audio/`,
`transcribir/.venv/` y `transcribir_nohup.log`. Con excepción explícita para `progreso.log` y
`transcribir_invitados.log`, que la plantilla de Python se llevaba por delante con `*.log`.

## Enlaces

- Playlist YouTube: <https://www.youtube.com/playlist?list=PLLbN7SMQhMVbsBcHlP9RnBXFjZyPgam6y>
- Feed RSS: <https://feeds.megaphone.fm/PMSL3601016455>
- Spotify: <https://open.spotify.com/show/444xAKuV4A4WUlSXqyl51P>
- Web de las autoras: <https://punzadas.com/punzadas-sonoras/>
- Newsletter: <https://punzadas.substack.com>
- Radio Primavera Sound: <https://www.primaverasound.com/es/radio/shows/punzadas-sonoras>

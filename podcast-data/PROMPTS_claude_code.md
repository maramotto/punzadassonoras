# Prompts para Claude Code — transcripción y extracción

Manual de uso. Cada bloque es un prompt para copiar y pegar en Claude Code, abierto en la
raíz del repo. Sustituye lo que va en `«…»`.

Los dos procesos son independientes: se transcribe una vez y se extrae las veces que haga
falta. Si cambia el criterio de extracción, se re-extrae sin volver a transcribir.

---

## Índice

| Situación | Bloques a usar |
|---|---|
| Episodio nuevo del podcast | A0 → A1 → B1 |
| Rehacer una transcripción que salió mal | A2 |
| Rehacer la extracción de un episodio ya transcrito | B1 |
| Extraer un lote de episodios | B2 |
| Cambió el criterio y hay que re-extraer todo | B3 |

---

# BLOQUE A — Transcripción

Corre en el Mac de Mara, con `mlx-whisper` + `pyannote`. Necesita el entorno de
`podcast-data/transcribir/` activado y la variable `HF_TOKEN`. Ver
`podcast-data/transcribir/README.md` si algo falla.

**Antes de nada, en la Terminal:**

```bash
cd podcast-data/transcribir
source .venv/bin/activate
export HF_TOKEN=hf_tu_token
```

## A0 — Dar de alta un episodio nuevo

Solo para episodios que aún no están en el manifiesto (los 117 actuales ya lo están).

```
Hay un episodio nuevo de Punzadas Sonoras que todavía no está en el proyecto.

1. Descarga el feed RSS actualizado a podcast-data/data/feed.xml:
   https://feeds.megaphone.fm/PMSL3601016455
   Guarda antes una copia como feed_anterior.xml para poder comparar.

2. Compara el feed nuevo con podcast-data/transcribir/manifiesto_audio.json (117
   entradas) e identifica los episodios que están en el feed y no en el manifiesto.
   Muéstramelos antes de tocar nada: título, fecha y duración.

3. Para cada uno, añade una entrada al manifiesto con esta forma exacta:
   {"codigo": "«5x22»", "titulo": "...", "fecha": "AAAA-MM-DD", "video_id": "",
    "url_audio": "https://traffic.megaphone.fm/....mp3", "duracion_s": 1234,
    "slug": "AAAA-MM-DD_«5x22»"}

   - El `codigo` lo decides tú por continuidad de temporada y fecha. Si dudas del
     número de temporada, PREGÚNTAME antes de escribirlo.
   - `video_id` se deja vacío salvo que el episodio esté en la playlist de YouTube
     PLLbN7SMQhMVbsBcHlP9RnBXFjZyPgam6y. Compruébalo.
   - `duracion_s` sale del campo itunes:duration del feed.

4. Copia el manifiesto actualizado también a podcast-data/data/manifiesto_audio.json
   (las dos copias estaban desincronizadas; deja las dos iguales).

5. Guarda la descripción del episodio: añádela a podcast-data/data/refs_all.json NO,
   eso es un paso posterior. De momento vuélcala en
   podcast-data/data/desc_nuevos.md con su código como cabecera.

No transcribas todavía.
```

## A1 — Transcribir uno o varios episodios

```
Transcribe «5x22» con el script del proyecto.

Ejecuta desde podcast-data/transcribir con el venv activado y HF_TOKEN puesto:

    python3 transcribir.py --solo «5x22»

Para varios, sepáralos por comas: --solo 5x22,5x23
Si el episodio tiene invitada (tres voces), añade: --hablantes 3

El script es reanudable y borra el audio al terminar cada episodio.

Cuando acabe, comprueba y dime:
- Que existen transcripciones/«AAAA-MM-DD_5x22».json y .txt
- Cuántos segmentos tiene y la duración total, contrastada con duracion_s del manifiesto
  (si difieren más de un 2%, algo falló en la descarga)
- El reparto de tiempo entre hablantes. Si una voz se lleva más del 85% del total, la
  diarización falló: avísame, no lo des por bueno
- Pégame los primeros 300 caracteres del .txt para que vea si el texto tiene sentido
```

## A2 — Rehacer una transcripción que salió mal

```
La transcripción de «3x17» está mal: «di qué pasa — la diarización desequilibrada / el
texto está cortado / faltan minutos al final».

Relánzala forzando el reproceso:

    python3 transcribir.py --solo «3x17» --forzar --hablantes «2 o 3»

Antes de sobrescribir, mueve la transcripción antigua a
transcripciones/_descartadas/ por si acaso.

Al terminar, compara la nueva con la antigua: nº de segmentos, duración cubierta y
reparto por hablante. Dime si ha mejorado de verdad o no.

Ojo: los cuatro directos con invitada son 3x17 (Blanca Lacasa), 4x05 (Elena López
Riera), 4x08 (Pau Luque) y 4x10 (Marta Jiménez Serrano). Esos van con --hablantes 3.
```

---

# BLOQUE B — Extracción

No necesita el Mac ni el venv: solo la transcripción en JSON.

**El criterio completo está en `podcast-data/CRITERIO_extraccion.md`.** Los prompts de
abajo lo invocan; no repitas las reglas en el prompt.

## B1 — Extraer un episodio

```
Extrae las referencias culturales de «5x22» desde su transcripción.

Lee primero podcast-data/CRITERIO_extraccion.md y aplícalo al pie de la letra.

Entrada:
- podcast-data/transcribir/transcripciones/«AAAA-MM-DD_5x22».json
- La descripción oficial del episodio (en data/episodios.json campo desc_limpia, o en
  data/refs_all.json campo descripcion, según dónde esté)

Salida, en podcast-data/extraccion/:
- «5x22».json
- «5x22».md   (genérala con scripts/12_generar_ficha_extraccion.py, no a mano)

Después ejecuta el validador y no des el trabajo por terminado hasta que pase limpio:

    python3 podcast-data/scripts/11_validar_extraccion.py «5x22»

Si falla, corrige el JSON. Nunca el validador.

Al final resúmeme: nº de menciones, entidades distintas, reparto por fuente/tipo/función,
las menciones con confianza distinta de alta, y cualquier caso que te haya obligado a
interpretar el criterio. Ese último punto es el que más me interesa.
```

## B2 — Extraer un lote

```
Extrae las referencias de estos episodios: «3x06, 1x03, 4x10».

Lee podcast-data/CRITERIO_extraccion.md y aplícalo a cada uno.

Trabaja EPISODIO A EPISODIO, no todos a la vez:
  1. Lee la transcripción completa de uno
  2. Extrae, escribe el JSON, genera el .md
  3. Pasa el validador
  4. Solo entonces pasa al siguiente

Guarda el progreso según avanzas: si te quedas sin contexto quiero poder retomar sin
repetir lo hecho. Lleva un podcast-data/extraccion/_progreso.md con una línea por
episodio: código, nº de menciones, si pasó el validador, y las dudas que te surgieron.

Al terminar el lote, dame una tabla comparando los episodios entre sí (menciones,
entidades nuevas frente a la descripción, % con confianza alta) y dime si el criterio
aguanta igual de bien en todos o si hay perfiles de episodio donde se rompe.
```

## B3 — Re-extraer todo tras un cambio de criterio

```
He cambiado podcast-data/CRITERIO_extraccion.md. Concretamente: «describe el cambio».

1. Léelo entero y dime qué implica el cambio para lo ya extraído: qué campos se ven
   afectados y qué menciones existentes habría que revisar. No toques nada todavía.

2. Comprueba si el cambio se puede aplicar con un script sobre los JSON existentes
   (renombrar valores, mover campos) o si obliga a releer las transcripciones. Dime
   cuál de las dos y por qué.

3. Si basta con un script, escríbelo en podcast-data/scripts/ numerado a continuación
   del último, con --dry-run que enseñe los cambios antes de aplicarlos.

4. Si hay que releer, dímelo y espera: eso lo lanzo yo por lotes con el bloque B2.

En cualquier caso, actualiza el validador para que compruebe el criterio nuevo, y
vuelve a pasarlo sobre todo lo que haya en podcast-data/extraccion/.
```

---

# Recordatorios

**Lo que nunca se toca sin pedirlo explícitamente:** `data/refs_all.json`, el `.xlsx`,
las caches `cache_*.json` y las transcripciones ya validadas.

**Scripts con rutas rotas:** `01_ingest.sh`, `02_batch.sh` y `03_index.py` tienen `BASE`
hardcodeado de una sesión antigua. No ejecutarlos. Todo script nuevo calcula `BASE` con
`os.path.dirname`, como `04` a `12`.

**La cadena de regeneración del entregable** (independiente de todo esto):
`06_unificar.py` → `08_retag.py` → `04_enriquecer.py` → `09_enriquecer_dialnet.py` →
`10_enriquecer_mcu.py` → `05_hoja.py`. Si se corre `06`, hay que relanzar `08` después o
se pierden los tags controlados.

**Enriquecimiento bibliográfico:** no es trabajo de la extracción. La extracción solo
recoge lo que se dice en el audio, con su cita. Editoriales, años y traductores vienen
después, de los catálogos.

# Criterio de extracción — v2

Reglas para extraer las referencias culturales de un episodio desde su transcripción.
Este documento es la fuente de verdad: los prompts de `PROMPTS_claude_code.md` lo invocan
en vez de repetirlo.

**v2 (2026-08-04)** — corrige tres fallos detectados en la prueba del 5x21: `datos_nuevos`
sin validar, `contrapunto` sin usar y `confianza` midiendo dos cosas a la vez. Añade el
campo `parte`. El histórico está al final.

---

## 1. Principio

La transcripción es la **única** fuente de la pasada principal. La descripción del
episodio se consulta al final, para contrastar, nunca para rellenar huecos.

Todo dato que acabe en el JSON tiene que poder señalarse con el dedo en la transcripción.
Lo que no se oye, no existe. Si algo se sabe por cultura general y no se dice en el
episodio, no entra: eso es enriquecimiento y va en otra fase, desde catálogos.

---

## 2. Unidad: una fila por mención

Si la misma obra aparece dos veces en el episodio con funciones distintas, son dos
menciones. *Sentido y sensibilidad* en el 5x21 aparece primero como obra que analiza el
artículo de Pahl y luego como ejemplo propio de cierre: dos filas.

Para obras muy estructuradas —*Fragmentos de un discurso amoroso* sobre todo— **una fila
por figura o capítulo**, con el nombre de la figura en el campo `parte`. Barthes es el eje
del podcast, con más de 60 menciones en las cinco temporadas: ese mapa de figuras es
precisamente lo que hace distinta a la base de datos. No se colapsa.

---

## 3. Schema

```json
{
  "codigo": "5x21",
  "titulo": "...",
  "fecha": "2026-07-16",
  "video_id": "KMPT0YIutUk",
  "duracion_s": 3925,
  "transcripcion": "2026-07-16_5x21.json",
  "criterio": "v2",
  "menciones": [ ... ]
}
```

Cada mención:

```json
{
  "id": "5x21-005",
  "autor": "Adriana Cavarero",
  "obra": "Cuéntame mi historia. Filosofía de la narración",
  "parte": "",
  "tipo": "libro",
  "subtipo": "",
  "funcion": "apoyo teórico",
  "alcance": "un capítulo o figura",
  "soporte": "leído",
  "tono": "entusiasta",
  "grado": "primera mano",
  "via": null,
  "autores_citados": [],
  "fuente": "ambas",
  "inicio_s": 906,
  "segmento_idx": 388,
  "hablante": "SPEAKER_01",
  "cita": "leí un libro de Adriana Cabarero, que en realidad son unos capítulos",
  "contexto": "Lo leen en paralelo a Barthes para sostener que la muerte está constitutivamente excluida de la narración.",
  "en_dialogo_con": ["Fragmentos de un discurso amoroso"],
  "datos_nuevos": [
    {"campo": "editorial_mencionada", "valor": "Katz",
     "cita": "que está editado en Cats", "inicio_s": 906}
  ],
  "confianza": "alta"
}
```

### Vocabularios cerrados

Si un valor no encaja, usa el más cercano y explica el matiz en `subtipo` o `contexto`.
Nunca inventes valores nuevos.

| campo | valores |
|---|---|
| `tipo` | `libro` · `artículo` · `película` · `serie` · `obra de teatro` · `poema` · `obra de arte` · `música` · `podcast` · `persona` · `concepto` · `otro` |
| `funcion` | `eje del episodio` · `apoyo teórico` · `ejemplo` · `contrapunto` · `mención de pasada` · `recomendación` |
| `alcance` | `obra completa` · `un capítulo o figura` · `un pasaje o cita` · `solo el autor` |
| `soporte` | `leído` · `visto` · `escuchado` · `citado de oídas` · `sin determinar` |
| `tono` | `entusiasta` · `crítico` · `ambivalente` · `neutro` |
| `grado` | `primera mano` · `dentro de otra fuente` |
| `fuente` | `audio` · `descripción` · `ambas` |
| `confianza` | `alta` · `media` · `baja` |

---

## 4. Reglas por campo

### `cita` — la regla que sostiene todo lo demás

Sin cita literal, la mención no existe. Debe ser **subcadena exacta** del `texto` de uno o
varios segmentos consecutivos. Cópiala, no la reescribas de memoria.

**Nunca corrijas dentro de la cita.** Si Whisper transcribe «Adriana Cabarero», «Bartes» o
«derexian france», la cita conserva el error tal cual. El nombre correcto va en `autor`.

### `autor` y `obra` — se normalizan, no se completan

Puedes corregir la grafía de un nombre que reconoces. **No puedes** completar un título que
no dicen. Si dicen «el libro de Cavarero» sin más, `obra` queda vacío y `alcance` es
`solo el autor`.

### `parte`

Figura, capítulo o sección concreta cuando la nombran: `"Exilio"`, `"Catástrofe"`,
`"capítulo 3"`. Vacío si hablan de la obra en bloque.

### `funcion` — atención a `contrapunto`

`contrapunto` es la obra que traen **para marcar distancia**: para decir que su episodio no
va de eso, para discrepar, o para contrastar con la tesis que defienden. En el 5x21, la
broma sobre Marian Rojas —«¿te imaginas que esto se convierte en paso uno, el enfado?»— es
un contrapunto, no una mención de pasada: define el episodio por oposición.

Si en un episodio no usas `contrapunto` ni una vez, revisa: suele haber al menos uno.

### `tono`

Describe cómo la tratan **ellas**, no la calidad de la obra. `ambivalente` cuando la usan y
a la vez la critican: el artículo de López-Cantero les sirve pero les parece farragoso.

### `grado`, `via` y `autores_citados` — el segundo grado

Cuando resumen otra fuente y esa fuente cita cosas:

- **Si hay obra concreta** → mención propia, con `grado: "dentro de otra fuente"` y `via`
  apuntando al `id` de la fuente que la contiene. *Persuasión* y *Jane Eyre* dentro del
  artículo de Pahl: sí, fila propia.
- **Si es solo un apellido, sin obra** → **no** genera fila. Va a `autores_citados` de la
  mención madre. «La autora cita a Nussbaum o Goldie» no son dos referencias, es un dato
  de la ficha del artículo de López-Cantero.
- **Si es un chiste** → no entra. «Otros se dedican a traducir las obras de Hume al
  sumerio» no es una referencia a Hume.

### `fuente`

Se rellena en la pasada 3. `descripción` si solo está en la descripción, `audio` si solo
está en la transcripción, `ambas` si en las dos. Las de `descripción` van con `cita: null`,
`funcion` y `tono` vacíos, `confianza: "media"`.

### `datos_nuevos` — con cita propia, sin excepción

Es una **lista** de objetos, cada uno con `campo`, `valor`, `cita` e `inicio_s`. La cita se
valida igual que la principal.

**No normalices el valor más allá de la grafía.** Si dicen «la edición de El paseo», el
valor es `"El paseo"`, no `"El Paseo Editorial"`. Completar el nombre comercial es
enriquecimiento, y el enriquecimiento se hace después, contra catálogos, no aquí. Este es
exactamente el mecanismo que produjo los emparejamientos falsos del MCU.

### `confianza` — mide solo si se oyó bien

- `alta`: autor y obra se entienden con claridad.
- `media`: el título está incompleto, o Whisper deforma un nombre propio pero se reconoce.
- `baja`: el nombre es una conjetura razonable a partir de un audio dudoso.

**No mezcles esto con si la mención merece existir.** Eso lo decide la sección de segundo
grado. Una mención de una sola línea perfectamente audible es `alta`.

### `inicio_s` y `hablante`

`inicio_s` es el `inicio` del segmento donde empieza la cita, redondeado a entero. No lo
estimes. `hablante` se copia del segmento tal cual, sin mapear a Inés ni a Paula: la
diarización agrupa por bloques pero cuela réplicas de la otra voz, así que **no atribuyas
opiniones a una persona concreta en `contexto`**.

### `contexto`

Una o dos frases tuyas, en tercera persona, sobre para qué usan la obra en la conversación.
Es interpretación, y va marcada como tal por estar en un campo aparte. No metas datos que
no estén en la transcripción: ni fechas, ni editoriales, ni argumentos del libro que
conozcas por tu cuenta.

---

## 5. Procedimiento

Lee la transcripción **entera**, en orden. No uses grep para el barrido principal: es
exactamente así como se pierden menciones.

**Pasada 1 — barrido secuencial.** Del primer segmento al último. Anota cada mención según
aparece. No vuelvas atrás, no filtres por relevancia. Incluye lo dudoso.

**Pasada 2 — repesca.** Recorre otra vez buscando construcciones que introducen referencia:

> «un libro de» · «el libro que» · «la peli» · «la película» · «la serie» · «un artículo» ·
> «un texto de» · «escribe» · «dice» · «cuenta» · «leí» · «hemos leído» · «hemos visto» ·
> «estamos leyendo» · «os recomiendo» · «nuestro club» · «editado en» · «traducido» ·
> «la figura de» · «la edición de»

Atención especial a los resúmenes de otras fuentes y a la primera y última rueda de
conversación: las recomendaciones y los cierres se pierden con facilidad.

**Pasada 3 — cruce con la descripción.** Lee ahora la descripción oficial y marca `fuente`.
Lo que esté en la descripción y no en el audio entra con `fuente: "descripción"`.

**Pasada 4 — coherencia.** Ordena por `inicio_s`, renumera los `id`, resuelve los `via`,
rellena `en_dialogo_con` solo cuando enlacen dos obras explícitamente.

---

## 6. Validación

`scripts/11_validar_extraccion.py «codigo»` debe pasar limpio antes de dar nada por bueno.
Si falla, se corrige el JSON, nunca el validador. Comprueba:

1. Cada `cita` es subcadena literal de la transcripción (normalizando espacios, mayúsculas
   y tildes). **Y cada `cita` de `datos_nuevos` también.**
2. La cita cae dentro de `[inicio_s - 30, inicio_s + 90]`.
3. El `hablante` coincide con el del segmento en `inicio_s`.
4. Todos los campos cerrados usan valores de las listas.
5. Obligatorios presentes; `cita` e `inicio_s` salvo si `fuente == "descripción"`.
6. Los `via` apuntan a `id` existentes. Los `id` no se repiten.
7. `0 <= inicio_s <= duracion_s`.
8. Ninguna mención con `grado: "dentro de otra fuente"` tiene `obra` vacía.

Resumen final: nº de menciones, entidades distintas, reparto por `fuente`, `tipo` y
`funcion`, y las de confianza distinta de `alta`.

---

## 7. Historial

**v2 (2026-08-04)** — tras auditar la prueba del 5x21:

- `datos_nuevos` pasa de objeto suelto a lista con cita propia y validación. Motivo: se
  coló `"El Paseo Editorial"` donde el audio solo dice «El paseo», sin que nada lo
  detectara.
- Definido `contrapunto` con ejemplo. Motivo: no se usó ni una vez en 29 menciones, y
  Marian Rojas quedó como `mención de pasada` cuando es el contraejemplo que define el
  episodio.
- `confianza` acotada a fiabilidad de transcripción. Motivo: Hume (un chiste) salía `alta`
  y Goldie (cita real, nombre deformado) `baja`.
- Añadido `parte` y fijada la granularidad por figura.
- Añadido `autores_citados`: los nombres sueltos de segundo grado dejan de generar fila.

**v1 (2026-08-03)** — `PLAN_extraccion_5x21.md`, prueba sobre un episodio.

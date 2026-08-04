# Plan de extracción — prueba con el 5x21

Instrucciones para Claude Code. Objetivo: extraer las referencias culturales del episodio
5x21 **desde la transcripción del audio**, con el esquema blando, y comparar el resultado
contra la extracción actual (que salió solo de la descripción).

No se toca ningún dato existente. Todo lo nuevo va a `podcast-data/extraccion/`.

---

## 0. Contexto

| | |
|---|---|
| Transcripción | `podcast-data/transcribir/transcripciones/2026-07-16_5x21.json` |
| Descripción oficial | `podcast-data/data/episodios.json`, campo `desc_limpia` del código `5x21` |
| Extracción actual | `podcast-data/data/refs_all.json`, entrada con `codigo == "5x21"` (9 refs) |
| Piloto del criterio | `podcast-data/PILOTO_esquema_blando.md` |
| Duración | 3.925 s (65 min), 1.619 segmentos |
| `video_id` | `KMPT0YIutUk` |

La transcripción cabe entera en contexto. **Léela completa, de principio a fin. No uses
grep ni búsquedas por palabra clave para el barrido principal** — es exactamente así como
se pierden menciones.

Estructura de cada segmento: `{"inicio": float, "fin": float, "hablante": "SPEAKER_00|01",
"texto": str}`.

**Sobre los hablantes:** la diarización agrupa por bloques pero dentro de un bloque se
cuelan réplicas de la otra voz. Guarda el `hablante` del segmento tal cual, sin mapear a
Inés ni a Paula, y no atribuyas opiniones a una persona concreta en el campo `contexto`.

---

## 1. Salida

Crea `podcast-data/extraccion/` con tres archivos:

- `5x21.json` — fuente de verdad
- `5x21.md` — ficha legible, **generada a partir del JSON**, nunca escrita a mano
- `5x21_comparativa.md` — informe del punto 5

### Schema de `5x21.json`

```json
{
  "codigo": "5x21",
  "titulo": "Dejar de amar: la ruptura amorosa",
  "fecha": "2026-07-16",
  "video_id": "KMPT0YIutUk",
  "duracion_s": 3925,
  "transcripcion": "2026-07-16_5x21.json",
  "menciones": [ ... ]
}
```

### Schema de cada mención

Una fila **por mención**, no por obra. Si la misma obra aparece dos veces con funciones
distintas, son dos entradas (ver el caso *Sentido y sensibilidad* en el piloto).

```json
{
  "id": "5x21-001",
  "autor": "Adriana Cavarero",
  "obra": "Cuéntame mi historia. Filosofía de la narración",
  "tipo": "libro",
  "subtipo": "",
  "funcion": "apoyo teórico",
  "alcance": "un capítulo o figura",
  "soporte": "leído",
  "tono": "entusiasta",
  "grado": "primera mano",
  "via": null,
  "fuente": "ambas",
  "inicio_s": 906,
  "segmento_idx": 388,
  "hablante": "SPEAKER_01",
  "cita": "leí un libro de Adriana Cabarero, que en realidad son unos capítulos",
  "contexto": "Lo leen en paralelo a Barthes para sostener que la muerte está constitutivamente excluida de la narración.",
  "en_dialogo_con": ["Fragmentos de un discurso amoroso"],
  "datos_nuevos": {"editorial_mencionada": "Katz Editores"},
  "confianza": "alta"
}
```

### Vocabularios cerrados

Si un valor no encaja en la lista, **usa el más cercano y explica el matiz en `subtipo` o
en `contexto`**. No inventes valores nuevos.

| campo | valores admitidos |
|---|---|
| `tipo` | `libro` · `artículo` · `película` · `serie` · `obra de teatro` · `poema` · `obra de arte` · `música` · `podcast` · `persona` · `concepto` · `otro` |
| `funcion` | `eje del episodio` · `apoyo teórico` · `ejemplo` · `contrapunto` · `mención de pasada` · `recomendación` |
| `alcance` | `obra completa` · `un capítulo o figura` · `un pasaje o cita` · `solo el autor` |
| `soporte` | `leído` · `visto` · `escuchado` · `citado de oídas` · `sin determinar` |
| `tono` | `entusiasta` · `crítico` · `ambivalente` · `neutro` |
| `grado` | `primera mano` · `dentro de otra fuente` |
| `fuente` | `audio` · `descripción` · `ambas` |
| `confianza` | `alta` · `media` · `baja` |

Notas por campo:

- **`subtipo`**: texto libre para el matiz que el vocabulario cerrado pierde (`"tesis
  doctoral"`, `"cortometraje"`, `"ópera"`, `"experimento mental"`). Vacío si no aporta.
- **`grado` / `via`**: si `grado` es `dentro de otra fuente`, `via` lleva el `id` de la
  mención de la obra que la contiene. *Persuasión* y *Jane Eyre* salen porque las analiza
  el artículo de Pahl: van con `grado: "dentro de otra fuente"` y `via` apuntando a Pahl.
- **`fuente`**: `descripción` si solo está en `desc_limpia`, `audio` si solo está en la
  transcripción, `ambas` si está en las dos. Se rellena en la pasada 3.
- **`tono`** describe cómo la tratan **ellas**, no la calidad de la obra. El artículo de
  López-Cantero es `ambivalente`: lo usan y a la vez lo critican por farragoso.
- **`datos_nuevos`**: objeto libre para lo que el audio aporta y la descripción no
  (editorial, traductor, año, edición concreta). Vacío si no hay nada.
- **`confianza`**: `alta` si autor y obra se oyen con claridad; `media` si el título está
  incompleto o Whisper deforma un nombre propio; `baja` si es una conjetura razonable. Si
  bajaría de `baja`, no la incluyas.

---

## 2. Reglas anti-alucinación

Son las que fallaron la vez anterior. Innegociables.

1. **Toda mención necesita `cita`.** Sin cita literal, la mención no existe. La cita debe
   ser una subcadena **exacta** de `texto` de algún segmento de la transcripción — cópiala,
   no la reescribas de memoria. Puede abarcar segmentos consecutivos.

2. **Nunca corrijas dentro de `cita`.** Si Whisper transcribe «Adriana Cabarero» o «derex
   ian france», la cita conserva el error. El nombre correcto va en `autor`.

3. **`autor` y `obra` se normalizan, no se inventan.** Puedes corregir la grafía de un
   nombre que reconoces del audio. **No puedes** completar un título que ellas no dicen. Si
   dicen «el libro de Cavarero» sin más, `obra` queda vacío y `alcance` es `solo el autor`.

4. **`contexto` es tuyo, `cita` es de ellas.** El contexto son una o dos frases de
   interpretación, en tercera persona, sobre para qué usan la obra en la conversación. No
   metas datos que no estén en la transcripción: ni fechas, ni editoriales, ni argumentos
   del libro que sepas por tu cuenta.

5. **La descripción del episodio no es fuente en la pasada 1.** Solo se consulta en la
   pasada 3, y para contrastar, nunca para rellenar huecos del audio.

6. **`inicio_s` es el `inicio` del segmento donde empieza la cita**, redondeado a entero.
   No lo estimes.

---

## 3. Procedimiento

### Pasada 1 — barrido secuencial

Lee la transcripción entera en orden, de `inicio: 0.0` al final. Anota cada mención según
aparece. No vuelvas atrás, no saltes, no filtres por relevancia todavía. Incluye lo dudoso.

### Pasada 2 — repesca

Vuelve a recorrer la transcripción buscando construcciones que suelen introducir una
referencia y comprueba que ninguna se quedó fuera:

> «un libro de» · «el libro que» · «la peli» · «la película» · «la serie» · «un artículo»
> · «un texto de» · «escribe» · «dice» · «cuenta» · «leí» · «hemos leído» · «hemos visto»
> · «estamos leyendo» · «os recomiendo» · «nuestro club» · «editado en» · «traducido»

Presta atención especial a los **resúmenes de otras fuentes**: cuando cuentan de qué va un
artículo, suelen enumerar obras que analiza ese artículo. Esas son las de `grado: dentro de
otra fuente`.

Revisa también la primera y la última rueda de conversación: las recomendaciones y los
cierres se pierden fácil.

### Pasada 3 — cruce con la descripción

Lee ahora `desc_limpia` del 5x21. Para cada obra que aparezca ahí:

- Si ya la tienes → `fuente: "ambas"`.
- Si no la tienes → búscala en la transcripción. Si está, añádela. **Si no está en el
  audio, añádela igualmente con `fuente: "descripción"`, `cita: null` y
  `confianza: "media"`** — pero no le inventes `funcion` ni `tono`: déjalos vacíos.

Las que solo salen del audio quedan como `fuente: "audio"`. Esas son la medida de lo que
gana el proyecto con las transcripciones.

### Pasada 4 — coherencia

- Ordena `menciones` por `inicio_s` y renumera los `id` correlativos.
- Resuelve los `via` (deben apuntar a `id` existentes).
- Rellena `en_dialogo_con` solo cuando en la conversación se enlacen explícitamente dos
  obras.

---

## 4. Validador

Escribe `podcast-data/scripts/11_validar_extraccion.py`. Recibe el código de episodio y
falla con código de salida distinto de cero si algo no cuadra. Comprobaciones:

1. **Cita literal.** Normalizando solo espacios, minúsculas y tildes, cada `cita` debe
   aparecer en el texto concatenado de la transcripción. Si no aparece → error, con el `id`
   y la cita ofensora. *Esta es la comprobación importante: es la que detecta invención.*
2. **Coherencia temporal.** La cita debe encontrarse dentro de la ventana
   `[inicio_s - 30, inicio_s + 90]`.
3. **Hablante.** El `hablante` declarado coincide con el del segmento en `inicio_s`.
4. **Vocabularios.** Todos los campos cerrados usan valores de las listas del punto 1.
5. **Obligatorios.** `id`, `autor`, `tipo`, `funcion`, `fuente`, `confianza` presentes;
   `cita` e `inicio_s` presentes salvo si `fuente == "descripción"`.
6. **Referencias.** Todo `via` apunta a un `id` que existe. Los `id` no se repiten.
7. **Rango.** `0 <= inicio_s <= duracion_s`.

Ejecútalo y **no des la extracción por buena hasta que pase limpio**. Si falla, corrige el
JSON, no el validador.

Al final imprime un resumen: nº de menciones, reparto por `fuente`, por `tipo` y por
`funcion`, y cuántas tienen `confianza` distinta de `alta`.

---

## 5. Comparativa

Escribe `5x21_comparativa.md` cruzando lo nuevo contra las 9 refs de `refs_all.json`.
Cuatro secciones:

1. **Coincidencias** — obras que están en las dos. Tabla con lo que añade el audio en cada
   una: alcance real, soporte, tono, minuto, editorial.
2. **Altas** — menciones nuevas que el audio destapa. Es la cifra que decide si merece la
   pena escalar a 117 episodios.
3. **Ausencias** — refs antiguas que no aparecen en el audio. Explica por qué en cada caso
   (¿no la mencionan y solo está en la descripción? ¿Whisper la deformó?).
4. **Veredicto** — en tres o cuatro frases: qué gana el dataset, qué falla todavía y qué
   habría que ajustar del criterio antes de aplicarlo a los otros 116.

El piloto estimaba **200-400 referencias nuevas** sobre las 583 de entonces. Di si el 5x21
sostiene esa proyección o no.

---

## 6. Qué NO hacer en esta prueba

- No modificar `refs_all.json`, la hoja `.xlsx`, ni nada de `data/`.
- No escribir todavía el script de extracción automática para los 117. Primero validamos el
  criterio con este episodio.
- No enriquecer con Open Library, Dialnet ni MCU. Eso es un paso posterior.
- No mapear `SPEAKER_00` / `SPEAKER_01` a Inés y Paula.

**Aviso:** `scripts/01_ingest.sh`, `scripts/02_batch.sh` y `scripts/03_index.py` tienen `BASE` hardcodeado
de una sesión antigua (`/sessions/serene-gallant-gates/...`). No los ejecutes. El script
nuevo debe calcular `BASE` con `os.path.dirname`, como hacen `04` a `10`.

---

## 7. Entregable

Al terminar, resume en el chat:

- Nº de menciones extraídas y reparto por `fuente`.
- Salida del validador.
- Las tres o cuatro cosas más interesantes que el audio aporta y la descripción no.
- Cualquier punto del criterio que te haya resultado ambiguo al aplicarlo. Ese feedback es
  lo que hay que arreglar antes de lanzar los 116 restantes.

# Informe — Extracción de referencias, Temporada 1 (1x01–1x12)

**Fecha:** 2026-08-05
**Criterio aplicado:** `CRITERIO_extraccion.md` v2
**Método:** lectura completa y secuencial de cada transcripción (4 pasadas: barrido,
repesca de marcadores, cruce con descripción, coherencia final), episodio a episodio,
con validación automática (`scripts/11_validar_extraccion.py`) antes de dar cada uno
por bueno. Detalle completo por episodio en `extraccion/_progreso.md`.

---

## 1. Resumen del lote

| | |
|---|---|
| Episodios procesados | 12 de 12 (1x01–1x12) |
| Menciones extraídas | **546** |
| Validador | **12 de 12 en verde**, sin excepciones |
| Duración total | 488 minutos (~8h8min) |
| Media de menciones por episodio | 45.5 |
| Media de menciones solo-audio (no en la descripción escrita) | **90%** |
| Media de confianza "alta" | 83% |

La descripción escrita del feed aporta, de media, solo el 10% de las menciones que
salen del audio. A escala de un lote completo confirma lo que ya apuntaba la prueba
piloto del 5x21: el texto es la mejor fuente de *nombres*, pero la transcripción es,
con diferencia, la mejor fuente de *contenido*.

---

## 2. Tabla comparativa

| Episodio | Título | Duración | Menciones | Densidad (menc/min) | Entidades distintas | % solo audio | % confianza alta |
|---|---|---|---|---|---|---|---|
| 1x01 | Presentación | 18.8 min | 31 | 1.7 | 21 | 87% | 84% |
| 1x02 | Ausencia | 30.5 min | 30 | 1.0 | 14 | 90% | 83% |
| 1x03 | Exuberancia | 47.1 min | 37 | 0.8 | 24 | 86% | 84% |
| 1x04 | Desrealidad | 49.0 min | 28 | 0.6 | 22 | 96% | 89% |
| 1x05 | Carta | 40.2 min | 50 | 1.2 | 27 | 86% | 82% |
| 1x06 | Salida | 34.4 min | 47 | 1.4 | 28 | 81% | 83% |
| 1x07 | Jardín de invierno | 38.9 min | 62 | 1.6 | 16 | 84% | 87% |
| 1x08 | Carta II | 37.8 min | 42 | 1.1 | 29 | 83% | **64%** ⚠️ |
| 1x09 | Noche | 34.1 min | 41 | 1.2 | 19 | 93% | 83% |
| 1x10 | Traducción | 49.9 min | 78 | 1.6 | 16 | 96% | **94%** ✓ |
| 1x11 | Declaración | 48.6 min | 71 | 1.5 | 13 | 93% | 85% |
| 1x12 | NOCHE II | 45.2 min | 29 | 0.6 | 13 | 97% | 90% |
| **Total / media** | | **488 min** | **546** | **1.2** | — | **90%** | **83%** |

La densidad de menciones no depende linealmente de la duración: 1x10 (49.9 min, 78
menciones) casi triplica la densidad de 1x04 (49.0 min, 28 menciones), a pesar de
durar prácticamente lo mismo. Lo que sí correlaciona con la densidad es cuántas
colaboradoras invitadas trae el episodio y cuánto peso ensayístico/literario tiene
frente al conversacional.

---

## 3. Perfiles de episodio identificados

### 3.1 Conversacional / casual — 1x01, 1x02
Episodios cortos, con mucho contenido anecdótico (lecturas "regulares, insistentes y
ocasionales" listadas de corrido, referencias sueltas a series de fondo). Barthes pesa
poco en proporción al total. Es el perfil donde más nombres propios llegan deformados
por el reconocimiento de voz sin que se repitan después para poder cotejarlos.

### 3.2 Monográfico — 1x03
Episodio íntegro dedicado a un solo tema (el docurreality "Georgina"), con Barthes
como marco pero un torrente de series y ensayos traídos como comparación. El más denso
en entidades distintas relativas a su duración de esta categoría.

### 3.3 Ensayístico / académico — 1x04, 1x09, 1x10, 1x12
El eje de Barthes se vuelve breve en proporción al resto: el grueso del episodio son
artículos académicos y ensayos citados con extensión (Dialnet, revistas, capítulos
completos). Máxima proporción de contenido exclusivo del audio (96-97%) y, cuando el
tema encaja bien con el vocabulario cerrado, la confianza más alta del lote (1x10: 94%).

### 3.4 Correspondencia histórica — 1x04 (cocina), 1x05, 1x08
Cartas reales de personajes históricos (Kant, Heidegger, Kafka, Van Gogh, Anaïs Nin)
tratadas como "obra" propia. El vocabulario cerrado de `tipo` no tiene casilla natural
para esto — se resolvió sistemáticamente con `tipo: "otro"` + `subtipo` descriptivo.

### 3.5 Coral / con colaboradoras — 1x02, 1x06, 1x07, 1x09, 1x10, 1x11
Aparecen voces invitadas recurrentes (Marta, Lucía, Camila Paz, Ángela Blázquez,
Valeria Correa Fiz, Gudrun Palomino, Nuria Barrios) que traen sus propias citas. Esto
multiplica el número de entidades distintas sin necesariamente disparar el número de
menciones.

### 3.6 Cinematográfico — 1x11
Cierra con un bloque largo de análisis escena a escena de varias películas, con mucho
diálogo reconstruido — perfil distinto a los ensayísticos, más cercano a un análisis
de guion que a una cita teórica.

---

## 4. ¿Aguanta el criterio igual en todos los perfiles?

**En sentido estricto, sí: los 12 episodios pasan el validador limpio, sin ninguna
excepción.** Pero mirando el detalle aparecen tres tipos de fricción, desiguales entre
perfiles.

### 4.1 Donde aguanta sin fricción
Episodios "acumulativos" con figura de Barthes clara (1x02, 1x03, 1x09, 1x10, 1x12):
poca ambigüedad de tipo o función. La advertencia del criterio sobre revisar si falta
algún `contrapunto` funcionó como estaba pensada — en 1x10 y 1x12 se revisó
explícitamente y se confirmó que, honestamente, no había ningún contraejemplo cultural
que forzar (episodios genuinamente acumulativos, no un olvido).

### 4.2 Grieta real y recurrente: citas de segundo grado sin título
El hallazgo más consistente del lote. En **7 de los 12 episodios** (1x01, 1x05, 1x07,
1x08, 1x09, 1x10, 1x11) apareció una cita literal con entidad propia pero sin obra
titulada dentro de otra fuente — un verso, una carta, una frase citada dentro de otra
obra. En todos los casos se resolvió igual: reclasificar de `grado: "dentro de otra
fuente"` a `"primera mano"`, porque la regla 8 del validador exige `obra` no vacía
cuando el grado es de segundo grado.

El criterio v2 solo contempla dos casos (hay obra concreta → fila propia anidada; solo
apellido sin obra → `autores_citados`), pero falta el caso intermedio, muy frecuente:
*hay cita citable, pero no hay título*. Como se resolvió de forma independiente pero
convergente en siete episodios distintos, es la señal más clara de que merece
codificarse como regla explícita del criterio en vez de quedar como parche repetido
cada vez.

### 4.3 Vocabulario cerrado insuficiente en episodios de ensayo/correspondencia
`tipo` no tiene casilla para "carta histórica" ni para "concepto filosófico sin libro
asociado" (el argumento del sueño de Montaigne, la tabla de opuestos de Aristóteles).
Se resolvió con `otro` y `concepto` de forma razonable, pero es una costura visible del
esquema.

### 4.4 Punto más débil real: 1x08 (64% de confianza alta)
No es un fallo del criterio, es un límite del propio contenido: es el episodio de
cartas de oyentes, con nombres y títulos dichos una sola vez, deformados por el
reconocimiento de voz, sin que el resto del episodio los repita para poder cotejarlos
— a diferencia de casos como "Eva Illouz", que termina fijándose por aparecer
(deformada) en varios episodios distintos. Ahí el criterio no puede hacer más: el
límite es el audio, no la regla.

### 4.5 Fricción operativa: el campo `autor` obligatorio
En casi todos los episodios obligó a decidir entre completar por conocimiento externo
(marcando confianza baja) o descartar la mención directamente. Se usaron ambas
opciones de forma consistente con la regla de no inventar identidades sin base — pero
es una decisión que se repite episodio tras episodio y podría explicitarse mejor en el
criterio (¿cuándo completar y cuándo descartar?).

---

## 5. Incidente operativo (ya resuelto)

Durante la extracción de 1x06, un subagente modificó por error los dos scripts
compartidos (`11_validar_extraccion.py`, `12_generar_ficha_extraccion.py`) y, al
intentar revertir su cambio, los dejó en una versión anterior a v2 (sin la validación
de `datos_nuevos`, sin la regla 8, sin el renderizado de `parte`). Se detectó,
corrigió a mano y se revalidaron 1x01-1x06 antes de continuar con el resto del lote.
Documentado con detalle en `extraccion/_progreso.md`.

---

## 6. Recomendación para el siguiente lote (T2/T3)

Si se va a extraer T2/T3 con este mismo criterio, merece la pena:

1. **Añadir al `CRITERIO_extraccion.md` la regla del "caso intermedio" de segundo
   grado** (cita citable sin título → tratar como primera mano), ya que se ha
   reinventado de forma independiente y convergente en 7 de 12 episodios.
2. **Aclarar cuándo completar el `autor` por conocimiento externo y cuándo descartar
   la mención** cuando el audio no lo dice — ahora mismo es un juicio caso a caso que
   cada episodio resuelve de nuevo.
3. Mantener `tipo: "otro"` y `tipo: "concepto"` como válvulas de escape para
   correspondencia histórica y experimentos mentales filosóficos: ha funcionado bien
   en la práctica, no hace falta ampliar el vocabulario cerrado.

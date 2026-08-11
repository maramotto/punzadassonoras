# Informe — Extracción de referencias, Temporada 5 (5x01–5x21)

**Fecha:** 2026-08-11
**Criterio aplicado:** `CRITERIO_extraccion.md` v2
**Método:** lectura completa y secuencial de cada transcripción (4 pasadas: barrido,
repesca de marcadores, cruce con descripción, coherencia final), episodio a episodio,
con validación automática (`scripts/11_validar_extraccion.py`) antes de dar cada uno
por bueno, más una verificación independiente del validador desde la conversación
principal (no solo del reporte del subagente que hizo la extracción). Detalle completo
por episodio en `extraccion/_progreso.md`. El 5x21 —episodio piloto del criterio,
hecho en v1 el 2026-08-03— se re-extrajo íntegramente a v2 para que el lote quedara
homogéneo.

---

## 1. Resumen del lote

| | |
|---|---|
| Episodios procesados | 21 de 21 (5x01–5x21) |
| Menciones extraídas | **1.163** |
| Validador | **21 de 21 en verde**, sin excepciones |
| Duración total | 1.494,5 minutos (~24h 55min) |
| Media de menciones por episodio | 55,4 |
| Media de menciones exclusivas del audio (`fuente: "audio"`) | **87,4%** |
| Menciones que aparecen solo en la descripción (`fuente: "descripción"`) | **0** — ninguna, en ningún episodio |
| Media de confianza "alta" | 84,6% |
| Entidades (autores) distintas, total del lote | 273 |
| Correcciones aplicadas tras revisión independiente | 3 (ver §5) |

El hallazgo más marcado del lote frente a T1: en T1 la descripción escrita aportaba
de media un 10% de las menciones que no estaban en el audio. **En T5 esa cifra es
cero en los 21 episodios** — no hay ni una sola mención que solo esté en la
descripción oficial. Esto no significa que la descripción sea inútil (sigue sirviendo
para contrastar nombres y detectar erratas), pero sí confirma que, para T5, todo lo
que aparece en la descripción también se dice en el audio; el aporte real del texto
escrito está en la ortografía de los nombres propios, no en referencias nuevas.

---

## 2. Tabla comparativa

| Episodio | Título | Duración | Menciones | Densidad (menc/min) | Entidades distintas | % nuevas vs. descripción | % confianza alta |
|---|---|---|---|---|---|---|---|
| 5x01 | Hacerse cargo, mirarse a los ojos | 70,2 min | 77 | 1,10 | 16 | 56% | 82% |
| 5x02 | En defensa de lo breve | 70,0 min | 51 | 0,73 | 27 | 85% | 84% |
| 5x03 | La voyeur: un baile de miradas | 66,7 min | 45 | 0,67 | 17 | 41% | 84% |
| 5x04 | La familia: cárcel y refugio | 83,0 min | 66 | 0,79 | 16 | 50% | 80% |
| 5x05 | Sacrificio: ritual, ascesis, violencia | 71,7 min | 52 | 0,73 | 17 | 59% | 71% |
| 5x06 | Saberlo todo del otro | 73,7 min | 75 | 1,02 | 15 | 60% | 81% |
| 5x07 | Incidentes: Barthes y la homosexualidad | 80,6 min | 76 | 0,94 | 17 | 53% | 79% |
| 5x08 | Hacer hablar al mundo | 76,2 min | 52 | 0,68 | 18 | 67% | 77% |
| 5x09 | Compasión: me duele el otro | 65,0 min | 70 | 1,08 | 19 | 74% | 87% |
| 5x10 | Las tonalidades del silencio | 68,8 min | 72 | 1,05 | 12 | 58% | 90% |
| 5x11 | Márgenes silentes | 63,2 min | 46 | 0,73 | 26 | 73% | 78% |
| 5x12 | Quien teme morir ya está muerto de miedo | 68,7 min | 70 | 1,02 | 6 | 33% | 91% |
| 5x13 | La culpa: asesinar, imaginar, sobrevivir | 70,5 min | 61 | 0,87 | 7 | 29% | 93% |
| 5x14 | Patrimonio: formar parte, darle vida | 71,2 min | 62 | 0,87 | 8 | 62% | 90% |
| 5x15 | Decir el mar | 59,8 min | 57 | 0,95 | 23 | 74% | 95% |
| 5x16 | ¿Qué sujeto puede permitirse morir? | 72,2 min | 65 | 0,90 | 15 | 53% | 83% |
| 5x17 | Pensar el museo (live) | 72,3 min | 32 | 0,44 | 17 | 59% | 91% |
| 5x18 | El grano de la voz | 63,6 min | 34 | 0,53 | 12 | 58% | 79% |
| 5x19 | Un imaginario rural | 78,7 min | 37 | 0,47 | 11 | 45% | 97% |
| 5x20 | El valor de la crueldad | 82,8 min | 36 | 0,43 | 19 | 79% | 78% |
| 5x21 | Dejar de amar: la ruptura amorosa (re-extraído a v2) | 65,4 min | 27 | 0,41 | 13 | 31% | 81% |
| **Total / media** | | **1.494,5 min** | **1.163** | **0,78** | — | **58%** | **85%** |

"% nuevas vs. descripción" mide cuántas de las entidades detectadas en el audio no
aparecían ya en la extracción previa solo-texto de `refs_all.json` (columna `refs` de
cada episodio). Es distinta de la "% exclusiva del audio" del §1 (que mide menciones,
no entidades): aquí se compara contra el trabajo de extracción anterior del proyecto,
no contra la descripción oficial en bruto.

La densidad no depende de la duración: 5x17 y 5x20-5x21 son los episodios menos
densos (0,4-0,5 menc/min) pese a estar entre los más largos o de duración media,
mientras que 5x01 y 5x09 superan 1,0 menc/min con duraciones similares a la mediana.

---

## 3. Perfiles de episodio identificados

### 3.1 Ensayístico-denso — 5x01, 5x02, 5x07, 5x08
Episodios de arranque de bloque teórico, con mucha cita académica encadenada y varios
niveles de segundo grado (artículos que citan artículos que citan libros). Es el
perfil donde más se activa la regla de `autores_citados` frente a fila propia: 5x02
tuvo que resolver hasta tres capas de cita anidada (Hui → Hegel/Platón/Kant/Foucault
con `via`; Heráclito/Pascal/Nietzsche sin obra, fuera de fila).

### 3.2 Monográfico sobre una obra ajena "vista, no leída" — 5x09, 5x10, 5x15, 5x21
El episodio gira en torno a una obra que las presentadoras acaban de terminar o están
terminando (Maillard en 5x09, varias novelas/películas del mar en 5x15, *Fragmentos*
por bloques en 5x21). Máxima proporción de confianza alta del lote (90-97%) porque
los nombres se repiten y se fijan a lo largo del episodio.

### 3.3 Baja densidad de entidades, alta cohesión temática — 5x12, 5x13, 5x14
Episodios apoyados en 2-4 fuentes bibliográficas que se citan una y otra vez en vez
de acumular referencias nuevas (6-8 entidades distintas frente a las 15-27 de otros
perfiles). Correlaciona con la confianza más alta del lote (90-93%): pocos nombres,
repetidos muchas veces, se transcriben mejor. El 5x13 es el caso extremo — **el único
episodio de las cinco temporadas revisadas hasta ahora sin ninguna mención de
Barthes**, confirmado por el barrido completo, no un descuido.

### 3.4 En directo / formato especial — 5x17
Único episodio en directo del lote (Feria del Libro, con público). Densidad más baja
de todo T5 (0,44 menc/min) porque buena parte del tiempo es interacción con el
público y presentaciones, no contenido citable. Aparece aquí el único caso de "autor
institucional" del lote sin precedente (`autor: "Museo La Casa de Carta"`), repetido
después en 5x20 (`autor: "HBO"` para *Sharp Objects* sin creador nombrado) — ver §4.3.

### 3.5 Coral / con voces citadas de segundo grado ricas — 5x02, 5x11, 5x15
Máxima proporción de entidades distintas relativas a la duración (23-27 entidades):
5x02 por la cadena de citas académicas, 5x11 por la paráfrasis extensa de un TFM
ajeno, 5x15 por el desfile de autoras y poetas del mar. Es el perfil con más fricción
en la frontera `grado: "primera mano"` vs. `"dentro de otra fuente"` (ver §4.1).

---

## 4. ¿Aguanta el criterio igual en todos los perfiles?

**En sentido estricto, sí: los 21 episodios pasan el validador limpio.** Pero, a
diferencia de T1 (que no tuvo que corregir nada tras la extracción), en T5 se
detectaron y corrigieron **tres violaciones reales de la regla "no se completa lo no
dicho"** que el validador automático no puede pillar por no ser un problema de cita
literal, sino de contenido inventado con una cita literal válida alrededor. Es la
grieta más seria que ha aparecido hasta ahora en el criterio.

### 4.1 Grieta nueva y seria: "no completar" es más difícil de cumplir de lo que parece
Se encontraron y corrigieron tres casos donde el subagente rellenó un dato con
conocimiento externo en vez de dejarlo vacío:

- **5x18-001**: `obra: "Roland Barthes"` para la biografía de Samoyault, cuando el
  audio solo dice «la biografía de Tiffany Samoyold» sin título. Corregido a
  `obra: ""`, `alcance: "solo el autor"`.
- **5x19-015**: `autor: "Los puentes de Madison"` (el título de la película metido en
  el campo autor, porque no se nombra director ni autor de la novela). Corregido a
  `autor: "desconocido"`, `obra: "Los puentes de Madison"`.
- **5x21-017/016** (*Jane Eyre*, *Persuasión*): autoría (Brontë, Austen) añadida sin
  que el audio la diga, solo el título (deformado). **Este caso se dejó tal cual**,
  a diferencia de los otros dos, por una razón distinta: aquí el título SÍ se
  pronuncia (aunque deformado), y solo se completa la autoría de una obra canónica
  inequívoca — más cerca de normalización bibliográfica que de invención de
  contenido — y porque es precisamente el ejemplo ya documentado y aprobado en
  `CLAUDE.md` como hallazgo fundacional del piloto. Es una distinción defendible,
  pero el hecho de que el mismo patrón produjera tres decisiones distintas en tres
  episodios distintos es la prueba de que la regla necesita un ejemplo explícito de
  "autor conocido pero no dicho" en el criterio, con el mismo nivel de detalle que ya
  tiene el ejemplo de Cavarero para "obra no dicha".

**Recomendación concreta**: añadir a `CRITERIO_extraccion.md` §4 un apartado
específico para el caso inverso al de Cavarero — título dicho, autor no dicho — con
una regla explícita de cuándo se permite la normalización (autoría inequívoca de
dominio público, un único candidato razonable) y cuándo no (biografías, ensayos o
artículos que podrían tener varios títulos plausibles para la misma descripción).

### 4.2 Grieta ya conocida de T1, reaparece igual: segundo grado con desarrollo pero sin obra
Igual que en T1 (7 de 12 episodios), en T5 aparece el caso intermedio no contemplado
por el criterio: hay desarrollo y cita citable, pero no hay título. En 5x15 se
resolvió dando fila propia (`grado: "primera mano"`, `alcance: "solo el autor"`) en
vez de fundir en `autores_citados`, criterio que coincide con el usado en T1. Sigue
siendo la señal más repetida de que el criterio necesita esta tercera categoría
explícita entre "segundo grado con obra" y "apellido suelto sin más".

### 4.3 Grieta nueva, menor: autor institucional cuando no hay persona física
Dos casos en el lote (5x17: "Museo La Casa de Carta"; 5x20: "HBO" para *Sharp
Objects* sin creador nombrado) usan una institución como valor de `autor` porque el
campo es obligatorio y no hay ninguna persona citada. Es una solución razonable y sin
precedente explícito en el criterio; conviene decidir si se acepta como norma o si
esas filas deberían descartarse (igual que se descartó *Turandot* en 5x18 por la
misma razón, con el criterio inverso).

### 4.4 Caso límite ya señalado en el propio lote: menciones tangenciales de club de lectura
Detectado explícitamente durante la extracción (no en revisión posterior): en 5x01,
la mención al club de lectura de Proust se incluyó como mención de pasada legítima
(precedente ya usado también en 1x02, según sus notas de T1). En 5x09, en cambio, el
agente **excluyó** una mención equivalente (*Crimen y Castigo* de Dostoyevski,
también anécdota de club de lectura) razonando que "no aporta autor/obra en sentido
bibliográfico propio del podcast" — inconsistencia real frente al precedente de 5x01,
señalada por el propio agente en su reporte. A partir de ese hallazgo se añadió una
instrucción explícita a los prompts de los lotes siguientes ("incluye siempre
menciones tangenciales si hay autor y obra identificables"), lo que probablemente
explica por qué no se repitió en los lotes 4-6. Sigue sin corregirse retroactivamente
en 5x09 — pendiente de decisión: ¿se reabre esa fila o se deja como está, documentada?

### 4.5 Donde aguanta sin fricción
Los episodios del perfil 3.2 y 3.3 (5x09, 5x10, 5x12, 5x13, 5x14, 5x15) son los que
menos fricción dieron: pocas fuentes, mucho desarrollo, `contrapunto` fácil de
identificar cuando existe y fácil de descartar honestamente cuando no (5x05, con un
matiz «más débil que en otros episodios», documentado como tal en vez de forzado).

### 4.6 Vocabulario cerrado: sin sorpresas nuevas
A diferencia de T1 (que necesitó resolver "carta histórica" y "concepto filosófico
sin libro"), T5 no encontró ningún valor de `tipo` que no encajara ya en el
vocabulario existente, salvo el ya conocido de "ensayo"/"ópera" (resuelto con
`subtipo`, mismo patrón que en T3-T4).

---

## 5. Correcciones aplicadas durante la revisión

Todas las correcciones de este informe se hicieron **después** de que el validador
automático diera cada episodio por bueno — el validador no detecta contenido
completado con cita literal válida alrededor, solo detecta citas no literales o
incoherencias de rango/vocabulario. Las tres correcciones (§4.1) se aplicaron a mano
sobre los JSON, se regeneraron las fichas `.md` con `12_generar_ficha_extraccion.py`
y se re-validó cada episodio tras el cambio. Ninguna requirió tocar el validador.

---

## 6. Estado del dataset T5

Los 21 episodios de temporada 5 están en `podcast-data/extraccion/5x01.json` …
`5x21.json`, con sus fichas `.md` generadas, todos con `criterio: "v2"`. El histórico
completo de decisiones episodio a episodio está en `extraccion/_progreso.md`. Este
lote deja pendientes, para la fase de fundido con `refs_all.json` o para una revisión
posterior del propio criterio: los §4.1, 4.3 y 4.4 de este informe.

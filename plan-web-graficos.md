# universopunzadas.com — plan de estructura, buscadores y gráficos

Versión 2 · 19 de agosto de 2026 · sustituye a la anterior

Repositorio de trabajo: **`github.com/maramotto/punzadassonoras`**
(el repo `punzadas-sonoras-referencias` es la versión antigua, con 66 episodios y
referencias sacadas solo de las descripciones de YouTube; no se usa).

---

## 1. Los datos, a 19 de agosto de 2026

Todo lo que sigue está contado sobre `podcast-data/extraccion/*.json`, no estimado.

| | |
|---|---|
| Episodios en el catálogo | 118 |
| Episodios con extracción | **104** (T1–T5 completas) |
| Menciones | **5.596** — 5.592 con segundo exacto |
| Autoras y autores distintos | 1.109 |
| Obras distintas | 1.224 (1.317 pares autor + obra) |
| Horas de audio | 103,9 |
| Temas curados | **37**, media de 3,7 por episodio (solo el 5x22 se ha quedado sin tema) |
| Menciones con `parte` | 885, de las cuales **375 son figuras de *Fragmentos de un discurso amoroso*** (60 figuras distintas) |
| Menciones con `en_dialogo_con` | 902 |
| Menciones con `datos_nuevos` | 394 (editorial dicha en voz alta en el propio episodio) |
| Episodios con vídeo en YouTube | **58 de los 104 extraídos** |

**Facetas disponibles y su reparto real**

| Campo | Valores | Reparto |
|---|---|---|
| `tipo` | 12 | libro 3.420 · artículo 629 · persona 536 · otro 253 · película 212 · concepto 165 · serie 103 · obra de arte 72 · podcast 63 · poema 54 · música 47 · teatro 42 |
| `funcion` | 6 | apoyo teórico 3.038 · eje del episodio 1.020 · mención de pasada 627 · ejemplo 451 · recomendación 275 · contrapunto 185 |
| `tono` | 4 | entusiasta 2.696 · neutro 2.346 · crítico 444 · ambivalente 110 |
| `soporte` | 5 | leído 3.894 · sin determinar 704 · citado de oídas 488 · visto 368 · escuchado 142 |
| `alcance` | 4 | un pasaje o cita 3.159 · obra completa 1.258 · solo el autor 891 · un capítulo o figura 288 |
| `grado` | 2 | primera mano 5.371 · dentro de otra fuente 225 |
| `confianza` | 3 | alta 4.702 · media 800 · baja 94 |

**Grafo de `en_dialogo_con`**, normalizando títulos: 747 nodos, 714 aristas,
127 componentes. El componente gigante tiene 393 obras; hay 26 componentes de 4 o más
nodos que reúnen 515 obras. Las otras 232 obras quedan en 101 grupitos de dos o tres — se
dice en la nota del gráfico, no se esconde.

**Enriquecimiento externo, lo que hay de verdad**: 253 entradas en el cache de OpenLibrary,
de las cuales **139 traen año de primera edición**; 43 resultados útiles del MCU y 42 de
Dialnet. Sobre 1.317 obras, es cobertura baja. Decisión tomada: **se muestra lo que hay y
no se promete lo que no hay** — nada de ordenar por año ni de gráficos cronológicos de obra.

**Tamaño del índice para el navegador**: el `index.json` con las 5.596 menciones y sus citas
literales pesa **780 KB en crudo, 280 KB comprimido**. Cabe entero en el cliente. Esto
condiciona toda la arquitectura para bien: **no hace falta servidor, ni API, ni paginación
remota. Se carga una vez y todo lo demás es instantáneo.**

---

## 2. Las ocho decisiones, ya tomadas

1. **Portada = mapa visual.** Al entrar se ve la matriz temas × episodios a pantalla
   completa, con el buscador en la barra superior.
2. **La matriz de portada es temas (filas) × episodios (columnas)**, celda pintada si el
   episodio trata ese tema e **intensidad según el número de menciones del episodio**.
3. **El buscador devuelve cuatro pestañas** sobre la misma consulta: Autoras · Obras ·
   Menciones · Episodios, con el recuento en cada una.
4. **Audio: enlaces con marca de tiempo donde los haya** (58 episodios llevan a YouTube en
   el segundo exacto) y **el minuto escrito donde no** (los otros 46, T1 y T2 completas).
   Sin reproductor propio, sin usar el mp3 de Megaphone.
5. **Se publica con los 118 episodios**: primero se extraen los 14 que faltan, luego se
   lanza. No hay versión parcial.
6. **Navegación por tema, por tipo de obra, por temporada y por figura de Barthes**, además
   de autoría, obra y episodio.
7. **Enriquecimiento**: se muestra el año y la editorial cuando existen, y punto.
8. **Dominio**: universopunzadas.com, ya registrado. **Sin página de descarga de datos**:
   la web se consulta, no se exporta.

---

## 3. Mapa de la web

```
/                      Portada. Matriz temas × episodios a pantalla completa.
                       Buscador en la barra. Cuatro contadores. Nada más.
/buscar                Buscador con las cuatro pestañas. Estado en la query string.
/explorar              Los gráficos, todos contra la misma barra de filtros.
/episodio/[codigo]     Ficha de episodio: regleta de tiempo con las marcas, temas,
                       lista de menciones con su cita, enlace a YouTube si lo hay.
/autor/[slug]          1.109 páginas. Obras citadas, episodios, evolución, citas.
/obra/[slug]           1.224 páginas. Menciones, partes citadas, con qué dialoga,
                       año y editorial si los tenemos.
/tema/[slug]           37 páginas. Episodios del tema y lo que se cita en ellos.
/figura/[slug]         60 páginas, una por figura de «Fragmentos de un discurso amoroso».
/tipo/[slug]           12 páginas: todas las películas, todos los poemas, etc.
/temporada/[n]         5 temporadas + especiales + Las Glosas.
/sobre                 Qué es esto, cómo se ha hecho, criterio de extracción, aviso.
```

Regla de oro que atraviesa todo: **una sola barra de filtros, pegajosa arriba, y todos los
gráficos y tablas de la página se re-renderizan contra la misma porción de datos.** Nunca
un filtro dentro de la tarjeta de un gráfico. El estado vive en la query string, así que
cualquier vista es un enlace que se puede mandar por WhatsApp.

---

## 4. El buscador

**Una consulta, cuatro respuestas.** Escribes «Ernaux» y ves de un golpe:

```
Autoras (1)   Obras (23)   Menciones (236)   Episodios (36)
```

(Las cuatro cifras son las reales de Annie Ernaux en el archivo de hoy.)

- **Autoras** — ficha compacta: nombre, número de menciones, número de obras, temporadas en
  las que aparece, una sparkline de su presencia por episodio.
- **Obras** — título, autoría, tipo, número de menciones, año y editorial si los tenemos.
- **Menciones** — el resultado más fino: la cita literal con el término resaltado, el
  episodio, el minuto, y las etiquetas de tono y función. Es la pestaña que justifica todo
  el proyecto.
- **Episodios** — título, fecha, temas, cuántas menciones tiene y cuántas casan con la
  búsqueda.

**Cómo se implementa.** Se carga `index.json` una vez (280 KB comprimidos) y se construye el
índice de Orama en un Web Worker al arrancar. Sobre 5.596 documentos tarda unas décimas y
libera el hilo principal. Se indexan `obra`, `autor`, `parte`, `cita`, `contexto` y
`titulo_episodio`, con tolerancia a erratas (`tolerance: 1`) y sin acentos. Las otras tres
pestañas se calculan agregando los resultados de menciones más una búsqueda directa sobre
las listas de autores, obras y episodios, que son minúsculas.

**Facetas de la barra de filtros**, en este orden y todas multiselección:

```
temporada · tema · tipo · función · tono · soporte · alcance · confianza
```

Con `funcion` = «eje del episodio» se separa lo central de lo anecdótico: es el mejor filtro
de calidad que tiene el archivo y conviene que esté a la vista, no escondido.

Al lado del buscador, siempre, el contador: **«1.240 de 5.596 menciones»** y los chips de los
filtros activos, cada uno con su aspa.

---

## 5. Los gráficos

Siete, en este orden de importancia.

**1. Matriz temas × episodios — la portada.**
37 filas (temas) × 118 columnas (episodios, en orden cronológico). Celda pintada si el
episodio lleva ese tema; intensidad por número de menciones del episodio, escala raíz para
que los episodios densos no aplasten al resto. Rampa secuencial de un solo tono. Cabecera
con las bandas de temporada, clicables. Filas ordenadas por primera aparición, no por
frecuencia: así se ve el podcast abrir temas nuevos con el tiempo. Hover en la celda:
título, fecha, temas, número de menciones. Clic: va al episodio. Clic en el nombre de la
fila: va al tema.

**2. Regleta del episodio.**
Sustituye a la forma de onda del plan anterior, que ya no tiene sentido sin reproductor.
Es una barra horizontal de 0 a la duración del episodio, con una marca fina por cada
`inicio_s`. Color de la marca por tono. Hover: la cita literal. Clic: abre YouTube en ese
segundo, o copia «1x04 · 12:34» al portapapeles si el episodio no tiene vídeo. Va en cada
ficha de episodio y en miniatura en las tarjetas de episodio del buscador.

**3. Pulso — fecha × minuto.**
Dispersión de las 5.592 menciones con hora: eje X la fecha del episodio, eje Y el minuto
dentro del episodio, color por tono con paleta divergente (entusiasta ↔ crítico, gris en
medio). Se ve que los episodios se alargan por temporada y que el tono crítico aparece a
partir de la T3. Brush vertical para filtrar por tramo de minutos.

**4. Grafo de obras en diálogo.**
sigma.js + graphology sobre las 902 menciones con `en_dialogo_con`. Se dibujan los 26
componentes de 4 o más nodos (515 obras); las 232 parejas sueltas quedan fuera y la nota al
pie lo dice. ForceAtlas2, etiquetas solo en los nodos de mayor grado y con evasión de
colisiones. Clic en un nodo: ficha de obra.

**5. Matriz autoría × episodio.**
La del plan anterior, ahora en `/explorar` y no en portada: 24 autoras más citadas × 118
episodios, escala raíz para que Barthes (794 menciones) no aplaste el resto.

**6. Área apilada por tipo.**
libro / artículo / persona / película / otros a lo largo de los 118 episodios, con las
temporadas marcadas.

**7. Tabla con la cita literal.**
TanStack Table virtualizada. El gemelo accesible de todo lo anterior y, en la práctica, la
vista que más se usa.

**Restricciones de diseño, no negociables:**

- Máximo 8 colores categóricos, asignados en orden fijo. **El color sigue a la entidad, no a
  su posición en el ranking**: filtrar no puede repintar a los supervivientes.
- Nunca dos ejes Y en el mismo gráfico.
- Rampa secuencial de un solo tono, claro a oscuro. Nada de arcoíris.
- Marcas finas; rejilla y ejes a un pelo; sin líneas discontinuas.
- Leyenda siempre presente con dos o más series; etiquetas directas solo en los extremos.
- Cada gráfico tiene su equivalente en tabla.
- Tooltip en hover y **el mismo contenido accesible con foco de teclado**.
- Modo oscuro por defecto, con conmutador.

---

## 6. Stack

| Pieza | Elección |
|---|---|
| Base | Astro 5, salida estática, TypeScript |
| Islas interactivas | React (solo donde hace falta: tabla, grafo, matrices) |
| Buscador | Orama en cliente, índice construido en un Web Worker |
| Gráficos | Observable Plot |
| Grafo | sigma.js + graphology |
| Tabla | TanStack Table + virtualización |
| Hosting | Cloudflare Pages, build desde el repo, dominio universopunzadas.com |

Nada en tiempo de ejecución: un paso de build lee `podcast-data/extraccion/*.json` y escribe
`web/public/data/*.json`. Cero peticiones a servicios externos desde el navegador.

---

## 7. Lo que hay que arreglar antes de tocar la web

Dos cosas bloquean, y las dos son de datos, no de diseño.

**a) Los identificadores no cuadran.** 13 episodios extraídos (3x03, 3x13, 3x17, 3x21, 4x03,
4x08, 4x16, 4x19, 5x11, 5x13, 5x14, 5x17, 5x18) no tienen entrada en
`data/manifiesto_audio.json`, y 27 entradas del manifiesto —los especiales y Las Glosas—
tienen el campo `codigo` vacío. Si esto no se reconcilia, habrá episodios sin enlace ni
metadatos por un fallo de cruce, no por falta de datos.

**b) Faltan 14 episodios por extraer** para llegar a los 118, y se ha decidido publicar con
todo. Son las Glosas, los especiales y el 5x22.

Y tres cosas que no bloquean pero que la web va a poner a la vista de todo el mundo, así que
conviene arreglarlas antes:

- **227 menciones tienen `autor: "desconocido"`**. Es el tercer «autor» más frecuente del
  archivo. En la web no puede aparecer como si fuera una persona: hay que tratarlo como
  ausencia de dato y dejarlo fuera de rankings y de la página de autoría.
- **Títulos duplicados por variantes de escritura.** Por ejemplo *Los años de Super 8* y
  *Los años del súper 8* conviven como dos obras distintas de Ernaux. El script de build
  tiene que unificar por título normalizado, y hay que revisar a mano la lista de fusiones
  que proponga.
- **Alguna atribución cruzada.** *La distinción* aparece atribuida a Annie Ernaux cuando es
  de Bourdieu. Merece una pasada de control antes de publicar 1.109 páginas de autoría.

---

## 8. Comandos para Claude Code

Desde la raíz de `punzadassonoras`, uno por uno, revisando entre pasos.

### Paso 0 — reconciliar identificadores

```
Hay un desajuste de identificadores entre ficheros del repo que hay que resolver antes
de construir nada.

1. Cruza podcast-data/extraccion/*.json (104 episodios, campo "codigo") con
   podcast-data/data/manifiesto_audio.json (118 entradas) y con
   podcast-data/data/refs_all.json (117 entradas). Enséñame una tabla con:
   - episodios extraídos sin entrada en el manifiesto (deberían ser 13)
   - entradas del manifiesto con "codigo" vacío (deberían ser 27)
   - episodios del manifiesto sin extracción (deberían ser 14)
   No cambies nada todavía.

2. Propón un identificador único y estable para TODOS los episodios, incluidos los
   especiales y Las Glosas, que hoy no tienen código de temporada. Mi preferencia es
   usar el slug de fecha + título que ya existe en el manifiesto ("2023-10-19_islas-
   anomalias-fragmentarias"), manteniendo "codigo" como campo aparte y opcional.
   Explícame la propuesta antes de aplicarla.

3. Cuando la apruebe, escribe podcast-data/scripts/13_reconciliar_ids.py que aplique el
   identificador a los tres ficheros de forma idempotente, guarde una copia .bak de cada
   uno y termine imprimiendo un resumen. Añade un test que compruebe que después de
   correrlo todo episodio del manifiesto tiene identificador único y que toda extracción
   casa con exactamente una entrada del manifiesto.
```

### Paso 1 — extraer los 14 episodios que faltan

```
Faltan por extraer 14 episodios (Las Glosas, los especiales y el 5x22). Usa el
procedimiento del bloque B de PROMPTS_claude_code.md y el criterio de
CRITERIO_extraccion.md, sin cambiar el criterio.

Hazlo de tres en tres, y después de cada tanda:
- corre podcast-data/scripts/11_validar_extraccion.py sobre los nuevos ficheros
- enséñame el recuento de menciones de cada uno y las que hayan quedado con
  confianza "baja", para que las revise antes de seguir

No pases a la siguiente tanda sin que te lo confirme.
```

### Paso 1b — control de calidad del archivo

```
Antes de generar nada para la web, escribe podcast-data/scripts/15_qa_archivo.py que
recorra todas las extracciones y me saque un informe en Markdown con:

1. Todos los pares de títulos de obra que normalizados coinciden pero se escriben
   distinto (minúsculas, tildes, puntuación, "Super 8" vs "súper 8"), con el número de
   menciones de cada variante, para que yo decida cuál se queda.
2. Las obras atribuidas a más de una autoría, y las autorías con obras que probablemente
   no son suyas. Ordénalas por número de menciones.
3. Las 227 menciones con autor "desconocido", agrupadas por obra, para ver cuáles se
   pueden completar y cuáles no.
4. Las menciones con confianza "baja" (94), con su cita y su episodio.
5. Nombres de autoría que se parecen mucho entre sí (distancia de edición pequeña), que
   suelen ser la misma persona transcrita de dos maneras.

Solo el informe. No corrijas nada automáticamente: lo reviso yo y luego decidimos qué
correcciones aplicar y sobre qué fichero.
```

### Paso 2 — los datos de la web

```
Escribe podcast-data/scripts/14_build_web_data.py que lea podcast-data/extraccion/*.json,
podcast-data/data/refs_all.json (temas), podcast-data/data/manifiesto_audio.json y los
caches de enriquecimiento (cache_openlibrary.json, cache_mcu.json, cache_dialnet.json),
y genere en web/public/data/:

- index.json → todo lo que necesita el cliente para filtrar y buscar, con las cadenas
  repetidas indexadas por posición:
  {
    eps:  [[id, codigo, titulo, fecha, duracion_s, temporada, video_id, [temaIdx...]]],
    aut:  [nombres], obr: [titulos], par: [partes],
    tip: [], fun: [], ton: [], sop: [], alc: [], temas: [],
    refs: [[epIdx, autIdx, obrIdx, parIdx, tipIdx, funIdx, tonIdx, sopIdx, alcIdx,
            inicio_s, cita]]
  }
  Objetivo de tamaño: por debajo de 1 MB sin comprimir. Con los datos actuales sale
  en 780 KB; si te pasas, avísame antes de recortar nada.

- obras.json → una entrada por par autor+obra: título, autoría, tipo, subtipo, número de
  menciones, episodios en los que aparece, partes citadas, año y editorial SI existen en
  los caches, y las editoriales dichas en el audio que vengan en "datos_nuevos".
  Deja el campo vacío cuando no haya dato; no inventes ni infieras.

- autores.json → una entrada por autoría: nombre, número de menciones, obras, episodios,
  primera y última aparición.

- dialogo.json → grafo de "en_dialogo_con": { nodes:[{id, titulo, menciones}],
  edges:[[a, b, peso]] }, normalizando los títulos (minúsculas, sin tildes, sin
  puntuación) para unir duplicados. Marca en cada nodo el tamaño de su componente para
  que el cliente pueda dibujar solo los de 4 o más.

- figuras.json → las partes citadas de «Fragmentos de un discurso amoroso» (hay 60), con
  sus menciones y episodios.

- episodios/<id>.json → ficha completa por episodio con todas sus menciones y todos los
  campos, incluidos contexto, hablante, confianza y datos_nuevos.

El script tiene que ser idempotente, no tocar nada fuera de web/public/data/, y terminar
imprimiendo un resumen con los conteos. Añade tests que comprueben:
- que el total de menciones de index.json coincide con la suma de los ficheros de
  extracción
- que todo episodio de index.json tiene al menos un tema
- que todo índice de cadena usado en refs existe en su lista correspondiente
```

### Paso 3 — esqueleto de la web

```
Crea en web/ un proyecto Astro 5 con salida estática y TypeScript, con islas de React solo
donde haga falta. Estructura:

- src/lib/datos.ts    → carga y cachea index.json; helpers para resolver los índices de
                        cadena a texto.
- src/lib/store.ts    → estado global de filtros (q, temporada, tema, tipo, funcion, tono,
                        soporte, alcance, confianza, episodio, autor, obra, figura,
                        rangoMinutos) con suscripción, una función filtrar() que devuelve
                        la porción activa, y sincronización bidireccional con la query
                        string.
- src/components/BarraFiltros.tsx → la ÚNICA barra de filtros, pegajosa arriba, con el
                        buscador, las facetas multiselección, los chips de filtro activo
                        con aspa y el contador "N de 5.596 menciones".
- src/components/Tabla.tsx        → TanStack Table virtualizada con la cita literal.
- src/components/Regleta.tsx      → barra de tiempo del episodio con una marca por
                        inicio_s, color por tono, hover con la cita, clic que abre YouTube
                        en ese segundo o copia "1x04 · 12:34" si no hay vídeo.

Páginas: /, /buscar, /explorar, /episodio/[id], /autor/[slug], /obra/[slug], /tema/[slug],
/figura/[slug], /tipo/[slug], /temporada/[n], /sobre.

Reglas:
- Cero peticiones en tiempo de ejecución: todo sale de web/public/data.
- Modo oscuro por defecto, con conmutador que recuerda la elección en memoria de sesión
  (nada de localStorage).
- Los filtros viven SOLO en la barra superior, nunca dentro de la tarjeta de un gráfico.
- Toda vista filtrada tiene que ser enlazable por su URL.
- Cada página con datos tiene título y meta description propios, generados desde los
  datos.
```

### Paso 4 — el buscador

```
Monta el buscador con Orama en cliente:

- Construye el índice en un Web Worker al cargar la aplicación, a partir de index.json.
  Indexa obra, autor, parte, cita, contexto y título de episodio. Sin acentos, con
  tolerancia a erratas de 1 carácter.
- La página /buscar muestra cuatro pestañas sobre la misma consulta, con el recuento en
  cada una: Autoras · Obras · Menciones · Episodios. Las pestañas de autoras, obras y
  episodios se calculan agregando los resultados de menciones y buscando además en las
  listas de autores.json y obras.json.
- En la pestaña de menciones, resalta el término encontrado dentro de la cita literal.
- Debounce de 150 ms. La consulta y la pestaña activa van en la query string.
- Si el worker no está listo todavía, que la caja de búsqueda funcione igual con un
  filtrado por subcadena mientras tanto, en vez de quedarse bloqueada.
```

### Paso 5 — los gráficos

```
Implementa en web/src/components/ los siguientes gráficos, uno por fichero, todos
suscritos al store de filtros y todos clicables (un clic añade o quita un filtro):

1. MatrizTemasEpisodios.tsx — LA PORTADA. 37 temas (filas) × 118 episodios (columnas, en
   orden cronológico). Celda pintada si el episodio trata ese tema, intensidad por número
   de menciones del episodio con escala raíz, rampa secuencial de un solo tono. Filas
   ordenadas por primera aparición del tema. Cabecera con bandas de temporada clicables.
   Hover: título, fecha, temas y número de menciones. Clic en celda: al episodio. Clic en
   el nombre de la fila: al tema.
2. Regleta.tsx — ya creada en el paso 3; intégrala en la ficha de episodio y en miniatura
   en las tarjetas de episodio del buscador.
3. Pulso.tsx — dispersión fecha × minuto de las 5.592 menciones con hora, color por tono
   con paleta divergente (entusiasta / neutro / crítico), brush vertical para filtrar por
   tramo de minutos.
4. GrafoDialogo.tsx — sigma.js + graphology sobre dialogo.json, dibujando solo los
   componentes de 4 o más nodos, ForceAtlas2, etiquetas únicamente en los nodos de mayor
   grado y con evasión de colisiones. Nota al pie diciendo cuántas parejas sueltas quedan
   fuera.
5. MatrizAutorEpisodio.tsx — 24 autorías más citadas × 118 episodios, escala raíz.
6. AreaPorTipo.tsx — área apilada de tipos a lo largo de los episodios, con las
   temporadas marcadas.

Restricciones de diseño, no negociables:
- Máximo 8 colores categóricos, asignados en orden fijo; el color sigue a la entidad,
  nunca a su posición en el ranking (filtrar no debe repintar a los supervivientes).
- Nunca dos ejes Y en el mismo gráfico.
- Rampa secuencial de un solo tono, claro a oscuro. Nada de arcoíris.
- Marcas finas, rejilla y ejes en línea de un pelo, sin líneas discontinuas.
- Leyenda siempre presente con 2 o más series; etiquetas directas solo en los extremos.
- Cada gráfico tiene su equivalente en tabla, accesible desde la propia tarjeta.
- Tooltip en hover y el mismo contenido con foco de teclado.
```

### Paso 6 — páginas de navegación

```
Genera las páginas de navegación desde los JSON de web/public/data, todas estáticas:

- /tema/[slug] (37): descripción del tema, sus episodios en línea de tiempo, las obras y
  autorías más citadas dentro de él, y la tabla de menciones filtrada.
- /figura/[slug] (60): una página por figura de «Fragmentos de un discurso amoroso», con
  las citas literales en las que aparece, los episodios que la trabajan y las obras que se
  ponen en diálogo con ella. Estas páginas son el corazón del proyecto: cuídalas.
- /tipo/[slug] (12): "todas las películas citadas", "todos los poemas", etc.
- /temporada/[n]: las cinco temporadas más los especiales y Las Glosas, cada una con sus
  episodios, sus temas dominantes y lo que entra y sale respecto de la anterior.
- /autor/[slug] y /obra/[slug]: ficha con menciones, episodios, partes citadas, con qué
  dialoga, y año y editorial SOLO si existen en los datos.

En las fichas de obra, cuando haya editorial dicha en el audio (campo datos_nuevos),
muéstrala citando la frase textual en la que se dice. Es información que no está en
ningún catálogo.
```

### Paso 7 — publicación

```
Prepara el despliegue en Cloudflare Pages:
- build desde el repo, comando de build que ejecute primero
  podcast-data/scripts/14_build_web_data.py y después el build de Astro
- dominio universopunzadas.com
- cabeceras de caché largas para web/public/data/*.json con hash en el nombre
- sitemap.xml y robots.txt
- página /sobre con qué es el proyecto, cómo se han hecho las transcripciones y la
  extracción, el criterio de extracción enlazado, y el aviso de que es un proyecto de
  aficionadas

Comprueba con Lighthouse que la portada carga por debajo de 2 s en 4G simulada y que la
navegación por teclado funciona en la matriz, el buscador y la tabla.
```

---

## 9. Lo que queda fuera, y por qué

- **Reproductor de audio propio.** Decidido que no. Si algún día se quiere, la vía es
  hablar antes con Radio Primavera Sound y comprobar que los minutos guardados siguen
  cuadrando con el mp3 que sirve Megaphone, porque la publicidad dinámica los puede
  desplazar.
- **Página de descarga de datos.** Decidido que no. El repositorio ya es público.
- **Gráficos de año de publicación.** Solo 139 obras de 1.317 tienen año. Cuando el
  enriquecimiento suba, se desbloquea el gráfico de doble tiempo (cuándo se publicó la
  obra frente a cuándo se citó).
- **Navegación por hablante** (lo que cita Paula frente a lo que cita Inés). Los datos lo
  permiten, pero antes hay que mapear SPEAKER_00 / SPEAKER_01 a nombres reales episodio a
  episodio, y no está hecho.
- **Nube de figuras.** Redundante con las páginas de figura y con las burbujas de autoría.

---

## 10. Aviso

Proyecto de aficionadas, sin relación oficial con Punzadas Sonoras, Paula Ducay,
Inés García ni Radio Primavera Sound.

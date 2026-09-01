# Paleta rojo · rosa · negro para universopunzadas.com

Complemento de `prompts-unificacion-estilos.md`. **Sustituye** el apartado (b) del Paso 1
y reescribe el Paso 4. Todos los valores de este documento están calculados y
verificados: gamut sRGB, contraste WCAG y separación perceptual en Oklab.

---

## 1. La buena noticia: la marca ya es roja

El lettering a mano (`web/public/images/marca/*.svg`) lleva la tinta horneada en los
paths. Convertida a OKLCH:

| hex | OKLCH | qué es |
|---|---|---|
| `#69000f` | `oklch(33% 0.133 24)` | rojo sangre profundo |
| `#792135` | `oklch(39% 0.122 11)` | carmín oscuro |
| `#7c2144` | `oklch(40% 0.128 1)` | vino |
| `#804950` `#824c54` | `oklch(47–48% 0.075 11)` | ciruela apagado |
| `#83495f` `#844c63` | `oklch(48–49% 0.082 355)` | ciruela frío |
| `#936985` `#956c89` | `oklch(57–58% 0.066 338)` | malva |
| `#9c94a4` | `oklch(68% 0.025 308)` | gris lila |

Todo vive entre **matiz 338 y 24**, luminosidad 33–68%, croma 0.025–0.133. Es decir:
rojos, rosas y ciruelas. Lo que pides no es un cambio de rumbo, es alinear la web con
la tinta que ya tiene. El acento naranja actual, `oklch(52% 0.16 55)`, es el
elemento fuera de sitio.

**Consecuencia de diseño:** la paleta no se inventa. Se deriva del lettering. El
`--color-secuencial-5` que propongo abajo es literalmente `#69000f`.

---

## 2. La decisión que hay que tomar: qué significa "negros"

Hay dos lecturas y llevan a sitios muy distintos.

### Opción CLARA — negro como tinta *(recomendada)*

Fondo casi blanco con matiz rosado, texto negro rojizo, rojo sangre como acento, y
negro usado a propósito en las bandas: barra de filtros, pie, cabeceras de sección,
celdas densas de las matrices. El lettering sigue funcionando sin tocarlo.

### Opción OSCURA — negro como fondo

Fondo `oklch(15% 0.02 15)`, rosa claro como acento. Más dramático y más cerca de lo
que probablemente estás imaginando. **Pero:**

- Rompe el lettering. La tinta es oscura y está dentro del SVG; no hay CSS que la
  cambie. Habría que **re-exportar los `marca/*.svg` con tinta clara**, una versión
  por tema, y conmutarlas. Trabajo real, y hay que tener los originales.
- El comentario que hay hoy en `global.css` documenta esta decisión: *"Un solo tema,
  claro: el lettering a mano trae su tinta horneada en el propio SVG, pensada para
  leerse sobre papel claro."* Ir a oscuro es revertirla conscientemente.
- Las 5.592 marcas del Pulso y las matrices de 118 columnas se leen distinto sobre
  negro: las rampas oscuras necesitan ir de oscuro a claro, no al revés, y la
  percepción de intensidad se invierte.

Doy los valores para las dos. Los prompts asumen la clara; si eliges la oscura, la
sección 6 dice qué cambia.

---

## 3. Lo que NO puede ser rojo, y por qué

Esto es lo importante y no hay forma de rodearlo.

**Los 8 categóricos existen para distinguirse entre sí.** Están hoy repartidos cada
45° en el círculo de matiz por esa razón. Si los metes todos en el rango rojo-rosa,
dejan de cumplir su función: la leyenda del área apilada por tipo se vuelve ilegible y
el grafo de diálogo pierde la codificación.

Dentro de rojo-rosa-ciruela **caben 6 categorías distinguibles, no 8**, y solo si las
separas también por luminosidad, no únicamente por matiz. Así que la propuesta es:

> **Reducir de 8 categorías a 6 + "otros".** En `AreaPorTipo.tsx`, `MAX_TIPOS` pasa de
> 7 a 5 (5 + otros = 6). Los tipos reales son libro / artículo / persona / película /
> otros: cinco ya cubre el uso real, y las ocho ranuras siempre fueron holgura.

Los valores de abajo están verificados: el par más cercano queda en ΔE Oklab **0.115**,
por encima del umbral de 0.10 en el que se confunden. La última categoría (`cat-6`,
matiz 315) se va hacia el lila; es el precio de sacar seis colores de esta familia, y
además rima con el `#9c94a4` gris-lila del propio lettering.

**El tono también cambia de mecanismo.** Hoy es divergente por matiz
(verde entusiasta ↔ rojo crítico). Si todo es rojo, el rojo deja de significar
"crítico". La propuesta es hacerlo **divergente por luminosidad** dentro de la familia
—rosa claro entusiasta ↔ negro rojizo crítico, gris en medio— y añadir redundancia de
forma en `.punto-tono` (relleno / anillo / medio relleno), que además arregla la
dependencia del color solo.

---

## 4. Tokens — tema claro (verificados)

```css
:root {
  /* Semánticos. Derivados de la tinta del lettering.
     Contrastes verificados contra --color-fondo. */
  --color-fondo:            oklch(98% 0.008 15);   /* #FEF6F7  papel con calor rosado */
  --color-superficie:       oklch(100% 0 0);       /* #FFFFFF  tarjetas               */
  --color-superficie-alta:  oklch(95% 0.012 15);   /* #F6EBEC  cabeceras, hover        */
  --color-borde:            oklch(87% 0.020 10);   /* #E1CFD1                          */
  --color-texto:            oklch(18% 0.030 15);   /* #1D0C0D  negro rojizo, no #000   */
  --color-texto-tenue:      oklch(43% 0.045 10);   /* #66464A                          */
  --color-acento:           oklch(45% 0.175 22);   /* #A00C24  rojo sangre             */

  /* Negro de banda: barra de filtros, pie, cabeceras de sección */
  --color-tinta:            oklch(15% 0.020 15);   /* #130808                          */
  --color-tinta-texto:      oklch(95% 0.010 15);   /* #F5ECEC  texto sobre --tinta     */

  /* Rampa secuencial, un solo tono. El peldaño 5 ES la tinta del lettering. */
  --color-secuencial-1: oklch(95% 0.020 15);  /* #FCE9EA */
  --color-secuencial-2: oklch(84% 0.065 15);  /* #F2BABD */
  --color-secuencial-3: oklch(68% 0.130 18);  /* #DD747A */
  --color-secuencial-4: oklch(50% 0.180 22);  /* #B32130 */
  --color-secuencial-5: oklch(33% 0.133 24);  /* #6A000E ≡ #69000f del SVG */

  /* Categóricos: 6 + otros. Antes 8. Ver sección 3. */
  --color-cat-1: oklch(45% 0.175 25);   /* #A00E1C  rojo profundo */
  --color-cat-2: oklch(62% 0.150 15);   /* #D05A69  coral        */
  --color-cat-3: oklch(80% 0.085 5);    /* #EEA7B6  rosa claro   */
  --color-cat-4: oklch(40% 0.135 348);  /* #781F54  vino         */
  --color-cat-5: oklch(58% 0.145 332);  /* #AA56A0  magenta      */
  --color-cat-6: oklch(70% 0.095 315);  /* #B58CC7  lila         */
  --color-cat-otros: oklch(58% 0.015 340); /* #81777D gris rosado */

  /* Tono: divergente por LUMINOSIDAD, no por matiz. Siempre con forma redundante. */
  --color-tono-entusiasta:  oklch(60% 0.150 5);    /* #C75374  relleno       */
  --color-tono-ambivalente: oklch(48% 0.130 345);  /* #8E3A6E  medio relleno */
  --color-tono-neutro:      oklch(52% 0.012 340);  /* #6E666B  anillo        */
  --color-tono-critico:     oklch(27% 0.100 25);   /* #4C070A  relleno       */
}
```

**Verificación ya hecha (no hay que repetirla, sí hay que no romperla):**

| par | ratio | nivel |
|---|---|---|
| texto / fondo | 17,82:1 | AAA |
| texto-tenue / fondo | 7,82:1 | AAA |
| acento / fondo | 7,69:1 | AAA |
| acento / superficie-alta | 7,03:1 | AAA |
| blanco / acento (botón) | 8,17:1 | AA |
| tinta-texto / tinta | 16,99:1 | AAA |

Todos los tokens caen dentro del gamut sRGB. El acento está a croma 0.175, justo por
debajo del máximo alcanzable a esa luminosidad (0.180): no subas más, se sale.

Categóricos, pares más próximos en ΔE Oklab: cat-2/cat-5 **0,115** · cat-1/cat-4
**0,117** · cat-3/cat-6 **0,126**. Umbral de seguridad 0,10.

Tono, par más próximo: ambivalente/neutro **0,125**.

---

## 5. Tokens — tema oscuro (por si eliges la opción B)

```css
:root {
  --color-fondo:            oklch(15% 0.020 15);   /* #130808 */
  --color-superficie:       oklch(19% 0.024 15);   /* #1D0F10 */
  --color-superficie-alta:  oklch(25% 0.030 15);   /* #2F1C1D */
  --color-borde:            oklch(34% 0.035 12);   /* #483033 */
  --color-texto:            oklch(95% 0.010 15);   /* #F5ECEC */
  --color-texto-tenue:      oklch(72% 0.025 12);   /* #B49FA0 */
  --color-acento:           oklch(70% 0.160 18);   /* #F16F78 */

  /* La rampa se INVIERTE: de oscuro a claro. */
  --color-secuencial-1: oklch(28% 0.040 15);  /* #3A2022 */
  --color-secuencial-2: oklch(40% 0.090 18);  /* #703135 */
  --color-secuencial-3: oklch(54% 0.150 20);  /* #B54249 */
  --color-secuencial-4: oklch(68% 0.170 20);  /* #EF656B */
  --color-secuencial-5: oklch(82% 0.120 15);  /* #FFA3AB */
}
```

Contrastes: texto/fondo 16,99:1 (AAA) · texto-tenue/fondo 7,86:1 (AAA) ·
acento/fondo 6,86:1 (AA) · negro/acento 7,30:1. Todo en gamut.

Los categóricos del tema claro **no sirven tal cual sobre negro**: cat-1 y cat-4 se
hunden. Habría que subirlos a luminosidad 55–85%. Eso es trabajo adicional que la
opción clara se ahorra.

---

## 6. Prompt que sustituye al Paso 4

> Repo: punzadassonoras. Lee antes este documento entero.

```
Vas a cambiar la paleta de universopunzadas.com a una familia rojo / rosa / negro,
derivada de la tinta del lettering a mano de web/public/images/marca/*.svg.

La especificación completa, con todos los valores OKLCH ya verificados (gamut,
contraste WCAG y separación perceptual en Oklab), está en
docs/paleta-universo-punzadas.md. Úsala tal cual. NO recalcules ni "mejores" los
valores: están ajustados al límite del gamut y al umbral de distinción.

Tema: CLARO. Fondo casi blanco con matiz rosado, negro usado como tinta y como banda,
no como fondo de página. Motivo: el lettering SVG lleva la tinta oscura horneada en
los paths y está pensado para papel claro.

Trabaja en este orden, commiteando después de cada bloque:

BLOQUE 1 — semánticos.
  Sustituye en web/src/styles/global.css los siete tokens semánticos por los de la
  sección 4 del documento. Añade --color-tinta y --color-tinta-texto.
  Verifica que no queda ningún oklch(...) con matiz 55 en todo web/src.

BLOQUE 2 — rampa secuencial.
  Los cinco peldaños. Comprueba después que la matriz temas × episodios y la matriz
  autoría × episodio siguen legibles: la escala raíz no cambia, pero el contraste
  entre peldaños sí. Captura las dos matrices antes y después y compáralas.

BLOQUE 3 — categóricos: de 8 a 6 + otros.
  Esto es un cambio de estructura, no solo de color.
  - En web/src/components/AreaPorTipo.tsx, MAX_TIPOS pasa de 7 a 5.
  - El array PALETA pasa de 8 entradas a 6 (cat-1..cat-6) y "otros" usa
    --color-cat-otros.
  - Busca TODOS los demás consumidores de --color-cat-7 y --color-cat-8 en web/src
    y decide caso por caso: o entran en las 6, o van a "otros". No dejes referencias
    colgando a tokens que ya no existen.
  - REGLA QUE NO SE ROMPE: el color sigue a la entidad, no a su posición en el
    ranking. Filtrar no puede repintar a los supervivientes. Con 6 ranuras en vez de
    8 esto es más fácil de romper, así que verifícalo explícitamente: filtra por una
    temporada y comprueba que ningún tipo cambia de color.
  - Comprueba las leyendas: con menos categorías, "otros" agrupa más. Si "otros"
    pasa a ser la banda más grande del área apilada, dímelo, porque entonces 5 tipos
    es demasiado poco y hay que reconsiderar.

BLOQUE 4 — tono, que cambia de mecanismo.
  Hoy es divergente por matiz (verde ↔ rojo). Pasa a ser divergente por LUMINOSIDAD
  dentro de la familia roja, con los cuatro valores de la sección 4.
  Como el matiz ya no distingue, añade redundancia de forma en .punto-tono:
    entusiasta  → círculo relleno
    ambivalente → círculo medio relleno
    neutro      → anillo (borde, sin relleno)
    crítico     → círculo relleno oscuro
  Actualiza la leyenda del Pulso para que muestre la forma además del color, y el
  atributo accesible de cada punto para que el tono se anuncie por texto.
  Esto arregla de paso la dependencia del color solo, que era una deuda previa.

BLOQUE 5 — lo que NO se toca.
  Los SVG de marca/. Ni recolorear, ni filtros CSS, ni mix-blend-mode. Nada.
  Después de los bloques 1–4, comprueba que el lettering sigue teniendo contraste
  suficiente contra el nuevo --color-fondo (#FEF6F7 en vez del anterior casi
  neutro). La tinta más clara del SVG es #9c94a4: calcula su ratio contra el fondo
  nuevo y dime el número. Si baja de 3:1 sobre el fondo, avísame antes de seguir.

Verificación final, obligatoria:
- capturas en 375/768/1024/1440 de: portada, /explorar, /buscar, una ficha de
  episodio, una de obra, una de figura
- las tres visualizaciones críticas comparadas una a una: matriz temas × episodios,
  Pulso, grafo de diálogo
- recalcula el contraste de TODAS las parejas texto/fondo del sitio con los tokens
  nuevos y dame la tabla
- simulación de deuteranopia y protanopia sobre la leyenda de los categóricos y
  sobre la leyenda de tono: en una familia roja esto importa mucho más que antes.
  Si algún par se confunde, la forma redundante del bloque 4 tiene que bastar para
  desambiguar. Verifícalo, no lo asumas.
- navegación por teclado en buscador, tabla y matriz
```

---

## 7. Qué cambia en el resto del plan

**Paso 1, apartado (b)** — ya no hay que decidir el espacio de color de
universopunzadas: es OKLCH y son estos valores. Lo que queda por decidir en ese
apartado es solo la conversión de maramotto a OKLCH.

**Paso 1, nuevo apartado (f)** — pregunta abierta que ahora aparece: el acento de
maramotto es morado `#7B2D8E` y el de universopunzadas pasa a ser rojo `#A00C24`.
¿Siguen siendo dos acentos distintos, o esto es la señal de que maramotto también
quiere moverse hacia el rojo? No hace falta responderla ahora, pero conviene tenerla
sobre la mesa antes del Paso 3, porque migrar maramotto dos veces sería tonto.

**Paso 5** — el punto 2, botones. Con el rojo `#A00C24` los botones de
universopunzadas ganan mucho peso visual. Verifica que el botón primario no compite
con las matrices por la atención en `/explorar`.

**Paso 6, el iframe** — mejora sola. El hero teal `#1E6B7B` de
`universo-punzadas.html` en maramotto choca hoy con un sitio de acento naranja;
chocará todavía más con uno rojo. Ese paso pasa de "conviene" a "hay que".

---

## 8. Riesgo que conviene mirar de frente

Una paleta monocroma amplia es más difícil de usar bien que una policroma. Los tres
sitios donde esto se cae:

1. **Leyendas de 6 categorías rojas.** Verificadas en ΔE, pero ΔE es un modelo. Míralo
   impreso en pantalla con datos reales antes de dar el bloque 3 por bueno.
2. **Daltonismo.** Protanopia y deuteranopia comprimen justo este eje. Por eso el
   bloque 4 añade forma, y por eso la verificación final la exige explícitamente.
3. **El Pulso con 5.592 puntos.** Miles de marcas rojas sobre papel rosado pueden
   leerse como una mancha. Si pasa, la solución no es cambiar la paleta: es bajar la
   opacidad de la marca y subir su tamaño mínimo.

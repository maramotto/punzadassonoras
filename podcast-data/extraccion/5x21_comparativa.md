# 5x21 — Comparativa: extracción desde audio vs. extracción desde descripción

Cruza `5x21.json` (29 menciones, extraídas de la transcripción íntegra del episodio) contra
las 9 referencias que tenía `refs_all.json` para el 5x21, sacadas solo de la descripción de
YouTube.

---

## 1. Coincidencias

Las **9 referencias** de `refs_all.json` aparecen las 9 en el audio — ninguna era una
invención de la descripción. Lo que añade el audio a cada una:

| Obra | Autor/a | Alcance real | Soporte | Tono | Minuto | Dato nuevo |
|---|---|---|---|---|---|---|
| Fragmentos de un discurso amoroso | Roland Barthes | obra completa + 4 figuras concretas (Herrabundeo, Exilio, Catástrofe, Demonios) | leído | neutro/entusiasta/ambivalente según figura | [03:54](https://www.youtube.com/watch?v=KMPT0YIutUk&t=234s) | La descripción solo nombra 2 de las 4 figuras que citan (Exilio, Catástrofe); Herrabundeo y Demonios son descubrimiento del audio |
| Cuéntame mi historia. Filosofía de la narración | Adriana Cavarero | un capítulo o figura, no el libro entero | leído | entusiasta | [15:06](https://www.youtube.com/watch?v=KMPT0YIutUk&t=906s) | Editorial: **Katz** («editado en Cats») |
| The Break-Up Check | Pilar López-Cantero | obra completa | leído | **ambivalente** (útil pero «complejo... muy analítico») | [30:48](https://www.youtube.com/watch?v=KMPT0YIutUk&t=1848s) | Cita a Nussbaum y a «Goldi» dentro del artículo |
| The Language of Love's Lessening | Kerstin Maria Pahl | obra completa | leído | entusiasta | [40:02](https://www.youtube.com/watch?v=KMPT0YIutUk&t=2402s) | Analiza el desamor vía el verbo inglés «to unlove»; cita *Sentido y sensibilidad*, *Persuasión* y *Jane Eyre* como corpus |
| Blue Valentine | Derek Cianfrance | obra completa | **visto** | entusiasta | [42:29](https://www.youtube.com/watch?v=KMPT0YIutUk&t=2549s) | Año: 2010 |
| Annie Ernaux' ... Passion Simple and Se Perdre ... | Elizabeth Richardson Viti | obra completa | leído | entusiasta | [48:27](https://www.youtube.com/watch?v=KMPT0YIutUk&t=2907s) | — |
| Por el camino de Swann | Marcel Proust | obra completa + el capítulo «Un amor de Swann» como ejemplo | leído | entusiasta | [46:51](https://www.youtube.com/watch?v=KMPT0YIutUk&t=2811s) | Edición: **El Paseo Editorial**, «con muchas notas al pie», la que ha leído Inés |
| (autora mencionada) | Annie Ernaux | solo la autora en la descripción; el audio da título concreto (*Pura pasión*) | leído | entusiasta | [47:03](https://www.youtube.com/watch?v=KMPT0YIutUk&t=2823s) | — |
| Sentido y sensibilidad | Ang Lee | obra completa (**la película, no la novela**) | **visto** | entusiasta | [56:42](https://www.youtube.com/watch?v=KMPT0YIutUk&t=3402s) | Año: 1995. Aclaración: puede que Inés leyera la novela en su juventud, «pero no recuerdo» |

---

## 2. Altas — menciones nuevas que destapa el audio

**17 de las 29 menciones (59%) no estaban en la descripción.** Entre ellas, 8 son entidades
completamente nuevas que no aparecían de ninguna forma en `refs_all.json`:

- **Werther, de Goethe** — con dos funciones distintas: lo recomiendan ellas mismas como
  lectura necesaria para entender a Barthes (*«un libro que recomendamos leer mucho... se lee
  muy bien»*, [23:13](https://www.youtube.com/watch?v=KMPT0YIutUk&t=1393s)), y además Barthes
  lo usa como ejemplo dentro de la figura «Exilio» (grado: dentro de otra fuente).
- **Perderse (Se perdre), de Annie Ernaux** — un segundo título de Ernaux, nombrado junto a
  *Pura pasión* como ejemplo de su estilo confesional.
- **Persuasión** y **Jane Eyre** — las dos novelas que cita el artículo de Pahl junto a
  *Sentido y sensibilidad* como corpus de su análisis; ninguna de las dos aparece en la
  descripción.
- **Marian Rojas Estapé** — mención de pasada, en broma, sobre lo que el episodio no va a
  ser (un guion de autoayuda).
- **Martha Nussbaum**, **Peter Goldie** y **David Hume** — citados dentro del artículo de
  López-Cantero (Nussbaum y Goldie) y dentro del de López-Cantero también en tono de broma
  (Hume, «traducir las obras de Hume al sumerio»). Goldie tiene confianza baja: el audio
  deforma el nombre a «Goldi» y no se puede confirmar con certeza.

Además, el audio distingue **funciones y momentos distintos para la misma obra** que la
descripción funde en una sola mención:

- *Fragmentos de un discurso amoroso* aparece en 4 figuras distintas (Herrabundeo, Exilio,
  Catástrofe, Demonios), cada una con su propia cita y, en dos casos, su propio tono.
- *Pura pasión* de Ernaux aparece tres veces con matices distintos: como ejemplo genérico de
  su estilo (junto a *Perderse*), citada literalmente («han matado a Kennedy, me da igual»),
  y como eje de la comparación estructural con Proust vía los cinco estados del
  amor-enfermedad de Viti.
- *Por el camino de Swann* aparece como eje de sección, como recomendación (la anécdota del
  pin con la catleya, de su viaje a Normandía) y como ejemplo teórico (el amor de Swann por
  Odette).

## 3. Ausencias

**Ninguna.** Las 9 referencias de `refs_all.json` se localizan las 9 en el audio. No hay
ningún caso de una obra que la descripción mencionara y que ellas no lleguen a comentar
realmente, ni ningún nombre que Whisper deformara hasta hacerlo irrecuperable.

## 4. Veredicto

El audio no solo confirma el 100% de lo que ya teníamos, sino que casi **duplica** el número
de menciones de este episodio (9 → 29) y añade contexto real a las 9 originales: alcance
exacto (Cavarero leyó capítulos sueltos, no el libro), soporte (vieron la película de
*Sentido y sensibilidad*, no leyeron la novela), tono (el artículo de López-Cantero les
resulta útil pero pesado), una editorial nueva (El Paseo, para la edición de Proust) y ocho
entidades culturales que no aparecían por ningún lado en el texto. Si esta proporción se
sostiene, el 5x21 confirma la proyección del piloto de 200-400 referencias nuevas sobre las
583 originales — de hecho la sostiene con holgura, porque este episodio por sí solo aporta 20
menciones nuevas. Lo que habría que ajustar antes de escalar a los 116 restantes: decidir de
antemano cuánta granularidad dar a las figuras de un mismo libro (aquí se trató cada figura de
Barthes como una mención distinta, lo cual es rico pero multiplica las filas) y fijar un
criterio explícito para cuándo una mención "dentro de otra fuente" merece fila propia frente a
quedar solo como contexto (aquí se incluyeron incluso citas de una sola persona sin obra,
como Nussbaum o Hume, con confianza media/baja).

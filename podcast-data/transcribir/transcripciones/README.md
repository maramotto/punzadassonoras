# Transcripciones de Punzadas Sonoras

**Punzadas Sonoras** es un podcast de **Paula Ducay** e **Inés García**, producido por
**Radio Primavera Sound**. Todo el contenido transcrito aquí es obra suya.

- Podcast: <https://punzadas.com/punzadas-sonoras/>
- Radio Primavera Sound: <https://www.primaverasound.com/es/radio/shows/punzadas-sonoras>
- Newsletter: <https://punzadas.substack.com>

Este es un **proyecto de fans, sin ánimo de lucro y sin relación oficial con el podcast ni con
Radio Primavera Sound**. Existe para construir un catálogo navegable de las obras que se citan
en el programa. Si las autoras quieren que esta carpeta desaparezca, desaparece.

## Qué hay aquí

117 episodios (temporadas 1 a 5, especiales y Las Glosas), 111 horas de audio, 165.656
segmentos. Dos archivos por episodio, con el mismo nombre:

- `AAAA-MM-DD_codigo.json` — transcripción estructurada, es la fuente de verdad
- `AAAA-MM-DD_codigo.txt` — volcado legible del mismo contenido, derivado del JSON

Los episodios que no llegaron a subirse a la playlist de YouTube llevan `sincodigo` en el
nombre; su código de episodio está en `podcast-data/data/refs_all.json`, emparejado por fecha.

## Formato del JSON

```json
{
  "slug": "2026-07-16_5x21",
  "codigo": "5x21",
  "titulo": "Dejar de amar: la ruptura amorosa",
  "fecha": "2026-07-16",
  "video_id": "KMPT0YIutUk",
  "url_audio": "https://traffic.megaphone.fm/...mp3",
  "segmentos": [
    {"inicio": 913.4, "fin": 917.2, "texto": "...", "hablante": "SPEAKER_01"}
  ]
}
```

`inicio` y `fin` van en segundos. `video_id` está vacío en los 59 episodios que no están en
YouTube; para esos, el enlace profundo se construye sobre `url_audio` con `#t=segundos`.

## Cómo se generaron

`../transcribir.py`, en un Mac con Apple Silicon:

- **Texto:** mlx-whisper `large-v3`
- **Hablantes:** pyannote 3.1

## Advertencias

**Son transcripciones automáticas y contienen errores.** No son una fuente fiable para citar
literalmente a las autoras. En este proyecto se usan como fuente de *contexto*, nunca de
nombres propios: los nombres se toman siempre de las descripciones de los episodios, porque
Whisper los destroza con frecuencia (Cavarero → «cabarero», Cianfrance → «derexian france»).

**Las etiquetas de hablante no están emparejadas con personas.** `SPEAKER_00` y `SPEAKER_01`
son arbitrarias y **cambian de un episodio a otro**: el `SPEAKER_00` de un episodio no es
necesariamente la misma persona que el `SPEAKER_00` de otro. No asumas que una etiqueta
corresponde a Paula o a Inés.

Reparto de voces detectadas: 113 episodios con 2 voces y 4 con 3 voces (los directos con
invitada). El 0,14% del tiempo quedó sin asignar, etiquetado como `DESCONOCIDO`.

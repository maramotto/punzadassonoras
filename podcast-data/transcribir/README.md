# Transcribir Punzadas Sonoras

Transcribe los **117 episodios** (116 horas de audio) separando las voces de Inés y Paula.

Se descarga el audio del feed público del podcast, así que funciona igual para las cinco
temporadas: no depende de YouTube.

---

## 1. Instalar (una sola vez, ~10 minutos)

Abre la Terminal y pega esto:

```bash
# Homebrew, si no lo tienes ya
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

brew install ffmpeg python@3.11
```

Después, dentro de la carpeta `transcribir`:

```bash
cd ruta/a/transcribir
python3 -m venv .venv
source .venv/bin/activate

# Motor de transcripción
pip install mlx-whisper        # si tu Mac es Apple Silicon (M1/M2/M3/M4)
# pip install faster-whisper   # si tu Mac es Intel

# Separación de voces
pip install pyannote.audio torch torchaudio
```

## 2. Conseguir el permiso para separar voces

El modelo que distingue quién habla es gratis, pero exige aceptar sus condiciones:

1. Crea una cuenta en <https://huggingface.co/join>
2. Entra en <https://huggingface.co/pyannote/speaker-diarization-community-1> y pulsa **Agree**
3. Entra en <https://huggingface.co/pyannote/segmentation-3.0> y pulsa **Agree**
4. Ve a <https://huggingface.co/settings/tokens>, crea un token de tipo *Read* y cópialo

(El modelo clásico `speaker-diarization-3.1` no hace falta: con la versión de
`pyannote.audio` que se instala en el paso 1 sale muy desequilibrado —le adjudicaba
el 99% del episodio a una sola voz en la prueba con el 5x21—, así que el script usa
`speaker-diarization-community-1`, el pipeline pensado para esa versión.)

Luego, en la Terminal:

```bash
export HF_TOKEN=hf_tu_token_aqui
```

Si te saltas este paso, el script sigue funcionando pero no separa las voces.

## 3. Probar con un episodio

Antes de dejarlo toda la noche, comprueba que funciona:

```bash
python3 transcribir.py --solo 5x21
```

Tarda unos minutos. Cuando acabe, abre `transcripciones/2026-07-16_5x21.txt` y mira
si el texto tiene sentido y si los bloques `SPEAKER_00` / `SPEAKER_01` cambian donde
cambia la persona que habla.

## 4. Lanzarlo entero

```bash
caffeinate -i python3 transcribir.py
```

`caffeinate` evita que el Mac se duerma a media faena. Puedes cerrar la tapa igualmente si
lo dejas enchufado.

**Cuánto tarda:** en un Mac con Apple Silicon, entre 8 y 14 horas para los 117 episodios
(transcripción + separación de voces). En un Mac Intel es bastante más, del orden de dos o
tres días; en ese caso conviene lanzarlo por tandas con `--limite 20`.

**Si lo paras**, no pasa nada: al volver a lanzarlo continúa por donde iba. Puedes cortarlo
con Ctrl+C cuando quieras.

## 5. Qué te queda al terminar

En `transcripciones/` habrá dos archivos por episodio:

- `.json` — el que me interesa a mí: cada segmento con su minuto exacto y su hablante
- `.txt` — legible, para que puedas ojearlo tú

Mándame la carpeta `transcripciones/` (o solo los `.json`) y con eso monto la extracción
completa: función de cada obra en la conversación, alcance, contexto, cita textual y
enlace al minuto exacto.

---

## Detalles y avisos

**Los hablantes salen como `SPEAKER_00` y `SPEAKER_01`, no como «Inés» y «Paula».** El
modelo distingue voces, pero no sabe de quién son. Basta con que escuches los primeros
segundos de un par de episodios y me digas cuál es cuál; el reparto suele mantenerse dentro
de un mismo episodio, pero **puede cambiar de un episodio a otro**, así que lo asignaremos
episodio a episodio comparando huellas de voz.

**Los episodios con invitada saldrán peor.** El script asume dos voces (`N_HABLANTES = 2`).
En los episodios en vivo con Elena López Riera, Marta Jiménez Serrano, Pau Luque o Blanca
Lacasa habría que subirlo a 3. Están identificados en la hoja de cálculo; los podemos
relanzar aparte con el valor corregido.

**Espacio en disco:** el script borra el audio según termina cada episodio. Si quieres
conservarlo, usa `--conservar-audio` y reserva unos 8 GB.

**Si quieres ir más rápido** a costa de algo de precisión, abre `transcribir.py` y cambia
`MODELO_MLX` a `mlx-community/whisper-large-v3-turbo`. Yo no lo haría: lo que peor lleva
Whisper son justamente los nombres propios, que es lo que más nos importa aquí.

**El manifiesto** (`manifiesto_audio.json`) trae los 117 episodios con su URL de audio, su
fecha y su código. Los 27 que salen sin código son episodios que no están en la playlist de
YouTube; los numeraremos al integrarlos.

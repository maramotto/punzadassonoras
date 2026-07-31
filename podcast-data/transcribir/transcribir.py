#!/usr/bin/env python3
"""
Transcribe y diariza los episodios de Punzadas Sonoras.

Descarga el audio del feed público, lo transcribe con Whisper y separa las voces
(quién dice qué). Es reanudable: si lo paras, al volver a lanzarlo sigue donde iba.

Uso:
    python3 transcribir.py                 # todos los episodios pendientes
    python3 transcribir.py --limite 3      # solo 3 (para probar)
    python3 transcribir.py --solo 5x21     # un episodio concreto
    python3 transcribir.py --sin-diarizar  # solo transcripción, sin separar voces

Ver README.md para la instalación.
"""
import argparse, json, os, subprocess, sys, time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
MANIFIESTO = AQUI / 'manifiesto_audio.json'
AUDIO = AQUI / 'audio'
SALIDA = AQUI / 'transcripciones'
LOG = AQUI / 'progreso.log'

# large-v3 acierta bastante más con los nombres propios, que es justo lo que nos
# interesa. Si vas con prisa, 'mlx-community/whisper-large-v3-turbo' va el doble
# de rápido a costa de algo de precisión.
MODELO_MLX = 'mlx-community/whisper-large-v3-mlx'
MODELO_FW = 'large-v3'
IDIOMA = 'es'
N_HABLANTES = 2  # Inés y Paula. Los episodios con invitada se corrigen a mano.


def log(msg):
    linea = f'[{time.strftime("%H:%M:%S")}] {msg}'
    print(linea, flush=True)
    with open(LOG, 'a') as f:
        f.write(linea + '\n')


def es_apple_silicon():
    return sys.platform == 'darwin' and os.uname().machine == 'arm64'


def descargar(url, destino):
    if destino.exists() and destino.stat().st_size > 10000:
        return True
    tmp = destino.with_suffix('.parcial')
    try:
        subprocess.run(['curl', '-sL', '--fail', '--max-time', '900', url, '-o', str(tmp)], check=True)
        tmp.rename(destino)
        return True
    except subprocess.CalledProcessError:
        log(f'  ERROR descargando {url}')
        tmp.unlink(missing_ok=True)
        return False


def a_wav16k(mp3, wav):
    """pyannote quiere WAV mono a 16 kHz. Whisper también lo agradece."""
    if wav.exists():
        return True
    r = subprocess.run(['ffmpeg', '-y', '-i', str(mp3), '-ac', '1', '-ar', '16000',
                        '-loglevel', 'error', str(wav)], capture_output=True)
    if r.returncode != 0:
        log(f'  ERROR ffmpeg: {r.stderr.decode()[:200]}')
        return False
    return True


# ---------------------------------------------------------------- transcripción
_modelo_fw = None


def transcribir(wav):
    """Devuelve lista de segmentos {inicio, fin, texto}."""
    if es_apple_silicon():
        import mlx_whisper
        r = mlx_whisper.transcribe(str(wav), path_or_hf_repo=MODELO_MLX,
                                   language=IDIOMA, word_timestamps=False,
                                   condition_on_previous_text=False)
        return [{'inicio': s['start'], 'fin': s['end'], 'texto': s['text'].strip()}
                for s in r['segments'] if s['text'].strip()]
    global _modelo_fw
    from faster_whisper import WhisperModel
    if _modelo_fw is None:
        _modelo_fw = WhisperModel(MODELO_FW, device='cpu', compute_type='int8')
    segs, _ = _modelo_fw.transcribe(str(wav), language=IDIOMA, vad_filter=True,
                                    condition_on_previous_text=False)
    return [{'inicio': s.start, 'fin': s.end, 'texto': s.text.strip()}
            for s in segs if s.text.strip()]


# ---------------------------------------------------------------- diarización
_pipeline = None


def diarizar(wav):
    """Devuelve lista de turnos {inicio, fin, hablante}."""
    global _pipeline
    from pyannote.audio import Pipeline
    import torch
    if _pipeline is None:
        token = os.environ.get('HF_TOKEN')
        if not token:
            raise RuntimeError('Falta la variable de entorno HF_TOKEN (ver README).')
        # speaker-diarization-3.1 (el clasico) sale muy desequilibrado en
        # pyannote.audio 4.x -- en la prueba con el 5x21, el 99% del tiempo
        # se lo quedaba un solo hablante. community-1 es el pipeline pensado
        # para esta version de la libreria y da un reparto realista.
        _pipeline = Pipeline.from_pretrained('pyannote/speaker-diarization-community-1',
                                             token=token)
        if torch.backends.mps.is_available():
            _pipeline.to(torch.device('mps'))
    salida = _pipeline(str(wav), num_speakers=N_HABLANTES)
    # pyannote.audio 4.x devuelve un DiarizeOutput en vez de la Annotation de
    # las versiones 3.x; .exclusive_speaker_diarization es la pensada para
    # esto (no tiene solapes, un instante = un hablante).
    d = getattr(salida, 'exclusive_speaker_diarization', salida)
    return [{'inicio': t.start, 'fin': t.end, 'hablante': etiq}
            for t, _, etiq in d.itertracks(yield_label=True)]


def asignar_hablantes(segmentos, turnos):
    """A cada segmento le pone el hablante con el que más se solapa."""
    for s in segmentos:
        mejor, solape_max = None, 0
        for t in turnos:
            solape = min(s['fin'], t['fin']) - max(s['inicio'], t['inicio'])
            if solape > solape_max:
                mejor, solape_max = t['hablante'], solape
        s['hablante'] = mejor or 'DESCONOCIDO'
    return segmentos


def mmss(s):
    s = int(s)
    if s >= 3600:
        return f'{s//3600}:{(s%3600)//60:02d}:{s%60:02d}'
    return f'{s//60:02d}:{s%60:02d}'


def procesar(ep, diarizacion=True):
    slug = ep['slug']
    destino = SALIDA / f'{slug}.json'
    if destino.exists():
        return 'ya estaba'

    mp3 = AUDIO / f'{slug}.mp3'
    wav = AUDIO / f'{slug}.wav'
    if not descargar(ep['url_audio'], mp3):
        return 'error de descarga'
    if not a_wav16k(mp3, wav):
        return 'error de conversión'

    t0 = time.time()
    segmentos = transcribir(wav)
    log(f'  transcrito: {len(segmentos)} segmentos en {time.time()-t0:.0f}s')

    if diarizacion:
        try:
            t1 = time.time()
            turnos = diarizar(wav)
            segmentos = asignar_hablantes(segmentos, turnos)
            log(f'  diarizado: {len(turnos)} turnos en {time.time()-t1:.0f}s')
        except Exception as e:
            log(f'  AVISO: diarización fallida ({e}). Guardo sin hablantes.')

    salida = {'slug': slug, 'codigo': ep['codigo'], 'titulo': ep['titulo'],
              'fecha': ep['fecha'], 'video_id': ep['video_id'],
              'url_audio': ep['url_audio'], 'segmentos': segmentos}
    destino.write_text(json.dumps(salida, ensure_ascii=False, indent=1), encoding='utf-8')

    # versión legible, para poder ojearla sin abrir el JSON
    with open(SALIDA / f'{slug}.txt', 'w', encoding='utf-8') as f:
        f.write(f"{ep['codigo']} — {ep['titulo']} ({ep['fecha']})\n\n")
        actual = None
        for s in segmentos:
            h = s.get('hablante', '')
            if h != actual:
                f.write(f'\n[{mmss(s["inicio"])}] {h}\n')
                actual = h
            f.write(s['texto'] + ' ')

    try:  # el WAV pesa mucho y ya no hace falta
        wav.unlink(missing_ok=True)
    except OSError:
        pass
    return 'ok'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--limite', type=int, default=None)
    p.add_argument('--solo', type=str, default=None, help='código de episodio, p. ej. 5x21')
    p.add_argument('--sin-diarizar', action='store_true')
    p.add_argument('--conservar-audio', action='store_true')
    args = p.parse_args()

    AUDIO.mkdir(exist_ok=True)
    SALIDA.mkdir(exist_ok=True)
    eps = json.loads(MANIFIESTO.read_text(encoding='utf-8'))

    if args.solo:
        eps = [e for e in eps if e['codigo'] == args.solo]
        if not eps:
            sys.exit(f'No encuentro el episodio {args.solo}')
    pendientes = [e for e in eps if not (SALIDA / f"{e['slug']}.json").exists()]
    if args.limite:
        pendientes = pendientes[:args.limite]

    horas = sum(e['duracion_s'] or 0 for e in pendientes) / 3600
    log(f'motor: {"mlx-whisper (GPU Apple)" if es_apple_silicon() else "faster-whisper (CPU)"}')
    log(f'pendientes: {len(pendientes)} episodios ({horas:.1f} h de audio)')

    for i, ep in enumerate(pendientes, 1):
        log(f"[{i}/{len(pendientes)}] {ep['codigo'] or '(sin código)'} — {ep['titulo'][:55]}")
        try:
            log(f'  → {procesar(ep, diarizacion=not args.sin_diarizar)}')
        except KeyboardInterrupt:
            log('interrumpido; vuelve a lanzarlo para continuar')
            break
        except Exception as e:
            log(f'  ERROR: {type(e).__name__}: {e}')
        if not args.conservar_audio:
            try:
                (AUDIO / f"{ep['slug']}.mp3").unlink(missing_ok=True)
            except OSError:
                pass

    hechos = len(list(SALIDA.glob('*.json')))
    log(f'listo. transcripciones completas: {hechos}/{len(json.loads(MANIFIESTO.read_text()))}')


if __name__ == '__main__':
    main()

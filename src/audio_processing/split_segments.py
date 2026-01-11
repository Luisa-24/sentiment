r"""
Corte de un archivo de audio WAV en clips según segmentos definidos en JSON.

Este módulo lee un archivo de audio en formato WAV y un archivo JSON con una
lista de segmentos (cada uno con los campos `start` y `end` en segundos), y
exporta cada segmento como un nuevo archivo WAV en un directorio de salida.

Formato del JSON esperado:
[
    {"start": 0.500, "end": 3.200, "speaker": "SPEAKER_00"},
    {"start": 4.000, "end": 6.250, "speaker": "SPEAKER_01"},
    ...
]

Parameters (CLI)
----------------
--audio : str, opcional
    Ruta del archivo WAV original. Por defecto: "data/raw/audio.wav".
--segments : str, opcional
    Ruta del archivo JSON con los segmentos (claves `start` y `end` en segundos).
    Por defecto: "data/output/audio_diarizado.json".
--outdir : str, opcional
    Directorio de salida para los archivos WAV resultantes. Por defecto:
    "data/output/parts".

Returns
-------
None
    El script se ejecuta como programa principal, genera varios archivos WAV en
    el directorio de salida y muestra información por consola.

Notes
-----
- El corte se realiza con `pydub.AudioSegment` usando índices en milisegundos.
- Los archivos generados se nombran como `part_{idx}.wav`, donde `idx` es el
    índice del segmento en el JSON.
- El JSON puede incluir otras claves (por ejemplo, `speaker`), pero este script
    solo utiliza `start` y `end` para recortar; no renombra archivos por hablante.
- Se crean directorios intermedios si no existen.

Examples
--------
Ejecutar desde la línea de comandos:

    python src/split_segments.py --audio data/raw/audio.wav --segments data/output/audio_diarizado.json --outdir data/output/parts
"""

import argparse
import json
import os
from pydub import AudioSegment


def main():
    r"""
    Punto de entrada del script: corta el audio original en clips según un JSON de segmentos.

    Este flujo:
    1. Lee argumentos de línea de comandos (audio, segments, outdir).
    2. Crea el directorio de salida si no existe.
    3. Carga el audio WAV con `pydub.AudioSegment.from_wav`.
    4. Abre y parsea el archivo JSON que contiene una lista de segmentos.
    5. Por cada segmento:
        - Convierte `start` y `end` (en segundos) a milisegundos (`int(...) * 1000`).
        - Recorta el intervalo correspondiente del audio.
        - Exporta el clip en WAV a `outdir` con nombre `part_{idx}.wav`.
        - Imprime por consola el archivo exportado y su duración.
    6. Finaliza tras procesar todos los segmentos.

    Parameters
    ----------
    None
        Los parámetros se obtienen vía `argparse` desde la línea de comandos.

    Returns
    -------
    None
        Genera archivos WAV en el directorio de salida y muestra información por consola.

    Raises
    ------
    FileNotFoundError
        Si el archivo de audio o el archivo JSON de segmentos no existen.
    json.JSONDecodeError
        Si el archivo JSON no puede parsearse (formato inválido).
    KeyError
        Si algún segmento no contiene las claves `start` o `end`.
    ValueError
        Si `start` o `end` no son numéricos o `end < start`.
    OSError
        Si ocurre un error al crear directorios o exportar los clips WAV.

    Notes
    -----
    - Los índices de corte en `pydub` están basados en milisegundos; por ello
      se realiza la conversión: `start_ms = int(seg["start"] * 1000)`.
    - Este script no valida solapamientos ni continuidad entre segmentos; se
        limita a recortar exactamente los intervalos indicados.
    - Si deseas nombrar los archivos con la etiqueta del hablante, puedes
        extender el nombre de salida usando `seg.get("speaker", "unknown")`.

    Examples
    --------2
    >>> # En consola:
    >>> python src/split_segments.py --audio data/raw/audio.wav --segments data/output/audio_diarizado.json --outdir data/output/parts
    """

    parser = argparse.ArgumentParser(description="Cortar audio según segmentos JSON")
    parser.add_argument("--audio", default="data/raw/audio.wav", help="Ruta del audio .wav original")
    parser.add_argument("--segments", default="data/output/audio_diarizado.json", help="Ruta JSON con segmentos (start/end)")
    parser.add_argument("--outdir", default="data/output/parts", help="Directorio de salida para las partes .wav")
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    audio = AudioSegment.from_wav(args.audio)

    with open(args.segments, "r", encoding="utf-8") as f:
        data = json.load(f)

    for idx, seg in enumerate(data):
        start_ms = int(seg["start"] * 1000)
        end_ms = int(seg["end"] * 1000)
        clip = audio[start_ms:end_ms]
        out_path = os.path.join(args.outdir, f"part_{idx}.wav")
        clip.export(out_path, format="wav")
        print(f"Exportado: {out_path} (duración: {(end_ms-start_ms)/1000:.3f}s)")


if __name__ == "__main__":
    main()

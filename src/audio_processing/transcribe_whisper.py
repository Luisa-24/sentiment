r"""
Transcripcion de clips WAV con Whisper (ejecucion local) y salida en JSON.

Soporta transcripcion en INGLES y ESPAÑOL.
Auto-detecta el idioma del audio automaticamente.

Este modulo recorre un directorio con archivos de audio en formato WAV
segmentados (por ejemplo, `part_0.wav`, `part_1.wav`, ...), los transcribe con
un modelo Whisper local, y guarda un archivo JSON con la transcripcion de cada
clip. Los archivos se ordenan por su indice extraido del nombre (`part_{n}.wav`)
para conservar el orden original de segmentacion.

Formato del JSON de salida:
[
    {"index": 0, "text": "Texto transcrito del clip 0"},
    {"index": 1, "text": "Texto del clip 1"},
    ...
]

Parameters (CLI)
----------------
--parts : str, opcional
    Directorio que contiene las partes WAV con nombre `part_{idx}.wav`.
    Por defecto: "data/output/parts".
--outfile : str, opcional
    Ruta del archivo JSON de salida con las transcripciones.
    Por defecto: "data/output/transcriptions.json".
--model : str, opcional
    Tamaño del modelo Whisper a usar: {"tiny", "base", "small", "medium", "large"}.
    Por defecto: "small".
--language : str, opcional
    Codigo de idioma ISO (ej: es, en). Si es None, auto-detecta automaticamente.
    Por defecto: None (auto-detecta).
--min_seconds : float, opcional
    Duracion minima (en segundos) para intentar la transcripcion. Los clips
    mas cortos seran marcados con texto vacio. Por defecto: 0.1.

Returns
-------
None
    El script se ejecuta como programa principal: genera un JSON con
    transcripciones y muestra progreso por consola.

Examples
--------
Auto-detectar idioma:

    python src/transcribe_whisper.py --parts data/output/parts --outfile data/output/transcriptions.json --model small

Especificar idioma manualmente:

    python src/transcribe_whisper.py --parts data/output/parts --language en --model small
    python src/transcribe_whisper.py --parts data/output/parts --language es --model small
"""

import argparse
import json
import os
import re
from pydub import AudioSegment
import whisper



def extract_index(filename):
    r"""
    Extrae el indice numerico de un nombre de archivo con el patron `part_{n}.wav`.
    """
    m = re.search(r"part_(\d+)\.wav$", filename)
    return int(m.group(1)) if m else None


def detect_language_from_audio(model, audio_path):
    """
    Detecta el idioma de un archivo de audio usando Whisper.
    
    Parameters
    ----------
    model : whisper.model
        Modelo Whisper cargado
    audio_path : str
        Ruta del archivo de audio
    
    Returns
    -------
    str
        Codigo de idioma detectado (ej: 'en', 'es')
    """
    try:
        # Transcribir sin especificar idioma para que Whisper lo detecte
        result = model.transcribe(audio_path)
        detected_lang = result.get('language', 'en')
        return detected_lang
    except Exception as e:
        print(f"Error detectando idioma: {e}. Usando ingles por defecto.")
        return 'en'


def main():
    r"""
    Punto de entrada del script: transcribe clips WAV con Whisper y guarda JSON.

    Soporta auto-deteccion de idioma (ingles o español).

    Este flujo:
    1. Lee argumentos de linea de comandos (parts, outfile, model, language, min_seconds).
    2. Carga el modelo Whisper especificado.
    3. Si no se especifica idioma, detecta el idioma del primer clip.
    4. Lista y ordena los archivos `.wav` del directorio `--parts`.
    5. Para cada archivo:
        - Carga el clip y calcula su duracion en segundos.
        - Si la duracion es menor que `min_seconds`, lo marca con texto vacio.
        - En caso contrario, ejecuta `model.transcribe()` con el idioma detectado/especificado.
        - Agrega `{"index": idx, "text": text}` a la lista de resultados.
    6. Crea directorios intermedios si no existen y escribe el JSON de salida.

    Returns
    -------
    None
        Genera un archivo JSON con las transcripciones.
    """

    parser = argparse.ArgumentParser(description="Transcribir partes .wav con Whisper local (ingles y espanol)")
    parser.add_argument("--parts", default="data/output/parts", help="Directorio con partes .wav (part_#.wav)")
    parser.add_argument("--outfile", default="data/output/transcriptions.json", help="Ruta JSON de salida")
    parser.add_argument("--model", default="small", help="Modelo Whisper: tiny/base/small/medium/large")
    parser.add_argument("--language", default="en", help="Codigo idioma (es, en). Si es None, auto-detecta.")
    parser.add_argument("--min_seconds", type=float, default=0.1, help="Duracion minima para transcribir")
    args = parser.parse_args()

    print(f"Cargando modelo Whisper: {args.model} ...")
    model = whisper.load_model(args.model)

    files = [f for f in os.listdir(args.parts) if f.endswith(".wav")]
    files = sorted(files, key=lambda x: extract_index(x) if extract_index(x) is not None else 1e9)

    # Auto-detectar idioma si no se especifica
    language = args.language
    if language is None and files:
        print(f"Auto-detectando idioma del primer clip ...")
        first_path = os.path.join(args.parts, files[0])
        language = detect_language_from_audio(model, first_path)
        print(f"Idioma detectado: {language}")
    elif language is None:
        print("Advertencia: no hay clips para detectar idioma. Usando ingles por defecto.")
        language = "en"

    results = []
    for i, fname in enumerate(files):
        path = os.path.join(args.parts, fname)
        idx = extract_index(fname)
        print(f"[{i+1}/{len(files)}] Procesando {fname} ...")

        # Medir duracion y filtrar
        clip = AudioSegment.from_wav(path)
        dur = len(clip) / 1000.0
        if dur < args.min_seconds:
            results.append({"index": idx, "text": ""})
            print(f"Saltado (muy corto: {dur:.3f}s)")
            continue

        # Transcribir con idioma detectado/especificado
        result = model.transcribe(path, language=language)
        text = result.get("text", "").strip()
        results.append({"index": idx, "text": text})
        print(f"OK (dur: {dur:.3f}s, idioma: {language})")

    os.makedirs(os.path.dirname(args.outfile), exist_ok=True)
    with open(args.outfile, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Transcripciones guardadas en: {args.outfile}")


if __name__ == "__main__":
    main()

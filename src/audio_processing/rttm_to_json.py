
r"""
Conversión de archivos RTTM a formato JSON con segmentos de diarización.

Este módulo lee un archivo RTTM que contiene información sobre segmentos
de audio y sus hablantes, y genera un archivo JSON con una lista de
diccionarios, cada uno representando un segmento con:
- Tiempo de inicio (`start`)
- Tiempo de fin (`end`)
- Etiqueta del hablante (`speaker`)

Parameters (CLI)
----------------
--rttm : str, opcional
    Ruta del archivo RTTM de entrada. Por defecto: "data/interim/audio.rttm".
--json : str, opcional
    Ruta del archivo JSON de salida. Por defecto: "data/output/audio.diarizado.json".

Returns
-------
None
    Este script se ejecuta como programa principal. Genera un archivo JSON
    y muestra un mensaje por consola.

Notes
-----
- El formato RTTM esperado sigue la convención estándar: cada línea comienza
  con `SPEAKER` y contiene campos como `start`, `duration` y `speaker_label`.
- El JSON resultante es una lista de objetos con claves: `start`, `end`, `speaker`.
- Se crean directorios intermedios si no existen.

Examples
--------
Ejecutar desde la línea de comandos:

    python src/rttm_to_json.py --rttm data/interim/audio.rttm --json data/output/audio_diarizado.json
"""

import argparse
import json
import os


def main():
    r"""
    Punto de entrada del script: convierte un archivo RTTM en un JSON de segmentos.

    Este flujo:
    1. Lee argumentos de línea de comandos (rttm, json).
    2. Abre el archivo RTTM y procesa cada línea para extraer:
        - Tiempo de inicio (`start`)
        - Duración (`duration`)
        - Calcula tiempo de fin (`end = start + duration`)
        - Etiqueta del hablante (`speaker`)
    3. Construye una lista de diccionarios con estos datos.
    4. Crea directorios intermedios si no existen.
    5. Escribe el resultado en un archivo JSON con indentación para legibilidad.
    6. Imprime un mensaje indicando la ruta del archivo generado y el total
        de segmentos procesados.

    Parameters
    ----------
    None
        Los parámetros se obtienen vía `argparse` desde la línea de comandos.

    Returns
    -------
    None
        Genera un archivo JSON y muestra información por consola.

    Raises
    ------
    FileNotFoundError
        Si el archivo RTTM no existe.
    OSError
        Si ocurre un error al crear directorios o escribir el archivo JSON.
    ValueError
        Si el formato del archivo RTTM no es válido o no contiene los campos esperados.

    Notes
    -----
    - El formato RTTM esperado tiene índices fijos: `start` en posición 3,
        `duration` en posición 4 y `speaker_label` en posición 7.
    - El JSON resultante es útil para integraciones con sistemas que requieren
        datos estructurados para análisis o visualización.

    Examples
    --------
    >>> # En consola:
    >>> python src/rttm_to_json.py --rttm data/interim/audio.rttm --json data/output/audio_diarizado.json

    """
    parser = argparse.ArgumentParser(description="Convertir RTTM a JSON de segmentos")
    parser.add_argument("--rttm", default="data/interim/audio.rttm", help="Ruta del archivo RTTM")
    parser.add_argument("--json", default="data/output/audio.diarizado.json", help="Ruta de salida JSON")
    args = parser.parse_args()

    segments = []
    with open(args.rttm, "r") as f:
        for line in f:
            parts = line.strip().split()
            # Formato RTTM: SPEAKER file channel start duration ...
            # Índices típicos: start=3, duration=4, speaker_label=7
            start = float(parts[3])
            duration = float(parts[4])
            end = start + duration
            speaker = parts[7]
            segments.append({
                "start": start,
                "end": end,
                "speaker": speaker
                
            })

    os.makedirs(os.path.dirname(args.json), exist_ok=True)
    with open(args.json, "w", encoding="utf-8") as out:
        json.dump(segments, out, ensure_ascii=False, indent=2)

    print(f"Guardado JSON de segmentos en: {args.json}. Total: {len(segments)}")


if __name__ == "__main__":
    main()

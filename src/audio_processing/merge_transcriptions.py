
r"""
Unión de transcripciones con segmentos diarizados en un JSON final.

Este módulo toma:
1) Un archivo JSON con segmentos de diarización (cada elemento debe incluir
    al menos `start`, `end` y `speaker`).
2) Un archivo JSON con transcripciones (cada elemento con claves `index` y `text`,
    donde `index` corresponde al número del clip, e.g., `part_{index}.wav`).
Luego, ordena las transcripciones por `index` y las inserta, en orden, en los
segmentos, agregando la clave `transcription` a cada segmento. El resultado se
guarda en un archivo JSON final.

Formato esperado de entrada:
- `segments` (lista de dicts):
[
    {"start": 0.50, "end": 3.20, "speaker": "SPEAKER_00"},
    {"start": 4.00, "end": 6.25, "speaker": "SPEAKER_01"},
    ...
]
- `transcriptions` (lista de dicts):
[
    {"index": 0, "text": "Texto transcrito del clip 0"},
    {"index": 1, "text": "Texto transcrito del clip 1"},
    ...
]

Parameters (CLI)
----------------
--segments : str, requerido
    Ruta del archivo JSON que contiene la lista de segmentos con `start`, `end`, `speaker`.
--transcriptions : str, requerido
    Ruta del archivo JSON con objetos `{index, text}`.
--outfile : str, requerido
    Ruta de salida del archivo JSON final con la unión de segmentos + transcripción.

Returns
-------
None
    Este script se ejecuta como programa principal. Genera un archivo JSON de salida
    y muestra un mensaje por consola.

Notes
-----
- Las transcripciones se ordenan por `index` antes de unirse a los segmentos.
- Si el número de transcripciones difiere del número de segmentos, se imprime una
    advertencia. La unión continúa asignando por posición: si faltan transcripciones,
    la clave `transcription` se rellena con cadena vacía.
- Se crean directorios intermedios para `--outfile` si no existen.
- Este módulo asume que el orden de los segmentos corresponde al orden esperado
    de las transcripciones (e.g., mismo índice/posición que en `split_segments.py`).

Examples
--------
Ejecutar desde la línea de comandos:

    python src/merge_transcriptions.py --segments data/output/audio_diarizado.json --transcriptions data/output/transcriptions.json --outfile data/output/audio_diarizado_transcribed.json
"""

import argparse
import json
import os

def main():
    r"""
    Punto de entrada del script: une transcripciones con segmentos diarizados.

    Este flujo:
    1. Lee argumentos de línea de comandos: `segments`, `transcriptions`, `outfile`.
    2. Abre y carga el JSON de segmentos y el JSON de transcripciones.
    3. Ordena las transcripciones por `index` (entero).
    4. Verifica si el conteo de transcripciones coincide con el de segmentos; si no,
        muestra una advertencia y continúa.
    5. Inserta la clave `transcription` en cada segmento, tomando el texto de la
        transcripción correspondiente por posición; si no hay transcripción, usa "".
    6. Crea el directorio de salida (si no existe) y escribe el JSON final.
    7. Imprime por consola la ruta de salida.

    Parameters
    ----------
    None
        Los parámetros se obtienen vía `argparse` desde la línea de comandos.

    Returns
    -------
    None
        Genera un archivo JSON final y muestra información por consola.

    Raises
    ------
    FileNotFoundError
        Si `--segments` o `--transcriptions` no existen.
    json.JSONDecodeError
        Si alguno de los archivos JSON no tiene formato válido.
    KeyError
        Si los elementos de `transcriptions` no contienen las claves `index` o `text`,
        o si los segmentos carecen de `start`/`end`/`speaker`.
    ValueError
        Si `index` no puede convertirse a entero durante el ordenamiento.
    OSError
        Si ocurre un error al crear directorios o escribir el archivo de salida.

    Notes
    -----
    - La lógica de unión es por posición después de ordenar `transcriptions` por `index`,
        lo que asume correspondencia uno-a-uno con el orden de `segments`.
    - Si deseas unir por tiempos (`start`/`end`) en lugar de por orden, necesitarías
        una lógica de alineación temporal adicional (no implementada aquí).

    Examples
    --------
    >>> # En consola:
    >>> python src/merge_transcriptions.py --segments data/output/audio_diarizado.json --transcriptions data/output/transcriptions.json --outfile data/output/audio_diarizado_transcribed.json
    """

    parser = argparse.ArgumentParser(description="Unir transcripciones a segmentos diarizados")
    parser.add_argument("--segments", required=True, help="JSON con start/end/speaker")
    parser.add_argument("--transcriptions", required=True, help="JSON con {index, text}")
    parser.add_argument("--outfile", required=True, help="Ruta de salida JSON final")
    args = parser.parse_args()

    with open(args.segments, "r", encoding="utf-8") as f:
        segments = json.load(f)
    with open(args.transcriptions, "r", encoding="utf-8") as f:
        trans = json.load(f)

    # Asegurar orden por índice
    trans_sorted = sorted(trans, key=lambda x: int(x["index"]))

    if len(trans_sorted) != len(segments):
        print("ADVERTENCIA: El número de transcripciones y segmentos no coincide.")
        print(f"Segmentos: {len(segments)} | Transcripciones: {len(trans_sorted)}")
        # Continuamos, se asignarán por lo que exista.

    for i, seg in enumerate(segments):
        if i < len(trans_sorted):
            seg["transcription"] = trans_sorted[i]["text"]
        else:
            seg["transcription"] = ""

    os.makedirs(os.path.dirname(args.outfile), exist_ok=True)
    with open(args.outfile, "w", encoding="utf-8") as f:
        json.dump(segments, f, ensure_ascii=False, indent=2)

    print(f"JSON final guardado en: {args.outfile}")


if __name__ == "__main__":
    main()

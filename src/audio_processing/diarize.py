r"""
Módulo de diarización de hablantes con pyannote y exportación a RTTM.

Este módulo carga un archivo de audio en formato WAV, realiza diarización de
hablantes usando el modelo `pyannote/speaker-diarization-3.1`, y escribe los
segmentos detectados en un archivo RTTM. Además, imprime por consola un
resumen legible de los tramos y hablantes asignados.

Incluye:
- Manejo de token de HuggingFace para cargar el pipeline.
- Selección de dispositivo (`cpu`/`cuda`).
- Compatibilidad con distintas versiones de `pyannote.core` al generar RTTM.

Parameters (CLI)
----------------
--input : str, opcional
    Ruta del archivo de audio WAV de entrada. Por defecto: "data/raw/audio.wav".
--rttm : str, opcional
    Ruta de salida del archivo RTTM. Por defecto: "data/interim/audio.rttm".
--hf_token : str, opcional
    Token de acceso a HuggingFace. Por defecto se lee de la variable de entorno
    "HF_TOKEN".
--device : {"cpu", "cuda"}, opcional
    Dispositivo de ejecución para el pipeline. Por defecto: "cpu".

Returns
-------
None
    Este módulo se ejecuta como script. Escribe un archivo RTTM en disco y
    muestra salida por consola.

Notes
-----
- El archivo RTTM sigue el formato estándar: una línea por segmento con
    metadatos como inicio, duración y etiqueta de hablante.
- El pipeline `pyannote/speaker-diarization-3.1` requiere un token válido de
    HuggingFace para su descarga y uso.
- Para mejorar compatibilidad entre versiones de `pyannote.core`, la función
    `write_rttm_from_annotation` intenta usar `Annotation.to_rttm()` y, si no
    está disponible, aplica un método de escritura manual basado en `itertracks()`
    o iteración sobre pares `(turn, speaker)`.

Examples
--------
Ejecutar como script desde la línea de comandos:

    python src/diarize.py --input data/raw/audio.wav --rttm data/interim/audio.rttm --device cpu --hf_token "hf_tu token"
"""

import os
import argparse
import torch
import torchaudio
from pyannote.audio import Pipeline


def write_rttm_from_annotation(annotation, rttm_path: str):
    r"""
    Escribe un archivo RTTM a partir de un objeto `Annotation`.

    Esta función intenta serializar directamente la anotación usando
    `Annotation.to_rttm()` (cuando está disponible). Si la versión instalada
    de `pyannote.core` no provee ese método, realiza una escritura manual
    iterando sobre los segmentos y sus etiquetas de hablante.

    La función crea la carpeta de destino si no existe.

    Parameters
    ----------
    annotation : pyannote.core.Annotation
        Anotación de diarización que contiene segmentos (turnos) y sus
        etiquetas de hablante. Se recomienda que `annotation.uri` esté
        definido, ya que se incluye en el RTTM.
    rttm_path : str
        Ruta completa del archivo RTTM a generar. Se crearán directorios
        intermedios de ser necesario.

    Returns
    -------
    None
        Escribe el contenido en `rttm_path` y no retorna valor.

    Raises
    ------
    OSError
        Si ocurre un error al crear directorios o escribir el archivo.
    AttributeError
        Si la anotación no provee la interfaz esperada para iterar segmentos
        en el modo de compatibilidad (muy poco probable, pero posible con
        versiones inusuales).

    Notes
    -----
    - El formato RTTM generado utiliza líneas `SPEAKER` con los campos:
        `uri`, `channel` (fijado en 1), `start`, `duration` y `speaker`.
    - En el modo de compatibilidad, se calcula `duration = segment.end - segment.start`.
    - Si `annotation.uri` no está definido, se usa "unknown" como valor por defecto.

    Examples
    --------
    >>> # Supongamos que 'annotation' es una anotación válida y queremos
    >>> # escribir en 'data/interim/audio.rttm':
    >>> write_rttm_from_annotation(annotation, "data/interim/audio.rttm")
    """
    os.makedirs(os.path.dirname(rttm_path), exist_ok=True)
    try:
        # En algunas versiones de pyannote.core, to_rttm() no acepta argumentos
        rttm_str = annotation.to_rttm()
        with open(rttm_path, "w", encoding="utf-8") as f:
            f.write(rttm_str)
    except AttributeError:
        # Fallback manual si tu pyannote.core no trae to_rttm()
        with open(rttm_path, "w", encoding="utf-8") as f:
            # itertracks existe en Annotation legacy; en 4.x podemos iterar sobre (turn, speaker)
            try:
                for segment, _, speaker in annotation.itertracks(yield_label=True):
                    start = segment.start
                    duration = segment.end - segment.start
                    uri = annotation.uri or "unknown"
                    f.write(
                        f"SPEAKER {uri} 1 {start:.3f} {duration:.3f} <NA> <NA> {speaker} <NA> <NA>\n"
                    )
            except AttributeError:
                # Si itertracks no está, iterar como (turn, speaker) y usar track por defecto '_'
                for turn, speaker in annotation:
                    start = turn.start
                    duration = turn.end - turn.start
                    uri = annotation.uri or "unknown"
                    f.write(
                        f"SPEAKER {uri} 1 {start:.3f} {duration:.3f} <NA> <NA> {speaker} <NA> <NA>\n"
                    )


def main():
    r"""
    Punto de entrada del script: realiza diarización y escribe el archivo RTTM.

    Este flujo:
    1. Lee argumentos de línea de comandos (input, rttm, hf_token, device).
    2. Valida que exista un token de HuggingFace.
    3. Carga el audio WAV con `torchaudio.load` para evitar dependencias de
        `FFmpeg/torchcodec` al pasar directamente `waveform` y `sample_rate`
        al pipeline.
    4. Inicializa el pipeline de diarización (`pyannote/speaker-diarization-3.1`)
        y lo mueve al dispositivo indicado.
    5. Ejecuta la diarización y extrae el `Annotation` desde el resultado.
    6. Establece `annotation.uri` para incluir el nombre del archivo de audio
        en el RTTM.
    7. Llama a `write_rttm_from_annotation` para generar el archivo RTTM.
    8. Imprime en consola los tramos (inicio/fin) y el hablante asignado.

    Parameters
    ----------
    None
        Los parámetros se obtienen vía `argparse` desde la línea de comandos.

    Returns
    -------
    None
        Ejecuta la diarización, genera el archivo RTTM y muestra una salida
        por consola con los segmentos.

    Raises
    ------
    ValueError
        Si no se encuentra un token de HuggingFace (`HF_TOKEN`) vía entorno
        ni se proporciona mediante `--hf_token`.
    OSError
        Si el archivo de audio no existe, no se puede leer, o ocurre un error
        al escribir el archivo RTTM.
    RuntimeError
        Si el pipeline no puede inicializarse o ejecutarse correctamente.

    Notes
    -----
    - El pipeline `pyannote/speaker-diarization-3.1` requiere credenciales
        válidas; el token puede pasarse por `--hf_token` o vía variable de
        entorno `HF_TOKEN`.
    - El dispositivo puede ser "cpu" o "cuda"; usar "cuda" cuando haya GPU
        disponible puede acelerar la inferencia.

    Examples
    --------
    >>> # En consola:
    >>> # HF_TOKEN debe estar definido en el entorno o pasado explícitamente.
    >>> python src/diarize.py --input data/raw/audio.wav --rttm data/interim/audio.rttm --device cpu --hf_token "hf_tu token"
    """
    parser = argparse.ArgumentParser(description="Diarización con pyannote -> RTTM")
    parser.add_argument("--input", default="data/raw/audio.wav", help="Ruta del audio .wav de entrada")
    parser.add_argument("--rttm", default="data/interim/audio.rttm", help="Ruta de salida del archivo RTTM")
    parser.add_argument("--hf_token", default=os.getenv("HF_TOKEN"), help="HuggingFace token (opcional, por env)")
    parser.add_argument("--device", default="cpu", choices=["cpu", "cuda"], help="Dispositivo: cpu/cuda")
    args = parser.parse_args()

    if not args.hf_token:
        raise ValueError("HF_TOKEN no encontrado. Expórtalo o pásalo por --hf_token")

    # Pre-cargar audio para evitar torchcodec/FFmpeg
    waveform, sample_rate = torchaudio.load(args.input)

    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        token=args.hf_token
    )
    pipeline.to(torch.device(args.device))

    # En pyannote.audio 4.x, la salida es DiarizeOutput
    output = pipeline({"waveform": waveform, "sample_rate": sample_rate})

    # Tomar el Annotation de la salida
    annotation = output.speaker_diarization

    # Establecer el uri en la anotación (usado por to_rttm())
    annotation.uri = os.path.splitext(os.path.basename(args.input))[0]

    # Guardar RTTM
    write_rttm_from_annotation(annotation, args.rttm)

    # Imprimir por consola (API moderna 4.x)
    for turn, speaker in annotation:
        print(f"start={turn.start:.3f}s stop={turn.end:.3f}s speaker_{speaker}")


if __name__ == "__main__":
    main()

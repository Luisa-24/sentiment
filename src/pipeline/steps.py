"""Pipeline step definitions."""

import sys
from typing import List
from .executor import PipelineStep
from ..config.paths import ProjectPaths


def get_pipeline_steps(paths: ProjectPaths) -> List[PipelineStep]:
    """
    Get the complete list of pipeline steps.
    
    Parameters
    ----------
    paths : ProjectPaths
        Configured project paths
    
    Returns
    -------
    List[PipelineStep]
        List of all pipeline steps in execution order
    """
    return [
        PipelineStep(
            name="1. Diarización",
            command=[
                sys.executable,
                "src/audio_processing/diarize.py",
                "--input", str(paths.audio_wav),
                "--rttm", str(paths.rttm_file),
                "--device", "cpu"
            ],
            description="Identificando hablantes en el audio..."
        ),
        PipelineStep(
            name="2. Conversión RTTM a JSON",
            command=[
                sys.executable,
                "src/audio_processing/rttm_to_json.py",
                "--rttm", str(paths.rttm_file),
                "--json", str(paths.segments_json)
            ],
            description="Convirtiendo formato RTTM a JSON estructurado..."
        ),
        PipelineStep(
            name="3. Segmentación de Audio",
            command=[
                sys.executable,
                "src/audio_processing/split_segments.py",
                "--audio", str(paths.audio_wav),
                "--segments", str(paths.segments_json),
                "--outdir", str(paths.parts_dir)
            ],
            description="Dividiendo el audio en clips por cada segmento..."
        ),
        PipelineStep(
            name="4. Transcripcion con Whisper",
            command=[
                sys.executable,
                "src/audio_processing/transcribe_whisper.py",
                "--parts", str(paths.parts_dir),
                "--outfile", str(paths.transcriptions_json),
                "--model", "small"
            ],
            description="Transcribiendo cada clip con Whisper..."
        ),
        PipelineStep(
            name="5. Fusión de Transcripciones",
            command=[
                sys.executable,
                "src/audio_processing/merge_transcriptions.py",
                "--segments", str(paths.segments_json),
                "--transcriptions", str(paths.transcriptions_json),
                "--outfile", str(paths.final_json)
            ],
            description="Uniendo transcripciones con segmentos diarizados..."
        ),
        PipelineStep(
            name="6. Análisis de Sentimiento",
            command=[
                sys.executable,
                "src/analysis/emotions.py"
            ],
            description="Analizando el sentimiento de cada transcripción..."
        )
    ]

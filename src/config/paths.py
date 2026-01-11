"""Centralized path configuration for the audio processing pipeline."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ProjectPaths:
    """
    Container for all project file paths.
    
    Attributes
    ----------
    script_dir : Path
        Root directory of the project
    audio_mp3 : Path
        Input MP3 audio file
    audio_wav : Path
        Input WAV audio file (converted from MP3 if needed)
    rttm_file : Path
        Output RTTM file from diarization
    segments_json : Path
        JSON file with diarized segments
    parts_dir : Path
        Directory containing audio clips for each segment
    transcriptions_json : Path
        JSON file with transcriptions
    final_json : Path
        Final merged JSON with diarization and transcriptions
    sentiment_json : Path
        JSON file with sentiment analysis results
    """
    script_dir: Path
    audio_mp3: Path
    audio_wav: Path
    rttm_file: Path
    segments_json: Path
    parts_dir: Path
    transcriptions_json: Path
    final_json: Path
    sentiment_json: Path


def get_project_paths(script_dir: Path) -> ProjectPaths:
    """
    Create ProjectPaths instance with all configured paths.
    
    Parameters
    ----------
    script_dir : Path
        Root directory of the project
    
    Returns
    -------
    ProjectPaths
        Configured paths object
    """
    return ProjectPaths(
        script_dir=script_dir,
        audio_mp3=script_dir / "data" / "raw" / "audio.mp3",
        audio_wav=script_dir / "data" / "raw" / "audio.wav",
        rttm_file=script_dir / "data" / "interim" / "audio.rttm",
        segments_json=script_dir / "data" / "output" / "audio_diarizado.json",
        parts_dir=script_dir / "data" / "output" / "parts",
        transcriptions_json=script_dir / "data" / "output" / "transcriptions.json",
        final_json=script_dir / "data" / "output" / "audio_diarizado_transcribed.json",
        sentiment_json=script_dir / "data" / "output" / "sentiment_analysis.json",
    )

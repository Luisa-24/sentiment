"""Tests for config.paths module."""

from pathlib import Path
from src.config.paths import ProjectPaths, get_project_paths


def test_project_paths_initialization(tmp_path):
    """Test ProjectPaths can be initialized."""
    paths = ProjectPaths(
        script_dir=tmp_path,
        audio_mp3=tmp_path / "audio.mp3",
        audio_wav=tmp_path / "audio.wav",
        rttm_file=tmp_path / "audio.rttm",
        segments_json=tmp_path / "segments.json",
        parts_dir=tmp_path / "parts",
        transcriptions_json=tmp_path / "transcriptions.json",
        final_json=tmp_path / "final.json",
        sentiment_json=tmp_path / "sentiment.json"
    )
    
    assert paths.script_dir == tmp_path
    assert paths.audio_mp3 == tmp_path / "audio.mp3"


def test_get_project_paths_structure(tmp_path):
    """Test that get_project_paths returns correct structure."""
    paths = get_project_paths(tmp_path)
    
    assert paths.script_dir == tmp_path
    assert paths.audio_mp3 == tmp_path / "data" / "raw" / "audio.mp3"
    assert isinstance(paths.audio_wav, Path)

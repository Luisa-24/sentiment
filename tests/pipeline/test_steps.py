"""Tests for pipeline.steps module."""

from src.pipeline.steps import get_pipeline_steps
from src.pipeline.executor import PipelineStep
from src.config.paths import ProjectPaths


def test_get_pipeline_steps_returns_list(tmp_path):
    """Test that get_pipeline_steps returns a list."""
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
    
    steps = get_pipeline_steps(paths)
    
    assert isinstance(steps, list)
    assert len(steps) > 0
    assert all(isinstance(step, PipelineStep) for step in steps)

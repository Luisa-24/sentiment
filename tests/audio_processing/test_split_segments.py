"""Tests for audio_processing.split_segments module."""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock


@patch('src.audio_processing.split_segments.AudioSegment')
def test_split_segments_basic(mock_audio_segment, tmp_path):
    """Test básico para división de segmentos de audio."""
    segments = [
        {"start": 0.5, "end": 3.2, "speaker": "SPEAKER_00"},
        {"start": 3.2, "end": 6.0, "speaker": "SPEAKER_01"}
    ]
    
    audio_file = tmp_path / "audio.wav"
    segments_file = tmp_path / "segments.json"
    output_dir = tmp_path / "parts"
    
    audio_file.touch()
    segments_file.write_text(json.dumps(segments))
    
    mock_audio = MagicMock()
    mock_clip = MagicMock()
    mock_audio.__getitem__ = Mock(return_value=mock_clip)
    mock_audio_segment.from_wav.return_value = mock_audio
    
    with patch('sys.argv', ['split_segments.py',
                           '--audio', str(audio_file),
                           '--segments', str(segments_file),
                           '--outdir', str(output_dir)]):
        from src.audio_processing import split_segments
        split_segments.main()
    
    mock_audio_segment.from_wav.assert_called_once()
    assert mock_clip.export.call_count == 2

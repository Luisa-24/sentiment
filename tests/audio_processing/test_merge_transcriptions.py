"""Tests for audio_processing.merge_transcriptions module."""

import json
from pathlib import Path
from unittest.mock import patch


def test_merge_basic(tmp_path):
    """Test basic merging of transcriptions with segments."""
    segments = [
        {"start": 0.5, "end": 3.2, "speaker": "SPEAKER_00"},
        {"start": 3.2, "end": 6.0, "speaker": "SPEAKER_01"}
    ]
    transcriptions = [
        {"index": 0, "text": "First transcription"},
        {"index": 1, "text": "Second transcription"}
    ]
    
    segments_file = tmp_path / "segments.json"
    trans_file = tmp_path / "transcriptions.json"
    output_file = tmp_path / "output.json"
    
    segments_file.write_text(json.dumps(segments))
    trans_file.write_text(json.dumps(transcriptions))
    
    with patch('sys.argv', ['merge_transcriptions.py',
                           '--segments', str(segments_file),
                           '--transcriptions', str(trans_file),
                           '--outfile', str(output_file)]):
        from src.audio_processing import merge_transcriptions
        merge_transcriptions.main()
    
    with open(output_file) as f:
        result = json.load(f)
    
    assert len(result) == 2
    assert result[0]['transcription'] == 'First transcription'


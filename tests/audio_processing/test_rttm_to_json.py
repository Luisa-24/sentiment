"""Tests for audio_processing.rttm_to_json module."""

import json
from pathlib import Path
from unittest.mock import patch


def test_rttm_parsing_basic(tmp_path):
    """Test basico para parseo de RTTM."""
    rttm_content = "SPEAKER audio 1 0.500 2.700 <NA> <NA> SPEAKER_00 <NA> <NA>\n"
    rttm_file = tmp_path / "test.rttm"
    json_file = tmp_path / "output.json"
    rttm_file.write_text(rttm_content)
    
    with patch('sys.argv', ['rttm_to_json.py', '--rttm', str(rttm_file), '--json', str(json_file)]):
        from src.audio_processing import rttm_to_json
        rttm_to_json.main()
    
    assert json_file.exists()
    with open(json_file) as f:
        segments = json.load(f)
    
    assert len(segments) == 1
    assert segments[0]['start'] == 0.500
    assert segments[0]['speaker'] == 'SPEAKER_00'


def test_rttm_parsing_multiple_segments(tmp_path):
    """Test parseo de múltiples segmentos en RTTM."""
    rttm_content = """SPEAKER audio 1 0.500 2.700 <NA> <NA> SPEAKER_00 <NA> <NA>
SPEAKER audio 1 3.200 1.800 <NA> <NA> SPEAKER_01 <NA> <NA>
"""
    rttm_file = tmp_path / "test.rttm"
    json_file = tmp_path / "output.json"
    rttm_file.write_text(rttm_content)
    
    with patch('sys.argv', ['rttm_to_json.py', '--rttm', str(rttm_file), '--json', str(json_file)]):
        from src.audio_processing import rttm_to_json
        rttm_to_json.main()
    
    with open(json_file) as f:
        segments = json.load(f)
    
    assert len(segments) == 2
    assert segments[0]['speaker'] == 'SPEAKER_00'
    assert segments[1]['speaker'] == 'SPEAKER_01'

"""Tests for audio_processing.transcribe_whisper module."""

from unittest.mock import patch, MagicMock
from src.audio_processing.transcribe_whisper import extract_index, detect_language_from_audio


def test_extract_index_valid():
    """Test de estracción de índice válido."""
    
    assert extract_index("part_0.wav") == 0
    assert extract_index("part_5.wav") == 5
    assert extract_index("part_123.wav") == 123


@patch('src.audio_processing.transcribe_whisper.whisper')
def test_detect_language_success(mock_whisper):
    
    """Test detección exitosa de idioma."""
    mock_model = MagicMock()
    mock_model.transcribe.return_value = {'language': 'en', 'text': 'Hello'}
    
    result = detect_language_from_audio(mock_model, 'test.wav')
    
    assert result == 'en'
    mock_model.transcribe.assert_called_once()

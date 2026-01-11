"""Tests for audio_processing.converter module."""

from pathlib import Path
from unittest.mock import patch, MagicMock
from src.audio_processing.converter import convert_mp3_to_wav, ensure_wav_audio


@patch('pydub.AudioSegment')
def test_convert_mp3_to_wav_success(mock_audio_segment):
    """Test conversión exitosa de MP3 a WAV."""
    mp3_path = Path("test_audio.mp3")
    wav_path = Path("test_audio.wav")
    mock_audio = MagicMock()
    mock_audio_segment.from_mp3.return_value = mock_audio
    
    result = convert_mp3_to_wav(mp3_path, wav_path)
    
    assert result is True
    mock_audio_segment.from_mp3.assert_called_once_with(str(mp3_path))


@patch('src.audio_processing.converter.convert_mp3_to_wav')
def test_ensure_wav_audio_converts_from_mp3(mock_convert, tmp_path):
    """Test conversión desde MP3 cuando WAV no existe."""
    audio_mp3 = tmp_path / "audio.mp3"
    audio_wav = tmp_path / "audio.wav"
    audio_mp3.touch()
    mock_convert.return_value = True
    
    result = ensure_wav_audio(audio_mp3, audio_wav)
    
    assert result is True



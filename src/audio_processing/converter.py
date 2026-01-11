"""Audio format conversion utilities."""

from pathlib import Path
from typing import Optional


def convert_mp3_to_wav(mp3_path: Path, wav_path: Path) -> bool:
    """
    Convert an MP3 file to WAV format using pydub.
    
    Parameters
    ----------
    mp3_path : Path
        Path to input MP3 file
    wav_path : Path
        Path to output WAV file
    
    Returns
    -------
    bool
        True if conversion was successful, False otherwise
    """
    try:
        from pydub import AudioSegment
        print(f"Convirtiendo {mp3_path} a {wav_path}...")
        audio = AudioSegment.from_mp3(str(mp3_path))
        audio.export(str(wav_path), format="wav")
        print(f" Conversion completada: {wav_path}")
        return True
    except Exception as e:
        print(f" Error al convertir MP3 a WAV: {e}")
        return False


def ensure_wav_audio(audio_mp3: Path, audio_wav: Path) -> bool:
    """
    Ensure WAV audio file exists, converting from MP3 if necessary.
    
    Parameters
    ----------
    audio_mp3 : Path
        Path to MP3 file (fallback if WAV doesn't exist)
    audio_wav : Path
        Path to required WAV file
    
    Returns
    -------
    bool
        True if WAV file exists or was successfully created, False otherwise
    """
    if audio_wav.exists():
        print(f" Archivo WAV encontrado: {audio_wav}")
        return True
    
    if audio_mp3.exists():
        print(f"\n{'='*80}")
        print("PASO: 0. Conversión de Audio")
        print(f"{'='*80}")
        print(f"Archivo WAV no encontrado. Convirtiendo desde MP3...\n")
        return convert_mp3_to_wav(audio_mp3, audio_wav)
    
    print(f"\n Error: No se encontro el archivo de audio")
    print(f"  Buscado en: {audio_wav}")
    print(f"  Buscado en: {audio_mp3}")
    print("Por favor, coloca tu archivo de audio (WAV o MP3) en data/raw/")
    return False

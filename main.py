"""
Pipeline completo de procesamiento de audio: diarizacion, transcripcion y analisis de sentimiento.

Este script ejecuta el pipeline completo en el siguiente orden:
1. Diarizacion: Identifica los hablantes en el audio usando pyannote
2. Conversion RTTM a JSON: Convierte el formato RTTM a JSON estructurado
3. Segmentacion: Divide el audio en clips por cada segmento
4. Transcripcion: Transcribe cada clip usando Whisper
5. Fusion: Une las transcripciones con los segmentos diarizados
6. Analisis de sentimiento: Analiza el sentimiento de cada transcripcion

Uso:
    python main.py
"""


import os
import sys
from pathlib import Path
from src.config import setup_environment, get_project_paths
from src.audio_processing.converter import ensure_wav_audio
from src.pipeline import get_pipeline_steps, run_pipeline
from src.utils import cleanup_folders


def get_script_dir():
    """Obtiene el directorio donde esta ubicado el script."""
    return Path(__file__).parent.resolve()


def main():
    """Ejecuta el pipeline completo de procesamiento de audio."""
    print("="*80)
    print("PIPELINE DE PROCESAMIENTO DE AUDIO")
    print("="*80)
    
    # Cambiar al directorio del script
    script_dir = get_script_dir()
    os.chdir(script_dir)
    print(f"\n Directorio de trabajo: {script_dir}\n")
    
    # Limpiar archivos de ejecuciones previas
    cleanup_folders(script_dir)
    
    # Configurar entorno
    setup_environment(script_dir)
    
    # Obtener todas las rutas del proyecto
    paths = get_project_paths(script_dir)
    
    # Verificar y convertir audio de entrada si es necesario
    if not ensure_wav_audio(paths.audio_mp3, paths.audio_wav):
        return False
    
    # Obtener los pasos del pipeline
    steps = get_pipeline_steps(paths)
    
    # Ejecutar el pipeline
    success = run_pipeline(steps)
    
    if success:
        print(f"\n{'='*80}")
        print(" PIPELINE COMPLETADO EXITOSAMENTE")
        print(f"{'='*80}\n")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

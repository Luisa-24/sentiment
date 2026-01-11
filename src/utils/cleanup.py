"""
Utilidades para limpieza de archivos y carpetas del pipeline.
"""

import shutil
from pathlib import Path


def cleanup_folders(script_dir):
    """
    Limpia carpetas y archivos de ejecuciones previas.
    
    Parameters
    ----------
    script_dir : Path
        Directorio raíz del proyecto donde se ejecuta el script
    """
    # Carpetas a limpiar completamente
    folders_to_clean = [
        script_dir / "data" / "interim",
        script_dir / "data" / "output" / "parts"
    ]
    
    # Archivos especificos a eliminar en data/output
    files_to_clean = [
        script_dir / "data" / "output" / "audio_diarizado.json",
        script_dir / "data" / "output" / "audio_diarizado_transcribed.json",
        script_dir / "data" / "output" / "transcriptions.json",
        script_dir / "data" / "output" / "sentiment_analysis.json"
    ]
    
    print(f"\n{'='*80}")
    print("LIMPIEZA DE ARCHIVOS PREVIOS")
    print(f"{'='*80}")
    
    # Limpiar carpetas
    for folder in folders_to_clean:
        if folder.exists():
            # Eliminar contenido pero mantener la carpeta
            for item in folder.iterdir():
                try:
                    if item.is_file():
                        item.unlink()
                        print(f" Eliminado: {item.relative_to(script_dir)}")
                    elif item.is_dir():
                        shutil.rmtree(item)
                        print(f" Eliminado directorio: {item.relative_to(script_dir)}")
                except Exception as e:
                    print(f" No se pudo eliminar {item.relative_to(script_dir)}: {e}")
        else:
            # Crear la carpeta si no existe
            folder.mkdir(parents=True, exist_ok=True)
            print(f" Carpeta creada: {folder.relative_to(script_dir)}")
    
    # Limpiar archivos especificos
    for file in files_to_clean:
        if file.exists():
            try:
                file.unlink()
                print(f" Eliminado: {file.relative_to(script_dir)}")
            except Exception as e:
                print(f"No se pudo eliminar {file.relative_to(script_dir)}: {e}")
    
    print(" Limpieza completada\n")

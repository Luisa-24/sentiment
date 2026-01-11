## Cómo ejecutar el pipeline completo

### 1. Diarización (identificar hablantes)
Desde el directorio `interview-main\interview-main\`, ejecutar:

```powershell
# Configurar el token de HuggingFace (obtener en https://huggingface.co/settings/tokens)
$env:HF_TOKEN = "your_huggingface_token_here"

# Ejecutar la diarización
python src/diarize.py --input data/raw/audio.wav --rttm data/interim/audio.rttm --device cpu
```

**Resultado:** Se genera el archivo `data/interim/audio.rttm` con los segmentos de cada hablante.

### 2. Transcripción con Whisper
Desde el mismo directorio, ejecutar:

```powershell
# Configurar FFmpeg en el PATH
$env:PATH = "$env:PATH;$(Resolve-Path .\engines\ffmpeg-2026-01-05-git-2892815c45-full_build\bin)"

# Ejecutar la transcripción
python src/transcribe_whisper.py
```

**Resultado:** Se generan las transcripciones en `data/output/`.

### Notas importantes

- Para ejecutar 'src/diarize.py' debes tener creado el token y usarlo a la hora de ejecutar el modulo

- Antes de ejecutar 'src/transcribe_whisper.py debes ejecutar en la terminal el comando: $env:PATH = "$env:PATH;$(Resolve-Path .\engines\ffmpeg-2026-01-05-git-2892815c45-full_build\bin)"

- Debes tener el acceso a las siguientes paginas:
    * https://huggingface.co/pyannote/segmentation-3.0
    * https://huggingface.co/pyannote/speaker-diarization-3.1
    * https://huggingface.co/pyannote/speaker-diarization-community-1

- El siguiente es el repositorio del motor de whisper (Pero no lo usamos, lo importamos):
    * https://github.com/openai/whisper

- Repositorio en github de pyannote:
    * https://github.com/pyannote/pyannote-audio

- Repositorio en huggingface de pyannote con pretrained models and pipelines:
    * https://huggingface.co/pyannote

- En el repositorio no encontraras la carpeta '.\engines\ffmpeg-2026-01-05-git-2892815c45-full_build' debes crear el folder 'engines' y descomprimir la descarga del archivo 'ffmpeg-git-essentials.7z' realizada desde https://www.gyan.dev/ffmpeg/builds/


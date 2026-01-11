```mermaid
flowchart TD
    A[¿Audio disponible?] --> B[SI]
    A-->C[NO]
    C --> D{ERROR}
    B --> E[DE MP3 A WAV ]
    E --> F[DIARIZACIÓN]
    F--> G[SEGMENTACION]
    G--> H[TRANSCRIPCIÓN]
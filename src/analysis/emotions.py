"""
[En] Análisis de Sentimiento sobre Transcripciones usando spaCy + TextBlob
======================================================================

Este módulo analiza el sentimiento de cada segmento transcrito del audio,
usando spaCy con la extensión SpacyTextBlob para obtener polaridad y 
subjetividad de cada texto.

Uso:
    python src/analysis/emotions.py

Salida:
    data/output/sentiment_analysis.json
"""

import json
import os
from datetime import datetime
import spacy
from spacytextblob.spacytextblob import SpacyTextBlob


def load_diarized_transcriptions(path: str) -> list:
    """
    Carga las transcripciones diarizadas desde un archivo JSON.
    
    Args:
        Ruta al archivo JSON con las transcripciones diarizadas.
    
    Returns:
        Lista de diccionarios con las transcripciones.
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def analyze_sentiment(nlp, text: str) -> dict:
    """
    Analiza el sentimiento de un texto usando spaCy + TextBlob.
    
    Args:
        nlp : spacy.Language
            Pipeline de spaCy con SpacyTextBlob.
        text : str
            Texto a analizar.
    
    Returns
    -------
    dict
        Diccionario con label y score del sentimiento.
    """
    doc = nlp(text)
    
    polarity = doc._.blob.polarity  # -1 (negativo) a 1 (positivo)
    
    # Clasificar el sentimiento
    if polarity > 0.1:
        label = "POSITIVE"
    elif polarity < -0.1:
        label = "NEGATIVE"
    else:
        label = "NEUTRAL"
    
    # Normalizar score a 0-1
    score = (polarity + 1) / 2  # Convertir de [-1,1] a [0,1]
    
    return {
        "label": label,
        "score": round(score, 2)
    }


def detect_role(text: str, speaker: str, prev_speaker: str, language: str = "en") -> str:
    """ Detecta si el segmento es una pregunta o respuesta basandose en el contenido
     
     Args: Texto del segmento, codigo del hablante actual, codigo del hablante previo, idioma
     Returns: 'question' o 'answer'"""
    
    text_lower = text.lower().strip()
    
    # Palabras interrogativas segun idioma
    if language == "es":
        interrogativas = ["qué", "cómo", "cuándo", "donde", "por qué", "cuál", "quién"]
    else:  # ingles
        interrogativas = ["what", "how", "when", "where", "why", "which", "who"]
    
    # Si termina en ? es pregunta
    if text_lower.endswith("?"):
        return "question"
    
    # Si contiene palabras interrogativas al inicio, es pregunta
    first_words = text_lower.split()[:3]
    for word in first_words:
        word_clean = word.rstrip("?,").lower()
        if any(q in word_clean for q in interrogativas):
            return "question"
    
    return "answer"


def main():
    """
    Función principal que ejecuta el análisis de sentimiento.
    """
    # Rutas - usar ruta relativa desde interview-main/interview-main
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    
    input_path = os.path.join(project_root, "data", "output", "audio_diarizado_transcribed.json")
    output_path = os.path.join(project_root, "data", "output", "sentiment_analysis.json")
    
    print("Cargando modelos de spaCy para ambos idiomas...")
    
    # Cargar ambos modelos
    try:
        nlp_en = spacy.load("en_core_web_sm")
    except OSError:
        print("Descargando modelo de spaCy para inglés...")
        os.system("python -m spacy download en_core_web_sm")
        nlp_en = spacy.load("en_core_web_sm")
    
    try:
        nlp_es = spacy.load("es_core_news_sm")
    except OSError:
        print("Descargando modelo de spaCy para español...")
        os.system("python -m spacy download es_core_news_sm")
        nlp_es = spacy.load("es_core_news_sm")
    
    # Agregar SpacyTextBlob a ambos
    if "spacytextblob" not in nlp_en.pipe_names:
        nlp_en.add_pipe("spacytextblob")
    if "spacytextblob" not in nlp_es.pipe_names:
        nlp_es.add_pipe("spacytextblob")
    
    print("Modelos cargados correctamente")
    
    # Cargar transcripciones diarizadas
    transcriptions = load_diarized_transcriptions(input_path)
    print(f"Cargados {len(transcriptions)} segmentos")
    
    if len(transcriptions) == 0:
        print("No se encontraron transcripciones para analizar.")
        return
    
    # Detectar idioma: busca palabras en ingles comunes
    ingles_words = ["the", "a", "is", "are", "i", "you", "he", "she", "it", "we", "they", "to", "of", "and"]
    texto_completo = " ".join([t.get("transcription", "").lower() for t in transcriptions])
    
    palabras_encontradas_ingles = sum(1 for word in ingles_words if f" {word} " in f" {texto_completo} ")
    idioma = "en" if palabras_encontradas_ingles > 10 else "es"
    
    print(f"Idioma detectado: {'Inglés' if idioma == 'en' else 'Español'}")
    
    # Seleccionar modelo segun idioma detectado
    nlp = nlp_en if idioma == "en" else nlp_es
    
    # Calcular duración total
    first_start = transcriptions[0].get("start", 0)
    last_end = transcriptions[-1].get("end", 0)
    duration_s = round(last_end - first_start, 2)
    
    # Identificar participantes únicos
    speakers = list(set(t.get("speaker", "") for t in transcriptions))
    
    # Contar segmentos por hablante para identificar interviewer (menos habla)
    speaker_count = {}
    for t in transcriptions:
        sp = t.get("speaker", "")
        speaker_count[sp] = speaker_count.get(sp, 0) + 1
    
    # Ordenar por número de segmentos (menor primero = interviewer)
    sorted_speakers = sorted(speakers, key=lambda x: speaker_count.get(x, 0))
    
    speaker_map = {}
    for i, sp in enumerate(sorted_speakers):
        if i == 0:
            speaker_map[sp] = "Interviewer"
        else:
            speaker_map[sp] = "Interviewee"
    
    # Construir segmentos con emparejamiento pregunta-respuesta
    segments = []
    prev_speaker = None
    
    for idx, item in enumerate(transcriptions):
        text = item.get("transcription", "")
        speaker_code = item.get("speaker", "")
        speaker_name = speaker_map.get(speaker_code, speaker_code)
        
        if not text.strip():
            continue
        
        role = detect_role(text, speaker_code, prev_speaker, idioma)
        
        segment = {
            "segment_id": idx + 1,
            "speaker": speaker_name,
            "start": round(item.get("start", 0), 2),
            "end": round(item.get("end", 0), 2),
            "text": text,
            "role": role
        }
        
        # Emparejamiento pregunta-respuesta
        if role == "question":
            # Buscar la respuesta del otro hablante
            for future_idx in range(idx + 1, len(transcriptions)):
                future_item = transcriptions[future_idx]
                if future_item.get("speaker") != speaker_code:
                    future_text = future_item.get("transcription", "").strip()
                    if future_text:  # Solo si tiene texto
                        segment["paired_response_id"] = future_idx + 1
                        segment["paired_response_speaker"] = speaker_map.get(future_item.get("speaker"), future_item.get("speaker"))
                        break
        elif role == "answer":
            # Buscar la pregunta anterior del otro hablante
            for past_idx in range(idx - 1, -1, -1):
                past_item = transcriptions[past_idx]
                if past_item.get("speaker") != speaker_code:
                    past_text = past_item.get("transcription", "").strip()
                    if past_text:
                        past_role = detect_role(past_text, past_item.get("speaker"), None, idioma)
                        if past_role == "question":
                            segment["paired_question_id"] = past_idx + 1
                            segment["paired_question_speaker"] = speaker_map.get(past_item.get("speaker"), past_item.get("speaker"))
                            break
            
            # Agregar sentimiento a las respuestas
            sentiment = analyze_sentiment(nlp, text)
            segment["sentiment"] = sentiment
        
        segments.append(segment)
        prev_speaker = speaker_code
    
    # Calcular estadísticas para el reporte
    answers = [s for s in segments if s.get("role") == "answer"]
    questions = [s for s in segments if s.get("role") == "question"]
    
    positive = sum(1 for s in answers if s.get("sentiment", {}).get("label") == "POSITIVE")
    negative = sum(1 for s in answers if s.get("sentiment", {}).get("label") == "NEGATIVE")
    neutral = sum(1 for s in answers if s.get("sentiment", {}).get("label") == "NEUTRAL")
    
    # Calcular score promedio
    scores = [s.get("sentiment", {}).get("score", 0.5) for s in answers if "sentiment" in s]
    avg_score = round(sum(scores) / len(scores), 2) if scores else 0.5
    
    # Construir reporte
    report = {
        "total_segments": len(segments),
        "total_questions": len(questions),
        "total_answers": len(answers),
        "sentiment_distribution": {
            "positive": {
                "count": positive,
                "percentage": round(100 * positive / len(answers), 1) if answers else 0
            },
            "negative": {
                "count": negative,
                "percentage": round(100 * negative / len(answers), 1) if answers else 0
            },
            "neutral": {
                "count": neutral,
                "percentage": round(100 * neutral / len(answers), 1) if answers else 0
            }
        },
        "average_sentiment_score": avg_score,
        "dominant_sentiment": max(
            [("POSITIVE", positive), ("NEGATIVE", negative), ("NEUTRAL", neutral)],
            key=lambda x: x[1]
        )[0] if answers else "N/A"
    }
    
    # Construir resultado final con reporte incluido
    result = {
        "interview_id": "ent_001",
        "metadata": {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "participantes": list(speaker_map.values()),
            "duration_s": duration_s
        },
        "segments": segments,
        "report": report
    }
    
    # Guardar resultados
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\nResultados guardados en: {output_path}")
    
    # Mostrar resumen en consola
    print(f"\n=== Resumen de la Entrevista ===")
    print(f"Duración: {duration_s}s")
    print(f"Participantes: {', '.join(speaker_map.values())}")
    print(f"Total segmentos: {len(segments)}")
    print(f"Preguntas: {len(questions)}")
    print(f"Respuestas: {len(answers)}")
    
    if len(answers) > 0:
        print(f"\n=== Sentimiento en Respuestas ===")
        print(f"Positivos: {positive} ({report['sentiment_distribution']['positive']['percentage']}%)")
        print(f"Negativos: {negative} ({report['sentiment_distribution']['negative']['percentage']}%)")
        print(f"Neutrales: {neutral} ({report['sentiment_distribution']['neutral']['percentage']}%)")
        print(f"Score promedio: {avg_score}")
        print(f"Sentimiento dominante: {report['dominant_sentiment']}")


if __name__ == "__main__":
    main()

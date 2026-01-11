import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.analysis.emotions import load_diarized_transcriptions, analyze_sentiment, detect_role


def test_load_valid_json(tmp_path):
    """Testea la carga de un archivo JSON válido."""

    transcriptions = [
        {"start": 0.5, "end": 3.2, "speaker": "SPEAKER_00", "transcription": "Hello"},
        {"start": 3.2, "end": 6.0, "speaker": "SPEAKER_01", "transcription": "Hi there"}
    ]
    json_file = tmp_path / "transcriptions.json"
    json_file.write_text(json.dumps(transcriptions, ensure_ascii=False))

    result = load_diarized_transcriptions(str(json_file))

    assert len(result) == 2
    assert result[0]["speaker"] == "SPEAKER_00"
    assert result[1]["transcription"] == "Hi there"


@patch('src.analysis.emotions.spacy')
def test_analyze_positive_sentiment(mock_spacy):
    """Testea análisis de sentimiento positivo."""
    mock_nlp = MagicMock()
    mock_doc = MagicMock()
    mock_doc._.blob.polarity = 0.8
    mock_nlp.return_value = mock_doc

    result = analyze_sentiment(mock_nlp, "I love this product!")

    assert result["label"] == "POSITIVE"
    assert result["score"] == 0.9


@patch('src.analysis.emotions.spacy')
def test_analyze_negative_sentiment(mock_spacy):
    """Testea análisis de sentimiento negativo."""
    mock_nlp = MagicMock()
    mock_doc = MagicMock()
    mock_doc._.blob.polarity = -0.6
    mock_nlp.return_value = mock_doc

    result = analyze_sentiment(mock_nlp, "I hate this.")
    
    assert result["label"] == "NEGATIVE"
    assert result["score"] == 0.2


@patch('src.analysis.emotions.spacy')
def test_analyze_neutral_sentiment(mock_spacy):
    """Testea análisis de sentimiento neutral."""
    
    mock_nlp = MagicMock()
    mock_doc = MagicMock()
    mock_doc._.blob.polarity = 0.05
    mock_nlp.return_value = mock_doc
    
    result = analyze_sentiment(mock_nlp, "The sky is blue.")
    
    assert result["label"] == "NEUTRAL"
    assert 0.4 <= result["score"] <= 0.6


def test_detect_question_with_question_mark():
    """Detecta preguntas por signo de interrogación."""
    
    assert detect_role("How are you?", "SPEAKER_00", "SPEAKER_01", "en") == "question"
    assert detect_role("¿Cómo estás?", "SPEAKER_00", "SPEAKER_01", "es") == "question"


def test_detect_question_with_interrogative_words():
    """Detecta preguntas por palabras interrogativas."""
    
    test_cases_en = ["What is your name", "How do you do", "When did you arrive"]
    test_cases_es = ["Qué es tu nombre", "Como te llamas", "Cuando llegaste"]
    
    for text in test_cases_en:
        assert detect_role(text, "SPEAKER_00", "SPEAKER_01", "en") == "question"
    
    for text in test_cases_es:
        assert detect_role(text, "SPEAKER_00", "SPEAKER_01", "es") == "question"


def test_detect_answer():
    """Detecta respuestas."""
    
    assert detect_role("I am fine, thank you.", "SPEAKER_00", "SPEAKER_01", "en") == "answer"
    assert detect_role("Estoy bien, gracias.", "SPEAKER_00", "SPEAKER_01", "es") == "answer"


@patch('src.analysis.emotions.spacy.load')
def test_full_pipeline(mock_spacy_load, tmp_path):
    
    """Test del pipeline completo con múltiples hablantes."""
    transcriptions = [
        {"start": 0.0, "end": 2.0, "speaker": "SPEAKER_00", "transcription": "Hello, how are you?"},
        {"start": 2.0, "end": 4.0, "speaker": "SPEAKER_01", "transcription": "I'm doing great!"},
        {"start": 4.0, "end": 6.0, "speaker": "SPEAKER_00", "transcription": "What do you do?"},
        {"start": 6.0, "end": 8.0, "speaker": "SPEAKER_01", "transcription": "I work as a developer."}
    ]
    
    json_file = tmp_path / "input.json"
    json_file.write_text(json.dumps(transcriptions))
    
    mock_nlp = MagicMock()
    mock_doc = MagicMock()
    mock_doc._.blob.polarity = 0.3
    mock_nlp.return_value = mock_doc
    mock_spacy_load.return_value = mock_nlp
    
    loaded_data = load_diarized_transcriptions(str(json_file))
    
    results = []
    for item in loaded_data:
        text = item["transcription"]
        role = detect_role(text, item["speaker"], None, "en")
        
        result = {"text": text, "role": role, "speaker": item["speaker"]}
        
        if role == "answer":
            result["sentiment"] = analyze_sentiment(mock_nlp, text)
        
        results.append(result)
    
    assert len(results) == 4
    assert results[0]["role"] == "question"
    assert results[1]["role"] == "answer"
    assert "sentiment" in results[1]
    assert results[1]["sentiment"]["label"] == "POSITIVE"

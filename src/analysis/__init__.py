"""Sentiment analysis module for audio transcriptions."""

from .emotions import analyze_sentiment, load_diarized_transcriptions, detect_role

__all__ = [
    "analyze_sentiment", 
    "load_diarized_transcriptions",
    "detect_role"
]
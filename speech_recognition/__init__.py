"""
Пакет распознавания речи
"""

from .whisper_engine import WhisperEngine
from .speech_to_text import SpeechToText

__all__ = [
    'WhisperEngine',
    'SpeechToText'
]
"""
Пакет обработки аудио
"""

from .audio_capture import AudioCapture
from .noise_reduction import NoiseReduction
from .vad import VoiceActivityDetector

__all__ = [
    'AudioCapture',
    'NoiseReduction', 
    'VoiceActivityDetector'
]
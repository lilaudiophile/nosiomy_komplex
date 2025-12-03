"""
Детектор речевой активности (Voice Activity Detection)
"""

import numpy as np

class VoiceActivityDetector:
    def __init__(self, threshold=500, min_duration=0.1):
        self.threshold = threshold
        self.min_duration = min_duration
        self.speech_buffer = []
        self.is_speaking = False
    
    def detect_speech(self, audio_chunk):
        """Обнаружение речи в аудиочанке"""
        try:
            energy = np.sqrt(np.mean(audio_chunk**2))
            
            # Порог
            has_speech = energy > self.threshold
            
            if has_speech and not self.is_speaking:
                self.is_speaking = True
                return "start"
            elif not has_speech and self.is_speaking:
                self.is_speaking = False  
                return "end"
            elif has_speech and self.is_speaking:
                return "continue"
            else:
                return "silence"
                
        except Exception as e:
            print(f"Ошибка VAD: {e}")
            return "silence"
    
    def update_threshold(self, background_noise):
        """Адаптивное обновление порога на основе фонового шума"""
        bg_energy = np.sqrt(np.mean(background_noise**2))
        self.threshold = bg_energy * 1.5  # Порог на 50% выше шума
        print(f"Обновлен порог VAD: {self.threshold:.2f}")
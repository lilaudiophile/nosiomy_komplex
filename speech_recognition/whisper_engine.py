"""
Движок распознавания речи на основе Whisper
"""

import whisper
import numpy as np
import torch
from config.model_config import MODEL_CONFIG

class WhisperEngine:
    def __init__(self):
        self.model = None
        self.config = MODEL_CONFIG
        self.load_model()
    
    def load_model(self):
        """Загрузка модели Whisper"""
        try:
            print("Загрузка модели Whisper")
            self.model = whisper.load_model(self.config['whisper_model'])
            print(f"Модель Whisper '{self.config['whisper_model']}' загружена")
        except Exception as e:
            print(f"Ошибка загрузки модели Whisper: {e}")
    
    def transcribe_audio(self, audio_data, sample_rate=16000):
        """Транскрибация аудио в текст"""
        if self.model is None:
            return ""
        
        try:
            # Конвертация в float32 для Whisper
            if audio_data.dtype == np.int16:
                audio_float = audio_data.astype(np.float32) / 32768.0
            else:
                audio_float = audio_data.astype(np.float32)
            
            # Транскрибация
            result = self.model.transcribe(
                audio_float,
                language=self.config['whisper_language'],
                fp16=torch.cuda.is_available()  # Использовать FP16 если есть GPU
            )
            
            text = result["text"].strip()
            if text:
                print(f"Распознано: {text}")
            
            return text
            
        except Exception as e:
            print(f"Ошибка транскрибации: {e}")
            return ""
    
    def get_transcription_with_timestamps(self, audio_data):
        """Транскрибация с временными метками"""
        try:
            if audio_data.dtype == np.int16:
                audio_float = audio_data.astype(np.float32) / 32768.0
            
            result = self.model.transcribe(
                audio_float,
                language=self.config['whisper_language'],
                word_timestamps=True
            )
            
            return {
                'text': result["text"].strip(),
                'segments': result.get("segments", []),
                'words': result.get("words", [])
            }
            
        except Exception as e:
            print(f"Ошибка транскрибации с метками: {e}")
            return {'text': '', 'segments': [], 'words': []}
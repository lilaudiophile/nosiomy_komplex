"""
Модуль захвата аудио с микрофона
"""

import pyaudio
import numpy as np
from config.audio_config import AUDIO_CONFIG

class AudioCapture:
    def __init__(self):
        self.config = AUDIO_CONFIG
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.setup_stream()
    
    def setup_stream(self):
        """Настройка аудиопотока"""
        try:
            self.stream = self.audio.open(
                format=self.config['format'],
                channels=self.config['channels'],
                rate=self.config['rate'],
                input=True,
                frames_per_buffer=self.config['chunk']
            )
            print("Аудиопоток настроен")
        except Exception as e:
            print(f"Ошибка настройки аудиопотока: {e}")
    
    def record_chunk(self):
        """Запись одного чанка аудио"""
        try:
            data = self.stream.read(self.config['chunk'], exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.int16)
            return audio_data
        except Exception as e:
            print(f"Ошибка записи аудио: {e}")
            return None
    
    def record_continuous(self, duration=3):
        """Непрерывная запись указанной длительности"""
        frames = []
        for _ in range(0, int(self.config['rate'] / self.config['chunk'] * duration)):
            data = self.record_chunk()
            if data is not None:
                frames.append(data)
        return np.concatenate(frames) if frames else None
    
    def cleanup(self):
        """Очистка ресурсов"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.audio.terminate()
        print("Аудиоресурсы освобождены")
"""
Основной интерфейс распознавания речи
"""

from .whisper_engine import WhisperEngine
from audio.noise_reduction import NoiseReduction
from audio.vad import VoiceActivityDetector
from utils.logger import setup_logger

class SpeechToText:
    def __init__(self):
        self.logger = setup_logger('speech_to_text')
        self.whisper_engine = WhisperEngine()
        self.noise_reducer = NoiseReduction()
        self.vad = VoiceActivityDetector()
        self.speech_buffer = []
        self.is_listening = False
    
    def process_audio_chunk(self, audio_chunk):
        """Обработка аудиочанка"""
        try:
            # Детекция речи
            speech_state = self.vad.detect_speech(audio_chunk)
            
            if speech_state in ["start", "continue"]:
                if not self.is_listening:
                    self.is_listening = True
                    self.speech_buffer = []
                    self.logger.info("🎤 Начало речи обнаружено")
                
                # Подавление шума
                clean_audio = self.noise_reducer.reduce_noise_simple(audio_chunk)
                self.speech_buffer.append(clean_audio)
                
            elif speech_state == "end" and self.is_listening:
                self.is_listening = False
                if self.speech_buffer:
                    # Объединение буфера в один массив
                    full_audio = np.concatenate(self.speech_buffer)
                    text = self.transcribe(full_audio)
                    self.speech_buffer = []
                    return text
            
            return ""
            
        except Exception as e:
            self.logger.error(f"Ошибка обработки аудио: {e}")
            return ""
    
    def transcribe(self, audio_data):
        """Транскрибация аудио в текст"""
        try:
            if len(audio_data) == 0:
                return ""
            
            # Калибровка шума 
            if not self.noise_reducer.is_calibrated:
                self.noise_reducer.calibrate_noise(audio_data)
            
            # Подавление шума
            clean_audio = self.noise_reducer.spectral_gating(audio_data)
            
            # Распознавание речи
            text = self.whisper_engine.transcribe_audio(clean_audio)
            return text
            
        except Exception as e:
            self.logger.error(f"Ошибка транскрибации: {e}")
            return ""
    
    def real_time_transcription(self, audio_stream):
        """Режим реального времени"""
        pass
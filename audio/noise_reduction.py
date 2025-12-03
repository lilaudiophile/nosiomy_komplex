"""
Модуль подавления шума
"""

import numpy as np
import librosa

class NoiseReduction:
    def __init__(self):
        self.noise_profile = None
        self.is_calibrated = False
    
    def calibrate_noise(self, audio_data, duration=1):
        """Калибровка шумового профиля"""
        try:
            # Первые N семплов считаем шумом
            noise_samples = audio_data[:int(16000 * duration)]
            self.noise_profile = np.mean(np.abs(noise_samples))
            self.is_calibrated = True
            print("Шумовой профиль откалиброван")
        except Exception as e:
            print(f"Ошибка калибровки шума: {e}")
    
    def reduce_noise_simple(self, audio_data):
        """Простое подавление шума"""
        if not self.is_calibrated:
            return audio_data
        
        try:
            # Пороговая фильтрация
            threshold = self.noise_profile * 2
            filtered_audio = np.where(np.abs(audio_data) > threshold, audio_data, 0)
            return filtered_audio
        except Exception as e:
            print(f"Ошибка подавления шума: {e}")
            return audio_data
    
    def spectral_gating(self, audio_data, rate=16000):
        """Спектральное подавление шума"""
        try:
            # STFT
            stft = librosa.stft(audio_data.astype(float))
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            if self.noise_profile:
                # Маска на основе шумового профиля
                noise_mag = self.noise_profile
                mask = magnitude > noise_mag
                clean_magnitude = magnitude * mask
            else:
                clean_magnitude = magnitude
            
            # Обратное STFT
            clean_stft = clean_magnitude * np.exp(1j * phase)
            clean_audio = librosa.istft(clean_stft)
            
            return (clean_audio * 32767).astype(np.int16)
        except Exception as e:
            print(f"Ошибка спектрального подавления: {e}")
            return audio_data
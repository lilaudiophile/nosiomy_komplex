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
        self.selected_device = None
        self.setup_stream()
    
    def setup_stream(self):
        """Настройка аудиопотока с автоматическим поиском микрофона"""
        print("="*50)
        print("Поиск доступных микрофонов...")
        
        # Сначала выведем все доступные устройства для отладки
        self.list_audio_devices()
        
        # Пробуем разные устройства в порядке приоритета
        devices_to_try = [
            {'index': None, 'reason': 'устройство по умолчанию'},  # None = системное устройство по умолчанию
            {'index': 3, 'reason': 'карта 3 (ваш Fifine микрофон)'},
            {'index': 4, 'reason': 'карта 4'},
            {'index': 0, 'reason': 'карта 0 (встроенный)'},
            {'index': 1, 'reason': 'карта 1'},
            {'index': 2, 'reason': 'карта 2'},
        ]
        
        for device in devices_to_try:
            try:
                print(f"Пробуем {device['reason']}...")
                
                self.stream = self.audio.open(
                    format=self.audio.get_format_from_width(self.config['sample_width']),  # Правильный способ получить формат
                    channels=self.config['channels'],
                    rate=self.config['rate'],
                    input=True,
                    frames_per_buffer=self.config['chunk'],
                    input_device_index=device['index']  # Может быть None для устройства по умолчанию
                )
                
                self.selected_device = device['index']
                print(f"✅ Аудиопоток настроен: {device['reason']}")
                print("="*50)
                return  # Успешно - выходим
                
            except Exception as e:
                print(f"❌ Не сработало: {str(e)[:80]}...")
                continue  # Пробуем следующее устройство
        
        # Если ни одно устройство не сработало
        print("⚠ Внимание: Не удалось настроить аудиопоток.")
        print("⚠ Программа будет работать без микрофона.")
        print("="*50)
        self.stream = None
    
    def list_audio_devices(self):
        """Вывести список всех аудиоустройств"""
        print("\nДоступные аудиоустройства:")
        for i in range(self.audio.get_device_count()):
            dev = self.audio.get_device_info_by_index(i)
            if dev['maxInputChannels'] > 0:  # Это устройство ввода (микрофон)
                print(f"  [{i}] {dev['name']}")
                print(f"      Каналы: {dev['maxInputChannels']}, "
                      f"Частота: {dev.get('defaultSampleRate', 'неизвестно')} Hz")
        print()
    
    def record_chunk(self):
        """Запись одного чанка аудио"""
        try:
            # ВАЖНО: проверяем, создан ли поток
            if self.stream is None:
                # Возвращаем "тишину" если микрофон не настроен
                return np.zeros(self.config['chunk'], dtype=np.int16)
            
            data = self.stream.read(self.config['chunk'], exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.int16)
            return audio_data
            
        except Exception as e:
            print(f"Ошибка записи аудио: {e}")
            # Всегда возвращаем что-то, даже если ошибка
            return np.zeros(self.config['chunk'], dtype=np.int16)
    
    def record_continuous(self, duration=3):
        """Непрерывная запись указанной длительности"""
        frames = []
        for _ in range(0, int(self.config['rate'] / self.config['chunk'] * duration)):
            data = self.record_chunk()
            if data is not None:
                frames.append(data)
        return np.concatenate(frames) if frames else np.zeros(int(self.config['rate'] * duration), dtype=np.int16)
    
    def cleanup(self):
        """Очистка ресурсов"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            print("Аудиопоток закрыт")
        self.audio.terminate()
        print("Аудиоресурсы освобождены")
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
        
        # Автоматически определяем параметры подключенного микрофона
        self.device_info = self.detect_microphone()
        self.setup_stream()
    
    def detect_microphone(self):
        """Найти подключенный микрофон и его рабочие параметры"""
        print("\nПоиск доступных микрофонов...")
        
        available_devices = []
        
        for i in range(self.audio.get_device_count()):
            dev = self.audio.get_device_info_by_index(i)
            if dev['maxInputChannels'] > 0:  # Это устройство ввода
                available_devices.append({
                    'index': i,
                    'name': dev['name'],
                    'max_channels': dev['maxInputChannels'],
                    'default_rate': dev.get('defaultSampleRate', 44100.0),
                })
                print(f"  [{i}] {dev['name']} - {dev['maxInputChannels']} каналов, {dev.get('defaultSampleRate', 44100)} Hz")
        
        if not available_devices:
            print("Микрофонов не найдено")
            return None
        
        # Выбираем первое рабочее устройство
        selected_device = available_devices[0]
        
        # Определяем оптимальные параметры
        # Для USB микрофонов обычно 44100/48000 Hz, 1-2 канала
        # Для встроенных обычно 16000/44100 Hz, 1 канал
        
        # Проверяем, USB ли это (по названию)
        is_usb = any(keyword in selected_device['name'].lower() 
                    for keyword in ['usb', 'external', 'external'])
        
        if is_usb:
            # USB микрофон - пробуем стандартные параметры
            test_rates = [44100, 48000, 16000, 22050]
            test_channels = [2, 1]  # Сначала пробуем стерео, потом моно
        else:
            # Встроенный микрофон
            test_rates = [16000, 44100, 48000]
            test_channels = [1]
        
        # Тестируем параметры
        working_rate = None
        working_channels = None
        
        for rate in test_rates:
            for channels in test_channels:
                if channels <= selected_device['max_channels']:
                    try:
                        test_stream = self.audio.open(
                            format=self.audio.get_format_from_width(self.config['sample_width']),
                            channels=channels,
                            rate=rate,
                            input=True,
                            frames_per_buffer=self.config['chunk'],
                            input_device_index=selected_device['index']
                        )
                        test_stream.close()
                        working_rate = rate
                        working_channels = channels
                        print(f"Найден рабочий режим: {rate} Hz, {channels} канал(ов)")
                        break
                    except:
                        continue
            if working_rate:
                break
        
        if not working_rate:
            # Если не нашли рабочий режим, используем параметры по умолчанию
            working_rate = int(selected_device['default_rate'])
            working_channels = min(selected_device['max_channels'], 1)
            print(f"Используем параметры по умолчанию: {working_rate} Hz, {working_channels} канал(ов)")
        
        return {
            'index': selected_device['index'],
            'rate': working_rate,
            'channels': working_channels,
            'name': selected_device['name']
        }
    
    def setup_stream(self):
        """Настройка аудиопотока с определенными параметрами"""
        if self.device_info is None:
            print("Не удалось настроить микрофон")
            self.stream = None
            return
        
        try:
            print(f"Запуск микрофона: {self.device_info['rate']} Hz, {self.device_info['channels']} канал(ов)")
            
            self.stream = self.audio.open(
                format=self.audio.get_format_from_width(self.config['sample_width']),
                channels=self.device_info['channels'],
                rate=self.device_info['rate'],
                input=True,
                frames_per_buffer=self.config['chunk'],
                input_device_index=self.device_info['index']
            )
            
            print("Микрофон готов")
            
        except Exception as e:
            print(f"Ошибка запуска микрофона: {e}")
            print("Работа без микрофона")
            self.stream = None
    
    def record_chunk(self):
        """Запись одного чанка аудио"""
        try:
            if self.stream is None:
                channels = self.device_info['channels'] if self.device_info else 1
                return np.zeros(self.config['chunk'] * channels, dtype=np.int16)
            
            data = self.stream.read(self.config['chunk'], exception_on_overflow=False)
            return np.frombuffer(data, dtype=np.int16)
            
        except Exception as e:
            print(f"Ошибка записи аудио: {e}")
            channels = self.device_info['channels'] if self.device_info else 1
            return np.zeros(self.config['chunk'] * channels, dtype=np.int16)
    
    def record_continuous(self, duration=3):
        """Запись N секунд аудио"""
        if self.stream is None or self.device_info is None:
            rate = self.device_info['rate'] if self.device_info else 16000
            channels = self.device_info['channels'] if self.device_info else 1
            return np.zeros(int(rate * duration * channels), dtype=np.int16)
        
        frames = []
        chunks_needed = int(self.device_info['rate'] / self.config['chunk'] * duration)
        
        for _ in range(chunks_needed):
            frames.append(self.record_chunk())
        
        audio = np.concatenate(frames)
        
        # Форматируем для дальнейшей обработки
        if self.device_info['channels'] > 1:
            return audio.reshape(-1, self.device_info['channels'])
        else:
            return audio
    
    def get_audio_params(self):
        """Получить параметры аудио"""
        if self.device_info:
            return {
                'rate': self.device_info['rate'],
                'channels': self.device_info['channels']
            }
        return {'rate': 16000, 'channels': 1}
    
    def cleanup(self):
        """Очистка ресурсов"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.audio.terminate()
        print("Аудиоресурсы освобождены")
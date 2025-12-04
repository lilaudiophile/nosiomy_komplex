"""
Конфигурация параметров аудио
"""

AUDIO_CONFIG = {
    'format': 8,                    # pyaudio.paInt16
    'channels': 1,                  # Моно
    'rate': 16000,                  # Частота дискретизации
    'chunk': 1024,                  # Размер чанка
    'record_seconds': 3,            # Длительность записи
    'silence_threshold': 500,       # Порог тишины для VAD
    'noise_reduction': True,        # Включить шумоподавление
    'sample_width': 2,              # 16-bit audio
}


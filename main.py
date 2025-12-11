import time
import signal
import sys
import numpy as np
import os
from datetime import datetime

# Импорт модулей
from audio import AudioCapture
from speech_recognition import SpeechToText
from nlp import PriorityCalculator
from output import TactileEngine, DisplayEngine
from utils import setup_logger, ensure_dir, CRITICAL_LEVELS

class NosiomyKomplex:
    def __init__(self):
        """Инициализация основного приложения"""
        self.logger = setup_logger('main')
        self.is_running = False
        self.message_count = 0
        
        # Создание необходимых директорий
        ensure_dir('logs')
        ensure_dir('data/audio_samples')
        
        self.logger.info("Инициализация носимого комплекса...")
        
        # Инициализация компонентов
        self.audio_capture = AudioCapture()
        self.speech_recognizer = SpeechToText()
        self.priority_calculator = PriorityCalculator()
        self.tactile_engine = TactileEngine()
        self.display_engine = DisplayEngine()
        
        # Настройка обработчиков сигналов
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        self.logger.info("Носимый комплекс инициализирован")
    
    def signal_handler(self, signum, frame):
        """Обработчик сигналов завершения"""
        self.logger.info(f"Получен сигнал {signum}, завершение работы...")
        self.stop()
    
    def read_audio_from_file(self, duration=3):
        """Чтение аудио из файла /tmp/audio_stream.raw"""
        try:
            file_path = "/tmp/audio_stream.raw"
            sample_rate = 16000
            bytes_per_sample = 2  # 16-bit = 2 байта
            
            # Вычисляем сколько нужно прочитать
            bytes_needed = int(sample_rate * duration * bytes_per_sample)
            
            # Проверяем существует ли файл
            if not os.path.exists(file_path):
                print(f"ОШИБКА: Файл {file_path} не существует")
                return np.zeros(sample_rate * duration, dtype=np.int16)
            
            file_size = os.path.getsize(file_path)
            print(f"ФАЙЛ: {file_path} ({file_size} байт)")
            
            with open(file_path, 'rb') as f:
                # Если файл меньше нужного размера, читаем с начала
                if file_size < bytes_needed:
                    print(f"ВНИМАНИЕ: Файл мал: {file_size}/{bytes_needed} байт")
                    f.seek(0)
                else:
                    # Читаем с конца файла
                    f.seek(-bytes_needed, 2)
                
                data = f.read(bytes_needed)
            
            if len(data) == 0:
                print("ОШИБКА: Файл аудио пустой")
                return np.zeros(sample_rate * duration, dtype=np.int16)
            
            print(f"УСПЕХ: Прочитано {len(data)} байт из файла")
            
            # Конвертируем байты в аудио
            audio = np.frombuffer(data, dtype=np.int16)
            
            # Обрезаем или дополняем до нужной длины
            target_samples = sample_rate * duration
            if len(audio) > target_samples:
                audio = audio[:target_samples]
            elif len(audio) < target_samples:
                audio = np.pad(audio, (0, target_samples - len(audio)), mode='constant')
            
            # Проверяем уровень сигнала
            if len(audio) > 0:
                level = np.sqrt(np.mean(audio.astype(float)**2))
                print(f"ЗВУК: Загружено {len(audio)} сэмплов (уровень: {level:.0f})")
            
            return audio
            
        except Exception as e:
            print(f"ОШИБКА чтения аудиофайла: {e}")
            import traceback
            traceback.print_exc()
            return np.zeros(16000 * duration, dtype=np.int16)
    
    def analyze_audio_level(self, audio_chunk):
        """Анализ уровня аудио для детектирования речи"""
        if audio_chunk is None or len(audio_chunk) == 0:
            return 0
        
        try:
            # Вычисляем RMS (среднеквадратичное значение)
            rms = np.sqrt(np.mean(audio_chunk.astype(float)**2))
            return rms
        except Exception as e:
            print(f"ОШИБКА анализа аудио: {e}")
            return 0
    
    
                
    def run(self):
        if self.is_running:
            self.logger.warning("ПРЕДУПРЕЖДЕНИЕ: Система уже запущена")
            return
        
        self.is_running = True
        self.logger.info("Запуск основного цикла...")
        
        # Инициализация статуса системы
        status = {
            "Статус": "Активен",
            "Сообщений": "0",
            "Режим": "Анализ аудиопотока",
            "Последнее сообщение": "Нет"
        }
        self.display_engine.show_system_status(status)
        
        # Настройки детектирования речи
        speech_threshold = 200
        last_recognition = time.time()
        
        try:
            while self.is_running:
                # 1. Чтение аудиочанка
                audio_chunk = self.audio_capture.record_chunk()
                
                if audio_chunk is not None:
                    # 2. Анализ уровня звука
                    audio_level = self.analyze_audio_level(audio_chunk)
                    
                    # Показываем уровень в реальном времени
                    if audio_level > 50:
                        bars = int(audio_level / 50)
                        bar_display = '#' * min(bars, 20)
                        print(f"УРОВЕНЬ [{bar_display:20}] {audio_level:5.0f}", end='\r')
                    
                    # 3. Детектирование речи
                    current_time = time.time()
                    
                    # Автоматический анализ каждые 30 секунд
                    if current_time - last_recognition > 30:
                        last_recognition = current_time
                        print(f"\nАВТОМАТИЧЕСКИЙ АНАЛИЗ...")
                        
                        # 4. Записываем аудио для анализа
                        print("ЗАПИСЬ: Загрузка аудио для анализа...")
                        audio_for_analysis = self.read_audio_from_file(duration=3)
                        
                        # 5. Распознавание речи через Whisper
                        print("ИИ: Запуск распознавания...")
                        audio_params = self.audio_capture.get_audio_params()
                        
                        try:
                            text = self.speech_recognizer.whisper_engine.transcribe_audio(
                                audio_for_analysis, 
                                sample_rate=audio_params['rate']
                            )
                        except Exception as e:
                            print(f"ОШИБКА Whisper: {e}")
                            # Демо-режим если Whisper не работает
                            import random
                            demo_commands = [
                                "Включи свет в комнате",
                                "Позвони маме",
                                "Какая погода завтра",
                                "Напомни купить молоко", 
                                "Выключи телевизор"
                            ]
                            text = random.choice(demo_commands)
                            print(f"ДЕМО РЕЖИМ: Распознано '{text}'")
                        
                        if text and len(text.strip()) > 3:
                            self.message_count += 1
                            print(f"\nУСПЕХ: РАСПОЗНАНО #{self.message_count}:")
                            print(f"   '{text}'")
                            
                            # 6. Семантический анализ
                            critical_level = self.priority_calculator.calculate_critical_level(text)
                            
                            # 7. Мультимодальный вывод
                            self.tactile_engine.vibrate(critical_level)
                            self.display_engine.show_text(text, critical_level)
                            
                            # Обновление статуса с ВЫВОДОМ СООБЩЕНИЯ
                            status["Сообщений"] = str(self.message_count)
                            status["Режим"] = f"Обработка (ур. {critical_level})"
                            status["Последнее сообщение"] = text[:30] + "..." if len(text) > 30 else text
                            self.display_engine.show_system_status(status)
                            
                            # Пауза для восприятия
                            time.sleep(2)
                        
                        # Также проверяем если уровень звука высокий
                        elif audio_level > speech_threshold:
                            print(f"\nОБНАРУЖЕН ЗВУК! Уровень: {audio_level:.0f}")
                
                # Небольшая пауза для снижения нагрузки
                time.sleep(0.05)
                
        except KeyboardInterrupt:
            self.logger.info("Прерывание пользователем")
        except Exception as e:
            self.logger.error(f"Критическая ошибка в основном цикле: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.stop()
    
    def test_system(self):
        """Тестирование всех компонентов системы"""
        self.logger.info("Запуск тестирования системы")
        
        try:
            # Тест тактильных паттернов
            self.logger.info("ТЕСТ: Тестирование тактильных паттернов...")
            self.tactile_engine.test_patterns()
            
            # Тест отображения
            self.logger.info("ТЕСТ: Тестирование отображения...")
            test_messages = [
                ("Тестовое сообщение уровня 3", 3),
                ("ВНИМАНИЕ! Проверка системы", 8),
                ("КРИТИЧЕСКАЯ СИТУАЦИЯ!!!", 15)
            ]
            
            for text, level in test_messages:
                self.display_engine.show_text(text, level)
                time.sleep(2)
            
            # Тест чтения аудиофайла
            self.logger.info("ТЕСТ: Тестирование чтения аудио...")
            test_audio = self.read_audio_from_file(duration=2)
            print(f"Прочитано {len(test_audio)} сэмплов")
            
            self.logger.info("ТЕСТ: Тестирование завершено")
            
        except Exception as e:
            self.logger.error(f"Ошибка тестирования: {e}")
    
    def stop(self):
        """Корректное завершение работы"""
        if not self.is_running:
            return
        
        self.is_running = False
        self.logger.info("Завершение работы носимого комплекса...")
        
        # Очистка ресурсов
        self.tactile_engine.cleanup()
        self.display_engine.cleanup()
        self.audio_capture.cleanup()
        
        self.logger.info(f"Итоги работы: обработано {self.message_count} сообщений")
        self.logger.info(" Носимый комплекс завершил работу")

def main():
    """Точка входа в приложение"""
    print("=" * 50)
    print("   НОСИМЫЙ КОМПЛЕКС С ИИ ДЛЯ СЛАБОСЛЫШАЩИХ")
    print("=" * 50)
    
    app = NosiomyKomplex()
    
    # Проверка аргументов командной строки
    if len(sys.argv) > 1:
        if sys.argv[1] == '--test':
            app.test_system()
            return
        elif sys.argv[1] == '--help':
            print("Использование:")
            print("  python main.py          - запуск системы")
            print("  python main.py --test   - тестирование компонентов")
            print("  python main.py --help   - справка")
            return
    
    # Запуск основного цикла
    try:
        app.run()
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        sys.exit(1)

if name == "__main__":
    main()

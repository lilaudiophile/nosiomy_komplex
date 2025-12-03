#!/usr/bin/env python3

import time
import signal
import sys
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
    
    def run(self):
        """Основной цикл работы"""
        if self.is_running:
            self.logger.warning("⚠️ Система уже запущена")
            return
        
        self.is_running = True
        self.logger.info("Запуск основного цикла...")
        
        # Показать статус системы
        status = {
            "Статус": "Активен",
            "Сообщений": "0",
            "Режим": "Ожидание команд"
        }
        self.display_engine.show_system_status(status)
        
        try:
            while self.is_running:
                # 1. Захват аудио
                audio_data = self.audio_capture.record_chunk()
                
                if audio_data is not None:
                    # 2. Обработка аудио и распознавание речи
                    text = self.speech_recognizer.process_audio_chunk(audio_data)
                    
                    if text and len(text) > 3:  # Минимальная длина текста
                        self.message_count += 1
                        self.logger.info(f"💬 Сообщение #{self.message_count}: {text}")
                        
                        # 3. Семантический анализ и определение критичности
                        critical_level = self.priority_calculator.calculate_critical_level(text)
                        
                        # 4. Мультимодальный вывод
                        self.tactile_engine.vibrate(critical_level)
                        self.display_engine.show_text(text, critical_level)
                        
                        # Обновление статуса
                        status["Сообщений"] = str(self.message_count)
                        status["Режим"] = f"Обработка (уровень {critical_level})"
                        self.display_engine.show_system_status(status)
                        
                        # Пауза для восприятия сообщения
                        time.sleep(2)
                    
                # Небольшая пауза для снижения нагрузки на CPU
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            self.logger.info("Прерывание пользователем")
        except Exception as e:
            self.logger.error(f"Критическая ошибка в основном цикле: {e}")
        finally:
            self.stop()
    
    def test_system(self):
        """Тестирование всех компонентов системы"""
        self.logger.info("Запуск тестирования системы")
        
        try:
            # Тест тактильных паттернов
            self.logger.info("🔊 Тестирование тактильных паттернов...")
            self.tactile_engine.test_patterns()
            
            # Тест отображения
            self.logger.info("Тестирование отображения...")
            test_messages = [
                ("Тестовое сообщение уровня 3", 3),
                ("ВНИМАНИЕ! Проверка системы", 8),
                ("КРИТИЧЕСКАЯ СИТУАЦИЯ!!!", 15)
            ]
            
            for text, level in test_messages:
                self.display_engine.show_text(text, level)
                time.sleep(2)
            
            self.logger.info("Тестирование завершено")
            
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

if __name__ == "__main__":
    main()
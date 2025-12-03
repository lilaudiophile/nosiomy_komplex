"""
Управление вибромотором для тактильной обратной связи
"""

import time
import RPi.GPIO as GPIO
from .patterns import get_pattern
from config.gpio_config import GPIO_CONFIG, VIBRATION_CONFIG
from utils.logger import setup_logger

class TactileEngine:
    def __init__(self):
        self.logger = setup_logger('tactile_engine')
        self.config = GPIO_CONFIG
        self.vibration_config = VIBRATION_CONFIG
        self.pin = self.config['vibration_motor_pin']
        self.is_initialized = False
        self.current_level = 0
        
        self.initialize_gpio()
    
    def initialize_gpio(self):
        """Инициализация GPIO"""
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.OUT)
            
            # Создание PWM для контроля интенсивности
            self.pwm = GPIO.PWM(self.pin, self.config['pwm_frequency'])
            self.pwm.start(0)  # Начальное значение 0%
            
            self.is_initialized = True
            self.logger.info("Тактильный движок инициализирован")
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации GPIO: {e}")
            self.is_initialized = False
    
    def vibrate(self, level):
        """Активация вибрации по уровню критичности"""
        if not self.is_initialized or level == self.current_level:
            return
        
        try:
            self.current_level = level
            pattern_data = get_pattern(level)
            pattern = pattern_data['pattern']
            intensity = pattern_data['intensity']
            repeat_delay = pattern_data.get('repeat', 0)
            
            self.logger.info(f"🔊 Тактильный сигнал уровня {level}")
            
            # Преобразование интенсивности в процент ШИМ (0-100)
            pwm_duty_cycle = (intensity / 255) * 100
            
            # Воспроизведение паттерна
            for duration in pattern:
                self.pwm.ChangeDutyCycle(pwm_duty_cycle)
                time.sleep(duration)
                self.pwm.ChangeDutyCycle(0)  # Пауза между импульсами
                if duration > 0.1:  # Короткая пауза только для длинных импульсов
                    time.sleep(0.05)
            
            # Повтор для критических уровней
            if repeat_delay > 0:
                time.sleep(repeat_delay)
                self.vibrate(level)  # Рекурсивный повтор
            
        except Exception as e:
            self.logger.error(f"Ошибка активации вибрации: {e}")
    
    def test_patterns(self):
        """Тестирование всех тактильных паттернов"""
        if not self.is_initialized:
            self.logger.error("Тактильный движок не инициализирован")
            return
        
        self.logger.info("🧪 Тестирование тактильных паттернов...")
        
        for level in range(1, 16):
            print(f"Тестирование уровня {level}...")
            self.vibrate(level)
            time.sleep(2)  
        
        self.logger.info("Тестирование паттернов завершено")
    
    def stop_vibration(self):
        """Немедленная остановка вибрации"""
        try:
            self.pwm.ChangeDutyCycle(0)
            self.current_level = 0
        except Exception as e:
            self.logger.error(f"Ошибка остановки вибрации: {e}")
    
    def cleanup(self):
        """Очистка ресурсов"""
        try:
            self.stop_vibration()
            self.pwm.stop()
            GPIO.cleanup()
            self.logger.info("Ресурсы тактильного движка освобождены")
        except Exception as e:
            self.logger.error(f"Ошибка очистки ресурсов: {e}")
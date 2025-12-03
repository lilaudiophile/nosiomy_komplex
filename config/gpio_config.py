"""
Конфигурация GPIO для Raspberry Pi
"""

GPIO_CONFIG = {
    'vibration_motor_pin': 18,      # Пин для вибромотора
    'button_pin': 17,               # Пин для кнопки (опционально)
    'display_type': 'tft_3.5',      # Тип дисплея
    'i2c_bus': 1,                   # I2C шина
    'pwm_frequency': 1000,          # Частота ШИМ для мотора
}

# Настройки тактильного двигателя
VIBRATION_CONFIG = {
    'max_intensity': 255,           # Максимальная интенсивность
    'min_intensity': 96,            # Минимальная интенсивность
    'default_duration': 0.5,        # Длительность по умолчанию
}
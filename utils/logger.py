"""
Настройка логирования
"""

import logging
import sys
from datetime import datetime

def setup_logger(name='nosiomy_komplex'):
    """Настройка логгера"""
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Обработчик для консоли
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Обработчик для файла
    file_handler = logging.FileHandler(f'logs/{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger
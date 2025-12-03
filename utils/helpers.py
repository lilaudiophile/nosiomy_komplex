"""
Вспомогательные функции
"""

import os
import json
from datetime import datetime

def ensure_dir(directory):
    """Создает директорию если не существует"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def load_config(config_path):
    """Загружает конфиг из JSON файла"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_config(config, config_path):
    """Сохраняет конфиг в JSON файл"""
    ensure_dir(os.path.dirname(config_path))
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def timeit(func):
    """Декоратор для измерения времени выполнения"""
    def wrapper(*args, **kwargs):
        start = datetime.now()
        result = func(*args, **kwargs)
        end = datetime.now()
        print(f"{func.__name__} выполнена за {(end - start).total_seconds():.2f} сек")
        return result
    return wrapper
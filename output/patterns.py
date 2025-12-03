"""
Библиотека тактильных паттернов
"""

TACTILE_PATTERNS = {
    1: {'pattern': [0.15], 'intensity': 96},                              # Уровень 1
    2: {'pattern': [0.2], 'intensity': 128},                              # Уровень 2
    3: {'pattern': [0.15, 0.2, 0.15], 'intensity': 128},                 # Уровень 3
    4: {'pattern': [0.2, 0.15, 0.2], 'intensity': 160},                  # Уровень 4
    5: {'pattern': [0.15, 0.15, 0.15], 'intensity': 160},                # Уровень 5
    6: {'pattern': [0.4], 'intensity': 192},                              # Уровень 6
    7: {'pattern': [0.3, 0.1, 0.3], 'intensity': 192},                   # Уровень 7
    8: {'pattern': [0.2, 0.1, 0.2, 0.1, 0.2], 'intensity': 192},         # Уровень 8
    9: {'pattern': [0.4, 0.15, 0.15], 'intensity': 224},                 # Уровень 9
    10: {'pattern': [0.2, 0.08, 0.2, 0.08, 0.2, 0.08, 0.2], 'intensity': 224},  # Уровень 10
    11: {'pattern': [0.15, 0.15, 0.15, 0.4], 'intensity': 255},          # Уровень 11
    12: {'pattern': [0.15, 0.08, 0.15, 0.08, 0.15, 0.08, 0.15, 0.08, 0.15], 'intensity': 255},  # Уровень 12
    13: {'pattern': [0.1, 0.05] * 10, 'intensity': 255, 'repeat': 1.0},  # Уровень 13
    14: {'pattern': [0.1, 0.1, 0.1, 0.3, 0.3, 0.3, 0.1, 0.1, 0.1], 'intensity': 255, 'repeat': 0.5},  # Уровень 14
    15: {'pattern': [2.0], 'intensity': 255, 'repeat': 0.0}               # Уровень 15
}

def get_pattern(level):
    """Получение тактильного паттерна для уровня"""
    return TACTILE_PATTERNS.get(level, TACTILE_PATTERNS[1])

def validate_patterns():
    """Валидация всех паттернов"""
    for level, pattern_data in TACTILE_PATTERNS.items():
        pattern = pattern_data['pattern']
        intensity = pattern_data['intensity']
        
        if not (1 <= level <= 15):
            print(f"Неверный уровень: {level}")
            return False
        
        if not (0 < intensity <= 255):
            print(f"Неверная интенсивность для уровня {level}: {intensity}")
            return False
            
        if not pattern or len(pattern) == 0:
            print(f"Пустой паттерн для уровня {level}")
            return False
    
    print("Все тактильные паттерны валидны")
    return True
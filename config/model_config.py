"""
Конфигурация моделей машинного обучения
"""

MODEL_CONFIG = {
    'whisper_model': 'tiny',        # Модель Whisper (tiny, base, small)
    'whisper_language': 'ru',       # Язык распознавания
    
    'bert_model': 'cointegrated/rubert-tiny2',  # Модель для классификации
    'natasha_model': 'news',        # Модель для извлечения сущностей
    
    'critical_threshold': 0.7,      # Порог критичности
    'max_text_length': 512,         # Максимальная длина текста
}

# Маркеры
CRITICAL_MARKERS = {
    'emergency_terms': ['пожар', 'взрыв', 'авария', 'утечка', 'обрушение', 'эвакуация'],
    'urgency_terms': ['срочно', 'немедленно', 'быстро', 'опасно', 'осторожно'],
    'safety_denials': ['не работает', 'отказал', 'нет связи', 'аварийная'],
}
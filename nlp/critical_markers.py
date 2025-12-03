"""
Детектор критических маркеров в тексте
"""

import re
from config.model_config import CRITICAL_MARKERS

class CriticalMarkersDetector:
    def __init__(self):
        self.markers = CRITICAL_MARKERS
        self.setup_patterns()
    
    def setup_patterns(self):
        """Компиляция regex паттернов"""
        self.patterns = {
            'emergency': re.compile(r'\b(?:' + '|'.join(self.markers['emergency_terms']) + r')\b', re.IGNORECASE),
            'urgency': re.compile(r'\b(?:' + '|'.join(self.markers['urgency_terms']) + r')\b', re.IGNORECASE),
            'safety_denial': re.compile(r'\b(?:' + '|'.join(self.markers['safety_denials']) + r')\b', re.IGNORECASE),
            'numbers': re.compile(r'\b(\d+)\s*(°C|атм|бар|МПа|%)', re.IGNORECASE),
            'equipment': re.compile(r'\b(?:станок|реактор|насос|компрессор|трансформатор)\b', re.IGNORECASE)
        }
    
    def detect_markers(self, text):
        """Обнаружение критических маркеров"""
        markers_found = {
            'emergency_terms': [],
            'urgency_terms': [],
            'safety_denials': [],
            'numeric_values': [],
            'equipment_mentioned': []
        }
        
        try:
            # Поиск аварийных терминов
            emergency_matches = self.patterns['emergency'].findall(text)
            markers_found['emergency_terms'] = emergency_matches
            
            # Поиск маркеров срочности
            urgency_matches = self.patterns['urgency'].findall(text)
            markers_found['urgency_terms'] = urgency_matches
            
            # Поиск отрицаний безопасности
            safety_matches = self.patterns['safety_denial'].findall(text)
            markers_found['safety_denials'] = safety_matches
            
            # Поиск числовых значений
            number_matches = self.patterns['numbers'].findall(text)
            markers_found['numeric_values'] = number_matches
            
            # Поиск упоминаний оборудования
            equipment_matches = self.patterns['equipment'].findall(text)
            markers_found['equipment_mentioned'] = equipment_matches
            
            return markers_found
            
        except Exception as e:
            print(f"Ошибка поиска маркеров: {e}")
            return markers_found
    
    def calculate_marker_score(self, markers):
        """Расчет оценки на основе найденных маркеров"""
        score = 0
        
        # Аварийные термины +3
        score += len(markers['emergency_terms']) * 3
        
        # Маркеры срочности +2
        score += len(markers['urgency_terms']) * 2
        
        # Отрицания безопасности +2
        score += len(markers['safety_denials']) * 2
        
        # Числовые значения (проверка на превышение)
        for value, unit in markers['numeric_values']:
            if self._check_threshold_exceeded(value, unit):
                score += 2
        
        # Оборудование +1
        score += len(markers['equipment_mentioned'])
        
        return min(score, 10)  # Ограничиваем максимальный балл
    
    def _check_threshold_exceeded(self, value, unit):
        """Проверка превышения пороговых значений"""
        try:
            value_num = float(value)
            
            # Примеры пороговых значений
            thresholds = {
                '°C': 70,    # температура
                'атм': 8,    # давление
                'бар': 8,
                'МПа': 0.8,
                '%': 90      # концентрация
            }
            
            threshold = thresholds.get(unit, float('inf'))
            return value_num > threshold
            
        except ValueError:
            return False
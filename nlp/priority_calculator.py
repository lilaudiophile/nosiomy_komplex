"""
Расчет уровня критичности сообщений
"""

from .entity_extractor import EntityExtractor
from .speech_act_classifier import SpeechActClassifier
from .critical_markers import CriticalMarkersDetector
from utils.constants import SPEECH_ACTS
from utils.logger import setup_logger

class PriorityCalculator:
    def __init__(self):
        self.logger = setup_logger('priority_calculator')
        self.entity_extractor = EntityExtractor()
        self.speech_act_classifier = SpeechActClassifier()
        self.markers_detector = CriticalMarkersDetector()
        
        # Базовые веса для типов речевых актов
        self.speech_act_weights = {
            'DIRECTIVE': 8,      # команды - высокий приоритет
            'REPRESENTATIVE': 3, # информация - низкий приоритет
            'COMMISSIVE': 4,     # обязательства - средний
            'EXPRESSIVE': 5,     # предупреждения - повышенный
            'DECLARATIVE': 7,    # изменения статуса - высокий
            'UNKNOWN': 3         # по умолчанию
        }
    
    def calculate_critical_level(self, text):
        """Расчет уровня критичности для текста"""
        if not text:
            return 1  # Минимальный уровень для пустого текста
        
        try:
            self.logger.info(f"Анализ текста: {text}")
            
            # 1. Классификация речевого акта
            speech_act = self.speech_act_classifier.classify_speech_act(text)
            base_level = self.speech_act_weights.get(speech_act['act'], 3)
            self.logger.info(f"🎯 Речевой акт: {speech_act['act']} (уровень: {base_level})")
            
            # 2. Поиск критических маркеров
            markers = self.markers_detector.detect_markers(text)
            marker_score = self.markers_detector.calculate_marker_score(markers)
            self.logger.info(f"🔍 Найдено маркеров: {marker_score} баллов")
            
            # 3. Извлечение сущностей
            entities = self.entity_extractor.extract_entities(text)
            entity_bonus = min(len(entities) * 0.5, 2)  # Бонус за сущности
            self.logger.info(f"🏷️ Извлечено сущностей: {len(entities)}")
            
            # 4. Расчет итогового уровня
            critical_level = base_level + marker_score + entity_bonus
            critical_level = max(1, min(15, round(critical_level)))  # Ограничение 1-15
            
            self.logger.info(f"Итоговый уровень критичности: {critical_level}")
            
            return critical_level
            
        except Exception as e:
            self.logger.error(f"Ошибка расчета критичности: {e}")
            return 3  # Уровень по умолчанию при ошибке
    
    def get_detailed_analysis(self, text):
        """Детальный анализ с разбивкой по компонентам"""
        analysis = {
            'text': text,
            'speech_act': None,
            'markers': None,
            'entities': None,
            'critical_level': 1
        }
        
        try:
            # Речевой акт
            analysis['speech_act'] = self.speech_act_classifier.classify_speech_act(text)
            
            # Критические маркеры
            analysis['markers'] = self.markers_detector.detect_markers(text)
            
            # Сущности
            analysis['entities'] = self.entity_extractor.extract_entities(text)
            
            # Итоговый уровень
            analysis['critical_level'] = self.calculate_critical_level(text)
            
        except Exception as e:
            self.logger.error(f"Ошибка детального анализа: {e}")
        
        return analysis
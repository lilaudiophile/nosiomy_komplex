"""
Классификация речевых актов по теории Сёрла
"""

from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
from config.model_config import MODEL_CONFIG

class SpeechActClassifier:
    def __init__(self):
        self.config = MODEL_CONFIG
        self.classifier = None
        self.tokenizer = None
        self.model = None
        self.load_model()
        
        # Маппинг категорий
        self.speech_act_map = {
            'LABEL_0': 'DIRECTIVE',      # директивы
            'LABEL_1': 'REPRESENTATIVE', # репрезентативы  
            'LABEL_2': 'COMMISSIVE',     # комиссивы
            'LABEL_3': 'EXPRESSIVE',     # экспрессивы
            'LABEL_4': 'DECLARATIVE'     # декларативы
        }
    
    def load_model(self):
        """Загрузка модели для классификации"""
        try:
            print("Загрузка модели для классификации речевых актов...")
            
            self.classifier = pipeline(
                "text-classification",
                model=self.config['bert_model'],
                tokenizer=self.config['bert_model']
            )
            
            print("Модель для классификации загружена")
            
        except Exception as e:
            print(f"Ошибка загрузки модели классификации: {e}")
    
    def classify_speech_act(self, text):
        """Классификация речевого акта"""
        if not text or self.classifier is None:
            return {'act': 'UNKNOWN', 'confidence': 0.0}
        
        try:
            result = self.classifier(text[:512])  # Обрезаем длинный текст
            
            predicted_label = result[0]['label']
            confidence = result[0]['score']
            
            speech_act = self.speech_act_map.get(predicted_label, 'UNKNOWN')
            
            return {
                'act': speech_act,
                'confidence': confidence,
                'raw_label': predicted_label
            }
            
        except Exception as e:
            print(f"Ошибка классификации речевого акта: {e}")
            return {'act': 'UNKNOWN', 'confidence': 0.0}
    
    def batch_classify(self, texts):
        """Пакетная классификация"""
        results = []
        for text in texts:
            results.append(self.classify_speech_act(text))
        return results
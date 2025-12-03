"""
Извлечение именованных сущностей с помощью Natasha
"""

from natasha import (
    Segmenter,
    MorphVocab,
    NewsEmbedding,
    NewsMorphTagger,
    NewsSyntaxParser,
    NewsNERTagger,
    Doc
)

class EntityExtractor:
    def __init__(self):
        self.segmenter = Segmenter()
        self.morph_vocab = MorphVocab()
        self.emb = NewsEmbedding()
        self.morph_tagger = NewsMorphTagger(self.emb)
        self.syntax_parser = NewsSyntaxParser(self.emb)
        self.ner_tagger = NewsNERTagger(self.emb)
        
        # Доменно-специфичные сущности
        self.industrial_entities = {
            'оборудование': ['станок', 'реактор', 'насос', 'компрессор', 'трансформатор'],
            'зоны': ['цех', 'склад', 'участок', 'зона', 'помещение'],
            'опасности': ['пожар', 'взрыв', 'утечка', 'задымление', 'обрушение']
        }
    
    def extract_entities(self, text):
        """Извлечение сущностей из текста"""
        try:
            doc = Doc(text)
            doc.segment(self.segmenter)
            doc.tag_morph(self.morph_tagger)
            doc.tag_ner(self.ner_tagger)
            
            entities = []
            
            # Стандартные сущности Natasha
            for span in doc.spans:
                entities.append({
                    'text': span.text,
                    'type': span.type,
                    'start': span.start,
                    'stop': span.stop,
                    'normalized': span.normalized
                })
            
            # Доменно-специфичные сущности
            industrial_entities = self._extract_industrial_entities(text)
            entities.extend(industrial_entities)
            
            return entities
            
        except Exception as e:
            print(f"Ошибка извлечения сущностей: {e}")
            return []
    
    def _extract_industrial_entities(self, text):
        """Извлечение промышленных сущностей"""
        entities = []
        text_lower = text.lower()
        
        for entity_type, keywords in self.industrial_entities.items():
            for keyword in keywords:
                if keyword in text_lower:
                    entities.append({
                        'text': keyword,
                        'type': f'INDUSTRIAL_{entity_type.upper()}',
                        'start': text_lower.find(keyword),
                        'stop': text_lower.find(keyword) + len(keyword)
                    })
        
        return entities
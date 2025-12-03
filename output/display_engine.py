"""
Вывод информации на дисплей
"""

import pygame
import time
from utils.constants import COLORS, CRITICAL_LEVELS
from utils.logger import setup_logger

class DisplayEngine:
    def __init__(self, width=480, height=320):
        self.logger = setup_logger('display_engine')
        self.width = width
        self.height = height
        self.screen = None
        self.font = None
        self.small_font = None
        self.is_initialized = False
        
        self.initialize_display()
    
    def initialize_display(self):
        """Инициализация дисплея"""
        try:
            # Инициализация pygame
            pygame.init()
            
            # Создание экрана (для TFT дисплея)
            self.screen = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption("Носимый комплекс с ИИ")
            
            # Загрузка шрифтов
            self.font = pygame.font.Font(None, 36)
            self.small_font = pygame.font.Font(None, 24)
            
            self.is_initialized = True
            self.logger.info("Движок отображения инициализирован")
            
            # Показать заставку
            self.show_splash_screen()
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации дисплея: {e}")
            self.is_initialized = False
    
    def show_splash_screen(self):
        """Показать заставку при запуске"""
        if not self.is_initialized:
            return
        
        try:
            self.screen.fill((0, 0, 0))  
            
            # Заголовок
            title = self.font.render("Носимый комплекс с ИИ", True, (255, 255, 255))
            subtitle = self.small_font.render("Для слабослышащих сотрудников", True, (200, 200, 200))
            
            title_rect = title.get_rect(center=(self.width//2, self.height//2 - 20))
            subtitle_rect = subtitle.get_rect(center=(self.width//2, self.height//2 + 20))
            
            self.screen.blit(title, title_rect)
            self.screen.blit(subtitle, subtitle_rect)
            
            pygame.display.flip()
            time.sleep(2) 
            
            self.clear_screen()
            
        except Exception as e:
            self.logger.error(f"Ошибка отображения заставки: {e}")
    
    def show_text(self, text, critical_level=1):
        """Отображение текста с цветовым кодированием"""
        if not self.is_initialized:
            return
        
        try:
            # Очистка экрана
            self.screen.fill((0, 0, 0))
            
            # Получение цвета для уровня критичности
            color = COLORS.get(critical_level, (255, 255, 255))
            level_description = CRITICAL_LEVELS.get(critical_level, "информация")
            
            # Отображение уровня критичности
            level_text = self.small_font.render(f"Уровень: {critical_level} ({level_description})", True, color)
            level_rect = level_text.get_rect(center=(self.width//2, 30))
            self.screen.blit(level_text, level_rect)
            
            # Разбивка текста на строки
            words = text.split()
            lines = []
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                test_surface = self.font.render(test_line, True, color)
                
                if test_surface.get_width() <= self.width - 40:  # Отступы
                    current_line.append(word)
                else:
                    lines.append(' '.join(current_line))
                    current_line = [word]
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # Отображение строк текста
            y_position = 80
            for line in lines:
                if y_position < self.height - 40:  # Не выходить за границы
                    text_surface = self.font.render(line, True, color)
                    text_rect = text_surface.get_rect(center=(self.width//2, y_position))
                    self.screen.blit(text_surface, text_rect)
                    y_position += 40
            
            # Мигание для критических уровней
            if critical_level >= 13:
                pygame.display.flip()
                time.sleep(0.3)
                self.screen.fill((255, 0, 0))  # Красный мигание
                pygame.display.flip()
                time.sleep(0.3)
                self.screen.fill((0, 0, 0))
            
            pygame.display.flip()
            
        except Exception as e:
            self.logger.error(f"Ошибка отображения текста: {e}")
    
    def show_system_status(self, status_dict):
        """Отображение статуса системы"""
        if not self.is_initialized:
            return
        
        try:
            self.screen.fill((0, 0, 0))
            
            y_position = 30
            for key, value in status_dict.items():
                status_text = self.small_font.render(f"{key}: {value}", True, (255, 255, 255))
                self.screen.blit(status_text, (20, y_position))
                y_position += 30
            
            pygame.display.flip()
            
        except Exception as e:
            self.logger.error(f"Ошибка отображения статуса: {e}")
    
    def clear_screen(self):
        """Очистка экрана"""
        if self.is_initialized:
            self.screen.fill((0, 0, 0))
            pygame.display.flip()
    
    def cleanup(self):
        """Очистка ресурсов"""
        try:
            if self.is_initialized:
                pygame.quit()
                self.logger.info("Ресурсы дисплея освобождены")
        except Exception as e:
            self.logger.error(f"Ошибка очистки дисплея: {e}")
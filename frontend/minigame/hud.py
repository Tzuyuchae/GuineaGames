import pygame
from .settings import *

class HUD:
    def __init__(self):
        try:
            self.font = pygame.font.Font(None, 36)
        except: pass

    def draw(self, screen, score):
        if not self.font: return
        
        # Draw Score as Food
        text = self.font.render(f"Food: {score}", True, GREEN) # Green for food
        
        # Background box
        bg = pygame.Surface((text.get_width() + 20, text.get_height() + 10))
        bg.set_alpha(150)
        bg.fill((0, 0, 0))
        
        screen.blit(bg, (10, 10))
        screen.blit(text, (20, 15))
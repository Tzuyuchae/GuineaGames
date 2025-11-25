"""
Score Reviewing Screen
Shows user the final score at the end of a game.
"""
import pygame
import sys
import os

# Add parent directory to path for imports if needed
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from minigame.button import Button
from minigame.settings import *


class FinalScoreScreen:
    """Screen for reviewing the final score after a game."""
    
    def __init__(self, screen_width=672, screen_height=864):
        """
        Initialize the score review screen.
        Args:
            screen_width: Width of the game screen
            screen_height: Height of the game screen
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Initialize font
        pygame.font.init()
        try:
            self.title_font = pygame.font.SysFont('Arial', 40, bold=True)
            self.score_font = pygame.font.SysFont('Arial', 30, bold=True)
        except:
            self.title_font = pygame.font.Font(None, 50)
            self.score_font = pygame.font.Font(None, 36)
        
        # Create home button
        self.button_home = Button(
            screen_width // 2 - 100, self.screen_height // 2 + 110, 
            200, 60,
            'HOME', (150, 0, 0), (200, 0, 0)
        )

    def update(self, events):
        """
        Handle events and update selector state.
        Returns: 'home' OR None
        """
        mouse_pos = pygame.mouse.get_pos()
        
        for event in events:
            # Check home button
            if self.button_home.check_click(event):
                return 'home'
        
        # Update hover states
        self.button_home.check_hover(mouse_pos)
        
        return None
    
    def draw(self, screen):
        """Draws the review screen."""
        screen.fill((40, 40, 60))
        
        # Title
        title_text = self.title_font.render("Exited the area!", True, WHITE)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, self.screen_height // 3))
        screen.blit(title_text, title_rect)

        # Score text
        score_text = self.score_font.render("Total Score: placeholder", True, WHITE)
        text_rect = score_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))

        # Draw score box background
        bg_rect = text_rect.inflate(self.screen_width // 4, self.screen_height // 8)
        pygame.draw.rect(screen, BLACK, bg_rect, border_radius=5)
        pygame.draw.rect(screen, GOLD, bg_rect, 2, border_radius=5)

        # Draw score text
        screen.blit(score_text, text_rect)

        # Draw Back button
        self.button_home.draw(screen)
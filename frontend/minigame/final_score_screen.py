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
    
    def __init__(self, score, total_fruit, screen_width=672, screen_height=864):
        """
        Initialize the score review screen.
        Args:
            screen_width: Width of the game screen
            screen_height: Height of the game screen
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.score = score
        self.total_fruit = total_fruit
        self.shown = None

        # Initialize font
        pygame.font.init()
        try:
            self.title_font = pygame.font.SysFont('Arial', 40, bold=True)
            self.score_font = pygame.font.SysFont('Arial', 30, bold=True)
        except:
            self.title_font = pygame.font.Font(None, 50)
            self.score_font = pygame.font.Font(None, 36)
        
        # Load Assets
        self.background_img = self._load_background()

        # Create home button
        self.button_home = Button(
            screen_width // 2 - 100, self.screen_height // 2 + 110, 
            200, 60,
            'HOME', (150, 0, 0), (200, 0, 0)
        )

    def _load_background(self):
        """Loads and scales the title background."""
        base_path = os.path.dirname(os.path.abspath(__file__))
        # Check multiple locations
        paths_to_check = [
            os.path.join(base_path, "../../images/BG_Title.png"),
            os.path.join(base_path, "../images/BG_Title.png"),
            os.path.join(base_path, "../../Global Assets/Sprites/More Sprites/BG Art/Title/BG_Title.png")
        ]
        
        for p in paths_to_check:
            if os.path.exists(p):
                try:
                    img = pygame.image.load(p).convert()
                    return pygame.transform.scale(img, (self.screen_width, self.screen_height))
                except:
                    pass
        return None

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
        # 1. Draw Background
        if self.background_img:
            screen.blit(self.background_img, (0, 0))
        else:
            screen.fill((40, 40, 60))

        # 2. Draw Semi-Transparent Overlay for Readability
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(100)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # 3. Draw Title with Shadow
        title_text = self.title_font.render("Exited the area!", True, WHITE)
        shadow_text = self.title_font.render("Exited the area!", True, BLACK)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, self.screen_height // 5))
        screen.blit(shadow_text, (title_rect.x + 2, title_rect.y + 2))
        screen.blit(title_text, title_rect)

        # Score text
        score_text = self.score_font.render(f"Fruit Collected: {self.score}", True, WHITE)
        total_fruit_text = self.score_font.render(f"Total Fruit: {self.total_fruit}", True, WHITE)
        text_rect = score_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))

        # Draw score box background
        bg_rect = text_rect.inflate(self.screen_width // 4, self.screen_height // 8)
        pygame.draw.rect(screen, BLACK, bg_rect, border_radius=5)
        pygame.draw.rect(screen, GOLD, bg_rect, 2, border_radius=5)

        # Draw score text
        screen.blit(score_text, (text_rect.x, text_rect.y - 20))
        screen.blit(total_fruit_text, (text_rect.x, text_rect.y + 20))

        # Draw Back button
        self.button_home.draw(screen)
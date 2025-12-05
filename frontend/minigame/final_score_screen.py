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

# --- DEFINE COLORS TO PREVENT ERRORS ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
GOLD = (255, 215, 0)

class FinalScoreScreen:
    """Screen for reviewing the final score after a game."""
    
    def __init__(self, score, total_fruit, screen_width=672, screen_height=864):
        """
        Initialize the score review screen.
        Args:
            score: The amount of fruit collected (int)
            total_fruit: Total available fruit (int) - (Optional display)
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # --- FIXED: Use the actual score passed from the game ---
        self.score = score
        self.total_fruit = total_fruit
        
        # --- CALCULATE COIN REWARD (10%) ---
        self.coin_reward = int(self.score * 0.1)
        if self.coin_reward < 1 and self.score > 0:
            self.coin_reward = 1 # Minimum 1 coin if you got fruit

        # Initialize font
        pygame.font.init()
        try:
            self.title_font = pygame.font.SysFont('Arial', 40, bold=True)
            self.score_font = pygame.font.SysFont('Arial', 30, bold=True)
            self.small_font = pygame.font.SysFont('Arial', 24)
        except:
            self.title_font = pygame.font.Font(None, 50)
            self.score_font = pygame.font.Font(None, 36)
            self.small_font = pygame.font.Font(None, 28)
        
        # Load Assets
        self.background_img = self._load_background()
        self.coin_icon = self._load_coin()

        # Create home button
        self.button_home = Button(
            screen_width // 2 - 100, self.screen_height // 2 + 150, 
            200, 60,
            'HOME', (150, 0, 0), (200, 0, 0)
        )

    def _load_background(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
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
                except: pass
        return None

    def _load_coin(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        # Try finding coin sprite
        paths = [
            os.path.join(base_path, "../../Global Assets/Sprites/Global/GL_Coin.png"),
            os.path.join(base_path, "../images/GL_Coin.png")
        ]
        for p in paths:
             if os.path.exists(p):
                 try:
                     return pygame.transform.scale(pygame.image.load(p).convert_alpha(), (30, 30))
                 except: pass
        return None

    def update(self, events):
        mouse_pos = pygame.mouse.get_pos()
        for event in events:
            if self.button_home.check_click(event):
                return 'home'
        self.button_home.check_hover(mouse_pos)
        return None
    
    def draw(self, screen):
        # 1. Background
        if self.background_img:
            screen.blit(self.background_img, (0, 0))
        else:
            screen.fill((40, 40, 60))

        # 2. Overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # 3. Title
        title_text = self.title_font.render("Run Complete!", True, WHITE)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, self.screen_height // 4))
        screen.blit(title_text, title_rect)

        # 4. Score Box
        box_w, box_h = 400, 200
        box_x = (self.screen_width - box_w) // 2
        box_y = (self.screen_height - box_h) // 2
        
        bg_rect = pygame.Rect(box_x, box_y, box_w, box_h)
        pygame.draw.rect(screen, (30, 30, 30), bg_rect, border_radius=10)
        pygame.draw.rect(screen, GOLD, bg_rect, 3, border_radius=10)

        # --- CHANGED: "Fruit" -> "Food" ---
        score_str = f"Food Collected + Bonuses: {self.score}"
        score_surf = self.score_font.render(score_str, True, WHITE)
        screen.blit(score_surf, (box_x + 40, box_y + 40))

        # Text: Coin Reward
        reward_str = f"Coin Bonus (10%): +{self.coin_reward}"
        reward_surf = self.score_font.render(reward_str, True, GOLD)
        screen.blit(reward_surf, (box_x + 40, box_y + 90))
        
        # Coin Icon
        if self.coin_icon:
            screen.blit(self.coin_icon, (box_x + 330, box_y + 88))

        # Note
        note = self.small_font.render("Rewards added to inventory!", True, GRAY)
        note_rect = note.get_rect(center=(self.screen_width // 2, box_y + 160))
        screen.blit(note, note_rect)

        # Button
        self.button_home.draw(screen)
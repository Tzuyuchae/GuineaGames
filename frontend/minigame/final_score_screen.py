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
            self.title_font = pygame.font.SysFont("Arial", 40, bold=True)
            self.score_font = pygame.font.SysFont("Arial", 30, bold=True)
        except Exception:
            self.title_font = pygame.font.Font(None, 50)
            self.score_font = pygame.font.Font(None, 36)

        # Final results data
        self.final_score = 0      # We treat this as "fruit collected"
        self.player_won = False
        self.reward = 0           # Coins earned this run

        # Create home button
        self.button_home = Button(
            self.screen_width // 2 - 100,
            self.screen_height // 2 + 110,
            200,
            60,
            "HOME",
            (150, 0, 0),
            (200, 0, 0),
        )

    # -------------------------------------------------------------------------
    # Public API used by MinigamePage / Game
    # -------------------------------------------------------------------------
    def set_results(self, score: int, player_won: bool = False, reward: int | None = None):
        """
        Set the final results that this screen will display.

        Args:
            score: numeric score from the game (here: fruit collected)
            player_won: whether the player "won" the run
            reward: coins reward to grant; if None, derived from score
        """
        # Treat score as "fruit collected"
        self.final_score = max(0, int(score))
        self.player_won = bool(player_won)

        if reward is None:
            # Default: 10 coins per fruit
            self.reward = max(0, self.final_score * 10)
        else:
            self.reward = max(0, int(reward))

    def get_reward_amount(self) -> int:
        """Return how many coins this run should reward."""
        return int(self.reward)

    # -------------------------------------------------------------------------
    # Event / draw loop
    # -------------------------------------------------------------------------
    def update(self, events):
        """
        Handle events and update selector state.
        Returns: 'home' OR None
        """
        mouse_pos = pygame.mouse.get_pos()

        for event in events:
            # Check home button
            if self.button_home.check_click(event):
                return "home"

        # Update hover states
        self.button_home.check_hover(mouse_pos)

        return None

    def draw(self, screen):
        """Draws the review screen."""
        screen.fill((40, 40, 60))

        # Title changes slightly if player won vs lost/exited
        if self.player_won:
            title_str = "Level Complete!"
        else:
            title_str = "Exited the area!"

        title_text = self.title_font.render(title_str, True, WHITE)
        title_rect = title_text.get_rect(
            center=(self.screen_width // 2, self.screen_height // 3)
        )
        screen.blit(title_text, title_rect)

        # Score text (fruit)
        score_str = f"Fruit Collected: {self.final_score}"
        score_text = self.score_font.render(score_str, True, WHITE)
        score_rect = score_text.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2 - 20)
        )

        # Reward text (coins)
        reward_str = f"Coins Earned: {self.reward}"
        reward_text = self.score_font.render(reward_str, True, GOLD)
        reward_rect = reward_text.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2 + 30)
        )

        # Draw score box background (big enough for both lines)
        combined_rect = score_rect.union(reward_rect)
        bg_rect = combined_rect.inflate(self.screen_width // 4, self.screen_height // 8)
        pygame.draw.rect(screen, BLACK, bg_rect, border_radius=5)
        pygame.draw.rect(screen, GOLD, bg_rect, 2, border_radius=5)

        # Draw score and reward text
        screen.blit(score_text, score_rect)
        screen.blit(reward_text, reward_rect)

        # Draw Home button
        self.button_home.draw(screen)

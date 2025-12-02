# frontend/game_context.py

import pygame
from frontend_button import Button

class GameContext:
    def __init__(self):
        # -----------------------------
        # User info (from session)
        # -----------------------------
        self.user_id = None
        self.username = None
        self.email = None

        # -----------------------------
        # Save Data Reference
        # -----------------------------
        self.save_data = None

        # -----------------------------
        # Game Time (loaded from save file in main.py)
        # -----------------------------
        self.game_time = {
            "year": 1,
            "month": 1,
            "day": 1,
            "hour": 12,
            "minute": 0,
            "am": True
        }

        # Time simulation config
        self.SECONDS_PER_GAME_MINUTE = 5
        self.last_time_update = 0.0

        # -----------------------------
        # UI Buttons (initialized after pygame starts)
        # -----------------------------
        self.store_button = None
        self.pellet_button = None
        self.water_button = None
        self.pig_buttons = []

    # ----------------------------------
    # Initialize UI after pygame starts
    # ----------------------------------
    def init_ui(self):
        """Create all UI buttons once pygame is initialized."""
        if self.store_button is None:
            self.store_button = Button(pygame.Rect(1080, 20, 180, 60), "Store")

        if self.pellet_button is None:
            self.pellet_button = Button(pygame.Rect(100, 500, 200, 60), "Buy Pellets")

        if self.water_button is None:
            self.water_button = Button(pygame.Rect(100, 580, 200, 60), "Buy Water")

        if not self.pig_buttons:
            for i in range(3):
                self.pig_buttons.append(
                    Button(pygame.Rect(400 + i * 250, 500, 200, 60), f"Pig {i+1}")
                )


# Global shared instance
game_context = GameContext()

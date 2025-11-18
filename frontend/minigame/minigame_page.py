<<<<<<< HEAD:minigame/minigame_page.py
import pygame

from minigame.guinea_pig_selector import GuineaPigSelector
from minigame.game import Game

class MinigamePage:
    """Encapsulates state and logic for the minigame page."""
    def __init__(self, user_id=1):
        self.state = 'selector'  # Can be 'selector' or 'playing'
        self.guinea_pig_selector = None
        self.game_instance = None
        self.selected_guinea_pig = None
        self.user_id = user_id

    def initialize_selector(self):
        """Initialize the guinea pig selector."""
        self.guinea_pig_selector = GuineaPigSelector(user_id=self.user_id)

    def update(self, events):
        """Handles events for the minigame page."""
        # Initialize selector on first run
        if self.guinea_pig_selector is None:
            self.initialize_selector()

        if self.state == 'selector':
            # Handle selector events
            result = self.guinea_pig_selector.update(events)

            if result == 'back':
                # Reset state when going back
                self.state = 'selector'
                self.game_instance = None
                self.selected_guinea_pig = None
                return 'homescreen'

            elif isinstance(result, (tuple, list)) and len(result) > 0 and result[0] == 'start_game':
                # User selected a guinea pig and clicked start
                _, self.selected_guinea_pig = result
                self.game_instance = Game(selected_guinea_pig=self.selected_guinea_pig)
                self.state = 'playing'

        elif self.state == 'playing':
            # Handle game events
            if self.game_instance:
                result = self.game_instance.update(events)
                if result == 'homescreen':
                    # Game ended, reset state
                    self.state = 'selector'
                    self.game_instance = None
                    self.selected_guinea_pig = None
                    self.guinea_pig_selector = None  # Reinitialize next time
                    return 'homescreen'

        return None  # Stay on this screen

    def draw(self, screen):
        """Draws the minigame page."""
        if self.state == 'selector' and self.guinea_pig_selector:
            self.guinea_pig_selector.draw(screen)
        elif self.state == 'playing' and self.game_instance:
            self.game_instance.draw(screen)
=======
import pygame
from frontend.minigame.button import Button

# A 'Back' button, positioned for the 672x864 screen
button_back = Button(236, 500, 200, 70, 'BACK', (150, 150, 0), (200, 200, 0))

def minigame_update(events):
    """Handles events for the minigame page."""
    mouse_pos = pygame.mouse.get_pos()
    
    for event in events:
        if button_back.check_click(event):
            print("Back button clicked! Returning to homescreen.")
            return 'homescreen' # Return to the menu
            
    button_back.check_hover(mouse_pos)
    return None # Stay on this screen

def minigame_draw(screen):
    """Draws the minigame page."""
    # Draw the back button
    button_back.draw(screen)
>>>>>>> 9f7d620 (t):frontend/minigame/minigame_page.py

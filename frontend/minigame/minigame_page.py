import pygame
from minigame.guinea_pig_selector import GuineaPigSelector
from minigame.game import Game

class MinigamePage:
    """
    Encapsulates state and logic for the minigame section.
    Manages switching between the Guinea Pig Selector and the actual Game loop.
    """
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
        """
        Handles events for the minigame page.
        Returns 'homescreen' if the user backs out of the minigame entirely.
        """
        # Lazy initialization: Create selector on first run
        if self.guinea_pig_selector is None:
            self.initialize_selector()

        # --- LOGIC FOR SELECTOR SCREEN ---
        if self.state == 'selector':
            # Handle selector events
            result = self.guinea_pig_selector.update(events)

            # Case 1: User clicked Back in the selector
            if result == 'back':
                self._reset_state()
                return 'homescreen'

            # Case 2: User selected a pig and clicked Start
            # Expecting tuple: ('start_game', selected_pig_data)
            elif isinstance(result, (tuple, list)) and len(result) > 0 and result[0] == 'start_game':
                _, self.selected_guinea_pig = result
                
                # Initialize the Game with the selected pig
                self.game_instance = Game(selected_guinea_pig=self.selected_guinea_pig)
                self.state = 'playing'

        # --- LOGIC FOR PLAYING GAME ---
        elif self.state == 'playing':
            if self.game_instance:
                self.game_instance.update(events)

                # Check if the game loop has finished (Win, Lose, or Back button)
                # We check the .running attribute of the Game class
                if not self.game_instance.running:
                    self._reset_state()
                    return 'homescreen'

        return None  # Stay on this screen

    def draw(self, screen):
        """Draws the current state (Selector or Game) to the screen."""
        if self.state == 'selector' and self.guinea_pig_selector:
            self.guinea_pig_selector.draw(screen)
        
        elif self.state == 'playing' and self.game_instance:
            self.game_instance.draw(screen)

    def _reset_state(self):
        """Helper to reset all minigame state variables."""
        self.state = 'selector'
        self.game_instance = None
        self.selected_guinea_pig = None
        # We set selector to None so it reloads fresh next time (optional)
        self.guinea_pig_selector = None
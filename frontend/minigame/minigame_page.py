import pygame
from minigame.guinea_pig_selector import GuineaPigSelector
from minigame.game import Game
from minigame.pause_menu import PauseMenu  # <--- IMPORT THE NEW MENU

class MinigamePage:
    """
    Encapsulates state and logic for the minigame section.
    Manages switching between the Guinea Pig Selector, the Game loop, and the Pause Menu.
    """
    def __init__(self, user_id=1):
        self.state = 'selector'  # Can be 'selector', 'playing'
        self.guinea_pig_selector = None
        self.game_instance = None
        self.selected_guinea_pig = None
        self.user_id = user_id
        
        # --- PAUSE MENU SETUP ---
        self.paused = False
        # We use the screen size defined in main.py (672, 864)
        self.pause_menu = PauseMenu(672, 864) 

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

        # --- GLOBAL PAUSE TOGGLE (Only works while playing) ---
        if self.state == 'playing':
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.paused = not self.paused

            # IF PAUSED: INTERCEPT INPUTS HERE
            if self.paused:
                # We need to loop through events again or pass the specific event? 
                # Ideally, pass the event list to the menu if it supported it, 
                # but our menu takes single events. Let's filter mouse clicks.
                for event in events:
                    action = self.pause_menu.handle_input(event)
                    
                    if action == 'resume':
                        self.paused = False
                    elif action == 'quit':
                        self._reset_state()
                        return 'homescreen'
                    elif action == 'settings':
                        print("Settings clicked (Feature TODO)")
                
                # If paused, DO NOT run the rest of the game logic
                return None 

        # --- LOGIC FOR SELECTOR SCREEN ---
        if self.state == 'selector':
            # Handle selector events
            result = self.guinea_pig_selector.update(events)

            # Case 1: User clicked Back in the selector
            if result == 'back':
                self._reset_state()
                return 'homescreen'

            # Case 2: User selected a pig and clicked Start
            elif isinstance(result, (tuple, list)) and len(result) > 0 and result[0] == 'start_game':
                _, self.selected_guinea_pig = result
                
                # Initialize the Game with the selected pig
                self.game_instance = Game(selected_guinea_pig=self.selected_guinea_pig)
                self.state = 'playing'
                self.paused = False # Ensure we start unpaused

        # --- LOGIC FOR PLAYING GAME ---
        elif self.state == 'playing':
            if self.game_instance:
                # Only update game physics if NOT paused
                if not self.paused:
                    self.game_instance.update(events)

                    # Check if the game loop has finished (Win, Lose, or Back button)
                    if not self.game_instance.running:
                        self._reset_state()
                        return 'homescreen'

        return None  # Stay on this screen

    def draw(self, screen):
        """Draws the current state (Selector or Game) to the screen."""
        
        if self.state == 'selector' and self.guinea_pig_selector:
            self.guinea_pig_selector.draw(screen)
        
        elif self.state == 'playing' and self.game_instance:
            # 1. Draw the game first (so it appears "frozen" behind the menu)
            self.game_instance.draw(screen)

            # 2. Draw Pause Menu overlay on top if paused
            if self.paused:
                self.pause_menu.draw(screen)

    def _reset_state(self):
        """Helper to reset all minigame state variables."""
        self.state = 'selector'
        self.game_instance = None
        self.selected_guinea_pig = None
        self.guinea_pig_selector = None
        self.paused = False
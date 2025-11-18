import pygame
from button import Button
from minigame.guinea_pig_selector import GuineaPigSelector
from minigame.game import Game

# State management for minigame flow
minigame_state = 'selector'  # Can be 'selector' or 'playing'
guinea_pig_selector = None
game_instance = None
selected_guinea_pig = None

def initialize_selector():
    """Initialize the guinea pig selector."""
    global guinea_pig_selector
    guinea_pig_selector = GuineaPigSelector(user_id=1)

def minigame_update(events):
    """Handles events for the minigame page."""
    global minigame_state, game_instance, selected_guinea_pig, guinea_pig_selector
    
    # Initialize selector on first run
    if guinea_pig_selector is None:
        initialize_selector()
    
    if minigame_state == 'selector':
        # Handle selector events
        result = guinea_pig_selector.update(events)
        
        if result == 'back':
            # Reset state when going back
            minigame_state = 'selector'
            game_instance = None
            selected_guinea_pig = None
            return 'homescreen'
        
        elif result and result[0] == 'start_game':
            # User selected a guinea pig and clicked start
            _, selected_guinea_pig = result
            game_instance = Game(selected_guinea_pig=selected_guinea_pig)
            minigame_state = 'playing'
    
    elif minigame_state == 'playing':
        # Handle game events
        if game_instance:
            result = game_instance.update(events)
            if result == 'homescreen':
                # Game ended, reset state
                minigame_state = 'selector'
                game_instance = None
                selected_guinea_pig = None
                guinea_pig_selector = None  # Reinitialize next time
                return 'homescreen'
    
    return None  # Stay on this screen

def minigame_draw(screen):
    """Draws the minigame page."""
    global minigame_state, game_instance, guinea_pig_selector
    
    if minigame_state == 'selector' and guinea_pig_selector:
        guinea_pig_selector.draw(screen)
    
    elif minigame_state == 'playing' and game_instance:
        game_instance.draw(screen)
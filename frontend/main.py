import pygame
pygame.init()

from guineapig import Guineapig
from title import title_update, title_draw
from homescreen import homescreen_init, homescreen_update, homescreen_draw
# Import the actual minigame class from the minigame/game.py file
from minigame.game import Game 



# Original screen size for your main game
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Guinea Games")

clock = pygame.time.Clock()
FPS = 60
current_page = "title"

# Add a variable to hold the minigame instance
active_minigame = None

# Initialize homescreen assets
homescreen_init()

# Load guinea pig
player_pig = Guineapig(screen_width // 2, screen_height // 2)

running = True 
while running:
    # Get all events for this frame
    events = pygame.event.get()
    
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    if current_page == "title":
        # Make sure we're using the main screen size
        screen = pygame.display.set_mode((screen_width, screen_height))
        
        next_page = title_update(events)
        title_draw(screen)
        
        if next_page == "homescreen":
            current_page = "homescreen"

    elif current_page == "homescreen":
        # Make sure we're using the main screen size
        screen = pygame.display.set_mode((screen_width, screen_height))
        
        next_page = homescreen_update(events)
        homescreen_draw(screen)
        #player_pig.draw(screen)
        
        # Check if the button clicked was 'mini_games'
        if next_page == "mini_games":
            print("Starting minigame!")
            # Create an instance of the minigame
            active_minigame = Game()
            # Set the screen size to match the minigame's maze
            screen = pygame.display.set_mode((active_minigame.maze.width, active_minigame.maze.height))
            current_page = "minigame"
        elif next_page:
            # Handle other button clicks if needed
            print(f"Navigating to {next_page}")

    # Add a new state for running the minigame
    elif current_page == "minigame":
        if active_minigame:
            # Update the minigame
            next_page = active_minigame.update(events)
            # Draw the minigame
            active_minigame.draw(screen)
            
            # Check if the minigame's update function wants to return to the homescreen
            if next_page == "homescreen":
                current_page = "homescreen"
                active_minigame = None # Clear the game instance
                # Reset screen to main size
                screen = pygame.display.set_mode((screen_width, screen_height))
        else:
            # Failsafe: if no minigame is active, go home
            current_page = "homescreen"
            # Reset screen to main size
            screen = pygame.display.set_mode((screen_width, screen_height))


    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
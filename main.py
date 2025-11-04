import pygame
import homescreen
import details_page
import breeding
import minigame
# from guineapig import Guineapig 

# Initialize Pygame
pygame.init()

# Set screen dimensions
screen_width = 1920
screen_height = 1080
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("My Game")
clock = pygame.time.Clock() 

# This is your "state machine" variable
currentmenu = "homescreen"

# --- THIS IS THE "MAIN" LOOP ---
running = True
while running:
    # 1. Handle Events
    events = pygame.event.get() 
    for event in events: 
        if event.type == pygame.QUIT:
            running = False

    # 2. Update Game Logic
    if currentmenu == 'homescreen':
        new_state = homescreen.menu_update(events)
        if new_state:
            currentmenu = new_state
    
    elif currentmenu == 'details':
        new_state = details_page.details_update(events)
        if new_state:
            currentmenu = new_state

    elif currentmenu == 'breeding':
        new_state = breeding.breeding_update(events)
        if new_state:
            currentmenu = new_state

    elif currentmenu == 'minigame':
        new_state = minigame.minigame_update(events)
        if new_state:
            currentmenu = new_state

    # (We still need to add 'gameplay')
    # elif currentmenu == 'gameplay':
    #     ...


    # 3. Draw to Screen
    screen.fill((20, 20, 20))  # Fill with a dark grey background

    if currentmenu == 'homescreen':
        homescreen.menu_draw(screen)

    # --- (FIXED) ADDED THE DRAW CALLS FOR THE OTHER STATES ---
    elif currentmenu == 'details':
        details_page.details_draw(screen)

    elif currentmenu == 'breeding':
        breeding.breeding_draw(screen)

    elif currentmenu == 'minigame':
        minigame.minigame_draw(screen)

    # (We still need to add 'gameplay')
    # elif currentmenu == 'gameplay':
    #     ...


    # 4. Update the Display
    pygame.display.flip()
    
    # 5. Cap the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()

import pygame
from guineapig import Guineapig
from time import getPlayerPigs, inc_month, closingUpdate


# Initialize Pygame
pygame.init()
clock = pygame.time.clock()

# Set screen dimensions
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Image Display Example")

# --- THIS IS WHERE YOU SHOULD LOAD ASSETS ---
try:
    # Load the image ONCE here, before the loop
    image = pygame.image.load('images/guineapig.png') 
    player_pig = Guineapig(screen_width // 2, screen_height // 2)
except pygame.error as message:
    print(f"Cannot load image: {message}")
    pygame.quit()
    exit()

# Get the image rectangle for positioning
image_rect = image.get_rect()
image_rect.center = (screen_width // 2, screen_height // 2)  # Center the image
# --- END OF ASSET LOADING ---


# --- THIS IS YOUR "MAIN" LOOP ---
playerPigs = getPlayerPigs()
FPS = 30
running = True
while running:
    # 1. Handle Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = closingUpdate(playerPigs)

    # 2. Update Game Logic (nothing to update yet)


    # 3. In-game clock
    timePassed += 1
    if timePassed == 300000:        #300k ms is ~5 minutes
        timePassed = 0
        inc_month()

    # 4. Draw to Screen
    screen.fill((255, 255, 255))  # White background
    screen.blit(image, image_rect) # Draw the image

    # 5. Update the Display
    pygame.display.flip() # <--- THIS MUST BE INSIDE THE LOOP
    clock.tick(FPS)

# Quit Pygame
pygame.quit()

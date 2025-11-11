import pygame
pygame.init()

from guineapig import Guineapig
from title import title_update, title_draw
from homescreen import homescreen_init, homescreen_update, homescreen_draw



screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Guinea Games")

clock = pygame.time.Clock()
FPS = 60
current_page = "title"

# Initialize homescreen assets
homescreen_init()

# Load guinea pig
player_pig = Guineapig(screen_width // 2, screen_height // 2)

running = True
while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    if current_page == "title":
        next_page = title_update(events)
        title_draw(screen)
        if next_page == "homescreen":
            current_page = "homescreen"

    elif current_page == "homescreen":
        next_page = homescreen_update(events)
        homescreen_draw(screen)
        #player_pig.draw(screen)
        if next_page:
            print(f"Navigating to {next_page}")

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()

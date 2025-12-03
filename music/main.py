import pygame
import os
import homescreen
import details_page
import breeding
from minigame import minigame_page  # ← FIXED IMPORT
import title
import settings_page
import random  # --- NEW ---
from volume_settings import get_music_volume, load_settings

# Load volume settings on startup
load_settings()

def play_music_with_volume(music_path):
    """Helper function to play music with volume control."""
    try:
        if os.path.exists(music_path):
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(get_music_volume())
            pygame.mixer.music.play(-1)  # Loop indefinitely
            return True
        else:
            print(f"Music file not found: {music_path}")
            return False
    except Exception as e:
        print(f"Could not load music: {e}")
        return False

# --- NEW: Import all your game classes ---
from minigame.maze_generator import MazeGenerator
from minigame.maze import Maze
from minigame.player import Player
from minigame.enemy import Enemy
from minigame.fruits import Fruit

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen setup
screen_width = 672
screen_height = 864
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("My Game")
clock = pygame.time.Clock()

currentmenu = "title"

# Music flags
gameplay_music_playing = False
title_music_playing = False
home_music_playing = False
breeding_music_playing = False


def start_new_game():
    print("Starting new game...")

    generator = MazeGenerator(seed=random.randint(0, 9999))
    base_layout = generator.generate()

    player = Player()
    layout_with_player = player.add_player(base_layout)

    enemy = Enemy()
    final_layout = enemy.add_enemies(layout_with_player)

    maze = Maze(final_layout)
    fruit_obj = Fruit()

    return maze, player, enemy, fruit_obj


maze, player, enemy, fruit_obj = start_new_game()


running = True
while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    # Update Logic
    if currentmenu == 'title':
        if not title_music_playing:
            start_music_path = os.path.join("music", "start.wav")
            if play_music_with_volume(start_music_path):
                title_music_playing = True

        new_state = title.title_update(events)
        if new_state:
            currentmenu = new_state
            if title_music_playing:
                pygame.mixer.music.stop()
                title_music_playing = False

    elif currentmenu == 'homescreen':
        if not home_music_playing:
            journey_music_path = os.path.join("music", "journey.wav")
            if play_music_with_volume(journey_music_path):
                home_music_playing = True

        new_state = homescreen.menu_update(events)
        if new_state == 'gameplay':
            maze, player, enemy, fruit_obj = start_new_game()
            currentmenu = 'gameplay'
            if home_music_playing:
                pygame.mixer.music.stop()
                home_music_playing = False
            boss_music_path = os.path.join("music", "boss battle.wav")
            if play_music_with_volume(boss_music_path):
                gameplay_music_playing = True

        elif new_state:
            currentmenu = new_state
            if home_music_playing:
                pygame.mixer.music.stop()
                home_music_playing = False
            if gameplay_music_playing:
                pygame.mixer.music.stop()
                gameplay_music_playing = False
            if breeding_music_playing:
                pygame.mixer.music.stop()
                breeding_music_playing = False

    elif currentmenu == 'details':
        new_state = details_page.details_update(events)
        if new_state:
            currentmenu = new_state
            if new_state == 'homescreen' and not home_music_playing:
                journey_music_path = os.path.join("music", "journey.wav")
                if play_music_with_volume(journey_music_path):
                    home_music_playing = True

    elif currentmenu == 'breeding':
        if not breeding_music_playing:
            breeding_music_path = os.path.join("music", "yeahhhhh yuh.wav")
            if play_music_with_volume(breeding_music_path):
                breeding_music_playing = True

        new_state = breeding.breeding_update(events)
        if new_state:
            currentmenu = new_state
            if breeding_music_playing:
                pygame.mixer.music.stop()
                breeding_music_playing = False
            if new_state == 'homescreen' and not home_music_playing:
                journey_music_path = os.path.join("music", "journey.wav")
                if play_music_with_volume(journey_music_path):
                    home_music_playing = True

    elif currentmenu == 'minigame':
        new_state = minigame_page.minigame_update(events)
        if new_state:
            currentmenu = new_state
            if new_state == 'homescreen' and not home_music_playing:
                journey_music_path = os.path.join("music", "journey.wav")
                if play_music_with_volume(journey_music_path):
                    home_music_playing = True

    elif currentmenu == 'settings':
        if not hasattr(settings_page, 'button_back') or settings_page.button_back is None:
            settings_page.settings_init()

        new_state = settings_page.settings_update(events)
        if new_state:
            currentmenu = new_state
            if new_state == 'homescreen' and not home_music_playing:
                journey_music_path = os.path.join("music", "journey.wav")
                if play_music_with_volume(journey_music_path):
                    home_music_playing = True

    elif currentmenu == 'gameplay':
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    player.move(0, -1, maze)
                elif event.key == pygame.K_DOWN:
                    player.move(0, 1, maze)
                elif event.key == pygame.K_LEFT:
                    player.move(-1, 0, maze)
                elif event.key == pygame.K_RIGHT:
                    player.move(1, 0, maze)

        enemy.move_towards_player(player.player_pos(), maze)
        maze.layout = fruit_obj.if_collected(player.player_pos(), maze.layout)

        if player.player_pos() == enemy.enemy_pos():
            print("GAME OVER! You were caught!")
            currentmenu = 'homescreen'
            if gameplay_music_playing:
                pygame.mixer.music.stop()
                gameplay_music_playing = False
            if not home_music_playing:
                journey_music_path = os.path.join("music", "journey.wav")
                if play_music_with_volume(journey_music_path):
                    home_music_playing = True

        if fruit_obj.all_fruits_collected(maze.layout):
            print("YOU WIN! All fruits collected!")
            currentmenu = 'homescreen'
            if gameplay_music_playing:
                pygame.mixer.music.stop()
                gameplay_music_playing = False
            if not home_music_playing:
                journey_music_path = os.path.join("music", "journey.wav")
                if play_music_with_volume(journey_music_path):
                    home_music_playing = True

    # DRAWING
    screen.fill((20, 20, 20))

    if currentmenu == 'homescreen':
        homescreen.menu_draw(screen)
    elif currentmenu == 'details':
        details_page.details_draw(screen)
    elif currentmenu == 'breeding':
        breeding.breeding_draw(screen)
    elif currentmenu == 'minigame':
        minigame_page.minigame_draw(screen)
    elif currentmenu == 'settings':
        settings_page.settings_draw(screen)
    elif currentmenu == 'title':
        title.title_draw(screen)
    elif currentmenu == 'gameplay':
        maze.draw(screen)
        fruit_obj.draw(screen, maze.layout)
        player.draw(screen)
        enemy.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

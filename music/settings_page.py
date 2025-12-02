import pygame
import sys
import os
from button import Button

# Add parent directory to path to import volume_settings
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from volume_settings import (
    get_music_volume, set_music_volume,
    get_sfx_volume, set_sfx_volume,
    increase_music_volume, decrease_music_volume,
    increase_sfx_volume, decrease_sfx_volume
)

# Buttons
button_back = None
button_music_up = None
button_music_down = None
button_sfx_up = None
button_sfx_down = None

# Font
font = None
title_font = None

def settings_init():
    """Initialize settings page."""
    global button_back, button_music_up, button_music_down, button_sfx_up, button_sfx_down, font, title_font
    
    font = pygame.font.Font(None, 36)
    title_font = pygame.font.Font(None, 48)
    
    # Back button
    button_back = Button(400, 550, 200, 70, 'BACK', (150, 0, 0), (200, 0, 0))
    
    # Volume control buttons
    button_music_up = Button(500, 200, 80, 50, '+', (0, 150, 0), (0, 200, 0))
    button_music_down = Button(300, 200, 80, 50, '-', (150, 0, 0), (200, 0, 0))
    button_sfx_up = Button(500, 300, 80, 50, '+', (0, 150, 0), (0, 200, 0))
    button_sfx_down = Button(300, 300, 80, 50, '-', (150, 0, 0), (200, 0, 0))

def settings_update(events):
    """Handles events for the settings page."""
    global button_back, button_music_up, button_music_down, button_sfx_up, button_sfx_down
    
    mouse_pos = pygame.mouse.get_pos()
    
    for event in events:
        if button_back.check_click(event):
            print("Back button clicked! Returning to homescreen.")
            return 'homescreen'
        
        if button_music_up.check_click(event):
            increase_music_volume(0.1)
            # Update currently playing music volume
            try:
                pygame.mixer.music.set_volume(get_music_volume())
            except Exception:
                pass
        
        if button_music_down.check_click(event):
            decrease_music_volume(0.1)
            # Update currently playing music volume
            try:
                pygame.mixer.music.set_volume(get_music_volume())
            except Exception:
                pass
        
        if button_sfx_up.check_click(event):
            increase_sfx_volume(0.1)
        
        if button_sfx_down.check_click(event):
            decrease_sfx_volume(0.1)
    
    # Update hover states
    button_back.check_hover(mouse_pos)
    button_music_up.check_hover(mouse_pos)
    button_music_down.check_hover(mouse_pos)
    button_sfx_up.check_hover(mouse_pos)
    button_sfx_down.check_hover(mouse_pos)
    
    return None

def settings_draw(screen):
    """Draws the settings page."""
    global button_back, button_music_up, button_music_down, button_sfx_up, button_sfx_down, font, title_font
    
    # Fill background
    screen.fill((240, 240, 240))
    
    # Draw title
    title_text = title_font.render("Settings", True, (0, 0, 0))
    title_rect = title_text.get_rect(center=(screen.get_width() // 2, 50))
    screen.blit(title_text, title_rect)
    
    # Draw volume labels and values
    music_label = font.render("Music Volume:", True, (0, 0, 0))
    screen.blit(music_label, (200, 150))
    
    music_volume = int(get_music_volume() * 100)
    music_value = font.render(f"{music_volume}%", True, (0, 0, 0))
    screen.blit(music_value, (400, 150))
    
    sfx_label = font.render("SFX Volume:", True, (0, 0, 0))
    screen.blit(sfx_label, (200, 250))
    
    sfx_volume = int(get_sfx_volume() * 100)
    sfx_value = font.render(f"{sfx_volume}%", True, (0, 0, 0))
    screen.blit(sfx_value, (400, 250))
    
    # Draw buttons
    button_back.draw(screen)
    button_music_up.draw(screen)
    button_music_down.draw(screen)
    button_sfx_up.draw(screen)
    button_sfx_down.draw(screen)


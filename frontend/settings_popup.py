import pygame
import sys
import os

# --- ASSUMED EXTERNAL IMPORTS ---
# Assuming 'Button' class is available globally or imported from 'button'
try:
    from button import Button
except ImportError:
    class Button:
        """Mock Button class for combined script."""
        def __init__(self, x, y, w, h, text, color, hover_color):
            self.rect = pygame.Rect(x, y, w, h)
            self.text = text
            self.color = color
            self.hover_color = hover_color
            self.is_hovered = False
            self.font = pygame.font.Font(None, 30)

        def check_click(self, event):
            if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
                return True
            return False

        def check_hover(self, mouse_pos):
            self.is_hovered = self.rect.collidepoint(mouse_pos)
            
        def draw(self, screen):
            color = self.hover_color if self.is_hovered else self.color
            pygame.draw.rect(screen, color, self.rect, border_radius=8)
            text_surf = self.font.render(self.text, True, (255, 255, 255))
            screen.blit(text_surf, text_surf.get_rect(center=self.rect.center))
    print("Warning: Using Mock Button class.")

# Add parent directory to path to import volume_settings
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from volume_settings import (
        get_music_volume, set_music_volume,
        get_sfx_volume, set_sfx_volume,
        increase_music_volume, decrease_music_volume,
    )
    # Ensure all required volume functions exist or provide mocks
    def increase_sfx_volume(delta):
        set_sfx_volume(min(1.0, get_sfx_volume() + delta))
    def decrease_sfx_volume(delta):
        set_sfx_volume(max(0.0, get_sfx_volume() - delta))
except ImportError:
    print("Warning: volume_settings not found. Using simple internal volume logic.")
    _music_vol = 0.5
    _sfx_vol = 0.5
    def get_music_volume(): return _music_vol
    def set_music_volume(v): global _music_vol; _music_vol = max(0.0, min(1.0, v))
    def get_sfx_volume(): return _sfx_vol
    def set_sfx_volume(v): global _sfx_vol; _sfx_vol = max(0.0, min(1.0, v))
    def increase_music_volume(d): set_music_volume(get_music_volume() + d)
    def decrease_music_volume(d): set_music_volume(get_music_volume() - d)
    def increase_sfx_volume(d): set_sfx_volume(get_sfx_volume() + d)
    def decrease_sfx_volume(d): set_sfx_volume(get_sfx_volume() - d)


# --- COLORS ---
OVERLAY_COLOR = (0, 0, 0, 180)
PANEL_COLOR = (50, 50, 60)
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
GOLD = (255, 215, 0) 
BLACK = (0, 0, 0) 


class SettingsPopup:
    def __init__(self, screen_width, screen_height):
        self.screen_w = screen_width
        self.screen_h = screen_height
        self.active = False
        
        # Panel sizing (adjusted to fit new elements)
        self.panel_w = 400
        self.panel_h = 580 
        self.panel_x = (screen_width - self.panel_w) // 2
        self.panel_y = (screen_height - self.panel_h) // 2
        
        # State
        self.confirm_active = False 
        
        # Fonts
        try:
            pygame.font.init()
            self.font = pygame.font.SysFont("Arial", 24, bold=True)
            self.font_small = pygame.font.SysFont("Arial", 20, bold=True)
            self.font_label = pygame.font.SysFont("Arial", 22)
            self.font_title = pygame.font.SysFont("Arial", 30, bold=True)
        except:
            self.font = pygame.font.Font(None, 30)
            self.font_small = pygame.font.Font(None, 24)
            self.font_label = pygame.font.Font(None, 26)
            self.font_title = pygame.font.Font(None, 36)


        # UI Element Rects
        self.rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_w, self.panel_h)
        self.close_btn = pygame.Rect(self.panel_x + self.panel_w - 40, self.panel_y + 10, 30, 30)
        
        # Position for labels and volume buttons
        self.music_label_y = self.panel_y + 80
        self.sfx_label_y = self.panel_y + 180
        
        # Volume buttons (placed relative to panel)
        btn_w, btn_h = 50, 30
        self.button_music_up = Button(self.panel_x + 300, self.music_label_y + 40, btn_w, btn_h, '+', GREEN, (0, 255, 0))
        self.button_music_down = Button(self.panel_x + 100, self.music_label_y + 40, btn_w, btn_h, '-', RED, (255, 0, 0))
        self.button_sfx_up = Button(self.panel_x + 300, self.sfx_label_y + 40, btn_w, btn_h, '+', GREEN, (0, 255, 0))
        self.button_sfx_down = Button(self.panel_x + 100, self.sfx_label_y + 40, btn_w, btn_h, '-', RED, (255, 0, 0))

        # Action Buttons (Starting lower down)
        self.help_btn = pygame.Rect(self.panel_x + 50, self.panel_y + 300, 300, 40)
        self.restart_btn = pygame.Rect(self.panel_x + 50, self.panel_y + 360, 300, 40)
        self.quit_btn = pygame.Rect(self.panel_x + 50, self.panel_y + 450, 300, 40)

        # Confirmation Rects (Will be drawn dynamically on top of main panel)
        self.confirm_message = "ARE YOU SURE? All progress will be LOST."
        self.btn_confirm_yes = pygame.Rect(0, 0, 100, 40) 
        self.btn_confirm_no = pygame.Rect(0, 0, 100, 40)


    def toggle(self):
        self.active = not self.active
        self.confirm_active = False # Reset confirmation state on toggle

    def handle_event(self, event):
        if not self.active:
            return None
        
        mouse_pos = event.pos if event.type == pygame.MOUSEBUTTONDOWN else pygame.mouse.get_pos()
        
        # --- CONFIRMATION SCREEN LOGIC ---
        if self.confirm_active:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.btn_confirm_yes.collidepoint(mouse_pos):
                    self.confirm_active = False
                    self.active = False
                    return 'confirm_restart'
                elif self.btn_confirm_no.collidepoint(mouse_pos):
                    self.confirm_active = False
                    return 'close' 
            return None 

        # --- MAIN SETTINGS LOGIC ---

        # 1. Volume Buttons (From settings_page.py)
        if self.button_music_up.check_click(event):
            increase_music_volume(0.1)
            try: pygame.mixer.music.set_volume(get_music_volume())
            except Exception: pass
        
        if self.button_music_down.check_click(event):
            decrease_music_volume(0.1)
            try: pygame.mixer.music.set_volume(get_music_volume())
            except Exception: pass
        
        if self.button_sfx_up.check_click(event):
            increase_sfx_volume(0.1)
        
        if self.button_sfx_down.check_click(event):
            decrease_sfx_volume(0.1)

        # 2. General Buttons (From SettingsPopup)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.close_btn.collidepoint(mouse_pos):
                self.active = False
                return 'close'
            
            elif self.help_btn.collidepoint(mouse_pos):
                return 'help' 
            
            elif self.restart_btn.collidepoint(mouse_pos):
                self.confirm_active = True
                return None 
                
            elif self.quit_btn.collidepoint(mouse_pos):
                return 'quit_game' 
            
        # Update hover states for volume buttons
        if event.type == pygame.MOUSEMOTION:
            self.button_music_up.check_hover(mouse_pos)
            self.button_music_down.check_hover(mouse_pos)
            self.button_sfx_up.check_hover(mouse_pos)
            self.button_sfx_down.check_hover(mouse_pos)

        return None

    def draw(self, screen):
        if not self.active:
            return

        # Overlay
        overlay = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        overlay.fill(OVERLAY_COLOR)
        screen.blit(overlay, (0, 0))

        # Panel
        pygame.draw.rect(screen, PANEL_COLOR, self.rect, border_radius=15)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=15)
        
        # Title
        title = self.font_title.render("SETTINGS", True, WHITE)
        screen.blit(title, (self.panel_x + 20, self.panel_y + 20))
        
        # Close X
        pygame.draw.rect(screen, RED, self.close_btn, border_radius=5)
        x_txt = self.font.render("X", True, WHITE)
        screen.blit(x_txt, (self.close_btn.x + 8, self.close_btn.y + 2))

        # --- VOLUME CONTROLS (Integrated from settings_page.py) ---
        
        # Music Volume
        music_label = self.font_label.render("Music Volume:", True, WHITE)
        screen.blit(music_label, (self.panel_x + 50, self.music_label_y))
        
        music_volume = int(get_music_volume() * 100)
        music_value = self.font_label.render(f"{music_volume}%", True, GOLD)
        screen.blit(music_value, (self.panel_x + 180, self.music_label_y + 45)) 
        
        self.button_music_up.draw(screen)
        self.button_music_down.draw(screen)

        # SFX Volume
        sfx_label = self.font_label.render("SFX Volume:", True, WHITE)
        screen.blit(sfx_label, (self.panel_x + 50, self.sfx_label_y))
        
        sfx_volume = int(get_sfx_volume() * 100)
        sfx_value = self.font_label.render(f"{sfx_volume}%", True, GOLD)
        screen.blit(sfx_value, (self.panel_x + 180, self.sfx_label_y + 45))
        
        self.button_sfx_up.draw(screen)
        self.button_sfx_down.draw(screen)


        # --- ACTION BUTTONS ---

        # Help Button
        pygame.draw.rect(screen, GOLD, self.help_btn, border_radius=8)
        h_txt = self.font.render("Help / How to Play", True, (50, 50, 50)) 
        screen.blit(h_txt, h_txt.get_rect(center=self.help_btn.center))
        
        # Restart Game Button
        pygame.draw.rect(screen, RED, self.restart_btn, border_radius=8)
        r_txt = self.font.render("RESTART GAME", True, WHITE)
        screen.blit(r_txt, r_txt.get_rect(center=self.restart_btn.center))

        # Quit Button
        pygame.draw.rect(screen, GRAY, self.quit_btn, border_radius=8)
        q_txt = self.font.render("Quit to Desktop", True, WHITE)
        screen.blit(q_txt, q_txt.get_rect(center=self.quit_btn.center))
        
        # --- DRAW CONFIRMATION SCREEN ---
        if self.confirm_active:
            # Draw dark overlay over the settings panel
            confirm_overlay = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
            confirm_overlay.fill(OVERLAY_COLOR)
            screen.blit(confirm_overlay, (0, 0))

            # Confirmation Box
            box_w, box_h = 350, 180
            box_x = (self.screen_w - box_w) // 2
            box_y = (self.screen_h - box_h) // 2
            box_rect = pygame.Rect(box_x, box_y, box_w, box_h)
            
            pygame.draw.rect(screen, WHITE, box_rect, border_radius=15)
            pygame.draw.rect(screen, RED, box_rect, 4, border_radius=15)

            # Draw text
            text_surf = self.font.render(self.confirm_message, True, BLACK)
            text_rect = text_surf.get_rect(center=(box_rect.centerx, box_y + 40))
            screen.blit(text_surf, text_rect)

            # Define and draw Yes/No buttons
            btn_w, btn_h = 100, 40
            
            self.btn_confirm_yes.topleft = (box_x + 50, box_y + 100)
            self.btn_confirm_yes.size = (btn_w, btn_h)
            
            self.btn_confirm_no.topleft = (box_x + box_w - btn_w - 50, box_y + 100)
            self.btn_confirm_no.size = (btn_w, btn_h)
            
            # Draw the buttons
            pygame.draw.rect(screen, GREEN, self.btn_confirm_yes, border_radius=8)
            pygame.draw.rect(screen, RED, self.btn_confirm_no, border_radius=8)
            
            yes_txt = self.font.render("YES", True, WHITE)
            no_txt = self.font.render("NO", True, WHITE)
            
            screen.blit(yes_txt, yes_txt.get_rect(center=self.btn_confirm_yes.center))
            screen.blit(no_txt, no_txt.get_rect(center=self.btn_confirm_no.center))
import pygame

# Colors
OVERLAY_COLOR = (0, 0, 0, 180)
PANEL_COLOR = (50, 50, 60)
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
GOLD = (255, 215, 0) # Added for Help Button

class SettingsPopup:
    def __init__(self, screen_width, screen_height):
        self.screen_w = screen_width
        self.screen_h = screen_height
        self.active = False
        
        # Increased height slightly to fit the Help button
        self.panel_w = 400
        self.panel_h = 360 
        self.panel_x = (screen_width - self.panel_w) // 2
        self.panel_y = (screen_height - self.panel_h) // 2
        
        # Fake settings state
        self.music_on = True
        self.sfx_on = True
        
        # UI Elements
        self.rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_w, self.panel_h)
        self.close_btn = pygame.Rect(self.panel_x + self.panel_w - 40, self.panel_y + 10, 30, 30)
        
        self.music_btn = pygame.Rect(self.panel_x + 50, self.panel_y + 80, 300, 40)
        self.sfx_btn = pygame.Rect(self.panel_x + 50, self.panel_y + 140, 300, 40)
        
        # New Help Button
        self.help_btn = pygame.Rect(self.panel_x + 50, self.panel_y + 200, 300, 40)
        
        self.quit_btn = pygame.Rect(self.panel_x + 50, self.panel_y + 280, 300, 40)

        try:
            self.font = pygame.font.SysFont("Arial", 24, bold=True)
        except:
            self.font = pygame.font.Font(None, 30)

    def toggle(self):
        self.active = not self.active

    def handle_event(self, event):
        if not self.active:
            return None
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.close_btn.collidepoint(event.pos):
                self.active = False
            
            elif self.music_btn.collidepoint(event.pos):
                self.music_on = not self.music_on
                # Here you would actually toggle mixer music
                
            elif self.sfx_btn.collidepoint(event.pos):
                self.sfx_on = not self.sfx_on

            elif self.help_btn.collidepoint(event.pos):
                return 'help'
                
            elif self.quit_btn.collidepoint(event.pos):
                return 'quit_game'
                
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
        title = self.font.render("SETTINGS", True, WHITE)
        screen.blit(title, (self.panel_x + 20, self.panel_y + 20))
        
        # Close X
        pygame.draw.rect(screen, RED, self.close_btn, border_radius=5)
        x_txt = self.font.render("X", True, WHITE)
        screen.blit(x_txt, (self.close_btn.x + 8, self.close_btn.y + 2))

        # Music Toggle
        color = GREEN if self.music_on else RED
        pygame.draw.rect(screen, color, self.music_btn, border_radius=8)
        txt = f"Music: {'ON' if self.music_on else 'OFF'}"
        surf = self.font.render(txt, True, WHITE)
        screen.blit(surf, (self.music_btn.x + 100, self.music_btn.y + 8))

        # SFX Toggle
        color = GREEN if self.sfx_on else RED
        pygame.draw.rect(screen, color, self.sfx_btn, border_radius=8)
        txt = f"SFX: {'ON' if self.sfx_on else 'OFF'}"
        surf = self.font.render(txt, True, WHITE)
        screen.blit(surf, (self.sfx_btn.x + 100, self.sfx_btn.y + 8))

        # Help Button
        pygame.draw.rect(screen, GOLD, self.help_btn, border_radius=8)
        h_txt = self.font.render("Help / How to Play", True, (50, 50, 50)) # Dark text for contrast
        screen.blit(h_txt, (self.help_btn.x + 60, self.help_btn.y + 8))

        # Quit Button
        pygame.draw.rect(screen, GRAY, self.quit_btn, border_radius=8)
        q_txt = self.font.render("Quit to Desktop", True, WHITE)
        screen.blit(q_txt, (self.quit_btn.x + 70, self.quit_btn.y + 8))
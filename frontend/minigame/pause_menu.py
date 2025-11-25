import pygame

# --- Colors (Matched to Tailwind CSS Grays) ---
OVERLAY_COLOR = (17, 24, 39, 200)  # gray-900 with ~80% opacity
PANEL_COLOR = (31, 41, 55)         # gray-800
TEXT_WHITE = (255, 255, 255)
BUTTON_COLOR = (75, 85, 99)        # gray-600
BUTTON_HOVER = (107, 114, 128)     # gray-500

class PauseMenu:
    def __init__(self, screen_width, screen_height):
        self.screen_w = screen_width
        self.screen_h = screen_height
        
        # Dimensions for the menu box
        self.panel_w = 400
        self.panel_h = 350
        self.panel_x = (self.screen_w - self.panel_w) // 2
        self.panel_y = (self.screen_h - self.panel_h) // 2
        
        # Fonts
        self.title_font = pygame.font.SysFont("Arial", 40, bold=True)
        self.btn_font = pygame.font.SysFont("Arial", 24)

        # Button Layout
        btn_w = 300
        btn_h = 50
        btn_x = self.panel_x + (self.panel_w - btn_w) // 2
        start_y = self.panel_y + 100
        gap = 70

        # Define rectangles for click detection
        self.btn_resume = pygame.Rect(btn_x, start_y, btn_w, btn_h)
        self.btn_quit = pygame.Rect(btn_x, start_y + gap, btn_w, btn_h)
        self.btn_settings = pygame.Rect(btn_x, start_y + (gap * 2), btn_w, btn_h)

    def draw(self, screen):
        # 1. Draw Semi-Transparent Overlay
        overlay = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        overlay.fill(OVERLAY_COLOR)
        screen.blit(overlay, (0, 0))

        # 2. Draw Menu Panel (Rounded Box)
        panel_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_w, self.panel_h)
        pygame.draw.rect(screen, PANEL_COLOR, panel_rect, border_radius=20)

        # 3. Draw Title ("Paused")
        title_surf = self.title_font.render("Paused", True, TEXT_WHITE)
        title_rect = title_surf.get_rect(center=(self.screen_w // 2, self.panel_y + 50))
        screen.blit(title_surf, title_rect)

        # 4. Draw Buttons
        mouse_pos = pygame.mouse.get_pos()
        self._draw_button(screen, "Resume Game", self.btn_resume, mouse_pos)
        self._draw_button(screen, "Save & Quit", self.btn_quit, mouse_pos)
        self._draw_button(screen, "Settings", self.btn_settings, mouse_pos)

    def _draw_button(self, screen, text, rect, mouse_pos):
        # Hover Effect
        color = BUTTON_HOVER if rect.collidepoint(mouse_pos) else BUTTON_COLOR
        
        # Draw Button Shape
        pygame.draw.rect(screen, color, rect, border_radius=12)
        
        # Draw Text
        text_surf = self.btn_font.render(text, True, TEXT_WHITE)
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)

    def handle_input(self, event):
        """
        Returns a string action if a button is clicked, else None.
        Actions: 'resume', 'quit', 'settings'
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left click
                if self.btn_resume.collidepoint(event.pos):
                    return 'resume'
                elif self.btn_quit.collidepoint(event.pos):
                    return 'quit'
                elif self.btn_settings.collidepoint(event.pos):
                    return 'settings'
        return None
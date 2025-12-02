# frontend/title.py

import pygame
pygame.font.init()  # ensure fonts are ready before Button is created

from frontend_button import Button
from game_context import game_context
import session  # central backend/player session state


# -------------------------------
# Lazy Button Creation
# -------------------------------
button_start = None

def get_start_button():
    global button_start
    if button_start is None:
        button_start = Button(pygame.Rect(300, 450, 200, 70), "Start")
    return button_start


# -------------------------------
# Fonts (Lazy Loaded)
# -------------------------------
_TITLE_FONT = None
_STATUS_FONT = None


def _init_fonts():
    """Initialize fonts once."""
    global _TITLE_FONT, _STATUS_FONT
    if _TITLE_FONT is None or _STATUS_FONT is None:
        _TITLE_FONT = pygame.font.Font(None, 72)
        _STATUS_FONT = pygame.font.Font(None, 24)


# -------------------------------
# Session Sync
# -------------------------------
def _sync_game_context_from_session():
    """
    Make sure game_context uses the same user as session/current_user.
    """
    if not getattr(session, "api_available", False):
        print("[TITLE] Backend not available; running in offline mode.")
        return

    if session.current_user is None:
        print("[TITLE] No current_user in session; running in offline mode.")
        return

    user = session.current_user

    game_context.user_id = user["id"]
    game_context.username = user.get("username")
    game_context.email = user.get("email")

    print(f"[TITLE] Using backend user id={game_context.user_id}, username={game_context.username}")


# -------------------------------
# Title Update
# -------------------------------
def title_update(events):
    """
    Handle input on the title screen.
    Returns the next page or None to stay here.
    """
    start_btn = get_start_button()

    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if start_btn.is_clicked(event):
                print("[TITLE] Start button clicked")
                _sync_game_context_from_session()
                return "homescreen"

    return None


# -------------------------------
# Title Draw
# -------------------------------
def title_draw(screen):
    _init_fonts()

    # Fill background
    screen.fill((0, 0, 0))

    # Draw title
    title_surf = _TITLE_FONT.render("Guinea Games", True, (255, 255, 255))
    title_rect = title_surf.get_rect(
        center=(screen.get_width() // 2, screen.get_height() // 3)
    )
    screen.blit(title_surf, title_rect)

    # Draw start button
    get_start_button().draw(screen)

    # Backend status text
    status = "Backend: offline"
    color = (220, 60, 60)

    if getattr(session, "api_available", False):
        if session.current_user:
            status = f"Backend: connected (user: {session.current_user.get('username', 'unknown')})"
        else:
            status = "Backend: connected"
        color = (60, 220, 60)

    status_surf = _STATUS_FONT.render(status, True, color)
    screen.blit(status_surf, (10, 10))

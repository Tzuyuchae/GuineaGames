# frontend/title.py

import pygame
from frontend_button import Button
from game_context import game_context
import session  # central backend/player session state

# Title button
button_start = Button(pygame.Rect(300, 450, 200, 70), "Start")

# Fonts (lazy init so this works even if pygame wasn't fully set up yet)
_TITLE_FONT = None
_STATUS_FONT = None


def _init_fonts():
    """Initialize fonts once."""
    global _TITLE_FONT, _STATUS_FONT
    if _TITLE_FONT is None or _STATUS_FONT is None:
        pygame.font.init()
        _TITLE_FONT = pygame.font.Font(None, 72)
        _STATUS_FONT = pygame.font.Font(None, 24)


def _sync_game_context_from_session():
    """
    Make sure game_context uses the same user as session/current_user.
    This is the key glue between the backend and the rest of the frontend.
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


def title_update(events):
    """
    Handle input on the title screen.
    Returns the next page name (e.g. 'homescreen') or None to stay here.
    """
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if button_start.is_clicked(event):
                print("[TITLE] Start button clicked")

                # Keep everything in sync with the existing backend session
                _sync_game_context_from_session()

                # Frontend/main.py will see this and swap to homescreen
                return "homescreen"

    return None


def title_draw(screen):
    """
    Draw the title screen.
    """
    _init_fonts()

    # Fill background
    screen.fill((0, 0, 0))

    # Draw game title text
    title_text = "Guinea Games"
    title_surf = _TITLE_FONT.render(title_text, True, (255, 255, 255))
    title_rect = title_surf.get_rect(
        center=(screen.get_width() // 2, screen.get_height() // 3)
    )
    screen.blit(title_surf, title_rect)

    # Draw the Start button
    button_start.draw(screen)

    # Optional: show backend status in top-left
    status = "Backend: offline"
    color = (220, 60, 60)
    if getattr(session, "api_available", False):
        status = f"Backend: connected (user: {session.current_user.get('username', 'unknown')})" \
            if session.current_user else "Backend: connected"
        color = (60, 220, 60)

    status_surf = _STATUS_FONT.render(status, True, color)
    screen.blit(status_surf, (10, 10))

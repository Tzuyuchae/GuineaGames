import pygame
from frontend_button import Button
from game_context import game_context

# Optional: Import API client for database connectivity
try:
    from api_client import api
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False
    print("API client not available. Run in standalone mode.")

# A 'Back' button
button_start = Button(pygame.Rect(400, 500, 200, 70), 'Start')

def _ensure_backend_user():
    """
    Make sure we have a backend user and store it in game_context.
    For now, we can hard-code a simple test account.
    """
    if not API_AVAILABLE:
        print("API unavailable; skipping backend user setup.")
        return False

    # If we already created a user earlier in this run, skip
    if game_context.user_id is not None:
        return True

    username = "test_player"
    email = "test_player@example.com"
    password = "password123"

    try:
        # Simple strategy:
        # 1. Try to create the user.
        # 2. If HTTP 400 because of duplicate, fall back to querying users and pick that one.
        user = api.create_user(username, email, password)
    except Exception as e:
        print("create_user failed, trying to reuse existing user:", e)
        try:
            users = api.get_users()
            existing = next((u for u in users if u["username"] == username), None)
            if not existing:
                print("No existing user found either.")
                return False
            user = existing
        except Exception as e2:
            print("Unable to get or create user:", e2)
            return False

    game_context.user_id = user["id"]
    game_context.username = user["username"]
    game_context.email = user["email"]
    print(f"Using backend user id={game_context.user_id}")
    return True


def title_update(events):
    """
    Handle input on the title screen.
    Returns the next page name (e.g. 'homescreen') or None to stay here.
    """
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if button_start.is_clicked(event):
                print("Start button clicked")

                # Try to connect to backend and set up the user
                if API_AVAILABLE:
                    ok = _ensure_backend_user()
                    if not ok:
                        print("Warning: could not set up backend user; continuing in offline mode")
                return "homescreen"   # or 'guinea_pig_selector' if that’s your next page

    return None

def title_draw(screen):
    """Draws the breeding page."""
    # Draw the back button
    button_start.draw(screen)

    # Optional: Display API connection status (commented out by default)
    # if API_AVAILABLE:
    #     font = pygame.font.Font(None, 24)
    #     if api.check_connection():
    #         status_text = font.render("API: Connected", True, (0, 128, 0))
    #     else:
    #         status_text = font.render("API: Offline", True, (255, 0, 0))
    #     screen.blit(status_text, (10, 10))

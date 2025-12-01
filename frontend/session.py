# session.py
"""
This module manages the *player's runtime session* — meaning:
• Which user is currently playing
• Whether the backend is available
• What pets that user owns
• How we keep these values synchronized with the database

WHY WE NEED THIS FILE:
----------------------
The frontend (Pygame) needs data from the backend (FastAPI), but we
don't want every screen (homescreen, details, breeding, minigame, etc.)
to repeatedly write networking code.

Instead, we centralize all backend interaction in a single module.

This gives us:
    1. A single source of truth for the player's data.
    2. Cleaner frontend code (screens just read `session.current_user`).
    3. The ability to later switch to an offline mode or WASM version
       by modifying only this file.

This is the heart of backend–frontend integration.
"""

from typing import Optional, List, Dict, Any

# We import the API client you already validated with test_api_connection.py.
# WHY: This keeps ALL backend I/O in one place instead of spreading it in UI code.
# The try/except makes this work whether you run:
#   - `python main.py` from inside the frontend folder, or
#   - import `frontend` as a package from the project root.
try:
    from api_client import api  # running from frontend/ directory
except ImportError:
    from frontend.api_client import api  # running from project root as a package


# ---- SESSION STATE ----
# These variables represent the current state of the player inside the game.
# They update when the game starts and whenever we refresh user or pet data.

api_available: bool = False     # Whether the backend responded successfully
api_status: str = "Not initialized"  # Human-readable status for UI display

current_user: Optional[Dict[str, Any]] = None   # dict returned by /users/{id}
user_pets: List[Dict[str, Any]] = []            # list returned by /pets/owner/{id}


# =====================================================================
#  init_session()
# =====================================================================
def init_session() -> None:
    """
    Called exactly ONCE at game startup.

    WHY THIS MATTERS:
    -----------------
    When the game launches, we want it to:
        1. Ping the backend (FastAPI server)
        2. Find or create a default user
        3. Load that user’s pets into memory
    
    After this function runs, the rest of the game (homescreen, details,
    minigame, etc.) can simply read from:
    
        session.current_user
        session.user_pets
        session.api_status
    
    This keeps your entire frontend clean and decoupled from the database.
    """

    global api_available, api_status, current_user, user_pets

    try:
        # Step 1 — Check backend status
        # WHY: The game must handle offline cases gracefully instead of crashing.
        if not api.check_connection():
            api_available = False
            api_status = "Backend offline"
            current_user = None
            user_pets = []
            return

        api_available = True
        api_status = "Connected"

        # Step 2 — Retrieve existing users
        # WHY: Frontend needs an active user profile to store pets, coins, etc.
        users = api.get_users()

        # If there are no users yet, create a default one.
        # WHY: Guarantees the game ALWAYS has an identity to use.
        if users:
            current_user = users[0]
        else:
            current_user = api.create_user(
                "Player1",
                "player1@example.com",
                "password",
            )

        # Step 3 — Load this user's pets
        # WHY: Pets are shown in multiple screens, so we load once here.
        user_pets = api.get_user_pets(current_user["id"])

    except Exception as e:
        # WHY: Without this try/except, any server hiccup would crash the game.
        api_available = False
        api_status = f"API error: {e}"
        current_user = None
        user_pets = []


# =====================================================================
#  refresh_user()
# =====================================================================
def refresh_user() -> None:
    """
    Reload the current user from the backend.

    WHY THIS IS NECESSARY:
    ----------------------
    After certain actions (like earning coins from a minigame or making
    a purchase), the user’s data changes in the database. The in-memory
    copy must be updated so the UI shows correct values.
    """
    global current_user

    if api_available and current_user:
        current_user = api.get_user(current_user["id"])


# =====================================================================
#  refresh_pets()
# =====================================================================
def refresh_pets() -> None:
    """
    Reload the user's pet list from the backend.

    WHY THIS IS NECESSARY:
    ----------------------
    Actions like:
        • Breeding
        • Marketplace purchases
        • Reward pets
    will change the pet list.
    
    Calling this function ensures the UI always shows the newest data.
    """
    global user_pets

    if api_available and current_user:
        user_pets = api.get_user_pets(current_user["id"])

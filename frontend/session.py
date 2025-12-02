# frontend/session.py
"""
Central session state for the Guinea Games frontend.

This module is the single source of truth for:
    • Whether the backend is available
    • Which user is currently playing
    • Which pets that user owns

Other screens (title, homescreen, store, minigame, etc.) should only read
from / call things in this module instead of talking to the API directly.
"""

from typing import Optional, Dict, Any, List

try:
    # Shared API client used everywhere in the frontend
    from api_client import api
except ImportError:
    api = None  # Fallback so imports don't explode during dev / tests


# ---- SESSION STATE (GLOBAL) -----------------------------------------

api_available: bool = False          # True if backend is up AND init_session succeeded
api_status: str = "Not initialized"  # Human-readable status for UI

current_user: Optional[Dict[str, Any]] = None   # dict returned by /users/
user_pets: List[Dict[str, Any]] = []            # list returned by /pets/owner/{id}


# ====================================================================
#  init_session()
# ====================================================================
def init_session() -> None:
    """
    Called exactly ONCE at game startup.

    Steps:
        1. Verify that the backend is reachable.
        2. Create or reuse a default user ("Player1").
        3. Load that user's pets into memory.
    """
    global api_available, api_status, current_user, user_pets

    if api is None:
        # api_client could not be imported for some reason
        api_available = False
        api_status = "API client not available"
        current_user = None
        user_pets = []
        print("[SESSION] API client import failed; running completely offline.")
        return

    try:
        # ---- Step 1: basic connectivity check ----
        if not api.check_connection():
            api_available = False
            api_status = "Backend offline"
            current_user = None
            user_pets = []
            print("[SESSION] Backend is not reachable; offline mode.")
            return

        api_available = True
        api_status = "Connected"
        print("[SESSION] Backend connection OK.")

        # ---- Step 2: always create OR reuse a default user ----
        # Backend's POST /users/ is written so that if this email already
        # exists, it simply returns the existing user instead of failing.
        current_user = api.create_user(
            "Player1",
            "player1@example.com",
            "password",
        )
        print(f"[SESSION] Using user id={current_user['id']}, "
              f"username={current_user.get('username')}")

        # ---- Step 3: load this user's pets ----
        user_pets = api.get_user_pets(current_user["id"])
        print(f"[SESSION] Loaded {len(user_pets)} pets for this user.")

    except Exception as e:
        # Any error here means we cannot safely rely on the backend.
        api_available = False
        api_status = f"API error: {e}"
        current_user = None
        user_pets = []
        print(f"[SESSION] FAILED to initialize session: {e}")


# ====================================================================
#  refresh_user()
# ====================================================================
def refresh_user() -> None:
    """
    Reload the current user from the backend.

    Call this after actions that change coins/balance or other user-level
    fields (e.g., store purchases, minigame rewards).
    """
    global current_user

    if not api_available or current_user is None:
        return

    try:
        current_user = api.get_user(current_user["id"])
        print(f"[SESSION] Refreshed user id={current_user['id']}")
    except Exception as e:
        print(f"[SESSION] refresh_user failed: {e}")


# ====================================================================
#  refresh_pets()
# ====================================================================
def refresh_pets() -> None:
    """
    Reload the current user's pets from the backend.

    Call this after actions that add/remove pets (breeding, marketplace,
    rewards, etc.).
    """
    global user_pets

    if not api_available or current_user is None:
        return

    try:
        user_pets = api.get_user_pets(current_user["id"])
        print(f"[SESSION] Refreshed pets; now have {len(user_pets)} total.")
    except Exception as e:
        print(f"[SESSION] refresh_pets failed: {e}")

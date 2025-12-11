# run_game.py
import os
import sys
import threading
import time
from pathlib import Path

import requests
import sqlalchemy  # 👈 Force PyInstaller to see SQLAlchemy
from sqlalchemy.orm import Session  # 👈 Extra nudge for ORM submodule


def start_backend():
    """
    Start the FastAPI backend using uvicorn in a background thread.
    Importing sqlalchemy here as well helps PyInstaller detect usage.
    """
    # These imports happen at runtime, but sqlalchemy is already imported above
    import uvicorn
    from backend.main import app  # this imports routes, etc.

    # Run uvicorn server
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")


def wait_for_backend(timeout_seconds: int = 10) -> bool:
    """
    Poll the backend root endpoint until it responds or the timeout is reached.
    """
    deadline = time.time() + timeout_seconds
    url = "http://127.0.0.1:8000/"

    while time.time() < deadline:
        try:
            r = requests.get(url, timeout=0.5)
            if r.status_code < 500:
                print("Backend is up!")
                return True
        except Exception:
            pass
        time.sleep(0.2)

    print("Warning: backend did not start in time; game may run in offline mode.")
    return False


def main():
    # 1. Determine the path to the CODE (Internal)
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        # Running inside PyInstaller Bundle (Temp Folder)
        internal_base = Path(sys._MEIPASS)
        # 2. Determine the path to the EXE (External / Persistent)
        external_base = Path(sys.executable).parent
    else:
        # Running from Source
        internal_base = Path(__file__).resolve().parent
        external_base = internal_base

    print(f"Code running in: {internal_base}")
    print(f"Save data location: {external_base}")

    # Set the working directory to internal_base so imports work
    os.chdir(internal_base)

    # ---- CRITICAL FIX ----
    # Tell the backend where to save the database file
    # We set an environment variable that the backend can read
    os.environ["GAME_SAVE_DIR"] = str(external_base)

    # ---- Ensure backend/ and frontend/ are importable ----
    sys.path.insert(0, str(internal_base / "backend"))
    sys.path.insert(0, str(internal_base / "frontend"))

    # ---- Start backend in a background (daemon) thread ----
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()

    # Wait for backend to be ready
    wait_for_backend(timeout_seconds=10)

    # ---- Start Pygame frontend ----
    import frontend.main  # noqa: F401

if __name__ == "__main__":
    main()

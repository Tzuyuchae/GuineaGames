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
    # ---- Locate base directory (supports PyInstaller) ----
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        # Running inside a PyInstaller bundle
        base_dir = Path(sys._MEIPASS)
    else:
        # Running from source
        base_dir = Path(__file__).resolve().parent

    print(f"Base directory: {base_dir}")

    # Make sure we run from the base dir so relative paths work
    os.chdir(base_dir)

    # ---- Ensure backend/ and frontend/ are importable ----
    sys.path.insert(0, str(base_dir / "backend"))
    sys.path.insert(0, str(base_dir / "frontend"))

    # ---- Start backend in a background (daemon) thread ----
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()

    # Wait for backend to be ready (or time out)
    wait_for_backend(timeout_seconds=10)

    # ---- Start Pygame frontend ----
    import frontend.main  # noqa: F401

    # When the Pygame window closes, the process will exit and
    # the daemon backend thread will be killed automatically.


if __name__ == "__main__":
    main()

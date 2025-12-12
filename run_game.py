# run_game.py (Revised with Subprocess)
import os
import sys
import time
import subprocess
from pathlib import Path

import requests
import sqlalchemy
from sqlalchemy.orm import Session
# import config
# config.ASSET_BASE_PATH = str(internal_base)


if len(sys.argv) > 1 and sys.argv[1] == "--server-mode":
    # If this is the subprocess, run the backend and exit.
    print("--- Subprocess: Running Backend ---")
    
    # We need to manually perform the imports that start the server application
    # since Uvicorn won't be running it via the command line arguments correctly.
    try:
        import uvicorn
        from backend.main import app
        # NOTE: uvicorn.run will block until the server is shut down.
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info", lifespan="on")
    except Exception as e:
        print(f"Subprocess Backend Fatal Error: {e}")
    sys.exit(0)


def start_backend_subprocess(base_dir: Path) -> subprocess.Popen:
    print("Starting backend server in separate process...")
    
    # CHECK: Are we running as a PyInstaller EXE or a Python script?
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        # --- EXE MODE ---
        # We launch the EXE itself with the guard flag
        command = [sys.executable, "--server-mode"]
    else:
        # --- DEVELOPMENT/PYTHON MODE ---
        # We launch Uvicorn using the standard module command
        command = [
            sys.executable, "-m", "uvicorn", 
            "backend.main:app", 
            "--host", "127.0.0.1", 
            "--port", "8000", 
            "--log-level", "info"
        ]

    process = subprocess.Popen(
        command,
        cwd=base_dir,
        env=os.environ.copy()
    )
    print(f"Backend process started with PID: {process.pid}")
    return process

def wait_for_backend(timeout_seconds: int = 10) -> bool:
    """
    Poll the backend root endpoint until it responds or the timeout is reached.
    (This function remains the same)
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
    backend_process = None
    try:
        # --- Determine paths and set up environment ---
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            internal_base = Path(sys._MEIPASS)
            external_base = Path(sys.executable).parent
        else:
            internal_base = Path(__file__).resolve().parent
            external_base = internal_base

        print(f"Code running in: {internal_base}")
        print(f"Save data location: {external_base}")

        # Set the working directory to internal_base so imports work
        os.chdir(internal_base)

        # Tell the backend where to save the database file (via environment variable)
        os.environ["GAME_SAVE_DIR"] = str(external_base)

        # Ensure backend/ and frontend/ are importable
        # NOTE: Since the server runs in a separate process, we only need to 
        # ensure frontend/ is importable for the main process.
        sys.path.insert(0, str(internal_base / "frontend"))
        # You may also still need backend in path for 'import frontend.main' 
        # if frontend.main uses other backend utilities besides models.
        sys.path.insert(0, str(internal_base / "backend"))


        # ---- Start backend in a separate PROCESS ----
        backend_process = start_backend_subprocess(internal_base)

        # Wait for backend to be ready
        wait_for_backend(timeout_seconds=10)

        # ---- Start Pygame frontend ----
        # This will now safely import backend.models in the main process 
        # without conflicting with the separate backend process.
        import frontend.main

    except Exception as e:
        print(f"An unexpected error occurred in the main thread: {e}")

    finally:
        # Ensure the backend process is terminated when the game closes
        if backend_process:
            print("\nShutting down backend process...")
            backend_process.terminate()
            try:
                # Give it a moment to terminate
                backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if termination fails
                print("Force killing backend process.")
                backend_process.kill()


if __name__ == "__main__":
    main()
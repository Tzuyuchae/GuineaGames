import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- DATABASE PATH CONFIGURATION FOR PYINSTALLER ---

# 1. Get the persistent directory from the environment variable set in run_game.py.
#    This should be the persistent path (e.g., C:\Users\ashty\GuineaGames\dist).
PERSISTENT_SAVE_DIR = os.environ.get("GAME_SAVE_DIR") 

if PERSISTENT_SAVE_DIR:
    # If running inside the EXE bundle (PERSISTENT_SAVE_DIR is set):
    # The database folder goes inside the persistent save directory.
    # We reconstruct the path relative to the persistent root.
    DATABASE_ROOT = os.path.join(PERSISTENT_SAVE_DIR, "backend", "database")
else:
    # Fallback for development mode (running from source):
    # The base directory is the folder where this db_connect.py file lives.
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATABASE_ROOT = os.path.join(BASE_DIR, "database")

# CRITICAL: Ensure the persistent folder structure exists before creating the database file
os.makedirs(DATABASE_ROOT, exist_ok=True) 

# 2. Build the final, absolute path to the database file
DB_PATH = os.path.join(DATABASE_ROOT, "GuineaGames.db")

# Debug print to confirm it's looking in the right persistent place
print(f"--- DATABASE PATH: {DB_PATH} ---")

# 3. Create the SQLAlchemy URL
DATABASE_URL = f"sqlite:///{DB_PATH}"

# 4. Create the SQLAlchemy Engine
# The 'connect_args' is required for SQLite to handle multi-threading/async operations
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# 5. Create Session and Base objects
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# --- Dependency ---
def get_db():
    """Returns a new SQLAlchemy session instance for use as a FastAPI Dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
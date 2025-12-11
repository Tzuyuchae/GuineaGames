import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ---- DB LOCATION SETUP ----
if "GAME_SAVE_DIR" in os.environ:
    # SCENARIO 1: Running as .exe
    # run_game.py told us where the real folder is.
    # We save the DB right next to the .exe file.
    save_dir = os.environ["GAME_SAVE_DIR"]
    db_path = os.path.join(save_dir, "GuineaGames.db")
else:
    # SCENARIO 2: Running from Source (VS Code / Terminal)
    # Use the original location inside backend/database
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Ensure the 'database' folder actually exists so we don't crash
    db_folder = os.path.join(BASE_DIR, 'database')
    os.makedirs(db_folder, exist_ok=True)
    
    db_path = os.path.join(db_folder, "GuineaGames.db")

# Print for debugging (helps you see where it's saving!)
print(f"--- DATABASE PATH: {db_path} ---")

DATABASE_URL = f"sqlite:///{db_path}"
# ---------------------------

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
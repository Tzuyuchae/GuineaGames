import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Get the folder where THIS file (backend/database.py) lives
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Point to the 'database' subfolder where your GuineaGames.db actually is
#    (Matches the structure shown in your screenshot)
DB_PATH = os.path.join(BASE_DIR, "database", "GuineaGames.db")

# Debug print to confirm it's looking in the right place
print(f"--- DATABASE PATH: {DB_PATH} ---")

DATABASE_URL = f"sqlite:///{DB_PATH}"

# 3. Create the connection
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
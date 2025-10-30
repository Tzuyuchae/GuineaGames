import sqlite3
import os

"""
=========================================================
DATABASE CREATION SCRIPT (GuineaGames.db)
=========================================================

Purpose:
- Creates the SQLite database schema for the GuineaGames virtual pet game.
- Defines all core tables: USERS, PETS, INVENTORY, MINI_GAMES, LEADERBOARDS,
  TRANSACTIONS, and SHOP_ITEMS.
- Drops and recreates tables on each run (for clean dev/test cycles).

Tables:
1. USERS — player accounts and credentials
2. PETS — each player’s guinea pigs
3. INVENTORY — tracks owned materials/items
4. MINI_GAMES — defines mini-games and rewards
5. LEADERBOARDS — ranks players by score/happiness
6. TRANSACTIONS — logs all player balance/item updates
7. SHOP_ITEMS — store items (food, accessories)

Frontend/backend integration:
- Run this script once before API or gameplay logic to initialize DB.
- Use consistent field names for CRUD operations in backend logic.
"""

# =========================================================
# Database setup
# =========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "GuineaGames.db")

sqliteConnection = sqlite3.connect(DB_PATH)
cursor = sqliteConnection.cursor()

# =========================================================
# Drop old tables (for dev convenience)
# =========================================================
tables = [
    "TRANSACTIONS",
    "LEADERBOARDS",
    "MINI_GAMES",
    "INVENTORY",
    "GUINEA_PIGS",
    "GENETICS",
    "SHOP_ITEMS",
    "USERS",
]
for t in tables:
    cursor.execute(f"DROP TABLE IF EXISTS {t};")

# =========================================================
# Schema creation
# =========================================================
sql_commands = """

-- =============================
-- USERS
-- Stores player login info
-- =============================
CREATE TABLE USERS (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME
);

-- =============================
-- GUINEA PIGS
-- Each record stores one guinea pig
-- =============================
CREATE TABLE GUINEA_PIGS (
    id INTEGER PRIMARY KEY,
    owner_id INTEGER NOT NULL,
    name TEXT,
    genetic_id INTEGER NOT NULL,
    age_months INTEGER DEFAULT 0,
    hunger INTEGER CHECK(hunger BETWEEN 0 AND 3) DEFAULT 3,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES USERS(id),
    FOREIGN KEY (genetic_id) REFERENCES GENETICS(id)
);

-- =============================
-- GENETICS
-- Each record stores one guinea pig
-- =============================
CREATE TABLE GENETICS (
    id INTEGER PRIMARY KEY,
    speed INTEGER CHECK (speed BETWEEN 1 AND 10) DEFAULT 1,
    endurance INTEGER CHECK (endurance BETWEEN 1 AND 10) DEFAULT 1,
    head_color TEXT CHECK (head_color IN ('BB', 'Bw', 'ww')),
    middle_color TEXT CHECK (middle_color IN ('BB', 'Bw', 'ww')),
    accent_color TEXT CHECK (accent_color IN ('BB', 'Bw', 'ww')),
    coat TEXT CHECK (coat IN ('SS', 'Sf', 'ff'))
);

-- =============================
-- INVENTORY
-- Tracks player-owned items
-- =============================
CREATE TABLE INVENTORY (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    item_name TEXT NOT NULL,
    quantity INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES USERS(id)
);

-- =============================
-- MINI_GAMES
-- Defines each game and its reward base
-- =============================
CREATE TABLE MINI_GAMES (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    base_reward INTEGER DEFAULT 0,
    cooldown_sec INTEGER
);

-- =============================
-- LEADERBOARDS
-- Tracks player ranking by score/happiness
-- =============================
CREATE TABLE LEADERBOARDS (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    score INTEGER DEFAULT 0,
    rank INTEGER,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES USERS(id)
);

-- =============================
-- TRANSACTIONS
-- Logs game actions that change balance or items
-- =============================
CREATE TABLE TRANSACTIONS (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    type TEXT NOT NULL,
    amount INTEGER DEFAULT 0,
    description TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES USERS(id)
);

-- =============================
-- SHOP_ITEMS
-- Store catalog for buying items
-- =============================
CREATE TABLE SHOP_ITEMS (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    cost INTEGER NOT NULL,
    description TEXT,
    effect TEXT
);
"""

cursor.executescript(sql_commands)
sqliteConnection.commit()
sqliteConnection.close()

print("✅ GuineaGames.db created successfully with all tables.")

import sqlite3
import os

"""
=========================================================
DATABASE CREATION SCRIPT (GuineaGames.db)
=========================================================

Purpose:
- Creates the SQLite database schema for the GuineaGames virtual pet game.
- Merges legacy genetics structure with new Mendelian system.
- Supports backward compatibility with GUINEA_PIGS references.

Tables:
1. USERS — player accounts and credentials
2. PETS (alias GUINEA_PIGS) — guinea pigs with genetics, stats, and legacy color traits
3. INVENTORY — tracks owned materials/items
4. MINI_GAMES — defines mini-games and rewards
5. LEADERBOARDS — ranks players by score/happiness
6. TRANSACTIONS — logs all player balance/item updates
7. SHOP_ITEMS — store items (food, accessories)
8. GENES — genetic traits (color, size, speed, etc.)
9. ALLELES — variants of genes with dominance relationships
10. PET_GENETICS — genetic code per pet
11. OFFSPRING — breeding outcomes and inheritance
"""

# =========================================================
# Database setup
# =========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "GuineaGames.db")

sqliteConnection = sqlite3.connect(DB_PATH)
cursor = sqliteConnection.cursor()

# =========================================================
# Drop old tables and views
# =========================================================
# Drop view first
cursor.execute("DROP VIEW IF EXISTS GUINEA_PIGS;")

# Then drop tables
tables = [
    "PET_SALES_HISTORY",
    "PET_MARKETPLACE",
    "OFFSPRING",
    "PET_GENETICS",
    "ALLELES",
    "GENES",
    "TRANSACTIONS",
    "LEADERBOARDS",
    "MINI_GAMES",
    "INVENTORY",
    "PETS",
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
-- =============================
CREATE TABLE USERS (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    balance INTEGER DEFAULT 0 CHECK(balance >= 0),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME
);

-- =============================
-- PETS (Primary Animal Table)
-- =============================
CREATE TABLE PETS (
    id INTEGER PRIMARY KEY,
    owner_id INTEGER NOT NULL,
    name TEXT,
    species TEXT CHECK(species IN ('guinea_pig', 'hamster', 'predator')),
    color TEXT,
    color_phenotype TEXT,
    hair_type TEXT CHECK(hair_type IN ('short', 'fluffy')) DEFAULT 'short',
    age_days INTEGER DEFAULT 0,
    health INTEGER CHECK(health BETWEEN 0 AND 100) DEFAULT 100,
    happiness INTEGER CHECK(happiness BETWEEN 0 AND 100) DEFAULT 100,
    hunger INTEGER CHECK(hunger BETWEEN 0 AND 3) DEFAULT 3,
    cleanliness INTEGER CHECK(cleanliness BETWEEN 0 AND 100) DEFAULT 100,
    points INTEGER DEFAULT 0,
    genetic_code TEXT,
    speed INTEGER CHECK(speed BETWEEN 0 AND 100) DEFAULT 50,
    endurance INTEGER CHECK(endurance BETWEEN 0 AND 100) DEFAULT 50,
    rarity_score INTEGER DEFAULT 0,
    rarity_tier TEXT CHECK(rarity_tier IN ('Common', 'Uncommon', 'Rare', 'Legendary')) DEFAULT 'Common',
    market_value INTEGER DEFAULT 100,
    for_sale INTEGER DEFAULT 0,
    asking_price INTEGER,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES USERS(id)
);

-- Legacy alias for backward compatibility
CREATE VIEW GUINEA_PIGS AS SELECT * FROM PETS;

-- =============================
-- INVENTORY
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
-- =============================
CREATE TABLE MINI_GAMES (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    base_reward INTEGER DEFAULT 0,
    cooldown_sec INTEGER
);

-- =============================
-- LEADERBOARDS
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
-- =============================
CREATE TABLE SHOP_ITEMS (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT CHECK(category IN ('food', 'accessory', 'toy', 'medicine')) DEFAULT 'food',
    cost INTEGER NOT NULL,
    description TEXT,
    effect TEXT
);

-- =============================
-- GENES
-- =============================
CREATE TABLE GENES (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    trait TEXT NOT NULL,
    description TEXT,
    default_allele_id INTEGER
);

-- =============================
-- ALLELES
-- =============================
CREATE TABLE ALLELES (
    id INTEGER PRIMARY KEY,
    gene_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    symbol TEXT NOT NULL,
    dominance_level INTEGER DEFAULT 1,
    effect_value INTEGER DEFAULT 0,
    description TEXT,
    FOREIGN KEY (gene_id) REFERENCES GENES(id)
);

-- =============================
-- PET_GENETICS
-- =============================
CREATE TABLE PET_GENETICS (
    id INTEGER PRIMARY KEY,
    pet_id INTEGER UNIQUE NOT NULL,
    gene_id INTEGER NOT NULL,
    allele1_id INTEGER NOT NULL,
    allele2_id INTEGER NOT NULL,
    FOREIGN KEY (pet_id) REFERENCES PETS(id),
    FOREIGN KEY (gene_id) REFERENCES GENES(id),
    FOREIGN KEY (allele1_id) REFERENCES ALLELES(id),
    FOREIGN KEY (allele2_id) REFERENCES ALLELES(id)
);

-- =============================
-- OFFSPRING
-- =============================
CREATE TABLE OFFSPRING (
    id INTEGER PRIMARY KEY,
    parent1_id INTEGER NOT NULL,
    parent2_id INTEGER NOT NULL,
    child_id INTEGER NOT NULL,
    breeding_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    punnett_square_data TEXT,
    inheritance_notes TEXT,
    FOREIGN KEY (parent1_id) REFERENCES PETS(id),
    FOREIGN KEY (parent2_id) REFERENCES PETS(id),
    FOREIGN KEY (child_id) REFERENCES PETS(id)
);

-- =============================
-- PET_MARKETPLACE
-- =============================
CREATE TABLE PET_MARKETPLACE (
    id INTEGER PRIMARY KEY,
    pet_id INTEGER UNIQUE NOT NULL,
    seller_id INTEGER NOT NULL,
    asking_price INTEGER NOT NULL,
    listed_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pet_id) REFERENCES PETS(id),
    FOREIGN KEY (seller_id) REFERENCES USERS(id)
);

-- =============================
-- PET_SALES_HISTORY
-- =============================
CREATE TABLE PET_SALES_HISTORY (
    id INTEGER PRIMARY KEY,
    pet_id INTEGER NOT NULL,
    seller_id INTEGER NOT NULL,
    buyer_id INTEGER NOT NULL,
    sale_price INTEGER NOT NULL,
    sale_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pet_id) REFERENCES PETS(id),
    FOREIGN KEY (seller_id) REFERENCES USERS(id),
    FOREIGN KEY (buyer_id) REFERENCES USERS(id)
);
"""

cursor.executescript(sql_commands)
sqliteConnection.commit()
sqliteConnection.close()

print("✅ GuineaGames.db created successfully with merged schema and legacy support.")
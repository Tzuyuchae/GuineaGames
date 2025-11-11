import sqlite3
import os
import json

"""
Seeds initial food items into the GuineaGames database.
Run this script after creating the database to populate shop with food items.
"""

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "GuineaGames.db")

# Food items to seed
FOOD_ITEMS = [
    {
        "name": "Carrot",
        "category": "food",
        "cost": 5,
        "description": "Crunchy orange vegetable, very filling",
        "effect": json.dumps({"hunger": 2, "health": 5})
    },
    {
        "name": "Lettuce",
        "category": "food",
        "cost": 3,
        "description": "Fresh leafy greens",
        "effect": json.dumps({"hunger": 1, "happiness": 3})
    },
    {
        "name": "Premium Pellets",
        "category": "food",
        "cost": 10,
        "description": "Nutritionally balanced feed",
        "effect": json.dumps({"hunger": 3, "health": 10, "happiness": 5})
    },
    {
        "name": "Apple Slice",
        "category": "food",
        "cost": 7,
        "description": "Sweet treat",
        "effect": json.dumps({"hunger": 1, "happiness": 8, "health": 3})
    },
    {
        "name": "Hay",
        "category": "food",
        "cost": 2,
        "description": "Basic fibrous food",
        "effect": json.dumps({"hunger": 1})
    },
    {
        "name": "Vitamin Supplement",
        "category": "medicine",
        "cost": 15,
        "description": "Boosts overall health",
        "effect": json.dumps({"health": 20})
    },
    {
        "name": "Timothy Hay",
        "category": "food",
        "cost": 4,
        "description": "High-quality hay",
        "effect": json.dumps({"hunger": 2, "health": 3})
    },
    {
        "name": "Bell Pepper",
        "category": "food",
        "cost": 6,
        "description": "Vitamin C rich vegetable",
        "effect": json.dumps({"hunger": 1, "health": 8, "happiness": 2})
    },
]

# Connect to database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Clear existing shop items (optional - comment out if you want to keep existing items)
cursor.execute("DELETE FROM SHOP_ITEMS")

# Insert food items
for item in FOOD_ITEMS:
    cursor.execute("""
        INSERT INTO SHOP_ITEMS (name, category, cost, description, effect)
        VALUES (?, ?, ?, ?, ?)
    """, (item["name"], item["category"], item["cost"], item["description"], item["effect"]))

conn.commit()
conn.close()

print(f"✅ Successfully seeded {len(FOOD_ITEMS)} food items into the database!")
print("\nFood items added:")
for item in FOOD_ITEMS:
    print(f"  - {item['name']} ({item['category']}) - ${item['cost']}")

import sqlite3
import os

DB_PATH = "data/telecom_ops.db"
SCHEMA_PATH = "sql/01_schema.sql"
SEED_PATH = "sql/02_seed_data.sql"

print("Building fresh database from official Capstone SQL files...")

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

# Connect to (and automatically create) the new database
try:
    with sqlite3.connect(DB_PATH) as conn:
        # 1. Execute Schema
        with open(SCHEMA_PATH, 'r') as f:
            conn.executescript(f.read())
            
        # 2. Execute Seed Data
        with open(SEED_PATH, 'r') as f:
            conn.executescript(f.read())
            
    print("✅ SUCCESS! telecom_ops.db has been completely rebuilt with official data!")
except Exception as e:
    print(f"❌ Error building database: {e}")
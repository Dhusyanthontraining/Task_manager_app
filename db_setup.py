import sqlite3
from datetime import datetime

conn = sqlite3.connect("tracker.db")
cursor = conn.cursor()

# -------------------- USERS TABLE --------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL
)
""")

# -------------------- HISTORY TABLE --------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    module TEXT NOT NULL,
    minutes INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")

conn.commit()
conn.close()

print("Database setup completed successfully.")

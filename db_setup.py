import sqlite3

conn = sqlite3.connect('tracker.db')
conn.execute('''CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY,
                user_id TEXT,
                date TEXT,
                module TEXT,
                minutes INTEGER)''')
conn.commit()
conn.close()

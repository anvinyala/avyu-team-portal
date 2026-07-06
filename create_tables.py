from database import get_connection

conn = get_connection()

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fullname TEXT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
)
""")

conn.commit()

print("Database Created Successfully")
from database import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
INSERT INTO users (fullname, username, password, role)
VALUES (?, ?, ?, ?)
""", (
    "Administrator",
    "admin",
    "admin123",
    "admin"
))

conn.commit()

print("Admin Created Successfully")
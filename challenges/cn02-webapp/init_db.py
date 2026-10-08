import sqlite3

conn = sqlite3.connect("/data/staff.db")
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS staff")
cur.execute("""
    CREATE TABLE staff (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        password TEXT NOT NULL
    )
""")

cur.execute(
    "INSERT INTO staff (username, password) VALUES (?, ?)",
    ("jfernando", "N3st!ngB1rd2024")
)

conn.commit()
conn.close()
print("Database seeded.")

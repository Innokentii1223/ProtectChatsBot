import sqlite3
conn = sqlite3.connect("Users.db", check_same_thread=False)
conn.execute("""CREATE TABLE IF NOT EXISTS Users(
id INTEGER,
name TEXT,
asset BOOLEAN,
ban BOOLEAN,
unban TEXT
)""")
conn.execute("""INSERT INTO Users (id, name, asset, ban, unban) VALUES (?, ?, ?, ?, ?)""", (0, "NULL", False, False, "n"))
conn.commit()
conn.close()

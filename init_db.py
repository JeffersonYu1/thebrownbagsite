import sqlite3

db = sqlite3.connect('database.db')

with open('schema.sql') as f:
    db.executescript(f.read())

cur = db.cursor()

cur.execute("INSERT INTO users (id, fname, lname, email) VALUES (?, ?, ?, ?)",
            (123456, 
            "John",
            "Doe",
            "test1@gmail.com")
            )

cur.execute("INSERT INTO users (id, fname, lname, email) VALUES (?, ?, ?, ?)",
            (456576, 
            "Aa",
            "Bb",
            "tes21@gmail.com")
            )

db.commit()
db.close()
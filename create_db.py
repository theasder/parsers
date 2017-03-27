import sqlite3

conn = sqlite3.connect('data/profiles.db')
c = conn.cursor()

c.execute('''CREATE TABLE github(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user VARCHAR(100),
            email VARCHAR(100),
            avatar VARCHAR(100),
            location VARCHAR(100),
            name VARCHAR(100),
            blog VARCHAR(100),
            commits BIGINT,
            watchers BIGINT,
            stars BIGINT,
            languages VARCHAR(5000));''')
conn.commit()

conn.close()
import sqlite3

# Establish SQLite database connection
conn = sqlite3.connect('timezones.db')
cursor = conn.cursor()

# Create timezone table if not exists
cursor.execute('''CREATE TABLE IF NOT EXISTS timezones
                  (id INTEGER PRIMARY KEY, name TEXT, offset INTEGER)''')

# Populate timezone data
timezones = [
    ("UTC", 0),
    ("America/New_York", -5),
    ("Europe/London", 0),
    # Add more timezone data as needed
]
cursor.executemany("INSERT INTO timezones (name, offset) VALUES (?, ?)", timezones)

# Commit changes and close connection
conn.commit()
conn.close()

print("Database created and populated successfully!")

import sqlite3
import datetime

# Create SQLite database connection
conn = sqlite3.connect('timezones.db')
cursor = conn.cursor()

# Create timezone table
cursor.execute('''CREATE TABLE IF NOT EXISTS timezones
                  (id INTEGER PRIMARY KEY, name TEXT, offset INTEGER)''')

# Populate timezone data (example)
timezones = [
    ("UTC", 0),
    ("America/New_York", -5),
    ("Europe/London", 0),
    # Add more timezone data as needed
]
cursor.executemany("INSERT INTO timezones (name, offset) VALUES (?, ?)", timezones)
conn.commit()

# Function to get live time for a specific timezone
def get_live_time(timezone):
    cursor.execute("SELECT offset FROM timezones WHERE name=?", (timezone,))
    offset = cursor.fetchone()
    if offset:
        offset = offset[0]
        current_utc_time = datetime.datetime.utcnow()
        live_time = current_utc_time + datetime.timedelta(hours=offset)
        return live_time
    else:
        return None

# Example usage
timezone = "America/New_York"
live_time = get_live_time(timezone)
if live_time:
    print(f"Live time in {timezone}: {live_time}")
else:
    print("Timezone not found in the database")

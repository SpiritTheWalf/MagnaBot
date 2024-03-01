import sqlite3

DATABASE_FILE = "logging_cog.db"

def create_database():
    # Connect to the database file or create it if it doesn't exist
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # Create the guilds table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS guilds (
        guild_id INTEGER PRIMARY KEY,
        default_logging_channel INTEGER
    )
    """)

    # Commit changes and close the connection
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
    print("Database created successfully.")

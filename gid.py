import sqlite3

DATABASE_FILE = "logging_cog.db"


def get_default_logging_channel(guild_id):
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT default_logging_channel FROM guilds WHERE guild_id = ?", (guild_id,))
        result = cursor.fetchone()
        default_channel_id = result[0] if result else None
        print(f"Default logging channel ID for guild {guild_id}: {default_channel_id}")
        return default_channel_id
    except sqlite3.Error as e:
        print(f"Error retrieving default logging channel ID: {e}")
    finally:
        if conn:
            conn.close()


# Example usage:
# Replace 'guild_id' with the actual guild ID for which you want to retrieve the default logging channel
guild_id = "1212032856847683634"
default_channel_id = get_default_logging_channel(guild_id)

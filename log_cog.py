import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
from datetime import datetime

DATABASE_FILE = "logging_cog.db"


class LoggingCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.conn = sqlite3.connect(DATABASE_FILE)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS default_logging_channel (
                            guild_id INTEGER PRIMARY KEY,
                            channel_id INTEGER
                          )''')
        self.conn.commit()

    def get_default_logging_channel(self, guild_id):
        cursor = self.conn.cursor()
        cursor.execute('''SELECT channel_id FROM default_logging_channel WHERE guild_id = ?''', (guild_id,))
        row = cursor.fetchone()
        if row:
            return row[0]
        else:
            return None

    def set_default_logging_channel(self, guild_id, channel_id):
        cursor = self.conn.cursor()
        cursor.execute('''REPLACE INTO default_logging_channel (guild_id, channel_id) VALUES (?, ?)''',
                       (guild_id, channel_id))
        self.conn.commit()

    async def send_logging_embed(self, guild, action, member):
        channel_id = self.get_default_logging_channel(guild.id)
        if channel_id:
            channel = guild.get_channel(channel_id)
            if channel:
                embed = discord.Embed(
                    title=f"Member {action}",
                    color=discord.Color.green() if action == 'joined' else discord.Color.red()
                )
                embed.set_thumbnail(url=member.avatar.url)
                embed.add_field(name="User", value=member.mention, inline=False)
                embed.add_field(name="User ID", value=member.id, inline=False)
                embed.add_field(name="Timestamp", value=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                                inline=False)
                await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.send_logging_embed(member.guild, "joined", member)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await self.send_logging_embed(member.guild, "left", member)

    @app_commands.command(name="defaultloggingchannel", description="Prints the default logging channel for the server")
    async def default_logging_channel(self, inter: discord.Interaction):
        guild_id = inter.guild.id
        channel_id = self.get_default_logging_channel(guild_id)
        if channel_id:
            channel = inter.guild.get_channel(channel_id)
            if channel:
                await inter.response.send_message(f"The default logging channel for this server is: {channel.mention}")
            else:
                await inter.response.send_message("The default logging channel is not set.")
        else:
            await inter.response.send_message("The default logging channel is not set.")

    @app_commands.command(name="setloggingchannel", description="Sets the default logging channel for the server")
    async def set_logging_channel(self, inter: discord.Interaction, channel: discord.TextChannel):
        guild_id = inter.guild.id
        if not inter.user.guild_permissions.administrator:
            await inter.response.send_message("You do not have permission to use this command.")
            return

        self.set_default_logging_channel(guild_id, channel.id)
        await inter.response.send_message(f"Default logging channel set to {channel.mention}")

    def __unload(self):
        self.conn.close()


async def setup(bot: commands.Bot):
    try:
        await bot.add_cog(LoggingCog(bot))
        print("LoggingCog has been loaded successfully!")
    except Exception as e:
        print(f"An error occurred while loading the LoggingCog: {e}")

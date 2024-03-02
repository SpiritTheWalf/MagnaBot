import discord
import sqlite3
from discord import app_commands
from discord.ext import commands
from datetime import datetime

DATABASE_FILE = "logging_cog.db"


class ModerationCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def get_connection(self):
        return sqlite3.connect(DATABASE_FILE)

    async def get_default_logging_channel(self, guild_id):
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

    async def send_warning_embeds(self, channel, guild, user, issuer, reason):
        warning_embed = discord.Embed(title="User Warned", color=discord.Color.orange())
        warning_embed.add_field(name="User", value=user.display_name, inline=False)
        warning_embed.set_thumbnail(url=user.avatar.url)
        warning_embed.add_field(name="Issuer", value=issuer.display_name, inline=False)
        warning_embed.add_field(name="Reason", value=reason, inline=False)
        warning_embed.add_field(name="Timestamp", value=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                                inline=False)

        await channel.send(embed=warning_embed)

    @app_commands.command(name="warn", description="Warn a user for violating rules")
    async def warn_command(self, inter: discord.Interaction, user: discord.Member, reason: str):
        guild = inter.guild
        if not guild:
            await inter.response.send_message("This command must be used in a server.")
            return

        # Check if the issuer has the "Kick Members" permission or is an administrator
        issuer = inter.user
        if not issuer.guild_permissions.kick_members and not issuer.guild_permissions.administrator:
            await inter.response.send_message("You don't have permission to use this command.")
            return

        # Get the default logging channel
        default_channel_id = await self.get_default_logging_channel(guild.id)
        if not default_channel_id:
            await inter.response.send_message("Default logging channel not found.")
            return

        # Get the default logging channel
        default_channel = guild.get_channel(default_channel_id)
        if not default_channel:
            await inter.response.send_message("Default logging channel not found.")
            return

        # Send warning embed to default logging channel
        await self.send_warning_embeds(default_channel, guild, user, issuer, reason)

        # Direct message the user being warned
        try:
            warning_embed = discord.Embed(title="You have been warned!", color=discord.Color.orange())
            warning_embed.set_thumbnail(url=user.avatar.url)
            warning_embed.add_field(name="Server", value=guild.name, inline=False)
            warning_embed.add_field(name="Issuer", value=issuer.display_name, inline=False)
            warning_embed.add_field(name="Reason", value=reason, inline=False)
            warning_embed.add_field(name="Timestamp", value=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                                    inline=False)

            await user.send(embed=warning_embed)
        except discord.Forbidden:
            await inter.response.send_message("Failed to DM the user. Make sure they have DMs enabled.")

        await inter.response.send_message("User has been warned successfully.")

    @app_commands.command(name="kick", description="Kick a user from the server")
    async def kick_command(self, inter: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
        guild = inter.guild
        issuer = inter.user

        # Check if the issuer has the "Kick Members" permission or is an administrator
        if not issuer.guild_permissions.kick_members and not issuer.guild_permissions.administrator:
            await inter.response.send_message("You don't have permission to use this command.")
            return

        # Send DM to the kicked user
        try:
            kick_dm_embed = discord.Embed(title="You have been kicked from the server!", color=discord.Color.red())
            kick_dm_embed.set_thumbnail(url=user.avatar.url)
            kick_dm_embed.add_field(name="Server", value=guild.name, inline=False)
            kick_dm_embed.add_field(name="Issuer", value=issuer.display_name, inline=False)
            kick_dm_embed.add_field(name="Reason", value=reason, inline=False)
            kick_dm_embed.add_field(name="Timestamp", value=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"), inline=False)

            await user.send(embed=kick_dm_embed)
        except discord.Forbidden:
            await inter.response.send_message("Failed to send a DM to the kicked user. Make sure they have DMs enabled.")

        # Kick the user
        try:
            await user.kick(reason=reason)
        except discord.Forbidden:
            await inter.response.send_message("I don't have permission to kick that user.")
            return

        # Get the default logging channel
        default_channel_id = await self.get_default_logging_channel(guild.id)
        if not default_channel_id:
            await inter.response.send_message("Default logging channel not found.")
            return

        # Get the default logging channel
        default_channel = guild.get_channel(default_channel_id)
        if not default_channel:
            await inter.response.send_message("Default logging channel not found.")
            return

        # Send kick embed to default logging channel
        try:
            await self.send_logging_embed(default_channel, guild, user, issuer, reason)
            await inter.response.send_message(f"{user.mention} has been kicked from the server for: {reason}")
        except Exception as e:
            await inter.response.send_message(f"Failed to send embed to the default logging channel: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(ModerationCog(bot))
    print("ModerationCog loaded successfully!")

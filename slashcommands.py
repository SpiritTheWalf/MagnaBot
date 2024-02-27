from discord.ext import commands
import datetime
import discord
from discord import app_commands, interactions


class MyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="set_timezone")
    async def set_timezone(self, interaction: discord.Interaction, timezone: str):
        # You may want to validate the timezone input here
        # Save the user's timezone information in your database or cache
        pass

    @app_commands.command(name="time")
    async def time(self, interaction: discord.Interaction):
        # Retrieve the user's timezone information from your database or cache
        # For demonstration purposes, let's assume we have a function to get the timezone
        user_timezone = None  # Placeholder for get_user_timezone(ctx.author.id)

        if user_timezone:
            # Convert the current time to the user's timezone
            current_time = datetime.datetime.now(user_timezone)
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S %Z")
            await interaction.response.send_message(f"Your local time is: {formatted_time}")
        else:
            await interaction.response.send_message("Please set your timezone using the set_timezone command.")

    @app_commands.command(name="test")
    async def test(self, interaction: discord.Interaction):
        await interaction.response.send_message("The Bot is working")

    @app_commands.command(name="ping")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("Pong!")

    @app_commands.command(name="invite")
    async def invite(self, interaction: discord.Interaction):
        await interaction.response.send_message("Join my server for development updates! https://discord.gg/bYEYvA7R3G")

async def setup(bot: commands.Bot):
    await bot.add_cog(MyCog(bot))



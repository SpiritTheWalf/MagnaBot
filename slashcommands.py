import discord
from discord import app_commands
from discord.ext import commands

class MyCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="command-1")
    async def my_command(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Hello from command 1!")

    @app_commands.command(name="ping")
    async def ping(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Pong!")

    @app_commands.command(name="invite")
    async def invite(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Join my server for development updates! https://discord.gg/bYEYvA7R3G")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MyCog(bot))
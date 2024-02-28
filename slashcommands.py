import discord
from discord.ext import commands
from discord import app_commands, interactions
import discord.app_commands
import interactions
from discord.ext.commands import bot


class MyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @app_commands.command(name="test")
    async def test(self, interaction: discord.Interaction):
        await interaction.response.send_message("The Bot is working")

    @app_commands.command(name="ping")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("Pong!")

    @app_commands.command(name="invite")
    async def invite(self, interaction: discord.Interaction):
        await interaction.response.send_message("Join my server for development updates! https://discord.gg/bYEYvA7R3G")
    @app_commands.command(name="list_commands", description="List all available commands")
    async def list_commands(self, interaction: discord.Interaction):
        normal_commands = [command.name for command in self.bot.commands]

        slash_commands = []
        for cog in self.bot.cogs.values():
            if isinstance(cog, commands.Cog):
                    slash_commands.extend([
                        command.name for command in cog.get_commands() if isinstance(command, app_commands.Command)
                    ])

        response = f"**Normal Commands:**\n{', '.join(normal_commands)}\n\n"
        response += f"**Slash Commands:**\n{', '.join(slash_commands)}"

        await interaction.response.send_message(content=response)

async def setup(bot: commands.Bot):
    await bot.add_cog(MyCog(bot))
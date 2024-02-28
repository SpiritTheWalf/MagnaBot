from datetime import datetime

import discord.app_commands
from discord import app_commands
from discord.ext import commands
from pytz import timezone, all_timezones

intents = discord.Intents.default()
intents.members = True
intents.message_content = True


class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


bot = MyBot(intents=intents, command_prefix="?")


# noinspection PyUnresolvedReferences,PyShadowingNames,PyUnusedLocal
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
                    command.name for command in cog.get_app_commands() if isinstance(command, app_commands.Command)
                ])

        response = f"**Normal Commands:**\n{', '.join(normal_commands)}\n\n"
        response += f"**Slash Commands:**\n{', '.join(slash_commands)}"

        await interaction.response.send_message(content=response)

    @app_commands.command()
    async def timenow(self, interaction: discord.Interaction, timezone_name: str, ):  # formerly printCurrentTime
        fmt = "%Y-%m-%d %H:%M:%S %Z%z"

        if timezone_name not in all_timezones:
            await interaction.response.send_message("Unknown timezone. Please provide a valid timezone name.")

        # Current time in UTC
        now_utc = datetime.now(timezone('UTC'))

        # Convert to Europe/London time zone
        now_london = now_utc.astimezone(timezone('Europe/London'))
        now_berlin = now_utc.astimezone(timezone('Europe/Berlin'))
        now_cet = now_utc.astimezone(timezone('CET'))
        now_israel = now_utc.astimezone(timezone('Israel'))
        now_canada_east = now_utc.astimezone(timezone('Canada/Eastern'))
        now_central = now_utc.astimezone(timezone('US/Central'))
        now_pacific = now_utc.astimezone(timezone('US/Pacific'))

        selected_timezone = timezone(timezone_name)
        selected_time = now_utc.astimezone(selected_timezone)

        await interaction.response.send_message(selected_time.strftime(fmt) + f" ({timezone_name})")

    @app_commands.command(name="tzlist")
    async def tzlist(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "The valid timezones are:\n Europe/London\n Europe/Berlin\n CET\n Israel\n Canada/Eastern\n US/Central\n "
            "US/Pacific")

    @app_commands.command(
        name="embed",
        description="Create an embed with custom fields"
    )
    async def embed(self, inter: commands.Context, title: str, description: str, field1_name: str, field1_value: str,
                    field2_name: str, field2_value: str):
        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.blue()
        )

        embed.add_field(name=field1_name, value=field1_value, inline=False)
        embed.add_field(name=field2_name, value=field2_value, inline=False)
        embed.set_footer(text="MagnaBot - Made by SpiritTheWalf")
        await inter.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(MyCog(bot))

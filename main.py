import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
TOKEN = os.getenv('BOT_TOKEN')


class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def setup_hook(self):
        print("Bot is starting")
        if not self.get_cog("slashcommands"):
            await self.load_extension("slashcommands")
        if not self.get_cog("log_cog"):
            await self.load_extension("log_cog")
        if not self.get_cog("moderation"):
            await self.load_extension("moderation")
        print("Cogs loaded!")


bot = MyBot(intents=intents, command_prefix="?")

@bot.command()
async def embed(ctx):
    embed = discord.Embed(
        title="Title",
        description="description",
        color=discord.Color.blue()
    )
    embed.add_field(name='Field 1', value="Value 1", inline=False)
    embed.add_field(name="Field 2", value="Value 2", inline=True)
    embed.set_footer(text="Footer text")

    await ctx.send(embed=embed)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    for command in bot.commands:
        print(command.name)
    members = 0

    # Iterate over each guild the bot is in
    for guild in bot.guilds:
        members += guild.member_count - 1

        # Check if the bot's name has changed
        if guild.me.name != bot.user.name:
            # Find the bot's member object in the guild
            me = guild.me
            try:
                # Change the bot's nickname to match its updated name
                await me.edit(nick=bot.user.name)
                print(f"Nickname updated in {guild.name}")
            except discord.Forbidden:
                print(f"Couldn't change nickname in {guild.name} due to lack of permissions.")
            except Exception as e:
                print(f"An error occurred while changing nickname in {guild.name}: {e}")

    # Set the bot's presence
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,
        name=f'{members} members'
    ))
    print('Ready!')





@bot.command(pass_context=True)
@commands.is_owner()
async def sync(ctx):
    await ctx.bot.tree.sync()
    await ctx.send("Commands synced, you will need to reload Discord to see them")


@bot.command()
async def load(ctx):
    print('Load command executed!')
    await load_cogs()
    await ctx.send('Cogs loaded!')


@bot.command()
@commands.is_owner()
async def dotstatus(ctx: commands.Context, status: str):
    status = status.lower()
    if status == "online":
        presence_status = discord.Status.online
    elif status == "idle":
        presence_status = discord.Status.idle
    elif status == "dnd" or status == "do_not_disturb":
        presence_status = discord.Status.do_not_disturb
    elif status == "offline":
        presence_status = discord.Status.invisible
    else:
        await ctx.send("Invalid status. Please use one of the following: online, idle, dnd, offline")
        return

    await bot.change_presence(status=presence_status)
    await ctx.send(f"Bot presence status set to: {status.capitalize()}")


async def load_cogs():
    await bot.setup_hook()


bot.run(TOKEN)

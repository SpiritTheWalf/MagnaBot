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
        await self.load_extension("slashcommands")
        print('Cogs loaded!')

bot = MyBot(intents=intents, command_prefix="?")

async def setup_bot():
    await bot.load_extension("slashcommands")

    await bot.setup_hook()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    for command in bot.commands:
        print(command.name)

@bot.event
async def on_message(message):
    await bot.process_commands(message)

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

async def load_cogs():
    await bot.setup_hook()

setup_bot()
bot.run(TOKEN)

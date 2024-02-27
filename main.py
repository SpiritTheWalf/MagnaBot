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
    async def setup_hook(self):
        print("Bot is starting")
        await self.load_extension("slashcommands")

bot=MyBot(intents=intents, command_prefix="?")
@bot.command()
async def sync(ctx):
    await ctx.bot.tree.sync()
    await ctx.send("commands synced, you may need to reload Discord to see them")



bot.run(TOKEN)
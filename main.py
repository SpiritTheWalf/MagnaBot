#main.py
import os
import discord
from dotenv import  load_dotenv
from discord.ext import commands


load_dotenv()
intents= discord.Intents.all()
TOKEN = os.getenv('BOT_TOKEN')
bot = commands.Bot(command_prefix= '%', intents=intents)


client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'{client.user} has connedted to Discord!')

client.run(TOKEN)
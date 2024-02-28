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

    for guild in bot.guilds:
        members += guild.member_count - 1
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,

        name=f'{members} members'
    ))
    await bot.change_presence(status=discord.Status.do_not_disturb)
    print('ready!')


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
    await setup_bot()


bot.run(TOKEN)

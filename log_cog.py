import sqlite3
import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime

DATABASE_FILE = "logging_cog.db"


class LoggingCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def get_connection(self):
        return sqlite3.connect(DATABASE_FILE)

    def load_default_logging_channel(self, guild_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT default_logging_channel FROM guilds WHERE guild_id = ?", (guild_id,))
            result = cursor.fetchone()
            logging_channel_id = result[0] if result else None
            if logging_channel_id:
                print(f"Loaded default logging channel ID {logging_channel_id} for guild {guild_id}")
            else:
                print(f"No default logging channel found for guild {guild_id}")
            return logging_channel_id

    def save_default_logging_channel(self, guild_id, channel_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("REPLACE INTO guilds (guild_id, default_logging_channel) VALUES (?, ?)",
                           (guild_id, channel_id))
            conn.commit()
            print(f"Saved default logging channel ID {channel_id} for guild {guild_id}")

    @app_commands.command(name="defaultloggingchannel", description="Prints the default logging channel for the server")
    async def default_logging_channel(self, inter: discord.Interaction):
        guild = inter.guild
        channel_id = self.load_default_logging_channel(guild.id)
        if channel_id:
            channel = guild.get_channel(int(channel_id))
            if channel:
                await inter.response.send_message(f"The default logging channel for this server is: {channel.mention}")
            else:
                await inter.response.send_message("The default logging channel is not set.")
        else:
            await inter.response.send_message("The default logging channel is not set.")

    @app_commands.command(name="setloggingchannel", description="Sets the default logging channel for the server")
    async def set_logging_channel(self, inter: discord.Interaction, channel: discord.TextChannel):
        guild = inter.guild
        if not inter.user.guild_permissions.administrator:
            await inter.response.send_message("You do not have permission to use this command.")
            return

        self.save_default_logging_channel(guild.id, channel.id)
        await inter.response.send_message(f"Default logging channel set to {channel.mention}")

    async def send_jl_logging_embed(self, guild, action, member):
        channel_id = self.load_default_logging_channel(guild.id)
        if channel_id:
            channel = guild.get_channel(int(channel_id))
            if channel:
                embed = discord.Embed(
                    title=f"Member {action}",
                    color=discord.Color.green() if action == 'joined' else discord.Color.red()
                )
                embed.set_thumbnail(url=member.avatar.url)
                embed.add_field(name="User", value=member.mention, inline=False)
                embed.add_field(name="User ID", value=member.id, inline=False)
                embed.add_field(name="Timestamp", value=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                                inline=False)
                await channel.send(embed=embed)

    async def send_message_edit_logging_embed(self, before, after):  # Edited Messages
        channel_id = self.load_default_logging_channel(after.guild.id)
        if channel_id:
            channel = after.guild.get_channel(int(channel_id))
            if channel:
                embed = discord.Embed(
                    title="Message Edited",
                    color=discord.Color.gold()
                )
                embed.add_field(name="Original Message", value=before.content, inline=False)
                embed.add_field(name="Edited Message", value=after.content, inline=False)
                embed.add_field(name="Author", value=before.author.mention, inline=False)
                embed.add_field(name="Channel", value=after.channel.mention, inline=False)
                embed.add_field(name="Timestamp", value=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                                inline=False)
                await channel.send(embed=embed)

    async def send_reaction_logging_embed(self, guild, action, target, user):  # Reaction logging
        default_channel_id = self.load_default_logging_channel(guild.id)
        if not default_channel_id:
            return

        default_channel = guild.get_channel(default_channel_id)
        if not default_channel:
            return

        embed = discord.Embed(title=f"Reaction {action}",
                              color=discord.Color.green() if action == 'added' else discord.Color.red())
        embed.set_thumbnail(url=target.guild.icon.url)
        embed.add_field(name="Message Author", value=target.author.mention, inline=False)
        embed.add_field(name="Message Content", value=target.content, inline=False)
        embed.add_field(name="Reaction Author", value=user.mention, inline=False)
        embed.add_field(name="Emoji", value=str(reaction.emoji), inline=False)
        embed.add_field(name="Channel", value=target.channel.mention, inline=False)
        embed.add_field(name="Timestamp", value=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"), inline=False)

        await default_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        await self.send_jl_logging_embed(guild, "joined", member)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild = member.guild
        # Check if the member is no longer in the guild due to being kicked
        if member not in guild.members:
            await self.send_jl_logging_embed(guild, "kicked", member)
        else:
            await self.send_jl_logging_embed(guild, "left", member)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        await self.send_message_edit_logging_embed(before, after)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        await self.log_reaction_event(payload, "added")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        await self.log_reaction_event(payload, "removed")

    async def log_reaction_event(self, payload, action):
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        channel = guild.get_channel(payload.channel_id)
        if not channel:
            return

        try:
            message = await channel.fetch_message(payload.message_id)
        except discord.NotFound:
            return

        user = guild.get_member(payload.user_id)
        if not user:
            return

        emoji = payload.emoji

        default_channel_id = self.load_default_logging_channel(guild.id)
        if not default_channel_id:
            return

        default_channel = guild.get_channel(default_channel_id)
        if not default_channel:
            return

        embed = discord.Embed(
            title=f"Reaction {action}",
            description=f"Emoji: {emoji}",
            color=discord.Color.green() if action == "added" else discord.Color.red()
        )
        embed.add_field(name="User", value=user.mention, inline=False)
        embed.add_field(name="Message", value=message.content, inline=False)
        embed.add_field(name="Channel", value=channel.mention, inline=False)
        embed.add_field(name="Timestamp", value=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"), inline=False)

        try:
            await default_channel.send(embed=embed)
        except Exception as e:
            print(f"Error occurred while sending reaction event embed: {e}")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        guild = member.guild

        # Check if the user joined or left a voice channel
        if before.channel != after.channel:
            action = "joined" if after.channel else "left"
            voice_channel = after.channel if after.channel else before.channel

            default_channel_id = self.load_default_logging_channel(guild.id)
            if default_channel_id:
                default_channel = guild.get_channel(default_channel_id)
                if default_channel:
                    try:
                        embed = discord.Embed(
                            title=f"Voice {action.capitalize()}",
                            color=discord.Color.green() if action == "joined" else discord.Color.red()
                        )
                        embed.add_field(name="User", value=member.mention, inline=False)
                        embed.add_field(name="Voice Channel", value=voice_channel.mention, inline=False)
                        embed.add_field(name="Timestamp", value=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                                        inline=False)

                        await default_channel.send(embed=embed)
                    except Exception as e:
                        print(f"Error occurred while sending voice event embed: {e}")
                else:
                    print("Default logging channel not found.")
            else:
                print("Default logging channel ID not found.")

    async def send_message_deleted_embed(self, channel, message):
        if not message.author:
            return

        embed = discord.Embed(
            title="Message Deleted",
            color=discord.Color.red()
        )
        embed.add_field(name="Author", value=message.author.mention, inline=False)
        embed.add_field(name="Channel", value=message.channel.mention, inline=False)
        embed.add_field(name="Content", value=message.content, inline=False)
        embed.add_field(name="Timestamp", value=message.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"), inline=False)

        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        guild = message.guild

        default_channel_id = self.load_default_logging_channel(guild.id)
        if not default_channel_id:
            return

        default_channel = guild.get_channel(default_channel_id)
        if not default_channel:
            return

        # Send message deleted embed to default logging channel
        await self.send_message_deleted_embed(default_channel, message)


async def setup(bot: commands.Bot):
    await bot.add_cog(LoggingCog(bot))

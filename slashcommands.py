from datetime import datetime
from pytz import all_timezones, timezone
import discord.app_commands
from discord import app_commands
from discord.ext import commands
import json
from discord import Interaction

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
try:
    with open('blacklisted_domains.json', 'r') as file:
        blacklisted_domains = json.load(file)
except FileNotFoundError:
    blacklisted_domains = []
DEFAULT_LOGGING_CHANNEL_FILE = "default_logging_channel.txt"

class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


bot = MyBot(intents=intents, command_prefix="?")


# noinspection PyUnresolvedReferences,PyShadowingNames,PyUnusedLocal

class MyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.reaction_channel_id = None  # Initialize reaction_channel_id
        self.vc_logs_channel_id = None

        self.load_default_logging_channel()

        async def set_edit_channel(self, inter: Interaction):
            return

    def load_default_logging_channel(self):
        global default_logging_channel_id
        try:
            with open(DEFAULT_LOGGING_CHANNEL_FILE, "r") as file:
                default_logging_channel_id = int(file.read().strip())
        except FileNotFoundError:
            default_logging_channel_id = None

    def save_default_logging_channel(self, channel_id):
        with open(DEFAULT_LOGGING_CHANNEL_FILE, "w") as file:
            file.write(str(channel_id))

    @app_commands.command(name="test", description="Is the bot working?")
    async def test(self, interaction: discord.Interaction):
        await interaction.response.send_message("The Bot is working")

    @app_commands.command(name="ping", description="Prints Pong!")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("Pong!")

    @app_commands.command(name="support", description="Prints an invite to the support server")
    async def support(self, interaction: discord.Interaction):
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

    @app_commands.command(name="timenow", description="What is the time in a particular time zone?")
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

    @app_commands.command(name="tzlist", description="Prints all available timezones")
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
        return

    @app_commands.command(
        name="roleadd",
        description="Adds a role to a user"
    )
    async def roleadd(self, inter: discord.Interaction, user: discord.Member, role: discord.Role):
        author = inter.user  # Get the author of the interaction
        guild = inter.guild  # Get the guild object
        default_role = guild.default_role  # Get the default role of the guild

        # Check if the author is the owner of the server
        if author.id == guild.owner_id:
            # Owner can always manage roles
            pass
        # Check if the author has the "manage roles" permission or is an administrator
        elif not author.guild_permissions.manage_roles and not author.guild_permissions.administrator:
            await inter.response.send_message("You do not have permission to change roles.")
            return

        # Get the author's highest role (defaulting to the guild's default role if the author has no roles)
        author_highest_role = max(author.roles, key=lambda r: r.position, default=default_role)

        # Check if the author is not the server owner or has no roles
        if author_highest_role != default_role:
            # Check if the role to be added is equal to or higher than the author's highest role
            if role.position >= author_highest_role.position:
                await inter.response.send_message(
                    "You cannot change that role because its position on the list is equal to or higher than your "
                    "highest role. Please ask someone with a higher role, e.g., an admin, to apply the role.")
                return

        # Check if the user already has the role
        if role in user.roles:
            await inter.response.send_message("The user already has that role.")
            return

        # Add the role to the user
        await user.add_roles(role)
        await inter.response.send_message(f"Added role {role.name} to {user.display_name}")

    @app_commands.command(
        name="roleremove",
        description="Removes a role from a user"
    )
    async def roleremove(self, inter: discord.Interaction, user: discord.Member, role: discord.Role):
        author = inter.user  # Get the author of the interaction
        guild = inter.guild  # Get the guild object

        # Check if the author is the owner of the server
        if author.id == guild.owner_id:
            # Owner can always manage roles
            pass
        # Check if the author has the "manage roles" permission or is an administrator
        elif not author.guild_permissions.manage_roles and not author.guild_permissions.administrator:
            await inter.response.send_message("You do not have permission to change roles.")
            return

        # Check if the role to be removed is higher than the bot's highest role
        if role.position >= max(inter.guild.me.roles, key=lambda r: r.position).position:
            await inter.response.send_message("I do not have permission to change that role.")
            return

        # Check if the user has the role to be removed
        if role not in user.roles:
            await inter.response.send_message("The user does not have that role.")
            return

        # Remove the role from the user
        await user.remove_roles(role)
        await inter.response.send_message(f"Removed role {role.name} from {user.display_name}")

    @app_commands.command(
        name="rolequery",
        description="Check if a user has a particular role"
    )
    async def rolequery(self, inter: discord.Interaction, user: discord.Member, role: discord.Role):
        # Check if the user has the role
        if role in user.roles:
            await inter.response.send_message(f"{user.display_name} has the role {role.name}.")
        else:
            await inter.response.send_message(f"{user.display_name} does not have the role {role.name}.")  #

    @app_commands.command(
        name="getuserroles",
        description="List all roles a user has"
    )
    async def getuserroles(self, inter: discord.Interaction, user: discord.Member):
        # Get the list of roles for the user
        user_roles = [role.name for role in user.roles]

        if user_roles:
            # Create a string with each role on a new line
            role_list = "\n".join(user_roles)
            # Send an ephemeral message in the same channel with the role list
            await inter.response.send_message(f"{user.display_name} has the following roles:\n{role_list}",
                                              ephemeral=True)
        else:
            await inter.response.send_message(f"{user.display_name} does not have any roles.")
        @app_commands.command(
            name="blacklistdomain",
            description="Add a domain to the blacklist",
        )
        async def blacklist_domain(self, inter: discord.Interaction, domain: str):
            global blacklisted_domains
            if domain not in blacklisted_domains:
                blacklisted_domains.append(domain)
                await inter.response.send_message(f"Domain '{domain}' has been added to the blacklist.", ephemeral=True)
                # Save updated list to file
                with open('blacklisted_domains.json', 'w') as file:
                    json.dump(blacklisted_domains, file)
            else:
                await inter.response.send_message(f"Domain '{domain}' is already blacklisted.", ephemeral=True)

        @commands.Cog.listener()
        async def on_message(self, message):
            if message.author == self.bot.user or message.author.guild_permissions.administrator:
                return  # Ignore messages sent by the bot itself

            for domain in blacklisted_domains:
                if domain in message.content:
                    server_name = message.guild.name if message.guild else "DM"
                    # Send DM to the user who sent the message
                    try:
                        await message.author.send(
                            f"The server '{server_name}' does not permit the domain '{domain}' to be posted. "
                            f"A message has been sent informing the admins and the message has been deleted."
                        )
                    except discord.Forbidden:
                        # If unable to send DM, send the message in the server's channel
                        await message.channel.send(
                            f"{message.author.mention}, the server '{server_name}' does not permit the domain '{domain}' "
                            f"to be posted."
                            f"A message has been sent informing the admins and the message has been deleted."
                        )

                    # Delete the message
                    await message.delete()
                    break  # Exit loop after deleting the message

        @app_commands.command(
            name="bldomainlist",
            description="List all blacklisted domains",
        )
        async def blacklist_domain_list(self, inter: discord.Interaction):
            if not inter.user.guild_permissions.administrator:
                await inter.response.send_message("You do not have permission to use this command.", ephemeral=True)
                return

            if not blacklisted_domains:
                await inter.response.send_message("There are no domains blacklisted.", ephemeral=True)
                return

            domains_list = "\n".join(blacklisted_domains)
            await inter.response.send_message(f"**Blacklisted Domains:**\n{domains_list}", ephemeral=True)
async def setup(bot: commands.Bot):
        await bot.add_cog(MyCog(bot))

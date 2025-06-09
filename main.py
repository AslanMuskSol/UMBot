import discord
import asyncio
import datetime
from discord.ext import commands, tasks
from keep_alive import keep_alive

# ======================== CONFIG SECTION ========================
TOKEN = "MTM4MTU0MjA2MzA5ODY5MTYxNQ.GMQ0Dd.LzFLSJO9AsW2bfuJH9hBuo3lJ9Zg9ozSyHFQfA"  # Replace with your bot token
GUILD_ID = 1245617853311356989  # Replace with your server ID
CHANNEL_ID = 1381538971430944778  # The channel where trigger messages are monitored
ROLE_NAME = "UM"  # Role to give and auto-remove

JOIN_TRIGGER = "1316"  # Message that gives the role
LEAVE_TRIGGER = "1613"  # Message that removes the role

INACTIVITY_LIMIT = 60  # Inactivity duration in seconds (1 hour = 3600)

INTENTS = discord.Intents.default()
INTENTS.message_content = True
INTENTS.guilds = True
INTENTS.members = True
INTENTS.messages = True
# ================================================================

bot = commands.Bot(command_prefix="!", intents=INTENTS)

# Store timestamps for activity tracking
user_activity = {}

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")
    check_inactive_users.start()

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.channel.id != CHANNEL_ID:
        return

    member = message.author
    guild = bot.get_guild(GUILD_ID)
    role = discord.utils.get(guild.roles, name=ROLE_NAME)

    # Save last message timestamp
    user_activity[member.id] = datetime.datetime.utcnow()

    # Trigger: Join role
    if message.content.strip() == JOIN_TRIGGER:
        await message.delete()
        if role not in member.roles:
            await member.add_roles(role)
            print(f"Gave role to {member}")
        return

    # Trigger: Leave role
    if message.content.strip() == LEAVE_TRIGGER:
        await message.delete()
        if role in member.roles:
            await member.remove_roles(role)
            print(f"Removed role from {member}")
        return

    await bot.process_commands(message)

@tasks.loop(minutes=1)
async def check_inactive_users():
    """Check every minute for inactive users and remove their role."""
    now = datetime.datetime.utcnow()
    guild = bot.get_guild(GUILD_ID)
    role = discord.utils.get(guild.roles, name=ROLE_NAME)

    for member_id, last_active in list(user_activity.items()):
        delta = (now - last_active).total_seconds()
        if delta > INACTIVITY_LIMIT:
            member = guild.get_member(member_id)
            if member and role in member.roles:
                await member.remove_roles(role)
                print(f"Auto-removed role from {member}")
            user_activity.pop(member_id, None)

keep_alive()
bot.run(TOKEN)

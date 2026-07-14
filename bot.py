import discord
from discord import app_commands

from config import TOKEN

intents = discord.Intents.default()

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@client.event
async def on_ready():
    await tree.sync()
    print(f"✅ Logged in as {client.user}")


client.run(TOKEN)

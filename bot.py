import discord
from discord import app_commands

from config import TOKEN

intents = discord.Intents.default()

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@tree.command(name="menu", description="Open the main menu")
async def menu(interaction: discord.Interaction):

    embed = discord.Embed(
        title="Main Menu",
        description="Choose an option below.",
        color=0x5865F2
    )

    await interaction.response.send_message(embed=embed)


@client.event
async def on_ready():
    await tree.sync()
    print(f"✅ {client.user} is online!")


client.run(TOKEN)

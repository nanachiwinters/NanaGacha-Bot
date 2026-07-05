import discord
from discord import app_commands
import random
import os

TOKEN = os.getenv("DISCORD_TOKEN")

ROOM_CODES = {
    "Room 1": "4829",
    "Room 2": "7314",
    "Room 3": "1962",
    "Room 4": "8501"
}

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

class GachaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎰 Roll Nanagacha", style=discord.ButtonStyle.primary)
    async def roll(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.defer(ephemeral=True)

        rooms = {
    "Room 1": 55,
    "Room 2": 25,
    "Room 3": 15,
    "Room 4": 5
}

room = random.choices(
    list(rooms.keys()),
    weights=list(rooms.values()),
    k=1
)[0]

code = ROOM_CODES[room]

            try:
                await interaction.user.send(
                    f"✨ You won **{room}**!\n🔑 Passcode: `{code}`"
                )
            except:
                pass

            await interaction.followup.send(
                f"🔑 You obtained access to **{room}**. Check your DMs.",
                ephemeral=True
            )
        else:
            await interaction.followup.send(
                "🌸 Nanachi found nothing… try again.",
                ephemeral=True
            )

@tree.command(name="nanagacha", description="Open Nanachi's gacha")
async def nanagacha(interaction: discord.Interaction):
    view = GachaView()
    await interaction.response.send_message(
        "🎒 **Nanachi's Lucky Pouch**\nPress the button to roll.",
        view=view
    )

@client.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {client.user}")

client.run(TOKEN)

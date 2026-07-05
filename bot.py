import discord
from discord import app_commands
import random
import os

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# 4-digit room codes
ROOM_CODES = {
    "Room 1": "4829",
    "Room 2": "7314",
    "Room 3": "1962",
    "Room 4": "8501"
}

# Weighted chances (Room 1 common → Room 4 rare)
ROOM_WEIGHTS = {
    "Room 1": 55,
    "Room 2": 25,
    "Room 3": 15,
    "Room 4": 5
}


class GachaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎰 Roll Nanagacha", style=discord.ButtonStyle.primary)
    async def roll(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.defer(ephemeral=True)

        room = random.choices(
            list(ROOM_WEIGHTS.keys()),
            weights=list(ROOM_WEIGHTS.values()),
            k=1
        )[0]

        code = ROOM_CODES[room]

        try:
            await interaction.user.send(
                f"✨ You obtained **{room}**!\n🔑 Passcode: `{code}`"
            )

            await interaction.followup.send(
                f"🎰 You got **{room}**. Check your DMs.",
                ephemeral=True
            )

        except:
            await interaction.followup.send(
                "I could not DM you. Please enable DMs from server members.",
                ephemeral=True
            )


@tree.command(name="nanagacha", description="Roll the Nanagacha")
async def nanagacha(interaction: discord.Interaction):
    await interaction.response.send_message(
        "🎰 Nanachi's Gacha is ready.",
        view=GachaView()
    )


@client.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {client.user}")


client.run(TOKEN)

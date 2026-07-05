import discord
from discord import app_commands
import random
import os

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# -----------------------------
# DATA
# -----------------------------

ROOM_CODES = {
    "Room 1": "4829",
    "Room 2": "7314",
    "Room 3": "1962",
    "Room 4": "8501"
}

ROOM_WEIGHTS = {
    "Room 1": 55,
    "Room 2": 25,
    "Room 3": 15,
    "Room 4": 5
}

# currency storage
user_currency = {}
# -----------------------------
# GACHA BUTTON
# -----------------------------

class GachaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎰 Roll Nanagacha", style=discord.ButtonStyle.primary)
    async def roll(self, interaction: discord.Interaction, button: discord.ui.Button):

        user_id = interaction.user.id

        if user_currency.get(user_id, 0) < 1:
            await interaction.response.send_message(
                "❌ Not enough coins. Use /daily.",
                ephemeral=True
            )
            return

        user_currency[user_id] -= 1

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
                "I could not DM you. Enable DMs from server members.",
                ephemeral=True
            )
            # -----------------------------
# COMMANDS
# -----------------------------

@tree.command(name="nanagacha", description="Roll the Nanagacha")
async def nanagacha(interaction: discord.Interaction):
    await interaction.response.send_message(
        "🎰 Nanagacha is ready. Roll if you have coins.",
        view=GachaView()
    )


import time

daily_claims = {}

COOLDOWN = 86400  # 24 hours


@tree.command(name="daily", description="Claim your daily ticket")
async def daily(interaction: discord.Interaction):

    user_id = interaction.user.id
    now = time.time()

    last_claim = daily_claims.get(user_id, 0)

    if now - last_claim < COOLDOWN:
        remaining = int(COOLDOWN - (now - last_claim))
        hours = remaining // 3600
        minutes = (remaining % 3600) // 60

        await interaction.response.send_message(
            f"⏳ You already claimed your daily.\nTry again in {hours}h {minutes}m.",
            ephemeral=True
        )
        return

    daily_claims[user_id] = now

    user_currency[user_id] = user_currency.get(user_id, 0) + 1

    await interaction.response.send_message(
        "🎟️ You claimed your daily ticket (1).",
        ephemeral=True
    )


@tree.command(name="givecoins", description="Admin: give coins")
async def givecoins(interaction: discord.Interaction, user: discord.Member, amount: int):

    user_currency[user.id] = user_currency.get(user.id, 0) + amount

    await interaction.response.send_message(
        f"Given {amount} coins to {user.mention}",
        ephemeral=True
    )


# -----------------------------
# READY + RUN
# -----------------------------

@client.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {client.user}")

client.run(TOKEN)



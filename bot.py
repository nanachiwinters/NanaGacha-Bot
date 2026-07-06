import discord
from discord import app_commands
import random
import os
import json
import time

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# -----------------------------
# ROOMS SYSTEM
# -----------------------------

def load_rooms():
    with open("rooms.json", "r") as f:
        return json.load(f)

def save_rooms(data):
    with open("rooms.json", "w") as f:
        json.dump(data, f, indent=4)

rooms = load_rooms()

# -----------------------------
# COINS SYSTEM
# -----------------------------

def load_coins():
    try:
        with open("coins.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_coins(data):
    with open("coins.json", "w") as f:
        json.dump(data, f, indent=4)

user_currency = load_coins()

# -----------------------------
# DATA
# -----------------------------

daily_claims = {}
COOLDOWN = 86400

ALLOWED_ROLE_ID = 1517330293101564036

# -----------------------------
# GACHA BUTTON
# -----------------------------

class GachaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎰 Normal Roll (1 coin)", style=discord.ButtonStyle.primary)
    async def roll(self, interaction: discord.Interaction, button: discord.ui.Button):

        user_id = interaction.user.id

        if user_currency.get(str(user_id), 0) < 1:
            await interaction.response.send_message(
                "❌ Not enough coins. Use /daily.",
                ephemeral=True
            )
            return

        user_currency[str(user_id)] -= 1
        save_coins(user_currency)

        await interaction.response.defer(ephemeral=True)

        room = random.choices(
            list(rooms.keys()),
            weights=[rooms[r]["weight"] for r in rooms],
            k=1
        )[0]

        code = rooms[room]["code"]

        try:
            await interaction.user.send(
                f"✨ NORMAL ROLL!\nYou got **{room}**!\n🔑 Passcode: `{code}`"
            )

            await interaction.followup.send(
                f"🎰 Normal roll success! Check your DMs.",
                ephemeral=True
            )

        except:
            await interaction.followup.send(
                "I could not DM you. Enable DMs.",
                ephemeral=True
            )

    # 🍀 LUCKY ROLL BUTTON (NEW)
    @discord.ui.button(label="🍀 Lucky Roll (3 coins)", style=discord.ButtonStyle.success)
    async def lucky_roll(self, interaction: discord.Interaction, button: discord.ui.Button):

        user_id = interaction.user.id

        if user_currency.get(str(user_id), 0) < 3:
            await interaction.response.send_message(
                "❌ You need 3 Nanacoins for a lucky roll.",
                ephemeral=True
            )
            return

        user_currency[str(user_id)] -= 3
        save_coins(user_currency)

        await interaction.response.defer(ephemeral=True)

        lucky_pool = [r for r in rooms if rooms[r].get("lucky")]

        if not lucky_pool:
            await interaction.followup.send("❌ No lucky rooms set.", ephemeral=True)
            return

        room = random.choices(
            lucky_pool,
            weights=[rooms[r]["weight"] for r in lucky_pool],
            k=1
        )[0]

        code = rooms[room]["code"]

        await interaction.user.send(
            f"🍀 LUCKY ROLL!\nYou got **{room}**!\n🔑 Code: `{code}`"
        )

        await interaction.followup.send(
            "🍀 Lucky roll success! Check DMs.",
            ephemeral=True
        )

# -----------------------------
# COMMANDS
# -----------------------------

@tree.command(name="nanagacha", description="Roll the Nanagacha")
async def nanagacha(interaction: discord.Interaction):
    await interaction.response.send_message(
        "🎰 Nanagacha is ready.",
        view=GachaView()
    )

# -----------------------------
# DAILY
# -----------------------------

@tree.command(name="daily", description="Claim your daily Nanacoin")
async def daily(interaction: discord.Interaction):

    user_id = interaction.user.id
    now = time.time()

    last_claim = daily_claims.get(user_id, 0)

    if now - last_claim < COOLDOWN:
        remaining = int(COOLDOWN - (now - last_claim))
        hours = remaining // 3600
        minutes = (remaining % 3600) // 60

        await interaction.response.send_message(
            f"⏳ Try again in {hours}h {minutes}m.",
            ephemeral=True
        )
        return

    daily_claims[user_id] = now

    user_currency[str(user_id)] = user_currency.get(str(user_id), 0) + 1
    save_coins(user_currency)

    await interaction.response.send_message(
        "🎟️ You got 1 Nanacoin.",
        ephemeral=True
    )

# -----------------------------
# GIVE COINS
# -----------------------------

@tree.command(name="givecoins", description="Admin: give coins")
async def givecoins(interaction: discord.Interaction, user: discord.Member, amount: int):

    if ALLOWED_ROLE_ID not in [role.id for role in interaction.user.roles]:
        await interaction.response.send_message("❌ No permission.", ephemeral=True)
        return

    user_currency[str(user.id)] += amount
    save_coins(user_currency)

    await interaction.response.send_message(
        f"✅ Gave {amount} coins.",
        ephemeral=True
    )

# -----------------------------
# BALANCE
# -----------------------------

@tree.command(name="balance", description="Check coins")
async def balance(interaction: discord.Interaction):

    amount = user_currency.get(str(interaction.user.id), 0)

    await interaction.response.send_message(
        f"🪙 You have {amount} Nanacoins.",
        ephemeral=True
    )

# -----------------------------
# READY
# -----------------------------

@client.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {client.user}")

client.run(TOKEN)

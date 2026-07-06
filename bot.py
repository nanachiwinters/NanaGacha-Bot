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
# DATA
# -----------------------------

user_currency = {}
daily_claims = {}
COOLDOWN = 86400

ALLOWED_ROLE_ID = 1517330293101564036  # YOUR ROLE ID

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
            list(rooms.keys()),
            weights=[rooms[r]["weight"] for r in rooms],
            k=1
        )[0]

        code = rooms[room]["code"]

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
        "🎰 Nanagacha is ready. Roll if you have Nanacoins.",
        view=GachaView()
    )


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
            f"⏳ You already claimed your daily.\nTry again in {hours}h {minutes}m.",
            ephemeral=True
        )
        return

    daily_claims[user_id] = now
    user_currency[user_id] = user_currency.get(user_id, 0) + 1

    await interaction.response.send_message(
        "🎟️ You claimed your daily Nanacoin (1).",
        ephemeral=True
    )


# -----------------------------
# GIVE COINS (ROLE LOCKED)
# -----------------------------

@tree.command(name="givecoins", description="Admin: give coins")
async def givecoins(interaction: discord.Interaction, user: discord.Member, amount: int):

    if ALLOWED_ROLE_ID not in [role.id for role in interaction.user.roles]:
        await interaction.response.send_message(
            "❌ You don't have permission to use this command.",
            ephemeral=True
        )
        return

    if amount <= 0:
        await interaction.response.send_message(
            "❌ Amount must be greater than 0.",
            ephemeral=True
        )
        return

    user_currency[user.id] = user_currency.get(user.id, 0) + amount

    await interaction.response.send_message(
        f"✅ Gave {amount} Nanacoins to {user.mention}.",
        ephemeral=True
    )


# -----------------------------
# SET ROOM CODE (ROLE LOCKED)
# -----------------------------

class RoomSelect(discord.ui.Select):
    def __init__(self, rooms, code):

        options = [
            discord.SelectOption(label=room)
            for room in rooms
        ]

        self.rooms = rooms
        self.code = code

        super().__init__(
            placeholder="Choose a room...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):

        room = self.values[0]

        if ALLOWED_ROLE_ID not in [role.id for role in interaction.user.roles]:
            await interaction.response.send_message(
                "❌ You don't have permission.",
                ephemeral=True
            )
            return

        rooms[room]["code"] = self.code
        save_rooms(rooms)

        await interaction.response.send_message(
            f"✅ Updated **{room}** passcode to `{self.code}`.",
            ephemeral=True
        )


class RoomDropdownView(discord.ui.View):
    def __init__(self, code):
        super().__init__(timeout=60)
        self.add_item(RoomSelect(list(rooms.keys()), code))


@tree.command(name="setcode", description="Admin: change room passcode (dropdown)")
async def setcode(interaction: discord.Interaction, code: str):

    if ALLOWED_ROLE_ID not in [role.id for role in interaction.user.roles]:
        await interaction.response.send_message(
            "❌ You don't have permission.",
            ephemeral=True
        )
        return

    await interaction.response.send_message(
        "Select the room you want to update:",
        view=RoomDropdownView(code),
        ephemeral=True
    )

# -----------------------------
# BALANCE
# -----------------------------

@tree.command(name="balance", description="Check Nanacoin balance")
async def balance(interaction: discord.Interaction):

    amount = user_currency.get(interaction.user.id, 0)

    await interaction.response.send_message(
        f"🪙 You have **{amount} Nanacoins**.",
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

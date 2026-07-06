import discord
from discord import app_commands
import random
import os
import json
import time
import asyncio

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# -----------------------------
# FILE SYSTEM
# -----------------------------

def load_rooms():
    try:
        with open("rooms.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_rooms(data):
    with open("rooms.json", "w") as f:
        json.dump(data, f, indent=4)

rooms = load_rooms()

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
# RARITY SYSTEM
# -----------------------------

RARITY_COLORS = {
    "Common": 0x95a5a6,
    "Rare": 0x3498db,
    "Epic": 0x9b59b6,
    "Legendary": 0xf1c40f
}

RARITY_EMOJI = {
    "Common": "🟢",
    "Rare": "🔵",
    "Epic": "🟣",
    "Legendary": "🟡"
}

# -----------------------------
# GACHA
# -----------------------------

class GachaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎰 Normal (1)", style=discord.ButtonStyle.primary)
    async def normal(self, interaction: discord.Interaction, button: discord.ui.Button):

        uid = str(interaction.user.id)

        if user_currency.get(uid, 0) < 1:
            await interaction.response.send_message("❌ Not enough coins.", ephemeral=True)
            return

        user_currency[uid] -= 1
        save_coins(user_currency)

        await self.spin(interaction, lucky=False)

    @discord.ui.button(label="🍀 Lucky (3)", style=discord.ButtonStyle.success)
    async def lucky(self, interaction: discord.Interaction, button: discord.ui.Button):

        uid = str(interaction.user.id)

        if user_currency.get(uid, 0) < 3:
            await interaction.response.send_message("❌ Not enough coins.", ephemeral=True)
            return

        user_currency[uid] -= 3
        save_coins(user_currency)

        await self.spin(interaction, lucky=True)

    # -----------------------------
    # SPIN ANIMATION
    # -----------------------------

    async def spin(self, interaction, lucky=False):

        await interaction.response.send_message("🎡 Spinning...", ephemeral=True)
        msg = await interaction.original_response()

        frames = ["🎡 Spinning", "🎡 Spinning.", "🎡 Spinning..", "🎡 Spinning..."]

        for _ in range(2):
            for f in frames:
                await msg.edit(content=f)
                await asyncio.sleep(0.15)

        if lucky:
            pool = [r for r in rooms if rooms[r].get("lucky") is True]
        else:
            pool = [r for r in rooms if not rooms[r].get("lucky", False)]

        if not pool:
            await msg.edit(content="❌ No rooms available.")
            return

        room = random.choices(
            pool,
            weights=[rooms[r]["weight"] for r in pool],
            k=1
        )[0]

        data = rooms[room]
        rarity = data.get("rarity", "Common")

        embed = discord.Embed(
            title=f"{RARITY_EMOJI.get(rarity)} {rarity} ROLL",
            description=f"**{room}**\n🔑 Code: `{data['code']}`",
            color=RARITY_COLORS.get(rarity, 0x3498db)
        )

        try:
            await interaction.user.send(embed=embed)
            await msg.edit(content="📩 Check your DMs!")
        except:
            await msg.edit(content="❌ Could not DM you.")

# -----------------------------
# NANAGACHA
# -----------------------------

@tree.command(name="nanagacha", description="Play Nanagacha")
async def nanagacha(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🎰 NANAGACHA",
        description="Click a button below to roll!",
        color=0x3498db
    )
    embed.set_footer(text="Normal = 1 coin | Lucky = 3 coins")

    await interaction.response.send_message(embed=embed, view=GachaView())

# -----------------------------
# DAILY
# -----------------------------

@tree.command(name="daily", description="Claim coins")
async def daily(interaction: discord.Interaction):

    uid = str(interaction.user.id)
    now = time.time()

    if now - daily_claims.get(uid, 0) < COOLDOWN:
        remaining = int(COOLDOWN - (now - daily_claims[uid]))
        await interaction.response.send_message(f"⏳ Wait {remaining//3600}h", ephemeral=True)
        return

    daily_claims[uid] = now
    user_currency[uid] = user_currency.get(uid, 0) + 1
    save_coins(user_currency)

    await interaction.response.send_message("🎟️ +1 coin", ephemeral=True)

# -----------------------------
# LEADERBOARD
# -----------------------------

@tree.command(name="leaderboard", description="Top players")
async def leaderboard(interaction: discord.Interaction):

    top = sorted(user_currency.items(), key=lambda x: x[1], reverse=True)[:10]

    desc = ""
    for i, (uid, coins) in enumerate(top, start=1):
        desc += f"**{i}.** <@{uid}> — {coins}\n"

    embed = discord.Embed(
        title="🏆 LEADERBOARD",
        description=desc or "No data",
        color=0xf1c40f
    )

    await interaction.response.send_message(embed=embed)

# -----------------------------
# GIVE COINS
# -----------------------------

@tree.command(name="givecoins", description="Admin give coins")
async def givecoins(interaction: discord.Interaction, user: discord.Member, amount: int):

    if ALLOWED_ROLE_ID not in [role.id for role in interaction.user.roles]:
        await interaction.response.send_message("❌ No permission", ephemeral=True)
        return

    uid = str(user.id)
    user_currency[uid] = user_currency.get(uid, 0) + amount
    save_coins(user_currency)

    await interaction.response.send_message("✅ Done", ephemeral=True)

# -----------------------------
# SETCODE
# -----------------------------

class RoomSelect(discord.ui.Select):
    def __init__(self, code):

        self.code = code

        options = [discord.SelectOption(label=r) for r in rooms.keys()]

        super().__init__(
            placeholder="Select room...",
            options=options,
            min_values=1,
            max_values=1
        )

    async def callback(self, interaction: discord.Interaction):

        if ALLOWED_ROLE_ID not in [role.id for role in interaction.user.roles]:
            await interaction.response.send_message("❌ No permission", ephemeral=True)
            return

        room = self.values[0]
        rooms[room]["code"] = self.code
        save_rooms(rooms)

        await interaction.response.send_message(f"✅ Updated {room}", ephemeral=True)

class RoomView(discord.ui.View):
    def __init__(self, code):
        super().__init__(timeout=60)
        self.add_item(RoomSelect(code))

@tree.command(name="setcode", description="Change room code")
async def setcode(interaction: discord.Interaction, code: str):

    if ALLOWED_ROLE_ID not in [role.id for role in interaction.user.roles]:
        await interaction.response.send_message("❌ No permission", ephemeral=True)
        return

    await interaction.response.send_message(
        "Select room:",
        view=RoomView(code),
        ephemeral=True
    )

# -----------------------------
# BALANCE
# -----------------------------

@tree.command(name="balance", description="Check coins")
async def balance(interaction: discord.Interaction):

    uid = str(interaction.user.id)

    await interaction.response.send_message(
        f"🪙 {user_currency.get(uid, 0)} coins",
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

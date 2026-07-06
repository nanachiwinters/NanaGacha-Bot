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
    with open("rooms.json", "r") as f:
        return json.load(f)

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

# -----------------------------
# GACHA VIEW
# -----------------------------

class GachaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎰 Normal Roll (1 coin)", style=discord.ButtonStyle.primary)
    async def normal(self, interaction: discord.Interaction, button: discord.ui.Button):

        user_id = str(interaction.user.id)

        if user_currency.get(user_id, 0) < 1:
            await interaction.response.send_message("❌ Not enough coins.", ephemeral=True)
            return

        user_currency[user_id] -= 1
        save_coins(user_currency)

        await self.spin(interaction, lucky=False)

    @discord.ui.button(label="🍀 Lucky Roll (3 coins)", style=discord.ButtonStyle.success)
    async def lucky(self, interaction: discord.Interaction, button: discord.ui.Button):

        user_id = str(interaction.user.id)

        if user_currency.get(user_id, 0) < 3:
            await interaction.response.send_message("❌ Not enough coins.", ephemeral=True)
            return

        user_currency[user_id] -= 3
        save_coins(user_currency)

        await self.spin(interaction, lucky=True)

    # -----------------------------
    # 🎡 SPINNING ANIMATION
    # -----------------------------

    async def spin(self, interaction, lucky=False):

        await interaction.response.send_message("🎡 Spinning roulette...", ephemeral=True)

        msg = await interaction.original_response()

        spin_texts = ["🎡 Spinning.", "🎡 Spinning..", "🎡 Spinning..."]

        for _ in range(3):
            for t in spin_texts:
                await msg.edit(content=t)
                await asyncio.sleep(0.5)

        pool = list(rooms.keys())

        if lucky:
            pool = [r for r in rooms if rooms[r].get("lucky")]

        room = random.choices(
            pool,
            weights=[rooms[r]["weight"] for r in pool],
            k=1
        )[0]

        data = rooms[room]
        rarity = data.get("rarity", "Common")
        code = data["code"]

        embed = discord.Embed(
            title=f"{self.get_emoji(rarity)} {rarity} ROLL",
            description=f"**{room}**\n🔑 Code: `{code}`",
            color=RARITY_COLORS.get(rarity, 0x3498db)
        )

        await interaction.user.send(embed=embed)

        await msg.edit(content="📩 Check your DMs!")

    def get_emoji(self, rarity):
        return {
            "Common": "🟢",
            "Rare": "🔵",
            "Epic": "🟣",
            "Legendary": "🟡"
        }.get(rarity, "⚪")

# -----------------------------
# NANAGACHA
# -----------------------------

@tree.command(name="nanagacha", description="Play Nanagacha")
async def nanagacha(interaction: discord.Interaction):

    view = GachaView()

    embed = discord.Embed(
        title="🎰 NANAGACHA",
        description="Click a button below to roll!",
        color=0x3498db
    )

    embed.set_footer(text="Normal = 1 coin | Lucky = 3 coins")

    await interaction.response.send_message(embed=embed, view=view)

# -----------------------------
# DAILY
# -----------------------------

@tree.command(name="daily", description="Claim daily coin")
async def daily(interaction: discord.Interaction):

    user_id = str(interaction.user.id)
    now = time.time()

    last = daily_claims.get(user_id, 0)

    if now - last < COOLDOWN:
        remaining = int(COOLDOWN - (now - last))
        await interaction.response.send_message(f"⏳ Try again in {remaining//3600}h", ephemeral=True)
        return

    daily_claims[user_id] = now
    user_currency[user_id] = user_currency.get(user_id, 0) + 1
    save_coins(user_currency)

    await interaction.response.send_message("🎟️ +1 coin", ephemeral=True)

# -----------------------------
# LEADERBOARD
# -----------------------------

@tree.command(name="leaderboard", description="Top coin players")
async def leaderboard(interaction: discord.Interaction):

    sorted_users = sorted(user_currency.items(), key=lambda x: x[1], reverse=True)[:10]

    desc = ""
    for i, (uid, coins) in enumerate(sorted_users, start=1):
        desc += f"**{i}.** <@{uid}> — {coins} coins\n"

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

    await interaction.response.send_message(f"✅ Gave {amount} coins", ephemeral=True)

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

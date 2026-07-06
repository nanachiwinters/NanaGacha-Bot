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
# SETTINGS
# -----------------------------

daily_claims = {}
COOLDOWN = 86400
ALLOWED_ROLE_ID = 1517330293101564036

gacha_open = True

# -----------------------------
# RARITY
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
# GACHA SYSTEM
# -----------------------------

class GachaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    # NORMAL
    @discord.ui.button(label="🎰 Normal (1)", style=discord.ButtonStyle.primary)
    async def normal(self, interaction: discord.Interaction, button: discord.ui.Button):

        global gacha_open

        uid = str(interaction.user.id)

        if not gacha_open:
            await interaction.response.send_message("🚫 Gacha is CLOSED", ephemeral=True)
            return

        if user_currency.get(uid, 0) < 1:
            await interaction.response.send_message("❌ Not enough coins", ephemeral=True)
            return

        user_currency[uid] -= 1
        save_coins(user_currency)

        await self.spin(interaction, lucky=False)

    # LUCKY
    @discord.ui.button(label="🍀 Lucky (3)", style=discord.ButtonStyle.success)
    async def lucky(self, interaction: discord.Interaction, button: discord.ui.Button):

        global gacha_open

        uid = str(interaction.user.id)

        if not gacha_open:
            await interaction.response.send_message("🚫 Gacha is CLOSED", ephemeral=True)
            return

        if user_currency.get(uid, 0) < 3:
            await interaction.response.send_message("❌ Not enough coins", ephemeral=True)
            return

        user_currency[uid] -= 3
        save_coins(user_currency)

        await self.spin(interaction, lucky=True)

    # -----------------------------
    # SLOT SPIN
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
            await msg.edit(content="❌ No rooms available")
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
            await msg.edit(content="❌ Could not DM you")

# -----------------------------
# NANAGACHA
# -----------------------------

@tree.command(name="nanagacha", description="Play Nanagacha")
async def nanagacha(interaction: discord.Interaction):

    status = "🟢 OPENED" if gacha_open else "🔴 CLOSED"

    embed = discord.Embed(
        title="🎰 NanaGacha",
        description=f"Click a button below to roll!\n\nStatus: {status}",
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

    await interaction.response.send_message("🪙 +1 coin", ephemeral=True)

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
# SET ROOM CODE
# -----------------------------

async def room_autocomplete(
    interaction: discord.Interaction,
    current: str,
):
    return [
        app_commands.Choice(name=room, value=room)
        for room in rooms.keys()
        if current.lower() in room.lower()
    ][:25]
    
@tree.command(name="setcode", description="Change the code for an existing room")
@app_commands.autocomplete(room=room_autocomplete)
async def setcode(
    interaction: discord.Interaction,
    room: str,
    new_code: str
):

    if ALLOWED_ROLE_ID not in [role.id for role in interaction.user.roles]:
        await interaction.response.send_message(
            "❌ No permission.",
            ephemeral=True
        )
        return

    old_code = rooms[room]["code"]
    rooms[room]["code"] = new_code
    save_rooms(rooms)

    embed = discord.Embed(
        title="✅ Room Code Updated",
        color=0x2ecc71
    )

    embed.add_field(name="Room", value=room, inline=False)
    embed.add_field(name="Old Code", value=f"`{old_code}`")
    embed.add_field(name="New Code", value=f"`{new_code}`")

    await interaction.response.send_message(embed=embed, ephemeral=True)

# -----------------------------
# OPEN / CLOSE GACHA
# -----------------------------

@tree.command(name="open_gacha", description="Open gacha shop")
async def open_gacha(interaction: discord.Interaction):

    global gacha_open

    if ALLOWED_ROLE_ID not in [role.id for role in interaction.user.roles]:
        await interaction.response.send_message("❌ No permission", ephemeral=True)
        return

    gacha_open = True
    await interaction.response.send_message("🟢 Gacha OPENED")

@tree.command(name="close_gacha", description="Close gacha shop")
async def close_gacha(interaction: discord.Interaction):

    global gacha_open

    if ALLOWED_ROLE_ID not in [role.id for role in interaction.user.roles]:
        await interaction.response.send_message("❌ No permission", ephemeral=True)
        return

    gacha_open = False
    await interaction.response.send_message("🔴 Gacha CLOSED")

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
# ADMIN PANEL
# -----------------------------

class AdminView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="🔑 Rooms", style=discord.ButtonStyle.primary)
    async def rooms_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "🚧 Rooms menu coming next!",
            ephemeral=True
        )

    @discord.ui.button(label="💰 Economy", style=discord.ButtonStyle.success)
    async def economy_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "🚧 Economy menu coming next!",
            ephemeral=True
        )

    @discord.ui.button(label="🟢 Open", style=discord.ButtonStyle.secondary)
    async def open_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "🚧 Open button coming next!",
            ephemeral=True
        )

    @discord.ui.button(label="🔴 Close", style=discord.ButtonStyle.secondary)
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "🚧 Close button coming next!",
            ephemeral=True
        )

    @discord.ui.button(label="❌ Close Panel", style=discord.ButtonStyle.danger, row=1)
    async def exit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(view=self)


@tree.command(name="admin", description="Open the admin panel")
async def admin(interaction: discord.Interaction):

    if ALLOWED_ROLE_ID not in [role.id for role in interaction.user.roles]:
        await interaction.response.send_message(
            "❌ No permission.",
            ephemeral=True
        )
        return

    status = "🟢 OPENED" if gacha_open else "🔴 CLOSED"

    embed = discord.Embed(
        title="🛠️ NanaGacha Admin Panel",
        description=f"**Gacha Status:** {status}",
        color=0x5865F2
    )

    embed.set_footer(text="Select an option below.")

    await interaction.response.send_message(
        embed=embed,
        view=AdminView(),
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



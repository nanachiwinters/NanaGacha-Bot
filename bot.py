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
# NORMAL ROOM MODAL
# -----------------------------

class NormalRoomsModal(discord.ui.Modal, title="🏠 Edit Normal Rooms"):

    room1 = discord.ui.TextInput(
        label="Room 1 Code",
        placeholder="Enter Room 1 code",
        required=True,
        max_length=20
    )

    room2 = discord.ui.TextInput(
        label="Room 2 Code",
        placeholder="Enter Room 2 code",
        required=True,
        max_length=20
    )

    room3 = discord.ui.TextInput(
        label="Room 3 Code",
        placeholder="Enter Room 3 code",
        required=True,
        max_length=20
    )

    room4 = discord.ui.TextInput(
        label="Room 4 Code",
        placeholder="Enter Room 4 code",
        required=True,
        max_length=20
    )

    async def on_submit(self, interaction: discord.Interaction):

        old_codes = {
            "Room 1": rooms["Room 1"]["code"],
            "Room 2": rooms["Room 2"]["code"],
            "Room 3": rooms["Room 3"]["code"],
            "Room 4": rooms["Room 4"]["code"]
        }

        rooms["Room 1"]["code"] = self.room1.value
        rooms["Room 2"]["code"] = self.room2.value
        rooms["Room 3"]["code"] = self.room3.value
        rooms["Room 4"]["code"] = self.room4.value

        save_rooms(rooms)

        embed = discord.Embed(
            title="✅ Normal Room Codes Updated",
            color=0x2ecc71
        )

        for room in old_codes:
            embed.add_field(
                name=room,
                value=f"`{old_codes[room]}` ➜ `{rooms[room]['code']}`",
                inline=False
            )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )
# -----------------------------
# LUCKY ROOM MODAL
# -----------------------------

class LuckyRoomsModal(discord.ui.Modal, title="🍀 Edit Lucky Rooms"):

    room1 = discord.ui.TextInput(
        label="Lucky Room 1 Code",
        placeholder="Enter Lucky Room 1 code",
        required=True,
        max_length=20
    )

    room2 = discord.ui.TextInput(
        label="Lucky Room 2 Code",
        placeholder="Enter Lucky Room 2 code",
        required=True,
        max_length=20
    )

    room3 = discord.ui.TextInput(
        label="Lucky Room 3 Code",
        placeholder="Enter Lucky Room 3 code",
        required=True,
        max_length=20
    )

    room4 = discord.ui.TextInput(
        label="Lucky Room 4 Code",
        placeholder="Enter Lucky Room 4 code",
        required=True,
        max_length=20
    )

    async def on_submit(self, interaction: discord.Interaction):

        old_codes = {
            "Lucky Room 1": rooms["Lucky Room 1"]["code"],
            "Lucky Room 2": rooms["Lucky Room 2"]["code"],
            "Lucky Room 3": rooms["Lucky Room 3"]["code"],
            "Lucky Room 4": rooms["Lucky Room 4"]["code"]
        }

        rooms["Lucky Room 1"]["code"] = self.room1.value
        rooms["Lucky Room 2"]["code"] = self.room2.value
        rooms["Lucky Room 3"]["code"] = self.room3.value
        rooms["Lucky Room 4"]["code"] = self.room4.value

        save_rooms(rooms)

        embed = discord.Embed(
            title="✅ Lucky Room Codes Updated",
            color=0xf1c40f
        )

        for room in old_codes:
            embed.add_field(
                name=room,
                value=f"`{old_codes[room]}` ➜ `{rooms[room]['code']}`",
                inline=False
            )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )
        
# -----------------------------
# ROOM MENU
# -----------------------------

class RoomMenuView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="🏠 Normal Rooms", style=discord.ButtonStyle.primary)
    async def normal_rooms(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_modal(
            NormalRoomsModal()
    )

    @discord.ui.button(label="🍀 Lucky Rooms", style=discord.ButtonStyle.success)
    async def lucky_rooms(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_modal(
            LuckyRoomsModal()
        )

    @discord.ui.button(label="📋 List Rooms", style=discord.ButtonStyle.secondary)
    async def list_rooms(self, interaction: discord.Interaction, button: discord.ui.Button):

        embed = discord.Embed(
            title="📋 Room List",
            color=0x3498db
        )

        for room, data in rooms.items():
            lucky = " 🍀" if data.get("lucky") else ""
            embed.add_field(
                name=f"{room}{lucky}",
                value=(
                    f"🔑 `{data['code']}`\n"
                    f"⭐ {data['rarity']}\n"
                    f"⚖️ Weight: {data['weight']}"
                ),
                inline=False
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="◀ Back", style=discord.ButtonStyle.danger)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):

        status = "🟢 OPENED" if gacha_open else "🔴 CLOSED"

        embed = discord.Embed(
            title="🛠️ NanaGacha Admin Panel",
            description=f"**Gacha Status:** {status}",
            color=0x5865F2
        )

        embed.set_footer(text="Select an option below.")

        await interaction.response.edit_message(
            embed=embed,
            view=AdminView()
        )
        
# -----------------------------
# GIVE COINS MODAL
# -----------------------------

class GiveCoinsModal(discord.ui.Modal, title="➕ Give Coins"):

    user_id = discord.ui.TextInput(
        label="User ID",
        placeholder="Enter the user's Discord ID",
        required=True
    )

    amount = discord.ui.TextInput(
        label="Amount",
        placeholder="How many coins?",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):

    try:
        user = await client.fetch_user(int(self.user_id.value))
    except:
        await interaction.response.send_message(
            "❌ Invalid User ID.",
            ephemeral=True
        )
        return

        try:
            amount = int(self.amount.value)
        except:
            await interaction.response.send_message(
                "❌ Amount must be a number.",
                ephemeral=True
            )
            return

        uid = str(user.id)

        user_currency[uid] = user_currency.get(uid, 0) + amount
        save_coins(user_currency)

        embed = discord.Embed(
            title="✅ Coins Given",
            color=0x2ecc71
        )

        embed.add_field(name="User", value=user.mention, inline=False)
        embed.add_field(name="Amount", value=f"🪙 {amount}", inline=False)
        embed.add_field(
            name="New Balance",
            value=f"🪙 {user_currency[uid]}",
            inline=False
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )
        
# -----------------------------
# REMOVE COINS MODAL
# -----------------------------

class RemoveCoinsModal(discord.ui.Modal, title="➖ Remove Coins"):

    user_id = discord.ui.TextInput(
        label="User ID",
        placeholder="Enter the user's Discord ID",
        required=True
    )

    amount = discord.ui.TextInput(
        label="Amount",
        placeholder="How many coins?",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):

        try:
            user = await client.fetch_user(int(self.user_id.value))
        except:
            await interaction.response.send_message(
                "❌ Invalid User ID.",
                ephemeral=True
            )
            return

        try:
            amount = int(self.amount.value)
        except:
            await interaction.response.send_message(
                "❌ Amount must be a number.",
                ephemeral=True
            )
            return

        uid = str(user.id)

        current = user_currency.get(uid, 0)
        new_balance = max(0, current - amount)

        user_currency[uid] = new_balance
        save_coins(user_currency)

        embed = discord.Embed(
            title="➖ Coins Removed",
            color=0xe74c3c
        )

        embed.add_field(name="User", value=user.mention, inline=False)
        embed.add_field(name="Removed", value=f"🪙 {amount}", inline=False)
        embed.add_field(name="New Balance", value=f"🪙 {new_balance}", inline=False)

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )
        
# -----------------------------
# SET COINS MODAL
# -----------------------------

class SetCoinsModal(discord.ui.Modal, title="💎 Set Coins"):

    user_id = discord.ui.TextInput(
        label="User ID",
        placeholder="Enter the user's Discord ID",
        required=True
    )

    amount = discord.ui.TextInput(
        label="New Balance",
        placeholder="Enter the new coin balance",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):

        try:
            user = await client.fetch_user(int(self.user_id.value))
        except:
            await interaction.response.send_message(
                "❌ Invalid User ID.",
                ephemeral=True
            )
            return

        try:
            amount = int(self.amount.value)
        except:
            await interaction.response.send_message(
                "❌ Amount must be a number.",
                ephemeral=True
            )
            return

        if amount < 0:
            amount = 0

        uid = str(user.id)

        user_currency[uid] = amount
        save_coins(user_currency)

        embed = discord.Embed(
            title="💎 Coins Set",
            color=0x3498db
        )

        embed.add_field(name="User", value=user.mention, inline=False)
        embed.add_field(name="New Balance", value=f"🪙 {amount}", inline=False)

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )
        
# -----------------------------
# VIEW BALANCE MODAL
# -----------------------------

class ViewBalanceModal(discord.ui.Modal, title="👛 View Balance"):

    user_id = discord.ui.TextInput(
        label="User ID",
        placeholder="Enter the user's Discord ID",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):

        try:
            user = await client.fetch_user(int(self.user_id.value))
        except:
            await interaction.response.send_message(
                "❌ Invalid User ID.",
                ephemeral=True
            )
            return

        uid = str(user.id)
        balance = user_currency.get(uid, 0)

        embed = discord.Embed(
            title="👛 User Balance",
            color=0xf1c40f
        )

        embed.add_field(
            name="User",
            value=user.mention,
            inline=False
        )

        embed.add_field(
            name="Balance",
            value=f"🪙 {balance} coins",
            inline=False
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )
        
# -----------------------------
# ECONOMY MENU
# -----------------------------

class EconomyMenuView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="➕ Give Coins", style=discord.ButtonStyle.success)
    async def give(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_modal(
            GiveCoinsModal()
        )

    @discord.ui.button(label="➖ Remove Coins", style=discord.ButtonStyle.danger)
    async def remove(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_modal(
            RemoveCoinsModal()
        )

    @discord.ui.button(label="💎 Set Coins", style=discord.ButtonStyle.primary)
    async def setcoins(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_modal(
            SetCoinsModal()
        )

    @discord.ui.button(label="👛 View Balance", style=discord.ButtonStyle.secondary)
    async def balance(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_modal(
            ViewBalanceModal()
        )

    @discord.ui.button(label="◀ Back", style=discord.ButtonStyle.danger, row=1)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):

        status = "🟢 OPENED" if gacha_open else "🔴 CLOSED"

        embed = discord.Embed(
            title="🛠️ NanaGacha Admin Panel",
            description=f"**Gacha Status:** {status}",
            color=0x5865F2
        )

        embed.set_footer(text="Select an option below.")

        await interaction.response.edit_message(
            embed=embed,
            view=AdminView()
        )
        
# -----------------------------
# ADMIN PANEL
# -----------------------------

class AdminView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="🔑 Rooms", style=discord.ButtonStyle.primary)
    async def rooms_button(self, interaction: discord.Interaction, button: discord.ui.Button):

        embed = discord.Embed(
            title="🏠 Room Management",
            description="Choose an option below.",
            color=0x3498db
        )

        await interaction.response.edit_message(
            embed=embed,
            view=RoomMenuView()
        )

    @discord.ui.button(label="💰 Economy", style=discord.ButtonStyle.success)
    async def economy_button(self, interaction: discord.Interaction, button: discord.ui.Button):

        embed = discord.Embed(
            title="💰 Economy Management",
            description="Choose an option below.",
            color=0x2ecc71
        )

        await interaction.response.edit_message(
            embed=embed,
            view=EconomyMenuView()
        )

    @discord.ui.button(label="🟢 Open", style=discord.ButtonStyle.success)
    async def open_button(self, interaction: discord.Interaction, button: discord.ui.Button):

        global gacha_open

        gacha_open = True

        embed = discord.Embed(
            title="🛠️ NanaGacha Admin Panel",
            description="**Gacha Status:** 🟢 OPENED",
            color=0x2ecc71
        )

        embed.set_footer(text="Select an option below.")

        await interaction.response.edit_message(
            embed=embed,
            view=AdminView()
        )

    @discord.ui.button(label="🔴 Close", style=discord.ButtonStyle.danger)
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):

        global gacha_open

        gacha_open = False

        embed = discord.Embed(
            title="🛠️ NanaGacha Admin Panel",
            description="**Gacha Status:** 🔴 CLOSED",
            color=0xe74c3c
        )

        embed.set_footer(text="Select an option below.")

        await interaction.response.edit_message(
            embed=embed,
            view=AdminView()
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


